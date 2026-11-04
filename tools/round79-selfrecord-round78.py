#!/usr/bin/env python3
"""round79-selfrecord-round78.py - round-79 C1 (calibration): grade the round-78 self-record.

The round-78 record is `SCORECARD.md` section `## Round 78 ...` at the sealed revision
(round 78's tip).  Six facts that record declares are re-derived from the tree at that
revision; a fact whose declared value does not re-derive is stale, and a stale fact is
answered only by exactly one dated, value-bound correction block in the round-79 lesson
(`corpus/lessons/round-79.md`, section `## Corrections`) whose `at` is the sealed revision,
whose `old` is the declared value, and whose `new` itself re-derives at the tip.

PREDICATE (frozen: plans/round-79-claims.md section C1):

    `python3 tools/round79-selfrecord-round78.py --repo <lane>` prints one
    `SELFRECORD_R78 claims=6 mismatches=0 corrected=2 unbacked=0` line and exits 0 only
    when each of the six facts the round-78 self-record declares re-derives from the tree
    at the sealed revision 7a3cd98243b69fcbee0cc9e31878782bd8459320, or is answered by
    exactly one committed correction block at that revision whose stated new value
    re-derives at the tip; it exits 1 naming every unanswered fact otherwise.

Facts (each declared value is parsed from the record's own bytes at the sealed revision;
each observed value is derived from the tree at that same revision):

  F1 lowest-axis     the record's "the lowest assigned axis (calibration 7) carries C1"
                     sentence vs the sealed `## Axes` table over the assigned pair
  F2 population      "sources registry 292 rows ...; filtered knowledge entries 51" vs the
                     sealed source-row count and filtered knowledge-blob count
  F3 wave shape      the record's "One v1 wave of 12 seats (3 executor, ...)" sentence vs
                     `.ufo/waves/round-78/w1-spec.json` at the sealed revision
  F4 wave dead seats "Three seats returned output (...); nine returned empty" vs
                     `.ufo/waves/round-78/w1-results.json` at the sealed revision
  F5 tip accounting  "the tip accounting ... green at `rev=22cce544`" vs the sealed tip:
                     the named revision must be the sealed revision, not an ancestor
  F6 pre-correction  the record's freeze-divergence item 4 says the pre-correction tip run
                     "and the corrected tip run are both in the lesson"; the run's output
                     must be a committed blob under `.ufo/waves/round-78/` at the sealed
                     revision, not prose

A correction block is `corrected F<n> old=<value> new=<value> at=<40-hex> date=<ISO>`;
a block counts only when `at` is the sealed revision (40 hex, resolving to it), `old`
equals the fact's declared value, and `new` re-derives at the tip.

Exit codes: 0 every fact re-derives or is answered; 1 stale facts remain unanswered or a
correction's new value does not re-derive; 2 could-not-evaluate (repo absent, sealed
revision unresolvable, record section absent).

`--selftest` builds throwaway fixture repositories under a scratch dir and runs nine named
arms (golden, missing-correction, duplicate-correction, wrong-at, unbacked-new, bad-width,
fact-mutation, sealed-unresolvable, enumerate-mode).  `--work DIR` selects the scratch root
(honours TMPDIR); each fixture repo is created with `git init` and asserted to be its own
toplevel before the first commit.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SEALED = "7a3cd98243b69fcbee0cc9e31878782bd8459320"
RECORD_HEADING = "## Round 78"
LESSON_PATH = "corpus/lessons/round-79.md"
WAVE_DIR = ".ufo/waves/round-78"
AXES = ("operability", "freshness", "calibration", "depth", "coverage", "adjacency")
WAVE_ROLES = ("executor", "scribe", "scout", "connector", "reviewer", "critic",
              "mutation-tester")
ATTACK_ROLES = ("reviewer", "critic", "mutation-tester", "labrat")
ASSIGNED_AXES = ("operability", "calibration")


class Unevaluable(Exception):
    """The counter cannot grade (repo/sealed/record absent) - exit 2, never a pass."""


def resolve(repo: Path, rev: str) -> str | None:
    proc = subprocess.run(["git", "-C", str(repo), "rev-parse", "--verify", f"{rev}^{{commit}}"],
                          capture_output=True, text=True)
    if proc.returncode != 0:
        return None
    return proc.stdout.strip()


def show(repo: Path, rev: str, path: str) -> str | None:
    proc = subprocess.run(["git", "-C", str(repo), "show", f"{rev}:{path}"],
                          capture_output=True, text=True)
    if proc.returncode != 0:
        return None
    return proc.stdout


def norm(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def record_section(scorecard: str) -> str:
    out: list[str] = []
    inside = False
    for line in scorecard.split("\n"):
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


def axes_table(scorecard: str) -> dict[str, int]:
    """First axes table only: stop at the historical-table heading."""
    got: dict[str, int] = {}
    for line in scorecard.split("\n"):
        if line.startswith("### Historical axes table"):
            break
        m = re.match(r"^\|\s*\*{0,2}(operability|freshness|depth|coverage|calibration|adjacency)"
                     r"\*{0,2}\s*\|\s*\*{0,2}(\d+)\*{0,2}\s*\|", line)
        if m and m.group(1) not in got:
            got[m.group(1)] = int(m.group(2))
    return got


def canonical_rounds(scorecard: str, round_no: int) -> list[tuple[str, int]]:
    rows: list[tuple[str, int]] = []
    inside = False
    for line in scorecard.split("\n"):
        if line.startswith(f"**Capabilities — canonical list as of round {round_no}**"):
            inside = True
            continue
        if inside and line.startswith("### "):
            break
        if not inside or not line.startswith("| "):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 4 or cells[0] == "Capability" or set(cells[0]) <= set("-: "):
            continue
        try:
            first = int(cells[3])
        except ValueError:
            continue
        rows.append((cells[0], first))
    return rows


def knowledge_population(repo: Path, rev: str) -> tuple[int, list[str]]:
    proc = subprocess.run(["git", "-C", str(repo), "ls-tree", "-r", "--name-only", rev,
                           "--", "corpus/knowledge"], capture_output=True, text=True)
    files = [p for p in proc.stdout.split() if p.endswith(".md")]
    filtered = [p for p in files if "engine-sides" not in Path(p).name
                and "processes" not in Path(p).name]
    return len(filtered), [Path(p).stem for p in filtered]


def blob_shape(repo: Path, rev: str, path: str) -> tuple[str, int]:
    proc = subprocess.run(["git", "-C", str(repo), "show", f"{rev}:{path}"],
                          capture_output=True)
    if proc.returncode != 0:
        raise Unevaluable(f"{path} absent at {rev[:8]}")
    raw = proc.stdout
    return hashlib.sha256(raw).hexdigest(), raw.count(b"\n")


def sources_rows(repo: Path, rev: str) -> int:
    proc = subprocess.run(["git", "-C", str(repo), "show", f"{rev}:corpus/SOURCES.md"],
                          capture_output=True, text=True)
    if proc.returncode != 0:
        raise Unevaluable(f"corpus/SOURCES.md absent at {rev[:8]}")
    return len(re.findall(r"^ {0,3}\| *S[0-9]{3,}", proc.stdout, re.M))


def population_observed(repo: Path, rev: str) -> dict:
    knowledge, names = knowledge_population(repo, rev)
    skill, skill_lines = blob_shape(repo, rev, "SKILL.md")
    province, province_lines = blob_shape(repo, rev, "PROVINCE.md")
    return {"sources": sources_rows(repo, rev), "knowledge": knowledge,
            "skill": skill[:8], "skill_lines": skill_lines,
            "province": province[:8], "province_lines": province_lines,
            "names": names}


def wave_spec(repo: Path, rev: str) -> dict:
    raw = show(repo, rev, f"{WAVE_DIR}/w1-spec.json")
    if raw is None:
        raise Unevaluable(f"{WAVE_DIR}/w1-spec.json absent at {rev[:8]}")
    return json.loads(raw)


def wave_results(repo: Path, rev: str) -> dict:
    raw = show(repo, rev, f"{WAVE_DIR}/w1-results.json")
    if raw is None:
        raise Unevaluable(f"{WAVE_DIR}/w1-results.json absent at {rev[:8]}")
    return json.loads(raw)


def wave_mismatch_hits(repo: Path, rev: str) -> list[str]:
    listing = subprocess.run(["git", "-C", str(repo), "ls-tree", "-r", "--name-only", rev,
                              "--", WAVE_DIR], capture_output=True, text=True).stdout.split()
    hits: list[str] = []
    for path in listing:
        proc = subprocess.run(["git", "-C", str(repo), "show", f"{rev}:{path}"],
                              capture_output=True, text=True)
        if proc.returncode == 0 and "mismatches=1" in proc.stdout:
            hits.append(path)
    return hits


def value(key: str, payload: dict) -> str:
    if key == "axes":
        return "axes=" + ",".join(f"{axis}:{payload[axis]}" for axis in AXES)
    if key == "lowest-axis":
        return f"lowest-axis={payload['axis']}:{payload['score']}"
    if key == "population":
        return (f"population=sources:{payload['sources']},knowledge:{payload['knowledge']},"
                f"skill:{payload['skill']}/{payload['skill_lines']},"
                f"province:{payload['province']}/{payload['province_lines']}")
    if key == "wave":
        parts = [f"seats:{payload['seats']}"] + [
            f"{role}:{payload[role]}" for role in WAVE_ROLES] + [
            f"attack:{payload['attack']}/{payload['total']}"]
        return "wave=" + ",".join(parts)
    if key == "wave-dead":
        return (f"wave-dead=returned:{payload['returned']}({payload['names']})"
                f"/empty:{payload['empty']}")
    if key == "tip-accounting":
        return (f"tip-accounting=rev:{payload['rev']}/is-tip:"
                f"{'true' if payload['is-tip'] else 'false'}")
    if key == "c1-pre-correction-run":
        if payload["state"] == "committed" and "path" in payload:
            return f"c1-pre-correction-run=committed:{payload['path']}"
        return f"c1-pre-correction-run={payload['state']}"
    raise AssertionError(key)


def wave_observed(spec: dict) -> dict:
    items = spec.get("items") or []
    counts = {role: 0 for role in WAVE_ROLES}
    for item in items:
        if item.get("role") in counts:
            counts[item["role"]] += 1
    attack = sum(1 for item in items if item.get("role") in ATTACK_ROLES)
    return {"seats": len(items), **counts, "attack": attack, "total": len(items),
            "pct": round(100 * attack / len(items)) if items else 0}


def dead_observed(results: dict) -> dict:
    rows = results.get("results") or []
    returned = sorted(r.get("name", "") for r in rows if (r.get("output") or "").strip())
    return {"returned": len(returned), "names": ",".join(returned),
            "empty": len(rows) - len(returned)}


class Record:
    """Six declared facts of the round-78 self-record, each with declare/observe/verify."""

    def __init__(self, repo: Path, sealed: str):
        self.repo = repo
        self.sealed = sealed
        card = show(repo, sealed, "SCORECARD.md")
        if card is None:
            raise Unevaluable(f"SCORECARD.md absent at {sealed[:8]}")
        self.section = norm(record_section(card))
        self.card = card

    def facts(self) -> list[tuple[str, str, str, callable]]:
        return [("F1", *self.f1(), self.verify_f1),
                ("F2", *self.f2(), self.verify_f2),
                ("F3", *self.f3(), self.verify_f3),
                ("F4", *self.f4(), self.verify_f4),
                ("F5", *self.f5(), self.verify_f5),
                ("F6", *self.f6(), self.verify_f6)]

    def f1(self) -> tuple[str, str]:
        m = re.search(r"the lowest assigned axis \(calibration (\d+)\) carries C1",
                      self.section)
        if not m:
            raise Unevaluable("F1: record's 'lowest assigned axis' sentence absent")
        table = axes_table(self.card)
        if set(table) != set(AXES):
            raise Unevaluable(f"F1: sealed axes table incomplete: {sorted(table)}")
        low = min(ASSIGNED_AXES, key=lambda axis: table[axis])
        return (value("lowest-axis", {"axis": "calibration", "score": int(m.group(1))}),
                value("lowest-axis", {"axis": low, "score": table[low]}))

    def f2(self) -> tuple[str, str]:
        m_src = re.search(r"sources registry (\d+) rows with the census exit 0", self.section)
        m_k = re.search(r"filtered knowledge entries (\d+) \(two new: `([^`]+)`, "
                        r"`([^`]+)`\)", self.section)
        m_skill = re.search(r"`SKILL\.md` sha256 `([0-9a-f]+)…` \((\d+) lines", self.section)
        m_prov = re.search(r"`PROVINCE\.md` sha256 `([0-9a-f]+)…` \((\d+) lines", self.section)
        if not (m_src and m_k and m_skill and m_prov):
            raise Unevaluable("F2: record's population sentence is incomplete")
        declared = {"sources": int(m_src.group(1)), "knowledge": int(m_k.group(1)),
                    "skill": m_skill.group(1), "skill_lines": int(m_skill.group(2)),
                    "province": m_prov.group(1), "province_lines": int(m_prov.group(2)),
                    "names": []}
        observed = population_observed(self.repo, self.sealed)
        declared["names"] = [m_k.group(2), m_k.group(3)]
        if not all(name in observed["names"] for name in declared["names"]):
            observed = dict(observed)
            observed["names"] = sorted(set(observed["names"]) - set(declared["names"]))
        return value("population", declared), value("population", observed)

    def f3(self) -> tuple[str, str]:
        m = re.search(r"One v1 wave of (\d+) seats \((\d+) executor, (\d+) scribe, "
                      r"(\d+) scout, (\d+) connector, (\d+) reviewer, (\d+) critic, "
                      r"(\d+) mutation-tester; attack (\d+)/(\d+) = (\d+) %\)", self.section)
        if not m:
            raise Unevaluable("F3: record's wave-shape sentence absent")
        declared = dict(zip(("seats",) + WAVE_ROLES + ("attack", "total", "pct"),
                            (int(g) for g in m.groups())))
        return (value("wave", declared),
                value("wave", wave_observed(wave_spec(self.repo, self.sealed))))

    def f4(self) -> tuple[str, str]:
        m = re.search(r"Three seats returned output \(([^)]*)\); nine returned empty",
                      self.section)
        if not m:
            raise Unevaluable("F4: record's dead-seat sentence absent")
        names = sorted(p.strip() for p in m.group(1).split(","))
        return (value("wave-dead", {"returned": len(names), "names": ",".join(names),
                                    "empty": 9}),
                value("wave-dead", dead_observed(wave_results(self.repo, self.sealed))))

    def f5(self) -> tuple[str, str]:
        m = re.search(r"which is green at `rev=([0-9a-f]{7,40})`", self.section)
        if not m:
            raise Unevaluable("F5: record's tip-accounting revision absent")
        rev = m.group(1)
        full = resolve(self.repo, rev)
        return (value("tip-accounting", {"rev": rev, "is-tip": True}),
                value("tip-accounting", {"rev": rev, "is-tip": bool(full)
                                         and full == self.sealed}))

    def f6(self) -> tuple[str, str]:
        if "the pre-correction tip run and the corrected tip run are both in the lesson" \
                not in self.section:
            raise Unevaluable("F6: record's pre-correction-run sentence absent")
        hits = wave_mismatch_hits(self.repo, self.sealed)
        return (value("c1-pre-correction-run", {"state": "committed"}),
                value("c1-pre-correction-run", {"state": "absent", "blobs": len(hits)}))

    def verify_f1(self, token: str) -> bool:
        card = show(self.repo, "master", "SCORECARD.md") or self.card
        table = axes_table(card)
        low = min(ASSIGNED_AXES, key=lambda axis: table[axis])
        return token == value("lowest-axis", {"axis": low, "score": table[low]})

    def verify_f2(self, token: str) -> bool:
        return token == value("population", population_observed(self.repo, "master"))

    def verify_f3(self, token: str) -> bool:
        return token == value("wave", wave_observed(wave_spec(self.repo, "master")))

    def verify_f4(self, token: str) -> bool:
        return token == value("wave-dead",
                              dead_observed(wave_results(self.repo, "master")))

    def verify_f5(self, token: str) -> bool:
        m = re.match(r"^tip-accounting=rev:([0-9a-f]{7,40})/is-tip:(true|false)$", token)
        if not m:
            return False
        full = resolve(self.repo, m.group(1))
        tip = resolve(self.repo, "master")
        if not full or not tip:
            return False
        return (full == tip) is (m.group(2) == "true")

    def verify_f6(self, token: str) -> bool:
        m = re.match(r"^c1-pre-correction-run=committed:(.+)$", token)
        if not m:
            return False
        raw = show(self.repo, "master", m.group(1))
        return bool(raw) and "mismatches=1" in raw


# The record's own bullet shape wraps every token in backticks (round-78 style); a plain
# `corrected F<n> old=... new=...` line is accepted too so a fixture needs no markup.
CORRECTION_BULLET_RE = re.compile(
    r"`corrected (F\d)` old=`([^`]*)` new=`([^`]*)` at=`([0-9a-fA-F]+)` "
    r"date=`(\d{4}-\d{2}-\d{2})`")
CORRECTION_PLAIN_RE = re.compile(
    r"corrected (F\d) old=(\S+) new=(\S+) at=([0-9a-fA-F]+) date=(\d{4}-\d{2}-\d{2})")


def corrections(repo: Path, rev: str) -> list[dict]:
    raw = show(repo, rev, LESSON_PATH)
    if raw is None:
        return []
    text = norm(raw)
    matches = list(CORRECTION_BULLET_RE.finditer(text)) or list(
        CORRECTION_PLAIN_RE.finditer(text))
    return [{"fact": m.group(1), "old": m.group(2), "new": m.group(3),
             "at": m.group(4), "date": m.group(5)} for m in matches]


def audit(repo: Path, sealed: str, tip: str) -> dict:
    record = Record(repo, sealed)
    facts = record.facts()
    blocks = corrections(repo, tip)
    rows = []
    corrected = 0
    unbacked = 0
    stale = 0
    for name, declared, observed, verify in facts:
        is_stale = declared != observed
        if is_stale:
            stale += 1
        matched = [b for b in blocks if b["fact"] == name and b["old"] == declared]
        ok = False
        if is_stale and len(matched) == 1:
            block = matched[0]
            at_ok = block["at"].lower() == sealed.lower() and len(block["at"]) == 40
            if at_ok and verify(block["new"]):
                ok = True
                corrected += 1
            else:
                unbacked += 1
        rows.append({"fact": name, "stale": is_stale, "declared": declared,
                     "observed": observed, "corrected": ok, "blocks": len(matched)})
    mismatches = sum(1 for r in rows if r["stale"] and not r["corrected"])
    return {"claims": len(rows), "rows": rows, "mismatches": mismatches,
            "corrected": corrected, "unbacked": unbacked, "stale": stale}


# ------------------------------------------------------------------ fixtures
def git(repo: Path, *args: str) -> str:
    proc = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"fixture git {' '.join(args)}: {proc.stderr.strip()[:300]}")
    return proc.stdout


FIXTURE_SPEC = {"items": [{"name": f"EX{i:02d}", "role": role} for i, role in enumerate(
    ["executor"] * 3 + ["scribe"] * 3 + ["scout", "connector", "reviewer",
                                        "critic", "critic", "mutation-tester"])]}
FIXTURE_RESULTS = {"results": [
    {"name": name, "output": out} for name, out in
    [("EX01", "ok"), ("SC02", "ok"), ("SCT01", "ok")] + [(f"X{i:02d}", "") for i in range(9)]]}
FIXTURE_AXES_TABLE = (
    "| **operability** | **8** | e | r |\n| **freshness** | **8** | e | r |\n"
    "| depth | **7** | e | r |\n| coverage | **9** | e | r |\n"
    "| calibration | **7** | e | r |\n| adjacency | **7** | e | r |\n")
FIXTURE_CAPS = (
    "**Capabilities — canonical list as of round 78**\n\n"
    "| Capability | What | Evidence | First |\n|---|---|---|---|\n"
    "| a | x | p | 77 |\n| b | x | p | 78 |\n| c | x | p | 78 |\n| d | x | p | 78 |\n"
    "\n### next\n")


def fixture_card(ancestor: str, pop: dict, mutate: str = "") -> str:
    dead = "Three seats returned output (EX01,SC02,SCT01); nine returned empty"
    lowest = 6 if mutate == "axes" else 7
    return (
        f"# card\n\n## Axes\n\n| Axis | Score | Evidence | Last |\n|---|---|---|---|\n"
        f"{FIXTURE_AXES_TABLE}\n### Historical axes table\n\n"
        f"| operability (worked round 1) | 0 -> 8 | e | r |\n\n"
        f"## Round 78 — fixture record (2026-11-04)\n\n"
        f"Three claims on three distinct axes; the lowest assigned axis "
        f"(calibration {lowest}) carries C1. Population at `rev={ancestor}`: sources "
        f"registry {pop['sources']} rows with the census exit 0; filtered knowledge "
        f"entries {pop['knowledge']} (two new: `entry-a`, `entry-b`); `SKILL.md` sha256 "
        f"`{pop['skill']}…` ({pop['skill_lines']} lines, gate row rewritten in place); "
        f"`PROVINCE.md` sha256 `{pop['province']}…` ({pop['province_lines']} lines, three "
        f"instruments appended). {dead}. One v1 wave of 12 seats (3 executor, 3 scribe, "
        f"1 scout, 1 connector, 1 reviewer, 2 critic, 1 mutation-tester; attack 4/12 = "
        f"33 %). The tip accounting is the counter, which is green at `rev={ancestor}`.\n\n"
        f"### Freeze divergences\n\n4. the pre-correction tip run and the corrected tip "
        f"run are both in the lesson.\n\n{FIXTURE_CAPS}")


def build_fixture(root: Path, mutate: str = "", corrections: str | None = None,
                  at_token: str | None = None) -> tuple[Path, str]:
    """Three commits: skeleton, sealed record, corrections (+tip receipt)."""
    repo = root / f"fixture-{mutate or 'golden'}"
    if repo.exists():
        shutil.rmtree(repo)
    repo.mkdir(parents=True)
    subprocess.run(["git", "-C", str(repo), "init", "-q"], check=True, capture_output=True)
    toplevel = Path(git(repo, "rev-parse", "--show-toplevel").strip()).resolve()
    if toplevel != repo.resolve():
        raise RuntimeError(f"fixture toplevel {toplevel} != {repo}")
    git(repo, "symbolic-ref", "HEAD", "refs/heads/master")
    git(repo, "config", "user.name", "fixture")
    git(repo, "config", "user.email", "fixture@example.invalid")

    (repo / "README.md").write_text("fixture\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "skeleton")
    ancestor = git(repo, "rev-parse", "--short=8", "HEAD").strip()

    (repo / WAVE_DIR).mkdir(parents=True)
    (repo / "corpus" / "lessons").mkdir(parents=True)
    (repo / "corpus" / "knowledge").mkdir(parents=True)
    rows = ["| S001 | a | docs | A | s | a | t | mined | 2026-11-04 | 90d | . |",
            "| S002 | a | docs | A | s | a | t | mined | 2026-11-04 | 90d | . |",
            "| S003 | a | docs | A | s | a | t | mined | 2026-11-04 | 90d | . |"]
    if mutate == "population":
        rows.append("| S004 | a | docs | A | s | a | t | mined | 2026-11-04 | 90d | . |")
    (repo / "corpus" / "SOURCES.md").write_text("# SOURCES\n\n" + "\n".join(rows) + "\n")
    (repo / "corpus" / "knowledge" / "entry-a.md").write_text("a\n")
    (repo / "corpus" / "knowledge" / "entry-b.md").write_text("b\n")
    (repo / "SKILL.md").write_text("s1\ns2\ns3\ns4\ns5\n")
    (repo / "PROVINCE.md").write_text("p1\np2\np3\np4\np5\np6\np7\n")
    skill = hashlib.sha256((repo / "SKILL.md").read_bytes()).hexdigest()[:8]
    province = hashlib.sha256((repo / "PROVINCE.md").read_bytes()).hexdigest()[:8]
    pop = {"sources": len(rows), "knowledge": 2, "skill": skill, "skill_lines": 5,
           "province": province, "province_lines": 7}
    (repo / "SCORECARD.md").write_text(fixture_card(ancestor, pop, mutate))
    results = FIXTURE_RESULTS if mutate != "results" else {"results": [
        {"name": "EX01", "output": "ok"}, {"name": "SC02", "output": "ok"}] + [
        {"name": f"X{i:02d}", "output": ""} for i in range(10)]}
    (repo / WAVE_DIR / "w1-spec.json").write_text(json.dumps(FIXTURE_SPEC))
    (repo / WAVE_DIR / "w1-results.json").write_text(json.dumps(results))
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "sealed record")
    sealed = git(repo, "rev-parse", "master").strip()

    token = at_token or sealed
    if corrections is None:
        corrections = (
            f"# fixture lesson\n\n## Corrections\n\n"
            f"corrected F5 old=tip-accounting=rev:{ancestor}/is-tip:true "
            f"new=tip-accounting=rev:{ancestor}/is-tip:false at={token} date=2026-11-04\n\n"
            f"corrected F6 old=c1-pre-correction-run=committed "
            f"new=c1-pre-correction-run=committed:.ufo/waves/round-79/measured/v2/pre.out "
            f"at={token} date=2026-11-04\n")
    (repo / LESSON_PATH).write_text(corrections)
    receipt = repo / ".ufo" / "waves" / "round-79" / "measured" / "v2"
    receipt.mkdir(parents=True)
    (receipt / "pre.out").write_text("SELFRECORD_R77 claims=6 mismatches=1 corrected=0\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "corrections")
    return repo, sealed


def run(repo: Path, sealed: str, *extra: str) -> tuple[int, str]:
    import contextlib
    import io
    old = sys.argv
    sys.argv = ["round79-selfrecord-round78.py", "--repo", str(repo), "--sealed", sealed,
                "--tip", "master", *extra]
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            rc, message = main()
    finally:
        sys.argv = old
    return rc, (message + "\n" + buf.getvalue()).strip()


def selftest(work: Path) -> int:
    arms: list[tuple[str, bool, str]] = []
    root = work / "fixtures"
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True)

    def arm(name: str, cond: bool, detail: str = "") -> None:
        arms.append((name, cond, detail))

    repo, sealed = build_fixture(root, "golden")
    rc, out = run(repo, sealed)
    arm("golden", rc == 0 and "claims=6 mismatches=0 corrected=2 unbacked=0" in out,
        out[-200:])

    repo, sealed = build_fixture(root, "missing")
    lesson = (repo / LESSON_PATH).read_text()
    (repo / LESSON_PATH).write_text(lesson.split("corrected F6")[0])
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "drop F6")
    rc, out = run(repo, sealed)
    arm("missing-correction", rc == 1 and "mismatches=1 corrected=1" in out, out[-200:])

    repo, sealed = build_fixture(root, "duplicate")
    lesson = (repo / LESSON_PATH).read_text()
    first = next(l for l in lesson.splitlines() if l.startswith("corrected F5"))
    (repo / LESSON_PATH).write_text(lesson + first + "\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "duplicate F5")
    rc, out = run(repo, sealed)
    arm("duplicate-correction", rc == 1 and "mismatches=1" in out, out[-200:])

    repo, sealed = build_fixture(root, "wrongat", at_token="b" * 40)
    rc, out = run(repo, sealed)
    arm("wrong-at", rc == 1 and "mismatches=2" in out and "unbacked=2" in out, out[-200:])

    repo, sealed = build_fixture(root, "unbacked")
    lesson = re.sub(r"(new=tip-accounting=rev:)([0-9a-f]+)(/is-tip:)false",
                    r"\1\2\3true", (repo / LESSON_PATH).read_text())
    (repo / LESSON_PATH).write_text(lesson)
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "unbacked")
    rc, out = run(repo, sealed)
    arm("unbacked-new", rc == 1 and "unbacked=1" in out, out[-200:])

    repo, sealed = build_fixture(root, "badwidth", at_token=sealed + "a")
    rc, out = run(repo, sealed)
    arm("bad-width", rc == 1 and "mismatches=2" in out and "unbacked=2" in out,
        out[-200:])

    repo, sealed = build_fixture(root, "results")
    rc, out = run(repo, sealed)
    arm("fact-mutation", rc == 1 and "F4 stale" in out and "mismatches=1" in out,
        out[-200:])

    repo, _ = build_fixture(root, "sealedbad")
    rc, out = run(repo, "0" * 40)
    arm("sealed-unresolvable", rc == 2 and "could-not-evaluate" in out, out[-200:])

    repo, sealed = build_fixture(root, "enumerate")
    rc, out = run(repo, sealed, "--enumerate")
    arm("enumerate-mode",
        rc == 1 and "SELFRECORD_R78_ENUM claims=6 stale=2 corrected=0" in out, out[-200:])

    failed = 0
    for name, ok, detail in arms:
        print(f"SELFRECORD_R78_SELFTEST {name} {'PASS' if ok else 'FAIL'}"
              + ("" if ok else " " + detail.replace("\n", " | ")))
        if not ok:
            failed += 1
    print(f"SELFRECORD_R78_SELFTEST pass={len(arms) - failed} fail={failed}")
    return 0 if failed == 0 else 1


def main() -> tuple[int, str]:
    ap = argparse.ArgumentParser(description="grade the round-78 self-record")
    ap.add_argument("--repo", default=".")
    ap.add_argument("--sealed", default=SEALED)
    ap.add_argument("--tip", default="master")
    ap.add_argument("--enumerate", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--work", default=None)
    args = ap.parse_args()

    if args.selftest:
        base = Path(args.work) if args.work else Path(tempfile.mkdtemp(
            prefix="selftest-", dir=os.environ.get("TMPDIR")))
        base.mkdir(parents=True, exist_ok=True)
        try:
            rc = selftest(base)
        finally:
            shutil.rmtree(base, ignore_errors=True)
        return rc, ""

    repo = Path(args.repo).resolve()
    if not (repo / ".git").exists() and not (repo / "SCORECARD.md").exists():
        return 2, f"could-not-evaluate: {repo} is not a lane repository"
    sealed = resolve(repo, args.sealed)
    if not sealed:
        return 2, f"could-not-evaluate: sealed revision {args.sealed} does not resolve"
    tip = resolve(repo, args.tip)
    if not tip:
        return 2, f"could-not-evaluate: tip revision {args.tip} does not resolve"
    try:
        result = audit(repo, sealed, tip)
    except Unevaluable as exc:
        return 2, f"could-not-evaluate: {exc}"

    if args.json:
        result.update({"sealed": sealed, "tip": tip})
        print(json.dumps(result, indent=2))
    if args.enumerate:
        print(f"SELFRECORD_R78_ENUM claims={result['claims']} stale={result['stale']} "
              f"corrected=0 | sealed={sealed} tip={tip}")
    else:
        for row in result["rows"]:
            print(f"SELFRECORD_R78_FACT {row['fact']} "
                  f"{'stale' if row['stale'] else 'fresh'} "
                  f"corrected={'yes' if row['corrected'] else 'no'}")
        print(f"SELFRECORD_R78 claims={result['claims']} mismatches={result['mismatches']} "
              f"corrected={result['corrected']} unbacked={result['unbacked']} "
              f"| sealed={sealed} tip={tip}")
    ok = result["mismatches"] == 0 and result["unbacked"] == 0
    if args.enumerate:
        ok = result["stale"] == 0
    return (0 if ok else 1), ""


if __name__ == "__main__":
    code, message = main()
    if message:
        print(message)
    sys.exit(code)
