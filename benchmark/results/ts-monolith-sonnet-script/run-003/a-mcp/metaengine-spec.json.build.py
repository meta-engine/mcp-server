#!/usr/bin/env python3
import json
import re
import os

SPEC_PATH = "<benchmark>/spec/monolith.json"
OUT_PATH = "<benchmark>/results/20260426-223154-typescript-script-sonnet-monolith/run-003/a-mcp/metaengine-spec.json"

PRIMITIVES = {"string", "number", "boolean", "Date", "void"}
PRIM_MAP = {"string": "String", "number": "Number", "boolean": "Boolean", "Date": "Date"}
# TypeScript built-in utility/generic types — not internal, never emit templateRef
TS_BUILTINS = {"Partial", "Required", "Readonly", "Pick", "Omit", "Record",
               "Promise", "Array", "Map", "Set", "Extract", "Exclude", "NonNullable"}


def kebab(name):
    """Convert PascalCase to kebab-case."""
    return re.sub(r'([A-Z])', r'-\1', name).lstrip('-').lower()


def build_type_registry(spec):
    """Map every type name in the spec → its kebab typeIdentifier."""
    registry = {}
    for module in spec["modules"]:
        for t in module.get("types", []):
            registry[t["name"]] = kebab(t["name"])
    return registry


def replace_types_in_expr(expr, type_registry):
    """
    Replace every internal type name in a TS type expression with a $placeholder.
    Returns (new_expr, refs) where refs = {placeholder: typeIdentifier}.
    Uses word-boundary regex so 'Product' won't clobber 'ProductState'.
    Sorts by length descending so longer names are replaced first.
    """
    words = re.findall(r'[A-Z][a-zA-Z]*', expr)
    to_replace = sorted(
        [w for w in words if w in type_registry and w not in TS_BUILTINS],
        key=len, reverse=True
    )
    refs = {}
    new_expr = expr
    for word in to_replace:
        ph = f"${word}"
        refs[ph] = type_registry[word]
        new_expr = re.sub(r'\b' + re.escape(word) + r'\b', ph, new_expr)
    return new_expr, refs


def field_to_property(f, type_registry):
    """Unified helper for value_object properties AND aggregate constructorParameters."""
    t = f["type"]
    if t in PRIMITIVES:
        return {"name": f["name"], "primitiveType": PRIM_MAP[t]}
    return {"name": f["name"], "typeIdentifier": kebab(t)}


def method_to_custom_code(method, type_registry):
    """Build one customCode entry per method with full templateRefs."""
    all_refs = {}
    param_parts = []

    for p in method["params"]:
        t = p["type"]
        if t in PRIMITIVES:
            param_parts.append(f"{p['name']}: {t}")
        else:
            new_t, refs = replace_types_in_expr(t, type_registry)
            all_refs.update(refs)
            param_parts.append(f"{p['name']}: {new_t}")

    ret = method["returns"]
    ret_type = ret["type"] if isinstance(ret, dict) else ret

    if ret_type == "void" or ret_type in PRIMITIVES:
        ret_str = ret_type
    else:
        ret_str, refs = replace_types_in_expr(ret_type, type_registry)
        all_refs.update(refs)

    params_str = ", ".join(param_parts)
    code = f"{method['name']}({params_str}): {ret_str} {{ throw new Error('not implemented'); }}"

    result = {"code": code}
    if all_refs:
        result["templateRefs"] = [{"placeholder": k, "typeIdentifier": v} for k, v in all_refs.items()]
    return result


def process_type(t, module_path, type_registry):
    """Return (bucket, entry) for a spec type entry."""
    kind = t["kind"]
    name = t["name"]
    type_id = kebab(name)

    if kind == "enum":
        return "enums", {
            "name": name,
            "typeIdentifier": type_id,
            "path": f"src/{module_path}/enums",
            "members": [{"name": m["name"], "value": m["value"]} for m in t["members"]],
        }

    if kind == "value_object":
        props = [field_to_property(f, type_registry) for f in t.get("fields", [])]
        return "interfaces", {
            "name": name,
            "typeIdentifier": type_id,
            "path": f"src/{module_path}/value-objects",
            "properties": props,
        }

    if kind == "aggregate":
        ctor = [field_to_property(f, type_registry) for f in t.get("fields", [])]
        return "classes", {
            "name": name,
            "typeIdentifier": type_id,
            "path": f"src/{module_path}/aggregates",
            "constructorParameters": ctor,
        }

    raise ValueError(f"Unknown kind: {kind}")


def process_service(svc, module_path, type_registry):
    """Service → class with customCode."""
    name = svc["name"]
    return {
        "name": name,
        "typeIdentifier": kebab(name),
        "path": f"src/{module_path}/services",
        "customCode": [method_to_custom_code(m, type_registry) for m in svc.get("methods", [])],
    }


def main():
    with open(SPEC_PATH) as f:
        spec = json.load(f)

    type_registry = build_type_registry(spec)

    classes, interfaces, enums = [], [], []

    for module in spec["modules"]:
        mp = module["path"]
        for t in module.get("types", []):
            bucket, entry = process_type(t, mp, type_registry)
            {"classes": classes, "interfaces": interfaces, "enums": enums}[bucket].append(entry)
        for svc in module.get("services", []):
            classes.append(process_service(svc, mp, type_registry))

    orch = spec.get("orchestrators", {})
    for svc in orch.get("services", []):
        classes.append(process_service(svc, orch.get("path", "orchestrators"), type_registry))

    result = {
        "language": "typescript",
        "classes": classes,
        "interfaces": interfaces,
        "enums": enums,
    }

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w") as f:
        json.dump(result, f, indent=2)

    print(f"Written: {OUT_PATH}")
    print(f"Classes: {len(classes)}, Interfaces: {len(interfaces)}, Enums: {len(enums)}")


if __name__ == "__main__":
    main()
