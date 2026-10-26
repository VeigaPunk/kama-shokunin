#!/usr/bin/env python3
"""Independent hand-derivation of v2 event fields (R1Sample, round 47).

Deliberately does NOT import tools/append-only-audit.py.
Deleted lines are reconstructed by slicing the PARENT blob with the
-U0 hunk-header old ranges (byte-exact, independent of '-'-line parsing);
a second, '-'-body parse is used only as a cross-check, as is numstat.
"""
import collections
import json
import random
import re
import subprocess
import sys

REPO = "/fast/scratch/hyaku/kama-r47/R1Sample/lane"
TO = "3a09a1d93dcc16799cf6c4b48786e6440af134c4"
SEED = 47

HUNK = re.compile(rb"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")


def git(*a, inp=None):
    r = subprocess.run(["git", "-C", REPO, *a], input=inp, capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"git {a[:4]}: {r.stderr[:300]}")
    return r.stdout


def blob_lines(rev, path):
    if subprocess.run(["git", "-C", REPO, "cat-file", "-e", f"{rev}:{path}"],
                      capture_output=True).returncode != 0:
        return None
    data = git("cat-file", "blob", f"{rev}:{path}")
    segs = data.split(b"\n")
    if segs and segs[-1] == b"":
        segs.pop()
    return segs


def deleted_by_header_slice(parent, commit, path):
    """Deleted lines = parent blob lines addressed by each hunk's old range."""
    raw = git("diff", "--no-renames", "--no-color", "--no-ext-diff", "-U0",
              "--text", parent, commit, "--", path)
    plines = blob_lines(parent, path)
    if plines is None:
        plines = []
    out, bodies = [], []
    for ln in raw.split(b"\n"):
        m = HUNK.match(ln)
        if m:
            a = int(m.group(1))
            ac = int(m.group(2)) if m.group(2) is not None else 1
            start = a - 1 if a > 0 else 0
            out.extend(plines[start:start + ac])
        elif ln.startswith(b"-") and not ln.startswith(b"--- "):
            bodies.append(ln[1:])
    return out, bodies


def numstat_del(parent, commit, path):
    txt = git("diff", "--numstat", "--no-renames", parent, commit, "--", path).decode()
    for line in txt.splitlines():
        f = line.split("\t")
        if len(f) == 3 and f[2] == path:
            return None if f[1] == "-" else int(f[1])
    return 0


def sub_multiset(big, small):
    """big - small; raises when small is not contained in big."""
    rem = collections.Counter(big)
    for k, v in collections.Counter(small).items():
        if rem[k] < v:
            raise RuntimeError("deleted lines not contained in parent blob")
        rem[k] -= v
        if rem[k] == 0:
            del rem[k]
    return rem


def held(m_x, kept, deleted):
    total = 0
    for l, d in deleted.items():
        total += min(d, max(0, m_x.get(l, 0) - kept.get(l, 0)))
    return total


def derive(commit, path):
    parent = git("rev-parse", f"{commit}^").decode().strip()
    ns = numstat_del(parent, commit, path)
    hdr, body = deleted_by_header_slice(parent, commit, path)
    assert len(hdr) == len(body), f"header-slice {len(hdr)} != body-parse {len(body)}"
    assert ns is not None and len(hdr) == ns, f"deleted {len(hdr)} != numstat {ns}"
    parent_lines = blob_lines(parent, path) or []
    kept = sub_multiset(parent_lines, hdr)
    deleted = collections.Counter(hdr)

    order = git("rev-list", "--topo-order", "--reverse", TO).decode().split()
    i0 = order.index(commit)
    window = order[i0:]

    # No history simplification: resolve the blob id at EVERY window commit
    # (one batch-check), then read each distinct blob once.
    specs = [f"{x}:{path}" for x in window]
    blob_of = {}
    out = git("cat-file", "--batch-check=%(objectname) %(objecttype)",
              inp=("\n".join(specs) + "\n").encode()).decode()
    for spec, line in zip(specs, out.split("\n")):
        parts = line.split()
        blob_of[spec] = parts[0] if len(parts) == 2 and parts[1] == "blob" else None
    mcache = {}

    def multiset_at(x):
        b = blob_of[f"{x}:{path}"]
        if b not in mcache:
            mcache[b] = collections.Counter(blob_lines(x, path) or []) if b else collections.Counter()
        return mcache[b]

    traj = []
    best = 0
    best_at = None
    by = None
    for x in window:
        h = held(multiset_at(x), kept, deleted)
        traj.append((x, h))
        if h > best:
            best, best_at = h, x
        if h == len(hdr) and by is None:
            by = x
    status = "restored" if best == len(hdr) else ("unrestored" if best == 0 else "partial")
    return dict(commit=commit, file=path, parent=parent, numstat=ns,
                deleted=hdr, deleted_n=len(hdr), kept_n=sum(kept.values()),
                parent_n=len(parent_lines), traj=traj,
                restored_max=best,
                restored_best=best_at if best else None,
                restored_by=by,
                status=status)


def show(ev, res):
    c8 = res["commit"][:8]
    print(f"== EVENT {c8} {res['file']}")
    print(f"   parent {res['parent'][:8]}  parent_lines={res['parent_n']} kept={res['kept_n']}")
    print(f"   numstat deletions={res['numstat']}  header-slice deleted={res['deleted_n']}  (equal: {res['numstat']==res['deleted_n']})")
    shown = res["deleted"][:6]
    extra = res["deleted_n"] - len(shown)
    for l in shown:
        print(f"   - {l.decode('utf-8','replace')[:100]}")
    if extra > 0:
        print(f"   - ... ({extra} more deleted lines)")
    pts = [t for k, t in enumerate(res["traj"])
           if k == 0 or t[1] != res["traj"][k - 1][1]]
    tail = pts[-8:]
    if len(pts) > len(tail):
        print(f"   held trajectory change-points ({len(pts)}, showing first 1 + last 7):")
        print(f"   {pts[0][0][:8]} held={pts[0][1]}  ... ")
    else:
        print(f"   held trajectory change-points ({len(pts)}):")
    for x, h in tail:
        print(f"   {x[:8]} held={h}")
    print(f"   HAND: deleted={res['deleted_n']} restored_max={res['restored_max']} "
          f"restored_best={res['restored_best'][:8] if res['restored_best'] else '-'} "
          f"restored_by={res['restored_by'][:8] if res['restored_by'] else '-'} status={res['status']}")
    tool = next(e for e in EVENTS if e["commit"] == res["commit"] and e["file"] == res["file"])
    same = (tool["deleted"] == res["deleted_n"]
            and tool["restored_max"] == res["restored_max"]
            and tool["restored_best"] == res["restored_best"]
            and tool["restored_by"] == res["restored_by"]
            and tool["status"] == res["status"])
    print(f"   V2  : deleted={tool['deleted']} restored_max={tool['restored_max']} "
          f"restored_best={(tool['restored_best'] or '-')[:8]} "
          f"restored_by={(tool['restored_by'] or '-')[:8]} status={tool['status']}")
    print(f"   MATCH: {'YES' if same else 'NO  <<< DIFFERENCE'}")
    return same


audit = json.load(open("/fast/scratch/hyaku/kama-r47/R1Sample/audit.json"))
EVENTS = audit["events"]
rng = random.Random(SEED)
sample = rng.sample(EVENTS, 10)
print(f"seed={SEED} sampled {len(sample)} of {len(EVENTS)} events")
for k, e in enumerate(sample, 1):
    print(f"  #{k}: {e['commit'][:8]} {e['file']} (v2: deleted={e['deleted']} max={e['restored_max']} {e['status']})")
print()

mismatches = []
for k, e in enumerate(sample, 1):
    res = derive(e["commit"], e["file"])
    if not show(e, res):
        mismatches.append(res)

print("\n### aggregate: independent recompute of ALL 91 events (same machinery, no evidence print)")
diffs = []
for e in EVENTS:
    r = derive(e["commit"], e["file"])
    if not (e["deleted"] == r["deleted_n"] and e["restored_max"] == r["restored_max"]
            and e["restored_best"] == r["restored_best"] and e["restored_by"] == r["restored_by"]
            and e["status"] == r["status"]):
        diffs.append((e, r["deleted_n"], r["restored_max"], r["restored_best"], r["restored_by"], r["status"]))
print(f"all-91 mismatches: {len(diffs)}")
for d in diffs:
    print("  DIFF", d)
print(f"\nsampled mismatches: {len(mismatches)}")
