from sqlalchemy import Column, Float, ForeignKey, Integer, String, JSON
from sqlalchemy.orm import relationship

from app.db import Base


class Hackathon(Base):
    __tablename__ = "hackathons"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    team_size = Column(Integer, nullable=False)
    requirements = Column(JSON, nullable=False)

    students = relationship(
        "StudentRow",
        back_populates="hackathon",
        cascade="all, delete-orphan",
    )


class StudentRow(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True)
    hackathon_id = Column(
        Integer,
        ForeignKey("hackathons.id"),
        nullable=False,
    )

    name = Column(String, nullable=False)
    skills = Column(JSON, nullable=False)
    slots = Column(JSON, nullable=False)
    role = Column(String, nullable=False)
    avoid = Column(JSON, nullable=False)

    hackathon = relationship(
        "Hackathon",
        back_populates="students",
    )


class TeamRun(Base):
    __tablename__ = "team_runs"

    id = Column(Integer, primary_key=True)
    hackathon_id = Column(
        Integer,
        ForeignKey("hackathons.id"),
        nullable=False,
    )

    coverage = Column(Float, nullable=False)
    seconds = Column(Float, nullable=False)
    result = Column(JSON, nullable=False)