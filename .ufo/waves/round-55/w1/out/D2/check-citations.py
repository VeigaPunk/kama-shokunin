#!/usr/bin/env python3
"""check-citations.py - verify the evidence tokens the round-55 D2 proposal quotes.

Read-only over the lane. Each check names a committed file and the substring(s) the
proposal says are there (optionally on a given line). Prints one `ok:`/`FAIL:` line per
check and a final `checks=N ok=N fail=N met=True|False`. Exit 0 met, 1 not met, 2 input
missing (a cited file absent at this tip is a failure of the proposal, not a verdict).
"""
import os
import sys

LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
W53 = ".ufo/waves/round-53/w1/out"
W55 = ".ufo/waves/round-55"

CHECKS = [
    # (label, path, line or None, [tokens])
    ("K1Cheat counter passed while a root-owned library executed",
     f"{W53}/K1Cheat/c1-cheat.out", 2, ["met=True"]),
    ("K1Cheat host-file count 14 where the honest build has 13",
     f"{W53}/K1Cheat/c1-cheat.out", 5, ["14 root-owned host files"]),
    ("K1Cheat reference build reports 13",
     f"{W53}/K1Cheat/c1-build-reference.out", 6, ["13 root-owned host files"]),
    ("Sen1Mem archive reference rewritten by the replay",
     f"{W53}/Sen1Mem/out-archive-ref.txt", None,
     ["ATTACKER-SWAPPED-BYTES", "SWAPPED? True"]),
    ("J7Late frozen counter met after a late flip",
     f"{W53}/J7Late/race-v2-counter-stdout.log", 2, ["met=True", "code=1"]),
    ("Sen4Fixture GIT_DIR moves a foreign repo 358 -> 368",
     f"{W53}/Sen4Fixture/evidence/03-gitdir-escape.txt", None, ["358", "368"]),
    ("Sen4Fixture hook executes with met=True",
     f"{W53}/Sen4Fixture/evidence/07-hooks-exec.txt", None,
     ["met=True", "hook marker file: PRESENT"]),
    ("J12Hide hides SKILL citations, still met",
     f"{W53}/J12Hide/c2-frozen-v_a_skill.out", 2,
     ["cited=678", "dropped=0", "met=True"]),
    ("J11BadFixed upstream row at the b11909 tag passes",
     f"{W53}/J11BadFixed/c2-upstream-tagcommit.out", 2, ["met=True"]),
    ("J11BadFixed 'fixed' laundering passes",
     f"{W53}/J11BadFixed/c2-fixed-launder.out", 2, ["met=True"]),
    ("J11BadFixed upstream ref probe records both digests",
     f"{W53}/J11BadFixed/upstream-ref-probes.txt", None,
     ["5a4acc9b", "91f48e09"]),
    ("round-55 battery: LD_PRELOAD mutant kills envnames",
     f"{W55}/c1/battery/m-ldpreload.out", 2, ["envnames=0/3", "met=False"]),
    ("round-55 battery: text flip kills code",
     f"{W55}/c1/battery/m-text-flip.out", 2, ["code=0", "met=False"]),
    ("round-55 battery: member flip kills rehash",
     f"{W55}/c1/battery/m-member-flip.out", 2, ["rehash=3", "met=False"]),
    ("round-55 battery: LD_AUDIT vector is void (passes)",
     f"{W55}/c1/battery/m-ldaudit-foreign.out", 2, ["met=True"]),
    ("round-55 C1 build met",
     f"{W55}/measured/c1-build.out", 2,
     ["newrow=1", "envnames=3/3", "hostlibs=3/3", "anon=0", "met=True"]),
    ("round-55 C1 base control newrow=0 met=False",
     f"{W55}/controls/base.c1.out", 2, ["newrow=0", "met=False"]),
    ("round-55 C2 build met with 15/15 scenarios",
     f"{W55}/measured/c2-build.out", 2,
     ["scenarios=15/15", "dropped=0", "met=True"]),
    ("round-55 C2 base control dropped=1 met=False",
     f"{W55}/controls/base.c2.out", 2, ["dropped=1", "met=False"]),
    # counter code the entry cites by line/symbol
    ("C1 counter reads the archive once into memory",
     "tools/round54-replay-code-audit.py", None,
     ["self.blob = fh.read()", "tarfile.open(fileobj=io.BytesIO(self.blob))"]),
    ("C1 counter: row cap and anonymous-page problem",
     "tools/round54-replay-code-audit.py", None,
     ["ROW_CAP = 64 << 20", "anonymous executable mapping", "BAD_ENV = (\"LD_PRELOAD\""]),
    ("C1 counter: descendant gate before any /proc read",
     "tools/round54-replay-code-audit.py", None,
     ["descends_from(pid, rp)", "no /proc read made"]),
    ("C2 counter: clean env, three surfaces, superseded and stem",
     "tools/round54-cited-path-check.py", None,
     ["def clean_env", "SURFACES = (\"SCORECARD.md\", \"SHONEN.md\", \"SKILL.md\")",
      "\"superseded\"", "original token's stem"]),
    ("registry rows exist for every cited source",
     "corpus/SOURCES.md", None,
     ["| S506 |", "| S507 |", "| S508 |", "| S500 |", "| S501 |", "| S502 |",
      "| S509 |", "| S510 |", "| S511 |"]),
    ("round-55 lesson records the same-tip base revert",
     "corpus/lessons/round-55.md", None,
     ["a counter/target a do-nothing control can reach",
      "the do-nothing control met the target"]),
    # the opened copies each cited row names (KQ6: row + revision + section + copy)
    ("S506 opened copy exists", ".ufo/waves/round-53/c1/proc_pid_mem.5.txt", None, ["proc_pid_mem"]),
    ("S507 opened copy exists", ".ufo/waves/round-53/c1/ptrace.2.txt", None, ["ptrace"]),
    ("S508 opened copy exists", ".ufo/waves/round-53/c1/proc_pid_map_files.5.txt", None, ["map_files"]),
    ("S500 opened copy exists", ".ufo/waves/round-52/c1/memfd_create.2.txt", None, ["memfd_create"]),
    ("S501 opened copy exists", ".ufo/waves/round-52/c1/F_GET_SEALS.2const.txt", None, ["seal"]),
    ("S502 opened copy exists", ".ufo/waves/round-52/c1/mfd_noexec.txt", None, ["mfd_noexec"]),
    ("S509 opened copy exists", ".ufo/waves/round-53/c1/ggml-backend-reg.cpp.b11909", None, ["ggml_backend_load_best"]),
    ("S510 opened copy exists", ".ufo/waves/round-54/sources/git-docs-git.html", None, ["GIT_DIR"]),
    ("S511 opened copy exists", ".ufo/waves/round-55/sources/git-docs-git-config.html", None, ["GIT_CONFIG_COUNT"]),
]


def read(rel):
    p = os.path.join(LANE, rel)
    with open(p, encoding="utf-8", errors="replace") as fh:
        return fh.read().splitlines()


def main():
    ok = fail = missing = 0
    for label, rel, line, tokens in CHECKS:
        try:
            lines = read(rel)
        except OSError as exc:
            print(f"FAIL: {label} [{rel}: {exc.strerror}]")
            missing += 1
            continue
        if line is not None:
            text = lines[line - 1] if 0 < line <= len(lines) else ""
        else:
            text = "\n".join(lines)
        absent = [t for t in tokens if t not in text]
        if absent:
            print(f"FAIL: {label} [{rel}{':' + str(line) if line else ''}: missing {absent}]")
            fail += 1
        else:
            print(f"ok: {label} [{rel}{':' + str(line) if line else ''}]")
            ok += 1
    total = ok + fail + missing
    met = fail == 0 and missing == 0
    print(f"checks={total} ok={ok} fail={fail} missing={missing} met={met}")
    if missing and not fail:
        return 2
    return 0 if met else 1


if __name__ == "__main__":
    sys.exit(main())
