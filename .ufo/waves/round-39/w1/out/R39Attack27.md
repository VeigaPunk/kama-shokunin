# R39Attack27 — wave artifact reference resolution

**Axes:** calibration, coverage. **Severity:** Medium (claim-evidence lineage defect).

## Finding

The round-39 artifact package resolves the declared README coverage pointer and S472 source-row path to working-tree files in the scratch clone, but does not establish that those evidence artifacts are present in the declared base commit or the reported final source repo. The reference resolution is internally inconsistent across the two repositories checked.

## Evidence

- The scratch lane root is at `6a4afdfe48b0b54239d127761d21a5cf21b5b0ea`. Its round-39 `assimilation/validate` clone is also at that base and has working changes to `corpus/README.md` and `corpus/SOURCES.md`, plus untracked `corpus/knowledge/served-identity-crosswalk-amendment-2026-10-24-r16.md` and `corpus/lessons/round-39.md`.
- In that clone, README's round-39 coverage row names the amendment path; the file exists (27 lines) and has a round-39 addendum. `SOURCES.md` has row S472 at line 216, citing that amendment as `used-by`. This verifies the local working-tree path chain, not a committed chain.
- Frozen preregistration's C2 explicitly requires the README pointer, file existence, and S472 present at tip/absent at base; the claim capture `claim-after.out` reports these as `1/1/1`, with its base control as `0/0/0`. C1's counter likewise says the new source row quote resolves at Markdown line 17.
- The independent declared destination `/home/vgpnk/Projects/shokunin/kama-shokunin` has neither amendment nor round-39 lesson; direct checks returned `No such file or directory`. The round-39 out directory exists and is empty for this report before writing. The path mentioned by the report context is distinct from the lane scratch working copy that contains the evidence.
- `claim-after-initial.out` further describes README pointer=1 and claims S472 was absent at base and present at tip, but the scratch root itself remains at base while those files are only in the nested working clone. Thus “tip” is ambiguous unless qualified as the nested checkout's working tree.

## Exploit path / impact

A reviewer following the trailer or README/S472 `used-by` path at the declared source-repository location cannot resolve the amendment, and a reviewer treating the scratch root's base commit as the tip cannot resolve the round-39 additions either. The nested clone's uncommitted additions make the predicates look satisfied while no committed artifact lineage is demonstrated at either declared root. This can overstate calibration/coverage evidence and make later replay depend on inaccessible/uncommitted bytes. No evidence supports malicious execution or secret exposure.

## Smallest remediation

Publish the referenced amendment, lesson and relevant README/SOURCES additions to the declared source checkout (or correct the report root consistently), then capture the exact commit/tree and ensure the report's relative trailer paths resolve there. Recompute the frozen-predicate evidence against that exact tree; do not count working-tree presence as committed lineage.
