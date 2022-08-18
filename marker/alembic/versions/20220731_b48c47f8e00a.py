"""Rename branches to tags

Revision ID: b48c47f8e00a
Revises: b68ff97b05fe
Create Date: 2022-07-31 10:35:19.825061

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b48c47f8e00a'
down_revision = 'b68ff97b05fe'
branch_labels = None
depends_on = None

def upgrade():
    op.drop_constraint(op.f('fk_branches_creator_id_users'), 'branches')
    op.drop_constraint(op.f('fk_branches_editor_id_users'), 'branches')
    op.drop_constraint(op.f('fk_companies_branches_branch_id_branches'), 'companies_branches')
    op.drop_constraint(op.f('fk_companies_branches_company_id_companies'), 'companies_branches')
    op.drop_constraint(op.f('pk_branches'), 'branches')
    op.rename_table('branches', 'tags')
    op.rename_table('companies_branches', 'companies_tags')
    op.alter_column(table_name='companies_tags', column_name='branch_id', new_column_name='tag_id')
    op.create_primary_key('pk_tags', 'tags', ['id'])
    op.create_foreign_key(op.f('fk_tags_creator_id_users'), 'tags', 'users', ['creator_id'], ['id'], ondelete='SET NULL')
    op.create_foreign_key(op.f('fk_tags_editor_id_users'), 'tags', 'users', ['editor_id'], ['id'], ondelete='SET NULL')
    op.create_foreign_key(op.f('fk_companies_tags_tag_id_tags'), 'companies_tags', 'tags', ['tag_id'], ['id'], onupdate='CASCADE', ondelete='CASCADE')
    op.create_foreign_key(op.f('fk_companies_tags_company_id_companies'), 'companies_tags', 'companies', ['company_id'], ['id'], onupdate='CASCADE', ondelete='CASCADE')

def downgrade():
    op.drop_constraint(op.f('fk_tags_creator_id_users'), 'tags')
    op.drop_constraint(op.f('fk_tags_editor_id_users'), 'tags')
    op.drop_constraint(op.f('fk_companies_tags_tag_id_tags'), 'companies_tags')
    op.drop_constraint(op.f('fk_companies_tags_company_id_tags'), 'companies_tags')
    op.drop_constraint(op.f('pk_tags'), 'tags')
    op.rename_table('tags', 'branches')
    op.rename_table('companies_tags', 'companies_branches')
    op.alter_column(table_name='companies_branches', column_name='tag_id', new_column_name='branch_id')
    op.create_primary_key('pk_branches', 'branches', ['id'])
    op.create_foreign_key(op.f('fk_branches_creator_id_users'), 'branches', 'users', ['creator_id'], ['id'], ondelete='SET NULL')
    op.create_foreign_key(op.f('fk_branches_editor_id_users'), 'branches', 'users', ['editor_id'], ['id'], ondelete='SET NULL')
    op.create_foreign_key(op.f('fk_companies_branches_branch_id_branches'), 'companies_branches', 'branches', ['branch_id'], ['id'], onupdate='CASCADE', ondelete='CASCADE')
    op.create_foreign_key(op.f('fk_companies_branches_company_id_companies'), 'companies_branches', 'companies', ['company_id'], ['id'], onupdate='CASCADE', ondelete='CASCADE')
