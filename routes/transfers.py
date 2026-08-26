from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from services.transfer_service import TransferService
from services.account_service import AccountService

transfers_bp = Blueprint('transfers', __name__, url_prefix='/transfers')

from services.beneficiary_service import BeneficiaryService

@transfers_bp.route('/', methods=['GET', 'POST'])
@login_required
def transfer():
    if request.method == 'POST':
        data = request.form.to_dict()
        try:
            TransferService.transfer(current_user.id, data)
            flash('Transfer successful.', 'success')
            return redirect(url_for('dashboard.index'))
        except Exception as e:
            flash(str(e), 'danger')
            
    accounts = AccountService.get_user_accounts(current_user.id)
    beneficiaries = BeneficiaryService.get_user_beneficiaries(current_user.id)
    return render_template('transfers/index.html', accounts=accounts, beneficiaries=beneficiaries)

@transfers_bp.route('/verify-account')
@login_required
def verify_account():
    account_number = request.args.get('account_number')
    try:
        holder_name = AccountService.verify_account_number(account_number)
        return jsonify({'success': True, 'holder_name': holder_name})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
