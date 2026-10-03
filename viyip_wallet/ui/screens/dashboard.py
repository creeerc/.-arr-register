"""Dashboard screen with balance, quick actions, and history."""

import tkinter as tk

from ... import styles as S
from .base import (BaseScreen, action_button, card, divider, label,
                   status_badge)


class DashboardScreen(BaseScreen):
    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, app, **kwargs)
        self._build()

    def _build(self):
        # Top bar
        top = tk.Frame(self, bg=S.BG_CARD, height=56)
        top.pack(fill="x")
        top.pack_propagate(False)

        user = self.app.current_user
        name = user["name"] if user else "Guest"
        label(top, f"Hello, {name}", font=S.FONT_HEADING, fg=S.TEXT).pack(
            side="left", padx=16, pady=14)
        viyip_id = user["viyip_id"] if user else ""
        label(top, viyip_id, font=S.FONT_SMALL, fg=S.TEXT_MUTED).pack(
            side="left", padx=(0, 16), pady=14)

        logout_btn = tk.Button(top, text="Logout", bg="transparent",
                               fg=S.TEXT_MUTED, activeforeground=S.DANGER,
                               font=S.FONT_SMALL, bd=0, cursor="hand2",
                               command=self.app.logout)
        logout_btn.pack(side="right", padx=16, pady=14)

        hist_btn = tk.Button(top, text="History", bg=S.BG_CARD_2, fg=S.ACCENT,
                             activebackground=S.ACCENT, activeforeground=S.TEXT,
                             font=S.FONT_SMALL, bd=0, cursor="hand2",
                             command=lambda: self.app.show_screen("HistoryScreen"))
        hist_btn.pack(side="right", padx=(0, 8), pady=10)

        # Balance card
        balance_card = card(self, padx=24, pady=24)
        balance_card.pack(fill="x", padx=24, pady=16)
        label(balance_card, "Total Balance", font=S.FONT_SMALL,
              fg=S.TEXT_MUTED).pack(pady=(0, 4))
        self.balance_label = label(balance_card, "₹0.00", font=("Segoe UI", 30,
                                                                "bold"),
                                   fg=S.TEXT)
        self.balance_label.pack(pady=(0, 14))

        # Quick actions
        actions = tk.Frame(balance_card, bg=S.BG_CARD)
        actions.pack(fill="x")
        actions.grid_columnconfigure((0, 1, 2), weight=1)

        self._action(actions, "Send", S.ACCENT,
                     lambda: self.app.show_screen("TransferScreen")).grid(
            row=0, column=0, sticky="ew", padx=4)
        self._action(actions, "Add", S.SUCCESS,
                     lambda: self.app.show_screen("AddMoneyScreen")).grid(
            row=0, column=1, sticky="ew", padx=4)
        self._action(actions, "Pay", S.WARN,
                     lambda: self.app.show_screen("PaymentScreen")).grid(
            row=0, column=2, sticky="ew", padx=4)

        # History header
        hist_header = tk.Frame(self, bg=S.BG)
        hist_header.pack(fill="x", padx=24, pady=(16, 8))
        label(hist_header, "Recent Transactions", font=S.FONT_HEADING,
              fg=S.TEXT).pack(side="left")
        self._history_container = tk.Frame(self, bg=S.BG)
        self._history_container.pack(fill="both", expand=True, padx=24,
                                     pady=(0, 16))

        self.refresh()

    def _action(self, parent, text, color, command):
        b = tk.Button(parent, text=text, bg=S.BG_CARD_2, fg=color,
                      activebackground=color, activeforeground=S.TEXT,
                      font=S.FONT_HEADING, bd=0, cursor="hand2",
                      height=2, command=command,
                      highlightbackground=S.BORDER, highlightthickness=1)
        return b

    def refresh(self):
        user = self.app.current_user
        if not user:
            return
        balance = self.app.wallet.get_balance(user["id"])
        self.balance_label.configure(text=f"₹{balance:,.2f}")

        # Clear history
        for w in self._history_container.winfo_children():
            w.destroy()

        txs = self.app.wallet.get_history(user["id"], limit=5)
        if not txs:
            label(self._history_container, "No transactions yet",
                  font=S.FONT_BODY, fg=S.TEXT_MUTED).pack(pady=12)
            return

        for tx in txs:
            self._tx_row(tx)

    def _tx_row(self, tx):
        row = card(self._history_container, padx=16, pady=6)
        row.pack(fill="x", pady=4)

        # Left: type + counterparty
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
        counterparty = tx.get("counterparty") or ""
        note = tx.get("note") or ""
        sub = counterparty or note
        label(left, sub, font=S.FONT_SMALL, fg=S.TEXT_MUTED).pack(anchor="w")

        # Right: amount + status
        right = tk.Frame(row, bg=S.BG_CARD)
        right.pack(side="right", padx=12, pady=10)
        sign = "-" if tx["type"] in ("transfer_out", "payment") else "+"
        color = S.DANGER if sign == "-" else S.SUCCESS
        amt = tx.get("amount", 0)
        label(right, f"{sign}₹{amt:,.2f}", font=S.FONT_BODY, fg=color).pack(
            anchor="e")
        label(right, tx.get("status", ""), font=S.FONT_SMALL,
              fg=S.TEXT_MUTED).pack(anchor="e")