#!/usr/bin/env python3
"""CR02DefaultsCounter round 3: T ids in the decision cell, and rows outside the section."""
import argparse, shutil, subprocess, sys, tempfile
from pathlib import Path

HEAD = "## Serving defaults (round 92 revision)"


def sh(*a, **k):
    return subprocess.run(list(a), capture_output=True, text=True, **k)


def run(lane, counter, skill, srcs, sec_start, section, name, want, binary, work):
    d = Path(tempfile.mkdtemp(prefix="r92-c1c-", dir=work)).resolve()
    try:
        sh("git", "-C", str(d), "init", "-q")
        top = sh("git", "-C", str(d), "rev-parse", "--show-toplevel").stdout.strip()
        if Path(top).resolve() != d:
            print(f"CASE {name} SETUP-REFUSED toplevel={top!r}")
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

    # F14: drop R15, name T14 only in R01's *decision* cell -> must NOT count (safe direction)
    cells = rows["R01"].split(" | ")
    cells[9] = cells[9].rstrip().rstrip("|").rstrip() + " supersedes T14 |"
    f14 = section.replace(rows["R01"], " | ".join(cells), 1).replace(rows["R15"] + "\n", "", 1)

    # F15: a wrong row placed before the section heading -> out of population (safe direction)
    bad_row = ("| R99 | llama.cpp b12177 | listen port `port` | `--port` | 9999 | S593 | 632 | "
               "`int32_t port                = 9931;` | T01 | wrong value, out of the section |")
    f15 = bad_row + "\n\n" + section   # sec_start points at HEAD, so prefix is skill[:sec_start] + this

    work = Path(a.work)
    work.mkdir(parents=True, exist_ok=True)
    bad = 0
    bad += run(lane, counter, skill, srcs, sec_start, f14, "F14-decision-text-T14", 1, a.binary, work)
    print(f"C1_ATTACK3 cases=1 as_expected={1-bad}")
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
