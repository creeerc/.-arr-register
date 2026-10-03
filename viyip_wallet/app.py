"""Main application window and screen navigation."""

import tkinter as tk

from . import config
from .ui import styles as S
from .wallet_service import WalletService
from .database import Database
from .viyip_gateway import ViyipGateway


class ViyipWalletApp(tk.Tk):
    """Root Tkinter window hosting all screens."""

    def __init__(self):
        super().__init__()
        self.title(f"{config.APP_NAME} - Digital Wallet")
        self.geometry("430x780")
        self.resizable(False, False)
        self.configure(bg=S.BG)

        # Backend
        self.db = Database()
        self.gateway = ViyipGateway()
        self.wallet = WalletService(self.db, self.gateway)
        self.current_user = None

        # Container for screens
        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.screens = {}
        self._register_screens()
        self.show_screen("WelcomeScreen")

    # ------------------------------------------------------------------
    # Screen management
    # ------------------------------------------------------------------
    def _register_screens(self):
        from .ui.screens.welcome import WelcomeScreen
        from .ui.screens.login import LoginScreen
        from .ui.screens.signup import SignupScreen
        from .ui.screens.dashboard import DashboardScreen
        from .ui.screens.transfer import TransferScreen
        from .ui.screens.add_money import AddMoneyScreen
        from .ui.screens.payment import PaymentScreen
        from .ui.screens.history import HistoryScreen

        self.screens = {
            "WelcomeScreen": WelcomeScreen,
            "LoginScreen": LoginScreen,
            "SignupScreen": SignupScreen,
            "DashboardScreen": DashboardScreen,
            "TransferScreen": TransferScreen,
            "AddMoneyScreen": AddMoneyScreen,
            "PaymentScreen": PaymentScreen,
            "HistoryScreen": HistoryScreen,
        }

    def show_screen(self, name: str, **kwargs):
        for widget in self.container.winfo_children():
            widget.destroy()
        screen_cls = self.screens[name]
        screen = screen_cls(self.container, self, **kwargs)
        screen.grid(row=0, column=0, sticky="nsew")
        self.current_screen = screen
        return screen

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def set_user(self, user: dict):
        self.current_user = user

    def current_user_id(self) -> int:
        return self.current_user["id"] if self.current_user else None

    def logout(self):
        self.current_user = None
        self.show_screen("WelcomeScreen")


def run():
    app = ViyipWalletApp()
    app.mainloop()