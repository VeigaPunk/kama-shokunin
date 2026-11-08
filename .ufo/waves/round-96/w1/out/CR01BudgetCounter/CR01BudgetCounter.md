# CR01BudgetCounter — attack on frozen C1 counter `tools/round96-router-budget.py`

Lane: `kama-shokunin` @ `bbdfc930cf99845f7b5c4ab63f3bfd51ba39e582` (HEAD at attack time).
Frozen plan: `plans/round-96-claims.md` §C1 (predicate: 12 cells, `mismatches=0`,
`load_stable=1`, exit 0, counter bytes identical to freeze commit `58001b71`).
Counter bytes: byte-identical to freeze commit — verified:
`git show 58001b71:tools/round96-router-budget.py | sha256sum` =
`sha256sum tools/round96-router-budget.py` = `3f6107c3…` (also = `git show HEAD:…`).
Probe at HEAD: `MAX_STEPS = 5_000_000`, wrapper `local limit=$((20 + 25 * npaths))` (line 871).

**Axes named.** This seat attacks counter integrity (operability axis, §C1). Each attack
below is scored: does the counter let a broken instrument pass, or fail a sound one,
against the frozen predicate?

---

## Attack 1 — both passes in one invocation with `--skip-load` (must NOT print green)

Commands (scratch work dirs under `/fast/scratch/hyaku/kama-r96/CR01BudgetCounter/`; all
used `--repo /home/vgpnk/Projects/shokunin/kama-shokunin --rev HEAD --burners 0 --runs 1`):

- `… w1 … --slow-files 8 --skip-load --allow-clock` → exit **1**.
  Summary: `cells=12 mismatches=-2 positive_mismatches=-2 load_cells=0 load_stable=0 …
  load_note=skipped`, preceded by
  `ROUTER_BUDGET96 load_skipped=true … (no second pass ran; predicate unreachable)`.
- `… w2 … --slow-files 8 --skip-load` (no `--allow-clock`) → exit **2**
  (`could-not-evaluate: W03 natural pass 9.8s < 1.2 x 60s …`, margin guard; see Attack 6).
- `… w5 … --slow-files 40 --skip-load --allow-clock` → exit **1**, same
  `load_cells=0 load_stable=0 load_note=skipped` summary.

The counter never prints `load_cells=12/load_stable=1` under `--skip-load`; skip-load
forces exit ≠ 0 and uses the sentinel `mismatches=-2` (not a plausible green).
**Verdict: HOLDS** — CR01 DEFECT-3 from round 95 is genuinely closed. Not a blocker.

## Attack 2 — probe whose `MAX_STEPS` is halved (does the counter distinguish?)

`cp tools/kama-probe.sh` → scratch, `sed 's/MAX_STEPS = 5_000_000/MAX_STEPS = 2_500_000/'`
(2 500 000 / 6 = ceiling ≈416 666 < 600 000-tensor slow fixtures), run via
`--probe-file … --skip-load --allow-clock` (`w3`):

- W01, W02, W03, W08, W11, W10 all grade `MODEL_OK/router-unloaded-autoload` (the slow
  fixtures become undecidable→loadable), each `ok=0` against the frozen expectation.
- Summary: `cells=12 mismatches=-2 … probe=override …`, exit **1**.

The counter distinguishes a halved budget cell-by-cell; no silent pass.
**Verdict: HOLDS.** Not a blocker. (Also confirms `probe_sha256` in the receipt binds
to the exact bytes graded.)

## Attack 3 — docstring formula vs wrapper literal

- Counter docstring line 21: `` (`20 + 25 * npaths` seconds) ``.
- Probe line 871: `local limit=$((20 + 25 * npaths))`.
- Both literals identical; no stale `20 + 15 * ncand` anywhere in either file.

**Verdict: HOLDS** (this is C3's check (2); it also closes the routed defect).
Not a blocker.

## Attack 4 — `KILL=1200` vs derived limit for W03 (`20 + 25 * 40 = 1020 s`)

- Counter `KILL = 1200` (line 92); `Runner.check` passes `timeout=KILL` to the
  `check --json` subprocess.
- Derived wrapper limit for W03 (40 npaths) = 1020 s < 1200 s → 180 s headroom for the
  `check` harness outside the `router_file_states` timeout (curl, JSON render, interpreter
  startup inside the probe).

**Verdict: HOLDS.** The round-95 defect (KILL tighter than the derived limit) is closed;
no last cell is structurally unrunnable. Not a blocker.

## Attack 5 — margin guard at 40 files: can a truncated pass still grade green?

Truncation attack: scratch probe copy with the wrapper limit replaced by `local limit=5`,
run `--probe-file … --skip-load --allow-clock --slow-files 40` (`trunc`):

- W02 and W03 grade `MODEL_OK/router-unloaded-autoload` (`ok=0`) — truncated passes are
  scored mismatches, never passes, exactly as the frozen predicate requires.
- Exit **1**. Full cells W03 at 40 files (w5, untruncated): `ok=1` at 52.0 s.

Also observed: the margin guard (`w03 < 1.2 * 60 s → exit 2`) fires without
`--allow-clock` whenever this host's natural W03 pass is < 72 s — *including at HEAD with
a healthy probe* (w2: 9.8 s, full run: 58.7 s → exit 2). On a fast host the full
predicate run exits 2 rather than grading; it never grades green on a truncated pass.
**Verdict: HOLDS** for the frozen predicate (a truncated pass cannot pass). The
host-speed dependence is the disclosed guard behaviour, and `--allow-clock` bypasses it
for the red control — but integration (M1) must run where W03 ≥ 72 s or will land in
exit 2. Not a blocker against the frozen predicate as written; noted for M1.

## Attack 6 — full two-pass run at HEAD (the frozen predicate itself)

`… full … --burners 4 --runs 1 --slow-files 40` (both passes, no skip):
every cell `ok=1` **except W12-strings** (`ok=0`), then the margin guard exits 2
(`W03 natural pass 58.7s < 1.2 x 60s`). With `--allow-clock` (skip-load runs w1/w5),
same W12 failure, exit 1.

## ⚠️ BLOCKER — W12-strings is deterministically red at HEAD (and in the committed base receipt)

W12 (`strbig.gguf`: 0 tensors, one KV uint32-string-array of 6 000 000 elements) is
designed `-` (undecidable→loadable) → expectation `MODEL_OK/router-unloaded-autoload`.
The probe grades it `invalid` → `MODEL_UNLOADED/router-model-invalid` → `ok=0` in
**every** observed run: w1, w2, w3, w4 (base rev `5d43528b`), w5, trunc, full.
Critically, the **committed frozen base control**
`.ufo/waves/round-96/controls/c1-base.out` (freeze commit `58001b71`, and unchanged at
amendment commit `bbdfc930`) already carries the same red line
(`W12-strings ok=0 … run1/2=MODEL_UNLOADED/router-model-invalid`), and the same receipt
shows W11 red at base (`ok=0`, `MODEL_OK…`) — exactly the designed discriminator, so the
*other* 11 cells behave as frozen and W12 is the single outlier. The full predicate
(`mismatches=0 … exit 0`) **cannot be met at M1 as frozen**, because W12 is a cell error,
not a load instability or a margin refusal.

Root cause (traced in scratch `x2/`, receipts under `out/…/receipts/`): the fixture
builder `gguf_strbig()` writes **one** `<Q>` length prefix (=1) followed by 6 000 000
raw `x` bytes, but the GGUF string-array layout the probe parses is
`n` × (`u64` length + string bytes). The probe's `skip_strings(6_000_000)` then reads
the `x` bytes as lengths (`0x7878…`), the first read past the file triggers `Bad`
(or `base+off > size`) → `invalid`, *before* the `steps > MAX_STEPS → Unknown → "-"`
path the cell was designed to exercise. The fixture never reaches the step budget; the
counter's own oracle `fixture_class` returns `"-"` (it special-cases `n_tensors == 0
and n_kv >= 1` from the header counts only, never the array bytes), so the fixture
sanity gate passes while the cell is unmeetable. A correct fixture must write 6 000 000
per-element prefixes (`<Q>(1) + b"x"` each, ≈54 MB) so that per-element step charging
in `skip_strings` (one step per element) trips `MAX_STEPS` at element 5 000 000 → `-`.

**This is a BLOCKER against the frozen C1 predicate.** One cell (W12) fails in both
natural and loaded passes at M1; `mismatches` will be ≥1 and exit ≠ 0 whatever the host.
The counter is otherwise sound (Attacks 1–5 hold; the instrument correctly *reports* the
failure — the defect is in the frozen fixture bytes, which K3 forbids changing after F).

Smallest safe correction (does not alter the predicate, only makes the fixture meet it;
requires a plan amendment since the counter is frozen): rewrite `gguf_strbig()` to emit
6 000 000 × (`struct.pack("<Q", 1) + b"x"`). Note the knock-on: the file grows from
6 000 057 B to ≈54 000 049 B + header, and a 5 000 000-step parse of it costs the probe
real CPU — re-time W12 against the 1020 s W03-derived limit before M1. Also note the
counter docstring line 19 still says `` `MAX_STEPS` (4 000 000) `` (round-95 prose)
while the code is 5 000 000 — C3-adjacent staging determinism issue, not a C1 blocker.

## Summary

| Attack | Result | Blocker? |
|---|---|---|
| 1. `--skip-load` both-passes | holds (exit≠0, `load_cells=0`, `mismatches=-2`) | no |
| 2. halved `MAX_STEPS` | holds (cells redden, exit 1) | no |
| 3. docstring formula vs wrapper | holds (`20 + 25 * npaths` both) | no |
| 4. `KILL=1200` vs 1020 s derived | holds (180 s headroom) | no |
| 5. margin guard / truncation | holds (truncated pass = mismatch; fast host exits 2) | no |
| 6+7. full run / W12 fixture | **W12 red in both passes, all runs, and frozen base receipt** | **YES** |

**Overall verdict: BLOCKER.** The frozen C1 counter is a sound instrument (its
skip-load/KILL/margin/truncation guards all hold in both directions), but the frozen
W12 fixture bytes cannot produce the frozen expectation, so the frozen predicate
(`mismatches=0, load_stable=1, exit 0` at M1) is unsatisfiable as-is. The instrument
did its job by reporting it. A fixtures-only amendment (correct per-element string-array
bytes) is the smallest safe correction; it must be re-timed and re-frozen before M1.

## Artifacts

- This report: `.ufo/waves/round-96/w1/out/CR01BudgetCounter/CR01BudgetCounter.md`
- Scratch receipts (probe copies incl. halved/trunc, extracted `ROUTER_PY`, strbig
  buffer): `.ufo/waves/round-96/w1/out/CR01BudgetCounter/receipts/`, and the raw
  `w1–w5/trunc/full` output buffers left in scratch (copied metadata there).
- No tracked lane file was modified; no commit/push performed.

### Suspicious patterns noticed (context only, not claimed)

- `tools/round96-router-budget.py` line 19 docstring: `` `MAX_STEPS` (4 000 000) ``
  (round-95 value) beside code `MAX_STEPS = 5_000_000` in the probe — likely C3's
  staged item, not mine.
- Committed `controls/c1-base.out` at freeze time already contains the W12 red line
  (identical at `58001b71` and `bbdfc930`): the base receipt proves W11 discriminates,
  but a claim holder reading the receipt should have seen the W12 red before freeze.
- Scratch tree under `/fast/scratch/hyaku/kama-r96/CR01BudgetCounter/` retained
  (out-dir copies made) — left on disk intentionally for the integrator; deletion
  deferred to coordinator cleanup (see seat spec).
