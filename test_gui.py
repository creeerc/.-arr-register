"""Headless GUI smoke test using Xvfb.

Exercises the real Tkinter UI code paths (not just the service layer):
- welcome -> signup -> login -> dashboard -> transfer -> add money -> payment -> history
- verifies balance labels, transaction rows, fee previews update
"""

import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Start Xvfb
xvfb = subprocess.Popen(
    ["Xvfb", ":99", "-screen", "0", "430x780x24"],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
)
os.environ["DISPLAY"] = ":99"
time.sleep(1.0)

try:
    import tkinter as tk
    from viyip_wallet.app import ViyipWalletApp
    from viyip_wallet import config

    failures = []

    def check(cond, msg):
        print(f"[{'PASS' if cond else 'FAIL'}] {msg}")
        if not cond:
            failures.append(msg)

    # Use a fresh DB so the GUI test is repeatable across runs.
    config.DB_PATH = os.path.join(config.DATA_DIR, "test_gui_wallet.db")
    if os.path.exists(config.DB_PATH):
        os.remove(config.DB_PATH)

    app = ViyipWalletApp()
    app.update()

    # --- Welcome screen ---
    check(app.current_screen.__class__.__name__ == "WelcomeScreen",
          "Starts on WelcomeScreen")

    # --- Signup ---
    app.show_screen("SignupScreen")
    app.update()
    scr = app.current_screen
    scr.name_entry.delete(0, "end"); scr.name_entry.insert(0, "Alice Smith")
    scr.email_entry.delete(0, "end"); scr.email_entry.insert(0, "alice@example.com")
    scr.pass_entry.delete(0, "end"); scr.pass_entry.insert(0, "secret123")
    scr._signup()
    app.update()
    check(app.current_user is not None, "Signup sets current_user")
    check(app.current_user["balance"] == 0.0, "Initial balance 0")
    check(app.current_screen.__class__.__name__ == "DashboardScreen",
          "Signup navigates to Dashboard")

    # --- Dashboard balance ---
    app.update()
    bal_text = app.current_screen.balance_label.cget("text")
    check(bal_text == "₹0.00", f"Dashboard shows ₹0.00, got {bal_text}")

    # --- Add money ---
    app.show_screen("AddMoneyScreen")
    app.update()
    scr = app.current_screen
    scr.amount_entry.delete(0, "end"); scr.amount_entry.insert(0, "500")
    scr._preview()
    app.update()
    check("₹5.00" in scr.fee_label.cget("text"),
          f"Add money fee preview ₹5.00: {scr.fee_label.cget('text')}")
    check("₹495.00" in scr.net_label.cget("text"),
          f"Add money net preview ₹495.00: {scr.net_label.cget('text')}")
    scr._add()
    app.update()
    check(app.current_screen.__class__.__name__ == "DashboardScreen",
          "Add money returns to dashboard")
    app.update()
    check(app.current_screen.balance_label.cget("text") == "₹495.00",
          f"Dashboard balance ₹495.00: {app.current_screen.balance_label.cget('text')}")

    # --- Transfer ---
    # Need a recipient: signup Bob first via service directly
    from viyip_wallet.viyip_gateway import ViyipGateway
    bob_ok, _, bob = app.wallet.signup("Bob Jones", "bob@example.com", "secret123")

    app.show_screen("TransferScreen")
    app.update()
    scr = app.current_screen
    scr.recipient_entry.delete(0, "end")
    scr.recipient_entry.insert(0, bob["viyip_id"])
    scr.amount_entry.delete(0, "end"); scr.amount_entry.insert(0, "100")
    scr._preview()
    app.update()
    check("₹1.50" in scr.fee_label.cget("text"),
          f"Transfer fee preview ₹1.50: {scr.fee_label.cget('text')}")
    check("₹101.50" in scr.total_label.cget("text"),
          f"Transfer total preview ₹101.50: {scr.total_label.cget('text')}")
    scr._transfer()
    app.update()
    check(app.current_screen.__class__.__name__ == "DashboardScreen",
          "Transfer returns to dashboard")
    app.update()
    check(app.current_screen.balance_label.cget("text") == "₹393.50",
          f"Dashboard balance ₹393.50: {app.current_screen.balance_label.cget('text')}")

    # --- Payment ---
    app.show_screen("PaymentScreen")
    app.update()
    scr = app.current_screen
    scr.amount_entry.delete(0, "end"); scr.amount_entry.insert(0, "200")
    scr._preview()
    app.update()
    check("₹4.00" in scr.fee_label.cget("text"),
          f"Payment fee preview ₹4.00: {scr.fee_label.cget('text')}")
    scr._pay()
    app.update()
    check(app.current_screen.__class__.__name__ == "DashboardScreen",
          "Payment returns to dashboard")
    app.update()
    check(app.current_screen.balance_label.cget("text") == "₹193.50",
          f"Dashboard balance ₹193.50: {app.current_screen.balance_label.cget('text')}")

    # --- History ---
    app.show_screen("HistoryScreen")
    app.update()
    scr = app.current_screen
    check("₹10.50" in scr.total_fees_label.cget("text"),
          f"History total fees ₹10.50 (5+1.5+4): {scr.total_fees_label.cget('text')}")
    check(scr.tx_count_label.cget("text") == "Transactions: 3",
          f"History tx count 3: {scr.tx_count_label.cget('text')}")

    # --- Logout ---
    app.logout()
    app.update()
    check(app.current_user is None, "Logout clears current_user")
    check(app.current_screen.__class__.__name__ == "WelcomeScreen",
          "Logout returns to WelcomeScreen")

    print("\n" + ("ALL GUI TESTS PASSED" if not failures else f"{len(failures)} FAILURES"))
    sys.exit(1 if failures else 0)
finally:
    if 'app' in dir() and app is not None:
        try:
            app.quit()
        except Exception:
            pass
    try:
        if os.path.exists(config.DB_PATH):
            os.remove(config.DB_PATH)
    except Exception:
        pass
    xvfb.terminate()
    try:
        xvfb.wait(timeout=5)
    except Exception:
        pass