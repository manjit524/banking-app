from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from flask_login import login_required, current_user
from services.transaction_service import TransactionService

transactions_bp = Blueprint('transactions', __name__, url_prefix='/transactions')

@transactions_bp.route('/')
@login_required
def index():
    filters = {
        'type': request.args.get('type'),
        'status': request.args.get('status'),
        'date_from': request.args.get('date_from'),
        'date_to': request.args.get('date_to'),
        'search': request.args.get('search'),
        'page': request.args.get('page', 1, type=int)
    }
    transactions = TransactionService.get_transactions(current_user.id, filters)
    return render_template('transactions/index.html', transactions=transactions)

@transactions_bp.route('/<txn_id>')
@login_required
def detail(txn_id):
    txn = TransactionService.get_transaction_by_id(txn_id, current_user.id)
    return render_template('transactions/detail.html', transaction=txn)

@transactions_bp.route('/<txn_id>/receipt')
@login_required
def receipt(txn_id):
    txn = TransactionService.get_transaction_by_id(txn_id, current_user.id)
    return render_template('transactions/receipt.html', transaction=txn)

@transactions_bp.route('/<txn_id>/receipt/pdf')
@login_required
def receipt_pdf(txn_id):
    pdf_path = TransactionService.generate_receipt_pdf(txn_id, current_user.id)
    return send_file(pdf_path, as_attachment=True)

@transactions_bp.route('/deposit', methods=['POST'])
@login_required
def deposit():
    mpin = request.form.get('mpin')
    amount = request.form.get('amount')
    account_id = request.form.get('account_id')
    try:
        TransactionService.deposit(current_user.id, account_id, amount, mpin)
        flash('Deposit successful.', 'success')
    except Exception as e:
        flash(str(e), 'danger')
    return redirect(url_for('accounts.detail', account_id=account_id))

@transactions_bp.route('/withdraw', methods=['POST'])
@login_required
def withdraw():
    mpin = request.form.get('mpin')
    amount = request.form.get('amount')
    account_id = request.form.get('account_id')
    try:
        TransactionService.withdraw(current_user.id, account_id, amount, mpin)
        flash('Withdrawal successful.', 'success')
    except Exception as e:
        flash(str(e), 'danger')
    return redirect(url_for('accounts.detail', account_id=account_id))
