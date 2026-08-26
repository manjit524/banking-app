from models.audit_log import AuditLog, AuditAction
from extensions import db
from flask import request

class AuditService:
    @staticmethod
    def log(action, user_id=None, actor_id=None, resource_type=None, resource_id=None, description=None, result='SUCCESS', request_obj=None):
        try:
            req = request_obj or request
            ip_address = req.remote_addr if req else None
            user_agent = req.headers.get('User-Agent') if req and hasattr(req, 'headers') else None

            audit_log = AuditLog(
                action=action,
                user_id=user_id,
                actor_id=actor_id,
                resource_type=resource_type,
                resource_id=resource_id,
                description=description,
                result=result,
                ip_address=ip_address,
                user_agent=user_agent
            )
            db.session.add(audit_log)
            db.session.commit()
            return audit_log
        except Exception as e:
            db.session.rollback()
            raise e
