import importlib.util, json, copy, sys, traceback
spec = importlib.util.spec_from_file_location('c1', '/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round63-c1-counter.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
S = '/fast/scratch/hyaku/kama-r63/w/RV02C1CounterCode'
base = json.load(open(S + '/work/receipt.json'))
m.NONCE = base['nonce']
def body_edit(name, fn):
    r = copy.deepcopy(base); c = r['captures'][name]; o = json.loads(c['body']); fn(o)
    c['body'] = json.dumps(o, separators=(',', ':')); c['body_sha256'] = m.sha256_b(c['body'].encode()); c['body_bytes'] = len(c['body'].encode())
    return r
def probe(label, r, w=None):
    try:
        out, inc = m.grade(r); s = m.score(r, w)
        print(label, 'OK met=', s['met'], 'fails=', sorted(s['fails'])[:3])
    except Exception as e:
        print(label, 'CRASH', type(e).__name__, e)
probe('genuine', base)
probe('usage=5 (non-dict usage)', body_edit('completion', lambda o: o.update({'usage': 5})))
probe('usage=[] ', body_edit('completion', lambda o: o.update({'usage': []})))
probe('models data=5', body_edit('models', lambda o: o.update({'data': 5})))
probe('props non-dict', body_edit('props', lambda o: None) if False else (lambda r: (r['captures'].__setitem__('props', 'x'), r)[1])(copy.deepcopy(base)))
probe('captures list', dict(base, captures=[1]))
probe('hold non-dict teardown str', dict(base, teardown='x'))
probe('checks stored non-dict', (lambda r: (r['checks'].__setitem__('hold_released', 'yes'), r)[1])(copy.deepcopy(base)))
probe('receipt usage NaN', body_edit('completion', lambda o: o['usage'].update({'prompt_tokens': float('nan')})))
probe('timings NaN', body_edit('completion', lambda o: o['timings'].update({'predicted_ms': float('nan')})))
probe('fp trailing newline', body_edit('completion', lambda o: o.update({'system_fingerprint': o['system_fingerprint'] + '\n'})))
print('FP_RE nl:', bool(m.FP_RE.match('b1-aaaaaaaaa\n')), ' fullmatch:', bool(m.FP_RE.fullmatch('b1-aaaaaaaaa\n')))
print('FP_RE unicode digit:', bool(m.FP_RE.match('b\u0661-aaaaaaaaa')))
