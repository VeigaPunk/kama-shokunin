#!/usr/bin/env python3
"""Build the round-57 E03 frozen-counter selftest fixtures.

Every fixture is an isolated git repo under $S/fix/<name>.  Before any commit the
script asserts `git rev-parse --show-toplevel` is the fixture directory itself.
The lane repository is only read (git show / git archive).

C1 fixtures are small (preregistration + battery only).  C2 fixtures are the
committed lane tree at PIN_C2; variants are hardlink copies with a fresh .git so
six 400 MB trees cost one extraction.  The single excluded subtree is a
round-36 nested probe dump that no C2 check reads.
"""
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys

S = pathlib.Path("/fast/scratch/hyaku/kama-r57/E03CounterSelftest")
LANE = pathlib.Path("/home/vgpnk/Projects/shokunin/kama-shokunin")
PIN_C1_PRE = "7c873d7b4e3839489a93d6334cdf93fe5d34d19f"
PIN_C2 = "b89bdab2cc114735ec5d331c6c610134258f7864"   # frozen round-57 base (stale count 42)
EXCLUDE = ":(exclude).ufo/waves/round-36/w3/out/MutRowPipe"
ENV = {**os.environ, "GIT_AUTHOR_NAME": "e03", "GIT_AUTHOR_EMAIL": "e03@selftest",
       "GIT_COMMITTER_NAME": "e03", "GIT_COMMITTER_EMAIL": "e03@selftest"}


def sh(*args, cwd=None, check=True, input=None):
    p = subprocess.run(args, cwd=cwd, capture_output=True, text=True, env=ENV, input=input)
    if check and p.returncode:
        raise SystemExit(f"{args}: {p.returncode}\n{p.stdout}\n{p.stderr}")
    return p


def lane_blob(rev, path):
    return sh("git", "-C", str(LANE), "show", f"{rev}:{path}").stdout


def assert_root(d):
    got = sh("git", "-C", str(d), "rev-parse", "--show-toplevel").stdout.strip()
    assert pathlib.Path(got).resolve() == d.resolve(), (got, d)


def fresh_repo(d):
    if d.exists():
        shutil.rmtree(d)
    d.mkdir(parents=True)
    sh("git", "init", "-q", str(d))
    assert_root(d)


def commit(d, msg):
    sh("git", "-C", str(d), "add", "-A")
    sh("git", "-C", str(d), "-c", "commit.gpgsign=false", "commit", "-q", "-m", msg)
    return sh("git", "-C", str(d), "rev-parse", "HEAD").stdout.strip()


def c1_repo(name, files):
    d = S / "fix" / name
    fresh_repo(d)
    for rel, text in files.items():
        p = d / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)
    return d, commit(d, f"fixture {name}")


BATTERY = lane_blob(PIN_C1_PRE, "tools/round56-env-leg-battery.py")
PREREG = lane_blob(PIN_C1_PRE, ".ufo/waves/round-56/preregistration.json")
ROSTER_LIT = BATTERY[BATTERY.index("ROSTER = {"):BATTERY.index("}\n", BATTERY.index("ROSTER = {")) + 1]


def deadcode_battery():
    return ("#!/usr/bin/env python3\n"
            f"{ROSTER_LIT}\n\n"
            "def run(label, counter, expected, out):\n"
            "    return True\n\n"
            "def main():\n"
            "    return 0\n"
            "    run('base-old-counter', None, 'missed', None)\n"
            "    run('round56-counter', None, 'detected', None)\n"
            "    run('m-drop-ldaudit', None, 'missed', None)\n\n"
            "if __name__ == '__main__':\n"
            "    raise SystemExit(main())\n")


def unusedfn_battery():
    return ("#!/usr/bin/env python3\n"
            f"{ROSTER_LIT}\n\n"
            "def run(label, counter, expected, out):\n"
            "    return True\n\n"
            "def _never_called():\n"
            "    run('base-old-counter', None, 'missed', None)\n"
            "    run('round56-counter', None, 'detected', None)\n"
            "    run('m-drop-ldaudit', None, 'missed', None)\n\n"
            "def main():\n"
            "    return 0\n\n"
            "if __name__ == '__main__':\n"
            "    raise SystemExit(main())\n")


def literal_only_battery():
    return ("#!/usr/bin/env python3\n"
            f"{ROSTER_LIT}\n\n"
            "def main():\n"
            "    return 0\n\n"
            "if __name__ == '__main__':\n"
            "    raise SystemExit(main())\n")


def stale_roster_battery():
    return BATTERY.replace('"m-drop-ldaudit": {"designation": "kill", "expected": "missed"}',
                           '"m-drop-ldaudit": {"designation": "control", "expected": "missed"}')


def hardlink_variant(base, name, mutate):
    d = S / "fix" / name
    if d.exists():
        shutil.rmtree(d)
    sh("cp", "-al", str(base), str(d))
    shutil.rmtree(d / ".git")
    sh("git", "init", "-q", str(d))
    assert_root(d)
    mutate(d)
    return d, commit(d, f"fixture {name}")


def rewrite(path, text):
    path.unlink()          # break the hard link; never touch the base inode
    path.write_text(text)


def main():
    meta = {"pin_c1_pre": PIN_C1_PRE, "pin_c2": PIN_C2, "exclude": EXCLUDE, "c1": {}, "c2": {}}
    c1 = {
        "c1-genuine": {"tools/round56-env-leg-battery.py": BATTERY,
                       ".ufo/waves/round-56/preregistration.json": PREREG},
        "c1-noop-deadcode": {"tools/round56-env-leg-battery.py": deadcode_battery(),
                             ".ufo/waves/round-56/preregistration.json": PREREG},
        "c1-noop-unusedfn": {"tools/round56-env-leg-battery.py": unusedfn_battery(),
                             ".ufo/waves/round-56/preregistration.json": PREREG},
        "c1-noop-literal": {"tools/round56-env-leg-battery.py": literal_only_battery(),
                            ".ufo/waves/round-56/preregistration.json": PREREG},
        "c1-stale-roster": {"tools/round56-env-leg-battery.py": stale_roster_battery(),
                            ".ufo/waves/round-56/preregistration.json": PREREG},
        "c1-absent": {"README.md": "no preregistration or battery at this tip\n"},
        "c1-badjson": {"tools/round56-env-leg-battery.py": BATTERY,
                       ".ufo/waves/round-56/preregistration.json": "{not json"},
    }
    for name, files in c1.items():
        d, tip = c1_repo(name, files)
        meta["c1"][name] = {"dir": str(d), "tip": tip}

    base = S / "fix" / "c2-base"
    fresh_repo(base)
    arc = subprocess.run(["git", "-C", str(LANE), "archive", "--format=tar", PIN_C2, EXCLUDE],
                         capture_output=True, check=True)
    subprocess.run(["tar", "-x", "-C", str(base)], input=arc.stdout, check=True)
    meta["c2"]["c2-base"] = {"dir": str(base), "tip": commit(base, "fixture c2-base")}

    def mut_fixed(d):
        p = d / "SCORECARD.md"
        sc = p.read_text()
        pat = re.compile(r"(verifier-spotcheck\.md'\)\)\)\"`\s*\u2192\s*`)(\d+)(`)")
        hits = pat.findall(sc)
        assert len(hits) == 1, hits
        rewrite(p, pat.sub(lambda m: m.group(1) + "43" + m.group(3), sc))

    def mut_minus(d):
        (d / "corpus/lessons/round-56-verifier-spotcheck.md").unlink()

    def mut_trim(d):
        p = d / "SCORECARD.md"
        sc = p.read_text()
        rewrite(p, sc[:sc.index("\n## Round 47")] + "\n")

    def mut_inflate(d):
        p = d / "SCORECARD.md"
        sc = p.read_text()
        rewrite(p, sc + "\n## Round 99 \u2014 injected selftest heading\n")

    def mut_drop(d):
        (d / "SCORECARD.md").unlink()

    d, t = hardlink_variant(base, "c2-fixed", mut_fixed)
    meta["c2"]["c2-fixed"] = {"dir": str(d), "tip": t}
    fixed = S / "fix" / "c2-fixed"
    d, t = hardlink_variant(fixed, "c2-fixed-minus-lesson", mut_minus)
    meta["c2"]["c2-fixed-minus-lesson"] = {"dir": str(d), "tip": t}
    for name, mut in (("c2-maxn-trim", mut_trim), ("c2-maxn-inflated", mut_inflate),
                      ("c2-no-scorecard", mut_drop)):
        d, t = hardlink_variant(base, name, mut)
        meta["c2"][name] = {"dir": str(d), "tip": t}

    (S / "out" / "fixtures.json").write_text(json.dumps(meta, indent=1) + "\n")
    print(json.dumps(meta, indent=1))


if __name__ == "__main__":
    main()
