"""
models/transaction.py — High-level transaction record with full lifecycle
"""
import enum
import uuid
from datetime import datetime, timezone
from extensions import db


class TransactionType(str, enum.Enum):
    DEPOSIT = 'DEPOSIT'
    WITHDRAWAL = 'WITHDRAWAL'
    TRANSFER = 'TRANSFER'
    PAYMENT = 'PAYMENT'
    REFUND = 'REFUND'
    FEE = 'FEE'
    REVERSAL = 'REVERSAL'
    CARD_PAYMENT = 'CARD_PAYMENT'
    BILL_PAYMENT = 'BILL_PAYMENT'
    SCHEDULED = 'SCHEDULED'


class TransactionStatus(str, enum.Enum):
    PENDING = 'PENDING'
    PROCESSING = 'PROCESSING'
    COMPLETED = 'COMPLETED'
    FAILED = 'FAILED'
    REVERSED = 'REVERSED'
    CANCELLED = 'CANCELLED'


def generate_txn_id():
    return f'TXN{uuid.uuid4().hex[:12].upper()}'


class Transaction(db.Model):
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)
    txn_id = db.Column(
        db.String(20), unique=True, nullable=False,
        default=generate_txn_id, index=True,
    )
    # Idempotency — prevents duplicate submissions
    idempotency_key = db.Column(db.String(100), unique=True, nullable=True, index=True)

    # ── Accounts ──────────────────────────────────────
    from_account_id = db.Column(
        db.Integer, db.ForeignKey('accounts.id', ondelete='RESTRICT'),
        nullable=True, index=True,
    )
    to_account_id = db.Column(
        db.Integer, db.ForeignKey('accounts.id', ondelete='RESTRICT'),
        nullable=True, index=True,
    )
    # For external/demo transfers, store target account number
    to_account_number_ext = db.Column(db.String(30), nullable=True)
    to_name_ext = db.Column(db.String(120), nullable=True)

    # ── Financial ─────────────────────────────────────
    amount = db.Column(db.Numeric(18, 2), nullable=False)
    fee = db.Column(db.Numeric(18, 2), nullable=False, default=0)
    currency = db.Column(db.String(3), nullable=False, default='INR')

    # ── Classification ────────────────────────────────
    type = db.Column(db.Enum(TransactionType), nullable=False)
    status = db.Column(
        db.Enum(TransactionStatus),
        nullable=False,
        default=TransactionStatus.PENDING,
        index=True,
    )
    category = db.Column(db.String(50), nullable=True)  # Food, Travel, Bills etc.

    # ── Meta ──────────────────────────────────────────
    description = db.Column(db.String(300), nullable=True)
    reference = db.Column(db.String(100), nullable=True)
    is_demo = db.Column(db.Boolean, nullable=False, default=True)
    failure_reason = db.Column(db.String(300), nullable=True)

    # ── Timestamps ────────────────────────────────────
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    completed_at = db.Column(db.DateTime(timezone=True), nullable=True)

    # ── Relationships ─────────────────────────────────
    from_account = db.relationship(
        'Account', foreign_keys=[from_account_id], backref='sent_transactions'
    )
    to_account = db.relationship(
        'Account', foreign_keys=[to_account_id], backref='received_transactions'
    )
    ledger_entries = db.relationship('LedgerEntry', backref='transaction', lazy='dynamic')

    # ── Properties ────────────────────────────────────
    @property
    def total_amount(self):
        return self.amount + (self.fee or 0)

    @property
    def display_amount(self):
        return f'₹{self.amount:,.2f}'

    @property
    def is_credit(self):
        """True if this transaction increases the to_account balance."""
        return self.type in (
            TransactionType.DEPOSIT, TransactionType.REFUND,
            TransactionType.REVERSAL,
        )

    @property
    def status_badge_class(self):
        mapping = {
            TransactionStatus.COMPLETED: 'success',
            TransactionStatus.PENDING: 'warning',
            TransactionStatus.PROCESSING: 'info',
            TransactionStatus.FAILED: 'danger',
            TransactionStatus.REVERSED: 'secondary',
            TransactionStatus.CANCELLED: 'secondary',
        }
        return mapping.get(self.status, 'secondary')

    def __repr__(self):
        return f'<Transaction {self.txn_id} {self.type.value} ₹{self.amount} [{self.status.value}]>'
