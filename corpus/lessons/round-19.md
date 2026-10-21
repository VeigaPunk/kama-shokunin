# Round 19 — revision-qualified citations and the install-tree pin

## Declared claims

- **C1 calibration, 7 → 8 (lowest assigned axis; sourced):** the four routed
  round-18 pointer defects become machine-checkable. `tools/citation-provenance.py`
  + `registry/required-citations.json` require a `cite(<rev>, <path>, sha256=…)`
  token per material citation and verify the blob at that revision; the lesson,
  `SOURCES.md` (S055 qualification), `SCORECARD.md` erratum and
  `residual/assignments.json` carry the corrections. Counting command:
  `python3 tools/citation-provenance.py` (prints `required=3 found=3 verified=3
  missing=0 mismatch=0`, exit 0; before the tokens: `missing=3`, exit 1).
- **C2 operability, 8 → 8 (delta 0; sourced in S057):** a sixth receipt pin,
  `--expect-install-tree-sha256`, plus `tests/llamacpp-live/install-tree-grid.py`.
  Counting command: the grid over the committed recovery receipt with and
  without `--tree-sha` — consistent swaps of `libggml-base`, `libllama-common`
  and `libllama` are rejected 0/3 (all three accepted) before the pin and rejected 3/3 with it,
  baseline VALID both times.

Causally separable: C1 owns the checker/registry/lesson/SOURCES/SCORECARD
corrections; C2 owns the gate, runner argv and grid. No shared source file.

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
