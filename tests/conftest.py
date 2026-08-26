"""
tests/conftest.py — pytest fixtures for NexusBank
"""
import pytest
from app import create_app
from extensions import db as _db
from flask_bcrypt import Bcrypt


@pytest.fixture(scope='session')
def app():
    """Create application for testing."""
    app = create_app('testing')
    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()


@pytest.fixture(scope='function')
def db(app):
    """Provide a fresh DB for each test."""
    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def bcrypt_inst(app):
    return Bcrypt(app)


@pytest.fixture
def admin_user(db, bcrypt_inst):
    from models.user import User, UserRole
    u = User(
        name='Test Admin',
        email='admin_test@nexusbank.com',
        role=UserRole.ADMIN,
        is_active=True,
        email_verified=True,
        password_hash=bcrypt_inst.generate_password_hash('Admin@1234'),
        mpin_hash=bcrypt_inst.generate_password_hash('123456'),
    )
    db.session.add(u)
    db.session.commit()
    return u


@pytest.fixture
def demo_user(db, bcrypt_inst):
    from models.user import User, UserRole
    u = User(
        name='Test User',
        email='user_test@nexusbank.com',
        role=UserRole.USER,
        is_active=True,
        email_verified=True,
        password_hash=bcrypt_inst.generate_password_hash('Demo@1234'),
        mpin_hash=bcrypt_inst.generate_password_hash('112233'),
    )
    db.session.add(u)
    db.session.commit()
    return u


@pytest.fixture
def demo_account(db, demo_user):
    from models.account import Account, AccountType, AccountStatus
    from decimal import Decimal
    acc = Account(
        user_id=demo_user.id,
        account_type=AccountType.SAVINGS,
        currency='INR',
        status=AccountStatus.ACTIVE,
        balance=Decimal('10000.00'),
        available_balance=Decimal('10000.00'),
    )
    db.session.add(acc)
    db.session.commit()
    return acc
