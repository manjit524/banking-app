from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from services.notification_service import NotificationService

notifications_bp = Blueprint('notifications', __name__, url_prefix='/notifications')

@notifications_bp.route('/')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    notifications = NotificationService.get_user_notifications(current_user.id, page)
    return render_template('notifications/index.html', notifications=notifications)

@notifications_bp.route('/<int:id>/read', methods=['POST'])
@login_required
def read(id):
    try:
        NotificationService.mark_read(current_user.id, id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@notifications_bp.route('/read-all', methods=['POST'])
@login_required
def read_all():
    try:
        NotificationService.mark_all_read(current_user.id)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': True})
        flash('All notifications marked as read.', 'success')
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': str(e)}), 400
        flash(str(e), 'danger')
    return redirect(url_for('notifications.index'))