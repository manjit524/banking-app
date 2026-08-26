"""
config.py — NexusBank Configuration Classes
"""
import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


class Config:
    # ── Core ──────────────────────────────────────────
    SECRET_KEY = os.environ.get('SECRET_KEY', 'fallback-secret-change-me')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }

    # ── Session / Cookie ──────────────────────────────
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    REMEMBER_COOKIE_DURATION = timedelta(days=7)
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SAMESITE = 'Lax'

    # ── CSRF ─────────────────────────────────────────
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600

    # ── Rate Limiting ─────────────────────────────────
    RATELIMIT_DEFAULT = "500 per day;100 per hour"
    RATELIMIT_STORAGE_URL = "memory://"
    RATELIMIT_HEADERS_ENABLED = True

    # ── Mail ─────────────────────────────────────────
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', '1') == '1'
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get(
        'MAIL_DEFAULT_SENDER', 'NexusBank <noreply@nexusbank.com>'
    )

    # ── App Settings ──────────────────────────────────
    APP_NAME = os.environ.get('APP_NAME', 'NexusBank')
    APP_URL = os.environ.get('APP_URL', 'http://127.0.0.1:5000')
    APP_CURRENCY = '₹'
    APP_CURRENCY_CODE = 'INR'
    DEMO_MODE = os.environ.get('DEMO_MODE', '1') == '1'

    # ── Pagination ────────────────────────────────────
    TRANSACTIONS_PER_PAGE = 20
    USERS_PER_PAGE = 25

    # ── Security ──────────────────────────────────────
    MAX_LOGIN_ATTEMPTS = 5
    ACCOUNT_LOCKOUT_MINUTES = 30
    OTP_EXPIRY_MINUTES = 10

    # ── Admin Seed ────────────────────────────────────
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'admin@nexusbank.com')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'Admin@1234')
    ADMIN_NAME = os.environ.get('ADMIN_NAME', 'Super Admin')
    ADMIN_MPIN = os.environ.get('ADMIN_MPIN', '123456')

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', 'sqlite:///nexusbank.db'
    )
    SESSION_COOKIE_SECURE = False
    REMEMBER_COOKIE_SECURE = False
    # More verbose SQL logging in dev
    SQLALCHEMY_ECHO = False


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    RATELIMIT_DEFAULT = "200 per day;50 per hour"

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        # Log to stderr in production
        import logging
        from logging import StreamHandler
        file_handler = StreamHandler()
        file_handler.setLevel(logging.WARNING)
        app.logger.addHandler(file_handler)


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SESSION_COOKIE_SECURE = False
    MAIL_SUPPRESS_SEND = True


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig,
}
