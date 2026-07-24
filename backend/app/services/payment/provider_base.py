import abc


class PaymentProvider(abc.ABC):

    @abc.abstractmethod
    def initialize_payment(
        self,
        email: str,
        amount: float,
        reference: str,
        callback_url: str = None
    ) -> dict:
        """
        Initialize a payment.
        """
        pass

    @abc.abstractmethod
    def verify_payment(
        self,
        reference: str
    ) -> dict:
        """
        Verify a payment.
        """
        pass

    @abc.abstractmethod
    def resolve_account_number(
        self,
        account_number: str,
        bank_code: str
    ) -> dict:
        """
        Resolve a bank account number to a verified account name.
        """
        pass

    @abc.abstractmethod
    def verify_webhook_signature(
        self,
        payload_bytes: bytes,
        signature: str,
        timestamp: str
    ) -> bool:
        """
        Verify BursaPay webhook signature.
        """
        pass