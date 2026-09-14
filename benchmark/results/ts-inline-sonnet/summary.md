# MetaEngine MCP — Benchmark Summary

Experiment: `ts-inline-sonnet`. Means [min–max]; all recorded runs, including failed judgments.

Regenerated from original streams with measurement schema 2. Historical result.json files
remain unchanged; their legacy visible/thinking decomposition must not be used.

## Generation with a prepared brief

The assisted generation session receives the separate warm-up's brief in its prompt.
This measures a prepared workflow; it does not simulate training or guarantee future cache state.

| Session | n | Assistant messages | Tool calls | Output tokens | Cache-read tokens | Pass |
| --- | --- | --- | --- | --- | --- | --- |
| generation | 5 | 5.0 [5.0–5.0] | 4.0 [4.0–4.0] | 21,299 [17,474–31,142] | 225,230 [219,366–233,480] | 3/5 |
| baseline | 5 | 3.2 [3.0–4.0] | 72.0 [72.0–72.0] | 16,280 [15,258–18,568] | 48,484 [46,054–58,205] | 5/5 |
| warmup | 5 | 5.6 [5.0–6.0] | 4.6 [4.0–5.0] | 8,921 [6,704–10,079] | 146,879 [111,719–167,725] | — |

## Duration and recorded API-equivalent cost

These are the original result event's duration and cost fields. Cost is a dated
API-price calculation, not a subscription bill or a measure of subscription allowance.

| Session | Duration ms | Recorded cost USD |
| --- | --- | --- |
| generation | 214,860 [173,965–271,056] | 0.6296 [0.5561–0.8160] |
| baseline | 148,089 [121,419–193,327] | 0.5863 [0.5434–0.6815] |
| warmup | 152,536 [124,139–164,628] | 0.2961 [0.2152–0.3309] |

Warm-up plus generation, per paired run:

- Output tokens: 30,220 [26,443–39,954]
- Summed session duration ms: 367,396 [324,794–435,684]
- Recorded cost USD: 0.9257 [0.8194–1.1241]

## Observable content size

Characters count text blocks and Python's sorted-key JSON serialization of tool input
(`json.dumps`, default escaping and spacing). They are not token counts or wire bytes.
Assistant-event usage is not a visible-text token measurement. No thinking-token residual is inferred.

| Session | Text characters | Tool-input characters |
| --- | --- | --- |
| generation | 429 [285–544] | 34,750 [34,694–34,923] |
| baseline | 168 [81–358] | 35,022 [34,780–35,517] |
| warmup | 412 [195–615] | 28,781 [22,942–31,929] |

## Per-run message and call counts

`assistant_messages` counts distinct assistant message IDs; multiple tool blocks may
share one message. It is a trace-observed response count, not a count of invisible retries.
In these traces the CLI's `num_turns` equals tool calls plus one; it is retained separately.

| Run | Session | CLI num_turns | Assistant messages | Tool calls | Cache-read tokens | Verdict |
| --- | --- | --- | --- | --- | --- | --- |
| run-001 | warmup | 5 | 5 | 4 | 111,719 | — |
| run-001 | generation | 5 | 5 | 4 | 219,366 | pass |
| run-001 | baseline | 73 | 3 | 72 | 46,054 | pass |
| run-002 | warmup | 6 | 6 | 5 | 167,725 | — |
| run-002 | generation | 5 | 5 | 4 | 226,837 | missing_entities |
| run-002 | baseline | 73 | 4 | 72 | 58,205 | pass |
| run-003 | warmup | 6 | 6 | 5 | 165,987 | — |
| run-003 | generation | 5 | 5 | 4 | 233,480 | pass |
| run-003 | baseline | 73 | 3 | 72 | 46,054 | pass |
| run-004 | warmup | 5 | 5 | 4 | 121,324 | — |
| run-004 | generation | 5 | 5 | 4 | 220,171 | missing_entities |
| run-004 | baseline | 73 | 3 | 72 | 46,054 | pass |
| run-005 | warmup | 6 | 6 | 5 | 167,641 | — |
| run-005 | generation | 5 | 5 | 4 | 226,297 | pass |
| run-005 | baseline | 73 | 3 | 72 | 46,054 | pass |

## Caveats

- Five runs per cell on one day and a limited spec grid; no general savings or reliability estimate.
- The baseline is prompted to use Write per file; it can still emit multiple Write calls in one response.
- Fewer tool calls need not mean fewer model responses. Cache reads alone do not diagnose cache policy.
- Arms use different prompts; batches differ in concurrency and warm-up briefs. This is not a randomized causal experiment.
- A pass checks the compiler and the checked-in structural judge, not runtime semantics.
- Failed judgments remain in means. Missing or inconsistent source evidence causes recomputation to fail.
- New runs use today's configured tools and service behavior; they cannot recreate the historical environment exactly.
