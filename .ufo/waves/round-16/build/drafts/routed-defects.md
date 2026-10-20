# Round 16 — dispositions of round-15 routed defects (items 1–6)

Drafted 2026-10-20 by ScribeRoutedDefects for L1 integration. Source of the routed list: `corpus/lessons/round-15-verifier-spotcheck.md:163-172` (access 2026-10-20). No gate, harness, selftest or runner was executed for this draft; code claims are static reads. `corpus/lessons/round-16.md` does not exist yet; the prose below is intended as its body or as an appended block, whichever L1 uses.

## Summary table

| # | Routed item (round-15 verifier) | Round-16 disposition | Action this round |
|---|---|---|---|
| 1 | Prior R1 → resolved | Closed by round-15 repair | None to runner or guard |
| 2 | Prior R2 → resolved | Closed by round-15 clarification | None |
| 3 | Process incidents → next steered round / operator awareness | Carried forward, partially controlled in-round | Verify bounding clauses in every seat output; no rerun |
| 4 | Dispatch provenance → kama next round | Carried forward into a round-16 build item, not yet delivered | L1 runs the new ledger script once it exists |
| 5 | Replay precision → kama | Precision appended this round | Append-only correction below |
| 6 | Source wording precision → kama | Cross-source note appended this round; registry cell unchanged | Append-only note below; no row edit |

## 1. Prior R1 (missing count comparison) — closed, no round-16 change

The repair is in the runner: `.ufo/waves/round-14/measure.py:358-360` now reads `if len(declared) != unique:` / `problems.append("duplicate case names")`. The replay record of the repair is `corpus/knowledge/ollama-evidence-replay.md:317-348`, which states "The promise was false for ≥16 unique names" and names the frozen pre-repair snapshot `.ufo/waves/round-15/frozen/measure-before.py`. The fail-capable criterion is KQ18 at `corpus/QUALITY.md:87`, with its scope clarification at `corpus/QUALITY.md:89-92`: "name injectivity" means the runner's declared nonblank string names, stripped and compared case-sensitively; missing, blank and non-string names are not certified by this repair.

Round 16 adds no runner, guard or fixture change for this item. Unknown and not established here: the round-15 red/green matrix results. This draft reads the code only and does not re-measure it.

## 2. Prior R2 (provider-failure versus partial output) — closed, no round-16 change

The clarification is the attribution row in `corpus/lessons/round-15.md:30`: the fix is "Append clarification below; no fabricated terminal completion or rerun of provider failure; this clarification earns no separate C1/axis credit." The governing statement is `corpus/lessons/round-15-verifier-spotcheck.md:54`: "Provider failure is not proof of absent partial output and advice presence alone is not terminal completion." `corpus/QUALITY.md:81-83` records that the R2 clarification is append-only history and adds no criterion.

Round 16 adds nothing for this item. Terminal success for any round-16 seat must come from its completion summary, not from file presence.

## 3. Process incidents — carried forward; in-round control present, not proof of compliance

The round-15 verifier retains these as incidents, not evidentiary wins (`corpus/lessons/round-15-verifier-spotcheck.md:60-61`): a broad lane-local grep matched an ignored session-directory snippet against the session-access restriction, a name-only directory listing was disclosed, and two seats evaluated or parsed content against no-execution or no-verification instructions.

The round-16 build spec carries the bounding text in its shared context (`.ufo/waves/round-16/build/spec.json`, shared context line 2): "Never read `.ufo/interactive-sessions/`, ~/.omp sessions/history, or any session/transcript/credential store; bound every grep/glob to the paths your item names." It also states "Measurements belong to L1: run no lane gate, harness or test against the lane except what your item explicitly allows."

These clauses are a control for future seats. They do not show the round-15 incidents were resolved, and they do not show that any round-16 seat obeyed them. L1 must check each round-16 seat's disclosed commands against those clauses when recording conformance. No retrospective rerun of prohibited access is requested. Unknown: whether the round-15 operator notification was delivered; this draft has no evidence either way.

## 4. Dispatch provenance — carried forward into a round-16 build item; not closed

The round-15 gap was that validation receipts record effective policy bands but their argv does not retain the environment bindings. Refused payload bytes and retry timing were also not independently established (`corpus/lessons/round-15-verifier-spotcheck.md:56` and `:62`).

The round-16 build spec assigns this as item `ProvenanceLedger` (`.ufo/waves/round-16/build/spec.json`, the item prompt quoting "Routed defect 4 ... wave validation receipts must preserve the environment bindings and refused-attempt identity"). As specified, the script records argv, cwd, exactly three environment bindings (`UFO_CONFIG_PATH`, `UFO_FLEET_ALLOW_EXTERNAL_TOOLS`, `UFO_PROJECT_ROOT`), exit, stdout digest and a taskCall digest, and appends refused or spawned attempts with their result digest.

Status at drafting: the script `.ufo/waves/round-16/dispatch-provenance.py` does not exist (glob returned no files). The round-16 `dispatch.json` top-level keys are `compaction, counts, note, policy, registry, resumeSends, schema, taskCall, wave`; none is an environment record. Limits that remain: a `result_sha256` proves the identity of the recorded attempt result, not of a refused payload the result does not contain; the ledger does not certify omitted environment variables beyond the three named ones. Item 4 stays open until L1 runs the script on the real round-16 spec and checks the output.

## 5. Replay precision — appended correction (no history rewritten)

`corpus/knowledge/ollama-evidence-replay.md:332-334` says the repaired runner rejects repeated names "before the minimum-unique check and before any child process". The precise reading, appended here and not a rewrite of that entry:

In `corpus_problems` (`.ufo/waves/round-14/measure.py:357-365`), the duplicate predicate appends `"duplicate case names"` first in list order. The minimum predicate (`unique < MINIMUM_UNIQUE_CASES`) is then evaluated and may append its own problem. Neither predicate short-circuits the other: a corpus with both defects reports both problems. The pre-child rejection is enforced by `run()` (`.ufo/waves/round-14/measure.py:378-381`): when the corpus problem list is non-empty, every case becomes an unmeasured record, and the per-case `measure_case` call (`:386`) is not reached. The admitted outcome is unchanged: a valid all-distinct corpus of at least sixteen names measures as before.

## 6. Source wording precision — cross-source note appended; registry cell unchanged

The S012 `teaches` cell (`corpus/SOURCES.md:24`) reads "Separates running models from the available-model list and exposes digest, context length, VRAM use, and expiry." The reopened `https://docs.ollama.com/api/ps` page (access 2026-10-20) says, in its summary, "Retrieve a list of models that are currently running", and its 200 description is "Models currently loaded into memory". It does not mention an available-model list. The available side is on `https://docs.ollama.com/api/tags` (access 2026-10-20): operation description "Fetch a list of models and their details", 200 "List available models", and `ModelSummary` "Summary information for a locally available model".

So the separation is a cross-source synthesis: S012 supplies the running-state fields, and the available-list contrast comes from S011/S031 on the tags page. The S012 cell is not edited in this round. The round-15 verifier's standing rule still applies: a corrected immutable cell is superseded by an appended row, not rewritten. Whether to add such a row is a registry decision for L1 and is not made here. The fields S012 does document (`name`, `model`, `digest`, `size`, `size_vram`, `context_length`, `expires_at`) and the readiness boundary (S012 does not establish readiness or local weights) are unaffected.

## Closing note

No new L0 decision is needed for these dispositions. Items 3 and 4 remain open by their nature: item 3 needs seat-level verification by L1, and item 4 needs the round-16 script to exist and be run by L1. No promotion, host transaction, service restart, tool installation or lane gate run is implied by this draft.
