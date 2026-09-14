# MetaEngine MCP — Benchmark Summary

Experiment: `java-multilang`. Means [min–max]; all recorded runs, including failed judgments.

Regenerated from original streams with measurement schema 2. Historical result.json files
remain unchanged; their legacy visible/thinking decomposition must not be used.

## Generation with a prepared brief

The assisted generation session receives the separate warm-up's brief in its prompt.
This measures a prepared workflow; it does not simulate training or guarantee future cache state.

| Session | n | Assistant messages | Tool calls | Output tokens | Cache-read tokens | Pass |
| --- | --- | --- | --- | --- | --- | --- |
| generation | 5 | 5.0 [5.0–5.0] | 4.0 [4.0–4.0] | 20,955 [17,324–24,018] | 233,577 [230,228–238,464] | 5/5 |
| baseline | 5 | 76.6 [73.0–82.0] | 75.6 [72.0–81.0] | 26,435 [23,821–30,468] | 5,095,268 [4,640,866–5,783,206] | 5/5 |
| warmup | 5 | 8.4 [7.0–10.0] | 7.4 [6.0–9.0] | 12,549 [10,170–13,616] | 309,261 [247,734–397,154] | — |

## Duration and recorded API-equivalent cost

These are the original result event's duration and cost fields. Cost is a dated
API-price calculation, not a subscription bill or a measure of subscription allowance.

| Session | Duration ms | Recorded cost USD |
| --- | --- | --- |
| generation | 176,938 [134,012–209,740] | 1.3801 [1.2860–1.4574] |
| baseline | 326,978 [292,335–357,548] | 3.7399 [3.3259–4.3633] |
| warmup | 178,210 [141,974–202,615] | 0.8972 [0.7120–0.9988] |

Warm-up plus generation, per paired run:

- Output tokens: 33,504 [30,940–36,480]
- Summed session duration ms: 355,147 [316,046–388,782]
- Recorded cost USD: 2.2773 [2.0709–2.3658]

## Observable content size

Characters count text blocks and Python's sorted-key JSON serialization of tool input
(`json.dumps`, default escaping and spacing). They are not token counts or wire bytes.
Assistant-event usage is not a visible-text token measurement. No thinking-token residual is inferred.

| Session | Text characters | Tool-input characters |
| --- | --- | --- |
| generation | 204 [137–326] | 36,978 [36,468–37,768] |
| baseline | 174 [86–334] | 50,382 [44,693–58,290] |
| warmup | 117 [11–241] | 29,879 [26,360–33,102] |

## Per-run message and call counts

`assistant_messages` counts distinct assistant message IDs; multiple tool blocks may
share one message. It is a trace-observed response count, not a count of invisible retries.
In these traces the CLI's `num_turns` equals tool calls plus one; it is retained separately.

| Run | Session | CLI num_turns | Assistant messages | Tool calls | Cache-read tokens | Verdict |
| --- | --- | --- | --- | --- | --- | --- |
| run-001 | warmup | 7 | 7 | 6 | 247,734 | — |
| run-001 | generation | 5 | 5 | 4 | 230,228 | pass |
| run-001 | baseline | 82 | 82 | 81 | 5,677,908 | pass |
| run-002 | warmup | 10 | 10 | 9 | 397,154 | — |
| run-002 | generation | 5 | 5 | 4 | 234,244 | pass |
| run-002 | baseline | 73 | 73 | 72 | 4,722,414 | pass |
| run-003 | warmup | 8 | 8 | 7 | 274,465 | — |
| run-003 | generation | 5 | 5 | 4 | 231,378 | pass |
| run-003 | baseline | 82 | 82 | 81 | 5,783,206 | pass |
| run-004 | warmup | 9 | 9 | 8 | 335,328 | — |
| run-004 | generation | 5 | 5 | 4 | 238,464 | pass |
| run-004 | baseline | 73 | 73 | 72 | 4,651,947 | pass |
| run-005 | warmup | 8 | 8 | 7 | 291,624 | — |
| run-005 | generation | 5 | 5 | 4 | 233,570 | pass |
| run-005 | baseline | 73 | 73 | 72 | 4,640,866 | pass |

## Caveats

- Five runs per cell on one day and a limited spec grid; no general savings or reliability estimate.
- The baseline is prompted to use Write per file; it can still emit multiple Write calls in one response.
- Fewer tool calls need not mean fewer model responses. Cache reads alone do not diagnose cache policy.
- Arms use different prompts; batches differ in concurrency and warm-up briefs. This is not a randomized causal experiment.
- A pass checks the compiler and the checked-in structural judge, not runtime semantics.
- Failed judgments remain in means. Missing or inconsistent source evidence causes recomputation to fail.
- New runs use today's configured tools and service behavior; they cannot recreate the historical environment exactly.
