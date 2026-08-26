"""
models/account.py — Bank Account model (multiple accounts per user)
"""
import enum
import random
import string
from datetime import datetime, timezone
from extensions import db


class AccountType(str, enum.Enum):
    SAVINGS = 'Savings'
    CURRENT = 'Current'
    SALARY = 'Salary'
    WALLET = 'Demo Wallet'


class AccountStatus(str, enum.Enum):
    ACTIVE = 'ACTIVE'
    INACTIVE = 'INACTIVE'
    FROZEN = 'FROZEN'
    CLOSED = 'CLOSED'


def generate_account_number():
    """Generate a 12-digit account number prefixed with 'NXS'."""
    digits = ''.join(random.choices(string.digits, k=12))
    return f'NXS{digits}'


class Account(db.Model):
    __tablename__ = 'accounts'

    id = db.Column(db.Integer, primary_key=True)
    account_number = db.Column(
        db.String(20), unique=True, nullable=False,
        default=generate_account_number, index=True,
    )
    user_id = db.Column(
        db.Integer, db.ForeignKey('users.id', ondelete='RESTRICT'),
        nullable=False, index=True,
    )

    # ── Account Details ───────────────────────────────
    account_type = db.Column(
        db.Enum(AccountType), nullable=False, default=AccountType.SAVINGS
    )
    currency = db.Column(db.String(3), nullable=False, default='INR')
    status = db.Column(
        db.Enum(AccountStatus), nullable=False, default=AccountStatus.ACTIVE
    )
    nickname = db.Column(db.String(60), nullable=True)

    # ── Balance ───────────────────────────────────────
    # NOTE: balance is a cached value derived from ledger entries.
    # Always update via transaction_service to maintain ledger integrity.
    balance = db.Column(db.Numeric(18, 2), nullable=False, default=0)
    available_balance = db.Column(db.Numeric(18, 2), nullable=False, default=0)

    # ── Timestamps ────────────────────────────────────
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
    ledger_entries = db.relationship('LedgerEntry', backref='account', lazy='dynamic')
    cards = db.relationship('Card', backref='account', lazy='dynamic')

    # ── Properties ────────────────────────────────────
    @property
    def masked_account_number(self):
        """Show only last 4 digits: NXS****1234"""
        if len(self.account_number) >= 4:
            return f"{'*' * (len(self.account_number) - 4)}{self.account_number[-4:]}"
        return self.account_number

    @property
    def is_active(self):
        return self.status == AccountStatus.ACTIVE

    @property
    def display_balance(self):
        return f'₹{self.balance:,.2f}'

    def __repr__(self):
        return f'<Account {self.account_number} [{self.account_type.value}] ₹{self.balance}>'
