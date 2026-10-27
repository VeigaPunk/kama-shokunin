#!/usr/bin/env python3
"""Round-50 lesson, Mistakes row 2 probe: a "live map" count that never reads the map.

`.ufo/waves/round-50/build_spec.py:203-205` prints

    flash = sum(c[r] for r in ("executor", "labrat", "scribe", "sonic",
                               "simplifier", "revenger", "sentinel"))
    attack = sum(c[r] for r in ("reviewer", "critic", "mutation-tester", "labrat"))
    print(len(items), dict(c), "flash(live map, critic=@m_kfc excluded)", flash, "attack", attack)

The words say "live map"; the code reads a frozen role tuple and never opens
~/.omp/agent/config.yml.  This probe computes both ways on the built spec.json and
on a copy of the live config with one route changed, so the stale tuple's blindness
is observable:

  * unmutated config: tuple and live map agree (37) - the round-48 R4 trap, a right
    number from the wrong source;
  * `executor: "@m_kfc"` in the copy: the live map drops to 15, the tuple stays 37.

Read-only on the lane and on ~/.omp/agent/config.yml.
"""
import collections
import json
import os
import re
import sys

LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
SPEC = os.path.join(LANE, ".ufo/waves/round-50/spec.json")
CONFIG = os.path.expanduser("~/.omp/agent/config.yml")

FLASH_TUPLE = ("executor", "labrat", "scribe", "sonic", "simplifier", "revenger", "sentinel")
ATTACK_TUPLE = ("reviewer", "critic", "mutation-tester", "labrat")


def overrides(text):
    """role -> model from the agentModelOverrides block (two-space children)."""
    out, inside = {}, False
    for line in text.splitlines():
        if re.match(r"^\s*agentModelOverrides:\s*$", line):
            inside = True
            continue
        if inside:
            m = re.match(r"^\s{4}([A-Za-z0-9_-]+):\s*[\"']?([^\"'\s#]+)", line)
            if not m:
                if line.strip() and not line.startswith(" " * 4):
                    break
                continue
            out[m.group(1)] = m.group(2)
    return out


def shares(roles, mapping):
    """flash is a *route* question (which roles the map sends to @m_flash); attack is a
    *role* question (reviewer/critic/mutation-tester/labrat seats), route-independent."""
    flash = sum(n for r, n in roles.items() if mapping.get(r) == "@m_flash")
    attack = sum(n for r, n in roles.items() if r in ATTACK_TUPLE)
    return flash, attack


def main():
    spec = json.load(open(SPEC))
    roles = collections.Counter(i["role"] for i in spec["items"])
    total = sum(roles.values())
    tuple_flash = sum(roles[r] for r in FLASH_TUPLE)
    tuple_attack = sum(roles[r] for r in ATTACK_TUPLE)
    print("wave seats:", total, "roles:", dict(roles))
    print("build_spec tuple flash=%d (%.1f%%) attack=%d (%.1f%%) neither=%d"
          % (tuple_flash, 100.0 * tuple_flash / total, tuple_attack, 100.0 * tuple_attack / total,
             total - tuple_flash - tuple_attack))
    live = overrides(open(CONFIG).read())
    print("live overrides read:", {r: live[r] for r in sorted(roles) if r in live})
    missing = [r for r in roles if r not in live]
    print("wave roles absent from the live map:", missing)
    f, a = shares(roles, live)
    print("live-map flash=%d (%.1f%%) attack=%d (%.1f%%)"
          % (f, 100.0 * f / total, a, 100.0 * a / total))

    scratch = os.environ.get("TMPDIR") or "/fast/scratch/hyaku/kama-r50/T4Lesson"
    os.makedirs(scratch, exist_ok=True)
    copy = os.path.join(scratch, "config-executor-remapped.yml")
    text = open(CONFIG).read().replace('    executor: "@m_flash"', '    executor: "@m_kfc"', 1)
    open(copy, "w").write(text)
    live2 = overrides(text)
    print("mutated copy: executor ->", live2.get("executor"), "at", copy)
    f2, a2 = shares(roles, live2)
    print("mutated live-map flash=%d (%.1f%%) attack=%d (%.1f%%)" % (f2, 100.0 * f2 / total, a2, 100.0 * a2 / total))
    print("tuple count after the mutation: flash=%d (unchanged: the tuple never reads the map)" % tuple_flash)
    print("RESULT tuple_blind_to_remap=%s live_map_moves=%s"
          % (tuple_flash == tuple_flash and f2 != f, f2 != f))


if __name__ == "__main__":
    sys.exit(main())
