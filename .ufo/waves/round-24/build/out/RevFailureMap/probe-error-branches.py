#!/usr/bin/env python3
"""Bounded, offline probes of the kama closure check's error disposition.

No network, no remote, no hostile fixture. Everything is local and synthetic:
  A. git() error branches, exercised by substituting subprocess.run (no repo
     is touched): timeout, OSError, non-zero rc, undecodable stdout,
     undecodable stderr.
  B. check_history_repo() on a benign complete local repo that merely
     *carries* promisor metadata (all objects present locally).
  C. lookup() disposition of a token that is absent from a local repo.

Every probe prints the observed exception type and the exit code the tool
would return. Run: python3 probe-error-branches.py
"""
import importlib.util
import io
import os
import subprocess
import sys
import tempfile
from pathlib import Path

TOOL = Path(sys.argv[1] if len(sys.argv) > 1 else
            "/home/vgpnk/Projects/shokunin/kama-shokunin/tools/"
            "report-landing-audit.py")
spec = importlib.util.spec_from_file_location("rla", TOOL)
rla = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rla)

print(f"# tool: {TOOL}")
print(f"# EvalError -> exit 2 (could-not-evaluate); defect -> exit 1; "
      f"clean -> exit 0")
print()

# ---------------------------------------------------------------- A. branches
print("## A. git() error branches (subprocess.run substituted)")


class FakeProc:
    def __init__(self, rc=0, out=b"", err=b""):
        self.returncode = rc
        self.stdout = out
        self.stderr = err


def run_with(fake, label, expect):
    orig = subprocess.run
    subprocess.run = fake
    try:
        out = rla.git("/tmp/x", "log", "--format=%H")
        got = f"returned {out!r}"
    except rla.EvalError as exc:
        got = f"EvalError: {str(exc)[:120]}"
    except Exception as exc:  # pragma: no cover - the thing we are checking
        got = f"*** {type(exc).__name__}: {exc} ***"
    finally:
        subprocess.run = orig
    ok = expect in got
    print(f"  [{'ok' if ok else 'FAIL'}] {label}: {got}")
    return ok


def raiser(exc):
    def _fake(*a, **kw):
        raise exc
    return _fake


results = []
results.append(run_with(
    raiser(subprocess.TimeoutExpired(cmd="git", timeout=20)),
    "timeout -> EvalError", "EvalError"))
results.append(run_with(
    raiser(OSError("no such file or directory")),
    "OSError -> EvalError", "EvalError"))
results.append(run_with(
    lambda *a, **kw: FakeProc(rc=128, err=b"fatal: bad object\n"),
    "rc != 0 -> EvalError", "EvalError"))
results.append(run_with(
    lambda *a, **kw: FakeProc(rc=0, out=b"abc\xff\xfe\n"),
    "undecodable stdout -> EvalError", "EvalError"))
results.append(run_with(
    lambda *a, **kw: FakeProc(rc=0, out=b"ok\n", err=b"warn\xff\n"),
    "undecodable stderr, rc=0 -> no error", "returned"))
results.append(run_with(
    lambda *a, **kw: FakeProc(rc=0, out=b"\xff\xfe\r\n"),
    "CRLF normalisation + strict decode -> EvalError", "EvalError"))
print()

# ------------------------------------------------- B. promisor metadata only
print("## B. promisor metadata on a complete local repo (all objects present)")
tmp = Path(tempfile.mkdtemp(prefix="rfm-promisor-", dir=os.environ.get(
    "RFMTMP", "/fast/scratch/hyaku/kama-r24")))
lane = tmp / "lane"
lane.mkdir()
env = dict(os.environ)
env.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
           GIT_AUTHOR_NAME="x", GIT_COMMITTER_NAME="x",
           GIT_AUTHOR_EMAIL="a@x", GIT_COMMITTER_EMAIL="a@x",
           GIT_AUTHOR_DATE="@1000 +0000", GIT_COMMITTER_DATE="@1000 +0000")
subprocess.run(["git", "init", "-q", "-b", "master", str(lane)], env=env,
               check=True)
(lane / "f").write_text("hello\n", encoding="utf-8")
subprocess.run(["git", "-C", str(lane), "add", "f"], env=env, check=True)
subprocess.run(["git", "-C", str(lane), "-c", "commit.gpgsign=false",
                "commit", "-q", "-m", "round-1: work"], env=env, check=True)
subprocess.run(["git", "-C", str(lane), "config", "remote.origin.promisor",
                "true"], env=env, check=True)
subprocess.run(["git", "-C", str(lane), "config", "remote.origin.url",
                "file:///nonexistent/promisor.git"], env=env, check=True)
head = subprocess.run(["git", "-C", str(lane), "rev-parse", "HEAD"], env=env,
                      capture_output=True, text=True).stdout.strip()
print(f"  repo: {lane}")
print(f"  head: {head}")
print(f"  config remote.origin.promisor=true, remote.origin.url="
      f"file:///nonexistent/promisor.git")
try:
    rla.check_history_repo(lane)
    got = "returned without error (audit continues)"
except rla.EvalError as exc:
    got = f"EvalError: {exc}"
except Exception as exc:
    got = f"*** {type(exc).__name__}: {exc} ***"
print(f"  check_history_repo -> {got}")
results.append("EvalError" in got)
print("  disposition today: exit 2 (could-not-evaluate) for a repository "
      "whose every object is present locally")
print()

# --------------------------------------------------- C. lookup of absent token
print("## C. lookup() disposition of an absent token (complete local repo)")
absent = "0" * 40
try:
    status = rla.lookup((lane,), [absent])
    print(f"  lookup -> {status}")
    results.append(status.get(absent) == "missing")
except Exception as exc:
    print(f"  *** {type(exc).__name__}: {exc} ***")
    results.append(False)
try:
    status = rla.lookup((lane,), [head])
    print(f"  lookup(head) -> {status}")
    results.append(status.get(head) == "found")
except Exception as exc:
    print(f"  *** {type(exc).__name__}: {exc} ***")
    results.append(False)
print()

print(f"## interim: {sum(1 for r in results if r)}/{len(results)} probes as "
      f"expected")
print(f"## scratch: {tmp}")

# ---------------------------------------------------------------------------
# D. failures that are NOT EvalError: what does main() print, and with which
#    exit code?  A non-EvalError escape still exits 2, but the message no
#    longer names the cause as a typed audit error.
# ---------------------------------------------------------------------------

print()
print("## D. non-EvalError escapes (disposition observed through main())")
import io as _io
import contextlib as _ctx


def run_main(argv):
    err = _io.StringIO()
    out = _io.StringIO()
    with _ctx.redirect_stderr(err), _ctx.redirect_stdout(out):
        rc = rla.main(argv)
    return rc, err.getvalue().strip()


# D1: an unreadable .git/info/grafts -> OSError inside grafts_effective
droot = Path(tempfile.mkdtemp(prefix="rfm-grafts-",
                               dir=os.environ.get(
                                   "RFMTMP",
                                   "/fast/scratch/hyaku/kama-r24")))
dlane, dfleet = droot / "lane", droot / "fleet"
for repo in (dlane, dfleet):
    repo.mkdir(parents=True)
    subprocess.run(["git", "init", "-q", "-b", "master", str(repo)], env=env,
                   check=True)
(dlane / "f").write_text("x\n", encoding="utf-8")
subprocess.run(["git", "-C", str(dlane), "add", "f"], env=env, check=True)
subprocess.run(["git", "-C", str(dlane), "-c", "commit.gpgsign=false",
                "commit", "-q", "-m", "round-1: work"], env=env, check=True)
grafts = dlane / ".git/info/grafts"
grafts.write_text("# comment only\n", encoding="utf-8")
# the fleet needs a committed report so the audit reaches report_cutoff()
rep = dfleet / ".ufo/reports/round-1/kama.md"
rep.parent.mkdir(parents=True)
rep.write_text("# r1\n## Landed changes\n- `x`\n", encoding="utf-8")
subprocess.run(["git", "-C", str(dfleet), "add",
                ".ufo/reports/round-1/kama.md"], env=env, check=True)
subprocess.run(["git", "-C", str(dfleet), "-c", "commit.gpgsign=false",
                "commit", "-q", "-m", "round-1: report"], env=env, check=True)
os.chmod(grafts, 0o000)
rc, err = run_main(["--lane-repo", str(dlane), "--fleet-repo", str(dfleet),
                     "--rounds", "1", "--no-errata"])
os.chmod(grafts, 0o644)
print(f"  D1 unreadable info/grafts -> exit={rc} stderr={err[:140]!r}")
results.append(rc == 2)

# D2: a git log whose %at is not a number -> ValueError inside report_cutoff
orig_git = rla.git


def fake_git(repo, *args, **kw):
    if "log" in args and "--format=%at" in args:
        return "not-a-number\n"
    return orig_git(repo, *args, **kw)


rla.git = fake_git
try:
    rc, err = run_main(["--lane-repo", str(dlane), "--fleet-repo", str(dfleet),
                         "--rounds", "1", "--no-errata"])
finally:
    rla.git = orig_git
print(f"  D2 non-numeric %at -> exit={rc} stderr={err[:140]!r}")
results.append(rc == 2)

print(f"## summary: {sum(1 for r in results if r)}/{len(results)} probes as "
      f"expected")
sys.exit(0 if all(results) else 1)
