# MetaEngine MCP — Benchmark Summary

Experiment: `ts-monolith-sonnet-inline`. Means [min–max]; all recorded runs, including failed judgments.

Regenerated from original streams with measurement schema 2. Historical result.json files
remain unchanged; their legacy visible/thinking decomposition must not be used.

## Generation with a prepared brief

The assisted generation session receives the separate warm-up's brief in its prompt.
This measures a prepared workflow; it does not simulate training or guarantee future cache state.

| Session | n | Assistant messages | Tool calls | Output tokens | Cache-read tokens | Pass |
| --- | --- | --- | --- | --- | --- | --- |
| generation | 5 | 5.0 [5.0–5.0] | 4.0 [4.0–4.0] | 31,285 [23,956–44,623] | 234,199 [206,670–259,247] | 5/5 |
| baseline | 5 | 8.4 [4.0–17.0] | 69.6 [69.0–70.0] | 22,327 [19,662–26,947] | 278,321 [58,627–843,529] | 5/5 |
| warmup | 5 | 6.2 [4.0–9.0] | 5.4 [3.0–9.0] | 8,374 [6,918–10,040] | 159,977 [84,049–266,948] | — |

## Duration and recorded API-equivalent cost

These are the original result event's duration and cost fields. Cost is a dated
API-price calculation, not a subscription bill or a measure of subscription allowance.

| Session | Duration ms | Recorded cost USD |
| --- | --- | --- |
| generation | 329,086 [263,718–500,088] | 0.8272 [0.6782–1.0696] |
| baseline | 208,585 [183,230–240,562] | 0.9951 [0.7497–1.2779] |
| warmup | 146,679 [115,599–180,570] | 0.2908 [0.2123–0.3631] |

Warm-up plus generation, per paired run:

- Output tokens: 39,660 [31,724–53,957]
- Summed session duration ms: 475,765 [393,774–661,725]
- Recorded cost USD: 1.1180 [0.9657–1.4327]

## Observable content size

Characters count text blocks and Python's sorted-key JSON serialization of tool input
(`json.dumps`, default escaping and spacing). They are not token counts or wire bytes.
Assistant-event usage is not a visible-text token measurement. No thinking-token residual is inferred.

| Session | Text characters | Tool-input characters |
| --- | --- | --- |
| generation | 439 [293–592] | 30,150 [30,136–30,159] |
| baseline | 301 [196–400] | 32,925 [31,907–33,582] |
| warmup | 500 [182–864] | 27,521 [24,448–32,321] |

## Per-run message and call counts

`assistant_messages` counts distinct assistant message IDs; multiple tool blocks may
share one message. It is a trace-observed response count, not a count of invisible retries.
In these traces the CLI's `num_turns` equals tool calls plus one; it is retained separately.

| Run | Session | CLI num_turns | Assistant messages | Tool calls | Cache-read tokens | Verdict |
| --- | --- | --- | --- | --- | --- | --- |
| run-001 | warmup | 6 | 6 | 5 | 134,062 | — |
| run-001 | generation | 5 | 5 | 4 | 223,837 | pass |
| run-001 | baseline | 70 | 4 | 69 | 58,627 | pass |
| run-002 | warmup | 4 | 4 | 3 | 84,049 | — |
| run-002 | generation | 5 | 5 | 4 | 206,670 | pass |
| run-002 | baseline | 70 | 4 | 69 | 58,627 | pass |
| run-003 | warmup | 6 | 6 | 5 | 167,641 | — |
| run-003 | generation | 5 | 5 | 4 | 253,947 | pass |
| run-003 | baseline | 71 | 9 | 70 | 220,730 | pass |
| run-004 | warmup | 10 | 9 | 9 | 266,948 | — |
| run-004 | generation | 5 | 5 | 4 | 259,247 | pass |
| run-004 | baseline | 71 | 17 | 70 | 843,529 | pass |
| run-005 | warmup | 6 | 6 | 5 | 147,185 | — |
| run-005 | generation | 5 | 5 | 4 | 227,294 | pass |
| run-005 | baseline | 71 | 8 | 70 | 210,094 | pass |

## Caveats

- Five runs per cell on one day and a limited spec grid; no general savings or reliability estimate.
- The baseline is prompted to use Write per file; it can still emit multiple Write calls in one response.
- Fewer tool calls need not mean fewer model responses. Cache reads alone do not diagnose cache policy.
- Arms use different prompts; batches differ in concurrency and warm-up briefs. This is not a randomized causal experiment.
- A pass checks the compiler and the checked-in structural judge, not runtime semantics.
- Failed judgments remain in means. Missing or inconsistent source evidence causes recomputation to fail.
- New runs use today's configured tools and service behavior; they cannot recreate the historical environment exactly.
