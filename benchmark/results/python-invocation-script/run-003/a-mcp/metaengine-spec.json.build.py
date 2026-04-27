import json
import re
from pathlib import Path

SRC = Path("<benchmark>/spec/large.json")
DST = Path("<benchmark>/results/20260426-115000-python-script/run-003/a-mcp/metaengine-spec.json")


def kebab(name: str) -> str:
    s = re.sub(r'(.)([A-Z][a-z]+)', r'\1-\2', name)
    s = re.sub(r'([a-z0-9])([A-Z])', r'\1-\2', s)
    return s.lower()


PRIM_MAP = {
    "string": "String",
    "number": "Number",
    "boolean": "Boolean",
    "Date": "Date",
    "any": "Any",
}


def field_to_param(field, type_index):
    name = field["name"]
    t = field["type"]
    if t in PRIM_MAP:
        return {"name": name, "primitiveType": PRIM_MAP[t]}
    if t in type_index:
        return {"name": name, "typeIdentifier": type_index[t]}
    return {"name": name, "primitiveType": "Any"}


def py_param_type(t: str, type_index):
    # Returns (literal_for_signature, list_of_templaterefs_to_add, optional_imports)
    refs = []
    raw = t.strip()
    # Partial<X>
    m = re.match(r"^Partial<(\w+)>$", raw)
    if m:
        target = m.group(1)
        if target in type_index:
            ph = f"${target}"
            refs.append({"placeholder": ph, "typeIdentifier": type_index[target]})
            return (ph, refs)
        return (target, refs)
    # X[]
    m = re.match(r"^(\w+)\[\]$", raw)
    if m:
        target = m.group(1)
        if target in type_index:
            ph = f"${target}"
            refs.append({"placeholder": ph, "typeIdentifier": type_index[target]})
            return (f"list[{ph}]", refs)
        if target == "string":
            return ("list[str]", refs)
        if target == "number":
            return ("list[float]", refs)
        return (f"list[{target}]", refs)
    # X | null
    m = re.match(r"^(\w+)\s*\|\s*null$", raw)
    if m:
        target = m.group(1)
        if target in type_index:
            ph = f"${target}"
            refs.append({"placeholder": ph, "typeIdentifier": type_index[target]})
            return (f"{ph} | None", refs)
        if target == "string":
            return ("str | None", refs)
        if target == "number":
            return ("float | None", refs)
        return (f"{target} | None", refs)
    if raw == "string":
        return ("str", refs)
    if raw == "number":
        return ("float", refs)
    if raw == "boolean":
        return ("bool", refs)
    if raw == "void":
        return ("None", refs)
    if raw == "Date":
        return ("datetime", refs)
    if raw in type_index:
        ph = f"${raw}"
        refs.append({"placeholder": ph, "typeIdentifier": type_index[raw]})
        return (ph, refs)
    return (raw, refs)


def build():
    src = json.loads(SRC.read_text())
    # Index: type name -> typeIdentifier
    type_index = {}
    for domain in src["domains"]:
        for t in domain.get("types", []):
            type_index[t["name"]] = kebab(t["name"])

    classes = []
    enums = []

    for domain in src["domains"]:
        dname = domain["name"]
        for t in domain.get("types", []):
            kind = t["kind"]
            tname = t["name"]
            tid = type_index[tname]
            if kind == "enum":
                enums.append({
                    "name": tname,
                    "typeIdentifier": tid,
                    "path": f"{dname}/enums",
                    "members": t["members"],
                    "comment": f"{tname} enum.",
                })
            elif kind == "aggregate":
                classes.append({
                    "name": tname,
                    "typeIdentifier": tid,
                    "path": f"{dname}/aggregates",
                    "constructorParameters": [field_to_param(f, type_index) for f in t["fields"]],
                    "comment": f"{tname} aggregate root for the {dname} domain.",
                })
            elif kind == "value_object":
                classes.append({
                    "name": tname,
                    "typeIdentifier": tid,
                    "path": f"{dname}/value_objects",
                    "constructorParameters": [field_to_param(f, type_index) for f in t["fields"]],
                    "comment": f"{tname} value object.",
                })

        for svc in domain.get("services", []):
            sname = svc["name"]
            sid = kebab(sname)
            custom_code = []
            for m in svc["methods"]:
                params = []
                refs = []
                for p in m["params"]:
                    lit, r = py_param_type(p["type"], type_index)
                    refs.extend(r)
                    params.append(f"{p['name']}: {lit}")
                ret_lit, ret_refs = py_param_type(m["returns"], type_index)
                refs.extend(ret_refs)
                # Deduplicate templateRefs by placeholder
                seen = {}
                for r in refs:
                    seen[r["placeholder"]] = r["typeIdentifier"]
                template_refs = [{"placeholder": k, "typeIdentifier": v} for k, v in seen.items()]
                params_str = ", ".join(["self"] + params)
                code = (
                    f"def {m['name']}({params_str}) -> {ret_lit}:\n"
                    f"    raise NotImplementedError('not implemented')"
                )
                entry = {"code": code}
                if template_refs:
                    entry["templateRefs"] = template_refs
                custom_code.append(entry)
            classes.append({
                "name": sname,
                "typeIdentifier": sid,
                "path": f"{dname}/services",
                "customCode": custom_code,
                "comment": f"{sname} service.",
            })

    spec = {
        "language": "python",
        "packageName": "metaengine_demo",
        "classes": classes,
        "enums": enums,
    }
    DST.write_text(json.dumps(spec, indent=2))


if __name__ == "__main__":
    build()
