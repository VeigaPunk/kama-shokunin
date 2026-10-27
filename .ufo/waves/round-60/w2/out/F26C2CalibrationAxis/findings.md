# F26C2CalibrationAxis — C2 calibration axis fit (round 60, w2 falsify; advisory leaf)

## Question
Does C2 count self-assessment mismatches, or only coverage + receipt predicates?

## Definitions consulted
- Fleet `AXES.md`, six-axes table: calibration = "Self-assessment quality: gaps named honestly, confidence graded, overreach caught"; expert signal = "SHONEN.md/SCORECARD entries match observed repo state".
- Hyaku claim rule: "A calibration claim must count mismatches between self-assessment and observed repo state. It cannot be an assertion." (`goal-20261023-hyaku-24h.md:145`; same wording in `goal-20261018-game-dev-2d-training.md:155-156` and the chousa-round prompt templates).
- Lane precedent: kama r25 was rejected-harmed because its calibration claim "counted instrument-versus-auditor mismatches instead of self-assessment mismatches, so the lowest-axis rule went unmet" (fleet `.ufo/l0-questions.md`, kama round-26 item).

## Freeze quotes (freeze.txt, unchanged since freeze commit)
- "C2 calibration 7 -> 7 (lowest assigned axis; calibration 7 < operability 8; nudge inactive)"
- Predicate (verbatim core): "…at least 5 rows over at least 4 distinct lines carry a live predicate; every predicate is falsifiable (a mutation of a capture it reads flips its result); its recorded verdict equals its evaluation on the committed receipt's captures (true = confirmed, false = contradicted); every contradicted row is named with its observed text in corpus/knowledge/ollama-live-amendment-r60.md; the committed receipt's capture hashes are intact; and the 5 control families (tautology predicates, flipped verdicts, corrupted quotes, dropped lines, tampered capture) are all rejected, errors=0."
- Limits (stated before data): "checks lane statements about one Ollama version on one fixture model, as recorded in one committed receipt; a confirmed statement is confirmed for that run only; not-observable rows are not credited as evaluated."

## What the counter actually counts (`tools/round60-c2-counter.py` @ HEAD 8f5f4e33; bytes unchanged since e0b5b1ea)
1. Coverage: `met` requires `len(covered) == len(pop)` (14 frozen base lines); a quote must be 3–25 words and a substring of the base line.
2. Live floor: `ev_rows >= MIN_EVAL_ROWS (5)` over `len(ev_lines) >= MIN_EVAL_LINES (4)`.
3. Falsifiability: `falsifiable()` mutates every `c[...]` chain (None / deep sentinel / empty) and demands a result flip; counted as `sensitive=E/E`.
4. Self-assessment-mismatch gate: `if (res and r["verdict"] != "confirmed") or (not res and r["verdict"] != "contradicted"): continue` — a recorded verdict that disagrees with the re-evaluation over the receipt's parsed capture bodies drops the row, `good == len(rows)` fails, `met=False`. The `verdict_flip` control flips each row's verdict one at a time and requires `met` to fail.
5. Honest-gap accounting: contradicted rows are permitted (not forced to zero) iff `amended == contra`, where a row counts amended only if its id and its observed text appear in the amendment file.
6. Receipt integrity: `receipt_caps()` requires schema `kama-ollama-live/v1` and per-capture sha256 == hash of its own body; the tamper control appends one space to a capture body.
7. `grep -i 'SCORECARD|SHONEN' tools/round60-c2-counter.py` → no matches. The counter never reads the SCORECARD/SHONEN artifacts that AXES names as the calibration signal.

## Answer
C2 is not "only coverage + receipt": clauses 4–5 count a real self-assessment-mismatch class (the registry `verdict` column is the lane's per-statement self-assessment; any mismatch against instrument re-evaluation breaks `met`, and the flip control proves per-row sensitivity). But the self-assessed artifact is the round-60 registry, not SCORECARD/SHONEN, and the "observed state" anchor is the lane's own committed receipt: `receipt_caps()` proves only internal hash consistency; authenticity is delegated to C1's fresh-nonce lifecycle. A self-consistent fabricated receipt (bodies plus recomputed sha256) passes `receipt_ok`, the tamper control, and every verdict gate — so the mismatch count is receipt-relative, strictly narrower than AXES's "observed repo state". Under the strict hyaku rule and the r25 precedent, C2 sits between the rejected shape and the demanded shape: it is self-record-vs-own-instrument, not SCORECARD/SHONEN-vs-repo-state. Not an assertion (the verdict column is graded and flip-sensitive), but not the AXES-defined count either.

## Boundedness findings (attack, no repair applied)
- not-observable rows (no predicate, reason ≥20 chars) count as covered and good while excluded from `evaluated`: up to 10 of 14 lines can ride not-observable rows and still meet the claim (floor is 5 rows / 4 lines). W1 drafts so far: 25 data rows across `.ufo/waves/round-60/w1/out/M*/rows.tsv` = 11 `confirmed` + 14 `not-observable` + 0 `contradicted` — the contradiction/amendment path (`contradicted=0 amended=0/0`) is vacuously satisfied and unexercised by real data.
- Current tip state: `registry/ollama-live-claims-r60.tsv` is absent at HEAD 8f5f4e33 and at freeze commit e0b5b1ea (`git cat-file -e` fails both). `python3 tools/round60-c2-counter.py --repo . --tip HEAD` (TMPDIR=/fast/scratch/hyaku/kama-r60/F26C2CalibrationAxis) → `population=14 rows=0 covered=0/14 evaluated=0 eval_lines=0 sensitive=0/0 bound=0 contradicted=0 amended=0/0 receipt_ok=1 controls_rejected=0/0 errors=0 met=False`, exit 1; at `--tip e0b5b1ea` the same with `receipt_ok=0`. Matches the committed pre-wave controls `controls/c2-freeze-tip.out` and `controls/c2-base.out` (population=14 confirmed). Until rows land at a measured tip, the mismatch machinery is exercised only by the counter's own synthetic controls.
- SCORECARD calibration 7 is not re-derived by C2; the freeze declares 7→7 with no re-derivable axis metric (AXES: "a score no reader can re-derive is an opinion, not a measurement"). The calibration content lives entirely in the registry gates.

## Freeze integrity (pinned hashes resolved)
`e0b5b1ead9adb7a5a4744caca8837ec6496e1ca1` and `8b9f3060966c22bede3094d748974caf041b4c33` are lane git commits (w1-spec.json: "freeze commit"/"controls commit"), not content hashes. Both are ancestors of HEAD 8f5f4e334fbecc2251c331f7301a0e8c01805391 (`git merge-base --is-ancestor` → yes). `git diff --stat e0b5b1ea HEAD -- .ufo/waves/round-60/controls/freeze.txt tools/round60-c2-counter.py` → empty: frozen claim text and counter bytes unchanged since the freeze commit.

## Verdict
Axis fit: **partial**. C2 counts a bounded self-assessment-mismatch class (verdict vs receipt re-evaluation; visible in output as `evaluated=E sensitive=E/E bound=N contradicted=K amended=K/K`) in addition to coverage + receipt predicates; it does NOT count SCORECARD/SHONEN-vs-observed-repo-state mismatches, and its observation anchor is the lane's own receipt, so its calibration meaning is conditional on C1 receipt authenticity and on registry rows actually landing. No predicate altered, no verdict claimed, no lane file edited.
