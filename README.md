# MetaEngine MCP Server

[![npm version](https://img.shields.io/npm/v/@metaengine/mcp-server.svg)](https://www.npmjs.com/package/@metaengine/mcp-server)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Generate related source files from a type graph, a compact JSON recipe, or an API schema through your MCP client.

MetaEngine combines structured classes, interfaces, enums, collections, and generics with target-language code supplied in `customCode`. Explicit references connect that code to the same type graph, so the generator can resolve names and imports across the batch. Use it for models, services, adapters, or other structures you describe; the format does not prescribe an application architecture.

## Install

Node.js 18 or later is required. Add the server to your MCP client's configuration:

```json
{
  "mcpServers": {
    "metaengine": {
      "command": "npx",
      "args": ["-y", "@metaengine/mcp-server@1.5.0"]
    }
  }
}
```

For Claude Code:

```bash
claude mcp add metaengine -- npx -y @metaengine/mcp-server@1.5.0
```

The hosted service requires no API key or account. MCP clients include Claude Code, Claude Desktop, Cursor, Cline, and others with stdio support.

## Start with a recipe

Call `generate_from_recipe` with these arguments:

```json
{
  "recipe": {
    "recipeVersion": 1,
    "language": "typescript",
    "typeScriptOptions": { "relativeImportExtension": "js" },
    "classes": [
      { "name": "Customer", "id": "customer", "properties": { "id": "string", "name": "string" } },
      { "name": "Order", "properties": { "customer": { "ref": "customer" }, "total": "number", "note?": "string" } }
    ]
  },
  "outputPath": "src/models"
}
```

The local MCP server expands the recipe into the existing generation payload, sends that payload to the MetaEngine API, and writes the returned files. Add named templates and parameter rows when structures repeat. Existing `customCode`, `templateRefs`, imports, decorators, inheritance, and generic definitions remain available.

A version-controlled recipe can be invoked with `{"recipeFilePath":"specs/models.recipe.json"}`. Reading a file avoids resending its contents in the tool call. Files still need to be authored or maintained.

[Recipe grammar and examples](./RECIPES.md) · [Generation guide](./METAENGINE_AI_GUIDE.md) · [Language examples](./EXAMPLES.md)

## Tools

| Tool | Purpose |
| --- | --- |
| `generate_from_recipe` | Expand compact JSON fields, named templates, and local JSON input rows into the existing type graph, then generate files. |
| `generate_code` | Generate from the complete native JSON type graph, including arbitrary target-language code with explicit references. |
| `load_spec_from_file` | Read a native `generate_code` payload from a local JSON file. |
| `generate_openapi` | Generate a typed client from an OpenAPI document supplied inline or by URL. |
| `generate_graphql` | Generate a typed client from GraphQL SDL, with optional named fragments. |
| `generate_protobuf` | Generate a typed client from Protocol Buffers definitions. |
| `generate_sql` | Generate model types from SQL DDL. |
| `metaengine_initialize` | Load generation rules and language notes for the assistant. |

Type and model generation supports TypeScript, Python, Go, C#, Java, Kotlin, Groovy, Scala, Swift, PHP, and Rust. Client generation targets Angular, React, TypeScript Fetch, Go net/http, Java Spring, Python httpx, C# HttpClient, Kotlin Ktor, Rust Reqwest, and Swift URLSession.

`generate_code`, `load_spec_from_file`, and `generate_from_recipe` share generation and file-writing behavior:

- `outputPath` chooses the local output directory; the default is the MCP server's working directory.
- `skipExisting` defaults to `true`. Set it to `false` to overwrite generated files.
- `dryRun: true` returns generated file contents without writing them. Generation still calls the hosted API.
- Related type references resolve within one batch. Include the complete graph in that call.
- The hosted limit is 250 counted types per generation request. The exact count is described in [the recipe guide](./RECIPES.md#limits).

For Node16/NodeNext TypeScript ESM, use `typeScriptOptions: {"relativeImportExtension":"js"}`. Other TypeScript output retains extensionless relative imports by default.

## Where recipes help

Field maps remove repeated property metadata. Templates describe repeated structure once and bind explicit parameter values. Local JSON inputs can supply those values from a file you already maintain. The adapter executes no JavaScript from a recipe.

Savings depend on the amount of repetition, the chosen model and tokenizer, and the surrounding agent workflow. Custom business logic still needs to be written. A recorded development fixture compares a 59-interface recipe with its expanded payload; it measures JSON bytes, not model tokens or usage-limit guarantees.

The compact format keeps one readable path for common declarations and the existing native fields for advanced code. Native type expressions and `customCode` remain specific to their target language. Review and compile generated code in your project, including its dependencies and compiler settings.

## Privacy and execution

The local MCP server runs over stdio and performs recipe expansion, declared local file reads, and generated-file writes. The hosted MetaEngine API performs ephemeral processing of the expanded generation payload and returns source files.

The server does not automatically scan or upload existing project source files. Source or `customCode` content explicitly included in a generation request is part of that request and is sent to the hosted MetaEngine API. Values read from recipe inputs are included only when the recipe uses them in the expanded payload.

Submitted generation content and generated file contents are not persisted or logged; anonymous operational metadata is retained. See the [Privacy Policy](./PRIVACY.md) and [Terms](./TERMS.md) for the processing and retention details.

## Recorded agent workflows

A single MCP call can produce many files, reducing required tool operations. Model responses are a separate measure: in the recorded TypeScript runs Opus often issued one Write per response, while Sonnet usually batched the Writes. The corrected [benchmark findings](./benchmark/FINDINGS.md) separate those counts and retain output-token totals and pass rates.

For reproducible measurements across languages, models, and spec shapes, see [`benchmark/`](./benchmark) — a self-contained harness with the prompts, judging tools, and 15 canonical result folders. Numbers there are illustrations from one author's runs at N=5 per cell; reproduce in your own environment to see what holds for you.

## Links

- [npm package](https://www.npmjs.com/package/@metaengine/mcp-server)
- [Website](https://www.metaengine.eu/mcp)
- [Playground](https://www.metaengine.eu/playground)
- [Documentation and issues](https://github.com/meta-engine/mcp-server)

## License

MIT

## About this repository

This repository contains public documentation, examples, benchmarks, and issue tracking for MetaEngine MCP Server. The compiled npm package is available at [@metaengine/mcp-server](https://www.npmjs.com/package/@metaengine/mcp-server). The server implementation is maintained in a private repository.
