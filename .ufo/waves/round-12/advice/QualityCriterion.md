# Round 12 — KQ15 source-correspondence criterion

Seat: KamaR12.QualityCriterion (executor, author advisor). Scope: only
`corpus/QUALITY.md`. Axes: calibration (historical-evidence repair) and quality
(criterion honesty); operability, freshness, depth and adjacency untouched. No
scalar, capability, serving-readiness or live-host claim.

## Change made

Appended a new section at `corpus/QUALITY.md:43-49`, after the unchanged KQ14
row:

```text
## Criteria added — round 12 (2026-10-20, author-appended; no outside review yet)

No earlier criterion is superseded. KQ14's semantic-human boundary remains in force.
```

KQ15 requires, in the admit column:

- byte comparison of a frozen copy with `git show <pinned-commit>:<source-path>`
  bytes, with **source correspondence reported separately from SHA-256 digest
  integrity** against a pinned manifest that names snapshot hash, source commit
  and source path;
- clean only when both hold; mismatch, snapshot tamper and unavailable source
  each get distinct nonzero exits;
- an overridden snapshot without its manifest can only expose a mismatch, never
  authorize a pass;
- corrections land as a new dated snapshot plus its own manifest, old frozen
  receipt byte-intact, with an appended erratum naming it.

Reject/limit column refuses a shipped-expected digest match, green `--selftest`,
size/line count, or pager/artifact-rendered copy (the round-11 D1 truncated tail
carried an `artifact://1157` marker) as evidence of correspondence with git
history; refuses rewriting old frozen bytes/manifest so a mismatch is merely
restated. It restates KQ14: correspondence or digest alone does not prove the
historical claim's content.

Motivating lesson column cites `lessons/round-12.md` Mistakes
(frozen-snapshot correspondence) and `lessons/round-11-verifier-spotcheck.md`
D1, which records the actual-before and frozen-before SOURCES hashes differing
while the shipped expected digest matched.

## Static findings

- Before this edit, `corpus/QUALITY.md` ended at KQ14 (line 41); no KQ15 or
  round-12 section existed.
- KQ1-KQ14 rows are unchanged; the KQ14 row was not reflowed or rewritten.
- `corpus/lessons/round-12.md` does **not** exist yet: `corpus/lessons/` contains
  no `round-12*` file, and no other round-12 seat prompt owns that path
  (MistakeScribe drafts only `advice/MistakeScribe.md`). KQ15's motivating
  citation therefore names a lesson L1 must author at integration. If the lesson
  does not land its D1 correspondence row, KQ15's motivating citation is
  unsupported and L1 should amend the citation rather than leave it dangling.
- `git status` before the edit showed only the untracked `.ufo/waves/round-12/`
  directory; HEAD was `79fa257` (round-11 verifier spot-check). No prior
  round-12 tracked edits existed.

## Unrun (not pass)

No `fidelity.py`, `reproduce.py`, `--selftest`, digest comparison, `git show`
extraction, source census, endpoint call, build, lint or test was run by this
seat. The exact-bytes CLI behavior and the claimed 1 -> 0 corrective-snapshot
result are **not demonstrated here**; KQ15's control clauses are obligations,
not observed exits. No failure is asserted as demonstrated before the L1
acceptance run.

## Checks for L1

1. `git diff -- corpus/QUALITY.md` shows additions only (new section plus row);
   KQ1-KQ14 absent from the diff.
2. Author `corpus/lessons/round-12.md` with a §Mistakes row for frozen-snapshot
   correspondence (D1) and confirm the KQ15 motivating cell resolves to it.
3. Run `python3 .ufo/waves/round-12/reproduce.py` once and record the actual
   old-snapshot mismatch and new-snapshot clean receipts; only then rely on the
   1 -> 0 claim. Do not treat KQ15's header or reject examples as that receipt.
4. Confirm SKILL.md's D3 registry/list names all appended criteria, including
   KQ15, rather than stopping at KQ14.
5. Keep the round-12 heading labeled unreviewed; an outside review of record is
   still absent.

## Risks

- The lesson citation is forward-looking (see above), the one non-self-contained
  reference in the row.
- KQ15 overlaps KQ11 (provenance-field presence) and KQ14 (claim-content review)
  but does not supersede either: it isolates input-file correspondence from
  digest integrity, while KQ14 keeps human/source review as the semantic gate.
- `artifact://1157` is quoted only as a presentation-channel marker from the
  round-11 verifier observation, not as current artifact content.

Tools installed/updated: none.
