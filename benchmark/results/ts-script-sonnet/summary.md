# MetaEngine MCP — Benchmark Summary

Experiment: `ts-script-sonnet`. Means [min–max]; all recorded runs, including failed judgments.

Regenerated from original streams with measurement schema 2. Historical result.json files
remain unchanged; their legacy visible/thinking decomposition must not be used.

## Generation with a prepared brief

The assisted generation session receives the separate warm-up's brief in its prompt.
This measures a prepared workflow; it does not simulate training or guarantee future cache state.

| Session | n | Assistant messages | Tool calls | Output tokens | Cache-read tokens | Pass |
| --- | --- | --- | --- | --- | --- | --- |
| generation | 5 | 7.0 [7.0–7.0] | 6.0 [6.0–6.0] | 5,275 [4,075–6,530] | 320,572 [308,938–329,068] | 5/5 |
| baseline | 5 | 17.0 [3.0–73.0] | 72.0 [72.0–72.0] | 16,936 [15,803–18,298] | 798,591 [46,054–3,808,741] | 5/5 |
| warmup | 5 | 5.8 [4.0–7.0] | 4.8 [3.0–6.0] | 8,525 [5,623–10,515] | 151,223 [84,412–205,240] | — |

## Duration and recorded API-equivalent cost

These are the original result event's duration and cost fields. Cost is a dated
API-price calculation, not a subscription bill or a measure of subscription allowance.

| Session | Duration ms | Recorded cost USD |
| --- | --- | --- |
| generation | 77,543 [65,739–95,166] | 0.3584 [0.3463–0.3701] |
| baseline | 174,785 [119,154–294,553] | 0.7750 [0.5488–1.6086] |
| warmup | 139,945 [106,717–185,580] | 0.2922 [0.1988–0.3808] |

Warm-up plus generation, per paired run:

- Output tokens: 13,799 [11,607–15,365]
- Summed session duration ms: 217,488 [190,186–257,903]
- Recorded cost USD: 0.6506 [0.5467–0.7271]

## Observable content size

Characters count text blocks and Python's sorted-key JSON serialization of tool input
(`json.dumps`, default escaping and spacing). They are not token counts or wire bytes.
Assistant-event usage is not a visible-text token measurement. No thinking-token residual is inferred.

| Session | Text characters | Tool-input characters |
| --- | --- | --- |
| generation | 397 [269–534] | 4,571 [4,160–5,076] |
| baseline | 140 [99–168] | 33,884 [30,814–34,788] |
| warmup | 549 [189–811] | 27,246 [17,365–32,812] |

## Per-run message and call counts

`assistant_messages` counts distinct assistant message IDs; multiple tool blocks may
share one message. It is a trace-observed response count, not a count of invisible retries.
In these traces the CLI's `num_turns` equals tool calls plus one; it is retained separately.

| Run | Session | CLI num_turns | Assistant messages | Tool calls | Cache-read tokens | Verdict |
| --- | --- | --- | --- | --- | --- | --- |
| run-001 | warmup | 6 | 6 | 5 | 155,830 | — |
| run-001 | generation | 7 | 7 | 6 | 326,205 | pass |
| run-001 | baseline | 73 | 3 | 72 | 46,054 | pass |
| run-002 | warmup | 7 | 7 | 6 | 205,240 | — |
| run-002 | generation | 7 | 7 | 6 | 328,553 | pass |
| run-002 | baseline | 73 | 3 | 72 | 46,054 | pass |
| run-003 | warmup | 6 | 6 | 5 | 166,948 | — |
| run-003 | generation | 7 | 7 | 6 | 329,068 | pass |
| run-003 | baseline | 73 | 3 | 72 | 46,054 | pass |
| run-004 | warmup | 6 | 6 | 5 | 143,687 | — |
| run-004 | generation | 7 | 7 | 6 | 308,938 | pass |
| run-004 | baseline | 73 | 3 | 72 | 46,054 | pass |
| run-005 | warmup | 4 | 4 | 3 | 84,412 | — |
| run-005 | generation | 7 | 7 | 6 | 310,097 | pass |
| run-005 | baseline | 73 | 73 | 72 | 3,808,741 | pass |

## Caveats

- Five runs per cell on one day and a limited spec grid; no general savings or reliability estimate.
- The baseline is prompted to use Write per file; it can still emit multiple Write calls in one response.
- Fewer tool calls need not mean fewer model responses. Cache reads alone do not diagnose cache policy.
- Arms use different prompts; batches differ in concurrency and warm-up briefs. This is not a randomized causal experiment.
- A pass checks the compiler and the checked-in structural judge, not runtime semantics.
- Failed judgments remain in means. Missing or inconsistent source evidence causes recomputation to fail.
- New runs use today's configured tools and service behavior; they cannot recreate the historical environment exactly.
