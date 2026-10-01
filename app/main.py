import time

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import FileResponse, Response
from prometheus_client import Counter, Gauge, Histogram, generate_latest
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db import Base, engine, get_db
from app.tables import Hackathon, StudentRow, TeamRun
from engine.greedy import form_teams
from engine.models import Student
from engine.optimizer import optimize
from engine.scoring import (
    avg_coverage,
    availability_score,
    conflict_penalty,
    role_diversity,
    team_score,
)


Base.metadata.create_all(bind=engine)

app = FastAPI(title="TeamForge")


# -------------------------------------------------------------------
# Prometheus metrics
# -------------------------------------------------------------------

team_generation_requests = Counter(
    "teamforge_team_generation_requests_total",
    "Total number of team generation requests.",
)

team_generation_duration = Histogram(
    "teamforge_team_generation_duration_seconds",
    "Time spent generating teams.",
)

students_processed = Gauge(
    "teamforge_students_processed",
    "Number of students processed in the most recent team generation.",
)

teams_generated = Gauge(
    "teamforge_teams_generated",
    "Number of teams generated in the most recent team generation.",
)

team_coverage = Gauge(
    "teamforge_team_coverage",
    "Average skill coverage of the most recently generated teams.",
)


class HackathonCreate(BaseModel):
    name: str
    team_size: int = Field(gt=0)
    requirements: dict[str, int]


class StudentCreate(BaseModel):
    name: str
    skills: dict[str, int]
    slots: list[int]
    role: str
    avoid: list[int] = []


class GenerateRequest(BaseModel):
    hackathon_id: int
    optimize_teams: bool = True


@app.get("/")
def home():
    return FileResponse("app/static/index.html")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/metrics")
def metrics():
    return Response(
        generate_latest(),
        media_type="text/plain; version=0.0.4; charset=utf-8",
    )


@app.post("/hackathons")
def create_hackathon(
    payload: HackathonCreate,
    db: Session = Depends(get_db),
):
    hackathon = Hackathon(
        name=payload.name,
        team_size=payload.team_size,
        requirements=payload.requirements,
    )

    db.add(hackathon)
    db.commit()
    db.refresh(hackathon)

    return {
        "id": hackathon.id,
        "name": hackathon.name,
        "team_size": hackathon.team_size,
        "requirements": hackathon.requirements,
    }


@app.get("/hackathons")
def list_hackathons(
    db: Session = Depends(get_db),
):
    hackathons = db.query(Hackathon).all()

    return [
        {
            "id": hackathon.id,
            "name": hackathon.name,
            "team_size": hackathon.team_size,
            "requirements": hackathon.requirements,
        }
        for hackathon in hackathons
    ]


@app.get("/hackathons/{hackathon_id}")
def get_hackathon(
    hackathon_id: int,
    db: Session = Depends(get_db),
):
    hackathon = (
        db.query(Hackathon)
        .filter(Hackathon.id == hackathon_id)
        .first()
    )

    if hackathon is None:
        raise HTTPException(
            status_code=404,
            detail="Hackathon not found",
        )

    students = (
        db.query(StudentRow)
        .filter(StudentRow.hackathon_id == hackathon_id)
        .all()
    )

    return {
        "id": hackathon.id,
        "name": hackathon.name,
        "team_size": hackathon.team_size,
        "requirements": hackathon.requirements,
        "students": [
            {
                "id": student.id,
                "name": student.name,
                "skills": student.skills,
                "slots": student.slots,
                "role": student.role,
                "avoid": student.avoid,
            }
            for student in students
        ],
    }


@app.post("/hackathons/{hackathon_id}/students")
def add_student(
    hackathon_id: int,
    payload: StudentCreate,
    db: Session = Depends(get_db),
):
    hackathon = (
        db.query(Hackathon)
        .filter(Hackathon.id == hackathon_id)
        .first()
    )

    if hackathon is None:
        raise HTTPException(
            status_code=404,
            detail="Hackathon not found",
        )

    for skill, level in payload.skills.items():
        if not 1 <= level <= 5:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid skill level for {skill}",
            )

    student = StudentRow(
        hackathon_id=hackathon_id,
        name=payload.name,
        skills=payload.skills,
        slots=payload.slots,
        role=payload.role,
        avoid=payload.avoid,
    )

    db.add(student)
    db.commit()
    db.refresh(student)

    return {
        "id": student.id,
        "name": student.name,
    }


@app.post("/teams/generate")
def generate_teams(
    payload: GenerateRequest,
    db: Session = Depends(get_db),
):
    # Count every team-generation request.
    team_generation_requests.inc()

    hackathon = (
        db.query(Hackathon)
        .filter(Hackathon.id == payload.hackathon_id)
        .first()
    )

    if hackathon is None:
        raise HTTPException(
            status_code=404,
            detail="Hackathon not found",
        )

    rows = (
        db.query(StudentRow)
        .filter(
            StudentRow.hackathon_id == payload.hackathon_id
        )
        .all()
    )

    if not rows:
        raise HTTPException(
            status_code=400,
            detail="No students registered",
        )

    # Record the number of students processed.
    students_processed.set(len(rows))

    students = [
        Student(
            id=row.id,
            skills=row.skills,
            slots=frozenset(row.slots),
            role=row.role,
            avoid=frozenset(row.avoid),
        )
        for row in rows
    ]

    start = time.perf_counter()

    teams = form_teams(
        students,
        hackathon.requirements,
        hackathon.team_size,
    )

    if payload.optimize_teams:
        teams = optimize(
            teams,
            hackathon.requirements,
            iterations=200,
            seed=42,
        )

    seconds = time.perf_counter() - start

    # Record generation duration.
    team_generation_duration.observe(seconds)

    team_results = []

    for team in teams:
        coverage = avg_coverage(
            [team],
            hackathon.requirements,
        )

        team_results.append(
            {
                "members": [
                    {
                        "id": student.id,
                        "name": next(
                            row.name
                            for row in rows
                            if row.id == student.id
                        ),
                        "skills": student.skills,
                        "role": student.role,
                    }
                    for student in team
                ],
                "coverage": coverage,
                "availability": availability_score(team),
                "role_diversity": role_diversity(team),
                "conflicts": conflict_penalty(team),
                "score": team_score(
                    team,
                    hackathon.requirements,
                ),
            }
        )

    overall_coverage = avg_coverage(
        teams,
        hackathon.requirements,
    )

    overall_score = sum(
        team["score"]
        for team in team_results
    )

    # Record the latest generation results.
    teams_generated.set(len(team_results))
    team_coverage.set(overall_coverage)

    result = {
        "hackathon_id": hackathon.id,
        "team_count": len(team_results),
        "teams": team_results,
        "overall_coverage": overall_coverage,
        "overall_score": overall_score,
        "seconds": seconds,
    }

    run = TeamRun(
        hackathon_id=hackathon.id,
        coverage=overall_coverage,
        seconds=seconds,
        result=result,
    )

    db.add(run)
    db.commit()

    return result