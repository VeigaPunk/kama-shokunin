VERDICT: confirm - eight stale round-19 C1 count lines in SCORECARD.md, LOG.md and corpus/lessons/round-19.md; round-18.md erratum has none; four-row registry and 15-case selftest reproduce at pin 37bd4c5.

Scope: lane 37bd4c5bd456a2f8a54d3312c28495c321715856 (read-only; no lane edits). Measured values from `.ufo/waves/round-19/evidence/c1-counting.txt` (measured_commit 028235e6, four rows, selftest 15) and re-run in a scratch clone at 37bd4c5.

## Re-verified at pin (exit codes observed)
- `git merge-base --is-ancestor 028235e6 37bd4c5` → 0 (measured commit is an ancestor; 8 commits between).
- `registry/required-citations.json` at 37bd4c5 → 4 rows (s055-commands, gate-live-1, c2-official-stdout, gate-live-checkpoint), counted via python json, exit 0.
- `python3 tools/citation-provenance.py` → `required=4 found=4 verified=4 missing=0 mismatch=0 off_ref=0`, exit 0.
- `python3 tools/citation-provenance.py --selftest` → `selftest: ok (15 cases)`, exit 0.
- `python3 tools/citation-provenance.py --json` → counts `required 4 / verified 4 / missing 0 / mismatch 0`, exit 0.
- `python3 tools/citation-provenance.py --docs /dev/null` (all tokens absent) → `required=4 found=0 verified=0 missing=4 mismatch=0 off_ref=0`, exit 1. Matches the before-state in c1-counting.txt. [INFERENCE that /dev/null equals the measured no-token state: same counts, not the same bytes.]
- `git grep -n -E 'required=3|missing=3|verified=3|found=3|three registry-row digests|selftest 5 cases|3 rows' 37bd4c5…` → exit 0 (hit list below).

## Stale hits to correct (file:line → stale text → correct value at 028235e6/37bd4c5)
| # | file:line | stale text | correct value |
|---|---|---|---|
| 1 | SCORECARD.md:823 | `before required=3 found=0 verified=0 missing=3` exit 1 | `required=4 found=0 verified=0 missing=4 mismatch=0` exit 1 |
| 2 | SCORECARD.md:824 | `required=3 found=3 verified=3 missing=0 mismatch=0` exit 0, `selftest 5 cases` | `required=4 found=4 verified=4 missing=0 mismatch=0` exit 0, `selftest 15 cases` |
| 3 | SCORECARD.md:846 | erratum: "checker binds three registry-row digests" | "four registry-row digests" (15 selftest cases at 847 already correct) |
| 4 | LOG.md:1146 | `missing=3 exit 1 → missing=0 verified=3 exit 0; selftest 15 cases` | `missing=4 exit 1 → missing=0 verified=4 exit 0`; selftest 15 correct |
| 5 | LOG.md:1172 | erratum: "binds three registry-row digests" | "four" |
| 6 | corpus/lessons/round-19.md:12 | `before the tokens: missing=3, exit 1` | `missing=4`, exit 1 (the same line's `required=4 found=4 verified=4` is already correct) |
| 7 | corpus/lessons/round-19.md:75 | M1 row: `before/after missing=3 → missing=0` | `missing=4 → missing=0` |
| 8 | corpus/lessons/round-19.md:83 | "digests and ancestry of the three registry rows" | "four registry rows" |

Round-18 erratum (corpus/lessons/round-18.md, lines 386-424 at 37bd4c5): zero stale C1 counts. Its cite-token list (418-424) names four tokens, consistent with the four-row registry. No draft.

## Drafted corrections (append-only; not applied)
`.ufo/waves/round-20/build/out/StaleCountSweep-2/correction-drafts.md` holds one appended paragraph each for SCORECARD.md, LOG.md and corpus/lessons/round-19.md. Each states the four-row before/after with exits and cites `c1-counting.txt`; none rewrites an existing line. Receipts: `out/StaleCountSweep-2/receipts.txt`.

## Out of scope (hits found, not edited)
- corpus/lessons/round-19-verifier-spotcheck.md:105,129-130,184-187 — the verifier spotcheck that routed this sweep; it describes the stale state correctly as stale. Line 76 already has the correct 15 cases / 028235e6. Not in the sweep list; L1 to decide.
- .ufo/waves/round-19/evidence/final-selftests.txt:9 (`required=3 … verified=3`). Last changed at f1790e2 (ancestor of 028235e6), so it is a 3-row-era record superseded by c1-counting.txt. Left untouched.
- .ufo/waves/round-19/build/advice/*.md (about 30 hits, e.g. C1WrongDigest.md:25 "selftest 5 cases", CritC1Inflation.md:6). Contemporaneous seat outputs; not edited. [INFERENCE that they were run against the 3-row tree; not checked individually.]
- "3 rows" hits in SCORECARD.md:19,89 and LOG.md:228,522 concern endpoint-consumers.tsv (operability registry), not C1: excluded.

## Tools
No installs. No lane modifications. Scratch clone `/tmp/kama-r20-StaleCountSweep` removed after the run.

Open for L1: apply the three appended paragraphs (SCORECARD, LOG, lesson-19) and decide the verifier-spotcheck file. The appended paragraphs are drafted, not applied, per the instruction to leave the lane untouched.
