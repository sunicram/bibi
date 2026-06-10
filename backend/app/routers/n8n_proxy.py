import json
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from uuid import UUID

from datetime import date, datetime, timedelta
from app.core.db import get_db
from app.core.config import settings
from app.routers.auth import get_current_user
from app.models.user import User
from app.models.plan import Plan, Workout, Activity, WellnessDaily, DecisionObject, PlanVersion
from app.ml.policy import PolicyEngine

# Import LiteLLM safely
try:
    from litellm import completion
except ImportError:
    completion = None

router = APIRouter(prefix="/n8n", tags=["n8n"])
logger = logging.getLogger("uvicorn.error")

class ChatRequest(BaseModel):
    user_id: UUID
    message: str

class WorkoutSummaryRequest(BaseModel):
    activity_id: UUID

class AmendmentRequest(BaseModel):
    user_id: UUID
    trigger_type: str # "wellness_red" | "workout_failed" | "missed_session"

# Helper function to call LLM using LiteLLM
def call_llm(model: str, system_prompt: str, user_prompt: str, json_mode: bool = False) -> str:
    if not completion:
        return "LiteLLM is not installed. AI features disabled."
    
    # Map model keys to providers if needed. LiteLLM handles gpt-4o-mini and claude-3-5-sonnet natively
    # If keys are missing, mock responses to prevent crash.
    api_key = settings.OPENAI_API_KEY if "gpt" in model else settings.ANTHROPIC_API_KEY
    if api_key == "dummy_openai_key" or api_key == "dummy_anthropic_key":
        # Mock responses for local testing
        if json_mode:
            return json.dumps({
                "decision": "approve",
                "rationale": "Mock safety confirmation. Looks good.",
                "explanation": "Mock adjustment applied.",
                "modified_intervals": []
            })
        return "This is a mock response from the Coach bot. Set up API keys in your .env file to enable actual AI coaching!"

    try:
        response_format = {"type": "json_object"} if json_mode else None
        
        response = completion(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format=response_format
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"LLM call failed: {str(e)}")
        if json_mode:
            return json.dumps({"decision": "reject", "rationale": f"LLM error: {str(e)}", "explanation": "Fallback rejection due to AI timeout."})
        return "Sorry, I encountered a temporary error analyzing your data. Please try again shortly."

@router.post("/workout-summary")
def generate_workout_summary(req: WorkoutSummaryRequest, db: Session = Depends(get_db)):
    activity = db.query(Activity).filter(Activity.id == req.activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
        
    user = db.query(User).filter(User.id == activity.user_id).first()
    profile = user.profile if user else None
    
    # Context gathering
    power_stats = f"Avg Power: {activity.avg_power:.1f}W, NP: {activity.normalized_power:.1f}W, IF: {activity.intensity_factor:.2f}"
    tss_stats = f"TSS: {activity.tss} (Adherence: {activity.adherence_score:.1f}%)"
    hr_stats = f"Avg HR: {activity.avg_hr:.1f}BPM"
    decoupling_stats = f"Aerobic Decoupling: {activity.aerobic_decoupling:.2f}%" if activity.aerobic_decoupling else "Decoupling: N/A"
    
    user_context = f"Athlete FTP: {profile.ftp if profile else 200}W, Weight: {profile.weight_kg if profile else 75}kg"
    
    system_prompt = (
        "You are Bibi, a premium, supportive AI cycling coach. Analyze the completed ride metrics "
        "and explain them in plain, encouraging language. Focus on TSS, decoupling, and zone time. "
        "Keep it concise, maximum 3 short paragraphs. No markdown bolding overkill."
    )
    
    user_prompt = f"Athlete Stats:\n{user_context}\n\nActivity Metrics:\n{power_stats}\n{hr_stats}\n{tss_stats}\n{decoupling_stats}"
    
    summary = call_llm(settings.COACH_MODEL, system_prompt, user_prompt)
    return {"summary": summary}

@router.post("/coaching-chat")
def chat_with_coach(req: ChatRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == req.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    # Gather recent workouts & activity context (past 7 days)
    recent_activities = db.query(Activity).filter(
        Activity.user_id == req.user_id,
        Activity.date >= date.today() - timedelta(days=7)
    ).all()
    
    activity_log = "\n".join([f"- Date: {a.date}, TSS: {a.tss}, Avg Power: {a.avg_power:.1f}W, NP: {a.normalized_power:.1f}W" for a in recent_activities])
    
    system_prompt = (
        "You are Bibi, an autonomous AI cycling coach. Answer the athlete's questions using their recent ride data. "
        "Be encouraging, knowledgeable about cycling physiology (TSS, FTP, base, recovery), and keep answers concise. "
        "Never make up physical metrics. If asked about plan edits, tell them you will draft a proposal."
    )
    
    user_prompt = f"Athlete Recent Activity Log:\n{activity_log}\n\nAthlete Message: {req.message}"
    
    reply = call_llm(settings.COACH_MODEL, system_prompt, user_prompt)
    return {"reply": reply}

@router.post("/amendment-proposal")
def propose_and_validate_amendment(req: AmendmentRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == req.user_id).first()
    plan = db.query(Plan).filter(Plan.user_id == req.user_id, Plan.status == "active").first()
    
    if not user or not plan:
        raise HTTPException(status_code=404, detail="Active plan not found for user")
        
    profile = user.profile
    
    # 1. Trigger Policy Engine on Wellness Tier
    readiness = "green"
    hrv_z, rhr_z = 0.0, 0.0
    
    if req.trigger_type == "wellness_red":
        today_wellness = db.query(WellnessDaily).filter(
            WellnessDaily.user_id == req.user_id,
            WellnessDaily.date == date.today()
        ).first()
        if today_wellness:
            readiness = today_wellness.readiness_tier
            hrv_z = today_wellness.hrv_z_score or 0.0
            rhr_z = today_wellness.rhr_z_score or 0.0
            
    # Load upcoming workout (tomorrow/next session)
    next_workout = db.query(Workout).filter(
        Workout.plan_id == plan.id,
        Workout.date >= date.today(),
        Workout.status == "scheduled"
    ).order_by(Workout.date).first()
    
    if not next_workout:
        return {"verdict": "no_workouts", "explanation": "No upcoming scheduled workouts to amend."}
        
    # Enforce deterministic policy engine safety rules on upcoming workouts
    modified_intervals, triggered_policies, policy_explanation = PolicyEngine.enforce_readiness_rules(
        readiness, next_workout.intervals_json, hrv_z, rhr_z
    )
    
    # If no policies triggered, and it's a simple review, return no change
    if not triggered_policies and req.trigger_type == "wellness_red":
        return {"verdict": "no_change", "explanation": "Readiness is normal. No safety adjustments required."}

    # 2. Setup Coach Model (Actor) to draft communication
    coach_prompt = (
        "You are Bibi, the Coach model. We have a safety policy trigger requiring a workout adjustment. "
        "Triggered rules: {rules}.\n"
        "Draft a structured JSON proposal explaining the adjustment to the athlete.\n"
        "Output JSON only: \n"
        "{{\n"
        "  \"explanation\": \"Explain why we are changing tomorrow's ride in supportive, clear language.\",\n"
        "  \"proposed_workout_title\": \"New suggested workout title\"\n"
        "}}"
    ).format(rules=", ".join(triggered_policies))
    
    user_prompt = f"Upcoming workout: {next_workout.title} (Target TSS: {next_workout.tss_target}).\nReadiness State: {readiness} (HRV Z: {hrv_z:.2f}, RHR Z: {rhr_z:.2f})"
    
    coach_json_str = call_llm(settings.COACH_MODEL, coach_prompt, user_prompt, json_mode=True)
    try:
        coach_proposal = json.loads(coach_json_str)
    except json.JSONDecodeError:
        coach_proposal = {
            "explanation": "Your wellness signals indicate recovery is needed, so I've scaled down the intensity.",
            "proposed_workout_title": f"Recovery: {next_workout.title}"
        }

    # 3. Setup Reviewer Model (Critic) to audit the change
    reviewer_system = (
        "You are the AI Reviewer. Audit the Coach's proposed adjustment. "
        "Verify: Did the Coach correctly strip/scale intensity as requested by the triggered policies? "
        "Triggered rules: {rules}.\n"
        "Output JSON only:\n"
        "{{\n"
        "  \"decision\": \"approve\" or \"modify\" or \"reject\",\n"
        "  \"rationale\": \"Reasoning verifying safety rules compliance.\"\n"
        "}}"
    ).format(rules=", ".join(triggered_policies))
    
    reviewer_user = f"Original intervals: {next_workout.intervals_json}\nModified intervals: {modified_intervals}\nCoach explanation: {coach_proposal.get('explanation')}"
    
    reviewer_json_str = call_llm(settings.REVIEWER_MODEL, reviewer_system, reviewer_user, json_mode=True)
    try:
        reviewer_verdict = json.loads(reviewer_json_str)
    except json.JSONDecodeError:
        reviewer_verdict = {"decision": "approve", "rationale": "Fallback auto-approval."}
        
    # 4. Write decision and update plan version if approved
    if reviewer_verdict.get("decision") in ["approve", "modify"]:
        # Write Decision Object
        db_decision = DecisionObject(
            decision_type="reviewer_approved" if reviewer_verdict.get("decision") == "approve" else "reviewer_modified",
            trigger_type=req.trigger_type,
            policy_rules_triggered=triggered_policies,
            coach_reasoning=coach_proposal.get("explanation"),
            reviewer_rationale=reviewer_verdict.get("rationale"),
            diff={"workout_id": str(next_workout.id), "old_title": next_workout.title, "new_title": coach_proposal.get("proposed_workout_title")}
        )
        db.add(db_decision)
        db.commit()
        db.refresh(db_decision)
        
        # Get latest plan version
        latest_version = db.query(PlanVersion).filter(PlanVersion.plan_id == plan.id).order_by(PlanVersion.version.desc()).first()
        next_ver_num = (latest_version.version + 1) if latest_version else 1
        
        db_ver = PlanVersion(
            plan_id=plan.id,
            version=next_ver_num,
            decision_object_id=db_decision.id
        )
        db.add(db_ver)
        
        # Apply the changes to the workout
        next_workout.title = coach_proposal.get("proposed_workout_title", next_workout.title)
        next_workout.intervals_json = modified_intervals
        # Approximate new TSS target (scale TSS roughly)
        if readiness == "red":
            next_workout.tss_target = int(round(next_workout.tss_target * 0.40))
        elif readiness == "yellow":
            next_workout.tss_target = int(round(next_workout.tss_target * 0.85))
            
        next_workout.updated_at = datetime.utcnow()
        db.commit()
        
        return {
            "verdict": "applied",
            "explanation": coach_proposal.get("explanation"),
            "new_title": next_workout.title,
            "new_tss": next_workout.tss_target,
            "version": next_ver_num
        }
    else:
        return {
            "verdict": "rejected",
            "explanation": "The proposed adjustments were rejected by safety audit parameters. Plan remains unchanged."
        }
