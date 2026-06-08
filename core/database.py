"""
SQLite database layer — no external ORM required.
All DB access goes through Database.get() singleton.
"""

import sqlite3
import os
import json
from datetime import datetime


_DB_PATH = None


def _resolve_db_path():
    global _DB_PATH
    if _DB_PATH:
        return _DB_PATH
    try:
        from android.storage import app_storage_path  # type: ignore
        base = app_storage_path()
    except ImportError:
        base = os.path.expanduser('~')
    _DB_PATH = os.path.join(base, 'expense_tracker.db')
    return _DB_PATH


class Database:
    _instance = None

    @classmethod
    def get(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self._conn = sqlite3.connect(_resolve_db_path(), check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute('PRAGMA journal_mode=WAL')
        self._create_tables()
        self._seed_defaults()

    def _create_tables(self):
        self._conn.executescript("""
            CREATE TABLE IF NOT EXISTS transactions (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                date        TEXT    NOT NULL,
                amount      REAL    NOT NULL,
                currency    TEXT    NOT NULL DEFAULT 'SAR',
                merchant    TEXT    DEFAULT '',
                category    TEXT    DEFAULT 'other',
                bank_id     TEXT    DEFAULT '',
                raw_sms     TEXT    DEFAULT '',
                sms_address TEXT    DEFAULT '',
                type        TEXT    NOT NULL DEFAULT 'debit',
                is_verified INTEGER NOT NULL DEFAULT 0,
                created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS budgets (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                category      TEXT    NOT NULL UNIQUE,
                monthly_limit REAL    NOT NULL DEFAULT 0,
                updated_at    TEXT    NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS settings (
                key   TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS sms_log (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                sms_id      TEXT    NOT NULL UNIQUE,
                processed   INTEGER NOT NULL DEFAULT 0,
                processed_at TEXT
            );

            CREATE INDEX IF NOT EXISTS idx_tx_date     ON transactions(date);
            CREATE INDEX IF NOT EXISTS idx_tx_category ON transactions(category);
            CREATE INDEX IF NOT EXISTS idx_tx_type     ON transactions(type);
        """)
        self._conn.commit()

    def _seed_defaults(self):
        defaults = {
            'language': 'ar',
            'currency': 'SAR',
            'theme': 'dark',
            'last_sync': '',
            'onboarded': '0',
        }
        for k, v in defaults.items():
            self._conn.execute(
                'INSERT OR IGNORE INTO settings(key, value) VALUES (?, ?)', (k, v)
            )
        self._conn.commit()

    # ── Transactions ──────────────────────────────────────────────────────────────

    def insert_transaction(self, tx: dict) -> int:
        cur = self._conn.execute(
            """INSERT INTO transactions
               (date, amount, currency, merchant, category, bank_id, raw_sms, sms_address, type)
               VALUES (:date, :amount, :currency, :merchant, :category,
                       :bank_id, :raw_sms, :sms_address, :type)""",
            tx
        )
        self._conn.commit()
        return cur.lastrowid

    def update_transaction(self, tx_id: int, fields: dict):
        sets = ', '.join(f'{k}=:{k}' for k in fields)
        fields['id'] = tx_id
        self._conn.execute(f'UPDATE transactions SET {sets} WHERE id=:id', fields)
        self._conn.commit()

    def delete_transaction(self, tx_id: int):
        self._conn.execute('DELETE FROM transactions WHERE id=?', (tx_id,))
        self._conn.commit()

    def get_transactions(self, month: str = None, category: str = None,
                         tx_type: str = None, limit: int = 200) -> list:
        query = 'SELECT * FROM transactions WHERE 1=1'
        params = []
        if month:
            query += " AND strftime('%Y-%m', date) = ?"
            params.append(month)
        if category:
            query += ' AND category = ?'
            params.append(category)
        if tx_type:
            query += ' AND type = ?'
            params.append(tx_type)
        query += ' ORDER BY date DESC LIMIT ?'
        params.append(limit)
        rows = self._conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]

    def get_monthly_summary(self, month: str) -> dict:
        row = self._conn.execute(
            """SELECT
                   SUM(CASE WHEN type='debit'  THEN amount ELSE 0 END) as total_debit,
                   SUM(CASE WHEN type='credit' THEN amount ELSE 0 END) as total_credit,
                   COUNT(*) as tx_count
               FROM transactions
               WHERE strftime('%Y-%m', date) = ?""",
            (month,)
        ).fetchone()
        return dict(row) if row else {'total_debit': 0, 'total_credit': 0, 'tx_count': 0}

    def get_category_breakdown(self, month: str) -> list:
        rows = self._conn.execute(
            """SELECT category, SUM(amount) as total
               FROM transactions
               WHERE type='debit' AND strftime('%Y-%m', date) = ?
               GROUP BY category
               ORDER BY total DESC""",
            (month,)
        ).fetchall()
        return [dict(r) for r in rows]

    def get_daily_spending(self, month: str) -> list:
        rows = self._conn.execute(
            """SELECT strftime('%d', date) as day, SUM(amount) as total
               FROM transactions
               WHERE type='debit' AND strftime('%Y-%m', date) = ?
               GROUP BY day ORDER BY day""",
            (month,)
        ).fetchall()
        return [dict(r) for r in rows]

    # ── Budgets ─────────────────────────────────────────────────────────────────

    def set_budget(self, category: str, limit: float):
        self._conn.execute(
            """INSERT INTO budgets(category, monthly_limit, updated_at)
               VALUES(?, ?, datetime('now'))
               ON CONFLICT(category) DO UPDATE SET monthly_limit=excluded.monthly_limit,
               updated_at=excluded.updated_at""",
            (category, limit)
        )
        self._conn.commit()

    def get_budgets(self) -> list:
        rows = self._conn.execute('SELECT * FROM budgets').fetchall()
        return [dict(r) for r in rows]

    def get_budget(self, category: str) -> float:
        row = self._conn.execute(
            'SELECT monthly_limit FROM budgets WHERE category=?', (category,)
        ).fetchone()
        return row['monthly_limit'] if row else 0.0

    # ── Settings ───────────────────────────────────────────────────────────────

    def get_setting(self, key: str, default: str = '') -> str:
        row = self._conn.execute(
            'SELECT value FROM settings WHERE key=?', (key,)
        ).fetchone()
        return row['value'] if row else default

    def set_setting(self, key: str, value: str):
        self._conn.execute(
            'INSERT INTO settings(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value',
            (key, value)
        )
        self._conn.commit()

    # ── SMS log ────────────────────────────────────────────────────────────────

    def is_sms_processed(self, sms_id: str) -> bool:
        row = self._conn.execute(
            'SELECT processed FROM sms_log WHERE sms_id=?', (sms_id,)
        ).fetchone()
        return bool(row and row['processed'])

    def mark_sms_processed(self, sms_id: str):
        self._conn.execute(
            """INSERT INTO sms_log(sms_id, processed, processed_at)
               VALUES(?, 1, datetime('now'))
               ON CONFLICT(sms_id) DO UPDATE SET processed=1,
               processed_at=excluded.processed_at""",
            (sms_id,)
        )
        self._conn.commit()

    def close(self):
        self._conn.close()
        Database._instance = None
