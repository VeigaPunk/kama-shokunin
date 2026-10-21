#!/usr/bin/env python3
"""Exception and framing fault battery for tools/report-landing-audit.py.

usage: probe-exceptions.py BASE_SCRIPT CURRENT_SCRIPT

BASE_SCRIPT is the frozen blob, e.g.
  git -C <lane> show 4fe9339f:tools/report-landing-audit.py > base.py
Every fixture is a fresh repo under a new temp directory with
GIT_CONFIG_GLOBAL=/dev/null and GIT_CONFIG_NOSYSTEM=1. The lane and fleet
repos are never read or written. One row per case per script:
  TRACEBACK = an uncaught exception escaped main() (Python exits 1, the same
              code as a `failed` verdict);
  rc=2      = could-not-evaluate (EvalError / OSError handled);
  rc=0/1    = clean / failed verdict.
"""
import hashlib
import os
import pathlib
import subprocess
import sys
import tempfile

BASE, CUR = sys.argv[1], sys.argv[2]
HOME = pathlib.Path(tempfile.mkdtemp(prefix="kama-r23-home-"))
ROOT = pathlib.Path(tempfile.mkdtemp(prefix="kama-r23-fx-"))
ENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
ENV.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1", HOME=str(HOME))
T0 = 1700000000
NONE = b"# Round 1\n\n## Landed changes\n- none\n"
ASCII_ENV = {"LC_ALL": "C", "PYTHONUTF8": "0", "PYTHONCOERCECLOCALE": "0"}
ERR_ROW = b"# h\n1\tlanded-unresolved\tdeadbee\tcaf\xc3\xa9\tev\n"
LATIN = [("normal", b"round-1: caf\xc3\xa9 work\n", b"kama-shokunin")]
BAD_CFG = (("i18n.logOutputEncoding", "ISO-8859-1"),)


def sh(cmd, input=None, env=None):
    return subprocess.run(cmd, capture_output=True, env=env or ENV, input=input)


def git(repo, *args, input=None):
    r = sh(["git", "-C", str(repo), *args], input=input)
    if r.returncode:
        raise RuntimeError(f"git {args[:2]} rc={r.returncode}: {r.stderr[:200]!r}")
    return r.stdout.decode().strip()


def ident(name_bytes, when):
    name = os.fsdecode(name_bytes)
    return dict(ENV, GIT_AUTHOR_NAME=name, GIT_AUTHOR_EMAIL="a@x.invalid", GIT_AUTHOR_DATE=when,
                GIT_COMMITTER_NAME=name, GIT_COMMITTER_EMAIL="a@x.invalid", GIT_COMMITTER_DATE=when)


def new_repo(path):
    path.mkdir(parents=True)
    git(path, "init", "-q", "-b", "master")
    return path


def put(repo, rel, data):
    blob = git(repo, "hash-object", "-w", "--stdin", input=data)
    git(repo, "update-index", "--add", "--cacheinfo", f"100644,{blob},{rel}")


def commit(repo, msg, author, when):
    """`git commit`: re-encodes invalid UTF-8 in the message and author (observed)."""
    r = sh(["git", "-C", str(repo), "commit", "-q", "--allow-empty", "--no-verify", "-F", "-"],
           input=msg, env=ident(author, when))
    if r.returncode:
        raise RuntimeError(f"commit: {r.stderr[:200]!r}")
    return git(repo, "rev-parse", "HEAD")


def raw_commit(repo, msg, author, when):
    """Commit object written verbatim with hash-object --literally (keeps invalid bytes)."""
    tree = git(repo, "rev-parse", "HEAD^{tree}")
    parent = git(repo, "rev-parse", "HEAD")
    line = author + b" <a@x.invalid> " + when.encode()
    body = (b"tree " + tree.encode() + b"\nparent " + parent.encode() + b"\nauthor " + line
            + b"\ncommitter " + line + b"\n\n" + msg)
    sha = git(repo, "hash-object", "-t", "commit", "-w", "--literally", "--stdin", input=body)
    git(repo, "update-ref", "refs/heads/master", sha)
    return sha


def build(name, steps=None, errata=b"# header\n", report=None, lane_cfg=(), fleet_cfg=(),
          lane_files=None, fleet_files=None, attrs=None):
    steps = steps or [("normal", b"round-1: work\n", b"kama-shokunin")]
    d = ROOT / name
    lane = new_repo(d / "lane")
    fleet = new_repo(d / "fleet")
    for k, v in lane_cfg:
        git(lane, "config", k, v)
    for k, v in fleet_cfg:
        git(fleet, "config", k, v)
    if attrs is not None:
        (fleet / ".git" / "info" / "attributes").write_text(attrs)
    (d / "bad.tsv").write_bytes(b"# h\n\xff\n")
    if errata is not None:
        put(lane, "registry/report-landing-errata.tsv", errata)
    for rel, data in (lane_files or {}).items():
        put(lane, rel, data)
    commit(lane, b"registry\n", b"fixture", f"{T0 + 100} +0000")
    shas = []
    for i, (kind, msg, author) in enumerate(steps):
        fn = commit if kind == "normal" else raw_commit
        shas.append(fn(lane, msg, author, f"{T0 + i} +0000"))
    if report is None:
        report = f"# Round 1\n\n## Landed changes\n- {shas[0][:7]} round-1: work\n".encode()
    put(fleet, ".ufo/reports/round-1/kama.md", report)
    for rel, data in (fleet_files or {}).items():
        put(fleet, rel, data)
    commit(fleet, b"round-1 report\n", b"fixture", f"{T0 + 1000} +0000")
    return d


def audit(d, script, args=("--rounds", "1"), env=None, lane=None):
    e = dict(ENV)
    e.update(env or {})
    cmd = ["python3", script, "--lane-repo", str(lane or d / "lane"), "--fleet-repo", str(d / "fleet"),
           "--branch", "master", *[a.replace("{d}", str(d)) for a in args]]
    r = subprocess.run(cmd, capture_output=True, env=e)
    err = r.stderr.decode("utf-8", "replace").strip().splitlines()
    out = r.stdout.decode("utf-8", "replace").strip().splitlines()
    if any(line.startswith("Traceback") for line in err):
        return f"rc={r.returncode} TRACEBACK {err[-1][:80]}"
    if r.returncode == 2:
        return f"rc=2 {err[-1][:80] if err else ''}"
    return f"rc={r.returncode} {out[-1][:60] if out else ''}"


def sha(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()[:16]


# (label, expectation, build kwargs, audit kwargs)
CASES = [
    ("C0", "control: clean", {}, {}),
    ("C0b", "control: valid UTF-8 non-ASCII subject, default config",
     {"steps": LATIN}, {}),
    ("A1a", "repo-local i18n.logOutputEncoding=ISO-8859-1 + non-ASCII subject",
     {"lane_cfg": BAD_CFG, "steps": LATIN}, {}),
    ("A1b", "control: same repo config, ASCII subject", {"lane_cfg": BAD_CFG}, {}),
    ("A1c", "raw commit, invalid UTF-8 subject, round commit NOT cited",
     {"steps": [("raw", b"round-1: caf\xe9 work\n", b"kama-shokunin")], "report": NONE}, {}),
    ("A1d", "raw commit, invalid UTF-8 author on a NON-round commit",
     {"steps": [("raw", b"misc\n", b"kama\xe9"), ("normal", b"round-1: work\n", b"kama-shokunin")],
      "report": NONE}, {}),
    ("A2a", "raw commit, invalid UTF-8 author on the round commit, NOT cited",
     {"steps": [("raw", b"round-1: work\n", b"kama\xe9")], "report": NONE}, {}),
    ("A2c", "control: valid author, NOT cited",
     {"steps": [("raw", b"round-1: work\n", b"kama-shokunin")], "report": NONE}, {}),
    ("A3", "invalid UTF-8 committed fleet report (git show HEAD:rel)",
     {"report": b"# Round 1\n\n\xe9\n"}, {}),
    ("A4", "invalid UTF-8 errata blob on branch (git show branch:ERRATA)",
     {"errata": b"# h\n\xff\n"}, {}),
    ("A4c", "control: invalid errata via --errata PATH (wrapped)",
     {}, {"args": ("--rounds", "1", "--errata", "{d}/bad.tsv")}),
    ("A5", "fleet core.quotePath=false + raw non-UTF-8 name under .ufo/reports, open-ended rounds",
     {"fleet_cfg": (("core.quotePath", "false"),),
      "fleet_files": {".ufo/reports/round-2/" + os.fsdecode(b"\xff") + ".md": b"x\n"}},
     {"args": ("--rounds", "1-")}),
    ("A5c", "control: same name, default quotePath",
     {"fleet_files": {".ufo/reports/round-2/" + os.fsdecode(b"\xff") + ".md": b"x\n"}},
     {"args": ("--rounds", "1-")}),
    ("A6", "CLI --lane with invalid UTF-8 bytes (git stderr echoes them, rc!=0)",
     {}, {"args": ("--rounds", "1", "--lane", os.fsdecode(b"\xff"))}),
    ("A7", "ASCII locale env + valid non-ASCII subject",
     {"steps": LATIN}, {"env": ASCII_ENV}),
    ("A8", "ASCII locale env + non-ASCII errata correction",
     {"errata": ERR_ROW}, {"env": ASCII_ENV}),
    ("A9", "control: invalid corpus/SOURCES.md blob (wrapped)",
     {"lane_files": {"corpus/SOURCES.md": b"\xff\n"}}, {}),
    ("B1", "errata round field of 4301 digits (int limit, every default run)",
     {"errata": b"# h\n" + b"9" * 4301 + b"\tlanded-section-missing\t-\t-\tx\n"}, {}),
    ("B1c", "control: 4300-digit round field",
     {"errata": b"# h\n" + b"9" * 4300 + b"\tlanded-section-missing\t-\t-\tx\n"}, {}),
    ("B2", "fleet path .ufo/reports/round-<4301 digits>/kama.md, open-ended rounds",
     {"fleet_files": {".ufo/reports/round-" + "9" * 4301 + "/kama.md": b"x\n"}},
     {"args": ("--rounds", "1-")}),
    ("B2c", "control: fleet round-2 report, open-ended rounds",
     {"fleet_files": {".ufo/reports/round-2/kama.md": b"x\n"}}, {"args": ("--rounds", "1-")}),
    ("B3", "CLI --rounds with 4301 digits", {}, {"args": ("--rounds", "9" * 4301)}),
    ("C1", "non-ASCII errata field printed to ASCII stdout (text output)",
     {"errata": ERR_ROW}, {"env": {"PYTHONIOENCODING": "ascii"}}),
    ("C1c", "control: same, --json (ASCII-escaped)",
     {"errata": ERR_ROW}, {"env": {"PYTHONIOENCODING": "ascii"}, "args": ("--rounds", "1", "--json")}),
    ("D1", "plain git commit, author name contains 0x1f + digits, NOT cited (framing)",
     {"steps": [("normal", b"round-1: work\n", b"kama-shokunin\x1f1700000000")], "report": NONE}, {}),
    ("D1c", "control: plain author, NOT cited",
     {"steps": [("normal", b"round-1: work\n", b"kama-shokunin")], "report": NONE}, {}),
]


def pipe_closed(d, script):
    cmd = ["python3", script, "--lane-repo", str(d / "lane"), "--fleet-repo", str(d / "fleet"),
           "--branch", "master", "--rounds", "1"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=ENV)
    p.stdout.close()
    _, err = p.communicate()
    tail = err.decode("utf-8", "replace").strip().splitlines()[-1:]
    return f"rc={p.returncode} {tail}"


def textconv_probe():
    log = ROOT / "textconv.log"
    rel = ".ufo/reports/round-1/kama.md"
    d = build("E3", fleet_cfg=(("diff.rep.textconv", f"sh -c 'echo textconv >> {log}; cat \"$1\"' sh"),),
              attrs=".ufo/reports/*/kama.md diff=rep\n")
    probes = {
        "git show HEAD:rel": ["show", f"HEAD:{rel}"],
        "git show --textconv": ["show", "--textconv", f"HEAD:{rel}"],
        "git log --diff-filter=A": ["log", "--diff-filter=A", "--format=%at", "--", rel],
        "git log -p": ["log", "-p", "--format=%H", "--", rel],
        "git cat-file blob": ["cat-file", "blob", f"HEAD:{rel}"],
    }
    for label, args in probes.items():
        log.unlink(missing_ok=True)
        r = sh(["git", "-C", str(d / "fleet"), *args])
        n = log.read_text().count("textconv") if log.exists() else 0
        print(f"E3   {label:26} rc={r.returncode} textconv_runs={n}")
    log.unlink(missing_ok=True)
    print(f"     audit (base) textconv_runs during run:", end=" ")
    audit(d, BASE)
    print(log.read_text().count("textconv") if log.exists() else 0)


def main():
    print(f"base sha256={sha(BASE)} current sha256={sha(CUR)}")
    for label, expect, bk, ak in CASES:
        d = build(label, **bk)
        args = ak.get("args", ("--rounds", "1"))
        env = ak.get("env")
        print(f"{label:4} {expect}")
        print(f"     base: {audit(d, BASE, args, env)}")
        print(f"     cur : {audit(d, CUR, args, env)}")
    d = build("E1")
    os.symlink("loopB", d / "loopA")
    os.symlink("loopA", d / "loopB")
    print("E1   symlink loop as --lane-repo")
    print(f"     base: {audit(d, BASE, lane=d / 'loopA')}")
    print(f"     cur : {audit(d, CUR, lane=d / 'loopA')}")
    d = build("E2")
    print("E2   stdout pipe closed before output (clean run)")
    print(f"     base: {pipe_closed(d, BASE)}")
    print(f"     cur : {pipe_closed(d, CUR)}")
    textconv_probe()
    for label, script in (("base", BASE), ("cur", CUR)):
        r = sh(["python3", script, "--selftest"], env=dict(ENV, TMPDIR=str(ROOT)))
        print(f"E4   selftest {label}: rc={r.returncode} "
              f"traceback={b'Traceback' in r.stderr} out={r.stdout.decode().strip().splitlines()[-1:]}")


if __name__ == "__main__":
    main()
