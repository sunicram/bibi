from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime
from uuid import UUID

class ActivityTelemetryResponse(BaseModel):
    timestamp: datetime
    power: int
    heart_rate: int
    cadence: int
    speed: float
    altitude: float
    wbal: int

    class Config:
        from_attributes = True

class ActivityResponse(BaseModel):
    id: UUID
    workout_id: Optional[UUID] = None
    user_id: UUID
    external_icu_id: Optional[str] = None
    external_strava_id: Optional[str] = None
    date: date
    duration_seconds: int
    tss: int
    intensity_factor: float
    normalized_power: float
    avg_power: float
    avg_hr: float
    aerobic_decoupling: Optional[float] = None
    wbal_depleted_flag: bool
    adherence_score: float
    created_at: datetime

    class Config:
        from_attributes = True
