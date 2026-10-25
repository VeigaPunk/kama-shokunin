# RevReadmeBytes — round 36 wave 3, README block byte audit

Scope: last heading block of `corpus/README.md`, i.e. the block starting at
`## Coverage map — round 36 addition` and ending at the next `## ` heading.
Measured result; README.md not modified.

## Block boundaries (measured)

- Block start: line 546, heading `## Coverage map — round 36 addition`.
- End of block: end of file at line 560. The grep of all `^## ` headings shows
  no later heading after line 546, so the block is lines 546–560 (15 lines).

## Count (measured)

Occurrences of the string `knowledge/sglang-native-route-deprecation.md`
inside lines 546–560: **1**.

Measured two ways, both agree:
- `grep -c` on the extracted block: 1 (lines containing it).
- `grep -o | sort | uniq -c`: one single occurrence, no repeats.

## Does the table row name the entry exactly once?

Yes. The single occurrence is in the table row on line 550, in the `Entry`
column, backticked: `` `knowledge/sglang-native-route-deprecation.md` ``. The
Covers and Round columns and the surrounding prose (lines 552–560, which name
S328/S329 and `corpus/lessons/round-36.md`) contain no further occurrence of
the entry path string.

## Findings by severity

- None. The block's byte-level contract holds: exactly one reference to the
  draft entry, in the table's Entry column; no duplicate naming, no dangling
  or misspelled path in the block.

## Residual risk / verification gaps

- Only the literal string was counted; a semantically equivalent reference
  under a different spelling (e.g. missing `knowledge/` prefix) was not part
  of the requested count and was not separately audited.
- The prose tail (lines 552–560) makes factual claims about S325–S458 staged
  ids, S327 collision, and 2026-10-24 dates; those belong to other seats'
  scopes (registry/lesson) and were not verified here.
