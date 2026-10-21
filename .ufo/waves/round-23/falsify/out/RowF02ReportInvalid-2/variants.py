#!/usr/bin/env python3
"""Near variants of the F02 report-bytes channel, checked against the
committed (current) auditor and the frozen blob."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile

FROZEN = Path("/tmp/kama-r23w2/frozen-audit.py")
CURRENT = Path("/tmp/kama-r23w2/RowF02ReportInvalid-2/tools/report-landing-audit.py")
REL = ".ufo/reports/round-1/kama.md"


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


def body(cites, head=b"# kama round 1\n\n## Landed changes\n\n", tail=b""):
    return head + b"".join(b"- " + c.encode() + b"\n" for c in cites) + tail


def base(root):
    lane, fleet = Path(root, "lane"), Path(root, "fleet")
    init(lane)
    init(fleet)
    lc = commit(lane, "kama-shokunin", 1000, "round-1: work")
    return lane, fleet, lc


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
        import json
        try:
            doc = json.loads(p.stdout)
            kinds = sorted({d["kind"] for r in doc["results"]
                            for d in r["defects"]})
        except Exception as exc:
            kinds = f"UNPARSEABLE {exc}"
    print(f"== {label}: exit={p.returncode} tb={tb} kinds={kinds}")
    err = p.stderr.decode(errors="replace").strip()
    print("   stderr:", (err[-300:] or "<empty>").replace("\n", " | "))
    return p.returncode, tb, kinds, p.stdout, p.stderr


def main():
    root = Path(tempfile.mkdtemp(prefix="f02-var-", dir="/tmp/kama-r23w2/f02"))
    print(f"# root {root}")

    # V2: draft override with invalid UTF-8 (no grid row)
    d = Path(root, "v2"); d.mkdir()
    lane, fleet, lc = base(d)
    commit(fleet, "fleet", 2000, "round-1: report", REL, body([lc]))
    draft = Path(d, "draft.md")
    draft.write_bytes(body([lc]) + b"\xff\xfe bad\n")
    run("V2 draft-bad-bytes/frozen", FROZEN, lane, fleet, ["--report", f"1={draft}"])
    run("V2 draft-bad-bytes/current", CURRENT, lane, fleet, ["--report", f"1={draft}"])

    # V3: lane SOURCES.md with invalid UTF-8 (no grid row)
    d = Path(root, "v3"); d.mkdir()
    lane, fleet, lc = base(d)
    commit(lane, "fixture", 1100, "sources", "corpus/SOURCES.md",
           b"## Registry\n\n| S001 | caf\xe9 |\n")
    commit(fleet, "fleet", 2000, "round-1: report", REL, body([lc]))
    run("V3 sources-bad-bytes/frozen", FROZEN, lane, fleet)
    run("V3 sources-bad-bytes/current", CURRENT, lane, fleet)

    # V4: UTF-8 BOM immediately before a first-line Landed section
    d = Path(root, "v4"); d.mkdir()
    lane, fleet, lc = base(d)
    commit(fleet, "fleet", 2000, "round-1: report", REL,
           b"\xef\xbb\xbf" + body([lc], head=b"## Landed changes\n\n"))
    run("V4 bom-firstline-clean/current", CURRENT, lane, fleet)
    run("V4 bom-firstline-clean/frozen", FROZEN, lane, fleet)
    # control: same report with no BOM
    d = Path(root, "v4c"); d.mkdir()
    lane, fleet, lc = base(d)
    commit(fleet, "fleet", 2000, "round-1: report", REL,
           body([lc], head=b"## Landed changes\n\n"))
    run("V4c no-bom-firstline/current", CURRENT, lane, fleet)

    # V5: NUL byte in a committed report (valid UTF-8, not decodable text)
    d = Path(root, "v5"); d.mkdir()
    lane, fleet, lc = base(d)
    commit(fleet, "fleet", 2000, "round-1: report", REL,
           body([lc], tail=b"\x00\x00\n"))
    run("V5 nul-tail/current", CURRENT, lane, fleet)
    # V5b: NUL inside the Landed section between cited lines
    d = Path(root, "v5b"); d.mkdir()
    lane, fleet, lc = base(d)
    commit(fleet, "fleet", 2000, "round-1: report", REL,
           body([], head=b"# kama round 1\n\n## Landed changes\n\n- ", tail=b"\x00" + lc.encode() + b"\n"))
    run("V5b nul-inside-landed/current", CURRENT, lane, fleet)

    # V6: invalid UTF-8 in the middle of a Landed citation line
    d = Path(root, "v6"); d.mkdir()
    lane, fleet, lc = base(d)
    commit(fleet, "fleet", 2000, "round-1: report", REL,
           body([], head=b"# kama round 1\n\n## Landed changes\n\n- " + lc.encode() + b"\xff\n"))
    run("V6 bad-byte-on-cite-line/current", CURRENT, lane, fleet)

    # V7: UTF-16LE report with BOM
    d = Path(root, "v7"); d.mkdir()
    lane, fleet, lc = base(d)
    commit(fleet, "fleet", 2000, "round-1: report", REL,
           body([lc]).decode().encode("utf-16"))
    run("V7 utf16-report/current", CURRENT, lane, fleet)

    # V8: report committed as a symlink blob (git show returns link target)
    d = Path(root, "v8"); d.mkdir()
    lane, fleet, lc = base(d)
    link = Path(fleet, REL)
    link.parent.mkdir(parents=True)
    os.symlink("/tmp/kama-r23w2/v8-target-missing.md", link)
    g(fleet, "add", "--", REL)
    g(fleet, "-c", "commit.gpgsign=false", "commit", "-q", "-m",
      "round-1: report", GIT_AUTHOR_DATE="@2000 +0000",
      GIT_COMMITTER_DATE="@2000 +0000")
    print("# v8 tree:", g(fleet, "ls-tree", "HEAD", "--", REL))
    run("V8 symlink-report/current", CURRENT, lane, fleet)


if __name__ == "__main__":
    main()
