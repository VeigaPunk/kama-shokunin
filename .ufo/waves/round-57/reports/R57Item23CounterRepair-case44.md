# Case 44 — independent test of the stale maxN/count assignment

Seat: R57Item23CounterRepair. Independent of the wave’s frozen control literals: every expected
value below is re-derived from committed bytes at the pinned tip, then compared with the frozen
counter’s behavior. Isolated scratch only; no shared writes; no installs.

Pinned coordinates:

- lane: `/home/vgpnk/Projects/shokunin/kama-shokunin`
- base: `b89bdab2cc114735ec5d331c6c610134258f7864`
- counter bytes: `tools/round42-selfdesc-reconcile.py` sha256
  `9736923ec3086c6e56512cd67fa7c00a22cbb8ac63022bef45a676f2200f9ef0`, dependency
  `tools/round41-scorecard-reconcile.py` sha256
  `eff934a27b3e7525226c78e376ce774f3ab0b225ab98427b19201e5312176cd6`
- isolated base fixture `2665285…`, build fixture `750c555…`, mutants `9ce2321`, `1edfbaa`,
  `3fa69f6`, `f38b39a`.

## Assertions and outcomes

| id | independent assertion | derived value | outcome |
|---|---|---|---|
| A1 | number of `corpus/lessons/*verifier-spotcheck.md` blobs at base vs the calibration row literal | blobs `43`; literal `42` | the base mismatch is caused by the row literal, and the row is stale by exactly one |
| A2 | greatest `^## Round (\d+)` heading at base vs the head’s declared latest round | headings `57`, max `56`; head `Latest measured round: 56` | `maxN=56` is tree-derived and agrees with the head |
| A3 | is `46` derivable anywhere in the tree? | only `SCORECARD.md:2676` round-46 regression text, `SCORECARD.md:2744` historical banner, and `controls/c1-noop.py` literal | `46` is stale, not an expectation |
| A4 | does changing only the calibration literal `42`→`43` make the frozen counter pass? | build fixture, one insertion/one deletion | `mismatches=0 maxN=56 met=True`, exit 0; reverting to `42` or using `44` fails, exit 1 |
| A5 | is canonical-list selection/content preserved by the repair? | base and build both select round 49, 11 rows, first rounds `[10,14,16,20,25,30,41,42,43,46,47]` | unchanged; the repair touches no canonical heading or row |
| A6 | is `maxN` hardcoded or derived from headings? | added a `## Round 58` heading in a fixture | `maxN=58`, `banner=1`, `planned=2`, `mismatches=3`, exit 1 — derived, and a repair to `46` would break head agreement |
| A7 | is the no-op’s `met=True maxN=46` evidence? | script: 3 lines, 0 imports, 0 file-access names, only `print`; identical from another cwd | no: it reads nothing, so its literal output cannot measure the counter |

## Exact outputs

```text
A1/A2  r8_derivation.out
spotcheck_files_at_base=43
scorcard_literal_at_base=42
round_headings_at_base=57
maxN_at_base=56
latest_measured_round_at_base=56
noop_literal=print("mismatches=0 maxN=46 met=True")

A3     SCORECARD.md:2676  … round-42 self-description counter `mismatches=0 maxN=46 met=True` …
       SCORECARD.md:2744  **Current authority (round 46):** … Latest measured round: 46. …

A4     r3_build.out   tip=750c555…  r41=0 … mismatches=0 maxN=56 met=True   exit=0
       r6_mut42.out  tip=9ce2321…  r41=1 … mismatches=1 maxN=56 met=False  exit=1
       r6_mut44.out  tip=1edfbaa…  r41=1 … mismatches=1 maxN=56 met=False  exit=1

A5     r5_semantics_base.out / r5_semantics_build.out
canonical_markers=[16, 34, 41, 42, 43, 46, 47, 48, 49] highest=49
canonical_rows=11 names=[append-only-audit, context-capacity-receipt, digest-ledger,
gguf-declared-identity-replay, hexrun-census, instrument-agreement, live-llamacpp-lifecycle,
live-receipt-replay, ollama-offline-evidence-replay, pin-watch, sources-registry]
canonical_first_rounds=[10, 14, 16, 20, 25, 30, 41, 42, 43, 46, 47]

A6     r6_mutround.out  tip=f38b39a…  maxN=58 banner=1 planned=2 … mismatches=3 met=False exit=1
       detail: banner: head lacks 'Latest measured round: 58'
       detail: planned: section does not name '### Planned (round 59)'

A7     r4_noop.out       mismatches=0 maxN=46 met=True   exit=0
       r4_noop_cwd2.out  mismatches=0 maxN=46 met=True   exit=0
       r4_noop_shape.out imports= [] calls= ['print'] file_access_names= [] lines= 3
```

## Standing of the delivered claim

- “counter currently reports maxN=56 instead of expected 46” — **rejected by A2/A3/A6**. `56` is
  the derived maximum round at the base and matches the head’s “Latest measured round: 56”; `46`
  is a round-46-era value still copied into the frozen no-op. There is no tree-derived `46`.
- “repair the stale canonical capability row count … before output mismatch=1” — **the failing
  count exists but is not 46**: the calibration row’s verifier-spotcheck census says `42` where the
  tree holds `43` (A1). Re-anchoring that one literal makes the frozen counter pass with
  `maxN=56` (A4), while canonical heading selection and row content stay byte-identical (A5).
- The no-op `met=True` is unbound (A7), so matching its printed line — including its `46` — is not
  evidence for any repair.

## Verdict

The assigned case is **partially confirmed and part corrected**: a stale count does make the
frozen round-42 counter report `mismatches=1` at the base, and the minimal repair is the one-token
SCORECARD re-anchor `42`→`43` with no counter-code change; the delivered `expected 46` and the
`maxN=56` framing are stale and are rejected. Canonical heading semantics are preserved.

Independent-reproduction recipe (scratch, from a clean dir):

```bash
S=/fast/scratch/hyaku/kama-r57/R57Item23CounterRepair; LANE=/home/vgpnk/Projects/shokunin/kama-shokunin
git -C "$LANE" ls-tree --name-only b89bdab2… corpus/lessons/ | grep -c 'verifier-spotcheck\.md$'   # 43
git -C "$LANE" show b89bdab2…:SCORECARD.md | grep '^| calibration' | grep -oP '→ `\K[0-9]+(?=` \(outside closures)'   # 42
git -C "$LANE" show b89bdab2…:SCORECARD.md | grep -oP '^## Round \K[0-9]+' | sort -n | tail -1   # 56
python3 "$S/bin/round42-selfdesc-reconcile.py" --repo "$LANE" --tip b89bdab2…                     # exit 1
python3 "$S/bin/round42-selfdesc-reconcile.py" --repo "$S/fixtures/build" --tip HEAD               # exit 0
python3 "$S/bin/c1-noop.py"                                                                       # exit 0, unbound
```

Receipts: `.ufo/waves/round-57/measured/R57Item23CounterRepair/` (see its `MANIFEST.txt`).

Report: .ufo/waves/round-57/reports/R57Item23CounterRepair-case44.md
