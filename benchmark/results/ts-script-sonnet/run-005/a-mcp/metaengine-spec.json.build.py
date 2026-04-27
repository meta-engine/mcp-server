import json
import re

def to_kebab(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1-\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1-\2', s1).lower()

def map_primitive(t):
    return {'string': 'String', 'number': 'Number', 'Date': 'Date', 'boolean': 'Boolean'}.get(t, 'String')

def transform_method(method, agg_name, agg_id):
    def replace_agg(s):
        return s.replace(agg_name, '$Agg') if agg_name else s

    params_str = ', '.join(f"{p['name']}: {replace_agg(p['type'])}" for p in method['params'])
    ret = replace_agg(method['returns'])
    code = f"{method['name']}({params_str}): {ret} {{ throw new Error('not implemented'); }}"

    entry = {'code': code}
    if '$Agg' in code and agg_id:
        entry['templateRefs'] = [{'placeholder': '$Agg', 'typeIdentifier': agg_id}]
    return entry

with open('<benchmark>/spec/large.json') as f:
    spec = json.load(f)

classes, interfaces, enums = [], [], []

for domain in spec['domains']:
    domain_name = domain['name']
    agg_type = next((t for t in domain['types'] if t['kind'] == 'aggregate'), None)
    agg_name = agg_type['name'] if agg_type else None
    agg_id = to_kebab(agg_name) if agg_name else None

    for t in domain['types']:
        name = t['name']
        tid = to_kebab(name)

        if t['kind'] == 'aggregate':
            ctor_params = [{'name': f['name'], 'primitiveType': map_primitive(f['type'])} for f in t.get('fields', [])]
            classes.append({
                'name': name,
                'typeIdentifier': tid,
                'path': f'src/domain/{domain_name}/aggregates',
                'constructorParameters': ctor_params,
            })

        elif t['kind'] == 'value_object':
            props = [{'name': f['name'], 'primitiveType': map_primitive(f['type'])} for f in t.get('fields', [])]
            interfaces.append({
                'name': name,
                'typeIdentifier': tid,
                'path': f'src/domain/{domain_name}/value-objects',
                'properties': props,
            })

        elif t['kind'] == 'enum':
            enums.append({
                'name': name,
                'typeIdentifier': tid,
                'path': f'src/domain/{domain_name}/enums',
                'members': [{'name': m['name'], 'value': m['value']} for m in t.get('members', [])],
            })

    for svc in domain.get('services', []):
        svc_name = svc['name']
        custom_code = [transform_method(m, agg_name, agg_id) for m in svc.get('methods', [])]
        classes.append({
            'name': svc_name,
            'typeIdentifier': to_kebab(svc_name),
            'path': f'src/domain/{domain_name}/services',
            'customCode': custom_code,
        })

result = {'language': 'typescript', 'classes': classes, 'interfaces': interfaces, 'enums': enums}

out = '<benchmark>/results/20260426-182553-typescript-script-sonnet/run-005/a-mcp/metaengine-spec.json'
with open(out, 'w') as f:
    json.dump(result, f, indent=2)

print(f'Done. classes={len(classes)} interfaces={len(interfaces)} enums={len(enums)}')
