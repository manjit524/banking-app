from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from flask_login import login_required, current_user
from services.account_service import AccountService

accounts_bp = Blueprint('accounts', __name__, url_prefix='/accounts')

@accounts_bp.route('/')
@login_required
def index():
    accounts = AccountService.get_user_accounts(current_user.id)
    return render_template('accounts/index.html', accounts=accounts)

@accounts_bp.route('/<int:account_id>')
@login_required
def detail(account_id):
    account = AccountService.get_account_by_id(account_id, current_user.id)
    transactions = AccountService.get_account_transactions(account_id)
    
    import datetime
    from decimal import Decimal
    now = datetime.datetime.utcnow()
    start_of_month = datetime.datetime(now.year, now.month, 1)
    
    total_credited = Decimal('0.00')
    total_debited = Decimal('0.00')
    for tx in transactions:
        if tx.created_at >= start_of_month and tx.status == 'COMPLETED':
            if tx.to_account_id == account_id:
                total_credited += tx.amount
            elif tx.from_account_id == account_id:
                total_debited += tx.amount
                
    return render_template(
        'accounts/detail.html',
        account=account,
        transactions=transactions,
        total_credited=total_credited,
        total_debited=total_debited
    )

@accounts_bp.route('/create', methods=['POST'])
@login_required
def create():
    mpin = request.form.get('mpin')
    account_type = request.form.get('account_type')
    try:
        AccountService.create_account(current_user.id, account_type, mpin)
        flash('Account created successfully.', 'success')
    except Exception as e:
        flash(str(e), 'danger')
    return redirect(url_for('accounts.index'))

@accounts_bp.route('/<int:account_id>/statement')
@login_required
def statement(account_id):
    return redirect(url_for('accounts.detail', account_id=account_id))

@accounts_bp.route('/<int:account_id>/statement/pdf')
@login_required
def statement_pdf(account_id):
    pdf_path = AccountService.generate_statement_pdf(account_id, current_user.id)
    return send_file(pdf_path, as_attachment=True)

@accounts_bp.route('/<int:account_id>/statement/csv')
@login_required
def statement_csv(account_id):
    csv_path = AccountService.generate_statement_csv(account_id, current_user.id)
    return send_file(csv_path, as_attachment=True)
