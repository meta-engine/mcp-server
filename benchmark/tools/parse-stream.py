#!/usr/bin/env python3
"""Parse `claude -p --output-format stream-json` output. Emit authoritative totals
plus a per-phase decomposition of what's directly measurable.

Important measurement note:
  Stream-json emits MULTIPLE `assistant` events per logical message (one per content
  block streamed). All events for the same `message.id` carry the SAME `usage` block,
  which is the message's *visible-text* output_tokens — it does NOT include the
  structured tool_use input bytes the model generates as tool arguments, nor the
  encrypted thinking-block tokens. The result event's `usage.output_tokens` is the
  authoritative aggregate (visible + tool_input + thinking).

  This parser:
    1. Deduplicates events by message.id and reads visible_output once per message.
    2. Sums tool_use input chars per message (these chars are billed as output tokens
       at roughly chars / TOOL_INPUT_CHARS_PER_TOKEN).
    3. Reports the result event's `usage` unmodified as the authoritative top-level.
    4. Computes a `thinking_residual_unmeasured_tokens` =
         result.output_tokens - sum(visible) - sum(tool_input_chars / ratio).
       This residual is per-RUN, not per-PHASE — we cannot precisely allocate it
       to warmup vs generation from stream data alone.

Usage:
  parse-stream.py --start-phase warmup     < stream.ndjson > result.json
  parse-stream.py --start-phase generation < stream.ndjson > result.json
"""
import json, sys, argparse

DEFAULT_MARKER = "===WARMUP_COMPLETE==="
DEFAULT_GEN_TOOL_PREFIX = "mcp__metaengine__generate"
TOOL_INPUT_CHARS_PER_TOKEN = 3.5  # rough estimate for structured JSON


def empty_phase():
    return {
        "messages": 0,
        "visible_output_tokens": 0,
        "tool_input_chars": 0,
        "tool_input_tokens_estimated": 0,
        "input_tokens": 0,
        "cache_creation_input_tokens": 0,
        "cache_read_input_tokens": 0,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--marker", default=DEFAULT_MARKER)
    ap.add_argument("--gen-tool-prefix", default=DEFAULT_GEN_TOOL_PREFIX)
    ap.add_argument("--start-phase", choices=["warmup", "generation"], default="warmup")
    args = ap.parse_args()

    # Group events by message id; collect content + final usage per message.
    messages = {}     # id -> dict
    msg_order = []    # preserve first-seen order
    result_event = None

    for line in sys.stdin:
        line = line.strip()
        if not line or not line.startswith("{"):
            continue
        try:
            ev = json.loads(line)
        except Exception:
            continue

        if ev.get("type") == "assistant":
            m = ev.get("message") or {}
            mid = m.get("id")
            if not mid:
                continue
            if mid not in messages:
                messages[mid] = {
                    "visible_output_tokens": 0,
                    "input_tokens": 0,
                    "cache_creation_input_tokens": 0,
                    "cache_read_input_tokens": 0,
                    "tool_input_chars": 0,
                    "has_marker_text": False,
                    "has_gen_tool": False,
                }
                msg_order.append(mid)
            # All events for one message report the same usage; overwrite each time.
            u = m.get("usage") or {}
            messages[mid]["visible_output_tokens"] = int(u.get("output_tokens", 0) or 0)
            messages[mid]["input_tokens"] = int(u.get("input_tokens", 0) or 0)
            messages[mid]["cache_creation_input_tokens"] = int(u.get("cache_creation_input_tokens", 0) or 0)
            messages[mid]["cache_read_input_tokens"] = int(u.get("cache_read_input_tokens", 0) or 0)
            # Accumulate content across the per-block events.
            for b in (m.get("content") or []):
                if not isinstance(b, dict):
                    continue
                bt = b.get("type")
                if bt == "text":
                    if args.marker in (b.get("text") or ""):
                        messages[mid]["has_marker_text"] = True
                elif bt == "tool_use":
                    inp_str = json.dumps(b.get("input") or {})
                    messages[mid]["tool_input_chars"] += len(inp_str)
                    if (b.get("name") or "").startswith(args.gen_tool_prefix):
                        messages[mid]["has_gen_tool"] = True
        elif ev.get("type") == "result":
            result_event = ev

    # Walk messages in order, assign phase based on boundary triggers.
    phase = args.start_phase
    boundary_seen = False
    boundary_trigger = None
    msgs_by_phase = {"warmup": [], "generation": []}
    for mid in msg_order:
        m = messages[mid]
        if not boundary_seen and (m["has_marker_text"] or m["has_gen_tool"]):
            boundary_seen = True
            boundary_trigger = "marker" if m["has_marker_text"] else "gen_tool"
            phase = "generation"  # boundary message is the first generation message
        msgs_by_phase[phase].append(mid)

    # No fold-back. If start_phase=warmup and boundary never crossed, all
    # messages legitimately stayed in warmup (e.g., warmup-only session).
    # The previous fold-back into generation conflated "agent didn't generate"
    # with "agent generated successfully" and inflated generation tokens.

    # Compute per-phase decomposition.
    def phase_decomposition(mids):
        d = empty_phase()
        d["messages"] = len(mids)
        for mid in mids:
            m = messages[mid]
            d["visible_output_tokens"] += m["visible_output_tokens"]
            d["tool_input_chars"] += m["tool_input_chars"]
            d["input_tokens"] += m["input_tokens"]
            d["cache_creation_input_tokens"] += m["cache_creation_input_tokens"]
            d["cache_read_input_tokens"] += m["cache_read_input_tokens"]
        d["tool_input_tokens_estimated"] = round(d["tool_input_chars"] / TOOL_INPUT_CHARS_PER_TOKEN)
        return d

    phases = {p: phase_decomposition(msgs_by_phase[p]) for p in ("warmup", "generation")}

    # Authoritative total from result event.
    auth_usage = (result_event or {}).get("usage") or {}
    auth_total_output = int(auth_usage.get("output_tokens", 0) or 0)

    sum_visible = sum(m["visible_output_tokens"] for m in messages.values())
    sum_tool_input_chars = sum(m["tool_input_chars"] for m in messages.values())
    sum_tool_input_est = round(sum_tool_input_chars / TOOL_INPUT_CHARS_PER_TOKEN)
    residual = auth_total_output - sum_visible - sum_tool_input_est

    output = dict(result_event) if result_event else {"error": "no result event in stream"}
    output["phases"] = phases
    output["measurement"] = {
        "authoritative_total_output_tokens": auth_total_output,
        "measured_visible_output_tokens": sum_visible,
        "measured_tool_input_chars": sum_tool_input_chars,
        "measured_tool_input_tokens_estimated": sum_tool_input_est,
        "thinking_residual_unmeasured_tokens": residual,
        "tool_input_chars_per_token_assumed": TOOL_INPUT_CHARS_PER_TOKEN,
        "note": (
            "Authoritative total comes from the result event's usage.output_tokens. "
            "Visible+tool_input are exact-per-message; thinking residual is the "
            "remainder and cannot be precisely allocated to warmup vs generation "
            "from stream data alone. Phase split applies to visible+tool_input only."
        ),
    }
    output["boundary_trigger"] = boundary_trigger
    output["marker_found"] = boundary_seen
    output["start_phase"] = args.start_phase

    json.dump(output, sys.stdout, indent=2)


if __name__ == "__main__":
    main()
