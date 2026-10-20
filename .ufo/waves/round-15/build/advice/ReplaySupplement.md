# ReplaySupplement — R1 named correction appended to replay knowledge entry

seat: KamaR15.ReplaySupplement-3 (leaf)
scope: `corpus/knowledge/ollama-evidence-replay.md` append only

## Files changed

- `corpus/knowledge/ollama-evidence-replay.md` — appended section
  "Round-15 correction — measurement runner duplicate-corpus promise was
  false (R1)" after the closing `## Cited sources` block (inserted after
  old line 315; new section at lines 317-355). No prior byte modified;
  frontmatter, claims, decision table and QUALITY clearance untouched.

## Behavior (what the append records)

- The round-14 runner's promise that "narrower or duplicated corpora fail
  before any child runs" was false for corpora with ≥16 unique names:
  `corpus_problems()` compared only the unique `name.strip()` count against
  the minimum and never compared declared total vs unique.
- The repair (sibling seat, verified by read of
  `.ufo/waves/round-14/measure.py:350-364`) adds
  `if len(declared) != unique: problems.append("duplicate case names")`
  before the minimum check, so any duplicate corpus now fails before any
  child process; a valid ≥16 all-distinct corpus measures unchanged.
  Runner repaired in place at its historical path; pre-repair snapshot
  frozen at `.ufo/waves/round-15/frozen/measure-before.py`.
- Committed test surface cited: `python3 tests/ollama-corpus-guard/check.py`
  (+ `--selftest`, + `--runner .ufo/waves/round-15/frozen/measure-before.py`
  to expose the old defect) over `tests/ollama-corpus-guard/*.json`.
- Old receipt kept as the historical actual unique-corpus result
  (independently recounted 51/51 unique); only the generalized
  "duplicated corpora fail" guarantee is corrected, not rewritten.
- Explicit bound: no new API fact, engine behavior, runtime observation or
  classifier rule; the correction covers the harness guard only and does
  not touch the classifier's own duplicate-selection `invalid_input`
  (decision-table row 3).

## Evidence retained

- `corpus/lessons/round-14-verifier-spotcheck.md:142` — R1 routes exactly
  this repair + named prose correction; records the false-guard finding,
  the 51/51 recount, and "do not rewrite this round's receipt".
- `.ufo/waves/round-14/measure.py:13-14,77` — original false promise text
  (docstring + LIMITS[3]); `:350-364` — repaired guard read back post-edit.
- `SKILL.md:478-501` — committed gate row for
  `tests/ollama-corpus-guard/check.py` and frozen-runner flag; matches the
  commands cited in the append.
- `tests/ollama-corpus-guard/` — 9 fixture JSONs present at write time
  (AppendDuplicate, DistantDuplicate, MiddleDuplicate, MultipleDuplicates,
  ObjectEnvelope, PrependDuplicate, TabCollision, TriplicateName,
  WhitespaceCollision). `check.py` is a sibling-owned file; it did not
  exist at my write time but is cited as the committed command per the
  wave contract and the SKILL gate row already landed.
- `.ufo/waves/round-15/build/advice/GuardRepair.md` — sibling executor's
  report confirming the two-line guard insert.

## Risks / limitations

- The append describes the repair and test command as of the wave
  contract; I executed nothing (no verification runs, per leaf policy).
  L1 post-integration gate should confirm `check.py` exists and the cited
  matrix behavior holds.
- `check.py` not yet on disk at append time — transient in-flight state,
  not a scope conflict; the citation is contract-correct once the sibling
  lands. If it does not land, the SKILL row and this section's test
  citation would both need the missing prerequisite flagged.
- UnicodeDuplicate.json and ValidBoundaries.json fixture files were also
  absent at write time (sibling seats still in flight); the section's
  enumeration mentions "a non-ASCII duplicate" and "valid ≥16-unique
  controls" generically and remains accurate once those files land.
- R2 partial-output clarification is not in this file's scope (named
  elsewhere in routing); GuardRepair.md records that ownership split.

## Blockers

None.

## Tools installed

None. No pacman/uv/npm actions; RULES.md not needed.

Report: .ufo/waves/round-15/build/advice/ReplaySupplement.md
