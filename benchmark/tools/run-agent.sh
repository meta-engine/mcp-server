#!/usr/bin/env bash
# Invoke claude -p for one variant. For a-mcp this runs TWO sessions
# (warmup → gen) so each phase has its own authoritative result event.
# For b-baseline this runs ONE session.
#
# Args: <variant: a-mcp | b-baseline> <run_dir> <spec_path>
set -uo pipefail

variant="$1"
run_dir="$2"
spec_path="$3"

ROOT=$(cd "$(dirname "$0")/.." && pwd)
out_dir="$run_dir/output"
mkdir -p "$out_dir"

common_flags=(
  --output-format stream-json
  --verbose
  --dangerously-skip-permissions
)
if [ -n "${MODEL:-}" ]; then
  common_flags+=(--model "$MODEL")
fi


run_baseline() {
  local prompt
  local prompt_path="$ROOT/prompts/${LANGUAGE:-typescript}/agent-b-baseline${SHAPE_SUFFIX:-}.md"
  prompt=$(<"$prompt_path")
  prompt="${prompt//\{\{SPEC_PATH\}\}/$spec_path}"
  prompt="${prompt//\{\{OUT_DIR\}\}/$out_dir}"

  local empty_mcp="$run_dir/empty-mcp.json"
  printf '{"mcpServers":{}}' > "$empty_mcp"

  echo "  -> claude -p (variant=b-baseline, single session)"
  claude -p "$prompt" "${common_flags[@]}" \
    --max-turns 100 \
    --strict-mcp-config --mcp-config "$empty_mcp" \
    --allowed-tools "Write,Read,Bash" \
    > "$run_dir/stream.ndjson" 2> "$run_dir/stderr.log"
  local rc=$?

  python3 "$ROOT/tools/parse-stream.py" --start-phase generation \
    < "$run_dir/stream.ndjson" > "$run_dir/result.json" 2> "$run_dir/parse-err.log" || {
      python3 -c "import json, sys; json.dump({'error':'parse failed','exit_code':$rc}, sys.stdout)" \
        > "$run_dir/result.json"
    }
  return $rc
}


run_a_mcp_two_session() {
  local warmup_dir="$run_dir/warmup"
  local gen_dir="$run_dir/gen"
  local summary_file="$warmup_dir/summary.md"
  local arm="${ARM:-inline}"
  local tmp_file="$run_dir/metaengine-spec.json"
  mkdir -p "$warmup_dir" "$gen_dir"

  # ─── Session 1: WARMUP ───────────────────────────────────────────────
  local warmup_prompt
  warmup_prompt=$(<"$ROOT/prompts/${LANGUAGE:-typescript}/agent-a-mcp-warmup.md")
  warmup_prompt="${warmup_prompt//\{\{SUMMARY_FILE\}\}/$summary_file}"

  echo "  -> claude -p (variant=a-mcp, session=warmup)"
  claude -p "$warmup_prompt" "${common_flags[@]}" \
    --max-turns 30 \
    --allowed-tools "mcp__metaengine__metaengine_initialize,Read,Bash" \
    > "$warmup_dir/stream.ndjson" 2> "$warmup_dir/stderr.log"
  local warmup_rc=$?

  python3 "$ROOT/tools/parse-stream.py" --start-phase warmup \
    < "$warmup_dir/stream.ndjson" > "$warmup_dir/result.json" 2> "$warmup_dir/parse-err.log" || {
      python3 -c "import json, sys; json.dump({'error':'parse failed','exit_code':$warmup_rc}, sys.stdout)" \
        > "$warmup_dir/result.json"
    }

  # ─── Session 2: GENERATION ───────────────────────────────────────────
  local gen_prompt_path="$ROOT/prompts/${LANGUAGE:-typescript}/agent-a-mcp-gen-${arm}${SHAPE_SUFFIX:-}.md"
  if [ ! -f "$gen_prompt_path" ]; then
    echo "ERROR: gen prompt not found: $gen_prompt_path" >&2
    echo "       (ARM=${arm}, LANGUAGE=${LANGUAGE:-typescript})" >&2
    return 1
  fi
  local gen_template
  gen_template=$(<"$gen_prompt_path")
  gen_template="${gen_template//\{\{SPEC_PATH\}\}/$spec_path}"
  gen_template="${gen_template//\{\{OUT_DIR\}\}/$out_dir}"
  gen_template="${gen_template//\{\{TMP_FILE\}\}/$tmp_file}"

  local summary_content
  if [ -f "$summary_file" ]; then
    summary_content=$(<"$summary_file")
  else
    summary_content="(WARNING: warmup did not produce a summary file at $summary_file)"
    echo "  WARNING: warmup did not write summary file" >&2
  fi

  # Compose the gen prompt: knowledge brief, then the task.
  local gen_prompt="Knowledge brief from a prior warmup session:
============================================================
${summary_content}
============================================================

Now your task:

${gen_template}"

  echo "  -> claude -p (variant=a-mcp, session=gen, arm=${arm}, summary $(wc -c < "$summary_file" 2>/dev/null || echo 0)c)"
  # NOTE: metaengine_initialize is intentionally NOT in --allowed-tools, so the
  # gen session cannot re-read docs and must rely on the brief.
  claude -p "$gen_prompt" "${common_flags[@]}" \
    --max-turns 30 \
    --allowed-tools "mcp__metaengine__generate_code,mcp__metaengine__load_spec_from_file,Read,Bash" \
    > "$gen_dir/stream.ndjson" 2> "$gen_dir/stderr.log"
  local gen_rc=$?

  python3 "$ROOT/tools/parse-stream.py" --start-phase generation \
    < "$gen_dir/stream.ndjson" > "$gen_dir/result.json" 2> "$gen_dir/parse-err.log" || {
      python3 -c "import json, sys; json.dump({'error':'parse failed','exit_code':$gen_rc}, sys.stdout)" \
        > "$gen_dir/result.json"
    }

  # Return non-zero if either session errored.
  if [ $warmup_rc -ne 0 ] || [ $gen_rc -ne 0 ]; then
    return 1
  fi
  return 0
}


case "$variant" in
  a-mcp)      run_a_mcp_two_session ;;
  b-baseline) run_baseline ;;
  *) echo "Unknown variant: $variant" >&2; exit 2 ;;
esac
