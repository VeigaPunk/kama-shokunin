# Candidate cross-lane-scope rows — kama round 90 (CN01SiblingOverlap)

For `corpus/knowledge/cross-lane-scope.md`. Two rows, in the file's
`## Contested scope and arbitration` table shape (`| Contested claim | Recommended owner / boundary |`);
the L1 may instead land them as round-90 bullet rules (the rounds 71/72 convention) — the bold lead
sentence at the head of each cell is written to survive that conversion.

Provenance: read-only reads of the sibling files cited; **no sibling gate was executed**, so these
rows record adjacency and attribution, not sibling green/red state. kama side at
`2ee0b55f4d3fd0cb3157d26b03280c1d21e27b2d`, probe sha256 `c197912f8b3b5567e3ffd38178cb3a6e87187d7fb13136308c9a461ba8d2ef97`.

| Contested claim | Recommended owner / boundary |
|---|---|
| **A probe's answer bound is one number, so kama's 4 MiB cap can be compared with a sibling's 8 MiB cap.** | **Split three ways and owned per fetcher: wire bytes, decoded bytes, wall clock — and the receipt must name which bound fired.** chousa holds 8 MiB on *both* the wire and the inflated bytes (`tools/quote-reopen.py:28,54,313-336`) and returns `body over 8 MiB` with nothing parsed (`:420-424`); kotodama holds a 4 MiB wire cap read with `read1` under a monotonic deadline (`tools/reopen-row.py:541-567` — a buffered `read` would let a drip outlive the budget), a separate 64 MiB `GZIP_LIMIT` (`:142,400-410`) and a first-class `TRUNCATED` verdict (`:18-19,713-714`); kagi holds 8 MiB and proves the over-cap branch by shrinking the cap to 8 bytes in its self-test (`corpus/release-clock.py:32,768-775,810,1583-1596`); mori holds 8 MiB but folds an over-cap answer into `unavailable`, the same outcome as a transport failure (`tools/mori-ua-variance.py:97,143`); kumitate's route-health probe caps child output at 1 MiB, flags overflow separately and names it `output_overflow` (`corpus/knowledge/route-probe-cluster.md:225,522,563`). kama holds a 4 MiB **wire** cap with no decode path and `body-too-large` as its own reason (`tools/kama-probe.sh:103,340-346,846`). Rule: cap values are not comparable across lanes; what transfers is the pairing — a cap with a clock, a second cap if the fetcher ever decodes, and an over-cap outcome distinguishable from a transport failure. kama's cap stays a true wire cap only while the probe does not request `--compressed`; adding it would make `--max-filesize` bound received bytes, not the decoded body. |
| **Control characters in listener text are one sanitizer's job, and kama's C0/DEL/C1 set is the fleet's set.** | **Escape what is shown, refuse what is parsed as a key, and treat the codepoint set as the owning lane's own claim.** kama escapes C0/DEL/C1 as `\uXXXX` inside ids and drops them from `Server:`/`Content-Type`/status values, keeping identity (`corpus/knowledge/probe-answer-bounds.md` decision rows; `jstr` escapes U+0001–U+001F and DEL per RFC 8259 §7). souji **refuses** C0/C1/DEL in a path or receipt field before parsing because a TAB shifts every following TSV column, then space-replaces on emit (`tools/cand-b1-quarantine.sh:157-162,196-204`); tameshi refuses C0/DEL in a verdict-bearing receipt path because an embedded newline forges a verdict line (`tools/design-blob-audit.py:179-184`); kotodama refuses inside a verdict token by name — NBSP, VT, FF, LS/PS/FS, NEL, ANSI, any `Cc`, combining marks, any `Zs` (`tools/check-advance-evidence.py:295-325`); the fleet display sanitizer strips C0/C1, ANSI/OSC, **bidi controls and tmux format tokens** (`scripts/ufo-mission-activity.mjs:57`, as annotated in `kumitate-shokunin/corpus/knowledge/remaining-scripts-census.md:660`). Rule: a cell that is displayed is escaped (identity preserved — kama cells P3/P4), a field that is a key is refused; kama's frozen class is C0+DEL+C1, so bidi U+202A–U+202E, OSC and U+2028/U+2029 sit outside it and a held-out cell in that class is a scope finding, not a C1 falsification. The fleet display surface itself is fleet-repo ground, not kama's. |

## Notes for the L1 (not part of the rows)

- Both rows are **corroboration plus a rule**, not contested scope: no sibling claims kama's probe
  or its reason table, and kama claims none of theirs.
- Row 1's only live constraint on C1 is negative: `--compressed` must stay absent from
  `fetch()`, `probe_short()` and the `/props` fetch (`tools/kama-probe.sh:340,375,761`). If a future
  round adds it, the cap needs a decode-side re-check (chousa's `_inflate_stream` shape) before the
  C1 predicate is re-frozen.
- Row 2's `\uXXXX` choice is the identity-preserving direction and is what makes cells P3 (non-ASCII
  kept verbatim) and P4 (`"` and `\` round-tripped) separable from an over-sanitizer (forgery F2).
  souji's space-replacement would fail P3's intent; that is a surface difference, not a defect.
- A third adjacency was found and deliberately **not** drafted as a row: kama's C2 population is
  print-site-derived (23 `C_REASON=`/`RT_REASON=` assignments at `99cdb4d6`, plus the post-C1
  `body-too-large` row), while kumitate's route-health vocabulary is declared and names one
  unreachable member (`route-probe-cluster.md:231`) and kake's registry names 12 codes no fixture
  covers (`SKILL.md:777-816`). C2 already handles the seam with its `additional` row and its
  exclusion note for `dns-failure`, so a cross-lane row would restate C2 rather than place it.
