from models import Account
from extensions import db
import random
import string
from decimal import Decimal

class AccountService:
    @staticmethod
    def get_user_accounts(user_id):
        return Account.query.filter_by(user_id=user_id, status='ACTIVE').all()

    @staticmethod
    def get_account(account_id, user_id):
        account = Account.query.filter_by(id=account_id, user_id=user_id).first()
        if not account:
            raise ValueError("Account not found")
        return account

    @staticmethod
    def create_account(user_id, account_type, mpin=None, nickname=None):
        try:
            from models import User
            from services.auth_service import AuthService
            user = db.session.get(User, user_id)
            if not user:
                raise ValueError("User not found")
            if mpin and not AuthService.verify_mpin(user, mpin):
                raise ValueError("Invalid MPIN")

            account_number = 'NXS' + ''.join(random.choices(string.digits, k=12))
            account = Account(
                user_id=user_id,
                account_type=account_type,
                account_number=account_number,
                nickname=nickname,
                balance=Decimal('0.00'),
                available_balance=Decimal('0.00'),
                status='ACTIVE'
            )
            db.session.add(account)
            db.session.commit()
            return account
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def get_account_by_id(account_id, user_id):
        return AccountService.get_account(account_id, user_id)

    @staticmethod
    def get_account_transactions(account_id):
        from models import Transaction
        from sqlalchemy import or_, desc
        return Transaction.query.filter(or_(
            Transaction.from_account_id == account_id,
            Transaction.to_account_id == account_id
        )).order_by(desc(Transaction.created_at)).all()

    @staticmethod
    def generate_statement_pdf(account_id, user_id):
        import os
        import tempfile
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib import colors
        
        account = AccountService.get_account(account_id, user_id)
        transactions = AccountService.get_account_transactions(account_id)
        
        fd, pdf_path = tempfile.mkstemp(suffix='.pdf')
        os.close(fd)
        
        doc = SimpleDocTemplate(pdf_path, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        story.append(Paragraph("<b>NexusBank Statement</b>", styles['Title']))
        story.append(Spacer(1, 15))
        story.append(Paragraph(f"<b>Account Number:</b> {account.account_number}", styles['Normal']))
        story.append(Paragraph(f"<b>Account Type:</b> {account.account_type}", styles['Normal']))
        story.append(Paragraph(f"<b>Balance:</b> INR {account.balance}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        data = [["Date", "TXN ID", "Type", "Description", "Amount"]]
        for tx in transactions:
            amt = f"+{tx.amount}" if tx.to_account_id == account_id else f"-{tx.amount}"
            data.append([
                tx.created_at.strftime('%Y-%m-%d %H:%M'),
                tx.txn_id,
                tx.type,
                tx.description or '',
                amt
            ])
            
        t = Table(data)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.grey),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,0), 6),
            ('BACKGROUND', (0,1), (-1,-1), colors.beige),
            ('GRID', (0,0), (-1,-1), 1, colors.black),
        ]))
        story.append(t)
        
        doc.build(story)
        return pdf_path

    @staticmethod
    def generate_statement_csv(account_id, user_id):
        import csv
        import tempfile
        import os
        
        account = AccountService.get_account(account_id, user_id)
        transactions = AccountService.get_account_transactions(account_id)
        
        fd, csv_path = tempfile.mkstemp(suffix='.csv')
        os.close(fd)
        
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Account Number", account.account_number])
            writer.writerow(["Account Type", account.account_type])
            writer.writerow(["Balance", account.balance])
            writer.writerow([])
            writer.writerow(["Date", "Transaction ID", "Type", "Description", "Amount"])
            for tx in transactions:
                amt = f"+{tx.amount}" if tx.to_account_id == account_id else f"-{tx.amount}"
                writer.writerow([
                    tx.created_at.strftime('%Y-%m-%d %H:%M'),
                    tx.txn_id,
                    tx.type,
                    tx.description or '',
                    amt
                ])
                
        return csv_path

    @staticmethod
    def get_total_balance(user_id):
        accounts = AccountService.get_user_accounts(user_id)
        return sum(account.balance for account in accounts)

    @staticmethod
    def freeze_account(account_id):
        try:
            account = Account.query.get(account_id)
            if account:
                account.status = 'FROZEN'
                db.session.commit()
            return account
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def unfreeze_account(account_id):
        try:
            account = Account.query.get(account_id)
            if account:
                account.status = 'ACTIVE'
                db.session.commit()
            return account
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def verify_account_number(account_number):
        account = Account.query.filter_by(account_number=account_number).first()
        if not account:
            raise ValueError("Account not found")
        return account.owner.name
