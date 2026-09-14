# MetaEngine MCP — Benchmark Summary

Experiment: `ts-monolith-sonnet-script`. Means [min–max]; all recorded runs, including failed judgments.

Regenerated from original streams with measurement schema 2. Historical result.json files
remain unchanged; their legacy visible/thinking decomposition must not be used.

## Generation with a prepared brief

The assisted generation session receives the separate warm-up's brief in its prompt.
This measures a prepared workflow; it does not simulate training or guarantee future cache state.

| Session | n | Assistant messages | Tool calls | Output tokens | Cache-read tokens | Pass |
| --- | --- | --- | --- | --- | --- | --- |
| generation | 5 | 7.0 [7.0–7.0] | 6.0 [6.0–6.0] | 10,261 [8,538–12,160] | 325,339 [314,175–333,192] | 5/5 |
| baseline | 5 | 8.0 [4.0–12.0] | 69.6 [69.0–70.0] | 22,468 [19,907–29,323] | 233,146 [48,604–540,245] | 5/5 |
| warmup | 5 | 5.8 [5.0–6.0] | 4.8 [4.0–5.0] | 7,457 [6,664–8,510] | 142,931 [111,461–158,611] | — |

## Duration and recorded API-equivalent cost

These are the original result event's duration and cost fields. Cost is a dated
API-price calculation, not a subscription bill or a measure of subscription allowance.

| Session | Duration ms | Recorded cost USD |
| --- | --- | --- |
| generation | 151,916 [121,451–185,349] | 0.4418 [0.4025–0.4782] |
| baseline | 198,310 [183,337–240,448] | 1.0818 [0.8079–1.3424] |
| warmup | 119,188 [100,314–136,600] | 0.2494 [0.2228–0.2988] |

Warm-up plus generation, per paired run:

- Output tokens: 17,719 [15,202–19,388]
- Summed session duration ms: 271,104 [221,765–299,521]
- Recorded cost USD: 0.6912 [0.6286–0.7389]

## Observable content size

Characters count text blocks and Python's sorted-key JSON serialization of tool input
(`json.dumps`, default escaping and spacing). They are not token counts or wire bytes.
Assistant-event usage is not a visible-text token measurement. No thinking-token residual is inferred.

| Session | Text characters | Tool-input characters |
| --- | --- | --- |
| generation | 362 [231–506] | 6,937 [6,165–7,687] |
| baseline | 292 [158–415] | 33,190 [31,810–34,056] |
| warmup | 450 [316–557] | 24,803 [21,986–27,982] |

## Per-run message and call counts

`assistant_messages` counts distinct assistant message IDs; multiple tool blocks may
share one message. It is a trace-observed response count, not a count of invisible retries.
In these traces the CLI's `num_turns` equals tool calls plus one; it is retained separately.

| Run | Session | CLI num_turns | Assistant messages | Tool calls | Cache-read tokens | Verdict |
| --- | --- | --- | --- | --- | --- | --- |
| run-001 | warmup | 6 | 6 | 5 | 158,611 | — |
| run-001 | generation | 7 | 7 | 6 | 329,569 | pass |
| run-001 | baseline | 71 | 12 | 70 | 540,245 | pass |
| run-002 | warmup | 6 | 6 | 5 | 153,402 | — |
| run-002 | generation | 7 | 7 | 6 | 318,418 | pass |
| run-002 | baseline | 71 | 7 | 70 | 193,127 | pass |
| run-003 | warmup | 6 | 6 | 5 | 144,757 | — |
| run-003 | generation | 7 | 7 | 6 | 314,175 | pass |
| run-003 | baseline | 71 | 9 | 70 | 225,947 | pass |
| run-004 | warmup | 5 | 5 | 4 | 111,461 | — |
| run-004 | generation | 7 | 7 | 6 | 331,341 | pass |
| run-004 | baseline | 70 | 4 | 69 | 48,604 | pass |
| run-005 | warmup | 6 | 6 | 5 | 146,425 | — |
| run-005 | generation | 7 | 7 | 6 | 333,192 | pass |
| run-005 | baseline | 70 | 8 | 69 | 157,808 | pass |

## Caveats

- Five runs per cell on one day and a limited spec grid; no general savings or reliability estimate.
- The baseline is prompted to use Write per file; it can still emit multiple Write calls in one response.
- Fewer tool calls need not mean fewer model responses. Cache reads alone do not diagnose cache policy.
- Arms use different prompts; batches differ in concurrency and warm-up briefs. This is not a randomized causal experiment.
- A pass checks the compiler and the checked-in structural judge, not runtime semantics.
- Failed judgments remain in means. Missing or inconsistent source evidence causes recomputation to fail.
- New runs use today's configured tools and service behavior; they cannot recreate the historical environment exactly.
