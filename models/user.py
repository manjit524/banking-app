"""
models/user.py — User model with full profile, security, and RBAC
"""
import enum
from datetime import datetime, timezone
from extensions import db, login_manager
from flask_login import UserMixin


class UserRole(str, enum.Enum):
    USER = 'USER'
    ADMIN = 'ADMIN'
    SUPPORT = 'SUPPORT'
    AUDITOR = 'AUDITOR'


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    # ── Identity ─────────────────────────────────────
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20), nullable=True)
    date_of_birth = db.Column(db.Date, nullable=True)
    address = db.Column(db.String(300), nullable=True)
    country = db.Column(db.String(100), nullable=True, default='India')
    profile_photo = db.Column(db.String(300), nullable=True)

    # ── Security ──────────────────────────────────────
    password_hash = db.Column(db.LargeBinary, nullable=False)
    mpin_hash = db.Column(db.LargeBinary, nullable=True)
    role = db.Column(db.Enum(UserRole), nullable=False, default=UserRole.USER)

    # ── Account Status ────────────────────────────────
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    is_suspended = db.Column(db.Boolean, nullable=False, default=False)
    email_verified = db.Column(db.Boolean, nullable=False, default=False)
    email_verify_token = db.Column(db.String(200), nullable=True)

    # ── Login Protection ──────────────────────────────
    failed_login_attempts = db.Column(db.Integer, nullable=False, default=0)
    locked_until = db.Column(db.DateTime(timezone=True), nullable=True)
    last_login_at = db.Column(db.DateTime(timezone=True), nullable=True)
    last_login_ip = db.Column(db.String(50), nullable=True)

    # ── Password Reset ────────────────────────────────
    reset_token = db.Column(db.String(200), nullable=True)
    reset_token_expiry = db.Column(db.DateTime(timezone=True), nullable=True)

    # ── Preferences ───────────────────────────────────
    preferred_language = db.Column(db.String(10), nullable=False, default='en')
    notify_email = db.Column(db.Boolean, nullable=False, default=True)
    notify_inapp = db.Column(db.Boolean, nullable=False, default=True)

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
    accounts = db.relationship('Account', backref='owner', lazy='dynamic')
    notifications = db.relationship(
        'Notification', backref='user', lazy='dynamic',
        order_by='Notification.created_at.desc()',
    )
    audit_logs = db.relationship('AuditLog', backref='user', lazy='dynamic', foreign_keys='AuditLog.user_id')
    beneficiaries = db.relationship('Beneficiary', backref='user', lazy='dynamic')

    # ── Properties ────────────────────────────────────
    @property
    def is_admin(self):
        return self.role == UserRole.ADMIN

    @property
    def is_auditor(self):
        return self.role in (UserRole.ADMIN, UserRole.AUDITOR)

    @property
    def is_support(self):
        return self.role in (UserRole.ADMIN, UserRole.SUPPORT)

    @property
    def is_locked(self):
        if self.locked_until and self.locked_until > datetime.now(timezone.utc):
            return True
        return False

    @property
    def unread_notification_count(self):
        return self.notifications.filter_by(is_read=False).count()

    def __repr__(self):
        return f'<User {self.id} {self.email} [{self.role.value}]>'


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))
