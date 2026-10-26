# M1Ctr — round 48 w1 — C1 counter mutation test (`tools/round48-append-audit-v3-check.py`)

**Verdict: no defect found in the frozen C1 counter — its verdict is correct on every probe input (the tip run reproduces the L1 dry run exactly; all three controls are rejected). 52 mutants: 28 killed, 3 equivalent by construction, 21 survived as coverage gaps — and 10 of those 21 are demonstrated killable by one proposed fixture-leg fix. Dominant blind spot: the fixture leg never cross-checks the counter's own recompute against the tool, and every event on every probe input is `status=restored` with `held_at_to == restored_max == graded`, so counter-side logic for partial / unrestored / ungraded / negative-held / threshold-boundary states is unobservable.**

## Method

- Pristine copy of the counter at `$S/pristine.py`, sha256 `92b0f9f1027b8214c7a702d928f89e5a6d9fb814fc565c234f6deee3f2d82ac7` — identical before and after the campaign (re-verified at the end).
- One live clone: `git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin $S/lane` (toplevel asserted = the clone). Only read-only git ran against it; the lane repo itself was never written.
- Controls rebuilt into scratch with a scratch copy of `.ufo/waves/round-48/controls/build_controls.py` (its receipts land beside the copy, not in the lane): `v2-relabel` @ `adb2ba7f6215fce637621f2dce080ec44b95f084`, `drop-scorecard` @ `4aead806ce915ec3265e3a15cd427920c06eee1a`.
- Probe inputs (invocation `python3 <counter> --repo R --tip T --scratch $S/runs/<tag>`):
  1. `tip` — lane clone @ `380bcdff9c8af06997c482f6eb03db926a794a2b`
  2. `base` — lane clone @ `33e005827742b29772b153cda036ec9f27f653be`
  3. `v2relabel` — control clone @ `adb2ba7f…`
  4. `dropscore` — control clone @ `4aead806…`
- 52 mutants, one minimal replacement each; every old string asserted to occur exactly once (52/52 applied, 0 apply failures). Each mutant ran all four inputs; afterwards the pristine bytes were written back over the mutant path and hash-verified — 52/52 `restored_ok` (`results.json`).
- Detection: per input, exit code + stdout compared to the pristine reference after replacing `[0-9a-f]{7,40}` → `H` (fixture commit hashes legitimately differ per run). Killed = any difference on any input (tip flip, control leniency flip, or output-only change); survived = identical normalized output and exit on all four inputs.
- Baseline check ran first (`BASELINE_OK=True`); a baseline failure would have made every result inconclusive — it did not occur.

## Pristine baselines (all four inputs)

| input | exit | first line |
|---|---|---|
| tip | 0 | `selftest=1 contract=1 lane=1 fixture=1 stable=1 rows=9 files=89 lane_events=5 lane_failures=0 ungraded_lines=89 fixture_fail=0 met=True` |
| base | 1 | `selftest=0 contract=0 lane=0 fixture=0 stable=0 rows=0 files=0 … met=False` — `contract: header is not the v3 header (or CR present)`, `stable: base equals tip` |
| v2relabel | 1 | `selftest=0 contract=0 lane=0 fixture=0 stable=0 rows=9 files=89 lane_events=5 lane_failures=0 ungraded_lines=89 … met=False` |
| dropscore | 1 | `selftest=0 contract=0 lane=0 fixture=0 stable=0 rows=8 files=88 lane_events=3 lane_failures=0 ungraded_lines=0 … met=False` — `contract: required row SCORECARD.md missing` |

The tip line reproduces the L1 pre-wave dry run field-for-field. Raw outputs: `runs/pristine__{tip,base,v2relabel,dropscore}.txt`.

Why the survivors survive — measured at the tip with the v3 tool (`tip-tool.json`): all 5 lane events are `status=restored` with `held_at_to == restored_max == graded` (deleted 31 / 2292 / 2421 / 375 / 663; ungraded lines 17 + 72 = 89); the v2-relabel and drop-scorecard controls likewise have only restored events (`lane_failures=0`, `ungraded_lines` 89 / 0), and the base control never reaches `recompute` (v2 contract header rejected). On every probe input the counter's recompute therefore exercises only the restored branch of every definition.

## Results (52 mutants)

Columns: exit code per input; `→` marks a change vs the pristine reference on that input (the detection).

| # | mutant | area | tip | base | v2relabel | dropscore | verdict | detection |
|---|---|---|---|---|---|---|---|---|
| 1 | `A1-threshold-21` | threshold | 0 | 1 | 1 | 1 | **survived** |  |
| 2 | `A2-threshold-19` | threshold | 0 | 1 | 1 | 1 | **survived** |  |
| 3 | `A3-threshold-le` | threshold | 0 | 1 | 1 | 1 | **survived** |  |
| 4 | `B1-hunk-regex-comma` | hunk-position parse | 0→1 | 1 | 1→1 | 1→1 | **killed** | tip exit 0->1; v2relabel output-only exit=1->1; dropscore output-only exit=1->1 |
| 5 | `B2-hunk-count-minus1` | hunk-position parse | 0→1 | 1 | 1→1 | 1→1 | **killed** | tip exit 0->1; v2relabel output-only exit=1->1; dropscore output-only exit=1->1 |
| 6 | `B3-hunk-plus-side` | hunk-position parse | 0→1 | 1 | 1→1 | 1→1 | **killed** | tip exit 0->1; v2relabel output-only exit=1->1; dropscore output-only exit=1->1 |
| 7 | `C1-neg-drop-notappendonly` | NEG list | 0 | 1 | 1 | 1 | **survived** |  |
| 8 | `C2-neg-first-only` | NEG list | 0 | 1 | 1 | 1 | **survived** |  |
| 9 | `C3-neg-check-dropped` | NEG list | 0 | 1 | 1 | 1 | **survived** |  |
| 10 | `D1-token-wildcard-base` | token() | 0 | 1 | 1 | 1 | **survived** |  |
| 11 | `D2-token-keep-ext` | token() | 0→1 | 1 | 1→1 | 1→1 | **killed** | tip exit 0->1; v2relabel output-only exit=1->1; dropscore output-only exit=1->1 |
| 12 | `E1-binds-drop-selfdecl` | binds() self-declaration | 0→1 | 1 | 1→1 | 1→1 | **killed** | tip exit 0->1; v2relabel output-only exit=1->1; dropscore output-only exit=1->1 |
| 13 | `E2-binds-eq-not-fnmatch` | binds() self-declaration | 0→1 | 1 | 1→1 | 1→1 | **killed** | tip exit 0->1; v2relabel output-only exit=1->1; dropscore output-only exit=1->1 |
| 14 | `F1-region-title-hash-dropped` | region regex | 0 | 1 | 1 | 1 | **survived** |  |
| 15 | `F2-region-pointer-plus1` | region regex | 0→1 | 1 | 1→1 | 1→1 | **killed** | tip exit 0->1; v2relabel output-only exit=1->1; dropscore output-only exit=1->1 |
| 16 | `G1-required-drop-errata` | REQUIRED regions | 0 | 1 | 1 | 1 | **survived** |  |
| 17 | `G2-required-titles-drop-cap` | REQUIRED regions | 0→1 | 1 | 1→1 | 1 | **killed** | tip exit 0->1; v2relabel output-only exit=1->1 |
| 18 | `G3-required-kind-only` | REQUIRED regions | 0 | 1 | 1 | 1 | **survived** |  |
| 19 | `H1-eligible-gt` | eligibility >= | 0→1 | 1 | 1→1 | 1 | **killed** | tip exit 0->1; v2relabel output-only exit=1->1 |
| 20 | `H2-eligible-always` | eligibility >= | 0→1 | 1 | 1→1 | 1 | **killed** | tip exit 0->1; v2relabel output-only exit=1->1 |
| 21 | `I1-only-filter-dropped` | graded filter only/exempt | 0 | 1 | 1 | 1 | **survived** |  |
| 22 | `I2-exempt-filter-dropped` | graded filter only/exempt | 0→1 | 1 | 1→1 | 1 | **killed** | tip exit 0->1; v2relabel output-only exit=1->1 |
| 23 | `J1-clamp-max0-dropped` | held clamp | 0 | 1 | 1 | 1 | **survived** |  |
| 24 | `J2-clamp-min-dropped` | held clamp | 0→1 | 1 | 1→1 | 1→1 | **killed** | tip exit 0->1; v2relabel output-only exit=1->1; dropscore output-only exit=1->1 |
| 25 | `K1-restoredby-drop-ng` | restored_by | 0 | 1 | 1 | 1 | **survived** |  |
| 26 | `K2-best-geq-tie-last` | restored_by | 0→1 | 1 | 1→1 | 1 | **killed** | tip exit 0->1; v2relabel output-only exit=1->1 |
| 27 | `K3-restoredbest-swap` | restored_by | 0→1 | 1 | 1→1 | 1 | **killed** | tip exit 0->1; v2relabel output-only exit=1->1 |
| 28 | `K4-restoredby-geq` | restored_by | 0 | 1 | 1 | 1 | **survived** |  |
| 29 | `L1-status-labels-swapped` | status classes | 0 | 1 | 1 | 1 | **survived** |  |
| 30 | `L2-status-partial-dead` | status classes | 0 | 1 | 1 | 1 | **survived** |  |
| 31 | `M2-regressed-le` | regressed formula | 0→1 | 1 | 1→1 | 1→1 | **killed** | tip exit 0->1; v2relabel output-only exit=1->1; dropscore output-only exit=1->1 |
| 32 | `M3-regressed-partial-dropped` | regressed formula | 0 | 1 | 1 | 1 | **survived** |  |
| 33 | `N1-exit-always0` | exit derivation | 0 | 1→0 | 1→0 | 1→0 | **killed** | base leniency flip exit=0; v2relabel leniency flip exit=0; dropscore leniency flip exit=0 |
| 34 | `N2-exit-always1` | exit derivation | 0→1 | 1 | 1 | 1 | **killed** | tip exit 0->1 |
| 35 | `N3-met-drop-stable` | exit derivation | 0 | 1 | 1 | 1 | **survived** |  |
| 36 | `N4-selftest-threshold-1` | exit derivation | 0 | 1→1 | 1 | 1→1 | **killed** | base output-only exit=1->1; dropscore output-only exit=1->1 |
| 37 | `N5-met-drop-fixture` | exit derivation | 0 | 1 | 1 | 1 | **survived** |  |
| 38 | `N6-derivedexit-drop-regressed` | exit derivation | 0 | 1 | 1→1 | 1 | **killed** | v2relabel output-only exit=1->1 |
| 39 | `O1-s1-expect-deleted19` | fixture expectations | 0→1 | 1 | 1→1 | 1 | **killed** | tip exit 0->1; v2relabel output-only exit=1->1 |
| 40 | `O2-s6-expect-restmax10` | fixture expectations | 0→1 | 1 | 1→1 | 1 | **killed** | tip exit 0->1; v2relabel output-only exit=1->1 |
| 41 | `O3-s11-nev-3` | fixture expectations | 0→1 | 1 | 1→1 | 1 | **killed** | tip exit 0->1; v2relabel output-only exit=1->1 |
| 42 | `O4-nt-eq-10` | nt == 11 | 0→1 | 1 | 1 | 1 | **killed** | tip exit 0->1 |
| 43 | `O6-nt-check-dropped` | nt == 11 | 0 | 1 | 1 | 1 | **survived** |  |
| 44 | `P1-stablekeys-drop-best` | stable keys | 0 | 1 | 1 | 1 | **survived** |  |
| 45 | `Q1-ung-geq0` | ungraded_lines > 0 | 0 | 1 | 1 | 1→1 | **killed** | dropscore output-only exit=1->1 |
| 46 | `R1-K-nosub` | recompute internals | 0→1 | 1 | 1→1 | 1→1 | **killed** | tip exit 0->1; v2relabel output-only exit=1->1; dropscore output-only exit=1->1 |
| 47 | `R3-psec-child` | recompute internals | 0→1 | 1 | 1→1 | 1→1 | **killed** | tip exit 0->1; v2relabel output-only exit=1->1; dropscore output-only exit=1->1 |
| 48 | `R4-sections-hash1` | recompute internals | 0→1 | 1 | 1→1 | 1 | **killed** | tip exit 0->1; v2relabel output-only exit=1->1 |
| 49 | `R5-sections-nostrip` | recompute internals | 0 | 1 | 1 | 1 | **survived** |  |
| 50 | `R7-files-unsorted` | recompute internals | 0→1 | 1 | 1→1 | 1 | **killed** | tip exit 0->1; v2relabel output-only exit=1->1 |
| 51 | `R8-vanished-empty` | recompute internals | 0 | 1 | 1 | 1 | **survived** |  |
| 52 | `R8b-vanished-list-memb` | recompute internals | 0 | 1 | 1 | 1 | **survived** |  |

Totals: {'survived': 24, 'killed': 28} — 52 mutants, all applied, all restored (52/52 `restored_ok`).

## Findings — survivors are coverage gaps in the frozen counter; fixes are proposals for the next round, not in-place edits

**F1 — headline (kills 10 survivors): the fixture leg never cross-checks the counter's own recompute against the tool.** `fixture_leg` (`tools/round48-append-audit-v3-check.py:594-620`) validates the tool only against by-construction expectations; the recompute-vs-tool `diff_result` exists only in the lane leg (`:717`), and the lane's 5 events exercise only the restored branch (see baselines). Proposed fix — insert after the summary checks in `fixture_leg` (`:614-617`):

```python
            try:
                rows_fx, _why = parse_contract(open(os.path.join(repo, CONTRACT),
                                                    encoding="utf-8", errors="replace").read())
                if rows_fx is not None:
                    rcx = recompute(repo, "HEAD", rows_fx)
                    fxm = diff_result(j, rcx, code, [], "fxrecomp")
                    if fxm:
                        probs.append(f"counter-recompute-vs-tool mismatches {fxm}")
            except EvalError as exc:
                probs.append(f"counter recompute failed: {exc}")
```

Demonstrated (`demo_fixture_recompute.json`): **patch-only stays `met=True` exit 0** (`fixture=1`, all legs green — the patch itself is sound); patch + survivor flips each to `met=False` exit 1:

| survivor | fixture that catches it | mechanism |
|---|---|---|
| A1 threshold 21 | threshold, only-errata, regressed, dashdash-crlf, clean (5) | recompute drops every `deleted=20` event |
| A2 threshold 19 | threshold | recompute adds the `deleted=19` event |
| A3 `nd <= THRESHOLD` | same 5 as A1 | drops every `deleted=20` event |
| C1 NEG minus `not append-only` | bad-declarations | counter `bad_declarations`=2 vs tool 3 |
| C3 negation check dropped | bad-declarations | counter `bad_declarations`=2 vs tool 3 |
| I1 only-filter dropped | only-errata | body deletion graded 25 vs tool 0 (6 mismatches) |
| J1 clamp `max(0,.)` dropped | clamp | `restored_max` 10 vs 20, `held_at_to` 10 vs 20 |
| K1 `restored_by` without `ng` guard | exempt-rewritten, only-errata, clean | `restored_by`=commit vs tool `None` on `ng==0` events |
| L1 status labels swapped | 7 fixtures | unrestored ↔ partial labels |
| L2 `best < ng` → unrestored | clamp | partial event relabeled unrestored |

**F2 — threshold boundary untested on the measured lane (A1, A2, A3 — killed by F1's fix).** The counter's own `THRESHOLD = 20` (`:137`) is observable only through lane events, and no event on any probe input has `deleted` ∈ {19, 20, 21} (tip events: 31, 2292, 2421, 375, 663). Killing case = F1's patch (demonstrated).

**F3 — NEG-list leniency invisible counter-side (C1, C2, C3).** `binds()` (`:226-233`) leniency never flips a verdict: every contract row binds at the tip, and S10's `bad_declarations` are computed by the unmutated tool. C1/C3 killed by F1's patch (demonstrated). **C2 survives even that** (`NEG[:1]` still contains S10's only negation, `not append-only`). Killing case for C2: extend fixture S10 with a second negation form — row `ledger3.md	A	NOTES.md:8	*	fixture` with `NOTES.md:8` = `ledger3.md is no longer append-only.` → pristine counter bad=4 = tool 4; C2 counter bad=3 → mismatch → killed.

**F4 — `only=` region filter untested on the lane (I1 — killed by F1's fix).** No probe input has an event in an `only=`-region file (`corpus/knowledge/consumer-registry.md` has no ≥20-line deletion in any window), so the `only_prefixes` filter (`:356`) never fires outside fixtures — and fixtures never run the counter's recompute (F1). Killing case = F1's patch (demonstrated, 6 mismatches on only-errata).

**F5 — `max(0, .)` clamp untested counter-side (J1 — killed by F1's fix); `min(n, .)` is tested (J2 killed on the lane).** Every probe event is restored with `held == restored_max`, where dropping the clamp is termwise inert (`h` can only decrease, and the commit achieving `ng` still achieves it). The lane does exercise over-restoration (`M[l]−K[l] > n`: J2's `min` drop flips the tip verdict) but never under-restoration (`M[l]−K[l] < 0`). Killing case = F1's patch on S6 (demonstrated: `restored_max` 10 vs 20).

**F6 — `restored_by` on `ng == 0` events (K1 — killed by F1's fix).** No probe event has `graded == 0`, so the `ng and` guard (`:369`) is unobservable. Killing case = F1's patch (demonstrated).

**F7 — status labels (L1, L2 — killed by F1's fix).** No probe event has `best == 0` (unrestored) or is partial, so the label choices (`:374`) are unobservable on the lane. Killing case = F1's patch (demonstrated).

**F8 — `regressed` ignores partial events (M3 — survives even F1's fix).** S6's partial event has `held_at_to == restored_max` (not regressed) and S8's regressed event is restored-status, which M3 keeps. Killing case: new fixture S12 — `base = ["dup"]*30 + L("u",20)`; `c1 = ["dup"]*10` (deletes 40); `c2 = ["dup"]*15 + L("u",20)` (restores 25 → `restored_max`=25, status partial); `c3 = ["dup"]*10 + L("u",20)` (`held_at_to`=20 < 25 → regressed 1, status partial). Expect `{"partial": 1, "regressed": 1}`, exit 1; M3 recomputes `regressed`=0 → mismatch → killed.

**F9 — `met` conjunction mutants unobservable (N3 drops `stab`, N5 drops `fix`).** No probe input fails exactly one leg, so `met = bool(sel and con and lane and fix and stab)` (`:760`) tolerates dropping any single conjunct. Proposed controls for `build_controls.py`: a *stable-only* control — tip tree plus a tool patched to emit `restored_best: None` only when `--to` equals the base-hash literal → only the stable leg fails → N3 flips the control to `met=True`; a *fixture-only* control — tool patched to exit 2 on repos with ≤ 12 commits (fixtures are tiny; the lane has 311) → only the fixture leg fails → N5 flips.

**F10 — REQUIRED is only a lower bound (G1, G3).** The lane contract satisfies the strict check, so loosening it (`:140-146`, `:676-681`) is invisible. Killing cases: (a) G1 — assert the contract's row set equals `REQUIRED` exactly (no extra rows): the lane contract has exactly the 9 required rows (stays green), and dropping `registry/report-landing-errata.tsv` from REQUIRED leaves that row "extra" → `contract=0` → killed. (b) G3 — constructed input: lane clone + contract with `SCORECARD.md … exempt=## Wrong@SCORECARD.md:6` and `SCORECARD.md:6` rewritten to name `## Wrong` as re-derived → pristine: REQUIRED title mismatch → `contract=0`; G3: kind-only check passes, pointer binds, tool agrees → `met=True` → flip.

**F11 — region regex looseness (F1-mutant).** `parse_region` accepting titles without `## ` (`:176-177`) is unobservable: all probe titles start `## `, and a contract the tool rejects masks the difference at the lane level. Killing case: contract-leg unit assert — `parse_region("exempt=Axes@X:1") is None and parse_region("only=Errata@X:1") is None` must hold; the mutant makes it fail → `contract=0` → killed.

**F12 — wildcard token branch dead on all inputs (D1).** The lane's only wildcard row (`corpus/lessons/*.md`) self-matches via `fnmatch` — its declared_at line `corpus/lessons/round-23.md:100` is `are append-only.`, which contains neither `lessons` nor the path, so binding rests entirely on self-declaration — making the `parts[-2]` branch (`:213-214`) unobservable. Killing case: fixture row `corpus/lessons/*.md	A-corr	NOTES.md:8	*	fixture` with `NOTES.md:8` = `lessons are append-only.` → pristine binds via token `lessons`; D1 (token `*.md`) does not → counter bad=1 vs tool 0 → killed (with F1's patch).

**F13 — minor survivors.** O6 (`nt == 11` dropped from `fix`, `:733` — unobservable while there are exactly 11 scenarios; keep the assert and pin it to a frozen module-level tuple of the 11 scenario names). R5 (section-title `rstrip()` dropped, `:272` — no probe title has trailing whitespace; constructed input: fixture head section `## Axes ` (trailing space) + F1's patch → pristine eligible/ungraded, mutant graded → killed). R8 (`vanished` forced empty, `:308` — `vanished`=0 on every probe input; constructed input: a control commit deleting `registry/report-landing-errata.tsv` → pristine rc exit 1 == tool exit 1 with verdict False; R8 derives exit 0 ≠ tool exit 1 → `diff_result` detail → detection).

**Equivalents (3 — unobservable by construction, not coverage gaps):** K4 (`h >= ng` ≡ `h == ng`: `h = Σ min(n, ·) ≤ Σ n = ng`); R8b (`t not in files` ≡ `t not in set(files)`); P1 (dropping `restored_best` from the stable key tuple `:757`: `restored_best` is the *first* achiever of `restored_max`; the tip window ⊇ the base window, so equal maxima have equal first achievers, and differing maxima already fail on `restored_max`).

## Killed mutants (28) — representative detections

- **B1** hunk regex requires a comma → `lane: recomputation failed: dd9f5dc6c0e6 SCORECARD.md: hunk positions 29 != numstat 31` (tip exit 0→1) — incidentally proves the lane's dd9f5dc6 SCORECARD diff contains two comma-less single-line hunks, i.e. the comma-less branch *is* exercised on the lane.
- **B2** `cnt−1`, **B3** `+`-side positions → same recompute-failure class (tip exit 0→1).
- **D2** token keeps extension → the SOURCES row (`SKILL.md:578` says `SOURCES append-only guard`, no `sources.md`) stops binding → `contract=0`.
- **E1/E2** self-declaration dropped / `==` instead of fnmatch → `corpus/lessons/round-23.md:100` (`are append-only.`) stops binding → `contract=0`.
- **F2** region pointer +1 → `SCORECARD.md:7` is empty → pointer does not bind → `contract=0`.
- **G2** REQUIRED titles minus `## Capabilities` → REQUIRED mismatch → `contract=0`.
- **H1** `>=`→`>`, **H2** `>= 0` → eligibility flips on the lane (e.g. 0718b6ab SCORECARD graded 2349→2399, status restored→partial) → `lane=0`.
- **I2** exempt filter dropped → dd9f5dc6 graded 14→22 → `lane=0`.
- **J2** `min` dropped → held/restored_max inflate → `lane=0`.
- **K2** tie-last, **K3** `restored_best` swap → field mismatches → `lane=0`.
- **M2** `<`→`<=` → dd9f5dc6 (held 14 == max 14) becomes regressed → verdict fails → `lane=0`.
- **N1** exit always 0 → all three controls exit 0 (leniency flip). **N2** exit always 1 → tip exit 1.
- **N4** selftest `>= 1` → v2-tool controls report `selftest=1` (output-only detection).
- **N6** derived exit drops `regressed` → v2-relabel: derived exit 0 vs tool exit 1 → mismatch (output-only).
- **O1/O2/O3/O4** fixture-expectation and `nt` tampers → `fixture=0` at tip.
- **Q1** `ung > 0` → `ung >= 0` → drop-scorecard: lane verdict turns True (the `lane: derived verdict …` detail line disappears) — output-only detection.
- **R1** `K` not reduced, **R3** child sections, **R4** `# ` sections, **R7** unsorted files → lane mismatches.

## Commands

```
S=/fast/scratch/hyaku/kama-r48/M1Ctr; mkdir -p "$S"; export TMPDIR="$S"
cp /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round48-append-audit-v3-check.py $S/pristine.py
cp /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/controls/build_controls.py $S/
git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin $S/lane
python3 $S/build_controls.py /home/vgpnk/Projects/shokunin/kama-shokunin $S v2-relabel drop-scorecard
python3 $S/mut_driver.py     # baselines + 52 mutants × 4 inputs + restore/hash-verify → results.json
python3 $S/demo_kill.py      # killing-case demo: fixture-leg recompute cross-check
```

Tooling authorization: nothing installed or upgraded (no pacman, no uv, no binaries); stock python 3.14.8 and git only.

## Artifacts (all under `kama-shokunin/.ufo/waves/round-48/w1/out/M1Ctr/`)

- `results.json` — per mutant: area, old→new, mutant sha256, restored sha256 + `restored_ok`, per-input exit / first line / same-as-pristine, verdict, mechanism.
- `runs/` — raw stdout of every run: `pristine__<input>.txt` (4) and `<mutant>__<input>.txt` (208).
- `demo_fixture_recompute.json` — the F1 killing-case demo (patch-only green; 10 survivors flip).
- `junk-c1-v2-relabel.c1.out`, `junk-c1-drop-scorecard.c1.out` — my rebuilt control receipts (fresh commit hashes, same shape as the frozen ones).
- `tip-tool.json` — v3 tool JSON at the tip (the restored-only evidence).
- Report: `kama-shokunin/.ufo/waves/round-48/w1/out/M1Ctr.md`.

Scratch `/fast/scratch/hyaku/kama-r48/M1Ctr` is removed at the end; the lane repo and all frozen files untouched (read-only git only).
