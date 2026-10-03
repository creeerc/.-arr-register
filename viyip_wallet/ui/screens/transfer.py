"""Transfer / send money screen."""

import tkinter as tk

from ... import styles as S
from .base import (BaseScreen, action_button, card, divider, entry, label,
                   status_badge)


class TransferScreen(BaseScreen):
    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, app, **kwargs)
        self._build()

    def _build(self):
        self.header("Send Money", show_back=True)

        c = card(self, padx=24, pady=24)
        c.pack(fill="x", padx=24, pady=24)

        label(c, "Recipient Viyip ID", font=S.FONT_SMALL, fg=S.TEXT_MUTED).pack(
            anchor="w", pady=(0, 4))
        self.recipient_entry = entry(c, width=36)
        self.recipient_entry.pack(fill="x", pady=(0, 14))
        self.recipient_entry.insert(0, "viyip_USER123456")

        label(c, "Amount (₹)", font=S.FONT_SMALL, fg=S.TEXT_MUTED).pack(
            anchor="w", pady=(0, 4))
        self.amount_entry = entry(c, width=36)
        self.amount_entry.pack(fill="x", pady=(0, 8))
        self.amount_entry.insert(0, "100")
        self.amount_entry.bind("<KeyRelease>", self._preview)

        label(c, "Note (optional)", font=S.FONT_SMALL, fg=S.TEXT_MUTED).pack(
            anchor="w", pady=(8, 4))
        self.note_entry = entry(c, width=36)
        self.note_entry.pack(fill="x", pady=(0, 14))
        self.note_entry.insert(0, "Gift")

        # Fee preview
        self.preview = card(c, padx=16, pady=12)
        self.preview.pack(fill="x", pady=(0, 14))
        self.fee_label = label(self.preview, "Viyip fee: ₹0.00",
                               font=S.FONT_BODY, fg=S.TEXT)
        self.fee_label.pack(anchor="w")
        self.total_label = label(self.preview, "Total to debit: ₹0.00",
                                 font=S.FONT_BODY, fg=S.TEXT_MUTED)
        self.total_label.pack(anchor="w")

        self.status = status_badge(c, "", "info")
        self.status.pack(fill="x", pady=(0, 10))

        action_button(c, "Send Money", command=self._transfer, width=36).pack(
            fill="x")

        self._preview()

    def _preview(self, event=None):
        try:
            amount = float(self.amount_entry.get() or 0)
        except ValueError:
            amount = 0
        fee = self.app.wallet.get_fee_estimate(amount, "transfer")
        total = round(amount + fee, 2)
        self.fee_label.configure(text=f"Viyip fee: ₹{fee:,.2f}")
        self.total_label.configure(text=f"Total to debit: ₹{total:,.2f}")

    def _transfer(self):
        try:
            amount = float(self.amount_entry.get() or 0)
        except ValueError:
            self.status.configure(text="Enter a valid amount", fg=S.DANGER)
            return
        recipient = self.recipient_entry.get().strip()
        note = self.note_entry.get().strip()
        ok, msg, data = self.app.wallet.transfer(
            self.app.current_user_id(), recipient, amount, note)
        if ok:
            self.status.configure(text=msg, fg=S.SUCCESS)
            self.app.show_screen("DashboardScreen")
        else:
            self.status.configure(text=msg, fg=S.DANGER)