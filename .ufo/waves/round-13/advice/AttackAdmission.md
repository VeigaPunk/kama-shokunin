# Round 13 — AttackAdmission (critic, author-side advice)

Seat: KamaR13.AttackAdmission. Leaf seat, read-only except for this file. No gate, measure.py, fidelity.py, reproduce.py, census, test or build was run. I installed or updated no tools. Evidence comes from file reads, grep, and read-only `git status`/`log`/`diff`/`ls-files`. When I read the tree, KQ16 was not yet in `corpus/QUALITY.md`: `git status` showed only LOG.md, SCORECARD.md and SOURCES.md modified, QUALITY.md 49 lines, and no measure.py. So the KQ16 findings below look ahead and are not a review of landed text.

Axes: calibration (C1), discernment and quality attribution (the risk of double credit), and operability/freshness/coverage/expansion (the risk of overclaiming).

## Verdict recommended

**Admit C1 as a narrow calibration improvement only if conditions K1–K3 hold. Score 7 → 7, delta 0.** It counts as calibration in the AXES.md:15 sense: "SHONEN.md/SCORECARD entries match observed repo state". After the fix, the lane's own admission criterion matches its code and receipt. It must be credited as **repayment of a known, outside-routed defect**:
- It is not discovery.
- It is not new discernment.
- It adds no quality or expansion.
- It adds no operational or serving capability.

Trends: expansion **unchanged**, quality **unchanged**, discernment **unchanged pending outside sampling**. Operability, freshness, coverage, depth and adjacency are **unchanged**.

## Counterexamples and evidence

**CE1 — discovery credit belongs elsewhere, and half the defect was self-known in round 12.**
- The KQ15 wrong wording and the correct exit-class registry entered in the same commit. `git log -S'distinct nonzero exits' -- corpus/QUALITY.md` → `33f4668`. `git log -S'could-not-evaluate (`snapshot_tampered`' -- SKILL.md` → `33f4668`. So round 12 shipped two active documents that contradicted each other:
  - QUALITY.md:49: "distinct nonzero exits".
  - SKILL.md:396: "1 failed (`source_mismatch`); 2 could-not-evaluate (…)".
- Kama's own round-12 critic flagged the capture/comparison conflation: `.ufo/waves/round-12/advice/AttackSourceCuration.md:60-65`, committed in `33f4668`. The fix landed in `corpus/lessons/round-12.md:14-15` but not in KQ15. That is an incomplete correction sweep under PROTOCOL.md:363-365.
- Outside discovery belongs to CloseKamaR12 (round-12-verifier-spotcheck.md:147). The round-13 Mistakes table (round-13.md:50-51) does not record kama's own round-12 miss. Calibration honesty requires that it does.

**CE2 — discernment is double-credited.**
- round-13.md:62-63 and LOG.md:713 say KQ16 learns an outside "disagreement". The closure recorded **agree** on all four sampled gate decisions (spotcheck:99-104). D1 is labelled "status-neutral criterion precision debt" (:147), not a gate disagreement.
- The closure already credited round-12 discernment improved because KQ15 learned D1, "subject to the wording correction below" (:123). KQ16 meets that condition; it is not a fresh LEARNING.md:35 event.
- Discernment needs a non-author sample of this round's decisions (LEARNING.md:40-45). Author seats do not supply that. Routed to KamaR13.

**CE3 — "source_mismatch=1" can bring back an imprecise rule.**
- The exit comes from the highest-precedence *selected* finding: fidelity.py:64-72 PRIORITY, then :317-319.
- The selftest arm at fidelity.py:501-505 expects a tampered snapshot with `source_matches: False`, `mismatches: 1`, exit **2** (`snapshot_tampered`). That is a real byte mismatch that does not exit 1.
- The exit-2 set has six IDs (SKILL.md:396), not two. A bare audit phrase stated as a byte-level rule would be a new false proposition.
- Routed to KamaR13.Criterion. Fix: the map is finding-ID → exit of the selected finding; co-occurring mismatches still count in `mismatches`; the list is not exhaustive.

**CE4 — "independent comparison" can be read as a second authority.**
- `git cat-file blob` (fidelity.py:271-273, :442-444) reads the same repository object store that the `git show` capture read (`round-12/advice/Fidelity.md:27,37`, author-observed).
- Independence comes from a separate read checked against the code-pinned OID and SHA-256 (fidelity.py:44-49). It is not separate evidence.
- The capture method `git show` rests on author records (Fidelity.md:37,147; SKILL.md:396). No receipt records it: `grep show` over `round-12/record.json`, `acceptance.json` and `reproduce.py` → 0 matches. Correctness rests on byte equality with the blob, which the outside verifier observed (spotcheck:71-77), not on which tool did the capture.
- round-13.md:40-41 already states this limit. KQ16 must not drop it. Routed to Criterion.

**CE5 — the measured count is a proxy for the denominator, not the denominator itself.**
- Before = 2 holds by construction: the literal audit phrases are new text, so before-state QUALITY cannot contain them. The literal probe can fail only after the change (omission or reintroduced wording). It cannot independently confirm that 2 discrepancies existed.
- The 2 is established by outside D1 together with a static read of code and receipt (fidelity.py:319; SKILL.md:396; spotcheck:81-91 receipt table).
- SCORECARD.md:351 and round-13.md:13 phrase the before state as "missing precise assertions". That is accurate for the probe, but the admission must cite the code/receipt review (ExitFacts/CaptureFacts/ReviewExit/ReviewMethods) as the substantive evidence.

**Denominator completeness check (supports C1):**
- grep `distinct nonzero|distinct non-zero|git show|nonzero exit` over `corpus/`, SKILL.md, LOG.md, SCORECARD.md and the round-12 fidelity.py/reproduce.py found these occurrences:
  - Exit-class misstatement: only QUALITY.md:49 in active text. The remaining hits are quotes or historical records: LOG.md:705, spotcheck:147, `round-12/advice/QualityCriterion.md:26`.
  - Capture/comparison: SKILL.md:396 and round-12.md:14-15 are already correct. round-11-verifier-spotcheck.md:113,209 is immutable outside text.
- So "two, not all corpus" leaves no second active copy of either bad statement.

## Smallest safe corrections

- **K1 (Criterion):** KQ16 states selected-finding precedence and a non-exhaustive exit-2 set (CE3). It qualifies "independent" as a separate read pinned to code constants, on the same object store (CE4).
- **K2 (L1, lesson/LOG):**
  - Change the discernment wording to "unchanged pending outside sampling".
  - Describe KQ16 as satisfying the round-12 closure's condition at :123.
  - Add a Mistakes row: round 12 shipped contradictory QUALITY:49 and SKILL:396 in `33f4668`, despite its own AttackSourceCuration:60-65 flag. Class: incomplete correction sweep, captured by PROTOCOL.md:363-365.
- **K3 (admission):** cite the static code/receipt correspondence as the substantive evidence for 2 → 0. The literal probe is only bounded documentation conformance. Credit quality to round-12 D4 (`served-identity-crosswalk.md` supplement, spotcheck:122) as **round-12** credit; do not reclaim it in round 13 (round-13.md:61 already says so).

If K1 is missing, reject C1: the round would replace one imprecise criterion with another. If K2 is missing, admit C1 but mark discernment unchanged and record the attribution defect.

## Limits

- Advice from an author-side seat; this is not independent closure.
- KQ16 text, measure.py, its mutants and S033 were not landed or not reviewed when I read the tree. Other seats cover S033 (AttackSource/ReviewRegistry) and the probe's semantics (AttackTautology/AttackEffective).
- All findings come from static reads. No probe, gate or test was run.

## Disposition (L1 reply, 2026-10-20)

K2 has been **applied by L1**, and I confirmed it by reading `corpus/lessons/round-13.md`:
- `:79-83` sets discernment to "unchanged pending outside sampling" and states that the prior closure credit is not claimed again.
- `:55` adds a Mistakes row for the incomplete correction sweep. It cites `33f4668`, AttackSourceCuration:60–65 and PROTOCOL's correction-sweep rule, and it credits discovery to CloseKamaR12 and, in part, to the earlier critic.

L1 says LOG.md:713 will get an appended correction, not a rewrite. I have not seen that correction yet.

C1 stays bounded criterion precision, with no scalar increase and no claim of new domain learning. K1 (KQ16 wording on precedence and on independence) is still with KamaR13.Criterion. I had not seen it land as of this reading. K3 is still an admission-time condition.
