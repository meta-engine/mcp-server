import json
import re

SOURCE = "<benchmark>/spec/large.json"
TARGET = "<benchmark>/results/20260426-115000-python-script/run-001/a-mcp/metaengine-spec.json"

def kebab(name):
    s1 = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1-\2', name)
    s2 = re.sub(r'([a-z\d])([A-Z])', r'\1-\2', s1)
    return s2.lower()

FIELD_TYPE_MAP = {
    'string': 'String',
    'number': 'Number',
    'Date': 'Date',
}

def render_method_type(t, refs):
    """Return python type expression with $placeholders. Mutates refs dict."""
    if t == 'string':
        return 'str'
    if t == 'number':
        return 'int'
    if t == 'void':
        return 'None'
    m = re.match(r'^Partial<(\w+)>$', t)
    if m:
        cls = m.group(1)
        ph = f'${cls}'
        refs[ph] = kebab(cls)
        return ph
    m = re.match(r'^(\w+)\[\]$', t)
    if m:
        cls = m.group(1)
        ph = f'${cls}'
        refs[ph] = kebab(cls)
        return f'List[{ph}]'
    m = re.match(r'^(\w+) \| null$', t)
    if m:
        cls = m.group(1)
        ph = f'${cls}'
        refs[ph] = kebab(cls)
        return f'Optional[{ph}]'
    if re.match(r'^\w+$', t):
        ph = f'${t}'
        refs[ph] = kebab(t)
        return ph
    raise ValueError(f"Unhandled method type: {t!r}")

def build():
    src = json.load(open(SOURCE))
    classes = []
    enums = []

    for dom in src['domains']:
        domain = dom['name']
        for t in dom.get('types', []):
            kind = t['kind']
            name = t['name']
            tid = kebab(name)
            if kind == 'enum':
                enums.append({
                    "name": name,
                    "typeIdentifier": tid,
                    "path": f"{domain}/enums",
                    "comment": f"{name} enum.",
                    "members": t['members'],
                })
                continue
            if kind == 'aggregate':
                sub, comment = 'aggregates', f"{name} aggregate root for the {domain} domain."
            else:
                sub, comment = 'value_objects', f"{name} value object."
            ctor_params = []
            for f in t.get('fields', []):
                ctor_params.append({
                    "name": f['name'],
                    "primitiveType": FIELD_TYPE_MAP[f['type']],
                })
            classes.append({
                "name": name,
                "typeIdentifier": tid,
                "path": f"{domain}/{sub}",
                "comment": comment,
                "constructorParameters": ctor_params,
            })

        for s in dom.get('services', []):
            sname = s['name']
            stid = kebab(sname)
            custom_code = []
            for m in s.get('methods', []):
                refs = {}
                rendered = [
                    f"{p['name']}: {render_method_type(p['type'], refs)}"
                    for p in m.get('params', [])
                ]
                params_str = ", ".join(rendered)
                ret = render_method_type(m['returns'], refs)
                head = f"def {m['name']}(self, {params_str})" if params_str else f"def {m['name']}(self)"
                code = f"{head} -> {ret}:\n    raise NotImplementedError('not implemented')"
                template_refs = [
                    {"placeholder": ph, "typeIdentifier": tid_}
                    for ph, tid_ in refs.items()
                ]
                custom_code.append({"code": code, "templateRefs": template_refs})
            classes.append({
                "name": sname,
                "typeIdentifier": stid,
                "path": f"{domain}/services",
                "comment": f"{sname} service.",
                "customCode": custom_code,
            })

    return {
        "language": "python",
        "packageName": "metaengine_demo",
        "classes": classes,
        "enums": enums,
    }

def main():
    spec = build()
    with open(TARGET, 'w') as f:
        json.dump(spec, f, indent=2)
    print(f"wrote {TARGET} ({sum(1 for _ in open(TARGET))} lines)")
    print(f"classes: {len(spec['classes'])}, enums: {len(spec['enums'])}")

if __name__ == '__main__':
    main()
