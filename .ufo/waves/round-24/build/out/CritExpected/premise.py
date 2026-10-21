#!/usr/bin/env python3
"""CritExpected bounded premise probe (offline, local file:// only).

Builds four synthetic fixtures under $SCRATCH and records, per fixture:
object closure via `git --no-lazy-fetch rev-list --objects --missing=print`,
presence of every object the base auditor actually reads, promisor signals,
and the base (0df800e8) auditor exit/reason. No network transport, no
configured programs, no candidate auditor. Every fixture root is checked
before any .git write.
"""
import json, os, subprocess, sys, tempfile
from pathlib import Path

LANE_DIR = Path("/home/vgpnk/Projects/shokunin/kama-shokunin")
BASE = "0df800e896f6bce285a81e794ad4ae1d1e6c3a71"
SCRATCH = Path("/fast/scratch/hyaku/kama-r24/CritExpected")
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
    p = subprocess.run(["git", "--no-lazy-fetch", "-C", str(repo), *args],
                       input=data, capture_output=True, env=env(**extra),
                       timeout=20)
    if check and p.returncode:
        raise SystemExit(f"premise: git {args}: {p.stderr.decode().strip()}")
    return p.stdout.decode(errors="surrogateescape").strip()


def assert_root(repo):
    top = g(repo, "rev-parse", "--show-toplevel")
    if Path(top).resolve() != Path(repo).resolve() or SCRATCH not in Path(top).resolve().parents:
        raise SystemExit(f"premise: fixture root escaped: {top}")


def init(path):
    path.mkdir(parents=True)
    subprocess.run(["git", "init", "-q", "-b", "master", str(path)], check=True,
                   env=env(), capture_output=True)
    assert_root(path)
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


def blobless(tmp, src, checkout=True):
    assert_root(src)
    g(src, "config", "uploadpack.allowFilter", "true")
    dst = Path(tmp, "blobless")
    args = ["-c", "protocol.file.allow=always", "clone", "-q",
            "--filter=blob:none", "--no-local"]
    if not checkout:
        args.append("--no-checkout")
    subprocess.run(["git", *args, f"file://{src}", str(dst)], check=True,
                   env=env(), capture_output=True, timeout=20)
    assert_root(dst)
    return dst


def closure(repo):
    out = g(repo, "rev-list", "--objects", "--missing=print",
            "--no-object-names", "--all")
    return sorted(l[1:] for l in out.splitlines() if l.startswith("?"))


def promisor_signals(repo):
    cfg = g(repo, "config", "--list", check=False).splitlines()
    keys = [l for l in cfg if l.startswith(("extensions.partialclone",
            "remote.origin.promisor", "remote.origin.partialclonefilter"))]
    pack = Path(g(repo, "rev-parse", "--git-path", "objects/pack"))
    pack = pack if pack.is_absolute() else Path(repo, pack)
    paired = sorted(p.name for p in pack.glob("*.promisor")
                    if p.with_suffix(".pack").exists()) if pack.is_dir() else []
    return {"config": keys, "paired_markers": paired}


def audit_read_missing(lane, fleet):
    """Objects the base auditor reads: lane commits (log), lane tip
    SOURCES/errata entries, fleet commits+trees on REL path, fleet HEAD
    report blob. Returns those absent locally."""
    need = set(g(lane, "rev-list", "HEAD").split())
    for path in ("corpus/SOURCES.md", "registry/report-landing-errata.tsv"):
        e = g(lane, "ls-tree", "HEAD", "--", path)
        if e:
            need.add(e.split()[2])
    need |= set(g(fleet, "rev-list", "HEAD").split())
    e = g(fleet, "ls-tree", "HEAD", "--", REL)
    if e:
        need.add(e.split()[2])
    # trees along REL in every fleet commit
    for c in g(fleet, "rev-list", "HEAD").split():
        need.add(g(fleet, "rev-parse", f"{c}^{{tree}}"))
    missing = []
    for o in sorted(need):
        r1 = subprocess.run(["git", "--no-lazy-fetch", "-C", str(lane),
                             "cat-file", "-e", o], env=env(), capture_output=True)
        r2 = subprocess.run(["git", "--no-lazy-fetch", "-C", str(fleet),
                             "cat-file", "-e", o], env=env(), capture_output=True)
        if r1.returncode and r2.returncode:
            missing.append(o)
    return missing


def run_base(auditor, lane, fleet):
    p = subprocess.run([sys.executable, str(auditor), "--lane-repo", str(lane),
                        "--fleet-repo", str(fleet), "--rounds", "1",
                        "--no-errata", "--json"], capture_output=True,
                       env=env(), timeout=60)
    kinds = None
    if p.returncode in (0, 1):
        d = json.loads(p.stdout)
        kinds = sorted({x["kind"] for r in d["results"] for x in r["defects"]})
    return {"exit": p.returncode, "kinds": kinds,
            "stderr": p.stderr.decode(errors="replace").strip()[-160:]}


# ---------------------------------------------------------------- fixtures

def t01_as_r23(tmp):
    """r23 T01 verbatim: one-commit lane, blob:none clone with checkout."""
    lane, fleet = init(Path(tmp, "lane")), init(Path(tmp, "fleet"))
    lc = commit(lane, "kama-shokunin", 1000, "round-1: work")
    commit(fleet, "fleet", 2000, "round-1: report", REL, report([lc]))
    return blobless(tmp, lane), fleet, {"full_lane": lane}


def two_commit_blobless_clean(tmp):
    """Counterexample: two cited lane commits; checkout hydrates tip blob
    only, so the first commit's blob is absent but never read by the audit."""
    lane, fleet = init(Path(tmp, "lane")), init(Path(tmp, "fleet"))
    a = commit(lane, "kama-shokunin", 1000, "round-1: work")
    b = commit(lane, "kama-shokunin", 1100, "round-1: more")
    commit(fleet, "fleet", 2000, "round-1: report", REL, report([a, b]))
    return blobless(tmp, lane), fleet, {"full_lane": lane}


def two_commit_blobless_omission(tmp):
    """Same clone; the second round commit is not cited (genuine omission)."""
    lane, fleet = init(Path(tmp, "lane")), init(Path(tmp, "fleet"))
    a = commit(lane, "kama-shokunin", 1000, "round-1: work")
    commit(lane, "kama-shokunin", 1100, "round-1: more")
    commit(fleet, "fleet", 2000, "round-1: report", REL, report([a]))
    return blobless(tmp, lane), fleet, {"full_lane": lane}


def f23_no_blob_citation(tmp):
    """r23 F23 shape (no-checkout, promisor config removed, paired marker
    kept) but the report does NOT cite the absent blob."""
    lane, fleet = init(Path(tmp, "lane")), init(Path(tmp, "fleet"))
    lc = commit(lane, "kama-shokunin", 1000, "round-1: work")
    commit(fleet, "fleet", 2000, "round-1: report", REL, report([lc]))
    clone = blobless(tmp, lane, checkout=False)
    for k in ("remote.origin.promisor", "remote.origin.partialclonefilter",
              "extensions.partialclone"):
        g(clone, "config", "--unset", k, check=False)
    return clone, fleet, {"full_lane": lane}


def f27_filter_only(tmp):
    """r23 F27 minus the configured program: filter-only promisor config on
    a complete lane; report cites a fabricated full hash."""
    lane, fleet = init(Path(tmp, "lane")), init(Path(tmp, "fleet"))
    lc = commit(lane, "kama-shokunin", 1000, "round-1: work")
    commit(fleet, "fleet", 2000, "round-1: report", REL,
           report([lc]) + b"\n## Notes\n\nsee " + FAKE.encode() + b"\n")
    full = Path(tmp, "full-copy")
    subprocess.run(["git", "clone", "-q", "--no-local", str(lane), str(full)],
                   check=True, env=env(), capture_output=True)
    assert_root(lane)
    g(lane, "config", "remote.origin.url", str(Path(tmp, "absent.git")))
    g(lane, "config", "remote.origin.partialclonefilter", "blob:none")
    return lane, fleet, {"full_lane": full}


def unhydrated_two_files(tmp):
    """CaseHydratedLane 'unhydrated/clean' shape: commits a (adds f) and b
    (adds g), blob:none --no-checkout lane clone; both blobs absent, every
    commit present, no SOURCES/errata in the lane."""
    lane, fleet = init(Path(tmp, "lane")), init(Path(tmp, "fleet"))
    a = commit(lane, "kama-shokunin", 1000, "round-1: work", "f")
    b = commit(lane, "kama-shokunin", 1500, "round-1: extra", "g")
    commit(fleet, "fleet", 2000, "round-1: report", REL, report([a, b]))
    return blobless(tmp, lane, checkout=False), fleet, {"full_lane": lane}


FIXTURES = [t01_as_r23, two_commit_blobless_clean, two_commit_blobless_omission,
            f23_no_blob_citation, f27_filter_only, unhydrated_two_files]
R22 = "4fe9339f8fc3a4a4a479d9c938a850da12f1124d"


def object_count(repo):
    return g(repo, "count-objects", "-v")


def main():
    SCRATCH.mkdir(parents=True, exist_ok=True)
    rows = []
    with tempfile.TemporaryDirectory(prefix="premise-", dir=SCRATCH) as root:
        auditors = {}
        for name, rev in (("r23_base", BASE), ("r22_frozen", R22)):
            auditors[name] = Path(root, f"{name}.py")
            auditors[name].write_bytes(subprocess.run(
                ["git", "-C", str(LANE_DIR), "cat-file", "blob",
                 f"{rev}:tools/report-landing-audit.py"], check=True,
                capture_output=True, env=env()).stdout)
        for fx in FIXTURES:
            tmp = Path(root, fx.__name__)
            tmp.mkdir()
            lane, fleet, extra = fx(tmp)
            # r22 has no --no-lazy-fetch: block every transport offline so a
            # lazy fetch attempt fails locally instead of contacting origin
            for repo in (lane, fleet, extra["full_lane"]):
                assert_root(repo)
                g(repo, "config", "protocol.allow", "never")
            before = object_count(lane)
            row = {
                "fixture": fx.__name__,
                "doc": fx.__doc__.split("\n")[0],
                "closure_missing": closure(lane),
                "audit_read_missing": audit_read_missing(lane, fleet),
                "promisor": promisor_signals(lane),
            }
            for name, auditor in auditors.items():
                row[f"{name}_on_marked"] = run_base(auditor, lane, fleet)
                row[f"{name}_on_full"] = run_base(auditor, extra["full_lane"],
                                                  fleet)
            row["lane_objects_unchanged"] = object_count(lane) == before
            rows.append(row)
    print(json.dumps({"git": subprocess.run(["git", "--version"],
                      capture_output=True, text=True).stdout.strip(),
                      "base": BASE, "rows": rows}, indent=1))


if __name__ == "__main__":
    main()
