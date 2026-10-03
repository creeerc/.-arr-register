"""SQLite database layer for the Viyip wallet."""

import sqlite3
import threading
from contextlib import contextmanager
from datetime import datetime
from typing import List, Optional

from . import config


class Database:
    """Thread-safe SQLite wrapper."""

    def __init__(self, db_path: str = None):
        # Resolve lazily so config.DB_PATH can be overridden at runtime
        # (e.g. for tests or a user-selected data directory).
        self.db_path = db_path or config.DB_PATH
        self._lock = threading.Lock()
        self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._create_schema()

    @contextmanager
    def _cursor(self):
        with self._lock:
            cur = self._conn.cursor()
            try:
                yield cur
                self._conn.commit()
            except Exception:
                self._conn.rollback()
                raise

    def _create_schema(self):
        with self._cursor() as cur:
            cur.executescript(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    viyip_id TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    balance REAL NOT NULL DEFAULT 0.0,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tx_id TEXT UNIQUE NOT NULL,
                    user_id INTEGER NOT NULL,
                    type TEXT NOT NULL,
                    amount REAL NOT NULL,
                    fee REAL NOT NULL DEFAULT 0.0,
                    debit REAL NOT NULL DEFAULT 0.0,
                    balance_after REAL NOT NULL,
                    counterparty TEXT,
                    method TEXT,
                    status TEXT NOT NULL,
                    note TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                );

                CREATE INDEX IF NOT EXISTS idx_tx_user ON transactions(user_id);
                CREATE INDEX IF NOT EXISTS idx_tx_created ON transactions(created_at);
                """
            )

    # ------------------------------------------------------------------
    # Users
    # ------------------------------------------------------------------
    def create_user(self, viyip_id: str, name: str, email: str,
                    password_hash: str) -> Optional[int]:
        try:
            with self._cursor() as cur:
                cur.execute(
                    "INSERT INTO users (viyip_id, name, email, password_hash, "
                    "balance, created_at) VALUES (?, ?, ?, ?, 0, ?)",
                    (viyip_id, name, email, password_hash,
                     datetime.utcnow().isoformat()),
                )
                return cur.lastrowid
        except sqlite3.IntegrityError:
            return None

    def get_user_by_email(self, email: str) -> Optional[dict]:
        with self._cursor() as cur:
            cur.execute("SELECT * FROM users WHERE email = ?", (email,))
            row = cur.fetchone()
            return dict(row) if row else None

    def get_user_by_viyip_id(self, viyip_id: str) -> Optional[dict]:
        with self._cursor() as cur:
            cur.execute("SELECT * FROM users WHERE viyip_id = ?", (viyip_id,))
            row = cur.fetchone()
            return dict(row) if row else None

    def get_user_by_id(self, user_id: int) -> Optional[dict]:
        with self._cursor() as cur:
            cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            row = cur.fetchone()
            return dict(row) if row else None

    def update_balance(self, user_id: int, new_balance: float):
        with self._cursor() as cur:
            cur.execute("UPDATE users SET balance = ? WHERE id = ?",
                        (new_balance, user_id))

    # ------------------------------------------------------------------
    # Transactions
    # ------------------------------------------------------------------
    def add_transaction(self, tx_id: str, user_id: int, tx_type: str,
                        amount: float, fee: float, debit: float,
                        balance_after: float, counterparty: str = None,
                        method: str = None, status: str = "COMPLETED",
                        note: str = None) -> Optional[int]:
        try:
            with self._cursor() as cur:
                cur.execute(
                    "INSERT INTO transactions (tx_id, user_id, type, amount, "
                    "fee, debit, balance_after, counterparty, method, status, "
                    "note, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, "
                    "?, ?, ?)",
                    (tx_id, user_id, tx_type, amount, fee, debit,
                     balance_after, counterparty, method, status, note,
                     datetime.utcnow().isoformat()),
                )
                return cur.lastrowid
        except sqlite3.IntegrityError:
            return None

    def get_transactions(self, user_id: int, limit: int = 50) -> List[dict]:
        with self._cursor() as cur:
            cur.execute(
                "SELECT * FROM transactions WHERE user_id = ? "
                "ORDER BY created_at DESC, id DESC LIMIT ?",
                (user_id, limit),
            )
            return [dict(r) for r in cur.fetchall()]

    def get_balance(self, user_id: int) -> float:
        with self._cursor() as cur:
            cur.execute("SELECT balance FROM users WHERE id = ?", (user_id,))
            row = cur.fetchone()
            return float(row["balance"]) if row else 0.0