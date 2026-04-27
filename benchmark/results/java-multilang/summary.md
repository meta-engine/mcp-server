# MetaEngine MCP — Benchmark Summary

> **These numbers are illustrations from one author's run on one spec on one day.** MetaEngine's whole philosophy is *try it yourself* — the harness is the deliverable, not the numbers. Reproduce in your own environment before quoting anything.

Runs requested: **5** per variant. Completed: a-mcp **5/5**, b-baseline **5/5**. Results: `<benchmark>/results/20260426-030529-java`

**The headline is steady-state** — what each codebase costs once the model has been instructed on the MCP (or, equivalently, what it would cost if MetaEngine were in the model's training corpus). Warmup is reported separately as a one-time outside-training tax that wouldn't exist in an integrated world.

## Steady-state — per-codebase cost

This is what every codebase costs after the one-time warmup. If MetaEngine were in the model's training, this would be the *first*-codebase cost too.

| | output_tokens | cost USD | turns | cache_read | pass |
|---|---|---|---|---|---|
| a-mcp gen        |     20,955 | $ 1.3801 |  5.0 |     233,577 | 5/5 |
| b-baseline       |     26,435 | $ 3.7399 | 76.6 |   5,095,268 | 5/5 |
| **reduction**    | ** 20.7%** | ** 63.1%** | **15.3× fewer** | ** 95.4%** | — |

## Agent-loop efficiency (structural — independent of training)

The cache_read difference is structural: it comes from **tool topology**, not from the model knowing MetaEngine.

- **Topology A (Write loop):** Many small tool calls — one per output. Each turn re-reads cumulative context. cache_read accumulates ~quadratically with output count.
- **Topology B (batched single call):** One large structured tool input → all outputs in one tool_result. cache_read is bounded.

Any MCP that consolidates multi-output work into one call benefits — this isn't MetaEngine-specific. It's a generalizable design pattern.

| session | turns | cache_read tokens | per-turn |
|---|---|---|---|
| a-mcp warmup | 8.4 ± 1.1 | 309,261 ± 58,549 | 36,625 ± 2,054 |
| a-mcp gen | 5.0 ± 0.0 | 233,577 ± 3,177 | 46,715 ± 635 |
| b-baseline | 76.6 ± 4.9 | 5,095,268 ± 581,971 | 66,352 ± 3,285 |

> Per-turn cache_read is similar (~40-60k); the headline gap comes from the **turn count**. Implication for smaller-context models: baseline at 73 turns is already large for a 200k-context model — the same workload could fail on Sonnet/Haiku, not just cost more. Topology B keeps loops short enough that cheaper models can do the same work.

## Wall-clock (indicative only — depends on Anthropic load)

Per-session `duration_ms` from each `claude -p` result event. Not reproducible across runs/days, but useful for spotting trends when other variables are held constant.

| session | duration mean | api_ms mean |
|---|---|---|
| a-mcp warmup | 178.2s ± 22.2s | 178.9s |
| a-mcp gen | 176.9s ± 27.6s | 176.7s |
| b-baseline | 327.0s ± 26.7s | 327.2s |

Script total wall-clock: **2107s** (35m 7s).

## Warmup — one-time outside-training tax

This is what a non-trained model pays to learn the MCP correctly via runtime docs. If MetaEngine were integrated into Claude Code's built-ins or the model's training, this row would be ~0.

| | output_tokens | cost USD | turns | summary written |
|---|---|---|---|---|
| a-mcp warmup | 12,549 ± 1,410 | $0.8972 ± $0.1093 | 8.4 ± 1.1 | 27,783 ± 2,635 chars |

## First-codebase total (for completeness)

What a user pays who runs MetaEngine *exactly once* and never again — warmup is not amortized. This is the worst-case framing.

- a-mcp (warmup + gen): 33,504 output tokens, $2.2773
- b-baseline:           26,435 output tokens, $3.7399
- Cost: 39.1% reduction — much smaller than steady-state because warmup is a one-shot.

## Output token decomposition (descriptive)

Authoritative `output_tokens` = visible text + tool_use input bytes (model-generated structured arguments) + thinking-block tokens (encrypted, billed). Per-event stream usage shows only the visible portion; the result event aggregates all three.

| session | visible (exact) | tool_input (≈chars/3.5) | thinking residual | sum (=auth) |
|---|---|---|---|---|
| a-mcp warmup | 273 ± 37 | 8,575 ± 785 | 3,701 ± 766 | 12,549 ± 1,410 |
| a-mcp gen | 97 ± 33 | 10,604 ± 149 | 10,254 ± 2,352 | 20,955 ± 2,389 |
| b-baseline | 5,163 ± 183 | 15,321 ± 1,710 | 5,951 ± 1,026 | 26,435 ± 2,872 |

## Per-run

| run | a-mcp warmup $ | a-mcp gen $ | a-mcp total $ | a-mcp output | baseline $ | baseline output | a-files | b-files |
|---|---|---|---|---|---|---|---|---|
| 001 | $0.7120 | $1.3589 | $2.0709 | 31,382 | $4.2399 | 28,239 | 71 | 71 |
| 002 | $0.9188 | $1.3852 | $2.3040 | 33,799 | $3.4220 | 25,671 | 71 | 71 |
| 003 | $0.9084 | $1.4574 | $2.3658 | 36,480 | $4.3633 | 30,468 | 71 | 71 |
| 004 | $0.9480 | $1.4130 | $2.3610 | 34,919 | $3.3483 | 23,976 | 71 | 71 |
| 005 | $0.9988 | $1.2860 | $2.2848 | 30,940 | $3.3259 | 23,821 | 71 | 71 |

## Caveats

- Authoritative numbers come from `claude -p`'s result event (`usage.output_tokens`, `total_cost_usd`). Per-event stream usage shows only visible-text output, which under-reports by excluding thinking and tool_use input bytes.
- The two-session methodology gives **exact** phase split: each session has its own result event total. The gen session has the warmup's knowledge brief in its user prompt (a few hundred input tokens) — slightly inflating gen vs an ideal trained-model case, in the honest direction.
- Output token decomposition (visible / tool_input / thinking) is *descriptive only* — the visible+tool_input parts are exact-per-message but tool_input tokens are estimated from chars (3.5/token). Thinking is the residual. The sum equals the authoritative total.
- A model trained natively on MetaEngine would have warmup ≈ 0 (it would already know the API). Steady-state approximates that.
- Failed/partial runs are *not* filtered. Pass rate alongside cost is the full picture.
- Wall-clock is reported as indicative only — depends on Anthropic server load and is not reproducible run-to-run.
