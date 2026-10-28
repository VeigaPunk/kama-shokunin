#!/usr/bin/env python3
"""apply-selfdesc-r63.py REPO - WR04 draft of the SCORECARD / PROVINCE edits.

Run ONLY against a scratch clone of the lane, never the lane itself. It
  1. appends PROVINCE.md a round-63 provenance paragraph (names the two r61/r63
     claim registries the reconciler's province fact needs);
  2. re-derives the SCORECARD head facts the reconciler reads (banner, Planned,
     Retired, Capabilities mirror + live-ollama row, Saturation, Axes coverage
     count and PROVINCE hash/lines);
  3. appends Part A of scorecard-append.md (the measured-results block and the
     Planned (round 64) block) at the end of SCORECARD.md.
Every replacement asserts its old text occurs exactly once; any drift stops the
script with exit 2 and writes nothing.
"""
import hashlib
import os
import sys

REPO = os.path.abspath(sys.argv[1])
HERE = os.path.dirname(os.path.abspath(__file__))


def rd(p):
    with open(os.path.join(REPO, p), encoding="utf-8") as f:
        return f.read()


def once(s, old, new):
    n = s.count(old)
    if n != 1:
        sys.exit(f"apply: expected 1 occurrence, found {n}: {old[:70]!r}")
    return s.replace(old, new)


PROVINCE_PARA = (
    "**Round-63 claim tables — provenance (2026-10-28).** `registry/ollama-live-claims-r61.tsv` "
    "is the round-61 claim table for the live Ollama lifecycle (capability `live-ollama-lifecycle`, "
    "instrument `tools/kama-ollama-live.py`); `registry/capability-claims-r63.tsv` is the round-63 "
    "twelve-row binding that `tools/round63-c2-counter.py` reads; `tools/round63-c1-counter.py` grades "
    "the request-plane instrument `tools/kama-completion-live.py` (schema `kama-completion-live/v2`). "
    "These are frozen inputs and instruments; a counter line admits a claim only in the SCORECARD "
    "round section that cites it."
)

BANNER = (
    "**Current authority (round 63):** assigned axes are operability + calibration (`shokunin.conf` kama "
    "row; the MISSION.md freshness conflict remains open at `.ufo/l0-questions.md:145`). Latest measured "
    "round: 63 (wave verdicts recorded in §Round 63 measured results). Calibration 7 remains the lowest "
    "assigned axis, below operability 8; nudge inactive. Scores are held at operability 8 / calibration 7 "
    "pending the round-63 verdicts. The `## Axes` table, §Planned, §Retired, §Saturation and §Capabilities "
    "below are re-derived by `tools/round42-selfdesc-reconcile.py`; round-specific outcomes stay in their "
    "round sections."
)

OLD_PLANNED = ("Superseded in round 42. The live plan is `### Planned (round 61)` below; the round-5 plan "
               "this section carried is kept verbatim under §Historical head sections.")
NEW_PLANNED = ("The live plan is `### Planned (round 64)` at the end of this file, after §Round 63 measured "
               "results. Earlier plans stay in their round sections; the round-5 plan this section carried is "
               "kept verbatim under §Historical head sections.")

OLD_RETIRED = "None. 6 axes and 11 capabilities remain active."
NEW_RETIRED = "None. 6 axes and 12 capabilities remain active."

OLD_CAPS = "Mirror of the round-49 canonical capability list that §Round 49 carries"
NEW_CAPS = "Mirror of the round-63 canonical capability list that §Round 63 carries"

OLD_SAT_ROUNDS = "47 (highest canonical list)"
NEW_SAT_ROUNDS = "47, 61 (highest canonical list)"
OLD_SAT_KEPT = "(kept current in round 49)"
NEW_SAT_KEPT = "(kept current in round 63)"
OLD_SAT_LAST = ("The last capability entered in round 47 is older than the N=4 stagnation window; the nudge "
                "remains inactive solely because the lowest assigned axis remains below saturation.")
NEW_SAT_LAST = ("The last capability entered is live-ollama-lifecycle (round 61), inside the N=4 stagnation "
                "window; nudge inactive, because the lowest assigned axis, calibration 7, remains below "
                "saturation.")

OLD_COV_RUN = "→ `36` (round 60 added `corpus/knowledge/ollama-live-lifecycle.md`)"
NEW_COV_RUN = ("→ `38` (round 60 added `corpus/knowledge/ollama-live-lifecycle.md`; round 61 added "
               "`corpus/knowledge/ollama-live-amendment-r61.md`; round 62 added "
               "`corpus/knowledge/completion-request-plane.md`)")
OLD_COV_PV = ("`PROVINCE.md` sha256 `a60591b77ac8a8f0bd90f3436d75fc8cbe1fbab820d37e6f57b0e386c32a01a9` "
              "(188 lines)")

PART_A_BEGIN = "## Part A"
PART_B_BEGIN = "## Part B"


def part_a():
    with open(os.path.join(HERE, "scorecard-append.md"), encoding="utf-8") as f:
        text = f.read().split("\n")
    b = next(i for i, l in enumerate(text) if l.startswith(PART_A_BEGIN))
    e = next(i for i, l in enumerate(text) if l.startswith(PART_B_BEGIN))
    return "\n".join(text[b + 1:e]).strip("\n")


def main():
    append = part_a()
    assert "### Round-63 measured results" in append and "### Planned (round 64)" in append

    # 1. PROVINCE.md first: its hash and line count feed the Axes coverage row.
    pv = rd("PROVINCE.md")
    pv_new = pv.rstrip("\n") + "\n\n" + PROVINCE_PARA + "\n"
    pv_sha = hashlib.sha256(pv_new.encode("utf-8")).hexdigest()
    pv_lines = pv_new.count("\n")

    # 2. SCORECARD head facts.
    sc = rd("SCORECARD.md")
    lines = sc.split("\n")
    idx6 = [i for i, l in enumerate(lines) if l.startswith("**Current authority (round 61):**")]
    assert idx6 == [5], idx6
    lines[5] = BANNER
    sc = "\n".join(lines)
    sc = once(sc, OLD_PLANNED, NEW_PLANNED)
    sc = once(sc, OLD_RETIRED, NEW_RETIRED)
    sc = once(sc, OLD_CAPS, NEW_CAPS)
    lines = sc.split("\n")
    k = next(i for i, l in enumerate(lines) if l.startswith("| live-receipt-replay |"))
    row = [l for l in lines if l.startswith("| live-ollama-lifecycle |")][-1]
    lines.insert(k + 1, row)
    sc = "\n".join(lines)
    sc = once(sc, OLD_SAT_ROUNDS, NEW_SAT_ROUNDS)
    sc = once(sc, OLD_SAT_KEPT, NEW_SAT_KEPT)
    sc = once(sc, OLD_SAT_LAST, NEW_SAT_LAST)
    sc = once(sc, OLD_COV_RUN, NEW_COV_RUN)
    sc = once(sc, OLD_COV_PV, f"`PROVINCE.md` sha256 `{pv_sha}` ({pv_lines} lines)")

    # 3. Append Part A at the end of SCORECARD.md.
    sc = sc.rstrip("\n") + "\n\n" + append + "\n"

    with open(os.path.join(REPO, "PROVINCE.md"), "w", encoding="utf-8") as f:
        f.write(pv_new)
    with open(os.path.join(REPO, "SCORECARD.md"), "w", encoding="utf-8") as f:
        f.write(sc)
    print(f"applied: PROVINCE.md sha256={pv_sha} lines={pv_lines}")


if __name__ == "__main__":
    main()
