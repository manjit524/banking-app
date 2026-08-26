from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from services.payment_service import PaymentService
from services.account_service import AccountService

payments_bp = Blueprint('payments', __name__, url_prefix='/payments')

@payments_bp.route('/bills')
@login_required
def bills():
    billers = PaymentService.get_billers()
    bills = PaymentService.get_user_bills(current_user.id)
    accounts = AccountService.get_user_accounts(current_user.id)
    return render_template('payments/bills.html', billers=billers, bills=bills, accounts=accounts)

@payments_bp.route('/bills/pay', methods=['POST'])
@login_required
def pay_bill():
    data = request.form.to_dict()
    try:
        PaymentService.pay_bill(
            user_id=current_user.id,
            from_account_id=data.get('from_account_id'),
            biller_id=data.get('biller_id'),
            amount=data.get('amount'),
            consumer_number=data.get('consumer_number'),
            mpin=data.get('mpin')
        )
        flash('Bill payment successful.', 'success')
    except Exception as e:
        flash(str(e), 'danger')
    return redirect(url_for('payments.bills'))

@payments_bp.route('/scheduled')
@login_required
def scheduled():
    payments = PaymentService.get_user_scheduled_payments(current_user.id)
    accounts = AccountService.get_user_accounts(current_user.id)
    from services.beneficiary_service import BeneficiaryService
    beneficiaries = BeneficiaryService.get_user_beneficiaries(current_user.id)
    return render_template('payments/scheduled.html', payments=payments, accounts=accounts, beneficiaries=beneficiaries)

@payments_bp.route('/scheduled/create', methods=['POST'])
@login_required
def create_scheduled_payment():
    data = request.form.to_dict()
    try:
        PaymentService.create_scheduled_payment(
            user_id=current_user.id,
            from_account_id=data.get('from_account_id'),
            to_account_id=data.get('to_account_id'),
            amount=data.get('amount'),
            frequency=data.get('frequency'),
            start_date=data.get('start_date'),
            description=data.get('description'),
            end_date=data.get('end_date') or None
        )
        flash('Scheduled payment created successfully.', 'success')
    except Exception as e:
        flash(str(e), 'danger')
    return redirect(url_for('payments.scheduled'))

@payments_bp.route('/scheduled/<int:id>/cancel', methods=['POST'])
@login_required
def cancel_scheduled_payment(id):
    try:
        PaymentService.cancel_scheduled_payment(payment_id=id, user_id=current_user.id)
        flash('Scheduled payment cancelled.', 'success')
    except Exception as e:
        flash(str(e), 'danger')
    return redirect(url_for('payments.scheduled'))
