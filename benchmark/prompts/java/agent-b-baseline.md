You are running the baseline variant of a code-generation benchmark — **Java** target.

OBJECTIVE
=========
Generate **Java** code for the DDD spec located at:
  {{SPEC_PATH}}

Write all generated files into:
  {{OUT_DIR}}

INSTRUCTIONS
============
1. Read the spec file. It is a JSON document with this shape:

   {
     "domains": [
       {
         "name": "<domain>",
         "types": [
           {"name": "X", "kind": "aggregate" | "value_object",
            "fields": [{"name": "...", "type": "..."}]},
           {"name": "Y", "kind": "enum",
            "members": [{"name": "Pascal", "value": 0}, ...]}
         ],
         "services": [
           {"name": "Z", "methods": [{"name": "...", "params": [...], "returns": "..."}]}
         ]
       }
     ]
   }

2. For every type and every service in the spec, create a separate Java file using the `Write` tool. Do not skip any entity. Do not summarise or batch — every entity gets its own file.

OUTPUT STRUCTURE (Maven-style layout)
=====================================
Use package `com.metaengine.demo.<domain>.<kind>` for every file. File path:

- `com/metaengine/demo/<domain>/aggregates/<TypeName>.java`     — for kind=aggregate
- `com/metaengine/demo/<domain>/value_objects/<TypeName>.java`  — for kind=value_object
- `com/metaengine/demo/<domain>/enums/<TypeName>.java`          — for kind=enum
- `com/metaengine/demo/<domain>/services/<ServiceName>.java`    — for services

Every file starts with:
```java
package com.metaengine.demo.<domain>.<kind>;

import ...;  // any cross-domain or stdlib types

/** ... JavaDoc ... */
public ...
```

STYLE
=====
- **Aggregates**: `public class <Name>` with `private final` fields and a constructor that assigns them, plus public getters. (Or `public record <Name>(...)` if you prefer the modern Java 14+ idiom — both are accepted.)
- **Value objects**: `public record <Name>(...)` (Java 14+) is preferred. `public class` with getters is also fine.
- **Enums**: `public enum <Name>` with each member from spec.members. Numeric values via constructor:
  ```java
  public enum OrderStatus {
    Draft(0), Placed(1), Paid(2), Shipped(3), Delivered(4), Cancelled(5);
    private final int value;
    OrderStatus(int value) { this.value = value; }
    public int getValue() { return value; }
  }
  ```
- **Services**: `public class <Name>` with the methods from the spec; method bodies must `throw new UnsupportedOperationException("not implemented")`. NOT an interface.
- Type mapping from spec strings:
  - `"string"` → `String`
  - `"number"` → `double` (or `int` for clearly-integer fields)
  - `"Date"`   → `java.time.Instant` (add the import)
  - `"Partial<T>"` → just use `T` (Java has no native Partial; treat parameter as the type)
  - `"T | null"` → return `T` and document nullability in JavaDoc, OR return `java.util.Optional<T>`
  - `"T[]"`    → `java.util.List<T>` (add the import)
  - `"void"`   → `void`
- Include a one-line JavaDoc on each top-level declaration.
- All imports must be explicit and resolve.
- Code must compile cleanly under `javac --release 17` (or higher) on the generated tree.

When every file in the spec has been written, output exactly: `DONE` and stop.
