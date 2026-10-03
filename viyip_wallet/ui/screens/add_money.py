"""Add money screen with Viyip payment system options."""

import tkinter as tk

from ... import styles as S
from .base import (BaseScreen, action_button, card, combo, divider, entry,
                   label, status_badge)


class AddMoneyScreen(BaseScreen):
    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, app, **kwargs)
        self._build()

    def _build(self):
        self.header("Add Money", show_back=True)

        c = card(self, padx=24, pady=24)
        c.pack(fill="x", padx=24, pady=24)

        label(c, "Amount (₹)", font=S.FONT_SMALL, fg=S.TEXT_MUTED).pack(
            anchor="w", pady=(0, 4))
        self.amount_entry = entry(c, width=36)
        self.amount_entry.pack(fill="x", pady=(0, 14))
        self.amount_entry.insert(0, "500")
        self.amount_entry.bind("<KeyRelease>", self._preview)

        label(c, "Payment Method", font=S.FONT_SMALL, fg=S.TEXT_MUTED).pack(
            anchor="w", pady=(0, 4))
        self.method_combo = combo(c)
        self.method_combo["values"] = ("card", "netbanking", "upi", "wallet")
        self.method_combo.set("card")
        self.method_combo.bind("<<ComboboxSelected>>", self._preview)
        self.method_combo.pack(fill="x", pady=(0, 14))

        label(c, "Source Account / UPI ID (optional)",
              font=S.FONT_SMALL, fg=S.TEXT_MUTED).pack(
            anchor="w", pady=(0, 4))
        self.source_entry = entry(c, width=36)
        self.source_entry.pack(fill="x", pady=(0, 14))
        self.source_entry.insert(0, "test@upi")

        # Fee preview
        self.preview = card(c, padx=16, pady=12)
        self.preview.pack(fill="x", pady=(0, 14))
        self.fee_label = label(self.preview, "Viyip fee: ₹0.00",
                               font=S.FONT_BODY, fg=S.TEXT)
        self.fee_label.pack(anchor="w")
        self.net_label = label(self.preview, "Net to be credited: ₹0.00",
                               font=S.FONT_BODY, fg=S.TEXT_MUTED)
        self.net_label.pack(anchor="w")

        self.status = status_badge(c, "", "info")
        self.status.pack(fill="x", pady=(0, 10))

        action_button(c, "Add Money", command=self._add, width=36).pack(
            fill="x")

        self._preview()

    def _preview(self, event=None):
        try:
            amount = float(self.amount_entry.get() or 0)
        except ValueError:
            amount = 0
        fee = self.app.wallet.get_fee_estimate(amount, "add_money")
        net = round(amount - fee, 2)
        self.fee_label.configure(text=f"Viyip fee: ₹{fee:,.2f}")
        self.net_label.configure(text=f"Net to be credited: ₹{net:,.2f}")

    def _add(self):
        try:
            amount = float(self.amount_entry.get() or 0)
        except ValueError:
            self.status.configure(text="Enter a valid amount", fg=S.DANGER)
            return
        method = self.method_combo.get()
        source = self.source_entry.get().strip()
        ok, msg, data = self.app.wallet.add_money(
            self.app.current_user_id(), amount, method, source)
        if ok:
            self.status.configure(text=msg, fg=S.SUCCESS)
            self.app.show_screen("DashboardScreen")
        else:
            self.status.configure(text=msg, fg=S.DANGER)