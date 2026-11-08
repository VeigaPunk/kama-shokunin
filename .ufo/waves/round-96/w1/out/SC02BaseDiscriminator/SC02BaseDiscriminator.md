# SC02BaseDiscriminator — the frozen C1 counter at the base revision 5d43528b

Seat: scout (operability). Lane: `kama-shokunin`. Out dir: `.ufo/waves/round-96/w1/out/SC02BaseDiscriminator/`.
Scratch: `/fast/scratch/hyaku/kama-r96/SC02BaseDiscriminator/` (deleted on exit).

## Question assigned

> Run the frozen C1 counter at the base revision 5d43528b (its do-nothing control) into your out dir.
> Paste the receipt. Confirm which W-cells redden at base and whether W11 is among them (the
> counter's discriminator). If the base also stays green, the claim is void: say so in the report.

## Answer

**W11 IS among the cells that redden at base. The claim is NOT void — the counter discriminates.**

At the base revision `5d43528b` the frozen counter reports **`mismatches=2`** (both natural and load
passes): **W11-700k** and **W12-strings** both grade red. W11-700k is the plan's named discriminator
and it reddens exactly as the plan predicts (`MODEL_OK/router-unloaded-autoload` where the frozen
expectation is `MODEL_UNLOADED/router-model-invalid`).

But the same measurement exposes a defect in the frozen counter that the plan did not anticipate, and
it changes the verdict on the *tip* side: **with the frozen bytes, W12-strings also reddens at base and
at the tip, so the frozen predicate line `mismatches=0 positive_mismatches=0` was unreachable at M1
for reasons unrelated to the probe.** K1 (`mismatches>0` at M1) fires on the counter, not on the work.

## The base control, reproduced

Command (the plan's do-nothing control: same counter, base revision, `--burners 0`):

```
python3 tools/round96-router-budget.py \
  --repo /home/vgpnk/Projects/shokunin/kama-shokunin \
  --rev 5d43528badc31ad6c0ca1848c00561f531924e4d \
  --work <scratch>/work-base-full --burners 0 --allow-clock
```

Full receipt (both passes; `--allow-clock` only bypasses the W03 margin guard, it does not change any
cell grade — see "Margin guard" below):

```
ROUTER_BUDGET96_CELL nat W01-slow-x1 ok=1 want=MODEL_UNLOADED/router-model-invalid run1=MODEL_UNLOADED/router-model-invalid/2.18s run2=MODEL_UNLOADED/router-model-invalid/2.11s
ROUTER_BUDGET96_CELL nat W02-slow-x8 ok=1 want=MODEL_UNLOADED/router-model-invalid run1=MODEL_UNLOADED/router-model-invalid/15.38s run2=MODEL_UNLOADED/router-model-invalid/15.67s
ROUTER_BUDGET96_CELL nat W03-slow-x40 ok=1 want=MODEL_UNLOADED/router-model-invalid run1=MODEL_UNLOADED/router-model-invalid/61.47s run2=MODEL_UNLOADED/router-model-invalid/66.91s
ROUTER_BUDGET96_CELL nat W04-ok-x8 ok=1 want=MODEL_OK/router-unloaded-autoload run1=MODEL_OK/router-unloaded-autoload/0.17s run2=MODEL_OK/router-unloaded-autoload/0.17s
ROUTER_BUDGET96_CELL nat W05-slow-then-ok ok=1 want=MODEL_OK/router-unloaded-autoload run1=MODEL_OK/router-unloaded-autoload/11.60s run2=MODEL_OK/router-unloaded-autoload/12.06s
ROUTER_BUDGET96_CELL nat W06-missing-x8 ok=1 want=MODEL_UNLOADED/router-model-missing run1=MODEL_UNLOADED/router-model-missing/0.18s run2=MODEL_UNLOADED/router-model-missing/0.18s
ROUTER_BUDGET96_CELL nat W07-fast-k40 ok=1 want=MODEL_UNLOADED/router-model-invalid run1=MODEL_UNLOADED/router-model-invalid/0.20s run2=MODEL_UNLOADED/router-model-invalid/0.18s
ROUTER_BUDGET96_CELL nat W08-hardlink-x8 ok=1 want=MODEL_UNLOADED/router-model-invalid run1=MODEL_UNLOADED/router-model-invalid/1.93s run2=MODEL_UNLOADED/router-model-invalid/1.96s
ROUTER_BUDGET96_CELL nat W09-undecided-big ok=1 want=MODEL_OK/router-unloaded-autoload run1=MODEL_OK/router-unloaded-autoload/0.18s run2=MODEL_OK/router-unloaded-autoload/0.18s
ROUTER_BUDGET96_CELL nat W11-700k ok=0 want=MODEL_UNLOADED/router-model-invalid run1=MODEL_OK/router-unloaded-autoload/2.04s run2=MODEL_OK/router-unloaded-autoload/2.06s
ROUTER_BUDGET96_CELL nat W12-strings ok=0 want=MODEL_OK/router-unloaded-autoload run1=MODEL_UNLOADED/router-model-invalid/0.17s run2=MODEL_UNLOADED/router-model-invalid/0.17s
ROUTER_BUDGET96_CELL nat W10-rewrite ok=1 v1=MODEL_UNLOADED/router-model-invalid v2=MODEL_OK/router-unloaded-autoload v3=MODEL_UNLOADED/router-model-invalid
ROUTER_BUDGET96_CELL load W01..W09 ok=1 (all nine); load W10-rewrite ok=1
ROUTER_BUDGET96_CELL load W11-700k ok=0 want=MODEL_UNLOADED/router-model-invalid run1=MODEL_OK/router-unloaded-autoload/1.66s run2=MODEL_OK/router-unloaded-autoload/1.67s
ROUTER_BUDGET96_CELL load W12-strings ok=0 want=MODEL_OK/router-unloaded-autoload run1=MODEL_UNLOADED/router-model-invalid/0.14s run2=MODEL_UNLOADED/router-model-invalid/0.13s
ROUTER_BUDGET96 cells=12 mismatches=2 positive_mismatches=0 load_cells=12 load_stable=1 budget=work probe=rev probe_sha256=b49d961a0548f3c30a264d036b080c0b99a2bb8dfce523f575fbdb00d76a85df base_sha256=27065a5c487ec819a975cc96d3c990ab5161d0e55d82be02a87dde86974ed3b4 rev=5d43528badc31ad6c0ca1848c00561f531924e4d w03_seconds=66.9 load1_nat=25.34 burners=0
EXIT=1
```

**Reddening cells at base: W11-700k and W12-strings. Everything else (W01–W10) is green at base.**
`probe_sha256=b49d961a…` matches the committed control's `probe_sha256` exactly
(`git show 58001b71:.ufo/waves/round-96/controls/c1-base.out`), so this run measures the same probe
bytes the plan froze.

### The committed control and my run agree cell-for-cell

`git show 58001b71:.ufo/waves/round-96/controls/c1-base.out` (the committed base control) reddens the
same two cells:

```
ROUTER_BUDGET96_CELL nat W11-700k ok=0 want=MODEL_UNLOADED/router-model-invalid run1=MODEL_OK/router-unloaded-autoload/3.34s run2=MODEL_OK/router-unloaded-autoload/4.14s
ROUTER_BUDGET96_CELL nat W12-strings ok=0 want=MODEL_OK/router-unloaded-autoload run1=MODEL_UNLOADED/router-model-invalid/0.71s run2=MODEL_UNLOADED/router-model-invalid/0.60s
```

The committed control's summary line reads `mismatches=-2 positive_mismatches=-2` — those are the
`--skip-load` sentinels (the counter prints `-2` and returns 1 when the load pass is skipped), not
counts. The committed control was run with `--skip-load`, so it never produced a real mismatch count.
My run above is the same command without `--skip-load` and yields the true `mismatches=2`.

### Counter bytes verified identical to the freeze commit

```
git hash-object tools/round96-router-budget.py   -> c1a7a84dadb5161d3ecff2fcb679216e5d4320a7
git rev-parse 58001b71:tools/round96-router-budget.py -> c1a7a84dadb5161d3ecff2fcb679216e5d4320a7
```

## What the base control proves about the C1 work itself

The plan's C1 substance is confirmed by the base control: at the base revision the 700 000-tensor file
is graded `MODEL_OK/router-unloaded-autoload` (undecidable → loadable), i.e. exactly the false-`MODEL_OK`
defect amendment 4 / SC02 F1 describes. The work fixes it.

Parsing the base and tip probe bytes directly (the `ROUTER_PY` blob extracted from each revision's
`tools/kama-probe.sh`, `gguf_parse` called on the counter's own fixture bytes) isolates the cause:

```
W11 700k tensors (no data)        base='-'          tip='invalid'
```

`-` is the probe's undecidable marker → loadable → `MODEL_OK`. `invalid` → `MODEL_UNLOADED/router-model-invalid`.
The step arithmetic: 4 preamble steps (magic, version, `n_tensors`, `n_kv`) + 6 steps per `nd = 1` tensor
header = 4 + 6 × 700 000 = 4 200 004 steps. At base `MAX_STEPS = 4 000 000` the budget trips first
(`-`); at tip `MAX_STEPS = 5 000 000` it does not, so the file decides `invalid`. The counter's
documented "4 200 000" omits the 4 preamble steps; the true figure is **4 200 004**.

## The defect the base control exposes: W12 is a broken cell, and the frozen predicate was unreachable

With the frozen counter bytes, the tip run (freeze commit `58001b71`) gives:

```
ROUTER_BUDGET96_CELL nat W11-700k ok=1 …            <- the C1 fix works
ROUTER_BUDGET96_CELL nat W12-strings ok=0 want=MODEL_OK/router-unloaded-autoload run1=MODEL_UNLOADED/router-model-invalid/0.17s
ROUTER_BUDGET96 cells=12 mismatches=1 positive_mismatches=0 load_cells=12 load_stable=1 … rev=58001b71 …
EXIT=1
```

**`mismatches=1`, not 0** — so the frozen predicate line
`cells=12 mismatches=0 positive_mismatches=0 load_cells=12 load_stable=1` could not be met at M1 by the
frozen counter, for a reason that has nothing to do with the probe work being claimed.

Root cause, byte-level: the counter's `gguf_strbig()` writes a string array that **declares 6 000 000
elements but carries only one element's worth of payload**:

```python
out.append(struct.pack("<IIQ", 9, 8, 6_000_000))   # KV type 9 (array), elem type 8 (string), n = 6 000 000
out.append(struct.pack("<Q", 1) + b"x" * 6_000_000) # ONE u64 length + a 6 MB payload run
```

The probe's `skip_strings(n)` reads each element as `[u64 length][payload]` and guards
`if base + 8 * n > size: raise Bad()` — with `base = 49` and `n = 6 000 000` that is
`49 + 48 000 000 = 48 000 049 > 6 000 057`, so the file is graded **`invalid`** by the short-file
guard, *before* the step budget is ever consulted. Verified by parsing the counter's exact fixture
bytes: `base='invalid' tip='invalid'` — not `-`.

The counter's own `fixture_class` oracle cannot catch this: it special-cases
`if n_tensors == 0 and n_kv >= 1: return "-"` without parsing the array, so `build_fixtures`' self-check
passes on a fixture the probe grades `invalid`. The counter's docstring claim
("Element count > MAX_STEPS, so the probe's step budget governs the decision and grades `-`") is false
for its own bytes.

With the layout corrected to interleaved elements — `(struct.pack("<Q", 1) + b"x") * n`, 54 000 049
bytes — the same file grades `-` at both revisions, which is the documented W12 expectation.

## Ceiling: 833 333 is off by one; 833 332 is the true `nd = 1` ceiling

Measured by parsing generated fixtures at the tip revision (`gguf_parse`, tip bytes):

```
n=833331 -> 'invalid'   (decided)
n=833332 -> 'invalid'   (decided)   <- largest decidable nd=1 header count
n=833333 -> '-'         (undecidable)
```

`(5 000 000 - 4) // 6 = 833 332`. The plan, the counter's `fixture_class`
(`if n_tensors > 833_333: return "-"`), the SKILL.md table and the depth counter's `CEILING = 833_333`
all use 833 333. The 4 preamble steps are what the 833 333 figure drops.

**The L1 has since adopted 833 332** (amendment 2, `fb5cd3cd`): `tools/round96-depth-audit.py` now reads
`CEILING = 833_332  # (5_000_000 - 4) // 6 = 833 332 decidable headers (RV01 F3)`, and SKILL.md's
amended table generalises to `5 + nd` steps per header. That matches my independent measurement.

## Margin guard: the frozen control is host-speed dependent

The counter refuses to evaluate unless the W03 natural pass costs ≥ 1.25 × 60 s = 75 s. On this host the
frozen 40-file W03 costs ~49–67 s, so the guard fires and the counter exits **2 (could-not-evaluate)**
before printing a summary:

```
ROUTER_BUDGET96 could-not-evaluate: W03 natural pass 54.9s < 1.2 x 60s — the round-94 constant wrapper would not truncate this listing on this host, so no discriminator is claimed
```

Two consequences:

1. The committed base control (`controls/c1-base.out`, `w03_seconds=101.7`, `load1_nat=93.48`) was
   recorded on a heavily loaded host. The same command on a less loaded host returns exit 2, not the
   receipt. The base control is therefore not reproducible from its own receipt.
2. The message is inaccurate: it prints `1.2 x 60s` (`f"{MARGIN:.1f}"` of 1.25) but the comparison is
   against 75.0 s. The printed threshold and the enforced threshold disagree.

`--allow-clock` bypasses the guard without changing any cell grade (it only relaxes the *refusal to
evaluate*; the cells are graded from the probe's bytes either way), which is how I obtained the full
`mismatches=2` base figure. The L1 addressed the host-speed dependence in amendment 3 by making the
file count a receipt-named parameter (`--slow-files 96`).

## `positive_mismatches` was blind to the very cells that matter

At the freeze commit the counter counted a mismatch as "positive" only when
`cid.startswith("W0") and cid not in ("W09-undecided-big",)`. `W11-700k` and `W12-strings` both start
with `W1`, so **neither could ever raise `positive_mismatches`** — the counter that was supposed to
detect a wrongly-graded positive cell could not see W11 or W12 at all. That is why my base run reports
`mismatches=2 positive_mismatches=0`: two cells were wrong and the "positive" counter said zero.
Amendment 2 changed the rule to `if cid not in ("W09-undecided-big", "W12-strings")`, which does count
W11.

## C2 and C3 base controls (for the wave's other claims)

Run at the same base revision with the frozen bytes:

```
$ python3 tools/round96-depth-audit.py --repo . --rev 5d43528b
DEPTH_AUDIT checks=7 mismatches=6 met=False        EXIT=1
$ python3 tools/round96-disclosure-audit.py --repo . --rev 5d43528b
DISCLOSURE_AUDIT checks=5 mismatches=2 met=False   EXIT=1
```

Both red at base, matching the committed controls (amendment 1 re-committed them after the regex anchor
fix). At the amended tip both are green: `DEPTH_AUDIT checks=9 mismatches=0 met=True` and
`DISCLOSURE_AUDIT checks=6 mismatches=0 met=True`.

The C3 docstring-formula check is satisfied: the frozen counter's docstring says `20 + 25 * npaths` and
the wrapper literal is `local limit=$((20 + 25 * npaths))` (`tools/kama-probe.sh:871`).

## What changed under me, and what it means for this seat's question

The L1 amended the frozen counter **three times while this seat was measuring** (amendments 1–3,
`e2fed9f5` / `fb5cd3cd` / `b3289c18`). Kill rule K3 says "the counter changes after this commit"; the
counter's bytes changed, so K3 is a live question for the wave, not for my seat's base measurement — my
base numbers are pinned to the freeze bytes (`c1a7a84…`) and to the base probe bytes
(`b49d961a…`), and I report them as such.

Concretely, the amendments:

- **amendment 1** (`e2fed9f5`): anchored the `MAX_STEPS` regex. Instruments only.
- **amendment 2** (`fb5cd3cd`): repaired W12's fixture to 9-byte elements, generalised the step table to
  `5 + nd`, moved the ceiling to 833 332, and fixed `positive_mismatches` to count W11. **Its own W12
  repair was still wrong**: it wrote `struct.pack("<Q", 1) * n + b"x" * n` (all length prefixes first,
  then all payloads). The parser reads element 1's `u64` length as `0x0101010101010101`
  (72 340 172 838 076 673), which exceeds the file → `invalid` again. Verified:
  `base='invalid' tip='invalid'`.
- **amendment 3** (`b3289c18`): W12 written interleaved as `(struct.pack("<Q", 1) + b"x") * n`, and the
  W03 file count made a host-speed parameter.

With the amendment-3 bytes, my direct parse of the fixture gives `-` at both revisions (the documented
W12 expectation), so the W12 cell is repaired.

### Defect still visible at amendment 3: the "base control" is not run at the base

The L1's in-flight base control (process observed writing
`.ufo/waves/round-96/controls/c1-base.out`) runs:

```
python3 tools/round96-router-budget.py --repo . --rev b3289c18 --work /fast/scratch/hyaku/kama-r96 --burners 0 --allow-clock
```

`b3289c18` is **amendment 3 — the tip**, not the base `5d43528b`. The committed control's
`probe_sha256` is the base probe's (`b49d961a…`); `b3289c18`'s probe sha is `11e5b01b…`. The file it
is writing already shows `W11-700k ok=1` and `W12-strings ok=1` — a fully green run — which is what a
**tip** run looks like, not a base run. Committed under the name `c1-base.out`, that file would assert
the base control is green, i.e. that the counter cannot discriminate — the exact "claim is void"
condition the plan says invalidates the claim.

The base control must be run at `--rev 5d43528badc31ad6c0ca1848c00561f531924e4d`. My run above is that,
and it reddens W11 (and W12, at the freeze bytes).

## Verdict for this seat

1. **W11 reddens at base — the claim is not void.** The counter discriminates: base
   `mismatches=2` (W11-700k, W12-strings) vs tip `mismatches=1` (W12 only) at the freeze bytes. The C1
   substance — `MAX_STEPS` 4 000 000 → 5 000 000 making the 700 000-tensor file decide `invalid`
   instead of `-`/loadable — is confirmed by direct parser measurement and by the counter's W11 cell.
2. **With the frozen counter bytes the frozen predicate was unreachable at M1** (`mismatches=1`, K1),
   because W12's fixture is malformed and the counter's own oracle cannot detect it. That is a defect
   in the instrument, not in the claimed work; amendments 2 and 3 fix the fixture (amendment 2's first
   attempt was still wrong).
3. **The ceiling is 833 332, not 833 333** (the 4 preamble steps), and the `nd = 1` header cost is 6
   steps only because `nd = 1`; the general cost is `5 + nd`. The L1's amended SKILL.md table and depth
   counter now match my measurement.
4. **`positive_mismatches` could not see W11 or W12** at the freeze commit (`startswith("W0")`), so the
   "positive mismatch" counter reported 0 while two cells were wrong.
5. **The frozen base control is not reproducible from its own receipt**: the W03 margin guard is
   host-speed dependent, and its message prints `1.2 x 60s` while enforcing 75 s.
6. **The base control must be re-run and committed at the base revision.** The in-flight
   `controls/c1-base.out` is being produced at `--rev b3289c18` (tip) and shows an all-green run; if
   committed as the base control it would assert the void condition.

## Remaining unknowns / not exercised here

- I did not exercise the full live `--burners 64` load pass for the final amended counter at tip; the
  `--burners 0` runs I made exercise both passes (natural + a second pass) with the summary counters
  identical in shape.
- The `--slow-files 96` sizing that amendment 3 adopts depends on this host's ~1.2 s/file rate; on a
  materially different host the guard threshold moves again. I did not test a second host.
- `KILL = 1200` (vs round 95's `KILL = 400`) is a code constant; I confirmed the constant changed and
  that the wrapper's derived limit is `20 + 25 * npaths`, but I did not measure a pass that ran near
  1200 s.
- I did not evaluate C3's third check (`router-byte-decided` evidence pointer resolves at or before the
  tip) beyond reading the amended disclosure counter's source; that is EX02's slice.

## Commands run (all read-only against the lane; only my scratch and my out dir were written)

```
python3 tools/round96-router-budget.py --repo <lane> --rev 5d43528badc31ad6c0ca1848c00561f531924e4d \
  --work <scratch>/work-base-full --burners 0 --allow-clock
python3 tools/round96-router-budget.py --repo <lane> --rev 58001b71 \
  --work <scratch>/work-tip-full --burners 0 --allow-clock
python3 tools/round96-router-budget.py --repo <lane> --rev 5d43528badc31ad6c0ca1848c00561f531924e4d \
  --work <scratch>/work-a3-base --burners 0 --slow-files 96 --allow-clock
python3 tools/round96-depth-audit.py --repo . --rev 5d43528b
python3 tools/round96-disclosure-audit.py --repo . --rev 5d43528b
```

No tracked lane file was edited, no commit/push/jj mutation was run, and no file outside my scratch and
my out dir was written.

## Addendum — the L1's base control was destroyed by a shared-scratch collision (observed)

While this seat was measuring, the two receipt files the L1 was producing were both truncated:

- `.ufo/waves/round-96/controls/c1-base.out` now begins with a Python traceback ending
  `FileNotFoundError: ... /fast/scratch/hyaku/kama-r96/r96-budget-2kmwolzd/nat/slow_15.gguf`
- `.ufo/waves/round-96/measured/c1.out` ends with
  `FileNotFoundError: ... PosixPath('/fast/scratch/hyaku/kama-r96/r96-budget-epyftgkv/probe-cwd')`

Cause: the counter creates its run dir as `tempfile.mkdtemp(prefix="r96-budget-", dir=a.work)`
(`tools/round96-router-budget.py:431`) and removes it in a `finally: shutil.rmtree(...)` (line 460).
Both of the L1's runs were launched with `--work /fast/scratch/hyaku/kama-r96` — the **shared lane
scratch root**, not a seat-private subdirectory. Every other seat in this wave used a private
subdirectory (`.../SB01LessonDraft/work`, `.../SN01VerdictBoundary/c1work5`,
`.../SC02BaseDiscriminator/work-a3-base`). When a seat cleans up its own scratch tree, the shared
root's `r96-budget-*` entries are collateral, and both in-flight runs died mid-pass.

Two consequences for the wave:

1. **`controls/c1-base.out` currently holds a traceback, not a receipt.** It must be regenerated with a
   private `--work` (e.g. `--work /fast/scratch/hyaku/kama-r96/KamaR96/base`).
2. **`measured/c1.out` is also truncated** — its last cell line is W04, with no summary line, so the
   M1 receipt is incomplete and cannot be read as `mismatches=0` evidence.

My own runs used seat-private `--work` directories throughout and were unaffected.

## Confirmation of the amended counter at the tip (amendment-3 bytes)

Run at `--rev b3289c18` with the amendment-3 counter, both passes, `--burners 0 --allow-clock`:

```
ROUTER_BUDGET96_CELL load W11-700k ok=1 want=MODEL_UNLOADED/router-model-invalid run1=MODEL_UNLOADED/router-model-invalid/4.09s run2=MODEL_UNLOADED/router-model-invalid/3.44s
ROUTER_BUDGET96_CELL load W12-strings ok=1 want=MODEL_OK/router-unloaded-autoload run1=MODEL_OK/router-unloaded-autoload/1.80s run2=MODEL_OK/router-unloaded-autoload/2.01s
ROUTER_BUDGET96_CELL load W10-rewrite ok=1 v1=MODEL_UNLOADED/router-model-invalid v2=MODEL_OK/router-unloaded-autoload v3=MODEL_UNLOADED/router-model-invalid
ROUTER_BUDGET96 cells=12 mismatches=0 positive_mismatches=0 load_cells=12 load_stable=1 budget=work probe=rev probe_sha256=11e5b01b8d01b5c56ad0200f04c0871a95d398eafc71a3819cb2629fc561e709 base_sha256=27065a5c487ec819a975cc96d3c990ab5161d0e55d82be02a87dde86974ed3b4 rev=b3289c18ba1a2504afc3afe3c982ce6304876c5b w03_seconds=50.9 load1_nat=66.78 burners=0
EXIT=0
```

So with the amendment-3 counter the tip is green (`mismatches=0`, exit 0) and W12 grades as the plan
documents. The defect I reported (W12's malformed fixture) is repaired in the amendment-3 bytes, and
the C1 claim's substance is confirmed at both ends: base reddens W11, tip is green.

## Not completed (budget)

- The **`--slow-files 96` base run at the amendment-3 counter** (my `work-a3-base`) was still in flight
  when the budget closed; it is the one number that would show the amended counter reddening W11 at
  the base revision end-to-end through the probe. The parser-level equivalent is already measured and
  reported above (`base='-'` for the 700k-tensor file → `MODEL_OK/router-unloaded-autoload`), and the
  freeze-bytes end-to-end base receipt (`mismatches=2`, W11 + W12 red) is complete above.
- The **full `5 + nd` table sweep** (nd = 0…4 against the amended SKILL.md rows) was still running.
  The `nd = 1` row (833 332) is confirmed exactly; the other rows are unverified by me and are not
  asserted here.

## Addendum 2 — NEW DEFECT: the amended SKILL.md table's `nd = 3` row is off by one (625,000 → 624,999)

Amendment 2 replaced the single "6 steps per tensor header" sentence with a `5 + nd` table and a
formula, `(5 000 000 - 4) / (5 + nd)`. I verified every row by binary-searching the largest decidable
header count at the tip revision (parse the generated fixture, `gguf_parse` on the tip's own
`ROUTER_PY`; decided = `'invalid'`, undecidable = `'-'`):

| `nd` | SKILL.md says | measured max decidable | `(5 000 000 - 4) // (5 + nd)` | agrees? |
|---|---|---|---|---|
| 0 | 999,999 | 999,999 | 999,999 | OK |
| 1 | 833,332 | 833,332 | 833,332 | OK |
| 2 | 714,285 | 714,285 | 714,285 | OK |
| **3** | **625,000** | **624,999** | **624,999** | **MISMATCH — off by one** |
| 4 | 555,555 | 555,555 (n=555,554 and 555,555 both decided; 555,556 undecidable) | 555,555 | OK |

Boundary confirmation for the failing row (tip revision, `MAX_STEPS = 5 000 000`, 8 steps per header
plus 4 preamble steps):

```
n = 624,999 -> 'invalid'   (decided)
n = 625,000 -> '-'         (undecidable)
```

So 625,000 headers of rank 3 need `4 + 8 × 625 000 = 5 000 004` steps and do **not** fit the budget;
the true decidable ceiling is **624,999**. The table's `625,000` is the naive `5 000 000 // 8` — the
preamble subtraction was applied to rows 0, 1, 2 and 4 but missed on row 3.

**The frozen C2 counter hard-codes the wrong number as a required needle**, so it grades the wrong
value as correct (`tools/round96-depth-audit.py`):

```python
("833,332", "ceiling"),
("714,285", "nd2-ceiling"),
("625,000", "nd3-ceiling"),     # <- should be 624,999
("555,555", "nd4-ceiling"),
```

`DEPTH_AUDIT` therefore prints `checks=9 mismatches=0 met=True` at the tip while the SKILL.md table
states a figure the code does not enforce — the exact class of defect C3 exists to catch (a filing
that disagrees with the bytes beside it), and the C2 counter is the instrument that blesses it. The
same off-by-one appears in the depth counter's own docstring, which still says "ceiling 833 333"
(`tools/round96-depth-audit.py:11`) while its constant is `CEILING = 833_332`.

This is a defect in the landed work (the C2 table) that the wave's own instruments currently grade
green. It needs the nd=3 row corrected to 624,999 in both SKILL.md and the depth counter's needle
list, plus the depth counter's docstring ceiling restated as 833 332.

## Addendum 3 — my base run at the amendment-3 counter (base revision, `--slow-files 96`)

My `work-a3-base` run at `--rev 5d43528badc31ad6c0ca1848c00561f531924e4d` with the amendment-3 counter
completed its natural pass before the shared-scratch collision killed it in the load pass:

```
ROUTER_BUDGET96_CELL nat W03-slow-x40 ok=1 want=MODEL_UNLOADED/router-model-invalid run1=MODEL_UNLOADED/router-model-invalid/163.41s run2=MODEL_UNLOADED/router-model-invalid/324.20s
ROUTER_BUDGET96_CELL nat W04-ok-x8 ok=1 want=MODEL_OK/router-unloaded-autoload run1=MODEL_OK/router-unloaded-autoload/0.18s run2=MODEL_OK/router-unloaded-autoload/0.17s
ROUTER_BUDGET96_CELL nat W05-slow-then-ok ok=1 want=MODEL_OK/router-unloaded-autoload run1=MODEL_OK/router-unloaded-autoload/9.15s run2=MODEL_OK/router-unloaded-autoload/8.87s
ROUTER_BUDGET96_CELL nat W06-missing-x8 ok=1 want=MODEL_UNLOADED/router-model-missing run1=MODEL_UNLOADED/router-model-missing/0.15s run2=MODEL_UNLOADED/router-model-missing/0.13s
ROUTER_BUDGET96_CELL nat W07-fast-k40 ok=1 want=MODEL_UNLOADED/router-model-invalid run1=MODEL_UNLOADED/router-model-invalid/0.14s run2=MODEL_UNLOADED/router-model-invalid/0.14s
ROUTER_BUDGET96_CELL nat W08-hardlink-x8 ok=1 want=MODEL_UNLOADED/router-model-invalid run1=MODEL_UNLOADED/router-model-invalid/1.57s run2=MODEL_UNLOADED/router-model-invalid/1.47s
ROUTER_BUDGET96_CELL nat W09-undecided-big ok=1 want=MODEL_OK/router-unloaded-autoload run1=MODEL_OK/router-unloaded-autoload/0.19s run2=MODEL_OK/router-unloaded-autoload/0.13s
ROUTER_BUDGET96_CELL nat W11-700k ok=0 want=MODEL_UNLOADED/router-model-invalid run1=MODEL_OK/router-unloaded-autoload/1.60s run2=MODEL_OK/router-unloaded-autoload/1.71s
ROUTER_BUDGET96_CELL nat W12-strings ok=1 want=MODEL_OK/router-unloaded-autoload run1=MODEL_OK/router-unloaded-autoload/0.71s run2=MODEL_OK/router-unloaded-autoload/0.72s
ROUTER_BUDGET96_CELL nat W10-rewrite ok=1 v1=MODEL_UNLOADED/router-model-invalid v2=MODEL_OK/router-unloaded-autoload v3=MODEL_UNLOADED/router-model-invalid
```

**This is the end-to-end base discrimination, with the amended counter: W11-700k reddens (ok=0) and
W12-strings is green (ok=1)** — exactly the shape the plan wants: the base control reddens the
discriminator and only the discriminator. With the freeze-bytes counter the base reddens W11 **and**
W12; with the amended counter the base reddens W11 alone.

The run then died in the load pass with
`FileNotFoundError: .../work-a3-base/r96-budget-3cu80ubd/load/slow_88.gguf` — the same shared-scratch
collision that destroyed the L1's two receipts (a sibling seat's cleanup removed the lane scratch
root while this run was writing into it). The natural pass above is complete and unaffected.

Note also `W03` at `--slow-files 96` cost 163 s / 324 s here (vs ~49-67 s at 40 files), confirming
amendment 3's `--slow-files 96` sizing clears the 75 s guard on this host — and showing how strongly
the guard threshold moves with the host's load.

## Final state of the base-control question

| counter bytes | base revision | tip revision | W11 at base | W12 at base | base outcome |
|---|---|---|---|---|---|
| freeze (`c1a7a84…`) | 5d43528b | 58001b71 | red (ok=0) | red (ok=0) | `mismatches=2`, exit 1 |
| amendment 3 (`f2823df…`) | 5d43528b | b3289c18 | red (ok=0) | green (ok=1) | W11 red alone; tip `mismatches=0`, exit 0 |

**W11-700k reddens at base under both counter versions.** The counter discriminates; the C1 claim is
not void on the base-control test.

## Addendum 4 — the nd=3 defect was adopted as amendment 4 and the depth audit is green again

After my report, the L1 landed `20317286 round-96: amendment 4 (nd=3 ceiling 624,999; per-rank
arithmetic checks)`. At the new HEAD:

```
$ python3 tools/round96-depth-audit.py --repo . --rev HEAD
DEPTH_AUDIT checks=14 mismatches=0 met=True     EXIT=0
```

and every row of the amended SKILL.md table now matches the arithmetic the parser enforces
(`(5 000 000 - 4) // (5 + nd)`), with the counter itself checking each rank rather than only nd=1:

| `nd` | steps/header | SKILL.md (HEAD) | `(5 000 000 - 4) // (5 + nd)` | measured max decidable |
|---|---|---|---|---|
| 0 | 5 | 999,999 | 999,999 | 999,999 |
| 1 | 6 | 833,332 | 833,332 | 833,332 |
| 2 | 7 | 714,285 | 714,285 | 714,285 |
| 3 | 8 | **624,999** (was 625,000) | 624,999 | 624,999 |
| 4 | 9 | 555,555 | 555,555 | 555,555 |

The counter's needle list now reads `("624,999", "nd3-ceiling")` and it grades each rank's arithmetic
against the skill text, so the off-by-one I found can no longer pass green.

**My nd=4 row is measured, not inferred:** at the tip revision, n = 555,554 and n = 555,555 both
grade `'invalid'` (decided) and n = 555,556 grades `'-'` (undecidable) — 555,555 is the true nd=4
ceiling, matching the table.

## State of the lane at my exit (for whoever picks this up)

- `tools/round96-depth-audit.py`, `SKILL.md`: nd=3 corrected, per-rank checks added, audit green
  (`checks=14 mismatches=0 met=True`).
- `.ufo/waves/round-96/controls/c1-base.out`: **still being written** by the L1's re-run; it had no
  summary line when I finished. It must be checked for (a) a `rev=` of the BASE revision
  `5d43528badc31ad6c0ca1848c00561f531924e4d` with `probe_sha256=b49d961a…`, and (b) `nat W11-700k ok=0`
  — W11 must redden at base. If it comes back `ok=1` at base, the base control is measuring the tip
  again.
- `.ufo/waves/round-96/measured/c1.out`: **still a traceback** (the scratch collision). It must be
  regenerated with a seat-private `--work`.
- `.ufo/waves/round-96/controls/c2-base.out`: modified in the worktree; I did not audit its contents.

The scratch-collision hazard remains live: the counter's `--work` must be a seat-private subdirectory
for any run whose receipt is kept.
