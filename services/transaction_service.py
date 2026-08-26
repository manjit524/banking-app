from models import Transaction, LedgerEntry, Account
from extensions import db
from datetime import datetime
from decimal import Decimal
from sqlalchemy import desc

class TransactionService:
    @staticmethod
    def deposit(account_id, amount, description=None, idempotency_key=None):
        try:
            if idempotency_key:
                existing = Transaction.query.filter_by(idempotency_key=idempotency_key).first()
                if existing:
                    return existing

            account = db.session.query(Account).with_for_update().get(account_id)
            if not account:
                raise ValueError("Account not found")

            if Decimal(amount) <= 0:
                raise ValueError("Deposit amount must be positive")

            txn = Transaction(
                to_account_id=account_id,
                type='DEPOSIT',
                amount=Decimal(amount),
                description=description,
                idempotency_key=idempotency_key,
                status='PROCESSING'
            )
            db.session.add(txn)
            db.session.flush()

            account.balance += Decimal(amount)
            account.available_balance += Decimal(amount)

            ledger = LedgerEntry(
                transaction_id=txn.id,
                account_id=account_id,
                amount=Decimal(amount),
                entry_type='CREDIT',
                balance_after=account.balance
            )
            db.session.add(ledger)

            txn.status = 'COMPLETED'
            txn.completed_at = datetime.utcnow()

            db.session.commit()
            return txn
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def withdraw(account_id, amount, description=None, idempotency_key=None):
        try:
            if idempotency_key:
                existing = Transaction.query.filter_by(idempotency_key=idempotency_key).first()
                if existing:
                    return existing

            account = db.session.query(Account).with_for_update().get(account_id)
            if not account:
                raise ValueError("Account not found")

            if Decimal(amount) <= 0:
                raise ValueError("Withdrawal amount must be positive")

            if account.available_balance < Decimal(amount):
                raise ValueError("Insufficient funds")

            txn = Transaction(
                from_account_id=account_id,
                type='WITHDRAWAL',
                amount=Decimal(amount),
                description=description,
                idempotency_key=idempotency_key,
                status='PROCESSING'
            )
            db.session.add(txn)
            db.session.flush()

            account.balance -= Decimal(amount)
            account.available_balance -= Decimal(amount)

            ledger = LedgerEntry(
                transaction_id=txn.id,
                account_id=account_id,
                amount=Decimal(amount),
                entry_type='DEBIT',
                balance_after=account.balance
            )
            db.session.add(ledger)

            txn.status = 'COMPLETED'
            txn.completed_at = datetime.utcnow()

            db.session.commit()
            return txn
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def get_transactions(account_id_or_user_id, page=1, per_page=20, type_filter=None, status_filter=None, date_from=None, date_to=None):
        from sqlalchemy import or_, desc
        
        if isinstance(page, dict):
            # Called as get_transactions(user_id, filters_dict)
            filters = page
            page = filters.get('page', 1) or 1
            type_filter = filters.get('type')
            status_filter = filters.get('status')
            date_from = filters.get('date_from')
            date_to = filters.get('date_to')
            search = filters.get('search')
            
            user_accounts = Account.query.filter_by(user_id=account_id_or_user_id).all()
            account_ids = [acc.id for acc in user_accounts]
            if not account_ids:
                return Transaction.query.filter(db.false()).paginate(page=page, per_page=per_page, error_out=False)
                
            query = Transaction.query.filter(or_(
                Transaction.from_account_id.in_(account_ids),
                Transaction.to_account_id.in_(account_ids)
            ))
            
            if search:
                query = query.filter(Transaction.description.ilike(f'%{search}%'))
        else:
            query = Transaction.query.filter(or_(
                Transaction.from_account_id == account_id_or_user_id,
                Transaction.to_account_id == account_id_or_user_id
            ))
            
        if type_filter:
            query = query.filter(Transaction.type == type_filter)
        if status_filter:
            query = query.filter(Transaction.status == status_filter)
        if date_from:
            query = query.filter(Transaction.created_at >= date_from)
        if date_to:
            query = query.filter(Transaction.created_at <= date_to)
            
        return query.order_by(desc(Transaction.created_at)).paginate(page=page, per_page=per_page, error_out=False)

    @staticmethod
    def get_transaction(txn_id, user_id):
        txn = Transaction.query.filter_by(txn_id=txn_id).first()
        if not txn:
            raise ValueError("Transaction not found")
        
        if txn.from_account_id:
            from_account = db.session.get(Account, txn.from_account_id)
            if from_account and from_account.user_id == user_id:
                return txn
        if txn.to_account_id:
            to_account = db.session.get(Account, txn.to_account_id)
            if to_account and to_account.user_id == user_id:
                return txn
                
        raise ValueError("Unauthorized access to transaction")

    @staticmethod
    def get_spending_by_category(user_id, month=None, year=None):
        # Implementation for analytics
        pass

    @staticmethod
    def get_recent_transactions(user_id, limit=5):
        from models import Account, Transaction
        from sqlalchemy import or_, desc
        
        # Get all account IDs of the user
        user_accounts = Account.query.filter_by(user_id=user_id).all()
        account_ids = [acc.id for acc in user_accounts]
        if not account_ids:
            return []
            
        # Get transactions belonging to these accounts
        transactions = Transaction.query.filter(
            or_(
                Transaction.from_account_id.in_(account_ids),
                Transaction.to_account_id.in_(account_ids)
            )
        ).order_by(desc(Transaction.created_at)).limit(limit).all()
        
        return transactions

    @staticmethod
    def get_transaction_by_id(txn_id, user_id):
        return TransactionService.get_transaction(txn_id, user_id)

    @staticmethod
    def generate_receipt_pdf(txn_id, user_id):
        import os
        import tempfile
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib import colors
        
        txn = TransactionService.get_transaction(txn_id, user_id)
        
        fd, pdf_path = tempfile.mkstemp(suffix='.pdf')
        os.close(fd)
        
        doc = SimpleDocTemplate(pdf_path, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        story.append(Paragraph("<b>NexusBank Transaction Receipt</b>", styles['Title']))
        story.append(Spacer(1, 15))
        
        data = [
            ["Transaction ID", txn.txn_id],
            ["Date", txn.created_at.strftime('%Y-%m-%d %H:%M:%S')],
            ["Type", txn.type],
            ["Amount", f"INR {txn.amount}"],
            ["Description", txn.description or ''],
            ["Reference", txn.reference or ''],
            ["Status", txn.status]
        ]
        
        t = Table(data)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,-1), colors.lightgrey),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
            ('GRID', (0,0), (-1,-1), 1, colors.black),
            ('PADDING', (0,0), (-1,-1), 8),
        ]))
        story.append(t)
        
        doc.build(story)
        return pdf_path
