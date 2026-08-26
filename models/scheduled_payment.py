"""
models/scheduled_payment.py — Scheduled and recurring payment jobs
"""
import enum
from datetime import datetime, timezone
from extensions import db


class PaymentFrequency(str, enum.Enum):
    ONE_TIME = 'ONE_TIME'
    DAILY = 'DAILY'
    WEEKLY = 'WEEKLY'
    MONTHLY = 'MONTHLY'
    CUSTOM = 'CUSTOM'


class ScheduledPaymentStatus(str, enum.Enum):
    ACTIVE = 'ACTIVE'
    PAUSED = 'PAUSED'
    COMPLETED = 'COMPLETED'
    CANCELLED = 'CANCELLED'
    FAILED = 'FAILED'


class ScheduledPayment(db.Model):
    __tablename__ = 'scheduled_payments'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False, index=True,
    )
    from_account_id = db.Column(
        db.Integer, db.ForeignKey('accounts.id', ondelete='RESTRICT'),
        nullable=False,
    )
    # Target: either a beneficiary or an account
    beneficiary_id = db.Column(
        db.Integer, db.ForeignKey('beneficiaries.id', ondelete='SET NULL'),
        nullable=True,
    )
    to_account_id = db.Column(
        db.Integer, db.ForeignKey('accounts.id', ondelete='SET NULL'),
        nullable=True,
    )

    # ── Payment Details ───────────────────────────────
    amount = db.Column(db.Numeric(18, 2), nullable=False)
    description = db.Column(db.String(200), nullable=True)
    reference = db.Column(db.String(100), nullable=True)

    # ── Schedule ──────────────────────────────────────
    frequency = db.Column(
        db.Enum(PaymentFrequency), nullable=False, default=PaymentFrequency.ONE_TIME
    )
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=True)
    next_run_date = db.Column(db.Date, nullable=False)
    last_run_date = db.Column(db.Date, nullable=True)
    run_count = db.Column(db.Integer, nullable=False, default=0)

    status = db.Column(
        db.Enum(ScheduledPaymentStatus),
        nullable=False,
        default=ScheduledPaymentStatus.ACTIVE,
    )
    failure_reason = db.Column(db.String(300), nullable=True)

    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # ── Relationships ─────────────────────────────────
    from_account = db.relationship('Account', foreign_keys=[from_account_id])
    to_account = db.relationship('Account', foreign_keys=[to_account_id])
    beneficiary = db.relationship('Beneficiary', foreign_keys=[beneficiary_id])

    def __repr__(self):
        return (
            f'<ScheduledPayment {self.id} ₹{self.amount} '
            f'{self.frequency.value} next:{self.next_run_date}>'
        )
