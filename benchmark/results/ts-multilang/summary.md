# MetaEngine MCP — Benchmark Summary

> **These numbers are illustrations from one author's run on one spec on one day.** MetaEngine's whole philosophy is *try it yourself* — the harness is the deliverable, not the numbers. Reproduce in your own environment before quoting anything.

Runs requested: **5** per variant. Completed: a-mcp **5/5**, b-baseline **5/5**. Results: `<benchmark>/results/20260426-015434`

**The headline is steady-state** — what each codebase costs once the model has been instructed on the MCP (or, equivalently, what it would cost if MetaEngine were in the model's training corpus). Warmup is reported separately as a one-time outside-training tax that wouldn't exist in an integrated world.

## Steady-state — per-codebase cost

This is what every codebase costs after the one-time warmup. If MetaEngine were in the model's training, this would be the *first*-codebase cost too.

| | output_tokens | cost USD | turns | cache_read | pass |
|---|---|---|---|---|---|
| a-mcp gen        |     18,872 | $ 1.3176 |  5.0 |     231,174 | 4/5 |
| b-baseline       |     21,007 | $ 3.4335 | 76.4 |   4,799,141 | 5/5 |
| **reduction**    | ** 10.2%** | ** 61.6%** | **15.3× fewer** | ** 95.2%** | — |

## Agent-loop efficiency (structural — independent of training)

The cache_read difference is structural: it comes from **tool topology**, not from the model knowing MetaEngine.

- **Topology A (Write loop):** Many small tool calls — one per output. Each turn re-reads cumulative context. cache_read accumulates ~quadratically with output count.
- **Topology B (batched single call):** One large structured tool input → all outputs in one tool_result. cache_read is bounded.

Any MCP that consolidates multi-output work into one call benefits — this isn't MetaEngine-specific. It's a generalizable design pattern.

| session | turns | cache_read tokens | per-turn |
|---|---|---|---|
| a-mcp warmup | 8.2 ± 2.2 | 317,125 ± 88,306 | 38,501 ± 2,270 |
| a-mcp gen | 5.0 ± 0.0 | 231,174 ± 3,773 | 46,235 ± 755 |
| b-baseline | 76.4 ± 4.7 | 4,799,141 ± 463,818 | 62,709 ± 2,200 |

> Per-turn cache_read is similar (~40-60k); the headline gap comes from the **turn count**. Implication for smaller-context models: baseline at 73 turns is already large for a 200k-context model — the same workload could fail on Sonnet/Haiku, not just cost more. Topology B keeps loops short enough that cheaper models can do the same work.

## Wall-clock (indicative only — depends on Anthropic load)

Per-session `duration_ms` from each `claude -p` result event. Not reproducible across runs/days, but useful for spotting trends when other variables are held constant.

| session | duration mean | api_ms mean |
|---|---|---|
| a-mcp warmup | 175.9s ± 19.3s | 176.5s |
| a-mcp gen | 158.1s ± 13.4s | 158.0s |
| b-baseline | 275.7s ± 20.4s | 275.9s |

Script total wall-clock: **1870s** (31m 10s).

## Warmup — one-time outside-training tax

This is what a non-trained model pays to learn the MCP correctly via runtime docs. If MetaEngine were integrated into Claude Code's built-ins or the model's training, this row would be ~0.

| | output_tokens | cost USD | turns | summary written |
|---|---|---|---|---|
| a-mcp warmup | 12,436 ± 1,370 | $0.9280 ± $0.1417 | 8.2 ± 2.2 | 26,671 ± 2,506 chars |

## First-codebase total (for completeness)

What a user pays who runs MetaEngine *exactly once* and never again — warmup is not amortized. This is the worst-case framing.

- a-mcp (warmup + gen): 31,308 output tokens, $2.2456
- b-baseline:           21,007 output tokens, $3.4335
- Cost: 34.6% reduction — much smaller than steady-state because warmup is a one-shot.

## Output token decomposition (descriptive)

Authoritative `output_tokens` = visible text + tool_use input bytes (model-generated structured arguments) + thinking-block tokens (encrypted, billed). Per-event stream usage shows only the visible portion; the result event aggregates all three.

| session | visible (exact) | tool_input (≈chars/3.5) | thinking residual | sum (=auth) |
|---|---|---|---|---|
| a-mcp warmup | 251 ± 77 | 8,267 ± 794 | 3,918 ± 560 | 12,436 ± 1,370 |
| a-mcp gen | 94 ± 29 | 9,880 ± 90 | 8,899 ± 1,527 | 18,872 ± 1,590 |
| b-baseline | 5,231 ± 200 | 10,716 ± 1,130 | 5,059 ± 486 | 21,007 ± 1,626 |

## Per-run

| run | a-mcp warmup $ | a-mcp gen $ | a-mcp total $ | a-mcp output | baseline $ | baseline output | a-files | b-files |
|---|---|---|---|---|---|---|---|---|
| 001 | $1.0261 | $1.3089 | $2.3350 | 32,329 | $3.8539 | 22,629 | 71 | 71 |
| 002 | $1.0283 | $1.3583 | $2.3866 | 32,610 | $3.9019 | 22,922 | 71 | 71 |
| 003 | $1.0261 | $1.3409 | $2.3670 | 31,957 | $3.1131 | 19,790 | 71 | 71 |
| 004 | $0.8391 | $1.3326 | $2.1717 | 31,430 | $3.1304 | 20,071 | 71 | 71 |
| 005 | $0.7205 | $1.2472 | $1.9676 | 28,214 | $3.1680 | 19,621 | 71 | 71 |

## Caveats

- Authoritative numbers come from `claude -p`'s result event (`usage.output_tokens`, `total_cost_usd`). Per-event stream usage shows only visible-text output, which under-reports by excluding thinking and tool_use input bytes.
- The two-session methodology gives **exact** phase split: each session has its own result event total. The gen session has the warmup's knowledge brief in its user prompt (a few hundred input tokens) — slightly inflating gen vs an ideal trained-model case, in the honest direction.
- Output token decomposition (visible / tool_input / thinking) is *descriptive only* — the visible+tool_input parts are exact-per-message but tool_input tokens are estimated from chars (3.5/token). Thinking is the residual. The sum equals the authoritative total.
- A model trained natively on MetaEngine would have warmup ≈ 0 (it would already know the API). Steady-state approximates that.
- Failed/partial runs are *not* filtered. Pass rate alongside cost is the full picture.
- Wall-clock is reported as indicative only — depends on Anthropic server load and is not reproducible run-to-run.
