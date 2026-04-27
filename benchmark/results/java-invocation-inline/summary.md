# MetaEngine MCP — Benchmark Summary

> **These numbers are illustrations from one author's run on one spec on one day.** MetaEngine's whole philosophy is *try it yourself* — the harness is the deliverable, not the numbers. Reproduce in your own environment before quoting anything.

Runs requested: **5** per variant. Completed: a-mcp **5/5**, b-baseline **5/5**. Results: `<benchmark>/results/20260426-111807-java-inline`

**The headline is steady-state** — what each codebase costs once the model has been instructed on the MCP (or, equivalently, what it would cost if MetaEngine were in the model's training corpus). Warmup is reported separately as a one-time outside-training tax that wouldn't exist in an integrated world.

## Steady-state — per-codebase cost

This is what every codebase costs after the one-time warmup. If MetaEngine were in the model's training, this would be the *first*-codebase cost too.

| | output_tokens | cost USD | turns | cache_read | pass |
|---|---|---|---|---|---|
| a-mcp gen        |     19,680 | $ 1.3088 |  5.0 |     231,116 | 5/5 |
| b-baseline       |     25,526 | $ 3.4897 | 73.0 |   4,841,747 | 5/5 |
| **reduction**    | ** 22.9%** | ** 62.5%** | **14.6× fewer** | ** 95.2%** | — |

## Agent-loop efficiency (structural — independent of training)

The cache_read difference is structural: it comes from **tool topology**, not from the model knowing MetaEngine.

- **Topology A (Write loop):** Many small tool calls — one per output. Each turn re-reads cumulative context. cache_read accumulates ~quadratically with output count.
- **Topology B (batched single call):** One large structured tool input → all outputs in one tool_result. cache_read is bounded.

Any MCP that consolidates multi-output work into one call benefits — this isn't MetaEngine-specific. It's a generalizable design pattern.

| session | turns | cache_read tokens | per-turn |
|---|---|---|---|
| a-mcp warmup | 8.8 ± 1.9 | 320,900 ± 87,459 | 36,066 ± 3,206 |
| a-mcp gen | 5.0 ± 0.0 | 231,116 ± 4,105 | 46,223 ± 821 |
| b-baseline | 73.0 ± 0.0 | 4,841,747 ± 59,406 | 66,325 ± 814 |

> Per-turn cache_read is similar (~40-60k); the headline gap comes from the **turn count**. Implication for smaller-context models: baseline at 73 turns is already large for a 200k-context model — the same workload could fail on Sonnet/Haiku, not just cost more. Topology B keeps loops short enough that cheaper models can do the same work.

## Wall-clock (indicative only — depends on Anthropic load)

Per-session `duration_ms` from each `claude -p` result event. Not reproducible across runs/days, but useful for spotting trends when other variables are held constant.

| session | duration mean | api_ms mean |
|---|---|---|
| a-mcp warmup | 156.9s ± 16.0s | 157.6s |
| a-mcp gen | 162.2s ± 17.1s | 162.6s |
| b-baseline | 348.9s ± 12.7s | 349.1s |

Script total wall-clock: **714s** (11m 54s).

## Warmup — one-time outside-training tax

This is what a non-trained model pays to learn the MCP correctly via runtime docs. If MetaEngine were integrated into Claude Code's built-ins or the model's training, this row would be ~0.

| | output_tokens | cost USD | turns | summary written |
|---|---|---|---|---|
| a-mcp warmup | 10,817 ± 854 | $0.8312 ± $0.1066 | 8.8 ± 1.9 | 23,131 ± 1,606 chars |

## First-codebase total (for completeness)

What a user pays who runs MetaEngine *exactly once* and never again — warmup is not amortized. This is the worst-case framing.

- a-mcp (warmup + gen): 30,497 output tokens, $2.1400
- b-baseline:           25,526 output tokens, $3.4897
- Cost: 38.7% reduction — much smaller than steady-state because warmup is a one-shot.

## Output token decomposition (descriptive)

Authoritative `output_tokens` = visible text + tool_use input bytes (model-generated structured arguments) + thinking-block tokens (encrypted, billed). Per-event stream usage shows only the visible portion; the result event aggregates all three.

| session | visible (exact) | tool_input (≈chars/3.5) | thinking residual | sum (=auth) |
|---|---|---|---|---|
| a-mcp warmup | 307 ± 111 | 7,274 ± 514 | 3,236 ± 370 | 10,817 ± 854 |
| a-mcp gen | 117 ± 26 | 10,538 ± 125 | 9,025 ± 2,158 | 19,680 ± 2,075 |
| b-baseline | 4,980 ± 170 | 14,801 ± 543 | 5,744 ± 583 | 25,526 ± 1,051 |

## Per-run

| run | a-mcp warmup $ | a-mcp gen $ | a-mcp total $ | a-mcp output | baseline $ | baseline output | a-files | b-files |
|---|---|---|---|---|---|---|---|---|
| 001 | $0.9051 | $1.2045 | $2.1096 | 30,950 | $3.5577 | 26,739 | 71 | 71 |
| 002 | $0.6473 | $1.4296 | $2.0769 | 33,062 | $3.4025 | 24,124 | 71 | 71 |
| 003 | $0.8311 | $1.3264 | $2.1574 | 29,610 | $3.4869 | 25,160 | 71 | 71 |
| 004 | $0.8778 | $1.3165 | $2.1943 | 29,986 | $3.5367 | 26,391 | 71 | 71 |
| 005 | $0.8948 | $1.2670 | $2.1618 | 28,875 | $3.4645 | 25,214 | 71 | 71 |

## Per-run wall-clock

Per-session `duration_ms` from each `claude -p` result event, broken out per run to make trends visible (cross-session cache warming, parallel-batch effects, etc.). Indicative only — depends on Anthropic load on the day.

| run | a-mcp warmup s | a-mcp gen s | b-baseline s |
|---|---|---|---|
| 001 | 180 | 163 | 364 |
| 002 | 141 | 188 | 331 |
| 003 | 143 | 159 | 343 |
| 004 | 161 | 159 | 353 |
| 005 | 160 | 141 | 355 |

## Caveats

- Authoritative numbers come from `claude -p`'s result event (`usage.output_tokens`, `total_cost_usd`). Per-event stream usage shows only visible-text output, which under-reports by excluding thinking and tool_use input bytes.
- **`cost USD` is the would-be API cost** at Anthropic's published rates — a token-usage proxy that's comparable across users and models. It's NOT what a subscription user (Claude Max/Pro) actually pays — those plans are flat-rate. The dollar figure still reflects the *relative work* of each variant; tokens × price is the universal benchmark unit.
- The two-session methodology gives **exact** phase split: each session has its own result event total. The gen session has the warmup's knowledge brief in its user prompt (a few hundred input tokens) — slightly inflating gen vs an ideal trained-model case, in the honest direction.
- Output token decomposition (visible / tool_input / thinking) is *descriptive only* — the visible+tool_input parts are exact-per-message but tool_input tokens are estimated from chars (3.5/token). Thinking is the residual. The sum equals the authoritative total.
- A model trained natively on MetaEngine would have warmup ≈ 0 (it would already know the API). Steady-state approximates that.
- Failed/partial runs are *not* filtered. Pass rate alongside cost is the full picture.
- Wall-clock is reported as indicative only — depends on Anthropic server load and is not reproducible run-to-run.
