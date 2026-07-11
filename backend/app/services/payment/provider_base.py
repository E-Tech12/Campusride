import abc

class PaymentProvider(abc.ABC):
    
    @abc.abstractmethod
    def initialize_payment(self, email: str, amount: float, reference: str, callback_url: str = None) -> dict:
        """
        Initializes a payment intent.
        :param email: Customer email
        :param amount: Amount in main currency (e.g. NGN)
        :param reference: Unique transaction reference
        :param callback_url: URL to redirect after payment
        :return: dict containing 'authorization_url' and 'reference'
        """
        pass

    @abc.abstractmethod
    def verify_payment(self, reference: str) -> dict:
        """
        Verifies a payment status with the provider.
        :return: dict containing 'status' (bool), 'amount' (in main currency), 'currency', etc.
        """
        pass

    @abc.abstractmethod
    def verify_webhook_signature(self, payload_bytes: bytes, signature: str) -> bool:
        """
        Verifies that a webhook request actually came from the provider.
        """
        pass
