from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
import uuid

from app.extensions import db, limiter
from app.models import Payment, PaymentStatus, PaymentWebhookLog, User
from app.services.payment.paystack_provider import PaystackProvider
from app.services.payment.wallet_service import WalletService

payment_bp = Blueprint("payment", __name__, url_prefix="/api/payments")
provider = PaystackProvider()


@payment_bp.route("/wallet", methods=["GET"])
@jwt_required()
def get_wallet():
    user_id = int(get_jwt_identity())
    wallet = WalletService.get_or_create_wallet(user_id)
    return jsonify({
        "balance": wallet.balance,
        "pending_balance": wallet.pending_balance,
    }), 200


@payment_bp.route("/transactions", methods=["GET"])
@jwt_required()
def get_transactions():
    user_id = int(get_jwt_identity())
    wallet = WalletService.get_or_create_wallet(user_id)
    limit = request.args.get("limit", default=20, type=int)
    from app.models import WalletTransaction
    txns = WalletTransaction.query.filter_by(wallet_id=wallet.id) \
        .order_by(WalletTransaction.created_at.desc()).limit(limit).all()
    return jsonify([t.to_dict() for t in txns]), 200


@payment_bp.route("/deposit", methods=["POST"])
@jwt_required()
@limiter.limit("10 per minute")
def initialize_deposit():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    amount = data.get("amount")
    
    if not amount or amount <= 0:
        return jsonify({"error": "Invalid amount"}), 400
        
    reference = f"dep_{uuid.uuid4().hex}"
    
    try:
        user = User.query.get(user_id)
        
        result = provider.initialize_payment(
            email=user.email,
            amount=amount,
            reference=reference,
            callback_url=data.get("callback_url")
        )
        
        payment = Payment(
            user_id=user_id,
            amount=amount,
            provider="paystack",
            provider_reference=reference,
            purpose="wallet_deposit"
        )
        db.session.add(payment)
        db.session.commit()
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@payment_bp.route("/webhook/paystack", methods=["POST"])
def paystack_webhook():
    signature = request.headers.get("x-paystack-signature")
    payload = request.get_data()
    
    if not provider.verify_webhook_signature(payload, signature):
        return jsonify({"error": "Invalid signature"}), 400
        
    data = request.get_json()
    event = data.get("event")
    
    log = PaymentWebhookLog(
        provider="paystack",
        event_type=event,
        payload=data
    )
    db.session.add(log)
    
    if event == "charge.success":
        ref = data["data"]["reference"]
        payment = Payment.query.filter_by(provider_reference=ref).first()
        if payment and payment.status == PaymentStatus.PENDING:
            try:
                WalletService.deposit(
                    user_id=payment.user_id,
                    amount=payment.amount,
                    reference=ref,
                    description="Wallet Deposit via Paystack"
                )
                payment.status = PaymentStatus.SUCCESS
                log.processed = True
            except Exception as e:
                current_app.logger.error(f"Webhook processing error: {e}")
                
    db.session.commit()
    return jsonify({"status": "received"}), 200
