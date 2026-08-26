from models import Transaction, LedgerEntry, Account
from extensions import db
from datetime import datetime
from decimal import Decimal

class TransferService:
    @staticmethod
    def transfer(from_account_id, to_account_id, amount=None, description=None, reference=None, idempotency_key=None, beneficiary_id=None):
        try:
            if isinstance(to_account_id, dict):
                # Called as transfer(user_id, data_dict)
                user_id = from_account_id
                data = to_account_id
                
                from models import User
                user = db.session.get(User, user_id)
                if not user:
                    raise ValueError("User not found")
                
                mpin = data.get('mpin')
                from services.auth_service import AuthService
                if not AuthService.verify_mpin(user, mpin):
                    raise ValueError("Invalid MPIN")
                
                from_account_id = int(data.get('from_account_id'))
                amount = Decimal(str(data.get('amount')))
                description = data.get('description')
                reference = data.get('reference')
                idempotency_key = data.get('idempotency_key')
                beneficiary_id = data.get('beneficiary_id')
                
                to_account_number = data.get('to_account_number')
                target_account_id = data.get('to_account_id')
                if target_account_id:
                    to_account_id = int(target_account_id)
                elif to_account_number:
                    to_acc = Account.query.filter_by(account_number=to_account_number).first()
                    if not to_acc:
                        raise ValueError("Recipient account not found")
                    to_account_id = to_acc.id
                else:
                    raise ValueError("Recipient account info missing")

            if idempotency_key:
                existing = Transaction.query.filter_by(idempotency_key=idempotency_key).first()
                if existing:
                    return existing

            if from_account_id == to_account_id:
                raise ValueError("Cannot transfer to the same account")

            # Lock accounts in consistent order to prevent deadlocks
            first_id, second_id = sorted([from_account_id, to_account_id])
            
            first_account = db.session.query(Account).with_for_update().get(first_id)
            second_account = db.session.query(Account).with_for_update().get(second_id)

            if first_id == from_account_id:
                from_account, to_account = first_account, second_account
            else:
                from_account, to_account = second_account, first_account

            if not from_account or from_account.status != 'ACTIVE':
                raise ValueError("From account invalid or inactive")
            if not to_account or to_account.status != 'ACTIVE':
                raise ValueError("To account invalid or inactive")

            if from_account.available_balance < Decimal(amount):
                raise ValueError("Insufficient funds")

            txn = Transaction(
                from_account_id=from_account_id,
                to_account_id=to_account_id,
                type='TRANSFER',
                amount=Decimal(amount),
                description=description,
                reference=reference,
                idempotency_key=idempotency_key,
                status='PROCESSING'
            )
            db.session.add(txn)
            db.session.flush()

            # Update balances
            from_account.balance -= Decimal(amount)
            from_account.available_balance -= Decimal(amount)
            to_account.balance += Decimal(amount)
            to_account.available_balance += Decimal(amount)

            ledger_debit = LedgerEntry(
                transaction_id=txn.id,
                account_id=from_account_id,
                amount=Decimal(amount),
                entry_type='DEBIT',
                balance_after=from_account.balance
            )
            db.session.add(ledger_debit)

            ledger_credit = LedgerEntry(
                transaction_id=txn.id,
                account_id=to_account_id,
                amount=Decimal(amount),
                entry_type='CREDIT',
                balance_after=to_account.balance
            )
            db.session.add(ledger_credit)

            txn.status = 'COMPLETED'
            txn.completed_at = datetime.utcnow()

            db.session.commit()
            return txn
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def verify_beneficiary_account(account_number):
        account = Account.query.filter_by(account_number=account_number).first()
        return account
