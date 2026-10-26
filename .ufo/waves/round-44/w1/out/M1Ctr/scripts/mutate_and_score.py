#!/usr/bin/env python3
"""M1Ctr mutation battery for the frozen C1 counter round44-release-recheck-audit.py.

Generates single-rule mutants of the pristine counter (never touching the lane file),
runs each mutant on every fixture from fixtures.json, and compares (exit, stdout minus
the tip= line) against the pristine baseline. Classifies each mutant:
  killed-behavioral   exit code or summary line differs on some fixture
  killed-strict-only  only detail lines differ (same exit + summary)
  survived            byte-identical behavior on every fixture
Writes matrix.json and prints a per-mutant report with the killing fixtures.
"""
import concurrent.futures as cf
import difflib, importlib.util, json, os, subprocess, sys

SCRATCH = "/fast/scratch/hyaku/kama-r44/M1Ctr"
LANE = os.path.join(SCRATCH, "lane")
UP = "/fast/scratch/hyaku/kama-r44/shared/llama.cpp"
PRISTINE = os.path.join(LANE, "tools", "round44-release-recheck-audit.py")
MUT = os.path.join(SCRATCH, "mut")
os.makedirs(MUT, exist_ok=True)

src = open(PRISTINE).read()
src_lines = src.splitlines()

# id, rule family, old (exact, must occur once), new, prediction
MUTANTS = [
    ("M01", "blob comparison", '    if lr["pin_blob"] != pb or lr["release_blob"] != rb:',
     '    if lr["pin_blob"] != pb:', "killed by F01"),
    ("M02", "blob comparison", '    if lr["pin_blob"] != pb or lr["release_blob"] != rb:',
     "    if False:", "killed by F01/F02"),
    ("M03", "changed flag", '    changed = "0" if pb == rb else "1"',
     '    changed = "0" if lr["pin_blob"] == lr["release_blob"] else "1"',
     "equivalent: blob check upstreams the same facts"),
    ("M04", "changed flag", '    if lr["changed"] != changed:', "    if False:", "killed by F03"),
    ("M05", "80-line cap", "        if a < 1 or b < a or b - a >= 80:",
     "        if a < 1 or b < a or b - a >= 800:", "killed by F04"),
    ("M06", "range parsing", "        if a < 1 or b < a or b - a >= 80:",
     "        if b < a or b - a >= 80:", "equivalent: no <=79-line pinned file"),
    ("M07", "range parsing", "        if a < 1 or b < a or b - a >= 80:",
     "        if a < 1 or b - a >= 80:", "killed by F32"),
    ("M08", "range parsing", '    pr = ranges(lr["pin_lines"], False)',
     '    pr = ranges(lr["pin_lines"], True)', "killed by IN3 (crash on '-')"),
    ("M09", "20-char pin-range rule",
     '        if len(re.sub(r"\\s", "", "".join(ptext[r[0] - 1:r[1]]))) < 20:',
     '        if len(re.sub(r"\\s", "", "".join(ptext[r[0] - 1:r[1]]))) < 2:', "killed by F05"),
    ("M10", "20-char pin-range rule",
     '        if len(re.sub(r"\\s", "", "".join(ptext[r[0] - 1:r[1]]))) < 20:',
     '        if len(re.sub(r"\\s", "", "".join(ptext[r[0] - 1:r[1]]))) < 0:', "killed by F05"),
    ("M11", "STRONG cited-line coverage", "        if miss:", "        if False:", "killed by F06"),
    ("M12", "WEAK cited-line coverage", "    elif weak and not any(covered(n) for n in weak):",
     "    elif False:", "equivalent: no weak-only population row"),
    ("M13a", "STRONG cited-line coverage", "    strong = {n for n in strong if n <= len(ptext)}",
     "    strong = set(strong)", "equivalent: no beyond-file strong cite"),
    ("M13b", "WEAK cited-line coverage", "    weak = {n for n in weak if n <= len(ptext)}",
     "    weak = set(weak)", "equivalent: no beyond-file weak cite"),
    ("M14", "verdict holds", '        return all(eq), "holds needs every pair text-equal"',
     '        return any(eq), "holds needs every pair text-equal"', "killed by F08"),
    ("M15", "verdict holds-reworded",
     '        return all(r is not None for r in rr) and not all(eq), "holds-reworded rule"',
     '        return all(r is not None for r in rr), "holds-reworded rule"', "killed by F09"),
    ("M16", "verdict holds-reworded", '    if v == "holds-reworded":\n        if len(note) < 20:',
     '    if v == "holds-reworded":\n        if False:', "killed by F10"),
    ("M17", "verdict holds-reworded",
     '        return all(r is not None for r in rr) and not all(eq), "holds-reworded rule"',
     '        return not all(eq), "holds-reworded rule"', "killed by F11"),
    ("M18", "verdict drifted", '        return not all(r is None for r in rr), "drifted rule"',
     '        return True, "drifted rule"', "killed by F12"),
    ("M19", "verdict drifted", '    if v == "drifted":\n        if len(note) < 20:',
     '    if v == "drifted":\n        if False:', "killed by F13"),
    ("M20", "verdict removed", "            if first is None or first in rset:",
     "            if False:", "killed by F14"),
    ("M21", "verdict removed", "        if len(note) < 20 or not all(r is None for r in rr):",
     "        if not all(r is None for r in rr):", "killed by F15"),
    ("M22", "verdict removed", "        if len(note) < 20 or not all(r is None for r in rr):",
     "        if len(note) < 20:", "killed by F16"),
    ("M23", "verdict dispatch", '    return False, "unknown verdict"', '    return True, ""',
     "killed by IN3"),
    ("M24", "release cell", '    if lr["release"] != RELEASE:', "    if False:", "killed by F25"),
    ("M25", "population binding", '    if lr["path"] != path or lr["pin_commit"] != pin:',
     "    if False:", "killed by F26"),
    ("M26", "duplicate-row handling", '                    if d["id"] in ledger:',
     "                    if False:", "killed by F24"),
    ("M27", "duplicate-row handling", '                    ledger[d["id"]] = d',
     '                    ledger.setdefault(d["id"], d)',
     "equivalent: dup flag still invalidates the row"),
    ("M28", "SOURCES section check", "    met = unverified == 0 and missing == 0 and section == 1",
     "    met = unverified == 0 and missing == 0",
     "equivalent: any valid drifted row forces missing>=1 when section absent"),
    ("M29", "SOURCES section check",
     '        section = int(any(SECTION in x and x.startswith("#") for x in tip_src.splitlines()))',
     '        section = int(any(SECTION in x for x in tip_src.splitlines()))', "killed by F22"),
    ("M30", "flag check drifted/removed",
     '            if not any(re.search(rf"\\b{sid}\\b", x) for x in sec_lines):',
     "            if False:", "killed by F17/F21"),
    ("M31", "flag check drifted/removed",
     '                if not any(re.search(rf"\\b{sid}\\b", x) and RELEASE in x for x in body.splitlines()):',
     "                if False:", "killed by F18"),
    ("M32", "flag check drifted/removed",
     '                if not any(re.search(rf"\\b{sid}\\b", x) and RELEASE in x for x in body.splitlines()):',
     '                if not any(re.search(rf"\\b{sid}\\b", x) for x in body.splitlines()):',
     "killed by F19"),
    ("M33", "flag check drifted/removed", '            if lr["verdict"] not in ("drifted", "removed"):',
     '            if lr["verdict"] != "drifted":', "killed by F20"),
    ("M34", "ledger header check", '            if lines and lines[0].split("\\t") == HEADER:',
     "            if lines:", "killed by F23"),
    ("M36", "population filter",
     '        if len(c) != 11 or c[9] != "on-release" or c[7] not in ("mined", "queued"):',
     "        if len(c) != 11:", "killed by IN1 (pop grows)"),
    ("M38", "exit code", "    return 0 if met else 1", "    return 0", "killed by IN1 (exit)"),
    ("M39", "range parsing", "        if r and r[1] > len(rtext):", "        if False:",
     "killed by F27"),
    ("M40", "range parsing", "        if r[1] > len(ptext):", "        if False:", "killed by F28"),
]

built = []
for mid, rule, old, new, pred in MUTANTS:
    n = src.count(old)
    assert n == 1, f"{mid}: old string occurs {n} times"
    mtext = src.replace(old, new)
    path = os.path.join(MUT, f"{mid}.py")
    open(path, "w").write(mtext)
    ln = next(i + 1 for i, x in enumerate(src_lines) if old.splitlines()[0] in x)
    diff = "\n".join(difflib.unified_diff(src_lines, mtext.splitlines(), "pristine", mid, lineterm=""))
    open(os.path.join(MUT, f"{mid}.diff"), "w").write(diff + "\n")
    built.append({"id": mid, "rule": rule, "path": path, "line": ln, "old": old, "new": new,
                  "prediction": pred})
print("mutants built:", len(built))

fx = json.load(open(os.path.join(SCRATCH, "fixtures.json")))
fixtures, baseline = fx["fixtures"], fx["baseline"]


def run(counter, repo, tip):
    p = subprocess.run([sys.executable, counter, "--repo", repo, "--tip", tip, "--upstream", UP],
                       capture_output=True, text=True, timeout=300)
    lines = p.stdout.splitlines()
    return p.returncode, lines[0], lines[1:]  # drop tip= line


def norm(pri):
    return (pri["exit"], tuple(pri["stdout"].splitlines()[1:]))


base_norm = {k: norm(v) for k, v in baseline.items()}


def score_one(arg):
    mid, mpath, name = arg
    fxr = fixtures[name]
    try:
        exitc, tip, rest = run(mpath, fxr["repo"], fxr["tip"])
        bexit, brest = base_norm[name]
        if (exitc, tuple(rest)) != (bexit, brest):
            strict = tuple(rest) == brest and exitc == bexit
            return (mid, name, "strict-only" if strict else "behavioral", exitc, bexit,
                    (rest[0] if rest else "")[:110], (brest[0] if brest else "")[:110])
        return (mid, name, "same", exitc, bexit, "", "")
    except Exception as e:  # timeout/crash outside returncode
        return (mid, name, "behavioral", -1, base_norm[name][0], f"EXC {type(e).__name__}", "")


args = [(m["id"], m["path"], name) for m in built for name in sorted(fixtures)]
print("battery runs:", len(args))
matrix = {}
with cf.ThreadPoolExecutor(max_workers=8) as ex:
    for mid, name, verdict, e, be, mine, theirs in ex.map(score_one, args):
        matrix.setdefault(mid, {})[name] = (verdict, e, be, mine, theirs)

json.dump({"mutants": built, "matrix": matrix}, open(os.path.join(SCRATCH, "matrix.json"), "w"), indent=1)
for m in built:
    mid = m["id"]
    kills = {k: v for k, v in matrix[mid].items() if v[0] != "same"}
    behav = sorted(k for k, v in kills.items() if v[0] == "behavioral")
    strict = sorted(k for k, v in kills.items() if v[0] == "strict-only")
    if behav:
        v = f"killed-behavioral by {','.join(behav[:6])}"
    elif strict:
        v = f"killed-strict-only by {','.join(strict[:6])}"
    else:
        v = "SURVIVED"
    print(f"{mid} [{m['rule']}] line {m['line']}: {v}   (pred: {m['prediction']})")
