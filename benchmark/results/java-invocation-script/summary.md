# MetaEngine MCP — Benchmark Summary

Experiment: `java-invocation-script`. Means [min–max]; all recorded runs, including failed judgments.

Regenerated from original streams with measurement schema 2. Historical result.json files
remain unchanged; their legacy visible/thinking decomposition must not be used.

## Generation with a prepared brief

The assisted generation session receives the separate warm-up's brief in its prompt.
This measures a prepared workflow; it does not simulate training or guarantee future cache state.

| Session | n | Assistant messages | Tool calls | Output tokens | Cache-read tokens | Pass |
| --- | --- | --- | --- | --- | --- | --- |
| generation | 5 | 8.6 [6.0–12.0] | 7.6 [5.0–11.0] | 5,779 [4,713–6,821] | 368,779 [279,644–497,565] | 5/5 |
| baseline | 5 | 73.0 [73.0–73.0] | 72.0 [72.0–72.0] | 24,050 [22,736–26,374] | 4,785,867 [4,731,932–4,875,125] | 5/5 |
| warmup | 5 | 9.2 [8.0–10.0] | 8.2 [7.0–9.0] | 10,304 [9,595–11,653] | 343,133 [280,076–383,889] | — |

## Duration and recorded API-equivalent cost

These are the original result event's duration and cost fields. Cost is a dated
API-price calculation, not a subscription bill or a measure of subscription allowance.

| Session | Duration ms | Recorded cost USD |
| --- | --- | --- |
| generation | 74,785 [57,475–83,183] | 0.8676 [0.7543–0.9824] |
| baseline | 325,167 [290,812–364,061] | 3.4123 [3.3442–3.5328] |
| warmup | 155,633 [133,138–186,059] | 0.8855 [0.7961–0.9777] |

Warm-up plus generation, per paired run:

- Output tokens: 16,083 [15,539–16,420]
- Summed session duration ms: 230,418 [216,321–243,534]
- Recorded cost USD: 1.7531 [1.6013–1.9462]

## Observable content size

Characters count text blocks and Python's sorted-key JSON serialization of tool input
(`json.dumps`, default escaping and spacing). They are not token counts or wire bytes.
Assistant-event usage is not a visible-text token measurement. No thinking-token residual is inferred.

| Session | Text characters | Tool-input characters |
| --- | --- | --- |
| generation | 64 [4–152] | 7,083 [5,085–8,506] |
| baseline | 172 [84–325] | 44,545 [40,800–50,989] |
| warmup | 128 [11–275] | 24,224 [22,261–26,691] |

## Per-run message and call counts

`assistant_messages` counts distinct assistant message IDs; multiple tool blocks may
share one message. It is a trace-observed response count, not a count of invisible retries.
In these traces the CLI's `num_turns` equals tool calls plus one; it is retained separately.

| Run | Session | CLI num_turns | Assistant messages | Tool calls | Cache-read tokens | Verdict |
| --- | --- | --- | --- | --- | --- | --- |
| run-001 | warmup | 8 | 8 | 7 | 280,076 | — |
| run-001 | generation | 10 | 10 | 9 | 421,140 | pass |
| run-001 | baseline | 73 | 73 | 72 | 4,784,181 | pass |
| run-002 | warmup | 9 | 9 | 8 | 350,063 | — |
| run-002 | generation | 12 | 12 | 11 | 497,565 | pass |
| run-002 | baseline | 73 | 73 | 72 | 4,763,679 | pass |
| run-003 | warmup | 9 | 9 | 8 | 324,870 | — |
| run-003 | generation | 6 | 6 | 5 | 279,644 | pass |
| run-003 | baseline | 73 | 73 | 72 | 4,731,932 | pass |
| run-004 | warmup | 10 | 10 | 9 | 376,765 | — |
| run-004 | generation | 9 | 9 | 8 | 365,898 | pass |
| run-004 | baseline | 73 | 73 | 72 | 4,875,125 | pass |
| run-005 | warmup | 10 | 10 | 9 | 383,889 | — |
| run-005 | generation | 6 | 6 | 5 | 279,650 | pass |
| run-005 | baseline | 73 | 73 | 72 | 4,774,417 | pass |

## Caveats

- Five runs per cell on one day and a limited spec grid; no general savings or reliability estimate.
- The baseline is prompted to use Write per file; it can still emit multiple Write calls in one response.
- Fewer tool calls need not mean fewer model responses. Cache reads alone do not diagnose cache policy.
- Arms use different prompts; batches differ in concurrency and warm-up briefs. This is not a randomized causal experiment.
- A pass checks the compiler and the checked-in structural judge, not runtime semantics.
- Failed judgments remain in means. Missing or inconsistent source evidence causes recomputation to fail.
- New runs use today's configured tools and service behavior; they cannot recreate the historical environment exactly.
