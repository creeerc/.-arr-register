"""Merchant payment screen using Viyip payment system."""

import tkinter as tk

from .. import styles as S
from ..base import (BaseScreen, action_button, card, combo, divider, entry,
                   label, status_badge)


class PaymentScreen(BaseScreen):
    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, app, **kwargs)
        self._build()

    def _build(self):
        self.header("Make Payment", show_back=True)

        c = card(self, padx=24, pady=24)
        c.pack(fill="x", padx=24, pady=24)

        label(c, "Merchant Name", font=S.FONT_SMALL, fg=S.TEXT_MUTED).pack(
            anchor="w", pady=(0, 4))
        self.merchant_entry = entry(c, width=36)
        self.merchant_entry.pack(fill="x", pady=(0, 14))
        self.merchant_entry.insert(0, "Amazon")

        label(c, "Amount (₹)", font=S.FONT_SMALL, fg=S.TEXT_MUTED).pack(
            anchor="w", pady=(0, 4))
        self.amount_entry = entry(c, width=36)
        self.amount_entry.pack(fill="x", pady=(0, 14))
        self.amount_entry.insert(0, "499")
        self.amount_entry.bind("<KeyRelease>", self._preview)

        label(c, "Payment Method", font=S.FONT_SMALL, fg=S.TEXT_MUTED).pack(
            anchor="w", pady=(0, 4))
        self.method_combo = combo(c)
        self.method_combo["values"] = ("viyip", "card", "upi", "netbanking")
        self.method_combo.set("viyip")
        self.method_combo.bind("<<ComboboxSelected>>", self._preview)
        self.method_combo.pack(fill="x", pady=(0, 14))

        label(c, "Order / Reference (optional)",
              font=S.FONT_SMALL, fg=S.TEXT_MUTED).pack(
            anchor="w", pady=(0, 4))
        self.ref_entry = entry(c, width=36)
        self.ref_entry.pack(fill="x", pady=(0, 14))

        # Fee preview
        self.preview = card(c, padx=16, pady=12)
        self.preview.pack(fill="x", pady=(0, 14))
        self.fee_label = label(self.preview, "Viyip fee: ₹0.00",
                               font=S.FONT_BODY, fg=S.TEXT)
        self.fee_label.pack(anchor="w")
        self.total_label = label(self.preview, "Amount to pay: ₹0.00",
                                 font=S.FONT_BODY, fg=S.TEXT_MUTED)
        self.total_label.pack(anchor="w")

        self.status = status_badge(c, "", "info")
        self.status.pack(fill="x", pady=(0, 10))

        action_button(c, "Pay Now", command=self._pay, width=36).pack(
            fill="x")

        self._preview()

    def _preview(self, event=None):
        try:
            amount = float(self.amount_entry.get() or 0)
        except ValueError:
            amount = 0
        fee = self.app.wallet.get_fee_estimate(amount, "payment")
        self.fee_label.configure(text=f"Viyip fee: ₹{fee:,.2f}")
        self.total_label.configure(text=f"Amount to pay: ₹{amount:,.2f}")

    def _pay(self):
        try:
            amount = float(self.amount_entry.get() or 0)
        except ValueError:
            self.status.configure(text="Enter a valid amount", fg=S.DANGER)
            return
        merchant = self.merchant_entry.get().strip()
        method = self.method_combo.get()
        reference = self.ref_entry.get().strip()
        ok, msg, data = self.app.wallet.make_payment(
            self.app.current_user_id(), merchant, amount, method, reference)
        if ok:
            self.status.configure(text=msg, fg=S.SUCCESS)
            self.app.show_screen("DashboardScreen")
        else:
            self.status.configure(text=msg, fg=S.DANGER)