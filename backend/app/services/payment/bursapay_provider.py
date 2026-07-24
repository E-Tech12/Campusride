import os
import json
import hmac
import hashlib
from urllib import response
import requests

from app.services.payment.provider_base import PaymentProvider


class BursaPayProvider(PaymentProvider):

    def __init__(self):
        self.secret_key = os.getenv("BURSAPAY_SECRET_KEY")
        self.webhook_secret = os.getenv("BURSAPAY_WEBHOOK_SECRET")
        self.base_url = os.getenv(
            "BURSAPAY_BASE_URL",
            "https://bursapay.com/api/v1/gateway"
        )

    def _headers(self):
        return {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json"
        }

    def initialize_payment(
        self,
        email: str,
        amount: float,
        reference: str,
        callback_url: str = None
    ) -> dict:

        if not self.secret_key:
            raise ValueError(
                "BURSAPAY_SECRET_KEY not configured"
            )

        payload = {
            "amount": amount,
            "email": email,
            "idempotency_key": reference,
            "metadata": {
                "reference": reference
            }
        }

        if callback_url:
            payload["callback_url"] = callback_url

        response = requests.post(
                f"{self.base_url}/payments/initialize/",
                json=payload,
                headers=self._headers(),
                timeout=(10,60)
        )

        print("BURSA STATUS:", response.status_code)
        print("BURSA RESPONSE:", response.text)

        response.raise_for_status()

        data = response.json()

        payment_data = data.get("data", {})

        return {
            "authorization_url": payment_data.get("authorization_url"),
            "reference": payment_data.get("reference")
        }

    def verify_payment(
        self,
        reference: str
    ) -> dict:

        if not self.secret_key:
            raise ValueError(
                "BURSAPAY_SECRET_KEY not configured"
            )

        response = requests.post(
            f"{self.base_url}/payments/verify/",
            json={
                "reference": reference
            },
            headers=self._headers(),
            timeout=(10,60)
        )

        response.raise_for_status()

        data = response.json()

        payment_data = data.get("data", {})

        return {
            "status": data.get("success", False),
            "reference": payment_data.get("reference"),
            "amount": float(payment_data.get("amount", 0)),
            "customer": payment_data.get("customer", {}),
            "metadata": payment_data.get("metadata", {})
        }

    def resolve_account_number(
        self,
        account_number: str,
        bank_code: str
    ) -> dict:

        if not self.secret_key:
            raise ValueError(
                "BURSAPAY_SECRET_KEY not configured"
            )

        payload = {
            "account_number": account_number,
            "bank_code": bank_code,
        }

        candidate_paths = [
            "/bank/resolve/",
            "/banks/resolve/",
            "/account/resolve/",
            "/accounts/resolve/",
        ]
        last_exception = None

        for path in candidate_paths:
            url = f"{self.base_url}{path}"
            try:
                response = requests.post(
                    url,
                    json=payload,
                    headers=self._headers(),
                    timeout=(10, 60)
                )
                if response.status_code == 404:
                    continue
                if response.status_code == 405:
                    response = requests.get(
                        url,
                        params=payload,
                        headers=self._headers(),
                        timeout=(10, 60)
                    )
                response.raise_for_status()
                data = response.json()
                account_data = data.get("data", data)
                account_name = account_data.get("account_name") or account_data.get("customer_name")
                if not account_name:
                    raise ValueError("Bank verification succeeded but no account name was returned.")
                return {
                    "account_number": account_data.get("account_number", account_number),
                    "account_name": account_name,
                }
            except requests.exceptions.RequestException as exc:
                last_exception = exc
                continue

        raise ValueError(
            "Bank account verification is unavailable. Please try again later."
            if last_exception else
            "Unable to verify bank account details."
        )

    def verify_webhook_signature(
        self,
        payload_bytes: bytes,
        signature: str,
        timestamp: str
    ) -> bool:

        if not self.webhook_secret:
            return False

        try:
            payload = json.loads(payload_bytes)
        except Exception:
            return False

        compact = json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":")
        )

        expected = hmac.new(
            self.webhook_secret.encode(),
            f"{timestamp}.{compact}".encode(),
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(
            expected,
            signature
        )