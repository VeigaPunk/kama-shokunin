# RerunCtlSourceBounds — independent re-execution of control CtlSourceBounds

- Claim served: **C1 (calibration) — pre-data controls**, kama lane round 29, wave 2.
- Seat: `kama-r29-w2-RerunCtlSourceBounds`. Date: 2026-10-23.
- Lane: `/home/vgpnk/Projects/shokunin/kama-shokunin` (read-only except this wave's report paths).
- Item: `.ufo/waves/round-29/controls/items/CtlSourceBounds.md`; committed artifacts:
  `.ufo/waves/round-29/controls/CtlSourceBounds/`.

## Verdict

The committed control reproduces **exactly**. Expected detector result (from the item):
`valid 9 false 7 unresolved 9 met False` — **confirmed**.

Mutant-arm counter line (my run, lane counter, sha256 `fe11d599…7383`):

```text
statements 69 mismatched_at_base 11 append_only True valid_corrections 9 false_corrections 7 unresolved 9 met False tip af96283389de
exit=0
```

- Byte-for-byte vs `.ufo/waves/round-29/controls/CtlSourceBounds/counter.out`:
  **IDENTICAL** (141 B, sha256 `8aa1b087da51988a314f4fc23b73c1e308cec0cf2ae4a2f46d7c18587dd299e2`).
- `receipt.json` (`dcf521fe…679d6`), `pristine-receipt.json` (`e6c7e3e7…615d8`),
  `restored-receipt.json` (`d24af203…64f9f`) and `change.diff` (`34f45afc…51adb`, 1748 B):
  **all byte-identical** to the recorded files.
- Control outcome: **refused** (`met False`). Mutation-frame verdict: **inconclusive** because the
  pristine baseline (freeze tip `827d1365`) also fails the target (`unresolved 11`, `met False`);
  this matches attempt-1's own classification and is not a killed-mutant claim. The counter was not
  modified.

## What was executed

1. Fresh clone, attempted exactly as committed (CONTEXT procedure step 1):

```bash
env -u GIT_DIR -u GIT_WORK_TREE -u GIT_INDEX_FILE \
  git clone -q /home/vgpnk/Projects/shokunin/kama-shokunin \
  /tmp/kama-r29-w2-RerunCtlSourceBounds/repo
git -C /tmp/kama-r29-w2-RerunCtlSourceBounds/repo checkout -q -B ctl 827d136546b85059a984b34970f5b493d9a71290
```

Clone HEAD `827d1365…1290`, tree `efe74520595f60b69e33b79b378348fe69a31043`, worktree clean.
`SCORECARD.md` sha256 `7af59cc0…2d1db`, `SHONEN.md` `1ff9e2f3…d3fb5` — identical to base
`2aa46e24…6e5d` blobs (verified by `git cat-file blob`).

2. Policy applied from a **path-adjusted copy** of the committed `source-policy.py`
   (sha256 `9e51c98a…5163`). The only change is the two path constants; logic is byte-identical:

```diff
-ROOT = Path('/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/controls/CtlSourceBounds')
-REPO = '/fast/scratch/hyaku/kama-r29/ctl/CtlSourceBounds/repo'
+ROOT = Path('/tmp/kama-r29-w2-RerunCtlSourceBounds/policy-out')
+REPO = '/tmp/kama-r29-w2-RerunCtlSourceBounds/repo'
```

Policy run: `source-only extracted 69 statements; predicted 16 false`. All five generated
artifacts are byte-identical to the recorded ones:

| artifact | sha256 | vs recorded |
|---|---|---|
| `source-statements.json` | `b4dcb528…f01a` | identical |
| `source-hashes.json` | `ac6dd955…e3c3` | identical |
| `predictions.json` | `f1a477ff…e22e` | identical |
| `policy-hashes.json` | `cc047e95…a4d` | identical |
| `correction-rows.md` | `c0af843f…855` | identical |

3. Rows appended to the clone's `SCORECARD.md`; resulting sha256
   `f3f5a351f4248e061769668d62c1773bacc18a5b3b3cb03ab1f1c9f2af9df17b` (matches recorded
   `policy-hashes.mutated_scorecard_sha256`); `SHONEN.md` unchanged (`1ff9e2f3…`).

4. Commit reproduced with the metadata read from the surviving attempt-1 clone
   (`/fast/scratch/hyaku/kama-r29/ctl/CtlSourceBounds/repo`), not guessed:

```bash
GIT_AUTHOR_NAME=ctl GIT_AUTHOR_EMAIL=ctl@local GIT_AUTHOR_DATE='1792753374 -0300' \
GIT_COMMITTER_NAME=ctl GIT_COMMITTER_EMAIL=ctl@local GIT_COMMITTER_DATE='1792753374 -0300' \
git -c user.name=ctl -c user.email=ctl@local commit -qam 'source-text-only prediction policy'
```

Result exactly `af96283389ded62899b386fdc988bd3ddcbca9e2`, parent `827d1365…`,
tree `410fb6f8d771558caa812dde93711e15cfb9e065`, author/committer `ctl <ctl@local> 1792753374 -0300`.
`git diff 827d1365 ctl` is 1748 B, sha256 `34f45afc…51adb` — identical to recorded `change.diff`.

5. Lane counter run (sha256 checked `fe11d599…7383` before the first run and again after all
   arms; unchanged):

```bash
timeout 300 /usr/bin/python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/count-c1.py \
  --repo <scratch clone> --tip <ctl|restored|ref> --out <fresh receipt>
```

Three phases, all exit 0; receipts and counter outputs compared byte-for-byte:

| phase | tip | counter line | counter.out vs recorded | receipt vs recorded |
|---|---|---|---|---|
| pristine | `827d136546b8` | statements 69 mismatched_at_base 11 append_only True valid_corrections 0 false_corrections 0 unresolved 11 met False tip 827d136546b8 | **identical** (142 B, `ddbd98d4…5782`) | **identical** (`e6c7e3e7…`) |
| mutated | `af96283389de` | statements 69 mismatched_at_base 11 append_only True valid_corrections 9 false_corrections 7 unresolved 9 met False tip af96283389de | **identical** (141 B, `8aa1b087…99e2`) | **identical** (`dcf521fe…`) |
| restored | `6df2824e7e43` | statements 69 mismatched_at_base 11 append_only True valid_corrections 0 false_corrections 0 unresolved 11 met False tip 6df2824e7e43 | **identical** (142 B, `8cfd3c33…04d7`) | **identical** (`d24af203…`) |

The restored commit was reproduced too: branch `restored` off `af962833`, `SCORECARD.md` checked
back to `827d1365` bytes, commit `restore exact pristine source bounds bytes` at
`1792753400 -0300` → `6df2824e7e43a74809aed51570171ed308818367`, tree
`efe74520595f60b69e33b79b378348fe69a31043` (identical to attempt-1).

6. Extra base-point arm (literal item wording "FRESH clone at 2aa46e24"): clone checked out
   `2aa46e2481d2ec41a7ee5ed793fc50ae967a6e5d`, same path-adjusted policy, generated artifacts
   again identical (`predictions.json` `f1a477ff…`, `correction-rows.md` `c0af843f…`), commit
   `f341be9da6924cc1f59afe77812aa62ea902715b`. Counter:

```text
statements 69 mismatched_at_base 11 append_only True valid_corrections 9 false_corrections 7 unresolved 9 met False tip f341be9da692
```

Receipt fields `statements`, `mismatched_at_base`, `append_only`, `valid_corrections`,
`unresolved`, `met`, `by_class`, `false_corrections`, `mismatches`, `unresolved_ids`, `target`,
`base` all match the recorded receipt; only `tip` differs (expected, different parent).

## Findings

**F1 — No substantive defect. The control's recorded evidence is faithful and reproducible.**
Commit hash, tree, diff bytes, policy outputs, counter lines and receipts all match exactly, from a
fresh clone. The recorded line equals the expected `valid 9 false 7 unresolved 9 met False`.

**F2 — Minor procedural observation (capture format, not the measured line).** The recorded
`counter.out`, `pristine-counter.out` and `restored-counter.out` were not produced by the literal
CONTEXT step-3 shell command; they were produced by attempt-1's `score-probe.py`, whose log
composition is `stdout + b"\n" + b"exit=N\n"`. That inserts one blank line before `exit=N`.
The literal command gives 140 B (mutated) / 141 B (pristine) / 141 B (restored) versus recorded
141 / 142 / 142 B; `cmp` differences start exactly at the inserted byte and are a one-byte length
delta. Composing the log the way `score-probe.py` does reproduces all three recorded `.out` files
**byte-identically**. No effect on the counter line, the receipt, or the verdict. `REPORT.md`
already describes `score-probe.py` as capture-only; the item/CONTEXT procedure text simply differs
from the capture actually used.

**F3 — Why 9 rows are "valid" without any observation (disclosed limit, not a defect).** For
P/Q statements the counter's failure strings are constant (`p:absent`, `q:no-artifact`), and the
policy guessed exactly those strings for statements that happened to be mismatches. The receipt
shows the 7 false corrections are Q rows on statements that hold
(`SCORECARD.md:Q:cda32b698f:0`, `…:f4c42debcc:1`, `…:bb5ad45ac4:0`, `…:6c62ea022e:0`,
`…:a0a60b0a90:0`, `…:7039180776:0`, `…:fd9d76ceed:0`), and the 2 missed mismatches are
`SCORECARD.md:Q:a7e98b1030:0` and `SCORECARD.md:Q:f1021c03db:0` → `unresolved = 2 + 7 = 9`.
This matches `controls/SUMMARY.md` and attempt-1's disclosure ("even if it meets by coincidence");
the counter validates the **selection** of false statements (and exact observed values for
H/N/C/T), not the provenance of the string.

**F4 — Clone-point wording is broader than the committed procedure.** The item says "fresh clone
at 2aa46e24"; CONTEXT step 1 and the committed `commit.json` use the freeze commit
`827d1365…` as the parent. Both were run. Because `SCORECARD.md`/`SHONEN.md` bytes are identical
at `2aa46e24` and `827d1365` (`7af59cc0…`, `1ff9e2f3…`), the mutant bytes and every counter count
are invariant; only the tip differs. For exact reproduction of the recorded artifacts the
`827d1365` parent is required; the base arm yields the same measured values.

## Restoration evidence

The scratch copy was treated as restorable even though it is disposable.

- `repo` (HEAD `restored`): `SCORECARD.md` `7af59cc0…2d1db`, `SHONEN.md` `1ff9e2f3…d3fb5`,
  worktree clean; scored commits retained: `ctl` = `af962833…`, `restored` = `6df2824e…`.
- `repo-base` (HEAD `ctl2` = `f341be9d…`): `SCORECARD.md` `7af59cc0…2d1db`,
  `SHONEN.md` `1ff9e2f3…d3fb5`.
- Before → after restoration of the mutated file:
  `f3f5a351…` → `7af59cc0…` (mutant commit still holds `f3f5a351…`).
- Counter sha256 `fe11d599d064f5749c829394fc813f43921de2f9903e41c7217e3daa4b647383` before and
  after all runs.
- No tracked lane file, lane index, jj state, fleet file, `.ufo/state/`, watchdog log or
  `MANIFEST.json` was written. Only reads of the lane; the only lane writes are the two assigned
  wave-2 report files. All scratch work is under `/tmp/kama-r29-w2-RerunCtlSourceBounds/`.
- Tool installs/updates: **none** (no pacman, uv, npx or binaries needed).

## Evidence (absolute paths)

Recorded inputs: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/controls/CtlSourceBounds/`
(`counter.out`, `receipt.json`, `pristine-*`, `restored-*`, `change.diff`, `source-policy.py`,
`predictions.json`, `correction-rows.md`, `policy-hashes.json`, `source-statements.json`,
`source-hashes.json`). Counter: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/count-c1.py`.

My evidence: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/w2/out/kama-r29-w2-RerunCtlSourceBounds/`
- `evidence/counter.out` (mutated, wrapper format, 141 B, `8aa1b087…`) — matches recorded.
- `evidence/pristine-counter.out` (142 B, `ddbd98d4…`) — matches recorded.
- `evidence/restored-counter.out` (142 B, `8cfd3c33…`) — matches recorded.
- `evidence/canon-counter.out`, `evidence/canon-pristine-counter.out`,
  `evidence/canon-restored-counter.out` — literal CONTEXT step-3 format (140/141/141 B); the only
  difference from the recorded files is the wrapper's extra newline (F2).
- `evidence/aux-mistaken-pristine-slot-tip-ctl-mutant.out` — the mutant-tip log that initially
  occupied my pristine slot before the explicit-hash rerun; kept for transparency (same bytes as
  `counter.out`).
- `evidence/mutated-receipt.json`, `evidence/pristine-receipt.json`,
  `evidence/restored-receipt.json`, `evidence/base-arm-receipt.json` — all identical to recorded
  except the base arm's `tip`.
- `evidence/base-arm-counter.out` — base-point arm line (`tip f341be9da692`).
- `evidence/change.diff` (1748 B, `34f45afc…`) — identical to recorded.
- `evidence/policy-out/`, `evidence/policy-out-base/` — regenerated policy artifacts.
- `evidence/policy-path-adjusted.py`, `evidence/policy-base-path-adjusted.py`,
  `evidence/wrap-run.py`, `evidence/policy-run.out`, `evidence/policy-base-run.out`.
- `evidence-manifest.txt` — sha256 of every evidence file.

Scratch clones: `/tmp/kama-r29-w2-RerunCtlSourceBounds/repo` (freeze parent, restored tip),
`/tmp/kama-r29-w2-RerunCtlSourceBounds/repo-base` (base parent, `ctl2`).
