# MetaEngine MCP — Agent-Loop Measurement Harness

This harness compares a prompted `Write`-per-file workflow with MetaEngine generation, then compares inline JSON with a transformer that writes generator input to a file. It includes original traces, prompts, generated code and judge results from 15 experiments, with five runs per cell on 2026-04-26.

**Tool calls and model responses are different measurements.** A model can request many Writes in one response. The [findings](FINDINGS.md) explain a correction discovered while auditing the traces: the CLI's `num_turns` counted tool operations plus one in these runs, not model responses. Earlier narration/thinking token decompositions were also unsupported. Original evidence is preserved; corrected reports and figures use independently counted assistant messages and tool calls.

The transformer arm emitted fewer output tokens in the recorded TypeScript comparisons on both models. A reduction in model responses did not hold universally: Sonnet often batched the baseline writes into one response. These are observations from specified workflows, not general savings claims.

## Verify the historical measurements offline

Requires Python 3; no packages, model calls or server access:

```bash
cd benchmark
python3 tools/recompute.py --check
python3 -m unittest discover -s tests -v
```

To regenerate the corrected JSON and all canonical summaries:

```bash
python3 tools/recompute.py
```

`results/canonical.json` identifies the 15 experiments, including model, concurrency and shape. `results/corrected-results.json` stores the recomputed session measurements and SHA-256 hashes of their source streams. Missing or inconsistent evidence is an error; it is never silently reported as a zero-cost run.

`result.json` and `stream.ndjson` in the canonical run folders are historical evidence. Their original result totals remain valid inputs to this analysis, but the old derived `phases` and `measurement` fields must not be reused. The offline path reads the streams and verifies agreement with the stored result totals.

## Run a new experiment

A new experiment consumes Claude usage and uses the currently available package and hosted service. It does not recreate the historical service environment exactly. The scripts use `--dangerously-skip-permissions`; run them in an environment appropriate for executing the supplied prompts and generated code.

Prerequisites:

- An authenticated `claude` CLI.
- Node.js and `npx` for the MCP adapter and TypeScript compiler gate.
- Python 3; Java experiments additionally need `javac`.
- MetaEngine MCP registered in the Claude configuration used for the run:

```bash
claude mcp add metaengine npx -- -y @metaengine/mcp-server@latest
```

Use an explicit model when comparing experiments:

```bash
MODEL=claude-opus-4-7 RUNS=1 PARALLEL=1 ./run.sh
MODEL=claude-opus-4-7 RUNS=5 PARALLEL=2 ./run.sh
MODEL=claude-opus-4-7 ARM=script RUNS=5 PARALLEL=5 ./run.sh
MODEL=claude-sonnet-4-6 ARM=inline RUNS=5 PARALLEL=1 ./run.sh
```

Those identifiers describe the historical models; availability and service behavior can change. The first two commands use the inline arm; the third is the transformer arm. The invocation comparison used five concurrent runs in each arm, while the original multilang cells used two. The Sonnet cells ran serially. See [the experiment inventory](results/README.md).

Configuration:

| Variable | Meaning |
| --- | --- |
| `RUNS` | Iterations per variant; default 3. |
| `PARALLEL` | Concurrent iterations; default 1. Record it when comparing cells. |
| `LANGUAGE` | `typescript`, `java` or `python`; default TypeScript. |
| `ARM` | `inline`, `script` or TypeScript-only `heredoc`; default inline. |
| `MODEL` | Model identifier passed to Claude; unset means the local CLI default. |
| `SHAPE` | `ddd` or `monolith`; default ddd. |
| `SPEC` | Alternate source spec path. |

The assisted variant runs warm-up and generation as separate sessions. Its generated knowledge brief is included in the second prompt. The baseline runs once with an empty strict MCP configuration. The judge checks compilation (`tsc --strict`, `javac`, or Python `py_compile`) and selected structural properties; it does not prove runtime equivalence. Failed judge verdicts remain in the means. An interrupted or malformed session prevents a summary from being presented as complete.

New runs write `results/<timestamp>-<language>-<arm>/summary.md` and retain their streams and output folders. Generation-only results describe a prepared brief; read the warm-up-plus-generation totals for first use. Recorded dollar amounts are API-equivalent costs from that run, not a subscription bill or a direct measurement of subscription allowance.

## Regenerate figures

```bash
./tools/setup-charts.sh
./.venv/bin/python tools/plot.py
```

The figure script consumes the corrected JSON. Every comparison uses that cell's own baseline. It shows content characters separately from token totals; it never treats characters as an exact token decomposition.

## Layout

- `prompts/`: workflow instructions by language and shape.
- `spec/`: deterministic synthetic source specifications and generators.
- `tools/stream_metrics.py`: observable stream measurements.
- `tools/result_reader.py`: source consistency checks and session records.
- `tools/report.py`: per-experiment report rendering.
- `tools/recompute.py`: offline canonical regeneration and drift check.
- `tools/aggregate.py`: report one new experiment.
- `tools/judge.py`: compiler and structural checks.
- `results/`: original evidence, experiment inventory and corrected measurements.
- `figures/`: regenerable charts referenced by the findings.
- `tests/`: measurement regressions, including batched Writes and tool-only messages.

The useful next step is another experiment on your workload. This small sample does not establish general resource savings, reliability, cache policy, or performance at larger spec sizes.
