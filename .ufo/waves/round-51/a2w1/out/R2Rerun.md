# R2Rerun — round 51 kama, C2 independent re-measurement (attack + frontier wave)

Verdict: **REPRODUCED — no defect found.** The frozen C2 counter (`tools/round51-append-audit-v6-check.py`, sha256 `254e63ba…9a1660`, matching the preregistration pin byte for byte) run twice at build tip 138af25b produced byte-identical met=True receipts matching the preregistered target (`fixture=1 lane=1 scenarios=9/9 met=True`); the base run at 57a2e25 reproduced the frozen do-nothing control (`met=False`, exit 1); and the v6 tool itself (`tools/append-only-audit.py`) run twice at 138af25b produced byte-identical exit-0 output with exactly the claimed counts (106 events, 166 disclosed lines in 51 disclosed events, 58 permitted lines).

## Method

- Scratch: `S=/fast/scratch/hyaku/kama-r51/R2Rerun`; `TMPDIR=$S`; one full clone: `git clone /home/vgpnk/Projects/shokunin/kama-shokunin $S/lane` (clone HEAD `4eca4892acca6ca4072a0a6fad577d0dd78a5dda`; `138af25b…` verified ancestor). Lane repo untouched (read-only); no subagents; no services started.
- Commits: build tip `T=138af25b963450b6520794995605fa7dbbcd87e0`, base `B=57a2e25bf702b03aa61f9265e968cf68058ecb82`, freeze `804bde75164444bdf0fe6783d7aa45774bf562bd`, measured receipt tip `73bf2a7a17104a62a3e442912c8776cbd8dedbd5`.

## 1. Counter identity vs preregistration

`sha256sum tools/round51-append-audit-v6-check.py`:

| source | sha256 |
|---|---|
| lane worktree | `254e63bab046428d4099d008929751701ed7b0600b96874760838a56eb9a1660` |
| clone @ 138af25b | `254e63ba…9a1660` |
| clone @ 804bde75 (freeze) | `254e63ba…9a1660` |
| clone @ 4eca4892 (HEAD) | `254e63ba…9a1660` |
| preregistration.json `claims[1].counter_sha256` | `254e63ba…9a1660` |

`git show 138af25b:tools/round51-append-audit-v6-check.py` vs lane worktree: `cmp` → identical. The frozen bytes are what ran.

## 2. Counter at build tip 138af25b — two runs, byte-identity

Commands:
```
python3 <lane>/tools/round51-append-audit-v6-check.py --repo $S/lane --tip 138af25b… --scratch $S/c2run1 --out …/out/R2Rerun/r2-c2-build-run1.out   # exit=0
python3 <lane>/tools/round51-append-audit-v6-check.py --repo $S/lane --tip 138af25b… --scratch $S/c2run2 --out …/out/R2Rerun/r2-c2-build-run2.out   # exit=0
```
- `cmp r2-c2-build-run1.out r2-c2-build-run2.out` → **byte-identical** (both sha256 `f0955565afdae09fefb12b8faec4f12aaa3d64370eedd18e086fc19fdcce4b00`).
- Receipt line 2: `fixture=1 lane=1 scenarios=9/9 lost=142 disclosed=166 met=True` — matches preregistration target `fixture=1 lane=1 scenarios=9/9 met=True`. All nine fixture scenarios `ok` (exit codes exactly as wanted, incl. `code-span-pipe`, `row-dropped`, `partial-disclosure`, `two-files-one-commit`).
- Lane leg: `tool v6 threshold 1 exit 0 events 106 disclosed_lines 166 permitted_lines 58; own lost lines in whole-file-graded files 142; ledger lines 166`.

Cross-check vs the build receipt `.ufo/waves/round-51/measured/c2-build.out` (taken at 73bf2a7a): `diff r2-c2-build-run1.out c2-build.out` shows only (a) the `tip=` line (73bf2a7a vs 138af25b) and (b) measure.sh's wrapper lines (the `$ python3 …` command echo and trailing `exit=0`). Every substantive line — the `fixture=…` verdict and all 13 `detail:` fixture/lane lines, numbers included — is byte-identical across 73bf2a7a → 138af25b. The v6 tool blob is also unchanged between those tips (below), so build-fix 2 did not move the measured claim.

## 3. Counter at base 57a2e25 — do-nothing control

```
python3 <lane>/tools/round51-append-audit-v6-check.py --repo $S/lane --tip 57a2e25… --scratch $S/c2base --out …/out/R2Rerun/r2-c2-base-run1.out   # exit=1
```
- Line 2: `fixture=0 lane=0 scenarios=0/9 lost=0 disclosed=0 met=False`.
- `diff <(head -2 r2-c2-base-run1.out) <(head -2 controls/base.c2.out)` → identical (`tip=…`, `fixture=0 lane=0 scenarios=0/9 lost=0 disclosed=0 met=False`); both files end `exit=1`. Kill rule not triggered (control is `met=False`, as required).
- The remaining detail lines differ from the frozen control only where each embeds its scratch path (`…/L1/c2base/r51c2-snq7y4ub/` vs `…/R2Rerun/c2base/r51c2-y68_i55l/`), which also changes the counter's fixed-width stderr truncation; the verdicts (`exit 0 (want 1) FAIL` etc.) match one for one. Byte-equality with the frozen control is impossible in principle for those lines; head-2 + exit were compared instead.

## 4. The tool itself (append-only-audit v6) — two runs, byte-identity

Blob continuity, `git show <rev>:tools/append-only-audit.py | sha256sum`:

| rev | sha256 |
|---|---|
| 57a2e25 (base) | `a3170a6fcbded95670e37750ab1ef72054e49ff83fc967e0c5f236ae10e205bd` (v5) |
| 804bde75 (freeze) | `a3170a6f…` (v5 — v6 not yet in tree, as the preregistration disclosure states) |
| 73bf2a7a (build) | `3d0eaa168c26f006da656e635995f14d43c57c3a9af43ddf1b954f5ca3070c11` (v6) |
| 138af25b (build-fix 2) | `3d0eaa16…` |
| clone HEAD 4eca4892 / worktree | `3d0eaa16…` |

Because the worktree bytes equal the 138af25b blob exactly, the assigned invocation runs the tip's own bytes:
```
python3 $S/lane/tools/append-only-audit.py --repo $S/lane --to 138af25b…   # run1 exit=0, run2 exit=0, stderr empty (0 bytes) both
```
- `cmp r2-aoa-138af25b-run1.out r2-aoa-138af25b-run2.out` → **byte-identical** (both sha256 `d84a9c69986b185c8d38086a8cc20a2909cc8687b48a8125e6975f04c35bccbd`).
- Summary line: `commits=341 files=96 events=106 restored=19 partial=0 unrestored=0 ungraded=36 disclosed=51 permitted_lines=58 disclosed_lines=166 bad_disclosures=0 ungraded_lines=205 regressed=0 vanished=0 unmatched=0 binary=0 bad_declarations=0`; `grep -c '^event '` → 106. Matches the build claim exactly: 106 events, 166 disclosed lines in 51 disclosed events, 58 permitted lines, exit 0, unrestored 0.

## Findings

None in scope. The re-measurement reproduces both legs of the C2 claim with no discrepancy: determinism (byte-identical reruns of both counter and tool), the preregistered target at 138af25b, the declared counts, and the base do-nothing control. No tooling was installed or upgraded (no pacman, no uv, no binaries); only `git`, `python3`, `cmp`/`diff`/`sha256sum` were used. No llama-server was started by this seat; `pgrep -af llama-server` at finish returned no processes at all.

## Residual risk / verification gaps

- I did not re-run C1 (`round51-replay-exe-audit.py`) — out of this seat's assignment; its build receipt (met=True) is taken as reported, not re-verified here.
- Counter-vs-frozen-control byte comparison is necessarily partial (scratch-path strings embedded in `detail:` stderr excerpts); head-2 + exit compared, verdict lines matched one for one.
- The counter receipts contain no timestamp or entropy source, so byte-identity here is expected, not merely observed once; still, only two reruns were taken, not a distribution.

## Files written (all under /home/vgpnk/Projects/shokunin/kama-shokunin)

- `.ufo/waves/round-51/a2w1/out/R2Rerun.md` (this report)
- `.ufo/waves/round-51/a2w1/out/R2Rerun/r2-c2-build-run1.out` (counter, 138af25b, run 1, exit 0)
- `.ufo/waves/round-51/a2w1/out/R2Rerun/r2-c2-build-run2.out` (counter, 138af25b, run 2, exit 0; byte-identical to run 1)
- `.ufo/waves/round-51/a2w1/out/R2Rerun/r2-c2-base-run1.out` (counter, 57a2e25, exit 1, met=False)
- `.ufo/waves/round-51/a2w1/out/R2Rerun/r2-aoa-138af25b-run1.out` (tool, run 1, exit 0)
- `.ufo/waves/round-51/a2w1/out/R2Rerun/r2-aoa-138af25b-run2.out` (tool, run 2, exit 0; byte-identical to run 1)
- `.ufo/waves/round-51/a2w1/out/R2Rerun/frozen-controls-base.c2.out` (copy of cited control)
- `.ufo/waves/round-51/a2w1/out/R2Rerun/measured-c2-build.out` (copy of cited build receipt)

Scratch `/fast/scratch/hyaku/kama-r51/R2Rerun` removed after all evidence was copied out.
