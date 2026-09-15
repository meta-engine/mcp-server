# Generation examples

These complete recipes demonstrate structured declarations, reusable templates, and target-language methods connected to the same graph with `templateRefs`. Call `generate_from_recipe` with `{"recipe": <document>, "outputPath": "src/generated"}`, or save a document and use `recipeFilePath`.

Save either JSON document below and invoke it through your MCP client using `recipeFilePath`. Compile the returned source in your target project to check its language settings and dependencies.

## TypeScript: linked models and behavior

The model template generates `Item`. `Batch` and `IItemReader` refer to that type, including from raw method bodies/signatures. The array definition is virtual. The ESM option selects relative `.js` imports in the generated TypeScript source.

```json
{
  "recipeVersion": 1,
  "language": "typescript",
  "typeScriptOptions": {
    "relativeImportExtension": "js"
  },
  "templates": {
    "model": {
      "parameters": [
        "name",
        "id",
        "fields"
      ],
      "body": {
        "classes": [
          {
            "name": {
              "$param": "name"
            },
            "id": {
              "$param": "id"
            },
            "path": "Models",
            "properties": {
              "$param": "fields"
            }
          }
        ]
      }
    }
  },
  "instances": [
    {
      "template": "model",
      "values": [
        {
          "name": "Item",
          "id": "item",
          "fields": {
            "Id": "string",
            "Price": {
              "type": "number"
            }
          }
        }
      ]
    }
  ],
  "interfaces": [
    {
      "name": "IItemReader",
      "id": "reader",
      "fileName": "item-reader",
      "path": "Contracts",
      "customCode": [
        {
          "code": "read(): Promise<$item>;",
          "templateRefs": [
            {
              "placeholder": "$item",
              "typeIdentifier": "item"
            }
          ]
        }
      ]
    }
  ],
  "classes": [
    {
      "name": "Batch",
      "id": "batch",
      "path": "Services",
      "properties": {
        "Primary": {
          "ref": "item"
        },
        "All": {
          "ref": "item-list"
        }
      },
      "customCode": [
        {
          "code": "total(item: $item): number { return item.Price; }",
          "templateRefs": [
            {
              "placeholder": "$item",
              "typeIdentifier": "item"
            }
          ]
        }
      ]
    }
  ],
  "arrayTypes": [
    {
      "id": "item-list",
      "elementTypeIdentifier": "item"
    }
  ]
}
```

## C#: the same structure with native code

The same recipe constructs apply. C# method bodies and native numeric types are explicit: `decimal` is supplied as a native `type`. `packageName` provides the root namespace; `Models`, `Services`, and `Contracts` contribute the type paths.

```json
{
  "recipeVersion": 1,
  "language": "csharp",
  "packageName": "Recipe.Example",
  "templates": {
    "model": {
      "parameters": [
        "name",
        "id",
        "fields"
      ],
      "body": {
        "classes": [
          {
            "name": {
              "$param": "name"
            },
            "id": {
              "$param": "id"
            },
            "path": "Models",
            "properties": {
              "$param": "fields"
            }
          }
        ]
      }
    }
  },
  "instances": [
    {
      "template": "model",
      "values": [
        {
          "name": "Item",
          "id": "item",
          "fields": {
            "Id": "string",
            "Price": {
              "type": "decimal"
            }
          }
        }
      ]
    }
  ],
  "interfaces": [
    {
      "name": "IItemReader",
      "id": "reader",
      "fileName": "item-reader",
      "path": "Contracts",
      "customCode": [
        {
          "code": "Task<$item> Read();",
          "templateRefs": [
            {
              "placeholder": "$item",
              "typeIdentifier": "item"
            }
          ]
        }
      ]
    }
  ],
  "classes": [
    {
      "name": "Batch",
      "id": "batch",
      "path": "Services",
      "properties": {
        "Primary": {
          "ref": "item"
        },
        "All": {
          "ref": "item-list"
        }
      },
      "customCode": [
        {
          "code": "public decimal Total($item item) { return item.Price; }",
          "templateRefs": [
            {
              "placeholder": "$item",
              "typeIdentifier": "item"
            }
          ]
        }
      ]
    }
  ],
  "arrayTypes": [
    {
      "id": "item-list",
      "elementTypeIdentifier": "item"
    }
  ]
}
```

## Native payloads

`generate_code` continues to accept native property arrays, and `load_spec_from_file` accepts those same payloads from disk. For example:

```json
{
  "language": "typescript",
  "interfaces": [
    { "name": "User", "typeIdentifier": "user", "properties": [{ "name": "id", "primitiveType": "String" }] },
    { "name": "Order", "typeIdentifier": "order", "properties": [{ "name": "user", "typeIdentifier": "user" }] }
  ],
  "outputPath": "src/models"
}
```

For a native type expression referencing a generated type, preserve the explicit link:

```json
{
  "name": "users",
  "type": "Map<string, $user>",
  "templateRefs": [{ "placeholder": "$user", "typeIdentifier": "user" }]
}
```

This fragment belongs in a TypeScript property's native array; include the `user` type in the same request. Recipes also accept the fragment's type/templateRefs fields in a compact property value.

[Full recipe grammar](./RECIPES.md) · [Generation guide](./METAENGINE_AI_GUIDE.md)
