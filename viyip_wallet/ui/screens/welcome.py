"""Welcome / landing screen."""

import tkinter as tk

from ... import styles as S
from .base import BaseScreen, action_button, label, card


class WelcomeScreen(BaseScreen):
    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, app, **kwargs)
        self._build()

    def _build(self):
        # Logo area
        top = tk.Frame(self, bg=S.BG)
        top.pack(fill="x", padx=30, pady=60)

        logo = tk.Label(top, text="V", bg=S.ACCENT, fg=S.TEXT,
                        font=("Segoe UI", 40, "bold"), width=3, height=1,
                        relief="flat")
        logo.pack(pady=(0, 18))

        label(top, "Viyip Wallet", font=S.FONT_TITLE, fg=S.TEXT).pack()
        label(top, "Your digital wallet powered by Viyip payment system",
              font=S.FONT_BODY, fg=S.TEXT_MUTED).pack(pady=(6, 0))

        # Features card
        c = card(self, padx=24, pady=24)
        c.pack(fill="x", padx=24, pady=20)

        features = [
            ("Send Money", "Transfer to any Viyip consumer instantly"),
            ("Merchant Payments", "Pay merchants via Viyip payment system"),
            ("Add Money", "Top up from card, UPI, netbanking"),
            ("Transaction History", "Track every payment and transfer"),
        ]
        for title, desc in features:
            row = tk.Frame(c, bg=S.BG_CARD)
            row.pack(fill="x", pady=6)
            tk.Label(row, text="•", bg=S.BG_CARD, fg=S.ACCENT,
                     font=S.FONT_BODY).pack(side="left", padx=(0, 8))
            col = tk.Frame(row, bg=S.BG_CARD)
            col.pack(side="left", fill="x", expand=True)
            label(col, title, font=S.FONT_HEADING, fg=S.TEXT).pack(anchor="w")
            label(col, desc, font=S.FONT_SMALL, fg=S.TEXT_MUTED).pack(anchor="w")

        # Actions
        action_button(self, "Login", command=self.app.show_screen("LoginScreen"),
                      width=24).pack(pady=(10, 8), padx=24, fill="x")
        action_button(self, "Create Account",
                      command=self.app.show_screen("SignupScreen"),
                      bg=S.BG_CARD_2, fg=S.TEXT, width=24).pack(
            pady=(0, 30), padx=24, fill="x")