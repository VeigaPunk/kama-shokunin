# MT01 — C1 selector mutants (kama round 86, wave w2, falsify)

Seat: `MT01SelectorMutants`, mutation-tester. Author-side advisor; no claim admission.
Target: C1 instrument `tools/round86-rendered-cells.py`, selection rules and the coupled gate fact.

## Revision measured

| Item | Value |
|---|---|
| Lane | `/home/vgpnk/Projects/shokunin/kama-shokunin` |
| Measured revision | `67eddac89f44e768b670301ea0feff06e766f32d` (lane HEAD at dispatch; `git -C … rev-parse HEAD`) |
| Instrument blob at that revision | `370de91021694c99fe70f5230d2d356b64d6f8f5`, 466 lines, 20237 bytes |
| Instrument sha256 (committed bytes, used as mutation base) | `e038b2c0ab52533ce86ba1551b0c8b66937bc664a395fae33ad82a7186bddcf9` |
| Frozen base `3ff23da3…` | `fatal: path 'tools/round86-rendered-cells.py' exists on disk, but not in '3ff23da3…'` — the instrument is new in round 86, so 67eddac is the only revision that carries it |

Working-tree note: `git -C … status --porcelain -- tools/round86-rendered-cells.py SCORECARD.md` printed
` M SCORECARD.md` (a capabilities-table append, 57 added lines) and nothing for the instrument. All
grading below reads **committed bytes** via `git show <rev>:<path>`, so the dirty `SCORECARD.md` is not
in any measurement; I did not write it.

## Method

```
git -C <lane> show 67eddac89f44e768b670301ea0feff06e766f32d:tools/round86-rendered-cells.py \
    > /fast/scratch/hyaku/kama-r86/MT01SelectorMutants/base/round86-rendered-cells.py   # exit 0
cd /fast/scratch/hyaku/kama-r86/MT01SelectorMutants/base && TMPDIR=… python3 round86-rendered-cells.py --selftest
    # exit 0, RENDERED_CELLS_SELFTEST pass=11 fail=0   (pristine control: green)
cd /fast/scratch/hyaku/kama-r86/MT01SelectorMutants && TMPDIR=… python3 mutate.py   # exit 0
```

`mutate.py` asserts each mutation string occurs **exactly once** in the pristine text, writes the
mutant to a separate scratch file (`mutants/<name>.py`), and runs the mutant's own `--selftest`.
Every mutant is a single contiguous site; the lane copy was never touched.

## Verdicts

| # | Mutant (site in pristine file) | `--selftest` exit | Arms red | Verdict |
|---|---|---|---|---|
| (a) | fence exclusion disabled — delete opener block, base lines 167–170 (`opener = FENCE.match(line)` … `continue`); `fence` is then never set, the whole `if fence is not None:` branch is dead | **1** | `unclosed-fence-fails-closed` (1) | **CAUGHT** — but by an indirect arm, see DEFECT-1 |
| (b) | HTML-comment exclusion disabled — delete the `while "<!--" in line:` block, base lines 156–163; `in_comment` can never arm, so the `if in_comment:` branch is dead | **0** | none (11/11 green) | **SURVIVED — DEFECT-2** |
| (c) | `round-N correction` exclusion disabled — delete the `CORRECTION.match` block, base lines 171–174; `depth` stays `None`, so the depth branch is dead | **0** | none (11/11 green) | **SURVIVED — DEFECT-3** |
| (d) | column-0 requirement relaxed to any indentation — `AUTHORITY = re.compile(r"^\*\*Current authority …")` → `r"^\s*\*\*Current authority …"`, base line 66 | **0** | none (11/11 green) | **SURVIVED — DEFECT-4** |
| (e) | coupled gate fact reduced to "revision present" — base lines 267–274 replaced by `coupled = [r for r in revisions if tree.ancestor(r)]`; the receipt-bytes membership test is dropped | **1** | `contradictory-receipt` (1) | **CAUGHT** (mutant prints `mismatches=0 gate=1` where the arm demands exit 1 / `gate=0`) |
| (d2) | extra probe: the *other* column-0 site relaxed — `CALIBRATION = re.compile(r"^\|\s*calibration\s*\|")` → `r"^\s*\|\s*calibration\s*\|"`, base line 67 | **0** | none (11/11 green) | **SURVIVED — DEFECT-4** (same rule, second site) |
| (f) | extra probe: tilde fences not excluded — `FENCE = re.compile(r"^ {0,3}(`{3,}\|~{3,})(.*)$")` → `r"^ {0,3}(`{3,})(.*)$"`, base line 63 (CommonMark 0.31.2 §4.5) | **0** | none (11/11 green) | **SURVIVED — DEFECT-1** (the arm named `tilde-fence-shadow` stays green) |

Per-mutant full selftest output is in `out/MT01SelectorMutants/<name>.selftest.out`.

## Why the four `*-shadow` arms cannot discriminate (root cause)

`fixture(stale_live=True, shadow=…)` places the stale live authority cell **first** and the correct
shadow cell **after** it, and puts the shadow's calibration row **before** `## Axes`. `select_cells`
takes the *first* rendered `AUTHORITY` match and the first `CALIBRATION` row inside `## Axes`, so the
shadow never becomes a candidate. The arms' expectations (`exit 1`, `gate=False`, `mismatch>=3`) are
therefore satisfied by the stale live cell alone.

`probe2.py` (exit 0) grades the pristine instrument on the shadow fixtures and on a **no-shadow**
fixture:

```
baseline no-shadow exit=1 RENDERED_CELLS facts=3 mismatches=3 gate=0 closure=0 disposition=0 newest_gate=85 newest_closure=85
fenced     exit=1 identical_to_no_shadow=True  …
commented  exit=1 identical_to_no_shadow=True  …
tilde      exit=1 identical_to_no_shadow=True  …
indented   exit=1 identical_to_no_shadow=True  …
IDENTICAL=5/5 (all four shadow arms are indistinguishable from a fixture with no shadow)
```

## Production-shape probe: survivors turn a fail-closed tree into a false green

`probe.py` (exit 0) builds the tree shape the round-85 defect actually had — the **only** authority
cell lives inside the fenced/comment/correction/indented block, with an otherwise-green record — and
grades it with pristine and with the mutant:

```
shadow-only-authority/fenced        mutant=a-fence-exclusion-off  pristine_exit=2 mutant_exit=0
shadow-only-authority/tilde-fenced  mutant=a-fence-exclusion-off  pristine_exit=2 mutant_exit=0
shadow-only-authority/commented     mutant=b-comment-exclusion-off pristine_exit=2 mutant_exit=0
shadow-only-authority/correction    mutant=c-correction-exclusion-off pristine_exit=2 mutant_exit=0
shadow-only-authority/indented      mutant=d-column0-relaxed      pristine_exit=2 mutant_exit=0
indented-row-only                   mutant=d2-calibration-column0-relaxed pristine_exit=2 mutant_exit=0
shadow-only-authority/tilde-fenced  mutant=f-tilde-fence-off      pristine_exit=2 mutant_exit=0
FALSE_GREEN_COUNT=7 of 10 probes (pristine fails closed exit 2, mutant grades green exit 0)
```

Pristine prints `could-not-evaluate: no rendered top-level Current authority cell` (exit 2); the mutant
prints `RENDERED_CELLS facts=3 mismatches=0 gate=1 closure=1 disposition=1 newest_gate=85
newest_closure=85` (exit 0). That is exactly R85V1's false green, restored by a one-site edit that the
frozen 11-arm selftest does not notice.

## Defects (each names the arm that should own it)

- **DEFECT-1 — `fenced-shadow` and `tilde-fence-shadow` are non-discriminating; `tilde-fence-shadow`
  is unguarded.** (f) survives 11/11 and grades a tilde-fenced-only authority green; (a) is red only
  because `unclosed-fence-fails-closed` stops failing closed, not because a fence shadow was accepted.
  Owning arm: `fenced-shadow` / `tilde-fence-shadow` — the fixture must make the shadow the **only**
  candidate cell (drop the stale live authority, or place the shadow first) and assert `exit 2`
  (`could-not-evaluate`) rather than re-asserting the stale-cell mismatch.
- **DEFECT-2 — `comment-shadow` is non-discriminating.** (b) survives 11/11; a comment-only authority
  grades green. Same fixture fix; owning arm `comment-shadow`.
- **DEFECT-3 — no arm owns the `round-N correction` exclusion at all.** (c) survives 11/11; a
  correction-only authority grades green. A `correction-shadow` arm must be added (the frozen plan
  lists 11 arms and none of them exercises `CORRECTION`).
- **DEFECT-4 — `indent-shadow` is non-discriminating, for both column-0 sites.** (d) and (d2) survive
  11/11; an indented-only authority and an indented-only calibration row both grade green. Owning arm
  `indent-shadow`, which must indent the *only* candidate cell inside `## Axes` for the row leg and
  must not carry a live authority for the gate leg.

Consequence for the frozen C1 kill rule ("Kill: … any control that stops discriminating"): four of the
eleven controls do not discriminate on the axis they are named for, and the `CORRECTION` selector has no
control. The instrument's *production* behaviour is correct today (see the live control below); the
defect is in the calibration evidence, not in the graded bytes.

## Positive controls (what did hold)

- Pristine `--selftest`: `RENDERED_CELLS_SELFTEST pass=11 fail=0`, exit 0.
- (e) is properly owned: `contradictory-receipt` goes red on exactly the receipt-bytes clause.
- Live grading at the measured revision:
  `python3 base/round86-rendered-cells.py --repo <lane> --rev 67eddac89f44e768b670301ea0feff06e766f32d`
  → exit 0, `RENDERED_CELLS facts=3 mismatches=0 gate=1 closure=1 disposition=1 newest_gate=85 newest_closure=85`
  (`live-67eddac.out`). The instrument is not broken; only its arm set is blind.

## Restoration

- Mutation base is a scratch copy; the lane file was never opened for write. sha256 before all runs and
  after all runs: `e038b2c0ab52533ce86ba1551b0c8b66937bc664a395fae33ad82a7186bddcf9` (identical, printed
  as `BASE_AFTER … restored=yes` by `mutate.py` and re-printed by `probe.py`).
- Lane re-checked read-only after the runs: `git -C <lane> rev-parse HEAD` = `67eddac89f44e768b670301ea0feff06e766f32d`;
  `sha256sum <lane>/tools/round86-rendered-cells.py` = `e038b2c0…bddcf9`; no mutant ever written there.
- No git/jj mutation, no commit, no fixture repo (none was needed — the instrument's `--selftest` uses
  in-memory `DictTree`), no `/tmp` use (every run under `TMPDIR=/fast/scratch/hyaku/kama-r86/MT01SelectorMutants`).
- Scratch `/fast/scratch/hyaku/kama-r86/MT01SelectorMutants/` removed after the receipts below were copied.

## Receipts (all under `out/MT01SelectorMutants/`)

`mutate.py`, `probe.py`, `probe2.py`, `selftest.log` (driver: base hash, per-mutant hash/exit/red arms,
restoration), `probe.log` (10 production-shape probes), `probe2.log` (shadow-arm vacuity),
`live-67eddac.out`, and `<mutant>.py` + `<mutant>.selftest.out` for
`a-fence-exclusion-off`, `b-comment-exclusion-off`, `c-correction-exclusion-off`, `d-column0-relaxed`,
`e-gate-coupling-to-revision-only`, `d2-calibration-column0-relaxed`, `f-tilde-fence-off`.

Tooling: none installed, none upgraded.
