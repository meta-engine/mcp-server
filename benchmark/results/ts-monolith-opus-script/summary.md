# MetaEngine MCP — Benchmark Summary

Experiment: `ts-monolith-opus-script`. Means [min–max]; all recorded runs, including failed judgments.

Regenerated from original streams with measurement schema 2. Historical result.json files
remain unchanged; their legacy visible/thinking decomposition must not be used.

## Generation with a prepared brief

The assisted generation session receives the separate warm-up's brief in its prompt.
This measures a prepared workflow; it does not simulate training or guarantee future cache state.

| Session | n | Assistant messages | Tool calls | Output tokens | Cache-read tokens | Pass |
| --- | --- | --- | --- | --- | --- | --- |
| generation | 5 | 7.6 [7.0–8.0] | 6.6 [6.0–7.0] | 8,531 [3,570–12,239] | 386,739 [350,196–415,733] | 5/5 |
| baseline | 5 | 72.2 [70.0–80.0] | 71.2 [69.0–79.0] | 23,583 [20,900–26,846] | 4,648,979 [4,322,692–5,284,682] | 5/5 |
| warmup | 5 | 8.0 [5.0–10.0] | 7.0 [4.0–9.0] | 10,076 [8,870–11,099] | 284,469 [126,576–388,878] | — |

## Duration and recorded API-equivalent cost

These are the original result event's duration and cost fields. Cost is a dated
API-price calculation, not a subscription bill or a measure of subscription allowance.

| Session | Duration ms | Recorded cost USD |
| --- | --- | --- |
| generation | 112,214 [55,968–152,195] | 1.0926 [0.9026–1.2246] |
| baseline | 326,530 [280,116–372,677] | 3.3804 [3.0914–3.9684] |
| warmup | 142,711 [134,486–154,620] | 0.7788 [0.6497–0.9011] |

Warm-up plus generation, per paired run:

- Output tokens: 18,607 [13,670–23,338]
- Summed session duration ms: 254,925 [197,075–300,566]
- Recorded cost USD: 1.8714 [1.7456–2.1258]

## Observable content size

Characters count text blocks and Python's sorted-key JSON serialization of tool input
(`json.dumps`, default escaping and spacing). They are not token counts or wire bytes.
Assistant-event usage is not a visible-text token measurement. No thinking-token residual is inferred.

| Session | Text characters | Tool-input characters |
| --- | --- | --- |
| generation | 134 [4–248] | 6,643 [6,331–7,166] |
| baseline | 221 [114–367] | 34,440 [31,238–43,680] |
| warmup | 67 [11–86] | 23,744 [21,474–25,601] |

## Per-run message and call counts

`assistant_messages` counts distinct assistant message IDs; multiple tool blocks may
share one message. It is a trace-observed response count, not a count of invisible retries.
In these traces the CLI's `num_turns` equals tool calls plus one; it is retained separately.

| Run | Session | CLI num_turns | Assistant messages | Tool calls | Cache-read tokens | Verdict |
| --- | --- | --- | --- | --- | --- | --- |
| run-001 | warmup | 7 | 7 | 6 | 231,365 | — |
| run-001 | generation | 8 | 8 | 7 | 415,733 | pass |
| run-001 | baseline | 71 | 71 | 70 | 4,471,840 | pass |
| run-002 | warmup | 9 | 9 | 8 | 341,900 | — |
| run-002 | generation | 7 | 7 | 6 | 362,344 | pass |
| run-002 | baseline | 70 | 70 | 69 | 4,441,567 | pass |
| run-003 | warmup | 5 | 5 | 4 | 126,576 | — |
| run-003 | generation | 7 | 7 | 6 | 350,196 | pass |
| run-003 | baseline | 70 | 70 | 69 | 4,724,115 | pass |
| run-004 | warmup | 9 | 9 | 8 | 333,627 | — |
| run-004 | generation | 8 | 8 | 7 | 410,600 | pass |
| run-004 | baseline | 70 | 70 | 69 | 4,322,692 | pass |
| run-005 | warmup | 10 | 10 | 9 | 388,878 | — |
| run-005 | generation | 8 | 8 | 7 | 394,821 | pass |
| run-005 | baseline | 80 | 80 | 79 | 5,284,682 | pass |

## Caveats

- Five runs per cell on one day and a limited spec grid; no general savings or reliability estimate.
- The baseline is prompted to use Write per file; it can still emit multiple Write calls in one response.
- Fewer tool calls need not mean fewer model responses. Cache reads alone do not diagnose cache policy.
- Arms use different prompts; batches differ in concurrency and warm-up briefs. This is not a randomized causal experiment.
- A pass checks the compiler and the checked-in structural judge, not runtime semantics.
- Failed judgments remain in means. Missing or inconsistent source evidence causes recomputation to fail.
- New runs use today's configured tools and service behavior; they cannot recreate the historical environment exactly.
