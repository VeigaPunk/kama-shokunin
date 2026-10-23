# RevAdmissionEvidence — wave-2 review of the two decisive artifacts

Report: .ufo/waves/round-31/w2/out/RevAdmissionEvidence/report.md
Receipts: .ufo/waves/round-31/w2/out/RevAdmissionEvidence/ (frozen-counter re-runs, base problem
list, reproduction JSONs, original artifact copies).

## Verdicts

- **no-op claim supported: YES.** `w1/out/CriticClaimSize/c1-noop.json` reads `registered 12
  counted 12 target 12 met True not-counted []` at fixture tip `e722ead7` (lane base `0e6f8ed6` +
  one fixture commit). I re-ran the unmodified frozen `count-c1.py` (sha256 verified) on that
  commit's objects: identical summary, all 12 rows `counted=true, reasons=[]`, live
  `{status 200, slot_task}` each. What makes the rows counted: **only `id` uniqueness**. The 12
  registry rows are byte-identical modulo `id` (`distinct-minus-id = 1`): `param "max_tokens"`,
  `sent 1`, `slot {n_predict: 1}`, all citing one source `S990`. Because `base_body` itself sends
  `max_tokens: 1`, every row request equals the base request and the live check re-observes the
  base's own stored `n_predict=1`; the KQ38 slot rule passes vacuously since `n_predict ≠
  max_tokens`. SKILL cells, `param`, `sent`, `outcome`, and `source` need not be distinct.
  Met-on-counter, zero new observations → the C1 not-admitted verdict stands on this evidence.

- **collapse claim supported: YES.** `controls/RefRepair/receipt.txt` reads verbatim
  `rows 28 base_mismatched 13 exempt 1 valid_corrections 10 false_corrections 3 unresolved 3
  append_only True met False tip 0dafe9e601e3` and `ARM-FAILED-THE-TARGET`. I independently
  regenerated the arm (one `CR31:` correction per listed problem, verbatim rid/class/observed):
  same summary on tip `7f434544`, and `--list` shows all three `row=C1 class=p1` corrections
  `ok=False` while the ten unique-key corrections are `ok=True`. The `(row, class)` collapse is in
  the counter's code (`problem_by_key` + `len(by_key[key]) == 1`, L257-265): three distinct
  population rows (SCORECARD.md lines 266/320/379, rounds 11/12/13) share the bare Claim cell `C1`
  and all fail `p1`, so their corrections share one key and are all false; `unresolved` counts the
  three distinct problem rows. Two precision notes for the L1: every correction on a shared key is
  false — not just "the second" as the counter docstring states; and the collapse is at the
  correction-key level (the problem list retains all three rows, hence `unresolved 3`). Since
  `met` requires `unresolved == 0`, the C2 counter makes the claim unreachable while the three
  bare-C1 rows remain failing — verified at `b4f3edc0` and `382d11b2` (`valid 10 false 0
  unresolved 3 met False`, verbatim). The not-admitted verdict is consistent; the defect is the
  frozen counter's, and the receipt is honest.

## Commands run (all exit 0 unless noted)

sha256sum both frozen counters (digests match preregistration); `git rev-parse HEAD` = bda324bb
(jj snapshot past dispatch tip); `git bundle list-heads` + clone/fetch of `scratch-fixtures.bundle`
(bundle is a delta needing lane base objects; direct clone exits 128, fetch-into-lane-clone works);
`git show`/`git log` on fixture commits; `count-c2.py --list` at `0e6f8ed6` (13 problems verbatim);
`sed -n` over `git show` for lines 255-268/316-322/375-381 of base SCORECARD.md; `gen_corr.py` (my
scratch script appending the 13 corrections, committing, re-running the counter); `count-c2.py` at
`b4f3edc0` and `382d11b2`; `count-c1.py` full live runs at `e722ead7` and `382d11b2` (own server on
47900-47999, own start/stop — `pgrep -fl llama-server` exit 1 afterward); `count-c1.py --explain
NOOP-01` → `200, n_predict = 1`. No tools installed. No tracked lane file modified; all writes under
`.ufo/waves/round-31/w2/out/RevAdmissionEvidence/` and `/tmp/kama-r31w2/RevAdmissionEvidence/`.

## Not established

The arm's exact appended bytes are unverifiable (scratch tree not retained; outcome reproduced by
independent construction). The collapse was tested at the arm base and two landed tips only. The 17
landed counted rows' quality is a different seat's item (RevCounterFair F1/F2). C3 untouched.
