#!/usr/bin/env python3
"""R41B04 -- fixture blind-spot probe for tools/round41-pinwatch-audit.py (C2 contract leg).

Method
------
The pristine counter source is loaded read-only from the private clone
(/tmp/r41b04-clone, HEAD 24aa1d3485c107f88b8b838892d43ea7587befcf). Feature-
weakened generator variants are derived by exact single-site string patches;
every patch consumes the same rng draws as the original code, so case i of a
weakened generator is the pristine case i minus exactly one feature (paired
design). A composed variant (pins-current + no-unreadable) probes
interactions between two weakenings.

The counter's own contract leg is then re-run -- same loop shape, same
functions (make_case / reference / pins_text / run_tool / CASES), same
comparison `got != want or gcode != wcode` -- against candidate pin-watch
tools placed at <export>/tools/pin-watch.py:

  real             lane tools/pin-watch.py at tip (ground truth, from clone)
  ref              oracle: delegates to the counter's reference() via
                   $R41B04_AUDIT, so it cannot drift from the oracle
  w1-peeled        counts peeled ^{} lines (multiset `newer`)  [tasking example]
  w2-match         re.match instead of fullmatch (decoys become release tags)
  w3-semver        hardcodes v(\d+)\.(\d+)\.(\d+), ignores tag_regex
  w4-noerr         unreadable tag list treated as empty -> missing, not error
  w5-alwayscurrent reports every pin current without reading any tag list
  w6-exit          correct statuses, exit code never 2

A generator feature is load-bearing for a candidate iff the candidate FAILS
the contract leg under the pristine generator but PASSES under the variant
that removes that feature.

The reference() oracle is contract-defined and is NOT weakened in any
variant; `ref` and `real` passing every variant is the check that a
weakened fixture stays self-consistent (weakening must not corrupt the
oracle, or the leg's verdicts are inconclusive).

Usage: python3 harness.py matrix|sweep
"""
import importlib.util
import json
import os
import random
import re
import shutil
import subprocess
import sys
import tempfile

CLONE = "/tmp/r41b04-clone"
AUDIT = os.path.join(CLONE, "tools", "round41-pinwatch-audit.py")
WORK = "/tmp/r41b04"
VAR_DIR = os.path.join(WORK, "variants")
CAND_DIR = os.path.join(WORK, "cands")
RES_DIR = os.path.join(WORK, "results")

SRC = open(AUDIT, encoding="utf-8").read()

# name -> list of (old, new); each `old` must occur exactly once in the source.
# All replacements keep the rng draw sequence identical to the pristine code.
PATCHES = {
    "no-decoys":     [("for t in tags + decoys:", "for t in tags:")],
    "no-peeled":     [("if rng.random() < 0.5:", "if (rng.random() < 0.5) and False:")],
    "semver-only":   [("semver = rng.random() < 0.6", "semver = (rng.random() < 0.6) or True")],
    "no-unreadable": [("if rng.random() < 0.3:  # an engine whose tag list is unreadable",
                       "if (rng.random() < 0.3) and False:  # an engine whose tag list is unreadable")],
    "pins-current":  [('mode = rng.choice(["current", "behind", "behind", "missing"])',
                       'mode = rng.choice(["current", "current", "current", "current"])')],
}
COMPOSED = "pins-current+no-unreadable"

GENERATORS = ["pristine", "no-decoys", "no-peeled", "semver-only",
              "no-unreadable", "pins-current", COMPOSED]
CANDIDATES = ["real", "ref", "w1-peeled", "w2-match", "w3-semver",
              "w4-noerr", "w5-alwayscurrent", "w6-exit"]


def build_variants():
    os.makedirs(VAR_DIR, exist_ok=True)
    paths = {"pristine": AUDIT}
    spec = dict(PATCHES)
    spec[COMPOSED] = PATCHES["pins-current"] + PATCHES["no-unreadable"]
    for name, patches in spec.items():
        src = SRC
        for old, new in patches:
            cnt = src.count(old)
            if cnt != 1:
                raise SystemExit(f"patch site not unique for {name}: {cnt}x {old!r}")
            src = src.replace(old, new)
        p = os.path.join(VAR_DIR, name + ".py")
        with open(p, "w", encoding="utf-8") as f:
            f.write(src)
        paths[name] = p
    return paths


_MODS = {}


def get_mod(paths, name):
    if name not in _MODS:
        spec = importlib.util.spec_from_file_location(
            "r41b04_gen_" + name.replace("+", "_"), paths[name])
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        _MODS[name] = mod
    return _MODS[name]


SEMVER = r"v(\d+)\.(\d+)\.(\d+)"


def case_features(rows, texts):
    """Per-case feature census, derived from the fixture bytes themselves."""
    f = {"engines": len(rows), "decoy_lines": 0, "peeled": 0, "nonsemver": 0,
         "unreadable": 0, "behind": 0, "missing": 0, "current": 0}
    for r in rows:
        if r["regex"] != SEMVER:
            f["nonsemver"] += 1
        text = texts.get(r["engine"])
        if text is None:
            f["unreadable"] += 1
            continue
        rx = re.compile(r["regex"])
        keyed = {}
        for line in text.splitlines():
            parts = line.split("\t")
            if len(parts) != 2:
                continue
            ref = parts[1].strip()
            if not ref.startswith("refs/tags/"):
                continue
            name = ref[len("refs/tags/"):]
            if name.endswith("^{}"):
                f["peeled"] += 1
                continue
            m = rx.fullmatch(name)
            if m:
                keyed[name] = tuple(int(g) for g in m.groups())
            else:
                f["decoy_lines"] += 1
        if r["pin"] not in keyed:
            f["missing"] += 1
        else:
            k = keyed[r["pin"]]
            f["behind" if any(v > k for v in keyed.values()) else "current"] += 1
    return f


def contract_leg(mod, run_tool, export, seed):
    """Mirror of evaluate()'s contract section in round41-pinwatch-audit.py."""
    rng = random.Random(seed)
    fails, feats = [], []
    for i in range(mod.CASES):
        rows, texts = mod.make_case(rng, i)
        feats.append(case_features(rows, texts))
        d = tempfile.mkdtemp(prefix=f"case{i}-", dir=export)
        with open(os.path.join(d, "pins.tsv"), "w") as f:
            f.write(mod.pins_text(rows))
        os.makedirs(os.path.join(d, "tags"))
        for eng, t in texts.items():
            with open(os.path.join(d, "tags", f"{eng}.txt"), "w") as f:
                f.write(t)
        want, wcode = mod.reference(rows, texts)
        try:
            got, gcode, err = run_tool(export, ["check", "--pins", os.path.join(d, "pins.tsv"),
                                                "--tags-dir", os.path.join(d, "tags")], timeout=60)
        except subprocess.TimeoutExpired:
            got, gcode, err = [], None, "timeout"
        if got != want or gcode != wcode:
            fails.append({"case": i, "want_exit": wcode, "want": want,
                          "got_exit": gcode, "got": got, "stderr": (err or "").strip()[:200]})
    return (not fails), fails, feats


def make_export(cand):
    export = tempfile.mkdtemp(prefix=f"r41b04-exp-{cand}-")
    os.makedirs(os.path.join(export, "tools"))
    shutil.copy(os.path.join(CAND_DIR, cand, "tools", "pin-watch.py"),
                os.path.join(export, "tools", "pin-watch.py"))
    return export


def run_legs(paths, legs, seeds):
    pristine = get_mod(paths, "pristine")
    run_tool = pristine.run_tool
    os.environ["R41B04_AUDIT"] = AUDIT
    exports = {c: make_export(c) for c in {c for c, _ in legs}}
    rows, feat_seen = [], {}
    try:
        for cand, gen in legs:
            mod = get_mod(paths, gen)
            for seed in seeds:
                ok, fails, feats = contract_leg(mod, run_tool, exports[cand], seed)
                agg = {}
                for f in feats:
                    for k, v in f.items():
                        agg[k] = agg.get(k, 0) + v
                feat_seen[(gen, seed)] = agg
                rows.append({"cand": cand, "gen": gen, "seed": seed,
                             "contract": int(ok), "nfails": len(fails),
                             "features": agg, "fails": fails[:2]})
    finally:
        for e in exports.values():
            shutil.rmtree(e, ignore_errors=True)
    return rows, feat_seen


def pivot(rows):
    grid = {}
    for r in rows:
        grid.setdefault((r["cand"], r["gen"]), {})[r["seed"]] = r["contract"]
    lines = []
    for (cand, gen) in sorted(grid):
        d = grid[(cand, gen)]
        seeds = sorted(d)
        codes = "".join("P" if d[s] == 1 else "F" for s in seeds)
        lines.append(f"{cand:18s} {gen:28s} {sum(d.values())}/{len(seeds)} {codes}")
    return "\n".join(lines)


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "matrix"
    paths = build_variants()
    if which == "matrix":
        legs = [(c, g) for c in CANDIDATES for g in GENERATORS]
        seeds = [41, 1, 2, 3]
        out = os.path.join(RES_DIR, "matrix.json")
    else:
        legs = ([("w1-peeled", g) for g in ("pristine", "no-peeled")]
                + [("w2-match", g) for g in ("pristine", "no-decoys")]
                + [("w3-semver", g) for g in ("pristine", "semver-only")]
                + [("w4-noerr", g) for g in ("pristine", "no-unreadable")]
                + [("w5-alwayscurrent", g) for g in ("pristine", "pins-current", COMPOSED)]
                + [("w6-exit", g) for g in ("pristine", "pins-current", "no-unreadable", COMPOSED)])
        seeds = list(range(1, 31))
        out = os.path.join(RES_DIR, "sweep.json")
    rows, feat_seen = run_legs(paths, legs, seeds)
    os.makedirs(RES_DIR, exist_ok=True)
    with open(out, "w") as f:
        json.dump(rows, f, indent=1)
    print(pivot(rows))
    print("--- feature census per (generator, seed) ---")
    for (gen, seed) in sorted(feat_seen, key=lambda x: (GENERATORS.index(x[0]), x[1])):
        a = feat_seen[(gen, seed)]
        print(f"FEAT gen={gen:28s} seed={seed:3d} engines={a['engines']:3d} "
              f"decoy_lines={a['decoy_lines']:3d} peeled={a['peeled']:3d} "
              f"nonsemver={a['nonsemver']:2d} unreadable={a['unreadable']:2d} "
              f"behind={a['behind']:2d} missing={a['missing']:2d} current={a['current']:2d}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
