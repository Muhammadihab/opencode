#!/usr/bin/env python3
import json
import os
import sqlite3
from datetime import datetime, timezone

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'memory', 'learning.db')
SIGNALS_PATH = os.path.join(os.path.dirname(__file__), 'signals.json')

class LearningEngine:
    def __init__(self, db_path=None):
        self.db_path = db_path or DB_PATH
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()
        self._load_signals()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS findings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            target TEXT,
            endpoint TEXT,
            vulnerability_class TEXT,
            signals TEXT,
            validation_state TEXT,
            source_provenance TEXT,
            created_at TEXT
        )''')
        cur.execute('''CREATE TABLE IF NOT EXISTS triage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            finding_id INTEGER,
            feedback_type TEXT,
            notes TEXT,
            provenance TEXT,
            created_at TEXT
        )''')
        conn.commit()
        conn.close()

    def _load_signals(self):
        if os.path.exists(SIGNALS_PATH):
            with open(SIGNALS_PATH) as f:
                self.signals = json.load(f)
        else:
            self.signals = {"weights": {"auth": 0.9, "idor": 0.8, "ssrf": 0.9, "xss": 0.7}, "thresholds": {"p1": 0.8}}

    def before_recon(self, target, techs=None):
        techs = techs or []
        return {"target": target, "techs": techs, "recommendations": ["scope_lock", "js_analysis"], "ok": True}

    def during_testing(self, signals=None, context=None):
        """Score discovered signals. `signals` = {signal_name: value(0-1)}.
        `context` = optional list/dict of escalation flags (cross_tenant,
        admin_bypass, auth_bypass, payment_impact, state_changing,
        sensitive_data, chainable) that multiply the score up. Score is
        bounded 0-1. Priority: P1 >= p1 threshold, P2 >= p2, else P3."""
        signals = signals or {}
        weights = self.signals.get("weights", {})
        escal = self.signals.get("escalation", {})
        thresholds = self.signals.get("thresholds", {})

        score = 0.0
        for k, v in signals.items():
            if k in weights and isinstance(v, (int, float)):
                score += min(1.0, v) * weights[k]

        # apply escalation multipliers from context flags
        flags = []
        if isinstance(context, dict):
            flags = [k for k, v in context.items() if v]
        elif isinstance(context, (list, tuple, set)):
            flags = list(context)
        for f in flags:
            if f in escal:
                score *= escal[f]

        score = min(1.0, round(score, 3))
        p1 = thresholds.get("p1", 0.8)
        p2 = thresholds.get("p2", 0.5)
        priority = "P1" if score >= p1 else "P2" if score >= p2 else "P3"
        return {"score": score, "priority": priority, "escalated_by": flags, "ok": True}

    def after_finding(self, target, endpoint, vulnerability_class, signals=None, validation_state="LEAD", source_provenance=None):
        signals = signals or {}
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("INSERT INTO findings (target, endpoint, vulnerability_class, signals, validation_state, source_provenance, created_at) VALUES (?,?,?,?,?,?,?)",
                    (target, endpoint, vulnerability_class, json.dumps(signals), validation_state, source_provenance or "", datetime.now(timezone.utc).isoformat()))
        fid = cur.lastrowid
        conn.commit()
        conn.close()
        return {"finding_id": fid, "stored": True, "ok": True}

    def before_summary(self, findings=None):
        findings = findings or []
        scored = sorted(findings, key=lambda x: x.get('score', 0), reverse=True)
        return {"ranked": scored, "ok": True}

    def after_triage(self, finding_id, feedback_type, notes="", provenance=None):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("INSERT INTO triage (finding_id, feedback_type, notes, provenance, created_at) VALUES (?,?,?,?,?)",
                    (finding_id, feedback_type, notes, provenance or "", datetime.now(timezone.utc).isoformat()))
        tid = cur.lastrowid
        conn.commit()
        conn.close()
        return {"triage_id": tid, "ingested": True, "ok": True}

    def retrieve(self, vulnerability_class=None, limit=10):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        if vulnerability_class:
            cur.execute("SELECT * FROM findings WHERE vulnerability_class=? ORDER BY id DESC LIMIT ?", (vulnerability_class, limit))
        else:
            cur.execute("SELECT * FROM findings ORDER BY id DESC LIMIT ?", (limit,))
        rows = cur.fetchall()
        conn.close()
        return rows
