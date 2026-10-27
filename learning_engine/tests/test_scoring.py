#!/usr/bin/env python3
"""Tests for signal scoring + escalation. Bounded, context-aware, tiered."""
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
from learning_engine.engine import LearningEngine


def _e():
    return LearningEngine(db_path=os.path.join(tempfile.gettempdir(), "test_score.db"))


def test_score_bounded_0_1():
    e = _e()
    r = e.during_testing({"rce": 1.0, "ssrf": 1.0, "auth": 1.0})
    assert 0.0 <= r["score"] <= 1.0


def test_tiers_order():
    e = _e()
    low = e.during_testing({"version_disclosure": 1.0})["score"]
    med = e.during_testing({"idor_parameter": 1.0})["score"]
    high = e.during_testing({"pii_in_response": 1.0})["score"]
    assert low < med < high


def test_priority_labels():
    e = _e()
    assert e.during_testing({"version_disclosure": 1.0})["priority"] == "P3"
    assert e.during_testing({"idor_parameter": 1.0})["priority"] == "P2"
    assert e.during_testing({"rce": 1.0})["priority"] == "P1"


def test_escalation_raises_score():
    e = _e()
    base = e.during_testing({"idor_parameter": 1.0})["score"]
    esc = e.during_testing({"idor_parameter": 1.0}, context=["cross_tenant"])
    assert esc["score"] > base
    assert "cross_tenant" in esc["escalated_by"]


def test_escalation_accepts_dict_context():
    e = _e()
    r = e.during_testing({"idor_parameter": 1.0}, context={"auth_bypass": True, "chainable": False})
    assert "auth_bypass" in r["escalated_by"]
    assert "chainable" not in r["escalated_by"]


def test_unknown_signal_ignored():
    e = _e()
    r = e.during_testing({"not_a_real_signal": 1.0})
    assert r["score"] == 0.0
