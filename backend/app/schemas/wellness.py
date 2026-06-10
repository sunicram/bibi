from pydantic import BaseModel
from typing import Optional
from datetime import date
from uuid import UUID

class WellnessCreate(BaseModel):
    date: date
    device_source: str # "garmin" | "apple_health" | "intervals.icu"
    hrv_rmssd: Optional[float] = None
    resting_hr: Optional[int] = None
    sleep_minutes: Optional[int] = None
    body_battery: Optional[int] = None

class WellnessResponse(BaseModel):
    user_id: UUID
    date: date
    device_source: str
    hrv_rmssd: Optional[float] = None
    resting_hr: Optional[int] = None
    sleep_minutes: Optional[int] = None
    body_battery: Optional[int] = None
    hrv_z_score: Optional[float] = None
    rhr_z_score: Optional[float] = None
    sleep_debt_minutes: Optional[int] = None
    readiness_tier: str
    data_quality_flag: str

    class Config:
        from_attributes = True
