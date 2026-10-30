# MT40RegistryRows — evidence index (round 64, wave f)

Seat: MT40RegistryRows (mutation-tester, leaf). Milestone: falsify C2. Judged on: calibration.
Tip under test: `23b3fdb1a925129a9961cf551f6d40bf251602cb` (the measured tip).
Clone: `/fast/scratch/hyaku/kama-r64/f/MT40RegistryRows/clone` (`--shared` clone of the lane, one
mutant commit per mutant, each committed tip scored by the **unmutated** counter run from
`$D/tools/` with `--repo $D --tip <committed tip> --work <fresh scratch>`).

Tooling installed: none (python3 / git / pgrep / bash only, all preinstalled). No pacman
transaction (pacman is PAUSED host-wide). No package was installed or upgraded.

## Baseline (pristine tip, same PATH as every mutant run)

```
tip=23b3fdb1a925 population=12 covered=12/12 mismatches=0 pinned=13/13 deps_pinned=2/2 regress_flipped=12/12 printers_rejected=12/12 idle_ok=1 work_reuse_refused=1 closure_ptr=1 recon_mismatches=0 tally_disclosed=8/8 tally_selftest=1 sens_selftest=4/4 controls_rejected=120/120 errors=0 recon[closure_ptr=1,mismatches=0,maxN=64,met=True] tally[56:disclosed:shortcut+survivor,57:disclosed:shortcut+survivor,58:disclosed:survivor,59:disclosed:shortcut,60:disclosed:shortcut,61:disclosed:no-falsify,62:disclosed:no-falsify+shortcut,63:ok] families[canon=4/4,closure=5/5,flip=11/11,gate=16/16,idle=21/21,pattern=5/5,pins=5/5,printer=2/2,reconciler=11/11,registry=17/17,regress=11/11,selftest=1/1,tally=8/8,work=3/3] met=True
```
(`out/BASELINE-pristine-tip.out`, stderr in `out/BASELINE-pristine-tip.err`.)

## Files

| file | content |
|---|---|
| `out/BASELINE-pristine-tip.out/.err` | pristine-tip counter line + per-row stderr |
| `out/M01..M12-*.out/.err` | round 1: the nine mandated mutants + three extra registry edits |
| `out/M13..M22-*.out/.err` | round 2: sharper registry edits that isolate the deciding field |
| `out/M23..M30-*.out/.err` | round 3: the same, plus quote/order/note variants |
| `out/*.rerun.out/.err` | confirmation rerun of the context-sensitive mutants |
| `out/mutants.log`, `out/sweep.log`, `out/sweep2.log`, `out/sweep3.log`, `out/confirm.log` | the sweep transcripts |
| `out/pattern-uniqueness.txt` | the 12-pattern failing-mode probe transcript |
| `out/probe-*.txt` | raw probe outputs (bad-argument and work-stage failures) |

## Runner scripts (in the scratch root, copied here for reproducibility)

`mutants.py` (round 1), `mutants2.py` (round 2), `mutants3.py` (round 3), `sweep.py` (round 1
with the corrected PATH and a fresh work dir per mutant), `confirm.py` (confirmation rerun).
Each script: `git checkout <base> -- registry/capability-claims-r64.tsv` → apply one edit →
`git add -A` → `git -c user.name=seat -c user.email=seat@seat.invalid commit` → run the
unmutated counter → delete the work dir.

## Environment note (a flake I had to correct, reported as data)

My first sweep (round 0, `out/mutants.log`) inherited `PATH=/usr/bin:/bin` from a probe shell
in which I had set it. `tools/kama-llamacpp-live.py` resolves its server with
`shutil.which('llama-server')` (`tools/kama-llamacpp-live.py:2111`), and `llama-server` lives
in `/home/vgpnk/.local/bin/`, so every mutant run of that sweep showed
`row live-llamacpp-lifecycle: tip=false` and an extra `registry: outcome:live-llamacpp-lifecycle:false`
mismatch that was **not** caused by the mutation. All rounds reported here were re-run with
`PATH=/home/vgpnk/.local/bin:/usr/local/bin:/usr/bin:/bin`; in every round-1/2/3 run the
live-llamacpp row is `tip=true`, so the deciding field of each KILLED mutant is isolated.
The round-0 outputs are kept only in the scratch root and are not used for any verdict here.
