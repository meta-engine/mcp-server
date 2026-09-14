# MetaEngine MCP — Benchmark Summary

Experiment: `java-invocation-inline`. Means [min–max]; all recorded runs, including failed judgments.

Regenerated from original streams with measurement schema 2. Historical result.json files
remain unchanged; their legacy visible/thinking decomposition must not be used.

## Generation with a prepared brief

The assisted generation session receives the separate warm-up's brief in its prompt.
This measures a prepared workflow; it does not simulate training or guarantee future cache state.

| Session | n | Assistant messages | Tool calls | Output tokens | Cache-read tokens | Pass |
| --- | --- | --- | --- | --- | --- | --- |
| generation | 5 | 5.0 [5.0–5.0] | 4.0 [4.0–4.0] | 19,680 [17,918–23,274] | 231,116 [225,694–237,105] | 5/5 |
| baseline | 5 | 73.0 [73.0–73.0] | 72.0 [72.0–72.0] | 25,526 [24,124–26,739] | 4,841,747 [4,750,924–4,895,596] | 5/5 |
| warmup | 5 | 8.6 [6.0–10.0] | 7.8 [5.0–10.0] | 10,817 [9,788–12,071] | 320,900 [189,584–394,386] | — |

## Duration and recorded API-equivalent cost

These are the original result event's duration and cost fields. Cost is a dated
API-price calculation, not a subscription bill or a measure of subscription allowance.

| Session | Duration ms | Recorded cost USD |
| --- | --- | --- |
| generation | 162,202 [140,696–188,458] | 1.3088 [1.2045–1.4296] |
| baseline | 348,887 [330,600–363,724] | 3.4897 [3.4025–3.5577] |
| warmup | 156,882 [140,554–180,305] | 0.8312 [0.6473–0.9051] |

Warm-up plus generation, per paired run:

- Output tokens: 30,497 [28,875–33,062]
- Summed session duration ms: 319,085 [300,226–343,598]
- Recorded cost USD: 2.1400 [2.0769–2.1943]

## Observable content size

Characters count text blocks and Python's sorted-key JSON serialization of tool input
(`json.dumps`, default escaping and spacing). They are not token counts or wire bytes.
Assistant-event usage is not a visible-text token measurement. No thinking-token residual is inferred.

| Session | Text characters | Tool-input characters |
| --- | --- | --- |
| generation | 130 [54–179] | 36,746 [36,232–37,277] |
| baseline | 124 [84–249] | 48,563 [47,096–51,685] |
| warmup | 156 [61–246] | 25,279 [23,439–27,935] |

## Per-run message and call counts

`assistant_messages` counts distinct assistant message IDs; multiple tool blocks may
share one message. It is a trace-observed response count, not a count of invisible retries.
In these traces the CLI's `num_turns` equals tool calls plus one; it is retained separately.

| Run | Session | CLI num_turns | Assistant messages | Tool calls | Cache-read tokens | Verdict |
| --- | --- | --- | --- | --- | --- | --- |
| run-001 | warmup | 10 | 10 | 9 | 391,972 | — |
| run-001 | generation | 5 | 5 | 4 | 237,105 | pass |
| run-001 | baseline | 73 | 73 | 72 | 4,895,596 | pass |
| run-002 | warmup | 6 | 6 | 5 | 189,584 | — |
| run-002 | generation | 5 | 5 | 4 | 229,929 | pass |
| run-002 | baseline | 73 | 73 | 72 | 4,750,924 | pass |
| run-003 | warmup | 9 | 9 | 8 | 351,782 | — |
| run-003 | generation | 5 | 5 | 4 | 231,951 | pass |
| run-003 | baseline | 73 | 73 | 72 | 4,841,701 | pass |
| run-004 | warmup | 8 | 8 | 7 | 276,774 | — |
| run-004 | generation | 5 | 5 | 4 | 230,903 | pass |
| run-004 | baseline | 73 | 73 | 72 | 4,894,038 | pass |
| run-005 | warmup | 11 | 10 | 10 | 394,386 | — |
| run-005 | generation | 5 | 5 | 4 | 225,694 | pass |
| run-005 | baseline | 73 | 73 | 72 | 4,826,474 | pass |

## Caveats

- Five runs per cell on one day and a limited spec grid; no general savings or reliability estimate.
- The baseline is prompted to use Write per file; it can still emit multiple Write calls in one response.
- Fewer tool calls need not mean fewer model responses. Cache reads alone do not diagnose cache policy.
- Arms use different prompts; batches differ in concurrency and warm-up briefs. This is not a randomized causal experiment.
- A pass checks the compiler and the checked-in structural judge, not runtime semantics.
- Failed judgments remain in means. Missing or inconsistent source evidence causes recomputation to fail.
- New runs use today's configured tools and service behavior; they cannot recreate the historical environment exactly.
