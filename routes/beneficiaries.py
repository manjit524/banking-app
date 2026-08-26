from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from services.beneficiary_service import BeneficiaryService

beneficiaries_bp = Blueprint('beneficiaries', __name__, url_prefix='/beneficiaries')

@beneficiaries_bp.route('/')
@login_required
def list_beneficiaries():
    beneficiaries = BeneficiaryService.get_user_beneficiaries(current_user.id)
    return render_template('beneficiaries/index.html', beneficiaries=beneficiaries)

@beneficiaries_bp.route('/add', methods=['POST'])
@login_required
def add():
    data = request.form.to_dict()
    try:
        BeneficiaryService.add_beneficiary(current_user.id, data)
        flash('Beneficiary added successfully.', 'success')
    except Exception as e:
        flash(str(e), 'danger')
    return redirect(url_for('beneficiaries.list_beneficiaries'))

@beneficiaries_bp.route('/<int:id>/edit', methods=['POST'])
@login_required
def edit(id):
    data = request.form.to_dict()
    try:
        BeneficiaryService.edit_beneficiary(current_user.id, id, data)
        flash('Beneficiary updated successfully.', 'success')
    except Exception as e:
        flash(str(e), 'danger')
    return redirect(url_for('beneficiaries.list_beneficiaries'))

@beneficiaries_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    mpin = request.form.get('mpin')
    try:
        BeneficiaryService.delete_beneficiary(current_user.id, id, mpin)
        flash('Beneficiary deleted successfully.', 'success')
    except Exception as e:
        flash(str(e), 'danger')
    return redirect(url_for('beneficiaries.list_beneficiaries'))

@beneficiaries_bp.route('/<int:id>/toggle-favorite', methods=['POST'])
@login_required
def toggle_favorite(id):
    try:
        BeneficiaryService.toggle_favorite(current_user.id, id)
        flash('Favorite status toggled.', 'success')
    except Exception as e:
        flash(str(e), 'danger')
    return redirect(url_for('beneficiaries.list_beneficiaries'))
