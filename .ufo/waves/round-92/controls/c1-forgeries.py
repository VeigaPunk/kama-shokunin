#!/usr/bin/env python3
"""Round-92 C1 pre-freeze control battery for tools/round92-server-defaults.py.

Builds one scratch fixture repo per case (git -C <D> only; D under --work), each holding the lane's
SKILL.md and corpus/SOURCES.md at BASE plus a case-specific `## Serving defaults (round 92 revision)`
section and the two candidate SOURCES rows (S596, S597), then runs the counter on it.

Cases (expected exit in brackets):
  P0  the candidate table as drafted before freeze                          [0]  positive control
  V1  R07 transplanted from round-91 T07: S593 line 464, value 1, `--parallel` [1] help disagrees
  V2  R07 value -1 but still citing S593 line 464 (the shared struct)       [1] value not in literal
  V3  R08 (flag `-`, derived) citing S593 line 464 instead of the entry point [1] not entry point
  V4  R15 dropped (14 rows, T14 not superseded)                              [1] supersedes=13
  V5  R02 flag cell `-` (an option default passed off as derived)           [1] not entry point
  V6  R01 flag cell names the env var `LLAMA_ARG_PORT`, not the option      [1] llama flag not option
  V7  R14 bound to the TYPE_CHECKING declaration envs.py:26 instead of 812  [0] DISCLOSED LIMIT:
      the counter does not know which vLLM line is read at run time; that is the K2 reviewer read
  V8  a binary that is not the pinned b12177 build (/usr/bin/true)          [2] could-not-evaluate
Usage: c1-forgeries.py --lane DIR --work DIR --binary PATH --section FILE --rows FILE
Prints one CASE line per case and `C1_FORGERIES cases=9 as_expected=<n>`; exit 0 when every case
exits as expected.
"""
import argparse, os, shutil, subprocess, sys, tempfile
from pathlib import Path

BASE = "ed018ca0fa956c5052b3dc6b714a2cb72973da21"


def sh(*a, **k):
    return subprocess.run(list(a), capture_output=True, text=True, **k)


def main():
    ap = argparse.ArgumentParser()
    for x in ("--lane", "--work", "--binary", "--section", "--rows"):
        ap.add_argument(x, required=True)
    a = ap.parse_args()
    lane = Path(a.lane).resolve()
    counter = lane / "tools" / "round92-server-defaults.py"
    section = Path(a.section).read_text()
    rows = Path(a.rows).read_text()
    skill = sh("git", "-C", str(lane), "show", f"{BASE}:SKILL.md").stdout
    srcs = sh("git", "-C", str(lane), "show", f"{BASE}:corpus/SOURCES.md").stdout
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
        ("P0-candidate", section, a.binary, 0),
        ("V1-r91-T07-transplant", swap(section, "R07", " | ".join(v1)), a.binary, 1),
        ("V2-shared-struct-line", swap(section, "R07", " | ".join(v2)), a.binary, 1),
        ("V3-derived-not-entry-point", swap(section, "R08", " | ".join(v3)), a.binary, 1),
        ("V4-drop-R15", section.replace(line_of("R15") + "\n", "", 1), a.binary, 1),
        ("V5-option-as-derived", swap(section, "R02", " | ".join(v5)), a.binary, 1),
        ("V6-env-not-option", swap(section, "R01", " | ".join(v6)), a.binary, 1),
        ("V7-typecheck-line-LIMIT", swap(section, "R14", " | ".join(v7)), a.binary, 0),
        ("V8-unpinned-binary", section, "/usr/bin/true", 2),
    ]
    Path(a.work).mkdir(parents=True, exist_ok=True)
    good = 0
    for name, sec, binary, want in cases:
        d = Path(tempfile.mkdtemp(prefix="r92-c1f-", dir=a.work)).resolve()
        try:
            sh("git", "-C", str(d), "init", "-q")
            top = sh("git", "-C", str(d), "rev-parse", "--show-toplevel").stdout.strip()
            if Path(top).resolve() != d:
                print(f"CASE {name} SETUP-REFUSED toplevel={top}")
                continue
            (d / "corpus").mkdir()
            (d / "SKILL.md").write_text(skill.rstrip("\n") + "\n\n" + sec)
            (d / "corpus" / "SOURCES.md").write_text(srcs2)
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
            print(f"CASE {name} expected_exit={want} exit={p.returncode} {'as-expected' if ok else 'UNEXPECTED'}")
            for l in summary + whys:
                print("  " + l)
        finally:
            shutil.rmtree(d, ignore_errors=True)
    print(f"C1_FORGERIES cases={len(cases)} as_expected={good}")
    return 0 if good == len(cases) else 1


if __name__ == "__main__":
    sys.exit(main())
