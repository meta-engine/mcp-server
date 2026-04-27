import json, re, os

def to_kebab(name):
    s = re.sub('(.)([A-Z][a-z]+)', r'\1-\2', name)
    s = re.sub('([a-z0-9])([A-Z])', r'\1-\2', s).lower()
    return s

PRIM_MAP = {'string': 'String', 'number': 'Number', 'Date': 'Date', 'boolean': 'Boolean'}

def map_field(f):
    p = PRIM_MAP.get(f['type'])
    if p:
        return {'name': f['name'], 'primitiveType': p}
    return {'name': f['name'], 'type': f['type']}

def build_method_code(method, agg_name, agg_tid):
    ph = '$Agg'
    def sub(s):
        return s.replace(agg_name, ph)
    params_str = ', '.join(f"{p['name']}: {sub(p['type'])}" for p in method['params'])
    ret_str = sub(method['returns'])
    code = f"{method['name']}({params_str}): {ret_str} {{ throw new Error('not implemented'); }}"
    uses_agg = any(agg_name in p['type'] for p in method['params']) or agg_name in method['returns']
    entry = {'code': code}
    if uses_agg:
        entry['templateRefs'] = [{'placeholder': ph, 'typeIdentifier': agg_tid}]
    return entry

SRC = '<benchmark>/spec/large.json'
OUT = '<benchmark>/results/20260426-182553-typescript-script-sonnet/run-002/a-mcp/metaengine-spec.json'

with open(SRC) as f:
    src = json.load(f)

classes, interfaces, enums = [], [], []

for domain in src['domains']:
    dn = domain['name']
    agg_type = next((t for t in domain['types'] if t['kind'] == 'aggregate'), None)
    agg_name = agg_type['name'] if agg_type else None
    agg_tid = to_kebab(agg_name) if agg_name else None

    for t in domain['types']:
        tid = to_kebab(t['name'])
        if t['kind'] == 'aggregate':
            classes.append({
                'name': t['name'],
                'typeIdentifier': tid,
                'path': f'src/domain/{dn}/aggregates',
                'comment': f"{t['name']} aggregate root for the {dn} domain.",
                'constructorParameters': [map_field(f) for f in t['fields']],
            })
        elif t['kind'] == 'value_object':
            interfaces.append({
                'name': t['name'],
                'typeIdentifier': tid,
                'path': f'src/domain/{dn}/value-objects',
                'comment': f"{t['name']} value object.",
                'properties': [map_field(f) for f in t['fields']],
            })
        elif t['kind'] == 'enum':
            enums.append({
                'name': t['name'],
                'typeIdentifier': tid,
                'path': f'src/domain/{dn}/enums',
                'comment': f"{t['name']} enum.",
                'members': [{'name': m['name'], 'value': m['value']} for m in t['members']],
            })

    for svc in domain.get('services', []):
        svc_tid = to_kebab(svc['name'])
        custom_code = [build_method_code(m, agg_name, agg_tid) for m in svc['methods']]
        classes.append({
            'name': svc['name'],
            'typeIdentifier': svc_tid,
            'path': f'src/domain/{dn}/services',
            'comment': f"{svc['name']} service.",
            'customCode': custom_code,
        })

result = {'language': 'typescript', 'classes': classes, 'interfaces': interfaces, 'enums': enums}
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, 'w') as f:
    json.dump(result, f, indent=2)
print(f"Written {OUT}")
