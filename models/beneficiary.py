"""
models/beneficiary.py — Saved beneficiary / payee
"""
from datetime import datetime, timezone
from extensions import db


class Beneficiary(db.Model):
    __tablename__ = 'beneficiaries'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False, index=True,
    )

    # ── Beneficiary Details ───────────────────────────
    name = db.Column(db.String(120), nullable=False)
    nickname = db.Column(db.String(60), nullable=True)
    bank_name = db.Column(db.String(100), nullable=True, default='NexusBank')
    account_number = db.Column(db.String(30), nullable=False)
    ifsc_code = db.Column(db.String(20), nullable=True)  # Bank routing code
    email = db.Column(db.String(150), nullable=True)
    phone = db.Column(db.String(20), nullable=True)

    # ── Status ────────────────────────────────────────
    is_verified = db.Column(db.Boolean, nullable=False, default=False)
    is_favorite = db.Column(db.Boolean, nullable=False, default=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    # For internal NexusBank transfers — link to actual account
    linked_account_id = db.Column(
        db.Integer, db.ForeignKey('accounts.id', ondelete='SET NULL'),
        nullable=True,
    )

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
    linked_account = db.relationship('Account', foreign_keys=[linked_account_id])

    @property
    def display_name(self):
        return self.nickname or self.name

    @property
    def masked_account(self):
        acc = self.account_number
        if len(acc) >= 4:
            return f"{'*' * (len(acc) - 4)}{acc[-4:]}"
        return acc

    def __repr__(self):
        return f'<Beneficiary {self.name} [{self.account_number}]>'
