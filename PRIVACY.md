# Privacy Policy

**Effective Date**: November 27, 2025

**Last Updated**: August 30, 2026

## Overview

MetaEngine MCP Server has two execution boundaries. The local MCP server runs on your machine over stdio and handles tool calls and local file writes. Code generation occurs in the hosted MetaEngine API, where each submitted generation payload receives ephemeral processing and the generated files are returned to the local server.

This policy distinguishes generation content from the anonymous operational metadata retained to operate and support the hosted service.

---

## Generation Data Sent to the Hosted API

A generation request may contain:

- **Semantic type specifications** — structured definitions of classes, interfaces, enums, generics, and related types
- **Converter inputs** — OpenAPI documents or URLs, GraphQL schemas, Protocol Buffer definitions, or SQL DDL
- **Target selection** — the requested language or client framework
- **Generator options** — the options needed to produce the requested output
- **Explicit source content** — source or `customCode` content explicitly included in a generation request is part of that request and is sent to the hosted MetaEngine API
- **MCP package version** — sent in the `X-MCP-Version` request header

The local MCP server does not automatically scan or upload existing project source files. A generation specification explicitly supplied inline or through `load_spec_from_file` is read locally and sent as the generation payload. Existing source content is sent only when the client or assistant deliberately includes that content in the submitted specification, such as a `customCode` block or custom file.

---

## Generation Content We Do Not Retain

Submitted generation content and generated source files are request-scoped:

- Specification, schema, DDL, Protocol Buffer, source, and `customCode` contents are not persisted or logged
- Generated file contents are returned to the caller and are not persisted or logged
- Validation rejects are recorded only by fixed field category and count; rejected values are not logged
- Failure telemetry records exception types only; exception messages are not logged because they can quote submitted content

The hosted API does not retain user identifiers, account identifiers, API keys, authentication tokens, IP addresses, or location data as generation telemetry. The service requires no account or API key.

---

## Anonymous Operational Metadata We Retain

The hosted API retains the following request-level operational metadata for service reliability, performance analysis, and support:

- **Request envelope** — request timestamp, response latency, request size in kilobytes (`RequestSizeKB`), HTTP status code, and error type
- **Incident reference** — a server-minted incident/correlation ID, also returned to the caller on errors so a support request can identify the failed operation
- **MCP client version** — the `X-MCP-Version` value only when it is version-shaped and no more than 32 characters; otherwise recorded as `unknown`
- **Target** — target language
- **Entity counts** — counts only for classes, interfaces, enums, array types, dictionary types, custom files, concrete generic classes, and concrete generic interfaces; names and contents are not retained
- **Validation outcome** — validation error count and a breakdown over fixed JSON-path field names, capped at 10 distinct fields, plus an omitted-field count when more categories are present; rejected values are not logged
- **Generation outcome** — elapsed generation time, response file count, generated-content UTF-8 byte count, and warning count
- **Failure shape** — exception type chain with up to five causes; exception messages are not logged

This metadata is not tied to an account or user identity. It does not contain submitted specification values or generated file contents.

### Content Not Collected in Operational Logs

- Type specification, schema, DDL, Protocol Buffer, source, or `customCode` contents
- Generated code contents
- Entity, member, file, or user-supplied names
- Validation rejected values or other submitted literals
- Exception messages
- User or account identifiers
- IP addresses or location data
- API keys, credentials, or authentication tokens

---

## How We Use Data

Submitted generation data is used only to:

1. Process the requested specification through the selected generator
2. Return the generated files to the local MCP server

Anonymous operational metadata is used only to:

1. Monitor reliability and performance
2. Diagnose incidents using the correlation ID supplied to the caller
3. Understand aggregate request and output shape without retaining content

---

## Security

### Transmission

- Requests to the hosted MetaEngine API use HTTPS encryption
- Generation content is encrypted in transit between the local MCP server and the hosted API

### Processing and Storage

- Generation content is held only for in-memory request processing and response delivery
- The MetaEngine application does not write submitted generation content or generated source files to persistent storage or application logs
- Only the anonymous operational metadata enumerated above is retained

---

## Local MCP Server

The npm package runs locally over stdio. It:

- Receives tool calls from the configured MCP client
- Reads a specification file only when `load_spec_from_file` is called with that path
- Sends generation payloads to the hosted MetaEngine API for ephemeral processing
- Writes returned files to the requested output directory, or returns them inline for a dry run
- Does not automatically scan or upload existing project source files

Source or `customCode` content explicitly included in a generation payload is part of that payload and is sent to the hosted MetaEngine API. The local server does not send a separate analytics or advertising telemetry stream.

---

## Infrastructure and Third-Party Services

The hosted MetaEngine API runs on Microsoft Azure. Azure Monitor/Application Insights receives the anonymous operational metadata enumerated in this policy as an infrastructure and operational telemetry processor.

Submitted generation content, generated file contents, validation rejected values, and exception messages are excluded from that telemetry. MetaEngine does not use generation content or operational metadata for advertising or profiling, and the MCP server does not use tracking pixels or cookies.

---

## Your Control

- **Installation** — you choose whether to configure the MCP server
- **Invocation** — generation runs only when your MCP client invokes a generation tool
- **Payload** — you and your MCP client control the specifications and any explicit source content included in each request
- **Output** — you select where returned files are written and can use dry-run mode to receive them inline
- **Removal** — removing the MCP server from your client configuration stops its use

---

## Children's Privacy

MetaEngine MCP Server is intended for software development and does not knowingly collect personal information from children under 13.

---

## Changes to This Policy

We may update this Privacy Policy from time to time. Changes will be posted at:

- [The public MCP server repository](https://github.com/meta-engine/mcp-server/blob/main/PRIVACY.md)
- [The MetaEngine MCP website](https://www.metaengine.eu/mcp)

Continued use of MetaEngine MCP Server after a change constitutes acceptance of the updated policy.

---

## Contact

For privacy or data-practice questions:

- **Email**: info@metaengine.eu
- **Issues**: [github.com/meta-engine/mcp-server/issues](https://github.com/meta-engine/mcp-server/issues)
- **Website**: [metaengine.eu](https://www.metaengine.eu)

---

## Summary

- The MCP adapter runs locally over stdio; generation runs in the hosted MetaEngine API
- Submitted specifications and any explicitly included source content receive ephemeral processing
- Submitted generation content and generated file contents are not persisted or logged
- Anonymous operational metadata is retained exactly as enumerated in this policy
- Existing project source files are not scanned or uploaded automatically
