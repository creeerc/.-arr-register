"""Wallet service: orchestrates Viyip gateway + database."""

import uuid
from typing import Optional, Tuple

from . import config
from .database import Database
from .viyip_gateway import ViyipGateway


class WalletService:
    """High-level wallet operations backed by DB + Viyip gateway."""

    def __init__(self, db: Database, gateway: ViyipGateway):
        self.db = db
        self.gateway = gateway

    # ------------------------------------------------------------------
    # Auth
    # ------------------------------------------------------------------
    def signup(self, name: str, email: str, password: str) -> Tuple[bool, str, Optional[dict]]:
        if not name or not email or not password:
            return False, "All fields are required", None
        if "@" not in email or "." not in email:
            return False, "Invalid email address", None
        if len(password) < 6:
            return False, "Password must be at least 6 characters", None

        password_hash = self._hash_password(password)
        viyip_id = self._generate_viyip_id(name)
        user_id = self.db.create_user(viyip_id, name, email, password_hash)
        if user_id is None:
            return False, "Email already registered", None
        user = self.db.get_user_by_id(user_id)
        return True, "Account created", user

    def login(self, email: str, password: str) -> Tuple[bool, str, Optional[dict]]:
        if not email or not password:
            return False, "Email and password required", None
        user = self.db.get_user_by_email(email)
        if user is None:
            return False, "No account found with that email", None
        if self._hash_password(password) != user["password_hash"]:
            return False, "Incorrect password", None
        return True, "Logged in", user

    # ------------------------------------------------------------------
    # Add money
    # ------------------------------------------------------------------
    def add_money(self, user_id: int, amount: float, method: str,
                  source_account: str = "") -> Tuple[bool, str, Optional[dict]]:
        if amount <= 0:
            return False, "Amount must be greater than 0", None
        if method not in config.PAYMENT_METHODS:
            return False, f"Unsupported payment method: {method}", None

        settlement = self.gateway.add_money(amount, method, source_account)
        if settlement.status != "SETTLED":
            return False, settlement.status, None

        # Credit the user's wallet (net amount after Viyip fee)
        current_balance = self.db.get_balance(user_id)
        new_balance = round(current_balance + settlement.net, 2)
        self.db.update_balance(user_id, new_balance)

        tx_id = settlement.settlement_id
        self.db.add_transaction(
            tx_id=tx_id, user_id=user_id, tx_type="add_money",
            amount=settlement.net, fee=settlement.fee,
            debit=settlement.amount, balance_after=new_balance,
            method=method, status="COMPLETED",
            note=f"Added money via {method}",
        )
        return True, "Money added", {
            "settlement_id": settlement.settlement_id,
            "amount": settlement.amount,
            "fee": settlement.fee,
            "net": settlement.net,
            "balance": new_balance,
        }

    # ------------------------------------------------------------------
    # Transfer / Send money
    # ------------------------------------------------------------------
    def transfer(self, user_id: int, recipient_viyip_id: str,
                 amount: float, note: str = "") -> Tuple[bool, str, Optional[dict]]:
        if amount <= 0:
            return False, "Amount must be greater than 0", None
        if not recipient_viyip_id:
            return False, "Recipient Viyip ID is required", None

        recipient = self.db.get_user_by_viyip_id(recipient_viyip_id)
        if recipient is None:
            return False, "Recipient Viyip account not found", None
        if recipient["id"] == user_id:
            return False, "Cannot transfer to yourself", None

        result = self.gateway.transfer(amount, recipient_viyip_id, note)
        if not result.success:
            return False, result.message, None

        # Debit sender
        sender_balance = self.db.get_balance(user_id)
        if sender_balance < result.debit_amount:
            return False, "Insufficient balance", None
        new_sender_balance = round(sender_balance - result.debit_amount, 2)
        self.db.update_balance(user_id, new_sender_balance)

        tx_id = result.transfer_id
        self.db.add_transaction(
            tx_id=tx_id, user_id=user_id, tx_type="transfer_out",
            amount=result.amount, fee=result.fee,
            debit=result.debit_amount, balance_after=new_sender_balance,
            counterparty=recipient_viyip_id, method="viyip",
            status="COMPLETED", note=note or f"Sent to {recipient_viyip_id}",
        )

        # Credit recipient
        recip_balance = self.db.get_balance(recipient["id"])
        new_recip_balance = round(recip_balance + result.amount, 2)
        self.db.update_balance(recipient["id"], new_recip_balance)
        self.db.add_transaction(
            tx_id=tx_id, user_id=recipient["id"], tx_type="transfer_in",
            amount=result.amount, fee=0.0, debit=0.0,
            balance_after=new_recip_balance, counterparty=None,
            method="viyip", status="COMPLETED",
            note=note or f"Received from sender",
        )

        return True, "Transfer completed", {
            "transfer_id": result.transfer_id,
            "amount": result.amount,
            "fee": result.fee,
            "debit": result.debit_amount,
            "balance": new_sender_balance,
        }

    # ------------------------------------------------------------------
    # Payment (merchant)
    # ------------------------------------------------------------------
    def make_payment(self, user_id: int, merchant_name: str, amount: float,
                     method: str = "viyip", reference: str = ""
                     ) -> Tuple[bool, str, Optional[dict]]:
        if amount <= 0:
            return False, "Amount must be greater than 0", None
        if not merchant_name:
            return False, "Merchant name required", None

        charge = self.gateway.charge(amount, method, description=merchant_name,
                                     reference=reference)
        if not charge.success:
            return False, charge.message, None

        # Deduct from wallet (net amount charged)
        balance = self.db.get_balance(user_id)
        if balance < charge.amount:
            return False, "Insufficient balance", None
        new_balance = round(balance - charge.amount, 2)
        self.db.update_balance(user_id, new_balance)

        self.db.add_transaction(
            tx_id=charge.charge_id, user_id=user_id, tx_type="payment",
            amount=charge.amount, fee=charge.fee, debit=charge.amount,
            balance_after=new_balance, counterparty=merchant_name,
            method=method, status="COMPLETED",
            note=f"Payment to {merchant_name}",
        )
        return True, "Payment successful", {
            "charge_id": charge.charge_id,
            "amount": charge.amount,
            "fee": charge.fee,
            "net": charge.net_amount,
            "balance": new_balance,
        }

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------
    def get_balance(self, user_id: int) -> float:
        return self.db.get_balance(user_id)

    def get_history(self, user_id: int, limit: int = 50):
        return self.db.get_transactions(user_id, limit)

    def get_fee_estimate(self, amount: float, kind: str) -> float:
        return self.gateway.get_fee_estimate(amount, kind)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _hash_password(self, password: str) -> str:
        import hashlib
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    def _generate_viyip_id(self, name: str) -> str:
        import random, string
        prefix = "".join(c for c in name.upper() if c.isalnum())[:4] or "USER"
        suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
        return f"viyip_{prefix}{suffix}"