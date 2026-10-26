#!/usr/bin/env python3
"""V1Code rig v2: unit + end-to-end probes of the frozen round-46 C1 counter
and check-fragment.py. All raw counter outputs saved to SCR/e-*.out."""
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys

SCR = "/fast/scratch/hyaku/kama-r46/V1Code"
LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
UP = "/fast/scratch/hyaku/kama-r46/L1/llama.git"
FREEZE = "5790944350ae41bfe2ce50934bba59e086e747f4"
BASE = "0163fea2dab3f282ebd70c71da9ab5de4cedf733"
REL = "4d71b42fd87db24b8b7c808c151b713aa4459cfd"
COUNTER_FROZEN = f"{SCR}/counter-frozen.py"
FRAGCHECK = f"{LANE}/.ufo/waves/round-46/tools/check-fragment.py"
LEDGER_PATH = "registry/release-recheck-b11906.tsv"
HEADER = ["id", "path", "pin_commit", "release", "pin_blob", "release_blob",
          "changed", "pin_lines", "release_lines", "witness_pin", "witness_new", "verdict", "note"]

results = []


def rec(name, ok, detail=""):
    results.append((name, ok, detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" :: {detail}" if detail else ""))


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def ws(x):
    return re.sub(r"\s+", " ", x).strip()


# ---------------------------------------------------------------- unit world
P_LINES = [
    "header line one",
    "header line two",
    "router readiness block starts here alpha",
    "the listener answers before any model load beta",
    "store true after start gamma",
    "router readiness block ends delta",
    "filler seven",
    "filler eight",
    "filler nine",
    "survivor line shared tail epsilon",
    "filler eleven",
    "filler twelve",
    "filler thirteen",
    "filler fourteen",
    "filler fifteen",
    "filler sixteen",
    "filler seventeen",
    "filler eighteen",
    "filler nineteen",
    "pin only sentence zeta unique wording",
    "common phrase extra pin words elsewhere",
    "filler twenty two",
    "trailer twenty three",
]
R_LINES = [
    "header line one",
    "header line two",
    "readiness moves after the pool warms up alpha two",
    "single model path loads first then marks ready beta two",
    "gamma two after start the flag flips",
    "delta two common phrase extra pin words",
    "filler seven",
    "filler eight",
    "filler nine",
    "a much longer release line wrapping survivor line shared tail epsilon into prose",
    "filler eleven",
    "filler twelve",
    "filler thirteen",
    "filler fourteen",
    "filler fifteen",
    "filler sixteen",
    "filler seventeen",
    "filler eighteen",
    "filler nineteen",
    "filler twenty one",
    "filler twenty two",
    "brand new release sentence eta only at release",
    "trailer twenty three",
]
WORLD_BLOB = {"pin": "a" * 40, "rel": "b" * 40}
SAME_BLOB = False  # when True the stub serves identical blobs for pin and release
SHOW_FAIL = {"pin": False, "rel": False}


class P:
    def __init__(self, rc, out="", err=""):
        self.returncode, self.stdout, self.stderr = rc, out, err


def fake_git(repo, *args, check=True):
    # the counter queries the FROZEN release commit string, not "rel"
    alias = {"rel": "rel", "pin": "pin", "a" * 40: "pin", ctr.RELEASE_COMMIT: "rel"}
    if args[0] == "rev-parse":
        rev, path = args[-1].split(":", 1)
        rev = alias.get(rev, rev)
        if path == "docs/x.md" and rev in WORLD_BLOB:
            sha = WORLD_BLOB["pin"] if (SAME_BLOB and rev == "rel") else WORLD_BLOB[rev]
            return P(0, sha + "\n")
        return P(1, "", "not found")
    if args[0] == "show":
        rev, path = args[1].split(":", 1)
        rev = alias.get(rev, rev)
        if SHOW_FAIL.get(rev):
            return P(1, "", "boom")
        if path == "docs/x.md" and rev in WORLD_BLOB:
            return P(0, "\n".join(P_LINES if rev == "pin" else R_LINES) + "\n")
        return P(1, "", "not found")
    if args[0] == "cat-file":
        return P(0, "")
    raise AssertionError(f"unexpected git call {args}")


spec = importlib.util.spec_from_file_location("ctr", COUNTER_FROZEN)
ctr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ctr)
ctr.git = fake_git
RELKEY = ctr.RELEASE_COMMIT  # the frozen release commit the counter actually queries

ENT = {"path": "docs/x.md", "pin": "pin",
       "cells": ["S001",
                 "src https://github.com/ggml-org/llama.cpp/blob/1111111111111111111111111111111111111111/docs/x.md #L3-L6",
                 "code", "A", "claim words", "anchor lines 3-6",
                 "statement", "mined", "2026-10-26", "on-release", "corpus/knowledge/k.md"]}


def lr(pin_lines, rel_lines, wp, wn, verdict, note, pin_blob=None, rel_blob=None, changed="1"):
    return dict(zip(HEADER, ["S001", "docs/x.md", "pin", "b11906",
                             pin_blob or WORLD_BLOB["pin"], rel_blob or WORLD_BLOB["rel"],
                             changed, pin_lines, rel_lines, wp, wn, verdict, note]))


ENT_EQ = json.loads(json.dumps(ENT))
ENT_EQ["cells"][1] = "src https://github.com/ggml-org/llama.cpp/blob/1111111111111111111111111111111111111111/docs/x.md #L7-L9"
ENT_EQ["cells"][5] = "anchor lines 7-9"

WP = ws("the listener answers before any model load beta")
WN = ws("single model path loads first then marks ready beta two")
LONG_NOTE = "reworded upstream at b11906; statement re-read and still true per note"

ok, why = ctr.check_row(ENT_EQ, lr("7-9", "7-9", "-", "-", "holds", "x"), "up")
rec("U1 holds equal ranges valid", ok is True, str(why))
ok, why = ctr.check_row(ENT, lr("3-6,7-9", "3-6,-", "-", "-", "holds", "x"), "up")
rec("U2 holds rejects dash release range", ok is False and "text-equal" in why, str(why))
ok, why = ctr.check_row(ENT, lr("3-6", "3-6", WP, WN, "holds-reworded", LONG_NOTE), "up")
rec("U3 holds-reworded valid", ok is True, str(why))
ok, why = ctr.check_row(ENT, lr("3-6", "3-6", WP, ws("common phrase extra pin words"),
                                "holds-reworded", LONG_NOTE), "up")
rec("U4 witness_new present in pin file rejected", ok is False and "witness_new" in why, str(why))
ok, why = ctr.check_row(ENT, lr("3-6", "3-6", ws("pin only sentence zeta unique wording"),
                                WN, "holds-reworded", LONG_NOTE), "up")
rec("U5 witness_pin outside ranges rejected", ok is False and "witness_pin" in why, str(why))
ok, why = ctr.check_row(ENT, lr("3-6,10", "-,-", WP, "-", "removed", LONG_NOTE), "up")
rec("U6 removed passes despite substring survivor (soundness gap)", ok is True, str(why))
ok, why = ctr.check_row(ENT, lr("3-10", "-", ws("filler seven"), "-", "removed", LONG_NOTE), "up")
rec("U7 removed rejects witness present in release file", ok is False and "witness_pin" in why, str(why))
SAME_BLOB = True
ok, why = ctr.check_row(ENT_EQ, lr("7-9", "7-9", "-", "-", "unchanged-file", "x",
                                   rel_blob=WORLD_BLOB["pin"], changed="0"), "up")
rec("U8a unchanged-file valid", ok is True, str(why))
ok, why = ctr.check_row(ENT_EQ, lr("7-9", "7-9", WP, "-", "unchanged-file", "x",
                                   rel_blob=WORLD_BLOB["pin"], changed="0"), "up")
rec("U8b unchanged-file rejects witnesses", ok is False and "witnesses" in why, str(why))
SAME_BLOB = False
ok, why = ctr.check_row(ENT, lr("3-6,7-9", "3-6,-", WP, WN, "drifted", LONG_NOTE), "up")
rec("U9 drifted with dash element valid", ok is True, str(why))
ok, why = ctr.check_row(ENT, lr("3-6,7-9", "3-6,-", WP, ws("brand new release sentence eta only at release"),
                                "drifted", LONG_NOTE), "up")
rec("U9b drifted witness_new outside R rejected", ok is False and "witness_new" in why, str(why))
ok, why = ctr.check_row(ENT, lr("3-6", "3-6", WP, WN, "holds-reworded", LONG_NOTE), "up")
rec("U10 covered cited lines ok (control)", ok is True, str(why))
ENT2 = json.loads(json.dumps(ENT))
ENT2["cells"][5] = "anchor lines 3-6 and line 20"
ok, why = ctr.check_row(ENT2, lr("3-6", "3-6", WP, WN, "holds-reworded", LONG_NOTE), "up")
rec("U10b strong cited line 20 uncovered rejected", ok is False and "cited" in why, str(why))
SHOW_FAIL["pin"] = True
try:
    ctr.check_row(ENT, lr("3-6", "3-6", WP, WN, "holds-reworded", LONG_NOTE), "up")
    rec("U11 show-None raises nothing", False, "no exception")
except AttributeError as e:
    rec("U11 show-None raises AttributeError (exit-1 crash class)", True, repr(e))
SHOW_FAIL["pin"] = False
rec("U12a ranges 1-81 rejected", ctr.ranges("1-81", False) is None)
rec("U12b ranges 0 rejected", ctr.ranges("0", False) is None)
rec("U12c ranges dash without allow rejected", ctr.ranges("-", False) is None)
rec("U12d ranges inverted rejected", ctr.ranges("5-4", False) is None)
rec("U12e ranges dash allowed in release", ctr.ranges("-", True) == [None])
rec("U12f empty spec None", ctr.ranges("", False) is None)
ok, why = ctr.check_row(ENT, lr("3-6", "3-6", WP, WN, "holds-reworded", "short"), "up")
rec("U13 note < 40 rejected", ok is False and "note" in why, str(why))
SAME_BLOB = True
ok, why = ctr.check_row(ENT_EQ, lr("7-9", "7-9", "-", "-", "holds", "x",
                                   rel_blob=WORLD_BLOB["pin"], changed="0"), "up")
rec("U14 holds needs changed=1", ok is False and "changed=1" in why, str(why))
SAME_BLOB = False
ent_fb = {"path": "docs/x.md", "pin": "a" * 40,
          "cells": ["S001", "src https://github.com/ggml-org/llama.cpp/blob/master/docs/x.md",
                    "code", "A", "claim", "commit " + "a" * 40 + " lines 3-6",
                    "statement", "mined", "2026-10-26", "on-release", "k.md"]}
d15 = lr("3-6", "3-6", WP, WN, "holds-reworded", LONG_NOTE)
d15["pin_commit"] = "a" * 40
ok, why = ctr.check_row(ent_fb, d15, "up")
rec("U15 non-hex ref pin from anchor cell", ok is True, str(why))

# ---------------------------------------------------------------- end-to-end
os.makedirs(f"{SCR}/fix", exist_ok=True)


def fixture_clone(name):
    d = f"{SCR}/fix/{name}"
    shutil.rmtree(d, ignore_errors=True)
    r = run(["git", "clone", "-q", "--shared", "--no-checkout", LANE, d])
    assert r.returncode == 0, r.stderr
    r = run(["git", "-C", d, "checkout", "-q", "--detach", FREEZE])
    assert r.returncode == 0, r.stderr
    top = run(["git", "-C", d, "rev-parse", "--show-toplevel"]).stdout.strip()
    assert os.path.realpath(top) == os.path.realpath(d), top
    for k, v in (("user.name", "rig"), ("user.email", "rig@fixture.invalid"), ("commit.gpgsign", "false")):
        run(["git", "-C", d, "config", k, v])
    return d


def commit_all(d, msg):
    run(["git", "-C", d, "add", "-A"])
    r = run(["git", "-C", d, "commit", "-qm", msg])
    assert r.returncode == 0, r.stderr
    return run(["git", "-C", d, "rev-parse", "HEAD"]).stdout.strip()


def counter(repo, tip, upstream, out=None, tag="e"):
    cmd = [sys.executable, COUNTER_FROZEN, "--repo", repo, "--tip", tip, "--upstream", upstream]
    if out:
        cmd += ["--out", out]
    r = run(cmd)
    with open(f"{SCR}/{tag}.out", "w") as fh:
        fh.write(f"rc={r.returncode}\nstdout:\n{r.stdout}\nstderr:\n{r.stderr}")
    return r


def parse(out):
    m = re.search(r"pop=(\d+) rows=(\d+) valid=(\d+) unverified=(\d+).*?flags_missing=(\d+) "
                  r"section=(\d) newrow=(\d) met=(True|False)", out)
    return m.groups() if m else None


d = fixture_clone("base")
r = counter(d, FREEZE, UP, out=f"{SCR}/e1-receipt.out", tag="e1")
g = parse(r.stdout)
rec("E1 freeze tip matches frozen control (91/0/0/91 flags0 sec0 newrow0 metFalse)",
    g == ("91", "0", "0", "91", "0", "0", "0", "False"), f"got {g} rc={r.returncode}")
rec("E1 exit code 1", r.returncode == 1, f"rc={r.returncode}")
rec("E1 --out receipt equals stdout", open(f"{SCR}/e1-receipt.out").read() == r.stdout)
r = counter(d, "0123456789abcdef0123456789abcdef01234567", UP, tag="e2a")
rec("E2a bad tip exit 2 + could-not-evaluate",
    r.returncode == 2 and "could-not-evaluate" in r.stderr, r.stderr.strip()[:120])
r = counter(d, FREEZE, d, tag="e2b")
rec("E2b upstream missing b11906 exit 2",
    r.returncode == 2 and "could-not-evaluate" in r.stderr, r.stderr.strip()[:120])

# E3 newrow leg
SECTION_MD = "\n## Round-46 release re-verification\n\n- S001 probe line for the section.\n"
ROW_BASEID = ("| S001 | duplicate probe rechecked at b11906 4d71b42fd87db24b8b7c808c151b713aa4459cfd"
              " | docs | A | probe | lines 3-6 | probe statement | mined | 2026-10-26 | on-release | x |\n")
ROW_NEWID = ("| S901 | fresh probe row opened at b11906 4d71b42fd87db24b8b7c808c151b713aa4459cfd"
             " | docs | A | probe | lines 3-6 | probe statement | mined | 2026-10-26 | on-release | x |\n")
ROW_NOTOKEN = ("| S902 | fresh probe row opened at b11906 without commit token"
               " | docs | A | probe | lines 3-6 | probe statement | mined | 2026-10-26 | on-release | x |\n")


def sources_with(rows):
    src = run(["git", "-C", d, "show", f"{FREEZE}:corpus/SOURCES.md"]).stdout
    return src + SECTION_MD + "".join(rows)


for name, rows, want in (("E3a", [ROW_BASEID], "0"),
                         ("E3b", [ROW_NEWID], "1"),
                         ("E3c", [ROW_NOTOKEN], "0"),
                         ("E3d", [ROW_BASEID, ROW_NEWID], "1")):
    dd = fixture_clone("nr-" + name[3:].lower())
    with open(f"{dd}/corpus/SOURCES.md", "w") as fh:
        fh.write(sources_with(rows))
    tip = commit_all(dd, name)
    r = counter(dd, tip, UP, tag=name.lower())
    g = parse(r.stdout)
    rec(f"{name} newrow={want}", g is not None and g[6] == want and g[5] == "1",
        f"got {g} rc={r.returncode}")

# E4 ledger variants for S037 (real bytes)
PIN = "704366d76f8748cf9ad3df62a464bfcc8d1ae6ad"
SRCP = "tools/server/server.cpp"
pb = run(["git", "-C", UP, "rev-parse", f"{PIN}:{SRCP}"]).stdout.strip()
rb = run(["git", "-C", UP, "rev-parse", f"{REL}:{SRCP}"]).stdout.strip()
pin_txt = run(["git", "-C", UP, "show", f"{PIN}:{SRCP}"]).stdout
rel_txt = run(["git", "-C", UP, "show", f"{REL}:{SRCP}"]).stdout
pl = pin_txt.splitlines()
rl = rel_txt.splitlines()
pr = [(440, 462), (493, 515)]
P_txt = ws(" ".join(" ".join(pl[a - 1:b]) for a, b in pr))
R_txt = ws(" ".join(" ".join(rl[a - 1:b]) for a, b in pr))
RF, PF = ws(rel_txt), ws(pin_txt)


def pick(lines, in_set, not_in):
    for x in lines:
        c = ws(x)
        if len(c) >= 12 and c in in_set and c not in not_in:
            return c
    return None


wp = pick([x for a, b in pr for x in pl[a - 1:b]], P_txt, RF)
wn = pick([x for a, b in pr for x in rl[a - 1:b]], R_txt, PF)
print(f"i  witnesses: wp={wp!r} wn={wn!r}")
assert wp and wn, "witness picking failed"
NOTE40 = "router start-up block was rewritten upstream; statement re-read and still holds"
ROW = dict(zip(HEADER, ["S037", SRCP, PIN, "b11906", pb, rb, "1" if pb != rb else "0",
                        "440-462,493-515", "440-462,493-515", "-", "-", "holds", "n"]))


def write_ledger(dd, row):
    os.makedirs(f"{dd}/registry", exist_ok=True)
    with open(f"{dd}/{LEDGER_PATH}", "w") as fh:
        fh.write("\t".join(HEADER) + "\n")
        fh.write("\t".join(row[h] for h in HEADER) + "\n")


d = fixture_clone("ledger")
USED_BY = ["corpus/knowledge/llamacpp-loading-lifecycle.md", "corpus/knowledge/endpoint-identity.md",
           "corpus/knowledge/served-identity-crosswalk.md", "corpus/knowledge/runtime-health-surface-matrix.md"]
existing = [u for u in USED_BY if run(["git", "-C", d, "cat-file", "-e", f"{FREEZE}:{u}"]).returncode == 0]
print(f"i  S037 used-by existing at freeze: {len(existing)}/4")
CASES = []
CASES.append(("E4a holds-on-changed-file", dict(ROW, verdict="holds", witness_pin="-", witness_new="-", note="n"),
              False, "text-equal"))
CASES.append(("E4b holds-reworded valid", dict(ROW, verdict="holds-reworded", witness_pin=wp, witness_new=wn, note=NOTE40),
              True, None))
CASES.append(("E4c drifted valid + flags_missing", dict(ROW, verdict="drifted", witness_pin=wp, witness_new=wn, note=NOTE40),
              True, None))
CASES.append(("E4d removed rejected while file alive",
              dict(ROW, verdict="removed", release_lines="-,-", witness_pin=wp, witness_new="-", note=NOTE40),
              False, "pin text still present"))
CASES.append(("E4e wrong blob", dict(ROW, verdict="holds", pin_blob="1" * 40, witness_pin="-", witness_new="-", note="n"),
              False, "blob mismatch"))
for name, row, want_ok, want_reason in CASES:
    write_ledger(d, row)
    tip = commit_all(d, name)
    r = counter(d, tip, UP, tag=name.lower().replace(" ", "-"))
    g = parse(r.stdout)
    det = [x for x in r.stdout.splitlines() if x.startswith("detail: S037")]
    inv = [x for x in det if "invalid:" in x]
    valid = (g is not None and g[2] == "1" and not inv) if want_ok else bool(inv)
    reason_ok = want_reason is None or (inv and want_reason in inv[0])
    rec(f"{name}", valid and reason_ok, f"got {g} detail={det} rc={r.returncode}")
    if name == "E4c drifted valid + flags_missing":
        want_flags = str(1 + len(existing))
        rec("E4c flags_missing = section(1) + used-by(n)",
            g is not None and g[4] == want_flags, f"flags_missing={g[4] if g else '?'} want {want_flags}")

# E5/E6 check-fragment.py
CHK = f"{SCR}/chk"


def frag(rows, path):
    with open(path, "w") as fh:
        fh.write("\t".join(HEADER) + "\n")
        fh.write("".join(rows))


os.makedirs(CHK, exist_ok=True)
frag(["\t".join(["S999", SRCP, PIN, "b11906", pb, rb, "1", "440-462,493-515", "440-462,493-515",
                 "-", "-", "holds", "note irrelevant"]) + "\n"], f"{SCR}/frag-s999.tsv")
r = run([sys.executable, FRAGCHECK, f"{SCR}/frag-s999.tsv", CHK, UP])
rec("E5 check-fragment prints VALID for non-population id S999 (false positive)",
    "VALID S999 holds" in r.stdout and r.returncode == 0, r.stdout.strip()[:200])
frag(["\t".join(["S037", SRCP, PIN, "b11906", "1" * 40, rb, "1", "440-462,493-515", "440-462,493-515",
                 "-", "-", "holds", "note irrelevant"]) + "\n"], f"{SCR}/frag-badblob.tsv")
r = run([sys.executable, FRAGCHECK, f"{SCR}/frag-badblob.tsv", CHK, UP])
rec("E6 check-fragment reports counter reason for bad row",
    "detail: S037 invalid: blob mismatch" in r.stdout and "VALID S037" not in r.stdout,
    r.stdout.strip()[:200])

frag(["\t".join([ROW[h] for h in HEADER]).replace("\t-\t-\tholds\tn", "\t" + wp + "\t" + wn + "\tholds-reworded\t" + NOTE40) + "\n"],
     f"{SCR}/frag-ok.tsv")
r = run([sys.executable, FRAGCHECK, f"{SCR}/frag-ok.tsv", CHK, UP])
rec("E6b check-fragment happy path prints VALID S037 holds-reworded",
    "VALID S037 holds-reworded" in r.stdout and r.returncode == 0, r.stdout.strip()[:200])

r = run([sys.executable, FRAGCHECK, f"{SCR}/frag-ok.tsv", f"{LANE}/.ufo/waves/round-46/w1/out/V1Code-probe", UP])
rec("E8 check-fragment refuses scratch inside the lane",
    "refusing: scratch inside the lane" in r.stdout and r.returncode == 2, r.stdout.strip()[:120])

# header equality between check-fragment and the frozen counter
import importlib.util as _ilu
_sp = _ilu.spec_from_file_location("fc", FRAGCHECK)
_fc = _ilu.module_from_spec(_sp); _sp.loader.exec_module(_fc)
rec("E9 check-fragment HEADER equals counter HEADER", _fc.HEADER == "\t".join(ctr.HEADER), _fc.HEADER[:60])

# E7 flags leg with real drifted row and used-by knowledge files
d = fixture_clone("flags")
src = run(["git", "-C", d, "show", f"{FREEZE}:corpus/SOURCES.md"]).stdout
with open(f"{d}/corpus/SOURCES.md", "w") as fh:
    fh.write(src + "\n## Round-46 release re-verification\n\n- S037 re-verified at b11906 (4d71b42fd87db24b8b7c808c151b713aa4459cfd): drifted.\n")
write_ledger(d, dict(ROW, verdict="drifted", witness_pin=wp, witness_new=wn, note=NOTE40))
for u in existing:
    with open(f"{d}/{u}", "a") as fh:
        fh.write(f"\n- S037 re-verified at b11906 (4d71b42fd87db24b8b7c808c151b713aa4459cfd).\n")
tip = commit_all(d, "flags all present")
r = counter(d, tip, UP, tag="e7a")
g = parse(r.stdout)
det = [x for x in r.stdout.splitlines() if "not flagged" in x or "not listed" in x]
rec("E7a drifted flagged everywhere -> flags_missing=0", g is not None and g[4] == "0" and not det,
    f"got {g} det={det}")
u0 = existing[0]
body = open(f"{d}/{u0}").read().replace(f"\n- S037 re-verified at b11906 (4d71b42fd87db24b8b7c808c151b713aa4459cfd).\n", "")
with open(f"{d}/{u0}", "w") as fh:
    fh.write(body)
tip = commit_all(d, "flags one removed")
r = counter(d, tip, UP, tag="e7b")
g = parse(r.stdout)
rec("E7b removing one flag line -> flags_missing=1 with detail",
    g is not None and g[4] == "1" and f"not flagged in {u0}" in r.stdout, f"got {g}")

print("\n==== summary ====")
bad = [x for x in results if not x[1]]
print(f"{len(results) - len(bad)}/{len(results)} checks passed")
for n, okv, dt in bad:
    print(f"FAILED: {n} :: {dt}")
