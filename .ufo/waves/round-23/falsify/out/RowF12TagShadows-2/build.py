#!/usr/bin/env python3
"""Independent fixtures for the F12 ref-shadow channel. Does not import the grid."""
import json, os, shutil, subprocess, sys
from pathlib import Path

ROOT = Path("/tmp/f12-lab/fixtures")
FROZEN = "/tmp/f12-lab/frozen-audit.py"
CURRENT = "/tmp/kama-r23w2/RowF12TagShadows-2/tools/report-landing-audit.py"
REL = ".ufo/reports/round-1/kama.md"


def env(**extra):
    e = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    e.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
             GIT_AUTHOR_EMAIL="a@x", GIT_COMMITTER_EMAIL="a@x",
             GIT_AUTHOR_NAME="fixture", GIT_COMMITTER_NAME="fixture")
    e.update(extra)
    return e


def g(repo, *args, data=None, check=True, **extra):
    p = subprocess.run(["git", "-C", str(repo), *args], input=data,
                       capture_output=True, env=env(**extra))
    if check and p.returncode:
        raise RuntimeError(f"git {args}: {p.stderr.decode(errors='replace')}")
    return p.stdout.decode(errors="surrogateescape").strip()


def init(path, fmt=None):
    path.mkdir(parents=True)
    args = ["init", "-q", "-b", "master"] + ([f"--object-format={fmt}"] if fmt else [])
    g(path, *args)
    return path


def commit(repo, who, when, msg, path="f", content=None):
    target = Path(repo, path)
    target.parent.mkdir(parents=True, exist_ok=True)
    if content is None:
        with open(target, "ab") as fh:
            fh.write((msg + "\n").encode())
    else:
        target.write_bytes(content)
    g(repo, "add", "--", path)
    stamp = f"@{when} +0000"
    g(repo, "-c", "commit.gpgsign=false", "commit", "-q", "-m", msg,
      GIT_AUTHOR_NAME=who, GIT_COMMITTER_NAME=who,
      GIT_AUTHOR_DATE=stamp, GIT_COMMITTER_DATE=stamp)
    return g(repo, "rev-parse", "HEAD")


def report_bytes(cited, extra=b""):
    return (b"# kama round 1\n\n## Landed changes\n\n- " + cited.encode() + b"\n" + extra)


def base(root, tag=None, more_subject="round-1: more", extra_uncited=True):
    lane = init(root / "lane")
    fleet = init(root / "fleet")
    lc = commit(lane, "kama-shokunin", 1000, "round-1: work")
    more = commit(lane, "kama-shokunin", 1500, more_subject) if extra_uncited else None
    commit(fleet, "fleet", 2000, "round-1: report", REL, report_bytes(lc))
    if tag:
        g(lane, "tag", *tag, lc)
    return lane, fleet, lc, more


def run(label, lane, fleet, branch="master", rounds="1"):
    out = {"label": label, "auditor": {}, "state": {}}
    for name, path in (("frozen", FROZEN), ("current", CURRENT)):
        p = subprocess.run([sys.executable, path, "--lane-repo", str(lane),
                            "--fleet-repo", str(fleet), "--branch", branch,
                            "--rounds", rounds, "--no-errata", "--json"],
                           capture_output=True, env=env(), timeout=30)
        rec = {"exit": p.returncode,
               "stdout": p.stdout.decode(errors="replace"),
               "stderr": p.stderr.decode(errors="replace")[:400],
               "traceback": b"Traceback (most recent call last)" in p.stderr}
        try:
            doc = json.loads(p.stdout)
            rec["kinds"] = sorted({d["kind"] for r in doc["results"] for d in r["defects"]})
            rec["round_commits"] = [r["round_commits"] for r in doc["results"]]
            rec["tokens"] = sorted({d.get("token", "")[:12] for r in doc["results"] for d in r["defects"]})
        except Exception:
            rec["kinds"] = None
        out["auditor"][name] = rec
    out["state"]["rev-parse-master"] = g(lane, "rev-parse", "--verify", "master^{commit}", check=False)
    out["state"]["refs"] = g(lane, "for-each-ref", "--format=%(refname) %(objectname:short)", check=False).split("\n")
    return out


def main():
    if ROOT.exists():
        shutil.rmtree(ROOT)
    ROOT.mkdir(parents=True)
    results = []

    # V0 control: same history, no tag -> the baseline truthful verdict.
    lane, fleet, lc, more = base(ROOT / "V0")
    results.append(run("V0-control-no-tag", lane, fleet))

    # V1 exact F12: tag master -> older cited commit, branch tip newer.
    lane, fleet, lc, more = base(ROOT / "V1", tag=("master",))
    results.append(run("V1-F12-tag-shadows-branch", lane, fleet))

    # V2 mirror: branch clean, tag master -> an orphan commit carrying an
    # uncited round-1 commit.  A flip of the other sign.
    lane = init(ROOT / "V2lane")
    fleet = init(ROOT / "V2fleet")
    lc = commit(lane, "kama-shokunin", 1000, "round-1: work")
    commit(fleet, "fleet", 2000, "round-1: report", REL, report_bytes(lc))
    # orphan commit: parentless raw commit with a round-1 subject
    tree = g(lane, "rev-parse", f"{lc}^{{tree}}")
    body = (f"tree {tree}\nauthor kama-shokunin <a@x> 1500 +0000\n"
            f"committer kama-shokunin <a@x> 1500 +0000\n\nround-1: orphan\n").encode()
    orphan = g(lane, "hash-object", "-t", "commit", "-w", "--stdin", data=body)
    g(lane, "tag", "master", orphan)
    results.append(run("V2-clean-branch-tag-newer", lane, fleet))

    # V3 branch named master gone, same-named tag remains.  No branch exists
    # for --branch master, yet the audit proceeds.
    lane, fleet, lc, more = base(ROOT / "V3", tag=("master",))
    g(lane, "branch", "-m", "master", "main")
    results.append(run("V3-no-branch-only-tag", lane, fleet))

    # V4 refs/heads/master kept as a dangling symref, tag master exists.
    lane, fleet, lc, more = base(ROOT / "V4", tag=("master",))
    g(lane, "branch", "-m", "master", "main")
    g(lane, "symbolic-ref", "refs/heads/master", "refs/heads/gone")
    results.append(run("V4-dangling-branch-symref", lane, fleet))

    # V5 explicit --branch release, only a tag release exists.
    lane, fleet, lc, more = base(ROOT / "V5", tag=("release",))
    g(lane, "branch", "-m", "master", "main")
    results.append(run("V5-explicit-branch-only-tag", lane, fleet, branch="release"))

    # V6 annotated tag named master.
    lane, fleet, lc, more = base(ROOT / "V6")
    g(lane, "tag", "-a", "-m", "shadow", "master", lc)
    results.append(run("V6-annotated-tag-master", lane, fleet))

    # V7 tag master points at a blob (unpeelable).
    lane, fleet, lc, more = base(ROOT / "V7", extra_uncited=False)
    blob = g(lane, "rev-parse", f"{lc}:f")
    g(lane, "tag", "master", blob)
    results.append(run("V7-tag-master-blob", lane, fleet))

    # V8 tag master = branch tip (no shadow effect at all).
    lane, fleet, lc, more = base(ROOT / "V8")
    tip = g(lane, "rev-parse", "master")
    g(lane, "tag", "master", tip)
    results.append(run("V8-tag-at-branch-tip", lane, fleet))

    print(json.dumps(results, indent=1))
    for r in results:
        a = r["auditor"]
        print(f"\n{r['label']}: rev-parse master={r['state']['rev-parse-master'][:12]}")
        for arm in ("frozen", "current"):
            x = a[arm]
            print(f"  {arm:7s} exit={x['exit']} kinds={x['kinds']} "
                  f"ncommits={x.get('round_commits')} tb={x['traceback']} "
                  f"err={x['stderr'].splitlines()[-1][:150] if x['stderr'].strip() else ''}")


if __name__ == "__main__":
    main()
