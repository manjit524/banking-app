"""
services/card_service.py — Card management logic for simulated debit cards
"""
import random
import string
import hashlib
from datetime import datetime, date
from decimal import Decimal
from models import Card, Account, User
from models.card import CardType, CardStatus, generate_card_number, generate_cvv
from extensions import db

class CardService:
    @staticmethod
    def get_user_cards(user_id):
        # Join cards with accounts to filter by user_id
        return Card.query.join(Account).filter(Account.user_id == user_id).all()

    @staticmethod
    def get_user_eligible_accounts(user_id):
        # Return accounts that do not already have a virtual debit card
        subquery = Card.query.join(Account).filter(Account.user_id == user_id).with_entities(Card.account_id).subquery()
        return Account.query.filter(Account.user_id == user_id, ~Account.id.in_(subquery)).all()

    @staticmethod
    def issue_virtual_card(user_id, account_id, card_type_str='Virtual Debit'):
        try:
            account = Account.query.filter_by(id=account_id, user_id=user_id).first()
            if not account:
                raise ValueError("Account not found")

            # Check if card already exists for this account
            existing = Card.query.filter_by(account_id=account_id).first()
            if existing:
                raise ValueError("Card already exists for this account")

            raw_number = '41111' + ''.join(random.choices(string.digits, k=11))
            hashed_number = hashlib.sha256(raw_number.encode()).hexdigest()
            last4 = raw_number[-4:]
            masked = f"**** **** **** {last4}"
            
            today = date.today()
            expiry_month = today.month
            expiry_year = today.year + 5  # 5 years expiry

            card = Card(
                account_id=account_id,
                card_number_hash=hashed_number,
                card_number_last4=last4,
                card_number_masked=masked,
                expiry_month=expiry_month,
                expiry_year=expiry_year,
                card_holder_name=account.owner.name.upper(),
                card_type=CardType.VIRTUAL_DEBIT,
                card_network='VISA',
                status=CardStatus.ACTIVE,
                is_frozen=False,
                online_payments_enabled=True,
                international_payments_enabled=False,
                contactless_enabled=True,
                daily_limit=Decimal('50000.00')
            )
            db.session.add(card)
            db.session.commit()
            return card
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def toggle_freeze(user_id, card_id):
        try:
            card = Card.query.join(Account).filter(Card.id == card_id, Account.user_id == user_id).first()
            if not card:
                raise ValueError("Card not found")
            card.is_frozen = not card.is_frozen
            db.session.commit()
            return card
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def toggle_online(user_id, card_id):
        try:
            card = Card.query.join(Account).filter(Card.id == card_id, Account.user_id == user_id).first()
            if not card:
                raise ValueError("Card not found")
            card.online_payments_enabled = not card.online_payments_enabled
            db.session.commit()
            return card
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def toggle_international(user_id, card_id):
        try:
            card = Card.query.join(Account).filter(Card.id == card_id, Account.user_id == user_id).first()
            if not card:
                raise ValueError("Card not found")
            card.international_payments_enabled = not card.international_payments_enabled
            db.session.commit()
            return card
        except Exception as e:
            db.session.rollback()
            raise e
