#!/usr/bin/env bash
# Wrapper around tools/judge.py — keeps the existing judge.sh interface
# while delegating actual structural verification to Python.
#
# Args:
#   <variant_dir>  e.g. results/<ts>/run-001/a-mcp
#   <spec_path>    optional; defaults to $SPEC env or the harness default
set -uo pipefail

vdir="$1"

ROOT=$(cd "$(dirname "$0")/.." && pwd)
spec="${2:-${SPEC:-$ROOT/spec/large.json}}"

python3 "$ROOT/tools/judge.py" "$vdir" --spec "$spec" > "$vdir/judge.json"

# Echo a concise summary line for run.sh's stdout.
python3 - <<PY
import json
d = json.load(open("$vdir/judge.json"))
sc = d.get("structural_counts", {})
print(f"  -> verdict={d['verdict']} files={d['ts_file_count']}/{d['expected_total']} "
      f"tsc={d['tsc_errors']} struct(pass={sc.get('pass',0)} "
      f"fail={sc.get('structural_fail',0)} missing={sc.get('missing',0)})")
PY
