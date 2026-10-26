#!/usr/bin/env python3
"""M1Ctr mutation campaign driver - round48-append-audit-v3-check.py (C1 counter).

For each mutant: apply one minimal replacement to a copy of the pristine
counter, run it on four inputs (lane tip 380bcdff, lane base 33e0058,
v2-relabel control, drop-scorecard control), restore the pristine bytes on the
mutant path, and classify killed / survived against the pristine references.
Artifacts: OUT/runs/*.txt (raw stdout per run), OUT/results.json.
"""
import concurrent.futures as cf
import hashlib
import json
import os
import re
import subprocess
import sys

S = "/fast/scratch/hyaku/kama-r48/M1Ctr"
OUT = "/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/M1Ctr"
LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
PRISTINE = os.path.join(S, "pristine.py")
TIP = "380bcdff9c8af06997c482f6eb03db926a794a2b"
BASE = "33e005827742b29772b153cda036ec9f27f653be"
ENV = dict(os.environ, TMPDIR=S)
HEX = re.compile(r"\b[0-9a-f]{7,40}\b")


def norm(t):
    return HEX.sub("H", t)


def rp(d):
    return subprocess.run(["git", "-C", d, "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()


INPUTS = [
    ("tip", os.path.join(S, "lane"), TIP),
    ("base", os.path.join(S, "lane"), BASE),
    ("v2relabel", os.path.join(S, "ctl-v2-relabel"), rp(os.path.join(S, "ctl-v2-relabel"))),
    ("dropscore", os.path.join(S, "ctl-drop-scorecard"), rp(os.path.join(S, "ctl-drop-scorecard"))),
]

# (name, area, old, new) - each old must occur exactly once in the pristine source.
MUTANTS = [
    ("A1-threshold-21", "threshold", r"THRESHOLD = 20", r"THRESHOLD = 21"),
    ("A2-threshold-19", "threshold", r"THRESHOLD = 20", r"THRESHOLD = 19"),
    ("A3-threshold-le", "threshold", "if nd < THRESHOLD:", "if nd <= THRESHOLD:"),
    ("B1-hunk-regex-comma", "hunk-position parse",
     r'''m = re.match(rb"^@@ -(\d+)(?:,(\d+))? \+\d+(?:,\d+)? @@", ln)''',
     r'''m = re.match(rb"^@@ -(\d+),(\d+) \+\d+(?:,\d+)? @@", ln)'''),
    ("B2-hunk-count-minus1", "hunk-position parse",
     "pos.extend(range(start, start + cnt))", "pos.extend(range(start, start + cnt - 1))"),
    ("B3-hunk-plus-side", "hunk-position parse",
     r'''m = re.match(rb"^@@ -(\d+)(?:,(\d+))? \+\d+(?:,\d+)? @@", ln)''',
     r'''m = re.match(rb"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@", ln)'''),
    ("C1-neg-drop-notappendonly", "NEG list",
     r'NEG = ("not append-only", "not append only", "no longer append", "never append-only")',
     r'NEG = ("not append only", "no longer append", "never append-only")'),
    ("C2-neg-first-only", "NEG list",
     "or any(n in low for n in NEG):", "or any(n in low for n in NEG[:1]):"),
    ("C3-neg-check-dropped", "NEG list",
     'if not ("append-only" in low or "append only" in low) or any(n in low for n in NEG):',
     'if not ("append-only" in low or "append only" in low):'),
    ("D1-token-wildcard-base", "token()",
     'return parts[-2] if len(parts) > 1 else ""', 'return parts[-1] if len(parts) > 1 else ""'),
    ("D2-token-keep-ext", "token()",
     'return base.rsplit(".", 1)[0] if "." in base else base', "return base"),
    ("E1-binds-drop-selfdecl", "binds() self-declaration",
     "return fnmatch.fnmatchcase(decl_path, pattern) or (bool(tok) and tok in low)",
     "return bool(tok) and tok in low"),
    ("E2-binds-eq-not-fnmatch", "binds() self-declaration",
     "return fnmatch.fnmatchcase(decl_path, pattern) or (bool(tok) and tok in low)",
     "return decl_path == pattern or (bool(tok) and tok in low)"),
    ("F1-region-title-hash-dropped", "region regex",
     'if not titles or not all(t.startswith("## ") for t in titles):', "if not titles:"),
    ("F2-region-pointer-plus1", "region regex",
     "kind, body, ptr = m.group(1), m.group(2), (m.group(3), int(m.group(4)))",
     "kind, body, ptr = m.group(1), m.group(2), (m.group(3), int(m.group(4)) + 1)"),
    ("G1-required-drop-errata", "REQUIRED regions",
     '"registry/history/DELTA.md": ("*",), "registry/report-landing-errata.tsv": ("*",),',
     '"registry/history/DELTA.md": ("*",),'),
    ("G2-required-titles-drop-cap", "REQUIRED regions",
     'HEAD_TITLES = {"## Axes", "## Planned", "## Retired", "## Saturation", "## Capabilities"}',
     'HEAD_TITLES = {"## Axes", "## Planned", "## Retired", "## Saturation"}'),
    ("G3-required-kind-only", "REQUIRED regions",
     'if want[0] != reg[0] or (want[0] in ("exempt", "only") and reg[1] != want[1]):',
     'if want[0] != reg[0]:'),
    ("H1-eligible-gt", "eligibility >=",
     "for x in window) >= need:", "for x in window) > need:"),
    ("H2-eligible-always", "eligibility >=",
     "for x in window) >= need:", "for x in window) >= 0:"),
    ("I1-only-filter-dropped", "graded filter only/exempt",
     "if only_prefixes and not any(s is not None and s.startswith(pp) for pp in only_prefixes):",
     "if False and only_prefixes and not any(s is not None and s.startswith(pp) for pp in only_prefixes):"),
    ("I2-exempt-filter-dropped", "graded filter only/exempt",
     "if s in eligible:", "if s in eligible and False:"),
    ("J1-clamp-max0-dropped", "held clamp",
     "h = sum(min(n, max(0, M[l] - K[l])) for l, n in G.items())",
     "h = sum(min(n, M[l] - K[l]) for l, n in G.items())"),
    ("J2-clamp-min-dropped", "held clamp",
     "h = sum(min(n, max(0, M[l] - K[l])) for l, n in G.items())",
     "h = sum(max(0, M[l] - K[l]) for l, n in G.items())"),
    ("K1-restoredby-drop-ng", "restored_by",
     "if by is None and ng and h == ng:", "if by is None and h == ng:"),
    ("K2-best-geq-tie-last", "restored_by",
     "if h > best:", "if h >= best:"),
    ("K3-restoredbest-swap", "restored_by",
     '"restored_best": best_c, "restored_by": by,', '"restored_best": best, "restored_by": by,'),
    ("K4-restoredby-geq", "restored_by",
     "if by is None and ng and h == ng:", "if by is None and ng and h >= ng:"),
    ("L1-status-labels-swapped", "status classes",
     'status = "restored" if best == ng else ("unrestored" if best == 0 else "partial")',
     'status = "restored" if best == ng else ("partial" if best == 0 else "unrestored")'),
    ("L2-status-partial-dead", "status classes",
     '("unrestored" if best == 0 else "partial")', '("unrestored" if best < ng else "partial")'),
    ("M2-regressed-le", "regressed formula",
     'e["held_at_to"] < e["restored_max"]', 'e["held_at_to"] <= e["restored_max"]'),
    ("M3-regressed-partial-dropped", "regressed formula",
     'e["status"] in ("restored", "partial") and e["held_at_to"]',
     'e["status"] in ("restored",) and e["held_at_to"]'),
    ("N1-exit-always0", "exit derivation", "return 0 if met else 1", "return 0"),
    ("N2-exit-always1", "exit derivation", "return 0 if met else 1", "return 1"),
    ("N3-met-drop-stable", "exit derivation",
     "met = bool(sel and con and lane and fix and stab)", "met = bool(sel and con and lane and fix)"),
    ("N4-selftest-threshold-1", "exit derivation",
     "int(m.group(1)) >= 20", "int(m.group(1)) >= 1"),
    ("N5-met-drop-fixture", "exit derivation",
     "met = bool(sel and con and lane and fix and stab)", "met = bool(sel and con and lane and stab)"),
    ("N6-derivedexit-drop-regressed", "exit derivation",
     'code = 1 if (s["partial"] or s["unrestored"] or s["regressed"] or s["vanished"] or bad) else 0',
     'code = 1 if (s["partial"] or s["unrestored"] or s["vanished"] or bad) else 0'),
    ("O1-s1-expect-deleted19", "fixture expectations",
     '{"deleted": 20, "graded": 20, "ungraded": 0, "restored_max": 0,',
     '{"deleted": 19, "graded": 20, "ungraded": 0, "restored_max": 0,'),
    ("O2-s6-expect-restmax10", "fixture expectations",
     '{"deleted": 40, "graded": 40, "restored_max": 20, "restored_best": c2,',
     '{"deleted": 40, "graded": 40, "restored_max": 10, "restored_best": c2,'),
    ("O3-s11-nev-3", "fixture expectations",
     '"bad_declarations": 0}, 0, 2)', '"bad_declarations": 0}, 0, 3)'),
    ("O4-nt-eq-10", "nt == 11", "fix = nf == 0 and nt == 11", "fix = nf == 0 and nt == 10"),
    ("O6-nt-check-dropped", "nt == 11", "fix = nf == 0 and nt == 11", "fix = nf == 0"),
    ("P1-stablekeys-drop-best", "stable keys",
     '("deleted", "graded", "ungraded", "restored_max", "restored_best")):',
     '("deleted", "graded", "ungraded", "restored_max")):'),
    ("Q1-ung-geq0", "ungraded_lines > 0",
     'and ung > 0 and rc["exit"] == 0)', 'and ung >= 0 and rc["exit"] == 0)'),
    ("R1-K-nosub", "recompute internals", "K = collections.Counter(pl) - D", "K = collections.Counter(pl)"),
    ("R3-psec-child", "recompute internals", "psec = sections(pl)", "psec = sections(B.get(c, f))"),
    ("R4-sections-hash1", "recompute internals", 'if ln.startswith(b"## "):', 'if ln.startswith(b"# "):'),
    ("R5-sections-nostrip", "recompute internals",
     'cur = ln.rstrip(b"\\r").decode("utf-8", "replace").rstrip()',
     'cur = ln.rstrip(b"\\r").decode("utf-8", "replace")'),
    ("R7-files-unsorted", "recompute internals",
     "files = sorted({t for t in tree if any(fnmatch.fnmatchcase(t, r[\"path\"]) for r in rows)})",
     "files = {t for t in tree if any(fnmatch.fnmatchcase(t, r[\"path\"]) for r in rows)}"),
    ("R8-vanished-empty", "recompute internals",
     'vanished = sorted(t for t in hist if t not in set(files) and any(fnmatch.fnmatchcase(t, r["path"]) for r in rows))',
     "vanished = []"),
    ("R8b-vanished-list-memb", "recompute internals",
     'vanished = sorted(t for t in hist if t not in set(files) and any(fnmatch.fnmatchcase(t, r["path"]) for r in rows))',
     'vanished = sorted(t for t in hist if t not in files and any(fnmatch.fnmatchcase(t, r["path"]) for r in rows))'),
]


def run_counter(py, repo, tip, tag):
    d = os.path.join(S, "runs", tag)
    os.makedirs(d, exist_ok=True)
    try:
        p = subprocess.run([sys.executable, py, "--repo", repo, "--tip", tip, "--scratch", d],
                           capture_output=True, text=True, timeout=900, env=ENV)
        return {"exit": p.returncode, "stdout": p.stdout, "stderr": p.stderr[-800:]}
    except subprocess.TimeoutExpired:
        return {"exit": "timeout", "stdout": "", "stderr": "timeout after 900s"}


def sha(b):
    return hashlib.sha256(b).hexdigest()


def main():
    os.makedirs(os.path.join(OUT, "runs"), exist_ok=True)
    src_bytes = open(PRISTINE, "rb").read()
    pristine_sha = sha(src_bytes)
    src = src_bytes.decode()
    results = {"pristine_sha256": pristine_sha, "inputs": {}, "mutants": {}}

    # baseline: pristine on every input
    refs = {}
    with cf.ThreadPoolExecutor(max_workers=4) as ex:
        futs = {ex.submit(run_counter, PRISTINE, repo, tip, f"pristine__{name}"): (name, repo, tip)
                for name, repo, tip in INPUTS}
        for f in cf.as_completed(futs):
            name = futs[f][0]
            r = f.result()
            refs[name] = r
            with open(os.path.join(OUT, "runs", f"pristine__{name}.txt"), "w") as fh:
                fh.write(f"exit={r['exit']}\n{r['stdout']}")
            results["inputs"][name] = {"repo": futs[f][1], "tip": futs[f][2], "exit": r["exit"],
                                       "first_line": r["stdout"].split("\n")[0]}
    print("BASELINES:")
    for name, r in refs.items():
        print(f"  {name}: exit={r['exit']} | {r['stdout'].splitlines()[0] if r['stdout'] else '(no stdout)'}")

    baseline_ok = (refs["tip"]["exit"] == 0 and "met=True" in refs["tip"]["stdout"]
                   and all(refs[c]["exit"] == 1 and "met=False" in refs[c]["stdout"]
                           for c in ("base", "v2relabel", "dropscore")))
    results["baseline_ok"] = baseline_ok
    print(f"BASELINE_OK={baseline_ok}")

    def one(mut):
        name, area, old, new = mut
        rec = {"area": area, "old": old, "new": new, "applied": False}
        if src.count(old) != 1:
            rec["apply"] = f"old-string count {src.count(old)} != 1"
            return name, rec
        mut_bytes = src.replace(old, new, 1).encode()
        mpath = os.path.join(S, "mut", f"{name}.py")
        os.makedirs(os.path.join(S, "mut"), exist_ok=True)
        with open(mpath, "wb") as fh:
            fh.write(mut_bytes)
        rec["applied"] = True
        rec["mutant_sha256"] = sha(mut_bytes)
        runs = {}
        with cf.ThreadPoolExecutor(max_workers=4) as ex:
            futs = {ex.submit(run_counter, mpath, repo, tip, f"{name}__{iname}"): iname
                    for iname, repo, tip in INPUTS}
            for f in cf.as_completed(futs):
                runs[futs[f]] = f.result()
        # restore pristine bytes on the mutant path, verify hash
        with open(mpath, "wb") as fh:
            fh.write(src_bytes)
        rec["restored_sha256"] = sha(open(mpath, "rb").read())
        rec["restored_ok"] = rec["restored_sha256"] == pristine_sha
        det, mech = False, []
        for iname, repo, tip in INPUTS:
            r = runs[iname]
            ref = refs[iname]
            with open(os.path.join(OUT, "runs", f"{name}__{iname}.txt"), "w") as fh:
                fh.write(f"exit={r['exit']}\n{r['stdout']}")
            same_exit = r["exit"] == ref["exit"]
            same_out = norm(r["stdout"]) == norm(ref["stdout"])
            first = r["stdout"].split("\n")[0] if r["stdout"] else "(no stdout)"
            runs[iname] = {"exit": r["exit"], "first_line": first,
                           "same_as_pristine": bool(same_exit and same_out)}
            if not (same_exit and same_out):
                det = True
                if iname == "tip":
                    mech.append(f"tip exit {ref['exit']}->{r['exit']}")
                elif r["exit"] == 0 or "met=True" in r["stdout"]:
                    mech.append(f"{iname} leniency flip exit={r['exit']}")
                else:
                    mech.append(f"{iname} output-only exit={ref['exit']}->{r['exit']}")
        rec["runs"] = runs
        if not baseline_ok:
            rec["verdict"] = "inconclusive-baseline"
        elif det:
            rec["verdict"] = "killed"
            rec["mechanism"] = mech
        else:
            rec["verdict"] = "survived"
        return name, rec

    with cf.ThreadPoolExecutor(max_workers=6) as ex:
        for name, rec in ex.map(one, MUTANTS):
            results["mutants"][name] = rec
            print(f"{rec['verdict']:>8} {name} :: {'; '.join(rec.get('mechanism', [])) or rec.get('apply', '')}")

    with open(os.path.join(OUT, "results.json"), "w") as fh:
        json.dump(results, fh, indent=1)
    v = {}
    for rec in results["mutants"].values():
        v[rec["verdict"]] = v.get(rec["verdict"], 0) + 1
    print("SUMMARY:", v)


if __name__ == "__main__":
    sys.exit(main())
