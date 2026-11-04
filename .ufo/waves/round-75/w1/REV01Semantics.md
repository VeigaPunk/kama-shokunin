# REV01Semantics

Scoped findings report: [REV01Semantics/report.md](REV01Semantics/report.md)
(sha256 `fe2b3aa32d3e61dff18b20f6d998edf80751952e6bd7e7547241ecdf05cef5e5`).

Raw run receipts: [REV01Semantics/receipts/](REV01Semantics/receipts/).

No production file was edited. Derivation read the freeze-commit bytes
(`0908bab5`) because the lane worktree copy of
`tools/round74-receipt-claim-binding.py` is being modified concurrently by the
C2 seat. Headline results:

- P1 (older-demonstrated): declared `total=3`, older-union mutant `total=5`
  reproduced on the plan's fixture; both older-table kinds give the same
  answer. Names in a table at the canonical round, or only in older tables,
  vanish from every printed counter.
- P2 (revision context): the `nc2_recorded_at_hex` shape exits 0 at freeze; the
  literal-hex mutant exits 1 with `stale-revision`. The code's rule is
  adjacency (`rev`/`revision` + whitespace + 40 hex), narrower than the plan's
  "introduced by" wording (`revision: <hex>` is not a mention).
- C2: the five frozen mutants reproduce `killed=3 escaped=2`; the failing arm
  per mutant is named (`blob-reader-seam`, `same-line-stale-claim`,
  `committed-fixtures`); the two escapes are only observable via
  `bound_revisions`/finding kind, not the exit code.
