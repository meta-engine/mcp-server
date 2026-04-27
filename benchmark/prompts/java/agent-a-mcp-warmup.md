You are doing a one-time WARMUP task. The metaengine MCP server is configured but you are not trained on it natively. A separate generation session will run after this one and will NOT have access to the metaengine MCP's documentation — it will only have whatever summary you produce here.

The next session will generate **Java** code from a DDD spec, so focus your summary on aspects relevant to Java generation (packageName handling, path conventions, type mapping for Date / numbers / collections, how the engine emits classes vs records, how customCode interacts with Java method stubs).

OBJECTIVE
=========
Read the metaengine MCP's `linkedResources` documentation, then write a comprehensive summary to:
  {{SUMMARY_FILE}}

EXECUTE THESE STEPS
===================

1. Call `mcp__metaengine__metaengine_initialize` (with `language: "java"` if the parameter exists).

2. Read every linkedResource it returns. These are the canonical guide.

3. Use Bash to write a comprehensive summary to {{SUMMARY_FILE}} via heredoc, e.g.:

       cat > {{SUMMARY_FILE}} <<'SUMMARY_EOF'
       # MetaEngine MCP — Knowledge Brief (Java focus)

       ## Tools exposed
       - `mcp__metaengine__generate_code`: ...
       (etc.)

       ## generate_code — input schema (full)
       ... include every field, type, optionality, expected values ...

       ## Java-specific notes
       - packageName behaviour
       - file path layout (src/main/java/<package>/...)
       - type mapping (Date → java.time.Instant? LocalDateTime?)
       - class vs record emission for Java 14+
       - customCode for method stubs (UnsupportedOperationException etc.)

       ## Critical rules
       - ONE call with the full spec. Splitting per-domain breaks the typegraph.
       - ...

       ## Output structure
       ... what the engine produces ...
       SUMMARY_EOF

   The summary must be *self-contained* — the next session won't have the docs.

4. Output the literal text `WARMUP_DONE` and stop.

CONSTRAINTS
===========
- Do NOT call `generate_code` here. This session is purely learning. (It's not in your allowed tools anyway.)
- Do NOT cut the summary short. Err on the side of completeness; the gen session needs to use this without re-reading docs.
- The summary length is part of what's being measured — be comprehensive but not redundant.
