"""Add editor to comments

Revision ID: 020e54cf08a7
Revises: 6290dc2e9b06
Create Date: 2022-07-31 14:16:20.829933

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '020e54cf08a7'
down_revision = '6290dc2e9b06'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('comments', sa.Column('updated_at', sa.DateTime(), nullable=True))
    op.add_column('comments', sa.Column('editor_id', sa.Integer(), nullable=True))
    op.create_foreign_key(op.f('fk_comments_editor_id_users'), 'comments', 'users', ['editor_id'], ['id'], ondelete='SET NULL')

def downgrade():
    op.drop_constraint(op.f('fk_comments_editor_id_users'), 'comments')
    op.drop_column('comments', 'editor_id')
    op.drop_column('comments', 'updated_at')

