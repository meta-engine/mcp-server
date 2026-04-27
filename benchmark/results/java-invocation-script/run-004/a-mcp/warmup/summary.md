# MetaEngine MCP — Knowledge Brief (Java focus)

This document is a self-contained brief produced from the MetaEngine MCP `linkedResources` for use by a follow-on session that will generate **Java** code from a DDD spec without re-reading the docs. It includes the full `generate_code` schema, all critical rules, Java-specific behaviors, and worked patterns.

---

## 1. What MetaEngine MCP is

A **semantic** code generator (not a template engine). You send one structured JSON spec describing types, relationships, and method bodies. The engine produces compilable source files for TypeScript, C#, Python, Go, **Java**, Kotlin, Groovy, Scala, Swift, PHP, and Rust. It resolves cross-references, manages imports automatically, and applies language idioms (e.g., Java `ALL_CAPS` enum members, Python `snake_case`, Java records vs classes). One well-formed call replaces dozens of file writes.

---

## 2. Tools exposed

The MCP server exposes:

- `mcp__metaengine__metaengine_initialize` — returns the AI guide (already consumed during warmup). Optional `language` arg restricts to language-specific patterns.
- `mcp__metaengine__generate_code` — the workhorse; takes a JSON spec and emits files.
- `mcp__metaengine__generate_openapi`, `generate_graphql`, `generate_protobuf`, `generate_sql`, `load_spec_from_file` — converters that turn external IDLs / files into MetaEngine input. Not needed for plain DDD generation.

Resources (read-only docs):
- `metaengine://guide/ai-assistant` — critical rules, patterns, language notes, common mistakes.
- `metaengine://guide/examples` — worked examples per pattern.

---

## 3. `generate_code` — full input schema

Top-level parameters:

| Field | Type | Required | Notes |
|---|---|---|---|
| `language` | enum | **yes** | `"java"` for Java |
| `packageName` | string | no | Defaults to `com.metaengine.generated` for Java/Kotlin/Groovy. Sets the Java `package` declaration and impacts directory layout. |
| `outputPath` | string | no | Defaults to `"."`. Output root directory. |
| `dryRun` | boolean | no | Default `false`. If `true`, returns generated file contents in the response and writes nothing to disk. |
| `skipExisting` | boolean | no | Default `true`. Useful for stub/customisation patterns: only new files are created, existing untouched. |
| `initialize` | boolean | no | Default `false`. When `true`, properties get default value initializers in supported languages. |
| `classes` | array | no | Class definitions (regular and generic templates) — see below. |
| `interfaces` | array | no | Interface definitions (regular and generic templates). |
| `enums` | array | no | Enum definitions. |
| `arrayTypes` | array | no | Reusable virtual array references (no files generated). |
| `dictionaryTypes` | array | no | Reusable virtual dict/map references (no files generated). |
| `concreteGenericClasses` | array | no | Virtual concrete generic instantiations (e.g. `Repository<User>`). |
| `concreteGenericInterfaces` | array | no | Same but for interfaces. |
| `customFiles` | array | no | Free-form files (utilities, type aliases, barrel exports). No class wrapper. |

### 3.1 Class object

| Field | Description |
|---|---|
| `name` | Class name (e.g. `User`). |
| `typeIdentifier` | Unique slug for cross-reference (e.g. `"user"`). |
| `path` | Sub-directory under output root (e.g. `"models"`, `"services/auth"`). |
| `fileName` | Override file name (no extension). |
| `comment` | Class-level docstring. |
| `isAbstract` | Boolean — abstract class. |
| `baseClassTypeIdentifier` | typeIdentifier of base class (or of a `concreteGenericClasses` entry to extend `Repository<User>`-style). |
| `interfaceTypeIdentifiers` | Array of interface typeIdentifiers this class implements. |
| `genericArguments` | Makes this a generic template (`Repository<T>`). Each item: `name` (e.g. `"T"`), `constraintTypeIdentifier`, `propertyName` (auto-create field of `T`), `isArrayProperty` (use `T[]`). |
| `constructorParameters` | Array of `{name, type | primitiveType | typeIdentifier}`. **In Java, constructor parameters auto-become properties — do NOT also list them in `properties`.** |
| `properties` | Array of property objects (see 3.4). For Java: only ADDITIONAL fields not already in `constructorParameters`. |
| `customCode` | Array of `{code, templateRefs?}`. ONE item == ONE member (method, initialized field, constructor body, etc.). Auto-newlines between blocks. |
| `customImports` | Array of `{path, types[]}`. ONLY for external libraries; never for stdlib. |
| `decorators` | Array of `{code, templateRefs?}`. In Java these are annotations (`@Service`, `@Entity`, etc.). |

### 3.2 Interface object

Same shape as a class but for interfaces: `name`, `typeIdentifier`, `path`, `fileName`, `comment`, `genericArguments`, `interfaceTypeIdentifiers` (extend other interfaces), `properties`, `customCode`, `customImports`, `decorators`.

For methods that an implementing class will override, put **method signatures inside `customCode`** (e.g. `"List<$user> findAll();"` with templateRefs), NOT as function-typed properties.

### 3.3 Enum object

`name`, `typeIdentifier`, `path`, `fileName`, `comment`, `members[]`. Each member `{name, value: number}`.

In **Java**, member names are emitted as `ALL_CAPS` (idiomatic). The judge / human review tolerates that transformation — input `Pending` becomes `PENDING`. Don't fight this.

### 3.4 Property object

| Field | Description |
|---|---|
| `name` | Property name. |
| `comment` / `commentTemplateRefs` | Docstring + refs. |
| `primitiveType` | One of `"String" | "Number" | "Boolean" | "Date" | "Any"`. |
| `typeIdentifier` | Reference to another generated type (class/interface/enum/arrayType/dictionaryType/concreteGeneric). |
| `type` | Free-form type expression for complex/library types (e.g. `"List<$user>"` with `templateRefs`). |
| `templateRefs` | `[{placeholder: "$user", typeIdentifier: "user"}]` — replaces `$user` in `type`/`code` and triggers import generation. |
| `decorators` | Property-level annotations (Java: `@NotNull`, `@Email`, `@Column(...)`). |
| `isOptional` | Marks the property optional (language-specific; in Java may emit `Optional<T>` wrapper or be ignored — verify on output). |
| `isInitializer` | Adds a default value initialization. |

### 3.5 arrayTypes / dictionaryTypes (virtual — NO files)

`arrayTypes[]`: `{typeIdentifier, elementPrimitiveType? | elementTypeIdentifier}`.
`dictionaryTypes[]`: `{typeIdentifier, keyPrimitiveType?|keyTypeIdentifier?|keyType?, valuePrimitiveType?|valueTypeIdentifier?}`.

Reference these by `typeIdentifier` from properties. In Java, `arrayTypes` becomes `List<T>` and `dictionaryTypes` becomes `Map<K,V>` (auto-imported from `java.util.*`).

### 3.6 concreteGenericClasses / concreteGenericInterfaces (virtual)

Lets you say "the type `Repository<User>`" without making a separate class file:

```json
"concreteGenericClasses": [{
  "identifier": "user-repo-concrete",
  "genericClassIdentifier": "repo-generic",
  "genericArguments": [{"typeIdentifier": "user"}]
}]
```

Then a real class can `baseClassTypeIdentifier: "user-repo-concrete"` to emit `extends Repository<User>` with imports resolved.

### 3.7 customFiles

`{name, path, fileName?, identifier?, customCode[], customImports[]}`. Use for files that don't fit the class/interface/enum mold. The optional `identifier` makes the file referenceable via `customImports` from other files.

---

## 4. Critical rules (most-broken first)

1. **ONE call with the full spec.** `typeIdentifier` references resolve **only within the same `generate_code` call**. Splitting a domain across calls breaks cross-imports — the typegraph is per-call. Batch the entire DDD model in one shot.

2. **`properties` = type declarations. `customCode` = everything else.** Properties carry no logic. Methods, initialized fields, constructor bodies, anything with code → exactly one entry in `customCode`. Never inline a method into `properties`. Never use `customCode` for a bare uninitialized type declaration.

3. **Use `templateRefs` for every internal type used in `customCode` or in a free-form `type` string.** Without `templateRefs`, the engine cannot infer that an `import` is required; the resulting Java code may fail to compile due to missing imports across packages. Pattern: write `$alias` in the code/type string and add `{"placeholder": "$alias", "typeIdentifier": "user"}`.

4. **Never list standard-library imports in `customImports`.** For Java the engine auto-imports: `java.util.*`, `java.time.*`, `java.util.stream.*`, `java.math.*`, `jakarta.validation.*`, `com.fasterxml.jackson.*`. Adding these manually causes duplicates / errors. `customImports` is reserved for **external libraries** (Spring, Lombok, etc.).

5. **`templateRefs` are ONLY for internal types** (defined in the same call). External library types must use `customImports`. Don't mix: same-batch type → `typeIdentifier`/`templateRefs`; library type → `customImports`.

6. **Constructor parameters auto-become properties (Java/C#/Go/Groovy).** Do NOT also put them in `properties[]` — that yields `Sequence contains more than one matching element`. Only put truly *additional* fields in `properties`.

7. **Virtual types never produce files.** `arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`, `concreteGenericInterfaces` are reusable type references only. They surface only via being referenced from a class/interface/property.

8. **Don't reference a `typeIdentifier` that isn't in the batch** — the property is silently dropped.

9. **Avoid reserved words** (`class`, `import`, `delete`, `package`, `interface`, etc.) as property/parameter names. Use `clazz`, `importData`, `remove`, `pkg`, etc.

10. **Don't put method signatures as function-typed properties on interfaces** that a class will implement — the implementing class will end up with both the method and a duplicate property declaration. Use `customCode` for interface method signatures.

---

## 5. Java-specific guidance

### 5.1 `packageName` and file paths

- Default `packageName` for Java: `com.metaengine.generated`.
- Set it explicitly to the spec's domain root (e.g. `com.example.shop`).
- The engine writes Java files following the package layout under `outputPath`. Conventional output: `<outputPath>/com/example/shop/<path>/Foo.java`. Treat `path` on a class as a *sub-directory inside the package* (sub-package), e.g. `path: "models"` → `com.example.shop.models`. (Some setups instead nest under `src/main/java/...`; the engine always honors `outputPath` as the root and builds the package-derived directory tree below it. Pass `outputPath` accordingly if a Maven/Gradle layout is desired.)
- File naming follows Java convention: PascalCase class name → `User.java`. Override with `fileName` (no extension) if needed.

### 5.2 Type mapping (Java targets)

| Engine input | Java emission |
|---|---|
| `primitiveType: "String"` | `String` |
| `primitiveType: "Number"` | Numeric primitive — typically `int` (consistent with C# behavior). For non-integers use the free-form `type: "double"`, `type: "long"`, `type: "BigDecimal"` (java.math is auto-imported), etc. |
| `primitiveType: "Boolean"` | `boolean` (or `Boolean` when wrapped) |
| `primitiveType: "Date"` | A `java.time.*` type (the engine auto-imports `java.time.*`). Most commonly `LocalDateTime` or `Instant`. If the spec demands a specific one (`Instant` for UTC timestamps, `LocalDate` for date-only), set it explicitly via `type: "Instant"` / `type: "LocalDate"` rather than relying on `primitiveType: "Date"`. |
| `primitiveType: "Any"` | `Object` |
| `arrayTypes` reference | `List<T>` (from `java.util`) |
| `dictionaryTypes` reference | `Map<K,V>` (from `java.util`) |
| `typeIdentifier` to a class/enum | The class / enum name with import auto-added |

When in doubt about a numeric mapping, use the explicit `type` field with an unambiguous Java type name (`long`, `BigDecimal`, `UUID`).

### 5.3 Class vs record emission

The engine emits a **class** for a normal `classes[]` entry. Java records (Java 14+) are not a separate top-level mode in the schema, so:

- For DTO/value-object styles where a record is desirable, prefer plain classes with `constructorParameters` (which auto-create properties / fields). The result is a constructor-initialized class — semantically close to a record's role.
- If you specifically need `record Foo(...)`, place it inside a `customFiles` entry with the exact source as `customCode`, since the engine's class emission is class-form.
- **Don't fight the engine** on this in the warmup target — emit classes. The DDD spec will likely call for behavior-bearing entities anyway, where records are wrong.

### 5.4 `customCode` for Java method stubs

A class in DDD often declares behavior whose body the engine has no spec for. Two acceptable patterns:

- **Throwing stub**: emit a method whose body throws `UnsupportedOperationException` so the file compiles and behavior is explicit.

  ```json
  {"code": "public void register() {\n    throw new UnsupportedOperationException(\"Not implemented\");\n}"}
  ```

- **Empty body returning sensible default** (`return null;`, `return false;`, `return 0;`) — pick whichever is least surprising for the return type.

Reference internal types with `templateRefs`:

```json
{
  "code": "public $user findByEmail(String email) {\n    throw new UnsupportedOperationException();\n}",
  "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]
}
```

`UnsupportedOperationException`, `String`, etc. are in `java.lang` — no imports needed.

### 5.5 Annotations (`decorators`)

Java annotations go in `decorators[]` on a class/property. For Spring / JPA / Bean Validation:

- Bean Validation (`@NotNull`, `@Email`, `@Size`) → auto-imported (jakarta.validation.*). Don't add to `customImports`.
- Jackson (`@JsonProperty`) → auto-imported.
- Spring / Lombok / JPA → use `customImports` with the library path:

  ```json
  "customImports": [{"path": "org.springframework.stereotype", "types": ["Service"]}],
  "decorators": [{"code": "@Service"}]
  ```

### 5.6 Enums

Java enums come out idiomatically with `ALL_CAPS` member names (e.g. `Pending` → `PENDING`). The engine handles file naming as `OrderStatus.java`. Numeric `value` is preserved as constructor arg or an internal mapping where idiomatic.

### 5.7 Generics

- `genericArguments` on a class/interface produces `class Repository<T> { ... }` with constraints emitted as `<T extends BaseEntity>`.
- `concreteGenericClasses` produces inline references to `Repository<User>` — used as `baseClassTypeIdentifier` or as a templateRef target in customCode/properties.

### 5.8 Constructor parameters

Java ctor params auto-create the corresponding `private final` field plus assignment. Do NOT duplicate in `properties`. To add fields not in the constructor, list those (and only those) in `properties`.

### 5.9 Optional / nullable

`isOptional` may be honored as `Optional<T>` wrapping or skipped depending on engine version. For Java, prefer expressing nullability explicitly via `type: "Optional<$user>"` + templateRefs when nullability is part of the contract.

---

## 6. Output structure (what to expect)

- One `.java` file per `classes[]`, `interfaces[]`, `enums[]` entry (plus any `customFiles[]`).
- Files placed at `<outputPath>/<package as path>/<class.path>/<ClassName>.java`. Example: `outputPath="src/main/java"`, `packageName="com.example.shop"`, `classes[].path="models"` → `src/main/java/com/example/shop/models/User.java`.
- Each file begins with `package com.example.shop.models;` then imports (auto-resolved + `customImports`) then the type body.
- `arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`, `concreteGenericInterfaces` produce **no files** — they only contribute to type strings and imports inside other files.
- The MCP response confirms each generated file path. With `dryRun: true`, the response includes the file contents for review without touching disk.

---

## 7. Worked patterns (Java-adapted)

### 7.1 Domain entity with VO ref

```json
{
  "language": "java",
  "packageName": "com.example.shop",
  "classes": [
    {"name": "Address", "typeIdentifier": "address", "path": "model",
     "properties": [
       {"name": "street", "primitiveType": "String"},
       {"name": "city", "primitiveType": "String"}
     ]},
    {"name": "User", "typeIdentifier": "user", "path": "model",
     "properties": [
       {"name": "id", "primitiveType": "String"},
       {"name": "address", "typeIdentifier": "address"}
     ]}
  ]
}
```

### 7.2 Inheritance + behavior stub

```json
{
  "language": "java",
  "packageName": "com.example.shop",
  "classes": [
    {"name": "BaseEntity", "typeIdentifier": "base-entity", "isAbstract": true,
     "properties": [{"name": "id", "primitiveType": "String"}]},
    {"name": "Order", "typeIdentifier": "order",
     "baseClassTypeIdentifier": "base-entity",
     "properties": [
       {"name": "createdAt", "type": "Instant"}
     ],
     "customCode": [
       {"code": "public void confirm() {\n    throw new UnsupportedOperationException();\n}"}
     ]}
  ]
}
```

### 7.3 Repository interface (method signatures via customCode + templateRefs)

```json
{
  "language": "java",
  "packageName": "com.example.shop",
  "interfaces": [{
    "name": "UserRepository", "typeIdentifier": "user-repo", "path": "repository",
    "customCode": [
      {"code": "List<$user> findAll();",
       "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]},
      {"code": "Optional<$user> findById(String id);",
       "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]}
    ]
  }]
}
```

### 7.4 Enum + class using it

```json
{
  "language": "java",
  "packageName": "com.example.shop",
  "enums": [{
    "name": "OrderStatus", "typeIdentifier": "order-status", "path": "model",
    "members": [{"name": "Pending", "value": 0}, {"name": "Shipped", "value": 2}]
  }],
  "classes": [{
    "name": "Order", "typeIdentifier": "order", "path": "model",
    "properties": [{"name": "status", "typeIdentifier": "order-status"}],
    "customCode": [{
      "code": "public void updateStatus($status s) {\n    this.status = s;\n}",
      "templateRefs": [{"placeholder": "$status", "typeIdentifier": "order-status"}]
    }]
  }]
}
```

(Idiomatic Java emission will yield `OrderStatus.PENDING`, `OrderStatus.SHIPPED`.)

### 7.5 Generic repo + concrete instantiation

```json
{
  "language": "java",
  "packageName": "com.example.shop",
  "classes": [
    {"name": "BaseEntity", "typeIdentifier": "base-entity", "isAbstract": true,
     "properties": [{"name": "id", "primitiveType": "String"}]},
    {"name": "Repository", "typeIdentifier": "repo-generic",
     "genericArguments": [{
       "name": "T", "constraintTypeIdentifier": "base-entity",
       "propertyName": "items", "isArrayProperty": true
     }],
     "customCode": [
       {"code": "public void add(T item) {\n    items.add(item);\n}"},
       {"code": "public List<T> getAll() {\n    return items;\n}"}
     ]},
    {"name": "User", "typeIdentifier": "user",
     "baseClassTypeIdentifier": "base-entity",
     "properties": [{"name": "email", "primitiveType": "String"}]},
    {"name": "UserRepository", "typeIdentifier": "user-repo",
     "baseClassTypeIdentifier": "user-repo-concrete",
     "customCode": [{
       "code": "public $user findByEmail(String email) {\n    return getAll().stream().filter(u -> u.getEmail().equals(email)).findFirst().orElse(null);\n}",
       "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]
     }]}
  ],
  "concreteGenericClasses": [{
    "identifier": "user-repo-concrete",
    "genericClassIdentifier": "repo-generic",
    "genericArguments": [{"typeIdentifier": "user"}]
  }]
}
```

### 7.6 Constructor parameters (Java rule)

```json
{
  "language": "java",
  "classes": [{
    "name": "User", "typeIdentifier": "user",
    "constructorParameters": [
      {"name": "email", "primitiveType": "String"},
      {"name": "status", "typeIdentifier": "order-status"}
    ],
    "properties": [
      {"name": "createdAt", "type": "Instant"}
    ]
  }]
}
```

`email` and `status` will appear as `private final` fields with the constructor wiring them. `createdAt` is the only entry in `properties[]` — it's the *additional* field.

### 7.7 Service with external Spring dep

```json
{
  "language": "java",
  "packageName": "com.example.shop",
  "classes": [{
    "name": "UserService", "typeIdentifier": "user-service", "path": "service",
    "decorators": [{"code": "@Service"}],
    "customImports": [{"path": "org.springframework.stereotype", "types": ["Service"]}],
    "constructorParameters": [
      {"name": "users", "typeIdentifier": "user-repo"}
    ],
    "customCode": [{
      "code": "public $user register(String email) {\n    throw new UnsupportedOperationException();\n}",
      "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]
    }]
  }]
}
```

---

## 8. Common mistakes — Java-tuned checklist

1. Splitting the spec into multiple `generate_code` calls → cross-package imports break. **Do one call.**
2. Putting method bodies in `properties` instead of `customCode`.
3. Writing internal type names as raw strings in `customCode` without `templateRefs` → missing imports across packages.
4. Adding `java.util.List`, `java.time.Instant`, `jakarta.validation.constraints.NotNull`, `com.fasterxml.jackson.annotation.JsonProperty`, etc. to `customImports` → duplicates / errors. They auto-import.
5. Listing the same field in both `constructorParameters` and `properties` → "Sequence contains more than one matching element".
6. Using `primitiveType: "Number"` and assuming `double` — it likely lands as `int`. Use explicit `type: "double"` / `"long"` / `"BigDecimal"`.
7. Using `primitiveType: "Date"` and assuming a specific `java.time` type — be explicit (`type: "Instant"` or `"LocalDate"`).
8. Trying to emit a Java `record` from `classes[]` — emit a class with `constructorParameters` instead, or drop into `customFiles` for a literal record source.
9. Referencing a `typeIdentifier` that isn't defined in the same call → silently dropped.
10. Using reserved Java keywords (`class`, `package`, `import`, `interface`, `record`) as property/parameter names.

---

## 9. Quick decision tree (Java)

- Need a value object / DTO → `classes[]` with `constructorParameters` (no duplicate `properties`).
- Need an interface → `interfaces[]`; method signatures in `customCode` (with `templateRefs` for any internal types).
- Need an enum → `enums[]` with numeric `value` per member; expect `ALL_CAPS` emission.
- Need `List<Foo>` as a property → either define an `arrayTypes` entry and reference its `typeIdentifier`, OR put `type: "List<$foo>"` with `templateRefs`. Both auto-import `java.util.List`.
- Need `Map<String, Foo>` as a property → define a `dictionaryTypes` entry, reference it.
- Need `Repository<User>` → `concreteGenericClasses[]`, then use as `baseClassTypeIdentifier` or templateRef target.
- Need a method whose body is unspecified → `customCode` entry with `throw new UnsupportedOperationException("Not implemented");`.
- Need a Spring/JPA annotation → `decorators` + `customImports` (since those packages are external, not auto-imported).
- Need a Bean Validation / Jackson annotation → `decorators` only (auto-imported).
- Need a `package-info.java`, `pom.xml`, or arbitrary file → `customFiles[]`.

---

## 10. End-state checklist before calling `generate_code`

- [ ] `language: "java"` set.
- [ ] `packageName` set to the desired Java package root.
- [ ] All cross-referenced types live in this single call.
- [ ] Every `typeIdentifier` referenced is defined somewhere in the same payload.
- [ ] No fields appear in BOTH `constructorParameters` and `properties` of the same class.
- [ ] Every internal type used inside `customCode` or `type` strings has a matching `templateRefs` entry with `$placeholder`.
- [ ] No `java.util.*`, `java.time.*`, `jakarta.validation.*`, `com.fasterxml.jackson.*` paths in `customImports`.
- [ ] External library imports (Spring, Lombok, JPA, etc.) listed in `customImports`.
- [ ] No reserved-word identifiers.
- [ ] Method bodies live in `customCode` (one entry per method), not in `properties`.
- [ ] Numeric / date semantics expressed via explicit `type:` strings where `primitiveType` would be ambiguous.
