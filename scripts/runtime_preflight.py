#!/usr/bin/env python3
import argparse
import os
import sys
from datetime import datetime

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--target')
    parser.add_argument('--scenario')
    parser.add_argument('--mode')
    parser.add_argument('--workspace')
    parser.add_argument('--ensure-session', action='store_true')
    args = parser.parse_args()

    if not args.target or not args.workspace:
        print("blocked: missing target or workspace", file=sys.stderr)
        sys.exit(1)
    ws_norm = args.workspace.replace('\\', '/')
    if 'testing/' not in ws_norm:
        print("blocked: workspace must be under testing/", file=sys.stderr)
        sys.exit(1)
    os.makedirs(args.workspace, exist_ok=True)
    notes_dir = os.path.join(args.workspace, 'notes')
    os.makedirs(notes_dir, exist_ok=True)
    bootstrap = os.path.join(notes_dir, 'bootstrap.md')
    with open(bootstrap, 'w') as f:
        f.write(f"# Bootstrap\n\nTarget: {args.target}\nScenario: {args.scenario}\nMode: {args.mode}\nTime: {datetime.utcnow().isoformat()}Z\n")
    print(f"bootstrap_created:{bootstrap}")
    sys.exit(0)

if __name__ == '__main__':
    main()
