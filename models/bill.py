"""
models/bill.py — Billers and bill payment records
"""
import enum
from datetime import datetime, timezone
from extensions import db


class BillerCategory(str, enum.Enum):
    ELECTRICITY = 'Electricity'
    WATER = 'Water'
    GAS = 'Gas'
    INTERNET = 'Internet'
    MOBILE = 'Mobile'
    INSURANCE = 'Insurance'
    EDUCATION = 'Education'
    CREDIT_CARD = 'Credit Card'
    SUBSCRIPTION = 'Subscription'
    OTHER = 'Other'


class BillStatus(str, enum.Enum):
    PENDING = 'PENDING'
    PAID = 'PAID'
    OVERDUE = 'OVERDUE'
    FAILED = 'FAILED'
    CANCELLED = 'CANCELLED'


class Biller(db.Model):
    __tablename__ = 'billers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    category = db.Column(db.Enum(BillerCategory), nullable=False)
    account_number = db.Column(db.String(30), nullable=True)
    description = db.Column(db.String(300), nullable=True)
    logo_icon = db.Column(db.String(60), nullable=True, default='fa-file-invoice')
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    bills = db.relationship('Bill', backref='biller', lazy='dynamic')

    def __repr__(self):
        return f'<Biller {self.name} [{self.category.value}]>'


class Bill(db.Model):
    __tablename__ = 'bills'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False, index=True,
    )
    biller_id = db.Column(
        db.Integer, db.ForeignKey('billers.id', ondelete='RESTRICT'),
        nullable=False,
    )
    from_account_id = db.Column(
        db.Integer, db.ForeignKey('accounts.id', ondelete='RESTRICT'),
        nullable=True,
    )
    transaction_id = db.Column(
        db.Integer, db.ForeignKey('transactions.id', ondelete='SET NULL'),
        nullable=True,
    )

    consumer_number = db.Column(db.String(50), nullable=True)  # meter/subscriber ID
    amount = db.Column(db.Numeric(18, 2), nullable=False)
    due_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.Enum(BillStatus), nullable=False, default=BillStatus.PENDING)
    notes = db.Column(db.String(200), nullable=True)

    paid_at = db.Column(db.DateTime(timezone=True), nullable=True)
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    from_account = db.relationship('Account', foreign_keys=[from_account_id])
    transaction = db.relationship('Transaction', foreign_keys=[transaction_id])

    @property
    def is_overdue(self):
        from datetime import date
        if self.due_date and self.status == BillStatus.PENDING:
            return self.due_date < date.today()
        return False

    def __repr__(self):
        return f'<Bill {self.id} ₹{self.amount} [{self.status.value}]>'
