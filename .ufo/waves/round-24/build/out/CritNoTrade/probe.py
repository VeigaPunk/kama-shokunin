#!/usr/bin/env python3
"""CritNoTrade bounded probe (offline, local file:// fixtures only).

Builds full-clone / promisor-marked twins and runs the r22 (4fe9339f) and
r23 (0df800e8) auditors. Expected exits/finding IDs are fixed from fixture
construction, never from an arm. Usage: probe.py SCRATCH OUT.json
"""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

SCRATCH = Path(sys.argv[1])
OUT = Path(sys.argv[2])
ARMS = {"r22": SCRATCH / "audit-r22.py", "r23": SCRATCH / "audit-r23.py"}
REL = ".ufo/reports/round-1/kama.md"
FAKE = "1234567890abcdef1234567890abcdef12345678"


def env(**extra):
    e = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    e.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
             GIT_AUTHOR_EMAIL="a@x", GIT_COMMITTER_EMAIL="a@x",
             GIT_AUTHOR_NAME="fixture", GIT_COMMITTER_NAME="fixture")
    e.update(extra)
    return e


def g(repo, *args, data=None, check=True, **extra):
    p = subprocess.run(["git", "-C", str(repo), *args], input=data,
                       capture_output=True, env=env(**extra), timeout=60)
    if check and p.returncode:
        raise SystemExit(f"premise: git {args}: {p.stderr.decode()}")
    return p.stdout.decode(errors="surrogateescape").strip()


def gi(repo, *args):
    """Run git with the auditor's isolation flags; return (rc, out, err)."""
    p = subprocess.run(["git", "--no-replace-objects", "--no-lazy-fetch",
                        "-C", str(repo), *args], capture_output=True,
                       env=env(), timeout=60)
    return p.returncode, p.stdout.decode(errors="replace").strip(), \
        p.stderr.decode(errors="replace").strip()[-200:]


def init(path):
    g(path.parent, "init", "-q", "-b", "master", str(path))
    return path


def commit(repo, author, when, msg, path="f", content=None):
    t = Path(repo, path)
    t.parent.mkdir(parents=True, exist_ok=True)
    if content is None:
        with open(t, "ab") as fh:
            fh.write((msg + "\n").encode())
    else:
        t.write_bytes(content)
    g(repo, "add", "--", path)
    s = f"@{when} +0000"
    g(repo, "-c", "commit.gpgsign=false", "commit", "-q", "-m", msg,
      GIT_AUTHOR_NAME=author, GIT_COMMITTER_NAME=author,
      GIT_AUTHOR_DATE=s, GIT_COMMITTER_DATE=s)
    return g(repo, "rev-parse", "HEAD")


def report(cites, extra=b""):
    return (b"# kama round 1\n\n## Landed changes\n\n"
            + b"".join(b"- " + c.encode() + b"\n" for c in cites) + extra)


def publish(fleet, text, when=2000):
    commit(fleet, "fleet", when, "round-1: report", REL, text)


def clone(src, dst, filt=None, honor=False, bare=False):
    up = []
    if honor:
        up = ["--upload-pack", "git -c uploadpack.allowFilter=true "
              "-c uploadpack.allowAnySHA1InWant=true upload-pack"]
    args = ["-c", "protocol.file.allow=always", "clone", "-q", "--no-local",
            *up, *([f"--filter={filt}"] if filt else []),
            *(["--bare"] if bare else []), f"file://{src}", str(dst)]
    g(src.parent, *args)
    return dst


def missing_count(repo):
    rc, out, _ = gi(repo, "rev-list", "--objects", "--missing=print", "--all")
    return sum(1 for l in out.split("\n") if l.startswith("?")) if rc == 0 \
        else f"rc{rc}"


def promisor_meta(repo):
    gd = Path(g(repo, "rev-parse", "--absolute-git-dir"))
    packs = [p.name for p in (gd / "objects/pack").glob("*.promisor")]
    cfg = g(repo, "config", "--list", check=False)
    keys = [l.split("=")[0] for l in cfg.split("\n")
            if "promisor" in l or "partialclone" in l]
    return {"promisor_packs": len(packs), "config": keys}


def audit(arm, lane, fleet):
    p = subprocess.run([sys.executable, str(ARMS[arm]), "--lane-repo",
                        str(lane), "--fleet-repo", str(fleet), "--json",
                        "--rounds", "1", "--no-errata"],
                       capture_output=True, env=env(), timeout=120)
    ids = None
    if p.returncode in (0, 1):
        doc = json.loads(p.stdout)
        ids = sorted(f"{d['kind']}:{d['token']}" for r in doc["results"]
                     for d in r["defects"])
    return {"exit": p.returncode, "ids": ids,
            "stderr": p.stderr.decode(errors="replace").strip()[-160:]}


ROWS = []
probes = {}


def row(name, lane, fleet, want_exit, want_ids, twin=None, note=""):
    r = {"row": name, "want_exit": want_exit, "want_ids": want_ids,
         "note": note, "lane_meta": promisor_meta(lane),
         "fleet_meta": promisor_meta(fleet),
         "lane_missing": missing_count(lane),
         "fleet_missing": missing_count(fleet)}
    for arm in ARMS:
        # private copies: the r22 arm may lazy-fetch and hydrate a fixture
        n = len(ROWS)
        lc_ = Path(lane.parent, f"{lane.name}.{arm}.{n}")
        fc_ = Path(fleet.parent, f"{fleet.name}.{arm}.{n}.f")
        witness = Path(lane.parent, f"fetch-witness.{arm}.{n}")
        witness.unlink(missing_ok=True)
        for src, dst in ((lane, lc_), (fleet, fc_)):
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst, symlinks=True)
            if g(dst, "config", "remote.origin.url", check=False):
                # any lazy fetch over file:// runs this upload-pack
                g(dst, "config", "remote.origin.uploadpack",
                  f"touch {witness}; git -c uploadpack.allowFilter=true "
                  f"-c uploadpack.allowAnySHA1InWant=true upload-pack")
        a = audit(arm, lc_, fc_)
        a["lazy_fetch_attempted"] = witness.exists()
        a["met"] = (a["exit"] == want_exit and
                    (want_ids is None or a["ids"] == sorted(want_ids)))
        a["lane_missing_after"] = missing_count(lc_)
        a["fleet_missing_after"] = missing_count(fc_)
        r[arm] = a
    if twin:
        r["twin_of"] = twin
    ROWS.append(r)


def fresh(name):
    d = SCRATCH / "fx" / name
    if d.exists():
        shutil.rmtree(d)
    d.mkdir(parents=True)
    return d


# ---- A: full vs complete-promisor (filter NOT honored) vs honored blob:none
def missing_info(repo):
    rc, out, _ = gi(repo, "rev-list", "--objects", "--missing=print-info",
                    "--all")
    return [l for l in out.split("\n") if l.startswith("?")] if rc == 0 \
        else f"rc{rc}"


def family(name, extra_fn, want_exit, want_ids_fn, override=None):
    """override: {variant: (exit, ids_or_None)} where twin parity is not
    the oracle (required evidence unavailable / absence unprovable)."""
    override = override or {}
    d = fresh(name)
    lane, fleet = init(d / "lane"), init(d / "fleet")
    lc = commit(lane, "kama-shokunin", 1000, "round-1: work")
    commit(lane, "fixture", 1100, "history blob", "h", b"old\n")
    commit(lane, "fixture", 1200, "history blob 2", "h", b"new\n")
    ctx = extra_fn(lane, fleet, lc)
    commit(fleet, "fleet", 3000, "later", "notes.md", b"n\n")
    ids = want_ids_fn(ctx)
    override.setdefault("fleet-tree0", (2, None))
    row(f"{name}/full", lane, fleet, want_exit, ids)
    variants = [
        ("promisor-complete", clone(lane, d / "pu", filt="blob:none"), fleet,
         "filter ignored by server: all objects local + promisor meta"),
        ("blobless-honored", clone(lane, d / "bh", filt="blob:none",
                                   honor=True), fleet,
         "historic blobs missing (blob-only ? set); commits/reports present"),
        ("tree0-honored", clone(lane, d / "t0", filt="tree:0", honor=True),
         fleet, "historic trees missing: ? set cannot enumerate absence"),
        ("fleet-blobless", lane, clone(fleet, d / "fb", filt="blob:none",
                                       honor=True),
         "lane full; fleet historic blobs missing, trees present"),
        ("fleet-tree0", lane, clone(fleet, d / "ft", filt="tree:0",
                                    honor=True),
         "lane full; fleet historic trees missing (cutoff evidence)"),
    ]
    meta = clone(lane, d / "mo")
    g(meta, "config", "remote.origin.partialclonefilter", "blob:none")
    variants.append(("filter-config-only", meta, fleet,
                     "F27 shape: config only, content complete"))
    for v, ln, fl, note in variants:
        we, wi = override.get(v, (want_exit, ids))
        row(f"{name}/{v}", ln, fl, we, wi, twin=f"{name}/full", note=note)
        ROWS[-1]["lane_missing_info"] = missing_info(ln)[:4]
        ROWS[-1]["fleet_missing_info"] = missing_info(fl)[:4]
    return ctx


def cite_blob(lane, fleet, lc):
    blob = g(lane, "rev-parse", "HEAD~1:h")
    publish(fleet, report([lc]) + b"\n## Notes\n\nblob " + blob.encode()
            + b"\n")
    return {"blob": blob}


def clean(lane, fleet, lc):
    publish(fleet, report([lc]))
    return {}


def omission(lane, fleet, lc):
    x = commit(lane, "kama-shokunin", 1500, "round-1: more")
    publish(fleet, report([lc]))
    return {"x": x}


def bogus(lane, fleet, lc):
    publish(fleet, report([lc]) + b"\n## Notes\n\nsee " + FAKE.encode()
            + b"\n")
    return {}


family("A1-clean", clean, 0, lambda c: [])
family("A2-omission", omission, 1, lambda c: [f"landed-omitted:{c['x']}"])
# absence of FAKE is provable only where the ? set is enumerable (blob-only)
family("A3-bogus-full", bogus, 1, lambda c: [f"unresolved-full-hash:{FAKE}"],
       override={"tree0-honored": (2, None)})
# a cited blob that is promised-missing: exists remotely, unavailable here
family("A4-cited-historic-blob", cite_blob, 0, lambda c: [],
       override={"blobless-honored": (2, None), "tree0-honored": (2, None)})


# ---- B: abbreviation ambiguity hidden by a missing (promised) blob
def collide(tree, n=1 << 15):
    blobs = {}
    for i in range(n):
        data = f"collide {i}\n".encode()
        oid = hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()
        blobs.setdefault(oid[:7], (oid, data))
    for i in range(n * 8):
        msg = f"round-1: work {i}\n".encode()
        who = b"kama-shokunin <a@x> 1000 +0000"
        body = (b"tree " + tree.encode() + b"\nauthor " + who
                + b"\ncommitter " + who + b"\n\n" + msg)
        oid = hashlib.sha1(b"commit %d\0" % len(body) + body).hexdigest()
        if oid[:7] in blobs:
            return body, oid, blobs[oid[:7]]
    raise SystemExit("premise: no 7-hex collision found")


d = fresh("B1-abbrev-ambiguity")
lane, fleet = init(d / "lane"), init(d / "fleet")
Path(lane, "f").write_bytes(b"base\n")
g(lane, "add", "f")
tree = g(lane, "write-tree")
body, coid, (boid, bdata) = collide(tree)
got = g(lane, "hash-object", "-t", "commit", "-w", "--stdin", data=body)
assert got == coid
g(lane, "update-ref", "refs/heads/master", coid)
g(lane, "reset", "-q", "--hard", coid)
commit(lane, "fixture", 1100, "hide", "h", bdata)
commit(lane, "fixture", 1200, "drop", "h", b"other\n")
assert g(lane, "rev-parse", f"HEAD~1:h") == boid
abbrev = coid[:7]
publish(fleet, report([abbrev]))
probes["B1-bare-vs-peeled"] = [
    subprocess.run(["git", "-C", str(lane), "cat-file", "--batch-check"],
                   input=f"{abbrev}\n{abbrev}^{{commit}}\n".encode(),
                   capture_output=True, env=env()).stdout.decode()]
# ^{commit} peel disambiguates to the unique commit, so the auditor reports
# found (lookup() overwrites the bare 'ambiguous'); twin parity is exit0
row("B1/full", lane, fleet, 0, [], note=f"commit {coid} blob {boid}")
hon = clone(lane, d / "blobless-honored", filt="blob:none", honor=True)
assert gi(hon, "cat-file", "-e", boid)[0] != 0
row("B1/blobless-honored", hon, fleet, 0, [], twin="B1/full",
    note="colliding blob promised-missing; type-peeled lookup unaffected")
unh = clone(lane, d / "promisor-unhonored", filt="blob:none")
row("B1/promisor-complete", unh, fleet, 0, [], twin="B1/full")

# ---- E1: cited blob promised only by an unreachable promisor commit
d = fresh("E1-unreachable-promised")
lane, fleet = init(d / "lane"), init(d / "fleet")
lc = commit(lane, "kama-shokunin", 1000, "round-1: work")
g(lane, "checkout", "-qb", "side")
commit(lane, "x", 1100, "side", "z", b"secret-z\n")
z = g(lane, "rev-parse", "HEAD:z")
g(lane, "checkout", "-q", "master")
publish(fleet, report([lc]) + b"\n## Notes\n\nblob " + z.encode() + b"\n")
full = clone(lane, d / "full")
part = clone(lane, d / "part", filt="blob:none", honor=True)
for r_ in (full, part):
    g(r_, "update-ref", "-d", "refs/remotes/origin/side")
refs_walk = [l for l in gi(part, "rev-list", "--objects", "--missing=print",
                           "--all")[1].split("\n") if l.startswith("?")]
roots = "".join(l.split()[1] + "\n" for l in subprocess.run(
    ["git", "--no-lazy-fetch", "-C", str(part), "cat-file",
     "--batch-all-objects", "--batch-check=%(objecttype) %(objectname)"],
    capture_output=True, env=env()).stdout.decode().split("\n")
    if l and not l.startswith("blob"))
pres_walk = [l for l in subprocess.run(
    ["git", "--no-lazy-fetch", "-C", str(part), "rev-list", "--objects",
     "--missing=print", "--stdin"], input=roots.encode(), capture_output=True,
    env=env()).stdout.decode().split("\n") if l.startswith("?")]
probes["E1-missing-set"] = {"z": z, "refs_walk": refs_walk,
                            "present_walk": pres_walk}
row("E1/full", full, fleet, 0, [])
row("E1/part", part, fleet, 2, None, twin="E1/full",
    note="z promised by unreachable promisor commit: refs-only ? walk "
         "misses it, so a refs-walk candidate would emit a false exit1")

# ---- C: git behaviour on missing required objects under --no-lazy-fetch
d = fresh("C-missing")
lane, fleet = init(d / "lane"), init(d / "fleet")
c1 = commit(lane, "kama-shokunin", 1000, "round-1: work")
c2 = commit(lane, "kama-shokunin", 1100, "round-1: more")
c3 = commit(lane, "fixture", 1200, "later")
publish(fleet, report([c1, c2]))
commit(fleet, "fleet", 3000, "later", "notes.md", b"n\n")


def promisorize(repo):
    g(repo, "config", "remote.origin.url", "file:///nonexistent")
    g(repo, "config", "remote.origin.promisor", "true")
    g(repo, "config", "extensions.partialclone", "origin")


def drop(repo, oid):
    p = Path(repo, ".git/objects", oid[:2], oid[2:])
    p.unlink()


# C1: lane with a missing required commit (c2), loose objects, promisor meta
lm = d / "lane-miss-commit"
shutil.copytree(lane, lm)
promisorize(lm)
drop(lm, c2)
probes["C1-lane-log-missing-required-commit"] = gi(
    lm, "log", "-z", "--format=%H%x00%an%x00%at%x00%s", "master")
row("C1/lane-missing-required-commit", lm, fleet, 2, None,
    note="required commit c2 unavailable")
# C2: fleet with missing tree of the report-adding commit (cutoff evidence)
fm = d / "fleet-miss-tree"
shutil.copytree(fleet, fm)
promisorize(fm)
add = g(fm, "log", "--diff-filter=A", "--format=%H", "--", REL)
t_add = g(fm, "rev-parse", f"{add}^{{tree}}")
t_ufo = g(fm, "rev-parse", f"{add}:.ufo")
drop(fm, t_ufo)
probes["C2-fleet-log-diff-filter-missing-subtree"] = gi(
    fm, "log", "--diff-filter=A", "--format=%at", "--", REL)
row("C2/fleet-missing-report-subtree", lane, fm, 2, None,
    note="tree of report-adding commit unavailable")
# C3: fleet report blob missing at HEAD
fb = d / "fleet-miss-blob"
shutil.copytree(fleet, fb)
promisorize(fb)
drop(fb, g(fb, "rev-parse", f"HEAD:{REL}"))
probes["C3-fleet-show-missing-report-blob"] = gi(fb, "show", f"HEAD:{REL}")
row("C3/fleet-missing-report-blob", lane, fb, 2, None)
# C4: lane missing a non-required later commit object (c3 tip) -> branch tip
lt = d / "lane-miss-tip"
shutil.copytree(lane, lt)
promisorize(lt)
drop(lt, c3)
row("C4/lane-missing-tip-commit", lt, fleet, 2, None,
    note="branch tip unavailable: history cannot be walked")
# C5: same missing commit WITHOUT promisor metadata (corruption, not promise)
lc5 = d / "lane-miss-commit-nometa"
shutil.copytree(lane, lc5)
drop(lc5, c2)
row("C5/lane-missing-commit-no-meta", lc5, fleet, 2, None)

# ---- D: errata correction lookup in a promisor repo
d = fresh("D-errata")
lane, fleet = init(d / "lane"), init(d / "fleet")
lc = commit(lane, "kama-shokunin", 1000, "round-1: work")
publish(fleet, report([lc]) + b"\n## Notes\n\nsee " + FAKE.encode() + b"\n")
commit(lane, "fixture", 1600, "errata", "registry/report-landing-errata.tsv",
       f"1\tunresolved-full-hash\t{FAKE}\t{'abcdef1' * 5}abcde\tev\n"
       .encode())
unh = clone(lane, d / "promisor-unhonored", filt="blob:none")
for name, repo in (("D1/full", lane), ("D1/promisor-complete", unh)):
    r = {"row": name, "want_exit": 1,
         "note": "errata correction absent locally: errata-invalid",
         "lane_meta": promisor_meta(repo), "lane_missing": missing_count(repo)}
    for arm in ARMS:
        p = subprocess.run([sys.executable, str(ARMS[arm]), "--lane-repo",
                            str(repo), "--fleet-repo", str(fleet), "--json",
                            "--rounds", "1"], capture_output=True, env=env())
        r[arm] = {"exit": p.returncode,
                  "stderr": p.stderr.decode(errors="replace")[-160:]}
    ROWS.append(r)

OUT.write_text(json.dumps({"git": g(SCRATCH, "--version"), "rows": ROWS,
                           "git_probes": probes}, indent=1) + "\n")
for r in ROWS:
    print(r["row"], "want", r["want_exit"], "| r22", r["r22"]["exit"],
          r["r22"].get("met", ""),
          "fetch" if r["r22"].get("lazy_fetch_attempted") else "nofetch",
          "| r23", r["r23"]["exit"], r["r23"].get("met", ""),
          "| miss", r.get("lane_missing"), r.get("fleet_missing", ""))
for k, v in probes.items():
    print(k, json.dumps(v)[-200:])
