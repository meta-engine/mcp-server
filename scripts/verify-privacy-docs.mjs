import { readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

class PrivacyDocumentationContract {
  constructor(packageRoot, readText, resolvePath) {
    this.packageRoot = packageRoot;
    this.readText = readText;
    this.resolvePath = resolvePath;
  }

  verify() {
    const documents = new Map(
      ["PRIVACY.md", "README.md", "TERMS.md"].map((name) => [
        name,
        this.readText(this.resolvePath(this.packageRoot, name), "utf8"),
      ]),
    );
    const violations = [];

    this.rejectContradictoryClaims(documents, violations);
    this.requirePolicyDates(documents, violations);
    this.requireProcessingBoundary(documents, violations);
    this.requireSourcePayloadDistinction(documents, violations);
    this.requireContentRetentionDistinction(documents, violations);
    this.requireSupportedLanguageDisclosure(documents.get("TERMS.md"), violations);
    this.requireRetentionDisclosure(documents.get("PRIVACY.md"), violations);

    if (violations.length > 0) {
      throw new Error(
        `MCP privacy documentation contract failed:\n${violations.map((item) => `- ${item}`).join("\n")}`,
      );
    }

    console.log("MCP privacy documentation states the hosted processing and retention contract consistently.");
  }

  requirePolicyDates(documents, violations) {
    const dates = [];
    for (const name of ["PRIVACY.md", "TERMS.md"]) {
      const match = documents.get(name).match(/\*\*Last Updated\*\*: ([^\n]+)/i);
      if (!match) {
        violations.push(`${name} is missing its Last Updated date`);
        continue;
      }
      dates.push([name, match[1]]);
      const parsed = Date.parse(match[1]);
      if (Number.isNaN(parsed)) {
        violations.push(`${name} has an invalid Last Updated date: ${match[1]}`);
      } else if (parsed < Date.parse("August 30, 2026")) {
        violations.push(`${name} has a Last Updated date older than August 30, 2026`);
      }
    }
    if (new Set(dates.map(([, date]) => date)).size > 1) {
      const rendered = dates.map(([name, date]) => `${name}=${date}`).join(", ");
      violations.push(`PRIVACY.md and TERMS.md have different Last Updated dates: ${rendered}`);
    }
  }

  rejectContradictoryClaims(documents, violations) {
    const forbiddenClaims = [
      /\brequests are not logged\b/i,
      /\bno data is (?:saved(?: or logged)?|logged)\b/i,
      /\bnothing is uploaded\b/i,
      /\bexisting code never leaves your machine\b/i,
      /\b(?:specifications?|schemas?|generation inputs?) never leave(?:s)? (?:the|your) (?:machine|page)\b/i,
    ];

    for (const [name, text] of documents) {
      for (const claim of forbiddenClaims) {
        if (claim.test(text)) {
          violations.push(`${name} contains contradictory absolute claim ${claim}`);
        }
      }
    }
  }

  requireProcessingBoundary(documents, violations) {
    for (const [name, text] of documents) {
      this.requirePatterns(
        name,
        text,
        [
          ["local stdio MCP boundary", /local[^.\n]{0,120}stdio/i],
          ["hosted MetaEngine API boundary", /hosted MetaEngine API/i],
          ["ephemeral processing", /ephemeral(?:ly)? process/i],
        ],
        violations,
      );
    }
  }

  requireSourcePayloadDistinction(documents, violations) {
    for (const [name, text] of documents) {
      this.requirePatterns(
        name,
        text,
        [
          [
            "no automatic existing-source upload",
            /does not automatically scan or upload existing project source files/i,
          ],
          [
            "explicit source/customCode payload exception",
            /source or `customCode` content explicitly included in a generation (?:request|payload)[^.\n]*sent/i,
          ],
        ],
        violations,
      );
    }
  }

  requireContentRetentionDistinction(documents, violations) {
    for (const [name, text] of documents) {
      this.requirePatterns(
        name,
        text,
        [
          [
            "content-scoped non-retention",
            /submitted generation content and generated file contents are not persisted or logged/i,
          ],
          ["retained anonymous operational metadata", /anonymous operational metadata is retained/i],
        ],
        violations,
      );
    }
  }

  requireSupportedLanguageDisclosure(terms, violations) {
    this.requirePatterns(
      "TERMS.md",
      terms,
      [
        [
          "complete supported language set",
          /TypeScript, Python, Go, C#, Java, Kotlin, Groovy, Scala, Swift, PHP, Rust/,
        ],
      ],
      violations,
    );
  }

  requireRetentionDisclosure(privacy, violations) {
    this.requirePatterns(
      "PRIVACY.md",
      privacy,
      [
        ["normalized MCP endpoint", /POST MCP generation/i],
        ["normalized converter endpoint", /POST Converter generation/i],
        ["request timestamp", /request timestamp/i],
        ["request duration", /request timestamp, duration/i],
        ["request status and success", /HTTP response status\/result code, and success outcome/i],
        ["Content-Length-derived request size", /Content-Length[^.\n]*kilobytes[^.\n]*RequestSizeKB/i],
        ["server-minted telemetry ID", /server-minted 32-character hexadecimal identifier[^.\n]*operation and request/i],
        ["request Source removal", /full request URL, and request Source field are removed/i],
        ["incoming trace-context removal", /incoming `Request-Id`[^.\n]*`traceparent`[^.\n]*`tracestate`[^.\n]*baggage[^.\n]*`Request-Context`[^.\n]*`Correlation-Context`[^.\n]*`ai_legacyRootId`[^.\n]*stripped or replaced/i],
        ["server-minted incident ID", /IncidentId[^.\n]*server-minted 32-character hexadecimal incident ID/i],
        [
          "MCP-only bounded client version",
          /MCP client version \(`McpVersion`\)[^.\n]*retained only for MCP generation requests and events[^.\n]*version-shaped[^.\n]*no more than 32 characters[^.\n]*unknown/i,
        ],
        ["bounded converter Api field", /Converter kind \(`Api`\)[^.\n]*OpenAPI[^.\n]*GraphQL[^.\n]*Protobuf[^.\n]*SQL/i],
        ["classified Language/Target/Framework fields", /Target \(`Language`, `Target`, or `Framework`\)[^.\n]*classified target language or client framework/i],
        [
          "all entity-count kinds",
          /classes, interfaces, enums, array types, dictionary types, custom files, concrete generic classes, and concrete generic interfaces/i,
        ],
        ["fixed rejection reason", /configuration-not-deserialized/i],
        ["type-limit count", /billable type count[^.\n]*TypeCount/i],
        ["type-limit maximum", /configured maximum[^.\n]*MaxAllowed/i],
        ["validation error count", /validation error count/i],
        ["fixed JSON-path fields", /fixed allowlisted JSON-path field categories/i],
        ["ten-field cap", /(?:maximum of|capped at) 10 distinct fields/i],
        ["omitted-field count", /omitted-field count/i],
        ["elapsed generation time", /elapsed generation time/i],
        ["response file count", /response file count/i],
        ["response byte count", /generated-content UTF-8 byte count/i],
        ["warning count", /warning count/i],
        ["bounded exception type chain", /exception type chain[^.\n]*(?:maximum of|up to) five causes/i],
        ["no exception messages", /exception messages?[^.\n]*(?:not|never) logged/i],
        ["no rejected values", /rejected values?[^.\n]*(?:not|never) logged/i],
        ["fixed trace message", /Generation traces use a fixed non-content message/i],
        ["dropped unsafe telemetry shapes", /ExceptionTelemetry[^.\n]*EventTelemetry[^.\n]*unrecognized telemetry shapes[^.\n]*dropped/i],
        ["redacted dependency outcome", /fixed external-dependency label\/type[^.\n]*timestamp, duration, success outcome, and status\/result code/i],
        ["dependency URL redaction", /submitted URL, domain, path, query, properties, and metrics are redacted/i],
        ["caller identity/context removal", /does not retain user or account identifiers[^.\n]*IP addresses[^.\n]*device or session values[^.\n]*trace or correlation context/i],
        ["Azure hosting", /hosted MetaEngine API runs on Microsoft Azure/i],
        [
          "Azure operational telemetry processor",
          /Azure Monitor\/Application Insights receives[^.\n]*sanitized request telemetry[^.\n]*allowlisted generation events[^.\n]*redacted external-dependency outcomes[^.\n]*infrastructure and operational telemetry processor/i,
        ],
        ["Azure telemetry/service/SDK envelope", /standard telemetry-record, service-resource, and SDK envelope[^.\n]*record type\/timestamp\/severity[^.\n]*Azure resource identity[^.\n]*Application Insights SDK\/version metadata/i],
        ["service role-name removal", /clears the service hostname\/role name/i],
        [
          "no advertising or profiling use",
          /does not use generation content or operational metadata for advertising or profiling/i,
        ],
        [
          "generation content excluded from Azure telemetry",
          /submitted generation content, generated file contents, validation rejected values, and exception messages are excluded from that telemetry/i,
        ],
      ],
      violations,
    );
  }

  requirePatterns(name, text, requirements, violations) {
    for (const [label, pattern] of requirements) {
      if (!pattern.test(text)) {
        violations.push(`${name} is missing ${label}`);
      }
    }
  }
}

new PrivacyDocumentationContract(
  resolve(dirname(fileURLToPath(import.meta.url)), ".."),
  readFileSync,
  resolve,
).verify();
