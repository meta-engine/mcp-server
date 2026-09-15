# JSON recipe guide

`generate_from_recipe` is available in `@metaengine/mcp-server` 1.5.0. It expands a versioned JSON document locally into the existing `generate_code` payload, then uses the same hosted API and file writer. A recipe is data; it cannot execute a script.

## Tool arguments

Supply exactly one of `recipe` or `recipeFilePath`:

```json
{
  "recipeFilePath": "specs/models.recipe.json",
  "outputPath": "src/models",
  "skipExisting": true,
  "dryRun": false
}
```

`outputPath`, `skipExisting`, and `dryRun` override the recipe's values. Their defaults are `.`, `true`, and `false`. Output paths are relative to the MCP server's working directory. `dryRun` returns generated code and performs no generated-file writes; it still calls the hosted API.

Recipe files are plain JSON. Comments, trailing commas, and executable expressions are not supported.

## Compact declarations

```json
{
  "recipeVersion": 1,
  "language": "typescript",
  "classes": [
    {
      "name": "User",
      "id": "user",
      "path": "models",
      "properties": {
        "id": "string",
        "name": "string",
        "nickname?": "string",
        "createdAt": "date"
      }
    },
    {
      "name": "Order",
      "properties": {
        "user": { "ref": "user" },
        "total": "number",
        "labels": { "type": "string[]" }
      }
    }
  ]
}
```

| Authoring form | Expansion |
| --- | --- |
| `"name": "string"` | A property named `name` with native `primitiveType: "String"`. |
| `"name?": "string"` | The same property with `isOptional: true`. |
| `"user": {"ref":"user"}` | A native `typeIdentifier` reference. |
| `"total": {"type":"decimal"}` | A literal target-language type; use this form for C# `decimal`. |
| `"name": {"primitiveType":"String","comment":"Display name"}` | A property with additional native metadata. |
| `"id":"user"` on a definition | Alias for `typeIdentifier`, or `identifier` on custom files and concrete generics. |

Compact primitive spellings are `string`, `number`, `boolean`, `date`, and `any`. These select the existing engine primitives; their target spelling varies by language. For example, `number` selects `int` in C#. Use an explicit `type` when you need a particular native spelling.

Class, interface, and enum IDs default to `name`. Explicit IDs are useful for stable references when names change. Do not supply both `id` and its native identifier field. A compact property must select exactly one primitive, reference, or native type. Use either the `?` key suffix or `isOptional`, not both. Ordinary map fields expand with `isOptional: false`.

Interfaces accept the same field-map form. Enum members also accept a map: `{"Pending":0,"Done":1}`, or string values such as `{"Ready":"ready"}`. Use one value kind consistently within an enum. Original property and enum-member arrays remain supported unchanged.

## Repeated structures

Templates declare parameter names and a body containing any of the eight native graph collections. Instances supply a list of parameter objects:

```json
{
  "recipeVersion": 1,
  "language": "typescript",
  "templates": {
    "model": {
      "parameters": ["name", "fields"],
      "body": {
        "interfaces": [
          { "name": { "$param": "name" }, "path": "contracts", "properties": { "$param": "fields" } }
        ]
      }
    }
  },
  "instances": [
    {
      "template": "model",
      "values": [
        { "name": "Customer", "fields": { "id": "string", "name": "string" } },
        { "name": "Order", "fields": { "id": "string", "customer": { "ref": "Customer" } } }
      ]
    }
  ]
}
```

Only two directives are evaluated, and only inside template bodies:

- `{"$param":"name"}` inserts that parameter's JSON value, preserving objects, arrays, numbers, and booleans.
- `{"$format":"{{name}}Repository"}` concatenates literal text with named scalar parameters. Parameters must be strings, numbers, or booleans.

Ordinary strings are always literal, including JavaScript `${value}` and `{{value}}` inside `customCode`. To parameterize a code string, wrap it explicitly in `$format`. Parameter values are inserted as data and are not interpreted as new directives. Object keys are literal. `$param` and `$format` are reserved directive keys inside template bodies; use native property or enum-member arrays when a literal member has either exact name. Other dollar-prefixed names, such as `$id`, remain ordinary map keys. Use `$param` to supply an entire field map when its keys vary.

Every declared parameter is required for every row. Extra parameters, unknown templates, unknown directives, and malformed placeholders are errors. Templates do not call other templates. There is no implicit casing, naming convention, conditional, or language translation of raw code. Supply those choices explicitly in the parameter rows.

Direct declarations appear first in each collection, followed by template instances in their listed order. IDs and references are validated after the complete graph is assembled, so forward references work.

## Existing local JSON data

A recipe file can declare data sources and select rows with an RFC 6901 JSON Pointer:

```json
{
  "recipeVersion": 1,
  "language": "typescript",
  "inputs": { "models": { "path": "models.json", "pointer": "/models" } },
  "templates": {
    "model": {
      "parameters": ["name", "fields"],
      "body": { "interfaces": [{ "name": { "$param": "name" }, "properties": { "$param": "fields" } }] }
    }
  },
  "instances": [{ "template": "model", "input": "models" }]
}
```

The selected value must be an array of parameter objects, for example:

```json
{ "models": [{ "name": "User", "fields": { "id": "string" } }] }
```

An instance supplies exactly one of `values` or `input`. A missing or empty pointer selects the whole document. Relative input paths resolve against the recipe file's directory. For an inline recipe, input paths must be absolute. A declared input is read when an instance uses it, and is read once per call. Referenced files must be local JSON; URLs are not fetched by recipe expansion.

Only values incorporated into the expanded payload are sent to the generation API. Local recipe paths, unused input rows, and template declarations are not sent as part of that payload.

## Arbitrary code and the native type graph

Recipes retain the native generation settings `language`, `typeScriptOptions`, `initialize`, `packageName`, and `skipEnumMembersValidation`. They accept all eight native collections:

- `classes`, `interfaces`, and `enums`
- `arrayTypes` and `dictionaryTypes`
- `concreteGenericClasses` and `concreteGenericInterfaces`
- `customFiles`

Existing fields inside those definitions retain their names and behavior: `customCode`, `customImports`, `templateRefs`, `decorators`, `constructorParameters`, `genericArguments`, `baseClassTypeIdentifier`, `interfaceTypeIdentifiers`, `path`, `fileName`, and comments. Full property arrays are available when you prefer the native form.

Keep internal references explicit. For example, this TypeScript member refers to a class with ID `user` in the same recipe:

```json
{
  "code": "find(id: string): Promise<$user> { return this.store.get(id); }",
  "templateRefs": [{ "placeholder": "$user", "typeIdentifier": "user" }]
}
```

The type graph resolves `$user` and its import. The method body and the `store` dependency remain code you supply. External library imports use `customImports`. Custom-file identifiers belong to a separate import mechanism: where the language supports it, reference them through `customImports.path`; in C#, import the custom file's namespace. A custom-file identifier cannot be the target of `ref` or `templateRefs.typeIdentifier`. Code inside a custom file can still reference regular types through `templateRefs`. Virtual collection and concrete generic definitions create referenceable types without files.

[Complete TypeScript and C# examples](./EXAMPLES.md) · [Native generation rules](./METAENGINE_AI_GUIDE.md)

## Validation

Expansion validates the recipe version and field names, primitive spellings, parameter bindings, duplicate identifiers and member names, and declared type references. These checks finish before an API request or generated-file write. Errors include a path to the invalid field. The shared writer also preflights returned file paths, identical resolved targets, and file/parent conflicts, including existing symlinked parents, before creating output. Use filenames that differ by more than letter case; the underlying filesystem determines whether differently cased names refer to one file. Later filesystem failures are not a transaction: files already written are not rolled back.

This preflight checks authoring structure and graph references. It does not compile arbitrary code, install dependencies, or prove language-level correctness. Generated code should be compiled and tested with the target project's settings. Existing `generate_code` and `load_spec_from_file` payloads retain their own behavior.

## Limits

The hosted limit is **250 counted types per request**, calculated using the existing API rule:

```text
classes + interfaces + enums
  - concreteGenericClasses - concreteGenericInterfaces
```

`arrayTypes`, `dictionaryTypes`, and `customFiles` do not contribute to that count. Recipe validation checks this same count after expansion.

Independent local expansion bounds are:

| Boundary | Maximum |
| --- | --- |
| Recipe plus files read during the call | 5 MiB of UTF-8 JSON in total |
| Expanded payload | 5 MiB of UTF-8 JSON |
| JSON nesting | 64 levels |
| JSON nodes visited across inputs and template expansion | 100,000 |
| Template parameter rows expanded | 1,000 |

These bounds apply even when a definition does not count toward the hosted type limit. Split large work into complete reference graphs with explicit external imports between batches.

## Size evidence

A recorded development fixture contains 59 interfaces. Its compact recipe expands to an identical native payload and retains the output settings. The comparison measured 23,685 bytes for the original minified JSON and 13,885 bytes for the recipe, a 41.4% reduction in that fixture. This fixture and its compiler parity check are maintained in the private implementation repository.

These are UTF-8 JSON byte measurements, not token counts or a general savings guarantee. The original generator script is a different baseline. Templates can remove additional repetition when the shape repeats; unique method bodies still need to be represented.
