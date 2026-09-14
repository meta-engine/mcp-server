# MetaEngine MCP — Benchmark Summary

Experiment: `ts-monolith-opus-inline`. Means [min–max]; all recorded runs, including failed judgments.

Regenerated from original streams with measurement schema 2. Historical result.json files
remain unchanged; their legacy visible/thinking decomposition must not be used.

## Generation with a prepared brief

The assisted generation session receives the separate warm-up's brief in its prompt.
This measures a prepared workflow; it does not simulate training or guarantee future cache state.

| Session | n | Assistant messages | Tool calls | Output tokens | Cache-read tokens | Pass |
| --- | --- | --- | --- | --- | --- | --- |
| generation | 5 | 5.2 [5.0–6.0] | 4.2 [4.0–5.0] | 20,410 [18,579–23,376] | 243,271 [215,328–303,596] | 5/5 |
| baseline | 5 | 60.4 [9.0–81.0] | 71.6 [69.0–80.0] | 25,820 [22,914–29,214] | 3,935,365 [414,983–5,518,068] | 5/5 |
| warmup | 5 | 9.0 [8.0–10.0] | 8.0 [7.0–9.0] | 11,259 [10,233–12,186] | 331,404 [265,568–391,182] | — |

## Duration and recorded API-equivalent cost

These are the original result event's duration and cost fields. Cost is a dated
API-price calculation, not a subscription bill or a measure of subscription allowance.

| Session | Duration ms | Recorded cost USD |
| --- | --- | --- |
| generation | 186,734 [171,917–224,604] | 1.3618 [1.3014–1.4350] |
| baseline | 315,899 [234,178–357,289] | 3.2402 [2.1219–4.1152] |
| warmup | 158,546 [144,072–171,039] | 0.9012 [0.8856–0.9162] |

Warm-up plus generation, per paired run:

- Output tokens: 31,669 [30,716–33,609]
- Summed session duration ms: 345,280 [335,145–368,676]
- Recorded cost USD: 2.2629 [2.2176–2.3254]

## Observable content size

Characters count text blocks and Python's sorted-key JSON serialization of tool input
(`json.dumps`, default escaping and spacing). They are not token counts or wire bytes.
Assistant-event usage is not a visible-text token measurement. No thinking-token residual is inferred.

| Session | Text characters | Tool-input characters |
| --- | --- | --- |
| generation | 123 [4–220] | 30,175 [30,112–30,362] |
| baseline | 300 [125–548] | 34,206 [31,202–44,185] |
| warmup | 68 [11–215] | 26,242 [23,539–28,041] |

## Per-run message and call counts

`assistant_messages` counts distinct assistant message IDs; multiple tool blocks may
share one message. It is a trace-observed response count, not a count of invisible retries.
In these traces the CLI's `num_turns` equals tool calls plus one; it is retained separately.

| Run | Session | CLI num_turns | Assistant messages | Tool calls | Cache-read tokens | Verdict |
| --- | --- | --- | --- | --- | --- | --- |
| run-001 | warmup | 8 | 8 | 7 | 265,568 | — |
| run-001 | generation | 5 | 5 | 4 | 215,328 | pass |
| run-001 | baseline | 71 | 71 | 70 | 4,481,690 | pass |
| run-002 | warmup | 9 | 9 | 8 | 341,593 | — |
| run-002 | generation | 5 | 5 | 4 | 231,132 | pass |
| run-002 | baseline | 71 | 71 | 70 | 4,665,776 | pass |
| run-003 | warmup | 8 | 8 | 7 | 268,260 | — |
| run-003 | generation | 5 | 5 | 4 | 235,590 | pass |
| run-003 | baseline | 81 | 81 | 80 | 5,518,068 | pass |
| run-004 | warmup | 10 | 10 | 9 | 390,418 | — |
| run-004 | generation | 5 | 5 | 4 | 230,709 | pass |
| run-004 | baseline | 70 | 9 | 69 | 414,983 | pass |
| run-005 | warmup | 10 | 10 | 9 | 391,182 | — |
| run-005 | generation | 6 | 6 | 5 | 303,596 | pass |
| run-005 | baseline | 70 | 70 | 69 | 4,596,310 | pass |

## Caveats

- Five runs per cell on one day and a limited spec grid; no general savings or reliability estimate.
- The baseline is prompted to use Write per file; it can still emit multiple Write calls in one response.
- Fewer tool calls need not mean fewer model responses. Cache reads alone do not diagnose cache policy.
- Arms use different prompts; batches differ in concurrency and warm-up briefs. This is not a randomized causal experiment.
- A pass checks the compiler and the checked-in structural judge, not runtime semantics.
- Failed judgments remain in means. Missing or inconsistent source evidence causes recomputation to fail.
- New runs use today's configured tools and service behavior; they cannot recreate the historical environment exactly.
