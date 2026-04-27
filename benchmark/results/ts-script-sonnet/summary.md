# MetaEngine MCP — Benchmark Summary

> **These numbers are illustrations from one author's run on one spec on one day.** MetaEngine's whole philosophy is *try it yourself* — the harness is the deliverable, not the numbers. Reproduce in your own environment before quoting anything.

Runs requested: **5** per variant. Completed: a-mcp **5/5**, b-baseline **5/5**. Results: `<benchmark>/results/20260426-182553-typescript-script-sonnet`

**The headline is steady-state** — what each codebase costs once the model has been instructed on the MCP (or, equivalently, what it would cost if MetaEngine were in the model's training corpus). Warmup is reported separately as a one-time outside-training tax that wouldn't exist in an integrated world.

## Steady-state — per-codebase cost

This is what every codebase costs after the one-time warmup. If MetaEngine were in the model's training, this would be the *first*-codebase cost too.

| | output_tokens | cost USD | turns | cache_read | pass |
|---|---|---|---|---|---|
| a-mcp gen        |      5,275 | $ 0.3584 |  7.0 |     320,572 | 5/5 |
| b-baseline       |     16,936 | $ 0.7750 | 73.0 |     798,591 | 5/5 |
| **reduction**    | ** 68.9%** | ** 53.8%** | **10.4× fewer** | ** 59.9%** | — |

## Agent-loop efficiency (structural — independent of training)

The cache_read difference is structural: it comes from **tool topology**, not from the model knowing MetaEngine.

- **Topology A (Write loop):** Many small tool calls — one per output. Each turn re-reads cumulative context. cache_read accumulates ~quadratically with output count.
- **Topology B (batched single call):** One large structured tool input → all outputs in one tool_result. cache_read is bounded.

Any MCP that consolidates multi-output work into one call benefits — this isn't MetaEngine-specific. It's a generalizable design pattern.

| session | turns | cache_read tokens | per-turn |
|---|---|---|---|
| a-mcp warmup | 5.8 ± 1.1 | 151,223 ± 43,894 | 25,633 ± 3,235 |
| a-mcp gen | 7.0 ± 0.0 | 320,572 ± 10,157 | 45,796 ± 1,451 |
| b-baseline | 73.0 ± 0.0 | 798,591 ± 1,682,725 | 10,940 ± 23,051 |

> Per-turn cache_read is similar (~40-60k); the headline gap comes from the **turn count**. Implication for smaller-context models: baseline at 73 turns is already large for a 200k-context model — the same workload could fail on Sonnet/Haiku, not just cost more. Topology B keeps loops short enough that cheaper models can do the same work.

## Wall-clock (indicative only — depends on Anthropic load)

Per-session `duration_ms` from each `claude -p` result event. Not reproducible across runs/days, but useful for spotting trends when other variables are held constant.

| session | duration mean | api_ms mean |
|---|---|---|
| a-mcp warmup | 139.9s ± 33.3s | 141.6s |
| a-mcp gen | 77.5s ± 11.8s | 77.6s |
| b-baseline | 174.8s ± 69.8s | 175.2s |

Script total wall-clock: **2006s** (33m 26s).

## Warmup — one-time outside-training tax

This is what a non-trained model pays to learn the MCP correctly via runtime docs. If MetaEngine were integrated into Claude Code's built-ins or the model's training, this row would be ~0.

| | output_tokens | cost USD | turns | summary written |
|---|---|---|---|---|
| a-mcp warmup | 8,525 ± 2,374 | $0.2922 ± $0.0841 | 5.8 ± 1.1 | 25,124 ± 7,095 chars |

## First-codebase total (for completeness)

What a user pays who runs MetaEngine *exactly once* and never again — warmup is not amortized. This is the worst-case framing.

- a-mcp (warmup + gen): 13,799 output tokens, $0.6506
- b-baseline:           16,936 output tokens, $0.7750
- Cost: 16.0% reduction — much smaller than steady-state because warmup is a one-shot.

## Output token decomposition (descriptive)

Authoritative `output_tokens` = visible text + tool_use input bytes (model-generated structured arguments) + thinking-block tokens (encrypted, billed). Per-event stream usage shows only the visible portion; the result event aggregates all three.

| session | visible (exact) | tool_input (≈chars/3.5) | thinking residual | sum (=auth) |
|---|---|---|---|---|
| a-mcp warmup | 74 ± 43 | 7,821 ± 2,106 | 630 ± 332 | 8,525 ± 2,374 |
| a-mcp gen | 140 ± 24 | 1,442 ± 102 | 3,692 ± 773 | 5,275 ± 884 |
| b-baseline | 900 ± 1,971 | 10,607 ± 492 | 5,430 ± 1,871 | 16,936 ± 1,023 |

## Per-run

| run | a-mcp warmup $ | a-mcp gen $ | a-mcp total $ | a-mcp output | baseline $ | baseline output | a-files | b-files |
|---|---|---|---|---|---|---|---|---|
| 001 | $0.3808 | $0.3463 | $0.7271 | 14,590 | $0.5488 | 15,803 | 71 | 71 |
| 002 | $0.3461 | $0.3626 | $0.7087 | 15,282 | $0.5592 | 16,358 | 71 | 71 |
| 003 | $0.3292 | $0.3701 | $0.6993 | 15,365 | $0.5626 | 16,541 | 71 | 71 |
| 004 | $0.2061 | $0.3651 | $0.5712 | 12,153 | $0.5955 | 18,298 | 71 | 71 |
| 005 | $0.1988 | $0.3479 | $0.5467 | 11,607 | $1.6086 | 17,680 | 71 | 71 |

## Per-run wall-clock

Per-session `duration_ms` from each `claude -p` result event, broken out per run to make trends visible (cross-session cache warming, parallel-batch effects, etc.). Indicative only — depends on Anthropic load on the day.

| run | a-mcp warmup s | a-mcp gen s | b-baseline s |
|---|---|---|---|
| 001 | 150 | 66 | 119 |
| 002 | 149 | 71 | 150 |
| 003 | 186 | 72 | 137 |
| 004 | 108 | 95 | 173 |
| 005 | 107 | 83 | 295 |

## Caveats

- Authoritative numbers come from `claude -p`'s result event (`usage.output_tokens`, `total_cost_usd`). Per-event stream usage shows only visible-text output, which under-reports by excluding thinking and tool_use input bytes.
- **`cost USD` is the would-be API cost** at Anthropic's published rates — a token-usage proxy that's comparable across users and models. It's NOT what a subscription user (Claude Max/Pro) actually pays — those plans are flat-rate. The dollar figure still reflects the *relative work* of each variant; tokens × price is the universal benchmark unit.
- The two-session methodology gives **exact** phase split: each session has its own result event total. The gen session has the warmup's knowledge brief in its user prompt (a few hundred input tokens) — slightly inflating gen vs an ideal trained-model case, in the honest direction.
- Output token decomposition (visible / tool_input / thinking) is *descriptive only* — the visible+tool_input parts are exact-per-message but tool_input tokens are estimated from chars (3.5/token). Thinking is the residual. The sum equals the authoritative total.
- A model trained natively on MetaEngine would have warmup ≈ 0 (it would already know the API). Steady-state approximates that.
- Failed/partial runs are *not* filtered. Pass rate alongside cost is the full picture.
- Wall-clock is reported as indicative only — depends on Anthropic server load and is not reproducible run-to-run.
- Data collected on Opus 4.7 (1M-context). Within a few-day window we assume Anthropic-side model behavior is stable; cross-arm and cross-language comparisons inside that window are apples-to-apples. Re-runs after a model update are out of scope for token-cost reasons (not a cross-model benchmark).
