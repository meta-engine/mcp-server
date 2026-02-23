# MetaEngine MCP Server

[![npm version](https://img.shields.io/npm/v/@metaengine/mcp-server.svg)](https://www.npmjs.com/package/@metaengine/mcp-server)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![MCP](https://img.shields.io/badge/MCP-Compatible-green)](https://modelcontextprotocol.io)

**Model Context Protocol server for AI-assisted code generation across 10 languages.**

Turn one conversation into 50 consistent files. Claude architects, MetaEngine builds.

---

## Quick Links

- **NPM Package**: [@metaengine/mcp-server](https://www.npmjs.com/package/@metaengine/mcp-server)
- **Website**: [metaengine.eu/mcp](https://www.metaengine.eu/mcp)
- **Playground**: [metaengine.eu/playground](https://www.metaengine.eu/playground)

---

## Installation

Add to `~/.claude/mcp.json` (Claude Code) or Claude Desktop config:

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

## What It Does

MetaEngine is a specialized tool for AI assistants like Claude Code and Claude Desktop. Instead of generating files one by one, you describe what you need in natural language—Claude constructs the type specifications, and MetaEngine generates all files instantly with perfect imports and namespaces.

### When Claude Uses This Tool

- Generating **20-100 interconnected files** where consistency matters
- **Multi-language projects** (same architecture in TypeScript, Python, Go, C#, Java, Kotlin, Groovy, Scala, Swift, PHP)
- **Pattern multiplication** (same structure applied to many entities)
- Complex **import management** across deep namespaces

### When Claude Generates Directly

- **1-15 files** — direct generation is faster for small tasks
- **Exploratory coding** where structure is evolving
- **One-off scripts** and utilities
- **Rapid prototyping** where flexibility beats consistency

Both approaches are valid. Claude picks the right tool for the job.

---

## Supported Languages

- TypeScript
- Python
- Go
- C#
- Java
- Kotlin
- Groovy
- Scala
- Swift
- PHP

Each generates idiomatic code (data classes in Kotlin, case classes in Scala, structs in Swift, etc.)

---

## Performance

- **Instant generation** — 25-100 files in one call
- **3.8x faster** than file-by-file generation at scale
- **57% fewer tokens** — compact spec vs full file text

The tipping point is around 20 files—below that, Claude's direct generation is simpler.

---

## Documentation

The AI guide is automatically embedded in the tool description on first use — no manual reading required. For reference:

- **METAENGINE_AI_GUIDE.md** — Critical rules, patterns, language notes, and common mistakes
- **EXAMPLES.md** — Real-world usage with input/output across all languages

---

## Privacy & Pricing

- **Free** — no API key, no signup, unlimited requests
- **Private** — specs sent for generation are never saved or logged (see [PRIVACY.md](./PRIVACY.md))
- **Local** — MCP server runs on your machine, MIT licensed
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
