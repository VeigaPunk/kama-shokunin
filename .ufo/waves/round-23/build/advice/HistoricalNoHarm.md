# HistoricalNoHarm: round-23 historical no-harm baseline

Seat: CloseKama22.HistoricalNoHarm (leaf executor). Lane: kama-shokunin.
Base: master = `4fe9339f8fc3a4a4a479d9c938a850da12f1124d`. Fleet HEAD observed: `7f48c5ed7e72c98af3a0b14ef28a07aa923ba982`.

## Verdict

- FROZEN (committed `4fe9339f:tools/report-landing-audit.py`, blob `fcc255ce5115a749dfbd09cf992ba9851a2dc90a`) over real fleet history, rounds 10-22: exit 0, `status=clean`.
- CURRENT (lane working-tree auditor, uncommitted L1 edit) matches FROZEN byte-for-byte on stdout, stderr and exit for all three variants. Final gate: `no-harm-gate=PASS`, tested on blob `d577c5aa5fbedc633b0ca25aae640fbe7bfbfe18`, pre-run and post-run hash identical.
- Gate is not vacuous: in a throwaway clone with one lane-commit filter forced to `False`, the gate printed `no-harm-gate=FAIL` (see Sensitivity).
- Axes: (A) verdict parity on history: PASS. (B) stdout/stderr/exit byte parity: PASS. (C) gate sensitivity to a verdict-changing mutant: detects it. (D) rerun determinism (4 full runs): identical counts.

## Baseline counts (FROZEN; CURRENT identical)

Command: `python3 tools/report-landing-audit.py --rounds 10-22 --lane-repo <lane> --fleet-repo <fleet> --json` (and `--no-errata`, `--selftest`).

| run | exit | status | reports | defects | corrected | uncorrected | required | post_report | errata rows (unmatched / invalid) |
|---|---|---|---|---|---|---|---|---|---|
| history, errata on | 0 | clean | 13 | 9 | 9 | 0 | 54 | 5 | 9 (0 / 0) |
| history, `--no-errata` | 1 | failed | 13 | 9 | 0 | 9 | 54 | 5 | 0 |
| `--selftest` | 0 | n/a | n/a | n/a | n/a | n/a | n/a | n/a | `selftest cases=50 failed=0` |

`by_kind` (history): `landed-omitted=8`, `unresolved-full-hash=1`; `landed-unresolved`, `landed-ambiguous`, `landed-section-missing` = 0.

Per-round defects (all corrected by errata TSV line shown):
- r10 (1): landed-omitted `40660352d4a9eb00a5d6195f0f064f5c64618143` (line 11)
- r18 (3): landed-omitted `101f3991d3570bc9350fbf9c5561f4be1185699d` (8), `1c325b2e58fcfdc6761f645b44cedfb1d65243e6` (9), `c6dc46fabc51eb1dd0e91647f2e5e6b2b8ae4d6d` (10)
- r20 (5): unresolved-full-hash `0957ce619789d13d894ef21bc863486bcb35b56c` (3); landed-omitted `33a6777866d0f63d894ef21bc863486bcb35b56c` (4), `0957ce619789d13bb5779606078fa1498114d2c7` (5), `92b146253fd3a8c4bfade94c909dc63b13d6f4a8` (6), `846e366dc9dbac58463494a7e05ad060ae3ed3b0` (7)
- r19: required 8, post_report 4, defects 0. r21: required 7, post_report 1, defects 0. r11-r17, r22: defects 0.

Sums check: required 2+2+2+2+2+3+3+2+7+8+9+7+5 = 54; post_report 4+1 = 5; defects 1+3+5 = 9.

stdout sha256 (identical current/frozen): history `1ae84922500fe6e41ae72d6eb022fc72fbb7c60f63e9995487fde32bed46cc51`; no-errata `13b17b1cb1e5042388b4797a12d77bb358e068893a0c451342c7f83e86504cdd`; selftest `91c3a6c99522c42e695cee8482e1abb0dcac21a91f2229ecca30269536982169`. All stderr files are empty (sha256 `e3b0c442…b855`).

## Pins and the moving CURRENT

The lane auditor was edited while I worked. Each harness run pins its own snapshot:

| run | CURRENT blob | CURRENT sha256 (prefix) | gate |
|---|---|---|---|
| 1 (12:14) | `17a670a936e5…` | `d5da69cbc8df…` | PASS |
| 2 | `cbb67e0236cc…` | `61da3f2646cd…` | PASS |
| final | `d577c5aa5fbe…` | `d0a96599ed0b…` | PASS |

A live blob `c3eaa06…` was observed between runs 1 and 2 and was not gated. The gate must be re-run on the integrated candidate. It takes about 1 s.

FROZEN blob `fcc255ce…` and sha256 `09ecd63bdc3a…` are constant across runs. Lane master stays `4fe9339f`; the lane has no committed changes from me. `git status`: ` M tools/report-landing-audit.py` (L1, pre-existing) and `?? .ufo/waves/round-23/` (untracked; my output directory and this report).

Absolute counts above are for fleet HEAD `7f48c5ed`. After any fleet move, re-read `baseline-counts.txt`. The gate compares CURRENT and FROZEN on the same state, so it does not depend on the absolute numbers.

## Sensitivity (gate is not vacuous)

Throwaway clone of lane at base, one mutation at `tools/report-landing-audit.py:160`: `if author == ... ` changed to `if False and author == ...` (tag `D359`→`DBD6`). Harness run with `KAMA_LANE_REPO` pointing at it:
- current-history: exit 1, defects 9→1, required 54→0, errata_unmatched 8
- current-selftest: exit 1, `selftest cases=50 failed=14`
- `no-harm-gate=FAIL`, harness exit 1

The probe ran from a copy of the harness under `/tmp` and wrote nothing into the real output directory. The probe clone and its outputs were removed.

## Harness

`.ufo/waves/round-23/build/out/HistoricalNoHarm/run-historical.sh` (sha256 `1ebfc863e19eb2ccbfb9dc22359b2b00fef31929f5516dd829d564950dd43914`).
- Usage: `cd .ufo/waves/round-23/build/out/HistoricalNoHarm && ./run-historical.sh` (overrides: `KAMA_LANE_REPO`, `KAMA_FLEET_REPO`, `PYTHON3`).
- Snapshots CURRENT and extracts FROZEN into `mktemp` (removed on exit). Unsets inherited `GIT_*` for its own git calls. Runs six jobs in parallel, then diffs.
- Writes per run `NAME.{out,err,exit,sha256}`, `pins.txt`, `{history,no-errata,selftest}.vs-diff`, `baseline-counts.txt` ending in `no-harm-gate=PASS|FAIL`. Exit 0 iff PASS.
- Read-only: audited git calls are `log/cat-file/rev-parse/ls-tree/show/hash-object`; selftest uses only tempdir sandboxes. Lane/fleet tree and index were checked unchanged (`index.lock` absent).

## Not verified

- Fault grid (a)-(e) from the L1 probe. Not run by me. Real history does not exercise the new refusal paths (for example `citation ... names a ref`, non-UTF-8 output, `--no-lazy-fetch` on old git), so this gate gives no evidence about them.
- Any state after live blob `d577c5aa`. Any later auditor edit needs a re-run.
- Fleet and lane are read only; no commits, pushes or jj commands.

## Installs and updates

None. Tools used were existing: bash, git, python3, sha256sum, diff, awk.

## Files written

- `.ufo/waves/round-23/build/advice/HistoricalNoHarm.md` (this report)
- `.ufo/waves/round-23/build/out/HistoricalNoHarm/run-historical.sh`
- `.ufo/waves/round-23/build/out/HistoricalNoHarm/pins.txt`
- `.ufo/waves/round-23/build/out/HistoricalNoHarm/baseline-counts.txt`
- `.ufo/waves/round-23/build/out/HistoricalNoHarm/{current,frozen}-{history,no-errata,selftest}.{out,err,exit,sha256}` (24 files)
- `.ufo/waves/round-23/build/out/HistoricalNoHarm/{history,no-errata,selftest}.vs-diff` (3 files, all empty)
- Scratch clone `/tmp/kama-r23/HistoricalNoHarm`, at base `4fe9339`, clean; nothing applied.
- Temporary files, all removed: `/tmp/kama-r23-historical.*` (trap), `/tmp/kama-r23-sensitivity/`, `/tmp/kama-r23-prev-pins.*`, `/tmp/kama-r23-final-run.txt`.

## Corrections (appended after writing)

- Determinism: five full harness runs on real history (not four) produced identical counts.
- Read-only checks: I verified only that the lane `git status` is unchanged and that no fleet `.git/index.lock` exists. I did not snapshot the fleet's full status before the run. The harness is read-only by construction (see Harness).
