#!/usr/bin/env python3
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)

from learning_engine.engine import LearningEngine

def test_hooks_shapes():
    db = os.path.join(tempfile.gettempdir(), 'test_learn.db')
    eng = LearningEngine(db_path=db)
    r1 = eng.before_recon('example.com', ['nginx'])
    assert isinstance(r1, dict) and 'ok' in r1
    r2 = eng.during_testing({'auth': 1.0})
    assert isinstance(r2, dict) and 0 <= r2['score'] <= 1
    r3 = eng.after_finding('example.com', '/login', 'auth', {'auth': 1.0}, 'LEAD', 'test')
    assert isinstance(r3, dict) and r3['stored'] == True
    r4 = eng.before_summary([{'score': 0.9}])
    assert isinstance(r4, dict)
    r5 = eng.after_triage(r3['finding_id'], 'accepted', 'ok')
    assert isinstance(r5, dict) and r5['ingested'] == True
    rows = eng.retrieve()
    assert len(rows) >= 1
