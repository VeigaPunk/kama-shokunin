#!/usr/bin/env python3
"""Extra probes: pure-UTF-8 history under a Latin-1 log encoding; %an
conversion; blob reads are untouched by i18n.logOutputEncoding."""
import os, shutil, subprocess, sys

ROOT = "/tmp/kama-r23/ScoutLogEncoding"
REPRO = ROOT + "/repro/extra"
BASE = ROOT + "/audit-base.py"
ENV = {"PATH": "/usr/bin:/bin", "HOME": REPRO + "/home",
       "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_NOSYSTEM": "1",
       "LC_ALL": "C.UTF-8"}


def git(args, cwd, inp=None, extra=None):
    env = dict(ENV)
    if extra:
        env.update(extra)
    return subprocess.run(["git", *args], cwd=cwd, input=inp,
                          capture_output=True, env=env)


def ok(args, cwd, inp=None, extra=None):
    p = git(args, cwd, inp, extra)
    assert p.returncode == 0, (args, p.returncode, p.stderr)
    return p.stdout


def commit(repo, msg, when, name=b"kama-shokunin", parent=None):
    args = ["commit-tree"]
    tree = ok(["write-tree"], repo).strip()
    args.append(tree)
    if parent:
        args += ["-p", parent]
    env = {"GIT_AUTHOR_NAME": name.decode(), "GIT_AUTHOR_EMAIL": "a@x",
           "GIT_COMMITTER_NAME": "kama-shokunin",
           "GIT_COMMITTER_EMAIL": "a@x",
           "GIT_AUTHOR_DATE": f"@{when} +0000",
           "GIT_COMMITTER_DATE": f"@{when} +0000"}
    return ok(args, repo, msg, env).strip()


shutil.rmtree(REPRO, ignore_errors=True)
os.makedirs(REPRO + "/home")

# --- byte probe: %an under a proper ISO-8859-1 header ---------------------
r = REPRO + "/an"
os.makedirs(r)
ok(["init", "-q", "-b", "master"], r)
open(r + "/f", "w").write("x\n")
ok(["add", "f"], r)
tree = ok(["write-tree"], r).strip()
body = (b"tree " + tree + b"\nauthor na\xefve <a@x> 1000 +0000\n"
        b"committer kama-shokunin <a@x> 1000 +0000\n"
        b"encoding ISO-8859-1\n\nround-1: plain\n")
sha = ok(["hash-object", "-w", "-t", "commit", "--stdin", "--literally"],
         r, body).strip()
for cfg in ([], ["-c", "i18n.logOutputEncoding=UTF-8"],
            ["-c", "i18n.logOutputEncoding=ISO-8859-1"]):
    p = git([*cfg, "log", "-1", "--format=%an", sha], r)
    print(f"%an header ISO-8859-1 cfg={cfg} rc={p.returncode} hex={p.stdout.hex()}")

# --- S3: pure UTF-8 history (no encoding header), repo logOut=ISO ---------
lane, fleet = REPRO + "/s3/lane", REPRO + "/s3/fleet"
for x in (lane, fleet):
    os.makedirs(x)
    ok(["init", "-q", "-b", "master"], x)
open(lane + "/f", "w").write("x\n")
ok(["add", "f"], lane)
sc = commit(lane, b"scaffold\n", 900)
w = commit(lane, "docs: caf\u00e9\n".encode(), 1000, name=b"someone", parent=sc)
ok(["update-ref", "refs/heads/master", w], lane)
report = ("# r1\n## Work performed\nnone\n## Landed changes\n"
          "- `%s` scaffold\n" % sc.decode())
rel = fleet + "/.ufo/reports/round-1/kama.md"
os.makedirs(os.path.dirname(rel))
open(rel, "w", encoding="utf-8").write(report)
ok(["add", ".ufo/reports/round-1/kama.md"], fleet)
p = git(["commit", "-q", "-m", "report"], fleet, extra={
    "GIT_AUTHOR_NAME": "kama-shokunin", "GIT_AUTHOR_EMAIL": "a@x",
    "GIT_COMMITTER_NAME": "kama-shokunin", "GIT_COMMITTER_EMAIL": "a@x",
    "GIT_AUTHOR_DATE": "@1100 +0000", "GIT_COMMITTER_DATE": "@1100 +0000"})
assert p.returncode == 0, p.stderr


def audit(label, cfg):
    if cfg:
        ok(["config", *cfg], lane)
    else:
        git(["config", "--unset-all", "i18n.logOutputEncoding"], lane)
        git(["config", "--unset-all", "i18n.commitEncoding"], lane)
    q = subprocess.run([sys.executable, BASE, "--lane-repo", lane,
                        "--fleet-repo", fleet, "--rounds", "1",
                        "--no-errata"], capture_output=True, text=True, env=ENV)
    last = (q.stderr.strip().splitlines() or [""])[-1]
    out = (q.stdout.strip().splitlines() or [""])[-1]
    print(f"S3 {label}: rc={q.returncode} out={out[:90]!r} err={last[:120]!r}")


audit("default (UTF-8 cafe subject)", None)
audit("repo logOutputEncoding=ISO-8859-1",
      ["i18n.logOutputEncoding", "ISO-8859-1"])
audit("repo commitEncoding=ISO-8859-1", ["i18n.commitEncoding", "ISO-8859-1"])

# --- blob invariance ------------------------------------------------------
open(lane + "/blob", "wb").write(b"raw \xef bytes\n")
ok(["add", "blob"], lane)
p = git(["commit", "-q", "-m", "blob", "-m", "x"], lane, extra={
    "GIT_AUTHOR_NAME": "kama-shokunin", "GIT_AUTHOR_EMAIL": "a@x",
    "GIT_COMMITTER_NAME": "kama-shokunin", "GIT_COMMITTER_EMAIL": "a@x"})
assert p.returncode == 0, p.stderr
for cfg in ([], ["-c", "i18n.logOutputEncoding=ISO-8859-1"],
            ["-c", "i18n.logOutputEncoding=UTF-8"]):
    a = git([*cfg, "show", "master:blob"], lane)
    b = git([*cfg, "cat-file", "blob", "master:blob"], lane)
    print(f"blob cfg={cfg} show_rc={a.returncode} show_hex={a.stdout.hex()} "
          f"cat_hex={b.stdout.hex()}")
