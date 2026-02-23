# Changelog

All notable changes to MetaEngine MCP Server will be documented in this file.

## [1.1.3] - 2026-02-23

### Changed
- **Dynamic tool descriptions** — full AI guide is now embedded in the `generate_code` tool description on first use, then swapped to a short directive after first successful call via `tools/list_changed` notification. This guarantees AI assistants read the guide before composing their first call, without permanently bloating context.
- **`metaengine_initialize` as recovery mechanism** — removed stale hardcoded response with outdated API references; now returns the guide file content directly. Serves as post-compaction recovery when the short directive tells the AI to reload the guide.
- Consolidated documentation: replaced `AI_ASSISTANT_GUIDE.md` and `QUICK_START.md` with a single `METAENGINE_AI_GUIDE.md` covering critical rules, patterns, language notes, and common mistakes.
- MCP resources simplified from 3 to 2 (guide + examples).

## [1.1.1] - 2025-12-05

### Fixed
- Added missing Swift and PHP to MCP tool enum definitions

## [1.1.0] - 2025-12-03

### Added
- **Swift and PHP** language support (10 languages total)
- C# optional namespace: when `packageName` is omitted, no namespace declaration is generated (ideal for GlobalUsings)

### Fixed
- Go and Python generation improvements

## [1.0.1] - 2025-11-27

### Added
- Tool titles for better UI display (required by Anthropic Directory)
- Safety annotations (readOnlyHint, destructiveHint) on all tools
- Terms of Service document
- Enhanced privacy policy with telemetry disclosure

### Changed
- Improved documentation for Anthropic Directory compliance
- Updated NPM package keywords for better discoverability

## [1.0.0] - 2025-11-27

### Added
- Production release (GA)
- Complete documentation (AI_ASSISTANT_GUIDE.md, QUICK_START.md, EXAMPLES.md)
- Support for 8 languages: TypeScript, Python, Go, C#, Java, Kotlin, Groovy, Scala
- Three core tools: generate_code, load_spec_from_file, metaengine_initialize
- MCP resources for documentation access
- Privacy policy
- MIT license
- **CustomFile identifier resolution** - Reference customFiles by identifier for automatic namespace imports

### Features
- Multi-language code generation with zero syntax errors
- Perfect cross-file import resolution
- Semantic dependency resolution via customFile identifiers
- Generic type system support
- Batch generation (20-100 files per request)
- Dry run mode for previewing output
- Skip existing files (stub pattern support)
- Automatic directory creation
- Automatic namespace calculation from file paths

## [0.9.x] - Pre-release versions

Development and testing phase with 50+ iterations of feature parity and bug fixes across all supported languages.

---

## Version History Summary

- **1.1.3** - Dynamic tool descriptions with guide injection
- **1.1.1** - Swift and PHP enum fix
- **1.1.0** - Swift, PHP support; C# optional namespace
- **1.0.1** - Anthropic Directory compliance updates
- **1.0.0** - Production release (GA)
- **0.9.x** - Beta testing and refinement
