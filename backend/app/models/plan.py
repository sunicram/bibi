import uuid
from datetime import datetime, date
from sqlalchemy import Column, String, DateTime, Date, ForeignKey, Integer, Float, JSON, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import Base

class Plan(Base):
    __tablename__ = "plans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    duration_weeks = Column(Integer, nullable=False)
    methodology = Column(String, nullable=False) # "polarized" | "sweet_spot" | "traditional"
    status = Column(String, default="active", nullable=False) # "active" | "completed" | "suspended" | "archived"
    start_date = Column(Date, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="plans")
    versions = relationship("PlanVersion", back_populates="plan", cascade="all, delete-orphan")
    workouts = relationship("Workout", back_populates="plan", cascade="all, delete-orphan")

class DecisionObject(Base):
    __tablename__ = "decision_objects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    decision_type = Column(String, nullable=False) # "auto_applied" | "reviewer_approved" | "reviewer_modified" | "rejected"
    trigger_type = Column(String, nullable=False) # "ml_flag" | "anomaly" | "user_request" | "wellness_red"
    policy_rules_triggered = Column(JSON, nullable=True) # list of rules triggered
    coach_reasoning = Column(String, nullable=True)
    reviewer_rationale = Column(String, nullable=True)
    diff = Column(JSON, nullable=True) # JSON diff of changes
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    plan_versions = relationship("PlanVersion", back_populates="decision_object")

class PlanVersion(Base):
    __tablename__ = "plan_versions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plan_id = Column(UUID(as_uuid=True), ForeignKey("plans.id", ondelete="CASCADE"), nullable=False)
    version = Column(Integer, nullable=False)
    decision_object_id = Column(UUID(as_uuid=True), ForeignKey("decision_objects.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    plan = relationship("Plan", back_populates="versions")
    decision_object = relationship("DecisionObject", back_populates="plan_versions")

class Workout(Base):
    __tablename__ = "workouts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plan_id = Column(UUID(as_uuid=True), ForeignKey("plans.id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False, index=True)
    title = Column(String, nullable=False)
    tss_target = Column(Integer, nullable=False)
    intervals_json = Column(JSON, nullable=False) # target steps: Warmup, Intervals, Cooldown
    status = Column(String, default="scheduled", nullable=False) # "scheduled" | "completed" | "skipped" | "missed"
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    plan = relationship("Plan", back_populates="workouts")
    activities = relationship("Activity", back_populates="workout")

class Activity(Base):
    __tablename__ = "activities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workout_id = Column(UUID(as_uuid=True), ForeignKey("workouts.id", ondelete="SET NULL"), nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    external_icu_id = Column(String, index=True, nullable=True)
    external_strava_id = Column(String, index=True, nullable=True)
    date = Column(Date, nullable=False, index=True)
    duration_seconds = Column(Integer, nullable=False)
    tss = Column(Integer, nullable=False)
    intensity_factor = Column(Float, nullable=False)
    normalized_power = Column(Float, nullable=False)
    avg_power = Column(Float, nullable=False)
    avg_hr = Column(Float, nullable=False)
    aerobic_decoupling = Column(Float, nullable=True) # Decoupling value (Pw:HR)
    wbal_depleted_flag = Column(Boolean, default=False, nullable=False)
    adherence_score = Column(Float, nullable=False) # % match with workout target
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    workout = relationship("Workout", back_populates="activities")
    user = relationship("User", back_populates="activities")
    telemetry = relationship("ActivityTelemetry", back_populates="activity", cascade="all, delete-orphan")

class ActivityTelemetry(Base):
    __tablename__ = "activity_telemetry"

    # Composite primary key for partitioning and indexing
    activity_id = Column(UUID(as_uuid=True), ForeignKey("activities.id", ondelete="CASCADE"), primary_key=True)
    timestamp = Column(DateTime, primary_key=True)
    power = Column(Integer, nullable=False) # Watts
    heart_rate = Column(Integer, nullable=False) # BPM
    cadence = Column(Integer, nullable=False) # RPM
    speed = Column(Float, nullable=False) # m/s
    altitude = Column(Float, nullable=False) # meters
    wbal = Column(Integer, nullable=False) # W' remaining in Joules

    activity = relationship("Activity", back_populates="telemetry")

class WellnessDaily(Base):
    __tablename__ = "wellness_daily"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    date = Column(Date, primary_key=True)
    device_source = Column(String, nullable=False) # "garmin" | "apple_health" | "intervals.icu"
    hrv_rmssd = Column(Float, nullable=True)
    resting_hr = Column(Integer, nullable=True)
    sleep_minutes = Column(Integer, nullable=True)
    body_battery = Column(Integer, nullable=True)
    hrv_z_score = Column(Float, nullable=True)
    rhr_z_score = Column(Float, nullable=True)
    sleep_debt_minutes = Column(Integer, nullable=True)
    readiness_tier = Column(String, default="green", nullable=False) # "green" | "yellow" | "red"
    data_quality_flag = Column(String, default="measured", nullable=False) # "measured" | "estimated" | "missing"
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="wellness_records")
