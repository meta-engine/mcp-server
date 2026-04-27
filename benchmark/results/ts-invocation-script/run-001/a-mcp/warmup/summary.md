# MetaEngine MCP — Knowledge Brief (TypeScript focus)

A self-contained reference for using the `metaengine` MCP server to generate TypeScript source files in ONE call from a structured JSON spec. Read end-to-end before generating.

---

## What it is

MetaEngine is a **semantic** code generator (not template-based). You describe types, relationships, methods, and decorators as structured JSON. The engine produces compilable, correctly-imported source files for TypeScript, Python, Go, C#, Java, Kotlin, Groovy, Scala, Swift, PHP, Rust. It resolves cross-references, manages imports, and applies language idioms automatically. A single MCP call replaces dozens of file writes.

---

## Tools exposed by the `metaengine` server

1. `mcp__metaengine__metaengine_initialize(language?)` — returns the AI guide. **Don't call again if you already have this brief.**
2. `mcp__metaengine__generate_code(spec)` — primary tool. Generates files from an inline JSON spec. Schema in detail below.
3. `mcp__metaengine__load_spec_from_file({ specFilePath, outputPath?, skipExisting?, dryRun? })` — same engine as `generate_code`, but loads the spec from a `.json` file on disk. Use this for very large specs to avoid bloating context. Spec file structure is identical to `generate_code` arguments.
4. `mcp__metaengine__generate_openapi(...)`, `generate_graphql(...)`, `generate_protobuf(...)`, `generate_sql(...)` — convert OpenAPI / GraphQL / Protobuf / SQL specs to code. Not used in this benchmark.

There are also two MCP **resources** at:
- `metaengine://guide/ai-assistant`
- `metaengine://guide/examples`

(Both are summarized into this brief; you do not need to re-fetch them.)

---

## generate_code — full input schema

Top-level fields (all optional unless noted):

| Field | Type | Notes |
|---|---|---|
| `language` | enum (REQUIRED) | `"typescript" \| "python" \| "go" \| "csharp" \| "java" \| "kotlin" \| "groovy" \| "scala" \| "swift" \| "php" \| "rust"` |
| `outputPath` | string | Directory for generated files. Default `.` |
| `packageName` | string | Module/namespace. TS doesn't need it. |
| `initialize` | boolean | Whether properties get default-value initializers. Default `false`. |
| `skipExisting` | boolean | Don't overwrite existing files. Default `true`. |
| `dryRun` | boolean | Preview only; returns code in response, writes nothing. Default `false`. |
| `classes` | Class[] | Class definitions (regular + generic templates). |
| `interfaces` | Interface[] | Interface definitions (regular + generic templates). |
| `enums` | Enum[] | Enum definitions. |
| `arrayTypes` | ArrayType[] | Virtual array types. **No file generated.** Reference via `typeIdentifier`. |
| `dictionaryTypes` | DictType[] | Virtual dict/map types. **No file generated.** |
| `concreteGenericClasses` | Concrete[] | Virtual concrete generic class types like `Repository<User>`. **No file generated.** |
| `concreteGenericInterfaces` | Concrete[] | Same, for generic interfaces. **No file generated.** |
| `customFiles` | CustomFile[] | Free-form files (type aliases, barrel exports, helpers) without a class wrapper. |

### Class object

```ts
{
  name: string,                       // "User"
  typeIdentifier: string,             // unique key, e.g. "user" — used for cross-references
  path?: string,                      // dir, e.g. "models" or "services/auth"
  fileName?: string,                  // without extension; overrides default naming
  comment?: string,                   // doc comment
  isAbstract?: boolean,
  baseClassTypeIdentifier?: string,   // extends — references another typeIdentifier
                                      // (can be a concreteGenericClasses identifier)
  interfaceTypeIdentifiers?: string[],// implements
  genericArguments?: GenericArg[],    // makes this a generic template (e.g. Repository<T>)
  constructorParameters?: Param[],    // auto-become properties in TS public-modifier syntax
  properties?: Property[],            // type declarations only (no logic, no init expressions)
  customCode?: CustomCodeBlock[],     // methods + initialized fields; ONE block = ONE member
  decorators?: CustomCodeBlock[],     // class-level decorators
  customImports?: ImportSpec[],       // ONLY for external libs; never for std lib
}
```

### Interface object

Same shape as class, but `properties` map to interface properties and `customCode` defines method **signatures** (not bodies). `genericArguments`, `interfaceTypeIdentifiers` (extends), `customImports`, `decorators`, `fileName`, `path`, `name`, `typeIdentifier`, `comment` all supported.

### Property object

```ts
{
  name: string,
  // Pick ONE of:
  primitiveType?: "String" | "Number" | "Boolean" | "Date" | "Any",
  typeIdentifier?: string,            // reference to another generated type
  type?: string,                      // raw type expression — e.g. "Map<string, $resp>", "List<$user>"
  // Modifiers:
  isOptional?: boolean,
  isInitializer?: boolean,            // add default-value init
  comment?: string,
  commentTemplateRefs?: TemplateRef[],
  decorators?: CustomCodeBlock[],     // property decorators (e.g. @IsEmail())
  templateRefs?: TemplateRef[],       // when `type` uses $placeholders
}
```

### CustomCodeBlock

```ts
{
  code: string,                       // a single member (method, initialized field, statement)
  templateRefs?: TemplateRef[]        // pairs of {placeholder, typeIdentifier}
}
```

### TemplateRef

```ts
{ placeholder: "$user",               // exact substring inside `code`
  typeIdentifier: "user" }            // resolves to the generated type's name; auto-imports
```

### ImportSpec

```ts
{ path: string,                       // external module path, e.g. "@angular/core", or
                                      // a customFiles `identifier` for in-batch helper files
  types?: string[] }                  // named imports
```

### GenericArg (on a class/interface template)

```ts
{ name: "T",
  constraintTypeIdentifier?: string,  // generic constraint — "where T : BaseEntity"
  propertyName?: string,              // creates a property of type T (or T[])
  isArrayProperty?: boolean }         // makes that property T[] instead of T
```

### Constructor Param

```ts
{ name, primitiveType? | typeIdentifier? | type? }
```

### Enum

```ts
{ name, typeIdentifier, fileName?, path?, comment?,
  members: [{ name, value: number }] }
```

### ArrayType (virtual, no file)

```ts
{ typeIdentifier: string,
  // Pick ONE element form:
  elementPrimitiveType?: "String"|"Number"|"Boolean"|"Date"|"Any",
  elementTypeIdentifier?: string }
```

### DictionaryType (virtual, no file)

```ts
{ typeIdentifier: string,
  keyPrimitiveType?: "String"|"Number"|"Boolean"|"Date"|"Any",
  keyType?: string,                   // raw string literal e.g. "string"
  keyTypeIdentifier?: string,
  valuePrimitiveType?: "String"|"Number"|"Boolean"|"Date"|"Any",
  valueTypeIdentifier?: string }
```

All four key/value combinations (prim/prim, prim/custom, custom/prim, custom/custom) are supported.

### ConcreteGenericClasses / ConcreteGenericInterfaces (virtual, no file)

```ts
{ identifier: string,                  // referenceable id for this concrete instantiation
  genericClassIdentifier: string,      // the generic template's typeIdentifier
  genericArguments: [{ primitiveType? | typeIdentifier? }] }
```

Use the `identifier` as a `baseClassTypeIdentifier` (or in templateRefs) to express e.g. `class UserRepository extends Repository<User>`.

### CustomFile (free-form file)

```ts
{ name: string,                        // file base name (no extension)
  path?: string,
  fileName?: string,
  identifier?: string,                 // referenceable id; other classes can `customImports: [{ path: identifier }]`
  customCode: CustomCodeBlock[],       // body lines; one entry per export/alias/function
  customImports?: ImportSpec[] }
```

---

## THE 7 CRITICAL RULES (most failures come from violating these)

1. **ONE call with the FULL spec.** `typeIdentifier` cross-references resolve only within the current batch. Splitting per-domain breaks cross-file imports.
2. **Properties = type declarations only. CustomCode = everything else.** A property is `{name, type}`. A method, an initialized field, a statement with logic — all go in `customCode`. **One `customCode` item == one member.** Never put methods in `properties`. Never put bare type declarations in `customCode`.
3. **Use `templateRefs` for in-batch type references inside `customCode`.** Write `$placeholder` in the code string, then bind `{placeholder, typeIdentifier}` in `templateRefs`. This is what triggers automatic import generation. Raw type names (`User`) inside `customCode` won't import.
4. **Never add framework/std-lib imports to `customImports`.** TypeScript needs no imports for built-ins. `customImports` is only for external packages (`@angular/core`, `rxjs`, `nestjs`, etc.).
5. **`templateRefs` are ONLY for in-batch types.** External types → `customImports`. In-batch types → `typeIdentifier` or `templateRefs`. Never mix.
6. **Constructor params auto-become properties** (in C#/Java/Go/Groovy — and in TS via `public` modifier). Do NOT also list them in `properties[]`. Causes "Sequence contains more than one matching element" errors. Put non-constructor fields in `properties[]`.
7. **Virtual types never generate files.** `arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`, `concreteGenericInterfaces` only create reusable type references; you must reference their `typeIdentifier` from a file-generating type (class/interface) for them to appear anywhere.

---

## Output structure & naming

- Files are written to `outputPath` (default `.`) in the directory under each entity's `path`.
- TypeScript file names are kebab-case of the class/interface name (`UserRepository` → `user-repository.ts`) unless `fileName` is set.
- Enums get suffixed: `OrderStatus` → `order-status.enum.ts` (TS) / `OrderStatus.cs` (C#).
- TypeScript: **strips the `I` prefix from interface names** (`IUserRepository` → exported as `UserRepository`). To prevent file collisions, set `fileName: "i-user-repository"` on the interface.
- Imports between generated files are inserted automatically based on `typeIdentifier` and `templateRefs` resolution.
- Each `customCode` block is separated by a blank line in output.

---

## TypeScript specifics

- Primitive mapping: `String → string`, `Number → number`, `Boolean → boolean`, `Date → Date`, `Any → unknown`.
- No imports needed for built-in types.
- Decorators supported directly on classes and properties.
- Auto-indents `\n` inside `customCode`.
- Constructor parameters render as `public param: T` style (TypeScript shorthand) and become properties automatically.
- For generic classes: `genericArguments` with `propertyName + isArrayProperty: true` produces `items!: T[]`.
- For interfaces with method signatures, put the **signatures** (no body, ending with `;`) in `customCode`. Do NOT use function-typed properties — implementing classes will then duplicate them as property declarations.

---

## Pattern library (TypeScript)

### Pattern A — Two interfaces, cross-referenced

```jsonc
{
  "language": "typescript",
  "interfaces": [
    {"name": "Address", "typeIdentifier": "address", "properties": [
      {"name": "street", "primitiveType": "String"},
      {"name": "city",   "primitiveType": "String"}
    ]},
    {"name": "User", "typeIdentifier": "user", "properties": [
      {"name": "id",      "primitiveType": "String"},
      {"name": "address", "typeIdentifier": "address"}
    ]}
  ]
}
```

### Pattern B — Class with inheritance + a method

```jsonc
{
  "language": "typescript",
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

### Pattern C — Generic + concrete via `concreteGenericClasses`

```jsonc
{
  "language": "typescript",
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

Output: `class UserRepository extends Repository<User>` with correct imports.

### Pattern D — Array & dictionary types

```jsonc
{
  "arrayTypes": [
    {"typeIdentifier": "user-list", "elementTypeIdentifier": "user"},
    {"typeIdentifier": "string-array", "elementPrimitiveType": "String"}
  ],
  "dictionaryTypes": [
    {"typeIdentifier": "scores", "keyPrimitiveType": "String", "valuePrimitiveType": "Number"},
    {"typeIdentifier": "user-lookup", "keyPrimitiveType": "String", "valueTypeIdentifier": "user"}
  ]
}
```

Reference via `"typeIdentifier": "user-list"` in any property. In TS, arrays render as `Array<User>` and dicts as `Record<K, V>`.

### Pattern E — Complex generic via raw `type` + templateRefs

```jsonc
"properties": [{
  "name": "cache",
  "type": "Map<string, $resp>",
  "templateRefs": [{"placeholder": "$resp", "typeIdentifier": "api-response"}]
}]
```

`templateRefs` work in `properties.type`, in `customCode.code`, and in decorator code.

### Pattern F — Enum + class that uses it

```jsonc
{
  "enums": [{"name": "OrderStatus", "typeIdentifier": "order-status",
    "members": [{"name": "Pending", "value": 0}, {"name": "Shipped", "value": 2}]}],
  "classes": [{"name": "Order", "typeIdentifier": "order",
    "properties": [{"name": "status", "typeIdentifier": "order-status"}],
    "customCode": [{
      "code": "updateStatus(s: $status): void { this.status = s; }",
      "templateRefs": [{"placeholder": "$status", "typeIdentifier": "order-status"}]
    }]}]
}
```

### Pattern G — Service with DI + external imports

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

### Pattern H — `customFiles` for type aliases / barrel exports

```jsonc
{
  "customFiles": [{
    "name": "types", "path": "shared", "identifier": "shared-types",
    "customCode": [
      {"code": "export type UserId = string;"},
      {"code": "export type Email  = string;"}
    ]
  }],
  "classes": [{
    "name": "UserHelper", "path": "helpers",
    "customImports": [{"path": "shared-types"}],
    "customCode": [{"code": "static format(email: Email): string { return email.trim(); }"}]
  }]
}
```

The `identifier` makes the customFile addressable in `customImports` (path resolution is automatic).

### Pattern I — Interface with method signatures (so a class can `implements` it cleanly)

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

Method signatures end with `;` and have no body. Do NOT model these as function-typed properties.

### Pattern J — Constructor params (correct vs duplicate)

```jsonc
// CORRECT — constructor params live in constructorParameters; only ADDITIONAL fields go in properties[]
{"name": "User", "typeIdentifier": "user",
 "constructorParameters": [
   {"name": "email", "type": "string"},
   {"name": "status", "typeIdentifier": "status"}
 ],
 "properties": [{"name": "createdAt", "primitiveType": "Date"}]}
```

Renders to:

```ts
import { Status } from './status.enum';

export class User {
  createdAt!: Date;
  constructor(public email: string, public status: Status) {}
}
```

---

## Common mistakes (do not commit)

1. Referencing a `typeIdentifier` that isn't in the same batch → silently dropped property.
2. Defining method signatures on an interface as function-typed properties → implementing class duplicates them.
3. Writing internal type names as raw strings inside `customCode` → no imports generated. Use `templateRefs` with `$placeholder`.
4. Adding framework imports (`System.*`, `typing.*`, `java.util.*`, etc.) to `customImports` — they're auto-imported.
5. Duplicating constructor parameters in the `properties` array.
6. Using JS reserved words (`delete`, `class`, `import`) as property names. Use `remove`, `clazz`, `importData`.
7. Splitting related types across multiple MCP calls. Cross-file imports only resolve within ONE call. **ALWAYS one call.**
8. Forgetting `fileName` when an `I`-prefixed interface and its concrete class would collide on disk in TypeScript.
9. Putting initialized fields (`private http = inject(HttpClient);`) into `properties` — they belong in `customCode`.
10. Expecting `arrayTypes` to give you a mutable `List<T>` — they generate idiomatic array forms (`Array<T>` in TS, `IEnumerable<T>` in C#). For mutable lists in C# use `"type": "List<$user>"` + templateRefs.

---

## Authoring checklist (before calling generate_code)

- [ ] All types in ONE call.
- [ ] Every `typeIdentifier` reference resolves to a defined type in the same call.
- [ ] Every internal type used inside `customCode.code` has a matching `templateRefs` entry with `$placeholder`.
- [ ] No std-lib types in `customImports`.
- [ ] No methods or initialized fields in `properties`.
- [ ] No constructor-param duplication in `properties`.
- [ ] One `customCode` block = exactly one member.
- [ ] `language: "typescript"`, optional `outputPath`, and (if needed) `dryRun: false`.

---

## Concrete TypeScript output references

Given Pattern G's input, output is roughly:

```ts
// pet.ts
export class Pet { name!: string; }

// services/pet-service.ts
import { Injectable, inject } from '@nestjs/common';
import { HttpClient } from '@nestjs/common/http';
import { Observable } from 'rxjs';
import { Pet } from '../pet';

@Injectable({ providedIn: 'root' })
export class PetService {
  private http = inject(HttpClient);
  private baseUrl = '/api/pets';

  getAll(): Observable<Array<Pet>> { return this.http.get<Array<Pet>>(this.baseUrl); }
  getById(id: string): Observable<Pet> { return this.http.get<Pet>(`${this.baseUrl}/${id}`); }
  create(pet: Pet): Observable<Pet>   { return this.http.post<Pet>(this.baseUrl, pet); }
}
```

Note `path: "services"` → file goes to `services/pet-service.ts`, and the import to `Pet` becomes `../pet` automatically.

---

## When to use `load_spec_from_file`

For very large specs, write the full JSON to a file (e.g. `/tmp/spec.json`) and call `load_spec_from_file({ specFilePath: "/tmp/spec.json", outputPath: "<outDir>" })`. Same engine, same rules, lower context cost. The spec file's JSON is structurally identical to the `generate_code` arguments object — including the `language` field.

---

## Final reminder

The structural advantage of MetaEngine is: **describe the typegraph once, get the whole tree of files generated coherently with correct imports.** Splitting into per-file edits or per-domain calls forfeits that and produces broken cross-references. ONE call with the full spec is the canonical pattern.
