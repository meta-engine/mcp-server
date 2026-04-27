#!/usr/bin/env bash
# MetaEngine MCP benchmark — orchestrator.
# Runs N iterations of {a-mcp, b-baseline} on the same spec and aggregates.
#
# Env vars:
#   RUNS=N         number of full runs per variant (default 3)
#   SPEC=path      spec JSON to generate from
#   LANGUAGE=lang  target language (default: typescript). Selects prompts/$LANGUAGE/.
#                  Supported (with prompts/<lang>/ present): typescript, java, python
#   ARM=name       a-mcp invocation pattern (default: inline). Selects
#                  prompts/$LANGUAGE/agent-a-mcp-gen-${ARM}.md.
#                  Defined arms: inline | script | heredoc (TypeScript only for now)
#   PARALLEL=N     run up to N runs concurrently (default 1 = sequential).
#                  PARALLEL=2 verified safe; PARALLEL=5 attempted to compress
#                  wall-clock at the cost of cross-session cache warming.
#                  Caveat: parallel runs share a cold cache start. Comparison
#                  within a run stays apples-to-apples; absolute numbers may
#                  differ from sequential runs and are recorded as such.
set -euo pipefail

ROOT=$(cd "$(dirname "$0")" && pwd)
RUNS=${RUNS:-3}
PARALLEL=${PARALLEL:-1}
LANGUAGE=${LANGUAGE:-typescript}
ARM=${ARM:-inline}
MODEL=${MODEL:-}
SHAPE=${SHAPE:-ddd}
# Shape suffix: empty for ddd (backward-compatible existing folder names);
# "-monolith" etc. for non-default shapes.
if [ "$SHAPE" = "ddd" ]; then
  SHAPE_SUFFIX=""
  DEFAULT_SPEC="$ROOT/spec/large.json"
else
  SHAPE_SUFFIX="-$SHAPE"
  DEFAULT_SPEC="$ROOT/spec/${SHAPE}.json"
fi
SPEC=${SPEC:-"$DEFAULT_SPEC"}
export LANGUAGE ARM MODEL SHAPE SHAPE_SUFFIX  # propagate to run-agent.sh / judge.sh subshells
MODEL_SUFFIX="${MODEL:+-$MODEL}"
RESULTS_DIR="$ROOT/results/$(date +%Y%m%d-%H%M%S)-${LANGUAGE}-${ARM}${MODEL_SUFFIX}${SHAPE_SUFFIX}"

if [ ! -d "$ROOT/prompts/$LANGUAGE" ]; then
  echo "ERROR: prompts/$LANGUAGE/ does not exist. Available: $(ls $ROOT/prompts | tr '\n' ' ')" >&2
  exit 1
fi
GEN_PROMPT="$ROOT/prompts/$LANGUAGE/agent-a-mcp-gen-${ARM}${SHAPE_SUFFIX}.md"
if [ ! -f "$GEN_PROMPT" ]; then
  echo "ERROR: $GEN_PROMPT does not exist." >&2
  echo "       Available arm/shape combos for $LANGUAGE: $(ls $ROOT/prompts/$LANGUAGE | sed -n 's/^agent-a-mcp-gen-\(.*\)\.md$/\1/p' | tr '\n' ' ')" >&2
  exit 1
fi
BASELINE_PROMPT="$ROOT/prompts/$LANGUAGE/agent-b-baseline${SHAPE_SUFFIX}.md"
if [ ! -f "$BASELINE_PROMPT" ]; then
  echo "ERROR: $BASELINE_PROMPT does not exist (need a baseline prompt for shape='$SHAPE')." >&2
  exit 1
fi

if ! command -v claude >/dev/null 2>&1; then
  echo "ERROR: claude CLI not in PATH" >&2; exit 1
fi
if ! command -v npx >/dev/null 2>&1; then
  echo "ERROR: npx not in PATH (needed by tools/judge.py for tsc)" >&2; exit 1
fi

if [ ! -f "$SPEC" ]; then
  echo "Spec not found at $SPEC — generating..."
  if [ "$SHAPE" = "ddd" ]; then
    python3 "$ROOT/spec/generate-spec.py" "$SPEC"
  else
    python3 "$ROOT/spec/generate-spec-${SHAPE}.py" "$SPEC"
  fi
fi

mkdir -p "$RESULTS_DIR"
SCRIPT_START=$(date +%s)

MODEL_DISPLAY="${MODEL:-default (claude CLI configured)}"
cat <<EOF
MetaEngine MCP benchmark
  Language: $LANGUAGE
  Shape:    $SHAPE
  Arm:      $ARM (a-mcp gen prompt)
  Model:    $MODEL_DISPLAY
  Spec:     $SPEC
  Runs:     $RUNS per variant
  Parallel: up to $PARALLEL concurrent
  Results:  $RESULTS_DIR

EOF

# Run a single iteration: a-mcp then baseline, plus judging for each.
run_one() {
  local i="$1"
  local run_dir
  run_dir=$(printf "%s/run-%03d" "$RESULTS_DIR" "$i")
  for variant in a-mcp b-baseline; do
    local vdir="$run_dir/$variant"
    mkdir -p "$vdir"
    echo "[run $i / $variant] generating..."
    "$ROOT/tools/run-agent.sh" "$variant" "$vdir" "$SPEC" \
      || echo "[run $i / $variant] claude exited non-zero — recorded, continuing"
    echo "[run $i / $variant] judging..."
    "$ROOT/tools/judge.sh" "$vdir" "$SPEC" || true
  done
}

# Chunk into batches of PARALLEL — each batch starts together and we wait for
# all to finish before launching the next. Bash 3.2 compatible (no `wait -n`).
i=1
while [ "$i" -le "$RUNS" ]; do
  batch_end=$((i + PARALLEL - 1))
  if [ "$batch_end" -gt "$RUNS" ]; then
    batch_end="$RUNS"
  fi
  if [ "$PARALLEL" -le 1 ]; then
    run_one "$i"
  else
    for j in $(seq "$i" "$batch_end"); do
      run_one "$j" &
    done
    wait
  fi
  i=$((batch_end + 1))
done

SCRIPT_END=$(date +%s)
WALL_SECONDS=$((SCRIPT_END - SCRIPT_START))
echo "$WALL_SECONDS" > "$RESULTS_DIR/wall_seconds.txt"

echo
echo "Aggregating..."
python3 "$ROOT/tools/aggregate.py" "$RESULTS_DIR" > "$RESULTS_DIR/summary.md"
echo
cat "$RESULTS_DIR/summary.md"
echo
echo "Full results:    $RESULTS_DIR"
echo "Total wall-clock: ${WALL_SECONDS}s"
