#!/usr/bin/env python3
"""CritFrozen bounded premise: r22 (4fe9339) vs r23 (0df800e) frozen auditors
on three local offline fixtures. No candidate, no suite. Fixtures live under
/fast/scratch/hyaku/kama-r24/CritFrozen."""
import json, os, subprocess, sys, tempfile
from pathlib import Path

LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
SCRATCH = Path("/fast/scratch/hyaku/kama-r24/CritFrozen")
REVS = {"r22": "4fe9339f8fc3a4a4a479d9c938a850da12f1124d",
        "r23": "0df800e896f6bce285a81e794ad4ae1d1e6c3a71"}
REL = ".ufo/reports/round-1/kama.md"


def env(**x):
    e = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    e.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
             GIT_AUTHOR_EMAIL="a@x", GIT_COMMITTER_EMAIL="a@x")
    e.update(x)
    return e


def g(repo, *a, data=None, lazy=False, **x):
    flag = [] if lazy else ["--no-lazy-fetch"]
    p = subprocess.run(["git", *flag, "-C", str(repo), *a],
                       input=data, capture_output=True, env=env(**x))
    if p.returncode:
        raise SystemExit(f"premise git {a}: {p.stderr.decode()}")
    return p.stdout.decode().strip()


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


def build(tmp, extra_lane_commit, no_checkout, cite_blob):
    lane, fleet = Path(tmp, "lane"), Path(tmp, "fleet")
    for r in (lane, fleet):
        g(tmp, "init", "-q", "-b", "master", str(r))
    lc = commit(lane, "kama-shokunin", 1000, "round-1: work")
    blob = g(lane, "rev-parse", f"{lc}:f")
    if extra_lane_commit:
        commit(lane, "someone", 1100, "note")
    text = b"# kama round 1\n\n## Landed changes\n\n- " + lc.encode() + b"\n"
    if cite_blob:
        text += b"\n## Notes\n\nblob " + blob.encode() + b"\n"
    commit(fleet, "fleet", 2000, "round-1: report", REL, text)
    g(lane, "config", "uploadpack.allowFilter", "true")
    clone = Path(tmp, "blobless")
    g(tmp, "-c", "protocol.file.allow=always", "clone", "-q",
      *(["--no-checkout"] if no_checkout else []),
      "--filter=blob:none", "--no-local", f"file://{lane}", str(clone),
      lazy=True)
    if cite_blob:  # F23 replica: config removed, pack marker kept
        for k in ("remote.origin.promisor", "remote.origin.partialclonefilter",
                  "extensions.partialclone"):
            subprocess.run(["git", "-C", str(clone), "config", "--unset", k],
                           capture_output=True, env=env())
    g(clone, "config", "remote.origin.url", str(Path(tmp, "absent-origin")))
    missing = g(clone, "rev-list", "--objects", "--missing=print",
                "--no-object-names", "HEAD").split("\n")
    missing = [m for m in missing if m.startswith("?")]
    return lane, clone, fleet, missing


def audit(rev, auditor, lane, fleet):
    p = subprocess.run([sys.executable, str(auditor), "--lane-repo", str(lane),
                        "--fleet-repo", str(fleet), "--rounds", "1",
                        "--no-errata", "--json"], capture_output=True,
                       env=env(), timeout=60, cwd=lane.parent)
    kinds = None
    if p.returncode in (0, 1):
        doc = json.loads(p.stdout)
        kinds = sorted({d["kind"] for r in doc["results"] for d in r["defects"]})
    return {"exit": p.returncode, "kinds": kinds,
            "stderr": p.stderr.decode(errors="replace").strip()[-160:]}


def main():
    SCRATCH.mkdir(parents=True, exist_ok=True)
    out = {}
    with tempfile.TemporaryDirectory(dir=SCRATCH) as root:
        auditors = {}
        for name, rev in REVS.items():
            p = subprocess.run(["git", "-C", LANE, "cat-file", "blob",
                                f"{rev}:tools/report-landing-audit.py"],
                               capture_output=True, check=True)
            auditors[name] = Path(root, f"{name}.py")
            auditors[name].write_bytes(p.stdout)
        cases = {
            "T01-replica-complete": (False, False, False),
            "T01-deep-history-blob-missing": (True, False, False),
            "F23-replica": (False, True, True),
        }
        for case, (deep, nochk, blob) in cases.items():
            tmp = Path(root, case)
            tmp.mkdir()
            lane, clone, fleet, missing = build(tmp, deep, nochk, blob)
            assert str(clone).startswith(str(SCRATCH))
            row = {"missing_objects": len(missing),
                   "full_lane": {}, "promisor_clone": {}}
            for name, a in auditors.items():
                row["full_lane"][name] = audit(name, a, lane, fleet)
                row["promisor_clone"][name] = audit(name, a, clone, fleet)
            out[case] = row
    print(json.dumps(out, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
