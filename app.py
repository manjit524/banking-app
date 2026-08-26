"""
app.py — NexusBank Application Factory
"""
import os
from flask import Flask, render_template, jsonify
from config import config
from extensions import db, login_manager, bcrypt, csrf, limiter, mail, migrate
from sqlalchemy import event
from sqlalchemy.engine import Engine
import sqlite3

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA busy_timeout=5000")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.close()

def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
        if config_name == 'development':
            config_name = 'development'

    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # ── Initialize Extensions ─────────────────────────
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)
    mail.init_app(app)

    # ── Import models so Flask-Migrate finds them ─────
    with app.app_context():
        from models import (  # noqa: F401
            User, Account, Transaction, LedgerEntry,
            Beneficiary, Card, Biller, Bill,
            ScheduledPayment, Notification, AuditLog,
        )

    # ── Zero-Config Auto-Database Setup ───────────────
    with app.app_context():
        db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
        if db_uri.startswith('sqlite:///'):
            db_filename = db_uri.split('sqlite:///')[1]
            if db_filename != ':memory:':
                if not os.path.isabs(db_filename):
                    db_path = os.path.join(app.instance_path, db_filename)
                else:
                    db_path = db_filename
                
                # Check if the database file exists on disk
                if not os.path.exists(db_path):
                    os.makedirs(os.path.dirname(db_path), exist_ok=True)
                    print(f"Database not found. Automatically creating SQLite database at {db_path}...")
                    db.create_all()
                    print("Seeding default database values...")
                    from seed import run_seed
                    run_seed(app)

    # ── Register Blueprints ───────────────────────────
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.accounts import accounts_bp
    from routes.transactions import transactions_bp
    from routes.transfers import transfers_bp
    from routes.beneficiaries import beneficiaries_bp
    from routes.payments import payments_bp
    from routes.cards import cards_bp
    from routes.analytics import analytics_bp
    from routes.notifications import notifications_bp
    from routes.profile import profile_bp
    from routes.api.notifications_api import notifications_api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(accounts_bp)
    app.register_blueprint(transactions_bp)
    app.register_blueprint(transfers_bp)
    app.register_blueprint(beneficiaries_bp)
    app.register_blueprint(payments_bp)
    app.register_blueprint(cards_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(notifications_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(notifications_api_bp)

    # ── Register CLI Commands ─────────────────────────
    from seed import register_commands
    register_commands(app)

    # ── Error Handlers ────────────────────────────────
    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403

    @app.errorhandler(500)
    def server_error(e):
        return render_template('errors/500.html'), 500

    # ── Template Globals ─────────────────────────────
    @app.context_processor
    def inject_globals():
        return {
            'app_name': app.config.get('APP_NAME', 'NexusBank'),
            'currency': app.config.get('APP_CURRENCY', '₹'),
            'demo_mode': app.config.get('DEMO_MODE', True),
        }

    # ── Root redirect ─────────────────────────────────
    @app.route('/')
    def index():
        from flask import redirect, url_for
        from flask_login import current_user
        if current_user.is_authenticated:
            return redirect(url_for('dashboard.index'))
        return redirect(url_for('auth.login'))

    return app