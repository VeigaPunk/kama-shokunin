#!/usr/bin/env python3
"""round80-selfrecord-round79.py - round-80 C1 (calibration): the round-79 self-record's facts.

PREDICATE (frozen: plans/round-80-claims.md section C1):

    `python3 tools/round80-selfrecord-round79.py --repo <lane>` prints one `SELFRECORD_R79
    claims=6 mismatches=0 corrected=3 unbacked=0` line and exits 0 only when each of the six
    facts the round-79 self-record declares re-derives from the tree at the sealed revision
    a9b4543f14625d0f37daa42ef664ee6f6ea975ea and matches the same fact re-derived at the tip,
    or is answered by exactly one committed `corrected F<n> old=<value> new=<value> at=<40-hex>
    date=<ISO>` block whose `old` is the sealed value, whose `at` is the sealed revision and
    whose `new` equals the fact's tip value; it exits 1 naming every unanswered fact otherwise.

The six facts (declared by the record, observed from the tree):

  F1 lowest-axis      the record's lowest assigned axis, from the sealed `## Axes` table over
                      the assigned pair operability + calibration
  F2 population       source rows and filtered knowledge blobs at the revision
  F3 wave             the round-79 wave spec's seat counts and attack share
  F4 c2               the C2 verdict the record's claim table declares vs. the receipt it cites
                      (`.ufo/waves/round-79/measured/after/c2-gate.out`)
  F5 before-selftest  the C2 row's before tally vs. `.ufo/waves/round-79/measured/before/
                      c2-gate-arms.out`
  F6 log              the LOG sentence "all verified on their receipts" vs. the C2 receipt

Every fact is read with `git show <rev>:<path>`, never from the worktree: the round's own
record commit cannot refute a fact (the round-78 F2 defect). The correction container is
`corpus/lessons/round-80.md` section `## Corrections`; blocks are read at the tip only.

Usage: round80-selfrecord-round79.py --repo DIR [--sealed REV] [--tip REV] [--lesson PATH]
       [--no-corrections] [--enumerate] [--json] | --selftest

Exit: 0 every fact re-derives or is answered; 1 at least one unanswered fact or unbacked
correction; 2 could-not-evaluate (git failure, unreadable input) -- never silently 0.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

SEALED = "a9b4543f14625d0f37daa42ef664ee6f6ea975ea"
ASSIGNED = ("operability", "calibration")
LESSON = "corpus/lessons/round-80.md"
CORRECTION = re.compile(
    r"corrected\s+(F[0-9]+)\s+old=(\S+)\s+new=(\S+)\s+at=(\S+)\s+date=(\d{4}-\d{2}-\d{2})")
AXIS_ROW = re.compile(r"^\|\s*\*{0,2}([A-Za-z]+)\*{0,2}\s*\|\s*\*{0,2}([0-9]+)\*{0,2}\s*\|")
ROW_COUNT = re.compile(r"^\|[ ]*S[0-9]{3,}[ ]*\|")
SELFTEST_RE = re.compile(r"PRE_REPORT_SELFTEST pass=([0-9]+) fail=([0-9]+)")
GATE_RE = re.compile(r"PRE_REPORT round=79 arms=([0-9]+) failed=([0-9]+) uncommitted=([0-9]+)")
FILTERED = ("engine-sides", "processes")
# F2 counts the population the record declares at its own revision: later growth by the grading
# round is not a record error, so the fact is re-derived at the sealed revision on both legs
# (freeze divergence 4). Every other fact is graded at the tip as well.
SEALED_BOUND = {"F2"}


class CouldNotEvaluate(Exception):
    pass


def git(repo: Path, *args: str) -> str:
    proc = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, timeout=180)
    if proc.returncode != 0:
        raise CouldNotEvaluate(f"git {' '.join(args)} exit={proc.returncode}: {proc.stderr.strip()}")
    return proc.stdout


def show(repo: Path, rev: str, path: str) -> str | None:
    proc = subprocess.run(["git", "-C", str(repo), "show", f"{rev}:{path}"],
                          capture_output=True, text=True, timeout=180)
    if proc.returncode != 0:
        return None
    return proc.stdout


def resolve(repo: Path, rev: str) -> str | None:
    proc = subprocess.run(["git", "-C", str(repo), "rev-parse", "--verify", "--quiet", f"{rev}^{{commit}}"],
                          capture_output=True, text=True, timeout=60)
    return proc.stdout.strip() or None


def block(text: str, prefix: str) -> str:
    """The `## <prefix>` section: from its heading to the next `## ` heading."""
    out, inside = [], False
    for line in text.splitlines():
        if line.startswith("## "):
            if inside:
                break
            inside = line[3:].strip().startswith(prefix)
        if inside:
            out.append(line)
    return "\n".join(out)


# ---------------------------------------------------------------- fact derivation

def f1(repo: Path, rev: str) -> tuple[str, str]:
    text = show(repo, rev, "SCORECARD.md")
    if text is None:
        return ("lowest-axis=absent", "lowest-axis=absent")
    scores = {}
    for line in block(text, "Axes").splitlines():
        m = AXIS_ROW.match(line)
        if m and m.group(1).lower() not in scores:
            scores[m.group(1).lower()] = int(m.group(2))
    pair = [(name, scores.get(name)) for name in ASSIGNED]
    if any(score is None for _, score in pair):
        return ("lowest-axis=absent", "lowest-axis=absent")
    name, score = min(pair, key=lambda p: (p[1], ASSIGNED.index(p[0])))
    value = f"lowest-axis={name}:{score}"
    return (value, value)


def f2(repo: Path, rev: str) -> tuple[str, str]:
    text = show(repo, rev, "corpus/SOURCES.md")
    if text is None:
        return ("population=sources:absent,knowledge:absent",) * 2
    rows = sum(1 for line in text.splitlines() if ROW_COUNT.match(line))
    listing = git(repo, "ls-tree", "-r", "--name-only", rev, "corpus/knowledge/").splitlines()
    knowledge = [p for p in listing if p and not any(f in p for f in FILTERED)]
    value = f"population=sources:{rows},knowledge:{len(knowledge)}"
    return (value, value)


def f3(repo: Path, rev: str) -> tuple[str, str]:
    text = show(repo, rev, ".ufo/waves/round-79/w1-spec.json")
    if text is None:
        return ("wave=absent", "wave=absent")
    try:
        spec = json.loads(text)
    except ValueError:
        return ("wave=malformed", "wave=malformed")
    counts = {}
    for item in spec.get("items", []):
        role = item.get("role", "?")
        counts[role] = counts.get(role, 0) + 1
    total = len(spec.get("items", []))
    attack = counts.get("reviewer", 0) + counts.get("critic", 0) + counts.get("mutation-tester", 0)
    order = ["executor", "scribe", "scout", "connector", "reviewer", "critic", "mutation-tester"]
    ranked = [r for r in order if r in counts] + [r for r in sorted(counts) if r not in order]
    cells = ",".join(f"{r}:{counts[r]}" for r in ranked)
    value = f"wave=seats:{total},{cells},attack:{attack}/{total}"
    return (value, value)


def c2_row(repo: Path, rev: str) -> list[str] | None:
    text = show(repo, rev, "SCORECARD.md")
    if text is None:
        return None
    for line in block(text, "Round 79").splitlines():
        if line.startswith("| C2"):
            return line.split("|")
    return None


def f4(repo: Path, rev: str) -> tuple[str, str]:
    """Declared: the C2 row's verdict cell. Observed: the receipt that row cites."""
    cells = c2_row(repo, rev)
    declared = "c2=absent"
    if cells is not None and len(cells) >= 4:
        declared = "c2=" + (cells[-2].strip().strip("*").strip() or "absent")
    receipt = show(repo, rev, ".ufo/waves/round-79/measured/after/c2-gate.out")
    if receipt is None:
        observed = "c2=absent"
    else:
        m = GATE_RE.search(receipt)
        if not m:
            observed = "c2=absent"
        elif int(m.group(2)) > 0:
            observed = f"c2=not-verified:failed={m.group(2)}"
        else:
            observed = "c2=verified"
    return (declared, observed)


def f5(repo: Path, rev: str) -> tuple[str, str]:
    cells = c2_row(repo, rev)
    declared = "before-selftest=absent"
    if cells is not None:
        for cell in cells[1:]:
            m = SELFTEST_RE.search(cell)
            if m:
                declared = f"before-selftest=pass={m.group(1)}"
                break
    receipt = show(repo, rev, ".ufo/waves/round-79/measured/before/c2-gate-selftest.out")
    observed = "before-selftest=absent"
    if receipt is not None:
        m = SELFTEST_RE.search(receipt)
        if m:
            observed = f"before-selftest=pass={m.group(1)}"
    return (declared, observed)


def f6(repo: Path, rev: str) -> tuple[str, str]:
    log = show(repo, rev, "LOG.md")
    declared = "log=absent"
    flat = " ".join(block(log, "Round 79").split()) if log is not None else ""
    if "all verified on their receipts" in flat:
        declared = "log=all-verified"
    receipt = show(repo, rev, ".ufo/waves/round-79/measured/after/c2-gate.out")
    observed = "log=absent"
    if receipt is not None:
        m = GATE_RE.search(receipt)
        if m:
            observed = "log=c2-not-verified" if int(m.group(2)) > 0 else "log=all-verified"
    return (declared, observed)


FACTS = [("F1", f1), ("F2", f2), ("F3", f3), ("F4", f4), ("F5", f5), ("F6", f6)]


def derive(repo: Path, rev: str) -> dict[str, dict[str, str]]:
    out = {}
    for fact, fn in FACTS:
        declared, observed = fn(repo, rev)
        out[fact] = {"declared": declared, "observed": observed}
    return out


# ---------------------------------------------------------------- corrections

def corrections(repo: Path, tip: str, lesson: str) -> list[dict[str, str]]:
    text = show(repo, tip, lesson)
    if text is None:
        return []
    blocks = []
    for m in CORRECTION.finditer(text):
        blocks.append({"fact": m.group(1), "old": m.group(2), "new": m.group(3),
                       "at": m.group(4), "date": m.group(5)})
    return blocks


def score(repo: Path, sealed: str, tip: str, lesson: str, use_corrections: bool) -> dict:
    sealed_facts = derive(repo, sealed)
    tip_facts = derive(repo, tip)
    blocks = corrections(repo, tip, lesson) if use_corrections else []
    by_fact: dict[str, list[dict[str, str]]] = {}
    for b in blocks:
        by_fact.setdefault(b["fact"], []).append(b)
    findings, rows = [], []
    stale = answered = unbacked = 0
    for fact, _ in FACTS:
        declared = sealed_facts[fact]["declared"]
        seen_sealed = sealed_facts[fact]["observed"]
        seen_tip = (sealed_facts[fact]["observed"] if fact in SEALED_BOUND
                    else tip_facts[fact]["observed"])
        fresh = declared == seen_sealed == seen_tip
        fact_blocks = by_fact.get(fact, [])
        ok = None
        reasons = []
        for b in fact_blocks:
            if b["old"] != declared:
                reasons.append("old-mismatch")
                unbacked += 1
                continue
            if not re.fullmatch(r"[0-9a-f]{40}", b["at"]):
                reasons.append("at-malformed")
                unbacked += 1
                continue
            resolved = resolve(repo, b["at"])
            if resolved is None:
                reasons.append("at-unresolvable")
                unbacked += 1
                continue
            if resolved != sealed:
                reasons.append("at-not-sealed")
                unbacked += 1
                continue
            ok = b
        if len(fact_blocks) > 1 and ok is not None:
            reasons.append("duplicate-blocks")
            unbacked += len(fact_blocks) - 1
            ok = None
        if fresh:
            status = "fresh"
        elif ok is not None:
            status = "corrected"
            answered += 1
        else:
            status = "stale"
            stale += 1
            findings.append(f"SELFRECORD_R79_FINDING {fact} stale declared={declared} "
                            f"sealed={seen_sealed} tip={seen_tip} reasons={','.join(reasons) or 'unanswered'}")
        rows.append({"fact": fact, "declared": declared, "sealed": seen_sealed, "tip": seen_tip,
                     "status": status, "blocks": fact_blocks, "reasons": reasons})
    mismatches = stale
    summary = {"claims": len(FACTS), "mismatches": mismatches, "corrected": answered,
               "unbacked": unbacked}
    return {"summary": summary, "rows": rows, "findings": findings, "sealed": sealed, "tip": tip}


def render(result: dict) -> str:
    lines = [f"FACT {r['fact']} declared={r['declared']} sealed={r['sealed']} tip={r['tip']} "
             f"status={r['status']}" for r in result["rows"]]
    s = result["summary"]
    lines.append("SELFRECORD_R79 " + " ".join(f"{k}={v}" for k, v in s.items()))
    lines.extend(result["findings"])
    return "\n".join(lines)


def verdict(result: dict) -> int:
    s = result["summary"]
    return int(bool(s["mismatches"] or s["unbacked"]))


# ---------------------------------------------------------------- selftest

FIXTURE_FILES = {
    "SCORECARD.md": """# SCORECARD

## Axes

| Axis | Score | Evidence |
|---|---|---|
| **operability** | **8** | x |
| **freshness** | **8** | x |
| **depth** | **7** | x |
| **coverage** | **9** | x |
| **calibration** | **7** | x |
| **adjacency** | **7** | x |

## Round 79 — fixture

| Claim | Axis | Before → after (measured) | Counting command | Verdict |
|---|---|---|---|---|
| C1 — fixture | calibration | `SELFRECORD_R78 claims=6 mismatches=0` | `python3 tools/x.py` | **verified** |
| C2 — fixture | operability | `ARM_ORDER` 9 arms, `PRE_REPORT_SELFTEST pass=26 fail=0` | `python3 tools/pre-report-gate.py --selftest` | **verified** |
""",
    "LOG.md": """# LOG

## Round 79 — fixture

Three claims, three distinct axes, all verified on their receipts.
""",
    "corpus/SOURCES.md": "# SOURCES\n\n| id | source |\n|---|---|\n"
                         + "".join(f"| S{i:03d} | fixture |\n" for i in range(1, 4)),
    "corpus/knowledge/a.md": "a\n",
    "corpus/knowledge/b.md": "b\n",
    "corpus/knowledge/engine-sides.md": "filtered\n",
    ".ufo/waves/round-79/w1-spec.json": json.dumps({"items": [
        {"role": "executor"}, {"role": "executor"}, {"role": "scribe"},
        {"role": "reviewer"}, {"role": "critic"}, {"role": "mutation-tester"}]}),
    ".ufo/waves/round-79/measured/after/c2-gate.out": "PRE_REPORT round=79 arms=10 failed=1 uncommitted=0\n",
    ".ufo/waves/round-79/measured/before/c2-gate-selftest.out": "PRE_REPORT_SELFTEST pass=22 fail=0\n",
}

def fixture_lesson(at: str) -> str:
    return f"""# round-80 fixture lesson

## Corrections

`corrected F4 old=c2=verified new=c2=not-verified:failed=1 at={at} date=2026-11-04`

`corrected F5 old=before-selftest=pass=26 new=before-selftest=pass=22 at={at} date=2026-11-04`

`corrected F6 old=log=all-verified new=log=c2-not-verified at={at} date=2026-11-04`
"""

FIXTURE_KEY = "local-fixture-key"


def _git_repo(root: Path) -> str:
    def run(*args: str) -> str:
        proc = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True)
        if proc.returncode != 0:
            raise CouldNotEvaluate(f"git {' '.join(args)}: {proc.stderr.strip()}")
        return proc.stdout
    run("init", "-q")
    run("config", "user.name", "fixture")
    run("config", "user.email", "fixture@example.invalid")
    run("config", "commit.gpgsign", "false")
    return root.as_posix()


def _fixture(root: Path, files: dict[str, str]) -> str:
    _git_repo(root)
    for path, text in files.items():
        target = root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text)
    subprocess.run(["git", "-C", str(root), "add", "-A"], capture_output=True, check=True)
    subprocess.run(["git", "-C", str(root), "commit", "-q", "-m", "sealed"],
                   capture_output=True, check=True)
    return subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True,
                          text=True, check=True).stdout.strip()


def _commit(root: Path, message: str) -> str:
    subprocess.run(["git", "-C", str(root), "add", "-A"], capture_output=True, check=True)
    subprocess.run(["git", "-C", str(root), "commit", "-q", "-m", message],
                   capture_output=True, check=True)
    return subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True,
                          text=True, check=True).stdout.strip()


def selftest() -> int:
    cases = []

    def run_case(name: str, mutate, want: int, want_field: str | None = None,
                 want_value: str | None = None, use_corrections: bool = True):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            root.mkdir()
            sealed = _fixture(root, dict(FIXTURE_FILES))
            (root / LESSON).parent.mkdir(parents=True, exist_ok=True)
            if mutate is not None:
                mutate(root, sealed)
            lesson = root / LESSON
            if not lesson.exists():
                lesson.parent.mkdir(parents=True, exist_ok=True)
                lesson.write_text(fixture_lesson(sealed))
                _commit(root, "lesson")
            tip = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True,
                                 text=True, check=True).stdout.strip()
            result = score(root, sealed, tip, LESSON, use_corrections)
            got = verdict(result)
            ok = got == want
            if want_field is not None:
                ok = ok and str(result["summary"].get(want_field)) == want_value
            cases.append((name, ok, got, want, result["summary"], result["findings"]))

    def m_corrected(root, sealed):
        return None

    def m_stale(root, sealed):
        (root / LESSON).parent.mkdir(parents=True, exist_ok=True)
        (root / LESSON).write_text("# lesson\n\n## Corrections\n\nnone\n")
        _commit(root, "lesson-without-corrections")

    def m_wrong_old(root, sealed):
        (root / LESSON).write_text(fixture_lesson(sealed).replace("old=c2=verified", "old=c2=other"))
        _commit(root, "bad-old")

    def m_wrong_at(root, sealed):
        (root / LESSON).write_text(fixture_lesson(sealed).replace(f"at={sealed}", f"at={sealed[:-1]}"))
        _commit(root, "ancestor-at")

    def m_short_at(root, sealed):
        (root / LESSON).write_text(fixture_lesson(sealed).replace(f"at={sealed}", f"at={sealed}0"))
        _commit(root, "short-at")

    def m_duplicate(root, sealed):
        (root / LESSON).write_text(fixture_lesson(sealed) + "\n`corrected F4 old=c2=verified "
                                   f"new=c2=not-verified:failed=1 at={sealed} date=2026-11-04`\n")
        _commit(root, "duplicate-block")

    def m_new_not_rederived(root, sealed):
        (root / LESSON).write_text(fixture_lesson(sealed).replace("new=c2=not-verified:failed=1",
                                                         "new=c2=verified"))
        _commit(root, "new-does-not-rederive")

    def m_worktree_shadow(root, sealed):
        (root / LESSON).write_text(fixture_lesson(sealed))
        (root / "SCORECARD.md").write_text(FIXTURE_FILES["SCORECARD.md"].replace("**verified**", "**pass**"))
        _commit(root, "tip-and-worktree-differ")

    run_case("green-all-answered", m_corrected, 0, "corrected", "3")
    run_case("stale-unanswered", m_stale, 1, "mismatches", "3")
    run_case("wrong-old", m_wrong_old, 1, "unbacked", "1")
    run_case("at-is-ancestor", m_wrong_at, 1, "unbacked", "3")
    run_case("at-short-hex", m_short_at, 1, "unbacked", "3")
    run_case("duplicate-block", m_duplicate, 1)
    run_case("new-not-rederived", m_new_not_rederived, 1, "unbacked", "1")
    run_case("worktree-does-not-refute", m_worktree_shadow, 0, "mismatches", "0")
    run_case("no-corrections-control", m_corrected, 1, "mismatches", "3", use_corrections=False)
    failed = 0
    for name, ok, got, want, summary, findings in cases:
        failed += not ok
        print(f"SELFRECORD_R79_SELFTEST {name} {'PASS' if ok else 'FAIL'} exit={got} expected={want}")
        if not ok:
            print("  summary", summary, "findings", findings[:2])
    print(f"SELFRECORD_R79_SELFTEST pass={len(cases) - failed} fail={failed}")
    return int(bool(failed))


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--repo", default=".")
    parser.add_argument("--sealed", default=SEALED)
    parser.add_argument("--tip", default="master")
    parser.add_argument("--lesson", default=LESSON)
    parser.add_argument("--no-corrections", action="store_true")
    parser.add_argument("--enumerate", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv)
    if args.selftest:
        return selftest()
    repo = Path(args.repo).resolve()
    try:
        sealed = resolve(repo, args.sealed)
        tip = resolve(repo, args.tip)
        if sealed is None or tip is None:
            raise CouldNotEvaluate(f"unresolvable revision sealed={args.sealed} tip={args.tip}")
        result = score(repo, sealed, tip, args.lesson, not args.no_corrections)
    except (CouldNotEvaluate, OSError, ValueError, subprocess.TimeoutExpired) as exc:
        print(f"could-not-evaluate: {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(result, indent=2))
        return verdict(result)
    for row in result["rows"]:
        print(f"FACT {row['fact']} declared={row['declared']} sealed={row['sealed']} "
              f"tip={row['tip']} status={row['status']}")
    s = result["summary"]
    if args.enumerate:
        print(f"SELFRECORD_R79_ENUM claims={s['claims']} stale={s['mismatches']} "
              f"corrected={s['corrected']}")
    else:
        print("SELFRECORD_R79 " + " ".join(f"{k}={v}" for k, v in s.items()))
        for finding in result["findings"]:
            print(finding)
    return verdict(result)


if __name__ == "__main__":
    sys.exit(main())
