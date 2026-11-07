# CR01RepeatCounter — kama round 93 wave 1 (operability)

Seat CR01RepeatCounter. Lane read-only except this report and `.ufo/waves/round-93/w1/out/CR01RepeatCounter/`;
scratch `/fast/scratch/hyaku/kama-r93/CR01RepeatCounter` removed after copying receipts. No tool installs.

## Scope

Attack the frozen C1 counter `tools/round93-router-repeat.py` (sha256 `053a915e…`; `git diff 0f272a37..HEAD` on
it is empty, so K3 holds) at the measured revision M1 `fe5f031cb1b9d33e1160360d892149b8ac3c7771` (probe sha
`159c8068…`) against BASE `5af794958b0fc08f574aa2e67650282269549b02` (probe sha `36631d49…`). 19 wrong
probe copies (`git show <M1>:tools/kama-probe.sh` + one exact-text replacement) were run exactly as the frozen
controls do — `--probe-file`, hence `probe=override` — plus the M1 control. The strongest forgery was also
committed in a scratch clone and run with `--rev`, so the printed predicate itself (`probe=rev`) comes from a
wrong probe. The counter's three fixtures were audited with its own `gguf()`/`ROUTER_PY` bytes, and every
passing forgery was tried on router listings the 10 cells do not contain. Host load 46–101 (`load1` in every
receipt); no counter cell run exceeded BUDGET (max 1.35 s vs 20 s).

## Commands and outputs (cwd = out dir unless noted; exit codes true)

1. `python3 forgeries.py` → **0** — `FORGERY_SWEEP total=16 pass10of10=12 caught=4` (`forge-sweep.out`,
   `forgery-sweep.json`).
2. `python3 forgeries.py cap64-bash-bad cap1024-bash-bad key-name-size identity-repeat-invalid` → **0** — 4/4
   pass 10/10 (`forge-sweep-2.out`).
3. `python3 fixture-check.py` → **0** — raw and `file_state` states of the counter's fixtures
   (`fixture-check.out`).
4. `python3 shapes.py`; `python3 shapes2.py`; `python3 shapes3.py`; `python3 shapes4.py` → **0** each
   (`shapes.out`, `shapes2.out`, `shapes3.out`, `shapes4.out`).
5. Clone: `git clone --shared <lane> <scratch>/wt`, `git checkout --detach fe5f031c…`, replace
   `tools/kama-probe.sh` with `forgeries/key-realpath.sh`, commit `9ba61d3149259f9e18ffd1b86bec3c5034e3ca0f`;
   then `python3 <lane>/tools/round93-router-repeat.py --repo <scratch>/wt --rev 9ba61d31… --work <scratch>/work/rev-forgery`
   → **0** — `ROUTER_REPEAT cells=10 mismatches=0 positive_mismatches=0 probe=rev probe_sha256=2a022772…`
   (`in-clone-forgery.out`).
6. M1 control through the same counter: `--probe-file forgeries/m1-control.sh` → **0** — 10/10, load1=72.6
   (`forge-sweep.out`); 16 of 20 variants overall score 10/10 (15 of 19 forgeries; `m1-control` is the 16th).

## Findings

"Passes" = `mismatches=0 positive_mismatches=0`. The shape shown is a real router listing (`GET /v1/models`,
`id=good`, `status=unloaded`, `status.args`) where the forgery's verdict differs from M1's.

**BLOCKER-1 (counter gap, false green).** A memo keyed by `os.path.realpath(path)` passes 10/10 and re-opens
the r92 SC02 F6 false green on hardlinks: 64 entries through 33 hardlinks to one slow invalid inode → M1
`MODEL_UNLOADED/router-model-invalid` 0.86 s, BASE `MODEL_OK/router-unloaded-autoload` 4.41 s, `key-realpath`
`MODEL_OK/…` 4.34 s (`shapes2.out` S8; `forgeries/key-realpath.sh`; in-clone `probe=rev` 0/0). R05's 33 aliases
are one symlink plus `dir/` + `./`*k (`tools/round93-router-repeat.py:216`), and every one collapses under
`realpath`; the rule says "whatever path string names it", so hardlinks are in scope and untested. This is the
plausible repair path for a `key=path` author whose R05 goes red. Smallest correction: R05b = 33 hardlinks
(`os.link`) to `slow.gguf`, 64 entries, expect `MODEL_UNLOADED/router-model-invalid`.

**DEFECT-1 (fail-closed cap at P02's edge passes).** A bash caller that parses only `${cand[@]:0:64}` and adds
the tail to `nbad` unparsed passes 10/10, but 64× slow-invalid + one distinct valid at position 65 becomes
`MODEL_UNLOADED/router-model-invalid` where M1 and BASE say `MODEL_OK/router-unloaded-autoload` (`shapes2.out`
S9; `cap1024-bash-bad` also passes). P02 has exactly 64 candidates (`:225`), so position 65 is outside every
positive cell, and R04's 2048 are all bad, so "tail assumed bad" and "tail parsed" are indistinguishable.
Smallest correction: P02 with 2048 candidates and the valid file last.

**DEFECT-2 (coarser keys pass; false red).** `key-basename`, `key-size` and `key-name-size` pass 10/10 and report
`MODEL_UNLOADED/router-model-invalid` on P02-shaped listings where M1 and BASE report `MODEL_OK`: 63×
`a/slow.gguf` invalid + `b/slow.gguf` valid, same basename (`shapes.out` S1); 63× slow + a valid GGUF padded to
the exact same length — trailing slack is legal to the parser (`gguf_parse` ok check) (S2); 63× 192-byte corrupt
`b/dup.gguf` + valid `a/dup.gguf` (S10). No cell contains two distinct files that agree on any proper sub-key,
so the identity tuple is never tested as a tuple. MT01 m01–m04 already show each single-field drop passes; the
missing evidence is a collision cell, not another key drop. Smallest correction: one cell with two distinct
same-basename same-size files, one invalid one valid, expect `MODEL_OK`.

**DEFECT-3 (repeat → invalid passes; false red).** `identity-repeat-invalid` (identity key, second sighting →
`"invalid"`) passes 10/10 and grades the one-entry listing `[exe, "-m", ok.gguf, "-md", ok.gguf]` as
`MODEL_UNLOADED/router-model-invalid` where M1 and BASE say `MODEL_OK/router-unloaded-autoload` (`shapes4.out`
S11). "Every candidate naming it gets the same state" is exactly what fails; no cell names one file twice
inside one entry (R05 names each alias once per entry, R06 names two different files). Smallest correction: a
one-entry, two-path-flag cell on `ok.gguf`.

**DEFECT-4 (per-call vs cross-call cache; false green).** `disk-cache-identity` (on-disk memo in `$TMPDIR`,
keyed by the identity tuple) passes 10/10 and false-greens the RV01 DEFECT-1 shape across calls: same path,
same inode, same 192-byte length, `os.utime` restores mtime after an in-place rewrite to a corrupt header →
M1 and tip `b3765799` (probe sha `1e21c1fb…`) `MODEL_UNLOADED/router-model-invalid`, the disk cache
`MODEL_OK/router-unloaded-autoload` (`shapes4.out` S12; `identity_unchanged=1`). The claim says "once per
_call_"; the counter never mutates a fixture between candidates, runs or calls. The landed ctime fix is itself
outside the frozen counter's evidence. Smallest correction: a two-invocation cell (same `--work`, same stub)
with the same-size mtime-restored rewrite between them, expect `MODEL_UNLOADED`.

**NOTE-1 (fixtures).** (a) `slow.gguf` is parsed through all 150 000 tensor infos before `invalid`:
`DIAG_INVALID_AT tell=6000024 size=6000048 steps=900004 ninfos=150000`, 0.80–0.96 s per parse
(`fixture-check.out`) — the slow shape is real, not an early-header reject. (b) `ok.gguf`'s raw state is `ok`,
but the counter's sanity loop asserts `file_state`, which maps both `ok` and `-` to `-`
(`tools/round93-router-repeat.py:208`; `FIXTURE_FILE_STATE … 1 - 2 -`), so the positive parse is never
asserted. (c) P02 needs no decided valid candidate, only a candidate that is not `missing`/`invalid`:
`ok-as-unknown` (returns `-` for every `ok`) passes 10/10. If the intent is "every candidate gets the same
state", the cells check the bad/not-bad bit, not the state.

**NOTE-2 (passing, no harm shape found).** `repeat-invalid` keyed by path string is *caught* by R05, but for
cost (33 distinct alias parses hit the 4 s deadline), not for the repeat rule; `key-size-mtime` and
`key-devino` are subsumed by MT01 m01–m04 (harm shape is RV01's in-call rewrite); the per-entry `file_state`
caps (`cap64-bad`, `cap64-unknown`) are unexercised because every cell entry has 1–2 path flags;
`overfit-names` (no parse at all: `"slow" in basename` → invalid) passes 10/10, i.e. any oracle over the three
fixture names / two sizes scores 0/0.

**NOTE-3.** Cell grading ignores the probe's exit code (false-red forgeries return rc=2; only verdict/reason are
compared), and the v0 4-alias R05 let `key-path` pass at load 87 (peer receipt `measured/m1-v0-alias-F2.out`);
the frozen 33-alias R05 catches it, but alias count — not just class — remains load-calibrated.

Impacted axes: operability (C1), calibration (10/10 is being read as evidence for the rule, not only for the
predicate), coverage (alias classes, identity collisions, candidate-count edge).

## Deliverables

`.ufo/waves/round-93/w1/out/CR01RepeatCounter/`: `forgeries.py`, `forgeries/*.sh` (20 variants incl. the M1
control), `forgery-sweep.json`, `forge-sweep.out`, `forge-sweep-2.out`, `fixture-check.py`, `fixture-check.out`,
`shapes.py`, `shapes.out`, `shapes2.py`, `shapes2.out`, `shapes3.py`, `shapes3.out`, `shapes4.py`,
`shapes4.out`, `in-clone-forgery.out`.

VERDICT: partial — C1's predicate holds at M1 (10/10, BASE still 5 red) and no listing falsifies M1, but the 10 cells do not pin the identity rule: 15 of 19 wrong probes score 0/0 and seven of them change the verdict on listings the cells omit, including a hardlink listing that re-opens the r92 F6 false green and a fail-closed cap at exactly P02's 64-candidate edge.
