# Round 64 · wave f · CR08C2DoNothingScan · C2 do-nothing control

Seat: CR08C2DoNothingScan (leaf member, no subagents). Axis: calibration. Milestone: C2 do-nothing control.
Lane: `/home/vgpnk/Projects/shokunin/kama-shokunin` (read-only for me). Base tip `0c1eff3cb9ac4c11402ab0124c35842f06a436fc`.
Scoring instrument: the **unmutated** `tools/round64-c2-counter.py` committed at the measured tip
`23b3fdb1a925129a9961cf551f6d40bf251602cb` (sha256 `c8b725e5…d93e2e`, verified equal to the freeze disclosure).
All variants were built and committed **only** in my scratch clone; nothing in the lane was touched
(`git status --porcelain` on the lane shows only other seats' `f/` files; the lane HEAD is `6203f6f5…`, unmodified by me).
Scratch: `/fast/scratch/hyaku/kama-r64/f/CR08C2DoNothingScan/` (removed at yield).
Evidence: `.ufo/waves/round-64/f/out/CR08C2DoNothingScan/`.
Tools installed: **none** (git 2.56.0, python3 3.14.8 stdlib, the counter itself). No pacman transaction.

## 1. What was built

Base tip + exactly **one** of the seven integration changes, each as its own commit (tree diff vs base verified
to be exactly the intended path list, `build_variants.py`):

| id | single change | commit |
|---|---|---|
| v1-claims | `registry/capability-claims-r64.tsv` | `14cfe7b65abe` |
| v2-regress | `registry/capability-regress-r64.tsv` | `edde67ff0afe` |
| v3-counter | `tools/round64-c2-counter.py` | `ca03ade07579` |
| v4-reconciler | `tools/round42-selfdesc-reconcile.py` | `b5c6da0e922` |
| v5-tally | `tools/shortcut-tally.py` | `9a3d9c07d9e5` |
| v6-canon | `SCORECARD.md` (base + the round-64 canonical-list section only) | `bb0a845789b4` |
| v6b-scorecard-full | `SCORECARD.md` (the tip's whole file) | `3562d1214160` |
| v6c-pointer-only | `SCORECARD.md` (only the calibration-row pointer repair) | `c469046ca4a9` |
| v7-hexrun-ledger | `registry/hexrun-ledger.tsv` | `37f504d5a563` |

Controls: **base** (`0c1eff3c`) and **full** (`23b3fdb1`) re-run for calibration.

## 2. Result: the do-nothing target holds — but not for the reason the brief expects

**All seven single-change variants print `met=False`.** No variant but the full set reaches `met=True`.
Base and full reproduce the frozen receipts exactly (`base` line byte-identical to `controls/c2-base.txt`;
full line byte-identical to `controls/c2-prewave-tip.txt`, 2 runs, `met=True` both).

**But the expected "a different failing field each" does not hold.** Two of the seven move **no field at all**,
and one crashes instead of scoring:

| variant | field movement vs base | verdict |
|---|---|---|
| v1-claims | `covered 0→12`, `mismatches 0→1`, `idle_ok 0→1`, `errors 2→1` | met=False |
| v2-regress | **no field line — the counter crashed** | met=False (by crash) |
| v3-counter | **none** (full stdout byte-identical to base) | met=False |
| v4-reconciler | `pinned 12→13`, `recon_mismatches 0→1` | met=False |
| v5-tally | `tally_disclosed 1→8`, `tally_selftest 0→1` | met=False |
| v6-canon | `population 0→12`, `recon_mismatches 0→2`, `errors 2→1` | met=False |
| v6b-scorecard-full | `population 0→12`, `errors 2→1` | met=False |
| v6c-pointer-only | none | met=False |
| v7-hexrun-ledger | **none** (full stdout byte-identical to base) | met=False |

## 3. Findings

### F1 (defect, fixable) — the counter crashes on a regress-table-only tree instead of scoring it

`v2-regress` prints `errors=1 met=False  (internal KeyError: 'reg-sources-registry')` — **no field line at all**,
reproduced twice. Traceback pins it to `tools/round64-c2-counter.py:1560`:

```python
mut_o = runner.outcome(cap, 'reg', runner.overlays['reg-' + cap])[0]
```

The `reg-<cap>` overlays are only built inside `if reg_text:` (line 1495), but the regress-flipped loop at
1553-1561 looks them up whenever `plan[cap]` yields a regression — which happens whenever the **regress table**
exists, independently of the registry. With the regress table present and the claims registry absent, the key
is missing. It is caught by the blanket `except` in `main()` and reported as an internal error, so the run
still exits 1 and still says `met=False` — the claim is not wrongly admitted — but the counter emits no
calibration fields at all, so a falsifier gets no field to name. **Smallest safe correction** (one condition,
in `fixes/fix-c2-counter.py`): `if data is not None and ('reg-' + cap) in runner.overlays:`. Verified: with it,
v2 prints a normal field line (`met=False`, `gate-misses` = base's ten) and the full tip still prints the
**byte-identical** `met=True` line. Both receipts in `runs/v2-regress-FIXED.out`, `runs/full-FIXED.out`.
Note the same latent key lookup is reachable at `runner.overlays['prn-'+cap]` in `printer_rejected()`; it is
currently guarded by `if reg_text and rtext`, so it does not fire, but it is the same shape.

### F2 (defect, fixable) — the counter does not pin its own bytes at the tip; a stub counter is accepted with `met=True`

The counter reads the 13 bound files at the tip by sha256 but never checks **its own** file
(`PINS` has 13 entries; `tools/round64-c2-counter.py` is not among them; `grep` for the path inside the
counter finds only the two docstring mentions). Two consequences:

1. `v3-counter` (the real counter added alone) is **byte-identical to the base run** — adding the instrument to
   the tree moves no field, because the instrument's own presence is not a graded artifact.
2. **A stub counter at the tip that only prints the frozen line and exits 0 is accepted.**
   Tip `860607052d2b` = `23b3fdb1` with `tools/round64-c2-counter.py` replaced by a 3-line printer
   (`fixes/stub-counter-printing-frozen-line.py`):
   - the *real* counter (run from the clone) scores that tip **`met=True`, exit 0**, with the full frozen
     field table — `runs/x-stub-frozen-line.out`;
   - the *stub*, executed **at the tip** exactly as the predicate sentence reads
     ("at the tip, `tools/round64-c2-counter.py --repo R --tip T --work W` exits 0 and prints every one of
     these fields"), prints the frozen line and exits 0 — `runs/x-stub-frozen-line.out` (second block).

   The claim's wording makes the counter at the tip the graded artifact, and the counter cannot tell a real
   instrument from a printer at its own path. **Smallest safe correction** (`fixes/fix-selfpin2-c2-counter.py`):
   pin the counter's own sha256 (`SELF_SHA`) and fold a mismatch into `F['errors']`, so the failure is a
   stderr `problem: pin-self:…` and `errors=1` while the frozen stdout line at the good tip stays
   byte-identical (verified: `runs/x-selfpin2-good.out` == `runs/full-23b3fdb1.out`;
   the stub tip then prints `met=False`, `errors=1`, `gate-misses: ['errors']` —
   `runs/x-selfpin2-stub.out`). A first attempt that only appended to `pin_probs` was **not** sufficient:
   `pin_probs` never reach `F['errors']` (`errors = reg_facts['errors'] + len(canon_probs)`), so the stub still
   scored `met=True` with `errors=0` — `runs/x-selfpin-stub.out` records that intermediate state.

### F3 (disclosure, not a defect) — the hexrun-ledger row is inert alone and is the one variant that moves nothing

`v7-hexrun-ledger` (the ledger row that classifies `72c7713ef48c…`) is byte-identical to the base run. The row
only matters through the `hexrun-census` bound row, and that row is only *executed* when the claims registry
exists. Isolated: `hexrun-census scan` at v1-claims reports `unknown=1` (the token
`72c7713ef48cd5d5d02964ece2975602e3402a08`, class=unknown — it is the fleet-repo report commit cited in
`corpus/lessons/round-63-verifier-spotcheck.md:5` and `:17`), so with the registry present the row is
`false` and `mismatches=1`. Adding the ledger row fixes the *classification* but the row still fails, because
the ledger's `evidence` cell points at `.ufo/waves/round-64/b/out/X09ScansTip/evidence-72c7713….json`, which
**is absent at the base tip** (present only from `bf0db9e3`): `ledger_bad=1`, exit 1 → still `false`.
`x-claims+hexrun` and `x-claims+regress+hexrun` confirm this (`registry: outcome:hexrun-census:false`).
So the ledger row is not independently effective; it is effective only together with the wave-b evidence file.

### F4 (honest finding for the L1, not a claim failure) — the enumerated seven-file delta is not self-sufficient

The freeze lists the C2 fix as "the canonical-list section, the claims registry, the calibration-row pointer
repair + reconciler conjunct, the tally reader, and the counter" (plus one hexrun ledger row, added by
X04/X09). Applying exactly those seven files to the base (`y-all7`, commit `7b4203133bba`) still yields
**`met=False`**: `gate-misses: ['mismatches', 'regress_flipped', 'printers_rejected']` — the hexrun row is
`false` for the reason in F3, and the two dependent fields follow it. Only when the wave-b evidence file
`.ufo/waves/round-64/b/out/X09ScansTip/evidence-72c7713….json` is added as well (`y-all7+evidence`,
`c83bd9349342`) does the seven-file set reach `met=True` with `controls_rejected=120/120`. **This is not a
defect in the claim** — the tip `23b3fdb1` has all of it — but the freeze's "Fix (only delta vs base)" list
is one file short of the delta that actually moves the claim from `met=False` to `met=True`. The L1 may want to
name the evidence file in the fix list so the delta is reconstructible from the base alone.

### F5 (coupling, expected) — the canonical list and the pointer repair are not separable the way the brief assumed

`v6-canon` (base SCORECARD + the round-64 canonical-list section only) moves `population 0→12` but *also*
breaks `recon_mismatches 0→2`: the reconciler at that tree reports
`banner: head lacks 'Latest measured round: 64'` and `planned: section does not name '### Planned (round 65)'`,
because the canonical list is only consistent with the banner and planned-section edits. The full tip SCORECARD
(`v6b`) repairs the banner and the closure pointer together (`recon[mismatches=0,met=True]`, `own=closure ptr=63`),
but `closure_ptr` still stays 0 because the *planted* stale-pointer check needs the reconciler conjunct
(v4): the base reconciler cannot see the planted pointer, so `planted_ok=False`
(`closure: own=closure ptr=63 newest=63 planted_ok=False mismatches={'fixed': 0, 'stale': 0}`).
The pointer repair alone (`v6c-pointer-only`) moves no field at all: `own=closure ptr=63` is reported on stderr,
but `closure_ptr` stays 0 because the reconciler at that tree does not have the conjunct. **The reconciler
conjunct and the canonical list are a genuine pair** — neither alone produces `closure_ptr=1`. Good calibration
signal, and it matches the freeze's conjunct wording.

## 4. Impacted axes and disposition

- **Calibration (the graded axis): intact.** No single-change variant and no incomplete set reaches `met=True`;
  the base reproduces the frozen do-nothing receipt byte-for-byte; the full tip reproduces the frozen
  `met=True` line byte-for-byte (2 runs).
- **Operability: untouched.** Nothing here bears on the C1 request plane.
- **F1** is a counter robustness defect on a partial tree (fixable in one condition, verified output-neutral).
- **F2** is a counter self-certification gap (fixable in ~4 lines, verified output-neutral at the good tip).
  It is the same class as the round-63 routed defect "bound tools and reconciler certify themselves"
  (KR03 S1/S2), one level up: here the *counter* certifies itself. The freeze discloses the counter's sha256
  in prose (`freeze.txt`: `sha256 c8b725e5…`), so the tip's counter is *nominally* pinned — but nothing in the
  instrument checks it, and the L1's own receipt (`c2-prewave-tip.txt`) records the frozen line without
  re-deriving the counter's digest at the tip.
- **F3/F4** are disclosure/completeness findings for the L1, not claim failures.

## 5. Smallest safe corrections (all in `out/CR08C2DoNothingScan/fixes/`, none applied to the lane)

1. `fix-c2-counter.py` — one condition: guard the `reg-<cap>` overlay lookup. Effect: v2 scores instead of
   crashing; the tip's frozen line unchanged.
2. `fix-selfpin2-c2-counter.py` — pin the counter's own sha256 and fold a mismatch into `F['errors']`
   (must reach `errors`, not just `pin_probs`). Effect: a printer at the counter's own path is refused
   (`met=False`, `errors=1`); the tip's frozen line unchanged.
3. Freeze text: name `.ufo/waves/round-64/b/out/X09ScansTip/evidence-72c7713….json` in the C2 fix list so the
   delta is reconstructible from the base alone (F4).

## 6. Reproduction

```
S=/fast/scratch/hyaku/kama-r64/f/CR08C2DoNothingScan; D=$S/clone
git clone -q --shared /home/vgpnk/Projects/shokunin/kama-shokunin $D
git -C $D checkout -q 23b3fdb1a925129a9961cf551f6d40bf251602cb
python3 $S/build_variants.py          # the 7 variants + commits
python3 $D/tools/round64-c2-counter.py --repo $D --tip <variant-sha> --work $S/work-<name>
```

Every run used a fresh `--work`; the counter's own `work_reused` guard was satisfied throughout
(`work_reuse_refused=1` on every scoring run).

## 7. Counter lines (one per scored tree)

```
base 0c1eff3cb9ac: tip=0c1eff3cb9ac population=0 covered=0/12 mismatches=0 pinned=12/13 deps_pinned=2/2 regress_flipped=0/12 printers_rejected=0/12 idle_ok=0 work_reuse_refused=1 closure_ptr=0 recon_mismatches=0 tally_disclosed=1/8 tally_selftest=0 sens_selftest=4/4 controls_rejected=0/120 errors=2 recon[mismatches=0,maxN=63,met=True] tally[56:no-disclosure,57:no-disclosure,58:no-disclosure,59:no-disclosure,60:no-disclosure,61:no-disclosure,62:no-disclosure,63:ok] families[] met=False
v1-claims 14cfe7b65abe: tip=14cfe7b65abe population=0 covered=12/12 mismatches=1 pinned=12/13 deps_pinned=2/2 regress_flipped=0/12 printers_rejected=0/12 idle_ok=1 work_reuse_refused=1 closure_ptr=0 recon_mismatches=0 tally_disclosed=1/8 tally_selftest=0 sens_selftest=4/4 controls_rejected=0/120 errors=1 recon[mismatches=0,maxN=63,met=True] tally[56:no-disclosure,57:no-disclosure,58:no-disclosure,59:no-disclosure,60:no-disclosure,61:no-disclosure,62:no-disclosure,63:ok] families[] met=False
v2-regress edde67ff0afe: errors=1 met=False  (internal KeyError: 'reg-sources-registry')
v3-counter ca03ade07579: tip=ca03ade07579 population=0 covered=0/12 mismatches=0 pinned=12/13 deps_pinned=2/2 regress_flipped=0/12 printers_rejected=0/12 idle_ok=0 work_reuse_refused=1 closure_ptr=0 recon_mismatches=0 tally_disclosed=1/8 tally_selftest=0 sens_selftest=4/4 controls_rejected=0/120 errors=2 recon[mismatches=0,maxN=63,met=True] tally[56:no-disclosure,57:no-disclosure,58:no-disclosure,59:no-disclosure,60:no-disclosure,61:no-disclosure,62:no-disclosure,63:ok] families[] met=False
v4-reconciler b5c6da0e922: tip=b5c6da0e922 population=0 covered=0/12 mismatches=0 pinned=13/13 deps_pinned=2/2 regress_flipped=0/12 printers_rejected=0/12 idle_ok=0 work_reuse_refused=1 closure_ptr=0 recon_mismatches=1 tally_disclosed=1/8 tally_selftest=0 sens_selftest=4/4 controls_rejected=0/120 errors=2 recon[closure_ptr=0,mismatches=1,maxN=63,met=False] tally[56:no-disclosure,57:no-disclosure,58:no-disclosure,59:no-disclosure,60:no-disclosure,61:no-disclosure,62:no-disclosure,63:ok] families[] met=False
v5-tally 9a3d9c07d9e5: tip=9a3d9c07d9e5 population=0 covered=0/12 mismatches=0 pinned=12/13 deps_pinned=2/2 regress_flipped=0/12 printers_rejected=0/12 idle_ok=0 work_reuse_refused=1 closure_ptr=0 recon_mismatches=0 tally_disclosed=8/8 tally_selftest=1 sens_selftest=4/4 controls_rejected=0/120 errors=2 recon[mismatches=0,maxN=63,met=True] tally[56:disclosed:shortcut+survivor,57:disclosed:shortcut+survivor,58:disclosed:survivor,59:disclosed:shortcut,60:disclosed:shortcut,61:disclosed:no-falsify,62:disclosed:no-falsify+shortcut,63:ok] families[] met=False
v6-canon bb0a845789b4: tip=bb0a845789b4 population=12 covered=0/12 mismatches=0 pinned=12/13 deps_pinned=2/2 regress_flipped=0/12 printers_rejected=0/12 idle_ok=0 work_reuse_refused=1 closure_ptr=0 recon_mismatches=2 tally_disclosed=1/8 tally_selftest=0 sens_selftest=4/4 controls_rejected=0/120 errors=1 recon[mismatches=2,maxN=64,met=False] tally[56:no-disclosure,57:no-disclosure,58:no-disclosure,59:no-disclosure,60:no-disclosure,61:no-disclosure,62:no-disclosure,63:ok] families[] met=False
v6b-scorecard-full 3562d1214160: tip=3562d1214160 population=12 covered=0/12 mismatches=0 pinned=12/13 deps_pinned=2/2 regress_flipped=0/12 printers_rejected=0/12 idle_ok=0 work_reuse_refused=1 closure_ptr=0 recon_mismatches=0 tally_disclosed=1/8 tally_selftest=0 sens_selftest=4/4 controls_rejected=0/120 errors=1 recon[mismatches=0,maxN=64,met=True] tally[56:no-disclosure,57:no-disclosure,58:no-disclosure,59:no-disclosure,60:no-disclosure,61:no-disclosure,62:no-disclosure,63:ok] families[] met=False
v6c-pointer-only c469046ca4a9: tip=c469046ca4a9 population=0 covered=0/12 mismatches=0 pinned=12/13 deps_pinned=2/2 regress_flipped=0/12 printers_rejected=0/12 idle_ok=0 work_reuse_refused=1 closure_ptr=0 recon_mismatches=0 tally_disclosed=1/8 tally_selftest=0 sens_selftest=4/4 controls_rejected=0/120 errors=2 recon[mismatches=0,maxN=63,met=True] tally[56:no-disclosure,57:no-disclosure,58:no-disclosure,59:no-disclosure,60:no-disclosure,61:no-disclosure,62:no-disclosure,63:ok] families[] met=False
v7-hexrun-ledger 37f504d5a563: tip=37f504d5a563 population=0 covered=0/12 mismatches=0 pinned=12/13 deps_pinned=2/2 regress_flipped=0/12 printers_rejected=0/12 idle_ok=0 work_reuse_refused=1 closure_ptr=0 recon_mismatches=0 tally_disclosed=1/8 tally_selftest=0 sens_selftest=4/4 controls_rejected=0/120 errors=2 recon[mismatches=0,maxN=63,met=True] tally[56:no-disclosure,57:no-disclosure,58:no-disclosure,59:no-disclosure,60:no-disclosure,61:no-disclosure,62:no-disclosure,63:ok] families[] met=False
full 23b3fdb1a925: tip=23b3fdb1a925 population=12 covered=12/12 mismatches=0 pinned=13/13 deps_pinned=2/2 regress_flipped=12/12 printers_rejected=12/12 idle_ok=1 work_reuse_refused=1 closure_ptr=1 recon_mismatches=0 tally_disclosed=8/8 tally_selftest=1 sens_selftest=4/4 controls_rejected=120/120 errors=0 recon[closure_ptr=1,mismatches=0,maxN=64,met=True] tally[56:disclosed:shortcut+survivor,57:disclosed:shortcut+survivor,58:disclosed:survivor,59:disclosed:shortcut,60:disclosed:shortcut,61:disclosed:no-falsify,62:disclosed:no-falsify+shortcut,63:ok] families[canon=4/4,closure=5/5,flip=11/11,gate=16/16,idle=21/21,pattern=5/5,pins=5/5,printer=2/2,reconciler=11/11,registry=17/17,regress=11/11,selftest=1/1,tally=8/8,work=3/3] met=True
```

Supplementary lines (coupling diagnostics and fixes) are in `out/CR08C2DoNothingScan/runs/`.

## 8. Cleanup

Scratch `/fast/scratch/hyaku/kama-r64/f/CR08C2DoNothingScan/` removed after the receipts were copied into
`out/CR08C2DoNothingScan/`. No process of mine is left running (checked `pgrep -f CR08C2DoNothingScan`: empty;
the four live `llama-server` processes belong to other seats — MT40RegistryRows and the operator's standing
server — and were not touched).
