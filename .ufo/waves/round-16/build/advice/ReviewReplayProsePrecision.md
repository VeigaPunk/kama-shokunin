# ReviewReplayProsePrecision — routed defect 5 (nonblocking prose precision)

Read-only review. Nothing edited except this Report. No lane gate, harness, matrix, or
probe was run (measurement belongs to L1); all implementation claims below are static
reads of the cited files.

## Verdict

Defect confirmed and nonblocking. `corpus/knowledge/ollama-evidence-replay.md:332-334`
compresses two independent guard checks into a misleading "before the minimum-unique
check" ordering. The implementation appends the duplicate problem and *then still*
evaluates the minimum check; rejection (unmeasured records, exit 1, zero children)
happens after both checks. The admitted round-15 outcome is unchanged. One exact
append-only sentence is proposed below; lines 332-334 must not be reworded.

## Axes (Godspeed)

| Axis | Effect |
| --- | --- |
| calibration | improved: prose claim is aligned with the literal predicate order, no new claim |
| operability | none: harness-only wording; no endpoint, launch, or service behavior |
| coverage / adjacency | none: no new surface, no province change |

## Evidence

- Routed defect: `corpus/lessons/round-15-verifier-spotcheck.md:169` —
  "Replay entry:332–334 says rejection occurs “before the minimum-unique check”;
  implementation first appends a duplicate problem, then still checks the minimum".
- Imprecise claim: `corpus/knowledge/ollama-evidence-replay.md:332-334` —
  "rejects any repeated declared name (`"duplicate case names"`) before the
  minimum-unique check and before any child process".
- Duplicate predicate first, then unconditional minimum predicate (independent `if`s):
  `.ufo/waves/round-14/measure.py:359-360` — `if len(declared) != unique:
  problems.append("duplicate case names")`; `.ufo/waves/round-14/measure.py:361-364` —
  `if unique < MINIMUM_UNIQUE_CASES: problems.append(...)`.
- Rejection after both checks, before any child: `.ufo/waves/round-14/measure.py:375-381`
  (`corpus, unique_names = corpus_problems(cases)`; `if corpus:` builds
  `unmeasured_record` for every case) with the only child branch at `:382` (`elif
  tool_present:`); exit 1 derived at `:396-398` (`failed == 0` fails because every
  unmeasured record has `passed: False`, `:174`).
- Frozen pre-repair source lacks the duplicate predicate:
  `.ufo/waves/round-15/frozen/measure-before.py:350-362`; its `manifest.json` records
  sha256 `fda61e001ca8c2533c99a1759bb4b82f3260a72fafccf72f863f3f4e3684b60d`, matching the
  file. A diff against the current runner shows the two appended predicate lines as the
  only functional change (docstring/`LIMITS` prose aside).
- Graded rejected contract: `tests/ollama-corpus-guard/check.py:36-41` — "A rejected
  expectation requires exit 1, a ``duplicate case names`` error"; grading at
  `:529-576` also requires `failed == total`, `observed_exit` null on every record, and
  `runner process events 0` / `subprocess.Popen events 0`.

## Exact append-only correction sentence

Insertion point: append at end of file, after
`corpus/knowledge/ollama-evidence-replay.md:374` (the existing `Final declared-name
boundary` bullet), preceded by one blank line. Every existing byte, including lines
332-334, stays untouched.

Exact text to append:

```markdown
- **Repair ordering precision (appended).** The Repair bullet's "before the minimum-unique check" denotes evaluation order, not short-circuit: `corpus_problems()` (`.ufo/waves/round-14/measure.py:351-365`) appends `"duplicate case names"` first and then still evaluates `unique < MINIMUM_UNIQUE_CASES` (so a duplicated and undersized corpus can report both problems), and `run()` (`.ufo/waves/round-14/measure.py:375-381,396-398`) rejects with per-case unmeasured records and exit 1 before spawning any child.
```

Why this is exact:

- "denotes evaluation order, not short-circuit" corrects the implicated reading without
  claiming the duplicate check is skipped or that the minimum check is skipped.
- "appends `"duplicate case names"` first and then still evaluates" matches the two
  independent `if` blocks at `:359-364`, including the dual-problem case.
- "rejects with per-case unmeasured records and exit 1 before spawning any child"
  matches `:375-381` + `:396-398` and the graded zero-child contract at
  `tests/ollama-corpus-guard/check.py:36-41`.
- Current-path line references are used, consistent with the replay entry's own
  "current path now contains the corrected guard" convention at `:359`.

## Residual risk and verification gaps

- **Static-only evidence for the dual-problem clause.** `corpus_problems()` appends the
  duplicate problem and the minimum problem in independent `if`s, so a duplicated and
  undersized corpus can emit both. No committed matrix case combines a duplicate with
  fewer than 16 unique names: a scan of all 12 `tests/ollama-corpus-guard/*.json` files
  found no `expected_rejected` case with `unique < 16`. `check.py` only requires the
  error to *include* `duplicate case names` (`:537-541`), so an optional L1
  dual-problem case would pass the existing rejected contract; adding it is L1's call,
  not this seat's.
- **Line-number drift.** The frozen snapshot has the guard at
  `.ufo/waves/round-15/frozen/measure-before.py:350-362`; the proposed sentence cites
  the current path `.ufo/waves/round-14/measure.py:351-365`. If the runner is later
  moved, the sentence's references drift, exactly like the entry it corrects.
- **Seat boundary.** No behavior, result, receipt, registry row, or frozen baseline was
  modified; the sentence records prose precision only and changes no measured outcome.
- **No installs.** No tool installation or upgrade was performed for this review.

## Node for L1

The proposed sentence is the complete deliverable of routed defect 5; no other wording
in `ollama-evidence-replay.md:325-374` needs an append. Do not rewrite lines 332-334.
