"""
seed.py — NexusBank seed data for development
Run: flask seed-db
"""
import os
import random
from datetime import datetime, date, timezone, timedelta
from decimal import Decimal
import click
from flask import Flask
from flask.cli import with_appcontext

def run_seed(app: Flask):
    from extensions import db
    from flask_bcrypt import Bcrypt

    bcrypt = Bcrypt(app)

    from models.user import User, UserRole
    from models.account import Account, AccountType, AccountStatus
    from models.transaction import Transaction, TransactionType, TransactionStatus
    from models.ledger import LedgerEntry, EntryType
    from models.beneficiary import Beneficiary
    from models.card import Card, CardType, CardStatus
    from models.bill import Biller, Bill, BillerCategory, BillStatus
    from models.scheduled_payment import ScheduledPayment, PaymentFrequency, ScheduledPaymentStatus
    from models.notification import Notification, NotificationType
    from models.audit_log import AuditLog, AuditAction

    print('Seeding NexusBank demo data...')

    # ── 1. Demo Users ─────────────────────────────────
    demo_users_data = [
        {
            'name': 'Arjun Sharma',
            'email': 'demo@nexusbank.com',
            'phone': '+91-9876543210',
            'password': 'Demo@1234',
            'mpin': '112233',
        },
        {
            'name': 'Priya Patel',
            'email': 'priya@nexusbank.com',
            'phone': '+91-9123456789',
            'password': 'Demo@1234',
            'mpin': '445566',
        },
        {
            'name': 'Rahul Verma',
            'email': 'rahul@nexusbank.com',
            'phone': '+91-9012345678',
            'password': 'Demo@1234',
            'mpin': '778899',
        },
    ]

    demo_users = []
    for ud in demo_users_data:
        if not User.query.filter_by(email=ud['email']).first():
            u = User(
                name=ud['name'],
                email=ud['email'],
                phone=ud['phone'],
                country='India',
                role=UserRole.USER,
                is_active=True,
                email_verified=True,
                password_hash=bcrypt.generate_password_hash(ud['password']),
                mpin_hash=bcrypt.generate_password_hash(ud['mpin']),
            )
            db.session.add(u)
            db.session.flush()
            demo_users.append(u)
            print(f"  [OK] User: {ud['email']} / {ud['password']} (MPIN: {ud['mpin']})")
        else:
            demo_users.append(User.query.filter_by(email=ud['email']).first())

    db.session.commit()

    # ── 2. Accounts ───────────────────────────────────
    def make_account(user, acc_type, balance, status=AccountStatus.ACTIVE):
        acc = Account(
            user_id=user.id,
            account_type=acc_type,
            currency='INR',
            status=status,
            balance=Decimal(str(balance)),
            available_balance=Decimal(str(balance)),
        )
        db.session.add(acc)
        db.session.flush()
        return acc

    # Arjun: savings + current + wallet
    a1_savings = make_account(demo_users[0], AccountType.SAVINGS, 125000)
    a1_current = make_account(demo_users[0], AccountType.CURRENT, 45000)
    a1_wallet  = make_account(demo_users[0], AccountType.WALLET, 5000)

    # Priya: savings + salary
    a2_savings = make_account(demo_users[1], AccountType.SAVINGS, 88500)
    a2_salary  = make_account(demo_users[1], AccountType.SALARY, 32000)

    # Rahul: savings
    a3_savings = make_account(demo_users[2], AccountType.SAVINGS, 62000)

    db.session.commit()
    print('  [OK] Accounts created')

    # ── 3. Demo Transactions + Ledger ─────────────────
    def record_txn(from_acc, to_acc, txn_type, amount, desc, days_ago=0, category=None):
        amt = Decimal(str(amount))
        txn = Transaction(
            from_account_id=from_acc.id if from_acc else None,
            to_account_id=to_acc.id if to_acc else None,
            type=txn_type,
            amount=amt,
            currency='INR',
            status=TransactionStatus.COMPLETED,
            description=desc,
            category=category,
            is_demo=True,
            completed_at=datetime.now(timezone.utc) - timedelta(days=days_ago),
            created_at=datetime.now(timezone.utc) - timedelta(days=days_ago),
        )
        db.session.add(txn)
        db.session.flush()

        # Ledger entries
        if from_acc:
            le_debit = LedgerEntry(
                transaction_id=txn.id,
                account_id=from_acc.id,
                entry_type=EntryType.DEBIT,
                amount=amt,
                balance_after=from_acc.balance,
                currency='INR',
            )
            db.session.add(le_debit)

        if to_acc:
            le_credit = LedgerEntry(
                transaction_id=txn.id,
                account_id=to_acc.id,
                entry_type=EntryType.CREDIT,
                amount=amt,
                balance_after=to_acc.balance,
                currency='INR',
            )
            db.session.add(le_credit)

        return txn

    # Sample transactions (past 30 days)
    record_txn(None, a1_savings, TransactionType.DEPOSIT, 50000, 'Opening Balance', 30, 'Income')
    record_txn(None, a1_savings, TransactionType.DEPOSIT, 75000, 'Salary Credit - July', 15, 'Income')
    record_txn(a1_savings, None, TransactionType.WITHDRAWAL, 12000, 'ATM Withdrawal', 14, 'Cash')
    record_txn(a1_savings, a2_savings, TransactionType.TRANSFER, 10000, 'Rent Payment', 10, 'Bills')
    record_txn(None, a1_savings, TransactionType.DEPOSIT, 5000, 'Freelance Income', 7, 'Income')
    record_txn(a1_savings, None, TransactionType.WITHDRAWAL, 2500, 'Grocery Shopping', 5, 'Food')
    record_txn(a1_savings, a3_savings, TransactionType.TRANSFER, 8000, 'Split Bill - Dinner', 3, 'Food')
    record_txn(None, a2_savings, TransactionType.DEPOSIT, 88500, 'Opening Balance', 30, 'Income')
    record_txn(None, a2_salary, TransactionType.DEPOSIT, 32000, 'Monthly Salary', 20, 'Income')
    record_txn(a2_savings, None, TransactionType.WITHDRAWAL, 5000, 'Shopping', 8, 'Shopping')
    record_txn(None, a3_savings, TransactionType.DEPOSIT, 62000, 'Opening Balance', 25, 'Income')

    db.session.commit()
    print('  [OK] Demo transactions created')

    # ── 4. Billers ────────────────────────────────────
    billers_data = [
        ('BESCOM - Electricity', BillerCategory.ELECTRICITY, 'fa-bolt'),
        ('BWSSB - Water', BillerCategory.WATER, 'fa-droplet'),
        ('Indane Gas', BillerCategory.GAS, 'fa-fire'),
        ('Airtel Broadband', BillerCategory.INTERNET, 'fa-wifi'),
        ('Jio Mobile', BillerCategory.MOBILE, 'fa-mobile'),
        ('LIC Insurance', BillerCategory.INSURANCE, 'fa-shield-halved'),
        ('Netflix', BillerCategory.SUBSCRIPTION, 'fa-tv'),
        ('Amazon Prime', BillerCategory.SUBSCRIPTION, 'fa-play'),
        ('HDFC Credit Card', BillerCategory.CREDIT_CARD, 'fa-credit-card'),
    ]
    billers = []
    for name, cat, icon in billers_data:
        if not Biller.query.filter_by(name=name).first():
            b = Biller(name=name, category=cat, logo_icon=icon, is_active=True)
            db.session.add(b)
            db.session.flush()
            billers.append(b)

    db.session.commit()
    print('  [OK] Billers seeded')

    # ── 5. Beneficiaries ──────────────────────────────
    if not Beneficiary.query.filter_by(user_id=demo_users[0].id).first():
        bene1 = Beneficiary(
            user_id=demo_users[0].id,
            name='Priya Patel',
            nickname='Priya',
            bank_name='NexusBank',
            account_number=a2_savings.account_number,
            linked_account_id=a2_savings.id,
            is_verified=True,
            is_favorite=True,
        )
        bene2 = Beneficiary(
            user_id=demo_users[0].id,
            name='Rahul Verma',
            nickname='Rahul',
            bank_name='NexusBank',
            account_number=a3_savings.account_number,
            linked_account_id=a3_savings.id,
            is_verified=True,
            is_favorite=False,
        )
        bene3 = Beneficiary(
            user_id=demo_users[0].id,
            name='External Account',
            bank_name='SBI',
            account_number='SBI000123456789',
            ifsc_code='SBIN0001234',
            is_verified=False,
        )
        db.session.add_all([bene1, bene2, bene3])

    db.session.commit()
    print('  [OK] Beneficiaries seeded')

    # ── 6. Virtual Cards ──────────────────────────────
    if not Card.query.filter_by(account_id=a1_savings.id).first():
        import hashlib
        raw_number = '4111111111111234'  # DEMO Visa number
        card = Card(
            account_id=a1_savings.id,
            card_number_hash=hashlib.sha256(raw_number.encode()).hexdigest(),
            card_number_last4='1234',
            card_number_masked='**** **** **** 1234',
            expiry_month=12,
            expiry_year=2028,
            card_holder_name=demo_users[0].name.upper(),
            card_type=CardType.VIRTUAL_DEBIT,
            card_network='VISA',
            status=CardStatus.ACTIVE,
        )
        db.session.add(card)

    db.session.commit()
    print('  [OK] Virtual card created')

    # ── 7. Scheduled Payment ──────────────────────────
    if not ScheduledPayment.query.filter_by(user_id=demo_users[0].id).first():
        sp = ScheduledPayment(
            user_id=demo_users[0].id,
            from_account_id=a1_savings.id,
            to_account_id=a2_savings.id,
            amount=Decimal('5000'),
            description='Monthly Rent to Priya',
            frequency=PaymentFrequency.MONTHLY,
            start_date=date.today(),
            next_run_date=date.today().replace(day=1) + timedelta(days=32),
            status=ScheduledPaymentStatus.ACTIVE,
        )
        db.session.add(sp)

    db.session.commit()
    print('  [OK] Scheduled payment created')

    # ── 8. Notifications ──────────────────────────────
    if not Notification.query.filter_by(user_id=demo_users[0].id).first():
        notifications = [
            Notification(
                user_id=demo_users[0].id,
                type=NotificationType.DEPOSIT,
                title='Salary Credited',
                message='Rs. 75,000 has been credited to your Savings account.',
                is_read=False,
            ),
            Notification(
                user_id=demo_users[0].id,
                type=NotificationType.TRANSFER_SENT,
                title='Transfer Successful',
                message='Rs. 10,000 transferred to Priya Patel successfully.',
                is_read=True,
            ),
            Notification(
                user_id=demo_users[0].id,
                type=NotificationType.SECURITY_ALERT,
                title='Welcome to NexusBank DEMO',
                message='You are in demo/sandbox mode. All transactions are simulated.',
                is_read=False,
            ),
        ]
        db.session.add_all(notifications)

    db.session.commit()
    print('\n NexusBank seed data complete!\n')
    print('+--------------------------------------+')
    print('|       DEMO CREDENTIALS               |')
    print('+--------------------------------------+')
    print('|  USER 1  demo@nexusbank.com          |')
    print('|          Password: Demo@1234         |')
    print('|          MPIN: 112233                |')
    print('+--------------------------------------+')
    print('|  USER 2  priya@nexusbank.com         |')
    print('|          Password: Demo@1234         |')
    print('|          MPIN: 445566                |')
    print('+--------------------------------------+')
    print('|  USER 3  rahul@nexusbank.com         |')
    print('|          Password: Demo@1234         |')
    print('|          MPIN: 778899                |')
    print('+--------------------------------------+')

def register_commands(app: Flask):
    @app.cli.command('seed-db')
    @click.option('--reset', is_flag=True, help='Drop all tables and recreate before seeding')
    @with_appcontext
    def seed_db(reset):
        """Seed the database with demo data."""
        from extensions import db
        if reset:
            click.echo('Dropping all tables...')
            db.drop_all()
            click.echo('Creating tables...')
            db.create_all()
        run_seed(app)

    @app.cli.command('create-db')
    @with_appcontext
    def create_db():
        """Create database tables without seeding."""
        from extensions import db
        db.create_all()
        click.echo('[OK] Database tables created.')
