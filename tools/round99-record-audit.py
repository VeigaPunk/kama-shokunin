#!/usr/bin/env python3
"""round99-record-audit.py - round-99 C2 (calibration) frozen counter, amendment 1.

PREDICATE (same sentence as plans/round-99-claims.md section C2 and
plans/round-99-amendment-1.md A2):

    `python3 tools/round99-record-audit.py --repo . --rev <M2> --work <scratch>`
    prints `RECORD_AUDIT99 checks=12 mismatches=0 met=True rev=<resolved>` and exits 0 at the
    measured commit M2 (the amendment-1 commit).

    Before (do-nothing control): at base `439fdb3d` the same counter prints `mismatches=10`
    (the round-99 corrections do not exist) and exits 1.

What is graded: the round-98 closure's routed defects 1-4 and 6, each as a mechanical proposition
over committed bytes. The wave of round 99 (CR01, EX02, MT01) showed the freeze revision's checks
accepted eight meaning-changing forgeries; amendment 1 hardens the twelve propositions below. The
claim is narrowed to exactly these mechanical propositions: negation, prose intent and the
authenticity of a committed receipt are NOT read by this counter (the non-author read remains the
semantic gate, KQ14).

 1. SCORECARD.md has at least one round-99 correction block after the stale "10 reported, 2 dead"
    line; its first such block states "12 reported, 0 dead"; no correction block in the file
    states the stale count.
 2. LOG.md: the same three conditions.
 3. Each file's correction text names both stale pointers `SCORECARD.md:6431` and `LOG.md:4040`.
 4. In each file, the attack segment (from "7 attack" to "5 non-attack") contains all seven
    derived attack-role names and none of the five non-attack names; the non-attack segment
    contains the five and none of the seven. The populations are derived from
    `.ufo/waves/round-98/w1-results.json`, not from the correction.
 5. In each file, a line joins "SB01-equivalent" to the clause `seat ... is `EX02BudgetControl``.
 6. In each file, `RV03Intent` is named in the attack segment (the round-98 SCORECARD list omitted
    it).
 7. corpus/lessons/round-99.md has exactly one line containing each revision: `681c80a4` with
    `361 ... A 344 ... B 11 ... C 6 ... mined 324 ... queued 8 ... rejected 29` and `649bb2e9`
    with `363 ... A 345 ... B 11 ... C 7 ... mined 325 ... queued 8 ... rejected 30`, each line
    labelled base/tip.
 8. Both census groups re-derive with `scripts/sources-census.sh census --file` over
    `git show <rev>:corpus/SOURCES.md` for the two frozen revisions (historical bytes always come
    from git, also under `--tree`).
 9. Each file's correction carries the exact gate verdict line `PRE_REPORT round=98 arms=14
    failed=6 uncommitted=1` and the exact six-arm phrase (in that order); the committed receipt
    re-derives the verdict and the six FAIL arms.
10. corpus/lessons/round-99.md has exactly one `## Mistakes` heading; its slice carries the
    carried round-98 M3 record (one line with `M3`, `round-98.md`, `sampling`, `outside` and
    `carried here`).
11. In each file, the correction carries the exact phrase `**12 seats** and **12 results**` and
    `12 reported, 0 dead`; the results file re-derives seats=12, results=12, no empty output.
12. The derived population (7 attack / 5 non-attack) is the population check 4 used.

Correction block: a heading matching `(?i)^## .*round[- ]99.*corrections?` up to the next `^## `.
`--tree <dir>` grades the records from a materialized copy; the historical census bytes still come
from git. Exit: 0 predicate met | 1 not met | 2 could-not-evaluate | 64 usage.
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
BLOCK_RE = re.compile(r"^## .*(?i:round)[- ]99.*(?i:corrections?).*$", re.M)
STALE = "10 reported, 2 dead"
CORRECT = "12 reported, 0 dead"
POINTERS = ("SCORECARD.md:6431", "LOG.md:4040")
VERDICT = "PRE_REPORT round=98 arms=14 failed=6 uncommitted=1"
ARM_PHRASE = ("`selfdesc`, `newest-closure`, `round-scope`, `round-clean`, "
              "`round75-instruments`, `round78-instruments`")


def blocks(text: str):
    out = []
    for m in BLOCK_RE.finditer(text):
        nxt = re.search(r"^## ", text[m.end():], re.M)
        end = m.end() + (nxt.start() if nxt else len(text) - m.end())
        out.append((m.start(), text[m.start():end]))
    return out


def first_after(text: str):
    """Return (all blocks, the first block that starts after the stale line or None)."""
    bs = blocks(text)
    stale = text.find(STALE)
    if stale < 0:
        return bs, None
    after = [b for start, b in bs if start > stale]
    return bs, (after[0] if after else None)


def segment(text: str, start_marker: str, end_marker: str) -> str:
    i = text.find(start_marker)
    if i < 0:
        return ""
    if not end_marker:
        return text[i + len(start_marker):]
    j = text.find(end_marker, i + len(start_marker))
    return text[i + len(start_marker): (j if j >= 0 else len(text))]


def section_strict(text: str, heading: str):
    hits = list(re.finditer(rf"^{re.escape(heading)}.*$", text, re.M))
    if len(hits) != 1:
        return None
    rest = text[hits[0].end():]
    nxt = re.search(r"^## ", rest, re.M)
    return rest[:nxt.start()] if nxt else rest


def census_counts(data: bytes, work: Path, tag: str):
    f = work / f"sources-{tag}.md"
    f.write_bytes(data)
    p = subprocess.run(["bash", str(CENSUS), "census", "--file", str(f)],
                       capture_output=True, text=True, timeout=120)
    if p.returncode != 0:
        raise RuntimeError(f"census rc={p.returncode}: {p.stderr.strip()[:200]}")
    counts = {}
    for key in EXPECT_BASE:
        m = re.search(rf"^(?:FLEET|file)\t{re.escape(key)}\t(\S+)$", p.stdout, re.M)
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

    def read_bytes_at(rev_name: str, path: str):
        # Historical census revisions always come from git, also under --tree: a materialized
        # tree holds only the current bytes (amendment 1, from MT01 F2 / EX02 3.1).
        p = subprocess.run(["git", "-C", str(a.repo), "show", f"{rev_name}:{path}"],
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

        s_blocks, s_first = first_after(score)
        l_blocks, l_first = first_after(log)
        s_text = "\n".join(b for _, b in s_blocks)
        l_text = "\n".join(b for _, b in l_blocks)
        s_seg_attack = segment(s_text, "7 attack", "5 non-attack")
        s_seg_non = segment(s_text, "5 non-attack", ".")
        l_seg_attack = segment(l_text, "7 attack", "5 non-attack")
        l_seg_non = segment(l_text, "5 non-attack", ".")

        def has_all(hay, names):
            return all(n in hay for n in names)

        def has_none(hay, names):
            return not any(n in hay for n in names)

        def clean(text, bs, first):
            # every correction block must follow the stale line; the first must state the
            # corrected count; no later block may restate the stale count (a later block that
            # quotes it as history is indistinguishable from a stale record, so it is refused).
            stale = text.find(STALE)
            if not bs or not first or stale < 0:
                return False
            starts = [start for start, _ in bs]
            if any(start < stale for start in starts):
                return False
            return CORRECT in first and not any(STALE in b for _, b in bs[1:])

        failed = sorted(re.findall(r"^PRE_REPORT_ARM (\S+) exit=\d+ FAIL", gate, re.M))
        gate_verdict = bool(re.search(rf"^{re.escape(VERDICT)}$", gate, re.M))
        base_bytes = read_bytes_at(R98_BASE, "corpus/SOURCES.md")
        tip_bytes = read_bytes_at(R98_TIP, "corpus/SOURCES.md")
        if base_bytes is None or tip_bytes is None:
            print("RECORD_AUDIT99 could-not-evaluate: census revision bytes unavailable")
            return 2
        got_base = census_counts(base_bytes, work, "base")
        got_tip = census_counts(tip_bytes, work, "tip")

        m3 = section_strict(lesson99 or "", "## Mistakes") or ""
        m3_paras = [p for p in re.split(r"\n\s*\n", m3)
                    if all(t in p for t in ("M3", "round-98.md", "sampling",
                                            "outside", "carried here"))]
        m3_line = m3_paras[0] if m3_paras else ""

        cen_base_line = next((ln for ln in (lesson99 or "").splitlines()
                              if R98_BASE[:8] in ln), "")
        cen_tip_line = next((ln for ln in (lesson99 or "").splitlines()
                             if R98_TIP[:8] in ln), "")
        cen_base = bool(re.search(
            r"base[^.\n]{0,30}681c80a4[^.\n]{0,30}361[^.\n]{0,60}A 344[^.\n]{0,40}B 11"
            r"[^.\n]{0,40}C 6[^.\n]{0,60}mined 324[^.\n]{0,40}queued 8[^.\n]{0,40}rejected 29",
            cen_base_line, re.I))
        cen_tip = bool(re.search(
            r"tip[^.\n]{0,30}649bb2e9[^.\n]{0,30}363[^.\n]{0,60}A 345[^.\n]{0,40}B 11"
            r"[^.\n]{0,40}C 7[^.\n]{0,60}mined 325[^.\n]{0,40}queued 8[^.\n]{0,40}rejected 30",
            cen_tip_line, re.I))
        cen_unique = (sum(1 for ln in (lesson99 or "").splitlines() if R98_BASE[:8] in ln) == 1 and
                      sum(1 for ln in (lesson99 or "").splitlines() if R98_TIP[:8] in ln) == 1)

        checks = []

        def chk(cid, ok, detail):
            checks.append((cid, bool(ok), detail))

        chk(1, clean(score, s_blocks, s_first), "SCORECARD: one after-block, first says 12/0, no later stale block")
        chk(2, clean(log, l_blocks, l_first), "LOG: one after-block, first says 12/0, no later stale block")
        chk(3, all(p in s_text for p in POINTERS) and all(p in l_text for p in POINTERS),
            "each file's correction names both stale pointers")
        chk(4, has_all(s_seg_attack, attack) and has_none(s_seg_attack, non) and
            has_all(s_seg_non, non) and has_none(s_seg_non, attack) and
            has_all(l_seg_attack, attack) and has_none(l_seg_attack, non) and
            has_all(l_seg_non, non) and has_none(l_seg_non, attack),
            f"attribution: attack={attack} non={non}")
        sb_re = re.compile(r"SB01-equivalent[^\n]{0,120}?seat[^.\n]{0,40}?is\s+`EX02BudgetControl`")
        chk(5, bool(sb_re.search(s_text)) and bool(sb_re.search(l_text)),
            "each file joins SB01-equivalent to 'seat ... is `EX02BudgetControl`'")
        chk(6, "RV03Intent" in s_seg_attack and "RV03Intent" in l_seg_attack,
            "RV03Intent named in each attack segment")
        chk(7, cen_base and cen_tip and cen_unique,
            f"census lines: base={cen_base} tip={cen_tip} unique={cen_unique}")
        chk(8, got_base == EXPECT_BASE and got_tip == EXPECT_TIP,
            f"census base={got_base} tip={got_tip}")
        chk(9, gate_verdict and failed == sorted(
            ["selfdesc", "newest-closure", "round-scope", "round-clean",
             "round75-instruments", "round78-instruments"]) and
            all(VERDICT in t and ARM_PHRASE in t for t in (s_text, l_text)),
            f"gate failed arms {failed}")
        chk(10, bool(m3_line), "carried M3 sampling record inside the single ## Mistakes")
        chk(11, all("**12 seats** and **12 results**" in t and CORRECT in t
                    for t in (s_text, l_text)) and
            results.get("seats") == len(seats) == 12 and not dead,
            f"seats={results.get('seats')} results={len(seats)} dead={dead}")
        chk(12, len(attack) == 7 and len(non) == 5 and len(attack) + len(non) == 12,
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


if __name__ == "__main__":
    sys.exit(main())
