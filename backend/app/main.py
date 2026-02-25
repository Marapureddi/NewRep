from collections import defaultdict
from datetime import date
import os

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from . import models, planner, schemas
from .database import Base, engine, get_db

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Study Planner")

default_origins = "http://localhost:5173,http://127.0.0.1:5173"
cors_origins = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", default_origins).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/goals", response_model=schemas.GoalRead)
def create_goal(payload: schemas.GoalCreate, db: Session = Depends(get_db)):
    goal = models.Goal(**payload.model_dump())
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return goal


@app.get("/goals", response_model=list[schemas.GoalRead])
def list_goals(db: Session = Depends(get_db)):
    return db.query(models.Goal).order_by(models.Goal.created_at.desc()).all()


@app.post("/plans/generate", response_model=schemas.WeeklyPlanView)
def generate_plan(payload: schemas.GeneratePlanRequest, db: Session = Depends(get_db)):
    goals = db.query(models.Goal).all()
    if not goals:
        raise HTTPException(status_code=400, detail="Add at least one goal before generating a plan.")

    normalized_week = planner.normalize_week_start(payload.week_start)

    plan = models.StudyPlan(week_start=normalized_week, available_hours=payload.available_hours)
    db.add(plan)
    db.flush()

    sessions = planner.generate_sessions(
        [
            planner.GoalInput(
                id=g.id,
                title=g.title,
                priority=g.priority,
                weekly_hours_target=g.weekly_hours_target,
            )
            for g in goals
        ],
        payload.available_hours,
    )

    for session in sessions:
        db.add(
            models.StudySession(
                plan_id=plan.id,
                goal_id=session.goal_id,
                day_of_week=session.day_of_week,
                title=session.title,
                duration_minutes=session.duration_minutes,
                notes=session.notes,
            )
        )

    db.commit()
    db.refresh(plan)

    response_sessions: list[schemas.StudySessionRead] = []
    for session in plan.sessions:
        response_sessions.append(
            schemas.StudySessionRead(
                id=session.id,
                goal_id=session.goal_id,
                goal_title=session.goal.title,
                day_of_week=session.day_of_week,
                title=session.title,
                duration_minutes=session.duration_minutes,
                notes=session.notes,
            )
        )

    grouped = defaultdict(list)
    totals = defaultdict(int)
    for session in response_sessions:
        grouped[session.day_of_week].append(session)
        totals[session.day_of_week] += session.duration_minutes

    days = [
        schemas.DayPlan(
            day_of_week=d,
            sessions=sorted(grouped[d], key=lambda s: s.goal_title.lower()),
            total_minutes=totals[d],
        )
        for d in range(7)
    ]

    return schemas.WeeklyPlanView(
        plan=schemas.StudyPlanRead(
            id=plan.id,
            week_start=plan.week_start,
            available_hours=plan.available_hours,
            generated_at=plan.generated_at,
            sessions=response_sessions,
        ),
        days=days,
    )
