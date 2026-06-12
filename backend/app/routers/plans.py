from datetime import date, datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from pydantic import BaseModel
import math

from typing import List, Optional
from app.core.db import get_db
from app.routers.auth import get_current_user
from app.models.user import User
from app.models.plan import Plan, Workout, PlanVersion
from app.schemas.plan import PlanCreate, PlanResponse, PlanRecommendationRequest, PlanRecommendationResponse, WorkoutResponse

router = APIRouter(prefix="/plans", tags=["plans"])

def build_polarized_week(start_date: date, week_num: int, is_recovery: bool) -> list[dict]:
    # Polarized 80/20 setup. If recovery week, all Z1/Z2.
    # Standard: Tue (VO2Max), Wed (Recovery), Thu (Z2), Sat (Long Z2), Sun (Z2)
    workouts = []
    
    if is_recovery:
        # Recovery week
        workouts.append({"day_offset": 1, "title": "Recovery Spin (Z1)", "tss": 30, "intervals": [
            {"type": "warmup", "duration_seconds": 600, "target_power_pct": 50},
            {"type": "active", "duration_seconds": 1800, "target_power_pct": 55},
            {"type": "cooldown", "duration_seconds": 600, "target_power_pct": 50}
        ]})
        workouts.append({"day_offset": 3, "title": "Easy Endurance (Z2)", "tss": 50, "intervals": [
            {"type": "warmup", "duration_seconds": 600, "target_power_pct": 55},
            {"type": "active", "duration_seconds": 3600, "target_power_pct": 65},
            {"type": "cooldown", "duration_seconds": 600, "target_power_pct": 55}
        ]})
        workouts.append({"day_offset": 5, "title": "Weekend Active Roll (Z2)", "tss": 60, "intervals": [
            {"type": "active", "duration_seconds": 5400, "target_power_pct": 60}
        ]})
    else:
        # High Intensity week
        workouts.append({"day_offset": 1, "title": "VO2 Max Intervals: 4x4 min", "tss": 80, "intervals": [
            {"type": "warmup", "duration_seconds": 900, "target_power_pct": 60},
            {"type": "active", "duration_seconds": 240, "target_power_pct": 115, "title": "Rep 1"},
            {"type": "recovery", "duration_seconds": 240, "target_power_pct": 50},
            {"type": "active", "duration_seconds": 240, "target_power_pct": 115, "title": "Rep 2"},
            {"type": "recovery", "duration_seconds": 240, "target_power_pct": 50},
            {"type": "active", "duration_seconds": 240, "target_power_pct": 115, "title": "Rep 3"},
            {"type": "recovery", "duration_seconds": 240, "target_power_pct": 50},
            {"type": "active", "duration_seconds": 240, "target_power_pct": 115, "title": "Rep 4"},
            {"type": "cooldown", "duration_seconds": 600, "target_power_pct": 55}
        ]})
        workouts.append({"day_offset": 2, "title": "Active Recovery (Z1)", "tss": 35, "intervals": [
            {"type": "active", "duration_seconds": 2700, "target_power_pct": 50}
        ]})
        workouts.append({"day_offset": 3, "title": "Base Endurance (Z2)", "tss": 75, "intervals": [
            {"type": "warmup", "duration_seconds": 600, "target_power_pct": 55},
            {"type": "active", "duration_seconds": 5400, "target_power_pct": 70},
            {"type": "cooldown", "duration_seconds": 600, "target_power_pct": 55}
        ]})
        workouts.append({"day_offset": 5, "title": "Long Endurance Ride (Z2)", "tss": 130, "intervals": [
            {"type": "active", "duration_seconds": 10800, "target_power_pct": 65}
        ]})
        workouts.append({"day_offset": 6, "title": "Aerobic Maintenance (Z2)", "tss": 90, "intervals": [
            {"type": "active", "duration_seconds": 7200, "target_power_pct": 65}
        ]})
        
    return workouts

def build_sweetspot_week(start_date: date, week_num: int, is_recovery: bool) -> list[dict]:
    # Sweet Spot Week: Tue (SS), Thu (SS), Sat (Long SS), Sun (Z2)
    workouts = []
    if is_recovery:
        workouts.append({"day_offset": 1, "title": "Recovery Flush (Z1)", "tss": 30, "intervals": [
            {"type": "active", "duration_seconds": 1800, "target_power_pct": 50}
        ]})
        workouts.append({"day_offset": 5, "title": "Endurance Spin (Z2)", "tss": 65, "intervals": [
            {"type": "active", "duration_seconds": 5400, "target_power_pct": 65}
        ]})
    else:
        workouts.append({"day_offset": 1, "title": "Sweet Spot: 3x10 min at 90%", "tss": 85, "intervals": [
            {"type": "warmup", "duration_seconds": 600, "target_power_pct": 60},
            {"type": "active", "duration_seconds": 600, "target_power_pct": 90, "title": "SST Block 1"},
            {"type": "recovery", "duration_seconds": 300, "target_power_pct": 50},
            {"type": "active", "duration_seconds": 600, "target_power_pct": 90, "title": "SST Block 2"},
            {"type": "recovery", "duration_seconds": 300, "target_power_pct": 50},
            {"type": "active", "duration_seconds": 600, "target_power_pct": 90, "title": "SST Block 3"},
            {"type": "cooldown", "duration_seconds": 600, "target_power_pct": 55}
        ]})
        workouts.append({"day_offset": 3, "title": "Sweet Spot: 2x15 min at 90%", "tss": 90, "intervals": [
            {"type": "warmup", "duration_seconds": 600, "target_power_pct": 60},
            {"type": "active", "duration_seconds": 900, "target_power_pct": 90, "title": "SST Block 1"},
            {"type": "recovery", "duration_seconds": 300, "target_power_pct": 50},
            {"type": "active", "duration_seconds": 900, "target_power_pct": 90, "title": "SST Block 2"},
            {"type": "cooldown", "duration_seconds": 600, "target_power_pct": 55}
        ]})
        workouts.append({"day_offset": 5, "title": "Weekend SST Progressions", "tss": 140, "intervals": [
            {"type": "warmup", "duration_seconds": 900, "target_power_pct": 60},
            {"type": "active", "duration_seconds": 1800, "target_power_pct": 88, "title": "Tempo SST"},
            {"type": "recovery", "duration_seconds": 600, "target_power_pct": 55},
            {"type": "active", "duration_seconds": 1800, "target_power_pct": 90, "title": "Sweet Spot Target"},
            {"type": "cooldown", "duration_seconds": 900, "target_power_pct": 55}
        ]})
        workouts.append({"day_offset": 6, "title": "Aerobic Endurance (Z2)", "tss": 80, "intervals": [
            {"type": "active", "duration_seconds": 5400, "target_power_pct": 65}
        ]})
        
    return workouts

def build_traditional_week(start_date: date, week_num: int, is_recovery: bool) -> list[dict]:
    # Traditional: Tue (Tempo/Z3), Thu (Endurance/Z2), Sat (Threshold/Z4 or Long Z2), Sun (Z2)
    workouts = []
    if is_recovery:
        workouts.append({"day_offset": 1, "title": "Recovery Ride (Z1)", "tss": 35, "intervals": [
            {"type": "active", "duration_seconds": 2400, "target_power_pct": 50}
        ]})
        workouts.append({"day_offset": 5, "title": "Endurance Spin (Z2)", "tss": 60, "intervals": [
            {"type": "active", "duration_seconds": 5400, "target_power_pct": 60}
        ]})
    else:
        workouts.append({"day_offset": 1, "title": "Tempo Intervals: 3x12 min Z3", "tss": 80, "intervals": [
            {"type": "warmup", "duration_seconds": 600, "target_power_pct": 60},
            {"type": "active", "duration_seconds": 720, "target_power_pct": 80},
            {"type": "recovery", "duration_seconds": 180, "target_power_pct": 55},
            {"type": "active", "duration_seconds": 720, "target_power_pct": 80},
            {"type": "recovery", "duration_seconds": 180, "target_power_pct": 55},
            {"type": "active", "duration_seconds": 720, "target_power_pct": 80},
            {"type": "cooldown", "duration_seconds": 600, "target_power_pct": 55}
        ]})
        workouts.append({"day_offset": 3, "title": "Aerobic Base (Z2)", "tss": 70, "intervals": [
            {"type": "active", "duration_seconds": 5400, "target_power_pct": 65}
        ]})
        workouts.append({"day_offset": 5, "title": "Threshold Efforts: 2x10 min Z4", "tss": 95, "intervals": [
            {"type": "warmup", "duration_seconds": 900, "target_power_pct": 60},
            {"type": "active", "duration_seconds": 600, "target_power_pct": 100},
            {"type": "recovery", "duration_seconds": 300, "target_power_pct": 50},
            {"type": "active", "duration_seconds": 600, "target_power_pct": 100},
            {"type": "cooldown", "duration_seconds": 900, "target_power_pct": 55}
        ]})
        workouts.append({"day_offset": 6, "title": "Long Endurance Ride (Z2)", "tss": 120, "intervals": [
            {"type": "active", "duration_seconds": 9000, "target_power_pct": 65}
        ]})
    return workouts

def generate_workouts_for_plan(plan: Plan, db: Session):
    start_date = plan.start_date
    weeks = plan.duration_weeks
    methodology = plan.methodology
    
    # 8, 12, 16 week configurations. Identify recovery weeks
    # 8 weeks: recovery is week 4, week 8 (taper)
    # 12 weeks: recovery is week 4, week 8, week 12 (taper)
    # 16 weeks: recovery is week 4, week 8, week 12, week 16 (taper)
    recovery_weeks = [4, 8, 12, 16]
    
    for w in range(1, weeks + 1):
        is_rec = w in recovery_weeks
        week_start_date = start_date + timedelta(weeks=w-1)
        
        # Determine week builder
        if methodology == "polarized":
            week_workouts = build_polarized_week(week_start_date, w, is_rec)
        elif methodology == "sweet_spot":
            week_workouts = build_sweetspot_week(week_start_date, w, is_rec)
        else:
            week_workouts = build_traditional_week(week_start_date, w, is_rec)
            
        for wo in week_workouts:
            workout_date = week_start_date + timedelta(days=wo["day_offset"])
            
            # FTP test protocol check:
            # First week first active workout (after adaptation) or last week last workout
            workout_title = wo["title"]
            intervals = wo["intervals"]
            
            # Inject FTP tests for start/end
            if w == 1 and wo["day_offset"] == 1:
                workout_title = "Ramp FTP Test Protocol"
                intervals = [
                    {"type": "warmup", "duration_seconds": 600, "target_power_pct": 50},
                    {"type": "active", "duration_seconds": 600, "target_power_pct": 100, "title": "Ramp Ascent"},
                    {"type": "cooldown", "duration_seconds": 300, "target_power_pct": 45}
                ]
            elif w == weeks and wo["day_offset"] == 5 and not is_rec:
                workout_title = "20-Min FTP Test Protocol"
                intervals = [
                    {"type": "warmup", "duration_seconds": 900, "target_power_pct": 60},
                    {"type": "active", "duration_seconds": 1200, "target_power_pct": 105, "title": "20-Min Max Test"},
                    {"type": "cooldown", "duration_seconds": 600, "target_power_pct": 50}
                ]
                
            db_workout = Workout(
                plan_id=plan.id,
                date=workout_date,
                title=workout_title,
                tss_target=wo["tss"],
                intervals_json=intervals,
                status="scheduled"
            )
            db.add(db_workout)
            
    db.commit()

@router.post("/recommend", response_model=PlanRecommendationResponse)
def recommend_plan(req: PlanRecommendationRequest):
    # Propose duration and methodology based on inputs
    reasoning = ""
    duration = 12
    methodology = "traditional"
    
    if req.primary_goal == "ftp_improvement":
        if req.hours_available_weekly < 6:
            methodology = "sweet_spot"
            reasoning = "Sweet Spot Training (SST) maximizes training stress per unit of time. Best for time-crunched athletes under 6 hours/week wanting to improve FTP."
        else:
            methodology = "polarized"
            reasoning = "Polarized (80/20) training produces superior cellular adaptation by focusing heavily on aerobic building (Z1-Z2) and strict high intensity (Z5-Z6). Ideal for athletes with 6+ hours/week."
    elif req.primary_goal == "endurance":
        methodology = "traditional"
        reasoning = "Traditional Periodization starts with base building, gradually adding aerobic density. Best for endurance goals and building a solid aerobic engine safely."
    else:
        methodology = "traditional"
        reasoning = "Traditional progression provides a balanced base -> build -> peak transition, which minimizes injury risk and builds robust, general fitness."
        
    if req.event_date:
        days_to_event = (req.event_date - date.today()).days
        weeks_to_event = days_to_event // 7
        if weeks_to_event <= 9:
            duration = 8
        elif weeks_to_event <= 14:
            duration = 12
        else:
            duration = 16
        reasoning += f" Adjusted duration to {duration} weeks based on event date ({req.event_date})."
    else:
        duration = 12 # standard default
        
    return {
        "duration_weeks": duration,
        "methodology": methodology,
        "reasoning": reasoning
    }

@router.post("/generate", response_model=PlanResponse)
def generate_plan(plan_in: PlanCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Archive any existing active plans first
    active_plans = db.query(Plan).filter(Plan.user_id == current_user.id, Plan.status == "active").all()
    for p in active_plans:
        p.status = "archived"
        p.updated_at = datetime.utcnow()
        
    # Generate new plan
    db_plan = Plan(
        user_id=current_user.id,
        duration_weeks=plan_in.duration_weeks,
        methodology=plan_in.methodology,
        status="active",
        start_date=plan_in.start_date
    )
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)
    
    # Write initial plan version (version 1)
    db_version = PlanVersion(
        plan_id=db_plan.id,
        version=1,
        created_at=datetime.utcnow()
    )
    db.add(db_version)
    db.commit()
    
    # Generate workouts and append to database
    generate_workouts_for_plan(db_plan, db)
    
    return db_plan

@router.get("/active", response_model=PlanResponse)
def get_active_plan(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    plan = db.query(Plan).filter(Plan.user_id == current_user.id, Plan.status == "active").first()
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No active training plan found.")
    return plan

@router.get("/active/workouts", response_model=List[WorkoutResponse])
def get_active_workouts(
    start: Optional[date] = None,
    end: Optional[date] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    plan = db.query(Plan).filter(Plan.user_id == current_user.id, Plan.status == "active").first()
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No active training plan found.")
        
    query = db.query(Workout).filter(Workout.plan_id == plan.id)
    if start:
        query = query.filter(Workout.date >= start)
    if end:
        query = query.filter(Workout.date <= end)
        
    return query.order_by(Workout.date).all()

class IllnessReportRequest(BaseModel):
    start_date: date
    end_date: date

@router.post("/active/reschedule", status_code=status.HTTP_200_OK)
def reschedule_week(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    plan = db.query(Plan).filter(Plan.user_id == current_user.id, Plan.status == "active").first()
    if not plan:
        raise HTTPException(status_code=404, detail="No active plan found")
        
    today = date.today()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    
    # Get all workouts for this week
    workouts = db.query(Workout).filter(
        Workout.plan_id == plan.id,
        Workout.date >= start_of_week,
        Workout.date <= end_of_week
    ).all()
    
    if not workouts:
        return {"status": "no_workouts", "message": "No workouts scheduled for the current week."}
        
    # Categorize workouts
    missed = []
    upcoming = []
    completed_or_skipped = []
    
    for wo in workouts:
        if wo.status in ["completed", "skipped", "missed"]:
            completed_or_skipped.append(wo)
        elif wo.date < today:
            missed.append(wo)
        else:
            upcoming.append(wo)
            
    if not missed:
        return {"status": "no_change", "message": "No missed workouts to reschedule."}
        
    # Workouts that need to be scheduled from today to Sunday
    to_schedule = missed + upcoming
    remaining_days = (end_of_week - today).days + 1
    
    # Calculate WS for each and sort
    from app.ml.metrics import calculate_workout_stimulus_score
    
    scored_workouts = []
    for wo in to_schedule:
        ws = calculate_workout_stimulus_score(wo.intervals_json, wo.tss_target)
        is_long = "long" in wo.title.lower() or "długa" in wo.title.lower() or "baza" in wo.title.lower() or "weekend" in wo.title.lower()
        scored_workouts.append((wo, ws, is_long))
        
    # Sort: is_long (Priority 1) first, then WS (Priority 2) desc
    # Priority 3 (rest) has lower WS and is_long = False
    scored_workouts.sort(key=lambda x: (x[2], x[1]), reverse=True)
    
    kept = []
    discarded = []
    
    if len(to_schedule) > remaining_days:
        kept = [x[0] for x in scored_workouts[:remaining_days]]
        discarded = [x[0] for x in scored_workouts[remaining_days:]]
    else:
        kept = [x[0] for x in to_schedule]
        
    # Update discarded status to skipped
    for wo in discarded:
        wo.status = "skipped"
        wo.updated_at = datetime.utcnow()
        
    # Distribute kept workouts across remaining days
    # Spaced out starting from today
    step = max(1, remaining_days // len(kept)) if kept else 1
    for idx, wo in enumerate(kept):
        target_day = today + timedelta(days=idx * step)
        if target_day > end_of_week:
            target_day = end_of_week
        wo.date = target_day
        wo.updated_at = datetime.utcnow()
        
    # Record Plan Version
    latest_version = db.query(PlanVersion).filter(PlanVersion.plan_id == plan.id).order_by(PlanVersion.version.desc()).first()
    next_ver = (latest_version.version + 1) if latest_version else 1
    
    db_version = PlanVersion(
        plan_id=plan.id,
        version=next_ver,
        created_at=datetime.utcnow()
    )
    db.add(db_version)
    db.commit()
    
    return {
        "status": "rescheduled",
        "kept_count": len(kept),
        "discarded_count": len(discarded),
        "new_version": next_ver
    }

@router.post("/active/report-illness", status_code=status.HTTP_200_OK)
def report_illness(req: IllnessReportRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    plan = db.query(Plan).filter(Plan.user_id == current_user.id, Plan.status == "active").first()
    if not plan:
        raise HTTPException(status_code=404, detail="No active plan found")
        
    # 1. Calculate illness parameters
    duration_days = (req.end_date - req.start_date).days + 1
    recovery_days = 2 * duration_days
    recovery_end_date = req.end_date + timedelta(days=recovery_days)
    
    # 2. Mark workouts during illness as skipped
    illness_workouts = db.query(Workout).filter(
        Workout.plan_id == plan.id,
        Workout.date >= req.start_date,
        Workout.date <= req.end_date
    ).all()
    
    for wo in illness_workouts:
        wo.status = "skipped"
        wo.updated_at = datetime.utcnow()
        
    # 3. If recovery starts in the middle of the week, replace remaining workouts with easy rides
    illness_end_weekday = req.end_date.weekday()
    if illness_end_weekday < 6: # not Sunday
        remaining_sunday = req.end_date + timedelta(days=(6 - illness_end_weekday))
        post_illness_week_workouts = db.query(Workout).filter(
            Workout.plan_id == plan.id,
            Workout.date > req.end_date,
            Workout.date <= remaining_sunday
        ).all()
        
        for wo in post_illness_week_workouts:
            # Replace with easy Recovery Ride
            wo.title = "Recovery Ride (Z1) - Post-Illness"
            wo.tss_target = 30
            wo.intervals_json = [
                {"type": "warmup", "duration_seconds": 600, "target_power_pct": 50},
                {"type": "active", "duration_seconds": 1800, "target_power_pct": 55},
                {"type": "cooldown", "duration_seconds": 600, "target_power_pct": 50}
            ]
            wo.updated_at = datetime.utcnow()
            
    # 4. Shift all subsequent weeks by W_shift weeks
    # W_shift is the number of weeks the illness spanned
    illness_week_monday = req.start_date - timedelta(days=req.start_date.weekday())
    next_monday = req.end_date + timedelta(days=(7 - req.end_date.weekday()))
    
    weeks_to_shift = int(math.ceil(duration_days / 7.0))
    
    # Find workouts originally scheduled after the illness week Monday
    future_workouts = db.query(Workout).filter(
        Workout.plan_id == plan.id,
        Workout.date >= next_monday
    ).all()
    
    # Shift them forward
    for wo in future_workouts:
        wo.date = wo.date + timedelta(weeks=weeks_to_shift)
        wo.updated_at = datetime.utcnow()
        
    # 5. Recreate/Repeat the interrupted week starting at next_monday
    # We copy workouts from the interrupted week
    original_week_workouts = db.query(Workout).filter(
        Workout.plan_id == plan.id,
        Workout.date >= illness_week_monday,
        Workout.date <= illness_week_monday + timedelta(days=6)
    ).all()
    
    for wo in original_week_workouts:
        # Calculate new date
        day_offset = (wo.date - illness_week_monday).days
        new_date = next_monday + timedelta(days=day_offset)
        
        # Apply illness recovery safety limits if this day is within recovery period
        title = wo.title
        tss = wo.tss_target
        intervals = wo.intervals_json
        
        if new_date <= recovery_end_date:
            # Protocol restrictions: IF <= 0.65, Z1/Z2 only, TSS <= 40% of original
            title = f"Recovery: {wo.title}"
            tss = int(round(wo.tss_target * 0.4))
            
            # Capping target_power_pct to Z2 (max 70% or 75%)
            new_intervals = []
            for step in intervals:
                new_step = dict(step)
                orig_pct = float(step.get("target_power_pct", 100))
                if orig_pct > 75.0:
                    new_step["target_power_pct"] = 70.0 # scale VO2max/SST to Z2
                    new_step["title"] = f"Scaled: {step.get('title', 'Active')}"
                new_intervals.append(new_step)
            intervals = new_intervals
            
        db_new_wo = Workout(
            plan_id=plan.id,
            date=new_date,
            title=title,
            tss_target=tss,
            intervals_json=intervals,
            status="scheduled"
        )
        db.add(db_new_wo)
        
    # Record Plan Version
    latest_version = db.query(PlanVersion).filter(PlanVersion.plan_id == plan.id).order_by(PlanVersion.version.desc()).first()
    next_ver = (latest_version.version + 1) if latest_version else 1
    
    db_version = PlanVersion(
        plan_id=plan.id,
        version=next_ver,
        created_at=datetime.utcnow()
    )
    db.add(db_version)
    db.commit()
    
    return {
        "status": "illness_processed",
        "duration_days": duration_days,
        "recovery_until": recovery_end_date,
        "weeks_shifted": weeks_to_shift,
        "new_version": next_ver
    }

