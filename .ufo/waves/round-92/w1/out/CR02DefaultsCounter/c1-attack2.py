#!/usr/bin/env python3
"""CR02DefaultsCounter round 2: supersession laundering and duplicate-id sanity."""
import argparse, shutil, subprocess, sys, tempfile
from pathlib import Path

HEAD = "## Serving defaults (round 92 revision)"


def sh(*a, **k):
    return subprocess.run(list(a), capture_output=True, text=True, **k)


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

    # F12: drop R15 (T14's row) and launder T14 into R01's supersedes cell
    r01 = rows["R01"].split(" | ")
    r01[8] = "T01 T14"
    f12 = section.replace(rows["R01"], " | ".join(r01), 1).replace(rows["R15"] + "\n", "", 1)
    # F13 sanity: a repeated R id must be a duplicate
    f13 = section.rstrip("\n") + "\n" + rows["R01"] + "\n"

    cases = [("F12-supersede-laundering", f12, 0), ("F13-duplicate-rid", f13, 1)]
    Path(a.work).mkdir(parents=True, exist_ok=True)
    bad = 0
    for name, sec, want in cases:
        d = Path(tempfile.mkdtemp(prefix="r92-c1b-", dir=a.work)).resolve()
        try:
            sh("git", "-C", str(d), "init", "-q")
            top = sh("git", "-C", str(d), "rev-parse", "--show-toplevel").stdout.strip()
            if Path(top).resolve() != d:
                print(f"CASE {name} SETUP-REFUSED")
                bad += 1
                continue
            (d / "corpus").mkdir()
            (d / "SKILL.md").write_text(skill[:sec_start] + sec)
            (d / "corpus" / "SOURCES.md").write_text(srcs)
            sh("git", "-C", str(d), "add", "-A")
            sh("git", "-C", str(d), "-c", "user.name=fixture", "-c", "user.email=fixture@invalid",
               "commit", "-q", "-m", name)
            p = sh(sys.executable, str(counter), "--repo", str(d), "--rev", "HEAD", "--binary", a.binary)
            got = p.returncode
            bad += got != want
            print(f"CASE {name} want={want} got={got} {'as-expected' if got == want else 'UNEXPECTED'}")
            for l in p.stdout.splitlines():
                if l.startswith("SERVER_DEFAULTS") or ("bound=0" in l):
                    print("   " + l)
        finally:
            shutil.rmtree(d, ignore_errors=True)
    print(f"C1_ATTACK2 cases={len(cases)} as_expected={len(cases)-bad}")
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
