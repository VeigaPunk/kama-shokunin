#!/usr/bin/env python3
"""R42B17 extension harness: does the frozen contract hold beyond the 8 cases the
counter samples?  Dir mode: 200 seeds.  Git mode: 24 committed fixture repos
(the counter's contract leg only ever exercises --dir, never git mode).
Also probes a non-UTF-8 tracked doc, where the tool and the counter's reference
decode differently."""
import hashlib
import importlib.util
import os
import random
import shutil
import subprocess
import sys
import tempfile

SEAT = "/fast/scratch/kama-r42/seats/R42B17"
CLONE = os.path.join(SEAT, "clone")
CNT = os.path.join(CLONE, "tools/round42-digest-audit.py")
TOOL = os.path.join(CLONE, "tools/digest-ledger.py")
TMP = os.path.join(SEAT, "tmp")
os.environ["TMPDIR"] = TMP

spec = importlib.util.spec_from_file_location("cnt", CNT)
cnt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cnt)


def tool_run(args, cwd):
    p = subprocess.run([sys.executable, TOOL, *args], cwd=cwd, capture_output=True, text=True, timeout=180)
    return p.stdout.strip(), p.returncode, p.stderr.strip()


def dir_leg(seeds):
    bad = []
    with tempfile.TemporaryDirectory(prefix="r42b17-dir-", dir=TMP) as work:
        for seed in seeds:
            rng = random.Random(seed)
            d = tempfile.mkdtemp(prefix=f"case{seed}-", dir=work)
            cnt.make_case(rng, d, seed)
            want = cnt.ref_dir(d)
            out, code, err = tool_run(["scan", "--dir", d], cwd=work)
            if out != cnt.summary(want) or code != cnt.exit_of(want):
                bad.append((seed, cnt.summary(want), cnt.exit_of(want), out, code, err[:120]))
            shutil.rmtree(d)
    return bad


def fixture_repo(seed, extra=None):
    d = tempfile.mkdtemp(prefix="r42b17-git-", dir=SEAT)
    subprocess.run(["git", "-C", d, "init", "-q"], check=True)
    top = subprocess.run(["git", "-C", d, "rev-parse", "--show-toplevel"],
                         capture_output=True, text=True).stdout.strip()
    assert top == d, (top, d)
    subprocess.run(["git", "-C", d, "config", "user.email", "r42b17@fixture.invalid"], check=True)
    subprocess.run(["git", "-C", d, "config", "user.name", "R42B17"], check=True)
    rng = random.Random(seed)
    cnt.make_case(rng, d, seed)
    for name, body in (extra or {}).items():
        path = os.path.join(d, name)
        os.makedirs(os.path.dirname(path), exist_ok=True) if os.path.dirname(path) else None
        with open(path, "wb") as f:
            f.write(body)
    subprocess.run(["git", "-C", d, "add", "-A"], check=True)
    subprocess.run(["git", "-C", d, "commit", "-qm", "fixture"], check=True)
    return d


def git_leg(seeds):
    bad = []
    for seed in seeds:
        d = fixture_repo(seed)
        try:
            want = cnt.ref_git(d, "HEAD")
            out, code, err = tool_run(["scan", "--repo", d, "--rev", "HEAD"], cwd=d)
            if out != cnt.summary(want) or code != cnt.exit_of(want):
                bad.append((seed, cnt.summary(want), cnt.exit_of(want), out, code, err[:160]))
        except Exception as e:  # noqa: BLE001 - report, do not abort the sweep
            bad.append((seed, "EXC", type(e).__name__, str(e)[:160], None, None))
        finally:
            shutil.rmtree(d, ignore_errors=True)
    return bad


print("== dir mode, seeds 1..200")
bad = dir_leg(range(1, 201))
print(f"mismatches={len(bad)}")
for b in bad[:6]:
    print("  ", b)

print("== git mode, seeds 1..24 (not exercised by the counter's contract leg)")
bad = git_leg(range(1, 25))
print(f"mismatches={len(bad)}")
for b in bad[:6]:
    print("  ", b)

print("== non-UTF-8 tracked doc (latin-1 bytes in a .md)")
d = fixture_repo(999, {"corpus/latin1.md": b"caf\xe9 \xff\xfe\n"})
try:
    print("  tool:", tool_run(["scan", "--repo", d, "--rev", "HEAD"], cwd=d)[:2])
    try:
        want = cnt.ref_git(d, "HEAD")
        print("  counter reference:", cnt.summary(want))
    except Exception as e:  # noqa: BLE001
        print("  counter reference EXC:", type(e).__name__, str(e)[:160])
    p = subprocess.run([sys.executable, CNT, "--repo", d, "--tip", "HEAD", "--seed", 3],
                       cwd=d, capture_output=True, text=True, timeout=600)
    print("  counter exit:", p.returncode)
    print("  counter stdout:", p.stdout.strip()[:160])
    print("  counter stderr tail:", p.stderr.strip()[-200:].replace("\n", "|"))
finally:
    shutil.rmtree(d, ignore_errors=True)
print("== done")
