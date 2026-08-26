from models.user import User
from models.account import Account
from extensions import db, bcrypt
import random
import string
from decimal import Decimal
from datetime import datetime, timedelta

class AuthService:
    MAX_LOGIN_ATTEMPTS = 5

    @staticmethod
    def register(name, email, password, mpin, phone=None):
        try:
            hashed_password = bcrypt.generate_password_hash(password)
            hashed_mpin = bcrypt.generate_password_hash(mpin)
            
            user = User(
                name=name,
                email=email,
                password_hash=hashed_password,
                mpin_hash=hashed_mpin,
                phone=phone
            )
            db.session.add(user)
            db.session.flush()
            
            # Create first Savings account
            account_number = ''.join(random.choices(string.digits, k=12))
            account = Account(
                user_id=user.id,
                account_type='Savings',
                account_number=account_number,
                balance=Decimal('0.00'),
                available_balance=Decimal('0.00'),
                status='ACTIVE'
            )
            db.session.add(account)
            db.session.commit()
            
            return user
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def authenticate(email, password):
        try:
            user = User.query.filter_by(email=email).first()
            if not user:
                return None, "Invalid credentials"

            if user.locked_until and user.locked_until > datetime.utcnow():
                return None, "Account is locked. Try again later."

            if bcrypt.check_password_hash(user.password_hash, password):
                user.failed_login_attempts = 0
                user.locked_until = None
                db.session.commit()
                return user, None
            else:
                user.failed_login_attempts += 1
                if user.failed_login_attempts >= AuthService.MAX_LOGIN_ATTEMPTS:
                    user.locked_until = datetime.utcnow() + timedelta(minutes=30)
                db.session.commit()
                return None, "Invalid credentials"
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def verify_mpin(user, mpin):
        return bcrypt.check_password_hash(user.mpin_hash, mpin)

    @staticmethod
    def change_password(user, old_password, new_password):
        try:
            if not bcrypt.check_password_hash(user.password_hash, old_password):
                raise ValueError("Invalid current password")
            user.password_hash = bcrypt.generate_password_hash(new_password)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def change_mpin(user, current_mpin, new_mpin):
        try:
            if not bcrypt.check_password_hash(user.mpin_hash, current_mpin):
                raise ValueError("Invalid current MPIN")
            user.mpin_hash = bcrypt.generate_password_hash(new_mpin)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def generate_reset_token(email):
        try:
            user = User.query.filter_by(email=email).first()
            if user:
                token = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
                user.reset_token = token
                # assuming 1 hour expiry
                db.session.commit()
                return token
            return None
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def reset_password(token, new_password):
        try:
            user = User.query.filter_by(reset_token=token).first()
            if not user:
                raise ValueError("Invalid or expired token")
            
            user.password_hash = bcrypt.generate_password_hash(new_password)
            user.reset_token = None
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def generate_email_verify_token(user):
        try:
            token = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
            user.email_verify_token = token
            db.session.commit()
            return token
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def verify_email(token):
        try:
            user = User.query.filter_by(email_verify_token=token).first()
            if not user:
                raise ValueError("Invalid token")
            
            user.email_verified = True
            user.email_verify_token = None
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise e
