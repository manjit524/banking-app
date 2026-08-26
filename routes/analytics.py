from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from services.analytics_service import AnalyticsService

analytics_bp = Blueprint('analytics', __name__, url_prefix='/analytics')

@analytics_bp.route('/')
@login_required
def index():
    data = AnalyticsService.get_dashboard_analytics(current_user.id)
    return render_template('analytics/index.html', data=data)

@analytics_bp.route('/api/monthly-summary')
@login_required
def api_monthly_summary():
    data = AnalyticsService.get_monthly_summary(current_user.id)
    return jsonify(data)

@analytics_bp.route('/api/category-spending')
@login_required
def api_category_spending():
    data = AnalyticsService.get_category_spending(current_user.id)
    return jsonify(data)

@analytics_bp.route('/api/balance-history')
@login_required
def api_balance_history():
    data = AnalyticsService.get_balance_history(current_user.id)
    return jsonify(data)
