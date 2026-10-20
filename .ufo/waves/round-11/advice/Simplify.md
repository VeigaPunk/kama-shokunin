# Simplify — round 11 YAGNI review of C1 provenance and C2 crosswalk

Review execution: `2026-10-20T02:15:08Z` (`date -u`). The steered round label `2026-10-19` appears only in the section heading. No new access or review is dated 2026-10-19. Historical observations keep their original dates or are marked undated. Read-only work only: `sha256sum`, `wc -c`, `grep`, `sed` on kama-shokunin files. No network, no endpoint, no build, no test, no edits outside this report.

## Verified grounding

- **Baseline is valid.** `legacy-baseline.json` lists 9 files. Current `sha256` and byte counts match it for all 9. Every file has 0 column-zero `source:`, `verified-at:` or `recheck:` lines.
- **Placement is forced for legacy files.** The three round-10 knowledge entries (`gguf-runtime-compatibility-boundary.md`, `runtime-health-surface-matrix.md`, `serving-metrics-crosswalk.md`) open with the trio at lines 2–4. Legacy files cannot take that placement without shifting every original byte, which breaks prefix preservation. Append is the only option. The round-11 lesson should state the two placements in one sentence and not add a parser.
- **Only one machine consumer exists.** No file under `tools/` reads `source:`, `verified-at:` or `recheck:`. The C3 counter in `SCORECARD.md` (round-10 row, line 196–203) is `grep -lE '^source: S[0-9]{3}' corpus/knowledge/*.md | wc -l`. I took this from the SCORECARD text. I did not open the census script outside kama-shokunin.
- **`served-model-identity.md` has no date.** The file is 37 lines and starts mid-document at `### Exact readiness-field probes`. It contains no `20YY-MM` string. It refers to a "combined endpoint command" that is absent from the file. The SCORECARD erratum describes it as "one dated llama.cpp metrics sample"; the file bytes do not support "dated". Legacy8's `verified-at` must say the original observation is undated in file bytes.
- **C2 gap is real.** `corpus/knowledge/` contains no `/api/tags`, no `/api/ps`, and no "loaded model" wording. Coverage of Ollama's available-versus-running split is absent.
- **Readiness/identity conflation exists.** `endpoint-identity.md` line 89 labels `GET /v1/models` as "Identity readiness". The crosswalk should separate identity from readiness by pointer. It should not rewrite that line.
- **Existing homes for adjacent topics:** `alias-endpoint-normalization.md` (alias and path normalization), `runtime-health-surface-matrix.md` (`/health` semantics), `serving-metrics-crosswalk.md` (`/metrics`), `cross-lane-scope.md` line 27 (province handoff).

## Deletion candidates

Ordered by weight.

1. **`.ufo/waves/round-11/measure.py` — delete.**
   - The `provenance` mode is a second admission method that duplicates a one-line grep. The `crosswalk` mode (`entry=0/1` by existence and source-ID presence) is a tautological gate. The spec itself says human review checks meaning.
   - Its only permanent value would be a wiring test. A module docstring and negative-control fixtures are maintenance cost with no reader.
   - Replace with pasteable commands in the round-11 lesson, in the style of the round-10 KQ7 count:
     ```sh
     # missing trio fields across the nine legacy files (expect 0)
     for f in alias-endpoint-normalization consumer-registry cross-lane-scope drift-timeline endpoint-identity free-tier-provider-limits listener-census served-model-identity snapshot-history; do
       for k in source verified-at recheck; do grep -qE "^$k:" corpus/knowledge/$f.md || echo "missing $f $k"; done
     done | wc -l
     # prefix preservation, one file: first N original bytes hash to the baseline sha256
     head -c <bytes> corpus/knowledge/<f>.md | sha256sum
     ```
   - One negative control, run once in a temp copy and not committed: delete one trio line, expect the count to become 1, restore.
   - Replacing `verified-at` wording with a pattern check is a speculative parser. Human review decides whether a phrase claims live revalidation.

2. **Five scout seats (SourceOpenAI, SourceLlama, SourceCompatibility, SourceTags, SourceRunning) — delete.**
   - The same five URLs are already opened by the Crosswalk executor and again by SourceCurator. That is seven opens of five URLs.
   - Fold the drift check (S011, S012, S016 quotes against the S-rows) into the Crosswalk acceptance criteria.
   - `SourceLlama` targets `raw.githubusercontent.com/.../master/...`. An unpinned `master` cannot verify the S001 pin at commit `c0fd7862`, so its output would not be admissible anyway.

3. **`ReviewPrior` — delete.** `corpus/lessons/round-10-verifier-spotcheck.md` is immutable and already records the adjudication (its §Spot-check and §Adjudication). Re-extracting it creates a second copy of the same facts.

4. **`FrontierScribe` and `ReportScribe` — delete.** The parent owns `LOG.md`, `SCORECARD.md`, the round-11 lesson, and the integration. Two more writers of the same counts create duplicated mutable state.

5. **Merge reviewer and critic pairs** (keep one seat per claim):
   - `ReviewProvenance` + `AttackFreshness` → C1.
   - `ReviewIdentity` + `AttackCoverage` → C2.
   - `ReviewContract` + `AttackAdmission` → admission.
   - `ProvenanceConnection` duplicates this report's C1 section.

6. **`Planner` — fold or delete.** Its acceptance skeleton duplicates the Measure criteria above. Taxonomy discrepancy stated explicitly: the spec gives role `revenger`, while the prompt says "validator excludes planner taxonomy". The seat is not needed for C1 or C2.

7. **`MutationPlan` — fold into the one-time control above.** Two named mutations are sufficient as a single shell check. A seat is not needed.

8. **Legacy executor seats — keep parallel, but use one template.** Nine seats each choose their own `verified-at` wording. That is nine conventions. One parent-authored template (below) should be pasted in every seat. Their nine separate report files can be replaced by one combined table in the lesson, computed from `git diff`.

9. **`legacy-baseline.json` `missing` arrays — leave as is, do not extend.** They are derivable, but the file is a frozen pre-edit snapshot. The `sha256` and `bytes` fields are the load-bearing part.

10. **Crosswalk per-engine table — shrink columns.** Keep identity route, model-list route, loaded-model route, and ID/name/digest fields. Drop `/health` and `/metrics` columns (pointers to the two matrix/crosswalk entries). Drop alias and path normalization limits (pointer to `alias-endpoint-normalization.md`). Drop province handoff (pointer to `cross-lane-scope.md` line 27).

## Minimum field design (no second admission method)

Legacy supplement, appended at end of file, three column-zero lines:

```
## Provenance supplement — round 11 (2026-10-19)
source: none — historical record            (or a retained local path, e.g. lessons/round-5.md §…)
verified-at: original observation <YYYY-MM-DD from file, or "undated in file bytes">; round-11 metadata review <actual date -u>; no live revalidation, no endpoint contacted
recheck: <safe path/command for authorized revalidation, or "unavailable — no retained source">
```

Rules:
- A legacy `source:` must not begin with `S###`. Otherwise the C3 counter `^source: S[0-9]{3}` inflates from 3 files without new coverage.
- Report the split `grep -c '^source: none'` versus evidence-backed `source:` lines. This prevents "none everywhere" from passing as freshness.
- Date truth: the heading may keep `2026-10-19`. `verified-at` must state the actual UTC review date (`2026-10-20`) and each original observation date, or "undated".
- `served-model-identity.md` → `verified-at: original observation undated in file bytes`.

New crosswalk file (`corpus/knowledge/served-identity-crosswalk.md`), trio at top like the round-10 entries:
- `verified-at:` cites the actual UTC date of the execution that opened each source, plus "vendor docs opened; no local runtime contacted".
- Sections: availability (`/api/tags`, S011; llama.cpp `/v1/models`), loaded models (`/api/ps`, S012), alias identity (pointer), readiness (pointer to `runtime-health-surface-matrix.md`, with the `endpoint-identity.md` line 89 label flagged).
- `S016` is reference-only: not local runtime proof.
- One file. No edits to `served-model-identity.md` beyond the appended supplement.

## Preserved contract

- No other files changed. Only `.ufo/waves/round-11/advice/Simplify.md` was written.
- No tool installs or upgrades.

## Limits

- The C3 counter is taken from `SCORECARD.md` text. The census script was not opened.
- I did not verify any live endpoint or source. Grounding is from kama-shokunin files only.
- Legacy-file meaning (whether each supplement's claim is true) is not judged here. That is for human review.
