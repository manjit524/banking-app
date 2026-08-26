import json
from models.notification import Notification
from extensions import db
from routes.api.notifications_api import sse_queues

class NotificationService:
    @staticmethod
    def create(user_id, type, title, message, transaction_id=None):
        try:
            notification = Notification(
                user_id=user_id,
                type=type,
                title=title,
                message=message,
                transaction_id=transaction_id
            )
            db.session.add(notification)
            db.session.commit()
            
            NotificationService.push_sse_event(user_id, {
                'type': 'notification',
                'data': {
                    'id': notification.id,
                    'title': notification.title,
                    'message': notification.message,
                    'type': notification.type
                }
            })
            return notification
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def mark_read(notification_id, user_id):
        try:
            notification = Notification.query.filter_by(id=notification_id, user_id=user_id).first()
            if notification:
                notification.is_read = True
                db.session.commit()
            return notification
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def mark_all_read(user_id):
        try:
            Notification.query.filter_by(user_id=user_id, is_read=False).update({'is_read': True})
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def get_unread_count(user_id):
        return Notification.query.filter_by(user_id=user_id, is_read=False).count()

    @staticmethod
    def get_recent(user_id, limit=20):
        return Notification.query.filter_by(user_id=user_id).order_by(Notification.created_at.desc()).limit(limit).all()

    @staticmethod
    def get_user_notifications(user_id, page=1, per_page=20):
        return Notification.query.filter_by(user_id=user_id).order_by(Notification.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)

    @staticmethod
    def push_sse_event(user_id, event_data):
        sse_queues.setdefault(user_id, []).append(json.dumps(event_data))
