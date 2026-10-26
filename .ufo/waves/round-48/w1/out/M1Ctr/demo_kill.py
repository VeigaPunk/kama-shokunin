#!/usr/bin/env python3
"""M1Ctr demo: the proposed fixture-leg recompute cross-check kills the survivors.

Patch = add a counter-recompute-vs-tool diff inside fixture_leg (the same
diff_result the lane leg uses). Run patch-only (must stay met=True) and
patch+survivor-mutant for each killable survivor (must flip to met=False).
"""
import concurrent.futures as cf
import json
import os
import re
import subprocess
import sys

S = "/fast/scratch/hyaku/kama-r48/M1Ctr"
OUT = "/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/M1Ctr"
TIP = "380bcdff9c8af06997c482f6eb03db926a794a2b"
LANE = os.path.join(S, "lane")
ENV = dict(os.environ, TMPDIR=S)

src = open(os.path.join(S, "pristine.py")).read()

PATCH_OLD = '''            s = j.get("summary") or {}
            for k, v in summ.items():
                if s.get(k) != v:
                    probs.append(f"summary {k}={s.get(k)} want {v}")
'''
PATCH_NEW = '''            s = j.get("summary") or {}
            for k, v in summ.items():
                if s.get(k) != v:
                    probs.append(f"summary {k}={s.get(k)} want {v}")
            try:
                rows_fx, _why = parse_contract(open(os.path.join(repo, CONTRACT),
                                                    encoding="utf-8", errors="replace").read())
                if rows_fx is not None:
                    rcx = recompute(repo, "HEAD", rows_fx)
                    fxm = diff_result(j, rcx, code, [], "fxrecomp")
                    if fxm:
                        probs.append(f"counter-recompute-vs-tool mismatches {fxm}")
            except EvalError as exc:
                probs.append(f"counter recompute failed: {exc}")
'''

SURVIVORS = {
    "A1-threshold-21": (r"THRESHOLD = 20", r"THRESHOLD = 21"),
    "A2-threshold-19": (r"THRESHOLD = 20", r"THRESHOLD = 19"),
    "A3-threshold-le": ("if nd < THRESHOLD:", "if nd <= THRESHOLD:"),
    "C1-neg-drop-notappendonly": (
        r'NEG = ("not append-only", "not append only", "no longer append", "never append-only")',
        r'NEG = ("not append only", "no longer append", "never append-only")'),
    "C3-neg-check-dropped": (
        'if not ("append-only" in low or "append only" in low) or any(n in low for n in NEG):',
        'if not ("append-only" in low or "append only" in low):'),
    "I1-only-filter-dropped": (
        "if only_prefixes and not any(s is not None and s.startswith(pp) for pp in only_prefixes):",
        "if False and only_prefixes and not any(s is not None and s.startswith(pp) for pp in only_prefixes):"),
    "J1-clamp-max0-dropped": (
        "h = sum(min(n, max(0, M[l] - K[l])) for l, n in G.items())",
        "h = sum(min(n, M[l] - K[l]) for l, n in G.items())"),
    "K1-restoredby-drop-ng": ("if by is None and ng and h == ng:", "if by is None and h == ng:"),
    "L1-status-labels-swapped": (
        'status = "restored" if best == ng else ("unrestored" if best == 0 else "partial")',
        'status = "restored" if best == ng else ("partial" if best == 0 else "unrestored")'),
    "L2-status-partial-dead": (
        '("unrestored" if best == 0 else "partial")', '("unrestored" if best < ng else "partial")'),
}


def run(py, tag):
    d = os.path.join(S, "demo_runs", tag)
    os.makedirs(d, exist_ok=True)
    p = subprocess.run([sys.executable, py, "--repo", LANE, "--tip", TIP, "--scratch", d],
                       capture_output=True, text=True, timeout=900, env=ENV)
    return p.returncode, p.stdout


def build(name, mut):
    text = src
    if mut is not None:
        old, new = mut
        assert text.count(old) == 1, (name, "survivor old count", text.count(old))
        text = text.replace(old, new, 1)
    assert text.count(PATCH_OLD) == 1, (name, "patch old count", text.count(PATCH_OLD))
    return text.replace(PATCH_OLD, PATCH_NEW, 1)


jobs = [("patch-only", None)] + [(n, m) for n, m in SURVIVORS.items()]
os.makedirs(os.path.join(S, "demo"), exist_ok=True)
res = {}
with cf.ThreadPoolExecutor(max_workers=6) as ex:
    futs = {}
    for name, mut in jobs:
        py = os.path.join(S, "demo", f"{name}.py")
        open(py, "w").write(build(name, mut))
        futs[ex.submit(run, py, name)] = name
    for f in cf.as_completed(futs):
        name = futs[f]
        code, out = f.result()
        first = out.split("\n")[0] if out else "(no stdout)"
        fx = [ln for ln in out.splitlines() if "fixture" in ln or "fxrecomp" in ln][:6]
        res[name] = {"exit": code, "first_line": first, "fixture_detail": fx}
        print(f"exit={code} {name}\n  {first}")
        for ln in fx:
            print(f"    {ln[:200]}")
json.dump(res, open(os.path.join(OUT, "demo_fixture_recompute.json"), "w"), indent=1)
