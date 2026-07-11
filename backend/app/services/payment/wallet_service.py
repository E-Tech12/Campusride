import uuid
from datetime import datetime
from app.extensions import db
from app.models import Wallet, WalletTransaction, TransactionType, TransactionStatus

class WalletService:
    @staticmethod
    def get_or_create_wallet(user_id):
        wallet = Wallet.query.filter_by(user_id=user_id).first()
        if not wallet:
            wallet = Wallet(user_id=user_id)
            db.session.add(wallet)
            db.session.commit()
        return wallet

    @staticmethod
    def deposit(user_id, amount, reference, description="Deposit"):
        wallet = WalletService.get_or_create_wallet(user_id)
        
        with db.session.begin_nested():
            if WalletTransaction.query.filter_by(reference=reference).first():
                raise ValueError("Transaction reference already exists")

            wallet.balance += amount
            txn = WalletTransaction(
                wallet_id=wallet.id,
                amount=amount,
                transaction_type=TransactionType.DEPOSIT,
                status=TransactionStatus.SUCCESS,
                reference=reference,
                description=description,
                completed_at=datetime.utcnow()
            )
            db.session.add(txn)
        db.session.commit()
        return wallet.balance

    @staticmethod
    def hold_funds_for_ride(user_id, amount, reference, description="Ride Payment Hold"):
        wallet = WalletService.get_or_create_wallet(user_id)
        
        with db.session.begin_nested():
            if wallet.balance < amount:
                raise ValueError("Insufficient balance")
                
            wallet.balance -= amount
            wallet.pending_balance += amount
            
            txn = WalletTransaction(
                wallet_id=wallet.id,
                amount=-amount,
                transaction_type=TransactionType.RIDE_PAYMENT,
                status=TransactionStatus.PENDING,
                reference=reference,
                description=description
            )
            db.session.add(txn)
        db.session.commit()
        return txn

    @staticmethod
    def complete_ride_payment(student_id, driver_user_id, amount, reference, platform_fee_percent=10):
        """NOTE: driver_user_id must be the driver's User.id (Wallet.user_id is a
        FK to users.id), not their Driver.id -- passing the Driver row's primary
        key here silently credits the wrong account."""
        student_wallet = WalletService.get_or_create_wallet(student_id)
        driver_wallet = WalletService.get_or_create_wallet(driver_user_id)
        
        platform_fee = amount * (platform_fee_percent / 100.0)
        driver_earning = amount - platform_fee
        
        with db.session.begin_nested():
            txn = WalletTransaction.query.filter_by(reference=reference, transaction_type=TransactionType.RIDE_PAYMENT, status=TransactionStatus.PENDING).first()
            if not txn:
                raise ValueError("Pending ride payment transaction not found")
                
            student_wallet.pending_balance -= amount
            txn.status = TransactionStatus.SUCCESS
            txn.completed_at = datetime.utcnow()
            
            driver_wallet.balance += driver_earning
            driver_txn = WalletTransaction(
                wallet_id=driver_wallet.id,
                amount=driver_earning,
                transaction_type=TransactionType.DRIVER_EARNING,
                status=TransactionStatus.SUCCESS,
                reference=f"ern_{reference}",
                description="Driver earning for ride",
                completed_at=datetime.utcnow()
            )
            db.session.add(driver_txn)
            
            comm_txn = WalletTransaction(
                wallet_id=driver_wallet.id, # Attaching logical fee track to driver wallet (or could be an admin wallet)
                amount=platform_fee,
                transaction_type=TransactionType.PLATFORM_COMMISSION,
                status=TransactionStatus.SUCCESS,
                reference=f"com_{reference}",
                description="Platform commission for ride",
                completed_at=datetime.utcnow()
            )
            db.session.add(comm_txn)
            
        db.session.commit()
        
    @staticmethod
    def refund_ride_payment(user_id, amount, reference, description="Ride Refund"):
        wallet = WalletService.get_or_create_wallet(user_id)
        
        with db.session.begin_nested():
            txn = WalletTransaction.query.filter_by(reference=reference, transaction_type=TransactionType.RIDE_PAYMENT, status=TransactionStatus.PENDING).first()
            if not txn:
                raise ValueError("Pending ride payment transaction not found")
                
            wallet.pending_balance -= amount
            wallet.balance += amount
            
            txn.status = TransactionStatus.FAILED
            txn.completed_at = datetime.utcnow()
            
            refund_txn = WalletTransaction(
                wallet_id=wallet.id,
                amount=amount,
                transaction_type=TransactionType.RIDE_REFUND,
                status=TransactionStatus.SUCCESS,
                reference=f"ref_{reference}",
                description=description,
                completed_at=datetime.utcnow()
            )
            db.session.add(refund_txn)
            
        db.session.commit()
