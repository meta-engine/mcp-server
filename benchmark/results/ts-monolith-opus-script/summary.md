# MetaEngine MCP — Benchmark Summary

> **These numbers are illustrations from one author's run on one spec on one day.** MetaEngine's whole philosophy is *try it yourself* — the harness is the deliverable, not the numbers. Reproduce in your own environment before quoting anything.

Runs requested: **5** per variant. Completed: a-mcp **5/5**, b-baseline **5/5**. Results: `<benchmark>/results/20260426-210323-typescript-script-monolith`

**The headline is steady-state** — what each codebase costs once the model has been instructed on the MCP (or, equivalently, what it would cost if MetaEngine were in the model's training corpus). Warmup is reported separately as a one-time outside-training tax that wouldn't exist in an integrated world.

## Steady-state — per-codebase cost

This is what every codebase costs after the one-time warmup. If MetaEngine were in the model's training, this would be the *first*-codebase cost too.

| | output_tokens | cost USD | turns | cache_read | pass |
|---|---|---|---|---|---|
| a-mcp gen        |      8,531 | $ 1.0926 |  7.6 |     386,739 | 5/5 |
| b-baseline       |     23,583 | $ 3.3804 | 72.2 |   4,648,979 | 5/5 |
| **reduction**    | ** 63.8%** | ** 67.7%** | **9.5× fewer** | ** 91.7%** | — |

## Agent-loop efficiency (structural — independent of training)

The cache_read difference is structural: it comes from **tool topology**, not from the model knowing MetaEngine.

- **Topology A (Write loop):** Many small tool calls — one per output. Each turn re-reads cumulative context. cache_read accumulates ~quadratically with output count.
- **Topology B (batched single call):** One large structured tool input → all outputs in one tool_result. cache_read is bounded.

Any MCP that consolidates multi-output work into one call benefits — this isn't MetaEngine-specific. It's a generalizable design pattern.

| session | turns | cache_read tokens | per-turn |
|---|---|---|---|
| a-mcp warmup | 8.0 ± 2.0 | 284,469 ± 105,317 | 34,463 ± 5,578 |
| a-mcp gen | 7.6 ± 0.5 | 386,739 ± 29,180 | 50,887 ± 1,142 |
| b-baseline | 72.2 ± 4.4 | 4,648,979 ± 384,261 | 64,347 ± 2,355 |

> Per-turn cache_read is similar (~40-60k); the headline gap comes from the **turn count**. Implication for smaller-context models: baseline at 73 turns is already large for a 200k-context model — the same workload could fail on Sonnet/Haiku, not just cost more. Topology B keeps loops short enough that cheaper models can do the same work.

## Wall-clock (indicative only — depends on Anthropic load)

Per-session `duration_ms` from each `claude -p` result event. Not reproducible across runs/days, but useful for spotting trends when other variables are held constant.

| session | duration mean | api_ms mean |
|---|---|---|
| a-mcp warmup | 142.7s ± 8.7s | 143.4s |
| a-mcp gen | 112.2s ± 37.4s | 110.2s |
| b-baseline | 326.5s ± 37.1s | 326.9s |

Script total wall-clock: **1843s** (30m 43s).

## Warmup — one-time outside-training tax

This is what a non-trained model pays to learn the MCP correctly via runtime docs. If MetaEngine were integrated into Claude Code's built-ins or the model's training, this row would be ~0.

| | output_tokens | cost USD | turns | summary written |
|---|---|---|---|---|
| a-mcp warmup | 10,076 ± 859 | $0.7788 ± $0.1109 | 8.0 ± 2.0 | 21,510 ± 1,382 chars |

## First-codebase total (for completeness)

What a user pays who runs MetaEngine *exactly once* and never again — warmup is not amortized. This is the worst-case framing.

- a-mcp (warmup + gen): 18,607 output tokens, $1.8714
- b-baseline:           23,583 output tokens, $3.3804
- Cost: 44.6% reduction — much smaller than steady-state because warmup is a one-shot.

## Output token decomposition (descriptive)

Authoritative `output_tokens` = visible text + tool_use input bytes (model-generated structured arguments) + thinking-block tokens (encrypted, billed). Per-event stream usage shows only the visible portion; the result event aggregates all three.

| session | visible (exact) | tool_input (≈chars/3.5) | thinking residual | sum (=auth) |
|---|---|---|---|---|
| a-mcp warmup | 209 ± 68 | 6,825 ± 455 | 3,042 ± 469 | 10,076 ± 859 |
| a-mcp gen | 258 ± 52 | 2,042 ± 93 | 6,231 ± 3,331 | 8,531 ± 3,344 |
| b-baseline | 4,763 ± 543 | 10,729 ± 1,497 | 8,091 ± 2,712 | 23,583 ± 2,359 |

## Per-run

| run | a-mcp warmup $ | a-mcp gen $ | a-mcp total $ | a-mcp output | baseline $ | baseline output | a-files | b-files |
|---|---|---|---|---|---|---|---|---|
| 001 | $0.6497 | $1.1402 | $1.7899 | 18,727 | $3.1848 | 22,329 | 68 | 68 |
| 002 | $0.9011 | $1.2246 | $2.1258 | 23,338 | $3.1967 | 22,775 | 68 | 68 |
| 003 | $0.6733 | $1.1366 | $1.8098 | 19,699 | $3.4605 | 26,846 | 68 | 68 |
| 004 | $0.8270 | $1.0588 | $1.8858 | 17,600 | $3.0914 | 20,900 | 68 | 68 |
| 005 | $0.8429 | $0.9026 | $1.7456 | 13,670 | $3.9684 | 25,064 | 68 | 68 |

## Per-run wall-clock

Per-session `duration_ms` from each `claude -p` result event, broken out per run to make trends visible (cross-session cache warming, parallel-batch effects, etc.). Indicative only — depends on Anthropic load on the day.

| run | a-mcp warmup s | a-mcp gen s | b-baseline s |
|---|---|---|---|
| 001 | 135 | 126 | 298 |
| 002 | 148 | 152 | 343 |
| 003 | 134 | 131 | 338 |
| 004 | 155 | 96 | 280 |
| 005 | 141 | 56 | 373 |

## Caveats

- Authoritative numbers come from `claude -p`'s result event (`usage.output_tokens`, `total_cost_usd`). Per-event stream usage shows only visible-text output, which under-reports by excluding thinking and tool_use input bytes.
- **`cost USD` is the would-be API cost** at Anthropic's published rates — a token-usage proxy that's comparable across users and models. It's NOT what a subscription user (Claude Max/Pro) actually pays — those plans are flat-rate. The dollar figure still reflects the *relative work* of each variant; tokens × price is the universal benchmark unit.
- The two-session methodology gives **exact** phase split: each session has its own result event total. The gen session has the warmup's knowledge brief in its user prompt (a few hundred input tokens) — slightly inflating gen vs an ideal trained-model case, in the honest direction.
- Output token decomposition (visible / tool_input / thinking) is *descriptive only* — the visible+tool_input parts are exact-per-message but tool_input tokens are estimated from chars (3.5/token). Thinking is the residual. The sum equals the authoritative total.
- A model trained natively on MetaEngine would have warmup ≈ 0 (it would already know the API). Steady-state approximates that.
- Failed/partial runs are *not* filtered. Pass rate alongside cost is the full picture.
- Wall-clock is reported as indicative only — depends on Anthropic server load and is not reproducible run-to-run.
- Data collected on Opus 4.7 (1M-context). Within a few-day window we assume Anthropic-side model behavior is stable; cross-arm and cross-language comparisons inside that window are apples-to-apples. Re-runs after a model update are out of scope for token-cost reasons (not a cross-model benchmark).
