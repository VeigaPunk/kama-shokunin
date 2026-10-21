VERDICT: refute - C1 as worded overreaches: the checker digest-checks three registry rows and nothing about the sentences beside them; one pin verifies bytes that contradict its sentence; defects 1 and 4 have no machine check.

Scope: `cp -a` snapshot of the lane (03:29Z, 2026-10-21) at /tmp/kama-r19-CritC1Inflation; lane untouched. Every command, exit and output: `/tmp/kama-r19-CritC1Inflation/out/RECEIPT.md`; raw receipts in `out/receipts/`; fixtures in `out/mutants/`.

## Holds (narrow mechanism only)
- `python3 tools/citation-provenance.py` -> `required=3 found=3 verified=3 missing=0 mismatch=0`, exit 0 (R0). `--selftest` -> `selftest: ok (5 cases)`, exit 0 (R2).
- Committed base (`git show 1b85a24:corpus/lessons/round-18.md`, zero tokens) -> `required=3 found=0 verified=0 missing=3`, exit 1 (B0). The before/after counts are real.
- The three registry digests equal git's blob digests (R1 `observed_sha256` = `sha256`).

## Counterexamples
1. **Contradicted sentence, verified pin (strongest).** round-18.md:418-419 says "The recovery gate output describes `live-recovery/`, not the checkpoint `live/`", pinned by `cite(eb78788b..., .ufo/waves/round-18/runs/live-gate-1.stdout, sha256=b2043ba8...)`. Those pinned bytes are `VALID .../round-18/live/receipt-1.json` (90 B, G5; `live-recovery` absent, P1). The recovery output is at 1b85a24 and 8bf99ca: sha `1cb5a41b...`, `VALID .../live-recovery/receipt-1.json` (G6, G7). Checker exit 0 on the current pin. Candidate re-pin to 1b85a24 / `1cb5a41b...` passes (M6); keeping the old token with the new pin fails (M6b, exit 1). The checker never reads the sentence; it accepts whichever pin is written. The round-18 SOURCES S055 qualification (SOURCES.md:217-221) says the tip's gate describes live-recovery, so two lane authorities now disagree.
2. **Token placement is not enforced (M2, exit 0).** A lesson with zero tokens plus the three tokens in a default-doc stand-in passes; `documents` is the stand-in. DEFAULT_DOCS is hard-coded to round-18.md, SOURCES, SCORECARD, LOG (citation-provenance.py:33-34); round-19.md is not scanned. This is round-19.md:37-39 candidate (a), still unfixed, and round-19.md:41 says a fix counts only once shown able to fail.
3. **The registry is the denominator.** `required = len(registry)` (citation-provenance.py:96). One row -> `required=1`, exit 0 (M3). Duplicated rows -> `required=6`, exit 0 (M4).
4. **Labels.** An altered registry digest reports `missing`, not `mismatch` (M5, exit 1). `mismatch` fires only when token and registry agree on a digest git disagrees with (citation-provenance.py:81-90).
5. **Not wired, not committed.** No test, gate or `run.py` references the checker (tree-wide search, RECEIPT). round-19.md:45 lists it as a manual step. `tools/citation-provenance.py`, `registry/required-citations.json` and `corpus/lessons/round-19.md` are untracked; round-18.md, SOURCES.md, SCORECARD.md are modified (G10).

## Unearned wording (lane file:line)
- round-19.md:5-6 "the four routed round-18 pointer defects become machine-checkable." The verifier's four defects (round-18-verifier-spotcheck.md:128-146): (1) verdict tally, (2) S055/Gate pointer, (3) SCORECARD command, (4) residual role record. Defects 1 and 4 are not pointers and have no check. Defect 2 has two tokens, one inverted (#1). Defect 3 pins only the stdout; the `c2/survivors.py` command and "the two agree" (round-18.md:403-408) are unpinned. LOG.md:1122, which the verifier named for defect 1, still says "five confirm, two partial"; no correction was appended there.
- round-19.md:7-8 "require a `cite(...)` token per material citation." The code loops over registry rows only (citation-provenance.py:75-82). "Material" is undefined in the lane. The lesson's own Gate relies on unpinned receipts: round-18.md:53 (`live/receipt-1.json`, `runs/commands.json`, `runs/live-gate-1.stdout`, all unqualified) and SOURCES.md:67 (S055 receipts, unqualified). If "material" means "registry row", the sentence must say so.
- round-19.md:8 "verify the blob at that revision." It verifies a digest of the blob. It does not verify what the sentence says (#1). "Verify" overstates.
- round-19.md:8-10 "`residual/assignments.json` carry the corrections." The file is untracked and absent from HEAD (G10, G11). Its "6 reviewer, 1 critic" totals match the erratum (round-18.md:393-394), but it is not a committed dispatch record, which is what defect 4 asked for. [INFERENCE: written in round 19; the untracked status and its `call` field support this.]
- round-19.md:5 "(sourced)": the round-19 Gate table (round-19.md:25-30) has no C1 row. S057 is marked "grounds C2" (round-19.md:27).
- SCORECARD.md:821-822 "revision-qualified citations become machine-checkable." 70 corpus lines carry a 40-hex commit id (SOURCES 29, round-18 12, SCORECARD 14, LOG 15; P2). Three tokens pin three of them. The 10 SOURCES revision URLs are upstream, so a lane-local `git cat-file` cannot check them.
- SCORECARD.md:825-826 cites S057 as C1 evidence; S057 grounds C2 (identity boundary). round-19.md:32-33 gives S057 `used-by: registry/required-citations.json`; the registry never mentions S057 (P2: 0).
- round-18.md:412 "The routed revision defects are now machine-checked": the same overclaim; defect 2's pin is inverted, defect 3 is partial.
- Not overreach: the tool's own docstring (citation-provenance.py:2-14) says "for every required row in the registry". The overreach is in the lesson and SCORECARD.

## Impacted axis
Calibration only (C1, 7 -> 8). Before the tokens the sentence at round-18.md:418 was unverified prose. Now a "verified" stamp sits beside bytes that contradict it. The +1 is not earned as worded. Operability is unaffected.

## Smallest safe correction
1. Re-pin `gate-live-1` to 1b85a24 / `1cb5a41bbfeb8f0f9306d9bf86df83d33cf9bc3aa46887c574e1dd07875574c7` in the registry and the token at round-18.md:419 (M6 passes). If the checkpoint `live/` sentence needs a pin, add a separate token for 1c325b2 / `b2043ba8...` (G5, G6 verified).
2. Reword C1: "three registry rows pin blob digests, checked for existence and digest. The checker does not read the sentences beside tokens, enforce placement, or cover citations outside the registry. Defects 2 and 3 are partly pinned; defects 1 and 4 are not machine-checked."
3. Drop "per material citation", "four pointer defects" and "carry the corrections" unless the lists are exact. Add the LOG.md:1122 correction; commit `residual/assignments.json` or stop calling it a dispatch record.
4. Hold calibration at 7 until (a) item 1 lands, (b) placement is restricted to the authoritative lesson or class (a) is disclosed as open, and (c) a fail-capable check covers the sentence-to-bytes relation for the pinned rows. Under round-19.md:41, class (a) cannot count toward calibration.
5. Remove S057 from C1 evidence (SCORECARD.md:826) and from the registry `used-by` (round-19.md:32-33). Drop "(sourced)" or add a C1 source row.
6. Commit the checker, registry, lesson and erratum before any "machine-checkable" claim is scored (G10). Wire the checker into the official harness or label it manual.

## Verification notes
- Every factual claim above has an executed command and exit in `out/RECEIPT.md`. Unexecuted reasoning is marked [INFERENCE].
- One shell `grep -c` was used for a count (B0b), against the tool rule. B0 reproduces the same fact.
- Installs: none. No servers, no `agent://all`, no model named. Lane files unchanged; this report is the only write at the lane path.
