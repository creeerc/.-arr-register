"""Login screen."""

import tkinter as tk

from .. import styles as S
from ..base import (BaseScreen, action_button, card, entry, label,
                   status_badge)


class LoginScreen(BaseScreen):
    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, app, **kwargs)
        self._build()

    def _build(self):
        self.header("Login", show_back=True)

        c = card(self, padx=24, pady=24)
        c.pack(fill="x", padx=24, pady=30)

        label(c, "Email", font=S.FONT_SMALL, fg=S.TEXT_MUTED).pack(
            anchor="w", pady=(0, 4))
        self.email_entry = entry(c, width=36)
        self.email_entry.pack(fill="x", pady=(0, 14))
        self.email_entry.insert(0, "user@example.com")

        label(c, "Password", font=S.FONT_SMALL, fg=S.TEXT_MUTED).pack(
            anchor="w", pady=(0, 4))
        self.pass_entry = entry(c, width=36, show="•")
        self.pass_entry.pack(fill="x", pady=(0, 8))
        self.pass_entry.insert(0, "password123")

        self.status = status_badge(c, "", "info")
        self.status.pack(fill="x", pady=(0, 10))

        action_button(c, "Login", command=self._login, width=36).pack(
            fill="x", pady=(4, 10))

        link = tk.Label(c, text="Don't have an account? Sign up",
                        bg=S.BG_CARD, fg=S.ACCENT, font=S.FONT_SMALL,
                        cursor="hand2")
        link.pack()
        link.bind("<Button-1>", lambda e: self.app.show_screen("SignupScreen"))

    def _login(self):
        email = self.email_entry.get().strip()
        password = self.pass_entry.get()
        ok, msg, user = self.app.wallet.login(email, password)
        if ok:
            self.app.set_user(user)
            self.app.show_screen("DashboardScreen")
        else:
            self.status.configure(text=msg, fg=S.DANGER)