from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from services.card_service import CardService

cards_bp = Blueprint('cards', __name__, url_prefix='/cards')

@cards_bp.route('/')
@login_required
def list_cards():
    cards = CardService.get_user_cards(current_user.id)
    accounts = CardService.get_user_eligible_accounts(current_user.id)
    return render_template('cards/index.html', cards=cards, accounts=accounts)

@cards_bp.route('/issue', methods=['POST'])
@login_required
def issue():
    account_id = request.form.get('account_id')
    card_type = request.form.get('card_type')
    try:
        CardService.issue_virtual_card(current_user.id, account_id, card_type)
        flash('Virtual card issued successfully.', 'success')
    except Exception as e:
        flash(str(e), 'danger')
    return redirect(url_for('cards.list_cards'))

@cards_bp.route('/<int:id>/freeze', methods=['POST'])
@login_required
def freeze(id):
    try:
        CardService.toggle_freeze(current_user.id, id)
        flash('Card freeze status updated.', 'success')
    except Exception as e:
        flash(str(e), 'danger')
    return redirect(url_for('cards.list_cards'))

@cards_bp.route('/<int:id>/toggle-online', methods=['POST'])
@login_required
def toggle_online(id):
    try:
        CardService.toggle_online(current_user.id, id)
        flash('Card online payment status updated.', 'success')
    except Exception as e:
        flash(str(e), 'danger')
    return redirect(url_for('cards.list_cards'))

@cards_bp.route('/<int:id>/toggle-international', methods=['POST'])
@login_required
def toggle_international(id):
    try:
        CardService.toggle_international(current_user.id, id)
        flash('Card international payment status updated.', 'success')
    except Exception as e:
        flash(str(e), 'danger')
    return redirect(url_for('cards.list_cards'))
