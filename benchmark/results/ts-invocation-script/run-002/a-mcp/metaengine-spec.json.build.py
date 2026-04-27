import json
import re
from pathlib import Path

SPEC_PATH = "<benchmark>/spec/large.json"
OUT_PATH = "<benchmark>/results/20260426-105828-typescript-script/run-002/a-mcp/metaengine-spec.json"

PRIMITIVE_MAP = {
    "string": "String",
    "number": "Number",
    "boolean": "Boolean",
    "Date": "Date",
}


def to_kebab(name: str) -> str:
    s1 = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1-\2', name)
    s2 = re.sub(r'([a-z\d])([A-Z])', r'\1-\2', s1)
    return s2.lower()


def field_to_property(f):
    t = f["type"]
    if t in PRIMITIVE_MAP:
        return {"name": f["name"], "primitiveType": PRIMITIVE_MAP[t]}
    return {"name": f["name"], "type": t}


def field_to_ctor_param(f):
    return {"name": f["name"], "type": f["type"]}


def with_placeholder(t: str, agg_name: str) -> str:
    if not agg_name:
        return t
    return re.sub(rf'\b{re.escape(agg_name)}\b', f"${agg_name}", t)


def build():
    spec = json.loads(Path(SPEC_PATH).read_text())
    classes, interfaces, enums = [], [], []

    for domain in spec["domains"]:
        dname = domain["name"]
        aggregates = [t for t in domain["types"] if t["kind"] == "aggregate"]
        agg_name = aggregates[0]["name"] if aggregates else None
        agg_id = to_kebab(agg_name) if agg_name else None

        for t in domain["types"]:
            kind = t["kind"]
            tname = t["name"]
            tid = to_kebab(tname)
            if kind == "aggregate":
                classes.append({
                    "name": tname,
                    "typeIdentifier": tid,
                    "constructorParameters": [field_to_ctor_param(f) for f in t["fields"]],
                    "path": f"src/domain/{dname}/aggregates",
                    "comment": f"{tname} aggregate root for the {dname} domain.",
                })
            elif kind == "value_object":
                interfaces.append({
                    "name": tname,
                    "typeIdentifier": tid,
                    "properties": [field_to_property(f) for f in t["fields"]],
                    "path": f"src/domain/{dname}/value-objects",
                    "comment": f"{tname} value object.",
                })
            elif kind == "enum":
                enums.append({
                    "name": tname,
                    "typeIdentifier": tid,
                    "members": t["members"],
                    "path": f"src/domain/{dname}/enums",
                    "comment": f"{tname} enum.",
                })

        for service in domain.get("services", []):
            custom_code = []
            for m in service["methods"]:
                params_str = ", ".join(
                    f"{p['name']}: {with_placeholder(p['type'], agg_name)}" for p in m["params"]
                )
                ret = with_placeholder(m["returns"], agg_name)
                code_str = f"{m['name']}({params_str}): {ret} {{ throw new Error('not implemented'); }}"
                template_refs = []
                if agg_name and f"${agg_name}" in code_str:
                    template_refs.append({"placeholder": f"${agg_name}", "typeIdentifier": agg_id})
                custom_code.append({"code": code_str, "templateRefs": template_refs})
            classes.append({
                "name": service["name"],
                "typeIdentifier": to_kebab(service["name"]),
                "customCode": custom_code,
                "path": f"src/domain/{dname}/services",
                "comment": f"{service['name']} service.",
            })

    out = {
        "language": "typescript",
        "classes": classes,
        "interfaces": interfaces,
        "enums": enums,
    }
    Path(OUT_PATH).parent.mkdir(parents=True, exist_ok=True)
    Path(OUT_PATH).write_text(json.dumps(out, indent=2))
    print(f"wrote {OUT_PATH}: {len(classes)} classes, {len(interfaces)} interfaces, {len(enums)} enums")


build()
