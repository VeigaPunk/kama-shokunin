#!/usr/bin/env python3
"""c1-mutbattery.py - mutant battery for tools/round92-server-defaults.py (round-92 C1).

Adapted from .ufo/waves/round-92/controls/c1-forgeries.py: identical 9 cases (P0, V1-V8) plus
P1-real-M1 (the landed table at M1, expected 0). Difference: the counter path is a parameter, so a
mutant copy can be graded without touching the lane.

Cases (expected exit in brackets):
  P0  the candidate table as drafted before freeze                          [0]
  P1  the real SKILL.md + corpus/SOURCES.md at M1 (no injected section)      [0]
  V1  R07 transplanted from round-91 T07 (S593:464, value 1)                [1]
  V2  R07 value -1 but still citing S593:464                                [1]
  V3  R08 (derived) citing S593:464 instead of the entry point              [1]
  V4  R15 dropped (T14 not superseded)                                      [1]
  V5  R02 option default passed off as derived                              [1]
  V6  R01 flag cell names the env var, not the option                       [1]
  V7  R14 bound to the TYPE_CHECKING declaration envs.py:26 (disclosed)     [0]
  V8  unpinned binary (/usr/bin/true)                                       [2]
Usage: c1-mutbattery.py --lane DIR --work DIR --binary PATH --section FILE --rows FILE
                         --counter FILE [--label NAME]
Prints one `CASE <name> exit=<n> want=<n> verdict=` line per case and a `C1_MUTBATTERY` summary line
with `cases=10 as_expected=<n>`; exit 0 when every case exits as expected.
"""
import argparse, shutil, subprocess, sys, tempfile
from pathlib import Path

BASE = "ed018ca0fa956c5052b3dc6b714a2cb72973da21"
M1 = "18153ebb5f9e2ae83f53e7fef57ee579bc409331"


def sh(*a, **k):
    return subprocess.run(list(a), capture_output=True, text=True, **k)


def main():
    ap = argparse.ArgumentParser()
    for x in ("--lane", "--work", "--binary", "--section", "--rows", "--counter"):
        ap.add_argument(x, required=True)
    ap.add_argument("--label", default="")
    a = ap.parse_args()
    lane = Path(a.lane).resolve()
    counter = Path(a.counter).resolve()
    section = Path(a.section).read_text()
    rows = Path(a.rows).read_text()
    skill = sh("git", "-C", str(lane), "show", f"{BASE}:SKILL.md").stdout
    srcs = sh("git", "-C", str(lane), "show", f"{BASE}:corpus/SOURCES.md").stdout
    skill_m1 = sh("git", "-C", str(lane), "show", f"{M1}:SKILL.md").stdout
    srcs_m1 = sh("git", "-C", str(lane), "show", f"{M1}:corpus/SOURCES.md").stdout
    if not skill_m1 or not srcs_m1:
        print("SETUP-FAILED cannot show M1 blobs")
        return 2
    anchor = next(l for l in srcs.split("\n") if l.startswith("| S595 |"))
    srcs2 = srcs.replace(anchor, anchor + "\n" + rows.rstrip("\n"), 1)

    def line_of(rid):
        return next(l for l in section.split("\n") if l.startswith(f"| {rid} |"))

    def swap(sec, rid, new):
        return sec.replace(line_of(rid), new, 1)

    r07 = line_of("R07").split(" | ")
    v1 = list(r07); v1[4] = "1"; v1[5] = "S593"; v1[6] = "464"; v1[7] = "`int32_t n_parallel            =     1;`"
    v2 = list(r07); v2[5] = "S593"; v2[6] = "464"; v2[7] = "`int32_t n_parallel            =     1;`"
    r08 = line_of("R08").split(" | ")
    v3 = list(r08); v3[4] = "1"; v3[5] = "S593"; v3[6] = "464"; v3[7] = "`int32_t n_parallel            =     1;`"
    r02 = line_of("R02").split(" | "); v5 = list(r02); v5[3] = "-"
    r01 = line_of("R01").split(" | "); v6 = list(r01); v6[3] = "`LLAMA_ARG_PORT`"
    r14 = line_of("R14").split(" | "); v7 = list(r14); v7[6] = "26"; v7[7] = "`VLLM_ENGINE_READY_TIMEOUT_S: int = 600`"
    cases = [
        ("P0-candidate", skill.rstrip("\n") + "\n\n" + section, srcs2, a.binary, 0),
        ("P1-real-M1", skill_m1, srcs_m1, a.binary, 0),
        ("V1-r91-T07-transplant", skill.rstrip("\n") + "\n\n" + swap(section, "R07", " | ".join(v1)), srcs2, a.binary, 1),
        ("V2-shared-struct-line", skill.rstrip("\n") + "\n\n" + swap(section, "R07", " | ".join(v2)), srcs2, a.binary, 1),
        ("V3-derived-not-entry-point", skill.rstrip("\n") + "\n\n" + swap(section, "R08", " | ".join(v3)), srcs2, a.binary, 1),
        ("V4-drop-R15", skill.rstrip("\n") + "\n\n" + section.replace(line_of("R15") + "\n", "", 1), srcs2, a.binary, 1),
        ("V5-option-as-derived", skill.rstrip("\n") + "\n\n" + swap(section, "R02", " | ".join(v5)), srcs2, a.binary, 1),
        ("V6-env-not-option", skill.rstrip("\n") + "\n\n" + swap(section, "R01", " | ".join(v6)), srcs2, a.binary, 1),
        ("V7-typecheck-line-LIMIT", skill.rstrip("\n") + "\n\n" + swap(section, "R14", " | ".join(v7)), srcs2, a.binary, 0),
        ("V8-unpinned-binary", skill.rstrip("\n") + "\n\n" + section, srcs2, "/usr/bin/true", 2),
    ]
    Path(a.work).mkdir(parents=True, exist_ok=True)
    good = 0
    for name, sk, sr, binary, want in cases:
        d = Path(tempfile.mkdtemp(prefix="r92-mtb-", dir=a.work)).resolve()
        try:
            sh("git", "-C", str(d), "init", "-q")
            top = sh("git", "-C", str(d), "rev-parse", "--show-toplevel").stdout.strip()
            if Path(top).resolve() != d:
                print(f"CASE {name} SETUP-REFUSED toplevel={top}")
                continue
            (d / "corpus").mkdir()
            (d / "SKILL.md").write_text(sk if sk.endswith("\n") else sk + "\n")
            (d / "corpus" / "SOURCES.md").write_text(sr)
            sh("git", "-C", str(d), "add", "-A")
            c = sh("git", "-C", str(d), "-c", "user.name=fixture", "-c", "user.email=fixture@invalid",
                   "commit", "-q", "-m", name)
            if c.returncode != 0:
                print(f"CASE {name} SETUP-FAILED {c.stderr.strip()}")
                continue
            p = sh(sys.executable, str(counter), "--repo", str(d), "--rev", "HEAD", "--binary", binary)
            summary = [l for l in p.stdout.splitlines() if l.startswith("SERVER_DEFAULTS")]
            whys = [l for l in p.stdout.splitlines() if l.startswith("SERVER_DEFAULT ") and "bound=0" in l]
            ok = p.returncode == want
            good += ok
            print(f"CASE {name} exit={p.returncode} want={want} verdict={'as-expected' if ok else 'UNEXPECTED'}")
            for l in summary + whys:
                print("  " + l)
            if p.stderr.strip():
                print("  STDERR " + p.stderr.strip().splitlines()[0][:200])
        finally:
            shutil.rmtree(d, ignore_errors=True)
    print(f"C1_MUTBATTERY label={a.label} counter={counter} cases={len(cases)} as_expected={good}")
    return 0 if good == len(cases) else 1


if __name__ == "__main__":
    sys.exit(main())
