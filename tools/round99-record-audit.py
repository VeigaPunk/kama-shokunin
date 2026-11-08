#!/usr/bin/env python3
"""round99-record-audit.py - round-99 C2 (calibration) frozen counter.

PREDICATE (same sentence as plans/round-99-claims.md section C2):

    `python3 tools/round99-record-audit.py --repo . --rev <M2> --work <scratch>`
    prints `RECORD_AUDIT99 checks=12 mismatches=0 met=True rev=<resolved>` and exits 0 at the
    measured commit M2.

    Before (do-nothing control): at base `439fdb3d` the same counter prints `mismatches=9`
    (the round-99 corrections do not exist) and exits 1.

What is graded (the round-98 closure's routed defects 1-4 and 6, `round-98-verifier-spotcheck.md`):
the lane's own round-98 records must agree with the committed wave evidence. Each check either
re-derives its value from committed bytes (git show + the frozen census generator) or requires the
appended round-99 correction block to name the re-derived value.

 1. SCORECARD.md carries a round-99 correction block AFTER the stale wave line and states
    "12 reported, 0 dead".
 2. LOG.md carries a round-99 correction block AFTER the stale wave line and states the same.
 3. Both blocks name the stale pointers `SCORECARD.md:6431` and `LOG.md:4040`.
 4. The correction text states `7 attack` and names the seven attack-role seats re-derived from
    `.ufo/waves/round-98/w1-results.json`, and `5 non-attack` and names the five others.
 5. The correction names EX02BudgetControl as the seat the round-98 LOG miscalled "SB01-equivalent".
 6. The correction names RV03Intent among the attack seats (the round-98 SCORECARD list omitted it).
 7. corpus/lessons/round-99.md states the round-98 census correction: base `681c80a4` -> 361 rows
    (A 344, B 11, C 6; mined 324, queued 8, rejected 29); round-98 tip `649bb2e9` -> 363 rows
    (A 345, B 11, C 7; mined 325, queued 8, rejected 30).
 8. Both census groups re-derive with `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh
    census --file <git show <rev>:corpus/SOURCES.md>`.
 9. The correction names the round-98 gate verdict `PRE_REPORT round=98 arms=14 failed=6
    uncommitted=1` and all six failed arms re-derived from the committed gate receipt, including
    `round-clean` (the round-98 erratum omitted it).
10. corpus/lessons/round-99.md has a `## Mistakes` section whose slice carries the round-98 M3
    `sampling` record (tokens `M3`, `round-98.md`, `sampling`).
11. `w1-results.json` re-derives seats=12, results=12, every result with a non-empty output, and
    the correction states `12 seats` and `12 results`.
12. The correction's seat counts are derived, not asserted: the counter's own parse of the results
    file (7 attack / 5 non-attack) is the source of check 4's population.

A correction block is the text from a heading matching
`^## .*[Rr]ound[- ]99.*(correction|corrections)` to the next `^## ` heading. `--tree <dir>` grades
a materialized copy (used only by the forged-correction control, never by the predicate).

Exit: 0 predicate met | 1 not met | 2 could-not-evaluate | 64 usage.
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

CENSUS = Path("/home/vgpnk/Projects/shokunin/scripts/sources-census.sh")
R98_BASE = "681c80a4e3c745c22559f74b2c2a1917bdc66fc6"
R98_TIP = "649bb2e94501ee8aa2d4ceaeae52f7a1fb8d1ce9"
ATTACK_ROLES = {"reviewer", "critic", "mutation-tester", "sentinel", "revenger"}
EXPECT_BASE = {"rows": "361", "tier.A": "344", "tier.B": "11", "tier.C": "6",
               "status.mined": "324", "status.queued": "8", "status.rejected": "29"}
EXPECT_TIP = {"rows": "363", "tier.A": "345", "tier.B": "11", "tier.C": "7",
              "status.mined": "325", "status.queued": "8", "status.rejected": "30"}
BLOCK_RE = re.compile(r"^## .*[Rr]ound[- ]99.*(?:correction|corrections).*$", re.M)


def correction_blocks(text: str) -> str:
    blocks = []
    for m in BLOCK_RE.finditer(text):
        start = m.start()
        nxt = re.search(r"^## ", text[start + len(m.group(0)):], re.M)
        end = start + len(m.group(0)) + (nxt.start() if nxt else len(text))
        blocks.append(text[start:end])
    return "\n".join(blocks)


def section(text: str, heading: str) -> str:
    m = re.search(rf"^{re.escape(heading)}.*$", text, re.M)
    if not m:
        return ""
    rest = text[m.end():]
    nxt = re.search(r"^## ", rest, re.M)
    return rest[:nxt.start()] if nxt else rest


def census_counts(data: bytes, work: Path, tag: str):
    f = work / f"sources-{tag}.md"
    f.write_bytes(data)
    p = subprocess.run(["bash", str(CENSUS), "census", "--file", str(f)],
                       capture_output=True, text=True, timeout=120)
    if p.returncode != 0:
        raise RuntimeError(f"census rc={p.returncode}: {p.stderr.strip()[:200]}")
    out = p.stdout
    counts = {}
    for key in EXPECT_BASE:
        m = re.search(rf"^(?:FLEET|file)\t{re.escape(key)}\t(\S+)$", out, re.M)
        if not m:
            raise RuntimeError(f"census prints no {key}")
        counts[key] = m.group(1)
    return counts


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--rev")
    ap.add_argument("--tree", type=Path, help="grade a materialized tree (control only)")
    ap.add_argument("--work", type=Path, required=True)
    a = ap.parse_args()
    if not a.rev and not a.tree:
        print("RECORD_AUDIT99 usage: --rev or --tree is required")
        return 64

    a.work.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix="r99-record-", dir=a.work)).resolve()

    def read(path: str):
        try:
            if a.tree:
                p = a.tree / path
                return p.read_text(encoding="utf-8", errors="replace") if p.exists() else None
            p = subprocess.run(["git", "-C", str(a.repo), "show", f"{rev}:{path}"],
                               capture_output=True, text=True)
            return p.stdout if p.returncode == 0 else None
        except Exception:  # noqa: BLE001
            return None

    def read_bytes(path: str):
        if a.tree:
            p = a.tree / path
            return p.read_bytes() if p.exists() else None
        p = subprocess.run(["git", "-C", str(a.repo), "show", f"{rev}:{path}"],
                           capture_output=True)
        return p.stdout if p.returncode == 0 else None

    try:
        if a.tree:
            rev = "tree:" + str(a.tree)
        else:
            p = subprocess.run(["git", "-C", str(a.repo), "rev-parse", "--verify",
                                a.rev + "^{commit}"], capture_output=True, text=True)
            if p.returncode != 0:
                print(f"RECORD_AUDIT99 could-not-evaluate: unresolvable rev {a.rev}")
                return 2
            rev = p.stdout.strip()

        score = read("SCORECARD.md")
        log = read("LOG.md")
        lesson98 = read("corpus/lessons/round-98.md")
        lesson99 = read("corpus/lessons/round-99.md")
        results_raw = read(".ufo/waves/round-98/w1-results.json")
        gate = read(".ufo/waves/round-98/measured/pre-report-gate.out")
        if score is None or log is None or lesson98 is None or results_raw is None or gate is None:
            print("RECORD_AUDIT99 could-not-evaluate: a round-98 record is missing at the revision")
            return 2
        results = json.loads(results_raw)
        seats = results.get("results") or []
        attack = sorted(s.get("name") for s in seats
                        if s.get("agent") in ATTACK_ROLES and s.get("name"))
        non = sorted(s.get("name") for s in seats
                     if s.get("agent") not in ATTACK_ROLES and s.get("name"))
        dead = [s.get("name") for s in seats if not (s.get("output") or "").strip()]

        s_block = correction_blocks(score)
        l_block = correction_blocks(log)
        both = s_block + "\n" + l_block
        stale_s = re.search(r"10 reported, 2 dead", score)
        stale_l = re.search(r"10 reported, 2 dead", log)
        cs = re.search(r"12 reported, 0 dead", s_block)
        cl = re.search(r"12 reported, 0 dead", l_block)
        checks = []

        def chk(cid, ok, detail):
            checks.append((cid, bool(ok), detail))

        # 1 / 2: appended block with the corrected count, after the stale line
        chk(1, bool(s_block) and bool(cs) and stale_s is not None and
            score.find(s_block[:20]) > stale_s.start(),
            "SCORECARD block states 12 reported, 0 dead after the stale line")
        chk(2, bool(l_block) and bool(cl) and stale_l is not None and
            log.find(l_block[:20]) > stale_l.start(),
            "LOG block states 12 reported, 0 dead after the stale line")
        # 3: stale pointers named
        chk(3, "SCORECARD.md:6431" in both and "LOG.md:4040" in both,
            "both stale pointers named")
        # 4: derived split and exact members named
        chk(4, bool(re.search(r"\b7 attack\b", both)) and bool(re.search(r"\b5 non-attack\b", both))
            and all(n in both for n in attack) and all(n in both for n in non),
            f"7 attack {attack} / 5 non-attack {non}")
        # 5: fifth non-attack seat named where the LOG said SB01-equivalent
        chk(5, "EX02BudgetControl" in both and "SB01-equivalent" in both,
            "EX02BudgetControl named against SB01-equivalent")
        # 6: RV03Intent named among the attack seats
        chk(6, "RV03Intent" in both, "RV03Intent named")
        # 7: lesson states the census correction in a base/tip-bound form
        base_pat = (r"base[^.\n]{0,220}361[^.\n]{0,220}A 344[^.\n]{0,120}B 11[^.\n]{0,120}C 6"
                    r"[^.\n]{0,220}mined 324[^.\n]{0,120}queued 8[^.\n]{0,120}rejected 29")
        tip_pat = (r"tip[^.\n]{0,220}363[^.\n]{0,220}A 345[^.\n]{0,120}B 11[^.\n]{0,120}C 7"
                   r"[^.\n]{0,220}mined 325[^.\n]{0,120}queued 8[^.\n]{0,120}rejected 30")
        chk(7, bool(lesson99) and bool(re.search(base_pat, lesson99, re.I)) and
            bool(re.search(tip_pat, lesson99, re.I)),
            "lesson carries the base/tip census correction")
        # 8: both census groups re-derive from committed bytes
        base_bytes = read_bytes_at(R98_BASE, "corpus/SOURCES.md", a.repo, a.tree)
        tip_bytes = read_bytes_at(R98_TIP, "corpus/SOURCES.md", a.repo, a.tree)
        if base_bytes is None or tip_bytes is None:
            print("RECORD_AUDIT99 could-not-evaluate: census revision bytes unavailable")
            return 2
        got_base = census_counts(base_bytes, work, "base")
        got_tip = census_counts(tip_bytes, work, "tip")
        chk(8, got_base == EXPECT_BASE and got_tip == EXPECT_TIP,
            f"census base={got_base} tip={got_tip}")
        # 9: gate verdict + six failed arms re-derived from the receipt
        failed_names = sorted(re.findall(r"^PRE_REPORT_ARM (\S+) exit=\d+ FAIL", gate, re.M))
        verdict = re.search(r"^PRE_REPORT round=98 arms=14 failed=6 uncommitted=1$", gate, re.M)
        chk(9, bool(verdict) and failed_names == sorted(
            ["selfdesc", "newest-closure", "round-scope", "round-clean",
             "round75-instruments", "round78-instruments"]) and
            all(n in both for n in failed_names),
            f"gate failed arms {failed_names}")
        # 10: the carried M3 record sits inside round-99's Mistakes section
        mistakes = section(lesson99 or "", "## Mistakes")
        chk(10, "M3" in mistakes and "round-98.md" in mistakes and "sampling" in mistakes,
            "carried M3 sampling record inside ## Mistakes")
        # 11: wave population re-derived and named
        chk(11, results.get("seats") == len(seats) == 12 and not dead and len(attack) == 7 and
            len(non) == 5 and "12 seats" in both and "12 results" in both,
            f"seats={results.get('seats')} results={len(seats)} dead={dead}")
        # 12: the split check used the counter's own derived population (not a doc token)
        chk(12, len(attack) + len(non) == 12 and len(attack) == 7,
            f"derived population attack={len(attack)} non={len(non)}")
    except subprocess.TimeoutExpired:
        print("RECORD_AUDIT99 could-not-evaluate: census timed out")
        return 2
    except Exception as e:  # noqa: BLE001
        print(f"RECORD_AUDIT99 could-not-evaluate: {e}")
        return 2
    finally:
        shutil.rmtree(work, ignore_errors=True)

    mismatches = 0
    for cid, ok, detail in checks:
        if not ok:
            mismatches += 1
            print(f"RECORD_AUDIT99_MISMATCH {cid} {detail}")
    print(f"RECORD_AUDIT99 checks={len(checks)} mismatches={mismatches} "
          f"met={mismatches == 0} rev={rev}")
    return 0 if mismatches == 0 else 1


def read_bytes_at(rev: str, path: str, repo: Path, tree):
    if tree:
        p = tree / path
        return p.read_bytes() if p.exists() else None
    p = subprocess.run(["git", "-C", str(repo), "show", f"{rev}:{path}"], capture_output=True)
    return p.stdout if p.returncode == 0 else None


if __name__ == "__main__":
    sys.exit(main())
