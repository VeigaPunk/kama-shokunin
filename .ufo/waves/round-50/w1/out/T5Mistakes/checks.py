#!/usr/bin/env python3
"""T5Mistakes round-50 sweep: fail-capable checks for the proposed rows.

Reads a git clone of the lane with `git show` only (never the working tree).

  A label-resolution -- a "round-NN closure RX" citation in the round-50 wave
    spec must name an item whose own text shares a content word with the
    descriptor the citation attaches, or whose seats it names are that item's.
  B routed-block -- a round whose base is a closure that routed lane items
    carries a `routed`/`carried` block in its preregistration.
  C sweep-consumed -- a wave's frontier-sweep verdict is cited by a committed
    corpus/ or registry/ file, not left as wave output only.
  D carried-limits -- every limit the previous closure's carried item names
    appears in the next preregistration's `limits`.

Usage: python3 checks.py --repo <clone> [--rev <commit>]
Exit 0 iff every check passes.
"""
import argparse
import json
import re
import subprocess
import sys

STOP = set("""the a an and or of to in on for with by from not no is are be as at it its that this which
carried against item round style do not rerun reading read per each every all any some""".split())
PATHISH = {"home", "vgpnk", "projects", "shokunin", "tools", "opt", "fast", "scratch", "kama", "py", "local"}
SEAT = re.compile(r"\b[A-Z][0-9][A-Za-z0-9]{2,}\b")


def git(repo, *args):
    return subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True)


def show(repo, rev, path):
    return git(repo, "show", f"{rev}:{path}").stdout


def words(text):
    out = set()
    for w in re.findall(r"[a-z0-9][a-z0-9-]{3,}", text.lower()):
        if w in STOP or w in PATHISH:
            continue
        out.add(w)
    return out


def closure_items(repo, rev, n):
    text = show(repo, rev, f"corpus/lessons/round-{n}-verifier-spotcheck.md")
    items = {}
    for line in text.splitlines():
        m = re.match(r"\s*(?:-|\d+\.)\s+\*\*([DR]\d+)\b(.*)", line)
        if m:
            items[m.group(1)] = m.group(2)
    return items


def check_labels(repo, rev, spec_path=".ufo/waves/round-50/spec.json"):
    failures = []
    spec = json.loads(show(repo, rev, spec_path))
    pat = re.compile(r"round-(\d\d) closure ((?:[DR]\d)(?:/[DR]\d)*)")
    for item in spec["items"]:
        text = item.get("item", "")
        for m in pat.finditer(text):
            n, ids = m.group(1), m.group(2).split("/")
            after = text[m.end():m.end() + 130]
            descriptor = re.split(r"[.;:]| against | at ", after)[0]
            items = closure_items(repo, rev, n)
            bodies = [items[i] for i in ids if i in items]
            if len(bodies) != len(ids):
                failures.append(f"{item['name']}: round-{n} closure {m.group(2)} has no such item")
                continue
            seats = set(SEAT.findall(descriptor))
            body = " ".join(bodies)
            if seats:
                if seats <= set(SEAT.findall(body)):
                    continue
                failures.append(f"{item['name']}: round-{n} closure {m.group(2)} cited with seats "
                                f"{sorted(seats)} but the item names {sorted(set(SEAT.findall(body)))}")
                continue
            desc = words(descriptor)
            if not desc or desc & words(body):
                continue
            failures.append(f"{item['name']}: round-{n} closure {m.group(2)} described as "
                            f"{descriptor.strip()!r} but the item says {body.strip()[:95]!r}")
    return failures


def check_routed(repo, rev, rounds=("48", "49", "50")):
    failures, detail = [], []
    for n in rounds:
        raw = show(repo, rev, f".ufo/waves/round-{n}/preregistration.json")
        pre = json.loads(raw) if raw.strip() else {}
        has = any(k in pre for k in ("routed", "carried"))
        prev = str(int(n) - 1)
        lane = [i for i, b in closure_items(repo, rev, prev).items()
                if not re.search(r"operator|driver", b, re.I)]
        detail.append((f"round-{n}", has, len(lane)))
        if not has and lane:
            failures.append(f"round-{n}: preregistration has no routed/carried block; "
                            f"round-{prev} closure routed {len(lane)} lane item(s)")
    return failures, detail


def check_sweep(repo, rev, rounds=("48", "49")):
    hits = git(repo, "grep", "-l", "N5Mistakes", rev, "--", "corpus", "registry").stdout.split()
    failures, detail = [], []
    for n in rounds:
        cited = any(f"round-{n}" in h for h in hits)
        detail.append((f"round-{n}", cited))
        if not cited:
            failures.append(f"round-{n}: .ufo/waves/round-{n}/w1/out/N5Mistakes/sweep.md "
                            f"is cited by no committed corpus/ or registry/ file")
    return failures, detail


def check_limits(repo, rev, need=("sub-20", "prerelease", "b11906")):
    text = show(repo, rev, ".ufo/waves/round-50/preregistration.json").lower()
    return [f"round-50 preregistration limits do not name carried limit {t!r} "
            f"(round-49 closure R5)" for t in need if t not in text]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--rev", default="HEAD")
    a = ap.parse_args()
    la = check_labels(a.repo, a.rev)
    lb, rb = check_routed(a.repo, a.rev)
    lc, rc = check_sweep(a.repo, a.rev)
    ld = check_limits(a.repo, a.rev)
    for name, fails in (("A label-resolution", la), ("B routed-block", lb),
                        ("C sweep-consumed", lc), ("D carried-limits", ld)):
        print(f"== check {name}: {'PASS' if not fails else 'FAIL'} ({len(fails)} finding(s))")
        for f in fails:
            print("   -", f)
    print("\nB detail (round, has_routed_block, lane_items_in_prev_closure):", rb)
    print("C detail (round, sweep_cited_by_committed_file):", rc)
    bad = len(la) + len(lb) + len(lc) + len(ld)
    print(f"\nRESULT: {bad} finding(s); exit 1" if bad else "\nRESULT: all checks pass; exit 0")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
