from flask import Blueprint, render_template, current_app
from flask_login import login_required, current_user
from services.account_service import AccountService
from services.transaction_service import TransactionService
from services.analytics_service import AnalyticsService

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/')

@dashboard_bp.route('/dashboard')
@dashboard_bp.route('/')
@login_required
def index():
    accounts = AccountService.get_user_accounts(current_user.id)
    recent_transactions = TransactionService.get_recent_transactions(current_user.id, limit=5)
    total_balance = sum((account.balance for account in accounts), 0)
    monthly_summary = AnalyticsService.get_monthly_summary(current_user.id)
    
    return render_template('dashboard/index.html', 
                           accounts=accounts, 
                           recent_transactions=recent_transactions, 
                           total_balance=total_balance,
                           monthly_summary=monthly_summary)
