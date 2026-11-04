# MT01 — mutation probes (operability + calibration)

**Escapes:** EX01(a) containment removal (other identity checks still reject outside fixture); EX01(e) inverted production descendant test; EX04(c) receipt-selected upper base. These are detector survivors, not contract changes.
**Inconclusive:** EX05 honest baseline was already red: `PIN_RECHECK_SELFTEST pass=1 fail=10`, exit 1. No pin mutant is credited as killed.

| Module / mutant | Verdict | Red arms |
|---|---|---|
| EX01 a: drop repo containment while retaining committed identity checks | survived | none |
| EX01 b: bind row introductions to register introduction instead of blame | killed | late-path-bound |
| EX01 c: accept untracked path with current revision row identity | killed | late-path-untracked |
| EX01 d: ignore late flag and read default register | killed | late-path-outside-repo, late-path-untracked |
| EX01 e: invert production strict-descendant test | survived | none |
| EX03 a: skip lesson-only-token rejection | killed | lesson-only-token |
| EX03 b: skip correction-restatement region exclusion | killed | token-only-in-correction-region |
| EX03 c: read F5 population at tip instead of sealed revision | killed | registry-base-bound |
| EX03 d: accept corrections for holding facts | killed | correction-for-holding-fact |
| EX03 e: remove at revision equality check | killed | wrong-at |
| EX04 a: declare falls yes despite declared-window mismatch | killed | declared-mismatch |
| EX04 b: accept event when only one of its multiple lines is covered | killed | window-uncovered |
| EX04 c: read round83 upper base from prior receipt instead of frozen plan | survived | none |
| EX05 a: trust declared verdict instead of byte comparison | inconclusive | missing-row, duplicate-row, unknown-row, holds-but-absent, drifted-but-present, quote-26-words, quote-not-at-line, digest-mismatch, ungraded-without-note, verdict-vocabulary |
| EX05 b: skip extract digest recomputation | inconclusive | missing-row, duplicate-row, unknown-row, holds-but-absent, drifted-but-present, quote-26-words, quote-not-at-line, digest-mismatch, ungraded-without-note, verdict-vocabulary |
| EX05 c: count ungraded row in graded tally | inconclusive | green-honest, missing-row, duplicate-row, unknown-row, holds-but-absent, drifted-but-present, quote-26-words, quote-not-at-line, digest-mismatch, ungraded-without-note, verdict-vocabulary |

Honest tallies: EX01 `28/0` exit 0; EX03 `16/0` exit 0; EX04 `7/0` exit 0; EX05 `1/10` exit 1 (pass/fail). All four drafts landed; none missing.
Detector command for every run: `TMPDIR=/fast/scratch/hyaku/kama-r83/MT01Mutants python3 /fast/scratch/hyaku/kama-r83/MT01Mutants/clone/tools/<module> --selftest`; cwd is that clone. Exact expanded commands, exits, red arms and absolute stdout/stderr receipt paths are in `MT01.json` and `probe-evidence.json` in this directory.
One mutant at a time; each followed by exact-byte restoration and the same detector. All 16 restored SHA-256 values equal their pristine values; restored exits equal baseline exits. Per-run hashes and complete actual outputs are retained in the JSON receipts.
Clone starts at frozen base; draft-only commits were made inside the verified scratch clone before runs. No lane module/register changed; no installs.
EX05 baseline failures include missing-row, duplicate-row and unknown-row returning exit=0 despite findings. Mutation output alone cannot establish a kill on this baseline.
Scratch root removed after receipt persistence. Report lives inside the permitted seat directory; conflicting trailer path outside it intentionally not written.
