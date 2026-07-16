"""add_orchestration_tables

Revision ID: e7b4628d53ca
Revises: 9a61dadb18c7
Create Date: 2026-07-17 01:44:55.174914

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e7b4628d53ca'
down_revision: Union[str, Sequence[str], None] = '9a61dadb18c7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_tables = inspector.get_table_names()

    # 1. Create ai_workflow_executions table if it does not exist
    if 'ai_workflow_executions' not in existing_tables:
        op.create_table(
            'ai_workflow_executions',
            sa.Column('id', sa.Uuid(), nullable=False),
            sa.Column('project_id', sa.Uuid(), nullable=False),
            sa.Column('workspace_id', sa.Uuid(), nullable=False),
            sa.Column('current_stage', sa.String(length=100), nullable=True),
            sa.Column('status', sa.String(length=50), nullable=False),
            sa.Column('progress', sa.Float(), nullable=False),
            sa.Column('context_json', sa.JSON(), nullable=False),
            sa.Column('retry_count', sa.Integer(), nullable=False),
            sa.Column('failure_reason', sa.String(length=4096), nullable=True),
            sa.Column('require_human_review', sa.Boolean(), nullable=False),
            sa.Column('checkpoint_reached', sa.String(length=100), nullable=True),
            sa.Column('started_at', sa.DateTime(), nullable=True),
            sa.Column('completed_at', sa.DateTime(), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
            sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('created_by', sa.Uuid(), nullable=True),
            sa.Column('updated_by', sa.Uuid(), nullable=True),
            sa.Column('version', sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(['project_id'], ['projects.id'], name='fk_executions_project_id', ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], name='fk_executions_workspace_id', ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_ai_workflow_executions_id'), 'ai_workflow_executions', ['id'], unique=False)
        op.create_index(op.f('ix_ai_workflow_executions_project_id'), 'ai_workflow_executions', ['project_id'], unique=False)
        op.create_index(op.f('ix_ai_workflow_executions_workspace_id'), 'ai_workflow_executions', ['workspace_id'], unique=False)

    # 2. Create ai_workflow_steps table if it does not exist
    if 'ai_workflow_steps' not in existing_tables:
        op.create_table(
            'ai_workflow_steps',
            sa.Column('id', sa.Uuid(), nullable=False),
            sa.Column('workflow_id', sa.Uuid(), nullable=False),
            sa.Column('agent_name', sa.String(length=100), nullable=False),
            sa.Column('status', sa.String(length=50), nullable=False),
            sa.Column('input_context', sa.JSON(), nullable=False),
            sa.Column('output_data', sa.JSON(), nullable=False),
            sa.Column('retry_count', sa.Integer(), nullable=False),
            sa.Column('failure_reason', sa.String(length=4096), nullable=True),
            sa.Column('started_at', sa.DateTime(), nullable=True),
            sa.Column('completed_at', sa.DateTime(), nullable=True),
            sa.Column('model_used', sa.String(length=100), nullable=True),
            sa.Column('input_tokens', sa.Integer(), nullable=False),
            sa.Column('output_tokens', sa.Integer(), nullable=False),
            sa.Column('total_tokens', sa.Integer(), nullable=False),
            sa.Column('execution_time', sa.Float(), nullable=False),
            sa.Column('estimated_cost', sa.Float(), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
            sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('created_by', sa.Uuid(), nullable=True),
            sa.Column('updated_by', sa.Uuid(), nullable=True),
            sa.Column('version', sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(['workflow_id'], ['ai_workflow_executions.id'], name='fk_steps_workflow_id', ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_ai_workflow_steps_agent_name'), 'ai_workflow_steps', ['agent_name'], unique=False)
        op.create_index(op.f('ix_ai_workflow_steps_id'), 'ai_workflow_steps', ['id'], unique=False)
        op.create_index(op.f('ix_ai_workflow_steps_workflow_id'), 'ai_workflow_steps', ['workflow_id'], unique=False)

    # 3. Add columns to projects table using batch mode
    project_columns = [c['name'] for c in inspector.get_columns('projects')]
    
    with op.batch_alter_table('projects') as batch_op:
        if 'generation_status' not in project_columns:
            batch_op.add_column(sa.Column('generation_status', sa.String(length=50), nullable=True))
            
        if 'generation_progress' not in project_columns:
            batch_op.add_column(sa.Column('generation_progress', sa.Float(), nullable=True, server_default='0.0'))
            
        if 'workflow_id' not in project_columns:
            batch_op.add_column(sa.Column('workflow_id', sa.Uuid(), sa.ForeignKey('ai_workflow_executions.id', name='fk_projects_workflow_id', ondelete='SET NULL'), nullable=True))
            batch_op.create_index('ix_projects_workflow_id', ['workflow_id'], unique=False)


def downgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    project_columns = [c['name'] for c in inspector.get_columns('projects')]
    existing_tables = inspector.get_table_names()

    # 1. Drop columns from projects using batch mode
    with op.batch_alter_table('projects') as batch_op:
        if 'workflow_id' in project_columns:
            batch_op.drop_index('ix_projects_workflow_id')
            batch_op.drop_column('workflow_id')
        if 'generation_progress' in project_columns:
            batch_op.drop_column('generation_progress')
        if 'generation_status' in project_columns:
            batch_op.drop_column('generation_status')

    # 2. Drop ai_workflow_steps table
    if 'ai_workflow_steps' in existing_tables:
        op.drop_index(op.f('ix_ai_workflow_steps_workflow_id'), table_name='ai_workflow_steps')
        op.drop_index(op.f('ix_ai_workflow_steps_id'), table_name='ai_workflow_steps')
        op.drop_index(op.f('ix_ai_workflow_steps_agent_name'), table_name='ai_workflow_steps')
        op.drop_table('ai_workflow_steps')

    # 3. Drop ai_workflow_executions table
    if 'ai_workflow_executions' in existing_tables:
        op.drop_index(op.f('ix_ai_workflow_executions_workspace_id'), table_name='ai_workflow_executions')
        op.drop_index(op.f('ix_ai_workflow_executions_project_id'), table_name='ai_workflow_executions')
        op.drop_index(op.f('ix_ai_workflow_executions_id'), table_name='ai_workflow_executions')
        op.drop_table('ai_workflow_executions')
