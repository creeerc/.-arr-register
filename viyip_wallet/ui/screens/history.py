"""Transaction history screen."""

import tkinter as tk

from ... import styles as S
from .base import (BaseScreen, action_button, card, divider, label,
                   status_badge)


class HistoryScreen(BaseScreen):
    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, app, **kwargs)
        self._build()

    def _build(self):
        self.header("Transaction History", show_back=True)

        # Pricing summary card
        summary = card(self, padx=24, pady=16)
        summary.pack(fill="x", padx=24, pady=16)
        label(summary, "Viyip Fee Summary", font=S.FONT_HEADING,
              fg=S.TEXT).pack(anchor="w", pady=(0, 8))

        self.total_fees_label = label(summary, "Total Viyip fees: ₹0.00",
                                       font=S.FONT_BODY, fg=S.TEXT)
        self.total_fees_label.pack(anchor="w")
        self.tx_count_label = label(summary, "Transactions: 0",
                                     font=S.FONT_SMALL, fg=S.TEXT_MUTED)
        self.tx_count_label.pack(anchor="w", pady=(4, 0))

        self.container = tk.Frame(self, bg=S.BG)
        self.container.pack(fill="both", expand=True, padx=24, pady=(0, 16))

        self.refresh()

    def refresh(self):
        user = self.app.current_user
        if not user:
            return
        txs = self.app.wallet.get_history(user["id"], limit=100)

        total_fees = sum(t.get("fee", 0) for t in txs)
        self.total_fees_label.configure(text=f"Total Viyip fees: ₹{total_fees:,.2f}")
        self.tx_count_label.configure(text=f"Transactions: {len(txs)}")

        for w in self.container.winfo_children():
            w.destroy()

        if not txs:
            label(self.container, "No transactions yet", font=S.FONT_BODY,
                  fg=S.TEXT_MUTED).pack(pady=20)
            return

        for tx in txs:
            self._tx_row(tx)

    def _tx_row(self, tx):
        row = card(self.container, padx=16, pady=6)
        row.pack(fill="x", pady=4)

        left = tk.Frame(row, bg=S.BG_CARD)
        left.pack(side="left", fill="x", expand=True, padx=12, pady=10)
        type_map = {
            "transfer_out": "Sent money",
            "transfer_in": "Received money",
            "add_money": "Added money",
            "payment": "Payment",
        }
        title = type_map.get(tx["type"], tx["type"])
        label(left, title, font=S.FONT_BODY, fg=S.TEXT).pack(anchor="w")
        sub = tx.get("counterparty") or tx.get("note") or ""
        label(left, sub, font=S.FONT_SMALL, fg=S.TEXT_MUTED).pack(anchor="w")
        label(left, tx.get("method", ""), font=S.FONT_SMALL,
              fg=S.TEXT_MUTED).pack(anchor="w")

        right = tk.Frame(row, bg=S.BG_CARD)
        right.pack(side="right", padx=12, pady=10)
        sign = "-" if tx["type"] in ("transfer_out", "payment") else "+"
        color = S.DANGER if sign == "-" else S.SUCCESS
        amt = tx.get("amount", 0)
        label(right, f"{sign}₹{amt:,.2f}", font=S.FONT_BODY, fg=color).pack(
            anchor="e")
        fee = tx.get("fee", 0)
        if fee:
            label(right, f"Fee ₹{fee:,.2f}", font=S.FONT_SMALL,
                  fg=S.TEXT_MUTED).pack(anchor="e")
        label(right, tx.get("status", ""), font=S.FONT_SMALL,
              fg=S.TEXT_MUTED).pack(anchor="e")