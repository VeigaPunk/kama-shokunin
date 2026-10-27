# K5Harm — round 53 no-harm critic (lane kama, build c22602bd)

**Verdict: the named build edits (SKILL.md 2-line in-place fix, SCORECARD `### Evidence-pointer corrections (round 53)` append, SOURCES.md S506–S509 append) break none of the assigned checks irreparably — but they are NOT harmless against the standing reconcilers: the SKILL.md edit adds one new red fact (SCORECARD head `depth` row hash), and the gate/r43 red state is entirely the two unregistered round-53 counters; both are standard integration repairs, and the base 4229ea1b was already red on the unrelated 38/39 spot count.**

All commands run on a scratch clone of the lane at build `c22602bd8d83ab26349d1087e916ca537ee4f9d1` (base `4229ea1b9a789148dded1f159c20967d9a01373f`), scratch `/fast/scratch/hyaku/kama-r53/K5Harm` (removed after the run). X6Battery had not landed, so I ran the round-52 measured commands myself. No counter, preregistration or lane file was edited; no services started (no llama-server ever spawned — the C1/C2 counters are not in this seat's list); nothing written to `.ufo/waves/round-53/measured/`.

## Answer to the assigned hint first: the SCORECARD append is outside the round-52 restored region

- The round-52 restored blocks (fenced re-appends) end at line 2996 of SCORECARD.md; `## Round 52` starts line 2998; the build's `### Evidence-pointer corrections (round 53)` lands at lines 3027–3030, after `### Round-52 measured results`, at the end of the file.
- Fence-line count of SCORECARD.md is 20 at base and 20 at build (`git show REV:SCORECARD.md | grep -c '^```'`): the +4 lines open/close no fence, so section/origin parsing of every prior line is unchanged.
- The round-52 C2 counter still passes at the build: `python3 tools/round52-append-restore-check.py --repo . --tip c22602bd… --scratch $S` → `lane: tool v6 threshold 1 exit 0 events 110 disclosed_lines 10; own unheld A-corr 0, A/A-row 10`, all 8 fixtures ok, exit 0 (`out/K5Harm/r52-append-restore-build.txt`).

## Per-check results at the build (evidence in `out/K5Harm/`)

| Check | Command | Result at build | Harm? |
|---|---|---|---|
| planned-pointer | `python3 tools/planned-pointer-check.py SCORECARD.md` | `met=True`, exit 0 (`pointer-build.txt`) | none — the append adds no `§Round-N measured results` reference and does not touch the first `## Planned` sentence; all 11 `§…` refs still resolve |
| sources-append-only | `python3 tools/sources-append-only.py --from 4229ea1b… --to c22602bd… --repo .` | `added S506…S509 (allowed); no append-only violations`, exit 0 (`sao-base-to-build.txt`) | none — pure row adds; S505 untouched (S509 is a new row, not an in-place anchor edit) |
| append-only-audit | `python3 tools/append-only-audit.py --repo . --to c22602bd…` | exit 0; summary unrestored=0 partial=0 regressed=0 bad_disclosures=0 bad_declarations=0 (`aoa-build.txt`) | none — the 110 graded events are byte-identical to the base run (`aoa-base.txt` diff); the build adds no deletion in any contract file (SCORECARD +4/-0, SOURCES +4/-0) and SKILL.md is not in `registry/append-only-contract.tsv` |
| report-landing-audit | `python3 tools/report-landing-audit.py --lane-repo . --fleet-repo /home/vgpnk/Projects/shokunin --rounds 10-52` | exit 1 at **base and build**, identical summary `reports=43 defects=41 corrected=9 uncorrected=32` (`rla-base.full.txt`, `rla-build.full.txt`) | none — the 32 uncorrected defects are pre-existing history over rounds 10–52; the build's two commits are round-53 commits and no round-53 fleet report exists yet |
| sources census | `bash scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama` | exit 0, `kama ok` (`census-validate.txt`) | none — diff vs the freeze-time `.ufo/waves/round-53/census/start.out` is exactly one added benign warning `W04 S509 duplicate url …ggml-backend-reg.cpp across scopes` (S509 shares S505's URL by design; warnings never change status); no E-code |
| round41-scorecard-reconcile | `python3 tools/round41-scorecard-reconcile.py --repo . --tip c22602bd…` | `mismatches=2 met=False`, exit 1 (`r41-build.txt`) | **1 new harm** (defect D1); the other mismatch is pre-existing |
| round42-selfdesc-reconcile | `python3 tools/round42-selfdesc-reconcile.py --repo . --tip c22602bd…` | `mismatches=2 met=False`, exit 1 (`r42-build.txt`) | same 1 new harm (D1) + pre-existing |
| round43-registry-audit | `python3 tools/round43-registry-audit.py --repo . --tip c22602bd…` | `unreg=2 selftest=1 spot=1 mismatches=4 met=False`, exit 1 (`r43-build.txt`) | unreg/selftest = known counter-registration item (D2); spot = pre-existing (D3) |
| gate-registry-check | `python3 tools/gate-registry-check.py --repo . --rev c22602bd…` | `registered 50 unregistered 2 defective 0`, exit 1 (`gate-build.txt`) | the two unregistered paths are exactly `tools/round53-replay-code-audit.py` and `tools/round53-cited-path-check.py`; `defective 0` proves the SKILL.md in-place edits broke no registry row (no missing-path defect) |

## Base-vs-build attribution (same commands at base 4229ea1b, `reconcilers-base.txt`, `gate-selftest.txt`)

- r41 base: `mismatches=1` — only the calibration run fact (38 vs 39 spotchecks). Build adds exactly the `depth` SKILL.md hash mismatch → `mismatches=2`.
- r42 base: `mismatches=1` (same pre-existing fact). Build: `mismatches=2`.
- r43 base: `mismatches=1` — only `spot=1`. Build: `unreg=2 selftest=1 spot=1` → 4.
- gate selftest with `master` pinned to base: `GATE_SELFTEST pass=6 fail=0` exit 0; pinned to build: `FAIL lane-tip c22602bd8d83: exit=1 line='registered 50 unregistered 2 defective 0'` → `pass=5 fail=1` exit 1. The selftest failure is byte-for-byte the unregistered counters, nothing else.
- The 38-vs-39 spot count is **pre-existing at the round-53 base**: commit `4229ea1b` (round-52 verifier spotcheck, integrator) added `corpus/lessons/round-52-verifier-spotcheck.md` after the round-52 measured commit `35e3b1dc` re-derived the head with `38`. `git ls-tree --name-only REV corpus/lessons/ | grep -c 'verifier-spotcheck.md$'` → 38 at `35e3b1dc`, 39 at base and build.

## Defects

### D1 (build-caused, new vs base) — SCORECARD head `depth` row hash desynced by the SKILL.md in-place edit

- File/line: `SCORECARD.md:16` — `| depth | **7** | `SKILL.md` sha256 `cfcc4291…` (1559 lines); …`.
- The build's SKILL.md edit (`/fast/scratch/.../lane` diff `4229ea1b..c22602bd`: line 113 `scripts/local-helper.mjs` → `~/Projects/ufo-fsd-alpha/scripts/local-helper.mjs`; line 895 `tests/report-audit/…` → `tests/report-audit/`) changes the SKILL.md blob, so the head fact is stale:
  `git cat-file blob 4229ea1b…:SKILL.md | sha256sum` → `cfcc429130edc5eab7aedf733a51c8cf4e14138cec4ce2249f3f03a286ca1c26` (matches the row);
  `git cat-file blob c22602bd…:SKILL.md | sha256sum` → `a6a19d13580151eaeb9c4a9cee6ad218dd5c5b0916c9717332b6d239a25a8add`.
- Command that shows it: `python3 tools/round41-scorecard-reconcile.py --repo . --tip c22602bd…` → `detail: depth sha256 SKILL.md cited cfcc4291… observed a6a19d13…` (also fails r42 via the imported r41 leg).
- Proposed fix (integration, where the head is re-derived in place per SCORECARD.md:6 — the head is exempt from append-only grading exactly for this; full text `scorecard-head-fix.diff` in the out dir):
```diff
--- a/SCORECARD.md
+++ b/SCORECARD.md
@@ -16 +16 @@
-| depth | **7** | `SKILL.md` sha256 `cfcc429130edc5eab7aedf733a51c8cf4e14138cec4ce2249f3f03a286ca1c26` (1559 lines); …
+| depth | **7** | `SKILL.md` sha256 `a6a19d13580151eaeb9c4a9cee6ad218ddc5c5b0916c9717332b6d239a25a8add` (1559 lines); …
```
(Line count stays 1559 — verified both blobs — and the row's `grep -c '^## ' SKILL.md` → `40` fact still holds at the build.)

### D2 (known integration item, attribution confirmed) — two round-53 counters unregistered

- `gate-registry-check` at the build: `unregistered tools/round53-cited-path-check.py`, `unregistered tools/round53-replay-code-audit.py` → exit 1; r43 reads `unreg=2` and its `selftest` fact fails only because gate selftest arm 6 evaluates the lane tip (`gate-selftest.txt`: `FAIL lane-tip … registered 50 unregistered 2 defective 0`). Not caused by the SKILL.md edits or the SCORECARD append (`defective 0` both sides). Already listed as a known integration item (SKILL §Round-53 instrument registry); no new content added by this seat.

### D3 (pre-existing at the base, NOT build-caused — recorded so the build is not blamed) — calibration spot count 38 vs 39

- `SCORECARD.md:18` calibration row: `… glob …` → `` `38` (outside closures on record) `` while the tree holds 39 `corpus/lessons/*verifier-spotcheck.md` blobs since base commit `4229ea1b`. r41/r42 report it as the run fact failure and r43 as `spot=1` at base and build alike. Same integration fix as D1 (head re-derivation), same diff hunk: `` `38` (outside closures on record) `` → `` `39` (outside closures on record) `` in `scorecard-head-fix.diff`.

## Integration must-dos this seat's evidence supports (no other action required)

1. Register the two round-53 counters in SKILL.md (known item) — repairs gate exit 1, r43 `unreg=2` + `selftest=1`, and restores `GATE_SELFTEST pass=6 fail=0`.
2. Re-derive the SCORECARD head per `scorecard-head-fix.diff` — repairs r41/r42 (`hash_bad` and the pre-existing `run_bad`) and r43 `spot=1`.

Nothing in the build requires touching the frozen counters, the preregistration, or any checked tool.

## Files written

- Report: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/K5Harm.md`
- Raw evidence: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/K5Harm/` (`r41-build.txt`, `r42-build.txt`, `r43-build.txt`, `gate-build.txt`, `gate-selftest.txt`, `pointer-build.txt`, `sao-base-to-build.txt`, `aoa-base.txt`, `aoa-build.txt`, `census-validate.txt`, `rla-base.full.txt`, `rla-build.full.txt`, `rla-base-build.txt`, `r52-append-restore-build.txt`, `reconcilers-base.txt`, `scorecard-head-fix.diff`)
