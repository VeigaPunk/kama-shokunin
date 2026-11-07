#!/usr/bin/env python3
"""CR02DefaultsCounter round 4: unit cell, and the TYPE_CHECKING declaration for R15."""
import argparse, shutil, subprocess, sys, tempfile
from pathlib import Path

HEAD = "## Serving defaults (round 92 revision)"


def sh(*a, **k):
    return subprocess.run(list(a), capture_output=True, text=True, **k)


def run(counter, skill, srcs, sec_start, section, name, want, binary, work):
    d = Path(tempfile.mkdtemp(prefix="r92-c1d-", dir=work)).resolve()
    try:
        sh("git", "-C", str(d), "init", "-q")
        top = sh("git", "-C", str(d), "rev-parse", "--show-toplevel").stdout.strip()
        if Path(top).resolve() != d:
            print(f"CASE {name} SETUP-REFUSED")
            return 1
        (d / "corpus").mkdir()
        (d / "SKILL.md").write_text(skill[:sec_start] + section)
        (d / "corpus" / "SOURCES.md").write_text(srcs)
        sh("git", "-C", str(d), "add", "-A")
        sh("git", "-C", str(d), "-c", "user.name=fixture", "-c", "user.email=fixture@invalid",
           "commit", "-q", "-m", name)
        p = sh(sys.executable, str(counter), "--repo", str(d), "--rev", "HEAD", "--binary", binary)
        got = p.returncode
        print(f"CASE {name} want={want} got={got} {'as-expected' if got == want else 'UNEXPECTED'}")
        for l in p.stdout.splitlines():
            if l.startswith("SERVER_DEFAULTS") or "bound=0" in l:
                print("   " + l)
        return got != want
    finally:
        shutil.rmtree(d, ignore_errors=True)


def main():
    ap = argparse.ArgumentParser()
    for x in ("--lane", "--work", "--binary", "--rev"):
        ap.add_argument(x, required=True)
    a = ap.parse_args()
    lane = Path(a.lane).resolve()
    counter = lane / "tools" / "round92-server-defaults.py"
    skill = sh("git", "-C", str(lane), "show", f"{a.rev}:SKILL.md").stdout
    srcs = sh("git", "-C", str(lane), "show", f"{a.rev}:corpus/SOURCES.md").stdout
    sec_start = skill.index(HEAD)
    section = skill[sec_start:]
    rows = {l.split("|")[1].strip(): l for l in section.split("\n") if l.startswith("| R")}

    def swap(rid, **kw):
        idx = dict(engine=1, name=2, flag=3, value=4, sid=5, line=6, lit=7, sup=8, decision=9)
        cells = rows[rid].split(" | ")
        for k, v in kw.items():
            cells[idx[k]] = v
        return " | ".join(cells)

    # F16: unit cell unvalidated even on a help-checked row: 3600 seconds stated as 3600 hours
    f16 = section.replace(rows["R02"], swap("R02", value="3600 h"), 1)
    # F17: R15 cited to the TYPE_CHECKING declaration (envs.py:111) instead of the run-time reader
    f17 = section.replace(rows["R15"], swap("R15", line="111",
                                            lit='`VLLM_HTTP_TIMEOUT_KEEP_ALIVE: int = 5  # seconds`'), 1)
    work = Path(a.work)
    work.mkdir(parents=True, exist_ok=True)
    bad = 0
    bad += run(counter, skill, srcs, sec_start, f16, "F16-unit-hours-on-help-row", 0, a.binary, work)
    bad += run(counter, skill, srcs, sec_start, f17, "F17-R15-typecheck-decl", 0, a.binary, work)
    print(f"C1_ATTACK4 cases=2 as_expected={2-bad}")
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
