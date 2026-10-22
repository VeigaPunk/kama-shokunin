import importlib.util, json, pathlib
root = pathlib.Path('/fast/scratch/hyaku/kama-r24/postfix/FinalCase03')
def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
pg = load('pg', root/'clone/tests/report-audit/promisor-grid.py')
aud = load('aud', root/'clone/tools/report-landing-audit.py')
built = pg.build(root/'fixt', root/'fixt/wt', lane_mark='marker')
lane, fleet = built['lane'], built['fleet']
blob = built['shas']['f_blob']
stores = (aud.build_store(lane,'refs/heads/master'), aud.build_store(fleet,'HEAD'))
print('blob in lane:', blob in pg.object_inventory(lane), 'in fleet:', blob in pg.object_inventory(fleet))
print('PINNED peeled status (blob token):', aud.lookup(stores, [blob], '^{commit}'))
orig = aud.bare_objects
union = {}
def merged(store, tokens):
    out = {}
    for t in tokens:
        if t not in union:
            for s in stores:
                r = orig(s, [t])
                if r[t][0] == 'found':
                    union[t] = r[t]; break
        out[t] = union.get(t, ('absent', None))
    return out
aud.bare_objects = merged
st = aud.lookup(stores, [blob], '^{commit}')
print('CONTROL union-merged peeled status (blob token):', st)
try:
    aud.refuse_unknown(1, st, stores); print('CONTROL union-merged: no refusal')
except aud.EvalError as e:
    print('CONTROL union-merged refusal:', e)
aud.bare_objects = orig
