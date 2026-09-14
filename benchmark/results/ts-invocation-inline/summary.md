# MetaEngine MCP — Benchmark Summary

Experiment: `ts-invocation-inline`. Means [min–max]; all recorded runs, including failed judgments.

Regenerated from original streams with measurement schema 2. Historical result.json files
remain unchanged; their legacy visible/thinking decomposition must not be used.

## Generation with a prepared brief

The assisted generation session receives the separate warm-up's brief in its prompt.
This measures a prepared workflow; it does not simulate training or guarantee future cache state.

| Session | n | Assistant messages | Tool calls | Output tokens | Cache-read tokens | Pass |
| --- | --- | --- | --- | --- | --- | --- |
| generation | 5 | 5.0 [5.0–5.0] | 4.0 [4.0–4.0] | 17,913 [16,154–21,021] | 219,408 [203,868–230,081] | 5/5 |
| baseline | 5 | 60.4 [10.0–73.0] | 72.0 [72.0–72.0] | 20,198 [18,738–21,261] | 3,776,774 [530,212–4,632,585] | 5/5 |
| warmup | 5 | 6.8 [6.0–9.0] | 5.8 [5.0–8.0] | 9,999 [8,740–11,882] | 209,587 [153,689–325,339] | — |

## Duration and recorded API-equivalent cost

These are the original result event's duration and cost fields. Cost is a dated
API-price calculation, not a subscription bill or a measure of subscription allowance.

| Session | Duration ms | Recorded cost USD |
| --- | --- | --- |
| generation | 146,158 [130,258–179,065] | 1.3132 [1.2323–1.3814] |
| baseline | 268,588 [154,017–364,020] | 2.8010 [1.1867–3.2445] |
| warmup | 147,991 [127,772–175,836] | 0.8867 [0.6675–1.1618] |

Warm-up plus generation, per paired run:

- Output tokens: 27,912 [24,894–31,098]
- Summed session duration ms: 294,149 [265,727–330,412]
- Recorded cost USD: 2.1999 [1.9737–2.5431]

## Observable content size

Characters count text blocks and Python's sorted-key JSON serialization of tool input
(`json.dumps`, default escaping and spacing). They are not token counts or wire bytes.
Assistant-event usage is not a visible-text token measurement. No thinking-token residual is inferred.

| Session | Text characters | Tool-input characters |
| --- | --- | --- |
| generation | 137 [91–185] | 34,689 [34,680–34,703] |
| baseline | 73 [67–80] | 33,048 [32,115–33,935] |
| warmup | 84 [11–118] | 24,025 [21,898–27,589] |

## Per-run message and call counts

`assistant_messages` counts distinct assistant message IDs; multiple tool blocks may
share one message. It is a trace-observed response count, not a count of invisible retries.
In these traces the CLI's `num_turns` equals tool calls plus one; it is retained separately.

| Run | Session | CLI num_turns | Assistant messages | Tool calls | Cache-read tokens | Verdict |
| --- | --- | --- | --- | --- | --- | --- |
| run-001 | warmup | 6 | 6 | 5 | 170,081 | — |
| run-001 | generation | 5 | 5 | 4 | 230,081 | pass |
| run-001 | baseline | 73 | 73 | 72 | 4,632,585 | pass |
| run-002 | warmup | 9 | 9 | 8 | 325,339 | — |
| run-002 | generation | 5 | 5 | 4 | 212,230 | pass |
| run-002 | baseline | 73 | 73 | 72 | 4,563,003 | pass |
| run-003 | warmup | 6 | 6 | 5 | 153,689 | — |
| run-003 | generation | 5 | 5 | 4 | 226,323 | pass |
| run-003 | baseline | 73 | 10 | 72 | 530,212 | pass |
| run-004 | warmup | 7 | 7 | 6 | 194,999 | — |
| run-004 | generation | 5 | 5 | 4 | 224,540 | pass |
| run-004 | baseline | 73 | 73 | 72 | 4,577,840 | pass |
| run-005 | warmup | 6 | 6 | 5 | 203,828 | — |
| run-005 | generation | 5 | 5 | 4 | 203,868 | pass |
| run-005 | baseline | 73 | 73 | 72 | 4,580,230 | pass |

## Caveats

- Five runs per cell on one day and a limited spec grid; no general savings or reliability estimate.
- The baseline is prompted to use Write per file; it can still emit multiple Write calls in one response.
- Fewer tool calls need not mean fewer model responses. Cache reads alone do not diagnose cache policy.
- Arms use different prompts; batches differ in concurrency and warm-up briefs. This is not a randomized causal experiment.
- A pass checks the compiler and the checked-in structural judge, not runtime semantics.
- Failed judgments remain in means. Missing or inconsistent source evidence causes recomputation to fail.
- New runs use today's configured tools and service behavior; they cannot recreate the historical environment exactly.
