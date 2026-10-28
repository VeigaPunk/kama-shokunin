import json, importlib.util, copy, sys
S = sys.argv[1]; CTR = sys.argv[2]
spec = importlib.util.spec_from_file_location('c1', CTR)
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

def rewrite(r):
    # valid JSON, same content, different bytes: indent=1 (body grows past the
    # Content-Length the real server sent, if one is captured)
    r = copy.deepcopy(r); c = r['captures']['completion']
    obj = json.loads(c['body'])
    c['body'] = json.dumps(obj, indent=1)
    c['body_bytes'] = len(c['body'].encode())
    c['body_sha256'] = m.sha256_b(c['body'].encode())
    return r

for name, path in (('real-headers (base tool)', S + '/realhdr-receipt.json'),
                   ('pinned-headers (mutant 1)', S + '/T1-receipt.json')):
    r = json.load(open(path))
    print(f'{name}: captured completion headers = {sorted(r["captures"]["completion"]["headers"])}')
    for label, rr in (('genuine', r), ('body rewritten, same content', rewrite(r))):
        rec, inc = m.grade(rr)
        print(f'  {label:30s} completion_untruncated={rec["completion_untruncated"]} '
              f'completion_envelope={rec["completion_envelope"]} inconsistent={inc}')

# third case: what a header lie hides. Honest capture of a non-JSON answer,
# then the mutant-1 transform (pin content-type to application/json).
r = json.load(open(S + '/realhdr-receipt.json'))
r['captures']['completion']['headers']['content-type'] = 'text/plain'
rec, _ = m.grade(r)
print(f'honest capture, server sent text/plain: completion_headers={rec["completion_headers"]}')
r['captures']['completion']['headers'] = {'content-type': 'application/json'}
rec, _ = m.grade(r)
print(f'after pin-to-application/json (mutant 1): completion_headers={rec["completion_headers"]}')
