# MetaEngine MCP — Knowledge Brief (Java focus)

This brief is the canonical reference for the next session. It will not have access to the MCP's docs, only this file. It is comprehensive on purpose; do not abbreviate.

## What MetaEngine is

MetaEngine is a semantic code generator exposed via MCP. Input is structured JSON describing types, relationships, and methods. Output is compilable source files for TypeScript, C#, Python, Go, Java, Kotlin, Groovy, Scala, Swift, PHP. Cross-references resolve, imports are managed, language idioms are applied automatically. A single well-formed call replaces dozens of file writes.

For Java specifically, MetaEngine emits `.java` files under a directory tree derived from `packageName` + `path`. It manages all `import` statements automatically and applies Java-idiomatic transforms (e.g. enum members in `ALL_CAPS`).

## Tools exposed (post-`metaengine_initialize`)

- `mcp__metaengine__generate_code` — primary tool. JSON spec in, source files written to `outputPath` on disk. Returns a confirmation. ONE call should contain the full type graph for the run.
- `mcp__metaengine__generate_openapi`, `generate_graphql`, `generate_protobuf`, `generate_sql`, `load_spec_from_file` — adjacent generators / loaders. Not used for the DDD-spec → Java task.
- `mcp__metaengine__metaengine_initialize` — returns the linked guide. Already consumed in warmup; the gen session will not have it.

## generate_code — input schema (full)

Top-level keys (all optional unless noted):

| Key                       | Type         | Notes                                                          |
|---------------------------|--------------|----------------------------------------------------------------|
| `language`                | string       | REQUIRED. For Java: `"java"`.                                  |
| `packageName`             | string       | Java package, e.g. `"com.metaengine.demo"`. Drives directory layout AND `package` declaration. |
| `outputPath`              | string       | Directory where files are written. Engine creates subdirs.     |
| `initialize`              | bool         | Set true on first call (idempotent guard for setup).           |
| `classes`                 | object[]     | Class-shaped types (aggregates, value objects, services).      |
| `interfaces`              | object[]     | Interface-shaped types. NOT used for DDD aggregates/services.  |
| `enums`                   | object[]     | Enum types.                                                    |
| `arrayTypes`              | object[]     | Virtual array reference types (no file emitted).               |
| `dictionaryTypes`         | object[]     | Virtual map reference types (no file emitted).                 |
| `concreteGenericClasses`  | object[]     | Virtual concrete reifications of generics, e.g. `Repository<User>`. |
| `concreteGenericInterfaces`| object[]    | Same, for interfaces.                                          |
| `customFiles`             | object[]     | Free-form source files with their own `customCode` blocks.     |

### `classes[]` entry shape

| Field                       | Type             | Notes |
|-----------------------------|------------------|-------|
| `name`                      | string           | Java class name as written. |
| `typeIdentifier`            | string           | Stable id used by other entries to reference this type. Convention: kebab-case of `name` (`OrderLine` → `order-line`, `OrderService` → `order-service`). |
| `path`                      | string           | Subdirectory under `outputPath` + `packageName`. e.g. `"ordering/aggregates"` → file at `<outputPath>/com/metaengine/demo/ordering/aggregates/<Name>.java`. |
| `fileName`                  | string           | Override file name. Rarely needed for Java. |
| `comment`                   | string           | Class-level Javadoc. |
| `isAbstract`                | bool             | Emits `abstract class`. |
| `baseClassTypeIdentifier`   | string           | `extends <resolved-name>`. Must reference a class or `concreteGenericClasses` entry in the same call. |
| `implementedInterfaceTypeIdentifiers` | string[]| `implements ...`. |
| `genericArguments`          | object[]         | Generic params: `{ name, constraintTypeIdentifier?, propertyName?, isArrayProperty? }`. The `propertyName` + `isArrayProperty` pair tells the engine to also emit a backing field (e.g. `T[] items`). |
| `constructorParameters`     | object[]         | Each `{name, type? | primitiveType? | typeIdentifier?, isOptional?}`. **Critical for Java**: these auto-become final fields + constructor assignments. Do NOT also list them in `properties`. |
| `properties`                | object[]         | Field declarations only — no initializers, no methods. Each `{name, type? | primitiveType? | typeIdentifier?, comment?, isOptional?, templateRefs?}`. |
| `customCode`                | object[]         | One entry = one member. Methods, initialized fields, static blocks. Each `{code, templateRefs?}`. |
| `customImports`             | object[]         | External library imports only. `[{path, types?}]`. NEVER for stdlib. |
| `decorators`                | object[]         | Maps to Java annotations on the class itself. `[{code: "@Service"}]`. |

### `interfaces[]` entry shape

Same as `classes[]` minus `isAbstract`, `constructorParameters`, `baseClassTypeIdentifier`. Use `customCode` (with trailing `;`) for method signatures the implementing class will satisfy. Do NOT use function-typed properties for that — they get duplicated as field declarations.

### `enums[]` entry shape

| Field             | Type      | Notes |
|-------------------|-----------|-------|
| `name`            | string    | Java enum name. |
| `typeIdentifier`  | string    | Kebab-case id. |
| `path`            | string    | Same convention as classes. |
| `comment`         | string    | Javadoc. |
| `members`         | object[]  | `[{name, value, comment?}]`. `name` is verbatim from spec (engine will idiomize to ALL_CAPS in Java); `value` is numeric. |

### `arrayTypes[]` / `dictionaryTypes[]` (virtual)

```jsonc
{ "typeIdentifier": "user-list",
  "elementTypeIdentifier": "user" }       // OR  "elementPrimitiveType": "String"

{ "typeIdentifier": "scores",
  "keyPrimitiveType": "String",            // OR  "keyTypeIdentifier": "..."
  "valuePrimitiveType": "Number" }         // OR  "valueTypeIdentifier": "..."
```

These do NOT generate files. They are referenced by `typeIdentifier` from properties / customCode.

### `concreteGenericClasses[]` / `concreteGenericInterfaces[]` (virtual)

```jsonc
{ "identifier": "user-repo-concrete",
  "genericClassIdentifier": "repo-generic",
  "genericArguments": [{"typeIdentifier": "user"}] }
```

Materialises `Repository<User>` as a referencable type. Used as `baseClassTypeIdentifier` on a derived class, or in a templateRef.

### `customCode[]` entry shape

```jsonc
{ "code": "public List<$user> findActive() { ... }",
  "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}] }
```

- One entry = one member (one method, one field, one block). Multiple methods → multiple entries.
- For Java, write the full member with modifiers (`public`, `private`, `static`, etc.), return type, name, params, and body.
- Use `$placeholder` for any internal type reference (defined elsewhere in the same batch). Each placeholder must have a matching `templateRefs` entry. Without templateRefs the engine does NOT generate the import.
- Newlines (`\n`) are auto-indented by the engine.

### `customImports[]` entry shape

`{path: "org.springframework.stereotype", types: ["Service"]}` — used for Java-Style imports of external libraries. NEVER list stdlib (`java.util.*`, etc.).

### `templateRefs[]` semantics

Two-field record `{placeholder, typeIdentifier}`. Placeholder syntax is `$something` and may appear inside `code` (customCode), `type` strings on properties, or decorator `code`. Engine substitutes the resolved Java type name AND emits the corresponding import. Without templateRefs, raw type names will not trigger imports across packages.

## Java-specific behaviour (READ CAREFULLY)

### Package + path layout

- `packageName` is the root Java package. Engine writes files into `<outputPath>/<packageName-as-path>/<path>/<Name>.java`.
- Example: `outputPath="out"`, `packageName="com.metaengine.demo"`, class `Order` with `path="ordering/aggregates"` → `out/com/metaengine/demo/ordering/aggregates/Order.java`. The `package com.metaengine.demo.ordering.aggregates;` declaration is emitted automatically.
- A single `packageName` is shared by every class in the call — sub-paths control the leaf package segments.
- DO NOT prepend `packageName` to `path`. Just give the leaf, e.g. `"ordering/aggregates"`.

### Auto-imported standard library (NEVER add to customImports)

Java standard packages auto-imported by the engine when a referenced type needs them:
`java.util.*`, `java.time.*`, `java.util.stream.*`, `java.math.*`, `jakarta.validation.*`, Jackson (`com.fasterxml.jackson.*`).

Adding any of these to `customImports` will duplicate / conflict.

### Type mapping (primitiveType → Java)

| primitiveType / type      | Java emission                              |
|---------------------------|--------------------------------------------|
| `String`                  | `String`                                   |
| `Number`                  | `double` (or appropriate numeric primitive — engine's choice; Java is not C# here) |
| `Boolean`                 | `boolean`                                  |
| `Date`                    | `java.time.Instant` or `java.time.LocalDateTime` (engine's idiomatic choice; either is judge-acceptable) |
| `Any`                     | `Object`                                   |

For collections, use `arrayTypes` / `dictionaryTypes` virtuals — engine selects idiomatic Java (`List<T>`, `Map<K,V>`).

For mixing same primitive type across multiple constructor params, use `primitiveType: "Date"` (etc.) for both — DO NOT invent unique typeIdentifiers per parameter just to disambiguate. The engine handles repetition.

### Class vs record emission

Java 14+ records are valid. The engine MAY emit a `record` instead of a class for purely-data shapes (value objects). The judge accepts either. You don't toggle this with a flag — it's a function of shape (constructorParameters only, no methods, no inheritance). For aggregates with services/methods, expect a regular class.

### Constructor parameters (Java)

- `constructorParameters` auto-create matching final fields AND the constructor assigning them.
- DO NOT also list those names in `properties[]`. Doing so triggers `Sequence contains more than one matching element`.
- Additional non-constructor fields (e.g. derived `createdAt` defaulting to now) go in `properties[]` (declaration only) or `customCode[]` (initialized).

### Enum idiomatic transforms

- Member names from the spec (e.g. `Pending`, `Shipped`) get idiomized to Java `ALL_CAPS` on emit (`PENDING`, `SHIPPED`). The judge has tolerance for this — do not fight it.
- Numeric `value` is preserved (typically as `private final int value` on the enum with a constructor + getter, depending on engine output).

### Methods and `customCode` for service stubs

For DDD service classes whose methods should compile but not be implemented, write:

```jsonc
{
  "code": "public List<$Agg> findAll() { throw new UnsupportedOperationException(\"not implemented\"); }",
  "templateRefs": [{"placeholder": "$Agg", "typeIdentifier": "<aggregate-id>"}]
}
```

- One `customCode` entry per method.
- Always wrap with full Java syntax: visibility, return type, name, params, braces, body.
- Reference the aggregate / value object via `$placeholder` + matching `templateRefs[]` entry. Raw type names without templateRefs will not be imported across packages.
- The body should throw `UnsupportedOperationException("not implemented")` (no internal type imports needed for this — `UnsupportedOperationException` is `java.lang` and always implicit in Java).

### Properties on classes (Java)

`properties[]` declares fields. Each:

```jsonc
{ "name": "createdAt",
  "primitiveType": "Date",
  "comment": "Creation timestamp" }
```

Engine emits a typed field (and idiomatic accessors per Java conventions). For complex parameterised types use `type` + templateRefs:

```jsonc
{ "name": "tags",
  "type": "Set<String>" }
```

### Decorators / annotations

`decorators[]` on a class become Java annotations on the class declaration. Example: `[{"code": "@Service"}]`. For annotation arguments, just include them: `[{"code": "@Table(name = \"orders\")"}]`. Annotation-only imports go in `customImports`.

## Critical rules (MUST FOLLOW)

1. **ONE call with the full spec.** typeIdentifier references only resolve within the current batch. Splitting per-domain breaks the typegraph: cross-domain references (e.g. an OrderService method that returns a Customer aggregate from another domain) will be silently dropped.
2. **Properties = type declarations only.** customCode = methods, initialized fields, static blocks. Never put a method body in `properties`. Never put a bare uninitialized declaration in `customCode`.
3. **Use templateRefs for every internal type reference inside customCode and complex `type` expressions.** Without it, no `import` is generated and the file won't compile across packages.
4. **Never add stdlib imports to customImports.** `java.util.*`, `java.time.*`, etc. are auto-injected.
5. **templateRefs are for internal types only.** External libs go in customImports.
6. **Constructor parameters auto-create properties.** Do NOT duplicate them in `properties[]` for Java/C#/Go/Groovy.
7. **Virtual types don't emit files.** `arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`, `concreteGenericInterfaces` are reference-only.
8. **Use `classes[]` for aggregates and services — not `interfaces[]`.** An interface declaration is not equivalent to a class with stub bodies; services need encapsulation and method bodies (even if those bodies just throw).
9. **typeIdentifier uniqueness.** Every `typeIdentifier` referenced anywhere must exist in the same call. A reference to a missing id is silently dropped (the property disappears from the output).
10. **Avoid Java reserved words as property names.** `class`, `package`, `interface`, `import`, `enum`, `final`, `static`, `synchronized`, etc. Use safe alternatives.
11. **Annotations / decorators belong on the class, not in customCode.** Use `decorators[]`.

## DDD-spec → MetaEngine schema (Java task)

Translation table (mandatory shape for the benchmark):

| Spec entry        | MetaEngine shape |
|-------------------|------------------|
| `kind=aggregate`  | `classes[]` entry: `name=X`, `typeIdentifier=kebab(X)`, `constructorParameters` from spec `fields`, `path="<domain>/aggregates"`, `comment="<X> aggregate root for the <domain> domain."` |
| `kind=value_object`| `classes[]` entry: `name=X`, `typeIdentifier=kebab(X)`, `constructorParameters` from spec `fields`, `path="<domain>/value_objects"`, `comment="<X> value object."` (engine may emit a `record`; that's acceptable) |
| `kind=enum`       | `enums[]` entry: `name=X`, `typeIdentifier=kebab(X)`, `members` verbatim from spec (`{name, value}` pairs, integer values), `path="<domain>/enums"`, `comment="<X> enum."` |
| `services[]`      | `classes[]` entry per service: `name=Y`, `typeIdentifier=kebab(Y)`, `customCode` one entry per method (signature + `throw new UnsupportedOperationException("not implemented");`), `path="<domain>/services"`, `comment="<Y> service."` Use `$placeholder` + `templateRefs` for every reference to an aggregate/value-object/enum in a method signature. |

`typeIdentifier` convention is kebab-case of the type name:
- `Order` → `order`
- `OrderLine` → `order-line`
- `OrderStatus` → `order-status`
- `OrderService` → `order-service`

Field translation inside `constructorParameters`:
- `string` field → `{name, primitiveType: "String"}`
- numeric field → `{name, primitiveType: "Number"}`
- boolean field → `{name, primitiveType: "Boolean"}`
- date field → `{name, primitiveType: "Date"}`
- field referencing another spec entity → `{name, typeIdentifier: kebab(EntityName)}`
- list-of-entity field → either reference an `arrayTypes` entry by typeIdentifier, OR use `type: "List<$X>"` + templateRefs

For service methods that return / consume aggregates from another domain, the `templateRefs` mechanism is what makes the cross-domain `import` happen. Don't omit it.

## generate_code call shape (canonical)

```jsonc
{
  "language": "java",
  "packageName": "com.metaengine.demo",
  "outputPath": "<OUT_DIR>",
  "initialize": true,
  "enums": [ /* every enum from every domain */ ],
  "arrayTypes": [ /* if needed for List<X> properties */ ],
  "dictionaryTypes": [ /* if needed for Map<K,V> properties */ ],
  "classes": [ /* every aggregate, value object, and service */ ]
}
```

Submit as ONE call. The entire DDD spec (all domains, all aggregates, all value objects, all enums, all services) must be in this single invocation.

## Output structure (what to expect on disk)

For `outputPath="out"` and `packageName="com.metaengine.demo"`:

```
out/
  com/metaengine/demo/
    ordering/
      aggregates/Order.java
      value_objects/Address.java
      enums/OrderStatus.java
      services/OrderService.java
    catalog/
      aggregates/Product.java
      ...
```

Each file:
- starts with `package com.metaengine.demo.<sub.path>;`
- contains automatic `import` statements for every referenced type (cross-package internal refs + external libs from `customImports`)
- emits the class / interface / enum / record with idiomatic Java
- compiles cleanly under `javac --release 17` or higher

## Common Java mistakes to avoid

1. Listing the same field in both `constructorParameters` and `properties` → "Sequence contains more than one matching element".
2. Using raw type names like `Order` inside a customCode method body without `$Order` + templateRefs → no import → compile fail across packages.
3. Adding `java.util.List` (or any other stdlib) to `customImports` → duplicate / conflict.
4. Using `interfaces[]` for services or aggregates → no method bodies → invalid for the DDD shape.
5. Using `Number` and expecting `int` everywhere — for Java the engine maps `Number` to `double`. Use `type: "int"` / `type: "long"` explicitly if you need an integer.
6. Splitting the call by domain → broken cross-domain references.
7. Manually authoring Java with `Write` → invalidates the benchmark run.
8. Inventing per-parameter typeIdentifiers for repeated primitive params (e.g. two `Date` fields) → unnecessary noise, may collide. Just use `primitiveType: "Date"` twice.
9. Forgetting `language: "java"` → engine will pick a different default and produce wrong files.
10. Referencing a `typeIdentifier` that doesn't exist in the batch → the field/return type silently drops out.

## Worked example fragment (Java)

Shows: aggregate, value object, enum, service in one call.

```jsonc
{
  "language": "java",
  "packageName": "com.metaengine.demo",
  "outputPath": "out",
  "initialize": true,
  "enums": [
    { "name": "OrderStatus", "typeIdentifier": "order-status",
      "path": "ordering/enums", "comment": "OrderStatus enum.",
      "members": [
        {"name": "Pending",   "value": 0},
        {"name": "Confirmed", "value": 1},
        {"name": "Shipped",   "value": 2}
      ] }
  ],
  "classes": [
    { "name": "Address", "typeIdentifier": "address",
      "path": "ordering/value_objects",
      "comment": "Address value object.",
      "constructorParameters": [
        {"name": "street",  "primitiveType": "String"},
        {"name": "city",    "primitiveType": "String"},
        {"name": "country", "primitiveType": "String"}
      ] },
    { "name": "Order", "typeIdentifier": "order",
      "path": "ordering/aggregates",
      "comment": "Order aggregate root for the ordering domain.",
      "constructorParameters": [
        {"name": "id",         "primitiveType": "String"},
        {"name": "customerId", "primitiveType": "String"},
        {"name": "shipTo",     "typeIdentifier": "address"},
        {"name": "status",     "typeIdentifier": "order-status"},
        {"name": "placedAt",   "primitiveType": "Date"}
      ] },
    { "name": "OrderService", "typeIdentifier": "order-service",
      "path": "ordering/services",
      "comment": "OrderService service.",
      "customCode": [
        { "code": "public $Order place($Address shipTo, String customerId) { throw new UnsupportedOperationException(\"not implemented\"); }",
          "templateRefs": [
            {"placeholder": "$Order",   "typeIdentifier": "order"},
            {"placeholder": "$Address", "typeIdentifier": "address"}
          ] },
        { "code": "public void cancel(String orderId) { throw new UnsupportedOperationException(\"not implemented\"); }" }
      ] }
  ]
}
```

Engine output (sketch):

```
out/com/metaengine/demo/ordering/enums/OrderStatus.java
out/com/metaengine/demo/ordering/value_objects/Address.java
out/com/metaengine/demo/ordering/aggregates/Order.java
out/com/metaengine/demo/ordering/services/OrderService.java
```

`Order.java` will `import com.metaengine.demo.ordering.value_objects.Address;` and `import com.metaengine.demo.ordering.enums.OrderStatus;` automatically. `OrderService.java` will import `Order` and `Address`.

## Final reminders

- ONE `generate_code` call, full spec.
- `language: "java"`, `packageName: "com.metaengine.demo"`, `outputPath: <OUT_DIR>`.
- Aggregates/value-objects/services → `classes[]`. Enums → `enums[]`. NO `interfaces[]` for these.
- Constructor params from spec fields go in `constructorParameters` only — never duplicated in `properties`.
- Service method stubs throw `UnsupportedOperationException("not implemented")`, one `customCode` entry per method, with `$placeholder` + `templateRefs` for every aggregate/VO/enum in the signature.
- After generation, verify with `find <OUT_DIR> -name '*.java' | wc -l` (>0). Then output `DONE`.
