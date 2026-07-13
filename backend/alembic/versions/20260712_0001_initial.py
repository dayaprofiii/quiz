"""initial schema

Revision ID: 20260712_0001
Revises:
Create Date: 2026-07-12
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = '20260712_0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.String(length=64), nullable=False),
        sa.Column('email', sa.String(length=320), nullable=False),
        sa.Column('name', sa.String(length=120), nullable=False),
        sa.Column('password_hash', sa.Text(), nullable=False),
        sa.Column('role', sa.String(length=32), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email', name='uq_users_email'),
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=False)

    op.create_table(
        'quizzes',
        sa.Column('id', sa.String(length=64), nullable=False),
        sa.Column('owner_id', sa.String(length=64), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('category', sa.String(length=120), nullable=False),
        sa.Column('time_limit', sa.Integer(), nullable=False),
        sa.Column('rules', sa.Text(), nullable=False),
        sa.Column('questions', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_quizzes_owner_id'), 'quizzes', ['owner_id'], unique=False)

    op.create_table(
        'history',
        sa.Column('id', sa.String(length=64), nullable=False),
        sa.Column('quiz_id', sa.String(length=64), nullable=True),
        sa.Column('quiz_title', sa.String(length=200), nullable=False),
        sa.Column('code', sa.String(length=16), nullable=False),
        sa.Column('finished_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('leaderboard', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.ForeignKeyConstraint(['quiz_id'], ['quizzes.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_history_code'), 'history', ['code'], unique=False)
    op.create_index(op.f('ix_history_quiz_id'), 'history', ['quiz_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_history_quiz_id'), table_name='history')
    op.drop_index(op.f('ix_history_code'), table_name='history')
    op.drop_table('history')
    op.drop_index(op.f('ix_quizzes_owner_id'), table_name='quizzes')
    op.drop_table('quizzes')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
