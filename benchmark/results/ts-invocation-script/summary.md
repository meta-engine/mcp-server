# MetaEngine MCP — Benchmark Summary

> **These numbers are illustrations from one author's run on one spec on one day.** MetaEngine's whole philosophy is *try it yourself* — the harness is the deliverable, not the numbers. Reproduce in your own environment before quoting anything.

Runs requested: **5** per variant. Completed: a-mcp **5/5**, b-baseline **5/5**. Results: `<benchmark>/results/20260426-105828-typescript-script`

**The headline is steady-state** — what each codebase costs once the model has been instructed on the MCP (or, equivalently, what it would cost if MetaEngine were in the model's training corpus). Warmup is reported separately as a one-time outside-training tax that wouldn't exist in an integrated world.

## Steady-state — per-codebase cost

This is what every codebase costs after the one-time warmup. If MetaEngine were in the model's training, this would be the *first*-codebase cost too.

| | output_tokens | cost USD | turns | cache_read | pass |
|---|---|---|---|---|---|
| a-mcp gen        |      4,691 | $ 0.8935 |  6.8 |     307,669 | 4/5 |
| b-baseline       |     21,353 | $ 3.2661 | 73.0 |   4,654,118 | 5/5 |
| **reduction**    | ** 78.0%** | ** 72.6%** | **10.7× fewer** | ** 93.4%** | — |

## Agent-loop efficiency (structural — independent of training)

The cache_read difference is structural: it comes from **tool topology**, not from the model knowing MetaEngine.

- **Topology A (Write loop):** Many small tool calls — one per output. Each turn re-reads cumulative context. cache_read accumulates ~quadratically with output count.
- **Topology B (batched single call):** One large structured tool input → all outputs in one tool_result. cache_read is bounded.

Any MCP that consolidates multi-output work into one call benefits — this isn't MetaEngine-specific. It's a generalizable design pattern.

| session | turns | cache_read tokens | per-turn |
|---|---|---|---|
| a-mcp warmup | 8.8 ± 1.3 | 332,208 ± 72,364 | 37,410 ± 3,202 |
| a-mcp gen | 6.8 ± 1.8 | 307,669 ± 63,798 | 45,661 ± 2,227 |
| b-baseline | 73.0 ± 0.0 | 4,654,118 ± 33,684 | 63,755 ± 461 |

> Per-turn cache_read is similar (~40-60k); the headline gap comes from the **turn count**. Implication for smaller-context models: baseline at 73 turns is already large for a 200k-context model — the same workload could fail on Sonnet/Haiku, not just cost more. Topology B keeps loops short enough that cheaper models can do the same work.

## Wall-clock (indicative only — depends on Anthropic load)

Per-session `duration_ms` from each `claude -p` result event. Not reproducible across runs/days, but useful for spotting trends when other variables are held constant.

| session | duration mean | api_ms mean |
|---|---|---|
| a-mcp warmup | 159.8s ± 15.0s | 161.2s |
| a-mcp gen | 70.2s ± 15.9s | 70.7s |
| b-baseline | 290.5s ± 13.4s | 291.0s |

Script total wall-clock: **576s** (9m 36s).

## Warmup — one-time outside-training tax

This is what a non-trained model pays to learn the MCP correctly via runtime docs. If MetaEngine were integrated into Claude Code's built-ins or the model's training, this row would be ~0.

| | output_tokens | cost USD | turns | summary written |
|---|---|---|---|---|
| a-mcp warmup | 11,283 ± 1,271 | $0.9099 ± $0.1086 | 8.8 ± 1.3 | 24,384 ± 2,502 chars |

## First-codebase total (for completeness)

What a user pays who runs MetaEngine *exactly once* and never again — warmup is not amortized. This is the worst-case framing.

- a-mcp (warmup + gen): 15,974 output tokens, $1.8034
- b-baseline:           21,353 output tokens, $3.2661
- Cost: 44.8% reduction — much smaller than steady-state because warmup is a one-shot.

## Output token decomposition (descriptive)

Authoritative `output_tokens` = visible text + tool_use input bytes (model-generated structured arguments) + thinking-block tokens (encrypted, billed). Per-event stream usage shows only the visible portion; the result event aggregates all three.

| session | visible (exact) | tool_input (≈chars/3.5) | thinking residual | sum (=auth) |
|---|---|---|---|---|
| a-mcp warmup | 284 ± 27 | 7,648 ± 790 | 3,351 ± 510 | 11,283 ± 1,271 |
| a-mcp gen | 189 ± 102 | 1,671 ± 189 | 2,831 ± 1,177 | 4,691 ± 1,071 |
| b-baseline | 5,061 ± 13 | 10,043 ± 53 | 6,249 ± 490 | 21,353 ± 472 |

## Per-run

| run | a-mcp warmup $ | a-mcp gen $ | a-mcp total $ | a-mcp output | baseline $ | baseline output | a-files | b-files |
|---|---|---|---|---|---|---|---|---|
| 001 | $0.8959 | $0.9102 | $1.8061 | 14,227 | $3.2700 | 21,227 | 71 | 71 |
| 002 | $1.0243 | $0.9796 | $2.0039 | 18,689 | $3.2736 | 21,396 | 71 | 71 |
| 003 | $0.9931 | $0.8554 | $1.8485 | 14,409 | $3.2123 | 20,630 | 71 | 71 |
| 004 | $0.8891 | $0.7632 | $1.6523 | 15,759 | $3.2941 | 21,870 | 71 | 71 |
| 005 | $0.7469 | $0.9592 | $1.7061 | 16,784 | $3.2805 | 21,643 | 71 | 71 |

## Per-run wall-clock

Per-session `duration_ms` from each `claude -p` result event, broken out per run to make trends visible (cross-session cache warming, parallel-batch effects, etc.). Indicative only — depends on Anthropic load on the day.

| run | a-mcp warmup s | a-mcp gen s | b-baseline s |
|---|---|---|---|
| 001 | 147 | 58 | 294 |
| 002 | 182 | 94 | 291 |
| 003 | 163 | 54 | 269 |
| 004 | 162 | 68 | 294 |
| 005 | 145 | 77 | 305 |

## Caveats

- Authoritative numbers come from `claude -p`'s result event (`usage.output_tokens`, `total_cost_usd`). Per-event stream usage shows only visible-text output, which under-reports by excluding thinking and tool_use input bytes.
- **`cost USD` is the would-be API cost** at Anthropic's published rates — a token-usage proxy that's comparable across users and models. It's NOT what a subscription user (Claude Max/Pro) actually pays — those plans are flat-rate. The dollar figure still reflects the *relative work* of each variant; tokens × price is the universal benchmark unit.
- The two-session methodology gives **exact** phase split: each session has its own result event total. The gen session has the warmup's knowledge brief in its user prompt (a few hundred input tokens) — slightly inflating gen vs an ideal trained-model case, in the honest direction.
- Output token decomposition (visible / tool_input / thinking) is *descriptive only* — the visible+tool_input parts are exact-per-message but tool_input tokens are estimated from chars (3.5/token). Thinking is the residual. The sum equals the authoritative total.
- A model trained natively on MetaEngine would have warmup ≈ 0 (it would already know the API). Steady-state approximates that.
- Failed/partial runs are *not* filtered. Pass rate alongside cost is the full picture.
- Wall-clock is reported as indicative only — depends on Anthropic server load and is not reproducible run-to-run.
