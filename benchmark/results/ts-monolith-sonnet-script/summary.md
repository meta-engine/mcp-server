# MetaEngine MCP — Benchmark Summary

> **These numbers are illustrations from one author's run on one spec on one day.** MetaEngine's whole philosophy is *try it yourself* — the harness is the deliverable, not the numbers. Reproduce in your own environment before quoting anything.

Runs requested: **5** per variant. Completed: a-mcp **5/5**, b-baseline **5/5**. Results: `<benchmark>/results/20260426-223154-typescript-script-sonnet-monolith`

**The headline is steady-state** — what each codebase costs once the model has been instructed on the MCP (or, equivalently, what it would cost if MetaEngine were in the model's training corpus). Warmup is reported separately as a one-time outside-training tax that wouldn't exist in an integrated world.

## Steady-state — per-codebase cost

This is what every codebase costs after the one-time warmup. If MetaEngine were in the model's training, this would be the *first*-codebase cost too.

| | output_tokens | cost USD | turns | cache_read | pass |
|---|---|---|---|---|---|
| a-mcp gen        |     10,261 | $ 0.4418 |  7.0 |     325,339 | 5/5 |
| b-baseline       |     22,468 | $ 1.0818 | 70.6 |     233,146 | 5/5 |
| **reduction**    | ** 54.3%** | ** 59.2%** | **10.1× fewer** | **-39.5%** | — |

## Agent-loop efficiency (structural — independent of training)

The cache_read difference is structural: it comes from **tool topology**, not from the model knowing MetaEngine.

- **Topology A (Write loop):** Many small tool calls — one per output. Each turn re-reads cumulative context. cache_read accumulates ~quadratically with output count.
- **Topology B (batched single call):** One large structured tool input → all outputs in one tool_result. cache_read is bounded.

Any MCP that consolidates multi-output work into one call benefits — this isn't MetaEngine-specific. It's a generalizable design pattern.

| session | turns | cache_read tokens | per-turn |
|---|---|---|---|
| a-mcp warmup | 5.8 ± 0.4 | 142,931 ± 18,449 | 24,565 ± 1,572 |
| a-mcp gen | 7.0 ± 0.0 | 325,339 ± 8,487 | 46,477 ± 1,212 |
| b-baseline | 70.6 ± 0.5 | 233,146 ± 184,184 | 3,292 ± 2,588 |

> Per-turn cache_read is similar (~40-60k); the headline gap comes from the **turn count**. Implication for smaller-context models: baseline at 73 turns is already large for a 200k-context model — the same workload could fail on Sonnet/Haiku, not just cost more. Topology B keeps loops short enough that cheaper models can do the same work.

## Wall-clock (indicative only — depends on Anthropic load)

Per-session `duration_ms` from each `claude -p` result event. Not reproducible across runs/days, but useful for spotting trends when other variables are held constant.

| session | duration mean | api_ms mean |
|---|---|---|
| a-mcp warmup | 119.2s ± 14.7s | 119.8s |
| a-mcp gen | 151.9s ± 28.2s | 148.8s |
| b-baseline | 198.3s ± 23.9s | 199.1s |

Script total wall-clock: **2395s** (39m 55s).

## Warmup — one-time outside-training tax

This is what a non-trained model pays to learn the MCP correctly via runtime docs. If MetaEngine were integrated into Claude Code's built-ins or the model's training, this row would be ~0.

| | output_tokens | cost USD | turns | summary written |
|---|---|---|---|---|
| a-mcp warmup | 7,457 ± 747 | $0.2494 ± $0.0304 | 5.8 ± 0.4 | 22,775 ± 2,268 chars |

## First-codebase total (for completeness)

What a user pays who runs MetaEngine *exactly once* and never again — warmup is not amortized. This is the worst-case framing.

- a-mcp (warmup + gen): 17,719 output tokens, $0.6912
- b-baseline:           22,468 output tokens, $1.0818
- Cost: 36.1% reduction — much smaller than steady-state because warmup is a one-shot.

## Output token decomposition (descriptive)

Authoritative `output_tokens` = visible text + tool_use input bytes (model-generated structured arguments) + thinking-block tokens (encrypted, billed). Per-event stream usage shows only the visible portion; the result event aggregates all three.

| session | visible (exact) | tool_input (≈chars/3.5) | thinking residual | sum (=auth) |
|---|---|---|---|---|
| a-mcp warmup | 103 ± 24 | 7,120 ± 709 | 234 ± 110 | 7,457 ± 747 |
| a-mcp gen | 114 ± 28 | 2,123 ± 179 | 8,024 ± 1,517 | 10,261 ± 1,507 |
| b-baseline | 252 ± 236 | 10,378 ± 249 | 11,838 ± 3,916 | 22,468 ± 3,888 |

## Per-run

| run | a-mcp warmup $ | a-mcp gen $ | a-mcp total $ | a-mcp output | baseline $ | baseline output | a-files | b-files |
|---|---|---|---|---|---|---|---|---|
| 001 | $0.2988 | $0.4401 | $0.7389 | 18,347 | $0.8079 | 20,579 | 68 | 68 |
| 002 | $0.2504 | $0.4192 | $0.6696 | 16,455 | $0.9874 | 20,786 | 68 | 69 |
| 003 | $0.2260 | $0.4025 | $0.6286 | 15,202 | $1.3424 | 21,745 | 68 | 68 |
| 004 | $0.2228 | $0.4782 | $0.7011 | 19,201 | $1.0091 | 29,323 | 68 | 68 |
| 005 | $0.2488 | $0.4689 | $0.7177 | 19,388 | $1.2623 | 19,907 | 68 | 68 |

## Per-run wall-clock

Per-session `duration_ms` from each `claude -p` result event, broken out per run to make trends visible (cross-session cache warming, parallel-batch effects, etc.). Indicative only — depends on Anthropic load on the day.

| run | a-mcp warmup s | a-mcp gen s | b-baseline s |
|---|---|---|---|
| 001 | 137 | 135 | 183 |
| 002 | 131 | 139 | 195 |
| 003 | 100 | 121 | 186 |
| 004 | 114 | 185 | 240 |
| 005 | 113 | 178 | 187 |

## Caveats

- Authoritative numbers come from `claude -p`'s result event (`usage.output_tokens`, `total_cost_usd`). Per-event stream usage shows only visible-text output, which under-reports by excluding thinking and tool_use input bytes.
- **`cost USD` is the would-be API cost** at Anthropic's published rates — a token-usage proxy that's comparable across users and models. It's NOT what a subscription user (Claude Max/Pro) actually pays — those plans are flat-rate. The dollar figure still reflects the *relative work* of each variant; tokens × price is the universal benchmark unit.
- The two-session methodology gives **exact** phase split: each session has its own result event total. The gen session has the warmup's knowledge brief in its user prompt (a few hundred input tokens) — slightly inflating gen vs an ideal trained-model case, in the honest direction.
- Output token decomposition (visible / tool_input / thinking) is *descriptive only* — the visible+tool_input parts are exact-per-message but tool_input tokens are estimated from chars (3.5/token). Thinking is the residual. The sum equals the authoritative total.
- A model trained natively on MetaEngine would have warmup ≈ 0 (it would already know the API). Steady-state approximates that.
- Failed/partial runs are *not* filtered. Pass rate alongside cost is the full picture.
- Wall-clock is reported as indicative only — depends on Anthropic server load and is not reproducible run-to-run.
- Data collected on Opus 4.7 (1M-context). Within a few-day window we assume Anthropic-side model behavior is stable; cross-arm and cross-language comparisons inside that window are apples-to-apples. Re-runs after a model update are out of scope for token-cost reasons (not a cross-model benchmark).
