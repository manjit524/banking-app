"""
tests/test_transactions.py — Financial logic tests (most critical)
"""
import pytest
from decimal import Decimal


class TestDeposit:
    def test_deposit_increases_balance(self, db, demo_account):
        from services.transaction_service import TransactionService
        from models.account import Account

        initial = demo_account.balance
        svc = TransactionService()
        txn = svc.deposit(demo_account.id, Decimal('5000.00'), 'Test deposit')

        db.session.refresh(demo_account)
        assert demo_account.balance == initial + Decimal('5000.00')
        assert txn is not None

    def test_deposit_zero_rejected(self, db, demo_account):
        from services.transaction_service import TransactionService
        svc = TransactionService()
        with pytest.raises(Exception):
            svc.deposit(demo_account.id, Decimal('0'), 'Zero deposit')

    def test_deposit_negative_rejected(self, db, demo_account):
        from services.transaction_service import TransactionService
        svc = TransactionService()
        with pytest.raises(Exception):
            svc.deposit(demo_account.id, Decimal('-100'), 'Negative deposit')

    def test_deposit_idempotency(self, db, demo_account):
        """Same idempotency key must not deposit twice."""
        from services.transaction_service import TransactionService
        svc = TransactionService()
        key = 'idem-test-key-001'
        svc.deposit(demo_account.id, Decimal('1000'), 'First', idempotency_key=key)
        initial_balance = demo_account.balance

        db.session.refresh(demo_account)
        balance_after_first = demo_account.balance

        # Second call with same key
        svc.deposit(demo_account.id, Decimal('1000'), 'Duplicate', idempotency_key=key)
        db.session.refresh(demo_account)
        # Balance should NOT change again
        assert demo_account.balance == balance_after_first

    def test_deposit_creates_ledger_entry(self, db, demo_account):
        from services.transaction_service import TransactionService
        from models.ledger import LedgerEntry, EntryType
        svc = TransactionService()
        txn = svc.deposit(demo_account.id, Decimal('2000'), 'Ledger test')
        entries = LedgerEntry.query.filter_by(
            transaction_id=txn.id, account_id=demo_account.id
        ).all()
        assert len(entries) >= 1
        credit = next((e for e in entries if e.entry_type == EntryType.CREDIT), None)
        assert credit is not None
        assert credit.amount == Decimal('2000')


class TestWithdrawal:
    def test_withdrawal_decreases_balance(self, db, demo_account):
        from services.transaction_service import TransactionService
        initial = demo_account.balance
        svc = TransactionService()
        txn = svc.withdraw(demo_account.id, Decimal('1000.00'), 'Test withdrawal')
        db.session.refresh(demo_account)
        assert demo_account.balance == initial - Decimal('1000.00')

    def test_withdrawal_insufficient_balance_rejected(self, db, demo_account):
        from services.transaction_service import TransactionService
        svc = TransactionService()
        with pytest.raises(Exception, match='[Ii]nsufficient'):
            svc.withdraw(demo_account.id, Decimal('999999'), 'Overdraft attempt')

    def test_balance_cannot_go_negative(self, db, demo_account):
        from services.transaction_service import TransactionService
        svc = TransactionService()
        current_balance = demo_account.balance
        with pytest.raises(Exception):
            svc.withdraw(demo_account.id, current_balance + Decimal('1'), 'Negative balance attempt')
        from models import Account
        account = db.session.get(Account, demo_account.id)
        assert account.balance >= Decimal('0')


class TestTransfer:
    def test_transfer_moves_money(self, db, demo_user, bcrypt_inst):
        """Transfer must debit sender and credit receiver."""
        from services.transaction_service import TransactionService
        from services.transfer_service import TransferService
        from models.user import User, UserRole
        from models.account import Account, AccountType, AccountStatus

        # Create receiver
        receiver = User(
            name='Receiver', email='receiver_txn@test.com',
            role=UserRole.USER, is_active=True, email_verified=True,
            password_hash=bcrypt_inst.generate_password_hash('Test@1234'),
            mpin_hash=bcrypt_inst.generate_password_hash('123456'),
        )
        db.session.add(receiver)
        db.session.flush()

        recv_acc = Account(
            user_id=receiver.id, account_type=AccountType.SAVINGS,
            currency='INR', status=AccountStatus.ACTIVE,
            balance=Decimal('0'), available_balance=Decimal('0'),
        )
        db.session.add(recv_acc)

        sender_acc = Account(
            user_id=demo_user.id, account_type=AccountType.SAVINGS,
            currency='INR', status=AccountStatus.ACTIVE,
            balance=Decimal('5000'), available_balance=Decimal('5000'),
        )
        db.session.add(sender_acc)
        db.session.flush()

        svc = TransferService()
        txn = svc.transfer(sender_acc.id, recv_acc.id, Decimal('2000'), 'Test transfer')

        db.session.refresh(sender_acc)
        db.session.refresh(recv_acc)

        assert sender_acc.balance == Decimal('3000')
        assert recv_acc.balance == Decimal('2000')
        assert txn is not None

    def test_transfer_to_self_rejected(self, db, demo_account):
        from services.transfer_service import TransferService
        svc = TransferService()
        with pytest.raises(Exception):
            svc.transfer(demo_account.id, demo_account.id, Decimal('100'), 'Self transfer')

    def test_transfer_insufficient_balance_rejected(self, db, demo_account):
        from services.transfer_service import TransferService
        from models.account import Account, AccountType, AccountStatus
        from models.user import User, UserRole

        other_user = User(
            name='Other', email='other_transfer@test.com', role=UserRole.USER,
            is_active=True, email_verified=True,
            password_hash=b'hash', mpin_hash=b'hash',
        )
        db.session.add(other_user)
        db.session.flush()

        other_acc = Account(
            user_id=other_user.id, account_type=AccountType.SAVINGS,
            currency='INR', status=AccountStatus.ACTIVE,
            balance=Decimal('0'), available_balance=Decimal('0'),
        )
        db.session.add(other_acc)
        db.session.flush()

        svc = TransferService()
        with pytest.raises(Exception, match='[Ii]nsufficient'):
            svc.transfer(demo_account.id, other_acc.id, Decimal('999999'), 'Overdraft')

    def test_no_money_created_in_transfer(self, db, demo_account):
        """The sum of balances must remain constant after transfer."""
        from services.transfer_service import TransferService
        from models.account import Account, AccountType, AccountStatus
        from models.user import User, UserRole

        other_user = User(
            name='OtherConserve', email='conserve@test.com', role=UserRole.USER,
            is_active=True, email_verified=True,
            password_hash=b'hash', mpin_hash=b'hash',
        )
        db.session.add(other_user)
        db.session.flush()

        other_acc = Account(
            user_id=other_user.id, account_type=AccountType.SAVINGS,
            currency='INR', status=AccountStatus.ACTIVE,
            balance=Decimal('1000'), available_balance=Decimal('1000'),
        )
        db.session.add(other_acc)
        db.session.flush()

        total_before = demo_account.balance + other_acc.balance

        svc = TransferService()
        svc.transfer(demo_account.id, other_acc.id, Decimal('500'), 'Conservation test')

        db.session.refresh(demo_account)
        db.session.refresh(other_acc)

        total_after = demo_account.balance + other_acc.balance
        assert total_before == total_after, "Money was created or destroyed!"
