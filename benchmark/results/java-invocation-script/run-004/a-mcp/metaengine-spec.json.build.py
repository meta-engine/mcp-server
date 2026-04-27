import json
import re

SRC = "<benchmark>/spec/large.json"
DST = "<benchmark>/results/20260426-113002-java-script/run-004/a-mcp/metaengine-spec.json"


def kebab(name: str) -> str:
    s = re.sub(r"(.)([A-Z][a-z]+)", r"\1-\2", name)
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", s)
    return s.lower()


PRIM = {
    "string": "String",
    "number": "Number",
    "boolean": "Boolean",
    "Date": "Date",
    "any": "Any",
}


def field_to_param(field, type_ids):
    name = field["name"]
    t = field["type"]
    if t in PRIM:
        return {"name": name, "primitiveType": PRIM[t]}
    if t in type_ids:
        return {"name": name, "typeIdentifier": type_ids[t]}
    # fallback: treat as primitive Any
    return {"name": name, "primitiveType": "Any"}


def java_type_for(t: str, agg_name: str, agg_id: str):
    """Returns (java_type_string, list_of_template_refs)."""
    t = t.strip()
    if t == "void":
        return "void", []
    if t == "string":
        return "String", []
    if t == "number":
        return "double", []
    if t == "boolean":
        return "boolean", []
    if t == "Date":
        return "java.time.Instant", []
    # Partial<Agg>
    m = re.match(r"^Partial<(.+)>$", t)
    if m:
        inner = m.group(1).strip()
        if inner == agg_name:
            return f"${agg_id}", [{"placeholder": f"${agg_id}", "typeIdentifier": agg_id}]
        return inner, []
    # Agg[]
    m = re.match(r"^(.+)\[\]$", t)
    if m:
        inner = m.group(1).strip()
        if inner == agg_name:
            return f"List<${agg_id}>", [{"placeholder": f"${agg_id}", "typeIdentifier": agg_id}]
        return f"List<{inner}>", []
    # Agg | null
    m = re.match(r"^(.+)\s*\|\s*null$", t)
    if m:
        inner = m.group(1).strip()
        if inner == agg_name:
            return f"${agg_id}", [{"placeholder": f"${agg_id}", "typeIdentifier": agg_id}]
        return inner, []
    # Plain Agg
    if t == agg_name:
        return f"${agg_id}", [{"placeholder": f"${agg_id}", "typeIdentifier": agg_id}]
    return t, []


def main():
    src = json.load(open(SRC))

    classes = []
    enums = []

    for domain in src["domains"]:
        dname = domain["name"]
        types = domain.get("types", [])
        services = domain.get("services", [])

        # Build a typeId map for this domain (aggregate, value_objects, enums)
        type_ids = {}
        for t in types:
            type_ids[t["name"]] = kebab(t["name"])

        # Find the aggregate
        agg = next((t for t in types if t["kind"] == "aggregate"), None)
        agg_name = agg["name"] if agg else None
        agg_id = kebab(agg_name) if agg_name else None

        for t in types:
            kind = t["kind"]
            name = t["name"]
            tid = kebab(name)
            if kind == "enum":
                enums.append({
                    "name": name,
                    "typeIdentifier": tid,
                    "path": f"{dname}/enums",
                    "comment": f"{name} enum.",
                    "members": t["members"],
                })
            elif kind == "aggregate":
                classes.append({
                    "name": name,
                    "typeIdentifier": tid,
                    "path": f"{dname}/aggregates",
                    "comment": f"{name} aggregate root for the {dname} domain.",
                    "constructorParameters": [field_to_param(f, type_ids) for f in t.get("fields", [])],
                })
            elif kind == "value_object":
                classes.append({
                    "name": name,
                    "typeIdentifier": tid,
                    "path": f"{dname}/value_objects",
                    "comment": f"{name} value object.",
                    "constructorParameters": [field_to_param(f, type_ids) for f in t.get("fields", [])],
                })

        for svc in services:
            sname = svc["name"]
            sid = kebab(sname)
            custom_code = []
            for m in svc.get("methods", []):
                ret_type, ret_refs = java_type_for(m["returns"], agg_name, agg_id)
                params = []
                refs = list(ret_refs)
                seen = {(r["placeholder"], r["typeIdentifier"]) for r in refs}
                for p in m.get("params", []):
                    pt, prefs = java_type_for(p["type"], agg_name, agg_id)
                    for r in prefs:
                        key = (r["placeholder"], r["typeIdentifier"])
                        if key not in seen:
                            refs.append(r)
                            seen.add(key)
                    params.append(f"{pt} {p['name']}")
                sig = f"public {ret_type} {m['name']}({', '.join(params)}) {{\n    throw new UnsupportedOperationException(\"not implemented\");\n}}"
                entry = {"code": sig}
                if refs:
                    entry["templateRefs"] = refs
                custom_code.append(entry)

            classes.append({
                "name": sname,
                "typeIdentifier": sid,
                "path": f"{dname}/services",
                "comment": f"{sname} service.",
                "customCode": custom_code,
            })

    out = {
        "language": "java",
        "packageName": "com.metaengine.demo",
        "classes": classes,
        "enums": enums,
    }

    with open(DST, "w") as f:
        json.dump(out, f, indent=2)
    print(f"Wrote {DST}: classes={len(classes)} enums={len(enums)}")


if __name__ == "__main__":
    main()
