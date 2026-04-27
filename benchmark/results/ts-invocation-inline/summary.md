# MetaEngine MCP — Benchmark Summary

> **These numbers are illustrations from one author's run on one spec on one day.** MetaEngine's whole philosophy is *try it yourself* — the harness is the deliverable, not the numbers. Reproduce in your own environment before quoting anything.

Runs requested: **5** per variant. Completed: a-mcp **5/5**, b-baseline **5/5**. Results: `<benchmark>/results/20260426-103402-typescript-inline`

**The headline is steady-state** — what each codebase costs once the model has been instructed on the MCP (or, equivalently, what it would cost if MetaEngine were in the model's training corpus). Warmup is reported separately as a one-time outside-training tax that wouldn't exist in an integrated world.

## Steady-state — per-codebase cost

This is what every codebase costs after the one-time warmup. If MetaEngine were in the model's training, this would be the *first*-codebase cost too.

| | output_tokens | cost USD | turns | cache_read | pass |
|---|---|---|---|---|---|
| a-mcp gen        |     17,913 | $ 1.3132 |  5.0 |     219,408 | 5/5 |
| b-baseline       |     20,198 | $ 2.8010 | 73.0 |   3,776,774 | 5/5 |
| **reduction**    | ** 11.3%** | ** 53.1%** | **14.6× fewer** | ** 94.2%** | — |

## Agent-loop efficiency (structural — independent of training)

The cache_read difference is structural: it comes from **tool topology**, not from the model knowing MetaEngine.

- **Topology A (Write loop):** Many small tool calls — one per output. Each turn re-reads cumulative context. cache_read accumulates ~quadratically with output count.
- **Topology B (batched single call):** One large structured tool input → all outputs in one tool_result. cache_read is bounded.

Any MCP that consolidates multi-output work into one call benefits — this isn't MetaEngine-specific. It's a generalizable design pattern.

| session | turns | cache_read tokens | per-turn |
|---|---|---|---|
| a-mcp warmup | 6.8 ± 1.3 | 209,587 ± 67,694 | 30,388 ± 4,455 |
| a-mcp gen | 5.0 ± 0.0 | 219,408 ± 10,967 | 43,882 ± 2,193 |
| b-baseline | 73.0 ± 0.0 | 3,776,774 ± 1,815,074 | 51,737 ± 24,864 |

> Per-turn cache_read is similar (~40-60k); the headline gap comes from the **turn count**. Implication for smaller-context models: baseline at 73 turns is already large for a 200k-context model — the same workload could fail on Sonnet/Haiku, not just cost more. Topology B keeps loops short enough that cheaper models can do the same work.

## Wall-clock (indicative only — depends on Anthropic load)

Per-session `duration_ms` from each `claude -p` result event. Not reproducible across runs/days, but useful for spotting trends when other variables are held constant.

| session | duration mean | api_ms mean |
|---|---|---|
| a-mcp warmup | 148.0s ± 18.4s | 148.9s |
| a-mcp gen | 146.2s ± 20.4s | 147.0s |
| b-baseline | 268.6s ± 74.8s | 268.6s |

Script total wall-clock: **654s** (10m 54s).

## Warmup — one-time outside-training tax

This is what a non-trained model pays to learn the MCP correctly via runtime docs. If MetaEngine were integrated into Claude Code's built-ins or the model's training, this row would be ~0.

| | output_tokens | cost USD | turns | summary written |
|---|---|---|---|---|
| a-mcp warmup | 9,999 ± 1,185 | $0.8867 ± $0.1781 | 6.8 ± 1.3 | 22,116 ± 2,115 chars |

## First-codebase total (for completeness)

What a user pays who runs MetaEngine *exactly once* and never again — warmup is not amortized. This is the worst-case framing.

- a-mcp (warmup + gen): 27,912 output tokens, $2.1999
- b-baseline:           20,198 output tokens, $2.8010
- Cost: 21.5% reduction — much smaller than steady-state because warmup is a one-shot.

## Output token decomposition (descriptive)

Authoritative `output_tokens` = visible text + tool_use input bytes (model-generated structured arguments) + thinking-block tokens (encrypted, billed). Per-event stream usage shows only the visible portion; the result event aggregates all three.

| session | visible (exact) | tool_input (≈chars/3.5) | thinking residual | sum (=auth) |
|---|---|---|---|---|
| a-mcp warmup | 182 ± 79 | 6,893 ± 660 | 2,924 ± 481 | 9,999 ± 1,185 |
| a-mcp gen | 117 ± 10 | 9,950 ± 4 | 7,846 ± 1,965 | 17,913 ± 1,956 |
| b-baseline | 4,162 ± 2,029 | 10,368 ± 243 | 5,668 ± 1,397 | 20,198 ± 914 |

## Per-run

| run | a-mcp warmup $ | a-mcp gen $ | a-mcp total $ | a-mcp output | baseline $ | baseline output | a-files | b-files |
|---|---|---|---|---|---|---|---|---|
| 001 | $0.9054 | $1.3675 | $2.2729 | 31,098 | $3.2445 | 21,261 | 71 | 71 |
| 002 | $1.1618 | $1.3814 | $2.5431 | 29,291 | $3.1814 | 20,234 | 71 | 71 |
| 003 | $0.8445 | $1.2323 | $2.0768 | 26,501 | $1.1867 | 18,738 | 71 | 71 |
| 004 | $0.8541 | $1.2788 | $2.1328 | 27,777 | $3.1992 | 20,454 | 71 | 71 |
| 005 | $0.6675 | $1.3062 | $1.9737 | 24,894 | $3.1933 | 20,302 | 71 | 71 |

## Per-run wall-clock

Per-session `duration_ms` from each `claude -p` result event, broken out per run to make trends visible (cross-session cache warming, parallel-batch effects, etc.). Indicative only — depends on Anthropic load on the day.

| run | a-mcp warmup s | a-mcp gen s | b-baseline s |
|---|---|---|---|
| 001 | 151 | 179 | 279 |
| 002 | 176 | 139 | 275 |
| 003 | 150 | 131 | 154 |
| 004 | 128 | 152 | 364 |
| 005 | 135 | 130 | 271 |

## Caveats

- Authoritative numbers come from `claude -p`'s result event (`usage.output_tokens`, `total_cost_usd`). Per-event stream usage shows only visible-text output, which under-reports by excluding thinking and tool_use input bytes.
- **`cost USD` is the would-be API cost** at Anthropic's published rates — a token-usage proxy that's comparable across users and models. It's NOT what a subscription user (Claude Max/Pro) actually pays — those plans are flat-rate. The dollar figure still reflects the *relative work* of each variant; tokens × price is the universal benchmark unit.
- The two-session methodology gives **exact** phase split: each session has its own result event total. The gen session has the warmup's knowledge brief in its user prompt (a few hundred input tokens) — slightly inflating gen vs an ideal trained-model case, in the honest direction.
- Output token decomposition (visible / tool_input / thinking) is *descriptive only* — the visible+tool_input parts are exact-per-message but tool_input tokens are estimated from chars (3.5/token). Thinking is the residual. The sum equals the authoritative total.
- A model trained natively on MetaEngine would have warmup ≈ 0 (it would already know the API). Steady-state approximates that.
- Failed/partial runs are *not* filtered. Pass rate alongside cost is the full picture.
- Wall-clock is reported as indicative only — depends on Anthropic server load and is not reproducible run-to-run.
