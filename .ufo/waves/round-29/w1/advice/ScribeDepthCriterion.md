# ScribeDepthCriterion — round 29 W1 report

## Behavior and findings
- Drafted two proposed `QUALITY.md` criterion blocks only: KQ38 for a future measured-depth re-claim and KQ39 for calibration/self-assessment. The current `corpus/QUALITY.md` tail ends with KQ37 and its round-28 qualification; the identifier search found KQ1–KQ37, so KQ38/KQ39 are the next IDs.
- KQ38 requires excluding type- or declared-bound-predictable rows before freeze and scoring both non-author shortcuts in a pre-freeze control wave, before data seats. It names the round-28 receipts that defeat the earlier tests: type-only A0 20/52 (met true) and post-data declared-bounds projection 20/20 (target 18, met true). The A1 counterpart of the type-only receipt records 0/52, met false.
- KQ39 distinguishes false-at-writing calibration mismatch from later freshness drift, requires append-only corrections with observed values, and counts false corrections as mismatches. It names the negative control receipts and outcomes in the committed round-29 `controls/SUMMARY.md`; `RefPaste` is kept separate as the reference policy that meets by design, not a control proving axis fit.

## Gates and provenance
- Round-28 conversion-control report records the exact historical command sequence:
  ```
  git clone -q /home/vgpnk/Projects/shokunin/kama-shokunin tree
  git -C tree checkout -q 75b78bb4900aae1edcdb6b229bb8c572c20fcbce
  git -C /home/vgpnk/Projects/shokunin/kama-shokunin show d8bf1804:.ufo/waves/round-28/count-c1.py > /tmp/a0-counter-kama-r28.py
  cp /tmp/a0-counter-kama-r28.py tree/.ufo/waves/round-28/count-c1-A0.py
  /usr/bin/python3 build_fixture.py
  timeout 900 /usr/bin/python3 tree/.ufo/waves/round-28/count-c1.py --lane tree --repo tree --out receipt.json
  timeout 900 /usr/bin/python3 tree/.ufo/waves/round-28/count-c1-A0.py --lane tree --repo tree --out receipt-A0.json
  ```
  In the inspected `controls-A1/CtlA1Conversion/REPORT.md`, A1 counted 0/52 and did not meet target 18; A0 counted 20/52 and met target 18. Receipt paths: `.ufo/waves/round-28/controls-A1/CtlA1Conversion/receipt.json` and `receipt-A0.json`.
- The post-data shortcut artifact records this exact invocation and result:
  ```
  /usr/bin/env -i PATH=/usr/bin:/bin HOME=/home/vgpnk LANG=C.UTF-8 /usr/bin/timeout 300 /usr/bin/python3 -I -S tree/.ufo/waves/round-28/count-c1.py --lane /fast/scratch/hyaku/kama-r28/w2/ExecShortcutPostData/tree --repo /fast/scratch/hyaku/kama-r28/w2/ExecShortcutPostData/tree --out /fast/scratch/hyaku/kama-r28/w2/ExecShortcutPostData/shortcut-receipt.json
  ```
  `counter-run.txt` records `registered 20 counted 20 target 18 met True not-counted []`, exit 0. Its report says the row policy was generated from declared bounds and the pinned declaration source, without using the landed outcome table, registry values or receipt live values.
- Round-29 `controls/SUMMARY.md` records the frozen counter SHA-256, 14 returned seats, all controls below target, and `RefPaste` as the reference policy. The observed lines include CtlTypeGuess unresolved 24; CtlSourceBounds unresolved 9; CtlBaseTree unresolved 9; CtlDeletion/CtlEditInPlace append-only false and unresolved 69; CtlJunk unresolved 22; CtlAllFalse unresolved 58; CtlLabelKeyed unresolved 80; CtlNoReader unresolved 22; CtlWorkingTree/CtlObjectStore unresolved 11; CtlDuplicate unresolved 22 or 1; RefPaste valid 11, false 0, unresolved 0.
- Calibration provenance: round-25 `SCORECARD.md:1278-1291` explicitly accepts that true-at-writing statements later made stale are drift under freshness, not overreach. Round-29 `preregistration.json:14-20` defines W via blame, observed-value correction rows, and false-correction handling.

## Touched surfaces and out of scope
- Created only `.ufo/waves/round-29/w1/out/ScribeDepthCriterion/quality-kq38.md`, `.ufo/waves/round-29/w1/out/ScribeDepthCriterion/quality-kq39.md`, and this report at `.ufo/waves/round-29/w1/advice/ScribeDepthCriterion.md`.
- No tracked product/corpus file, counter, judge, control, or receipt was edited. The drafts are proposals for L1 integration; no `QUALITY.md` update or claim judgment is asserted.
- No counter, build, test, server, or model command was run by this seat; the historical commands and outcomes above were transcribed from opened artifacts, not rerun. No tool was installed or updated.
- Directory creation command executed: `timeout 10s /usr/bin/mkdir -p /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/w1/out/ScribeDepthCriterion`; it returned no output and no error was reported.

## Known limits
- The two round-28 shortcuts are historical receipts used to specify a future rejection test; these drafts do not rescore round 28 or establish that any future counter passes.
- The round-29 summary demonstrates the existing control distinctions, but this seat did not independently rerun the frozen counter or verify control receipts beyond the inspected summary and named files.
