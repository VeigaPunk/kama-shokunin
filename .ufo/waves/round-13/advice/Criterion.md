# Criterion — round-13 KQ16 append

Owner: KamaR13.Criterion (executor). Write set: `corpus/QUALITY.md` and this
report only. No other file written by this seat. Tools installed/updated:
**none**.

## Change landed

`corpus/QUALITY.md` gains a new round-13 section after the round-12 table and
one `KQ16` row. KQ15 and every earlier byte are untouched.

- Original prefix: **8619 bytes**, SHA-256
  `157495271d58d6deb56260b093923961e40fb8402ed7475bc4a05c88cdd173cf`,
  equal to `HEAD:corpus/QUALITY.md` at lane HEAD
  `941bb32c3f591bc63cbf7579b2b6c552228307cd`. Final file: **12469 bytes**,
  SHA-256 `596f87caf560a5b6c70e7796597a9d2788b9074149ae99f205b73ef2dbb813da`,
  61 newline-terminated lines. `final.startswith(original)` is true.
- KQ15 line with its newline retains SHA-256
  `b559befa6bf3bbdabd00482d6a6630bbfbefdf8d4371f74d998f6e1f9c07618c`;
  only bytes after the original final newline were added.
- New header states the outside review and the limited supersession:
  `lessons/round-12-verifier-spotcheck.md` D1 routed defect 1. The section
  intro says KQ16 supersedes only KQ15's exit-class and capture/comparison
  formulations and preserves the rest. The ID cell is bare `KQ16` because the
  bounded probe's row regex (`^\|\s*KQ16\s*\|`) requires the pipe directly
  after the ID; the supersession is stated in the immediately preceding
  paragraph of the same section. The intro keeps every other KQ15 boundary,
  KQ14's semantic-human boundary, and states that no admission method is
  added.

## Literal audit assertions

Both exact phrases appear once, inside the KQ16 admit cell of the single
KQ16 row (4 cells, one physical line):

- `source_mismatch=1; snapshot_tampered=2; source_unavailable=2`
- `capture: git show; comparison: git cat-file blob`

The exit map is qualified in the same row: the exit belongs to the selected
primary finding under the code's `PRIORITY` order. `source_mismatch` is exit 1
only when it is selected and no higher-precedence could-not-evaluate finding
is present; `snapshot_tampered` and `source_unavailable` share exit 2 and are
distinguished by ID; the other declared could-not-evaluate IDs
(`snapshot_unavailable`, `manifest_invalid`, `unpinned`, `internal_error`)
also exit 2; a mismatch co-occurring with a higher-precedence finding exits 2
while the correspondence count records it only when the pinned anchor is
verified (`fidelity.py:323` counts only `source_matches is False and
anchor_matches is True`); an unavailable anchor counts zero mismatches; a
lower-precedence listed ID does not imply that ID's exit. The override
sentence says a mismatch is exposed as `source_mismatch` while a matching
unpinned snapshot is a could-not-evaluate exit-2 finding, never a pass.

Capture is labeled author-recorded provenance (S032), not gate-verified: the
committed comparison code corroborates only the separate `git cat-file blob`
read, checked against code-pinned revision/path/OID/digest, not which command
created the frozen file. The reject cell forbids treating the `git show`
capture as its own comparison, command-verified provenance, or reproducible
from committed comparison code; it also forbids treating a same-repository
read as independent provenance authority, collapsing the two shared-exit2
findings, or requiring different exits for distinct IDs. It ends with the
bounded-documentation limit: the quoted phrases are anchors, not semantic
proof; a textual gate does not establish semantic admission; KQ14 still
governs.

The active KQ16 row does not contain KQ15's rejected wording
`distinct nonzero exits` (whitespace-normalized static match false), nor the
rejected `fetched directly as` clause.

## Grounding (static reads only)

- `lessons/round-12-verifier-spotcheck.md:147` (routed defect 1) is the
  finding-ID/exit-class and `git show`/`git cat-file blob` correction;
  line 151 confirms a real mismatch may coexist with an exit-2
  integrity/manifest finding. Line 149 is the quality-attribution item.
- `lessons/round-13.md:51-68` records the number-drift and reference-drift
  Mistakes, the primary-finding mapping, and marks `fidelity.py:55-56`'s
  "every exit-2 finding outranks source_mismatch" comment inaccurate because
  `PRIORITY` places `unpinned` below `source_mismatch`. KQ16 uses the actual
  order and does not repeat that comment's claim.
- `lessons/round-12.md:14-15` states capture uses `git show` while the same
  measurement independently reads the pinned blob with `git cat-file blob`.
- Round-12 code, read statically: `fidelity.py:44-49` code pins;
  `:64-72` `PRIORITY`; `:272` `git cat-file blob` comparison;
  `:319` exit selection (`1` only when the selected finding is
  `source_mismatch`, else `2`); `:323` counts a mismatch only when
  `source_matches is False and anchor_matches is True`. `reproduce.py:80`
  also uses `git cat-file blob` for its measurement; no committed command
  records the `git show` capture, so the capture remains author-recorded
  provenance.
- `SKILL.md:396` registry exit map agrees (0 clean; 1 `source_mismatch`;
  exit 2 for `snapshot_tampered`, `snapshot_unavailable`, `manifest_invalid`,
  `source_unavailable`, `unpinned`, `internal_error`). `SKILL.md:430`
  registers the round-13 textual gate and says none of its verdicts is
  semantic admission or endpoint readiness.
- `SOURCES.md` S032 (`git show`, docs/A) and S033 (`git cat-file`, docs/A,
  used-by `corpus/lessons/round-13.md`) were present at final read. KQ16
  cites them only as method sources, not as proof of independence or outcome.

## Probe compatibility — static inspection, not execution

I read `.ufo/waves/round-13/measure.py` without running it. Its current row
regex `^\|\s*KQ16(?![\w-])` selects the last KQ16 row; it splits 4 cells,
requires both literals in the admit cell, rejects whitespace-normalized
`distinct nonzero exits`, and requires the historical prefix. The written file
statically presents: one KQ16 row, 4 cells, both literals in the admit cell,
rejected wording absent, prefix preserved. The immutable before blob has no
KQ16 row, so the probe's before missing-assertion count is 2 by construction
and the after count is 0. I messaged `KamaR13.Measure` with the final row shape
and literals before freeze; its regex accepts the bare ID cell. `KamaR13.Measure`
subsequently confirmed the frozen copy `.ufo/waves/round-13/frozen/after/corpus/QUALITY.md`
is byte-identical to the delivered file (12469 bytes, same SHA-256), the before
copy is the 8619-byte `941bb32` blob, and `frozen/expected.json` pins both.
`SKILL.md:430` now registers the round-13 gate with the same limit: textual
conformance is not semantic admission or endpoint readiness.
**No probe, fidelity gate, reproduce script, build, test or linter was run by
this seat**, and no probe result is claimed.

## Quality attribution and claim limits

C1 denominator is the fixed two named wording propositions, not the whole
corpus. Score remains 7 -> 7, delta 0; no runtime, serving, freshness,
coverage, expansion, depth or capability claim is made. Criterion bookkeeping
is discernment, not new serving knowledge: round-12's quality credit belongs
to D4's stronger retained `served-identity-crosswalk` interpretation (source
wording versus locality inference; lane-registry versus upstream
supersession), not to gate machinery, and round 13 does not reclaim it.
Authors are not independent closure.

## Risks / blockers

- KQ16 is intentionally one long table row so the bounded probe can parse it;
  it repeats KQ15 boundaries rather than relying on a reader to join sections.
- KQ16 cites `lessons/round-13.md` Mistakes; that file was absent mid-flight
  and is present at final static read (`:49-68`), so the citation resolves.
- The probe's clean condition includes `worktree_matches_head`. This seat may
  not commit; `corpus/QUALITY.md` is left modified in the worktree, so L1 must
  commit it before the final measurement.
- No blocker. Sibling edits in the shared worktree (`LOG.md`, `SCORECARD.md`,
  `SKILL.md`, `SOURCES.md`, `README.md`, `round-13.md`, wave files) were not
  authored or modified by this seat.
