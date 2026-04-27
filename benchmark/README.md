# MetaEngine MCP — Agent-Loop Efficiency Harness

I'm a practitioner — I build MetaEngine — not a researcher. While testing the MCP server I noticed two patterns I find genuinely interesting: agents using the MCP show meaningfully shorter loops and lower derived cost than agents writing the same code by hand. I built this harness to share what I saw, and because I think the mechanisms might be worth other people looking at too.

**The harness is the contribution. The numbers come from N=5 runs per cell across a grid of three languages (TS / Java / Python), two models (Opus 4.7 / Sonnet 4.6), two spec shapes (uniform DDD / modular-monolith), and three invocation arms (inline / script / heredoc) — though not every combination in the grid is filled in.** They illustrate the patterns; they aren't claims about how much MetaEngine "saves." Run it yourself, on your own spec, with your own model — that's what would tell you whether the patterns hold for you.

## Two patterns, in one sentence each (plus one robustness note)

1. **Topology** — when an MCP returns many generated artifacts in one call, the agent loop runs ~11–15× shorter than a Write-tool loop emitting one file per turn. cache_read accumulation drops correspondingly.
2. **Invocation** — when an agent writes a transformer script that produces the MCP's input file at runtime instead of inlining the spec as tool arguments, output tokens drop ~70–77% and gen wall-clock roughly halves. This works because tool_use input bytes are billed as output tokens; routing data through disk avoids that billing channel.
3. **Robustness** — both patterns reproduce across TypeScript / Java / Python, across a model swap (Opus → Sonnet 4.6), and across a spec-shape swap (uniform DDD → modular-monolith with cross-module refs and shared kernel). Several priors I went in with turned out partial or wrong — Java and Python cost reductions were more workload-specific than expected, and the cross-model Sonnet inversion on the inline arm was sharper than predicted. The wrong-prior stories are documented in [`FINDINGS.md`](FINDINGS.md) rather than buried.

Numbers, mechanisms, and limits in [`FINDINGS.md`](FINDINGS.md). The invocation pattern comes with a precondition (the spec must be computable from a smaller source you already have); the topology pattern doesn't. The two-layer model that decomposes which findings survive a model swap and which don't is the framing I'd most like other people to take away — see the *Two-layer model* section in FINDINGS.

## How to reproduce

```bash
RUNS=1 ./run.sh                                                  # smoke: ~10 min, ~$5 on Opus 4.7
RUNS=5 PARALLEL=2 ./run.sh                                       # canonical TS inline: ~30 min, ~$28 on Opus 4.7
ARM=script LANGUAGE=python RUNS=5 PARALLEL=2 ./run.sh            # script arm on Python
```

> **About the dollar figures.** The "$N" amounts are token usage × Anthropic's *published API rates* (snapshot 2026-04-26) — they're a comparable, model-neutral measurement of work done. Claude Max / Pro subscribers pay flat-rate plans, not these numbers; this is not your actual bill. Use the dollar amounts to compare *between* variants — that comparison is what the harness measures. If you're a subscription user, the equivalent reading is "how much of your usage budget would each variant consume."

### What you'll see

After a smoke run, the auto-generated `results/<run>/summary.md` has a steady-state table that looks like:

```
| | output_tokens | cost USD | turns | cache_read | pass |
|---|---|---|---|---|---|
| a-mcp gen        |  18,872 | $1.32 |  5.0 |   231,174 | 4/5 |
| b-baseline       |  21,007 | $3.43 | 76.4 | 4,799,141 | 5/5 |
| **reduction**    | **10.2%** | **61.6%** | **15.3× fewer** | **95.2%** | — |
```

That's one canonical TS run. Read the **Caveats** section at the bottom of the same file before quoting anything. Eyeball `run-NNN/<variant>/output/` directly if you want to see the actual generated code — the report can lie.

Env vars:

- `RUNS=N` — iterations per variant (default 3).
- `PARALLEL=N` — concurrent runs (default 1).
  - `PARALLEL=2` is verified safe.
  - Higher values trade parallelism for cold-cache premium.
  - Rate limits become the binding constraint above 2–3.
- `LANGUAGE` — `typescript` | `java` | `python` (default `typescript`).
- `ARM` — `inline` (default) | `script` (recommended for cost-minimization) | `heredoc` (retired methodological control, kept callable for reproducibility).
- `MODEL` — leave unset for default; set to `sonnet` to reproduce the cross-model section.
- `SPEC` — alternate spec JSON.

After a run finishes:
- `results/<timestamp>-<lang>-<arm>/summary.md` — aggregate report (read the **Caveats** section)
- `results/<timestamp>-<lang>-<arm>/run-NNN/<variant>/output/` — actual generated code

To regenerate the charts in [`figures/`](figures/) after promoting a new experiment to `results/`:

```bash
./tools/setup-charts.sh                     # one-time: creates .venv, installs matplotlib
./.venv/bin/python ./tools/plot.py          # any time data changes
```

The charts are referenced inline from [`FINDINGS.md`](FINDINGS.md).

## Layout

```
benchmark/
├── README.md                       # this file
├── FINDINGS.md                     # the two observations + caveats + how to interpret
├── run.sh                          # orchestrator
├── spec/
│   ├── generate-spec.py            # deterministic 71-entity DDD spec generator
│   └── large.json                  # the spec used in every canonical run
├── prompts/<lang>/                 # typescript / java / python — same shape per language
│   ├── agent-a-mcp-warmup.md       # session 1: read MCP docs, write knowledge brief
│   ├── agent-a-mcp-gen-{inline,script,heredoc}.md   # session 2: gen via various invocation patterns
│   └── agent-b-baseline.md         # baseline: write each file via Write
├── tools/
│   ├── run-agent.sh                # orchestrates a-mcp two-session + baseline single-session
│   ├── parse-stream.py             # extracts authoritative totals from claude stream-json
│   ├── judge.py                    # structural verification + per-language compile gate
│   ├── judge.sh                    # wrapper around judge.py
│   ├── aggregate.py                # report generation
│   ├── setup-charts.sh             # one-time chart venv setup (matplotlib)
│   └── plot.py                     # regenerable chart pipeline (reads results/, writes figures/)
├── figures/                        # charts referenced from FINDINGS.md, regenerable
│   ├── headline-absolute.png       # MCP vs traditional Write loop, absolute numbers
│   ├── cross-model-reductions.png  # same data as %-reduction
│   ├── cross-shape-reductions.png  # DDD vs modular-monolith %-reduction per (model, arm)
│   ├── multilang-topology.png      # Opus TS / Java / Python a-mcp vs baseline
│   ├── output-decomposition.png    # where the bytes go (visible / tool_input / thinking)
│   └── baseline-cache-per-run.png  # Sonnet cache anomaly, log-scale
└── results/                        # the 15 canonical runs that produced the numbers in FINDINGS
    ├── README.md                   # mapping friendly names → original timestamps
    ├── ts-multilang/               # topology comparison (a-mcp vs baseline) on TypeScript
    ├── java-multilang/             # topology comparison on Java
    ├── python-multilang/           # topology comparison on Python
    ├── ts-invocation-{inline,script,heredoc}/   # three-arm invocation experiment, TypeScript
    ├── java-invocation-{inline,script}/         # cross-language script reproduction, Java
    ├── python-invocation-script/                # cross-language script reproduction, Python
    ├── ts-{inline,script}-sonnet/               # cross-model reproduction on Sonnet 4.6
    └── ts-monolith-{opus,sonnet}-{inline,script}/   # cross-shape reproduction (modular-monolith)
```

## Prerequisites

- `claude` CLI authenticated (`claude --version`)
- MetaEngine MCP configured (`claude mcp list`):
  ```bash
  claude mcp add metaengine npx -- -y @metaengine/mcp-server@latest
  ```
- `python3` (stdlib only — no extra deps)
- `npx` (for the TypeScript compile gate; `javac` for Java; `python3 -m py_compile` for Python)

The harness uses your default MCP config for `a-mcp`; `b-baseline` uses `--strict-mcp-config` with an empty config to guarantee no MCP access.

## What I'm not claiming

- That MetaEngine is X% cheaper than Y. The numbers are what one author saw on one day on one workload.
- That this generalizes to any spec, any language, any model. The harness covers two spec shapes (DDD + modular-monolith), three languages (TS / Java / Python), and two models (Opus 4.7 / Sonnet 4.6) at N=5 per cell — not every combination is filled in, and N=5 isn't enough to put confidence intervals on most cell-level numbers.
- That the patterns are mine to prove. I'm sharing what I noticed because the mechanisms (turns × cumulative re-read; tool_use bytes as output tokens) seem structural enough that others might find them worth testing too.

If any of this looks worth investigating further, the harness is here for you to fork. If you reproduce, falsify, or measure something that contradicts what's here, I'd genuinely like to know — disagreement is more useful to me than confirmation.
