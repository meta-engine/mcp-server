# MetaEngine MCP — Benchmark Summary

> **These numbers are illustrations from one author's run on one spec on one day.** MetaEngine's whole philosophy is *try it yourself* — the harness is the deliverable, not the numbers. Reproduce in your own environment before quoting anything.

Runs requested: **5** per variant. Completed: a-mcp **5/5**, b-baseline **5/5**. Results: `<benchmark>/results/20260426-104532-typescript-heredoc`

**The headline is steady-state** — what each codebase costs once the model has been instructed on the MCP (or, equivalently, what it would cost if MetaEngine were in the model's training corpus). Warmup is reported separately as a one-time outside-training tax that wouldn't exist in an integrated world.

## Steady-state — per-codebase cost

This is what every codebase costs after the one-time warmup. If MetaEngine were in the model's training, this would be the *first*-codebase cost too.

| | output_tokens | cost USD | turns | cache_read | pass |
|---|---|---|---|---|---|
| a-mcp gen        |     20,217 | $ 1.4439 |  6.4 |     336,032 | 4/5 |
| b-baseline       |     21,112 | $ 3.2536 | 73.0 |   4,628,420 | 5/5 |
| **reduction**    | **  4.2%** | ** 55.6%** | **11.4× fewer** | ** 92.7%** | — |

## Agent-loop efficiency (structural — independent of training)

The cache_read difference is structural: it comes from **tool topology**, not from the model knowing MetaEngine.

- **Topology A (Write loop):** Many small tool calls — one per output. Each turn re-reads cumulative context. cache_read accumulates ~quadratically with output count.
- **Topology B (batched single call):** One large structured tool input → all outputs in one tool_result. cache_read is bounded.

Any MCP that consolidates multi-output work into one call benefits — this isn't MetaEngine-specific. It's a generalizable design pattern.

| session | turns | cache_read tokens | per-turn |
|---|---|---|---|
| a-mcp warmup | 10.0 ± 0.7 | 396,597 ± 40,742 | 39,605 ± 1,656 |
| a-mcp gen | 6.4 ± 0.5 | 336,032 ± 36,114 | 52,432 ± 1,323 |
| b-baseline | 73.0 ± 0.0 | 4,628,420 ± 50,726 | 63,403 ± 695 |

> Per-turn cache_read is similar (~40-60k); the headline gap comes from the **turn count**. Implication for smaller-context models: baseline at 73 turns is already large for a 200k-context model — the same workload could fail on Sonnet/Haiku, not just cost more. Topology B keeps loops short enough that cheaper models can do the same work.

## Wall-clock (indicative only — depends on Anthropic load)

Per-session `duration_ms` from each `claude -p` result event. Not reproducible across runs/days, but useful for spotting trends when other variables are held constant.

| session | duration mean | api_ms mean |
|---|---|---|
| a-mcp warmup | 162.0s ± 14.1s | 162.9s |
| a-mcp gen | 174.5s ± 18.1s | 174.6s |
| b-baseline | 305.4s ± 32.9s | 305.5s |

Script total wall-clock: **693s** (11m 33s).

## Warmup — one-time outside-training tax

This is what a non-trained model pays to learn the MCP correctly via runtime docs. If MetaEngine were integrated into Claude Code's built-ins or the model's training, this row would be ~0.

| | output_tokens | cost USD | turns | summary written |
|---|---|---|---|---|
| a-mcp warmup | 11,130 ± 1,036 | $0.9598 ± $0.0322 | 10.0 ± 0.7 | 23,270 ± 2,310 chars |

## First-codebase total (for completeness)

What a user pays who runs MetaEngine *exactly once* and never again — warmup is not amortized. This is the worst-case framing.

- a-mcp (warmup + gen): 31,347 output tokens, $2.4037
- b-baseline:           21,112 output tokens, $3.2536
- Cost: 26.1% reduction — much smaller than steady-state because warmup is a one-shot.

## Output token decomposition (descriptive)

Authoritative `output_tokens` = visible text + tool_use input bytes (model-generated structured arguments) + thinking-block tokens (encrypted, billed). Per-event stream usage shows only the visible portion; the result event aggregates all three.

| session | visible (exact) | tool_input (≈chars/3.5) | thinking residual | sum (=auth) |
|---|---|---|---|---|
| a-mcp warmup | 293 ± 19 | 7,353 ± 680 | 3,484 ± 368 | 11,130 ± 1,036 |
| a-mcp gen | 161 ± 43 | 13,128 ± 186 | 6,928 ± 1,482 | 20,217 ± 1,283 |
| b-baseline | 5,089 ± 10 | 10,396 ± 260 | 5,627 ± 749 | 21,112 ± 735 |

## Per-run

| run | a-mcp warmup $ | a-mcp gen $ | a-mcp total $ | a-mcp output | baseline $ | baseline output | a-files | b-files |
|---|---|---|---|---|---|---|---|---|
| 001 | $0.9989 | $1.5369 | $2.5358 | 32,098 | $3.2653 | 21,419 | 71 | 71 |
| 002 | $0.9322 | $1.3457 | $2.2778 | 29,795 | $3.1820 | 20,199 | 71 | 71 |
| 003 | $0.9872 | $1.4600 | $2.4472 | 34,164 | $3.3264 | 21,433 | 71 | 71 |
| 004 | $0.9272 | $1.5067 | $2.4339 | 30,413 | $3.2043 | 20,516 | 71 | 71 |
| 005 | $0.9535 | $1.3702 | $2.3237 | 30,265 | $3.2902 | 21,993 | 71 | 71 |

## Per-run wall-clock

Per-session `duration_ms` from each `claude -p` result event, broken out per run to make trends visible (cross-session cache warming, parallel-batch effects, etc.). Indicative only — depends on Anthropic load on the day.

| run | a-mcp warmup s | a-mcp gen s | b-baseline s |
|---|---|---|---|
| 001 | 174 | 169 | 288 |
| 002 | 157 | 150 | 287 |
| 003 | 175 | 200 | 300 |
| 004 | 162 | 174 | 287 |
| 005 | 141 | 180 | 363 |

## Caveats

- Authoritative numbers come from `claude -p`'s result event (`usage.output_tokens`, `total_cost_usd`). Per-event stream usage shows only visible-text output, which under-reports by excluding thinking and tool_use input bytes.
- **`cost USD` is the would-be API cost** at Anthropic's published rates — a token-usage proxy that's comparable across users and models. It's NOT what a subscription user (Claude Max/Pro) actually pays — those plans are flat-rate. The dollar figure still reflects the *relative work* of each variant; tokens × price is the universal benchmark unit.
- The two-session methodology gives **exact** phase split: each session has its own result event total. The gen session has the warmup's knowledge brief in its user prompt (a few hundred input tokens) — slightly inflating gen vs an ideal trained-model case, in the honest direction.
- Output token decomposition (visible / tool_input / thinking) is *descriptive only* — the visible+tool_input parts are exact-per-message but tool_input tokens are estimated from chars (3.5/token). Thinking is the residual. The sum equals the authoritative total.
- A model trained natively on MetaEngine would have warmup ≈ 0 (it would already know the API). Steady-state approximates that.
- Failed/partial runs are *not* filtered. Pass rate alongside cost is the full picture.
- Wall-clock is reported as indicative only — depends on Anthropic server load and is not reproducible run-to-run.
