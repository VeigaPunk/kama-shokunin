# R1Rerun2 — C1 independent re-measurement

**VERDICT: C1 CONFIRMED.** Independent re-run on a fresh full clone reproduces `bind=1 teardown=1 newrow=1 bound=3/3 met=True` at the build tip `97c864bead3ee4a2f629574e77263d33834ec98a` (twice, identical verdicts) and `bind=0 teardown=0 newrow=0 bound=0/3 met=False` at base `26ecba64ad6fb571d09074b07202d1618a46ecd1`. No defects found in the counter or the measured claims.

## Setup verification

- Clone: `git clone -q /home/vgpnk/Projects/shokunin/kama-shokunin /fast/scratch/hyaku/kama-r50/R1Rerun2/lane` — full clone, **not** `--shared`. Verified standalone: no `.git/objects/info/alternates` file; `count-objects -v` reports `in-pack: 20619`.
- Tip and base both present in the clone (`git cat-file -t` = `commit` for each).
- Counter bytes verified frozen: `sha256sum $S/lane/tools/round50-replay-bind-audit.py` = `ff6ac2ace541ea35a4d240ceebb019653c11a2a08c025e514770f3f94a9c5e89`, identical to the frozen lane copy and equal to `counter_sha256` in `.ufo/waves/round-50/preregistration.json` (claim C1).
- Clone HEAD was `3b79eaddf38246c637cc7ba1a94ab363422876b6` (lane has advanced past the build); `--tip` pins the measurement commits explicitly.

## Commands and receipts

Command shape (all three runs):
```
S=/fast/scratch/hyaku/kama-r50/R1Rerun2; export TMPDIR="$S"
python3 $S/lane/tools/round50-replay-bind-audit.py --repo $S/lane \
  --tip <commit> --scratch $S \
  --out /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/R1Rerun2/<file>
```

### Build tip 97c864bead3ee4a2f629574e77263d33834ec98a — run 1 (exit 0, 19.0 s)

`c1-build-1.out`:
```
tip=97c864bead3ee4a2f629574e77263d33834ec98a
bind=1 teardown=1 newrow=1 bound=3/3 met=True
detail: counter vocabulary: 512 tokens from its own download
detail: bind b1: pid 2352869 port 40659 exe+listen+tree+env+mapped ok, child_pid joined, mapping dev 103:05 inode 20620058 recorded, nonce 'kama witness 6dda0b5d62c293e9' round-tripped
detail: bind b2: pid 2370539 port 46247 exe+listen+tree+env+mapped ok, child_pid joined, mapping dev 103:05 inode 1082789435 recorded, nonce 'kama witness 87f408a2afb33636' round-tripped
detail: bind b3: pid 2388866 port 34725 exe+listen+tree+env+mapped ok, child_pid joined, mapping dev 103:05 inode 813632090 recorded, nonce 'kama witness 6026e8d69fa485aa' round-tripped
detail: teardown: invoker SIGKILLed with 3 descendants; after 0.10 s alive [] port refuses ok
detail: newrow: 3 rows new since base; 1 name proc_pid_maps(5): ['| S496 |']
```

### Build tip 97c864bead3ee4a2f629574e77263d33834ec98a — run 2 (exit 0, 16.7 s)

`c1-build-2.out`:
```
tip=97c864bead3ee4a2f629574e77263d33834ec98a
bind=1 teardown=1 newrow=1 bound=3/3 met=True
detail: counter vocabulary: 512 tokens from its own download
detail: bind b1: pid 2655182 port 40013 exe+listen+tree+env+mapped ok, child_pid joined, mapping dev 103:05 inode 143900008 recorded, nonce 'kama witness a7aeaed6210c8e0a' round-tripped
detail: bind b2: pid 2670926 port 38189 exe+listen+tree+env+mapped ok, child_pid joined, mapping dev 103:05 inode 1151777000 recorded, nonce 'kama witness 2ab79a56044d493d' round-tripped
detail: bind b3: pid 2690167 port 33915 exe+listen+tree+env+mapped ok, child_pid joined, mapping dev 103:05 inode 1955678163 recorded, nonce 'kama witness 9d029936cad35257' round-tripped
detail: teardown: invoker SIGKILLed with 3 descendants; after 0.10 s alive [] port refuses ok
detail: newrow: 3 rows new since base; 1 name proc_pid_maps(5): ['| S496 |']
```

### Base 26ecba64ad6fb571d09074b07202d1618a46ecd1 — run 1 (exit 1, 46.3 s)

`c1-base-1.out`:
```
tip=26ecba64ad6fb571d09074b07202d1618a46ecd1
bind=0 teardown=0 newrow=0 bound=0/3 met=False
detail: counter vocabulary: 512 tokens from its own download
detail: bind b1: server parent pid 2791928 carries the planted KAMA_R50_CANARY
detail: bind b1: rerun model_mapping None does not record the observed mapping ('103:05', '1282299537')
detail: bind b1: planted sitecustomize imported by 1 interpreter(s): ["2791928 [...]/tree/tools/kama-llamacpp-live.py --server [...]/llama-server"]
detail: bind b2: server parent pid 2803642 carries the planted KAMA_R50_CANARY
detail: bind b2: rerun model_mapping None does not record the observed mapping ('103:05', '75405080')
detail: bind b2: planted sitecustomize imported by 1 interpreter(s): ["2803642 [...]/kama-llamacpp-live.py --server [...]/llama-server"]
detail: bind b3: server parent pid 2820051 carries the planted KAMA_R50_CANARY
detail: bind b3: rerun model_mapping None does not record the observed mapping ('103:05', '349552798')
detail: bind b3: planted sitecustomize imported by 1 interpreter(s): ["2820051 [...]/kama-llamacpp-live.py --server [...]/llama-server"]
detail: teardown: invoker SIGKILLed with 3 descendants; after 30.06 s alive [2828121, 2841886, 2844433] port ACCEPTS FAIL
detail: newrow: 0 rows new since base; 0 name proc_pid_maps(5): []
```

## Run-to-run comparison (build run 1 vs build run 2)

`diff c1-build-1.out c1-build-2.out` — the only differing lines are the three `bind bN` details, and only in run-varying fields:

- `pid` (fresh server each run), `port` (ephemeral loopback port), `inode` (fresh download/extract each run — different scratch work dirs), `nonce` (fresh random).
- **Stable across runs**: verdict line byte-identical (`bind=1 teardown=1 newrow=1 bound=3/3 met=True`); `exe+listen+tree+env+mapped ok` and `child_pid joined` on all 3 binds; `mapping dev 103:05` (counter scratch is xfs per prereg limits); teardown `0.10 s alive []` both times; `newrow` finding S496/proc_pid_maps(5) both times; 512-token counter vocabulary.

No nondeterminism in any leg's pass/fail. The measurement is reproducible.

## Base-run failure analysis (the counter discriminates correctly)

At base the counter fails exactly the legs the round-49 closure flagged, which is the honest negative control:

- **env leg (R1/K1Cheat)**: server parent carries `KAMA_R50_CANARY` and the planted `sitecustomize` was imported by the live tool on all 3 binds — base tool was not `python -I` and inherited the counter's environment.
- **mapped leg (R1/K1Design/R0Controls)**: `model_mapping None` in the rerun receipt — base `kama-llamacpp-live.py` records no model mapping.
- **teardown leg (R2/X1Kill)**: after SIGKILL of the invoker, 3 descendants still alive at 30 s and the port still accepts — base had no own-pdeathsig on the replay.
- **newrow leg**: no proc_pid_maps(5) SOURCES row at base.

The build run shows every one of these closed: canary absent, marker file empty, `model_mapping` recorded with matching dev+inode and sha256, teardown in 0.10 s, S496 row present.

## Observations (non-blocking)

1. The counter exercised a real download path each run (~75 MB server tarball + model per replay leg — three binds plus one teardown = four replays per run), still completing in ~17–19 s at the tip; the base run takes 46 s because its teardown leg waits the full 30 s window before declaring survivors. Timing is consistent with the failure mode, not with flakiness.
2. `bound=3/3` and `child_pid joined` both runs — the observed-pid ↔ rerun-receipt join (the R1 defect) is held.
3. No stray processes: `pgrep -af llama-server` after all runs shows only processes belonging to other seats (`J2NoPdeathsig`, `Sen3Teardown`); nothing under `/fast/scratch/hyaku/kama-r50/R1Rerun2/`. The counter's own teardown verified `alive []` for each of my runs.
4. Known integration items (counter not yet in SKILL.md registry, round-50 SCORECARD/LOG/lesson entries unwritten) are L1/scribe scope, not counter defects — not re-reported per assignment.

## Tooling

No installs performed or needed (python3, git, curl/network already present). No pacman transactions.

## Deliverables written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/R1Rerun2/c1-build-1.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/R1Rerun2/c1-build-2.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/R1Rerun2/c1-base-1.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/R1Rerun2.md` (this report)
