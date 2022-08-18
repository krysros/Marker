"""Add timestamps to persons

Revision ID: 39a9144f106b
Revises: e4347a008dd5
Create Date: 2022-07-31 16:39:25.872080

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '39a9144f106b'
down_revision = 'e4347a008dd5'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('persons', sa.Column('created_at', sa.DateTime(), nullable=True))
    op.add_column('persons', sa.Column('updated_at', sa.DateTime(), nullable=True))
    op.add_column('persons', sa.Column('creator_id', sa.Integer(), nullable=True))
    op.add_column('persons', sa.Column('editor_id', sa.Integer(), nullable=True))
    op.create_foreign_key(op.f('fk_persons_creator_id_users'), 'persons', 'users', ['creator_id'], ['id'], ondelete='SET NULL')
    op.create_foreign_key(op.f('fk_persons_editor_id_users'), 'persons', 'users', ['editor_id'], ['id'], ondelete='SET NULL')

def downgrade():
    op.drop_column('persons', 'created_at')
    op.drop_column('persons', 'updated_at')
    op.drop_column('persons', 'creator_id')
    op.drop_column('persons', 'editor_id')
    op.drop_constraint(op.f('fk_persons_creator_id_users'), 'persons')
    op.drop_constraint(op.f('fk_persons_editor_id_users'), 'persons')
