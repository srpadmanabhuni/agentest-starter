#!/usr/bin/env bash
# Run agentest on the demo agent. Offline: no network, model or API key is needed to judge.
set -euo pipefail
cd "$(dirname "$0")/.."
AGENT_DIR="${AGENT_DIR:-agents/demo_agent}"
IDS="${IDS:-T5-001,T5-007,T2-001}"
mkdir -p build
for trace in "$AGENT_DIR"/traces/*.otlp.json*; do
  name="$(basename "$trace")"; name="${name%%.otlp.json*}"
  echo "== $name"
  agentest std run --otlp "$trace" --tools "$AGENT_DIR/tools.json" --ids "$IDS" --format md
  agentest std run --otlp "$trace" --tools "$AGENT_DIR/tools.json" --format junit --out "build/$name.junit.xml" >/dev/null
  agentest std run --otlp "$trace" --tools "$AGENT_DIR/tools.json" --format html --out "build/$name.html" >/dev/null
done
echo "Reports written to build/ (JUnit XML and HTML, all 130 checks)."
