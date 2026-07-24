"""phase1 security hardening: user lockout/withdrawal-lock/session-revocation
fields, security_logs, login_security

Revision ID: b1c2d3e4f5a6
Revises: f3a91c2d7e4b
Create Date: 2026-07-16 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa


revision = 'b1c2d3e4f5a6'
down_revision = 'f3a91c2d7e4b'
branch_labels = None
depends_on = None


def upgrade():
    # with op.batch_alter_table('users', schema=None) as batch_op:
    #     batch_op.add_column(sa.Column('withdrawal_locked_until', sa.DateTime(), nullable=True))
    #     batch_op.add_column(sa.Column('tokens_invalidated_at', sa.DateTime(), nullable=True))
    #     batch_op.add_column(sa.Column('failed_login_attempts', sa.Integer(), nullable=False, server_default='0'))
    #     batch_op.add_column(sa.Column('locked_until', sa.DateTime(), nullable=True))
    #     batch_op.add_column(sa.Column('password_changed_at', sa.DateTime(), nullable=True))

    op.create_table(
        'security_logs',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('event_type', sa.Enum(
            'PASSWORD_CHANGED', 'PASSWORD_RESET', 'EMAIL_CHANGED', 'PHONE_CHANGED',
            'BANK_ACCOUNT_CHANGED', 'LOGIN_SUCCESS', 'LOGIN_FAILED', 'LOGIN_NEW_DEVICE',
            'LOGIN_NEW_LOCATION', 'ACCOUNT_LOCKED', 'ACCOUNT_UNLOCKED', 'SESSIONS_REVOKED',
            'WITHDRAWAL_BLOCKED_LOCK', 'WITHDRAWAL_BLOCKED_LIMIT', 'WITHDRAWAL_BLOCKED_VELOCITY',
            'WITHDRAWAL_REQUESTED', 'OTP_REQUESTED', 'OTP_FAILED', 'OTP_RATE_LIMITED',
            'HIGH_RISK_ACTION_VERIFIED', 'KYC_SUBMITTED', 'KYC_APPROVED', 'KYC_REJECTED',
            'FRAUD_ALERT_RAISED',
            name='securityeventtype',
        ), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.Column('ip_address', sa.String(length=64), nullable=True),
        sa.Column('user_agent', sa.String(length=255), nullable=True),
        sa.Column('meta_data', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )
    op.create_index('idx_seclog_user_created', 'security_logs', ['user_id', 'created_at'])
    op.create_index('idx_seclog_event_created', 'security_logs', ['event_type', 'created_at'])
    op.create_index(op.f('ix_security_logs_user_id'), 'security_logs', ['user_id'])
    op.create_index(op.f('ix_security_logs_created_at'), 'security_logs', ['created_at'])

    op.create_table(
        'login_security',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('ip_address', sa.String(length=64), nullable=True),
        sa.Column('user_agent', sa.String(length=255), nullable=True),
        sa.Column('browser', sa.String(length=80), nullable=True),
        sa.Column('operating_system', sa.String(length=80), nullable=True),
        sa.Column('device_type', sa.String(length=40), nullable=True),
        sa.Column('device_hash', sa.String(length=64), nullable=True),
        sa.Column('country', sa.String(length=80), nullable=True),
        sa.Column('city', sa.String(length=80), nullable=True),
        sa.Column('successful', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('is_new_device', sa.Boolean(), nullable=True, server_default=sa.false()),
        sa.Column('is_new_location', sa.Boolean(), nullable=True, server_default=sa.false()),
        sa.Column('risk_score', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )
    op.create_index('idx_loginsec_user_created', 'login_security', ['user_id', 'created_at'])
    op.create_index('idx_loginsec_device_hash', 'login_security', ['user_id', 'device_hash'])
    op.create_index(op.f('ix_login_security_user_id'), 'login_security', ['user_id'])
    op.create_index(op.f('ix_login_security_device_hash'), 'login_security', ['device_hash'])
    op.create_index(op.f('ix_login_security_created_at'), 'login_security', ['created_at'])


def downgrade():
    op.drop_table('login_security')
    op.drop_table('security_logs')
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('password_changed_at')
        batch_op.drop_column('locked_until')
        batch_op.drop_column('failed_login_attempts')
        batch_op.drop_column('tokens_invalidated_at')
        batch_op.drop_column('withdrawal_locked_until')
