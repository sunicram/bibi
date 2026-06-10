"""initial

Revision ID: a1b2c3d4e5f6
Revises: 
Create Date: 2026-06-03 21:40:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. users table
    op.create_table(
        'users',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('password_hash', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # 2. profiles table
    op.create_table(
        'profiles',
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('ftp', sa.Integer(), nullable=False),
        sa.Column('w_prime', sa.Integer(), nullable=False),
        sa.Column('resting_hr', sa.Integer(), nullable=False),
        sa.Column('max_hr', sa.Integer(), nullable=False),
        sa.Column('weight_kg', sa.Float(), nullable=False),
        sa.Column('power_zones', sa.JSON(), nullable=True),
        sa.Column('hr_zones', sa.JSON(), nullable=True),
        sa.Column('weekly_availability', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('user_id')
    )

    # 3. auth_sessions table
    op.create_table(
        'auth_sessions',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('refresh_token', sa.String(), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_auth_sessions_refresh_token'), 'auth_sessions', ['refresh_token'], unique=False)

    # 4. plans table
    op.create_table(
        'plans',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('duration_weeks', sa.Integer(), nullable=False),
        sa.Column('methodology', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 5. decision_objects table
    op.create_table(
        'decision_objects',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('decision_type', sa.String(), nullable=False),
        sa.Column('trigger_type', sa.String(), nullable=False),
        sa.Column('policy_rules_triggered', sa.JSON(), nullable=True),
        sa.Column('coach_reasoning', sa.String(), nullable=True),
        sa.Column('reviewer_rationale', sa.String(), nullable=True),
        sa.Column('diff', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # 6. plan_versions table
    op.create_table(
        'plan_versions',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('plan_id', sa.UUID(), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('decision_object_id', sa.UUID(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['decision_object_id'], ['decision_objects.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['plan_id'], ['plans.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 7. workouts table
    op.create_table(
        'workouts',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('plan_id', sa.UUID(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('tss_target', sa.Integer(), nullable=False),
        sa.Column('intervals_json', sa.JSON(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['plan_id'], ['plans.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_workouts_date'), 'workouts', ['date'], unique=False)

    # 8. activities table
    op.create_table(
        'activities',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('workout_id', sa.UUID(), nullable=True),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('external_icu_id', sa.String(), nullable=True),
        sa.Column('external_strava_id', sa.String(), nullable=True),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('duration_seconds', sa.Integer(), nullable=False),
        sa.Column('tss', sa.Integer(), nullable=False),
        sa.Column('intensity_factor', sa.Float(), nullable=False),
        sa.Column('normalized_power', sa.Float(), nullable=False),
        sa.Column('avg_power', sa.Float(), nullable=False),
        sa.Column('avg_hr', sa.Float(), nullable=False),
        sa.Column('aerobic_decoupling', sa.Float(), nullable=True),
        sa.Column('wbal_depleted_flag', sa.Boolean(), nullable=False),
        sa.Column('adherence_score', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['workout_id'], ['workouts.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_activities_date'), 'activities', ['date'], unique=False)
    op.create_index(op.f('ix_activities_external_icu_id'), 'activities', ['external_icu_id'], unique=False)
    op.create_index(op.f('ix_activities_external_strava_id'), 'activities', ['external_strava_id'], unique=False)

    # 9. activity_telemetry table
    op.create_table(
        'activity_telemetry',
        sa.Column('activity_id', sa.UUID(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('power', sa.Integer(), nullable=False),
        sa.Column('heart_rate', sa.Integer(), nullable=False),
        sa.Column('cadence', sa.Integer(), nullable=False),
        sa.Column('speed', sa.Float(), nullable=False),
        sa.Column('altitude', sa.Float(), nullable=False),
        sa.Column('wbal', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['activity_id'], ['activities.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('activity_id', 'timestamp')
    )

    # 10. wellness_daily table
    op.create_table(
        'wellness_daily',
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('device_source', sa.String(), nullable=False),
        sa.Column('hrv_rmssd', sa.Float(), nullable=True),
        sa.Column('resting_hr', sa.Integer(), nullable=True),
        sa.Column('sleep_minutes', sa.Integer(), nullable=True),
        sa.Column('body_battery', sa.Integer(), nullable=True),
        sa.Column('hrv_z_score', sa.Float(), nullable=True),
        sa.Column('rhr_z_score', sa.Float(), nullable=True),
        sa.Column('sleep_debt_minutes', sa.Integer(), nullable=True),
        sa.Column('readiness_tier', sa.String(), nullable=False),
        sa.Column('data_quality_flag', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('user_id', 'date')
    )


def downgrade() -> None:
    op.drop_table('wellness_daily')
    op.drop_table('activity_telemetry')
    op.drop_index(op.f('ix_activities_external_strava_id'), table_name='activities')
    op.drop_index(op.f('ix_activities_external_icu_id'), table_name='activities')
    op.drop_index(op.f('ix_activities_date'), table_name='activities')
    op.drop_table('activities')
    op.drop_index(op.f('ix_workouts_date'), table_name='workouts')
    op.drop_table('workouts')
    op.drop_table('plan_versions')
    op.drop_table('decision_objects')
    op.drop_table('plans')
    op.drop_index(op.f('ix_auth_sessions_refresh_token'), table_name='auth_sessions')
    op.drop_table('auth_sessions')
    op.drop_table('profiles')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
