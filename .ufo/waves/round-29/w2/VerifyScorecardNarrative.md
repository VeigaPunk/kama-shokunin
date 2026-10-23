# VerifyScorecardNarrative — kama r29 w2 (seat kama-r29-w2-VerifyScorecardNarrative-4)

Scope: working-tree round-29 section of `/home/vgpnk/Projects/shokunin/kama-shokunin/SCORECARD.md`
(heading `## Round 29 — self-assessment evidence at writing (calibration); round-28 repairs (2026-10-23, attempt 1)`,
lines 1466–1504; C1 table row at line 1475): before/after receipt strings vs `before/c1-base.out` and a
fresh counter run; counting command vs preregistration; Planned row vs the claim record.
No lane file was modified; all runs in `/tmp/vsn-kama-r29-w2-VerifyScorecardNarrative-4/`.
Full copy: `.ufo/waves/round-29/w2/out/VerifyScorecardNarrative/report.md`.

## Verdict

The narrative is accurate in every checked field: the frozen counter (sha256 verified in three copies)
reproduces both receipts byte-for-byte at the pinned revisions, the counting command matches the
preregistration semantically, and the Planned row is consistent with the claim record (lesson
`corpus/lessons/round-29.md` limits/decisions). One minor deviation: both quoted receipt strings elide
the trailing `tip <12-hex>` field the counter always prints — under the stated byte-for-byte criterion
they are exact prefixes, not the full lines. Two informational notes on fresh-clone reproducibility.

## Findings

### F1 — minor: receipt cells are prefixes of the receipt lines, not byte-for-byte equal
- The C1 row (SCORECARD.md:1475) quotes before `…unresolved 11 met False` and after
  `…unresolved 0 met True`. The counter's stdout line always ends `… met <b> tip <12 hex>`
  (`count-c1.py:358-361`), and both receipt artifacts carry it:
  - `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/before/c1-base.out` line 1 ends
    ` tip 2aa46e2481d2` (plus a non-counter sentinel line `exit 0`);
  - `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/final/c1-513eba3b.out` ends
    ` tip 513eba3ba51a`.
- The preregistration's own documented line (`preregistration.json` `claims.C1.before.line`) includes
  ` tip 2aa46e2481d2`; I byte-compared it to `c1-base.out` line 1: identical (133 bytes, file adds `\n`).
- So the cells quote every field accurately but omit the 17-byte ` tip …` suffix in both cells. If the
  byte-for-byte wording is binding, the L1 should either append the tip field to both cells or drop the
  byte-for-byte wording. All quoted values themselves are correct.

### F2 — informational: `--tip refs/heads/master` only resolves on a clone of the actual remote
- Plain `git clone` of the LOCAL lane directory: the source HEAD is detached (at `513eba3`), so the clone
  creates no `refs/heads/master` and lands detached; the documented command then exits 2 with
  `could-not-evaluate: tip refs/heads/master unresolved` (observed).
- Plain `git clone` of origin (`https://github.com/VeigaPunk/kama-shokunin.git`): `ls-remote --symref`
  shows `ref: refs/heads/master HEAD`, the clone has `refs/heads/master`, and the documented command
  verbatim (`/usr/bin/python3 .ufo/waves/round-29/count-c1.py --tip refs/heads/master --out …`, run
  inside the clone) exits 0 and prints
  `statements 69 mismatched_at_base 11 append_only True valid_corrections 11 false_corrections 0 unresolved 0 met True tip 49f849f292c3`.
  "Fresh clone of the lane remote" is satisfied by the GitHub clone; local-path clones are not.

### F3 — informational: the pushed tip has advanced past the measured commit
- Origin `refs/heads/master` = `49f849f292c338f5e4e2cc8a60eb1372a8f40412`
  ("considerthese: 2026-10-23 daily reflection", committer 2026-10-23 09:21:19 -0300);
  `git merge-base --is-ancestor` confirms `513eba3` IS its ancestor.
- At that live tip the counter still reports every quoted field identically (only `tip` differs, per F1/F2
  mechanics). The row's "Measured commit" cell pins `513eba3…` with its own artifact, so the record is
  internally consistent and the claim remains met at the pushed tip. No defect; noted so no later reader
  expects a byte-identical fresh-clone line.

## Verifications (all passed)

- V1 Frozen bytes: `sha256sum` of `.ufo/waves/round-29/count-c1.py` in the lane, in my local clone, and in
  the GitHub clone = `fe11d599d064f5749c829394fc813f43921de2f9903e41c7217e3daa4b647383` (matches
  preregistration and the row's `fe11d599…7383`).
- V2 After receipt byte-for-byte: fresh run at the measured commit —
  `/usr/bin/python3 .ufo/waves/round-29/count-c1.py --repo <no-hardlinks clone> --tip 513eba3ba51a142c9936553e3a85918345eb5c4c --out fresh.json`
  → stdout `cmp` IDENTICAL to `final/c1-513eba3b.out` (`statements 69 mismatched_at_base 11 append_only
  True valid_corrections 11 false_corrections 0 unresolved 0 met True tip 513eba3ba51a`).
- V3 Before receipt byte-for-byte: fresh run at `--tip 2aa46e2…` → line 1 `cmp` IDENTICAL to
  `before/c1-base.out` line 1; that line byte-equals `claims.C1.before.line`. (`c1-base.out` additionally
  carries an `exit 0` sentinel line that is not counter stdout — cosmetic.)
- V4 Determinism corroboration: `final/c1-513eba3b-cleanenv.out` carries the same line plus annotation
  `env -i PATH=/usr/bin:/bin HOME=$HOME; clone of origin at 513eba3…; counter sha256 fe11d599…7383`.
- V5 JSON receipts agree with stdout and cells: `before/c1-base.json` (correction_rows 0, unresolved 11,
  met False, tip 2aa46e2…) and `final/c1-513eba3b.json` (correction_rows 11, valid 11, false [],
  unresolved 0, met True, tip 513eba3…); both carry `counter_sha256` = frozen hash.
- V6 Counting command vs preregistration: same interpreter `/usr/bin/python3`, same frozen script path,
  same `--tip refs/heads/master`, `--out` receipt; `--repo <fresh clone>` moved before `--tip`
  (argparse order-insensitive — my reproducing runs used exactly that order); `<fresh receipt.json>`
  renamed `<receipt.json>`; appended parenthetical counter sha verified full. Equivalent, not verbatim.
- V7 Commit-chain header facts: lane log order `827d136` (freeze) → `35b9018` (controls) → `513eba3`
  (data); HEAD `513eba3`; `shokunin.conf:52` is the kama row (`operability + calibration`), so the
  assigned-axis citation is accurate.
- V8 Working-tree shape: `git diff --stat 513eba3` = SCORECARD.md +40 (the evidence section incl. both
  receipt cells; zero `statements 69` occurrences in committed `513eba3:SCORECARD.md`) and SHONEN.md 1
  line (box-2 wording, per lesson decision line 118 — outside this item's scope). Consistent with
  "attempt-1 narrative leftovers under review".
- V9 Planned row vs claim record: "72 extractor misses" = lesson `corpus/lessons/round-29.md:54-56`
  (32 in SCORECARD lines 1-720 + 40 in 721-1441, none in SHONEN; 70 hold at W, 2 false — line 41 Q
  `file=yes`, line 901 Q `declared2048 = captured training2048`); 69+72=141 matches the section Limits
  "at least 141". "Line-824 '5 cases' prose mismatch" = base SCORECARD line 824 prose `selftest 5 cases`
  vs the tool printing 12 cases at W (lesson :57, ConfirmM07). Lesson decision :115 explicitly rejects
  counting either into C1 ("not in the frozen universe; disclosed as limits") — so Planned listing them
  as open calibration ground is consistent, not double-counted. Planned's KQ38 parenthetical matches
  `corpus/QUALITY.md:283`. "Work depth or adjacency (7)" matches held scores (depth 7, adjacency 7) and
  the calibration 7→7 no-promotion cell matches the preregistration (no promotion claimed).
- V10 Evidence pointers exist: `before/c1-base.out`, `final/c1-513eba3b.out`,
  `corpus/knowledge/self-assessment-at-writing.md`, `corpus/lessons/round-29.md`.

## Residual risk and gaps

- I did not re-verify the 11 correction rows' content sentence-by-sentence or the blame/W mapping
  (seats VerifyRow01..08, VerifyBaseMapping, VerifyAppendOnlyData cover those); the counter's own
  valid_corrections 11 / false_corrections 0 at the pinned tip is the only evidence I cite for them.
- The line-824 "12 cases" figure rests on the lesson's ConfirmM07 record; I confirmed the "5 cases"
  prose in the base blob but did not re-run the round-17 tool at W.
- SHONEN.md's single working-tree line change (box 2) was observed but not reviewed (other seat).

Tools installed: none. Scratch dir `/tmp/vsn-kama-r29-w2-VerifyScorecardNarrative-4` (clones + runs).
