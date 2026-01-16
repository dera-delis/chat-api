"""Add room invites and join requests

Revision ID: 9f1a5b7c2d01
Revises: 62b0588d11e2
Create Date: 2026-01-16 12:05:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9f1a5b7c2d01'
down_revision = '62b0588d11e2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'room_invites',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('room_id', sa.Integer(), nullable=False),
        sa.Column('token', sa.String(), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.ForeignKeyConstraint(['room_id'], ['rooms.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_room_invites_id'), 'room_invites', ['id'], unique=False)
    op.create_index(op.f('ix_room_invites_token'), 'room_invites', ['token'], unique=True)

    op.create_table(
        'room_join_requests',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('room_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(), nullable=False, server_default='pending'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['room_id'], ['rooms.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('room_id', 'user_id', name='uq_room_join_requests_room_user')
    )
    op.create_index(op.f('ix_room_join_requests_id'), 'room_join_requests', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_room_join_requests_id'), table_name='room_join_requests')
    op.drop_table('room_join_requests')
    op.drop_index(op.f('ix_room_invites_token'), table_name='room_invites')
    op.drop_index(op.f('ix_room_invites_id'), table_name='room_invites')
    op.drop_table('room_invites')

