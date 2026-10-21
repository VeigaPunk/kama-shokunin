#!/usr/bin/env python3
"""Two bounded offline shapes against the landed candidate auditor:

H-A  a citation names a blob that exists ONLY under a missing ancestor
     commit: the blob is absent locally AND absent from the missing set M
     (M is not transitively closed).  Correct answer: exit 2 (unknown).

H-B  the store has a missing commit that is UNRELATED to the citation
     (a different lineage), and the citation is a fabricated 40-hex.
     Names below the hole are unknown, so absence of the fabricated token
     cannot be proved either -> exit 2 is the safe answer; the question is
     whether the candidate reaches it, and whether it does so for the RIGHT
     reason (the hole) rather than a blanket refusal.
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
    out = p.stdout.decode(); err = p.stderr.decode().strip()
    kinds = []
    if p.returncode in (0, 1):
        try:
            d = json.loads(out)
            for r in d["results"]:
                for df in r["defects"]:
                    kinds.append((df["kind"], df["token"][:12]))
        except Exception:
            pass
    return p.returncode, err[:300], kinds

def loose(r, o):
    return Path(r, ".git/objects", o[:2], o[2:])

def missing_set(repo):
    p = subprocess.run(["git", "--no-lazy-fetch", "-C", str(repo), "rev-list",
                        "--objects", "--missing=print", "--no-object-names", "--all"],
                       capture_output=True, env=env(), timeout=60)
    return {l.strip()[1:] for l in p.stdout.decode().splitlines() if l.startswith("?")}

res = {}

# --- H-A ---
t = Path(tempfile.mkdtemp(prefix="holeA-", dir=BASE))
lane = t / "lane"; lane.mkdir(); g(lane, "init", "-q", "-b", "master")
c1 = commit(lane, "kama-shokunin", 1000, "round-1: work", "f", "work\n")
# unique blob: add a file, then remove it so its blob is reachable only via c1
commit(lane, "kama-shokunin", 1100, "round-1: add unique", "u.txt", "unique-payload\n")
ub = g(lane, "rev-parse", "HEAD:u.txt").stdout.decode().strip()
g(lane, "rm", "-q", "u.txt")
g(lane, "-c", "commit.gpgsign=false", "commit", "-q", "-m", "round-1: drop unique")
reg = lane / "registry/report-landing-errata.tsv"; reg.parent.mkdir(parents=True, exist_ok=True)
reg.write_text("# round\tkind\ttoken\tcorrection\tevidence\n")
g(lane, "add", "registry/report-landing-errata.tsv")
g(lane, "-c", "commit.gpgsign=false", "commit", "-q", "-m", "round-1: registry")
fleet = t / "fleet"; fleet.mkdir(); g(fleet, "init", "-q", "-b", "master")
commit(fleet, "kama-shokunin", 500, "seed", "seed.md", "seed\n")
publish(fleet, "# r1\n## Landed changes\n- `" + c1[:9] + "` work\n## Notes\nsee " + ub + "\n")
loose(lane, c1).unlink()      # the ancestor commit is gone
loose(lane, ub).unlink()      # the blob that lives ONLY under it
M = missing_set(lane)
rc, err, kinds = run_auditor(lane, fleet)
res["H_A_blob_hidden_behind_missing_commit"] = {
  "blob_absent_locally": not loose(lane, ub).exists(),
  "blob_in_missing_set": ub in M,
  "missing_set": sorted(M),
  "auditor_rc": rc, "stderr": err, "kinds": kinds,
  "M_is_not_closed": (ub not in M and not loose(lane, ub).exists()),
}

# --- H-B ---
t = Path(tempfile.mkdtemp(prefix="holeB-", dir=BASE))
lane = t / "lane"; lane.mkdir(); g(lane, "init", "-q", "-b", "master")
c1 = commit(lane, "kama-shokunin", 1000, "round-1: work", "f", "work\n")
other = commit(lane, "other-author", 900, "unrelated lineage", "g", "g\n")
reg = lane / "registry/report-landing-errata.tsv"; reg.parent.mkdir(parents=True, exist_ok=True)
reg.write_text("# round\tkind\ttoken\tcorrection\tevidence\n")
g(lane, "add", "registry/report-landing-errata.tsv")
g(lane, "-c", "commit.gpgsign=false", "commit", "-q", "-m", "round-1: registry")
fleet = t / "fleet"; fleet.mkdir(); g(fleet, "init", "-q", "-b", "master")
commit(fleet, "kama-shokunin", 500, "seed", "seed.md", "seed\n")
fake = "abcdefabcdefabcdefabcdefabcdefabcdefabcd"
publish(fleet, "# r1\n## Landed changes\n- `" + c1[:9] + "` work\n## Notes\nsee " + fake + "\n")
loose(lane, other).unlink()    # an unrelated missing commit
M = missing_set(lane)
rc, err, kinds = run_auditor(lane, fleet)
res["H_B_unrelated_missing_commit_fabricated_citation"] = {
  "missing_set": sorted(M),
  "fabricated_in_missing_set": fake in M,
  "auditor_rc": rc, "stderr": err, "kinds": kinds,
}
Path("holetest-result.json").write_text(json.dumps(res, indent=2))
print(json.dumps(res, indent=2))
