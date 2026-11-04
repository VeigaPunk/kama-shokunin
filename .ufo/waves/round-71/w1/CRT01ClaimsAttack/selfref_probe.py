#!/usr/bin/env python3
"""Self-reference probe on fixture copies (never the lane).

fx/selfref : fixture tip + citations patched to observed values, gate citation KEPT, committed
fx/nocite  : same but the gate citation clause removed from the calibration row, committed
"""
import hashlib
import re
import shutil
import subprocess
import sys
from pathlib import Path

S = Path("/fast/scratch/hyaku/kama-r71/CRT01ClaimsAttack")
GREEN = S / "fx" / "green"
CITE = ("run `python3 tools/pre-report-gate.py --repo . --round 71 --tip master` "
        "\u2192 `PRE_REPORT round=71 arms=5 failed=0 uncommitted=0` (exit 0); ")
IDENT = ["-c", "user.name=r71", "-c", "user.email=r71@example.invalid"]


def sh(*cmd, cwd=None, timeout=900):
    return subprocess.run(cmd, cwd=str(cwd) if cwd else None, capture_output=True,
                          text=True, timeout=timeout)


def assert_top(d: Path):
    top = sh("git", "-C", str(d), "rev-parse", "--show-toplevel").stdout.strip()
    if Path(top).resolve() != d.resolve():
        raise SystemExit(f"toplevel mismatch: {top} != {d}")
    return top


def make(name, drop_citation):
    d = S / "fx" / name
    if d.exists():
        shutil.rmtree(d)
    shutil.copytree(GREEN, d)
    assert_top(d)
    sc = d / "SCORECARD.md"
    text = sc.read_text(encoding="utf-8")
    data = (d / "PROVINCE.md").read_bytes()
    sha = hashlib.sha256(data).hexdigest()
    lines = data.decode("utf-8").count("\n")
    rc, out = sh(sys.executable, "-c",
                 "import glob;print(len([f for f in glob.glob('corpus/knowledge/*.md') "
                 "if 'engine-sides' not in f and 'processes' not in f]))", cwd=d)
    count = out.strip().splitlines()[-1]
    text2 = re.sub(r"(PROVINCE\.md` sha256 `)[0-9a-f]{64}", r"\g<1>" + sha, text, count=1)
    text2 = re.sub(r"(`" + sha + r"` \()(\d+)( lines)", r"\g<1>" + str(lines) + r"\g<3>", text2, count=1)
    text2 = re.sub(r"([)]\)\"` \u2192 `)(\d+)(`)", r"\g<1>" + count + r"\g<3>", text2, count=1)
    if text2 == text:
        print(f"WARN {name}: no citation substitution applied")
    if drop_citation:
        if CITE not in text2:
            raise SystemExit(f"{name}: citation clause not found")
        text2 = text2.replace(CITE, "", 1)
    sc.write_text(text2, encoding="utf-8")
    r = sh("git", "-C", str(d), "add", "-A")
    r = sh("git", "-C", str(d), *IDENT, "commit", "-q", "-m", f"fixture: {name}")
    if r.returncode != 0:
        raise SystemExit(f"{name}: commit failed: {r.stderr}")
    head = sh("git", "-C", str(d), "rev-parse", "--short", "HEAD").stdout.strip()
    print(f"{name}: head={head} sha={sha[:12]} lines={lines} coverage={count} "
          f"citation={'dropped' if drop_citation else 'kept'}")
    return d


def recon(d):
    rc, out = None, None
    p = sh(sys.executable, "tools/round42-selfdesc-reconcile.py", "--repo", ".", "--tip", "master", cwd=d)
    return p.returncode, p.stdout


def gate(d, *extra):
    p = sh(sys.executable, "tools/pre-report-gate.py", "--repo", ".", "--round",
           extra[0] if extra else "71", "--tip", "master", cwd=d)
    return p.returncode, p.stdout


def main():
    a = make("selfref", drop_citation=False)
    rc, out = recon(a)
    print(f"selfref reconciler exit={rc}")
    for ln in out.splitlines():
        print("   ", ln[:240])
    rc, out = gate(a)
    print(f"selfref gate exit={rc}")
    for ln in out.splitlines():
        print("   ", ln[:240])

    # one level of regress: a checkout of the same tip, as r41's harness builds it.
    probe = S / "fx" / "regress-checkout"
    if probe.exists():
        shutil.rmtree(probe)
    r = sh("git", "clone", "-q", "--shared", "--no-checkout", str(a), str(probe))
    assert_top(probe) if r.returncode == 0 else None
    sh("git", "-C", str(probe), "checkout", "-q", "--detach", "HEAD")
    rc, out = gate(probe)
    print(f"regress-checkout gate exit={rc} (cwd=checkout of the same tip)")
    for ln in out.splitlines():
        print("   ", ln[:240])

    b = make("nocite", drop_citation=True)
    rc, out = recon(b)
    print(f"nocite reconciler exit={rc}")
    for ln in out.splitlines()[:6]:
        print("   ", ln[:240])
    rc, out = gate(b)
    print(f"nocite gate exit={rc}")
    for ln in out.splitlines():
        print("   ", ln[:240])
    (S / "c1" / "selfref_gate.out").write_text(
        f"# fixture {a} (citation kept)\n" + "".join(
            ln + "\n" for ln in gate(a)[1].splitlines()) +
        f"# fixture regress-checkout\n" + "".join(
            ln + "\n" for ln in gate(probe)[1].splitlines()) +
        f"# fixture {b} (citation dropped)\n" + "".join(
            ln + "\n" for ln in gate(b)[1].splitlines()), encoding="utf-8")


if __name__ == "__main__":
    main()
