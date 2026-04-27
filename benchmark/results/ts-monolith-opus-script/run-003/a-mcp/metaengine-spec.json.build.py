import json
import re
from pathlib import Path

SOURCE = Path("<benchmark>/spec/monolith.json")
OUT = Path("<benchmark>/results/20260426-210323-typescript-script-monolith/run-003/a-mcp/metaengine-spec.json")

PRIMITIVE_MAP = {"string": "String", "number": "Number", "boolean": "Boolean", "Date": "Date"}
PRIMITIVES = set(PRIMITIVE_MAP.keys())


def kebab(name: str) -> str:
    s = re.sub(r'([a-z0-9])([A-Z])', r'\1-\2', name)
    s = s.replace('_', '-').replace('.', '-')
    return s.lower()


def build_registry(spec):
    """Map every type name (across all modules) to its kebab-case typeIdentifier."""
    reg = {}
    for m in spec["modules"]:
        for t in m["types"]:
            reg[t["name"]] = kebab(t["name"])
    return reg


def field_to_member(f):
    """Translate a field entry to MetaEngine property/constructorParameter shape.
    SAME helper used for value_object properties AND aggregate constructorParameters."""
    type_str = f["type"]
    if type_str in PRIMITIVES:
        return {"name": f["name"], "primitiveType": PRIMITIVE_MAP[type_str]}
    return {"name": f["name"], "typeIdentifier": kebab(type_str)}


def transform_type_string(type_str: str, registry: dict):
    """Replace every internal type identifier in a TS type expression with $placeholder.
    Returns (new_str, refs) where refs is {placeholder: typeIdentifier}."""
    refs = {}

    def replacer(match):
        word = match.group(0)
        if word in registry:
            ph = "$" + word
            refs[ph] = registry[word]
            return ph
        return word

    new_str = re.sub(r'\b[A-Z][a-zA-Z0-9]*\b', replacer, type_str)
    return new_str, refs


def method_to_custom_code(method, registry):
    """Build a single customCode entry from a service method.
    Replaces every non-primitive type in params/return with $placeholders + templateRefs."""
    refs = {}
    parts = []
    for p in method["params"]:
        type_str = p["type"]
        if type_str in PRIMITIVES:
            parts.append(f"{p['name']}: {type_str}")
        else:
            transformed, r = transform_type_string(type_str, registry)
            refs.update(r)
            parts.append(f"{p['name']}: {transformed}")

    ret = method["returns"]
    ret_type_str = ret["type"] if isinstance(ret, dict) else ret

    if ret_type_str in PRIMITIVES or ret_type_str == "void":
        ret_str = ret_type_str
    else:
        ret_str, r = transform_type_string(ret_type_str, registry)
        refs.update(r)

    code = f"{method['name']}({', '.join(parts)}): {ret_str} {{ throw new Error('not implemented'); }}"
    return {
        "code": code,
        "templateRefs": [{"placeholder": ph, "typeIdentifier": ti} for ph, ti in refs.items()],
    }


def main():
    spec = json.loads(SOURCE.read_text())
    registry = build_registry(spec)

    classes = []
    interfaces = []
    enums = []

    for m in spec["modules"]:
        path = m["path"]
        for t in m["types"]:
            tid = kebab(t["name"])
            kind = t["kind"]
            if kind == "aggregate":
                classes.append({
                    "name": t["name"],
                    "typeIdentifier": tid,
                    "path": f"src/{path}/aggregates",
                    "constructorParameters": [field_to_member(f) for f in t["fields"]],
                })
            elif kind == "value_object":
                interfaces.append({
                    "name": t["name"],
                    "typeIdentifier": tid,
                    "path": f"src/{path}/value-objects",
                    "properties": [field_to_member(f) for f in t["fields"]],
                })
            elif kind == "enum":
                enums.append({
                    "name": t["name"],
                    "typeIdentifier": tid,
                    "path": f"src/{path}/enums",
                    "members": t["members"],
                })
            else:
                raise ValueError(f"Unknown kind: {kind}")

        for s in m["services"]:
            classes.append({
                "name": s["name"],
                "typeIdentifier": kebab(s["name"]),
                "path": f"src/{path}/services",
                "customCode": [method_to_custom_code(meth, registry) for meth in s["methods"]],
            })

    orch = spec["orchestrators"]
    for s in orch["services"]:
        classes.append({
            "name": s["name"],
            "typeIdentifier": kebab(s["name"]),
            "path": f"src/{orch['path']}/services",
            "customCode": [method_to_custom_code(meth, registry) for meth in s["methods"]],
        })

    out = {
        "language": "typescript",
        "classes": classes,
        "interfaces": interfaces,
        "enums": enums,
    }
    OUT.write_text(json.dumps(out, indent=2))
    print(f"wrote {OUT}: {len(classes)} classes, {len(interfaces)} interfaces, {len(enums)} enums")


if __name__ == "__main__":
    main()
