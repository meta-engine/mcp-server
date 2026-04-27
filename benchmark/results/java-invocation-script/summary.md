# MetaEngine MCP — Benchmark Summary

> **These numbers are illustrations from one author's run on one spec on one day.** MetaEngine's whole philosophy is *try it yourself* — the harness is the deliverable, not the numbers. Reproduce in your own environment before quoting anything.

Runs requested: **5** per variant. Completed: a-mcp **5/5**, b-baseline **5/5**. Results: `<benchmark>/results/20260426-113002-java-script`

**The headline is steady-state** — what each codebase costs once the model has been instructed on the MCP (or, equivalently, what it would cost if MetaEngine were in the model's training corpus). Warmup is reported separately as a one-time outside-training tax that wouldn't exist in an integrated world.

## Steady-state — per-codebase cost

This is what every codebase costs after the one-time warmup. If MetaEngine were in the model's training, this would be the *first*-codebase cost too.

| | output_tokens | cost USD | turns | cache_read | pass |
|---|---|---|---|---|---|
| a-mcp gen        |      5,779 | $ 0.8676 |  8.6 |     368,779 | 5/5 |
| b-baseline       |     24,050 | $ 3.4123 | 73.0 |   4,785,867 | 5/5 |
| **reduction**    | ** 76.0%** | ** 74.6%** | **8.5× fewer** | ** 92.3%** | — |

## Agent-loop efficiency (structural — independent of training)

The cache_read difference is structural: it comes from **tool topology**, not from the model knowing MetaEngine.

- **Topology A (Write loop):** Many small tool calls — one per output. Each turn re-reads cumulative context. cache_read accumulates ~quadratically with output count.
- **Topology B (batched single call):** One large structured tool input → all outputs in one tool_result. cache_read is bounded.

Any MCP that consolidates multi-output work into one call benefits — this isn't MetaEngine-specific. It's a generalizable design pattern.

| session | turns | cache_read tokens | per-turn |
|---|---|---|---|
| a-mcp warmup | 9.2 ± 0.8 | 343,133 ± 42,279 | 37,213 ± 1,623 |
| a-mcp gen | 8.6 ± 2.6 | 368,779 ± 93,841 | 43,490 ± 2,893 |
| b-baseline | 73.0 ± 0.0 | 4,785,867 ± 53,624 | 65,560 ± 735 |

> Per-turn cache_read is similar (~40-60k); the headline gap comes from the **turn count**. Implication for smaller-context models: baseline at 73 turns is already large for a 200k-context model — the same workload could fail on Sonnet/Haiku, not just cost more. Topology B keeps loops short enough that cheaper models can do the same work.

## Wall-clock (indicative only — depends on Anthropic load)

Per-session `duration_ms` from each `claude -p` result event. Not reproducible across runs/days, but useful for spotting trends when other variables are held constant.

| session | duration mean | api_ms mean |
|---|---|---|
| a-mcp warmup | 155.6s ± 19.6s | 157.3s |
| a-mcp gen | 74.8s ± 10.5s | 75.0s |
| b-baseline | 325.2s ± 33.7s | 325.5s |

Script total wall-clock: **615s** (10m 15s).

## Warmup — one-time outside-training tax

This is what a non-trained model pays to learn the MCP correctly via runtime docs. If MetaEngine were integrated into Claude Code's built-ins or the model's training, this row would be ~0.

| | output_tokens | cost USD | turns | summary written |
|---|---|---|---|---|
| a-mcp warmup | 10,304 ± 823 | $0.8855 ± $0.0842 | 9.2 ± 0.8 | 22,188 ± 1,686 chars |

## First-codebase total (for completeness)

What a user pays who runs MetaEngine *exactly once* and never again — warmup is not amortized. This is the worst-case framing.

- a-mcp (warmup + gen): 16,083 output tokens, $1.7531
- b-baseline:           24,050 output tokens, $3.4123
- Cost: 48.6% reduction — much smaller than steady-state because warmup is a one-shot.

## Output token decomposition (descriptive)

Authoritative `output_tokens` = visible text + tool_use input bytes (model-generated structured arguments) + thinking-block tokens (encrypted, billed). Per-event stream usage shows only the visible portion; the result event aggregates all three.

| session | visible (exact) | tool_input (≈chars/3.5) | thinking residual | sum (=auth) |
|---|---|---|---|---|
| a-mcp warmup | 290 ± 28 | 6,962 ± 522 | 3,051 ± 378 | 10,304 ± 823 |
| a-mcp gen | 301 ± 142 | 2,193 ± 460 | 3,285 ± 1,398 | 5,779 ± 868 |
| b-baseline | 4,894 ± 211 | 13,653 ± 1,169 | 5,504 ± 329 | 24,050 ± 1,418 |

## Per-run

| run | a-mcp warmup $ | a-mcp gen $ | a-mcp total $ | a-mcp output | baseline $ | baseline output | a-files | b-files |
|---|---|---|---|---|---|---|---|---|
| 001 | $0.7961 | $0.8052 | $1.6013 | 15,674 | $3.4200 | 24,305 | 71 | 71 |
| 002 | $0.8098 | $0.8265 | $1.6363 | 15,539 | $3.3874 | 23,574 | 71 | 71 |
| 003 | $0.9638 | $0.9824 | $1.9462 | 16,416 | $3.3442 | 22,736 | 71 | 71 |
| 004 | $0.9777 | $0.7543 | $1.7319 | 16,366 | $3.5328 | 26,374 | 71 | 71 |
| 005 | $0.8802 | $0.9698 | $1.8500 | 16,420 | $3.3770 | 23,263 | 71 | 71 |

## Per-run wall-clock

Per-session `duration_ms` from each `claude -p` result event, broken out per run to make trends visible (cross-session cache warming, parallel-batch effects, etc.). Indicative only — depends on Anthropic load on the day.

| run | a-mcp warmup s | a-mcp gen s | b-baseline s |
|---|---|---|---|
| 001 | 145 | 74 | 304 |
| 002 | 156 | 76 | 291 |
| 003 | 158 | 83 | 308 |
| 004 | 186 | 57 | 364 |
| 005 | 133 | 83 | 359 |

## Caveats

- Authoritative numbers come from `claude -p`'s result event (`usage.output_tokens`, `total_cost_usd`). Per-event stream usage shows only visible-text output, which under-reports by excluding thinking and tool_use input bytes.
- **`cost USD` is the would-be API cost** at Anthropic's published rates — a token-usage proxy that's comparable across users and models. It's NOT what a subscription user (Claude Max/Pro) actually pays — those plans are flat-rate. The dollar figure still reflects the *relative work* of each variant; tokens × price is the universal benchmark unit.
- The two-session methodology gives **exact** phase split: each session has its own result event total. The gen session has the warmup's knowledge brief in its user prompt (a few hundred input tokens) — slightly inflating gen vs an ideal trained-model case, in the honest direction.
- Output token decomposition (visible / tool_input / thinking) is *descriptive only* — the visible+tool_input parts are exact-per-message but tool_input tokens are estimated from chars (3.5/token). Thinking is the residual. The sum equals the authoritative total.
- A model trained natively on MetaEngine would have warmup ≈ 0 (it would already know the API). Steady-state approximates that.
- Failed/partial runs are *not* filtered. Pass rate alongside cost is the full picture.
- Wall-clock is reported as indicative only — depends on Anthropic server load and is not reproducible run-to-run.
