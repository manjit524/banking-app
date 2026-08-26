from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from services.profile_service import ProfileService

profile_bp = Blueprint('profile', __name__, url_prefix='/profile')

@profile_bp.route('/')
@login_required
def index():
    return render_template('profile/index.html', user=current_user)

@profile_bp.route('/update', methods=['POST'])
@login_required
def update():
    data = request.form.to_dict()
    try:
        ProfileService.update_profile(current_user.id, data)
        flash('Profile updated successfully.', 'success')
    except Exception as e:
        flash(str(e), 'danger')
    return redirect(url_for('profile.index'))

@profile_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    try:
        ProfileService.change_password(current_user.id, current_password, new_password)
        flash('Password changed successfully.', 'success')
    except Exception as e:
        flash(str(e), 'danger')
    return redirect(url_for('profile.index'))

@profile_bp.route('/change-mpin', methods=['POST'])
@login_required
def change_mpin():
    current_mpin = request.form.get('current_mpin')
    new_mpin = request.form.get('new_mpin')
    try:
        ProfileService.change_mpin(current_user.id, current_mpin, new_mpin)
        flash('MPIN changed successfully.', 'success')
    except Exception as e:
        flash(str(e), 'danger')
    return redirect(url_for('profile.index'))

@profile_bp.route('/notification-preferences', methods=['POST'])
@login_required
def notification_preferences():
    data = {
        'notify_email': request.form.get('notify_email') == 'on',
        'notify_inapp': request.form.get('notify_inapp') == 'on'
    }
    try:
        ProfileService.update_notification_preferences(current_user.id, data)
        flash('Notification preferences updated.', 'success')
    except Exception as e:
        flash(str(e), 'danger')
    return redirect(url_for('profile.index'))
