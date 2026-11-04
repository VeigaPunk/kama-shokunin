#!/usr/bin/env python3
"""round72-receipt-tip-binding.py mutant family.

Detectors: the tool's own selftest plus 7 repo fixtures that separate the three
finding classes and the two expansion rules (brace alternatives, header window).
Baseline-relative: killed iff an observable (exit / cited / bound / unbound /
shifted / stale / named class set) differs from pristine on the same fixture.
"""
from __future__ import annotations

import json
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import detectors as D
from harness_lite import Row, apply, sha, write_row

LANE = Path("/home/vgpnk/Projects/shokunin/kama-shokunin")
S = Path("/fast/scratch/hyaku/kama-r72/MT01Mutants")
FIX = S / "fixtures"
LOGS = S / "logs"
MUT = S / "mut"

LINE = re.compile(r"RECEIPT_TIP_BINDING round=(\d+) cited=(\d+) bound=(\d+) "
                  r"unbound=(\d+) shifted=(\d+) stale=(\d+)")
FIND = re.compile(r"RECEIPT_TIP_FINDING (unbound|shifted|stale) (\S+)")
SELF = re.compile(r"RECEIPT_TIP_BINDING_SELFTEST pass=(\d+) fail=(\d+)")

CASES = ("clean", "unbound", "shifted", "stale", "nonancestor", "brace", "late-header",
         "conflict")

EXPECT = {
    "clean": (0, (1, 1, 0, 0, 0), []),
    "unbound": (1, (1, 0, 1, 0, 0), ["unbound"]),
    "shifted": (1, (1, 0, 0, 1, 0), ["shifted"]),
    "stale": (1, (1, 0, 0, 0, 1), ["stale"]),
    "nonancestor": (1, (1, 0, 0, 1, 0), ["shifted"]),
    "brace": (0, (2, 2, 0, 0, 0), []),
    "late-header": (1, (1, 0, 1, 0, 0), ["unbound"]),
    "conflict": (1, (1, 0, 1, 0, 0), ["unbound"]),
}

MUTANTS = [
    ("B1", "drop the ancestor check (header rev need only be a commit)",
     '''    if not _is_ancestor(repo, rev, tip):
        return "shifted", "header rev {} is not an ancestor of {}".format(rev[:12], tip[:12])
''', ''''''),
    ("B2", "parse the delta with the wrong rev order (tip..rev instead of rev..tip)",
     '''    for commit in _rev_list(repo, rev, tip):''',
     '''    for commit in _rev_list(repo, tip, rev):'''),
    ("B3", "skip brace expansion of a cited path",
     '''    for cand in _brace_expand(root):''',
     '''    for cand in [root]:'''),
    ("B4", "accept a tip=/rev= header anywhere in the receipt (not the first 5 lines)",
     '''    window = blob.decode("utf-8", "replace").splitlines()[:HEADER_WINDOW]''',
     '''    window = blob.decode("utf-8", "replace").splitlines()'''),
    ("B5", "count every cited path as bound",
     '''        "bound": cited - sum(counts.values()),''',
     '''        "bound": cited,'''),
    ("B6", "never call a delta shifted (instrument paths are accepted)",
     '''            if not _record_match(changed, specs):''',
     '''            if False:'''),
    ("B7", "treat an absent receipt as bound instead of stale",
     '''    if blob is None:
        return "stale", "absent at {}".format(tip)''',
     '''    if blob is None:
        return "bound", "absent at {}".format(tip)'''),
    ("B9", "accept the first of two conflicting headers instead of rejecting the receipt",
     '''    if len(set(revs)) > 1:
        return None, "conflicting header revisions: {}".format(",".join(sorted(set(revs))))
    return revs[0], ""''',
     '''    return revs[0], ""'''),
    ("B8", "exit 0 even when findings are named",
     '''    result["exit"] = 0 if clean else 1''',
     '''    result["exit"] = 0'''),
]


def one(tool: Path, repo: Path) -> dict:
    rc, text = D.run([sys.executable, tool, "--repo", repo, "--round", 72, "--tip", "master"],
                     cwd=tool.parent)
    m = LINE.search(text)
    return {"exit": rc,
            "counts": list(m.groups()[1:]) if m else None,
            "classes": sorted({c for c, _ in FIND.findall(text)}),
            "tail": [ln for ln in text.strip().splitlines()[-2:]]}


def observe(tool: Path) -> dict:
    obs = {case: one(tool, FIX / f"bind-{case}" / "repo") for case in CASES}
    rc, text = D.run([sys.executable, tool, "--selftest"], cwd=tool.parent, timeout=900)
    m = SELF.search(text)
    obs["_selftest"] = {"exit": rc, "line": m.group(0) if m else None,
                        "tail": [ln for ln in text.strip().splitlines()[-3:]]}
    return obs


def conformance(obs: dict) -> list[str]:
    bad = []
    for case, (want_exit, want_counts, want_classes) in EXPECT.items():
        o = obs[case]
        if o["exit"] != want_exit:
            bad.append(f"{case}:exit={o['exit']}!={want_exit}")
        if o["counts"] != [str(x) for x in want_counts]:
            bad.append(f"{case}:counts={o['counts']}!={list(want_counts)}")
        if o["classes"] != want_classes:
            bad.append(f"{case}:classes={o['classes']}!={want_classes}")
    if obs["_selftest"]["exit"] != 0:
        bad.append(f"selftest exit={obs['_selftest']['exit']}")
    return bad


def deviations(base: dict, obs: dict) -> list[str]:
    bad = []
    for case in CASES:
        for key in ("exit", "counts", "classes"):
            if base[case][key] != obs[case][key]:
                bad.append(f"{case}:{key}={obs[case][key]!r}!={base[case][key]!r}")
    if base["_selftest"]["exit"] != obs["_selftest"]["exit"]:
        bad.append(f"selftest:exit={obs['_selftest']['exit']}!={base['_selftest']['exit']}")
    if base["_selftest"]["line"] != obs["_selftest"]["line"] and obs["_selftest"]["exit"] == 0:
        bad.append(f"selftest:line={obs['_selftest']['line']!r}!=base")
    return bad


def main() -> int:
    LOGS.mkdir(parents=True, exist_ok=True)
    src = LANE / "tools/round72-receipt-tip-binding.py"
    pristine = MUT / "pristine-bind" / "round72-receipt-tip-binding.py"
    pristine.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, pristine)
    base = observe(pristine)
    nonconf = conformance(base)
    (LOGS / "bind-baseline.json").write_text(json.dumps(base, indent=2), encoding="utf-8")
    print(f"BASELINE sha={sha(src)[:16]} nonconforming={nonconf or 'none'}")
    rows = []
    for mid, desc, old, new in MUTANTS:
        try:
            mut = apply(pristine, mid, old, new)
        except Exception as exc:  # noqa: BLE001
            rows.append(Row(mid, "round72-receipt-tip-binding.py", desc, "ERROR", "-", str(exc)))
            print(f"{mid} ERROR {exc}")
            continue
        obs = observe(mut)
        dev = deviations(base, obs)
        (LOGS / f"{mid}.json").write_text(json.dumps(obs, indent=2), encoding="utf-8")
        (LOGS / f"{mid}.log").write_text(
            f"# {mid} {desc}\n## deviation\n" + "\n".join(dev or ["none"]) + "\n",
            encoding="utf-8")
        verdict = "killed" if dev else "survived"
        cmd = ("python3 mut/%s/round72-receipt-tip-binding.py --repo <fixture> --round 72 "
               "--tip master (7 fixtures) + --selftest") % mid
        rows.append(Row(mid, "round72-receipt-tip-binding.py", desc, verdict, cmd,
                        "; ".join(dev) or "no observable differed from pristine"))
        print(f"{mid} {verdict}: {'; '.join(dev) or 'no observable differed'}")
    write_row(rows, S / "rows-bind.jsonl")
    return 0


if __name__ == "__main__":
    sys.exit(main())
