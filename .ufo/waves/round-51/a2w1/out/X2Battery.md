# X2Battery — round-51 no-harm battery (operability + calibration lane seat)

**Verdict: NO HARM.** All 23 measure.sh instruments ran at base `57a2e25bf702b03aa61f9265e968cf68058ecb82` and build `138af25b963450b6520794995605fa7dbbcd87e0` on fresh `--shared` clones. Three instruments got worse — `gate`, `r43`, `r50c2` — and all three are expected: `gate`/`r43` are the known "SKILL registry lacks the two round-51 counters" integration item (r43's `selftest` leg is the same unregistration surfacing through gate's own `--selftest` lane-tip arm), and `r50c2` is the declared v6 supersession of the v5 counter. No instrument regressed for any other reason.

## Method

- Driver: `.ufo/waves/round-51/a2w1/out/X2Battery/measure-x2.sh` — the L1 `measured/measure.sh` command list verbatim, pointed at this seat's out dir. Recorded deltas: receipts land in `runs/` (lane `measured/` is read-only), the clone is `git clone --shared` (seat directive) instead of a full clone, and at the base the two round-51 counters — absent from the base tree — were invoked as the frozen lane bytes with `--repo <clone>` (the same shape that produced `controls/base.c{1,2}.out`; sha256 e5753c45… / 254e63ba… = the preregistration pins at both tips; at the build the clone's own copies are the same bytes).
- Receipts: `.ufo/waves/round-51/a2w1/out/X2Battery/runs/<name>-{base,build}.out`, each with the command line, full output, `exit=`, and tip.
- Table: `.ufo/waves/round-51/a2w1/out/X2Battery/table.md` (one row per instrument, both lines, verdict).
- Timings: base sweep 142 s, build sweep 140 s (03:50Z–03:56Z). `pgrep -af llama-server` clean afterward (exit 1, no leftovers).

## Fidelity anchor

The base run reproduces the frozen base controls exactly:

- `c1-base.out`: `bind=1 own=0 teardown=1 newrow=0 bound=3/3 owned=0/3 met=False exit=1` — identical headline to `controls/base.c1.out`.
- `c2-base.out`: `fixture=0 lane=0 scenarios=0/9 lost=0 disclosed=0 met=False exit=1` — identical to `controls/base.c2.out`.

And the build run reproduces the claim: `c1-build.out` `bind=1 own=1 teardown=1 newrow=1 bound=3/3 owned=3/3 met=True` and `c2-build.out` `fixture=1 lane=1 scenarios=9/9 lost=142 disclosed=166 met=True` — matching the L1's `-build` receipts (which were taken at 73bf2a7a; mine at 138af25b).

## Instruments that got worse

| instrument | base → build | class |
|---|---|---|
| gate | `unregistered 0 → 2`, exit 0→1 | **expected integration** — SKILL registry lacks `tools/round51-replay-exe-audit.py` and `tools/round51-append-audit-v6-check.py` (listed known item) |
| r43 | `unreg 0→2`, `selftest 0→1`, `pop 46→48`, `mismatches 1→4` | **expected integration** — same root cause: gate's `--selftest` 6th arm audits the lane tip itself, so it fails while the counters are unregistered (`detail: selftest: documented 'GATE_SELFTEST pass=6 fail=0', run printed 'GATE_SELFTEST pass=5 fail=1' exit 1`). `pop=48` counts the two new tools. `spot=1` (36 vs 37 calibration rows) was already failing at base. |
| r50c2 | `lane 1→0`, `met True→False`, exit 0→1 | **expected supersession** — v6 tool supersedes v5 definitions (listed known item; its `fixture=1` leg still holds) |

## Not newly worse, worth noting

- **r49c2**: `met=False` at the base already (`event 0718b6abbda6 SCORECARD.md ungraded 72 > natively exempt 65`). Under the v6 tool its lane leg sees `events 5→106, ungraded_lines 89→205` and emits more detail lines — the same supersession family as r50c2, not a new harm.
- **digest**: identical to base (`unknown=0`, exit 0) and strictly better than the L1's measured receipt at 73bf2a7a (`unknown=166`, exit 1): build-fix 2 (`digest-ledger` drops `registry/append-only-disclosures.tsv` from token scope) is a measured improvement *inside* this wave.
- **census** (`sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama`): tip-invariant — it reads the live lane tree, not the clone. Both runs print the identical 96-row output (`E=0 W=95`, `kama ok …/kama-shokunin/corpus/SOURCES.md`, exit 0). The `E11 S499` in the L1's `census-build.out` has since resolved on the live tree (`corpus/lessons/round-51.md` now exists). Consequence for future waves: this leg can never attribute a change to the tip under test — flag for the L1 if the instrument is meant to be per-tip.
- **hexrun**: `unknown=2` identical at both tips (9e38a361, f8cdb853 — carried base state, known item); `tokens=1885→2051` is new build files, not a regression.
- **aoa**: `commits=337→341` counts the four round-51 commits; `events=5→106` is the v6 threshold-1 grading itself (the claim), with `unrestored=0 regressed=0 bad_disclosures=0`.
- **r41/r42**: `run_bad=1`/`mismatches=1` identical at both tips (known pre-existing base failure).

## Evidence

- Commands: `bash .ufo/waves/round-51/a2w1/out/X2Battery/measure-x2.sh base 57a2e25bf702b03aa61f9265e968cf68058ecb82` and `… build 138af25b963450b6520794995605fa7dbbcd87e0` (each: clone --shared → checkout --detach → the 22 `run` lines from measure.sh in order).
- Outputs: 46 receipts in `.ufo/waves/round-51/a2w1/out/X2Battery/runs/`; every instrument's headline line is quoted in `table.md`.
- Cross-check: `sha256sum` of the invoked counters equals the preregistration `counter_sha256` pins at both tips (e5753c45…, 254e63ba…).
- No tools installed (nothing needed beyond python3/git/gawk already present).
- No lane mutation: clones only under `/fast/scratch/hyaku/kama-r51/X2Battery/`, removed on finish; fixture commits none.

## Defects / risks

- **None new.** The only behavior-level risks visible in the battery are carried/known items (unregistered counters, `hexrun unknown=2`, r41 run_bad, r49c2/r50c2 supersession shape) and the census tip-invariance note above.
