#!/usr/bin/env python3
"""Gate (pre-report-gate.py) mutant family: score the arm-6 wiring.

Detectors (all run on a copy, never on lane bytes):
  A selftest        -> exit 0, `PRE_REPORT_SELFTEST pass=N fail=0`, and case (h) present
  B argv probe      -> exit 0, verdict arms=6, `--round 72` reached the round-scope stub
  C build failure   -> exit 2 (could-not-evaluate), forced with PATH that has no git
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import detectors as D
from harness_lite import Row, apply, pristine_copy, sha, write_row

LANE = Path("/home/vgpnk/Projects/shokunin/kama-shokunin")
S = Path("/fast/scratch/hyaku/kama-r72/MT01Mutants")
LOGS = S / "logs"


def build_failure(tool: Path, tag: str):
    work = S / "gate-buildfail" / tag
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)
    env_path_backup = D.ENV.get("PATH")
    D.ENV["PATH"] = "/nonexistent-bin-dir"
    try:
        rc, text = D.run([sys.executable, tool, "--selftest", "--work", work],
                         cwd=tool.parent, timeout=300)
    finally:
        D.ENV["PATH"] = env_path_backup
    return {"exit": rc, "text": text.strip().splitlines()[-3:]}


def clean_probe(tool: Path) -> dict:
    """The round-clean arm on an untracked DIRECTORY inside the wave dir.

    `-uall` expands it into two records; plain `--porcelain` collapses it into one,
    so this is the observable that separates the two forms (the gate's own selftest
    adds a single file, which both forms count as 1).
    """
    repo = S / "fixtures/gate-uncommitted-dir/repo"
    if not (repo / ".git").exists():
        repo.mkdir(parents=True, exist_ok=True)
        D.run(["git", "init", "-q", "-b", "master", repo])
        (repo / ".ufo/waves/round-72").mkdir(parents=True, exist_ok=True)
        (repo / ".ufo/waves/round-72/committed.txt").write_text("c\n", encoding="utf-8")
        D.run(["git", "-C", repo, "add", "-A"])
        D.run(["git", "-C", repo, "-c", "user.name=fixture", "-c", "user.email=fixture@invalid",
               "-c", "commit.gpgsign=false", "commit", "-q", "-m", "probe"])
    (repo / ".ufo/waves/round-72/newdir").mkdir(parents=True, exist_ok=True)
    (repo / ".ufo/waves/round-72/newdir/a.txt").write_text("a\n", encoding="utf-8")
    (repo / ".ufo/waves/round-72/newdir/b.txt").write_text("b\n", encoding="utf-8")
    rc, text = D.run([sys.executable, tool, "--repo", repo, "--round", 72, "--tip", "master",
                      "--tools-dir", S / "gate-probe-tools"], cwd=tool.parent, timeout=300)
    line = next((ln for ln in text.splitlines() if ln.startswith("PRE_REPORT round=")), None)
    clean = next((ln for ln in text.splitlines() if "round-clean" in ln), None)
    return {"exit": rc, "line": line, "clean": clean}


MUTANTS = [
    ("G1", "gate", "drop the {round} substitution in the gate",
     '''            token.replace("{repo}", repo_path).replace("{tip}", tip)
                 .replace("{round}", str(round_no))''',
     '''            token.replace("{repo}", repo_path).replace("{tip}", tip)'''),
    ("G2", "gate", "return 0 on a fixture-build failure",
     '''    except (RuntimeError, OSError) as exc:
        print(f"PRE_REPORT_SELFTEST could-not-evaluate: {exc}")
        return 2''',
     '''    except (RuntimeError, OSError) as exc:
        print(f"PRE_REPORT_SELFTEST could-not-evaluate: {exc}")
        return 0'''),
    ("G3", "gate", "drop arm 6 from ARM_SPECS (gate stays at five arms)",
     '''    ("round-scope", ("round72-round-scope.py", "--repo", "{repo}", "--round", "{round}",
                     "--tip", "{tip}")),
''', ''''''),
    ("G4", "gate", "swap -uall for plain status in the round-clean arm",
     '''["git", "-C", repo_path, "status", "--porcelain", "-uall", "--", wave_rel]''',
     '''["git", "-C", repo_path, "status", "--porcelain", "--", wave_rel]'''),
]


def main() -> int:
    pristine = pristine_copy()
    rows = []
    base = {
        "selftest": D.gate_selftest(pristine),
        "probe": D.gate_argv_probe(pristine, S / "gate-probe-tools"),
        "buildfail": build_failure(pristine, "pristine"),
        "cleanprobe": clean_probe(pristine),
    }
    (LOGS / "gate-baseline.json").write_text(json.dumps(base, indent=2), encoding="utf-8")

    for mid, tool, desc, old, new in MUTANTS:
        try:
            mut = apply(pristine, mid, old, new)
        except Exception as exc:  # noqa: BLE001
            rows.append(Row(mid, tool, desc, "ERROR", "-", f"apply failed: {exc}"))
            continue
        obs = {
            "selftest": D.gate_selftest(mut),
            "probe": D.gate_argv_probe(mut, S / "gate-probe-tools"),
            "buildfail": build_failure(mut, mid),
            "cleanprobe": clean_probe(mut),
        }
        (LOGS / f"{mid}.json").write_text(json.dumps(obs, indent=2), encoding="utf-8")
        log = LOGS / f"{mid}.log"
        with log.open("w", encoding="utf-8") as fh:
            fh.write(f"# {mid} {desc}\n## pristine\n{json.dumps(base, indent=1)}\n")
            fh.write(f"## mutant\n{json.dumps(obs, indent=1)}\n")
        reasons = []
        if obs["selftest"]["exit"] != 0 or "fail=0" not in (obs["selftest"]["line"] or ""):
            reasons.append(f"SELFTEST exit={obs['selftest']['exit']} {obs['selftest']['line']}")
        if obs["probe"]["exit"] != 0:
            reasons.append(f"PROBE exit={obs['probe']['exit']}")
        if not any("--round" in c and "72" in c for c in obs["probe"]["calls"]):
            reasons.append(f"PROBE calls={obs['probe']['calls']}")
        if obs["buildfail"]["exit"] != 2:
            reasons.append(f"BUILDFAIL exit={obs['buildfail']['exit']} (want 2)")
        if obs["cleanprobe"]["line"] != base["cleanprobe"]["line"]:
            reasons.append(f"CLEANPROBE line={obs['cleanprobe']['line']!r} "
                           f"!= {base['cleanprobe']['line']!r}")
        verdict = "killed" if reasons else "survived"
        cmd = f"python3 mut/{mid}/pre-report-gate.py --selftest  (+ argv probe, + PATH-blind build failure)"
        rows.append(Row(mid, tool, desc, verdict, cmd, "; ".join(reasons) or "no detector differed"))
        print(f"{mid} {verdict}: {'; '.join(reasons) or 'no detector differed'}")

    write_row(rows, S / "rows-gate.jsonl")
    return 0


if __name__ == "__main__":
    sys.exit(main())
