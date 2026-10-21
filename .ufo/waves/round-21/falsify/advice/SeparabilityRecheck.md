VERDICT: confirm - C1 and C2 stay causally separable by file set at a6617149 (no counterexample); two provenance gaps (F4, F5) need a recipe-level fix.
Attacked: "each claim's counting commands depend only on their own file set" (C1: tools/report-landing-audit.py + registry/report-landing-errata.tsv; C2: tools/kama-llamacpp-live.py, tests/llamacpp-live/check-receipt.py, tests/llamacpp-live/install-links-grid.py). "confirm" = the claim survives this re-test.

## Method (all executed; lane, fleet and install tree read-only; no live launch, no llama-server, no downloads)
- Scratch clones /tmp/kama-r21-SeparabilityRecheck/<cfg> at a6617149. Each revert is a commit, because the audit reads the committed errata blob (see F4). Blob states verified in out/configs.json.
- Configs: ctrl (tip); ctrlnoop (empty commit); revC1 (C1 set removed); revC2 (producer and gate at 7a6bc911, grid removed); single-file revErrata, revProducer, revGate, revGrid.
- run_matrix.py (exit 0): 17 counting commands per config; c2-live-receipt excluded (live launch forbidden). Compared exit plus normalized stdout/stderr with runs/b76727f3. All 28 official sha256 values match commands.json.
- Deviation: audit runs add --fleet-repo /home/vgpnk/Projects/shokunin (the default here.parent is wrong in scratch; equal to the official default).
- serial_rerun.py (exit 0): same matrix serially, 136 rows, 0 differences vs parallel on exit, exit_ok, stdout_eq, stderr_eq.

## Matrix: exit and normalized output vs official (C1 4 cmds, C2 12, nh 1)
config      | C1           | C2             | nh  | exit mismatches
ctrl        | 4/4 & 4/4    | 12/12 & 11/12 | 1/1 | none
ctrlnoop    | 4/4 & 4/4    | 12/12 & 11/12 | 1/1 | none
revC1       | 1/4 & 0/4    | 12/12 & 11/12 | 1/1 | audit selftest/raw/ledger exit 2 (file absent)
revC2       | 4/4 & 4/4    | 5/12 & 3/12   | 1/1 | grid x4 exit 2 (file absent); live-gate-pinned, wrong-pin, legacy-required exit 2 (unknown flags)
revErrata   | 3/4 & 3/4    | 12/12 & 11/12 | 1/1 | ledger exit 2: "could-not-evaluate: git show master:registry/report-landing-errata.tsv ... does not exist"
revProducer | 4/4 & 4/4    | 9/12 & 7/12   | 1/1 | grid selftest/current/both exit 2: "current producer has no install_links()"
revGate     | 4/4 & 4/4    | 6/12 & 3/12   | 1/1 | grid selftest/current/both and live-gate-pinned/wrong-pin/legacy-required exit 2
revGrid     | 4/4 & 4/4    | 8/12 & 7/12   | 1/1 | grid x4 exit 2 (file absent)
Output-only: c2-producer-selftest differs in every config, including ctrl (F2).

## Findings
- F1 separability holds: C2 is unchanged with C1 reverted (revC1 = ctrl), and C1 is unchanged with C2 reverted (revC2 = ctrl). Static grep: no C1 name in the three C2 files and no C2 name in the audit. Errata evidence text is parsed (line 221) but never used in counting.
- F2 benign: the producer selftest prints random ephemeral loopback ports ("closed tcp6 listeners ::1:35371, ..."). Its commands.json stdout_sha256 cannot be reproduced even at the tip; exit 0 is stable.
- F3 benign: c1-absent-at-base stderr reads "exists on disk" or "does not exist" depending on the working tree; exit 128 is stable.
- F4 binding differs (observed): the C1 ledger reads the committed branch blob. Removing the errata from the working tree only leaves the ledger clean (exit 0, corrected 9; out/revWT). C2 reads the working-tree producer and gate; a working-tree-only producer revert gives grid exit 2 (out/revWT). Dirty trees move C2 results but not C1's ledger. The official C2 current arm did read committed content: current_sources_sha256 equals the tip blobs (check-receipt 6b8764..., producer e4cc6d...).
- F5 provenance gap (C2): the live receipt's tool.sha256 = e4cc6d88... equals the tip producer (verified). But the recipe's pinned gate command has no --expect-tool-sha256, and the gate's only file read is its receipt argument (check-receipt.py:2344; tool.path is never opened). So under revProducer the pinned gate still exits 0. Pinning the working-tree digest: tip exit 0 VALID; revProducer exit 1 INVALID ("tool.sha256 e4cc... != expected 83eac5c...", out/toolpin). The official evidence does not bind the receipt to the producer file.
- F6 counts, not exit: the old gate selftest exits 0 and prints "6 VALID and 1 NOT-EVALUATED; 77 mutations" (revC2, revGate). The new one prints "11 VALID ...; 91 mutations". Attribute C2 gate claims by printed counts.
- F7 minor: the audit reads fleet .ufo/reports/round-N/kama.md from the fleet working tree. All 11 round reports (10-20) currently hash-object equal HEAD. Not pinned in the recipe or output.
- F8 detector stands alone: with the errata absent, --no-errata still exits 1 with 9 defects (revErrata). Only the ledger changes, to exit 2, by design.

## Claims reproduced (ctrl = official)
- C1: selftest 32/32 failed=0; raw 9 defects (landed-omitted 8 = r10x1, r18x3, r20x4; unresolved-full-hash 1 = r20), required 42, post-report 4; ledger corrected 9, uncorrected 0; absent at base exit 128.
- C2: frozen link 0/13, subdir 0/1, regular 3/3, type 1/1, null 0/1; current link 13/13, subdir 1/1, regular 3/3, type 1/1, null 0/1; real tree unchanged (install_tree 6c2163..., links 5cb9f4...); gate selftest 11 VALID + 1 NOT-EVALUATED, 91 mutations; live receipt VALID with pins, INVALID with wrong links pin; legacy 1-3 VALID; legacy-1 with --require-install-links INVALID.

## Smallest safe correction (advisory; L1 decides)
1. Add --expect-tool-sha256 e4cc6d8885c7755717157fd23bfce3be39288990a9cf5985cb1c56a4b11cf68f to the pinned c2-live-gate command; re-run only that gate command (no live launch). Verified: tip exit 0; producer-changed exit 1.
2. Judge c2-producer-selftest by exit plus the "selftest: ok" prefix, not its stdout hash (F2).
3. [INFERENCE] Changing the recipe changes recipe_sha256 (9d68997d...), so the L1 records the new measurement.

## Commands and exits (executed)
- git clone, checkout, rm, commit for scratch configs: exit 0 each; blob states verified.
- run_matrix.py: exit 0. serial_rerun.py: exit 0 (0 differences).
- revWT: ledger exit 0 (errata removed from working tree only); grid --arm current exit 2.
- toolpin: ctrl pin=working-tree exit 0; revProducer pin=working-tree exit 1; revProducer pin=tip exit 0.
- sha256sum recipe.json = 9d68997d207756f7 (matches commands.json).
- Residue: no leftover processes; real install tree mtime unchanged (2026-10-20 08:10).

Tools: none installed or updated (system python3 3.14.8, git 2.56.0, jq and sha256sum pre-existing). No pacman. No model downloaded.
Out: .ufo/waves/round-21/falsify/out/SeparabilityRecheck/ (run_matrix.py, serial_rerun.py, matrix.tsv, matrix.json, configs.json, runs/, serial/, revWT/, toolpin/). Scratch removed after this report.
