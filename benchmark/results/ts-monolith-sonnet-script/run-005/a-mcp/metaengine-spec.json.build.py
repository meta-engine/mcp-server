#!/usr/bin/env python3
import json
import re
from pathlib import Path

SPEC_PATH = "<benchmark>/spec/monolith.json"
OUT_PATH = "<benchmark>/results/20260426-223154-typescript-script-sonnet-monolith/run-005/a-mcp/metaengine-spec.json"

PRIMITIVE_MAP = {
    "string": "String",
    "number": "Number",
    "boolean": "Boolean",
    "Date": "Date",
}
TS_PRIMITIVES = set(PRIMITIVE_MAP.keys()) | {"void", "null", "undefined", "unknown", "any"}


def kebab(name):
    s1 = re.sub(r'(.)([A-Z][a-z]+)', r'\1-\2', name)
    return re.sub(r'([a-z0-9])([A-Z])', r'\1-\2', s1).lower()


def collect_all_type_names(spec):
    """Collect every type name defined across all modules."""
    names = set()
    for module in spec.get("modules", []):
        for t in module.get("types", []):
            names.add(t["name"])
    return names


def field_to_prop(field):
    """Unified field -> MetaEngine property/constructorParameter shape.
    Handles primitives and all cross/same-module type references identically."""
    t = field["type"]
    if t in PRIMITIVE_MAP:
        return {"name": field["name"], "primitiveType": PRIMITIVE_MAP[t]}
    return {"name": field["name"], "typeIdentifier": kebab(t)}


def substitute_types(expr, all_type_names):
    """Replace every internal type name in expr with a $placeholder.
    Returns (transformed_expr, refs_dict {placeholder: typeIdentifier}).
    Uses word-boundary regex so Email never clobbers EmailTemplate, etc.
    Sorts by length descending as a belt-and-suspenders guard."""
    refs = {}
    result = expr
    for name in sorted(all_type_names, key=len, reverse=True):
        pattern = r'\b' + re.escape(name) + r'\b'
        if re.search(pattern, result):
            ph = f"${name}"
            result = re.sub(pattern, ph, result)
            refs[ph] = kebab(name)
    return result, refs


def method_to_custom_code(method, all_type_names):
    """Build a customCode entry for a service method.
    All non-primitive types in params and returns get $placeholder + templateRefs."""
    all_refs = {}
    param_strs = []

    for p in method.get("params", []):
        t = p["type"]
        if t in PRIMITIVE_MAP:
            # Emit the TypeScript primitive literal directly in the code string
            param_strs.append(f"{p['name']}: {t}")
        else:
            expr, refs = substitute_types(t, all_type_names)
            all_refs.update(refs)
            param_strs.append(f"{p['name']}: {expr}")

    ret = method.get("returns", "void")
    ret_type = ret["type"] if isinstance(ret, dict) else ret

    if ret_type == "void" or ret_type in TS_PRIMITIVES:
        ret_str = ret_type
    elif ret_type in PRIMITIVE_MAP:
        ret_str = ret_type
    else:
        ret_str, refs = substitute_types(ret_type, all_type_names)
        all_refs.update(refs)

    params_str = ", ".join(param_strs)
    code = f"{method['name']}({params_str}): {ret_str} {{ throw new Error('not implemented'); }}"

    entry = {"code": code}
    if all_refs:
        entry["templateRefs"] = [
            {"placeholder": k, "typeIdentifier": v} for k, v in all_refs.items()
        ]
    return entry


def process_module(module, all_type_names, classes, interfaces, enums):
    path = module["path"]

    for t in module.get("types", []):
        name = t["name"]
        kind = t["kind"]
        tid = kebab(name)

        if kind == "aggregate":
            ctor_params = [field_to_prop(f) for f in t.get("fields", [])]
            classes.append({
                "name": name,
                "typeIdentifier": tid,
                "path": f"src/{path}/aggregates",
                "constructorParameters": ctor_params,
            })

        elif kind == "value_object":
            props = [field_to_prop(f) for f in t.get("fields", [])]
            interfaces.append({
                "name": name,
                "typeIdentifier": tid,
                "path": f"src/{path}/value-objects",
                "properties": props,
            })

        elif kind == "enum":
            enums.append({
                "name": name,
                "typeIdentifier": tid,
                "path": f"src/{path}/enums",
                "members": t.get("members", []),
            })

    for svc in module.get("services", []):
        svc_name = svc["name"]
        svc_tid = kebab(svc_name)
        custom_code = [
            method_to_custom_code(m, all_type_names)
            for m in svc.get("methods", [])
        ]
        classes.append({
            "name": svc_name,
            "typeIdentifier": svc_tid,
            "path": f"src/{path}/services",
            "customCode": custom_code,
        })


def main():
    with open(SPEC_PATH) as f:
        spec = json.load(f)

    all_type_names = collect_all_type_names(spec)

    classes = []
    interfaces = []
    enums = []

    for module in spec.get("modules", []):
        process_module(module, all_type_names, classes, interfaces, enums)

    orch = spec.get("orchestrators", {})
    if orch:
        orch_path = orch.get("path", "orchestrators")
        for svc in orch.get("services", []):
            svc_name = svc["name"]
            svc_tid = kebab(svc_name)
            custom_code = [
                method_to_custom_code(m, all_type_names)
                for m in svc.get("methods", [])
            ]
            classes.append({
                "name": svc_name,
                "typeIdentifier": svc_tid,
                "path": f"src/{orch_path}/services",
                "customCode": custom_code,
            })

    result = {
        "language": "typescript",
        "classes": classes,
        "interfaces": interfaces,
        "enums": enums,
    }

    Path(OUT_PATH).parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, "w") as f:
        json.dump(result, f, indent=2)

    print(f"OK: {len(classes)} classes, {len(interfaces)} interfaces, {len(enums)} enums -> {OUT_PATH}")


if __name__ == "__main__":
    main()
