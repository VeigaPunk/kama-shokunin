# R2Partial — advisory read: partial output is not terminal success

**Seat:** `KamaR15.R2Partial-3` (scribe, leaf)
**Scope:** Read-only advisory of `.ufo/waves/round-14/advice/ExistingProbe.md` and `.ufo/waves/round-14/integration-review.json`, plus a draft clarification. No historical file edited. No checks, tests, builds, linters, or smoke runs executed.
**Tooling:** None installed or upgraded.

## 1. Evidence read

| Path (under kama-shokunin root) | Observation |
|---|---|
| `.ufo/waves/round-14/advice/ExistingProbe.md` (`#2AEF`) | Full advisory, header `verified-at: actual review 2026-10-20 (UTC)`, seat `KamaR14.ExistingProbe`, states read-only, no checks. |
| `.ufo/waves/round-14/integration-review.json` (`#9E02`) | `wave.dead_seats` lists `KamaR14.ExistingProbe`, reason "Cursor RESOURCE_EXHAUSTED; provider unreachable", scope "source convention independently held in SKILL and crosswalk". `accepted` row: "ScopeSimplifier/ExistingProbe contract: no basename/GGUF/case/implicit latest normalization; no integration with old live probe". |
| `.ufo/waves/round-14/advice/swarm-registry.json` | `ExistingProbe` member is a `spawn` with `agentId KamaR14.ExistingProbe`, role `scout`, `item: null`. |
| `.ufo/waves/round-14/rulings.json` (`#DBB3`) | Authoritative precedence. Selection is exact, case-sensitive `name == expected OR model == expected`; no basename, `.gguf`, or case normalization. |
| `tools/kama-probe.sh:324-388` | Spot-checked by reading only. Matches ExistingProbe §2.1–2.3: `served_ids` precedence at 324-325, grep fallback at 362-368, `normalize_id` at 370-371, `model_matches` at 373-388. |

## 2. Finding: the ExistingProbe file is partial output, not a terminal success

- The file exists and is complete as prose, but `integration-review.json` records its seat as **dead**. The accepted disposition for the area cites the **contract** (`ScopeSimplifier/ExistingProbe contract`, backed by `rulings.json` and the SKILL/crosswalk), not the ExistingProbe output.
- Therefore `advice/ExistingProbe.md` must be read as advisory partial output. It does not count as a terminal success of the ExistingProbe seat, and no acceptance credit should attach to it by existence alone.
- Provenance is not determinable from the files: nothing records which run wrote the file after the seat was recorded as dead. [INFERENCE] It was written after the RESOURCE_EXHAUSTED event or the dead-seat record was written without reconciling the file.

## 3. Finding: content issues in ExistingProbe.md (advisory, for owners)

1. **§4 C2 expected result is hedged and conflicts with `rulings.json`.** The file gives "`unknown` (exit 2) or `remote_inventory` (exit 1)" for `expect: qwen2.5:7b` against tag name `ollama.com/library/qwen2.5:7b`. Under rulings rule 3 and input rule "Selection: exact", that entry is not selected, so the only correct result is `unknown` (exit 2). `remote_inventory` requires a selected entry. Owner must pick one result, not both.
2. **Identifier collision.** ExistingProbe §4 labels adversarial rows `C1`–`C6`. The wave's calibration claim is also `C1`. Readers can conflate them. Owner should rename the adversarial rows (for example `A1`–`A6`) in any future integration.
3. **Citations not verified by this read:** `tools/kama-probe.sh:925-926, 959-971`, `SKILL.md:142-159`, `corpus/knowledge/endpoint-identity.md:20-22`, `corpus/knowledge/served-identity-crosswalk.md:23-45`, `corpus/knowledge/gguf-runtime-compatibility-boundary.md:8-14`, `corpus/SOURCES.md:23,24,43`, `corpus/QUALITY.md` KQ17. Only the `tools/kama-probe.sh:324-388` range was read.
4. **Recommendations §5.1–5.3** match `rulings.json` in substance (exact selection, no `normalize_id`/`basename`/`rstrip`/`lower`, cardinality checks, name/model conflict, digest compared only after selection). These are consistent with the authoritative ruling; they are not independent evidence that the implementation follows them.

## 4. Draft clarification (for L1 to append; not applied here)

> **Round-15 clarification — partial output is not terminal success.**
> A file under a round's `advice/` directory is partial output of one seat. It is terminal only when the integration record (`integration-review.json`, `rulings.json`) gives that seat an accepted disposition. `advice/ExistingProbe.md` (round-14, `#2AEF`) is advisory. Its seat, `KamaR14.ExistingProbe`, is listed in `integration-review.json` `wave.dead_seats` (Cursor RESOURCE_EXHAUSTED; provider unreachable). The round-14 accepted row for the area cites the contract (`ScopeSimplifier/ExistingProbe contract`, backed by `rulings.json`), not the file's prose. Existence of the file is not evidence of terminal success. Historical round-14 files are not rewritten; this clarification is appended only.

Placement suggestion: appended section in the round-15 integration artifact, never by editing `.ufo/waves/round-14/` files.

## 5. Limits

- Read-only; no command was run. No verification of tests, fixtures, or the `measure.py` guard was performed (out of scope for this seat).
- The ExistingProbe output was not re-derived from the code beyond the one cited range.
- Provenance of `ExistingProbe.md` relative to the dead-seat record cannot be settled from files alone.
- No history, session, credential, or `agent.db` access; no `omp` CLI invoked.
- No tools installed or upgraded.

## Report trailer

- Files read: `.ufo/waves/round-14/advice/ExistingProbe.md`, `.ufo/waves/round-14/integration-review.json`, `.ufo/waves/round-14/advice/swarm-registry.json`, `.ufo/waves/round-14/rulings.json`, `tools/kama-probe.sh:322-390`, round-15 `build/spec.json` items.
- Files written: this report only.
- Files not edited: all round-14 files, all round-15 files other than this report.
