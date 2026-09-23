from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from datetime import datetime

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(100), nullable=False)

    email = Column(
        String(255),
        unique=True,
        index=True,
        nullable=False
    )

    password_hash = Column(
        String(255),
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


class Interview(Base):
    __tablename__ = "interviews"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    job_title = Column(
        String(200),
        nullable=False
    )

    job_description = Column(
        Text,
        nullable=False
    )

    resume_filename = Column(
        String(255),
        nullable=False
    )

    resume_text = Column(
        Text,
        nullable=True
    )

    status = Column(
        String(50),
        default="created"
    )

    overall_score = Column(
        Integer,
        nullable=True
    )

    started_at = Column(
        DateTime,
        nullable=True
    )

    completed_at = Column(
        DateTime,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )
class InterviewQuestion(Base):
    __tablename__ = "interview_questions"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    interview_id = Column(
        Integer,
        ForeignKey("interviews.id"),
        nullable=False
    )

    question_number = Column(
        Integer,
        nullable=False
    )

    question_text = Column(
        Text,
        nullable=False
    )

    answer_text = Column(
        Text,
        nullable=True
    )

    score = Column(
        Integer,
        nullable=True
    )

    feedback = Column(
        Text,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )
class InterviewEvaluation(Base):
    __tablename__ = "interview_evaluations"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    interview_id = Column(
        Integer,
        ForeignKey("interviews.id"),
        nullable=False,
        unique=True
    )

    overall_score = Column(
        Integer,
        nullable=False
    )

    technical_score = Column(
        Integer,
        nullable=False
    )

    communication_score = Column(
        Integer,
        nullable=False
    )

    problem_solving_score = Column(
        Integer,
        nullable=False
    )

    relevance_score = Column(
        Integer,
        nullable=False
    )

    strengths = Column(
        Text,
        nullable=False
    )

    weaknesses = Column(
        Text,
        nullable=False
    )

    recommendations = Column(
        Text,
        nullable=False
    )

    summary = Column(
        Text,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )