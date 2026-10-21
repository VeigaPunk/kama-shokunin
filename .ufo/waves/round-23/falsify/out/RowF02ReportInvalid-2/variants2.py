#!/usr/bin/env python3
"""BOM / draft / whole-file encoding variants against the F02 channel."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

FROZEN = Path("/tmp/kama-r23w2/frozen-audit.py")
CURRENT = Path("/tmp/kama-r23w2/RowF02ReportInvalid-2/tools/report-landing-audit.py")
REL = ".ufo/reports/round-1/kama.md"
BOM = b"\xef\xbb\xbf"


def genv(**extra):
    e = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    e.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
             GIT_AUTHOR_EMAIL="a@x", GIT_COMMITTER_EMAIL="a@x",
             GIT_AUTHOR_NAME="fixture", GIT_COMMITTER_NAME="fixture")
    e.update(extra)
    return e


def g(repo, *args, data=None, check=True, **extra):
    p = subprocess.run(["git", "-C", str(repo), *args], input=data,
                       capture_output=True, env=genv(**extra))
    if check and p.returncode:
        raise SystemExit(f"git {' '.join(args)}: rc={p.returncode} "
                         f"{p.stderr.decode(errors='replace')}")
    return p.stdout.decode(errors="surrogateescape").strip()


def init(path):
    g(path.parent, "init", "-q", "-b", "master", str(path))
    return path


def commit(repo, author, when, msg, path="f", content=None):
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
      GIT_AUTHOR_NAME=author, GIT_COMMITTER_NAME=author,
      GIT_AUTHOR_DATE=stamp, GIT_COMMITTER_DATE=stamp)
    return g(repo, "rev-parse", "HEAD")


def run(label, auditor, lane, fleet, extra=(), json_mode=True):
    argv = [sys.executable, str(auditor), "--lane-repo", str(lane),
            "--fleet-repo", str(fleet)]
    if json_mode:
        argv.append("--json")
    argv += ["--rounds", "1", "--no-errata", *extra]
    p = subprocess.run(argv, capture_output=True, timeout=30, env=genv(),
                       cwd=str(Path(lane).parent))
    tb = b"Traceback (most recent call last)" in p.stderr
    kinds = ""
    if p.returncode in (0, 1) and p.stdout:
        try:
            doc = json.loads(p.stdout)
            kinds = sorted({d["kind"] for r in doc["results"]
                            for d in r["defects"]})
        except Exception as exc:
            kinds = f"UNPARSEABLE {exc}"
    print(f"== {label}: exit={p.returncode} tb={tb} kinds={kinds}")
    err = p.stderr.decode(errors="replace").strip()
    print("   stderr:", (err[-260:] or "<empty>").replace("\n", " | "))
    return p.returncode


def base(root):
    lane, fleet = Path(root, "lane"), Path(root, "fleet")
    init(lane)
    init(fleet)
    lc = commit(lane, "kama-shokunin", 1000, "round-1: work")
    return lane, fleet, lc


def flat(cites):
    return b"## Landed changes\n\n" + b"".join(
        b"- " + c.encode() + b"\n" for c in cites)


def main():
    root = Path(tempfile.mkdtemp(prefix="f02-bom-", dir="/tmp/kama-r23w2/f02"))
    print(f"# root {root}")

    # V9/V10: draft (--report) whose first line is the Landed heading,
    # with and without a UTF-8 BOM, exactly the selftest draft shape.
    for tag, blob in (("v9-bom-draft", BOM + flat([])),
                      ("v10-plain-draft", flat([]))):
        d = Path(root, tag); d.mkdir()
        lane, fleet, lc = base(d)
        # fleet HEAD exists but holds no round-1 report: cutoff = now
        commit(fleet, "fleet", 1500, "other", "README.md", b"x\n")
        draft = Path(d, "draft.md")
        draft.write_bytes(b"## Landed changes\n\n- " + lc.encode() + b"\n")
        if tag.startswith("v9"):
            draft.write_bytes(BOM + draft.read_bytes())
        run(f"{tag}/current", CURRENT, lane, fleet, ["--report", f"1={draft}"])
        run(f"{tag}/frozen", FROZEN, lane, fleet, ["--report", f"1={draft}"])

    # V11: committed report, title line then BOM directly before heading
    d = Path(root, "v11"); d.mkdir()
    lane, fleet, lc = base(d)
    commit(fleet, "fleet", 2000, "round-1: report", REL,
           b"# kama round 1\n\n" + BOM + flat([lc]))
    run("v11-bom-before-heading/current", CURRENT, lane, fleet)
    run("v11-bom-before-heading/frozen", FROZEN, lane, fleet)

    # V11c control: identical bytes, no BOM
    d = Path(root, "v11c"); d.mkdir()
    lane, fleet, lc = base(d)
    commit(fleet, "fleet", 2000, "round-1: report", REL,
           b"# kama round 1\n\n" + flat([lc]))
    run("v11c-no-bom-control/current", CURRENT, lane, fleet)

    # V12: invalid UTF-8 only in the title line, Landed clean
    d = Path(root, "v12"); d.mkdir()
    lane, fleet, lc = base(d)
    commit(fleet, "fleet", 2000, "round-1: report", REL,
           b"# kama round 1 \xff\n\n" + flat([lc]))
    run("v12-bad-title/current", CURRENT, lane, fleet)

    # V13: bad bytes after a later section, Landed clean
    d = Path(root, "v13"); d.mkdir()
    lane, fleet, lc = base(d)
    commit(fleet, "fleet", 2000, "round-1: report", REL,
           flat([lc]) + b"\n## Notes\n\nlatin-1 \xe9 byte\n")
    run("v13-bad-after-notes/current", CURRENT, lane, fleet)

    # V14: committed corrupt report but a clean draft override is audited
    d = Path(root, "v14"); d.mkdir()
    lane, fleet, lc = base(d)
    commit(fleet, "fleet", 2000, "round-1: report", REL,
           flat([lc]) + b"\xff\n")
    draft = Path(d, "draft.md")
    draft.write_bytes(flat([lc]))
    run("v14-draft-overrides-corrupt-commit/current", CURRENT, lane, fleet,
        ["--report", f"1={draft}"])

    # V15: report blob is a symlink whose target bytes are valid text
    d = Path(root, "v15"); d.mkdir()
    lane, fleet, lc = base(d)
    link = Path(fleet, REL)
    link.parent.mkdir(parents=True)
    os.symlink("../../../../somewhere/else.md", link)
    g(fleet, "add", "--", REL)
    g(fleet, "-c", "commit.gpgsign=false", "commit", "-q", "-m",
      "round-1: report", GIT_AUTHOR_DATE="@2000 +0000",
      GIT_COMMITTER_DATE="@2000 +0000")
    print("# v15 tree:", g(fleet, "ls-tree", "HEAD", "--", REL))
    run("v15-symlink-report/current", CURRENT, lane, fleet)


if __name__ == "__main__":
    main()
