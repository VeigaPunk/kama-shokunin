## Round 21 — report landing audit and soname-aware install identity (2026-10-21)

Assigned axes remain operability 8 + calibration 7 (`shokunin.conf:52`).
Calibration 7 is the lowest non-retired assigned axis and sits below the
saturation line 8, so the lowest-axis obligation binds (AXES.md:33-34) and the
stagnation waiver does not apply (AXES.md:68-70). Capability window: the last
entry is round 20 (line 913); round 21 adds none, so the window reads 1 of 4
[INFERENCE: counting convention; CapabilityRuleReader ruled the nudge inactive].

Round start `7a6bc911f9eb7dbea9e3b81f5f2449ecda10096d`; measured commit
`b76727f31e522763ce24e43d6ec86d21b507a11f`; lane tip under review
`a6617149722c73d90e142fbdc8154d6967055f7e`. No code, test, registry or corpus
path differs between the measured commit and the lane tip
(`git diff b76727f a661714 -- tools tests registry corpus SCORECARD.md AXES.md LOG.md SKILL.md`
printed nothing).

### Claims

- **C1 — calibration, 7 → 7 (measured axis-move, not a capability).**
  `tools/report-landing-audit.py` detects five mechanical defect kinds in the
  fleet kama reports `.ufo/reports/round-N/kama.md` (fleet repo). Before: the
  tool is absent at round start (`git cat-file -e 7a6bc91…:tools/report-landing-audit.py`,
  exit 128). The claimed improvement is the detector: 9 defects in rounds
  10–20 (8 `landed-omitted`, 1 `unresolved-full-hash`). The ledger
  `registry/report-landing-errata.tsv` moves the reported "uncorrected" count
  9 → 0; that movement is bookkeeping and is not counted as the improvement.
- **C2 — operability, 8 → 8 (delta 0; hardening, no capability row).**
  The producer `install_links()` records soname/link identity and fails closed
  (`install-tree-unpinnable`) on unpinnable trees; the gate checks link chains,
  recomputes `install_links_sha256` and accepts `--expect-install-links-sha256`
  and `--require-install-links`. On the real b11755 tree, the frozen detector
  (round-start arm) catches link 0/13 and subdir 0/1; the current arm catches
  link 13/13 and subdir 1/1. Regular 3/3, type 1/1 and null-quiet controls hold
  in both arms. `install_tree_sha256` is unchanged (back-compat). This is
  declared-link identity, not execution authentication.

### Counting commands and exits (measured commit `b76727f3`)

Run: `python3 .ufo/waves/round-21/run.py --recipe .ufo/waves/round-21/recipe.json`
→ `runs/b76727f3/`; recipe SHA-256 `9d68997d207756f72f5471daed1798ad9a1975a2c7193d40397e38c412194d3e`.
**28 commands, 28/28 declared exits met**; the 56 stdout/stderr streams re-hash
to the recorded SHA-256 values (checked by the scribe, mismatches 0).

| Claim | Command (as recorded in `commands.json`) | Exit | Observed |
|---|---|---|---|
| C1 before | `git -C kama-shokunin cat-file -e 7a6bc91…:tools/report-landing-audit.py` | 128 | tool absent at round start |
| C1 selftest | `/usr/bin/python3 tools/report-landing-audit.py --selftest` | 0 | cases=32 failed=0 |
| C1 detector | `/usr/bin/python3 tools/report-landing-audit.py --rounds 10-20 --no-errata --json` | 1 | defects=9, by_kind landed-omitted 8 / unresolved-full-hash 1, uncorrected=9, status failed, required_commits=42, post_report_commits=4, reports=11 |
| C1 ledger | `/usr/bin/python3 tools/report-landing-audit.py --rounds 10-20 --json` | 0 | corrected=9, uncorrected=0, errata_rows=9, errata_invalid=0, errata_unmatched=0, status clean |
| C2 grid selftest | `/usr/bin/python3 tests/llamacpp-live/install-links-grid.py --selftest` | 0 | cases=13 failed=0 |
| C2 grid frozen | `… install-links-grid.py --arm frozen --json` | 1 | link 0/13, subdir 0/1, regular 3/3, type 1/1, null quiet; status fail (expected: the frozen arm is the round-start control) |
| C2 grid current | `… install-links-grid.py --arm current --json` | 0 | link 13/13, subdir 1/1, regular 3/3, type 1/1, null quiet; real_tree_gate_clean true; wrong [] |
| C2 grid both | `… install-links-grid.py --arm both --json` | 1 | combined exit 1 because the frozen arm fails; back_compat_install_tree_sha256_equal true |
| C2 gate selftest | `/usr/bin/python3 tests/llamacpp-live/check-receipt.py --selftest` | 0 | 11 VALID + 1 NOT-EVALUATED accepted; 91 mutations + unreadable rejected |
| C2 producer selftest | `/usr/bin/python3 tools/kama-llamacpp-live.py --selftest` | 0 | ok |
| C2 live receipt pinned | `check-receipt.py runs/b76727f3/live-receipt.json --require-schema v3 --require-install-links --expect-model-sha256 270cba1b… --expect-install-tree-sha256 6c216313… --expect-install-links-sha256 5cb9f486…` | 0 | VALID |
| C2 live receipt wrong pin | `check-receipt.py … --require-install-links --expect-install-links-sha256 000…0` | 1 | INVALID, pin differs |
| C2 legacy R18 ×3 | `check-receipt.py .ufo/waves/round-18/live-recovery/receipt-{1,2,3}.json` | 0, 0, 0 | VALID |
| C2 legacy R18 required | `check-receipt.py …/receipt-1.json --require-install-links` | 1 | INVALID: no `server.install_links` block |

The live receipt (`runs/b76727f3/live-receipt.json`, schema
`kama-llamacpp-live/v3`, outcome `pass`) carries 10 links,
`install_links_sha256` `5cb9f4865c8e1315dbd1baa99310c9bc65ddcf469929488359c66587b6470060`,
`install_tree_sha256` `6c216313a88d71b141bc62f684b8f95c040710ff050801b13521861826785a2c`.
Its `teardown` block is recorded; the scribe observed no `llama-server` process
at 11:18 UTC (`pgrep`-equivalent count 0).

Frontier (round-end census, the sources registry): rows 65 → 74 (tier A 62 → 70,
tier B 0 → 1, tier C 3; mined 52 → 60, queued 6 → 7, rejected 7 → 7). The
`scripts/sources-census.sh validate … kama` and `census` runs exit 0; W04
duplicate-URL warnings are printed and named.

### Capability-table decision

**No new `capabilities:` row this round.** C2 hardens the existing
`live-llamacpp-lifecycle` row (canonical list, line 628) and does not add a
repertoire entry. Basis: AXES.md:59-64 (rows enter only through a demonstrated
round; a claim type must be declared, AXES.md:40-41) and the lane's own
precedent for hardening (R17 :669-670, R18 :749-751, R19 :828-829, each scored
8 → 8 with no row). The strongest counter is that before this change the gate
could not reject a retargeted soname link; the R19 install-tree pin had the
same blind spot for regular files and entered no row. Ruling source:
`.ufo/waves/round-21/build/advice/CapabilityRuleReader.md` (VERDICT partial).
If the operator rules "capability", the row needs a real-surface probe; the
grid runs on a mirror copy (`install-links-grid.py:44`, `mirror()` 83-91), so it
is not that probe [INFERENCE].

### Limits carried into this round's record

- C1 reads fleet reports from the fleet working tree (`Path(fleet_repo)/rel`,
  `tools/report-landing-audit.py` lines 161 and 168), not from a committed blob.
  The fleet `.ufo/reports` path was clean when the scribe checked (`git status`
  empty), but that is not shown for measurement time [INFERENCE]. The ledger is
  read from the committed branch blob (`git show <branch>:registry/...`).
- The "9/9 hand-confirmed, 0 FP/FN" claim is relayed from build seats; the
  scribe did not re-run those hand recounts.
- C2 is declared-link identity only: no execution authentication, no
  loaded-weight identity, no consumer-health claim.
- Scores are self-assessed. Other axes held: freshness 8, coverage 9, depth 7,
  adjacency 7 (carried from round 20 line 885; not re-measured this round).
- Trend verdicts for round 21 are not drafted here; the ScribeTrends seat owns them.

### Evidence pointers

- `runs/b76727f3/commands.json` (measured_commit, recipe_sha256, 28 entries)
- `runs/b76727f3/c1-audit-{selftest,raw,ledger}.stdout`, `c1-absent-at-base.stderr`
- `runs/b76727f3/c2-grid-{selftest,frozen,current,both}.stdout`, `c2-gate-selftest.stdout`, `c2-producer-selftest.stdout`
- `runs/b76727f3/c2-live-receipt.stdout`, `live-receipt.json`, `c2-live-gate-pinned.stdout`, `c2-live-gate-wrong-links-pin.stdout`
- `runs/b76727f3/c2-legacy-receipt-{1,2,3}.stdout`, `c2-legacy-receipt-1-required.stdout`
- `runs/b76727f3/fr-sources-{census,validate}.stdout`
- Lesson: `corpus/lessons/round-21.md`; ledger: `registry/report-landing-errata.tsv`; SKILL rows: `SKILL.md:683` (report landing audit), `SKILL.md:684-685` (links pin, grid)
