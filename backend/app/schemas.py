from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field


class GoalCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    description: str = Field(default="", max_length=2000)
    target_date: Optional[date] = None
    priority: int = Field(default=3, ge=1, le=5)
    weekly_hours_target: float = Field(default=2.0, gt=0, le=40)


class GoalRead(BaseModel):
    id: int
    title: str
    description: str
    target_date: Optional[date]
    priority: int
    weekly_hours_target: float
    created_at: datetime

    model_config = {"from_attributes": True}


class GeneratePlanRequest(BaseModel):
    available_hours: float = Field(..., gt=0, le=80)
    week_start: Optional[date] = None


class StudySessionRead(BaseModel):
    id: int
    goal_id: int
    goal_title: str
    day_of_week: int
    title: str
    duration_minutes: int
    notes: str


class StudyPlanRead(BaseModel):
    id: int
    week_start: date
    available_hours: float
    generated_at: datetime
    sessions: list[StudySessionRead]


class DayPlan(BaseModel):
    day_of_week: int
    sessions: list[StudySessionRead]
    total_minutes: int


class WeeklyPlanView(BaseModel):
    plan: StudyPlanRead
    days: list[DayPlan]
