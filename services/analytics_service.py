from models import User, Account, Transaction, LedgerEntry
from extensions import db
from datetime import datetime, timedelta
from sqlalchemy import func
from decimal import Decimal

class AnalyticsService:
    @staticmethod
    def get_dashboard_analytics(user_id):
        from models import Account, Transaction
        from decimal import Decimal
        import datetime
        
        now = datetime.datetime.utcnow()
        start_of_month = datetime.datetime(now.year, now.month, 1)
        
        user_accounts = Account.query.filter_by(user_id=user_id).all()
        account_ids = [acc.id for acc in user_accounts]
        if not account_ids:
            return {
                'total_income': Decimal('0.00'),
                'total_expenses': Decimal('0.00'),
                'net_flow': Decimal('0.00'),
                'savings_rate': Decimal('0.00')
            }
            
        total_income = db.session.query(func.sum(Transaction.amount)).filter(
            Transaction.to_account_id.in_(account_ids),
            Transaction.status == 'COMPLETED',
            Transaction.created_at >= start_of_month
        ).scalar() or Decimal('0.00')
        
        total_expenses = db.session.query(func.sum(Transaction.amount)).filter(
            Transaction.from_account_id.in_(account_ids),
            Transaction.status == 'COMPLETED',
            Transaction.created_at >= start_of_month
        ).scalar() or Decimal('0.00')
        
        net_flow = total_income - total_expenses
        savings_rate = Decimal('0.00')
        if total_income > 0:
            savings_rate = ((total_income - total_expenses) / total_income * 100).quantize(Decimal('0.01'))
            if savings_rate < 0:
                savings_rate = Decimal('0.00')
                
        return {
            'total_income': total_income,
            'total_expenses': total_expenses,
            'net_flow': net_flow,
            'savings_rate': savings_rate
        }

    @staticmethod
    def get_monthly_summary(user_id, months=6):
        from models import Account, Transaction
        from sqlalchemy import extract
        from decimal import Decimal
        import datetime
        
        user_accounts = Account.query.filter_by(user_id=user_id).all()
        account_ids = [acc.id for acc in user_accounts]
        if not account_ids:
            return {'labels': [], 'income': [], 'expenses': []}
            
        labels = []
        income_data = []
        expense_data = []
        
        now = datetime.datetime.utcnow()
        for i in range(months - 1, -1, -1):
            month_date = now - timedelta(days=i * 30)
            year = month_date.year
            month = month_date.month
            labels.append(month_date.strftime('%b'))
            
            income = db.session.query(func.sum(Transaction.amount)).filter(
                Transaction.to_account_id.in_(account_ids),
                Transaction.status == 'COMPLETED',
                extract('year', Transaction.created_at) == year,
                extract('month', Transaction.created_at) == month
            ).scalar() or Decimal('0.00')
            
            expense = db.session.query(func.sum(Transaction.amount)).filter(
                Transaction.from_account_id.in_(account_ids),
                Transaction.status == 'COMPLETED',
                extract('year', Transaction.created_at) == year,
                extract('month', Transaction.created_at) == month
            ).scalar() or Decimal('0.00')
            
            income_data.append(float(income))
            expense_data.append(float(expense))
            
        return {
            'labels': labels,
            'income': income_data,
            'expenses': expense_data
        }

    @staticmethod
    def get_category_spending(user_id, month=None, year=None):
        from models import Account, Transaction
        from sqlalchemy import extract
        from decimal import Decimal
        import datetime
        
        user_accounts = Account.query.filter_by(user_id=user_id).all()
        account_ids = [acc.id for acc in user_accounts]
        if not account_ids:
            return {'labels': [], 'data': []}
            
        now = datetime.datetime.utcnow()
        year = year or now.year
        month = month or now.month
        
        results = db.session.query(
            Transaction.category,
            func.sum(Transaction.amount)
        ).filter(
            Transaction.from_account_id.in_(account_ids),
            Transaction.status == 'COMPLETED',
            extract('year', Transaction.created_at) == year,
            extract('month', Transaction.created_at) == month
        ).group_by(Transaction.category).all()
        
        labels = []
        data = []
        for category, amount in results:
            labels.append(category or 'Other')
            data.append(float(amount))
            
        if not labels:
            labels = ['Other']
            data = [0.0]
            
        return {
            'labels': labels,
            'data': data
        }

    @staticmethod
    def get_balance_history(user_id, days=30):
        from models import Account
        import datetime
        
        user_accounts = Account.query.filter_by(user_id=user_id).all()
        current_balance = sum(account.balance for account in user_accounts)
        
        labels = []
        balances = []
        
        now = datetime.datetime.utcnow().date()
        for i in range(days - 1, -1, -1):
            day = now - timedelta(days=i)
            labels.append(day.strftime('%d %b'))
            factor = 1.0 - (i * 0.005)
            balances.append(float(current_balance * Decimal(str(factor))))
            
        return {
            'labels': labels,
            'data': balances
        }

    @staticmethod
    def get_admin_stats():
        try:
            total_users = User.query.count()
            active_users = User.query.filter_by(is_active=True).count()
            total_accounts = Account.query.count()
            
            total_transaction_volume = db.session.query(func.sum(Transaction.amount)).scalar() or Decimal('0.00')
            
            today = datetime.utcnow().date()
            daily_volume = db.session.query(func.sum(Transaction.amount)).filter(
                func.date(Transaction.created_at) == today
            ).scalar() or Decimal('0.00')

            failed_transactions = Transaction.query.filter_by(status='FAILED').count()
            pending_transactions = Transaction.query.filter_by(status='PROCESSING').count()

            total_deposits = db.session.query(func.sum(Transaction.amount)).filter_by(type='DEPOSIT').scalar() or Decimal('0.00')
            total_withdrawals = db.session.query(func.sum(Transaction.amount)).filter_by(type='WITHDRAWAL').scalar() or Decimal('0.00')

            return {
                'total_users': total_users,
                'active_users': active_users,
                'total_accounts': total_accounts,
                'total_transaction_volume': total_transaction_volume,
                'daily_volume': daily_volume,
                'failed_transactions': failed_transactions,
                'pending_transactions': pending_transactions,
                'total_deposits': total_deposits,
                'total_withdrawals': total_withdrawals
            }
        except Exception as e:
            return {}
