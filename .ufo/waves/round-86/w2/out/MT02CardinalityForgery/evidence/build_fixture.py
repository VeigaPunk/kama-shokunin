#!/usr/bin/env python3
"""Build the MT02 fixture repo: real tools/round81-append-debt.py bytes at 67eddac,
one targeted forgery per commit, so round86-mutant-owners.py's real CLI can be graded
against each forgery and its true exit code recorded."""
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent
FIX = ROOT / "fixture"
SOURCE = (ROOT / "debt.py").read_text(encoding="utf-8")
TARGET = FIX / "tools" / "round81-append-debt.py"

ARMS_LINE = ('    print(f"APPEND_DEBT_SELFTEST_ARMS arms={len(cases)} expected={EXPECTED_ARMS} '
             'fail_lines={fail}")\n')
SUMMARY_LINE = '    print(f"APPEND_DEBT_SELFTEST pass={len(cases) - fail} fail={fail} arms={len(cases)}")\n'
RETURN_LINE = "    return 0 if fail == 0 and len(cases) == EXPECTED_ARMS else 1\n"
DROP_ARM = '    cases.append(("same-commit", r, 1, "not-descendant"))\n'

TRACEBACK = ('    sys.stderr.write("Traceback (most recent call last):\\n'
             '  File \\"selftest\\", line 1, in <module>\\nRuntimeError: forged\\n")\n')
STDERR_NOISE = '    sys.stderr.write("warning: internal diagnostic on stderr\\n")\n'


def sub(text, old, new, label):
    if text.count(old) != 1:
        sys.exit(f"edit {label}: site count {text.count(old)}")
    return text.replace(old, new)


VARIANTS = {
    # (a0) an unhandled SyntaxError on stderr: no "Traceback (most recent call last)" header
    "a0-syntaxerror-on-stderr": lambda t: sub(
        t, SUMMARY_LINE, "    if False:\n" + SUMMARY_LINE, "summary"),
    # (a2) forged summary pass=0 fail=0 with the arms field dropped; ARMS line intact
    "a2-forged-summary-no-arms-field": lambda t: sub(
        sub(t, SUMMARY_LINE, "    if False:\n        " + SUMMARY_LINE.lstrip()
            + '    print("APPEND_DEBT_SELFTEST pass=0 fail=0")\n', "summary"), RETURN_LINE,
        RETURN_LINE, "return"),
    # (b) one real arm dropped (33 cases), ARMS line forged to arms=34, exit forced 0
    "b-forged-arms-34-with-dropped-case": lambda t: sub(
        sub(sub(t, ARMS_LINE, ARMS_LINE.replace("arms={len(cases)}", "arms=34"), "arms"),
            DROP_ARM, "", "drop-arm"),
        RETURN_LINE, "    return 0 if fail == 0 else 1\n", "return"),
    # (c) an extra FAIL line the summary does not count
    "c-extra-fail-line-uncounted": lambda t: sub(
        t, ARMS_LINE,
        '    print("APPEND_DEBT_SELFTEST_FAIL phantom-arm exit=1 want=0")\n' + ARMS_LINE,
        "extra-fail"),
    # (d) two summary lines
    "d-two-summary-lines": lambda t: sub(t, SUMMARY_LINE, SUMMARY_LINE + SUMMARY_LINE,
                                         "two-summaries"),
    # (e1) traceback on stderr with exit 0
    "e1-traceback-stderr-exit0": lambda t: sub(
        t, RETURN_LINE, TRACEBACK + RETURN_LINE, "traceback"),
    # (e2) non-traceback stderr noise, otherwise honest: the declared "empty stderr" clause
    "e2-stderr-noise-exit0": lambda t: sub(t, RETURN_LINE, STDERR_NOISE + RETURN_LINE,
                                           "stderr-noise"),
}

if not (FIX / ".git").exists():
    FIX.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "-C", str(FIX), "init", "-q", "-b", "main"], check=True)
top = subprocess.run(["git", "-C", str(FIX), "rev-parse", "--show-toplevel"],
                     text=True, capture_output=True, check=True).stdout.strip()
if pathlib.Path(top).resolve() != FIX.resolve():
    sys.exit(f"refusing to commit: toplevel {top} != {FIX}")

(FIX / "tools").mkdir(exist_ok=True)
(FIX / "README.md").write_text(
    "MT02 fixture: committed bytes of tools/round81-append-debt.py at "
    "67eddac89f44e768b670301ea0feff06e766f32d with one targeted forgery per commit.\n",
    encoding="utf-8")

revs = {}
for name, fn in VARIANTS.items():
    TARGET.write_text(fn(SOURCE), encoding="utf-8")
    subprocess.run(["git", "-C", str(FIX), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(FIX), "commit", "-q", "-m", f"fixture {name}",
                    "--author", "MT02 <mt02@fixture.invalid>"], check=True)
    revs[name] = subprocess.run(["git", "-C", str(FIX), "rev-parse", "HEAD"], text=True,
                                capture_output=True, check=True).stdout.strip()
    print(f"{name} {revs[name]}")
print(revs)
