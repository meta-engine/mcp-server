# MetaEngine MCP — Benchmark Summary

> **These numbers are illustrations from one author's run on one spec on one day.** MetaEngine's whole philosophy is *try it yourself* — the harness is the deliverable, not the numbers. Reproduce in your own environment before quoting anything.

Runs requested: **5** per variant. Completed: a-mcp **5/5**, b-baseline **5/5**. Results: `<benchmark>/results/20260426-115000-python-script`

**The headline is steady-state** — what each codebase costs once the model has been instructed on the MCP (or, equivalently, what it would cost if MetaEngine were in the model's training corpus). Warmup is reported separately as a one-time outside-training tax that wouldn't exist in an integrated world.

## Steady-state — per-codebase cost

This is what every codebase costs after the one-time warmup. If MetaEngine were in the model's training, this would be the *first*-codebase cost too.

| | output_tokens | cost USD | turns | cache_read | pass |
|---|---|---|---|---|---|
| a-mcp gen        |      5,458 | $ 0.9200 |  9.2 |     420,442 | 5/5 |
| b-baseline       |     23,560 | $ 1.8701 | 75.0 |   1,600,372 | 5/5 |
| **reduction**    | ** 76.8%** | ** 50.8%** | **8.2× fewer** | ** 73.7%** | — |

## Agent-loop efficiency (structural — independent of training)

The cache_read difference is structural: it comes from **tool topology**, not from the model knowing MetaEngine.

- **Topology A (Write loop):** Many small tool calls — one per output. Each turn re-reads cumulative context. cache_read accumulates ~quadratically with output count.
- **Topology B (batched single call):** One large structured tool input → all outputs in one tool_result. cache_read is bounded.

Any MCP that consolidates multi-output work into one call benefits — this isn't MetaEngine-specific. It's a generalizable design pattern.

| session | turns | cache_read tokens | per-turn |
|---|---|---|---|
| a-mcp warmup | 11.8 ± 4.8 | 502,004 ± 301,052 | 40,576 ± 6,256 |
| a-mcp gen | 9.2 ± 2.8 | 420,442 ± 97,517 | 46,495 ± 4,384 |
| b-baseline | 75.0 ± 4.5 | 1,600,372 ± 2,307,119 | 20,032 ± 27,377 |

> Per-turn cache_read is similar (~40-60k); the headline gap comes from the **turn count**. Implication for smaller-context models: baseline at 73 turns is already large for a 200k-context model — the same workload could fail on Sonnet/Haiku, not just cost more. Topology B keeps loops short enough that cheaper models can do the same work.

## Wall-clock (indicative only — depends on Anthropic load)

Per-session `duration_ms` from each `claude -p` result event. Not reproducible across runs/days, but useful for spotting trends when other variables are held constant.

| session | duration mean | api_ms mean |
|---|---|---|
| a-mcp warmup | 248.5s ± 140.8s | 249.2s |
| a-mcp gen | 74.5s ± 18.4s | 74.7s |
| b-baseline | 222.2s ± 84.0s | 222.9s |

Script total wall-clock: **729s** (12m 9s).

## Warmup — one-time outside-training tax

This is what a non-trained model pays to learn the MCP correctly via runtime docs. If MetaEngine were integrated into Claude Code's built-ins or the model's training, this row would be ~0.

| | output_tokens | cost USD | turns | summary written |
|---|---|---|---|---|
| a-mcp warmup | 11,058 ± 1,040 | $0.9696 ± $0.1815 | 11.8 ± 4.8 | 22,231 ± 1,906 chars |

## First-codebase total (for completeness)

What a user pays who runs MetaEngine *exactly once* and never again — warmup is not amortized. This is the worst-case framing.

- a-mcp (warmup + gen): 16,516 output tokens, $1.8897
- b-baseline:           23,560 output tokens, $1.8701
- Cost: -1.0% reduction — much smaller than steady-state because warmup is a one-shot.

## Output token decomposition (descriptive)

Authoritative `output_tokens` = visible text + tool_use input bytes (model-generated structured arguments) + thinking-block tokens (encrypted, billed). Per-event stream usage shows only the visible portion; the result event aggregates all three.

| session | visible (exact) | tool_input (≈chars/3.5) | thinking residual | sum (=auth) |
|---|---|---|---|---|
| a-mcp warmup | 421 ± 303 | 7,089 ± 549 | 3,548 ± 386 | 11,058 ± 1,040 |
| a-mcp gen | 332 ± 176 | 2,314 ± 454 | 2,812 ± 1,768 | 5,458 ± 1,825 |
| b-baseline | 1,209 ± 2,430 | 13,175 ± 1,124 | 9,177 ± 2,316 | 23,560 ± 2,158 |

## Per-run

| run | a-mcp warmup $ | a-mcp gen $ | a-mcp total $ | a-mcp output | baseline $ | baseline output | a-files | b-files |
|---|---|---|---|---|---|---|---|---|
| 001 | $0.7990 | $0.9637 | $1.7628 | 17,545 | $1.2251 | 21,725 | 71 | 71 |
| 002 | $1.0159 | $0.9807 | $1.9966 | 17,417 | $1.2571 | 22,660 | 71 | 71 |
| 003 | $0.8418 | $0.9229 | $1.7647 | 14,907 | $1.2223 | 21,673 | 71 | 71 |
| 004 | $1.2576 | $0.9306 | $2.1882 | 16,095 | $1.4337 | 25,553 | 71 | 71 |
| 005 | $0.9337 | $0.8024 | $1.7361 | 16,616 | $4.2120 | 26,191 | 71 | 71 |

## Per-run wall-clock

Per-session `duration_ms` from each `claude -p` result event, broken out per run to make trends visible (cross-session cache warming, parallel-batch effects, etc.). Indicative only — depends on Anthropic load on the day.

| run | a-mcp warmup s | a-mcp gen s | b-baseline s |
|---|---|---|---|
| 001 | 146 | 105 | 172 |
| 002 | 152 | 74 | 189 |
| 003 | 481 | 60 | 176 |
| 004 | 281 | 60 | 203 |
| 005 | 182 | 73 | 371 |

## Caveats

- Authoritative numbers come from `claude -p`'s result event (`usage.output_tokens`, `total_cost_usd`). Per-event stream usage shows only visible-text output, which under-reports by excluding thinking and tool_use input bytes.
- **`cost USD` is the would-be API cost** at Anthropic's published rates — a token-usage proxy that's comparable across users and models. It's NOT what a subscription user (Claude Max/Pro) actually pays — those plans are flat-rate. The dollar figure still reflects the *relative work* of each variant; tokens × price is the universal benchmark unit.
- The two-session methodology gives **exact** phase split: each session has its own result event total. The gen session has the warmup's knowledge brief in its user prompt (a few hundred input tokens) — slightly inflating gen vs an ideal trained-model case, in the honest direction.
- Output token decomposition (visible / tool_input / thinking) is *descriptive only* — the visible+tool_input parts are exact-per-message but tool_input tokens are estimated from chars (3.5/token). Thinking is the residual. The sum equals the authoritative total.
- A model trained natively on MetaEngine would have warmup ≈ 0 (it would already know the API). Steady-state approximates that.
- Failed/partial runs are *not* filtered. Pass rate alongside cost is the full picture.
- Wall-clock is reported as indicative only — depends on Anthropic server load and is not reproducible run-to-run.
- Data collected on Opus 4.7 (1M-context). Within a few-day window we assume Anthropic-side model behavior is stable; cross-arm and cross-language comparisons inside that window are apples-to-apples. Re-runs after a model update are out of scope for token-cost reasons (not a cross-model benchmark).
