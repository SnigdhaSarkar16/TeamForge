
import time

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import FileResponse, Response
from prometheus_client import Counter, Gauge, Histogram, generate_latest
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.assessment import (
    get_questions,
    grade_assessment,
    supported_skills,
)
from app.db import Base, engine, get_db
from app.tables import Hackathon, SkillAssessment, StudentRow, TeamRun
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


# -------------------------------------------------------------------
# Request models
# -------------------------------------------------------------------

class HackathonCreate(BaseModel):
    name: str
    team_size: int = Field(gt=0)
    requirements: dict[str, int]


class StudentCreate(BaseModel):
    name: str
    slots: list[int]
    role: str
    avoid: list[int] = Field(default_factory=list)


class GenerateRequest(BaseModel):
    hackathon_id: int
    optimize_teams: bool = True


class AssessmentSubmit(BaseModel):
    answers: dict[str, str]


# -------------------------------------------------------------------
# General endpoints
# -------------------------------------------------------------------

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


# -------------------------------------------------------------------
# Hackathon endpoints
# -------------------------------------------------------------------

@app.post("/hackathons")
def create_hackathon(
    payload: HackathonCreate,
    db: Session = Depends(get_db),
):
    if any(level < 0 or level > 5 for level in payload.requirements.values()):
        raise HTTPException(
            status_code=400,
            detail="Requirement levels must be between 0 and 5",
        )

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
def list_hackathons(db: Session = Depends(get_db)):
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
                "assessments": [
                    {
                        "skill": assessment.skill,
                        "percentage": assessment.percentage,
                        "proficiency_level": assessment.proficiency_level,
                        "proficiency_label": assessment.proficiency_label,
                    }
                    for assessment in student.assessments
                ],
            }
            for student in students
        ],
    }


# -------------------------------------------------------------------
# Student registration
# -------------------------------------------------------------------

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

    student = StudentRow(
        hackathon_id=hackathon_id,
        name=payload.name,
        skills={},
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
        "skills": student.skills,
        "message": "Registration successful. Complete skill assessments to establish proficiency.",
    }


# -------------------------------------------------------------------
# Skill assessment endpoints
# -------------------------------------------------------------------

@app.get("/assessments/skills")
def list_assessment_skills():
    return {"skills": supported_skills()}


@app.get("/assessments/{skill}/questions")
def assessment_questions(skill: str):
    questions = get_questions(skill)

    if not questions:
        raise HTTPException(
            status_code=404,
            detail=f"Unsupported skill: {skill}",
        )

    # get_questions should return questions without answer keys.
    return {
        "skill": skill.lower(),
        "total_questions": len(questions),
        "questions": questions,
    }


@app.post(
    "/hackathons/{hackathon_id}/students/{student_id}/assessments/{skill}"
)
def submit_assessment(
    hackathon_id: int,
    student_id: int,
    skill: str,
    payload: AssessmentSubmit,
    db: Session = Depends(get_db),
):
    student = (
        db.query(StudentRow)
        .filter(
            StudentRow.id == student_id,
            StudentRow.hackathon_id == hackathon_id,
        )
        .first()
    )

    if student is None:
        raise HTTPException(
            status_code=404,
            detail="Student not found in this hackathon",
        )

    normalized_skill = skill.strip().lower()

    if normalized_skill not in supported_skills():
        raise HTTPException(
            status_code=404,
            detail=f"Unsupported skill: {skill}",
        )

    try:
        result = grade_assessment(
            normalized_skill,
            payload.answers,
        )
    except (ValueError, KeyError) as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    assessment = SkillAssessment(
        student_id=student.id,
        skill=normalized_skill,
        correct_answers=result["correct_answers"],
        total_questions=result["total_questions"],
        percentage=result["percentage"],
        proficiency_level=result["proficiency_level"],
        proficiency_label=result["proficiency_label"],
        answers=payload.answers,
    )

    # Store the server-calculated proficiency, never a client-supplied score.
    updated_skills = dict(student.skills or {})
    updated_skills[normalized_skill] = result["proficiency_level"]
    student.skills = updated_skills

    db.add(assessment)
    db.commit()
    db.refresh(assessment)

    return {
        "assessment_id": assessment.id,
        "student_id": student.id,
        "skill": normalized_skill,
        "correct_answers": result["correct_answers"],
        "total_questions": result["total_questions"],
        "percentage": result["percentage"],
        "proficiency_level": result["proficiency_level"],
        "proficiency_label": result["proficiency_label"],
        "message": "Assessment submitted successfully.",
    }


@app.get(
    "/hackathons/{hackathon_id}/students/{student_id}/assessments"
)
def list_student_assessments(
    hackathon_id: int,
    student_id: int,
    db: Session = Depends(get_db),
):
    student = (
        db.query(StudentRow)
        .filter(
            StudentRow.id == student_id,
            StudentRow.hackathon_id == hackathon_id,
        )
        .first()
    )

    if student is None:
        raise HTTPException(
            status_code=404,
            detail="Student not found in this hackathon",
        )

    assessments = (
        db.query(SkillAssessment)
        .filter(SkillAssessment.student_id == student_id)
        .order_by(SkillAssessment.created_at.desc())
        .all()
    )

    return {
        "student_id": student_id,
        "assessments": [
            {
                "id": assessment.id,
                "skill": assessment.skill,
                "correct_answers": assessment.correct_answers,
                "total_questions": assessment.total_questions,
                "percentage": assessment.percentage,
                "proficiency_level": assessment.proficiency_level,
                "proficiency_label": assessment.proficiency_label,
                "created_at": assessment.created_at,
            }
            for assessment in assessments
        ],
    }


# -------------------------------------------------------------------
# Team generation
# -------------------------------------------------------------------

@app.post("/teams/generate")
def generate_teams(
    payload: GenerateRequest,
    db: Session = Depends(get_db),
):
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
        .filter(StudentRow.hackathon_id == payload.hackathon_id)
        .all()
    )

    if not rows:
        raise HTTPException(
            status_code=400,
            detail="No students registered",
        )

    # Do not generate teams using unassessed student skill profiles.
    unassessed_students = [
        row.name for row in rows if not row.skills
    ]

    if unassessed_students:
        raise HTTPException(
            status_code=400,
            detail={
                "message": (
                    "Every student must complete at least one skill "
                    "assessment before team generation."
                ),
                "students_without_assessments": unassessed_students,
            },
        )

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
    team_generation_duration.observe(seconds)

    student_names = {row.id: row.name for row in rows}
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
                        "name": student_names.get(
                            student.id,
                            "Unknown",
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
        team["score"] for team in team_results
    )

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
