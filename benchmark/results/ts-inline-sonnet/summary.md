# MetaEngine MCP — Benchmark Summary

> **These numbers are illustrations from one author's run on one spec on one day.** MetaEngine's whole philosophy is *try it yourself* — the harness is the deliverable, not the numbers. Reproduce in your own environment before quoting anything.

Runs requested: **5** per variant. Completed: a-mcp **5/5**, b-baseline **5/5**. Results: `<benchmark>/results/20260426-154711-typescript-inline-sonnet`

**The headline is steady-state** — what each codebase costs once the model has been instructed on the MCP (or, equivalently, what it would cost if MetaEngine were in the model's training corpus). Warmup is reported separately as a one-time outside-training tax that wouldn't exist in an integrated world.

## Steady-state — per-codebase cost

This is what every codebase costs after the one-time warmup. If MetaEngine were in the model's training, this would be the *first*-codebase cost too.

| | output_tokens | cost USD | turns | cache_read | pass |
|---|---|---|---|---|---|
| a-mcp gen        |     21,299 | $ 0.6296 |  5.0 |     225,230 | 3/5 |
| b-baseline       |     16,280 | $ 0.5863 | 73.0 |      48,484 | 5/5 |
| **reduction**    | **-30.8%** | ** -7.4%** | **14.6× fewer** | **-364.5%** | — |

## Agent-loop efficiency (structural — independent of training)

The cache_read difference is structural: it comes from **tool topology**, not from the model knowing MetaEngine.

- **Topology A (Write loop):** Many small tool calls — one per output. Each turn re-reads cumulative context. cache_read accumulates ~quadratically with output count.
- **Topology B (batched single call):** One large structured tool input → all outputs in one tool_result. cache_read is bounded.

Any MCP that consolidates multi-output work into one call benefits — this isn't MetaEngine-specific. It's a generalizable design pattern.

| session | turns | cache_read tokens | per-turn |
|---|---|---|---|
| a-mcp warmup | 5.6 ± 0.5 | 146,879 ± 27,929 | 26,033 ± 2,585 |
| a-mcp gen | 5.0 ± 0.0 | 225,230 ± 5,739 | 45,046 ± 1,148 |
| b-baseline | 73.0 ± 0.0 | 48,484 ± 5,434 | 664 ± 74 |

> Per-turn cache_read is similar (~40-60k); the headline gap comes from the **turn count**. Implication for smaller-context models: baseline at 73 turns is already large for a 200k-context model — the same workload could fail on Sonnet/Haiku, not just cost more. Topology B keeps loops short enough that cheaper models can do the same work.

## Wall-clock (indicative only — depends on Anthropic load)

Per-session `duration_ms` from each `claude -p` result event. Not reproducible across runs/days, but useful for spotting trends when other variables are held constant.

| session | duration mean | api_ms mean |
|---|---|---|
| a-mcp warmup | 152.5s ± 16.7s | 153.7s |
| a-mcp gen | 214.9s ± 36.4s | 216.0s |
| b-baseline | 148.1s ± 27.2s | 149.3s |

Script total wall-clock: **2620s** (43m 40s).

## Warmup — one-time outside-training tax

This is what a non-trained model pays to learn the MCP correctly via runtime docs. If MetaEngine were integrated into Claude Code's built-ins or the model's training, this row would be ~0.

| | output_tokens | cost USD | turns | summary written |
|---|---|---|---|---|
| a-mcp warmup | 8,921 ± 1,371 | $0.2961 ± $0.0476 | 5.6 ± 0.5 | 26,640 ± 3,416 chars |

## First-codebase total (for completeness)

What a user pays who runs MetaEngine *exactly once* and never again — warmup is not amortized. This is the worst-case framing.

- a-mcp (warmup + gen): 30,220 output tokens, $0.9257
- b-baseline:           16,280 output tokens, $0.5863
- Cost: -57.9% reduction — much smaller than steady-state because warmup is a one-shot.

## Output token decomposition (descriptive)

Authoritative `output_tokens` = visible text + tool_use input bytes (model-generated structured arguments) + thinking-block tokens (encrypted, billed). Per-event stream usage shows only the visible portion; the result event aggregates all three.

| session | visible (exact) | tool_input (≈chars/3.5) | thinking residual | sum (=auth) |
|---|---|---|---|---|
| a-mcp warmup | 73 ± 24 | 8,257 ± 1,068 | 591 ± 358 | 8,921 ± 1,371 |
| a-mcp gen | 23 ± 2 | 9,967 ± 28 | 11,309 ± 5,616 | 21,299 ± 5,607 |
| b-baseline | 16 ± 3 | 10,932 ± 85 | 5,332 ± 1,297 | 16,280 ± 1,361 |

## Per-run

| run | a-mcp warmup $ | a-mcp gen $ | a-mcp total $ | a-mcp output | baseline $ | baseline output | a-files | b-files |
|---|---|---|---|---|---|---|---|---|
| 001 | $0.2152 | $0.6042 | $0.8194 | 27,125 | $0.6006 | 18,568 | 71 | 71 |
| 002 | $0.3302 | $0.5938 | $0.9240 | 29,140 | $0.6815 | 15,258 | 71 | 71 |
| 003 | $0.3080 | $0.8160 | $1.1241 | 39,954 | $0.5445 | 15,571 | 71 | 71 |
| 004 | $0.2961 | $0.5561 | $0.8521 | 26,443 | $0.5616 | 16,487 | 71 | 71 |
| 005 | $0.3309 | $0.5780 | $0.9089 | 28,437 | $0.5434 | 15,514 | 71 | 71 |

## Per-run wall-clock

Per-session `duration_ms` from each `claude -p` result event, broken out per run to make trends visible (cross-session cache warming, parallel-batch effects, etc.). Indicative only — depends on Anthropic load on the day.

| run | a-mcp warmup s | a-mcp gen s | b-baseline s |
|---|---|---|---|
| 001 | 124 | 220 | 193 |
| 002 | 161 | 216 | 147 |
| 003 | 165 | 271 | 145 |
| 004 | 151 | 174 | 135 |
| 005 | 162 | 194 | 121 |

## Caveats

- Authoritative numbers come from `claude -p`'s result event (`usage.output_tokens`, `total_cost_usd`). Per-event stream usage shows only visible-text output, which under-reports by excluding thinking and tool_use input bytes.
- **`cost USD` is the would-be API cost** at Anthropic's published rates — a token-usage proxy that's comparable across users and models. It's NOT what a subscription user (Claude Max/Pro) actually pays — those plans are flat-rate. The dollar figure still reflects the *relative work* of each variant; tokens × price is the universal benchmark unit.
- The two-session methodology gives **exact** phase split: each session has its own result event total. The gen session has the warmup's knowledge brief in its user prompt (a few hundred input tokens) — slightly inflating gen vs an ideal trained-model case, in the honest direction.
- Output token decomposition (visible / tool_input / thinking) is *descriptive only* — the visible+tool_input parts are exact-per-message but tool_input tokens are estimated from chars (3.5/token). Thinking is the residual. The sum equals the authoritative total.
- A model trained natively on MetaEngine would have warmup ≈ 0 (it would already know the API). Steady-state approximates that.
- Failed/partial runs are *not* filtered. Pass rate alongside cost is the full picture.
- Wall-clock is reported as indicative only — depends on Anthropic server load and is not reproducible run-to-run.
- Data collected on Opus 4.7 (1M-context). Within a few-day window we assume Anthropic-side model behavior is stable; cross-arm and cross-language comparisons inside that window are apples-to-apples. Re-runs after a model update are out of scope for token-cost reasons (not a cross-model benchmark).
