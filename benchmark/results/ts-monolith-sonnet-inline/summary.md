# MetaEngine MCP — Benchmark Summary

> **These numbers are illustrations from one author's run on one spec on one day.** MetaEngine's whole philosophy is *try it yourself* — the harness is the deliverable, not the numbers. Reproduce in your own environment before quoting anything.

Runs requested: **5** per variant. Completed: a-mcp **5/5**, b-baseline **5/5**. Results: `<benchmark>/results/20260426-213406-typescript-inline-sonnet-monolith`

**The headline is steady-state** — what each codebase costs once the model has been instructed on the MCP (or, equivalently, what it would cost if MetaEngine were in the model's training corpus). Warmup is reported separately as a one-time outside-training tax that wouldn't exist in an integrated world.

## Steady-state — per-codebase cost

This is what every codebase costs after the one-time warmup. If MetaEngine were in the model's training, this would be the *first*-codebase cost too.

| | output_tokens | cost USD | turns | cache_read | pass |
|---|---|---|---|---|---|
| a-mcp gen        |     31,285 | $ 0.8272 |  5.0 |     234,199 | 5/5 |
| b-baseline       |     22,327 | $ 0.9951 | 70.6 |     278,321 | 5/5 |
| **reduction**    | **-40.1%** | ** 16.9%** | **14.1× fewer** | ** 15.9%** | — |

## Agent-loop efficiency (structural — independent of training)

The cache_read difference is structural: it comes from **tool topology**, not from the model knowing MetaEngine.

- **Topology A (Write loop):** Many small tool calls — one per output. Each turn re-reads cumulative context. cache_read accumulates ~quadratically with output count.
- **Topology B (batched single call):** One large structured tool input → all outputs in one tool_result. cache_read is bounded.

Any MCP that consolidates multi-output work into one call benefits — this isn't MetaEngine-specific. It's a generalizable design pattern.

| session | turns | cache_read tokens | per-turn |
|---|---|---|---|
| a-mcp warmup | 6.4 ± 2.2 | 159,977 ± 67,271 | 24,504 ± 2,893 |
| a-mcp gen | 5.0 ± 0.0 | 234,199 ± 21,967 | 46,840 ± 4,393 |
| b-baseline | 70.6 ± 0.5 | 278,321 ± 325,562 | 3,925 ± 4,581 |

> Per-turn cache_read is similar (~40-60k); the headline gap comes from the **turn count**. Implication for smaller-context models: baseline at 73 turns is already large for a 200k-context model — the same workload could fail on Sonnet/Haiku, not just cost more. Topology B keeps loops short enough that cheaper models can do the same work.

## Wall-clock (indicative only — depends on Anthropic load)

Per-session `duration_ms` from each `claude -p` result event. Not reproducible across runs/days, but useful for spotting trends when other variables are held constant.

| session | duration mean | api_ms mean |
|---|---|---|
| a-mcp warmup | 146.7s ± 25.0s | 147.9s |
| a-mcp gen | 329.1s ± 97.0s | 326.6s |
| b-baseline | 208.6s ± 23.9s | 209.3s |

Script total wall-clock: **3468s** (57m 48s).

## Warmup — one-time outside-training tax

This is what a non-trained model pays to learn the MCP correctly via runtime docs. If MetaEngine were integrated into Claude Code's built-ins or the model's training, this row would be ~0.

| | output_tokens | cost USD | turns | summary written |
|---|---|---|---|---|
| a-mcp warmup | 8,374 ± 1,275 | $0.2908 ± $0.0588 | 6.4 ± 2.2 | 25,419 ± 3,048 chars |

## First-codebase total (for completeness)

What a user pays who runs MetaEngine *exactly once* and never again — warmup is not amortized. This is the worst-case framing.

- a-mcp (warmup + gen): 39,660 output tokens, $1.1180
- b-baseline:           22,327 output tokens, $0.9951
- Cost: -12.4% reduction — much smaller than steady-state because warmup is a one-shot.

## Output token decomposition (descriptive)

Authoritative `output_tokens` = visible text + tool_use input bytes (model-generated structured arguments) + thinking-block tokens (encrypted, billed). Per-event stream usage shows only the visible portion; the result event aggregates all three.

| session | visible (exact) | tool_input (≈chars/3.5) | thinking residual | sum (=auth) |
|---|---|---|---|---|
| a-mcp warmup | 80 ± 37 | 7,897 ± 962 | 398 ± 345 | 8,374 ± 1,275 |
| a-mcp gen | 25 ± 8 | 8,653 ± 3 | 22,608 ± 8,012 | 31,285 ± 8,010 |
| b-baseline | 322 ± 382 | 10,302 ± 199 | 11,703 ± 3,162 | 22,327 ± 2,773 |

## Per-run

| run | a-mcp warmup $ | a-mcp gen $ | a-mcp total $ | a-mcp output | baseline $ | baseline output | a-files | b-files |
|---|---|---|---|---|---|---|---|---|
| 001 | $0.2876 | $0.6782 | $0.9657 | 31,724 | $0.9456 | 26,947 | 68 | 68 |
| 002 | $0.2123 | $0.8201 | $1.0324 | 35,726 | $0.8394 | 22,213 | 68 | 68 |
| 003 | $0.3301 | $0.8421 | $1.1721 | 42,072 | $1.2779 | 20,861 | 68 | 68 |
| 004 | $0.3631 | $1.0696 | $1.4327 | 53,957 | $0.7497 | 19,662 | 68 | 68 |
| 005 | $0.2611 | $0.7259 | $0.9870 | 34,819 | $1.1628 | 21,951 | 68 | 68 |

## Per-run wall-clock

Per-session `duration_ms` from each `claude -p` result event, broken out per run to make trends visible (cross-session cache warming, parallel-batch effects, etc.). Indicative only — depends on Anthropic load on the day.

| run | a-mcp warmup s | a-mcp gen s | b-baseline s |
|---|---|---|---|
| 001 | 136 | 264 | 241 |
| 002 | 116 | 278 | 183 |
| 003 | 181 | 299 | 186 |
| 004 | 162 | 500 | 215 |
| 005 | 140 | 304 | 218 |

## Caveats

- Authoritative numbers come from `claude -p`'s result event (`usage.output_tokens`, `total_cost_usd`). Per-event stream usage shows only visible-text output, which under-reports by excluding thinking and tool_use input bytes.
- **`cost USD` is the would-be API cost** at Anthropic's published rates — a token-usage proxy that's comparable across users and models. It's NOT what a subscription user (Claude Max/Pro) actually pays — those plans are flat-rate. The dollar figure still reflects the *relative work* of each variant; tokens × price is the universal benchmark unit.
- The two-session methodology gives **exact** phase split: each session has its own result event total. The gen session has the warmup's knowledge brief in its user prompt (a few hundred input tokens) — slightly inflating gen vs an ideal trained-model case, in the honest direction.
- Output token decomposition (visible / tool_input / thinking) is *descriptive only* — the visible+tool_input parts are exact-per-message but tool_input tokens are estimated from chars (3.5/token). Thinking is the residual. The sum equals the authoritative total.
- A model trained natively on MetaEngine would have warmup ≈ 0 (it would already know the API). Steady-state approximates that.
- Failed/partial runs are *not* filtered. Pass rate alongside cost is the full picture.
- Wall-clock is reported as indicative only — depends on Anthropic server load and is not reproducible run-to-run.
- Data collected on Opus 4.7 (1M-context). Within a few-day window we assume Anthropic-side model behavior is stable; cross-arm and cross-language comparisons inside that window are apples-to-apples. Re-runs after a model update are out of scope for token-cost reasons (not a cross-model benchmark).
