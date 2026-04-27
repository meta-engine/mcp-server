#!/usr/bin/env python3
import json
import re

SPEC_PATH = "<benchmark>/spec/monolith.json"
OUT_PATH = "<benchmark>/results/20260426-210323-typescript-script-monolith/run-005/a-mcp/metaengine-spec.json"

PRIMITIVE_MAP = {
    "string": "String",
    "number": "Number",
    "boolean": "Boolean",
    "Date": "Date",
}
PRIMITIVES = set(PRIMITIVE_MAP.keys())


def kebab(name: str) -> str:
    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1-\2", name)
    s2 = re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", s1)
    return s2.lower()


def field_to_property(f):
    """Translate a field entry to a MetaEngine property/parameter shape.
    Used for value_object properties, aggregate constructorParameters."""
    t = f["type"]
    if t in PRIMITIVES:
        return {"name": f["name"], "primitiveType": PRIMITIVE_MAP[t]}
    return {"name": f["name"], "typeIdentifier": kebab(t)}


def build_type_token(type_str, refs):
    """Translate a type expression like 'Product', 'Product[]', 'Product | null',
    'Partial<Product>' into a TS string with $placeholders. Mutates `refs`
    (placeholder -> typeIdentifier). Primitive scalar types are returned as-is."""
    if type_str == "void":
        return "void"
    # Match identifiers, replace non-primitive ones with $placeholders.
    def replace(match):
        ident = match.group(0)
        if ident in PRIMITIVES or ident in ("void", "null", "undefined", "Partial", "Promise", "Array"):
            return ident
        ph = "$" + ident
        refs[ph] = kebab(ident)
        return ph
    return re.sub(r"[A-Za-z_][A-Za-z0-9_]*", replace, type_str)


def method_to_custom_code(method):
    refs = {}
    parts = []
    for p in method["params"]:
        token = build_type_token(p["type"], refs)
        parts.append(f"{p['name']}: {token}")
    ret = method["returns"]
    ret_type = ret["type"] if isinstance(ret, dict) else ret
    ret_token = build_type_token(ret_type, refs)
    code = f"{method['name']}({', '.join(parts)}): {ret_token} {{ throw new Error('not implemented'); }}"
    template_refs = [{"placeholder": k, "typeIdentifier": v} for k, v in refs.items()]
    entry = {"code": code}
    if template_refs:
        entry["templateRefs"] = template_refs
    return entry


def main():
    with open(SPEC_PATH, "r") as f:
        spec = json.load(f)

    classes = []
    interfaces = []
    enums = []

    for module in spec["modules"]:
        mpath = module["path"]
        base = f"src/{mpath}"
        for t in module.get("types", []):
            kind = t["kind"]
            name = t["name"]
            tid = kebab(name)
            if kind == "aggregate":
                ctor_params = [field_to_property(f) for f in t.get("fields", [])]
                classes.append({
                    "name": name,
                    "typeIdentifier": tid,
                    "path": f"{base}/aggregates",
                    "constructorParameters": ctor_params,
                })
            elif kind == "value_object":
                props = [field_to_property(f) for f in t.get("fields", [])]
                interfaces.append({
                    "name": name,
                    "typeIdentifier": tid,
                    "path": f"{base}/value-objects",
                    "properties": props,
                })
            elif kind == "enum":
                members = [{"name": m["name"], "value": m["value"]} for m in t.get("members", [])]
                enums.append({
                    "name": name,
                    "typeIdentifier": tid,
                    "path": f"{base}/enums",
                    "members": members,
                })
            else:
                raise ValueError(f"Unknown kind: {kind}")

        for svc in module.get("services", []):
            custom_code = [method_to_custom_code(m) for m in svc.get("methods", [])]
            classes.append({
                "name": svc["name"],
                "typeIdentifier": kebab(svc["name"]),
                "path": f"{base}/services",
                "customCode": custom_code,
            })

    orch = spec.get("orchestrators")
    if orch:
        opath = orch["path"]
        for svc in orch.get("services", []):
            custom_code = [method_to_custom_code(m) for m in svc.get("methods", [])]
            classes.append({
                "name": svc["name"],
                "typeIdentifier": kebab(svc["name"]),
                "path": f"src/{opath}/services",
                "customCode": custom_code,
            })

    output = {
        "language": "typescript",
        "classes": classes,
        "interfaces": interfaces,
        "enums": enums,
    }

    with open(OUT_PATH, "w") as f:
        json.dump(output, f, indent=2)
    print(f"wrote {OUT_PATH}")
    print(f"classes: {len(classes)}, interfaces: {len(interfaces)}, enums: {len(enums)}")


if __name__ == "__main__":
    main()
