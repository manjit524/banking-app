"""
services/profile_service.py — Profile management logic
"""
from datetime import datetime
from models import User
from extensions import db
from services.auth_service import AuthService

class ProfileService:
    @staticmethod
    def update_profile(user_id, data):
        try:
            user = db.session.get(User, user_id)
            if not user:
                raise ValueError("User not found")

            user.name = data.get('name', user.name)
            user.phone = data.get('phone', user.phone)
            user.address = data.get('address', user.address)
            user.country = data.get('country', user.country)
            
            dob_str = data.get('date_of_birth')
            if dob_str:
                try:
                    user.date_of_birth = datetime.strptime(dob_str, '%Y-%m-%d').date()
                except ValueError:
                    pass

            db.session.commit()
            return user
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def change_password(user_id, current_password, new_password):
        user = db.session.get(User, user_id)
        if not user:
            raise ValueError("User not found")
        
        # Verify old password
        from extensions import bcrypt
        if not bcrypt.check_password_hash(user.password_hash, current_password):
            raise ValueError("Incorrect current password")
            
        if not new_password or len(new_password) < 6:
            raise ValueError("New password must be at least 6 characters long")

        try:
            user.password_hash = bcrypt.generate_password_hash(new_password)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def change_mpin(user_id, current_mpin, new_mpin):
        user = db.session.get(User, user_id)
        if not user:
            raise ValueError("User not found")
            
        from extensions import bcrypt
        if user.mpin_hash:
            if not bcrypt.check_password_hash(user.mpin_hash, current_mpin):
                raise ValueError("Incorrect current MPIN")

        if not new_mpin or len(new_mpin) != 6 or not new_mpin.isdigit():
            raise ValueError("New MPIN must be exactly 6 digits")

        try:
            user.mpin_hash = bcrypt.generate_password_hash(new_mpin)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def update_notification_preferences(user_id, data):
        try:
            user = db.session.get(User, user_id)
            if not user:
                raise ValueError("User not found")

            user.notify_email = data.get('notify_email', user.notify_email)
            user.notify_inapp = data.get('notify_inapp', user.notify_inapp)

            db.session.commit()
            return user
        except Exception as e:
            db.session.rollback()
            raise e
