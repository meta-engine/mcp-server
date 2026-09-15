# MetaEngine MCP — generation guide

MetaEngine generates source files from structured type definitions and target-language code. Type and model generation supports TypeScript, Python, Go, C#, Java, Kotlin, Groovy, Scala, Swift, PHP, and Rust.

## Choose a tool

- `generate_from_recipe`: compact property maps, explicit references, reusable parameter templates, and local JSON data rows. Start with [RECIPES.md](./RECIPES.md), also available as `metaengine://guide/recipes`.
- `generate_code`: the existing complete native JSON payload.
- `load_spec_from_file`: the same native payload read from a local file.
- `generate_openapi`, `generate_graphql`, `generate_protobuf`, `generate_sql`: convert an existing schema using their tool-specific options.

The three type-graph tools share the hosted generation API and local file writer. `dryRun` previews source without writing it; `skipExisting` defaults to true. The hosted request limit is 250 counted types, with the existing counting rule documented in the recipe guide.

## References and batch boundaries

Generate related types together. IDs resolve within a single request. A class or interface declares `typeIdentifier`; a property refers to it with the same field. Recipes also accept the compact aliases `id` on definitions and `ref` on map properties.

Use `templateRefs` wherever target-language text refers to an internal type:

```json
{
  "code": "read(): Promise<$item>;",
  "templateRefs": [{ "placeholder": "$item", "typeIdentifier": "item" }]
}
```

The reference resolves the type name and supports import generation. Merely writing an internal type's name in a raw code string does not create a graph reference. `templateRefs` are supported on custom code, native property type expressions, constructor parameter type expressions, and decorators; properties also support `commentTemplateRefs`.

External types use `customImports` with the target language's import path and names. The generator handles recognized standard-library imports. It does not install external packages.

Custom-file identifiers belong to import resolution, not the regular type graph. Where supported, refer to one with `customImports.path`; for C#, use the custom file's namespace. Do not target a custom-file identifier with `ref` or `templateRefs.typeIdentifier`. Code inside a custom file can still use `templateRefs` to refer to ordinary generated types.

## Declarations and custom code

Use `properties` for typed declarations. Use `customCode` for methods, initialized fields, constructors with bodies, and other target-language members. Keep each member in its own code block. `customFiles` produce files without a class wrapper and can hold functions, aliases, or other source content.

Use interface method signatures in `customCode` when classes will implement those methods. A function-typed property and a method are different declarations.

Constructor parameters can create properties in the selected language. Do not repeat a constructor parameter as an additional property. For a constructor with custom logic, supply the constructor code and any fields explicitly in `customCode`.

The generator renders your supplied structure and code. Compile the result in its real project to check method bodies, dependencies, language rules, and compiler options.

## Native features retained by recipes

| Feature | Native fields |
| --- | --- |
| Named types | `classes`, `interfaces`, `enums`, `typeIdentifier`, `name`, `path`, `fileName` |
| Properties | `name`, `primitiveType`, `typeIdentifier`, `type`, `isOptional`, `isInitializer`, comments and decorators |
| Inheritance | `baseClassTypeIdentifier`, `interfaceTypeIdentifiers` |
| Generic definitions | `genericArguments` with name, constraint, and optional property metadata |
| Concrete generic references | `concreteGenericClasses`, `concreteGenericInterfaces`, `identifier`, `genericClassIdentifier`, `genericArguments` |
| Collection references | `arrayTypes`, `dictionaryTypes` |
| Target-language content | `customCode`, `customFiles`, `customImports`, `templateRefs` |
| Generation settings | `initialize`, `packageName`, `typeScriptOptions`, `skipEnumMembersValidation` |

Array, dictionary, and concrete generic definitions are virtual types: they can be referenced but do not generate files of their own. A concrete generic's `genericClassIdentifier` refers to its generic declaration, including for interfaces; keep that existing field name.

## Language notes

### TypeScript

For Node16/NodeNext ESM, use `typeScriptOptions: {"relativeImportExtension":"js"}` so generated `.ts` source imports runtime `.js` paths. The default uses extensionless relative imports.

Native primitives `String`, `Number`, `Boolean`, `Date`, and `Any` render as `string`, `number`, `boolean`, `Date`, and `unknown`. Recipes spell those primitive choices in lowercase. For native expressions such as `Map<string, $item>`, use `type` plus `templateRefs`.

The engine can normalize interface names. Use references to obtain the rendered name, and explicit `fileName` values when an interface and class would otherwise share a file name.

### C#

`packageName` sets the root namespace; type paths contribute namespace segments. Omit the package name when you want no root namespace. Do not put namespace wrappers in individual custom members.

`Number` selects `int`. Use native `type: "decimal"` or `type: "double"` for those numeric types. Optional properties use the language's nullable representation. Configure nullable reference types and the language version in the consuming project.

Use `templateRefs` for internal cross-namespace types in custom code. For a specific collection such as `List<T>`, use `type: "List<$item>"` with a reference. The language emitter chooses the collection spelling for a virtual `arrayTypes` definition.

### Other languages

Keep method bodies and native type expressions in the selected language. Python bodies need valid indentation. Go multi-file output needs a package/module layout appropriate to the consuming project. Add the generated code's required libraries to the target project.

## Before generation

1. Include every internally referenced type in the same batch.
2. Use structured properties for declarations and custom code for behavior.
3. Make every internal reference in a raw type expression or code block explicit with `templateRefs`.
4. Choose output paths, native imports, package/namespace names, and compiler options deliberately.
5. Review and compile the generated output.

[Complete examples](./EXAMPLES.md) · [Recipe syntax and limits](./RECIPES.md)
