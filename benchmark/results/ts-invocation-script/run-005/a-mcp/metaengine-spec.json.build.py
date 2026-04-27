import json
import re
from pathlib import Path

SOURCE = "<benchmark>/spec/large.json"
OUTPUT = "<benchmark>/results/20260426-105828-typescript-script/run-005/a-mcp/metaengine-spec.json"

PRIM_MAP = {
    "string": "String",
    "number": "Number",
    "boolean": "Boolean",
    "Date": "Date",
}

def kebab(name: str) -> str:
    s = re.sub(r'(.)([A-Z][a-z]+)', r'\1-\2', name)
    s = re.sub(r'([a-z0-9])([A-Z])', r'\1-\2', s)
    return s.lower()

def translate_field(field):
    return {"name": field["name"], "primitiveType": PRIM_MAP[field["type"]]}

def make_method_code(method, aggregate_name):
    mname = method["name"]
    params = method.get("params", [])
    returns = method["returns"]
    placeholder = f"${aggregate_name}"

    param_strs = []
    refs_aggregate = False
    for p in params:
        ptype = p["type"]
        if aggregate_name in ptype:
            ptype = ptype.replace(aggregate_name, placeholder)
            refs_aggregate = True
        param_strs.append(f"{p['name']}: {ptype}")
    params_str = ", ".join(param_strs)

    ret = returns
    if aggregate_name in ret:
        ret = ret.replace(aggregate_name, placeholder)
        refs_aggregate = True

    code = f"{mname}({params_str}): {ret} {{ throw new Error('not implemented'); }}"

    entry = {"code": code}
    if refs_aggregate:
        entry["templateRefs"] = [
            {"placeholder": placeholder, "typeIdentifier": kebab(aggregate_name)}
        ]
    return entry

def main():
    with open(SOURCE) as f:
        spec = json.load(f)

    classes = []
    interfaces = []
    enums = []

    for domain in spec["domains"]:
        domain_name = domain["name"]
        aggregate_name = None
        for t in domain["types"]:
            if t["kind"] == "aggregate":
                aggregate_name = t["name"]
                break

        for t in domain["types"]:
            kind = t["kind"]
            name = t["name"]
            tid = kebab(name)

            if kind == "aggregate":
                classes.append({
                    "name": name,
                    "typeIdentifier": tid,
                    "constructorParameters": [translate_field(f) for f in t["fields"]],
                    "path": f"src/domain/{domain_name}/aggregates",
                    "comment": f"{name} aggregate root for the {domain_name} domain."
                })
            elif kind == "value_object":
                interfaces.append({
                    "name": name,
                    "typeIdentifier": tid,
                    "properties": [translate_field(f) for f in t["fields"]],
                    "path": f"src/domain/{domain_name}/value-objects",
                    "comment": f"{name} value object."
                })
            elif kind == "enum":
                enums.append({
                    "name": name,
                    "typeIdentifier": tid,
                    "members": [{"name": m["name"], "value": m["value"]} for m in t["members"]],
                    "path": f"src/domain/{domain_name}/enums",
                    "comment": f"{name} enum."
                })

        for service in domain.get("services", []):
            sname = service["name"]
            sid = kebab(sname)
            custom_code = [make_method_code(m, aggregate_name) for m in service["methods"]]
            classes.append({
                "name": sname,
                "typeIdentifier": sid,
                "customCode": custom_code,
                "path": f"src/domain/{domain_name}/services",
                "comment": f"{sname} service."
            })

    output = {
        "language": "typescript",
        "initialize": True,
        "classes": classes,
        "interfaces": interfaces,
        "enums": enums,
    }

    Path(OUTPUT).parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT, "w") as f:
        json.dump(output, f, indent=2)

    print(f"Wrote {len(classes)} classes, {len(interfaces)} interfaces, {len(enums)} enums")

if __name__ == "__main__":
    main()
