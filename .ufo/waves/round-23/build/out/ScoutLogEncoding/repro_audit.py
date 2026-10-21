#!/usr/bin/env python3
"""Audit-level probe at base 4fe9339f: repo-local encoding config vs verdict."""
import json, os, shutil, subprocess, sys

ROOT = "/tmp/kama-r23/ScoutLogEncoding"
REPRO = ROOT + "/repro/audit"
BASE = ROOT + "/audit-base.py"
CAND = ROOT + "/audit-cand-sim.py"
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


def commit_tree(repo, tree, parent, msg, when, name=b"kama-shokunin"):
    args = ["commit-tree", tree]
    if parent:
        args += ["-p", parent]
    env = {"GIT_AUTHOR_NAME": name.decode("latin-1"),
           "GIT_AUTHOR_EMAIL": "a@x", "GIT_COMMITTER_NAME": "kama-shokunin",
           "GIT_COMMITTER_EMAIL": "a@x",
           "GIT_AUTHOR_DATE": f"@{when} +0000",
           "GIT_COMMITTER_DATE": f"@{when} +0000"}
    p = git(args, repo, msg, env)
    assert p.returncode == 0, p.stderr
    return p.stdout.strip()


def craft_literal(repo, tree, parent, header, subject, when,
                  author=b"kama-shokunin"):
    body = (b"tree " + tree + b"\nparent " + parent + b"\n"
            b"author " + author + b" <a@x> " + str(when).encode()
            + b" +0000\n"
            b"committer kama-shokunin <a@x> " + str(when).encode()
            + b" +0000\n")
    if header is not None:
        body += b"encoding " + header + b"\n"
    body += b"\n" + subject + b"\n"
    sha = ok(["hash-object", "-w", "-t", "commit", "--stdin", "--literally"],
             repo, body).strip()
    ok(["update-ref", "refs/heads/master", sha], repo)
    return sha


def build(dst, tip):
    """lane: scaffold(900) -> W(1100) -> cafe(1150, utf8, other author)
    tip is 'latin1' -> N(1200, ISO-8859-1 header + Latin-1 subject)
              'noheader' -> N2(1200, raw Latin-1 bytes, no header)
    fleet report cites W and the tip."""
    shutil.rmtree(dst, ignore_errors=True)
    os.makedirs(dst + "/home")
    lane, fleet = dst + "/lane", dst + "/fleet"
    for r in (lane, fleet):
        os.makedirs(r)
        ok(["init", "-q", "-b", "master"], r)
    open(lane + "/f", "w").write("x\n")
    ok(["add", "f"], lane)
    tree = ok(["rev-parse", "f"], lane)  # placeholder overwritten below
    tree = ok(["write-tree"], lane).strip()
    scaffold = commit_tree(lane, tree, None, b"scaffold\n", 900)
    w = commit_tree(lane, tree, scaffold, b"round-1: work\n", 1100)
    cafe = commit_tree(lane, tree, w,
                       "docs: caf\u00e9\n".encode(), 1150,
                       name=b"someone")
    ok(["update-ref", "refs/heads/master", cafe], lane)
    if tip == "latin1":
        n = craft_literal(lane, tree, cafe, b"ISO-8859-1",
                          b"round-1: na\xefve", 1200)
    else:
        n = craft_literal(lane, tree, cafe, None,
                          b"round-1: na\xefve", 1200)
    report = ("# r1\n## Work performed\nnone\n## Landed changes\n"
              "- `%s` work\n- `%s` tip\n" % (w.decode(), n.decode()))
    rel = fleet + "/.ufo/reports/round-1/kama.md"
    os.makedirs(os.path.dirname(rel))
    open(rel, "w", encoding="utf-8").write(report)
    ok(["add", ".ufo/reports/round-1/kama.md"], fleet)
    cp = git(["commit", "-q", "-m", "round-1: kama report"], fleet, extra={
        "GIT_AUTHOR_NAME": "kama-shokunin", "GIT_AUTHOR_EMAIL": "a@x",
        "GIT_COMMITTER_NAME": "kama-shokunin", "GIT_COMMITTER_EMAIL": "a@x",
        "GIT_AUTHOR_DATE": "@1300 +0000", "GIT_COMMITTER_DATE": "@1300 +0000"})
    assert cp.returncode == 0, cp.stderr
    return lane, fleet, w.decode(), n.decode()


def run_audit(script, lane, fleet):
    p = subprocess.run([sys.executable, script, "--lane-repo", lane,
                        "--fleet-repo", fleet, "--rounds", "1",
                        "--no-errata"], capture_output=True, text=True,
                       env=ENV)
    return p.returncode, p.stdout, p.stderr


def show(label, rc, out, err):
    print(f"\n--- {label}: rc={rc}")
    print("  stdout_last:", out.strip().splitlines()[-1] if out.strip() else "")
    print("  stderr_last:", (err.strip().splitlines() or [""])[-1][:300])
    if "Traceback" in err:
        tb = err.strip().splitlines()
        print("  traceback:", " | ".join(tb[-3:])[:300])


shutil.rmtree(REPRO, ignore_errors=True)
os.makedirs(REPRO + "/home")

# Scenario 1: properly headed Latin-1 commit + UTF-8 café commit.
lane, fleet, w, n = build(REPRO + "/s1", "latin1")
show("S1 base, no repo config (control)", *run_audit(BASE, lane, fleet))

ok(["config", "i18n.logOutputEncoding", "ISO-8859-1"], lane)
show("S1 base, repo i18n.logOutputEncoding=ISO-8859-1",
     *run_audit(BASE, lane, fleet))
ok(["config", "--unset", "i18n.logOutputEncoding"], lane)

ok(["config", "i18n.commitEncoding", "ISO-8859-1"], lane)
show("S1 base, repo i18n.commitEncoding=ISO-8859-1",
     *run_audit(BASE, lane, fleet))
ok(["config", "--unset", "i18n.commitEncoding"], lane)

ok(["config", "i18n.logOutputEncoding", "UTF-8"], lane)
show("S1 base, repo i18n.logOutputEncoding=UTF-8",
     *run_audit(BASE, lane, fleet))

ok(["config", "i18n.logOutputEncoding", "ISO-8859-1"], lane)
show("S1 candidate-sim, repo i18n.logOutputEncoding=ISO-8859-1",
     *run_audit(CAND, lane, fleet))

# Scenario 2: no encoding header, raw invalid UTF-8 subject.
lane2, fleet2, w2, n2 = build(REPRO + "/s2", "noheader")
show("S2 base, no repo config (no header, raw \\xef)",
     *run_audit(BASE, lane2, fleet2))
ok(["config", "i18n.logOutputEncoding", "UTF-8"], lane2)
show("S2 base, repo i18n.logOutputEncoding=UTF-8",
     *run_audit(BASE, lane2, fleet2))
ok(["config", "i18n.logOutputEncoding", "ISO-8859-1"], lane2)
show("S2 base, repo i18n.logOutputEncoding=ISO-8859-1",
     *run_audit(BASE, lane2, fleet2))
show("S2 candidate-sim, repo i18n.logOutputEncoding=ISO-8859-1",
     *run_audit(CAND, lane2, fleet2))

# Blob reads are not affected by logOutputEncoding at all.
open(lane2 + "/blob", "wb").write(b"raw \xef bytes\n")
ok(["add", "blob"], lane2)
cp = git(["commit", "-q", "-m", "blob"], lane2)
assert cp.returncode == 0, cp.stderr
for cfg in ([], ["-c", "i18n.logOutputEncoding=ISO-8859-1"]):
    p = git([*cfg, "show", "master:blob"], lane2)
    print(f"\nblob show cfg={cfg} rc={p.returncode} hex={p.stdout.hex()}")
