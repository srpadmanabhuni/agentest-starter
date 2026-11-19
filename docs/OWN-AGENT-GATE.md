# Require passing evidence from your own agent

## Why this exists

The current starter demonstrates agentest well. Its workflow gates the repaired bundled sample, while the documented `AGENT_DIR` option changes the local reporting script only. A developer adapting the template must also change the workflow to gate their own traces.

Separately, agentest's `--strict` intentionally exits 1 on `fail`, not on `n/a`. Missing evidence is not a pass, but it is not an automatic CI failure either. The optional script in this pack is for teams who explicitly want particular checks to have passing evidence. It does not change agentest or the meaning of `n/a`.

## Files

- `scripts/gate.py`: optional require-pass helper.
- `docs/own-agent-ci.yml.example`: inactive workflow example.
- `tests/test_own_agent_gate.py`: offline tests, no extra dependency.

## Try the helper on the existing starter

From a clone of https://github.com/srpadmanabhuni/agentest-starter with its requirements installed, use the included `scripts/gate.py`. Run with the same virtual environment that has agentest installed:

```bash
python scripts/gate.py \
  --trace agents/demo_agent/traces/write-with-confirm.otlp.json \
  --tools agents/demo_agent/tools.json --ids T5-001,T5-007
```

Expected exit 0. Change the trace to `write-without-confirm.otlp.json`: expected exit 1. With the repaired trace, change `--ids` to `T2-001`: expected exit 1 because that trace has no prerequisite declaration. This last result is the deliberate difference from ordinary `--strict`.

The sample's confirmation flag is not proof of human consent. These are hand-written teaching traces. No agent or tool runs during judging.

## Then use your own recorded evidence

1. Replace the trace and tools paths. Add `--card path/to/agent-card.json` if a selected rule needs declarations from the card.
2. Choose exact check IDs that apply to your workflow and that your instrumentation supports. Do not copy the sample IDs as a universal safety policy.
3. Repeat `--trace path/to/another.otlp.json` for each recorded file that must pass. The helper does not collect fresh traces, test a running agent, or establish that the files cover production behaviour.
4. Keep intentionally bad teaching traces out of an all-pass production gate; test those separately as expected failures.
5. Inspect `build/own-agent-gate/001.json` and later numbered reports when a check blocks. Treat traces and reports as private unless you have reviewed/redacted them. The workflow example does not upload artifacts.

Return codes: 0 = all selected checks passed; 1 = selected evidence did not meet the gate; 2 = invalid input or runner/report error. JSON output uses agentest's legacy `--json` mapping; future changes to that output require re-testing this helper. The helper does not use `shell=True` or interpret file names as commands.

## Test this helper

```bash
python -m unittest discover -s tests -v
```

The tests read only the starter's use-case example traces. No model or API key is needed. The example workflow remains inactive in `docs/`. Review paths and exact IDs before placing it in `.github/workflows/`.
