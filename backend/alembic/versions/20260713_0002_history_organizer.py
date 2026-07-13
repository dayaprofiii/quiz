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
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {column['name'] for column in inspector.get_columns('history')}
    if 'organizer_id' not in columns:
        op.add_column('history', sa.Column('organizer_id', sa.String(length=64), nullable=True))

    indexes = {index['name'] for index in inspector.get_indexes('history')}
    if 'ix_history_organizer_id' not in indexes:
        op.create_index(op.f('ix_history_organizer_id'), 'history', ['organizer_id'], unique=False)

    foreign_keys = inspector.get_foreign_keys('history')
    has_organizer_fk = any(
        foreign_key.get('constrained_columns') == ['organizer_id'] and foreign_key.get('referred_table') == 'users'
        for foreign_key in foreign_keys
    )
    if not has_organizer_fk:
        op.create_foreign_key('fk_history_organizer_id_users', 'history', 'users', ['organizer_id'], ['id'], ondelete='SET NULL')


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    foreign_keys = inspector.get_foreign_keys('history')
    for foreign_key in foreign_keys:
        if foreign_key.get('constrained_columns') == ['organizer_id'] and foreign_key.get('referred_table') == 'users':
            op.drop_constraint(foreign_key['name'], 'history', type_='foreignkey')
            break

    indexes = {index['name'] for index in inspector.get_indexes('history')}
    if 'ix_history_organizer_id' in indexes:
        op.drop_index(op.f('ix_history_organizer_id'), table_name='history')

    columns = {column['name'] for column in inspector.get_columns('history')}
    if 'organizer_id' in columns:
        op.drop_column('history', 'organizer_id')
