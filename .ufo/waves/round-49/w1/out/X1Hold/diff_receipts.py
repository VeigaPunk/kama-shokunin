#!/usr/bin/env python3
"""X1Hold: diff every captured leaf across original receipt-1.json, rerun-a (unwitnessed)
and rerun-b (witnessed), and classify each differing path as compared or instance-only by
the replay tool's own rules (projection(), compare())."""
import importlib.util
import json
import sys

REPLAY = "/fast/scratch/hyaku/kama-r49/X1Hold/lane/tools/kama-live-replay.py"
orig_p, a_p, b_p = sys.argv[1:4]
spec = importlib.util.spec_from_file_location("klr", REPLAY)
klr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(klr)

orig, a, b = (json.load(open(p)) for p in (orig_p, a_p, b_p))


def leaves(o, p=""):
    if isinstance(o, dict):
        for k in sorted(o, key=str):
            yield from leaves(o[k], f"{p}.{k}" if p else str(k))
    elif isinstance(o, list):
        if all(not isinstance(x, (dict, list)) for x in o) and len(o) <= 24:
            yield p, json.dumps(o, sort_keys=True)
        else:
            for i, v in enumerate(o):
                yield from leaves(v, f"{p}[{i}]")
    else:
        yield p, json.dumps(o)


def flat(r):
    return dict(leaves(r))


fo, fa, fb = flat(orig), flat(a), flat(b)
paths = sorted(set(fo) | set(fa) | set(fb))

# compared set: derive by mutating each leaf and asking compare() what it reports
# (cheap enough: compare() is pure). Instead, use the documented compared surfaces.

def compared_paths():
    """Union of leaf paths that compare() actually reads, discovered by perturbation."""
    import copy
    base = copy.deepcopy(a)
    hits = set()

    def walk(node, prefix):
        if isinstance(node, dict):
            for k in list(node):
                if isinstance(node[k], (dict, list)):
                    walk(node[k], prefix + [k])
                else:
                    yield prefix + [k]
        elif isinstance(node, list):
            pass

    # brute force over every leaf path of the rerun receipt structure, perturb, compare
    def all_leaf_paths(node, prefix=()):
        if isinstance(node, dict):
            for k in node:
                yield from all_leaf_paths(node[k], prefix + (k,))
        elif isinstance(node, list):
            for i, v in enumerate(node):
                yield from all_leaf_paths(v, prefix + (i,))
        else:
            yield prefix

    for path in all_leaf_paths(base):
        if not path:
            continue
        node = copy.deepcopy(base)
        tgt = node
        ok = True
        for k in path[:-1]:
            try:
                tgt = tgt[k]
            except (KeyError, IndexError, TypeError):
                ok = False
                break
        if not ok:
            continue
        old = tgt[path[-1]]
        if isinstance(old, bool):
            new = not old
        elif isinstance(old, (int, float)):
            new = old + 7
        elif isinstance(old, str):
            new = old + "-x1hold"
        elif old is None:
            new = "x1hold"
        else:
            continue
        tgt[path[-1]] = new
        if klr.compare(a, node):
            hits.add(".".join(str(k) for k in path))
    return hits


comp = compared_paths()

rows = []
for p in paths:
    v_o, v_a, v_b = fo.get(p, "<absent>"), fa.get(p, "<absent>"), fb.get(p, "<absent>")
    same = v_o == v_a == v_b
    rows.append((p, same, p in comp, v_o, v_a, v_b))

diffs = [r for r in rows if not r[1]]
print(f"LEAVES total={len(rows)} equal={len(rows)-len(diffs)} differ={len(diffs)}")
print(f"COMPARED_PATHS discovered={len(comp)}")
print()
print("== differing leaves: path | compared-by-tool | orig | rerun-a | rerun-b ==")
for p, same, is_comp, v_o, v_a, v_b in diffs:
    print(f"{p} | compared={is_comp} | {v_o[:80]} | {v_a[:80]} | {v_b[:80]}")
print()
print("== differing leaves that the tool compares (would fail the replay) ==")
fails = [r for r in diffs if r[2]]
print("none" if not fails else "\n".join(r[0] for r in fails))

print()
print("== compare() verdicts ==")
for name, x, y in (("orig~rerun-a", orig, a), ("orig~rerun-b", orig, b), ("rerun-a~rerun-b", a, b)):
    m = klr.compare(x, y)
    print(f"{name}: mismatches={len(m)} {m}")

print()
print("== projection (tool's own stable projection) ==")
for name, r in (("orig", orig), ("rerun-a", a), ("rerun-b", b)):
    print(name, json.dumps(klr.projection(r), sort_keys=True))

print()
print("== witness blocks ==")
print("orig:", json.dumps(orig.get("witness")))
print("rerun-a:", json.dumps(a.get("witness")))
print("rerun-b:", json.dumps(b.get("witness")))

print()
print("== checks ==")
for name, r in (("orig", orig), ("rerun-a", a), ("rerun-b", b)):
    ev = [(c.get("id"), c.get("passed"), c.get("evaluated")) for c in r.get("checks") or []]
    print(name, f"outcome={r.get('outcome')} n={len(ev)}", ev)

print()
print("== teardown ==")
for name, r in (("orig", orig), ("rerun-a", a), ("rerun-b", b)):
    td = dict(r.get("teardown") or {})
    td.pop("log_lines", None)
    print(name, json.dumps(td, sort_keys=True))

print()
print("== loading envelope ==")
for name, r in (("orig", orig), ("rerun-a", a), ("rerun-b", b)):
    print(name, json.dumps({k: r.get(k) for k in ("loading_envelope_exact", "loading_observed",
                                                  "loading_bodies_dropped")}), 
          json.dumps(r.get("loading_503")), "n_bodies=", len(r.get("loading_503_bodies") or []))

print()
print("== timing envelope ==")
for name, r in (("orig", orig), ("rerun-a", a), ("rerun-b", b)):
    print(name, json.dumps({k: r.get(k) for k in ("started_utc", "ended_utc", "port", "child_pid")}),
          "witness=", r.get("witness"), "live_receipt_schema=", r.get("schema"))
