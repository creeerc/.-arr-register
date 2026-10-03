"""Headless smoke test for the Viyip wallet service layer.

Runs without a display to verify core logic: signup, login, add money,
transfer, payment, fees, and history.
"""

import os
import sys

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from viyip_wallet import config
from viyip_wallet.database import Database
from viyip_wallet.viyip_gateway import ViyipGateway
from viyip_wallet.wallet_service import WalletService


def main():
    # Use a temp DB so tests are repeatable
    db_path = os.path.join(config.DATA_DIR, "test_wallet.db")
    if os.path.exists(db_path):
        os.remove(db_path)
    db = Database(db_path=db_path)
    gw = ViyipGateway()
    ws = WalletService(db, gw)

    failures = []

    def check(cond, msg):
        status = "PASS" if cond else "FAIL"
        print(f"[{status}] {msg}")
        if not cond:
            failures.append(msg)

    # --- Signup ---
    ok, msg, alice = ws.signup("Alice Smith", "alice@example.com", "secret123")
    check(ok, f"Signup Alice: {msg}")
    check(alice is not None, "User object returned")
    check(alice["viyip_id"].startswith("viyip_"), f"Viyip id generated: {alice['viyip_id']}")
    check(alice["balance"] == 0.0, "Initial balance 0")

    # Duplicate email
    ok2, msg2, _ = ws.signup("Alice2", "alice@example.com", "secret123")
    check(not ok2, "Duplicate email rejected")

    # Weak password
    ok3, msg3, _ = ws.signup("Bob", "bob@example.com", "123")
    check(not ok3, "Weak password rejected")

    # --- Login ---
    ok, msg, user = ws.login("alice@example.com", "secret123")
    check(ok, f"Login Alice: {msg}")
    ok, msg, _ = ws.login("alice@example.com", "wrongpass")
    check(not ok, "Wrong password rejected")

    # --- Add money ---
    ok, msg, data = ws.add_money(alice["id"], 500, "card", "test@upi")
    check(ok, f"Add money: {msg}")
    check(data["net"] == 495.0, f"Net credited after 1% fee: {data['net']}")
    check(data["fee"] == 5.0, f"Fee 1% of 500 = 5: {data['fee']}")
    check(ws.get_balance(alice["id"]) == 495.0, "Balance updated to 495")

    # --- Transfer ---
    ok, msg, bob = ws.signup("Bob Jones", "bob@example.com", "secret123")
    ok, msg, data = ws.transfer(alice["id"], bob["viyip_id"], 100, "Gift")
    check(ok, f"Transfer 100: {msg}")
    check(data["fee"] == 1.5, f"Transfer fee 1.5% of 100 = 1.5: {data['fee']}")
    check(data["debit"] == 101.5, f"Debit 100 + 1.5 fee = 101.5: {data['debit']}")
    check(ws.get_balance(alice["id"]) == 393.5, f"Sender balance 393.5: {ws.get_balance(alice['id'])}")
    check(ws.get_balance(bob["id"]) == 100.0, f"Recipient balance 100: {ws.get_balance(bob['id'])}")

    # Insufficient balance
    ok, msg, _ = ws.transfer(alice["id"], bob["viyip_id"], 10000)
    check(not ok, "Insufficient balance rejected")

    # --- Payment ---
    ok, msg, data = ws.make_payment(alice["id"], "Amazon", 200, "viyip")
    check(ok, f"Payment 200: {msg}")
    check(data["fee"] == 4.0, f"Payment fee 2% of 200 = 4: {data['fee']}")
    check(ws.get_balance(alice["id"]) == 193.5, f"Balance after payment (200 debited): {ws.get_balance(alice['id'])}")

    # --- History ---
    txs = ws.get_history(alice["id"])
    check(len(txs) == 3, f"3 transactions for Alice: {len(txs)}")
    types = {t["type"] for t in txs}
    check({"add_money", "transfer_out", "payment"} <= types, "Expected tx types present")

    # --- Fee estimates ---
    check(ws.get_fee_estimate(1000, "transfer") == 15.0, "Fee estimate transfer")
    check(ws.get_fee_estimate(1000, "payment") == 20.0, "Fee estimate payment")

    # --- Cleanup ---
    os.remove(db_path)

    print("\n" + ("ALL TESTS PASSED" if not failures else f"{len(failures)} FAILURES"))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())