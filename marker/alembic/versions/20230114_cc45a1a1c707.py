"""Detect changes

Revision ID: cc45a1a1c707
Revises: 257985e0bffb
Create Date: 2023-01-14 13:16:14.508877

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'cc45a1a1c707'
down_revision = '257985e0bffb'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('comments', sa.Column('company_id', sa.Integer()))
    op.add_column('comments', sa.Column('project_id', sa.Integer()))
    op.create_foreign_key(op.f('fk_comments_project_id_projects'), 'comments', 'projects', ['project_id'], ['id'])
    op.create_foreign_key(op.f('fk_comments_company_id_companies'), 'comments', 'companies', ['company_id'], ['id'])
    op.add_column('persons', sa.Column('company_id', sa.Integer()))
    op.add_column('persons', sa.Column('project_id', sa.Integer()))
    op.create_foreign_key(op.f('fk_persons_company_id_companies'), 'persons', 'companies', ['company_id'], ['id'])
    op.create_foreign_key(op.f('fk_persons_project_id_projects'), 'persons', 'projects', ['project_id'], ['id'])

def downgrade():
    op.drop_constraint(op.f('fk_persons_project_id_projects'), 'persons', type_='foreignkey')
    op.drop_constraint(op.f('fk_persons_company_id_companies'), 'persons', type_='foreignkey')
    op.drop_column('persons', 'project_id')
    op.drop_column('persons', 'company_id')
    op.drop_constraint(op.f('fk_comments_company_id_companies'), 'comments', type_='foreignkey')
    op.drop_constraint(op.f('fk_comments_project_id_projects'), 'comments', type_='foreignkey')
    op.drop_column('comments', 'project_id')
    op.drop_column('comments', 'company_id')