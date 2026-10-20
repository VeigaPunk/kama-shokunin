# ScribeRoutedDefects — round-16 report

Scope: dispositions of routed defects 1–6 in `corpus/lessons/round-15-verifier-spotcheck.md:163-172` (access 2026-10-20). Only owned output written: `.ufo/waves/round-16/build/drafts/routed-defects.md`, plus this report.

## Findings

1. **R1 (prior, count comparison): closed.** Repair at `.ufo/waves/round-14/measure.py:358-360`; record at `corpus/knowledge/ollama-evidence-replay.md:317-348`; criterion KQ18 at `corpus/QUALITY.md:87`, scope at `:89-92`. No round-16 change.
2. **R2 (prior, provider failure vs partial output): closed.** Clarification at `corpus/lessons/round-15.md:30`; rule at `corpus/lessons/round-15-verifier-spotcheck.md:54`. No round-16 change.
3. **Process incidents: carried forward.** Bounding clauses are in the round-16 build spec shared context (`.ufo/waves/round-16/build/spec.json`, line 2). They control future seats only; they do not prove compliance. L1 must check each seat's disclosed commands. Interactive-session directories were not opened.
4. **Dispatch provenance: open.** Assigned as build item `ProvenanceLedger` in the round-16 spec. `.ufo/waves/round-16/dispatch-provenance.py` does not exist yet (glob empty). The round-16 `dispatch.json` has no environment-record key. L1 must run the script once it exists.
5. **Replay precision: correction drafted.** `corpus/knowledge/ollama-evidence-replay.md:332-334` says "before the minimum-unique check". In code (`.ufo/waves/round-14/measure.py:357-365`) the duplicate predicate is listed first, but the minimum predicate still runs and may append a second problem; neither short-circuits. Pre-child rejection is enforced at `:378-381`, before `measure_case` at `:386`.
6. **Source wording: cross-source note drafted; cell unchanged.** `corpus/SOURCES.md:24` S012 `teaches` says "Separates running models from the available-model list". The reopened ps page (`https://docs.ollama.com/api/ps`) says "Retrieve a list of models that are currently running" and does not mention an available list. The contrast comes from the tags page (`https://docs.ollama.com/api/tags`, "List available models"). Registry cell not edited; any superseding row is L1's decision.

## Evidence opened this session (access 2026-10-20)

- `corpus/lessons/round-15-verifier-spotcheck.md:163-172`, `:54`, `:56`, `:60-62`: items 1–6; "Provider failure is not proof of absent partial output and advice presence alone is not terminal completion." (line 54).
- `corpus/knowledge/ollama-evidence-replay.md:317-348`: "The promise was false for ≥16 unique names." (line 325); "before the minimum-unique check and before any child process" (lines 332–334).
- `.ufo/waves/round-14/measure.py:351-386` (read-only): `if len(declared) != unique:` / `problems.append("duplicate case names")` (lines 359–360); `if unique < MINIMUM_UNIQUE_CASES:` (line 361); `if corpus:` (line 378).
- `corpus/QUALITY.md:81-92`: KQ18 scope clarification, "nonblank string names".
- `corpus/lessons/round-15.md:17-19`, `:29-30`: attribution row "Append clarification below; no fabricated terminal completion".
- `corpus/SOURCES.md:24`: S012 `teaches` cell as quoted above.
- `https://docs.ollama.com/api/ps` (markdown alternate, 2026-10-20): "Retrieve a list of models that are currently running"; 200 "Models currently loaded into memory".
- `https://docs.ollama.com/api/tags` (markdown alternate, 2026-10-20): "List available models"; `ModelSummary` "Summary information for a locally available model".
- `.ufo/waves/round-16/build/spec.json` shared context (line 2) and `ProvenanceLedger` item (line 84).

## Limits and unknowns

- Code claims are static reads. No runner, classifier, `check.py`, selftest or gate was executed; the claimed pre-child behaviour is read from code only.
- `corpus/lessons/round-16.md` does not exist; the draft is written as its body or appended block for L1 to place.
- Unknown: whether the round-15 operator notification for item 3 was delivered; no evidence either way was in scope.
- Unknown: whether a refused round-16 attempt's payload is recoverable; the spec's ledger records the attempt result digest only.
- A sibling scribe (`ScribeLessonMistakes`) also writes round-16 incident entries; L1 should de-duplicate the item-3 wording against that draft.

## Tools

No installs or updates were performed. Commands run: read and glob only, plus two `_grep` searches and `_read` of the sources above. Nothing was written outside the owned draft and this report.
