#!/usr/bin/env python3
"""EX01C1Facts/rederive.py — independent re-derivation of the six round-78 facts.

Seat EX01 (kama round 79 w1). Re-derives, WITHOUT importing or executing the lane
counter (tools/round79-selfrecord-round78.py), the six facts that
plans/round-79-claims.md §C1 freezes:

  F1 lowest assigned axis  declared by the round-78 record sentence, observed in the
                           sealed `## Axes` table over the record's assigned pair
  F2 population            record's population sentence vs counts/hashes at sealed
  F3 wave shape            record's wave sentence vs .ufo/waves/round-78/w1-spec.json
  F4 wave dead seats       record's dead-seat sentence vs w1-results.json
  F5 tip accounting        record's `rev=22cce544` green claim vs the sealed tip
  F6 pre-correction run    record's "both in the lesson" claim vs committed blobs
                           under .ufo/waves/round-78/ carrying `mismatches=1`

Every fact is read from `git show <sealed>:...` (never the worktree). Declared value
strings are the frozen §C1 receipt labels; observed value strings are rebuilt from the
sealed tree by this harness's own parsing.

Output: one line per fact
    EX01 <Fk> declared=<value> observed=<value> match=yes|no
then `EX01 summary claims=6 mismatches=<n> stale=<csv|none>`.

Exit: 0 all six match; 1 at least one mismatch; 2 unevaluable (record/sealed absent).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
SEALED = "7a3cd98243b69fcbee0cc9e31878782bd8459320"
RECORD_HEADING = "## Round 78"
WAVE_DIR = ".ufo/waves/round-78"
AXES = ("operability", "freshness", "depth", "coverage", "calibration", "adjacency")
WAVE_ROLES = ("executor", "scribe", "scout", "connector", "reviewer", "critic",
              "mutation-tester")
BUILD_ROLES = ("executor", "scribe", "scout", "connector")
ATTACK_ROLES = ("reviewer", "critic", "mutation-tester", "labrat")
WORD_NUM = {"three": 3, "four": 4, "five": 5, "six": 6, "seven": 7,
            "eight": 8, "nine": 9, "ten": 10}
ELL = "\u2026"


class Unevaluable(Exception):
    pass


def git(repo: Path, *args: str, text: bool = True) -> tuple[int, str]:
    proc = subprocess.run(["git", "-C", str(repo), *args],
                          capture_output=True, text=text)
    out = proc.stdout if text else proc.stdout.decode("utf-8", "replace")
    return proc.returncode, out


def show_text(repo: Path, rev: str, path: str) -> str | None:
    rc, out = git(repo, "show", f"{rev}:{path}")
    return out if rc == 0 else None


def show_bytes(repo: Path, rev: str, path: str) -> bytes | None:
    proc = subprocess.run(["git", "-C", str(repo), "show", f"{rev}:{path}"],
                          capture_output=True)
    return proc.stdout if proc.returncode == 0 else None


def resolve(repo: Path, rev: str) -> str | None:
    rc, out = git(repo, "rev-parse", "--verify", f"{rev}^{{commit}}")
    return out.strip() if rc == 0 else None


def norm(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def record_section(card: str) -> str:
    out: list[str] = []
    inside = False
    for line in card.split("\n"):
        if line.startswith(RECORD_HEADING):
            inside = True
            out.append(line)
            continue
        if inside and line.startswith("## "):
            break
        if inside:
            out.append(line)
    if not inside:
        raise Unevaluable("SCORECARD.md has no '## Round 78' section at the sealed revision")
    return "\n".join(out)


def assigned_pair(card: str) -> tuple[str, str]:
    m = re.search(r"assigned axes are (\w+) \+ (\w+)", norm(card))
    if not m:
        raise Unevaluable("record banner does not name the assigned axis pair")
    return m.group(1), m.group(2)


def axes_table(card: str) -> dict[str, int]:
    """First axes table only: stop at the historical-table heading."""
    got: dict[str, int] = {}
    for line in card.split("\n"):
        if line.startswith("### Historical axes table"):
            break
        m = re.match(r"^\|\s*\*{0,2}(operability|freshness|depth|coverage|calibration|adjacency)"
                     r"\*{0,2}\s*\|\s*\*{0,2}(\d+)\*{0,2}\s*\|", line)
        if m and m.group(1) not in got:
            got[m.group(1)] = int(m.group(2))
    return got


def sources_rows(repo: Path, rev: str) -> int:
    raw = show_text(repo, rev, "corpus/SOURCES.md")
    if raw is None:
        raise Unevaluable("corpus/SOURCES.md absent at sealed")
    return len(re.findall(r"^ {0,3}\| *S[0-9]{3,}", raw, re.M))


def knowledge_population(repo: Path, rev: str) -> int:
    rc, out = git(repo, "ls-tree", "-r", "--name-only", rev, "--", "corpus/knowledge")
    if rc != 0:
        raise Unevaluable("corpus/knowledge absent at sealed")
    files = [p for p in out.split() if p.endswith(".md")]
    filtered = [p for p in files if "engine-sides" not in Path(p).name
                and "processes" not in Path(p).name]
    return len(filtered)


def blob_shape(repo: Path, rev: str, path: str) -> tuple[str, int]:
    raw = show_bytes(repo, rev, path)
    if raw is None:
        raise Unevaluable(f"{path} absent at sealed")
    return hashlib.sha256(raw).hexdigest()[:8], raw.count(b"\n")


def fmt_lowest(axis: str, score: int) -> str:
    return f"lowest-axis={axis}:{score}"


def fmt_pop(sources: int, knowledge: int, skill: str, skill_lines: int,
            province: str, province_lines: int) -> str:
    return (f"population=sources:{sources},knowledge:{knowledge},"
            f"skill:{skill}/{skill_lines},province:{province}/{province_lines}")


def fact_f1(repo: Path, card: str, section: str) -> tuple[str, str]:
    m = re.search(r"the lowest assigned axis \(calibration (\d+)\) carries C1", section)
    if not m:
        raise Unevaluable("F1: record's 'lowest assigned axis' sentence absent")
    declared = fmt_lowest("calibration", int(m.group(1)))
    a1, a2 = assigned_pair(card)
    table = axes_table(card)
    if a1 not in table or a2 not in table:
        raise Unevaluable(f"F1: assigned axis missing from sealed axes table: {a1},{a2}")
    low = min((a1, a2), key=lambda axis: table[axis])
    observed = fmt_lowest(low, table[low])
    return declared, observed


def fact_f2(repo: Path, section: str) -> tuple[str, str]:
    m_src = re.search(r"sources registry (\d+) rows with the census exit 0", section)
    m_k = re.search(r"filtered knowledge entries (\d+) \(two new: `[^`]+`, `[^`]+`\)",
                    section)
    m_skill = re.search(rf"`SKILL\.md` sha256 `([0-9a-f]+){ELL}` \((\d+) lines", section)
    m_prov = re.search(rf"`PROVINCE\.md` sha256 `([0-9a-f]+){ELL}` \((\d+) lines", section)
    if not (m_src and m_k and m_skill and m_prov):
        raise Unevaluable("F2: record's population sentence is incomplete")
    declared = fmt_pop(int(m_src.group(1)), int(m_k.group(1)),
                       m_skill.group(1), int(m_skill.group(2)),
                       m_prov.group(1), int(m_prov.group(2)))
    skill, skill_lines = blob_shape(repo, SEALED, "SKILL.md")
    province, province_lines = blob_shape(repo, SEALED, "PROVINCE.md")
    observed = fmt_pop(sources_rows(repo, SEALED), knowledge_population(repo, SEALED),
                       skill, skill_lines, province, province_lines)
    return declared, observed


def fact_f3(repo: Path, section: str) -> tuple[str, str]:
    m = re.search(r"One v1 wave of (\d+) seats \((\d+) executor, (\d+) scribe, "
                  r"(\d+) scout, (\d+) connector, (\d+) reviewer, (\d+) critic, "
                  r"(\d+) mutation-tester; attack (\d+)/(\d+) = (\d+) %\)", section)
    if not m:
        raise Unevaluable("F3: record's wave-shape sentence absent")
    seats = int(m.group(1))
    role_counts = [int(g) for g in m.groups()[1:8]]
    attack_d, total_d = int(m.group(9)), int(m.group(10))
    declared = (f"wave=seats:{seats}," +
                ",".join(f"{role}:{n}" for role, n in zip(WAVE_ROLES, role_counts)) +
                f",attack:{attack_d}/{total_d}")
    raw = show_text(repo, SEALED, f"{WAVE_DIR}/w1-spec.json")
    if raw is None:
        raise Unevaluable("F3: w1-spec.json absent at sealed")
    items = json.loads(raw).get("items") or []
    counts = {role: 0 for role in WAVE_ROLES}
    for item in items:
        if item.get("role") in counts:
            counts[item["role"]] += 1
    attack = sum(1 for item in items if item.get("role") in ATTACK_ROLES)
    complement = sum(1 for item in items if item.get("role") not in BUILD_ROLES)
    if attack != complement:
        raise Unevaluable(f"F3: attack-role set disagreement: {attack} vs {complement}")
    observed = (f"wave=seats:{len(items)}," +
                ",".join(f"{role}:{counts[role]}" for role in WAVE_ROLES) +
                f",attack:{attack}/{len(items)}")
    return declared, observed


def fact_f4(repo: Path, section: str) -> tuple[str, str]:
    m = re.search(r"(\w+) seats returned output \(([^)]*)\); (\w+) returned empty",
                  section)
    if not m:
        raise Unevaluable("F4: record's dead-seat sentence absent")
    names = sorted(p.strip() for p in m.group(2).split(",") if p.strip())
    returned_w = WORD_NUM.get(m.group(1).lower())
    empty_w = WORD_NUM.get(m.group(3).lower())
    if returned_w is None or empty_w is None or returned_w != len(names):
        raise Unevaluable(
            f"F4: record's dead-seat sentence inconsistent: '{m.group(0)}'")
    declared = f"wave-dead=returned:{len(names)}({','.join(names)})/empty:{empty_w}"
    raw = show_text(repo, SEALED, f"{WAVE_DIR}/w1-results.json")
    if raw is None:
        raise Unevaluable("F4: w1-results.json absent at sealed")
    rows = json.loads(raw).get("results") or []
    returned = sorted(r.get("name", "") for r in rows
                      if (r.get("output") or "").strip())
    observed = (f"wave-dead=returned:{len(returned)}({','.join(returned)})"
                f"/empty:{len(rows) - len(returned)}")
    return declared, observed


def fact_f5(repo: Path, section: str) -> tuple[str, str]:
    m = re.search(r"which is green at `rev=([0-9a-f]{7,40})`", section)
    if not m:
        raise Unevaluable("F5: record's tip-accounting revision absent")
    rev = m.group(1)
    declared = f"tip-accounting=rev:{rev}/is-tip:true"
    full = resolve(repo, rev)
    is_tip = full == SEALED
    observed = f"tip-accounting=rev:{rev}/is-tip:{'true' if is_tip else 'false'}"
    return declared, observed


def fact_f6(repo: Path, section: str) -> tuple[str, str]:
    if "the pre-correction tip run and the corrected tip run are both in the lesson" \
            not in section:
        raise Unevaluable("F6: record's pre-correction-run sentence absent")
    declared = "c1-pre-correction-run=committed"
    rc, listing = git(repo, "ls-tree", "-r", "--name-only", SEALED, "--", WAVE_DIR)
    if rc != 0:
        raise Unevaluable(f"F6: {WAVE_DIR} absent at sealed")
    hits: list[str] = []
    for path in listing.split():
        raw = show_bytes(repo, SEALED, path)
        if raw is not None and b"mismatches=1" in raw:
            hits.append(path)
    observed = (f"c1-pre-correction-run=committed:{hits[0]}" if hits
                else "c1-pre-correction-run=absent")
    return declared, observed


def main() -> int:
    global SEALED
    ap = argparse.ArgumentParser(description="independent EX01 re-derivation of the "
                                             "six round-78 facts (§C1)")
    ap.add_argument("--repo", default=LANE)
    ap.add_argument("--sealed", default=SEALED)
    args = ap.parse_args()
    repo = Path(args.repo).resolve()
    sealed = resolve(repo, args.sealed)
    if not sealed:
        print(f"EX01 ERROR could-not-evaluate: sealed revision {args.sealed} "
              f"does not resolve")
        return 2
    SEALED = sealed
    card = show_text(repo, sealed, "SCORECARD.md")
    if card is None:
        print(f"EX01 ERROR could-not-evaluate: SCORECARD.md absent at {sealed[:8]}")
        return 2
    try:
        section = norm(record_section(card))
        facts = [("F1", *fact_f1(repo, card, section)),
                 ("F2", *fact_f2(repo, section)),
                 ("F3", *fact_f3(repo, section)),
                 ("F4", *fact_f4(repo, section)),
                 ("F5", *fact_f5(repo, section)),
                 ("F6", *fact_f6(repo, section))]
    except Unevaluable as exc:
        print(f"EX01 ERROR could-not-evaluate: {exc}")
        return 2
    stale: list[str] = []
    for name, declared, observed in facts:
        ok = declared == observed
        if not ok:
            stale.append(name)
        print(f"EX01 {name} declared={declared} observed={observed} "
              f"match={'yes' if ok else 'no'}")
    print(f"EX01 summary claims={len(facts)} "
          f"mismatches={len(stale)} stale={','.join(stale) if stale else 'none'}")
    return 0 if not stale else 1


if __name__ == "__main__":
    sys.exit(main())
