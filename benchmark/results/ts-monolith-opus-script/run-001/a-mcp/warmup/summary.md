# MetaEngine MCP — Knowledge Brief (TypeScript-focused)

This brief is the **only** documentation the next (generation) session will have. It must stand on its own. Read it once, then call `mcp__metaengine__generate_code` ONCE with the entire spec.

---

## Tools exposed by the metaengine MCP server

- `mcp__metaengine__metaengine_initialize` — returns the AI guide. (Already called during warmup.)
- `mcp__metaengine__generate_code` — the main generator. Accepts a single JSON spec describing every type/file you want, and produces all source files. **All cross-file imports/references resolve only within ONE call.**
- `mcp__metaengine__load_spec_from_file` — load a spec from disk and pass it to generate_code (alternative to inlining the spec).
- `mcp__metaengine__generate_openapi` / `generate_graphql` / `generate_protobuf` / `generate_sql` — convert specs of those formats. Not needed for greenfield TypeScript class/interface generation.

The generation session in this benchmark uses `generate_code` only.

---

## The fundamental principle

**Generate ALL related types in ONE call.** `typeIdentifier` references resolve only within the current batch. Splitting into multiple calls breaks the typegraph: cross-file imports won't be generated. Even if it feels like a lot of types, batch them all.

---

## generate_code — input schema (top-level)

The input is one JSON object. Top-level fields:

| Field | Type | Purpose |
|---|---|---|
| `language` | string | Required. One of: `typescript`, `python`, `go`, `csharp`, `java`, `kotlin`, `groovy`, `scala`, `swift`, `php`. |
| `initialize` | bool | Optional. Used for first-call setup hints. |
| `packageName` | string | Optional. Namespace/package (C#, Java, Go). For TS usually omitted. |
| `classes` | array | File-generating classes. |
| `interfaces` | array | File-generating interfaces. |
| `enums` | array | File-generating enums. |
| `customFiles` | array | Free-form files (type aliases, barrel exports). |
| `arrayTypes` | array | **Virtual** — reusable array type references. No files produced. |
| `dictionaryTypes` | array | **Virtual** — reusable dict/map type references. No files produced. |
| `concreteGenericClasses` | array | **Virtual** — concrete instantiations like `Repository<User>`. No files produced. |
| `concreteGenericInterfaces` | array | **Virtual** — same idea for interfaces. No files produced. |

**Important**: if you supply `classes` more than once at the top-level (e.g., split among sections), only one wins in JSON. Combine all classes into one array. Same for the others.

---

## Class / Interface entry — fields

Each entry in `classes[]` or `interfaces[]` supports:

| Field | Type | Notes |
|---|---|---|
| `name` | string | The type name (PascalCase). **Required.** |
| `typeIdentifier` | string | Unique kebab-case ID used by other entries to reference this type. **Required for any type that will be referenced elsewhere.** |
| `fileName` | string | Optional override for the generated file name. Use it when an `I`-prefixed interface and its impl class would clash (TS strips `I` prefix from exported names). |
| `path` | string | Optional subdirectory (e.g., `services`, `dto`). |
| `isAbstract` | bool | Abstract class. |
| `baseClassTypeIdentifier` | string | Reference to a class typeIdentifier (extends). Can also reference a `concreteGenericClasses.identifier` to extend a concrete generic. |
| `implementedInterfaceTypeIdentifiers` | string[] | Interfaces implemented (or use `concreteGenericInterfaces`). |
| `genericArguments` | array | Type-parameter declarations (see below). |
| `properties` | array | **Field declarations only** — no logic, no initializers. |
| `constructorParameters` | array | Constructor params. **In C#/Java/Go/Groovy these become properties automatically — DO NOT duplicate them in `properties[]`.** TS allows duplicating but prefer not to. |
| `customCode` | array | Methods, initialized fields, anything with logic. ONE block = ONE member. |
| `customImports` | array | External libs only — never the standard lib (auto-imported). |
| `decorators` | array | `[{ "code": "@Injectable(...)" }, ...]` |
| `comment` / `documentation` | string | XML/JSDoc-style doc. |

### Property entry (inside `properties[]`)
- `name` — field name (avoid reserved words: `delete`, `class`, `import` → use `remove`, `clazz`, `importData`).
- One of:
  - `primitiveType` — `String`, `Number`, `Boolean`, `Date`, `Any`, etc.
  - `typeIdentifier` — reference another type defined in this same call (class/interface/enum/arrayType/dictionaryType/concreteGeneric*).
  - `type` — a literal type expression (e.g., `"Map<string, $resp>"` or `"List<$user>"`); pair with `templateRefs` if it embeds internal types.
- `templateRefs` — array of `{placeholder, typeIdentifier}` to resolve `$placeholder` substrings inside `type`.
- `comment` — generates JSDoc comment.
- `isOptional` — generates nullable variant (`string?` in C#).

### customCode entry
- `code` — string. Exactly **one** member per entry (one method, one initialized field, etc.). Auto newlines added between blocks.
- `templateRefs` — `[{placeholder: "$user", typeIdentifier: "user"}, ...]`. Replaces `$user` with the resolved type name **AND** triggers import generation. Without templateRefs, MetaEngine cannot generate the import for an internal type referenced inside customCode strings.

### customImports entry
- `path` — module specifier for external libs (`@angular/core`, `rxjs`, `@nestjs/common`).
- `types` — array of imported names.
- For internal customFiles, the `path` can equal the customFile `identifier` and MetaEngine resolves the relative path.

### genericArguments entry (on a generic class/interface)
```jsonc
{
  "name": "T",                               // type-parameter name
  "constraintTypeIdentifier": "base-entity", // optional bound (extends)
  "propertyName": "items",                   // optional: auto-generates a backing field
  "isArrayProperty": true                    // auto-generates `items: T[]`
}
```

### Enum entry
- `name`, `typeIdentifier`
- `members`: `[{ "name": "Pending", "value": 0 }, ...]`
- File suffix is auto: `*.enum.ts`, `OrderStatus.cs`, etc.

### customFiles entry (for type aliases / barrel files / non-class code)
```jsonc
{
  "name": "types",
  "path": "shared",
  "identifier": "shared-types",          // makes file referenceable from customImports
  "customCode": [
    {"code": "export type UserId = string;"},
    {"code": "export type Email = string;"}
  ]
}
```

### arrayTypes entry (virtual)
```jsonc
{ "typeIdentifier": "user-list", "elementTypeIdentifier": "user" }
{ "typeIdentifier": "string-array", "elementPrimitiveType": "String" }
```
TS output: `Array<User>` / `Array<string>`. C# output: `IEnumerable<T>` (use `"type": "List<$x>"` if you need List<T>).

### dictionaryTypes entry (virtual)
Combinations: `keyPrimitiveType|keyTypeIdentifier` × `valuePrimitiveType|valueTypeIdentifier`.
```jsonc
{ "typeIdentifier": "scores", "keyPrimitiveType": "String", "valuePrimitiveType": "Number" }
{ "typeIdentifier": "user-lookup", "keyPrimitiveType": "String", "valueTypeIdentifier": "user" }
```
TS output: `Record<string, number>`, `Record<string, User>`, etc.

### concreteGenericClasses entry (virtual)
Creates a concrete instantiation usable as a base type or via templateRefs.
```jsonc
{
  "identifier": "user-repo-concrete",
  "genericClassIdentifier": "repo-generic",   // refers to a class with genericArguments
  "genericArguments": [{"typeIdentifier": "user"}]
}
```
Then `"baseClassTypeIdentifier": "user-repo-concrete"` produces `class UserRepository extends Repository<User>` with imports.

### concreteGenericInterfaces — same idea, for interfaces.

---

## CRITICAL RULES (most violations cause compile errors)

1. **ONE call.** All related types in a single `generate_code` invocation. `typeIdentifier` is batch-scoped.

2. **Properties = type declarations only. CustomCode = anything with initializer or logic.**
   - `properties` = uninitialized field declarations (`id: string`, `email: string`).
   - `customCode` = methods, initialized fields (`private http = inject(HttpClient);`), getters, etc.
   - One `customCode` block = one member. Don't shove multiple methods in one string.

3. **Use `templateRefs` whenever a customCode/`type` string mentions an internal type.** Without `templateRefs`, no import will be generated. Use `$placeholder` syntax. Example:
   ```jsonc
   { "code": "getUser(): Promise<$user> { ... }",
     "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}] }
   ```

4. **Never put framework/stdlib imports in `customImports`.** TS has no auto-imports needed (built-ins). For other langs, MetaEngine auto-handles `System.*`, `typing.*`, `java.util.*`, etc. `customImports` is only for actual external libraries (`@angular/core`, `rxjs`, etc.).

5. **`templateRefs` is for INTERNAL types only.** External library types use `customImports`. Same-batch types use `typeIdentifier`/`templateRefs`.

6. **Constructor parameters auto-become properties** in C#/Java/Go/Groovy — never duplicate them in `properties[]` (causes "Sequence contains more than one matching element" error). For TypeScript the duplication is silently allowed but still wrong; treat the same way.

7. **Virtual types (`arrayTypes`, `dictionaryTypes`, `concreteGeneric*`) don't generate files.** They exist purely as referenceable type identifiers.

8. **Interface method signatures go in `customCode`** (e.g., `"findAll(): Promise<$user[]>;"` with templateRefs), NOT as function-typed properties. If you put them in properties, the implementing class will end up with duplicated property declarations alongside its method implementations.

9. **Avoid reserved words** as property names: `delete`, `class`, `import`. Use safe alternatives.

10. **Don't reference a `typeIdentifier` that isn't defined in the same batch** — the property is silently dropped.

---

## TypeScript-specific notes (this benchmark is TypeScript)

- TS strips the leading `I` from interface names when exporting. `IUserRepository` → `export interface UserRepository`. If a file collision results, set `fileName: "i-user-repository"` on the interface.
- Primitive type mapping: `Number` → `number`, `String` → `string`, `Boolean` → `boolean`, `Date` → `Date`, `Any` → `unknown`.
- No `customImports` needed for built-in types — TS has them all natively.
- `arrayTypes` produce `Array<T>` (never `T[]` syntax).
- `dictionaryTypes` produce `Record<K, V>`.
- `customCode` newlines (`\n`) are auto-indented. Multi-line bodies are fine inside one string.
- Decorators (`@Injectable(...)`) supported directly via `decorators: [{code: "@Injectable(...)"}]`.
- Class fields generate as `name!: Type;` for required; `name?: Type;` if `isOptional: true`. Simple primitives initialize (`id = '';`).
- File naming: classes/interfaces → kebab-case `.ts`. Enums → `*.enum.ts`. Subpath via `path` field.

---

## Patterns you will likely need

### A. Plain interface + class with cross-reference
```jsonc
{
  "language": "typescript",
  "interfaces": [{
    "name": "Address", "typeIdentifier": "address",
    "properties": [
      {"name": "street", "primitiveType": "String"},
      {"name": "city", "primitiveType": "String"}
    ]
  }],
  "classes": [{
    "name": "User", "typeIdentifier": "user",
    "properties": [
      {"name": "id", "primitiveType": "String"},
      {"name": "address", "typeIdentifier": "address"}
    ]
  }]
}
```

### B. Enum + class that uses it
```jsonc
{
  "enums": [{
    "name": "OrderStatus", "typeIdentifier": "order-status",
    "members": [
      {"name": "Pending", "value": 0},
      {"name": "Shipped", "value": 2}
    ]
  }],
  "classes": [{
    "name": "Order", "typeIdentifier": "order",
    "properties": [{"name": "status", "typeIdentifier": "order-status"}],
    "customCode": [{
      "code": "updateStatus(s: $status): void { this.status = s; }",
      "templateRefs": [{"placeholder": "$status", "typeIdentifier": "order-status"}]
    }]
  }]
}
```

### C. Class with inheritance + method using internal type
```jsonc
{
  "classes": [
    {"name": "BaseEntity", "typeIdentifier": "base-entity", "isAbstract": true,
     "properties": [{"name": "id", "primitiveType": "String"}]},
    {"name": "User", "typeIdentifier": "user",
     "baseClassTypeIdentifier": "base-entity",
     "properties": [{"name": "email", "primitiveType": "String"}],
     "customCode": [{"code": "getDisplayName(): string { return this.email; }"}]}
  ]
}
```

### D. Generic class + concrete instantiation as base
```jsonc
{
  "classes": [
    {"name": "Repository", "typeIdentifier": "repo-generic",
     "genericArguments": [{
       "name": "T", "constraintTypeIdentifier": "base-entity",
       "propertyName": "items", "isArrayProperty": true
     }],
     "customCode": [
       {"code": "add(item: T): void { this.items.push(item); }"},
       {"code": "getAll(): T[] { return this.items; }"}
     ]},
    {"name": "User", "typeIdentifier": "user",
     "baseClassTypeIdentifier": "base-entity",
     "properties": [{"name": "email", "primitiveType": "String"}]},
    {"name": "UserRepository", "typeIdentifier": "user-repo-class",
     "baseClassTypeIdentifier": "user-repo-concrete",
     "customCode": [{
       "code": "findByEmail(email: string): $user | undefined { return this.getAll().find(u => u.email === email); }",
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

### E. Service with external DI imports
```jsonc
{
  "classes": [{
    "name": "ApiService", "typeIdentifier": "api-service",
    "decorators": [{"code": "@Injectable({ providedIn: 'root' })"}],
    "customImports": [
      {"path": "@angular/core", "types": ["Injectable", "inject"]},
      {"path": "@angular/common/http", "types": ["HttpClient"]},
      {"path": "rxjs", "types": ["Observable"]}
    ],
    "customCode": [
      {"code": "private http = inject(HttpClient);"},
      {"code": "getUsers(): Observable<$list> { return this.http.get<$list>('/api/users'); }",
       "templateRefs": [{"placeholder": "$list", "typeIdentifier": "user-array"}]}
    ]
  }],
  "arrayTypes": [{"typeIdentifier": "user-array", "elementTypeIdentifier": "user-dto"}]
}
```

### F. Type aliases via customFiles
```jsonc
{
  "customFiles": [{
    "name": "types", "path": "utils", "identifier": "shared-types",
    "customCode": [
      {"code": "export type UserId = string;"},
      {"code": "export type Status = 'active' | 'inactive' | 'pending';"}
    ]
  }],
  "classes": [{
    "name": "UserService", "typeIdentifier": "service", "path": "services",
    "customImports": [{"path": "../utils/types", "types": ["UserId", "Status"]}],
    "customCode": [
      {"code": "updateStatus(id: UserId, status: Status): void { }"}
    ]
  }]
}
```

### G. Interface with method signatures (for class to implement)
```jsonc
{
  "interfaces": [{
    "name": "IUserRepository", "typeIdentifier": "user-repo",
    "fileName": "i-user-repository",
    "customCode": [
      {"code": "findAll(): Promise<$user[]>;",
       "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]},
      {"code": "findById(id: string): Promise<$user | null>;",
       "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]}
    ]
  }]
}
```

### H. Constructor parameters (CRITICAL — don't duplicate)
```jsonc
{
  "enums": [{
    "name": "Status", "typeIdentifier": "status",
    "members": [{"name": "Active", "value": 1}]
  }],
  "classes": [{
    "name": "User", "typeIdentifier": "user",
    "constructorParameters": [
      {"name": "email", "type": "string"},
      {"name": "status", "typeIdentifier": "status"}
    ],
    "properties": [
      {"name": "createdAt", "primitiveType": "Date"}    // ONLY non-constructor fields
    ]
  }]
}
```
Output:
```typescript
import { Status } from './status.enum';
export class User {
  createdAt!: Date;
  constructor(public email: string, public status: Status) {}
}
```

### I. Complex type expressions with templateRefs
```jsonc
"properties": [{
  "name": "cache",
  "type": "Map<string, $resp>",
  "templateRefs": [{"placeholder": "$resp", "typeIdentifier": "api-response"}]
}]
```

---

## Output structure

`generate_code` returns:
- A list of generated files, each with relative path and full source content.
- Imports are auto-resolved (relative paths between files in the same call).
- Decorators, generics, inheritance, and templateRef substitutions are all materialized.
- Empty/no-error response on success; errors include messages like "Sequence contains more than one matching element" (constructor param duplication) or silent property drops (unknown typeIdentifier).

The harness writes the resulting files into the working directory; the gen session does not need to manage files manually beyond invoking the tool.

---

## Common mistakes — avoid these

1. **Splitting types across multiple `generate_code` calls.** Cross-file imports break. Always one call.
2. **Method signatures as function-typed properties on interfaces** (`"type": "() => Promise<User[]>"`) → causes class to duplicate them as fields. Use `customCode` for interface method signatures.
3. **Raw internal type names in customCode strings** (e.g., `"private repo: IUserRepository"`) without `templateRefs` → no import generated → compile failure. Always use `$placeholder` + `templateRefs` for internal types.
4. **Adding stdlib/framework imports to `customImports`** → duplication / errors. Let the engine auto-handle them.
5. **Duplicating constructor parameters in `properties[]`** → "Sequence contains more than one matching element". Constructor params auto-become properties (in non-TS especially).
6. **Reserved words as property names** (`delete`, `class`, `import`) → compile errors. Use `remove`, `clazz`, `importData`.
7. **Referencing a typeIdentifier that isn't in the batch** → property silently dropped. Verify every reference resolves to a defined type in the same call.
8. **Interface name collision in TS** when both `IFoo` (exports as `Foo`) and a class `Foo` are generated. Set `fileName: "i-foo"` on the interface.
9. **One `customCode` block containing multiple methods** → only the first will be a recognized member. One block per member.
10. **Forgetting `typeIdentifier`** on a type that other entries reference → no way to wire it up.

---

## Mental model for building a spec

1. Enumerate every type in the domain (entities, DTOs, services, enums, unions, aliases).
2. Assign a kebab-case `typeIdentifier` to each that anything else will reference.
3. For each type, decide:
   - Plain field? → `properties[]` with `primitiveType` / `typeIdentifier`.
   - Initialized field or method? → `customCode[]` (one block per member).
   - Internal type used inside the code string? → wrap with `$placeholder` + `templateRefs`.
   - External lib needed? → `customImports[]`.
4. For collections: declare an `arrayTypes` or `dictionaryTypes` entry once, reuse via its `typeIdentifier`.
5. For `Foo<Bar>` as a base class or property type: add a `concreteGenericClasses` entry, then reference its `identifier`.
6. Submit ONE call with `classes`, `interfaces`, `enums`, `customFiles`, `arrayTypes`, `dictionaryTypes`, `concreteGenericClasses` all populated as needed.

This is the entire mental model. Don't over-engineer — the engine does the import wiring.

WARMUP_DONE
