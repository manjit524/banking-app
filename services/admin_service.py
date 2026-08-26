"""
services/admin_service.py — Administrative management logic
"""
from decimal import Decimal
from datetime import datetime, timezone
from models import User, Transaction, Account, AuditLog
from models.user import UserRole
from models.account import AccountStatus
from models.transaction import TransactionStatus, TransactionType
from models.ledger import LedgerEntry, EntryType
from extensions import db
from sqlalchemy import or_

class AdminService:
    @staticmethod
    def get_all_users(search=None, filter_role=None, page=1, per_page=20):
        query = User.query
        if search:
            query = query.filter(or_(
                User.name.ilike(f'%{search}%'),
                User.email.ilike(f'%{search}%'),
                User.phone.ilike(f'%{search}%')
            ))
        if filter_role:
            query = query.filter(User.role == filter_role)
        return query.paginate(page=page, per_page=per_page, error_out=False)

    @staticmethod
    def get_user_detail(user_id):
        user = db.session.get(User, user_id)
        if not user:
            raise ValueError("User not found")
        return user

    @staticmethod
    def suspend_user(user_id):
        try:
            user = db.session.get(User, user_id)
            if not user:
                raise ValueError("User not found")
            user.is_suspended = True
            db.session.commit()
            return user
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def activate_user(user_id):
        try:
            user = db.session.get(User, user_id)
            if not user:
                raise ValueError("User not found")
            user.is_suspended = False
            db.session.commit()
            return user
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def get_all_transactions(search=None, status_filter=None, page=1, per_page=20):
        query = Transaction.query
        if search:
            query = query.filter(or_(
                Transaction.txn_id.ilike(f'%{search}%'),
                Transaction.description.ilike(f'%{search}%'),
                Transaction.reference.ilike(f'%{search}%')
            ))
        if status_filter:
            query = query.filter(Transaction.status == status_filter)
        return query.order_by(Transaction.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)

    @staticmethod
    def get_transaction_detail(txn_id):
        txn = Transaction.query.filter_by(txn_id=txn_id).first()
        if not txn:
            raise ValueError("Transaction not found")
        return txn

    @staticmethod
    def reverse_transaction(txn_id):
        try:
            txn = Transaction.query.filter_by(txn_id=txn_id).first()
            if not txn:
                raise ValueError("Transaction not found")
            if txn.status != TransactionStatus.COMPLETED:
                raise ValueError("Only completed transactions can be reversed")

            # Check if already reversed
            already_reversed = Transaction.query.filter_by(
                reference=f"REV-{txn.txn_id}", status=TransactionStatus.COMPLETED
            ).first()
            if already_reversed:
                raise ValueError("Transaction is already reversed")

            # Reversal logic: create opposite entries
            rev_txn = Transaction(
                from_account_id=txn.to_account_id,
                to_account_id=txn.from_account_id,
                amount=txn.amount,
                type=TransactionType.REVERSAL,
                status=TransactionStatus.PROCESSING,
                description=f"Reversal of {txn.txn_id}",
                reference=f"REV-{txn.txn_id}",
                is_demo=txn.is_demo
            )
            db.session.add(rev_txn)
            db.session.flush()

            # Adjust accounts
            if txn.from_account_id:
                from_acc = db.session.query(Account).with_for_update().get(txn.from_account_id)
                from_acc.balance += txn.amount
                from_acc.available_balance += txn.amount
                le_credit = LedgerEntry(
                    transaction_id=rev_txn.id,
                    account_id=from_acc.id,
                    entry_type=EntryType.CREDIT,
                    amount=txn.amount,
                    balance_after=from_acc.balance
                )
                db.session.add(le_credit)

            if txn.to_account_id:
                to_acc = db.session.query(Account).with_for_update().get(txn.to_account_id)
                to_acc.balance -= txn.amount
                to_acc.available_balance -= txn.amount
                le_debit = LedgerEntry(
                    transaction_id=rev_txn.id,
                    account_id=to_acc.id,
                    entry_type=EntryType.DEBIT,
                    amount=txn.amount,
                    balance_after=to_acc.balance
                )
                db.session.add(le_debit)

            rev_txn.status = TransactionStatus.COMPLETED
            rev_txn.completed_at = datetime.now(timezone.utc)
            
            # Mark original transaction as reversed too
            txn.status = TransactionStatus.REVERSED
            
            db.session.commit()
            return rev_txn
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def get_all_accounts(search=None, page=1, per_page=20):
        query = Account.query
        if search:
            query = query.filter(Account.account_number.ilike(f'%{search}%'))
        return query.paginate(page=page, per_page=per_page, error_out=False)

    @staticmethod
    def freeze_account(account_id):
        try:
            account = db.session.get(Account, account_id)
            if not account:
                raise ValueError("Account not found")
            account.status = AccountStatus.FROZEN
            db.session.commit()
            return account
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def unfreeze_account(account_id):
        try:
            account = db.session.get(Account, account_id)
            if not account:
                raise ValueError("Account not found")
            account.status = AccountStatus.ACTIVE
            db.session.commit()
            return account
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def get_audit_logs(search=None, page=1, per_page=25):
        query = AuditLog.query
        if search:
            query = query.filter(or_(
                AuditLog.description.ilike(f'%{search}%'),
                AuditLog.ip_address.ilike(f'%{search}%'),
                AuditLog.result.ilike(f'%{search}%')
            ))
        return query.order_by(AuditLog.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)

    @staticmethod
    def get_security_events():
        # Fetch audit logs containing suspicious activities or failures
        from models.audit_log import AuditAction
        return AuditLog.query.filter(or_(
            AuditLog.action == AuditAction.SUSPICIOUS_ACTIVITY,
            AuditLog.result == 'FAILURE'
        )).order_by(AuditLog.created_at.desc()).all()
