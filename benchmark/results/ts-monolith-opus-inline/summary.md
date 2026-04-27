# MetaEngine MCP — Benchmark Summary

> **These numbers are illustrations from one author's run on one spec on one day.** MetaEngine's whole philosophy is *try it yourself* — the harness is the deliverable, not the numbers. Reproduce in your own environment before quoting anything.

Runs requested: **5** per variant. Completed: a-mcp **5/5**, b-baseline **5/5**. Results: `<benchmark>/results/20260426-202822-typescript-inline-monolith`

**The headline is steady-state** — what each codebase costs once the model has been instructed on the MCP (or, equivalently, what it would cost if MetaEngine were in the model's training corpus). Warmup is reported separately as a one-time outside-training tax that wouldn't exist in an integrated world.

## Steady-state — per-codebase cost

This is what every codebase costs after the one-time warmup. If MetaEngine were in the model's training, this would be the *first*-codebase cost too.

| | output_tokens | cost USD | turns | cache_read | pass |
|---|---|---|---|---|---|
| a-mcp gen        |     20,410 | $ 1.3618 |  5.2 |     243,271 | 5/5 |
| b-baseline       |     25,820 | $ 3.2402 | 72.6 |   3,935,365 | 5/5 |
| **reduction**    | ** 21.0%** | ** 58.0%** | **14.0× fewer** | ** 93.8%** | — |

## Agent-loop efficiency (structural — independent of training)

The cache_read difference is structural: it comes from **tool topology**, not from the model knowing MetaEngine.

- **Topology A (Write loop):** Many small tool calls — one per output. Each turn re-reads cumulative context. cache_read accumulates ~quadratically with output count.
- **Topology B (batched single call):** One large structured tool input → all outputs in one tool_result. cache_read is bounded.

Any MCP that consolidates multi-output work into one call benefits — this isn't MetaEngine-specific. It's a generalizable design pattern.

| session | turns | cache_read tokens | per-turn |
|---|---|---|---|
| a-mcp warmup | 9.0 ± 1.0 | 331,404 ± 62,212 | 36,569 ± 2,964 |
| a-mcp gen | 5.2 ± 0.4 | 243,271 ± 34,583 | 46,630 ± 2,697 |
| b-baseline | 72.6 ± 4.7 | 3,935,365 ± 2,010,402 | 53,710 ± 26,769 |

> Per-turn cache_read is similar (~40-60k); the headline gap comes from the **turn count**. Implication for smaller-context models: baseline at 73 turns is already large for a 200k-context model — the same workload could fail on Sonnet/Haiku, not just cost more. Topology B keeps loops short enough that cheaper models can do the same work.

## Wall-clock (indicative only — depends on Anthropic load)

Per-session `duration_ms` from each `claude -p` result event. Not reproducible across runs/days, but useful for spotting trends when other variables are held constant.

| session | duration mean | api_ms mean |
|---|---|---|
| a-mcp warmup | 158.5s ± 10.3s | 159.1s |
| a-mcp gen | 186.7s ± 21.9s | 182.8s |
| b-baseline | 315.9s ± 49.4s | 316.1s |

Script total wall-clock: **2101s** (35m 1s).

## Warmup — one-time outside-training tax

This is what a non-trained model pays to learn the MCP correctly via runtime docs. If MetaEngine were integrated into Claude Code's built-ins or the model's training, this row would be ~0.

| | output_tokens | cost USD | turns | summary written |
|---|---|---|---|---|
| a-mcp warmup | 11,259 ± 873 | $0.9012 ± $0.0127 | 9.0 ± 1.0 | 23,798 ± 1,909 chars |

## First-codebase total (for completeness)

What a user pays who runs MetaEngine *exactly once* and never again — warmup is not amortized. This is the worst-case framing.

- a-mcp (warmup + gen): 31,669 output tokens, $2.2629
- b-baseline:           25,820 output tokens, $3.2402
- Cost: 30.2% reduction — much smaller than steady-state because warmup is a one-shot.

## Output token decomposition (descriptive)

Authoritative `output_tokens` = visible text + tool_use input bytes (model-generated structured arguments) + thinking-block tokens (encrypted, billed). Per-event stream usage shows only the visible portion; the result event aggregates all three.

| session | visible (exact) | tool_input (≈chars/3.5) | thinking residual | sum (=auth) |
|---|---|---|---|---|
| a-mcp warmup | 272 ± 33 | 7,547 ± 588 | 3,441 ± 456 | 11,259 ± 873 |
| a-mcp gen | 116 ± 40 | 8,665 ± 41 | 11,629 ± 1,788 | 20,410 ± 1,779 |
| b-baseline | 3,832 ± 1,925 | 10,665 ± 1,602 | 11,322 ± 4,402 | 25,820 ± 2,393 |

## Per-run

| run | a-mcp warmup $ | a-mcp gen $ | a-mcp total $ | a-mcp output | baseline $ | baseline output | a-files | b-files |
|---|---|---|---|---|---|---|---|---|
| 001 | $0.9063 | $1.3556 | $2.2619 | 31,058 | $3.2569 | 22,914 | 68 | 68 |
| 002 | $0.8856 | $1.3337 | $2.2193 | 30,716 | $3.3718 | 24,982 | 68 | 68 |
| 003 | $0.8904 | $1.4350 | $2.3254 | 33,609 | $4.1152 | 27,037 | 68 | 68 |
| 004 | $0.9162 | $1.3014 | $2.2176 | 30,765 | $2.1219 | 29,214 | 68 | 68 |
| 005 | $0.9074 | $1.3831 | $2.2905 | 32,198 | $3.3353 | 24,951 | 68 | 68 |

## Per-run wall-clock

Per-session `duration_ms` from each `claude -p` result event, broken out per run to make trends visible (cross-session cache warming, parallel-batch effects, etc.). Indicative only — depends on Anthropic load on the day.

| run | a-mcp warmup s | a-mcp gen s | b-baseline s |
|---|---|---|---|
| 001 | 161 | 178 | 314 |
| 002 | 153 | 186 | 322 |
| 003 | 144 | 225 | 353 |
| 004 | 171 | 173 | 234 |
| 005 | 163 | 172 | 357 |

## Caveats

- Authoritative numbers come from `claude -p`'s result event (`usage.output_tokens`, `total_cost_usd`). Per-event stream usage shows only visible-text output, which under-reports by excluding thinking and tool_use input bytes.
- **`cost USD` is the would-be API cost** at Anthropic's published rates — a token-usage proxy that's comparable across users and models. It's NOT what a subscription user (Claude Max/Pro) actually pays — those plans are flat-rate. The dollar figure still reflects the *relative work* of each variant; tokens × price is the universal benchmark unit.
- The two-session methodology gives **exact** phase split: each session has its own result event total. The gen session has the warmup's knowledge brief in its user prompt (a few hundred input tokens) — slightly inflating gen vs an ideal trained-model case, in the honest direction.
- Output token decomposition (visible / tool_input / thinking) is *descriptive only* — the visible+tool_input parts are exact-per-message but tool_input tokens are estimated from chars (3.5/token). Thinking is the residual. The sum equals the authoritative total.
- A model trained natively on MetaEngine would have warmup ≈ 0 (it would already know the API). Steady-state approximates that.
- Failed/partial runs are *not* filtered. Pass rate alongside cost is the full picture.
- Wall-clock is reported as indicative only — depends on Anthropic server load and is not reproducible run-to-run.
- Data collected on Opus 4.7 (1M-context). Within a few-day window we assume Anthropic-side model behavior is stable; cross-arm and cross-language comparisons inside that window are apples-to-apples. Re-runs after a model update are out of scope for token-cost reasons (not a cross-model benchmark).
