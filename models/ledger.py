"""
models/ledger.py — Double-entry ledger entries (source of financial truth)

Every balance-changing operation creates ledger entries.
Account balance is a CACHE — the ledger is the source of truth.
"""
import enum
from datetime import datetime, timezone
from extensions import db


class EntryType(str, enum.Enum):
    DEBIT = 'DEBIT'    # Money leaving an account
    CREDIT = 'CREDIT'  # Money entering an account


class LedgerEntry(db.Model):
    __tablename__ = 'ledger_entries'

    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(
        db.Integer, db.ForeignKey('transactions.id', ondelete='RESTRICT'),
        nullable=False, index=True,
    )
    account_id = db.Column(
        db.Integer, db.ForeignKey('accounts.id', ondelete='RESTRICT'),
        nullable=False, index=True,
    )

    # ── Financial ─────────────────────────────────────
    entry_type = db.Column(db.Enum(EntryType), nullable=False)
    amount = db.Column(db.Numeric(18, 2), nullable=False)
    balance_after = db.Column(db.Numeric(18, 2), nullable=False)
    currency = db.Column(db.String(3), nullable=False, default='INR')

    # ── Meta ──────────────────────────────────────────
    description = db.Column(db.String(200), nullable=True)

    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self):
        return (
            f'<LedgerEntry {self.entry_type.value} ₹{self.amount} '
            f'Account:{self.account_id} TxnID:{self.transaction_id}>'
        )
