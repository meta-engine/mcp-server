# MetaEngine MCP — Benchmark Summary

Experiment: `python-multilang`. Means [min–max]; all recorded runs, including failed judgments.

Regenerated from original streams with measurement schema 2. Historical result.json files
remain unchanged; their legacy visible/thinking decomposition must not be used.

## Generation with a prepared brief

The assisted generation session receives the separate warm-up's brief in its prompt.
This measures a prepared workflow; it does not simulate training or guarantee future cache state.

| Session | n | Assistant messages | Tool calls | Output tokens | Cache-read tokens | Pass |
| --- | --- | --- | --- | --- | --- | --- |
| generation | 5 | 6.6 [5.0–12.0] | 5.6 [4.0–11.0] | 23,131 [18,820–27,932] | 365,379 [200,821–861,406] | 5/5 |
| baseline | 5 | 22.6 [6.0–74.0] | 72.8 [72.0–73.0] | 23,236 [20,982–24,907] | 1,334,301 [101,982–4,656,121] | 5/5 |
| warmup | 5 | 12.2 [9.0–21.0] | 14.0 [8.0–34.0] | 12,601 [10,576–16,235] | 522,698 [320,884–1,106,168] | — |

## Duration and recorded API-equivalent cost

These are the original result event's duration and cost fields. Cost is a dated
API-price calculation, not a subscription bill or a measure of subscription allowance.

| Session | Duration ms | Recorded cost USD |
| --- | --- | --- |
| generation | 195,407 [149,061–252,710] | 1.6082 [1.2849–2.1758] |
| baseline | 206,021 [152,054–306,711] | 1.8789 [1.2869–3.3044] |
| warmup | 190,171 [152,280–261,458] | 1.0838 [0.8293–1.5765] |

Warm-up plus generation, per paired run:

- Output tokens: 35,732 [30,327–40,804]
- Summed session duration ms: 385,578 [311,552–437,495]
- Recorded cost USD: 2.6919 [2.2683–3.1863]

## Observable content size

Characters count text blocks and Python's sorted-key JSON serialization of tool input
(`json.dumps`, default escaping and spacing). They are not token counts or wire bytes.
Assistant-event usage is not a visible-text token measurement. No thinking-token residual is inferred.

| Session | Text characters | Tool-input characters |
| --- | --- | --- |
| generation | 173 [70–281] | 38,922 [35,773–50,385] |
| baseline | 246 [89–428] | 44,196 [40,374–48,394] |
| warmup | 305 [234–502] | 27,602 [24,735–29,623] |

## Per-run message and call counts

`assistant_messages` counts distinct assistant message IDs; multiple tool blocks may
share one message. It is a trace-observed response count, not a count of invisible retries.
In these traces the CLI's `num_turns` equals tool calls plus one; it is retained separately.

| Run | Session | CLI num_turns | Assistant messages | Tool calls | Cache-read tokens | Verdict |
| --- | --- | --- | --- | --- | --- | --- |
| run-001 | warmup | 11 | 11 | 10 | 434,399 | — |
| run-001 | generation | 12 | 12 | 11 | 861,406 | pass |
| run-001 | baseline | 74 | 74 | 73 | 4,656,121 | pass |
| run-002 | warmup | 35 | 21 | 34 | 1,106,168 | — |
| run-002 | generation | 5 | 5 | 4 | 223,933 | pass |
| run-002 | baseline | 74 | 11 | 73 | 636,831 | pass |
| run-003 | warmup | 10 | 10 | 9 | 374,767 | — |
| run-003 | generation | 6 | 6 | 5 | 329,913 | pass |
| run-003 | baseline | 74 | 11 | 73 | 645,143 | pass |
| run-004 | warmup | 10 | 10 | 9 | 377,271 | — |
| run-004 | generation | 5 | 5 | 4 | 200,821 | pass |
| run-004 | baseline | 74 | 11 | 73 | 631,429 | pass |
| run-005 | warmup | 9 | 9 | 8 | 320,884 | — |
| run-005 | generation | 5 | 5 | 4 | 210,824 | pass |
| run-005 | baseline | 73 | 6 | 72 | 101,982 | pass |

## Caveats

- Five runs per cell on one day and a limited spec grid; no general savings or reliability estimate.
- The baseline is prompted to use Write per file; it can still emit multiple Write calls in one response.
- Fewer tool calls need not mean fewer model responses. Cache reads alone do not diagnose cache policy.
- Arms use different prompts; batches differ in concurrency and warm-up briefs. This is not a randomized causal experiment.
- A pass checks the compiler and the checked-in structural judge, not runtime semantics.
- Failed judgments remain in means. Missing or inconsistent source evidence causes recomputation to fail.
- New runs use today's configured tools and service behavior; they cannot recreate the historical environment exactly.
