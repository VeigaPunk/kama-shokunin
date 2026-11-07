# CR01LinearCounter — attack on the frozen C2 counter (round 92, wave 1)

## Scope
`tools/round92-linear-paths.py` @ F=309eadaf (sha256 64e7b35a…): the 9 D cells, the 6 L cells, the
`served_scaled` check, the 20 s budget / 120 s kill, and the BASE-and-M-same-path choice. Subject is
M2 `fa8aedb7` (probe sha256 36631d49…). Five one-change forgeries of M2 were built and scored twice:
with `--probe-file` (prints `probe=override`) and as commits in my own scratch clone
(`git clone --shared` of the lane; commits in `counter-runs/clone-revs.txt`) so the counter prints
`probe=rev`. Held-out cells H1–H5 are legal answers under the probe's 4 MiB cap that the 15 cells do
not contain; they run through the counter's own `Stub`/`Runner` (same cwd, TMPDIR, `--timeout 5`).
Host load 40–55 throughout; `uptime` stands next to every timing in the receipts. No tools installed.

## Commands and outputs (exit codes)
1. Counter at M2 (load 41): `python3 tools/round92-linear-paths.py --repo <lane> --rev fa8aedb7… --work <scratch>/cw-m2`
   → `cells=15 mismatches=0 positive_mismatches=0 probe=rev probe_sha256=36631d49…`, exit 0; slowest
   cell L1 2.74 s (`counter-runs/m2.out`).
2. Each forgery, `--probe-file`: exit 0, `cells=15 mismatches=0 positive_mismatches=0 probe=override`
   (`counter-runs/FG{1..5}-*.out`).
3. Each forgery as a rev in my clone: exit 0, `cells=15 mismatches=0 positive_mismatches=0 probe=rev
   probe_sha256=<forgery> rev=<commit>` (`counter-runs/FG{1..5}-*-rev.out`).
4. Held-outs: `bash run-holdouts.sh <lane> <scratch> <out>` → `holdout.out`, exit 0.
5. Same path / body transfer: `python3 samepath-probe.py …` → `samepath.out`, exit 0.

## Findings

**DEFECT 1 — the counter admits a probe that still has F1's quadratic escape path (false green).**
`forgeries/FG1-jstr-mixed.sh` = M2 with `jstr` falling back to BASE's `${s//…}` substitutions when one
value mixes `\` with `"`. Counter: exit 0, `probe=rev`, all 15 cells ok, L1 3.15 s, L2 2.36 s,
`served_scaled=1` (`counter-runs/FG1-jstr-mixed-rev.out`). Held-out H1, one id of n/2 `\` then n/2 `"`
(bodies 0.8/1.6/3.2 MB):
| n | M2 | FG1 | ratio M2 / FG1 |
|---|---|---|---|
| 400 000 | 0.59 s | 1.62 s | ×1.64 / ×3.48 |
| 800 000 | 0.97 s | 5.63 s | ×1.99 / ×4.82 |
| 1 600 000 | 1.93 s | 27.14 s | — (27 s > BUDGET 20 s) |
FG1's output is byte-identical to M2 at every size (`served_sha256 bac8eef2…/ade0d31d…/22a7e520…` in
`holdout.out`): correct but super-linear — the exact SC02 F1 defect, yet every cell is green because
L1/L2 only test one repeated byte. Smallest safe correction (predicates are frozen; next round): one
L cell whose id mixes escapes at the L1/L2 size, judged on served bytes + BUDGET.

**DEFECT 2 — a router count cap above the L-cell sizes passes.**
`forgeries/FG2-router-cap-85k.sh` (`router_entries | head -n 85000`); counter exit 0, `probe=rev`,
L3 (80 000) and L4 (60 001) green (`counter-runs/FG2-router-cap-85k-rev.out`). Held-out H2: 90 000
unloaded `g` entries then one loaded `g` last, body 3 690 065 B < MAX_BODY 4 194 304 → M2
MODEL_OK/matched (2.13 s) vs FG2 MODEL_UNLOADED/router-unloaded (2.14 s) (`holdout.out`).
Correction: a router cell above the largest present cell (e.g. 90 000 + loaded last). L3's judge is
only equality with D3's verdict/reason at 50 entries (counter:325-332).

**DEFECT 3 — served_persist correct only under `/m/` passes.**
`forgeries/FG3-served-persist-m-only.sh` (1001+ ids: strip through `/m/`, then one `.gguf`); counter
exit 0, `probe=rev`, L5 green because all 16 000 L5 ids are `/m/xNNNNN.gguf`
(`counter-runs/FG3-served-persist-m-only-rev.out`). Held-out H3: 12 ids `/srv/models/…` → base, M2,
FG3 all `x00000,…` (served_sha `de6a1237…`, the rule anchor); 20 000 ids → M2 139 999 B `x00000,…`
(`6b27314b…`) vs FG3 379 999 B `/srv/models/x00000,…` (`e197c409…`) (`holdout.out`). Correction: an
L5-shaped cell whose ids live outside `/m/`.

**DEFECT 4 — a served_persist count cap above L5 passes.**
`forgeries/FG5-served-persist-cap-20k.sh` (persist at most 20 000 ids; L5 has 16 000); counter exit 0,
`probe=rev` (`counter-runs/FG5-served-persist-cap-20k-rev.out`). Held-out H5: 30 000 ids
`/srv/xNNNNN.gguf` → M2 30 000 ids (209 999 B, `a1143b4c…`) vs FG5 20 000 (139 999 B = the first
20 000, `6b27314b…`) (`holdout.out`). Same class as DEFECT 2: the largest cell count is the cap's
ceiling.

**DEFECT 5 — the D population is not exhaustive, so a wrong output is accepted.**
`forgeries/FG4-served-ids-rstrip.sh` (`served_ids` strips a trailing space from each id); counter exit
0, `probe=rev` (`counter-runs/FG4-served-ids-rstrip-rev.out`). Held-out H4: ids `["x ","y"]`, expect
`"x "` → BASE and M2 MODEL_OK/matched, served `'x ,y'`; FG4 MODEL_MISMATCH/served-id-mismatch, served
`'x,y'` (`holdout.out`). No frozen cell carries an id with a leading/trailing space. Correction: add
such an id to D5, whose ids otherwise look exhaustive.

**NOTE 1 — `served_scaled` pins only the uniform-run extension, not correctness.**
`unit` comes from M's own D1/D2 `served_model` (counter:308-315) and L1/L2 require
`s == unit × 1 900 000`; with D1/D2 byte-equal to BASE this pins a context-free per-byte transform for
one repeated byte. It says nothing about mixed values (DEFECT 1 passes with `served_scaled=1`), the id
count, or the rest of the row. L4 checks only `verdict == MODEL_OK`, reason ignored (counter:333-335);
L3 only equals D3's pair; `big_snap` ignores `rc` and the JSON rows
(`ok = rc is not None and got == want and dt <= BUDGET`, counter:280), so a large snapshot whose
verdict or exit status flips passes while the served column matches.

**NOTE 2 — BASE and M on the same path hides nothing measurable.**
`install()` rewrites `<work>/probe/kama-probe.sh` before each run; cwd and TMPDIR are shared. Measured
after both the BASE and the M2 run: the shared cwd is empty (`samepath.out`,
`cwd_entries_after_run=[]`) because the probe's EXIT trap removes its mktemp root; `R.snapshot()`
rmtree's `<work>/snap` before each snapshot, so BASE's history cannot reach M. One path is what
prevents a `$0`-keyed divergence; the only residual is that BASE is invoked first, so a probe could
leave a file in the shared cwd and key on it — the L cells run M only, so that channel yields no
green, and no counter can separate a probe keyed on its own invocation order.

**NOTE 3 — budget/kill are fair on this host; no correct probe was found to fail.**
Slowest of the 15 cells at M2: 2.74 s (load 41; frozen receipt at load 79: 3.43 s) — 5.8–7.3× under
BUDGET 20 s; KILL 120 s is 6× the budget. The probe's own `--timeout 5` is curl `--max-time` only: the
3 800 036 B L1 body transfers in 3–10 ms with the probe's exact curl flags (`samepath.out`), so the
internal timeout is far away. Caveats: the D cells also require equal `rc` and M ≤ BUDGET
(counter:246,260), stricter than the docstring's "byte-equal stdout" — a probe changing only its exit
status would fail; and the absolute budget has no load normalisation (a probe ~7× today's L1 would
fail while still linear).

**NOTE 4 — the harm suite is no backstop for any of the five.** Its specials cells are ≤4 ids
(`tools/round90-hostile-answers.py:72,76`: BIG is a 64 MiB stream-cap test, P4 is `q"b\s`), so FG1's
mixed path is only exercised where BASE's substitutions are instant; no fixture has a 90 001-entry
router, an id outside `/m/`, 30 000 snapshot ids, or a trailing-space id
(`tests/probe-verdicts/*.json`, `tools/test-snapshot.sh`).

## Deliverables (`…/round-92/w1/out/CR01LinearCounter/`)
`build-forgeries.py`, `forgeries/FG{1..5}-*.sh` (full M2 copies; sha256 in each counter receipt),
`holdout.py`, `run-holdouts.sh`, `holdout.out`, `samepath-probe.py`, `samepath.out`,
`counter-runs/{m2,FG{1..5}-*,FG{1..5}-*-rev}.out`, `counter-runs/clone-revs.txt`.

VERDICT: partial — M2 itself is linear and correct on every held-out shape I built, but the frozen
counter certifies five probes that are still super-linear or wrong (probe=rev, exit 0), so C2's
predicate does not entail the claimed linearity.
