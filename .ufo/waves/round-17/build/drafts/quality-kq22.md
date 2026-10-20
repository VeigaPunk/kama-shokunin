## Criteria added — round 17 (2026-10-20, author-appended; no outside review yet)

No earlier criterion is superseded. KQ7's append-only correction rule, KQ14's
preserved append-only clause and KQ16 remain in force. KQ22 governs the
`corpus/SOURCES.md` registry's immutable cells, which the round-16 verifier
spot-check routed as defect 3 (`lessons/round-16-verifier-spotcheck.md:184`).
If KQ20 or KQ21 open this same round-17 section, drop this heading and append
the row after theirs.

| ID | Admit only when | Reject or limit when | Motivating lesson |
|---|---|---|---|
| KQ22 | A `corpus/SOURCES.md` registry row keeps its immutable cells (`id`, `source`, `kind`, `tier`, `scope`, `anchor`, `teaches`, `opened`) byte-identical from its first commit onward. Only `status`, `recheck` and `used-by` change in place, and each such change is logged old→new in the round lesson (`SOURCES-CONTRACT-v1` rule 2). A regenerated artefact, a re-measured receipt or a corrected anchor is recorded by a new row whose `teaches` opens `supersedes S0NN —`, and the superseded row keeps its bytes. The round-end check is `python3 tools/sources-append-only.py --from 1e41928 --to <tip>`. Its base is the registry's first commit, not the round start, because a round-start base cannot see an amendment already committed before it. The checker is a pure detector: it flags every immutable-cell change and every removed row, and it exits nonzero on any flag. Each flag that cannot be undone without rewriting history (currently S041 `anchor` and `teaches`, changed at `ccc4bb3`) is named in the round lesson's exception list with its commit, row and cell, and the round records the checker's result after that named list is applied. A round with an unnamed flag is not admitted. | A registry cell is edited in place to match a regenerated file; a `supersedes` row edits, deletes or renumbers its target; a row is removed or reused under a new meaning; or a flagged change is excluded from the range or from the round-end record without a named exception. A round-end check run from the round start (for round 17, `--from cff9e62`) is not evidence that the registry is append-only, because the S041 amendment is already inside that commit. A clean result that depends on an unnamed or undated exception is rejected. | `lessons/round-16-verifier-spotcheck.md:184` (routed defect 3); `lessons/round-16.md:147-149` (S041 anchor and teaches amended, no old→new logged); `corpus/SOURCES.md:53` (S041 row); `corpus/QUALITY.md:29` (KQ7 append-only); `.ufo/waves/kaika/SOURCES-CONTRACT-v1.md:49-51` (rule 2). |

Scope note: KQ22 admits no registry content. It constrains how existing and
future rows change. Corrections to S041 are a new superseding row; they do not
repair the historical `ccc4bb3` change.
