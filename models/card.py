"""
models/card.py — Virtual/physical card (demo simulation)
"""
import enum
import random
import string
from datetime import datetime, date, timezone
from dateutil.relativedelta import relativedelta
from extensions import db


class CardType(str, enum.Enum):
    VIRTUAL_DEBIT = 'Virtual Debit'
    PHYSICAL_DEBIT = 'Physical Debit'


class CardStatus(str, enum.Enum):
    ACTIVE = 'ACTIVE'
    FROZEN = 'FROZEN'
    BLOCKED = 'BLOCKED'
    EXPIRED = 'EXPIRED'
    PENDING = 'PENDING'


def generate_card_number():
    """Generate a 16-digit demo card number (never real)."""
    return ''.join(random.choices(string.digits, k=16))


def generate_cvv():
    """Generate a 3-digit demo CVV (never stored in plaintext in prod)."""
    return ''.join(random.choices(string.digits, k=3))


class Card(db.Model):
    __tablename__ = 'cards'

    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(
        db.Integer, db.ForeignKey('accounts.id', ondelete='CASCADE'),
        nullable=False, index=True,
    )

    # ── Card Details (DEMO — never store real card data this way) ─────
    card_number_hash = db.Column(db.String(64), nullable=False)   # hashed
    card_number_last4 = db.Column(db.String(4), nullable=False)
    card_number_masked = db.Column(db.String(19), nullable=False)  # **** **** **** 1234
    expiry_month = db.Column(db.Integer, nullable=False)
    expiry_year = db.Column(db.Integer, nullable=False)
    card_holder_name = db.Column(db.String(120), nullable=False)
    card_type = db.Column(db.Enum(CardType), nullable=False, default=CardType.VIRTUAL_DEBIT)
    card_network = db.Column(db.String(20), nullable=False, default='VISA')

    # ── Status & Controls ─────────────────────────────
    status = db.Column(db.Enum(CardStatus), nullable=False, default=CardStatus.ACTIVE)
    is_frozen = db.Column(db.Boolean, nullable=False, default=False)
    online_payments_enabled = db.Column(db.Boolean, nullable=False, default=True)
    international_payments_enabled = db.Column(db.Boolean, nullable=False, default=False)
    contactless_enabled = db.Column(db.Boolean, nullable=False, default=True)
    daily_limit = db.Column(db.Numeric(18, 2), nullable=True, default=50000)

    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    @property
    def expiry_display(self):
        return f'{self.expiry_month:02d}/{str(self.expiry_year)[-2:]}'

    @property
    def is_expired(self):
        today = date.today()
        return date(self.expiry_year, self.expiry_month, 1) < date(today.year, today.month, 1)

    @property
    def effective_status(self):
        if self.is_frozen:
            return CardStatus.FROZEN
        if self.is_expired:
            return CardStatus.EXPIRED
        return self.status

    def __repr__(self):
        return f'<Card {self.card_number_masked} [{self.card_type.value}]>'
