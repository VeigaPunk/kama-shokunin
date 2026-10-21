#!/usr/bin/env python3
"""Residual variants of the ref-name fallback in resolve_branch."""
import json, shutil, subprocess, sys
from pathlib import Path
sys.path.insert(0, "/tmp/f12-lab")
import build as B

ROOT = Path("/tmp/f12-lab/fixtures2")
CURRENT = B.CURRENT


def run(label, lane, fleet, branch="master", arms=("frozen", "current")):
    rec = {"label": label, "auditor": {}, "state": {}}
    for name in arms:
        path = B.FROZEN if name == "frozen" else CURRENT
        p = subprocess.run([sys.executable, path, "--lane-repo", str(lane),
                            "--fleet-repo", str(fleet), "--branch", branch,
                            "--rounds", "1", "--no-errata", "--json"],
                           capture_output=True, env=B.env(), timeout=30)
        r = {"exit": p.returncode, "stderr": p.stderr.decode(errors="replace")[:300],
             "traceback": b"Traceback (most recent call last)" in p.stderr}
        try:
            doc = json.loads(p.stdout)
            r["kinds"] = sorted({d["kind"] for x in doc["results"] for d in x["defects"]})
            r["n"] = [x["round_commits"] for x in doc["results"]]
            r["required"] = [x["required"] for x in doc["results"]]
        except Exception:
            r["kinds"] = None
        rec["auditor"][name] = r
    for probe in (["rev-parse", "--verify", f"refs/heads/{branch}^{{commit}}"],
                  ["rev-parse", "--verify", f"{branch}^{{commit}}"]):
        p = subprocess.run(["git", "-C", str(lane), *probe], capture_output=True, env=B.env())
        rec["state"][" ".join(probe[2:])] = (p.returncode,
                                             p.stdout.decode().strip()[:12],
                                             p.stderr.decode().strip()[:80])
    return rec


def main():
    if ROOT.exists():
        shutil.rmtree(ROOT)
    ROOT.mkdir(parents=True)
    out = []

    # V9 broken branch + tag pointing at a history with an UNCITED round commit:
    # does the fallback manufacture a defect from a ref the branch is not?
    lane, fleet, lc, more = B.base(ROOT / "V9", extra_uncited=False)
    tree = B.g(lane, "rev-parse", f"{lc}^{{tree}}")
    body = (f"tree {tree}\nauthor kama-shokunin <a@x> 1500 +0000\n"
            f"committer kama-shokunin <a@x> 1500 +0000\n\nround-1: orphan\n").encode()
    orphan = B.g(lane, "hash-object", "-t", "commit", "-w", "--stdin", data=body)
    B.g(lane, "tag", "master", orphan)
    B.g(lane, "symbolic-ref", "refs/heads/master", "refs/heads/gone")
    out.append(run("V9-dangling-branch-orphan-tag", lane, fleet))

    # V10 branch ref points at a tree; same-named tag at the cited commit.
    lane, fleet, lc, more = B.base(ROOT / "V10", tag=("master",))
    tree = B.g(lane, "rev-parse", f"{lc}^{{tree}}")
    Path(lane, ".git/refs/heads/master").write_text(tree + "\n")
    out.append(run("V10-branch-ref-tree-tag", lane, fleet))

    # V11 branch ref names a missing object; same-named tag at cited commit.
    lane, fleet, lc, more = B.base(ROOT / "V11", tag=("master",))
    Path(lane, ".git/refs/heads/master").write_text("0" * 40 + "\n")
    out.append(run("V11-branch-ref-missing-object", lane, fleet))

    # V12 exact F12 but with all refs packed.
    lane, fleet, lc, more = B.base(ROOT / "V12", tag=("master",))
    B.g(lane, "pack-refs", "--all")
    out.append(run("V12-F12-packed-refs", lane, fleet))

    # V13 no local branch, refs/remotes/master present (unqualified fallback order).
    lane, fleet, lc, more = B.base(ROOT / "V13", extra_uncited=False)
    B.g(lane, "branch", "-m", "master", "main")
    B.g(lane, "update-ref", "refs/remotes/master", lc)
    out.append(run("V13-no-branch-remote-ref", lane, fleet))

    # V14 control for V10/V11: broken branch with NO tag -> refusal.
    lane, fleet, lc, more = B.base(ROOT / "V14", extra_uncited=False)
    tree = B.g(lane, "rev-parse", f"{lc}^{{tree}}")
    Path(lane, ".git/refs/heads/master").write_text(tree + "\n")
    out.append(run("V14-broken-branch-no-tag", lane, fleet))

    print(json.dumps(out, indent=1))
    for r in out:
        print(f"\n{r['label']}  {r['state']}")
        for arm in ("frozen", "current"):
            x = r["auditor"][arm]
            print(f"  {arm:7s} exit={x['exit']} kinds={x['kinds']} n={x.get('n')} "
                  f"tb={x['traceback']} err={x['stderr'].splitlines()[-1][:120] if x['stderr'].strip() else ''}")


if __name__ == "__main__":
    main()
