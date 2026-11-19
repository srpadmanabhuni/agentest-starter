#!/usr/bin/env python3
"""Require selected checks to PASS on every supplied trace, not merely avoid FAIL.

Offline judging only. No agent or tool is executed. The installed agentest CLI
reads recorded trace files. This gate is not an approval or certification system.
Exit 0: required evidence passed; 1: unmet gate; 2: invalid inputs/runner error.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--trace', action='append', required=True, type=Path,
                        help='Recorded OTLP JSON/JSONL file; repeat for each trace')
    parser.add_argument('--tools', required=True, type=Path)
    parser.add_argument('--card', type=Path)
    parser.add_argument('--ids', required=True, help='Exact required IDs, comma-separated; no class prefixes')
    parser.add_argument('--out', type=Path, default=Path('build/own-agent-gate'))
    args = parser.parse_args()
    ids = list(dict.fromkeys(x.strip() for x in args.ids.split(',') if x.strip()))
    if not ids:
        parser.error('--ids must name at least one exact check ID')
    traces = list(dict.fromkeys(p.resolve() for p in args.trace))
    for p in [*traces, args.tools, *([args.card] if args.card else [])]:
        if not p.is_file() or p.stat().st_size == 0:
            print(f'ERROR: missing or empty input: {p}', file=sys.stderr)
            return 2
    args.out.mkdir(parents=True, exist_ok=True)
    unmet = False
    for index, trace in enumerate(traces, 1):
        report = (args.out / f'{index:03d}.json').resolve()
        # Remove stale evidence before invoking the runner.
        report.unlink(missing_ok=True)
        command = [sys.executable, '-c',
                   'from agentest.cli import main; raise SystemExit(main())',
                   'std', 'run',
                   '--otlp', str(trace), '--tools', str(args.tools),
                   '--ids', ','.join(ids), '--json', str(report)]
        if args.card:
            command += ['--card', str(args.card)]
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            print(f'ERROR: agentest could not judge {trace.name}', file=sys.stderr)
            print(result.stderr or result.stdout, file=sys.stderr)
            return 2
        try:
            data = json.loads(report.read_text(encoding='utf-8'))
            if not isinstance(data, dict) or not data:
                raise ValueError('empty or unexpected report')
            for agent, cells in data.items():
                if not isinstance(cells, dict):
                    raise ValueError('unexpected agent result')
                for check_id in ids:
                    cell = cells.get(check_id)
                    status = cell.get('status') if isinstance(cell, dict) else None
                    if status != 'pass':
                        unmet = True
                        print(f'BLOCK: trace {index} / {agent} / {check_id}: {status or "missing"}')
                    else:
                        print(f'PASS: trace {index} / {agent} / {check_id}')
        except (OSError, ValueError, TypeError) as error:
            print(f'ERROR: unreadable report: {error}', file=sys.stderr)
            return 2
    print(f'Reports: {args.out}')
    return 1 if unmet else 0


if __name__ == '__main__':
    raise SystemExit(main())
