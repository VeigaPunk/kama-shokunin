#!/usr/bin/env python3
"""round72-round-scope.py mutant family.

Two detectors per mutant:
  selftest  -> the tool's own fixture battery (`--selftest --repo <lane>`)
  fixtures  -> 11 independent runs on fixtures built to separate the frozen cases
               (incl. the boundary the module's own battery does not carry: an
               untracked directory for -uall, and a non-ignored record inside the
               wave dir for the `!!` filter).
Verdict is baseline-relative: killed iff some observable (exit / findings count /
named case set) differs from the pristine run on the same fixture.
"""
from __future__ import annotations

import json
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

RUNS = [
    ("clean", "clean", []),
    ("label-missing", "label-missing", []),
    ("label-wrong", "label-wrong", []),
    ("label-later", "label-later", []),
    ("stray", "stray", []),
    ("stray-dir", "stray-dir", []),
    ("wave-uncommitted", "wave-uncommitted", []),
    ("ignored", "ignored", []),
    ("ignored-root", "ignored-root", []),
    ("rename", "rename", []),
    ("allow-exact", "stray", ["--allow", "stray-note.md"]),
    ("allow-dir", "wave-record", ["--allow", ".ufo/waves/round-72/records/"]),
]

EXPECT = {
    "clean": (0, 0, []),
    "label-missing": (1, 1, ["label"]),
    "label-wrong": (1, 1, ["label"]),
    "label-later": (1, 1, ["label"]),
    "stray": (1, 1, ["stray"]),
    "stray-dir": (1, 2, ["stray"]),
    "wave-uncommitted": (1, 1, ["stray"]),
    "ignored": (1, 1, ["ignored"]),
    "ignored-root": (0, 0, []),
    "rename": (1, 2, ["stray"]),
    "allow-exact": (0, 0, []),
    "allow-dir": (0, 0, []),
}

MUTANTS = [
    ("S1", "drop the `!! ` filter (every wave-dir record counts as ignored)",
     '''        if not record.strip() or record[:2] != "!!":
            continue''',
     '''        if not record.strip():
            continue'''),
    ("S2", "swap -uall for plain status in the stray scan",
     '''    proc = _git(root, "status", "--porcelain", "-uall")''',
     '''    proc = _git(root, "status", "--porcelain")'''),
    ("S3", "drop the round-label case from evaluate()",
     '''    findings.extend(_label_findings(root, round_no, tip))
''', ''''''),
    ("S4", "treat every path as a finding (an allow-listed path is uncommitted too)",
     '''        for path in _record_paths(record):
            if not _allowed(path, allow):
                findings.append(_finding("stray", "{} status={}".format(path, status)))''',
     '''        for path in _record_paths(record):
            if True:
                findings.append(_finding("stray", "{} status={}".format(path, status)))'''),
    ("S5", "ignore the --ignored flag (only ordinary status records are read)",
     '''    proc = _git(root, "status", "--porcelain", "-uall", "--ignored", "--", wave_rel)''',
     '''    proc = _git(root, "status", "--porcelain", "-uall", "--", wave_rel)'''),
    ("S6", "accept a heading anywhere in the plan (not the first heading)",
     '''def _first_heading(text: str) -> str | None:
    for raw in text.splitlines():
        match = _HEADING_RE.match(raw)
        if match:
            return match.group(2).strip()
    return None''',
     '''def _first_heading(text: str) -> str | None:
    found = None
    for raw in text.splitlines():
        match = _HEADING_RE.match(raw)
        if match:
            found = match.group(2).strip()
    return found'''),
    ("S7", "exit 0 even when findings are named",
     '''        "exit": 0 if not findings else 1,''',
     '''        "exit": 0,'''),
    ("S9", "count only the destination path of a rename record",
     '''    if " -> " in body:
        old, new = body.rsplit(" -> ", 1)
        return [_cunquote(old), _cunquote(new)]''',
     '''    if " -> " in body:
        old, new = body.rsplit(" -> ", 1)
        return [_cunquote(new)]'''),
    ("S8", "drop the wave-dir pathspec from the ignored scan (whole-repo ignored paths)",
     '''    proc = _git(root, "status", "--porcelain", "-uall", "--ignored", "--", wave_rel)''',
     '''    proc = _git(root, "status", "--porcelain", "-uall", "--ignored")'''),
]

SCOPE_LINE = D.SCOPE_LINE
SCOPE_FIND = D.SCOPE_FIND


def one_run(tool: Path, repo: Path, extra: list[str]) -> dict:
    rc, text = D.run([sys.executable, tool, "--repo", repo, "--round", 72, "--tip", "master",
                      *extra], cwd=tool.parent)
    m = SCOPE_LINE.search(text)
    return {"exit": rc, "findings": int(m.group(3)) if m else None,
            "cases": sorted(set(SCOPE_FIND.findall(text))),
            "tail": [ln for ln in text.strip().splitlines()[-2:]]}


def observe(tool: Path) -> dict:
    obs = {label: one_run(tool, FIX / f"scope-{case}" / "repo", extra)
           for label, case, extra in RUNS}
    rc, text = D.run([sys.executable, tool, "--selftest", "--repo", LANE], cwd=tool.parent,
                     timeout=900)
    m = D.GATE_SELF if False else None
    import re
    sel = re.search(r"ROUND_SCOPE_SELFTEST pass=(\d+) fail=(\d+)", text)
    obs["_selftest"] = {"exit": rc, "line": sel.group(0) if sel else None,
                        "tail": [ln for ln in text.strip().splitlines()[-3:]]}
    return obs


def deviations(base: dict, obs: dict) -> list[str]:
    bad = []
    for label, case, _ in RUNS:
        b, o = base[label], obs[label]
        for key in ("exit", "findings", "cases"):
            if b[key] != o[key]:
                bad.append(f"{label}:{key}={o[key]!r}!={b[key]!r}")
    if base["_selftest"]["exit"] != obs["_selftest"]["exit"]:
        bad.append(f"selftest:exit={obs['_selftest']['exit']}!={base['_selftest']['exit']}")
    return bad


def conformance(obs: dict) -> list[str]:
    bad = []
    for label, (want_exit, want_n, want_cases) in EXPECT.items():
        o = obs[label]
        if o["exit"] != want_exit:
            bad.append(f"{label}:exit={o['exit']}!={want_exit}")
        if o["findings"] != want_n:
            bad.append(f"{label}:findings={o['findings']}!={want_n}")
        if o["cases"] != want_cases:
            bad.append(f"{label}:cases={o['cases']}!={want_cases}")
    if obs["_selftest"]["exit"] != 0:
        bad.append(f"selftest exit={obs['_selftest']['exit']}")
    return bad


def main() -> int:
    LOGS.mkdir(parents=True, exist_ok=True)
    src = LANE / "tools/round72-round-scope.py"
    pristine = MUT / "pristine-scope" / "round72-round-scope.py"
    pristine.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, pristine)
    base = observe(pristine)
    nonconf = conformance(base)
    (LOGS / "scope-baseline.json").write_text(json.dumps(base, indent=2), encoding="utf-8")
    print(f"BASELINE sha={sha(src)[:16]} nonconforming={nonconf or 'none'}")
    rows = []
    for mid, desc, old, new in MUTANTS:
        try:
            mut = apply(pristine, mid, old, new)
        except Exception as exc:  # noqa: BLE001
            rows.append(Row(mid, "round72-round-scope.py", desc, "ERROR", "-", str(exc)))
            print(f"{mid} ERROR {exc}")
            continue
        obs = observe(mut)
        dev = deviations(base, obs)
        (LOGS / f"{mid}.json").write_text(json.dumps(obs, indent=2), encoding="utf-8")
        (LOGS / f"{mid}.log").write_text(
            f"# {mid} {desc}\n## deviation\n" + "\n".join(dev or ["none"]) + "\n",
            encoding="utf-8")
        verdict = "killed" if dev else "survived"
        cmd = ("python3 mut/%s/round72-round-scope.py --repo <fixture> --round 72 --tip master"
               " (11 fixtures) + --selftest --repo <lane>") % mid
        rows.append(Row(mid, "round72-round-scope.py", desc, verdict, cmd,
                        "; ".join(dev) or "no observable differed from pristine"))
        print(f"{mid} {verdict}: {'; '.join(dev) or 'no observable differed'}")
    write_row(rows, S / "rows-scope.jsonl")
    return 0


if __name__ == "__main__":
    sys.exit(main())
