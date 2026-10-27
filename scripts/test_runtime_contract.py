#!/usr/bin/env python3
import os
import sys
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, 'scripts', 'runtime_preflight.py')

def test_preflight_creates_bootstrap():
    ws = os.path.join(ROOT, 'testing', 'test.example.com')
    os.makedirs(ws, exist_ok=True)
    r = subprocess.run([sys.executable, SCRIPT, '--target', 'test.example.com', '--scenario', 'login form', '--mode', 'hunt', '--workspace', ws, '--ensure-session'], cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    assert r.returncode == 0
    assert os.path.exists(os.path.join(ws, 'notes', 'bootstrap.md'))

def test_preflight_blocks_invalid_scope():
    ws = os.path.join(ROOT, 'bad_workspace')
    r = subprocess.run([sys.executable, SCRIPT, '--target', 'test.example.com', '--scenario', 'login', '--mode', 'hunt', '--workspace', ws], cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    assert r.returncode != 0
    assert b'blocked' in r.stderr
