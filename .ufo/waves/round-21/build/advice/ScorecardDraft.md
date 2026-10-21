VERDICT: partial - round-21 SCORECARD section drafted; C1 holds 7→7 (improved-bounded), C2 holds 8→8, no capability row recommended.

# ScorecardDraft (round 21) — scoped findings

Scope: draft text only. Lane untouched (work in /tmp/kama-r21-ScorecardDraft, deleted at end). Text: `.ufo/waves/round-21/build/out/ScorecardDraft/SCORECARD-R21-draft.md`. Lane checked at a29bb84.

## Commands run (exit observed)
Run from scratch clone at a29bb84, explicit `--lane-repo/--fleet-repo` (default fleet = lane parent is only valid in the real lane):
- `python3 tools/report-landing-audit.py --no-errata` → **1** (`summary reports=11 defects=9 corrected=0 uncorrected=9 … status=failed`)
- `python3 tools/report-landing-audit.py` → **0** (`corrected=9 uncorrected=0 status=clean`)
- `python3 tools/report-landing-audit.py --selftest` → **0** (`selftest cases=15 failed=0`)
- `… --report 21=/tmp/…/draft21.md --no-errata` (probe, draft lacks a29bb84) → **1** (`round=21 required=1 … landed-omitted a29bb84…`)
- `python3 tests/llamacpp-live/check-receipt.py --selftest` → **0** (`9 VALID and 1 NOT-EVALUATED … 90 mutations + unreadable case rejected`)
- `python3 tests/llamacpp-live/install-links-grid.py --selftest` → **0** (`selftest cases=12 failed=0`)
- `python3 tests/llamacpp-live/install-links-grid.py --arm current` → **0** (`link=9/9 regular=2/2 type=1/1 null=0/1 wrong=0 status=pass`)
- `… --arm frozen` → **1** (`link=0/9 wrong=9 status=fail`; expected)
- `… --arm both --json` → **1** (rc is 1 whenever any arm fails, so the frozen-arm failure makes the pair exit 1; `current.status=pass`)
- `python3 tests/llamacpp-live/check-receipt.py .ufo/waves/round-18/live-recovery/receipt-1.json` → **0** (legacy VALID)
- same + `--expect-install-links-sha256 b58f1b4d…` → **1** (`receipt has no server.install_links_sha256 digest`; correct rejection)
- `python3 tools/kama-llamacpp-live.py --help`, `install-links-grid.py --help`, `check-receipt.py --help` → 0 each (no live launch)
- `sh scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama` → **0**; census rows 65, tier A62/C3, mined52/queued6/rejected7 (matches census-before)
- `python3 tools/report-landing-audit.py --json --no-errata` → 1 (failed status, expected)

Archived outputs: `.ufo/waves/round-21/build/out/ScorecardDraft/` (small text/JSON).

## Findings
1. **C1 landing audit is measured, but the score move is bounded.** Raw 9 defects: r20 unresolved-full-hash ×1, landed-omitted r20 ×4, r18 ×3, r10 ×1. The closure's round-20 flags were 5 (hash + 4 omitted); the audit adds r18 ×3 and r10 ×1, which the closure did not list. Errata corrects records; the fleet reports stay uncorrected. The R19 erratum refuted a 7→8 for a checker that binds tokens but not the sentence under test (SCORECARD.md:844-848). Recommendation: 7→7 improved-bounded. 7→8 is the L1's decision only if the closure accepts the set-membership check as calibration. [INFERENCE on the judgment, executed on the counts]
2. **C2 install-links is measured on a mirrored tree.** Frozen 0/9 vs current 9/9 link cells; controls and null unchanged in both arms; back-compat `install_tree_sha256` equal; gate rejects legacy digest pins as designed. Score 8→8 (delta 0).
3. **Capability row: do not enter.** R19's install-tree pin (sixth pin, C2 8→8) entered no row; install-links is the same pin family. The grid never produced a live receipt (live launch forbidden). [INFERENCE] The conditional row text is in the draft if the closure disagrees.
4. **Stagnation:** no row enters → window reads 1 of 4; calibration 7 < 8 → no waiver.
5. **Hazard for the L1:** `install-links-grid.py --arm both` exits 1 even when the current arm passes. Record the arms separately (`--arm current` exit 0, `--arm frozen` exit 1).
6. **Round-21 report gate:** `required=1`; the committed round-21 report must cite `a29bb84…` under `## Landed changes`, or the audit exits 1.

## Sources and out-of-scope
- New SOURCES rows: none opened by this seat. Placeholder only in the draft; scouts open and quote them. [INFERENCE: not exercised by me]
- No installs or upgrades. No pacman, no service, no model download.
- No lane, fleet, MANIFEST, or `~/.local/opt` mutation (grid reads the real tree; it wrote no files there).
- Official measurements (`runs/<tree>/`) are placeholders for the L1.

## Checks the main agent should run
`python3 tools/report-landing-audit.py` (exit 0 required), `--selftest` (15/15), `--arm current` (exit 0), `check-receipt.py --selftest` (exit 0), and the round-21 `--report 21=` gate after the report is committed.
