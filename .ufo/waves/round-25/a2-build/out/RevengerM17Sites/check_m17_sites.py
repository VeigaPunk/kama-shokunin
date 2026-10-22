#!/usr/bin/env python3
"""Read-only check of the M17 / M33 refusal sites across pinned revisions.

Reads blobs with `git show <full-rev>:<path>` from the lane object store.
Writes nothing to the lane, the index, refs or the working copy.
Reports: anchor counts per revision, the registered counting command per
registry/auditor pair, refusal sites with their enclosing def, and every
lookup() / bare_objects() call with the peel argument it passes.
"""
import importlib.util
import pathlib
import re
import subprocess
import sys
import tempfile

LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
AUD = "tools/report-landing-audit.py"
MUT = "tests/report-audit/isolation-mutants.py"
REVS = {
    "r23-e876b95": "e876b953e9da28d2dffd29c923052bc626148c27",
    "ed1cc3a": "ed1cc3a342bd801fe2d0f54f7ba2eb4ca42d5f05",
    "92063cf": "92063cfc60e217fa7e2098c568578119b16a1b95",
    "efe58e9": "efe58e96e6cfbef88a0fba9d64505e18b7ad7356",
    "tip-1fc41e3": "1fc41e346853afd98cbd7010af5db4e54dc877f7",
}


def blob(rev, path):
    r = subprocess.run(["git", "-C", LANE, "--no-optional-locks", "show", f"{rev}:{path}"],
                       capture_output=True)
    if r.returncode != 0:
        sys.exit(f"git show {rev}:{path} failed rc={r.returncode}: {r.stderr.decode(errors='replace')}")
    return r.stdout.decode("utf-8")


tmp = pathlib.Path(tempfile.mkdtemp(prefix="m17-sites-"))
audits, registries = {}, {}
for name, rev in REVS.items():
    audits[name] = blob(rev, AUD)
    p = tmp / f"mut-{name}.py"
    p.write_text(blob(rev, MUT), encoding="utf-8")
    spec = importlib.util.spec_from_file_location(f"mut_{name.replace('-', '_')}", p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    registries[name] = mod


def lit(mod, prefix):
    for n, o, r in mod.MUTANTS:
        if n.startswith(prefix):
            return n, o, r
    return None


def positions(src, text):
    return [src.count("\n", 0, m.start()) + 1 for m in re.finditer(re.escape(text), src)]


print("## 1. registered counting command, registry (rows) x auditor (columns)")
for rn, mod in registries.items():
    for an, src in audits.items():
        bad = [n for n, o, _ in mod.MUTANTS if src.count(o) != 1]
        print(f"registry={rn:12s} auditor={an:12s} registered={len(mod.MUTANTS)} stale={len(bad)} {bad}")
print()

print("## 2. anchor literal positions per auditor")
anchors = [
    ("r23 M17 (registry e876b95)", registries["r23-e876b95"], "M17"),
    ("efe58e9 M17 (pre-repair)", registries["efe58e9"], "M17"),
    ("tip M17 (C1 repair)", registries["tip-1fc41e3"], "M17"),
    ("tip M33 (C1 repair)", registries["tip-1fc41e3"], "M33"),
]
for label, mod, pid in anchors:
    n, o, r = lit(mod, pid)
    print(f"## {label}: id={n} anchor={o!r} replacement={r!r}")
    for an, src in audits.items():
        print(f"    auditor={an:12s} count={src.count(o)} lines={positions(src, o)}")
print()

print("## 3. refusal sites ('names a ref') with enclosing def")


def enclosing(lines, n):
    for j in range(n - 1, -1, -1):
        if re.match(r"def \w+\(", lines[j]):
            return lines[j].split("(")[0][4:]
    return None


for an, src in audits.items():
    lines = src.splitlines()
    for i, l in enumerate(lines, 1):
        if "names a ref" in l:
            print(f"    auditor={an:12s} line {i} in def {enclosing(lines, i)}: {l.strip()}")
print()

print("## 4. call sites of lookup() and bare_objects(), with the peel argument")
for an, src in audits.items():
    lines = src.splitlines()
    print(f"    auditor={an}")
    for i, l in enumerate(lines, 1):
        if re.search(r"\b(lookup|bare_objects)\(", l) and not re.match(r"\s*def ", l):
            window = " ".join(x.strip() for x in lines[i - 1:i + 1])
            peel = "^{commit}" in window
            print(f"      {i}: peel={peel!s:5s} {l.strip()[:110]}")
