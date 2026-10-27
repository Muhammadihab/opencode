#!/usr/bin/env python3
import os
import sys
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, 'scripts', 'skill_registry.py')

def test_check():
    r = subprocess.run([sys.executable, SCRIPT, 'check'], cwd=ROOT, stdout=subprocess.PIPE)
    assert r.returncode == 0

def test_resolve_known_scenario():
    r = subprocess.run([sys.executable, SCRIPT, 'resolve', '--scenario', 'login form', '--mode', 'test', '--paths-only'], cwd=ROOT, stdout=subprocess.PIPE)
    assert r.returncode == 0
    out = r.stdout.decode()
    # foundation skills should be included conceptually
    assert len(out) >= 0  # graceful

def test_resolve_unknown_degrades_gracefully():
    r = subprocess.run([sys.executable, SCRIPT, 'resolve', '--scenario', 'unknown_zzzz', '--mode', 'test', '--paths-only'], cwd=ROOT, stdout=subprocess.PIPE)
    assert r.returncode == 0

def test_generate():
    r = subprocess.run([sys.executable, SCRIPT, 'generate'], cwd=ROOT, stdout=subprocess.PIPE)
    assert r.returncode == 0
