You are doing a one-time WARMUP task. The metaengine MCP server is configured but you are not trained on it natively. A separate generation session will run after this one and will NOT have access to the metaengine MCP's documentation — it will only have whatever summary you produce here.

The next session will generate **Python** code from a DDD spec, so focus your summary on aspects relevant to Python generation (packageName / module naming, file path layout, type mapping for Date / numbers / collections, how the engine handles dataclasses vs plain classes, how customCode interacts with Python method stubs).

OBJECTIVE
=========
Read the metaengine MCP's `linkedResources` documentation, then write a comprehensive summary to:
  {{SUMMARY_FILE}}

EXECUTE THESE STEPS
===================

1. Call `mcp__metaengine__metaengine_initialize` (with `language: "python"` if the parameter exists).

2. Read every linkedResource it returns. These are the canonical guide.

3. Use Bash to write a comprehensive summary to {{SUMMARY_FILE}} via heredoc. Cover:

   - Tools exposed and their schemas
   - generate_code input schema (full)
   - **Python-specific notes**:
     - packageName / module naming convention
     - file path layout
     - type mapping (Date → datetime.datetime / date? string → str? number → int / float?)
     - whether the engine emits @dataclass decorators or plain classes
     - how to declare enums (Enum subclass, IntEnum?)
     - method stub bodies (raise NotImplementedError vs pass)
   - Critical rules (single-call, etc.)
   - Output structure produced

   The summary must be *self-contained* — the next session won't have the docs.

4. Output the literal text `WARMUP_DONE` and stop.

CONSTRAINTS
===========
- Do NOT call `generate_code` here. This session is purely learning. (It's not in your allowed tools anyway.)
- Do NOT cut the summary short. Err on the side of completeness; the gen session needs to use this without re-reading docs.
