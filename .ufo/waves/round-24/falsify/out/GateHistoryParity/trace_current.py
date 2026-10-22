import sys, runpy, importlib.util, json, os
path = sys.argv[1]
spec = importlib.util.spec_from_file_location("curmod", path)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
calls = {"missing_reachable":0, "unknown_citation":0, "opaque_hole":0,
         "refuse_unknown":0, "required_read":0, "root_tree":0,
         "refuse_unknown_raise":0}
_mr = m.missing_reachable
def mr(repo, root):
    calls["missing_reachable"] += 1
    r = _mr(repo, root)
    sys.stderr.write(f"TRACE missing_reachable repo={repo} missing={len(r[0])} opaque={len(r[1])}\n")
    return r
m.missing_reachable = mr
_uc = m.unknown_citation
def uc(stores, token):
    calls["unknown_citation"] += 1
    r = _uc(stores, token)
    sys.stderr.write(f"TRACE unknown_citation token={token} -> {r}\n")
    return r
m.unknown_citation = uc
_oh = m.opaque_hole
def oh(stores):
    calls["opaque_hole"] += 1
    r = _oh(stores)
    sys.stderr.write(f"TRACE opaque_hole -> {r}\n")
    return r
m.opaque_hole = oh
_ru = m.refuse_unknown
def ru(rnd, status, stores):
    calls["refuse_unknown"] += 1
    try:
        r = _ru(rnd, status, stores)
    except m.EvalError as e:
        calls["refuse_unknown_raise"] += 1
        sys.stderr.write(f"TRACE refuse_unknown RAISED rnd={rnd}: {e}\n")
        raise
    from collections import Counter
    sys.stderr.write(f"TRACE refuse_unknown rnd={rnd} states={dict(Counter(status.values()))}\n")
    return r
m.refuse_unknown = ru
_rr = m.required_read
def rr(what, exc):
    calls["required_read"] += 1
    return _rr(what, exc)
m.required_read = rr
_rt = m.root_tree
def rt(repo, root):
    calls["root_tree"] += 1
    return _rt(repo, root)
m.root_tree = rt
sys.argv = [path] + sys.argv[2:]
rc = m.main()
sys.stderr.write("TRACE calls=" + json.dumps(calls, sort_keys=True) + "\n")
sys.exit(rc)
