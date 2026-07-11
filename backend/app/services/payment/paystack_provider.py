import os
import hmac
import hashlib
import requests
from flask import current_app
from app.services.payment.provider_base import PaymentProvider

class PaystackProvider(PaymentProvider):
    def __init__(self):
        self.secret_key = os.getenv("PAYSTACK_SECRET_KEY")
        self.base_url = "https://api.paystack.co"

    def _headers(self):
        return {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json"
        }

    def initialize_payment(self, email: str, amount: float, reference: str, callback_url: str = None) -> dict:
        if not self.secret_key:
            raise ValueError("Paystack secret key is not set.")
        
        payload = {
            "email": email,
            "amount": int(amount * 100), # Paystack uses kobo
            "reference": reference,
        }
        if callback_url:
            payload["callback_url"] = callback_url

        response = requests.post(
            f"{self.base_url}/transaction/initialize",
            json=payload,
            headers=self._headers()
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to initialize payment: {response.text}")
        
        data = response.json()["data"]
        return {
            "authorization_url": data["authorization_url"],
            "reference": data["reference"]
        }

    def verify_payment(self, reference: str) -> dict:
        if not self.secret_key:
            raise ValueError("Paystack secret key is not set.")

        response = requests.get(
            f"{self.base_url}/transaction/verify/{reference}",
            headers=self._headers()
        )
        
        if response.status_code != 200:
            return {"status": False, "message": "Verification failed."}
        
        data = response.json()["data"]
        return {
            "status": data["status"] == "success",
            "amount": data["amount"] / 100.0, # convert back to main currency
            "currency": data["currency"],
            "metadata": data.get("metadata", {})
        }

    def verify_webhook_signature(self, payload_bytes: bytes, signature: str) -> bool:
        if not self.secret_key:
            return False
            
        hash_val = hmac.new(
            self.secret_key.encode('utf-8'),
            payload_bytes,
            hashlib.sha512
        ).hexdigest()
        return hash_val == signature
