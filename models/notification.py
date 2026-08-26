"""
models/notification.py — In-app and email notifications
"""
import enum
from datetime import datetime, timezone
from extensions import db


class NotificationType(str, enum.Enum):
    TRANSFER_SENT = 'TRANSFER_SENT'
    TRANSFER_RECEIVED = 'TRANSFER_RECEIVED'
    DEPOSIT = 'DEPOSIT'
    WITHDRAWAL = 'WITHDRAWAL'
    BILL_PAYMENT = 'BILL_PAYMENT'
    BILL_DUE = 'BILL_DUE'
    LOGIN = 'LOGIN'
    PASSWORD_CHANGED = 'PASSWORD_CHANGED'
    NEW_DEVICE = 'NEW_DEVICE'
    SECURITY_ALERT = 'SECURITY_ALERT'
    TRANSACTION_FAILED = 'TRANSACTION_FAILED'
    SCHEDULED_PAYMENT = 'SCHEDULED_PAYMENT'
    ACCOUNT_FROZEN = 'ACCOUNT_FROZEN'
    CARD_FROZEN = 'CARD_FROZEN'
    GENERAL = 'GENERAL'


class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False, index=True,
    )
    transaction_id = db.Column(
        db.Integer, db.ForeignKey('transactions.id', ondelete='SET NULL'),
        nullable=True,
    )

    type = db.Column(db.Enum(NotificationType), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    message = db.Column(db.String(500), nullable=False)
    is_read = db.Column(db.Boolean, nullable=False, default=False, index=True)

    # For SSE delivery tracking
    delivered_via_sse = db.Column(db.Boolean, nullable=False, default=False)

    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )

    @property
    def icon_class(self):
        mapping = {
            NotificationType.TRANSFER_SENT: 'fa-paper-plane text-primary',
            NotificationType.TRANSFER_RECEIVED: 'fa-arrow-down text-success',
            NotificationType.DEPOSIT: 'fa-plus-circle text-success',
            NotificationType.WITHDRAWAL: 'fa-minus-circle text-warning',
            NotificationType.BILL_PAYMENT: 'fa-file-invoice text-info',
            NotificationType.BILL_DUE: 'fa-clock text-warning',
            NotificationType.LOGIN: 'fa-right-to-bracket text-secondary',
            NotificationType.PASSWORD_CHANGED: 'fa-lock text-warning',
            NotificationType.NEW_DEVICE: 'fa-mobile text-danger',
            NotificationType.SECURITY_ALERT: 'fa-shield-halved text-danger',
            NotificationType.TRANSACTION_FAILED: 'fa-circle-xmark text-danger',
            NotificationType.SCHEDULED_PAYMENT: 'fa-calendar-check text-info',
            NotificationType.ACCOUNT_FROZEN: 'fa-snowflake text-info',
            NotificationType.CARD_FROZEN: 'fa-credit-card text-info',
            NotificationType.GENERAL: 'fa-bell text-secondary',
        }
        return mapping.get(self.type, 'fa-bell text-secondary')

    @property
    def time_ago(self):
        now = datetime.now(timezone.utc)
        diff = now - self.created_at
        seconds = int(diff.total_seconds())
        if seconds < 60:
            return 'just now'
        elif seconds < 3600:
            return f'{seconds // 60}m ago'
        elif seconds < 86400:
            return f'{seconds // 3600}h ago'
        else:
            return f'{seconds // 86400}d ago'

    def __repr__(self):
        return f'<Notification {self.type.value} user:{self.user_id} read:{self.is_read}>'
