"""phase2-8: ride geofence/dispute fields, fraud_alerts, driver_kyc,
device_tokens, notification_logs

Revision ID: c7d8e9f0a1b2
Revises: b1c2d3e4f5a6
Create Date: 2026-07-16 00:05:00.000000
"""
from alembic import op
import sqlalchemy as sa


revision = 'c7d8e9f0a1b2'
down_revision = 'b1c2d3e4f5a6'
branch_labels = None
depends_on = None


def upgrade():
    # --- ride_requests: destination validation / dispute state ---
    with op.batch_alter_table('ride_requests', schema=None) as batch_op:
        batch_op.add_column(sa.Column('driver_near_pickup', sa.Boolean(), nullable=True, server_default=sa.false()))
        batch_op.add_column(sa.Column('driver_arrived_at', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('awaiting_completion_at', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('completion_deadline', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('dispute_reason', sa.String(length=500), nullable=True))
        batch_op.add_column(sa.Column('disputed_at', sa.DateTime(), nullable=True))

    # The RideRequestStatus enum gained AWAITING_COMPLETION and DISPUTED values.
    # Native Postgres enums must be altered explicitly; SQLite (and MySQL/Flask-
    # SQLAlchemy's Python-Enum-as-VARCHAR default) needs no DDL change.
    bind = op.get_bind()
    if bind.dialect.name == 'postgresql':
        # ALTER TYPE ... ADD VALUE cannot run inside the transaction block that
        # Alembic normally wraps each migration in (this restriction is
        # enforced on some Postgres versions/configs even though PG12+ relaxed
        # it in the common case) -- so we open a short-lived autocommit
        # connection just for these two statements.
        with bind.engine.connect().execution_options(isolation_level="AUTOCOMMIT") as autocommit_conn:
            autocommit_conn.execute(sa.text("ALTER TYPE riderequeststatus ADD VALUE IF NOT EXISTS 'AWAITING_COMPLETION'"))
            autocommit_conn.execute(sa.text("ALTER TYPE riderequeststatus ADD VALUE IF NOT EXISTS 'DISPUTED'"))

    # --- fraud_alerts ---
    op.create_table(
        'fraud_alerts',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('alert_type', sa.Enum(
            'UNUSUAL_WITHDRAWAL', 'REPEATED_OTP_FAILURES', 'RAPID_DEVICE_CHANGE',
            'SUSPICIOUS_LOGIN_LOCATION', 'EXCESSIVE_RIDE_CREATION', 'EXCESSIVE_CANCELLATION',
            'ABNORMAL_TRANSACTION_PATTERN', name='fraudalerttype',
        ), nullable=False),
        sa.Column('severity', sa.Enum('LOW', 'MEDIUM', 'HIGH', 'CRITICAL', name='fraudalertseverity'),
                  nullable=False, server_default='MEDIUM'),
        sa.Column('reason', sa.String(length=500), nullable=False),
        sa.Column('status', sa.Enum('OPEN', 'REVIEWING', 'RESOLVED', 'DISMISSED', name='fraudalertstatus'),
                  nullable=False, server_default='OPEN'),
        sa.Column('meta_data', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.Column('resolved_by', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('resolution_notes', sa.String(length=500), nullable=True),
    )
    op.create_index('idx_fraud_user_status', 'fraud_alerts', ['user_id', 'status'])
    op.create_index(op.f('ix_fraud_alerts_user_id'), 'fraud_alerts', ['user_id'])
    op.create_index(op.f('ix_fraud_alerts_created_at'), 'fraud_alerts', ['created_at'])

    # --- driver_kyc ---
    op.create_table(
        'driver_kyc',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('driver_id', sa.Integer(), sa.ForeignKey('drivers.id'), nullable=False),
        sa.Column('government_id_url', sa.String(length=500), nullable=False),
        sa.Column('government_id_type', sa.String(length=50), nullable=True),
        sa.Column('selfie_url', sa.String(length=500), nullable=False),
        sa.Column('drivers_license_url', sa.String(length=500), nullable=False),
        sa.Column('proof_of_ownership_url', sa.String(length=500), nullable=True),
        sa.Column('status', sa.Enum('PENDING', 'APPROVED', 'REJECTED', name='kycstatus'),
                  nullable=False, server_default='PENDING'),
        sa.Column('rejection_reason', sa.String(length=500), nullable=True),
        sa.Column('reviewed_by', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
    )
    op.create_index('idx_kyc_driver_created', 'driver_kyc', ['driver_id', 'created_at'])
    op.create_index(op.f('ix_driver_kyc_driver_id'), 'driver_kyc', ['driver_id'])

    # --- device_tokens ---
    op.create_table(
        'device_tokens',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('token', sa.String(length=500), nullable=False, unique=True),
        sa.Column('platform', sa.String(length=20), nullable=True, server_default='web'),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default=sa.true()),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('last_used_at', sa.DateTime(), nullable=True),
    )
    op.create_index('idx_devicetoken_user', 'device_tokens', ['user_id'])

    # --- notification_logs ---
    op.create_table(
        'notification_logs',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('event', sa.Enum(
            'RIDE_ACCEPTED', 'DRIVER_APPROACHING', 'DRIVER_ARRIVED', 'RIDE_STARTED',
            'RIDE_COMPLETED', 'RIDE_AWAITING_CONFIRMATION', 'DISPUTE_OPENED',
            'DEPOSIT_SUCCESSFUL', 'WITHDRAWAL_APPROVED', 'WITHDRAWAL_FAILED',
            'PASSWORD_CHANGED', 'SUSPICIOUS_LOGIN', 'KYC_APPROVED', 'KYC_REJECTED',
            name='notificationevent',
        ), nullable=False),
        sa.Column('title', sa.String(length=150), nullable=False),
        sa.Column('body', sa.String(length=500), nullable=False),
        sa.Column('data', sa.JSON(), nullable=True),
        sa.Column('delivered', sa.Boolean(), nullable=True, server_default=sa.false()),
        sa.Column('error', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )
    op.create_index('idx_notiflog_user_created', 'notification_logs', ['user_id', 'created_at'])


def downgrade():
    op.drop_table('notification_logs')
    op.drop_table('device_tokens')
    op.drop_table('driver_kyc')
    op.drop_table('fraud_alerts')
    with op.batch_alter_table('ride_requests', schema=None) as batch_op:
        batch_op.drop_column('disputed_at')
        batch_op.drop_column('dispute_reason')
        batch_op.drop_column('completion_deadline')
        batch_op.drop_column('awaiting_completion_at')
        batch_op.drop_column('driver_arrived_at')
        batch_op.drop_column('driver_near_pickup')
