"""production payment/wallet security upgrade

Revision ID: c7f2a9d1e834
Revises: f3a91c2d7e4b
Create Date: 2026-07-14

Adds:
- ride_requests.seats, ride_requests.completion_requested_at
- new RideRequestStatus values: AWAITING_CONFIRMATION, DISPUTED
- wallet_transactions.user_id, ride_id, balance_before, balance_after
- withdrawal_requests.provider_transfer_code, failure_reason
- new WithdrawalStatus values: PROCESSING, COMPLETED, FAILED
- security_logs table

NOTE on enum changes: PostgreSQL requires ALTER TYPE ... ADD VALUE to run
outside a transaction block. This migration uses Alembic's
autocommit_block() for those statements. Postgres does not support removing
enum values, so `downgrade()` for the enum additions is a documented no-op
rather than a real reversal -- if you need to roll back, restore from a
backup taken before this migration instead.
"""
from alembic import op
import sqlalchemy as sa

revision = 'c7f2a9d1e834'
down_revision = 'f3a91c2d7e4b'
branch_labels = None
depends_on = None


def upgrade():
    # --- ride_requests: multi-seat bookings + completion-confirmation flow ---
    # op.add_column('ride_requests', sa.Column('seats', sa.Integer(), nullable=False, server_default='1'))
    # op.add_column('ride_requests', sa.Column('completion_requested_at', sa.DateTime(), nullable=True))
    # op.alter_column('ride_requests', 'seats', server_default=None)

    # --- wallet_transactions: full audit trail (who, which ride, before/after balance) ---
    op.add_column('wallet_transactions', sa.Column('user_id', sa.Integer(), nullable=True))
    op.add_column('wallet_transactions', sa.Column('ride_id', sa.Integer(), nullable=True))
    op.add_column('wallet_transactions', sa.Column('balance_before', sa.Float(), nullable=True))
    op.add_column('wallet_transactions', sa.Column('balance_after', sa.Float(), nullable=True))
    op.create_foreign_key('fk_wallet_txn_user', 'wallet_transactions', 'users', ['user_id'], ['id'])
    op.create_foreign_key('fk_wallet_txn_ride', 'wallet_transactions', 'ride_requests', ['ride_id'], ['id'])

    # --- withdrawal_requests: real payout tracking ---
    op.add_column('withdrawal_requests', sa.Column('provider_transfer_code', sa.String(length=100), nullable=True))
    op.add_column('withdrawal_requests', sa.Column('failure_reason', sa.String(length=255), nullable=True))

    # --- security_logs: append-only audit trail ---
    op.create_table(
        'security_logs',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('action', sa.String(length=50), nullable=False),
        sa.Column('detail', sa.String(length=255), nullable=True),
        sa.Column('ip_address', sa.String(length=64), nullable=True),
        sa.Column('user_agent', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )
    op.create_index('idx_security_log_user', 'security_logs', ['user_id'])
    op.create_index('idx_security_log_action', 'security_logs', ['action'])

    # --- new enum values (must run outside the transaction on Postgres) ---
    with op.get_context().autocommit_block():
        op.execute("ALTER TYPE riderequeststatus ADD VALUE IF NOT EXISTS 'AWAITING_CONFIRMATION'")
        op.execute("ALTER TYPE riderequeststatus ADD VALUE IF NOT EXISTS 'DISPUTED'")
        op.execute("ALTER TYPE withdrawalstatus ADD VALUE IF NOT EXISTS 'PROCESSING'")
        op.execute("ALTER TYPE withdrawalstatus ADD VALUE IF NOT EXISTS 'COMPLETED'")
        op.execute("ALTER TYPE withdrawalstatus ADD VALUE IF NOT EXISTS 'FAILED'")


def downgrade():
    op.drop_index('idx_security_log_action', table_name='security_logs')
    op.drop_index('idx_security_log_user', table_name='security_logs')
    op.drop_table('security_logs')

    op.drop_column('withdrawal_requests', 'failure_reason')
    op.drop_column('withdrawal_requests', 'provider_transfer_code')

    op.drop_constraint('fk_wallet_txn_ride', 'wallet_transactions', type_='foreignkey')
    op.drop_constraint('fk_wallet_txn_user', 'wallet_transactions', type_='foreignkey')
    op.drop_column('wallet_transactions', 'balance_after')
    op.drop_column('wallet_transactions', 'balance_before')
    op.drop_column('wallet_transactions', 'ride_id')
    op.drop_column('wallet_transactions', 'user_id')

    op.drop_column('ride_requests', 'completion_requested_at')
    op.drop_column('ride_requests', 'seats')

    # NOTE: the new enum values (AWAITING_CONFIRMATION, DISPUTED, PROCESSING,
    # COMPLETED, FAILED) are intentionally NOT removed here -- Postgres has no
    # ALTER TYPE ... DROP VALUE. If you need a true rollback, restore the
    # database from a pre-migration backup.
