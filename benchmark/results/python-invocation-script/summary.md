# MetaEngine MCP — Benchmark Summary

Experiment: `python-invocation-script`. Means [min–max]; all recorded runs, including failed judgments.

Regenerated from original streams with measurement schema 2. Historical result.json files
remain unchanged; their legacy visible/thinking decomposition must not be used.

## Generation with a prepared brief

The assisted generation session receives the separate warm-up's brief in its prompt.
This measures a prepared workflow; it does not simulate training or guarantee future cache state.

| Session | n | Assistant messages | Tool calls | Output tokens | Cache-read tokens | Pass |
| --- | --- | --- | --- | --- | --- | --- |
| generation | 5 | 9.2 [6.0–13.0] | 8.2 [5.0–12.0] | 5,458 [3,812–8,159] | 420,442 [283,437–552,830] | 5/5 |
| baseline | 5 | 24.6 [10.0–83.0] | 74.0 [72.0–82.0] | 23,560 [21,673–26,191] | 1,600,372 [563,187–5,727,465] | 5/5 |
| warmup | 5 | 11.6 [9.0–20.0] | 10.8 [8.0–19.0] | 11,058 [9,386–12,214] | 502,004 [325,114–1,030,290] | — |

## Duration and recorded API-equivalent cost

These are the original result event's duration and cost fields. Cost is a dated
API-price calculation, not a subscription bill or a measure of subscription allowance.

| Session | Duration ms | Recorded cost USD |
| --- | --- | --- |
| generation | 74,547 [60,224–105,153] | 0.9200 [0.8024–0.9807] |
| baseline | 222,241 [172,146–370,906] | 1.8701 [1.2223–4.2120] |
| warmup | 248,467 [146,413–480,924] | 0.9696 [0.7990–1.2576] |

Warm-up plus generation, per paired run:

- Output tokens: 16,516 [14,907–17,545]
- Summed session duration ms: 323,014 [226,140–541,177]
- Recorded cost USD: 1.8897 [1.7361–2.1882]

## Observable content size

Characters count text blocks and Python's sorted-key JSON serialization of tool input
(`json.dumps`, default escaping and spacing). They are not token counts or wire bytes.
Assistant-event usage is not a visible-text token measurement. No thinking-token residual is inferred.

| Session | Text characters | Tool-input characters |
| --- | --- | --- |
| generation | 84 [4–207] | 7,496 [5,480–9,423] |
| baseline | 285 [72–393] | 42,873 [39,402–49,222] |
| warmup | 171 [11–335] | 24,531 [21,238–26,035] |

## Per-run message and call counts

`assistant_messages` counts distinct assistant message IDs; multiple tool blocks may
share one message. It is a trace-observed response count, not a count of invisible retries.
In these traces the CLI's `num_turns` equals tool calls plus one; it is retained separately.

| Run | Session | CLI num_turns | Assistant messages | Tool calls | Cache-read tokens | Verdict |
| --- | --- | --- | --- | --- | --- | --- |
| run-001 | warmup | 9 | 9 | 8 | 352,018 | — |
| run-001 | generation | 13 | 13 | 12 | 552,830 | pass |
| run-001 | baseline | 73 | 10 | 72 | 565,745 | pass |
| run-002 | warmup | 9 | 9 | 8 | 325,114 | — |
| run-002 | generation | 6 | 6 | 5 | 283,437 | pass |
| run-002 | baseline | 73 | 10 | 72 | 571,273 | pass |
| run-003 | warmup | 9 | 9 | 8 | 332,836 | — |
| run-003 | generation | 8 | 8 | 7 | 409,031 | pass |
| run-003 | baseline | 73 | 10 | 72 | 563,187 | pass |
| run-004 | warmup | 20 | 20 | 19 | 1,030,290 | — |
| run-004 | generation | 8 | 8 | 7 | 401,226 | pass |
| run-004 | baseline | 73 | 10 | 72 | 574,191 | pass |
| run-005 | warmup | 12 | 11 | 11 | 469,763 | — |
| run-005 | generation | 11 | 11 | 10 | 455,684 | pass |
| run-005 | baseline | 83 | 83 | 82 | 5,727,465 | pass |

## Caveats

- Five runs per cell on one day and a limited spec grid; no general savings or reliability estimate.
- The baseline is prompted to use Write per file; it can still emit multiple Write calls in one response.
- Fewer tool calls need not mean fewer model responses. Cache reads alone do not diagnose cache policy.
- Arms use different prompts; batches differ in concurrency and warm-up briefs. This is not a randomized causal experiment.
- A pass checks the compiler and the checked-in structural judge, not runtime semantics.
- Failed judgments remain in means. Missing or inconsistent source evidence causes recomputation to fail.
- New runs use today's configured tools and service behavior; they cannot recreate the historical environment exactly.
