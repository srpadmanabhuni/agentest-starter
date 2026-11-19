"""Offline smoke tests using the starter's use-case recorded traces.

Run after installing requirements.txt: python -m unittest discover -s tests -v
No pytest or extra dependency required. No agent or tool is executed.
"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / 'agents' / 'demo_agent'


class OwnAgentGateTests(unittest.TestCase):
    def run_gate(self, traces, ids='T5-001,T5-007', tools=None, card=None):
        with tempfile.TemporaryDirectory() as directory:
            command = [sys.executable, str(ROOT / 'scripts' / 'gate.py'),
                       '--tools', str(tools or DEMO / 'tools.json'),
                       '--ids', ids, '--out', directory]
            for trace in traces:
                command += ['--trace', str(DEMO / 'traces' / trace)]
            if card:
                command += ['--card', str(card)]
            result = subprocess.run(command, text=True, capture_output=True)
            reports = [json.loads(path.read_text()) for path in Path(directory).glob('*.json')]
            return result, reports

    def test_repaired_trace_passes(self):
        result, reports = self.run_gate(['write-with-confirm.otlp.json'])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(reports), 1)

    def test_unconfirmed_write_blocks(self):
        result, _ = self.run_gate(['write-without-confirm.otlp.json'])
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn('T5-007: fail', result.stdout)

    def test_no_evidence_blocks(self):
        result, _ = self.run_gate(['write-with-confirm.otlp.json'], ids='T2-001')
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn('T2-001: n/a', result.stdout)

    def test_missing_trace_is_error(self):
        result, _ = self.run_gate(['not-present.json'])
        self.assertEqual(result.returncode, 2)

    def test_missing_tools_is_error(self):
        result, _ = self.run_gate(['write-with-confirm.otlp.json'], tools=ROOT / 'not-present.json')
        self.assertEqual(result.returncode, 2)

    def test_missing_card_is_error(self):
        result, _ = self.run_gate(['write-with-confirm.otlp.json'], card=ROOT / 'not-present.json')
        self.assertEqual(result.returncode, 2)

    def test_unknown_id_is_error(self):
        result, _ = self.run_gate(['write-with-confirm.otlp.json'], ids='DOES-NOT-EXIST')
        self.assertEqual(result.returncode, 2)

    def test_empty_ids_is_error(self):
        result, _ = self.run_gate(['write-with-confirm.otlp.json'], ids=',')
        self.assertEqual(result.returncode, 2)

    def test_all_supplied_traces_are_checked(self):
        result, reports = self.run_gate(['write-with-confirm.otlp.json', 'write-without-confirm.otlp.json'])
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertEqual(len(reports), 2)


if __name__ == '__main__':
    unittest.main()
