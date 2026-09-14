# MetaEngine MCP — Benchmark Summary

Experiment: `ts-invocation-script`. Means [min–max]; all recorded runs, including failed judgments.

Regenerated from original streams with measurement schema 2. Historical result.json files
remain unchanged; their legacy visible/thinking decomposition must not be used.

## Generation with a prepared brief

The assisted generation session receives the separate warm-up's brief in its prompt.
This measures a prepared workflow; it does not simulate training or guarantee future cache state.

| Session | n | Assistant messages | Tool calls | Output tokens | Cache-read tokens | Pass |
| --- | --- | --- | --- | --- | --- | --- |
| generation | 5 | 6.8 [6.0–10.0] | 5.8 [5.0–9.0] | 4,691 [3,247–5,742] | 307,669 [271,891–421,262] | 4/5 |
| baseline | 5 | 73.0 [73.0–73.0] | 72.0 [72.0–72.0] | 21,353 [20,630–21,870] | 4,654,118 [4,603,017–4,690,710] | 5/5 |
| warmup | 5 | 8.8 [7.0–10.0] | 7.8 [6.0–9.0] | 11,283 [9,428–12,947] | 332,208 [223,250–396,531] | — |

## Duration and recorded API-equivalent cost

These are the original result event's duration and cost fields. Cost is a dated
API-price calculation, not a subscription bill or a measure of subscription allowance.

| Session | Duration ms | Recorded cost USD |
| --- | --- | --- |
| generation | 70,229 [54,446–93,840] | 0.8935 [0.7632–0.9796] |
| baseline | 290,456 [268,669–305,196] | 3.2661 [3.2123–3.2941] |
| warmup | 159,827 [145,421–182,443] | 0.9099 [0.7469–1.0243] |

Warm-up plus generation, per paired run:

- Output tokens: 15,974 [14,227–18,689]
- Summed session duration ms: 230,056 [204,784–276,283]
- Recorded cost USD: 1.8034 [1.6523–2.0039]

## Observable content size

Characters count text blocks and Python's sorted-key JSON serialization of tool input
(`json.dumps`, default escaping and spacing). They are not token counts or wire bytes.
Assistant-event usage is not a visible-text token measurement. No thinking-token residual is inferred.

| Session | Text characters | Tool-input characters |
| --- | --- | --- |
| generation | 129 [56–239] | 5,337 [4,663–6,279] |
| baseline | 93 [67–114] | 31,910 [31,740–32,115] |
| warmup | 35 [11–130] | 26,633 [22,758–30,116] |

## Per-run message and call counts

`assistant_messages` counts distinct assistant message IDs; multiple tool blocks may
share one message. It is a trace-observed response count, not a count of invisible retries.
In these traces the CLI's `num_turns` equals tool calls plus one; it is retained separately.

| Run | Session | CLI num_turns | Assistant messages | Tool calls | Cache-read tokens | Verdict |
| --- | --- | --- | --- | --- | --- | --- |
| run-001 | warmup | 8 | 8 | 7 | 298,826 | — |
| run-001 | generation | 6 | 6 | 5 | 271,891 | pass |
| run-001 | baseline | 73 | 73 | 72 | 4,645,221 | pass |
| run-002 | warmup | 10 | 10 | 9 | 396,531 | — |
| run-002 | generation | 6 | 6 | 5 | 287,447 | compile_errors |
| run-002 | baseline | 73 | 73 | 72 | 4,654,983 | pass |
| run-003 | warmup | 9 | 9 | 8 | 351,479 | — |
| run-003 | generation | 6 | 6 | 5 | 275,001 | pass |
| run-003 | baseline | 73 | 73 | 72 | 4,603,017 | pass |
| run-004 | warmup | 10 | 10 | 9 | 390,953 | — |
| run-004 | generation | 10 | 10 | 9 | 421,262 | pass |
| run-004 | baseline | 73 | 73 | 72 | 4,690,710 | pass |
| run-005 | warmup | 7 | 7 | 6 | 223,250 | — |
| run-005 | generation | 6 | 6 | 5 | 282,745 | pass |
| run-005 | baseline | 73 | 73 | 72 | 4,676,660 | pass |

## Caveats

- Five runs per cell on one day and a limited spec grid; no general savings or reliability estimate.
- The baseline is prompted to use Write per file; it can still emit multiple Write calls in one response.
- Fewer tool calls need not mean fewer model responses. Cache reads alone do not diagnose cache policy.
- Arms use different prompts; batches differ in concurrency and warm-up briefs. This is not a randomized causal experiment.
- A pass checks the compiler and the checked-in structural judge, not runtime semantics.
- Failed judgments remain in means. Missing or inconsistent source evidence causes recomputation to fail.
- New runs use today's configured tools and service behavior; they cannot recreate the historical environment exactly.
