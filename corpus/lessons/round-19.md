# Round 19 — revision-qualified citations and the install-tree pin

## Declared claims

- **C1 calibration, 7 → 8 (lowest assigned axis; sourced):** the four routed
  round-18 pointer defects become machine-checkable. `tools/citation-provenance.py`
  + `registry/required-citations.json` require a `cite(<rev>, <path>, sha256=…)`
  token per material citation and verify the blob at that revision; the lesson,
  `SOURCES.md` (S055 qualification), `SCORECARD.md` erratum and
  `residual/assignments.json` carry the corrections. Counting command:
  `python3 tools/citation-provenance.py` (prints `required=4 found=4 verified=4
  missing=0 mismatch=0`, exit 0; before the tokens: `missing=3`, exit 1).
- **C2 operability, 8 → 8 (delta 0; sourced in S057):** a sixth receipt pin,
  `--expect-install-tree-sha256`, plus `tests/llamacpp-live/install-tree-grid.py`.
  Counting command: the grid over the committed recovery receipt with and
  without `--tree-sha` — consistent swaps of `libggml-base`, `libllama-common`
  and `libllama` are rejected 0/3 (all three accepted) before the pin and rejected 3/3 with it,
  baseline VALID both times.

Causally separable by counting command: C1 owns the checker/registry and its
tokens; C2 owns the gate, runner argv and grid. They share two documents
(`corpus/SOURCES.md`, `SCORECARD.md`) as citation carriers, but neither
counter reads the other claim's inputs (CritSeparability 2x2 toggle).

## Gate

| Item | Decision | Source (opened 2026-10-21) |
|---|---|---|
| Shared libraries are found through DT_NEEDED and the loader search path, so a launcher's bytes do not identify the libraries it loads [INFERENCE for the identity conclusion] | admit (grounds C2; S057) | https://man7.org/linux/man-pages/man8/ld.so.8.html (man-pages 6.19, 2026-08-03) §Dynamic string tokens: "This expands to the directory containing the program or shared object" (11 words at the $ORIGIN entry) |
| A run-path entry is searched only for direct dependencies | admit; scope note | same page §DESCRIPTION (3): "are searched only to find those objects required by DT_NEEDED" (10 words) |
| A tree digest authenticates execution | reject | [INFERENCE] the page describes loader resolution and says nothing about digests; identity is not authentication |

New row S057 carries these two quotes and their section anchors; `used-by` is
this lesson and `registry/required-citations.json` (the pin's identity boundary).

## Mistakes (to be mined after the wave)

Candidate classes: (a) a citation token can be duplicated in a non-authoritative
document and still satisfy the checker (needs document precedence); (b) a tree
pin computed from the same directory it verifies is self-referential for the
*installed* bytes and must be recorded as an observed value, not an upstream
constant. Each fix counts only once shown able to fail.

## Measurement plan

After the waves: run `tools/citation-provenance.py` (before tokens/after), the
grid pair, the gate/tool/counter selftests, then the official harness on a clean
commit (it now includes `tree-grid-no-pin` exit 1, `tree-grid-pin` exit 0 and
`tree-pin-negative` exit 1). Record every exit and artifact digest.

## Falsify-wave and residual findings (appended during round 19)

- **Symlinked sonames are unpinned (TreeCap).** `install_tree()` pins regular
  files only; the launcher's `libllama.so.0`/`libggml.so.0` soname symlinks are
  skipped, so retargeting one leaves `install_tree_sha256` unchanged. The sixth
  pin is therefore regular-file identity, not complete install identity; a
  symlink-aware pin is named debt.
- **Citation document binding (CritAxisHarm).** A token could live in any
  default doc (e.g. `LOG.md`). Registry rows now carry `doc`, the checker
  requires the token in that document, and the selftest covers the LOG-only and
  widened-`--docs` cases; official runs must omit `--docs`.
- **Stale-token branch (DraftScorecard/CitationNegatives).** A token whose
  digest differs from the registry is now `mismatch`, not `missing`; a
  co-drifted doc+registry pair reaches the observed-vs-expected branch.
- **Uppercase/one-char TOKEN mutants (MutTokRegex/MutationChecker).** The
  selftest now rejects uppercase hex and 1-char revs, and asserts a non-empty
  default docs list.
- **Grid selftest absent-member case** used a present member; corrected to a
  genuinely absent name, and the whole grid selftest now runs green.

## Mistakes (mined this round)

| ID | Class | Evidence pointer | Captured-by | Fix / shown able to fail |
|---|---|---|---|---|
| M1 | A "machine-checkable" citation gate that accepts the token in any default doc does not bind it to the authoritative claim | `CritAxisHarm.md` (LOG-only token exits 0) | fresh critic attacked the claim wording, not the code | registry `doc` binding + LOG-only and widened-`--docs` selftest cases (15 total); before/after `missing=3` → `missing=0` |
| M2 | A grid selftest can pass a wrong fixture (present member asked for as absent) and still look green | `GridSelftest` delivered `absent member: row='rejected'` | first execution of the seat's selftest by L1 | genuinely absent member name; selftest green, absent case exercised |
| M3 | A pin computed from the directory it verifies is an observed value, not an upstream constant, and symlinked members escape it | `TreeCap.md` (retargeted soname leaves digest unchanged) | fresh scout's fixture probe | claim wording "observed bytes, not authentication"; symlink gap named as debt |

## C1 scope correction (falsify-wave refutation accepted, appended)

`CritC1Inflation` refuted the original C1 wording ("the four routed pointer
defects become machine-checkable"). What the instrument actually checks: the
digests and ancestry of the three registry rows, in the registry-bound document
(sentence-to-token correspondence is not checked; defects 1 and 4 are record
corrections, not pointer checks). The `gate-live-1` row is re-pinned to
`1b85a24` (`1cb5a41b…`), the blob that actually names `live-recovery/`. C1
therefore lands **calibration 7 → 7 (delta 0), verdict improved-bounded**, not
the declared 7 → 8; the score is not raised on a refuted wording.

- **Kill classification (TameshiConventions/C2BaselineInvalid).** The grid now
  counts a mutant as rejected only on gate exit 1 (INVALID); exit 2/3 and
  tracebacks are `error`, and an invalid baseline runs zero members and exits 2.
  The selftest covers the invalid-baseline and absent-member cases.
- **Citation scope honesty (RevisionDriftScan).** 609 of 635 lane-path citations
  in the four scanned docs still carry no revision; the claim is that the three
  registry-bound citations are machine-checked, not that all citations are.

## Round-20 appended record corrections

This appendix supersedes the stale C1 counts at lines 12, 75, 83 and 95.
The final round-19 registry has **4 rows**, not 3. Committed
`.ufo/waves/round-19/evidence/c1-counting.txt` measured `028235e6`:
`required=4 found=0 verified=0 missing=4` exit 1 → `required=4 found=4
verified=4 missing=0 mismatch=0 off_ref=0` exit 0. The selftest printed
"15 cases" (not the earlier five-case development state); round-20 review
also found its printed count was not an independently enumerated tally.
Round-20 adds the observed-digest branch regression rather than treating a
green historical selftest label as complete coverage.

The headings "Falsify-wave and residual findings" and "falsify-wave refutation
accepted" misattribute the advice: CritC1Inflation, CritAxisHarm, TreeCap,
TameshiConventions and C2BaselineInvalid were **build** seats. The validated
66-seat falsify call spawned **0**, all refused (`falsify/refused-attempt-1.json`).
No outside review or fresh falsify wave is implied by those headings.

The round-19 report's census paths were uncommitted. Retrospective before/after
receipts now live under round-20 `build/out/CensusR19Retro/`, explicitly
labelled source revisions `8bf99cae` and `3389513f`, rows **56 → 57**.
They were re-recorded in round 20, not recovered original round-19 runs.

`evidence/final-selftests.txt` was a dirty-tree run on `5b108c1a`, not a
measurement of that commit. **76** gate mutations apply at `7229fa9`/`5b108c1a`;
**77** apply from `f1790e2` through `37bd4c5`. Round-20
`build/out/SelftestsAtCommit/` re-records five selftests at clean `37bd4c5`,
all exit 0, with pre/post empty porcelain. No old receipt is overwritten.

S057 used-by old→new (previously unlogged): `corpus/lessons/round-19.md,
registry/required-citations.json` → `corpus/lessons/round-19.md, SCORECARD.md`
at `5b108c1a`. This supersedes lines 33–34; immutable source cells did not change.

The outside round-19 trend verdict is **expansion unchanged**, not the author's
"improved (narrow)": a source row alone added no knowledge entry or capability.
Quality and discernment were improved by the outside spot-check.


## Restored lines (round 52)

Lines this file lost in place, re-appended verbatim in round 52 (claim C2): the file is declared append-only with corrections appended (`registry/append-only-contract.tsv`), and `tools/append-only-audit.py` v6 graded each line below as deleted and no longer held (round-51 rows of `registry/append-only-disclosures.tsv`). They are historical bytes, kept so that no declared line is lost; where this file's later text replaced them, the later text stands. One fenced block per deleting commit, in history order.

Deleted by `5b108c1a7e94` (round-19: doc-bound citations, ancestry gate, fail-closed grid, wave evidence):

`````text
- **C2 operability, 8 → 8 (delta 0):** a sixth receipt pin,
  and `libllama` are accepted 0/3 before the pin and rejected 3/3 with it,
| Shared libraries are found through DT_NEEDED and the loader search path, so a launcher's bytes do not identify the libraries it loads | admit (grounds C2) | https://man7.org/linux/man-pages/man8/ld.so.8.html §Dynamic string tokens: "This expands to the directory containing the program or shared object" (11 words at the $ORIGIN entry) |
`````

Deleted by `f1790e25b421` (round-19: empty-tree rejection, C1 scope erratum, separability correction, final receipts):

`````text
Causally separable: C1 owns the checker/registry/lesson/SOURCES/SCORECARD
corrections; C2 owns the gate, runner argv and grid. No shared source file.
`````

Deleted by `028235e6f28d` (round-19: checkpoint Gate citation row; four-row C1 registry):

`````text
  `python3 tools/citation-provenance.py` (prints `required=3 found=3 verified=3
`````
