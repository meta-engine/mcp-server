# MetaEngine MCP — Benchmark Summary

> **These numbers are illustrations from one author's run on one spec on one day.** MetaEngine's whole philosophy is *try it yourself* — the harness is the deliverable, not the numbers. Reproduce in your own environment before quoting anything.

Runs requested: **5** per variant. Completed: a-mcp **5/5**, b-baseline **5/5**. Results: `results/20260426-041747-python`

**The headline is steady-state** — what each codebase costs once the model has been instructed on the MCP (or, equivalently, what it would cost if MetaEngine were in the model's training corpus). Warmup is reported separately as a one-time outside-training tax that wouldn't exist in an integrated world.

## Steady-state — per-codebase cost

This is what every codebase costs after the one-time warmup. If MetaEngine were in the model's training, this would be the *first*-codebase cost too.

| | output_tokens | cost USD | turns | cache_read | pass |
|---|---|---|---|---|---|
| a-mcp gen        |     23,131 | $ 1.6082 |  6.6 |     365,379 | 5/5 |
| b-baseline       |     23,236 | $ 1.8789 | 73.8 |   1,334,301 | 5/5 |
| **reduction**    | **  0.5%** | ** 14.4%** | **11.2× fewer** | ** 72.6%** | — |

## Agent-loop efficiency (structural — independent of training)

The cache_read difference is structural: it comes from **tool topology**, not from the model knowing MetaEngine.

- **Topology A (Write loop):** Many small tool calls — one per output. Each turn re-reads cumulative context. cache_read accumulates ~quadratically with output count.
- **Topology B (batched single call):** One large structured tool input → all outputs in one tool_result. cache_read is bounded.

Any MCP that consolidates multi-output work into one call benefits — this isn't MetaEngine-specific. It's a generalizable design pattern.

| session | turns | cache_read tokens | per-turn |
|---|---|---|---|
| a-mcp warmup | 15.0 ± 11.2 | 522,698 ± 328,632 | 36,391 ± 3,001 |
| a-mcp gen | 6.6 ± 3.0 | 365,379 ± 282,079 | 50,777 ± 13,055 |
| b-baseline | 73.8 ± 0.4 | 1,334,301 ± 1,871,399 | 18,035 ± 25,286 |

> Per-turn cache_read is similar (~40-60k); the headline gap comes from the **turn count**. Implication for smaller-context models: baseline at 73 turns is already large for a 200k-context model — the same workload could fail on Sonnet/Haiku, not just cost more. Topology B keeps loops short enough that cheaper models can do the same work.

## Wall-clock (indicative only — depends on Anthropic load)

Per-session `duration_ms` from each `claude -p` result event. Not reproducible across runs/days, but useful for spotting trends when other variables are held constant.

| session | duration mean | api_ms mean |
|---|---|---|
| a-mcp warmup | 190.2s ± 41.7s | 190.9s |
| a-mcp gen | 195.4s ± 45.6s | 195.3s |
| b-baseline | 206.0s ± 59.4s | 205.7s |

Script total wall-clock: **1890s** (31m 30s).

## Warmup — one-time outside-training tax

This is what a non-trained model pays to learn the MCP correctly via runtime docs. If MetaEngine were integrated into Claude Code's built-ins or the model's training, this row would be ~0.

| | output_tokens | cost USD | turns | summary written |
|---|---|---|---|---|
| a-mcp warmup | 12,601 ± 2,209 | $1.0838 ± $0.2884 | 15.0 ± 11.2 | 24,887 ± 1,919 chars |

## First-codebase total (for completeness)

What a user pays who runs MetaEngine *exactly once* and never again — warmup is not amortized. This is the worst-case framing.

- a-mcp (warmup + gen): 35,732 output tokens, $2.6919
- b-baseline:           23,236 output tokens, $1.8789
- Cost: -43.3% reduction — much smaller than steady-state because warmup is a one-shot.

## Output token decomposition (descriptive)

Authoritative `output_tokens` = visible text + tool_use input bytes (model-generated structured arguments) + thinking-block tokens (encrypted, billed). Per-event stream usage shows only the visible portion; the result event aggregates all three.

| session | visible (exact) | tool_input (≈chars/3.5) | thinking residual | sum (=auth) |
|---|---|---|---|---|
| a-mcp warmup | 408 ± 242 | 7,987 ± 648 | 4,207 ± 1,521 | 12,601 ± 2,209 |
| a-mcp gen | 187 ± 150 | 11,175 ± 1,860 | 11,769 ± 3,232 | 23,131 ± 4,102 |
| b-baseline | 1,256 ± 2,172 | 13,563 ± 1,006 | 8,418 ± 2,111 | 23,236 ± 1,570 |

## Per-run

| run | a-mcp warmup $ | a-mcp gen $ | a-mcp total $ | a-mcp output | baseline $ | baseline output | a-files | b-files |
|---|---|---|---|---|---|---|---|---|
| 001 | $1.0105 | $2.1758 | $3.1863 | 40,804 | $3.3044 | 22,772 | 71 | 71 |
| 002 | $1.5765 | $1.2849 | $2.8613 | 35,055 | $1.3446 | 24,907 | 71 | 71 |
| 003 | $1.0565 | $1.6011 | $2.6576 | 38,909 | $1.3436 | 24,543 | 71 | 71 |
| 004 | $0.8293 | $1.4390 | $2.2683 | 30,327 | $1.2869 | 22,978 | 71 | 71 |
| 005 | $0.9459 | $1.5402 | $2.4862 | 33,566 | $2.1152 | 20,982 | 71 | 71 |

## Caveats

- Authoritative numbers come from `claude -p`'s result event (`usage.output_tokens`, `total_cost_usd`). Per-event stream usage shows only visible-text output, which under-reports by excluding thinking and tool_use input bytes.
- The two-session methodology gives **exact** phase split: each session has its own result event total. The gen session has the warmup's knowledge brief in its user prompt (a few hundred input tokens) — slightly inflating gen vs an ideal trained-model case, in the honest direction.
- Output token decomposition (visible / tool_input / thinking) is *descriptive only* — the visible+tool_input parts are exact-per-message but tool_input tokens are estimated from chars (3.5/token). Thinking is the residual. The sum equals the authoritative total.
- A model trained natively on MetaEngine would have warmup ≈ 0 (it would already know the API). Steady-state approximates that.
- Failed/partial runs are *not* filtered. Pass rate alongside cost is the full picture.
- Wall-clock is reported as indicative only — depends on Anthropic server load and is not reproducible run-to-run.
