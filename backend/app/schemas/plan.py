from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import date, datetime
from uuid import UUID

class IntervalBlock(BaseModel):
    type: str # "warmup" | "active" | "recovery" | "cooldown"
    duration_seconds: int
    target_power_pct: int
    title: Optional[str] = None

class WorkoutBase(BaseModel):
    date: date
    title: str
    tss_target: int
    intervals_json: List[Dict[str, Any]]
    status: str = "scheduled"

class WorkoutResponse(WorkoutBase):
    id: UUID
    plan_id: UUID

    class Config:
        from_attributes = True

class PlanCreate(BaseModel):
    duration_weeks: int # 8 | 12 | 16
    methodology: str # "polarized" | "sweet_spot" | "traditional"
    start_date: date

class PlanResponse(BaseModel):
    id: UUID
    user_id: UUID
    duration_weeks: int
    methodology: str
    status: str
    start_date: date
    created_at: datetime

    class Config:
        from_attributes = True

class PlanRecommendationRequest(BaseModel):
    primary_goal: str # "ftp_improvement" | "endurance" | "event" | "general_fitness"
    weekly_frequency_days: int
    hours_available_weekly: float
    event_date: Optional[date] = None

class PlanRecommendationResponse(BaseModel):
    duration_weeks: int
    methodology: str
    reasoning: str
