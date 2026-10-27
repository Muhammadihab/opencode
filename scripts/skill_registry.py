#!/usr/bin/env python3
"""Skill registry resolver — the real one.

Reads runtime/registry.json (the single source of truth) and resolves a
described surface/scenario to the skills that should load, by matching the
scenario text against each skill's triggers. Foundations always load first.

CLI (unchanged contract, consumed across the project):
  skill_registry.py check
  skill_registry.py generate
  skill_registry.py resolve --scenario "<text>" --mode <mode> [--paths-only]
  skill_registry.py agent-skills --agent <agent-id> [--paths-only]   (new)

resolve prints, one per line:
  - with --paths-only: the skill file path (skills/<name>.md or the registered path)
  - without:           "<name>\t<path>\t<category>"
Foundations come first, then matched skills ordered by load_order then name.
"""
import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGISTRY = os.path.join(ROOT, "runtime", "registry.json")


def load_registry():
    try:
        with open(REGISTRY) as f:
            return json.load(f)
    except FileNotFoundError:
        return {"skills": {}, "agents": {}}
    except json.JSONDecodeError as e:
        print(f"error: registry.json is not valid JSON: {e}", file=sys.stderr)
        return {"skills": {}, "agents": {}}


def _exists(path):
    return os.path.exists(os.path.join(ROOT, path))


def _match(scenario, triggers):
    """A skill matches if any of its triggers is a substring of the scenario.
    '*always*' matches unconditionally (foundations)."""
    s = (scenario or "").lower()
    for t in triggers:
        if t == "*always*":
            return True
        if t.strip().lower() in s:
            return True
    return False


def resolve(scenario="", mode="test", paths_only=False, include_missing=True):
    """Return list of (name, path, category). Foundations first, then matches."""
    reg = load_registry()
    skills = reg.get("skills", {})

    foundation = []
    matched = []
    for name, meta in skills.items():
        triggers = meta.get("triggers", [])
        modes = meta.get("modes", [])
        if modes and mode and mode not in modes:
            continue
        if meta.get("foundation") or "*always*" in triggers:
            foundation.append((name, meta))
        elif _match(scenario, triggers):
            matched.append((name, meta))

    foundation.sort(key=lambda kv: (kv[1].get("load_order", 0), kv[0]))
    matched.sort(key=lambda kv: (kv[1].get("load_order", 10), kv[0]))

    out = []
    seen = set()
    for name, meta in foundation + matched:
        if name in seen:
            continue
        seen.add(name)
        path = meta.get("path", f"skills/{name}.md")
        if not include_missing and not _exists(path):
            continue
        out.append((name, path, meta.get("category", "")))
    return out


def agent_skills(agent_id, paths_only=False):
    reg = load_registry()
    agents = reg.get("agents", {})
    skills = reg.get("skills", {})
    a = agents.get(agent_id)
    if not a:
        return []
    out = []
    # foundations first for every agent
    for name, meta in skills.items():
        if meta.get("foundation"):
            out.append((name, meta.get("path", f"skills/{name}.md")))
    for name in a.get("skills", []):
        meta = skills.get(name, {})
        out.append((name, meta.get("path", f"skills/{name}.md")))
    return out


def check():
    reg = load_registry()
    skills = reg.get("skills", {})
    missing = [m.get("path") for m in skills.values() if not _exists(m.get("path", ""))]
    return {
        "ok": True,
        "skills": len(skills),
        "agents": len(reg.get("agents", {})),
        "missing_files": len(missing),
        "missing": missing[:20],
    }


def generate():
    """Regenerate registry.json from the generator if present (idempotent)."""
    gen = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gen_registry.py")
    if os.path.exists(gen):
        import subprocess
        subprocess.run([sys.executable, "-I", gen, REGISTRY], check=True)
        return {"generated": True, "path": REGISTRY}
    return {"generated": False, "reason": "gen_registry.py not found"}


def main():
    parser = argparse.ArgumentParser(description="Skill registry resolver")
    sub = parser.add_subparsers(dest="cmd")
    sub.add_parser("check")
    sub.add_parser("generate")
    p_res = sub.add_parser("resolve")
    p_res.add_argument("--scenario", default="")
    p_res.add_argument("--mode", default="test")
    p_res.add_argument("--paths-only", action="store_true")
    p_res.add_argument("--existing-only", action="store_true",
                       help="only emit skills whose files exist on disk")
    p_ag = sub.add_parser("agent-skills")
    p_ag.add_argument("--agent", required=True)
    p_ag.add_argument("--paths-only", action="store_true")

    args = parser.parse_args()
    if args.cmd == "check":
        print(json.dumps(check()))
    elif args.cmd == "generate":
        print(json.dumps(generate()))
    elif args.cmd == "resolve":
        rows = resolve(args.scenario, args.mode, args.paths_only,
                       include_missing=not args.existing_only)
        for name, path, cat in rows:
            print(path if args.paths_only else f"{name}\t{path}\t{cat}")
    elif args.cmd == "agent-skills":
        for name, path in agent_skills(args.agent, args.paths_only):
            print(path if args.paths_only else f"{name}\t{path}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
