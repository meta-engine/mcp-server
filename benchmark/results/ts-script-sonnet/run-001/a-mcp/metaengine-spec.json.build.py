import json, re

SRC = '<benchmark>/spec/large.json'
OUT = '<benchmark>/results/20260426-182553-typescript-script-sonnet/run-001/a-mcp/metaengine-spec.json'

PRIM = {'string': 'String', 'number': 'Number', 'boolean': 'Boolean', 'Date': 'Date'}

def to_kebab(name):
    return re.sub(r'([A-Z])', r'-\1', name).lstrip('-').lower()

def me_field(f):
    pt = PRIM.get(f['type'])
    if pt:
        return {'name': f['name'], 'primitiveType': pt}
    return {'name': f['name'], 'type': f['type']}

def method_entry(m, agg_name, agg_id):
    def sub(s):
        return s.replace(agg_name, '$Agg') if agg_name else s

    params = ', '.join(f"{p['name']}: {sub(p['type'])}" for p in m['params'])
    ret = sub(m['returns'])
    code = f"{m['name']}({params}): {ret} {{ throw new Error('not implemented'); }}"
    entry = {'code': code}
    if agg_name and '$Agg' in code:
        entry['templateRefs'] = [{'placeholder': '$Agg', 'typeIdentifier': agg_id}]
    return entry

with open(SRC) as f:
    src = json.load(f)

classes, interfaces, enums = [], [], []

for domain in src['domains']:
    dn = domain['name']
    agg = next((t for t in domain['types'] if t['kind'] == 'aggregate'), None)
    agg_name = agg['name'] if agg else None
    agg_id   = to_kebab(agg_name) if agg_name else None

    for t in domain['types']:
        name, tid = t['name'], to_kebab(t['name'])
        if t['kind'] == 'aggregate':
            classes.append({
                'name': name, 'typeIdentifier': tid,
                'path': f'src/domain/{dn}/aggregates',
                'comment': f'{name} aggregate root for the {dn} domain.',
                'constructorParameters': [me_field(f) for f in t['fields']]
            })
        elif t['kind'] == 'value_object':
            interfaces.append({
                'name': name, 'typeIdentifier': tid,
                'path': f'src/domain/{dn}/value-objects',
                'comment': f'{name} value object.',
                'properties': [me_field(f) for f in t['fields']]
            })
        elif t['kind'] == 'enum':
            enums.append({
                'name': name, 'typeIdentifier': tid,
                'path': f'src/domain/{dn}/enums',
                'comment': f'{name} enum.',
                'members': [{'name': m['name'], 'value': m['value']} for m in t['members']]
            })

    for svc in domain.get('services', []):
        sn, sid = svc['name'], to_kebab(svc['name'])
        classes.append({
            'name': sn, 'typeIdentifier': sid,
            'path': f'src/domain/{dn}/services',
            'comment': f'{sn} service.',
            'customCode': [method_entry(m, agg_name, agg_id) for m in svc['methods']]
        })

with open(OUT, 'w') as f:
    json.dump({'language': 'typescript', 'classes': classes, 'interfaces': interfaces, 'enums': enums}, f, indent=2)

print('Wrote', OUT)
