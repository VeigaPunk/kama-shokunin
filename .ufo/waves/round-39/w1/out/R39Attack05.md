# R39-05 — full mirror completeness and E11

Item: inspect working evidence for the lesson's claim that a full-repository scratch mirror resolves E11 used-by findings. No repo content modified.

## Axes
- Calibration (C1): does stored validation evidence support the claim that mirror completeness, not a weakened gate, explains E11 disappearance?
- Coverage (C2): are E11 used-by references covered by the full mirror and is the residual outcome stated accurately?

## Observable findings

### 1. E11 is a missing-path finding, not a blanket completeness proof
- `scripts/sources-census.sh` documents E11 as “used-by path missing on disk” and exit 1 for validation findings (header lines 16–18, 24–33). Its `usedby_findings` code checks each mined row's non-dash used-by path against `$dir/$path` (`538–570`).
- The lesson says the initial corpus-only mirror produced E11 for registry used-by paths outside the copied corpus subtree and was discarded (`corpus/lessons/round-39.md:27,39`). This matches the documented check's behavior.

### 2. Stored full-mirror validation has no E11; warnings remain
- `assimilation/validate.out` records 93 W04 duplicate-URL-across-scopes warnings and ends `file ok <mirror>/corpus/SOURCES.md`; counted E11 lines: **0**. W04 is explicitly nonfatal in the script header; warnings do not establish full correctness by themselves.
- In the scratch validate mirror, root-level `registry/`, `tools/`, etc. exist, and `corpus/knowledge/served-identity-crosswalk-amendment-2026-10-24-r16.md` exists. SOURCES and the round-39 lesson match the lane working copies byte-for-byte (both SOURCES SHA-256 `9cd2451a8a8f08a55df7da623af33dadb01aeeb3c31bac8f4366075c97e7735a`; lesson SHA-256 `c1c744cf92c9e299ae7dc37930e062c17dec7e6a2649fd9cd12486a21107135f`).
- The mirror is not an exact whole-tree snapshot: its top level contains `.git` plus the copied project files; `find` counted 16,754 files within the mirror (excluding nested `.git) versus 16,786 outside it, and a recursive comparison timed out before completion. Thus “full repository” is supported for the relevant registry and referenced paths inspected, but exact all-file completeness is not established by this independent observation.

### 3. Mirror validation is not the same as live lane census
- `census-start.out` records pre-state census as exit 2 because fleet configuration is unavailable from the scratch root. Therefore this artifact cannot independently confirm live fleet-wide census behavior.
- `census-end.out` is a stored validation/census-like output containing W04 rows; do not treat it as proof that the lane's full repository was passed as `--root`. The available clean validation evidence is specifically the recorded `validate --file .../corpus/SOURCES.md` result.

## Verdict
The E11 explanation is consistent with the script and the stored validation record: a corpus-only subset can omit repository-root used-by targets, while the broader mirror contains the cited root-level directories and the saved validate output has no E11. However, exact full-tree mirror completeness and live fleet census success are not proven by the available observations (recursive comparison timed out; census-start is exit 2). No falsification of C1/C2 follows from this scoped item; treat the stronger “full-repository complete” wording as only partially evidenced.
