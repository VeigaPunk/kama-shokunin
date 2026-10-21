# CritNoTrade — attack on the round-24 "no trade" claim (closure rounds[428])

Seat: KamaR23-2.CritNoTrade-2 · base `0df800e896f6bce285a81e794ad4ae1d1e6c3a71` · git 2.56.0 · 2026-10-21
Scope: critic only. No production edits, no lane/fleet writes, no full-suite or grid runs. Only
offline local `file://` fixtures under `/fast/scratch/hyaku/kama-r24/CritNoTrade/`.

## Verdict

**The preregistration, as written, cannot support a no-trade claim.** All four defects below are
fixable before implementation, and two of them can let a candidate pass every preregistered row
while still harming operability.

1. **The baseline is already harmed.** The measurement says `frozen=r23 base`. The closure ruled
   H1 harm against the r22 auditor (`4fe9339f`), and r23 is exit 2 on every promisor row. Any
   r24 loss against r22 therefore shows up as "unchanged".
2. **"Complete local" under-samples the harm.** Both of the closure's witnesses are
   content-complete: T01 has no missing objects after checkout, and the real-lane control was a
   clone whose server ignored the filter. Ordinary honored `blob:none` clones really are missing
   objects, yet they hold every piece of required evidence. A candidate that restores verdicts
   only when there are "zero missing objects" passes expectation [0], T01, and the closure control,
   but still refuses 6 fixture rows and the real lane+fleet pair. The 6 rows are A1, A2, A3
   and B1 under `blobless-honored`, plus A1 and A2 under `tree0-honored`.
3. **Preregistration lines [3] and [5] contradict each other.** Line [3] keys "unknown" on the
   repository being promisor-backed, which is metadata. Line [5] says metadata does not establish
   incompleteness. On 4 fixture rows the two lines require different exits (2 versus 1). The r23
   grid already disagrees with itself on this shape: F06 expects exit 2, F27 expects exit 1.
4. **Two implementation traps can produce false verdicts.** First, enumerating missing objects
   only from refs (`rev-list --all`) misses promised objects, which yields a false exit 1.
   Second, `--missing=print-info` raises the Git floor to at least 2.49, which worsens the
   closure's other harm (H2).

## Independent comparison (proposed oracle)

Expectations are fixed when the fixture is built. They are never derived from an auditor arm.

- **Restore rows:** all required evidence is present locally, and every missing object is a
  blob that is not cited. The candidate MUST return the same exit 0 or 1 as the otherwise
  identical full clone (the "twin"). The JSON MUST also match after normalizing paths: the same
  finding IDs (`kind:token`, not just the set of kinds), `errata_unmatched`, and `errata_invalid`.
  Exit 2 fails these rows.
- **Unknown rows:** a required or cited object is promised-missing, or a missing tree, commit, or
  tag means absence cannot be enumerated. The candidate MUST return exit 2 and MUST NOT return
  0 or 1.
- **Arms:** r22 `4fe9339f`, r23 `0df800e8`, and the candidate. Each r22 row records a lazy-fetch
  witness (`remote.origin.uploadpack` touches a marker). Every row where r22 is correct and the
  candidate returns exit 2 must be a row where r22 fetched, and the round must declare it as
  the cost of `--no-lazy-fetch`. It must not be reported as "unchanged versus frozen".
- **Safety, every row:** the candidate's witness is absent, with no traceback and no timeout.

Inability to prove versus complete-local evidence, stated operationally (git ≥ 2.45, no
`print-info`):

- `P` = all present non-blob object IDs, from
  `cat-file --batch-all-objects --batch-check='%(objecttype) %(objectname)'`.
- `M` = `rev-list --objects --missing=print --stdin <P`, i.e. missing objects referenced by
  anything present, reachable or not.
- `N` = the same walk plus `--filter=blob:none`, i.e. missing trees, commits, and tags only.
- A token missing from every audited repository is **proven absent** (the twin's defect) iff
  `N` is empty and the token is in no repository's `M`; for an abbreviation, no `M` entry may
  start with it. Otherwise it is **unknown**, which is exit 2.
- Lookups that walk required evidence (lane `log`, fleet `log --diff-filter=A`, `show HEAD:rel`,
  `ls-tree`, blob reads) already fail closed with rc 128 on missing objects (rows C1–C5). The
  candidate MUST NOT add `--missing=allow-*` or `--exclude-promisor-objects` to them.

## Evidence

Probe: `.ufo/waves/round-24/build/out/CritNoTrade/probe.py` (sha256 `d943651a…`). Run:
`python3 probe.py /fast/scratch/hyaku/kama-r24/CritNoTrade OUT.json`, about 5 s, 40 rows. Each
arm runs on private copies of the fixture repositories. Result:
`out/CritNoTrade/probe-result.json` (sha256 `ad6da1e6…`); tally: `out/CritNoTrade/tally.txt`.

- r22 meets 32 of 40 expectations, r23 meets 24. Neither returns a wrong 0 or 1 on any row.
- The r23 arm never triggered the lazy-fetch witness; r22 triggered it on 19 rows.

**Restore rows (expect 0 or 1; r23 returns 2): 16.**

- A1, A2, and A3 under `promisor-complete`, `blobless-honored`, and `fleet-blobless`; A1 and A2
  under `tree0-honored`.
- A4 under `promisor-complete` and `fleet-blobless`.
- B1 under `blobless-honored` and `promisor-complete`.
- D1 under `promisor-complete` (errata correction lookup).

**Fetch-dependent rows (r22 correct only via lazy fetch; candidate must return 2): 8.**

- A1, A2, A3, and A4 under `fleet-tree0` (the fleet cutoff needs historic trees).
- A3 and A4 under `tree0-honored`.
- A4 under `blobless-honored` (the cited blob is promised-missing).
- E1 `part`.

**Real lane+fleet pair (honored `blob:none`, offline).** Fixture builds are in my scratch; JSON
is in `out/CritNoTrade/real-*`.

- The blobless lane clone is missing 388 objects and the blobless fleet clone 1008; all are
  blobs.
- r22 with `--rounds 10-22` gives byte-identical normalized JSON for full/full,
  blobless/blobless, full/blobless and blobless/full. Summary: 13 reports, 54 required commits,
  9 defects with 9 corrected, `clean`.
- After the run the lane still had 388 missing objects, so r22 needed no fetch. r23 returns
  rc 2 with `partial clone (promisor pack)` on all three partial combinations.
- This is the strongest restore row. Expectation [0] ("complete local") does not cover it.

**Contradiction between [3] and [5].** These rows expect `unresolved-full-hash:FAKE` exit 1 by
twin parity, but [3] read literally forces exit 2:

- `A3-bogus-full/promisor-complete`
- `A3-bogus-full/blobless-honored`
- `A3-bogus-full/fleet-blobless`
- `A3-bogus-full/filter-config-only`

In the last one, r23 currently returns 1, so [3] would regress even the frozen r23 arm. The
same content shape gets different expectations in the r23 grid:
`tests/report-audit/repo-state-grid.py:651` (F06, exit 2, reason `partial clone`) versus
`:674-675` (F27, exit 1). Whichever line r24 keeps, one row changes and must be declared.

**E1 enumeration trap.** The fixture is a blob `z` that is referenced only by an unreachable
promisor commit; the full twin finds it and exits 0.

- `rev-list --all --missing=print` reports `[]`, so a candidate using it would treat `z` as
  absent and emit a false `unresolved-full-hash` exit 1.
- The walk over all present objects reports `?827d9e6e…`, which gives exit 2.

**Git floor.** `--missing=print-info` is absent from the official
`v2.48.0/Documentation/rev-list-options.txt` and present in `v2.49.0/…/rev-list-options.adoc`.
On 7 repositories (t0, bh, pu, E1 part, ft, real lane-blobless, real fleet-blobless), the
`--filter=blob:none` split `N` matched print-info's types exactly. I did not run it on git 2.45.

**Cost.** The present-object walk takes 0.016 s on the real lane and 0.033 s on the real fleet,
far below `GIT_TIMEOUT = 20` (`tools/report-landing-audit.py:108`).

**Errata path.** `apply_errata` calls `lookup()` (`tools/report-landing-audit.py:404`). D1 is a
correction that is absent locally: twin exit 1 with `errata-invalid`, r22 exit 1, r23 exit 2.
Expectation [3] names only "citation". The unknown/absent rule must cover correction lookups
too, or D1 regresses.

**Cross-repo lookup.** For `A*/fleet-blobless`, r22 lazy-fetched in the fleet because it looked
up the lane commit there. A token found in one repository must not become "unknown" because it
is missing from a promisor sibling. Expectation [3] already says this; these rows pin it.

**Weak oracle at base.** `repo-state-grid.py:743-752` grades only the sorted set of finding
kinds, never tokens. A candidate could restore exit 0 or 1 with different tokens. Grade full
finding IDs and twin JSON parity, as the preregistered "finding IDs" requires.

**Inherited, out of scope.** At `tools/report-landing-audit.py:150` the bare `ambiguous` status
is overwritten by the peeled `found` at `:173`. The docstring at `:141-143` is false on git
2.56: `8be5513` gives a bare `ambiguous`, and `8be5513^{commit}` resolves to the commit
(row B1). Two consequences:

- Missing blobs cannot change landed-citation verdicts, so blob filters are safe for
  landed checks.
- Do not "fix" this in r24. It changes non-promisor rows, which would breach non-promisor
  no-harm, and it is listed under `not_claimed` inherited findings.

## Impacted axes

- **Operability:** H1 is restored only if rows 2 and 3 above are covered. H2 gets worse if
  `print-info` is used.
- **Calibration:** exit 2 must mean "cannot prove", not "promisor metadata".
- **Discernment:** declare the 8 fetch-dependent losses against r22 rather than hiding them
  behind `frozen=r23`.

## Smallest safe correction

- **Preregistration:** rewrite [3] as "a token missing from every audited repository is unknown
  (exit 2) unless absence is enumerable: no missing tree, commit, or tag, and the token is not a
  referenced missing object or its prefix". Extend it to errata correction lookups.
- **Expectation [0]:** extend it to content-incomplete clones whose required evidence is present.
- **Grid:** add an r22 arm with the lazy-fetch witness, and add the twin-parity rows here (A1–A4
  × 7 variants, B1, D1, E1) plus the real lane+fleet blobless pair.
- **Grid policy rows:** declare F06's flip to exit 1 (marker absent) and F23's reason re-pin.
- **Code:**
  - Delete the metadata refusal at `tools/report-landing-audit.py:450-465`.
  - Keep `GIT_ISOLATION` and `GIT_TIMEOUT` unchanged.
  - Compute `M` and `N` once per repository with the floor-neutral commands above, and gate only
    the "missing" outcome of `lookup()` on them.

## Not run (unverified)

- Any candidate implementation (none existed in `/fast/scratch/hyaku/kama-r24/AuditRepair` at
  review time).
- The `--filter=blob:none` split on git 2.45.
- `repo-state-grid.py`, `isolation-mutants.py`, `--selftest`, and the preregistered
  `promisor-grid.py`.

Tool installs/updates: none. (`bc` was absent; I used Python for timing instead.)
