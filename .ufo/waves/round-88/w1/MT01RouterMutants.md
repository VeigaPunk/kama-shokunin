# MT01RouterMutants — kama r88 w1 mutation probe of C1 router logic

## Scope
Mutation-tested the C1 router logic (`router_entries`/`router_refine` + the `classify` hook) in
`tools/kama-probe.sh` at measured revision M=`138a75437bcd11b72446087e970f5dfc5abf9ccd` (blob
sha256 `bd7a6a2228d04b69abcc5d19f2907a9caf737347ef96ff92722edbc3180e7bdf`) against the frozen
counter `tools/round88-router-cells.py` (17 cells: 14 canned, 3 live on the pinned b11755 router
child; live oracle 200→MODEL_OK / 400 "model is not loaded"→MODEL_UNLOADED). 15 single-point
mutants, each one diff hunk in a scratch copy; the lane was never written. All runs used
`--probe-file`, so the counter's stub cells and live cells are identical to the frozen ones and
the summary says `probe=override` with our mutant hash.

Baseline (pristine bytes, exit 0):
`ROUTER_CELLS cells=17 mismatches=0 canned=14 live=3 probe=override probe_sha256=bd7a6a22…` — the
same blob the counter extracts for `--rev 138a7543…`, so the mutant baseline is not a stub.

## Commands and outputs
Scratch `/fast/scratch/hyaku/kama-r88/MT01RouterMutants`; probe extracted with
`git -C wt show 138a7543…:tools/kama-probe.sh`; one clone (`git clone --shared`), `rev-parse
--show-toplevel` printed the clone root. Mutants built by exact-substring replacement (each `old`
asserted to occur once), `bash -n` ok, `diff -u` shows exactly 1 `@@` hunk per mutant.

Per mutant (exit codes are the counter's):
```
TMPDIR=<scratch>/work/<M> python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round88-router-cells.py \
  --repo /home/vgpnk/Projects/shokunin/kama-shokunin --rev 138a75437bcd11b72446087e970f5dfc5abf9ccd \
  --work <scratch>/work/<M> --probe-file <scratch>/mutants/<M>.sh
```
| mutant | exit | mismatches | killed by / verdict |
|---|---|---|---|
| M01 drop `-failed` suffix | 0 | 0 | **ESCAPED** |
| M02 sleeping treated as loaded | 1 | 2 | C05, C12 |
| M03 drop `model_matches` filter for literal expect | 1 | 1 | C10 |
| M04 down precedence before loading | 0 | 0 | **ESCAPED** |
| M05 status-less match does not win | 0 | 0 | **ESCAPED** |
| M06 `any_status` early-return inverted (`\|\|`→`&&`) | 1 | 11 | C02,C03,C04,C05,C06,C07,C10,C12,C14,L01,L03 |
| M07 `models[]` read before `data[]` | 0 | 0 | **ESCAPED** |
| M08 skip refine for wildcard expectation | 1 | 1 | C12 |
| M09 unknown status value treated as loaded | 1 | 9 | C02,C04,C05,C07,C10,C12,C14,L01,L03 |
| M10 drop `[ "$C_VERDICT" = MODEL_OK ]` guard | 0 | 0 | **ESCAPED (equivalent)** |
| M11 drop `[ "$ok" -eq 1 ] && return 0` | 1 | 1 | C13 |
| M12 `any_status` set only for status-less entries | 1 | 11 | C02,C03,C04,C05,C06,C07,C10,C12,C14,L01,L03 |
| M13 status-less entries skipped in `router_entries` | 0 | 0 | **ESCAPED** |
| M14 wildcard set drops the empty expectation | 0 | 0 | **ESCAPED** |
| M15 `downloading` removed from the loading case | 1 | 1 | C06 |

Kill rate 8/15 (one escape is a true equivalent mutant). Reproduced twice: baseline and M08 were
re-run after M08 was rebuilt (its first build left `RT_VERDICT` unset and died on `set -u` with
`UNPARSEABLE`; the reported kill is the rebuilt, semantic mutant).

Witness escalation for every escaped mutant (own stub in scratch, same probe CLI as the counter,
`python3 witness.py --probe <copy> --expect <E> --body <body.json>`):
| witness | pristine | escaped mutant | frozen sentence broken |
|---|---|---|---|
| W1 m1 `unloaded failed:true` | UNLOADED `router-unloaded-failed` | M01 UNLOADED `router-unloaded` | "`-failed` appended when `failed` is true" |
| W2 m1 `unloaded` + m1 `loading` | **LOADING** `router-loading` | M04 **UNLOADED** `router-unloaded` | "else any loading/downloading, else MODEL_UNLOADED" |
| W3 m1 status-less + m1 `unloaded` | **OK** `matched` | M05 UNLOADED `router--`; M13 UNLOADED `router-unloaded` | "any loaded or status-less match wins" |
| W4 `data[]` m1 unloaded + `models[]` m1 loaded | **UNLOADED** `router-unloaded` | M07 **OK** `matched` | probe contract: "`data[].id -> models[].id`" (kama-probe.sh:57,346) |
| W5 `--expect ""` + m1 `unloaded` | **UNLOADED** `router-unloaded` | M14 **OK** `expected-wildcard` | "Wildcard expectation (`*`, `-`, empty)" |
| W6 expect m9, m1 loaded (M10) | MISMATCH `served-id-mismatch` | M10 identical | none — guard unreachable |

## Findings
- DEFECT — reasons are ungraded by the counter. `tools/round88-router-cells.py:268` is
  `ok = exp == got` (verdict only); the `reason=` column is printed but never compared. C04 already
  sends `failed: true` (`:65`) expecting the suffix per the frozen rule, so M01 survives in 17/17
  cells and the reason defect is invisible. Proposal for r89 (counter edit, not a predicate change):
  add an expected-reason column and grade C04 as `reason=router-unloaded-failed`.
- DEFECT — loading/downloading vs unloaded precedence is untested. Frozen rule: "Any matching
  `loaded` or status-less entry wins, then any loading/downloading." M04 escapes because no cell has
  two matching entries of different kinds. Proposal: `C15-unloaded+loading`, expect `MODEL_LOADING`
  reason `router-loading`; witness W2 is that body (`witness/W2-unloaded+loading.json`).
- DEFECT — status-less-entry precedence is untested (same missing cell class as above). Frozen rule:
  "any `loaded` or status-less match wins". Two independent mutants escape (M05 mutates `router_refine`,
  M13 mutates `router_entries`), so the gap is at both layers. Proposal: `C16-statusless+unloaded`,
  expect `MODEL_OK` reason `matched` (W3).
- DEFECT — `data[]` vs `models[]` precedence is untested. `router_entries` mutates silently
  (`kama-probe.sh:476`) and no canned body carries both keys; M07 flips UNLOADED→OK on W4, i.e. a
  false green on a body shape the probe's own contract orders explicitly. Proposal: `C17-both-arrays`
  (W4 body), expect `MODEL_UNLOADED` reason `router-unloaded`.
- DEFECT — the empty-string wildcard is untested. The frozen rule names it ("`*`, `-`, empty") and
  C12/C13 only use `*`; M14 turns W5's UNLOADED into MODEL_OK. Proposal: `C18-empty-expect` with
  `--expect ""`, expect `MODEL_UNLOADED`.
- NOTE — M10 is an equivalent mutant, not a gap: dropping the `$\{C_VERDICT\}` guard cannot change any
  verdict, because a MODEL_MISMATCH implies no entry matched the expected id and `router_refine`
  then returns with empty `RT_VERDICT` (witness W6 identical). The guard is defensive only; no cell
  is proposed.
- NOTE — live cells L01/L03 are load-bearing: both kill M06, M09 and M12, i.e. the only mutations
  caught by live routing are the ones that erase all router status handling; no live cell exercises
  precedence or reason text either (the router child has one model, so multi-entry states are
  unreachable live without extra fixture models).
- BLOCKER — none. No mutant falsified the frozen C1 predicate; every escape is a counter-coverage
  gap in cases the probe itself already handles correctly.

## Restoration evidence
No lane byte was written at any point. After the sweep: `sha256sum tools/kama-probe.sh` in the lane
= `bd7a6a2228d04b69abcc5d19f2907a9caf737347ef96ff92722edbc3180e7bdf`, identical to
`git show 138a7543…:tools/kama-probe.sh`; `git status --porcelain -- tools/kama-probe.sh` printed
nothing (exit 0); `git rev-parse HEAD` = `f77d2ae9f2797a19e7548989fb9e64d8f9411d3f`. The scratch
clone and all `--work` trees were removed after receipts were copied out.

## Deliverables
`.ufo/waves/round-88/w1/out/MT01RouterMutants/`: `mutants/M00-pristine.sh` + 15 `M*.sh` (each 1
hunk, syntax-checked), `logs/<M>.out` + `.exit` (full counter output, true exit code),
`logs/summary.tsv`, `logs/witness-matrix.jsonl`, `witness.py`, `witness/W*.json` + `.expect`,
`mutants.tsv`. Mutant hashes, one line each, in `logs/summary.tsv`; per-mutant `probe_sha256` in
each `.out`. Tooling installed/upgraded: none.

VERDICT: holds — frozen C1 predicate reproduces at M (17/17, exit 0) and 8/15 mutants are killed, but 6 escapes are a real counter-coverage DEFECT class (reason text, multi-entry precedence, data/models order, empty wildcard) with concrete proposed cells for round 89.
