# Canonical results

These are the 15 result folders that produced the numbers in [`../FINDINGS.md`](../FINDINGS.md). Each folder has a `summary.md` (aggregate report) and `run-NNN/<variant>/output/` (actual generated code per iteration).

| Friendly name | Original timestamp | What it shows |
|---|---|---|
| [`ts-multilang/`](ts-multilang/summary.md) | `20260426-015434` | TypeScript topology (a-mcp vs baseline), N=5 PARALLEL=2 |
| [`java-multilang/`](java-multilang/summary.md) | `20260426-030529-java` | Java topology, N=5 PARALLEL=2 |
| [`python-multilang/`](python-multilang/summary.md) | `20260426-041747-python` | Python topology, N=5 PARALLEL=2 |
| [`ts-invocation-inline/`](ts-invocation-inline/summary.md) | `20260426-103402-typescript-inline` | TS inline arm, N=5 PARALLEL=5 |
| [`ts-invocation-heredoc/`](ts-invocation-heredoc/summary.md) | `20260426-104532-typescript-heredoc` | TS heredoc arm (retired methodological control), N=5 PARALLEL=5 |
| [`ts-invocation-script/`](ts-invocation-script/summary.md) | `20260426-105828-typescript-script` | TS script arm, N=5 PARALLEL=5 |
| [`java-invocation-inline/`](java-invocation-inline/summary.md) | `20260426-111807-java-inline` | Java inline arm, N=5 PARALLEL=5 |
| [`java-invocation-script/`](java-invocation-script/summary.md) | `20260426-113002-java-script` | Java script arm, N=5 PARALLEL=5 |
| [`python-invocation-script/`](python-invocation-script/summary.md) | `20260426-115000-python-script` | Python script arm, N=5 PARALLEL=5 |
| [`ts-inline-sonnet/`](ts-inline-sonnet/summary.md) | `20260426-154711-typescript-inline-sonnet` | TS inline arm on Sonnet 4.6, N=5 **PARALLEL=1** |
| [`ts-script-sonnet/`](ts-script-sonnet/summary.md) | `20260426-182553-typescript-script-sonnet` | TS script arm on Sonnet 4.6, N=5 **PARALLEL=1** |
| [`ts-monolith-opus-inline/`](ts-monolith-opus-inline/summary.md) | `20260426-202822-typescript-inline-monolith` | TS inline arm, **modular-monolith spec**, Opus 4.7, N=5 PARALLEL=2 |
| [`ts-monolith-opus-script/`](ts-monolith-opus-script/summary.md) | `20260426-210323-typescript-script-monolith` | TS script arm, modular-monolith spec, Opus 4.7, N=5 PARALLEL=2 |
| [`ts-monolith-sonnet-inline/`](ts-monolith-sonnet-inline/summary.md) | `20260426-213406-typescript-inline-sonnet-monolith` | TS inline arm, modular-monolith spec, Sonnet 4.6, N=5 PARALLEL=1 |
| [`ts-monolith-sonnet-script/`](ts-monolith-sonnet-script/summary.md) | `20260426-223154-typescript-script-sonnet-monolith` | TS script arm, modular-monolith spec, Sonnet 4.6, N=5 PARALLEL=1 |

## Reading the evidence

The inventory above preserves the original experiment names and timestamps. `canonical.json` provides the same model/concurrency/shape information to the recomputation pipeline. `corrected-results.json` is the measurement-schema-2 view, rebuilt from source streams with their hashes.

Python's inline comparison uses `python-multilang/`; its script cell used different concurrency. The TypeScript multilang cell used two concurrent iterations, and its invocation cells used five. Sonnet cells were serial. These differences should be disclosed, not assumed to isolate cache effects.

The original interpretation confused CLI `num_turns` with model responses. Sonnet's low cache-read totals coincide with batched Writes in very few assistant responses; the traces do not establish a cache-policy anomaly. See [the correction and definitions](../FINDINGS.md).

Only the 15 canonical experiments are included; smoke, interrupted and discarded development runs are not part of this collection. Within each canonical cell, failed judge verdicts remain in the means. This selection and the small sample constrain generalization.

Regenerate the summaries and corrected JSON with `python3 tools/recompute.py` from the benchmark directory. Check for drift with `--check`. Original streams, generated artifacts and historical `result.json` files remain unchanged, including their obsolete derived measurement fields.
