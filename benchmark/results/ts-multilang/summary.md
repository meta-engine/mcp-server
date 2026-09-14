# MetaEngine MCP — Benchmark Summary

Experiment: `ts-multilang`. Means [min–max]; all recorded runs, including failed judgments.

Regenerated from original streams with measurement schema 2. Historical result.json files
remain unchanged; their legacy visible/thinking decomposition must not be used.

## Generation with a prepared brief

The assisted generation session receives the separate warm-up's brief in its prompt.
This measures a prepared workflow; it does not simulate training or guarantee future cache state.

| Session | n | Assistant messages | Tool calls | Output tokens | Cache-read tokens | Pass |
| --- | --- | --- | --- | --- | --- | --- |
| generation | 5 | 5.0 [5.0–5.0] | 4.0 [4.0–4.0] | 18,872 [16,940–20,817] | 231,174 [227,200–236,987] | 4/5 |
| baseline | 5 | 76.4 [73.0–82.0] | 75.4 [72.0–81.0] | 21,007 [19,621–22,922] | 4,799,141 [4,433,818–5,367,525] | 5/5 |
| warmup | 5 | 8.2 [5.0–10.0] | 7.2 [4.0–9.0] | 12,436 [11,274–14,776] | 317,125 [176,846–395,225] | — |

## Duration and recorded API-equivalent cost

These are the original result event's duration and cost fields. Cost is a dated
API-price calculation, not a subscription bill or a measure of subscription allowance.

| Session | Duration ms | Recorded cost USD |
| --- | --- | --- |
| generation | 158,107 [140,026–173,546] | 1.3176 [1.2472–1.3583] |
| baseline | 275,736 [258,112–306,329] | 3.4335 [3.1131–3.9019] |
| warmup | 175,870 [161,060–206,488] | 0.9280 [0.7205–1.0283] |

Warm-up plus generation, per paired run:

- Output tokens: 31,308 [28,214–32,610]
- Summed session duration ms: 333,978 [305,439–355,906]
- Recorded cost USD: 2.2456 [1.9676–2.3866]

## Observable content size

Characters count text blocks and Python's sorted-key JSON serialization of tool input
(`json.dumps`, default escaping and spacing). They are not token counts or wire bytes.
Assistant-event usage is not a visible-text token measurement. No thinking-token residual is inferred.

| Session | Text characters | Tool-input characters |
| --- | --- | --- |
| generation | 170 [81–213] | 34,446 [33,967–34,667] |
| baseline | 82 [73–94] | 34,267 [30,312–38,997] |
| warmup | 156 [85–312] | 28,808 [26,821–33,543] |

## Per-run message and call counts

`assistant_messages` counts distinct assistant message IDs; multiple tool blocks may
share one message. It is a trace-observed response count, not a count of invisible retries.
In these traces the CLI's `num_turns` equals tool calls plus one; it is retained separately.

| Run | Session | CLI num_turns | Assistant messages | Tool calls | Cache-read tokens | Verdict |
| --- | --- | --- | --- | --- | --- | --- |
| run-001 | warmup | 10 | 10 | 9 | 395,225 | — |
| run-001 | generation | 5 | 5 | 4 | 236,987 | tsc_errors |
| run-001 | baseline | 81 | 81 | 80 | 5,241,189 | pass |
| run-002 | warmup | 9 | 9 | 8 | 341,225 | — |
| run-002 | generation | 5 | 5 | 4 | 229,241 | pass |
| run-002 | baseline | 82 | 82 | 81 | 5,367,525 | pass |
| run-003 | warmup | 10 | 10 | 9 | 381,485 | — |
| run-003 | generation | 5 | 5 | 4 | 232,564 | pass |
| run-003 | baseline | 73 | 73 | 72 | 4,460,826 | pass |
| run-004 | warmup | 7 | 7 | 6 | 290,842 | — |
| run-004 | generation | 5 | 5 | 4 | 229,878 | pass |
| run-004 | baseline | 73 | 73 | 72 | 4,492,347 | pass |
| run-005 | warmup | 5 | 5 | 4 | 176,846 | — |
| run-005 | generation | 5 | 5 | 4 | 227,200 | pass |
| run-005 | baseline | 73 | 73 | 72 | 4,433,818 | pass |

## Caveats

- Five runs per cell on one day and a limited spec grid; no general savings or reliability estimate.
- The baseline is prompted to use Write per file; it can still emit multiple Write calls in one response.
- Fewer tool calls need not mean fewer model responses. Cache reads alone do not diagnose cache policy.
- Arms use different prompts; batches differ in concurrency and warm-up briefs. This is not a randomized causal experiment.
- A pass checks the compiler and the checked-in structural judge, not runtime semantics.
- Failed judgments remain in means. Missing or inconsistent source evidence causes recomputation to fail.
- New runs use today's configured tools and service behavior; they cannot recreate the historical environment exactly.
