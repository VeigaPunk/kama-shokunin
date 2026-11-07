#!/usr/bin/env python3
"""Round-93 C2 pre-freeze control battery (run from the lane root).

Every case grades SKILL.md at BASE + the (mutated) candidate section, and corpus/SOURCES.md at BASE + the
candidate rows S600-S603, through --skill-file/--sources-file (prints skill=override; such a run can never
meet the predicate). Expected outcome per case is named before the run; a case is as_expected when the
named finding appears in the counter output.
P0  candidate as drafted                          -> unbound=0 missing=0 derived_disagree=0 decisions_bound=2
V1  R16/R17 carry the round-92 R01/R08 decisions, no overriding rows -> decisions_bound=0
V2  row P11 (arg.cpp:4613, --embd-gemma-default port 8011) dropped  -> missing=1
V3  a fabricated row for arg.cpp:4614                                -> fabricated=1
V4  P13 condition names --fim-qwen-3b-default (wrong preset)         -> derived_disagree=1
V5  P11 scope LLAMA_EXAMPLE_SERVER only (drops EMBEDDING)            -> derived_disagree=1
V6  P11 value 8012                                                   -> P11 unbound value-literal
V7  P36 (AIP override) relabelled copies                             -> R16 unbound overriding-set
V8  P09 text altered to `params.port = 9931;`                        -> P09 unbound text
V9  P20 (gpt-oss-20b n_parallel 2) left out of R17 and its decision  -> R17 unbound overriding-set
V10 corrupt archive (first 1 MiB of the pinned one)                  -> exit 2 could-not-evaluate
L1  DISCLOSED LIMIT: P47 (a trace string) relabelled n_parallel/overrides/4 AND added to R17 -> binds
    (the counter cannot tell a string from an assignment; that is the K2 reviewer read)
Usage: c2-forgeries.py <scratch> <pinned archive>
"""
import os
import re
import subprocess
import sys
from pathlib import Path

BASE = "5af794958b0fc08f574aa2e67650282269549b02"
COUNTER = os.environ.get("C2_COUNTER", "tools/round93-setter-rows.py")
C = Path(".ufo/waves/round-93/controls")
scratch, archive = Path(sys.argv[1]), Path(sys.argv[2])
scratch.mkdir(parents=True, exist_ok=True)
skill0 = subprocess.run(["git", "show", f"{BASE}:SKILL.md"], capture_output=True, check=True).stdout.decode()
src0 = subprocess.run(["git", "show", f"{BASE}:corpus/SOURCES.md"], capture_output=True, check=True).stdout.decode()
sec = (C / "c2-candidate-section.md").read_text()
srcs = src0 + (C / "c2-candidate-sources.md").read_text()


def row(text, rid):
    m = re.search(r"^\| " + rid + r" \|.*$", text, re.M)
    assert m, rid
    return m.group(0)


def cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def put(text, rid, idx, val):
    old = row(text, rid)
    c = cells(old)
    c[idx] = val
    return text.replace(old, "| " + " | ".join(c) + " |")


def sub(text, old, new):
    assert text.count(old) == 1, old
    return text.replace(old, new)


r92_r01 = ("a llama-server started without `--port` (or `LLAMA_ARG_PORT`) listens on 9931 at this pin; a registry row "
           "pinning another port for such a unit must cite the argv or environment that sets it")
r92_r08 = "a llama-server outside the router role started without `-np` runs 4 slots with a unified KV cache"
v1 = put(put(sec, "R16", 4, "-"), "R17", 4, "-")
v1 = put(put(v1, "R16", 5, r92_r01), "R17", 5, r92_r08)
v3row = "| P99 | common/arg.cpp | 4614 | `x` | port | LLAMA_EXAMPLE_SERVER | invented | overrides | 1 | S596 |"
v9 = put(sub(sec, "P03, P12, P20, P22 |", "P03, P12, P22 |"), "R17", 5,
         cells(row(sec, "R17"))[5].replace("P20 `--gpt-oss-20b-default` and ", ""))
l1 = put(put(put(put(sec, "P47", 4, "n_parallel"), "P47", 7, "overrides"), "P47", 8, "4"), "P47", 6, "trace")
l1 = sub(l1, "P03, P12, P20, P22 |", "P03, P12, P20, P22, P47 |")
l1 = put(l1, "R17", 5, cells(row(l1, "R17"))[5] + " (P47)")
cases = {
    "P0": (sec, "unbound=0 missing=0 duplicates=0 fabricated=0", "decisions_bound=2", 1),
    "V1": (v1, "decisions_bound=0", None, 1),
    "V2": (sub(sec, row(sec, "P11") + "\n", ""), "missing=1", None, 1),
    "V3": (sub(sec, row(sec, "P12") + "\n", row(sec, "P12") + "\n" + v3row + "\n"), "fabricated=1", None, 1),
    "V4": (put(sec, "P13", 6, cells(row(sec, "P13"))[6].replace("--fim-qwen-1.5b-default", "--fim-qwen-3b-default")),
           "derived_disagree=1", None, 1),
    "V5": (put(sec, "P11", 5, "LLAMA_EXAMPLE_SERVER"), "derived_disagree=1", None, 1),
    "V6": (put(sec, "P11", 8, "8012"), "SETTER_ROW P11 unbound value-literal", None, 1),
    "V7": (put(sec, "P36", 7, "copies"), "SETTER_DECISION R16 unbound overriding-set", None, 1),
    "V8": (put(sec, "P09", 3, "`params.port = 9931;`"), "SETTER_ROW P09 unbound text", None, 1),
    "V9": (v9, "SETTER_DECISION R17 unbound overriding-set", None, 1),
    "V10": (sec, "could-not-evaluate", None, 2),
    "L1": (l1, "unbound=0 missing=0 duplicates=0 fabricated=0", "decisions_bound=2", 1),
}
bad_archive = scratch / "bad.tar.gz"
bad_archive.write_bytes(archive.read_bytes()[: 1 << 20])
fails = 0
for name, (section, want, want2, rc_want) in cases.items():
    sk = scratch / f"{name}-SKILL.md"
    sk.write_text(skill0 + "\n" + section)
    so = scratch / f"{name}-SOURCES.md"
    so.write_text(srcs)
    p = subprocess.run([sys.executable, COUNTER, "--repo", ".", "--rev", BASE,
                        "--work", str(scratch / name), "--archive", str(bad_archive if name == "V10" else archive),
                        "--skill-file", str(sk), "--sources-file", str(so)], capture_output=True, text=True)
    out = p.stdout
    ok = want in out and (want2 is None or want2 in out) and p.returncode == rc_want
    fails += 0 if ok else 1
    print(f"C2_CONTROL {name} as_expected={int(ok)} rc={p.returncode} want={want!r}{'' if want2 is None else ' + ' + repr(want2)}")
    for l in out.splitlines():
        if not l.startswith("SETTER_ROW ") or " unbound " in l:
            print(f"  {l}")
print(f"C2_CONTROLS total={len(cases)} as_expected={len(cases) - fails}")
sys.exit(0 if fails == 0 else 1)
