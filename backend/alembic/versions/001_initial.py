"""初始化数据库表

Revision ID: 001
Create Date: 2025-12-07
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision标识符
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """创建所有表"""

    # 用户表
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('email', sa.String(length=100), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('avatar_url', sa.String(length=500)),
        sa.Column('encrypted_api_keys', postgresql.JSON(), server_default='{}'),
        sa.Column('timezone', sa.String(length=50), server_default='UTC'),
        sa.Column('preferred_language', sa.String(length=10), server_default='en'),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True)),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_users_username', 'users', ['username'], unique=True)
    op.create_index('ix_users_email', 'users', ['email'], unique=True)

    # 角色表
    op.create_table(
        'characters',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('avatar_url', sa.String(length=500)),
        sa.Column('personality', sa.Text()),
        sa.Column('background_story', sa.Text()),
        sa.Column('system_prompt', sa.Text(), nullable=False),
        sa.Column('llm_provider', sa.String(length=50), server_default='openai'),
        sa.Column('llm_model', sa.String(length=100), server_default='gpt-3.5-turbo'),
        sa.Column('config', postgresql.JSON(), server_default='{}'),
        sa.Column('language', sa.String(length=10), server_default='en'),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('is_preset', sa.Boolean(), server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True)),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_characters_user_id', 'characters', ['user_id'])

    # 对话表
    op.create_table(
        'conversations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('character_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True)),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['character_id'], ['characters.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_user_character', 'conversations', ['user_id', 'character_id'], unique=True)

    # 消息表
    op.create_table(
        'messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('conversation_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('tokens_used', sa.Integer(), server_default='0'),
        sa.Column('is_proactive', sa.Boolean(), server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_messages_conversation_id', 'messages', ['conversation_id'])
    op.create_index('ix_messages_created_at', 'messages', ['created_at'])

    # 用户活跃状态表
    op.create_table(
        'user_activity',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('conversation_id', sa.Integer(), nullable=False),
        sa.Column('last_message_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('last_check_at', sa.DateTime(timezone=True)),
        sa.Column('next_proactive_at', sa.DateTime(timezone=True)),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('conversation_id')
    )
    op.create_index('ix_user_activity_next_proactive_at', 'user_activity', ['next_proactive_at'])

    # 好感度表
    op.create_table(
        'affection_scores',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('character_id', sa.Integer(), nullable=False),
        sa.Column('current_score', sa.Integer(), server_default='0', nullable=False),
        sa.Column('level', sa.String(length=50), server_default='普通'),
        sa.Column('last_interaction', sa.DateTime(timezone=True)),
        sa.Column('total_interactions', sa.Integer(), server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True)),
        sa.CheckConstraint('current_score >= -100 AND current_score <= 100', name='score_range'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['character_id'], ['characters.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_user_character_affection', 'affection_scores', ['user_id', 'character_id'], unique=True)

    # 好感度历史表
    op.create_table(
        'affection_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('affection_score_id', sa.Integer(), nullable=False),
        sa.Column('message_id', sa.Integer()),
        sa.Column('score_change', sa.Integer(), nullable=False),
        sa.Column('reason', sa.Text()),
        sa.Column('sentiment_analysis', postgresql.JSON()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['affection_score_id'], ['affection_scores.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['message_id'], ['messages.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_affection_logs_affection_score_id', 'affection_logs', ['affection_score_id'])
    op.create_index('ix_affection_logs_created_at', 'affection_logs', ['created_at'])

    # 主动消息任务表
    op.create_table(
        'proactive_message_tasks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('character_id', sa.Integer(), nullable=False),
        sa.Column('scheduled_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('status', sa.String(length=20), server_default='pending'),
        sa.Column('trigger_reason', sa.String(length=100)),
        sa.Column('message_content', sa.Text()),
        sa.Column('sent_at', sa.DateTime(timezone=True)),
        sa.Column('error_message', sa.Text()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['character_id'], ['characters.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_proactive_tasks_scheduled_at', 'proactive_message_tasks', ['scheduled_at'])
    op.create_index('ix_proactive_tasks_status', 'proactive_message_tasks', ['status'])


def downgrade() -> None:
    """删除所有表"""
    op.drop_table('proactive_message_tasks')
    op.drop_table('affection_logs')
    op.drop_table('affection_scores')
    op.drop_table('user_activity')
    op.drop_table('messages')
    op.drop_table('conversations')
    op.drop_table('characters')
    op.drop_table('users')
