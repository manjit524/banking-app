from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from services.analytics_service import AnalyticsService
from services.admin_service import AdminService
from models import UserRole

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.before_request
@login_required
def require_admin():
    if current_user.role != UserRole.ADMIN:
        return render_template('errors/403.html'), 403

@admin_bp.route('/')
def index():
    from models import Transaction, AuditLog
    stats = AnalyticsService.get_admin_stats()
    failed_txns = Transaction.query.filter_by(status='FAILED').order_by(Transaction.created_at.desc()).limit(5).all()
    suspicious_logs = AuditLog.query.filter_by(result='FAILURE').order_by(AuditLog.created_at.desc()).limit(3).all()
    return render_template(
        'admin/dashboard.html',
        stats=stats,
        failed_txns=failed_txns,
        suspicious_logs=suspicious_logs
    )

@admin_bp.route('/users')
def users():
    search = request.args.get('search')
    filter_role = request.args.get('role')
    page = request.args.get('page', 1, type=int)
    users_page = AdminService.get_all_users(search, filter_role, page)
    return render_template('admin/users.html', users_page=users_page)

@admin_bp.route('/users/<int:user_id>')
def user_detail(user_id):
    return redirect(url_for('admin.users'))

@admin_bp.route('/users/<int:user_id>/suspend', methods=['POST'])
def suspend_user(user_id):
    try:
        AdminService.suspend_user(user_id)
        flash('User suspended.', 'success')
    except Exception as e:
        flash(str(e), 'danger')
    return redirect(url_for('admin.users'))

@admin_bp.route('/users/<int:user_id>/activate', methods=['POST'])
def activate_user(user_id):
    try:
        AdminService.activate_user(user_id)
        flash('User activated.', 'success')
    except Exception as e:
        flash(str(e), 'danger')
    return redirect(url_for('admin.users'))

@admin_bp.route('/transactions')
def transactions():
    search = request.args.get('search')
    status_filter = request.args.get('status')
    page = request.args.get('page', 1, type=int)
    txns = AdminService.get_all_transactions(search, status_filter, page)
    return render_template('admin/transactions.html', txns=txns)

@admin_bp.route('/transactions/<txn_id>')
def transaction_detail(txn_id):
    return redirect(url_for('admin.transactions'))

@admin_bp.route('/transactions/<txn_id>/reverse', methods=['POST'])
def reverse_transaction(txn_id):
    try:
        AdminService.reverse_transaction(txn_id)
        flash('Transaction reversed.', 'success')
    except Exception as e:
        flash(str(e), 'danger')
    return redirect(url_for('admin.transactions'))

@admin_bp.route('/accounts')
def accounts():
    return redirect(url_for('admin.index'))

@admin_bp.route('/accounts/<int:account_id>/freeze', methods=['POST'])
def freeze_account(account_id):
    try:
        AdminService.freeze_account(account_id)
        flash('Account frozen.', 'success')
    except Exception as e:
        flash(str(e), 'danger')
    return redirect(url_for('admin.accounts'))

@admin_bp.route('/accounts/<int:account_id>/unfreeze', methods=['POST'])
def unfreeze_account(account_id):
    try:
        AdminService.unfreeze_account(account_id)
        flash('Account unfrozen.', 'success')
    except Exception as e:
        flash(str(e), 'danger')
    return redirect(url_for('admin.accounts'))

@admin_bp.route('/audit-logs')
def audit_logs():
    search = request.args.get('search')
    page = request.args.get('page', 1, type=int)
    logs = AdminService.get_audit_logs(search, page)
    return render_template('admin/audit_logs.html', logs=logs)

@admin_bp.route('/security-events')
def security_events():
    return redirect(url_for('admin.index'))
