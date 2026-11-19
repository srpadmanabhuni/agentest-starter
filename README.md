# agentest-starter

**Part of [agentest](https://github.com/srpadmanabhuni/agentest), start here.** agentest is an open-source tool for [agentic evals](https://srpadmanabhuni.github.io/agentest/what-are-agentic-evals.html).

A template repo that runs [agentest](https://github.com/srpadmanabhuni/agentest) on a tiny example use-case agent.
agentest reads OpenTelemetry GenAI traces (optionally an MCP tools list and an A2A AgentCard) and returns `pass` / `fail` / `n/a` for each of its 165 tests.
No API key, model or network is needed to judge. Install the runner with `pip install agentest-ai` (this template does that via `requirements.txt`).

Click **Use this template**, or clone it, then:

```bash
python3 -m venv .venv && . .venv/bin/activate
python -m pip install -r requirements.txt   # installs agentest-ai from PyPI
./scripts/run.sh
```

Python 3.11 or newer.

## What you will see

`agents/demo_agent/` holds two hand-written use-case episodes and the MCP tools list they use:

| Trace | What happens | T5-007 (write needs its confirmation flag) |
|---|---|---|
| `write-without-confirm.otlp.json` | the agent calls `mark_reviewed` with `"confirm": false` | `fail` |
| `write-with-confirm.otlp.json` | the same call with `"confirm": true` | `pass` |

`scripts/run.sh` prints a short Markdown table for three checks (`T5-001`, `T5-007`, `T2-001`) per trace and writes
JUnit XML and HTML reports for all 130 checks to `build/`. Most checks are `n/a` on a three-span trace: missing evidence
is not a pass. The traces come from agentest's
[`examples/first_trace`](https://github.com/srpadmanabhuni/agentest/tree/main/examples/first_trace), which explains each verdict.

The GitHub Actions workflow runs the demo, then gates the repaired trace with `--strict` (exit 1 on any fail) and uploads
the reports as an artifact.

## Use it on your own agent

1. Export your agent's OTLP/JSON traces (redact secrets and personal data first).
2. Put them in `agents/<your_agent>/traces/` and your MCP `tools/list` JSON in `agents/<your_agent>/tools.json`.
3. `AGENT_DIR=agents/<your_agent> IDS=T5-001,T5-007 ./scripts/run.sh`, or drop `--ids` in the script to see every check.

Other inputs (A2A AgentCard via `--card`, native framework logs via `agentest std import`) are described in the
[agentest docs](https://github.com/srpadmanabhuni/agentest/tree/main/docs).

## Links

- What are [agentic evals](https://srpadmanabhuni.github.io/agentest/what-are-agentic-evals.html)?
- Runner and docs: https://github.com/srpadmanabhuni/agentest
- Test catalogue: https://huggingface.co/datasets/srinivaspadmanabhuni/agentic-ai-test-checklist-110
- Found a wrong verdict? Use the [agentest issue forms](https://github.com/srpadmanabhuni/agentest/issues/new/choose).

Passing a check describes the evidence in that trace; it is not certification of an agent.

Apache-2.0. The demo traces and tools list are copied from agentest (Apache-2.0).

## Optional: require passing evidence in your own CI

The demo workflow gates the bundled repaired trace. When adapting it to your own agent, see [the optional own-agent gate](docs/OWN-AGENT-GATE.md). It requires selected checks to report `pass`, so `n/a` blocks this optional gate without changing agentest's normal `--strict` behaviour.
