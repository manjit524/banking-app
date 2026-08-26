"""
services/beneficiary_service.py — Beneficiary management logic
"""
from models import Beneficiary, Account, User
from extensions import db
from services.auth_service import AuthService

class BeneficiaryService:
    @staticmethod
    def get_user_beneficiaries(user_id):
        return Beneficiary.query.filter_by(user_id=user_id, is_active=True).all()

    @staticmethod
    def add_beneficiary(user_id, data):
        try:
            name = data.get('name')
            nickname = data.get('nickname')
            bank_name = data.get('bank_name', 'NexusBank')
            account_number = data.get('account_number')
            ifsc_code = data.get('ifsc_code')
            email = data.get('email')
            phone = data.get('phone')

            if not name or not account_number:
                raise ValueError("Name and Account Number are required")

            # Check if internal account number belongs to NexusBank
            linked_account = None
            if bank_name.lower() == 'nexusbank' or not bank_name:
                linked_account = Account.query.filter_by(account_number=account_number).first()

            beneficiary = Beneficiary(
                user_id=user_id,
                name=name,
                nickname=nickname,
                bank_name=bank_name or 'NexusBank',
                account_number=account_number,
                ifsc_code=ifsc_code,
                email=email,
                phone=phone,
                linked_account_id=linked_account.id if linked_account else None,
                is_verified=True if linked_account else False
            )
            db.session.add(beneficiary)
            db.session.commit()
            return beneficiary
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def edit_beneficiary(user_id, id, data):
        try:
            beneficiary = Beneficiary.query.filter_by(id=id, user_id=user_id).first()
            if not beneficiary:
                raise ValueError("Beneficiary not found")

            beneficiary.name = data.get('name', beneficiary.name)
            beneficiary.nickname = data.get('nickname', beneficiary.nickname)
            beneficiary.bank_name = data.get('bank_name', beneficiary.bank_name)
            beneficiary.account_number = data.get('account_number', beneficiary.account_number)
            beneficiary.ifsc_code = data.get('ifsc_code', beneficiary.ifsc_code)
            beneficiary.email = data.get('email', beneficiary.email)
            beneficiary.phone = data.get('phone', beneficiary.phone)

            # Update link if bank_name/account_number changed
            if beneficiary.bank_name.lower() == 'nexusbank':
                linked_account = Account.query.filter_by(account_number=beneficiary.account_number).first()
                beneficiary.linked_account_id = linked_account.id if linked_account else None
                beneficiary.is_verified = True if linked_account else False
            else:
                beneficiary.linked_account_id = None
                beneficiary.is_verified = False

            db.session.commit()
            return beneficiary
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def delete_beneficiary(user_id, id, mpin):
        try:
            user = db.session.get(User, user_id)
            if not user:
                raise ValueError("User not found")
            if not AuthService.verify_mpin(user, mpin):
                raise ValueError("Invalid MPIN")

            beneficiary = Beneficiary.query.filter_by(id=id, user_id=user_id).first()
            if not beneficiary:
                raise ValueError("Beneficiary not found")

            # Soft delete
            beneficiary.is_active = False
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def toggle_favorite(user_id, id):
        try:
            beneficiary = Beneficiary.query.filter_by(id=id, user_id=user_id).first()
            if not beneficiary:
                raise ValueError("Beneficiary not found")

            beneficiary.is_favorite = not beneficiary.is_favorite
            db.session.commit()
            return beneficiary
        except Exception as e:
            db.session.rollback()
            raise e
