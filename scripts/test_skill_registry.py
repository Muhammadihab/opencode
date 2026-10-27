#!/usr/bin/env python3
"""Tests for the skill registry resolver. Real behavioural assertions."""
import os
import sys
import json
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, 'scripts', 'skill_registry.py')


def _run(*args):
    return subprocess.run([sys.executable, SCRIPT, *args], cwd=ROOT,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def test_check_ok_and_registry_populated():
    r = _run('check')
    assert r.returncode == 0
    data = json.loads(r.stdout.decode())
    assert data['ok'] is True
    assert data['skills'] > 0, "registry.json must not be empty"
    assert data['agents'] == 5, "five collection agents must be registered"


def test_all_registered_skill_files_exist():
    r = _run('check')
    data = json.loads(r.stdout.decode())
    assert data['missing_files'] == 0, f"missing skill files: {data['missing']}"


def test_foundations_always_first():
    r = _run('resolve', '--scenario', 'anything at all', '--mode', 'test', '--paths-only')
    assert r.returncode == 0
    lines = [l for l in r.stdout.decode().splitlines() if l.strip()]
    assert lines[0].endswith('master-bugbounty-rules.md')
    assert 'learning-engine-integration' in lines[1]


def test_resolve_login_returns_auth_skills():
    r = _run('resolve', '--scenario', 'login form with password reset',
             '--mode', 'test', '--paths-only')
    out = r.stdout.decode()
    assert 'auth-bypass.md' in out
    assert 'forgot-password.md' in out


def test_resolve_idor_tenant_returns_authz_skills():
    r = _run('resolve', '--scenario', 'idor on user_id across tenant',
             '--mode', 'test', '--paths-only')
    out = r.stdout.decode()
    assert 'idor.md' in out
    assert 'business-context-analysis.md' in out


def test_resolve_ssrf_returns_ssrf():
    r = _run('resolve', '--scenario', 'url fetcher webhook import',
             '--mode', 'test', '--paths-only')
    assert 'ssrf.md' in r.stdout.decode()


def test_resolve_unknown_returns_only_foundations():
    r = _run('resolve', '--scenario', 'zzz_nonsense_qqq', '--mode', 'test', '--paths-only')
    assert r.returncode == 0
    lines = [l for l in r.stdout.decode().splitlines() if l.strip()]
    # unknown surface degrades gracefully to foundations only
    assert len(lines) == 2


def test_paths_only_resolve_to_existing_files():
    r = _run('resolve', '--scenario', 'graphql api xss sqli upload',
             '--mode', 'test', '--paths-only')
    for p in [l for l in r.stdout.decode().splitlines() if l.strip()]:
        assert os.path.exists(os.path.join(ROOT, p)), f"path does not exist: {p}"


def test_agent_skills_includes_foundations():
    r = _run('agent-skills', '--agent', 'recon-agent', '--paths-only')
    out = r.stdout.decode()
    assert 'master-bugbounty-rules.md' in out
    assert 'recon-workflow.md' in out


def test_generate_is_idempotent():
    r1 = _run('generate')
    assert r1.returncode == 0
    before = open(os.path.join(ROOT, 'runtime', 'registry.json')).read()
    r2 = _run('generate')
    after = open(os.path.join(ROOT, 'runtime', 'registry.json')).read()
    assert before == after, "generate must be idempotent"
