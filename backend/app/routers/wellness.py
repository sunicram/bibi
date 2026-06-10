from datetime import date, datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.db import get_db
from app.routers.auth import get_current_user
from app.models.user import User
from app.models.plan import WellnessDaily
from app.schemas.wellness import WellnessCreate, WellnessResponse
from app.ml.wellness import compute_daily_wellness_metrics

router = APIRouter(prefix="/wellness", tags=["wellness"])

@router.post("/", response_model=WellnessResponse, status_code=status.HTTP_201_CREATED)
def submit_wellness(
    wellness_in: WellnessCreate, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    profile = current_user.profile
    if not profile:
        raise HTTPException(status_code=400, detail="User profile must be initialized first")

    # Fetch past 7 days of wellness data to compute baselines
    past_dates = [wellness_in.date - timedelta(days=i) for i in range(1, 8)]
    past_records = db.query(WellnessDaily).filter(
        WellnessDaily.user_id == current_user.id,
        WellnessDaily.date.in_(past_dates)
    ).all()
    
    past_hrv = [r.hrv_rmssd for r in past_records if r.hrv_rmssd is not None]
    past_rhr = [r.resting_hr for r in past_records if r.resting_hr is not None]
    past_sleep = [r.sleep_minutes for r in past_records if r.sleep_minutes is not None][:3]
    
    # Compute metrics using ML logic
    metrics = compute_daily_wellness_metrics(
        today_hrv=wellness_in.hrv_rmssd,
        today_rhr=wellness_in.resting_hr,
        today_sleep=wellness_in.sleep_minutes,
        past_7d_hrv=past_hrv,
        past_7d_rhr=past_rhr,
        past_3d_sleep=past_sleep,
        target_sleep_minutes=540 # Default 9 hours, could be profile parameter
    )
    
    # Check if a record already exists for this date, overwrite if so
    db_wellness = db.query(WellnessDaily).filter(
        WellnessDaily.user_id == current_user.id,
        WellnessDaily.date == wellness_in.date
    ).first()
    
    if db_wellness:
        db_wellness.device_source = wellness_in.device_source
        db_wellness.hrv_rmssd = wellness_in.hrv_rmssd
        db_wellness.resting_hr = wellness_in.resting_hr
        db_wellness.sleep_minutes = wellness_in.sleep_minutes
        db_wellness.body_battery = wellness_in.body_battery
        db_wellness.hrv_z_score = metrics["hrv_z_score"]
        db_wellness.rhr_z_score = metrics["rhr_z_score"]
        db_wellness.sleep_debt_minutes = metrics["sleep_debt_minutes"]
        db_wellness.readiness_tier = metrics["readiness_tier"]
        db_wellness.updated_at = datetime.utcnow()
    else:
        db_wellness = WellnessDaily(
            user_id=current_user.id,
            date=wellness_in.date,
            device_source=wellness_in.device_source,
            hrv_rmssd=wellness_in.hrv_rmssd,
            resting_hr=wellness_in.resting_hr,
            sleep_minutes=wellness_in.sleep_minutes,
            body_battery=wellness_in.body_battery,
            hrv_z_score=metrics["hrv_z_score"],
            rhr_z_score=metrics["rhr_z_score"],
            sleep_debt_minutes=metrics["sleep_debt_minutes"],
            readiness_tier=metrics["readiness_tier"],
            data_quality_flag="measured"
        )
        db.add(db_wellness)
        
    db.commit()
    db.refresh(db_wellness)
    return db_wellness

@router.get("/", response_model=List[WellnessResponse])
def get_wellness_history(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(WellnessDaily).filter(WellnessDaily.user_id == current_user.id).order_by(WellnessDaily.date.desc()).all()

@router.get("/today", response_model=WellnessResponse)
def get_today_readiness(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    today_rec = db.query(WellnessDaily).filter(
        WellnessDaily.user_id == current_user.id,
        WellnessDaily.date == date.today()
    ).first()
    
    if not today_rec:
        # Gracefully degrade by providing a default neutral/green state if not logged yet
        return {
            "user_id": current_user.id,
            "date": date.today(),
            "device_source": "none",
            "readiness_tier": "green",
            "data_quality_flag": "missing"
        }
    return today_rec
