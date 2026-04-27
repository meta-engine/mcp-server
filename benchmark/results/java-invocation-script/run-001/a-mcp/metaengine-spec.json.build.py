import json, re, pathlib

SRC = "<benchmark>/spec/large.json"
DST = "<benchmark>/results/20260426-113002-java-script/run-001/a-mcp/metaengine-spec.json"

def kebab(name: str) -> str:
    s = re.sub(r'(.)([A-Z][a-z]+)', r'\1-\2', name)
    s = re.sub(r'([a-z0-9])([A-Z])', r'\1-\2', s)
    return s.lower()

PRIM_MAP = {"string": "String", "number": "Number", "Date": "Date", "boolean": "Boolean"}

def to_ctor_params(fields):
    return [{"name": f["name"], "primitiveType": PRIM_MAP[f["type"]]} for f in fields]

def java_param_type(t: str, agg_refs: dict, agg_names: set):
    # Strip Partial<X> -> X
    m = re.fullmatch(r"Partial<([A-Za-z_][A-Za-z0-9_]*)>", t)
    if m:
        t = m.group(1)
    if t == "string":
        return "String"
    if t == "number":
        return "double"
    if t == "boolean":
        return "boolean"
    if t == "Date":
        return "java.time.Instant"
    if t in agg_names:
        agg_refs[t] = kebab(t)
        return f"${kebab(t).replace('-', '_')}"
    return t

def java_return_type(t: str, agg_refs: dict, agg_names: set):
    if t == "void":
        return "void"
    # X[] -> List<X>
    m = re.fullmatch(r"([A-Za-z_][A-Za-z0-9_]*)\[\]", t)
    if m:
        inner = java_param_type(m.group(1), agg_refs, agg_names)
        return f"List<{inner}>"
    # X | null -> X
    m = re.fullmatch(r"([A-Za-z_][A-Za-z0-9_]*)\s*\|\s*null", t)
    if m:
        return java_param_type(m.group(1), agg_refs, agg_names)
    return java_param_type(t, agg_refs, agg_names)

def main():
    spec = json.load(open(SRC))

    # Collect all aggregate names across all domains
    agg_names = set()
    for d in spec["domains"]:
        for t in d.get("types", []):
            if t.get("kind") == "aggregate":
                agg_names.add(t["name"])

    classes = []
    enums = []

    for domain in spec["domains"]:
        dname = domain["name"]
        for t in domain.get("types", []):
            kind = t.get("kind")
            tname = t["name"]
            tid = kebab(tname)
            if kind == "aggregate":
                classes.append({
                    "name": tname,
                    "typeIdentifier": tid,
                    "path": f"{dname}/aggregates",
                    "comment": f"{tname} aggregate root for the {dname} domain.",
                    "constructorParameters": to_ctor_params(t.get("fields", [])),
                })
            elif kind == "value_object":
                classes.append({
                    "name": tname,
                    "typeIdentifier": tid,
                    "path": f"{dname}/value_objects",
                    "comment": f"{tname} value object.",
                    "constructorParameters": to_ctor_params(t.get("fields", [])),
                })
            elif kind == "enum":
                enums.append({
                    "name": tname,
                    "typeIdentifier": tid,
                    "path": f"{dname}/enums",
                    "comment": f"{tname} enum.",
                    "members": [{"name": m["name"], "value": m["value"]} for m in t.get("members", [])],
                })

        for svc in domain.get("services", []):
            sname = svc["name"]
            sid = kebab(sname)
            custom_code = []
            for m in svc.get("methods", []):
                agg_refs = {}
                ret = java_return_type(m["returns"], agg_refs, agg_names)
                params = []
                for p in m.get("params", []):
                    pjt = java_param_type(p["type"], agg_refs, agg_names)
                    pname = p["name"]
                    # Avoid Java reserved-word param names where possible (none expected here)
                    params.append(f"{pjt} {pname}")
                method_name = m["name"]
                # 'delete' is fine as a Java identifier
                sig = f'public {ret} {method_name}({", ".join(params)}) {{ throw new UnsupportedOperationException("not implemented"); }}'
                # Replace placeholders like $order_status into $order_status; templateRefs map them to type ids.
                # Our placeholders use underscored kebab form; convert them back to dollar+identifier with no hyphens
                template_refs = []
                for agg_name, agg_id in agg_refs.items():
                    placeholder = f"${agg_id.replace('-', '_')}"
                    template_refs.append({"placeholder": placeholder, "typeIdentifier": agg_id})
                entry = {"code": sig}
                if template_refs:
                    entry["templateRefs"] = template_refs
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
        "outputPath": ".",
        "classes": classes,
        "enums": enums,
    }
    pathlib.Path(DST).write_text(json.dumps(out, indent=2))
    print(f"wrote {DST}: {len(classes)} classes, {len(enums)} enums")

if __name__ == "__main__":
    main()
