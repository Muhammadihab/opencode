#!/usr/bin/env python3
"""Tests for the FP signature gate. Uses an isolated temp DB (never the repo DB)."""
import os
import sys
import importlib.util
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("fp_check", os.path.join(ROOT, "scripts", "fp_check.py"))
fp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fp)


def test_hash_is_8_hex():
    h = fp.signature("200", "hello world")
    assert len(h) == 8
    int(h, 16)  # must be hex


def test_same_page_different_token_same_hash():
    a = "Access Denied by WAF. Request blocked. ID: 7f3a9c2e1b4d token=abc123"
    b = "Access Denied by WAF. Request blocked. ID: 11119999aaaa2222 token=zzz999def"
    assert fp.signature("403", a) == fp.signature("403", b)


def test_different_content_different_hash():
    a = "Access Denied by WAF."
    b = "Welcome admin, 42 secret records."
    assert fp.signature("200", a) != fp.signature("200", b)


def test_status_affects_hash():
    body = "same body text"
    assert fp.signature("200", body) != fp.signature("403", body)


def test_check_and_add_roundtrip(monkeypatch):
    with tempfile.TemporaryDirectory() as d:
        dbpath = os.path.join(d, "FALSE_POSITIVE_DB.md")
        monkeypatch.setattr(fp, "DB", dbpath)
        sig = fp.signature("403", "WAF block page")
        assert fp.cmd_check(sig) is False          # miss on empty DB
        assert fp.cmd_add(sig, "waf", "note") is True
        assert fp.cmd_check(sig) is True           # now matches
        assert fp.cmd_add(sig, "waf", "note") is False  # no duplicate
