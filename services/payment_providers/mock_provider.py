from services.payment_providers.base import PaymentProvider
import uuid

class MockPaymentProvider(PaymentProvider):
    def create_payment(self, amount, currency, description, metadata):
        return {
            'payment_id': str(uuid.uuid4()),
            'status': 'SUCCESS',
            'watermark': 'DEMO',
            'amount': amount,
            'currency': currency,
            'description': description
        }

    def verify_payment(self, payment_id):
        return {
            'payment_id': payment_id,
            'status': 'VERIFIED',
            'watermark': 'DEMO'
        }

    def refund_payment(self, payment_id, amount):
        return {
            'payment_id': payment_id,
            'status': 'REFUNDED',
            'amount': amount,
            'watermark': 'DEMO'
        }

    def get_payment_status(self, payment_id):
        return {
            'payment_id': payment_id,
            'status': 'SUCCESS',
            'watermark': 'DEMO'
        }
