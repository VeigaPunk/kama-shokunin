#!/usr/bin/env python3
"""R42B18 edge-case divergence probe for tools/digest-ledger.py.

Builds deterministic adversarial fixtures, runs the tool with THIS interpreter,
and prints a normalised transcript (case -> exit code, stdout, stderr-class).
Diffing the transcript across interpreters shows any behavioural divergence on
inputs the C2 CASES fixtures do not cover. Read-only outside its own fixture dir.
"""
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile

TOOL = sys.argv[1]
ROOT = sys.argv[2]
REPO = sys.argv[3]


def h(b):
    return hashlib.sha256(b).hexdigest()


def run(args, cwd):
    p = subprocess.run([sys.executable, TOOL, *args], cwd=cwd, capture_output=True, text=True)
    err = p.stderr.strip().replace(ROOT, "<ROOT>")
    if err:
        err = "ERR:" + err.split("\n")[0][:120]
    out = p.stdout.strip().replace(ROOT, "<ROOT>").replace("\n", " | ")
    return f"exit={p.returncode} out=[{out}] {err}".strip()


def main():
    base = os.path.join(ROOT, "edge")
    shutil.rmtree(base, ignore_errors=True)
    os.makedirs(base)
    lines = []

    # 1 adjacency: 65 hex chars and 64 hex with a trailing hex char are not tokens
    d = os.path.join(base, "adj"); os.makedirs(d)
    good = h(b"adj")
    open(os.path.join(d, "a.bin"), "wb").write(b"adj")
    open(os.path.join(d, "x.md"), "w").write(good + "a\n" + "0" + good + "\n" + good + "\n")
    lines.append(("01 adjacency-65hex-and-prefixed", run(["scan", "--dir", d], base)))

    # 2 uppercase hex is not a token
    d = os.path.join(base, "upper"); os.makedirs(d)
    open(os.path.join(d, "x.md"), "w").write(good.upper() + "\n")
    lines.append(("02 uppercase-hex-ignored", run(["scan", "--dir", d], base)))

    # 3 invalid UTF-8 in a doc: latin-1 bytes replaced, ascii tokens survive
    d = os.path.join(base, "nonutf"); os.makedirs(d)
    open(os.path.join(d, "x.md"), "wb").write(b"\xff\xfe caf\xe9 " + good.encode() + b"\n")
    open(os.path.join(d, "x.bin"), "wb").write(b"nonutf")
    lines.append(("03 non-utf8-doc", run(["scan", "--dir", d], base)))

    # 4 CRLF doc
    d = os.path.join(base, "crlf"); os.makedirs(d)
    open(os.path.join(d, "x.md"), "wb").write(good.encode() + b"\r\n")
    open(os.path.join(d, "x.bin"), "wb").write(b"crlf")
    lines.append(("04 crlf-doc", run(["scan", "--dir", d], base)))

    # 5 duplicate ledger rows: last row wins
    d = os.path.join(base, "dup"); os.makedirs(d); os.makedirs(os.path.join(d, "registry"))
    t = "ab" * 32
    open(os.path.join(d, "x.md"), "w").write(t + "\n")
    open(os.path.join(d, "registry", "digest-ledger.tsv"), "w").write(
        "digest\tclass\tsubject\tpath\tcorrect\tverified-at\tnote\n"
        f"{t}\tunverifiable\ts\t\t\t\twhy\n{t}\tunknownclass\ts\t\t\t\t\n")
    lines.append(("05 duplicate-ledger-last-wins", run(["scan", "--dir", d], base)))

    # 6 short ledger row is padded
    d = os.path.join(base, "short"); os.makedirs(d); os.makedirs(os.path.join(d, "registry"))
    open(os.path.join(d, "x.md"), "w").write(t + "\n")
    open(os.path.join(d, "registry", "digest-ledger.tsv"), "w").write("digest\tclass\tsubject\n" f"{t}\tunverifiable\n")
    lines.append(("06 short-ledger-row", run(["scan", "--dir", d], base)))

    # 7 unknown class -> ledger_bad
    d = os.path.join(base, "bogus"); os.makedirs(d); os.makedirs(os.path.join(d, "registry"))
    open(os.path.join(d, "x.md"), "w").write(t + "\n")
    open(os.path.join(d, "registry", "digest-ledger.tsv"), "w").write(
        "digest\tclass\tsubject\tpath\tcorrect\tverified-at\tnote\n" f"{t}\tnonsense\ts\t\t\t\t\n")
    lines.append(("07 unknown-class-ledger_bad", run(["scan", "--dir", d], base)))

    # 8 symlink to an outside file is neither blob nor doc
    d = os.path.join(base, "link"); os.makedirs(d)
    outside = os.path.join(base, "outside.bin")
    open(outside, "wb").write(b"outside payload")
    os.symlink(outside, os.path.join(d, "link.md"))
    lines.append(("08 symlink-skipped", run(["scan", "--dir", d], base)))

    # 9 missing --dir
    lines.append(("09 missing-dir", run(["scan", "--dir", os.path.join(base, "nope")], base)))

    # 10 bad rev
    lines.append(("10 bad-rev", run(["scan", "--repo", REPO, "--rev", "nosuchrev"], base)))

    # 11 .ufo/ and the ledger file are not documents; a 64-hex in another .tsv is
    d = os.path.join(base, "scope"); os.makedirs(d); os.makedirs(os.path.join(d, ".ufo"))
    os.makedirs(os.path.join(d, "registry"))
    open(os.path.join(d, ".ufo", "h.md"), "w").write("cd" * 32 + "\n")
    open(os.path.join(d, "registry", "digest-ledger.tsv"), "w").write(
        "digest\tclass\tsubject\tpath\tcorrect\tverified-at\tnote\n" f"{t}\tunverifiable\ts\t\t\t\twhy\n")
    open(os.path.join(d, "data.tsv"), "w").write("ef" * 32 + "\n")
    open(os.path.join(d, "readme.MD"), "w").write("11" * 32 + "\n")
    lines.append(("11 scope-ufo-ledger-uppercase-suffix", run(["scan", "--dir", d], base)))

    # 12 --ledger override
    d = os.path.join(base, "override"); os.makedirs(d)
    open(os.path.join(d, "x.md"), "w").write(t + "\n")
    lp = os.path.join(base, "alt-ledger.tsv")
    open(lp, "w").write("digest\tclass\tsubject\tpath\tcorrect\tverified-at\tnote\n" f"{t}\tunverifiable\ts\t\t\t\twhy\n")
    lines.append(("12 ledger-override", run(["scan", "--dir", d, "--ledger", lp], base)))

    # 13 --details shape for one unknown + one wrong_unflagged
    d = os.path.join(base, "details"); os.makedirs(d)
    open(os.path.join(d, "b.bin"), "wb").write(b"details")
    real = h(b"details")
    open(os.path.join(d, "x.md"), "w").write("ff" * 32 + "\n" + real[:8] + "9" * 56 + "\n")
    lines.append(("13 details-output", run(["scan", "--dir", d, "--details"], base)))

    # 14 empty dir
    d = os.path.join(base, "empty"); os.makedirs(d)
    lines.append(("14 empty-dir", run(["scan", "--dir", d], base)))

    # 15 selftest
    lines.append(("15 selftest", run(["selftest"], base)))

    # 16 usage error (no mode)
    lines.append(("16 usage-error", run(["scan"], base)))

    for name, out in lines:
        print(f"{name}: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
