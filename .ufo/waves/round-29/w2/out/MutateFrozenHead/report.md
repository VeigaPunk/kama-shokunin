# MutateFrozenHead — round-29 ATTEMPT 2, w2 (C1 correction rows)

Seat: `kama-r29-w2-MutateFrozenHead` (leaf). Claim attacked: C1 calibration — that the
frozen counter accepts exactly the 11 committed correction rows and rejects a correction
table that is not bound to the required heading or that carries an invented statement id.

## Detector identity

- Counter: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/count-c1.py`
  sha256 `fe11d599d064f5749c829394fc813f43921de2f9903e41c7217e3daa4b647383`
  (verified in the lane and in the scratch clone — identical bytes).
- Base `2aa46e2481d2ec41a7ee5ed793fc50ae967a6e5d`; detector tip
  `513eba3ba51a142c9936553e3a85918345eb5c4c`.
- Scratch clone: `/tmp/mfh-w2/repo` (full clone of the lane repo; clone `HEAD` =
  `513eba3b...`, worktree clean at start; local identity configured, gpg off).
- Invocation: `python3 .ufo/waves/round-29/count-c1.py --repo /tmp/mfh-w2/repo --tip <rev> --out <file>`.
  The counter reads committed objects only (`git --no-replace-objects`), so each mutation
  was committed inside the scratch clone (the lane was never touched).

## Baseline (pristine bytes)

Command: `--tip 513eba3b` → exit 0.

```
statements 69 mismatched_at_base 11 append_only True valid_corrections 11 false_corrections 0 unresolved 0 met True tip 513eba3ba51a
```

Receipt `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/w2/out/MutateFrozenHead/baseline.json`
(sha256 `f3c7a43907d44a4780593e4a12d07b71950e7fd32debb27f144c7dc0069dd504`):
`correction_rows 11, valid_corrections 11, false_corrections [], unresolved_ids [], met true`.
`SCORECARD.md` at `513eba3b` sha256 `a46bcc744032bbab69738e654c657f58ee45c2ee55c8ee84f800251ab922f7b9`;
`SHONEN.md` sha256 `1ff9e2f363baedc09ae913c2036d79b53dcd270c851419ef33b8dc337a6d3fb5`.

## Mutant A — one valid correction row moved to a differently-named heading

Edit: removed the last table row (`SA29:SCORECARD.md:P:17a7db7c81:0`, the `count-c1.py:384`
row) from under `## Round 29 — self-assessment corrections` and re-emitted it verbatim
under a new heading `## Round 29 — relocated row` appended at end of file. Same row text,
same columns; only the owning heading changed. Commit `cea85789864ff7c975e50542d03d09e8afe07e99`
(`SCORECARD.md` blob sha256 `c7602ff29e73ae0aab8943c0d2beb39bf3f93872b2a5d4526a21001734f2e286`);
exact diff in `mutA.diff` (remove 1 row line, add heading + row).

**Expected:** row not counted → `valid_corrections 10`, `unresolved 1`, `met False`.

**Actual** (exit 0):

```
statements 69 mismatched_at_base 11 append_only True valid_corrections 10 false_corrections 0 unresolved 1 met False tip cea85789864f
```

Receipt `mutA.json` (sha256 `d32284eac788448ecc547251a3600baf5d8261375eff7f610eabd02a33760b65`):
`correction_rows 10`, `valid_corrections 10`, `false_corrections []`,
`unresolved_ids ["SCORECARD.md:P:17a7db7c81:0"]`, `met false`, `append_only true`.

**Verdict: KILLED (defect detected). Agent's prediction confirmed exactly.** The moved row
is invisible to the row parser; the defect surfaces as the sid still sitting in
`mism - valid`, i.e. `unresolved`, never as a misclassified correction.

## Mutant B — 12th row with a made-up sid

Edit: reverted Mutant A (`git checkout 513eba3b -- SCORECARD.md`, sha256 back to
`a46bcc74...`), then appended exactly one fabricated row:

```
| SA29:SCORECARD.md:P:deadbeef00:0 | SCORECARD.md:9999 | P | `made-up-probe.md:1` | deadbeef | fabricated probe row | p:absent |
```

Commit `8fd2d9b2cfd47ff1c5138c3faf1bc0e7a13321ea` (`SCORECARD.md` blob sha256
`349776c9279f23088b4d9d591f75b674c975cc3d4073c1de8b050c41cfc03743`); `mutB.diff` shows the
net change versus `513eba3b` is exactly `+1` line at the end of the table. Diff vs Mutant A
is 1 insertion / 3 deletions (A's heading removed, row returned, fabricated row added).

**Expected:** fabricated row counted → `false_corrections 1`.

**Actual** (exit 0):

```
statements 69 mismatched_at_base 11 append_only True valid_corrections 11 false_corrections 1 unresolved 1 met False tip 8fd2d9b2cfd4
```

Receipt `mutB.json` (sha256 `ad35a25344f6171b556343778379590076ec82c30c3fee746c0e896cf8b210a2`):
`correction_rows 12`, `valid_corrections 11`, `unresolved 1`, `unresolved_ids []`, `met false`, and

```json
false_corrections: [{"observed": "p:absent", "sid": "SCORECARD.md:P:deadbeef00:0", "why": "not-a-mismatch"}]
```

**Verdict: KILLED (defect detected). Agent's prediction confirmed exactly.** The unknown sid
is parsed as a row, can never enter `valid` (it is not in `mism`), is reported as
`not-a-mismatch`, and adds one to `unresolved` on top of the 11 covered mismatches.

## What the counter actually does (targeted semantics)

Observations from execution (A, B) plus code lines (`count-c1.py`):

1. **Heading binding (executed, A).** `corrections()` toggles parsing only on lines starting
   `## ` and requires `line.strip() == "## Round 29 — self-assessment corrections"`
   (lines 268–272). Any other `## ` heading switches rows off; rows under it are never parsed.
   A relocated row is therefore indistinguishable from a missing row at the row level.
2. **Row syntax (executed, A/B).** A row is a `|`-line whose first cell, backticks stripped,
   starts `SA29:` (line 277). The sid is `first[5:]`, the observed value is the **last** column
   (line 278). Header/prose lines are ignored.
3. **Unknown sid (executed, B).** Parsed rows whose sid is not among `mismatched_at_base` are
   `not-a-mismatch` false corrections (line 318); every false row increments `unresolved`
   (line 327) independently of coverage of the real mismatches. `met` requires
   `unresolved == 0`, so a fabricated row cannot pass.
4. **Append-only is a prefix test.** `tip` bytes must start with the base blob; deletion or
   relocation inside the appended region does not break it — Mutant A still reports
   `append_only True`, and the `unresolved = mism - valid` branch is taken.
5. **`###` subheadings** do not reset parsing (`"### ".startswith("## ")` is False), so a row
   under a `###` subheading inside the section would still count. [INFERENCE — code-read,
   not executed; outside the assigned probe.]
6. **Untested boundary [INFERENCE, code-read]:** because rows outside the heading are never
   scanned, a valid row *duplicated* outside the heading while its in-section copy remains
   would leave `unresolved 0 / met True`; the counter flags stray rows only through the
   missing-sid path. This is a scanner-boundary observation, not a contract change, and was
   not exercised (third mutation outside the assigned probe).

## Restoration evidence

`git reset --hard 513eba3b` in `/tmp/mfh-w2/repo` →

- `git rev-parse HEAD` = `513eba3ba51a142c9936553e3a85918345eb5c4c`; `git status --porcelain`
  empty (0 lines).
- `sha256sum SCORECARD.md` = `a46bcc744032bbab69738e654c657f58ee45c2ee55c8ee84f800251ab922f7b9`
  (identical to pristine committed blob); `SHONEN.md` = `1ff9e2f3...d3fb5` (unchanged by all
  mutations — the probe only wrote SCORECARD.md).
- Same detector re-run → exit 0:
  `statements 69 mismatched_at_base 11 append_only True valid_corrections 11 false_corrections 0 unresolved 0 met True tip 513eba3ba51a`;
  `restored.json` sha256 `f3c7a439...dd504` — **byte-identical to `baseline.json`**.

## Lane untouched evidence

All writes were confined to `/tmp/mfh-w2/` and this report pair. Lane reads only
(`git log/show`, `sha256sum`, `git clone`, `grep`); no `git add/commit/checkout/reset` in the
lane. At end of run, lane: `HEAD` = `513eba3ba51a142c9936553e3a85918345eb5c4c`, counter sha256
still `fe11d599...7383`, worktree `SCORECARD.md` sha256 `c1bd9cb7f85414b8cf026cc7ddd17cbbc8d1f1937854b6e74f03169d9bcd8b02`
(pre-existing attempt-1 edits, exactly the leftovers described in the brief), and
`git status --porcelain` lists only those known leftovers plus this wave's `w2/` directory.

## Tooling

None installed (no uv/npx/binary changes); used system `python3` and `/usr/bin/git`.

## Artifacts

All under `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/w2/out/MutateFrozenHead/`:
`baseline.json`, `mutA.json`, `mutB.json`, `restored.json`, `mutA.diff`, `mutB.diff`,
`mutA-commit.txt`, `mutB-commit.txt`, this `report.md`.

## Bottom line

Both mutants were killed by the frozen counter with exactly the predicted receipts. The
heading-binding path and the unknown-sid path both execute, are conservative (never accept),
and gate `met`. No surviving mutant on the tested behaviors; the two untested boundary notes
above are documented as coverage observations only.
