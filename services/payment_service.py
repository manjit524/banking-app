from models import Biller, Bill, ScheduledPayment, User
from services.transaction_service import TransactionService
from services.auth_service import AuthService
from extensions import db
from decimal import Decimal

class PaymentService:
    @staticmethod
    def get_billers(category=None):
        query = Biller.query.filter_by(is_active=True)
        if category:
            query = query.filter_by(category=category)
        return query.all()

    @staticmethod
    def pay_bill(user_id, from_account_id, biller_id, amount, consumer_number, mpin):
        try:
            user = User.query.get(user_id)
            if not AuthService.verify_mpin(user, mpin):
                raise ValueError("Invalid MPIN")

            biller = Biller.query.get(biller_id)
            if not biller or not biller.is_active:
                raise ValueError("Invalid Biller")

            bill = Bill(
                user_id=user_id,
                biller_id=biller_id,
                amount=Decimal(amount),
                consumer_number=consumer_number,
                status='PENDING'
            )
            db.session.add(bill)
            db.session.flush()

            txn = TransactionService.withdraw(
                account_id=from_account_id,
                amount=amount,
                description=f"Bill Payment: {biller.name}"
            )

            bill.transaction_id = txn.id
            bill.status = 'PAID'
            db.session.commit()
            return bill
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def get_user_bills(user_id, status=None):
        query = Bill.query.filter_by(user_id=user_id)
        if status:
            query = query.filter_by(status=status)
        return query.all()

    @staticmethod
    def create_scheduled_payment(user_id, from_account_id, to_account_id, amount, frequency, start_date, description=None, end_date=None):
        try:
            payment = ScheduledPayment(
                user_id=user_id,
                from_account_id=from_account_id,
                to_account_id=to_account_id,
                amount=Decimal(amount),
                frequency=frequency,
                start_date=start_date,
                end_date=end_date,
                description=description,
                status='ACTIVE'
            )
            db.session.add(payment)
            db.session.commit()
            return payment
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def get_user_scheduled_payments(user_id):
        return ScheduledPayment.query.filter_by(user_id=user_id, status='ACTIVE').all()

    @staticmethod
    def cancel_scheduled_payment(payment_id, user_id):
        try:
            payment = ScheduledPayment.query.filter_by(id=payment_id, user_id=user_id).first()
            if not payment:
                raise ValueError("Payment not found")
            payment.status = 'CANCELLED'
            db.session.commit()
            return payment
        except Exception as e:
            db.session.rollback()
            raise e
