"""Viyip payment system gateway.

This module wraps the Viyip payment API. In this demo it uses a simulated
in-process backend so the app runs fully offline. The interface mirrors a
real REST client so it can be pointed at the live API by changing config.
"""

import hashlib
import random
import time
import uuid
from dataclasses import dataclass, field
from typing import Optional

from . import config


@dataclass
class ViyipChargeResult:
    success: bool
    charge_id: str
    amount: float
    fee: float
    net_amount: float
    method: str
    status: str
    message: str
    reference: Optional[str] = None


@dataclass
class ViyipTransferResult:
    success: bool
    transfer_id: str
    amount: float
    fee: float
    debit_amount: float
    recipient_viyip_id: str
    status: str
    message: str


@dataclass
class ViyipSettlement:
    settlement_id: str
    amount: float
    fee: float
    net: float
    method: str
    timestamp: str
    status: str


class ViyipGateway:
    """Simulated Viyip payment gateway client."""

    def __init__(self):
        self.api_key = config.VIYIP_API_KEY
        self.merchant_id = config.VIYIP_MERCHANT_ID
        # In-memory ledger for demo; replaced by DB in production.
        self._charges = []
        self._transfers = []

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _generate_id(self, prefix: str) -> str:
        return f"{prefix}_{uuid.uuid4().hex[:12].upper()}"

    def _simulate_latency(self):
        time.sleep(0.15)

    def _compute_fee(self, amount: float, kind: str) -> float:
        rate = config.VIYIP_FEES.get(kind, config.VIYIP_FEES["payment"])
        fee = round(amount * rate, 2)
        fee = max(config.VIYIP_MIN_FEE, min(config.VIYIP_MAX_FEE, fee))
        return fee

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def charge(self, amount: float, method: str,
               description: str = "", reference: Optional[str] = None
               ) -> ViyipChargeResult:
        """Charge a Viyip consumer account for a payment."""
        self._simulate_latency()
        if amount <= 0:
            return ViyipChargeResult(False, "", amount, 0, 0, method,
                                     "FAILED", "Amount must be positive")
        if method not in config.PAYMENT_METHODS:
            return ViyipChargeResult(False, "", amount, 0, 0, method,
                                     "FAILED", f"Unsupported method: {method}")

        fee = self._compute_fee(amount, "payment")
        net = round(amount - fee, 2)
        charge_id = self._generate_id("CHG")

        # Simulate success ~95% of the time, with deterministic failures
        # when the card number ends in a specific pattern for testing.
        success = True
        status = "SUCCESS"
        message = "Payment captured successfully"
        if reference and reference.lower().endswith("fail"):
            success = False
            status = "FAILED"
            message = "Payment declined by issuer"

        result = ViyipChargeResult(
            success=success, charge_id=charge_id, amount=amount,
            fee=fee, net_amount=net, method=method, status=status,
            message=message, reference=reference,
        )
        if success:
            self._charges.append(result)
        return result

    def transfer(self, amount: float, recipient_viyip_id: str,
                 note: str = "") -> ViyipTransferResult:
        """Transfer money from one Viyip consumer account to another."""
        self._simulate_latency()
        if amount <= 0:
            return ViyipTransferResult(False, "", amount, 0, 0, "",
                                       "FAILED", "Amount must be positive")
        if not recipient_viyip_id:
            return ViyipTransferResult(False, "", amount, 0, 0, "",
                                       "FAILED", "Recipient required")

        fee = self._compute_fee(amount, "transfer")
        debit = round(amount + fee, 2)
        transfer_id = self._generate_id("TRF")

        success = True
        status = "COMPLETED"
        message = "Transfer completed"
        if recipient_viyip_id.upper().endswith("FAIL"):
            success = False
            status = "FAILED"
            message = "Recipient account invalid"

        result = ViyipTransferResult(
            success=success, transfer_id=transfer_id, amount=amount,
            fee=fee, debit_amount=debit,
            recipient_viyip_id=recipient_viyip_id, status=status,
            message=message,
        )
        if success:
            self._transfers.append(result)
        return result

    def add_money(self, amount: float, method: str,
                  source_account: str = "") -> ViyipSettlement:
        """Add money to a Viyip consumer account from an external source."""
        self._simulate_latency()
        if amount <= 0:
            return ViyipSettlement("", amount, 0, 0, method,
                                   time.strftime("%Y-%m-%d %H:%M:%S"),
                                   "FAILED")
        if method not in config.PAYMENT_METHODS:
            return ViyipSettlement("", amount, 0, 0, method,
                                   time.strftime("%Y-%m-%d %H:%M:%S"),
                                   "FAILED")

        fee = self._compute_fee(amount, "add_money")
        net = round(amount - fee, 2)
        settlement_id = self._generate_id("SET")

        success = True
        status = "SETTLED"
        message = "Money added to Viyip account"
        if source_account and source_account.lower().endswith("fail"):
            success = False
            status = "FAILED"
            message = "Source account rejected"

        settlement = ViyipSettlement(
            settlement_id=settlement_id, amount=amount, fee=fee,
            net=net, method=method,
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
            status=status if success else "FAILED",
        )
        return settlement

    def get_fee_estimate(self, amount: float, kind: str) -> float:
        """Return the fee Viyip would charge for a given amount/kind."""
        return self._compute_fee(amount, kind)

    def get_total_fees_collected(self) -> float:
        return round(sum(c.fee for c in self._charges) +
                     sum(t.fee for t in self._transfers), 2)