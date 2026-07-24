"""init

Revision ID: 81d3be6bdff9
Revises:
Create Date: 2026-07-09 01:37:19.610934

NOTE: this migration was originally auto-generated against a dev database
that already had most tables created via db.create_all(), so Alembic's
autogenerate diff only picked up the payment-related tables that were new
at the time -- it was missing users/otps/zones/drivers/routes/route_stops/
ride_requests entirely, and even referenced users.id / drivers.id foreign
keys before those tables existed. Rewritten here to create the full schema
in dependency order so a fresh database can actually run `flask db upgrade`.
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '81d3be6bdff9'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # --- users & auth ---
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=120), nullable=False),
        sa.Column('username', sa.String(length=80), nullable=False),
        sa.Column('full_name', sa.String(length=100), nullable=False),
        sa.Column('student_id', sa.String(length=50), nullable=False),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('password_hash', sa.String(length=200), nullable=False),
        sa.Column('role', sa.Enum('STUDENT', 'DRIVER', 'ADMIN', name='userrole'), nullable=False),
        sa.Column('is_verified', sa.Boolean(), nullable=True),
        sa.Column('account_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('last_login', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('username'),
        sa.UniqueConstraint('student_id'),
    )
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_users_email'), ['email'], unique=True)

    op.create_table('otps',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=120), nullable=False),
        sa.Column('otp_code', sa.String(length=6), nullable=False),
        sa.Column('purpose', sa.String(length=20), nullable=False),
        sa.Column('is_used', sa.Boolean(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    with op.batch_alter_table('otps', schema=None) as batch_op:
        batch_op.create_index('idx_otp_user_purpose', ['user_id', 'purpose'], unique=False)
        batch_op.create_index('idx_otp_expires_at', ['expires_at'], unique=False)

    op.create_table('password_reset_tokens',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('token', sa.String(length=100), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('is_used', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('token'),
    )
    with op.batch_alter_table('password_reset_tokens', schema=None) as batch_op:
        batch_op.create_index('idx_token_value', ['token'], unique=False)
        batch_op.create_index('idx_token_expires', ['expires_at'], unique=False)

    # --- zones ---
    op.create_table('zones',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=80), nullable=False),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('lat', sa.Float(), nullable=True),
        sa.Column('lng', sa.Float(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
    )

    # --- drivers (depends on users) ---
    op.create_table('drivers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('vehicle_make', sa.String(length=50), nullable=False),
        sa.Column('vehicle_model', sa.String(length=50), nullable=False),
        sa.Column('vehicle_color', sa.String(length=30), nullable=False),
        sa.Column('plate_number', sa.String(length=20), nullable=False),
        sa.Column('seat_capacity', sa.Integer(), nullable=False),
        sa.Column('license_number', sa.String(length=50), nullable=False),
        sa.Column('status', sa.Enum('PENDING', 'APPROVED', 'REJECTED', 'SUSPENDED', name='driverstatus'), nullable=False),
        sa.Column('approved_by', sa.Integer(), nullable=True),
        sa.Column('approved_at', sa.DateTime(), nullable=True),
        sa.Column('rejection_reason', sa.String(length=255), nullable=True),
        sa.Column('is_online', sa.Boolean(), nullable=True),
        sa.Column('current_lat', sa.Float(), nullable=True),
        sa.Column('current_lng', sa.Float(), nullable=True),
        sa.Column('last_location_update', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['approved_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id'),
        sa.UniqueConstraint('plate_number'),
    )

    # --- routes & stops (depend on drivers, zones) ---
    op.create_table('routes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('driver_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=120), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['driver_id'], ['drivers.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table('route_stops',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('route_id', sa.Integer(), nullable=False),
        sa.Column('zone_id', sa.Integer(), nullable=False),
        sa.Column('sequence', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['route_id'], ['routes.id'], ),
        sa.ForeignKeyConstraint(['zone_id'], ['zones.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )

    # --- ride requests (depend on users, drivers, routes, zones) ---
    op.create_table('ride_requests',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('driver_id', sa.Integer(), nullable=False),
        sa.Column('route_id', sa.Integer(), nullable=False),
        sa.Column('zone_id', sa.Integer(), nullable=False),
        sa.Column('pickup_lat', sa.Float(), nullable=True),
        sa.Column('pickup_lng', sa.Float(), nullable=True),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('status', sa.Enum('PENDING_PAYMENT', 'PENDING', 'ACCEPTED', 'REJECTED', 'ONGOING', 'COMPLETED', 'CANCELLED', name='riderequeststatus'), nullable=False),
        sa.Column('requested_at', sa.DateTime(), nullable=True),
        sa.Column('responded_at', sa.DateTime(), nullable=True),
        sa.Column('picked_up_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['student_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['driver_id'], ['drivers.id'], ),
        sa.ForeignKeyConstraint(['route_id'], ['routes.id'], ),
        sa.ForeignKeyConstraint(['zone_id'], ['zones.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )

    # --- payments / wallet (depend on users, drivers) ---
    op.create_table('payment_webhook_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('provider', sa.String(length=50), nullable=False),
        sa.Column('event_type', sa.String(length=100), nullable=False),
        sa.Column('payload', sa.JSON(), nullable=False),
        sa.Column('processed', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('payments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('provider', sa.String(length=50), nullable=False),
        sa.Column('provider_reference', sa.String(length=100), nullable=False),
        sa.Column('status', sa.Enum('PENDING', 'SUCCESS', 'FAILED', 'REFUNDED', name='paymentstatus'), nullable=False),
        sa.Column('purpose', sa.String(length=100), nullable=True),
        sa.Column('meta_data', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('payments', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_payments_provider_reference'), ['provider_reference'], unique=True)

    op.create_table('wallets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('balance', sa.Float(), nullable=False),
        sa.Column('pending_balance', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    op.create_table('wallet_transactions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('wallet_id', sa.Integer(), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('transaction_type', sa.Enum('DEPOSIT', 'WITHDRAWAL', 'RIDE_PAYMENT', 'RIDE_REFUND', 'DRIVER_EARNING', 'PLATFORM_COMMISSION', name='transactiontype'), nullable=False),
        sa.Column('status', sa.Enum('PENDING', 'SUCCESS', 'FAILED', name='transactionstatus'), nullable=False),
        sa.Column('reference', sa.String(length=100), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['wallet_id'], ['wallets.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('wallet_transactions', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_wallet_transactions_reference'), ['reference'], unique=True)

    op.create_table('withdrawal_requests',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('driver_id', sa.Integer(), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('status', sa.Enum('PENDING', 'APPROVED', 'REJECTED', 'PROCESSED', name='withdrawalstatus'), nullable=False),
        sa.Column('bank_code', sa.String(length=50), nullable=True),
        sa.Column('account_number', sa.String(length=50), nullable=True),
        sa.Column('account_name', sa.String(length=100), nullable=True),
        sa.Column('reference', sa.String(length=100), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('processed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['driver_id'], ['drivers.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('reference')
    )


def downgrade():
    op.drop_table('withdrawal_requests')
    with op.batch_alter_table('wallet_transactions', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_wallet_transactions_reference'))
    op.drop_table('wallet_transactions')
    op.drop_table('wallets')
    with op.batch_alter_table('payments', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_payments_provider_reference'))
    op.drop_table('payments')
    op.drop_table('payment_webhook_logs')
    op.drop_table('ride_requests')
    op.drop_table('route_stops')
    op.drop_table('routes')
    op.drop_table('drivers')
    op.drop_table('zones')
    with op.batch_alter_table('password_reset_tokens', schema=None) as batch_op:
        batch_op.drop_index('idx_token_expires')
        batch_op.drop_index('idx_token_value')
    op.drop_table('password_reset_tokens')
    with op.batch_alter_table('otps', schema=None) as batch_op:
        batch_op.drop_index('idx_otp_expires_at')
        batch_op.drop_index('idx_otp_user_purpose')
    op.drop_table('otps')
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_users_email'))
    op.drop_table('users')
