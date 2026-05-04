# Changelog

All notable changes to MetaEngine MCP Server will be documented in this file.

## [1.3.0] - 2026-05-04

### Added — `generate_openapi`

- Two shared options across all 10 frameworks:
  - `typeMappings` — override how spec types are emitted (e.g. `{decimal: 'string'}` to keep precision in JS).
  - `includeTags` — restrict generation to operations matching one of these tags.
- New per-framework options: `angularOptions.useInterceptors`, `goOptions.usePointersForOmittable` and `goOptions.useValidateStructTags`, `kotlinOptions.usePlugins`.

### Added — `generate_graphql`

- New shared options: `customScalars` (map GraphQL custom scalars to target-language types), `optionsObjectThreshold`.
- GraphQL framework options now reach feature parity with OpenAPI — middleware hooks, types-barrel, response date transformation, Go context + struct-tag validation, Kotlin Ktor plugins, Java Spring `@Component` + base-URL property, Python sync methods + camelCase aliases, Swift / C# middleware, and Result-pattern + `import.meta.env` for TypeScript Fetch are all reachable from the GraphQL tool now.

### Added — `generate_protobuf`

- New shared option: `optionsObjectThreshold`.
- Protobuf framework options gain coverage that previously only existed for OpenAPI: Angular interceptors + date transformation, Fetch result-pattern, Go context / JSON-library / struct-tag validation, Kotlin plugins, and `csharpOptions.useDependencyInjection` (HttpClientFactory + scoped-service registration).

### Added — `generate_sql`

- Four new shared options across all 11 languages:
  - `singularTypeNames` — singularize plural table names (table `users` becomes type `User`).
  - `precisionSafeDecimals` — emit decimals as precision-safe types (e.g. `string` in JS) instead of float.
  - `jsonAs` — control how JSON columns are typed (`'string'` keeps raw text, `'object'` parses).
  - `schemaPrefix` — prepend the SQL schema name to generated type names (e.g. `Auth_User`).

### Added — `generate_code`

- Enum members support `stringValue` alongside numeric `value` for languages where members carry string-typed values (TypeScript string-literal unions, Java `String`-backed enums); `value` is now nullable.

### Fixed

- `generate_sql` with `pythonOptions.modelStyle: 'pydantic'` was silently producing `typing.Protocol` output instead of `pydantic.BaseModel`. Now correctly maps to Pydantic.
- `generate_code` with an enum member missing both `value` and `stringValue` was silently treated as `value: 0`; now returns a validation error so the misconfig surfaces immediately.

### Changed

- Typed API client regenerated against the latest WebAPI Swagger.

## [1.2.2] - 2026-04-24

### Added
- `generate_openapi` → `fetchOptions` now exposes `useMiddleware` (emit `onRequest` / `onResponse` / `onError` hooks) and `useImportMetaEnv` (use `import.meta.env` for base-URL access in Vite / SvelteKit). Parity with the `@metaengine/openapi-fetch` CLI flags `--middleware` and `--import-meta-env`.
- `generate_code` language enum and tool description now include `rust` — the backend already supported it, but the tool schema was rejecting the value before the request reached the handler.

### Changed
- Typed API client regenerated against the latest WebAPI Swagger — `HttpError.response` is now optional and network errors surface as `HttpError(status=0)` instead of raw `fetch` rejections.
- JVM `Date` mapping unified across Java, Kotlin, Groovy, Scala — Groovy and Scala previously emitted `LocalDateTime`; now all four use `OffsetDateTime`.
- Go `Number` / integer aligned to native `int` (was `int32`, the outlier across languages).
- Java + Kotlin framework coupling (Jackson / kotlinx.serialization annotations) is now opt-in instead of forced on every generated type.

### Fixed — `generate_code` wire-bugs
- **Kotlin** — enums now emit a primary constructor when members carry values; class body `val`s are default-initialized (previously caused compile failures).
- **Scala** — case classes emit the primary parameter list; field `val`s are no longer bare.
- **Swift** — non-optional stored properties get synthesized default initializers; `Codable` / `Sendable` conformance is retained on data-class subclasses.
- **Groovy** — enums with `(int)` arguments now emit a primary constructor + field, so explicit integer values are no longer silently dropped.
- **Go** — integer enums emit explicit member values instead of `iota`, preserving spec-defined numbering.
- **C#** — removed redundant self-`using {namespace};` inside the same namespace.

## [1.2.1] - 2026-04-21

### Fixed
- `file-writer` joined `file.path` and `file.name` with plain string concat, producing `modelsuser.ts` instead of `models/user.ts` across all generators. Now uses `path.join()` so the directory separator is always present.

### Changed
- Package description and keywords aligned with metaengine.eu — 11 languages including Rust; accuracy framed as the CI gate ("regenerated and compiled on every merge across the validation corpus") rather than an unqualified claim.

## [1.2.0] - 2026-04-19

### Added
- Four new MCP tools exposing the full MetaEngine surface:
  - `generate_openapi` — 10 frameworks with per-framework typed options
  - `generate_graphql` — 10 frameworks from GraphQL SDL
  - `generate_protobuf` — 10 frameworks from `.proto` input
  - `generate_sql` — 11 languages from SQL DDL
- `AdditionalInfo` on tool responses for migration notices, deprecation warnings, and dynamic client messaging.
- Self-bootstrapping typed API client generated from the WebAPI's Swagger; all tool handlers call typed service methods.

### Changed
- Refactored the 1142-line monolithic `index.ts` into 15 focused modules (shared infrastructure + per-tool files).
- Default `METAENGINE_API_URL` is now `https://api.metaengine.eu` (previously the Azure dev slot).
- Protobuf `python-fastapi` framework renamed to `python-httpx` to reflect the backend's httpx-based client.
- Tool input schemas regenerated from the latest Swagger; per-framework options added, renamed, or removed.
- Auto-import coverage in the AI guide extended from 5 to 11 languages.

## [1.1.3] - 2026-02-23

### Changed
- Dynamic tool descriptions — the full AI guide is embedded in the `generate_code` tool description on first use, then swapped to a short directive after the first successful call via a `tools/list_changed` notification. Assistants read the guide on first use without permanently bloating context.
- `metaengine_initialize` now returns the guide file content directly, serving as post-compaction recovery when the short directive tells the assistant to reload the guide.
- Consolidated documentation: `AI_ASSISTANT_GUIDE.md` + `QUICK_START.md` replaced by a single `METAENGINE_AI_GUIDE.md`. MCP resources simplified from 3 to 2 (guide + examples).

## [1.1.1] - 2025-12-05

### Fixed
- Added missing Swift and PHP to MCP tool enums. Backend support was already present but the tool schema rejected both values.

## [1.1.0] - 2025-12-03

### Added
- Swift and PHP language support (10 languages total).
- C# optional namespace: when `packageName` is omitted, no namespace declaration is generated — ideal for GlobalUsings.

### Fixed
- Go customCode package qualifier handling for proper import resolution.
- Python absolute paths for better module resolution.

## [1.0.1] - 2025-11-27

### Added
- Tool titles and safety annotations (`readOnlyHint`, `destructiveHint`) on all tools — required for Anthropic Directory compliance.
- Terms of Service document and enhanced privacy policy with telemetry disclosure.

## [1.0.0] - 2025-11-27

### Added
- Production release (GA) with 8 languages: TypeScript, Python, Go, C#, Java, Kotlin, Groovy, Scala.
- Three core tools: `generate_code`, `load_spec_from_file`, `metaengine_initialize`.
- CustomFile identifier resolution for automatic namespace imports across generated files.
- MCP resources for documentation access; MIT license.

## [0.9.x] - Pre-release

50+ iterations to land `generate_code`: feature parity, cross-language import resolution, and bug fixes across all supported languages before the GA cut.
