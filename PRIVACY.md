# Privacy Policy

**Effective Date**: November 27, 2025
**Last Updated**: November 27, 2025

## Overview

MetaEngine MCP Server is designed with privacy as a core principle. This document explains what data is collected, how it's used, and how it's protected.

---

## What Data We Collect

### Code Generation Specifications

When you use MetaEngine MCP Server through Claude Code, Claude Desktop, or any MCP-compatible AI assistant, the following data is sent to the MetaEngine API:

- **Type specifications** (JSON structures describing classes, interfaces, types to generate)
- **Language selection** (e.g., TypeScript, Python, Go)
- **Configuration options** (output paths, file naming preferences)

### What We DO NOT Collect

- **Your existing source code** — never sent to our servers
- **File contents** — only generation specs are transmitted
- **Personal information** — no names, emails, or identifying data
- **Specification contents** — not logged or saved (ephemeral processing only)
- **Generated code** — returned to you and immediately discarded
- **User identifiers** — anonymous service, no tracking of individual users
- **API keys or credentials** — MetaEngine requires no authentication

---

## How We Use Data

### Generation Purposes Only

Data sent to the MetaEngine API is used exclusively for:

1. **Code generation** — processing type specifications to produce source files
2. **Returning generated code** — sending the output back to your local machine

### Data Retention

**Code Specifications and Generated Code:**

Type specifications and generated code are **never saved or logged**:

- Spec contents exist **only in memory** during the API request
- Generated code is **immediately discarded** after the response is sent
- **No persistent storage** of specification contents or generated code
- **No retention** of your type definitions or output

**Performance Telemetry (Anonymous):**

For performance monitoring and API reliability, we collect **anonymous request metadata only**:

- ✅ Request timestamp
- ✅ Response latency (processing time)
- ✅ Request size (bytes)
- ✅ HTTP status codes
- ✅ Error types (if any)

**NOT Collected:**
- ❌ Type specification contents
- ❌ Generated code contents
- ❌ User identifiers or personal information
- ❌ IP addresses or location data
- ❌ Authentication tokens (none exist)

This telemetry is **anonymous** and used solely for performance optimization and service reliability monitoring.

---

## Data Security

### Transmission

- All API requests use **HTTPS encryption** (TLS 1.2+)
- Data is encrypted in transit between your machine and MetaEngine servers

### Processing

- Data is processed **ephemerally** in server memory
- **No disk writes** of user specifications or generated code
- Server memory is cleared immediately after each request

---

## Third-Party Services

MetaEngine MCP Server does **not** use:

- Analytics services (Google Analytics, Mixpanel, etc.)
- Tracking pixels or cookies
- Third-party data processors
- Advertising networks

The MetaEngine API is self-hosted and does not share data with any third parties.

---

## Local MCP Server

The MetaEngine MCP Server runs **locally on your machine** via npx. The local server:

- **Only communicates with the MetaEngine API** for code generation
- **Does not send telemetry** or usage data
- **Does not access files** outside the specified output directories
- **Does not make network requests** except to the MetaEngine API

---

## Your Control

### What You Can Control

- **Installation**: You choose when to install and configure the MCP server
- **Usage**: The server only runs when invoked by your AI assistant
- **Output paths**: You specify where generated files are written
- **Removal**: Simply remove the MCP server from your configuration to stop using it

### No Accounts or Tracking

MetaEngine MCP Server requires:

- **No account creation** — use immediately without signup
- **No API keys** — completely anonymous usage
- **No user identification** — we cannot identify individual users
- **No usage quotas** — unlimited requests with no tracking

---

## Children's Privacy

MetaEngine MCP Server does not knowingly collect any information from users under the age of 13. The service is designed for software developers and does not target children.

---

## Changes to This Policy

We may update this Privacy Policy from time to time. Changes will be posted at:

- This repository: [PRIVACY.md](https://github.com/meta-engine/mcp-server/blob/main/PRIVACY.md)
- Website: [metaengine.eu/mcp](https://www.metaengine.eu/mcp)

Continued use of MetaEngine MCP Server after changes constitutes acceptance of the updated policy.

---

## Contact

If you have questions about this Privacy Policy or data practices:

- **Email**: info@metaengine.eu
- **Issues**: [GitHub Issues](https://github.com/meta-engine/mcp-server/issues)
- **Website**: [metaengine.eu](https://www.metaengine.eu)

---

## Summary

**TL;DR**:

- ✅ Specs sent to API for code generation
- ✅ **Never saved or logged** — ephemeral processing only
- ✅ No personal data collected
- ✅ No tracking or analytics
- ✅ Free and anonymous
- ✅ HTTPS encrypted transmission
- ✅ Open source MCP protocol (MIT licensed)
