# MetaEngine MCP Server

[![npm version](https://img.shields.io/npm/v/@metaengine/mcp-server.svg)](https://www.npmjs.com/package/@metaengine/mcp-server)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![MCP](https://img.shields.io/badge/MCP-Compatible-green)](https://modelcontextprotocol.io)

**Code generation, handed to your agent.**

MetaEngine exposes its code-generation platform — spec converters for OpenAPI, GraphQL, Protobuf, and SQL, plus a batch type generator — as Model Context Protocol tools. Connect the server to Claude Code, Claude Desktop, Cursor, Cline, or any MCP-aware assistant, and *"regenerate my billing client from the new OpenAPI spec"* becomes a real, typed, ready-to-commit diff.

Listed on the [official MCP Registry](https://registry.modelcontextprotocol.io) as `eu.metaengine/mcp-server`.

---

## Quick Links

- **npm package**: [@metaengine/mcp-server](https://www.npmjs.com/package/@metaengine/mcp-server)
- **Website & docs**: [metaengine.eu/mcp](https://www.metaengine.eu/mcp)
- **Playground**: [metaengine.eu/playground](https://www.metaengine.eu/playground)

---

## Installation

Claude Code:

```bash
claude mcp add metaengine -- npx -y @metaengine/mcp-server
```

Claude Desktop, Cursor, Cline, or any other MCP client — add to the client's MCP config (`claude_desktop_config.json`, `.cursor/mcp.json`, …):

```json
{
  "mcpServers": {
    "metaengine": {
      "command": "npx",
      "args": ["-y", "@metaengine/mcp-server"]
    }
  }
}
```

That's it. No API key, no signup, free to use.

---

## Tools

Seven tools. One call each. Plain text back.

| Tool | What it does |
| --- | --- |
| `generate_openapi` | Typed HTTP client from an OpenAPI 3.x document, passed inline or by URL — 10 frameworks |
| `generate_graphql` | Typed client from a GraphQL SDL schema, optionally with reusable named fragments — 10 frameworks |
| `generate_protobuf` | Typed client from Protocol Buffers (`.proto`) definitions — 10 frameworks |
| `generate_sql` | Typed model classes from SQL DDL (`CREATE TABLE`), parsed dialect-agnostically — 11 languages |
| `generate_code` | Arbitrary type graphs (classes, interfaces, enums, generics) from one structured spec, with imports and cross-references resolved — 11 languages |
| `load_spec_from_file` | Runs a `generate_code` spec from disk, so multi-file architectures stay version-controlled and context usage drops to a file path |
| `metaengine_initialize` | Primes the agent before its first generation: patterns, examples, and language-specific rules |

Every call is stateless and self-contained: pass the spec inline (or by file path), pick a framework or language, get a write summary back as text. `dryRun` returns the generated contents inline instead of writing — ready to diff. `skipExisting` (default) protects files you've already customized.

---

## Spec-first development

Your specs are already the source of truth — the OpenAPI document, the GraphQL schema, the `.proto` files, the DDL. This server puts them to work inside the agent loop: when a spec changes, the agent regenerates the typed surface instead of hand-editing it.

- **4 source specs** — OpenAPI 3.x, GraphQL SDL, Protocol Buffers, SQL DDL
- **10 client frameworks** — Angular, React, TypeScript Fetch, Go net/http, Java Spring, Python httpx, C# HttpClient, Kotlin Ktor, Rust Reqwest, Swift URLSession
- **11 languages** for type and model generation — TypeScript, Python, Go, C#, Java, Kotlin, Groovy, Scala, Swift, PHP, Rust — each emitted idiomatically (data classes in Kotlin, case classes in Scala, structs in Swift and Rust)
- **Deterministic** — generation is byte-reproducible at a fixed engine version, so agents can retry without drift

The converters surfaced through MCP are the same compiler pipeline that powers the [MetaEngine Playground](https://www.metaengine.eu/playground): a spec is parsed, normalized to MetaEngine's intermediate representation, and emitted through a language-specific target. Versions stay in lockstep across surfaces.

For small tasks — a handful of files, exploratory code, one-off scripts — an agent's direct generation is simpler, and agents are told exactly that. The server earns its place when the work is spec-driven, polyglot, or structurally repetitive.

---

## Measured behavior in agent loops

Agents that batch through this MCP run with substantially fewer turns and lower cumulative context re-reads than a file-by-file `Write` loop (~5 turns vs ~75 for the same DDD codebase).

For reproducible measurements across languages, models, and spec shapes, see [`benchmark/`](./benchmark) — a self-contained harness with the prompts, judging tools, and 15 canonical result folders. Numbers there are illustrations from one author's runs at N=5 per cell; reproduce in your own environment to see what holds for you.

---

## Context Durability

In long-running sessions where context may be summarized (compaction), MetaEngine survives in three ways:

- **Short loop by design** — the MCP returns many files per call rather than per turn, so the conversation stays small enough that compaction is rarely triggered (~5 turns vs ~75 for file-by-file `Write` — see [benchmark](./benchmark) for measurements).
- **Recovery path** — the full AI guide is embedded in the tool description on first use; after a successful call, the description swaps to a short directive that points the assistant back at `metaengine_initialize`, which returns the guide content directly. If compaction wipes the guide, the breadcrumb is enough to reload it.
- **Disk-backed state** — when the spec is loaded via `load_spec_from_file`, it lives outside the conversation. A compacted (or fully reset) session can re-run the producing script and pick up without re-reading anything.

---

## Documentation

The AI guide is automatically embedded in the tool description on first use — no manual reading required. For reference:

- **METAENGINE_AI_GUIDE.md** — Critical rules, patterns, language notes, and common mistakes
- **EXAMPLES.md** — Real-world usage with input/output across all languages

---

## Privacy & Pricing

- **Free** — no API key, no signup, unlimited requests
- **Private** — specs sent for generation are never saved or logged (see [PRIVACY.md](./PRIVACY.md))
- **Local** — MCP server runs on your machine over stdio, MIT licensed
- **Terms** — See [TERMS.md](./TERMS.md) for usage terms

---

## Support

- **Issues**: [GitHub Issues](https://github.com/meta-engine/mcp-server/issues)
- **Email**: info@metaengine.eu
- **Website**: [metaengine.eu](https://www.metaengine.eu)

---

## License

MIT License - see [LICENSE](./LICENSE) file for details.

---

## About This Repository

This is the **documentation and issue tracking repository** for MetaEngine MCP Server. The compiled NPM package is available at [@metaengine/mcp-server](https://www.npmjs.com/package/@metaengine/mcp-server).

Source code is proprietary, but the MCP server is free to use under MIT license.
