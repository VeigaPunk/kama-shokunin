import importlib.util, json, pathlib, sys
root = pathlib.Path('/fast/scratch/hyaku/kama-r24/postfix/FinalCase03')
def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
pg = load('pg', root/'clone/tests/report-audit/promisor-grid.py')
aud = load('aud', root/'clone/tools/report-landing-audit.py')
built = pg.build(root/'fixt', root/'fixt/probe', lane_mark='marker')
lane, fleet = built['lane'], built['fleet']
l1 = built['shas']['lane_commit']
stores = (aud.build_store(lane, 'refs/heads/master'), aud.build_store(fleet, 'HEAD'))
print('PREMISE', json.dumps(built['premise']))
print('per-store bare (lane):', {k: v for k, v in aud.bare_objects(stores[0], [l1]).items()})
print('per-store bare (fleet):', {k: v for k, v in aud.bare_objects(stores[1], [l1]).items()})
print('peeled lookup status:', aud.lookup(stores, [l1], '^{commit}'))
print('unpeeled lookup status:', aud.lookup(stores, [l1]))
print('absent token status:', aud.lookup(stores, [pg.FAKE], '^{commit}'))
print('lane missing:', stores[0].missing()[0], 'fleet missing:', stores[1].missing()[0])
# --- control: reintroduce the union merge (one shared bare lookup for all stores)
orig_bare = aud.bare_objects
union = {}
def merged_bare(store, tokens):
    out = {}
    for t in tokens:
        if t not in union:
            for s in stores:
                r = orig_bare(s, [t])
                if r[t][0] == 'found':
                    union[t] = r[t]; break
        out[t] = union.get(t, ('absent', None))
    return out
aud.bare_objects = merged_bare
st_union = aud.lookup(stores, [l1], '^{commit}')
print('CONTROL union-merged peeled status:', st_union)
try:
    aud.refuse_unknown(1, st_union, stores)
    print('CONTROL union-merged: no refusal')
except aud.EvalError as exc:
    print('CONTROL union-merged refusal:', exc)
aud.bare_objects = orig_bare
