#!/usr/bin/env python3
"""R57Item29 independent falsification of the frozen C1 no-op control and predicate.

Builds a throwaway fixture repo, plants battery variants, and runs two checkers:
  frozen   = committed blob  HEAD:tools/round56-prereg-check.py (sha c7b0d787...)
  repair   = current working-tree tools/round56-prereg-check.py copy (sha recorded)

Nothing in the lane is written; the only repo mutated is the scratch fixture.
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import pathlib

LANE = pathlib.Path("/home/vgpnk/Projects/shokunin/kama-shokunin")
SCRATCH = pathlib.Path("/fast/scratch/hyaku/kama-r57/R57Item29ClaimFalsifier")
FIX = SCRATCH / "fixture"
REC = SCRATCH / "receipts"
CHK = SCRATCH / "checkers"

PREREG_REL = ".ufo/waves/round-56/preregistration.json"
BATTERY_REL = "tools/round56-env-leg-battery.py"

ROSTER_LIT = '''ROSTER = {
    "base-old-counter": {"designation": "control", "expected": "missed"},
    "round56-counter": {"designation": "positive-control", "expected": "detected"},
    "m-drop-ldaudit": {"designation": "kill", "expected": "missed"},
}
'''


def run(cmd, cwd=None, env=None):
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, env=env)
    return p.returncode, p.stdout, p.stderr


def sha(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def sha_bytes(b):
    return hashlib.sha256(b).hexdigest()


def git(repo, *args, check=True):
    rc, out, err = run(["git", "-C", str(repo), *args])
    if check and rc != 0:
        raise SystemExit(f"git {' '.join(args)} failed rc={rc}: {err}")
    return rc, out, err


def assert_toplevel(repo):
    rc, out, err = git(repo, "rev-parse", "--show-toplevel")
    top = out.strip()
    if not top or pathlib.Path(top).resolve() != pathlib.Path(repo).resolve():
        raise SystemExit(f"toplevel guard failed: {top!r} != {repo}")
    return top


def reset_fixture():
    if FIX.exists():
        shutil.rmtree(FIX)
    FIX.mkdir(parents=True)
    (FIX / PREREG_REL).parent.mkdir(parents=True, exist_ok=True)
    (FIX / BATTERY_REL).parent.mkdir(parents=True, exist_ok=True)
    git(FIX, "init", "-q")
    git(FIX, "config", "user.name", "r57item29")
    git(FIX, "config", "user.email", "r57item29@invalid")
    assert_toplevel(FIX)


def lane_blob_at(ref, rel):
    rc, out, err = git(LANE, "show", f"{ref}:{rel}")
    if rc != 0:
        raise SystemExit(f"cannot read {rel} at {ref}: {err}")
    return out


def commit_battery(text, msg):
    (FIX / BATTERY_REL).write_text(text)
    git(FIX, "add", BATTERY_REL, PREREG_REL)
    git(FIX, "commit", "-q", "-m", msg)
    rc, out, err = git(FIX, "rev-parse", "HEAD")
    return out.strip()


def run_checker(checker, tip, out_path):
    rc, out, err = run([sys.executable, str(checker), "--repo", str(FIX),
                        "--tip", tip, "--out", str(out_path)])
    body = out + err
    return rc, body


def main():
    for d in (SCRATCH, REC, CHK):
        d.mkdir(parents=True, exist_ok=True)

    report = {
        "python": sys.version.split()[0],
        "lane_head": git(LANE, "rev-parse", "HEAD")[1].strip(),
        "frozen_base": "b89bdab2cc114735ec5d331c6c610134258f7864",
        "scratch": str(SCRATCH),
        "checkers": {},
        "variants": {},
    }

    # --- freeze the two checker sources into scratch (no shared writes) ---
    # frozen = blob at the round-57 freeze base; repair = current committed HEAD.
    frozen_ref = "b89bdab2cc114735ec5d331c6c610134258f7864"
    frozen_src = lane_blob_at(frozen_ref, "tools/round56-prereg-check.py")
    frozen_chk = CHK / "frozen-check.py"
    frozen_chk.write_text(frozen_src)
    repair_ref = "HEAD"
    repair_src = lane_blob_at(repair_ref, "tools/round56-prereg-check.py")
    repair_chk = CHK / "repair-check.py"
    repair_chk.write_text(repair_src)
    report["checkers"]["frozen"] = {
        "path": str(frozen_chk), "sha256": sha(frozen_chk), "ref": frozen_ref,
        "source": f"{frozen_ref}:tools/round56-prereg-check.py",
        "bound_by_round56_prereg_c2": "c7b0d787f348691bbc057114b455545f5abfb0c70ec497e1ad695591f1489853",
    }
    report["checkers"]["repair"] = {
        "path": str(repair_chk), "sha256": sha(repair_chk), "ref": repair_ref,
        "source": "HEAD:tools/round56-prereg-check.py (round-57 repair commit)",
    }
    report["checkers"]["frozen_sha_matches_bound"] = (
        report["checkers"]["frozen"]["sha256"]
        == report["checkers"]["frozen"]["bound_by_round56_prereg_c2"])
    if not report["checkers"]["frozen_sha_matches_bound"]:
        raise SystemExit("frozen checker digest does not match the frozen digest")
    report["battery_and_prereg_at_base_match_head"] = {
        rel: (sha_bytes(lane_blob_at(frozen_ref, rel).encode())
              == sha_bytes(lane_blob_at(repair_ref, rel).encode()))
        for rel in (PREREG_REL, BATTERY_REL)
    }

    # --- fixture: prereg + genuine battery at base ---
    reset_fixture()
    prereg_text = lane_blob_at("b89bdab2cc114735ec5d331c6c610134258f7864", PREREG_REL)
    (FIX / PREREG_REL).write_text(prereg_text)
    genuine = lane_blob_at("b89bdab2cc114735ec5d331c6c610134258f7864", BATTERY_REL)

    variants = {}
    variants["genuine"] = genuine
    variants["v1_roster_only"] = ROSTER_LIT + '''def main():
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''
    variants["v2_declare_print"] = ROSTER_LIT + '''def main():
    print("mismatches=0 executed=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''
    variants["v3_dead_calls"] = ROSTER_LIT + '''def run(label, counter, expected, out):
    return True


def main():
    if False:
        run("base-old-counter", None, "missed", None)
        run("round56-counter", None, "detected", None)
        run("m-drop-ldaudit", None, "missed", None)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''
    variants["v4_roster_plus_kill_call"] = ROSTER_LIT + '''def run(label, counter, expected, out):
    return True


def main():
    if False:
        run("base-old-counter", None, "missed", None)
        run("round56-counter", None, "detected", None)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''
    keyword = genuine
    pairs = [
        ('run("base-old-counter", OLD, "missed", OUT / "base-c1.out")',
         'run(label="base-old-counter", counter=OLD, expected="missed", out=OUT / "base-c1.out")'),
        ('run("round56-counter", NEW, "detected", OUT / "build-c1.out")',
         'run(label="round56-counter", counter=NEW, expected="detected", out=OUT / "build-c1.out")'),
        ('run("m-drop-ldaudit", mutant, "missed", OUT / "m-drop-ldaudit.out")',
         'run(label="m-drop-ldaudit", counter=mutant, expected="missed", out=OUT / "m-drop-ldaudit.out")'),
    ]
    for old, new in pairs:
        if keyword.count(old) != 1:
            raise SystemExit(f"v5 anchor not unique: {old!r} count={keyword.count(old)}")
        keyword = keyword.replace(old, new)
    variants["v5_keyword_identical"] = keyword
    variants["v6_crash_before_calls"] = ROSTER_LIT + '''def run(label, counter, expected, out):
    return True


def main():
    raise RuntimeError("battery cannot execute")
    run("base-old-counter", None, "missed", None)
    run("round56-counter", None, "detected", None)
    run("m-drop-ldaudit", None, "missed", None)


if __name__ == "__main__":
    raise SystemExit(main())
'''
    variants["v7_outside_main"] = ROSTER_LIT + '''def run(label, counter, expected, out):
    return True


def main():
    return 0


if False:
    run("base-old-counter", None, "missed", None)
    run("round56-counter", None, "detected", None)
    run("m-drop-ldaudit", None, "missed", None)


if __name__ == "__main__":
    raise SystemExit(main())
'''

    var_dir = SCRATCH / "variants"
    var_dir.mkdir(parents=True, exist_ok=True)
    for name, text in variants.items():
        (var_dir / f"{name}.py").write_text(text)
        tip = commit_battery(text, f"variant {name}")
        variants[name] = {"tip": tip, "sha256": sha_bytes(text.encode()), "results": {}}
        for cname, chk in (("frozen", frozen_chk), ("repair", repair_chk)):
            outp = REC / f"{name}.{cname}.out"
            rc, body = run_checker(chk, tip, outp)
            variants[name]["results"][cname] = {
                "exit": rc,
                "stdout": body.strip().splitlines(),
                "receipt": str(outp),
                "receipt_text": outp.read_text().strip().splitlines() if outp.exists() else [],
            }
        # normalize for report
    report["variants"] = variants

    # --- determinism: rerun the two decisive cells ---
    det = {}
    for name in ("v3_dead_calls", "genuine"):
        tip = variants[name]["tip"]
        rc, body = run_checker(repair_chk, tip, REC / f"{name}.repair.rerun.out")
        det[name] = {"exit": rc, "stdout": body.strip().splitlines()}
    report["determinism"] = det

    # --- verdict matrix ---
    def met(name, checker):
        lines = variants[name]["results"][checker]["stdout"]
        return any("met=True" in ln for ln in lines)

    report["matrix"] = {
        name: {c: met(name, c) for c in ("frozen", "repair")} for name in variants
    }
    report["predicate_holds"] = {
        "frozen_rejects_roster_only_noop": report["matrix"]["v1_roster_only"]["frozen"] is False,
        "repair_rejects_roster_only_noop": report["matrix"]["v1_roster_only"]["repair"] is False,
        "repair_rejects_declare_print_noop": report["matrix"]["v2_declare_print"]["repair"] is False,
        "repair_accepts_genuine": report["matrix"]["genuine"]["repair"] is True,
        "repair_rejects_dead_call_noop_executes_none": report["matrix"]["v3_dead_calls"]["repair"] is False,
    }

    (SCRATCH / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report["matrix"], indent=1))
    print(json.dumps(report["predicate_holds"], indent=1))
    for k, v in report["variants"].items():
        for c in ("frozen", "repair"):
            print(f"{k:28s} {c:7s} exit={v['results'][c]['exit']} :: "
                  + " | ".join(x for x in v['results'][c]['stdout'] if 'met=' in x))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
