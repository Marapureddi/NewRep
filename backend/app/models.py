from datetime import datetime
from typing import Optional

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class Goal(Base):
    __tablename__ = "goals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    target_date: Mapped[Optional[Date]] = mapped_column(Date, nullable=True)
    priority: Mapped[int] = mapped_column(Integer, default=3)
    weekly_hours_target: Mapped[float] = mapped_column(Float, default=2.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    sessions: Mapped[list["StudySession"]] = relationship("StudySession", back_populates="goal")


class StudyPlan(Base):
    __tablename__ = "study_plans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    week_start: Mapped[Date] = mapped_column(Date, nullable=False)
    available_hours: Mapped[float] = mapped_column(Float, nullable=False)
    generated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    sessions: Mapped[list["StudySession"]] = relationship(
        "StudySession", back_populates="plan", cascade="all, delete-orphan"
    )


class StudySession(Base):
    __tablename__ = "study_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    plan_id: Mapped[int] = mapped_column(ForeignKey("study_plans.id"), nullable=False)
    goal_id: Mapped[int] = mapped_column(ForeignKey("goals.id"), nullable=False)
    day_of_week: Mapped[int] = mapped_column(Integer, nullable=False)  # 0 = Monday
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    notes: Mapped[str] = mapped_column(Text, default="")

    plan: Mapped[StudyPlan] = relationship("StudyPlan", back_populates="sessions")
    goal: Mapped[Goal] = relationship("Goal", back_populates="sessions")
