"""add history organizer

Revision ID: 20260713_0002
Revises: 20260712_0001
Create Date: 2026-07-13
"""

from alembic import op
import sqlalchemy as sa


revision = '20260713_0002'
down_revision = '20260712_0001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('history', sa.Column('organizer_id', sa.String(length=64), nullable=True))
    op.create_index(op.f('ix_history_organizer_id'), 'history', ['organizer_id'], unique=False)
    op.create_foreign_key('fk_history_organizer_id_users', 'history', 'users', ['organizer_id'], ['id'], ondelete='SET NULL')


def downgrade() -> None:
    op.drop_constraint('fk_history_organizer_id_users', 'history', type_='foreignkey')
    op.drop_index(op.f('ix_history_organizer_id'), table_name='history')
    op.drop_column('history', 'organizer_id')
