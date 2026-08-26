from abc import ABC, abstractmethod

class PaymentProvider(ABC):
    @abstractmethod
    def create_payment(self, amount, currency, description, metadata):
        pass

    @abstractmethod
    def verify_payment(self, payment_id):
        pass

    @abstractmethod
    def refund_payment(self, payment_id, amount):
        pass

    @abstractmethod
    def get_payment_status(self, payment_id):
        pass
