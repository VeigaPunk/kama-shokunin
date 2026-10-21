#!/usr/bin/env python3
"""Bounded offline fixture: does the candidate's absence rule follow
(a) the CLOSURE twin-parity semantics (marked-complete == full clone) or
(b) prereg line 10's literal text (any missing citation in a promisor-backed
repo => exit2)?
And does an opaque hole in the FLEET change a LANE-side citation verdict?
"""
import json, os, shutil, subprocess, sys, tempfile
from pathlib import Path

CAND = "/fast/scratch/hyaku/kama-r24/ConnClosure/auditors/cand.py"
BASE = "/fast/scratch/hyaku/kama-r24"
REL = ".ufo/reports/round-1/kama.md"

def env(**e):
    d = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    d.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
             GIT_PROTOCOL_ALLOW="never",
             GIT_AUTHOR_NAME="kama-shokunin", GIT_AUTHOR_EMAIL="k@example.invalid",
             GIT_COMMITTER_NAME="kama-shokunin", GIT_COMMITTER_EMAIL="k@example.invalid",
             GIT_AUTHOR_DATE="@1000 +0000", GIT_COMMITTER_DATE="@1000 +0000", **e)
    return d

def g(r, *a, check=True):
    p = subprocess.run(["git", "-C", str(r), *a], capture_output=True, env=env(), timeout=60)
    if check and p.returncode != 0:
        raise RuntimeError(f"{a} rc={p.returncode} {p.stderr.decode()[:300]}")
    return p

def commit(r, author, when, msg, path="f", content=None):
    body = content if content is not None else msg + "\n"
    Path(r, path).parent.mkdir(parents=True, exist_ok=True)
    Path(r, path).write_text(body)
    g(r, "add", path)
    g(r, "-c", "commit.gpgsign=false", "commit", "-q", "-m", msg)
    return g(r, "rev-parse", "HEAD").stdout.decode().strip()

def publish(fleet, text, when=2000, path=REL):
    p = Path(fleet, path); p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text)
    g(fleet, "add", path)
    g(fleet, "-c", "commit.gpgsign=false", "commit", "-q", "-m", "round-1: kama report")

def run_auditor(lane, fleet):
    p = subprocess.run([sys.executable, CAND, "--lane-repo", str(lane),
                        "--fleet-repo", str(fleet), "--rounds", "1", "--json"],
                       capture_output=True, env=env(), timeout=120)
    out = p.stdout.decode(); err = p.stderr.decode()
    kinds = []
    if p.returncode in (0, 1):
        try:
            d = json.loads(out)
            for r in d["results"]:
                for df in r["defects"]:
                    kinds.append((df["kind"], df["token"][:12]))
        except Exception:
            pass
    return p.returncode, err.strip()[:220], kinds

def build(tmp, marked, fleet_hole=False):
    lane = Path(tmp, "lane"); lane.mkdir()
    g(lane, "init", "-q", "-b", "master")
    lc = commit(lane, "kama-shokunin", 1000, "round-1: work")
    fleet = Path(tmp, "fleet"); fleet.mkdir()
    g(fleet, "init", "-q", "-b", "master")
    seed = commit(fleet, "kama-shokunin", 500, "seed", "seed.md", "seed\n")
    fake = "abcdefabcdefabcdefabcdefabcdefabcdefabcd"
    publish(fleet, "# r1\n## Landed changes\n- `" + lc[:9] + "` work\n"
                      "## Notes\nsee " + fake + "\n")
    # errata registry (the auditor reads it from the lane tip)
    reg = Path(lane, "registry/report-landing-errata.tsv")
    reg.parent.mkdir(parents=True, exist_ok=True)
    reg.write_text("# round\tkind\ttoken\tcorrection\tevidence\n")
    g(lane, "add", "registry/report-landing-errata.tsv")
    g(lane, "-c", "commit.gpgsign=false", "commit", "-q", "-m", "round-1: registry")
    if marked:
        g(lane, "config", "core.repositoryformatversion", "1")
        g(lane, "config", "extensions.partialclone", "origin")
        g(lane, "config", "remote.origin.url", str(Path(tmp, "absent.git")))
        g(lane, "config", "remote.origin.promisor", "true")
    if fleet_hole:
        # delete the fleet's seed commit: an opaque hole (missing commit)
        p = Path(fleet, ".git/objects", seed[:2], seed[2:])
        if p.exists():
            p.unlink()
    return lane, fleet, fake

res = {}
tmp = Path(tempfile.mkdtemp(prefix="crosstest-", dir=BASE))
for label, marked, hole in (("plain_plain", False, False),
                            ("marked_plain", True, False),
                            ("plain_plain_fleethole", False, True),
                            ("marked_plain_fleethole", True, True)):
    t = Path(tempfile.mkdtemp(prefix=f"ct-{label}-", dir=BASE))
    lane, fleet, fake = build(t, marked, hole)
    rc, err, kinds = run_auditor(lane, fleet)
    res[label] = {"rc": rc, "stderr": err, "kinds": kinds}
    print(f"{label:26s} rc={rc} kinds={kinds} err={err[:120]}")
Path("crosstest-result.json").write_text(json.dumps(res, indent=2))
print("tmp:", tmp)
