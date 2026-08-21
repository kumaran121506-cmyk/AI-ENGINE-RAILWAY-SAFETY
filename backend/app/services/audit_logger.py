"""
Audit Logger Service: SQLite database manager for compliance logging and incident auditing.
"""

import sqlite3
import json
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from app.config import DB_PATH

class AuditLogger:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS audit_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    train_id TEXT NOT NULL,
                    risk_level TEXT NOT NULL,
                    details TEXT NOT NULL,
                    raw_payload TEXT
                )
            """)
            conn.commit()

    def log_event(
        self,
        event_type: str,
        train_id: str,
        risk_level: str,
        details: str,
        payload: Optional[Dict[str, Any]] = None
    ) -> int:
        timestamp_str = datetime.now(timezone.utc).isoformat()
        raw_payload_str = json.dumps(payload) if payload else None

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO audit_logs (timestamp, event_type, train_id, risk_level, details, raw_payload)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (timestamp_str, event_type, train_id, risk_level, details, raw_payload_str))
            conn.commit()
            return cursor.lastrowid

    def get_logs(self, limit: int = 50, train_id: Optional[str] = None, risk_level: Optional[str] = None) -> List[Dict[str, Any]]:
        query = "SELECT id, timestamp, event_type, train_id, risk_level, details, raw_payload FROM audit_logs WHERE 1=1"
        params = []

        if train_id:
            query += " AND train_id = ?"
            params.append(train_id)
        if risk_level:
            query += " AND risk_level = ?"
            params.append(risk_level)

        query += " ORDER BY id DESC LIMIT ?"
        params.append(limit)

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            results = []
            for r in rows:
                results.append({
                    "id": r[0],
                    "timestamp": r[1],
                    "event_type": r[2],
                    "train_id": r[3],
                    "risk_level": r[4],
                    "details": r[5],
                    "raw_payload": json.loads(r[6]) if r[6] else None
                })
            return results
