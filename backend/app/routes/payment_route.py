from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
import uuid
import requests

from app.extensions import db, limiter
from app.models import (
    Payment,
    PaymentStatus,
    PaymentWebhookLog,
    User
)

from app.services.payment.bursapay_provider import BursaPayProvider
from app.services.payment.wallet_service import WalletService

payment_bp = Blueprint(
    "payment",
    __name__,
    url_prefix="/api/payments"
)

provider = BursaPayProvider()


@payment_bp.route("/wallet", methods=["GET"])
@jwt_required()
def get_wallet():

    user_id = int(get_jwt_identity())

    wallet = WalletService.get_or_create_wallet(
        user_id
    )

    return jsonify({
        "balance": wallet.balance,
        "pending_balance": wallet.pending_balance
    }), 200


@payment_bp.route("/transactions", methods=["GET"])
@jwt_required()
def get_transactions():

    user_id = int(get_jwt_identity())

    wallet = WalletService.get_or_create_wallet(
        user_id
    )

    from app.models import WalletTransaction

    limit = request.args.get(
        "limit",
        default=20,
        type=int
    )

    transactions = (
        WalletTransaction.query
        .filter_by(wallet_id=wallet.id)
        .order_by(
            WalletTransaction.created_at.desc()
        )
        .limit(limit)
        .all()
    )

    return jsonify(
        [txn.to_dict() for txn in transactions]
    ), 200


@payment_bp.route("/deposit", methods=["POST"])
@jwt_required()
@limiter.limit("10 per minute")
def initialize_deposit():

    user_id = int(get_jwt_identity())

    data = request.get_json() or {}

    amount = data.get("amount")

    if not amount:
        return jsonify({
            "error": "Amount required"
        }), 400

    if float(amount) <= 0:
        return jsonify({
            "error": "Invalid amount"
        }), 400

    try:

        user = User.query.get(user_id)

        local_reference = (
            f"dep_{uuid.uuid4().hex}"
        )

        callback_url = data.get(
            "callback_url"
        )

        result = provider.initialize_payment(
            email=user.email,
            amount=float(amount),
            reference=local_reference,
            callback_url=f"{current_app.config['FRONTEND_URL']}/wallet/verify"
        )

        bursa_reference = result["reference"]

        payment = Payment(
            user_id=user_id,
            amount=float(amount),
            provider="bursapay",
            provider_reference=bursa_reference,
            purpose="wallet_deposit",
            status=PaymentStatus.PENDING,
            meta_data={
                "local_reference": local_reference
            }
        )

        db.session.add(payment)
        db.session.commit()

        return jsonify({
            "authorization_url":
                result["authorization_url"],
            "reference":
                bursa_reference
        })

    except requests.exceptions.Timeout:

        current_app.logger.exception(
            "BursaPay timeout"
        )

        return jsonify({
            "error": "Payment provider timeout. Please try again."
        }), 504


    except requests.exceptions.ConnectionError:

        current_app.logger.exception(
            "BursaPay connection failed"
        )

        return jsonify({
            "error": "Unable to connect to payment provider."
        }), 503


    except requests.exceptions.HTTPError as e:

        current_app.logger.exception(e)

        return jsonify({
            "error": "Payment provider rejected request",
            "details": str(e)
        }), 502

@payment_bp.route(
    "/webhook/bursapay",
    methods=["POST"]
)
def bursapay_webhook():

    signature = request.headers.get(
        "X-BursaPay-Signature"
    )

    timestamp = request.headers.get(
        "X-BursaPay-Timestamp"
    )

    payload = request.get_data()

    if not provider.verify_webhook_signature(
        payload,
        signature,
        timestamp
    ):
        return jsonify({
            "error": "Invalid signature"
        }), 400

    data = request.get_json()

    event = data.get("event")

    log = PaymentWebhookLog(
        provider="bursapay",
        event_type=event,
        payload=data
    )

    db.session.add(log)

    try:

        if event == "payment.success":

            payment_data = data.get(
                "data",
                {}
            )

            reference = payment_data.get(
                "reference"
            )

            payment = Payment.query.filter_by(
                provider_reference=reference
            ).first()

            if (
                payment and
                payment.status ==
                PaymentStatus.PENDING
            ):

                WalletService.deposit(
                    user_id=payment.user_id,
                    amount=payment.amount,
                    reference=reference,
                    description=
                    "Wallet Deposit via BursaPay"
                )

                payment.status = (
                    PaymentStatus.SUCCESS
                )

                log.processed = True

        db.session.commit()

    except Exception as e:

        current_app.logger.exception(e)

        db.session.rollback()

    return jsonify({
        "status": "received"
    }), 200


@payment_bp.route(
    "/verify/<reference>",
    methods=["GET"]
)
@jwt_required()
def verify_payment(reference):

    payment = Payment.query.filter_by(
        provider_reference=reference
    ).first()

    if not payment:

        return jsonify({
            "error": "Payment not found"
        }), 404

    if payment.status == PaymentStatus.SUCCESS:

        return jsonify({
            "success": True,
            "status": "success"
        })

    try:

        result = provider.verify_payment(
            reference
        )

        if result["status"]:

            WalletService.deposit(
                user_id=payment.user_id,
                amount=payment.amount,
                reference=reference,
                description=
                "Wallet Deposit"
            )

            payment.status = (
                PaymentStatus.SUCCESS
            )

            db.session.commit()

            return jsonify({
                "success": True,
                "status": "success"
            })

        return jsonify({
            "success": False,
            "status": "pending"
        })

    except Exception as e:

        current_app.logger.exception(e)

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500