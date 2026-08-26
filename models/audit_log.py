"""
models/audit_log.py — Immutable audit trail for all significant actions
"""
import enum
from datetime import datetime, timezone
from extensions import db


class AuditAction(str, enum.Enum):
    # Auth
    LOGIN_SUCCESS = 'LOGIN_SUCCESS'
    LOGIN_FAILED = 'LOGIN_FAILED'
    LOGOUT = 'LOGOUT'
    PASSWORD_CHANGED = 'PASSWORD_CHANGED'
    PASSWORD_RESET_REQUESTED = 'PASSWORD_RESET_REQUESTED'
    MPIN_CHANGED = 'MPIN_CHANGED'
    ACCOUNT_LOCKED = 'ACCOUNT_LOCKED'
    # Profile
    PROFILE_UPDATED = 'PROFILE_UPDATED'
    EMAIL_VERIFIED = 'EMAIL_VERIFIED'
    # Financial
    DEPOSIT = 'DEPOSIT'
    WITHDRAWAL = 'WITHDRAWAL'
    TRANSFER_SENT = 'TRANSFER_SENT'
    TRANSFER_RECEIVED = 'TRANSFER_RECEIVED'
    BILL_PAID = 'BILL_PAID'
    SCHEDULED_PAYMENT_CREATED = 'SCHEDULED_PAYMENT_CREATED'
    SCHEDULED_PAYMENT_CANCELLED = 'SCHEDULED_PAYMENT_CANCELLED'
    # Beneficiary
    BENEFICIARY_ADDED = 'BENEFICIARY_ADDED'
    BENEFICIARY_DELETED = 'BENEFICIARY_DELETED'
    BENEFICIARY_UPDATED = 'BENEFICIARY_UPDATED'
    # Card
    CARD_FROZEN = 'CARD_FROZEN'
    CARD_UNFROZEN = 'CARD_UNFROZEN'
    # Admin
    ADMIN_USER_SUSPENDED = 'ADMIN_USER_SUSPENDED'
    ADMIN_USER_ACTIVATED = 'ADMIN_USER_ACTIVATED'
    ADMIN_ACCOUNT_FROZEN = 'ADMIN_ACCOUNT_FROZEN'
    ADMIN_TRANSACTION_REVERSED = 'ADMIN_TRANSACTION_REVERSED'
    ADMIN_VIEWED_USER = 'ADMIN_VIEWED_USER'
    # Security
    SUSPICIOUS_ACTIVITY = 'SUSPICIOUS_ACTIVITY'


class AuditLog(db.Model):
    __tablename__ = 'audit_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'),
        nullable=True, index=True,
    )
    # Admin acting on behalf of another user
    actor_id = db.Column(
        db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'),
        nullable=True,
    )

    action = db.Column(db.Enum(AuditAction), nullable=False, index=True)
    resource_type = db.Column(db.String(50), nullable=True)   # 'transaction', 'account' etc.
    resource_id = db.Column(db.String(50), nullable=True)
    description = db.Column(db.String(500), nullable=True)

    ip_address = db.Column(db.String(50), nullable=True)
    user_agent = db.Column(db.String(300), nullable=True)
    result = db.Column(db.String(20), nullable=False, default='SUCCESS')  # SUCCESS | FAILURE

    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )

    # Relationships
    actor = db.relationship('User', foreign_keys=[actor_id])

    def __repr__(self):
        return f'<AuditLog {self.action.value} user:{self.user_id} [{self.result}]>'
