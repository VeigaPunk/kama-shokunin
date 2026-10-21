# SOURCES row candidate — Git git-rev-list manual (NOT applied)

Provisional ID `S103` (S101 is the highest row at base `0df800e8`; `S102` is already drafted by
peer `SrcPromisorCode`). L1 allocates the final ID at admission. No edit was made to
`corpus/SOURCES.md` (sha256 `274d50916eb04b158f4f2b2fbc0ffdfaec56270aeb54282d4f2d95d193744993`,
identical to base `0df800e8:corpus/SOURCES.md`).

```markdown
| S103 | Git git-rev-list manual — https://git-scm.com/docs/git-rev-list | docs | A | `--objects`, `--no-object-names` and `--missing=<action>` reporting at Git 2.56.0; not object-closure completeness, numeric exit status, or promisor fetch policy | §Object Traversal `--objects` (`#Documentation/git-rev-list.txt---objects`), `--no-object-names` (`#Documentation/git-rev-list.txt---no-object-names`), `--missing=<missing-action>` (`#Documentation/git-rev-list.txt---missingmissing-action`); page "git-rev-list last updated in 2.56.0", pinned `/2.56.0` text identical, opened 2026-10-21 | `--missing=print` keeps traversing and prints encountered missing objects prefixed `?`; `allow-any` omits them silently; default `error` stops; `--objects` adds objects referenced by the listed commits; `--no-object-names` suppresses names only. | queued | 2026-10-21 | on-release | — |
```

## Why this is a new row, not a reopened one

- Base `0df800e8:corpus/SOURCES.md` has zero occurrences of `rev-list` (`grep -c` → 0).
- The host `git-scm.com/docs` is already used by S032, S033, S070/S082, S071/S083, S073/S085,
  S089, S090, S093, S099, S100; this page is a **new scope inside an already-used official
  documentation family**, not a reopening of a row.
- Adjacent but not superseding: S089 `--no-lazy-fetch` (git(1)), S099 promisor missing-object fetch
  (partial-clone), S090 replacement-ref exception for "reachability traversal". This row owns only
  rev-list's option-level reporting semantics.

## Scope warning for the Gate

Tier A covers the manual page as a statement of option semantics at 2.56.0. The page itself calls
`--missing` "A debug option to help with future \"partial clone\" development", so the row must not
be cited as a stability or completeness contract. Exit-code mapping and required-object closure are
lane policy, not this page's claims.
