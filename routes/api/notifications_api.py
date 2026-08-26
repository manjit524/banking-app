from flask import Blueprint, request, jsonify, Response, stream_with_context
from flask_login import login_required, current_user
from services.transaction_service import TransactionService
from services.transfer_service import TransferService
from extensions import csrf
import queue, json, threading, time

notifications_api_bp = Blueprint('notifications_api', __name__, url_prefix='/api')

sse_queues = {}  # user_id -> list of pending event strings
sse_lock = threading.Lock()

@notifications_api_bp.route('/notifications/stream')
@login_required
@csrf.exempt
def stream():
    def event_stream():
        yield f'data: {json.dumps({"type": "connected", "user_id": current_user.id})}\n\n'
        while True:
            with sse_lock:
                events = sse_queues.pop(current_user.id, [])
            for event in events:
                yield f'data: {event}\n\n'
            time.sleep(1)
            
    response = Response(stream_with_context(event_stream()), content_type='text/event-stream')
    response.headers['Cache-Control'] = 'no-cache'
    response.headers['X-Accel-Buffering'] = 'no'
    return response

@notifications_api_bp.route('/notifications/poll')
@login_required
def poll():
    from services.notification_service import NotificationService
    from services.account_service import AccountService
    import datetime
    try:
        unread_cnt = NotificationService.get_unread_count(current_user.id)
        recent = NotificationService.get_recent(current_user.id, limit=3)
        total_balance = AccountService.get_total_balance(current_user.id)
        
        notifications_data = []
        now = datetime.datetime.utcnow()
        for n in recent:
            # If the notification was created within the last 15 seconds, include it to trigger a client toast
            created_at_naive = n.created_at.replace(tzinfo=None) if n.created_at.tzinfo else n.created_at
            if (now - created_at_naive).total_seconds() < 15:
                notifications_data.append({
                    'id': n.id,
                    'title': n.title,
                    'message': n.message,
                    'type': n.type
                })
                
        return jsonify({
            'success': True,
            'unread_count': unre_cnt if 'unre_cnt' in locals() else unread_cnt, # fallback
            'unread_count': unread_cnt,
            'total_balance': float(total_balance),
            'new_notifications': notifications_data
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@notifications_api_bp.route('/notifications/unread-count')
@login_required
def unread_count():
    from services.notification_service import NotificationService
    try:
        count = NotificationService.get_unread_count(current_user.id)
        return jsonify({'success': True, 'count': count})
    except Exception as e:
        return jsonify({'success': False, 'error': {'code': 'ERROR', 'message': str(e)}})

@notifications_api_bp.route('/transactions/deposit', methods=['POST'])
@login_required
@csrf.exempt
def api_deposit():
    data = request.get_json() or {}
    mpin = data.get('mpin')
    amount = data.get('amount')
    account_id = data.get('account_id')
    try:
        txn = TransactionService.deposit(current_user.id, account_id, amount, mpin)
        return jsonify({'success': True, 'data': {'transaction_id': txn.id if hasattr(txn, 'id') else txn}})
    except Exception as e:
        return jsonify({'success': False, 'error': {'code': 'DEPOSIT_FAILED', 'message': str(e)}})

@notifications_api_bp.route('/transactions/withdraw', methods=['POST'])
@login_required
@csrf.exempt
def api_withdraw():
    data = request.get_json() or {}
    mpin = data.get('mpin')
    amount = data.get('amount')
    account_id = data.get('account_id')
    try:
        txn = TransactionService.withdraw(current_user.id, account_id, amount, mpin)
        return jsonify({'success': True, 'data': {'transaction_id': txn.id if hasattr(txn, 'id') else txn}})
    except Exception as e:
        return jsonify({'success': False, 'error': {'code': 'WITHDRAW_FAILED', 'message': str(e)}})

@notifications_api_bp.route('/transfers', methods=['POST'])
@login_required
@csrf.exempt
def api_transfer():
    data = request.get_json() or {}
    try:
        txn = TransferService.transfer(current_user.id, data)
        return jsonify({'success': True, 'data': {'transfer_id': txn.id if hasattr(txn, 'id') else txn}})
    except Exception as e:
        return jsonify({'success': False, 'error': {'code': 'TRANSFER_FAILED', 'message': str(e)}})
