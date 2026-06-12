"""add wellness and activity feedback fields

Revision ID: b2c3d4e5f6a1
Revises: a1b2c3d4e5f6
Create Date: 2026-06-12 16:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f6a1'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add columns to activities
    op.add_column('activities', sa.Column('activity_notes', sa.String(), nullable=True))
    op.add_column('activities', sa.Column('feeling_before', sa.Integer(), nullable=True))
    op.add_column('activities', sa.Column('difficulty_after', sa.Integer(), nullable=True))
    op.add_column('activities', sa.Column('reserve_forces', sa.Integer(), nullable=True))
    op.add_column('activities', sa.Column('teq_score', sa.Float(), nullable=True))

    # Add columns to wellness_daily
    op.add_column('wellness_daily', sa.Column('weight_kg', sa.Float(), nullable=True))
    op.add_column('wellness_daily', sa.Column('body_fat_pct', sa.Float(), nullable=True))
    op.add_column('wellness_daily', sa.Column('muscle_mass_pct', sa.Float(), nullable=True))
    op.add_column('wellness_daily', sa.Column('water_pct', sa.Float(), nullable=True))

    # Add columns to profiles
    op.add_column('profiles', sa.Column('body_fat_pct', sa.Float(), nullable=True))
    op.add_column('profiles', sa.Column('muscle_mass_pct', sa.Float(), nullable=True))
    op.add_column('profiles', sa.Column('water_pct', sa.Float(), nullable=True))


def downgrade() -> None:
    # Drop columns from profiles
    op.drop_column('profiles', 'water_pct')
    op.drop_column('profiles', 'muscle_mass_pct')
    op.drop_column('profiles', 'body_fat_pct')

    # Drop columns from wellness_daily
    op.drop_column('wellness_daily', 'water_pct')
    op.drop_column('wellness_daily', 'muscle_mass_pct')
    op.drop_column('wellness_daily', 'body_fat_pct')
    op.drop_column('wellness_daily', 'weight_kg')

    # Drop columns from activities
    op.drop_column('activities', 'teq_score')
    op.drop_column('activities', 'reserve_forces')
    op.drop_column('activities', 'difficulty_after')
    op.drop_column('activities', 'feeling_before')
    op.drop_column('activities', 'activity_notes')
