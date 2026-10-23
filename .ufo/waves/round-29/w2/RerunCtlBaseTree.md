# RerunCtlBaseTree — re-execution of control CtlBaseTree (C1 pre-data controls)

Seat `kama-r29-w2-RerunCtlBaseTree`, kama lane round 29 wave 2, 2026-10-23.
Claim served: **C1 (calibration), pre-data controls**.
Full report + evidence: `.ufo/waves/round-29/w2/out/kama-r29-w2-RerunCtlBaseTree/report.md`.

## Result

The committed control reproduces exactly; the expected `valid 6 false 4 unresolved 9 met False`
is confirmed.

```text
statements 69 mismatched_at_base 11 append_only True valid_corrections 6 false_corrections 4 unresolved 9 met False tip 93efe2d45da5
exit=0
```

- Counter: lane `.ufo/waves/round-29/count-c1.py`, sha256
  `fe11d599d064f5749c829394fc813f43921de2f9903e41c7217e3daa4b647383`, verified before the first
  run and after all arms (unchanged; never modified or copied into a scored tree).
- vs recorded `.ufo/waves/round-29/controls/CtlBaseTree/counter.out`: **byte-identical**
  (140 B, sha256 `89c459b0206c10e6178d4fb53ac994250bc791af06ca4a08270dac9512519db1`).
- `receipt.json` (`fd9662f4…`), `change.diff` (`ac2fccb9…`), `base_rows.txt` (`7d52c27a…`):
  **byte-identical** to the recorded files. The scored commit reproduced too:
  `93efe2d45da5ed1f72455f16a97107ee6a151592`, tree `be55ce978a804b5752e599b0a7869ed4cf1442d9`,
  parent `827d136546b85059a984b34970f5b493d9a71290`; tip `SCORECARD.md` blob `e98c13c7…`.
- Control outcome **refused** (`met False`): correct behaviour for a policy that checks the base
  tree instead of the writing revision `W`.

## Reproduced pieces

Fresh clone of the lane at `827d1365…1290`; ran the recorded policy script
`controls/CtlBaseTree/base_tree_check.py` (path-free, `argv[1]` = repo) → 10 base failures,
byte-identical to the recorded pre-scoring `base_rows.txt`, and field-for-field identical to
`base_failures.jsonl`. Composed the `SCORECARD.md` append from those rows → blob `e98c13c7…`
(the recorded tip blob, 106 061 B = base 104 553 B + 1508 B); committed with the recorded
metadata to reproduce `93efe2d45da5…`; scored with the frozen counter.

Independent recompute at BASE `2aa46e24` (git `cat-file`/`grep` + `hashlib`, no policy code)
confirms all 10 observed values: `kama-probe.sh` md5 `e8bfdcac…`, 1138 newlines unterminated;
`test-snapshot.sh` md5 `3116d459…`; `SKILL.md` 1230 newlines terminated; the four `P` paths
(`MISSION.md`, `round-17-verifier-spotcheck.md`, `.ufo/reports/round-25/kama.md`,
`count-c1.py`) absent at base; the `snapshot=…` span and `baseline=VALID rejected=3/3` absent
at base (they exist only in freeze-added round-29 files).

## Findings for the L1

1. **No substantive defect.** Recorded evidence for CtlBaseTree is faithful and reproducible
   end-to-end from a fresh clone, including the exact commit hash and all four artifacts.
2. **Arithmetic confirmed** against the receipt: 11 `W`-mismatches ∩ 10 base failures = 6 valid;
   base-only = 4 false rows (`H:cda32b698f`, `N:cda32b698f`, `H:f4c42debcc`, `N:54da210e98`,
   each `holds_at_W=True`, counter `why: not-a-mismatch`); `W`-only = 5 missed
   (`Q:0ccd533544`, `Q:4c5d902830`, `Q:4f8083e30a`, `Q:f1021c03db`, `Q:f4c42debcc:2`);
   `unresolved 9 = 5 + 4`. The 6 valid rows are coincidental constant-string matches, not
   partial correctness.
3. **Wording nuance, harmless.** Checks are pinned to base `2aa46e24`; the scored commit is
   parented on freeze `827d1365` (the freeze commit added the round-29 files, which is exactly
   why two `Q` spans are present at freeze but absent at base). An extra arm parented at
   `2aa46e24` (tip `c86e624e2d51`) gives the identical counter line and receipt fields except
   `tip`, so the measured counts do not depend on the clone point.
4. **Limit.** The recorded claim "counter not run before scoring" is process testimony; what is
   verified is that the policy emits its rows from the base tree alone and reproduces without
   consulting the receipt.

## Restoration and bounds

Scratch clones retained with scored commits: `/tmp/kama-r29-w2-RerunCtlBaseTree/repo`
(`93efe2d4…`, clean) and `/tmp/kama-r29-w2-RerunCtlBaseTree/repo-base` (`c86e624e…`, clean).
Lane HEAD `513eba3b…` and `git status --porcelain` identical to session start; counter and
control artifacts unchanged. No tracked lane file, lane index, jj state, fleet file,
`.ufo/state/`, watchdog log or `MANIFEST.json` written; the only lane writes are this report
and `out/kama-r29-w2-RerunCtlBaseTree/`. No pacman, no tools installed or updated.

## Evidence paths

Mine: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/w2/out/kama-r29-w2-RerunCtlBaseTree/`
(`report.md`, `evidence-manifest.txt`, `evidence/`).
Recorded: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/controls/CtlBaseTree/`
(`counter.out`, `receipt.json`, `change.diff`, `base_rows.txt`, `base_failures.jsonl`, `REPORT.md`).
