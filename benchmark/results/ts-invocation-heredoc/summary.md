# MetaEngine MCP — Benchmark Summary

Experiment: `ts-invocation-heredoc`. Means [min–max]; all recorded runs, including failed judgments.

Regenerated from original streams with measurement schema 2. Historical result.json files
remain unchanged; their legacy visible/thinking decomposition must not be used.

## Generation with a prepared brief

The assisted generation session receives the separate warm-up's brief in its prompt.
This measures a prepared workflow; it does not simulate training or guarantee future cache state.

| Session | n | Assistant messages | Tool calls | Output tokens | Cache-read tokens | Pass |
| --- | --- | --- | --- | --- | --- | --- |
| generation | 5 | 6.4 [6.0–7.0] | 5.4 [5.0–6.0] | 20,217 [19,234–22,377] | 336,032 [306,061–379,506] | 4/5 |
| baseline | 5 | 73.0 [73.0–73.0] | 72.0 [72.0–72.0] | 21,112 [20,199–21,993] | 4,628,420 [4,569,513–4,686,205] | 5/5 |
| warmup | 5 | 10.0 [9.0–11.0] | 9.0 [8.0–10.0] | 11,130 [9,869–12,509] | 396,597 [351,631–460,004] | — |

## Duration and recorded API-equivalent cost

These are the original result event's duration and cost fields. Cost is a dated
API-price calculation, not a subscription bill or a measure of subscription allowance.

| Session | Duration ms | Recorded cost USD |
| --- | --- | --- |
| generation | 174,508 [149,898–200,069] | 1.4439 [1.3457–1.5369] |
| baseline | 305,360 [287,297–363,419] | 3.2536 [3.1820–3.3264] |
| warmup | 161,953 [141,057–175,334] | 0.9598 [0.9272–0.9989] |

Warm-up plus generation, per paired run:

- Output tokens: 31,347 [29,795–34,164]
- Summed session duration ms: 336,461 [306,671–375,403]
- Recorded cost USD: 2.4037 [2.2778–2.5358]

## Observable content size

Characters count text blocks and Python's sorted-key JSON serialization of tool input
(`json.dumps`, default escaping and spacing). They are not token counts or wire bytes.
Assistant-event usage is not a visible-text token measurement. No thinking-token residual is inferred.

| Session | Text characters | Tool-input characters |
| --- | --- | --- |
| generation | 143 [92–201] | 45,587 [44,445–45,996] |
| baseline | 79 [48–141] | 33,144 [31,701–34,101] |
| warmup | 92 [11–174] | 25,584 [22,441–28,639] |

## Per-run message and call counts

`assistant_messages` counts distinct assistant message IDs; multiple tool blocks may
share one message. It is a trace-observed response count, not a count of invisible retries.
In these traces the CLI's `num_turns` equals tool calls plus one; it is retained separately.

| Run | Session | CLI num_turns | Assistant messages | Tool calls | Cache-read tokens | Verdict |
| --- | --- | --- | --- | --- | --- | --- |
| run-001 | warmup | 11 | 11 | 10 | 460,004 | — |
| run-001 | generation | 7 | 7 | 6 | 379,506 | pass |
| run-001 | baseline | 73 | 73 | 72 | 4,662,860 | pass |
| run-002 | warmup | 10 | 10 | 9 | 372,813 | — |
| run-002 | generation | 6 | 6 | 5 | 307,452 | pass |
| run-002 | baseline | 73 | 73 | 72 | 4,569,513 | pass |
| run-003 | warmup | 10 | 10 | 9 | 396,337 | — |
| run-003 | generation | 6 | 6 | 5 | 316,202 | compile_errors |
| run-003 | baseline | 73 | 73 | 72 | 4,641,277 | pass |
| run-004 | warmup | 10 | 10 | 9 | 402,200 | — |
| run-004 | generation | 7 | 7 | 6 | 370,940 | pass |
| run-004 | baseline | 73 | 73 | 72 | 4,582,247 | pass |
| run-005 | warmup | 9 | 9 | 8 | 351,631 | — |
| run-005 | generation | 6 | 6 | 5 | 306,061 | pass |
| run-005 | baseline | 73 | 73 | 72 | 4,686,205 | pass |

## Caveats

- Five runs per cell on one day and a limited spec grid; no general savings or reliability estimate.
- The baseline is prompted to use Write per file; it can still emit multiple Write calls in one response.
- Fewer tool calls need not mean fewer model responses. Cache reads alone do not diagnose cache policy.
- Arms use different prompts; batches differ in concurrency and warm-up briefs. This is not a randomized causal experiment.
- A pass checks the compiler and the checked-in structural judge, not runtime semantics.
- Failed judgments remain in means. Missing or inconsistent source evidence causes recomputation to fail.
- New runs use today's configured tools and service behavior; they cannot recreate the historical environment exactly.
