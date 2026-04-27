import json, re, sys

SRC = "<benchmark>/spec/large.json"
DST = "<benchmark>/results/20260426-115000-python-script/run-004/a-mcp/metaengine-spec.json"

PRIMITIVE = {
    "string": "String",
    "number": "Number",
    "boolean": "Boolean",
    "Date": "Date",
    "any": "Any",
}

def kebab(s):
    return re.sub(r'(?<!^)(?=[A-Z])', '-', s).lower()

def py_param_type(t):
    # Returns (text_or_None_for_primitive, templateRef_or_None)
    # Used for parameter types in method signatures
    if t.startswith("Partial<") and t.endswith(">"):
        return ("dict", None)
    if t in PRIMITIVE:
        return ({"string": "str", "number": "int", "boolean": "bool", "Date": "datetime", "any": "Any"}[t], None)
    # custom type — needs templateRef
    return (f"${t}", t)

def py_return_type(r):
    # Returns (text, list of typeIdentifiers referenced)
    if r == "void":
        return ("None", [])
    if r.endswith("[]"):
        inner = r[:-2].strip()
        if inner in PRIMITIVE:
            mapped = {"string": "str", "number": "int", "boolean": "bool", "Date": "datetime", "any": "Any"}[inner]
            return (f"list[{mapped}]", [])
        return (f"list[${inner}]", [inner])
    if "|" in r:
        # e.g. "Order | null"
        parts = [p.strip() for p in r.split("|")]
        rendered = []
        refs = []
        for p in parts:
            if p == "null":
                rendered.append("None")
            elif p in PRIMITIVE:
                rendered.append({"string": "str", "number": "int", "boolean": "bool", "Date": "datetime", "any": "Any"}[p])
            else:
                rendered.append(f"${p}")
                refs.append(p)
        return (" | ".join(rendered), refs)
    if r in PRIMITIVE:
        return ({"string": "str", "number": "int", "boolean": "bool", "Date": "datetime", "any": "Any"}[r], [])
    return (f"${r}", [r])

def to_snake(s):
    return re.sub(r'(?<!^)(?=[A-Z])', '_', s).lower()

def build():
    with open(SRC) as f:
        spec = json.load(f)

    classes = []
    enums = []

    for domain in spec["domains"]:
        dname = domain["name"]
        for t in domain.get("types", []):
            kind = t["kind"]
            name = t["name"]
            tid = kebab(name)
            if kind == "enum":
                enums.append({
                    "name": name,
                    "typeIdentifier": tid,
                    "path": f"{dname}/enums",
                    "comment": f"{name} enum.",
                    "members": [{"name": m["name"], "value": m["value"]} for m in t["members"]],
                })
            else:
                layer = "aggregates" if kind == "aggregate" else "value_objects"
                comment = f"{name} aggregate root for the {dname} domain." if kind == "aggregate" else f"{name} value object."
                ctor_params = []
                for f_ in t["fields"]:
                    ftype = f_["type"]
                    pname = f_["name"]
                    if ftype in PRIMITIVE:
                        ctor_params.append({"name": pname, "primitiveType": PRIMITIVE[ftype]})
                    else:
                        ctor_params.append({"name": pname, "typeIdentifier": kebab(ftype)})
                classes.append({
                    "name": name,
                    "typeIdentifier": tid,
                    "path": f"{dname}/{layer}",
                    "comment": comment,
                    "constructorParameters": ctor_params,
                })

        for svc in domain.get("services", []):
            sname = svc["name"]
            stid = kebab(sname)
            custom_code = []
            for m in svc["methods"]:
                mname = to_snake(m["name"])
                params = ["self"]
                refs = []
                ref_set = set()
                for p in m["params"]:
                    pt, ref = py_param_type(p["type"])
                    params.append(f"{p['name']}: {pt}")
                    if ref and ref not in ref_set:
                        refs.append({"placeholder": f"${ref}", "typeIdentifier": kebab(ref)})
                        ref_set.add(ref)
                ret_text, ret_refs = py_return_type(m["returns"])
                for r in ret_refs:
                    if r not in ref_set:
                        refs.append({"placeholder": f"${r}", "typeIdentifier": kebab(r)})
                        ref_set.add(r)
                code = f"def {mname}({', '.join(params)}) -> {ret_text}:\n    raise NotImplementedError('not implemented')"
                entry = {"code": code}
                if refs:
                    entry["templateRefs"] = refs
                custom_code.append(entry)
            classes.append({
                "name": sname,
                "typeIdentifier": stid,
                "path": f"{dname}/services",
                "comment": f"{sname} service.",
                "customCode": custom_code,
            })

    out = {
        "language": "python",
        "packageName": "metaengine_demo",
        "classes": classes,
        "enums": enums,
    }
    with open(DST, "w") as f:
        json.dump(out, f, indent=2)
    print(f"wrote {DST}: {len(classes)} classes, {len(enums)} enums")

if __name__ == "__main__":
    build()
