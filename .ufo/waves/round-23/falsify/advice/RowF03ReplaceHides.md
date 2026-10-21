# F03-replace-hides-omission — falsify review (RowF03ReplaceHides)

**Verdict: HOLDS.** The fault premise is real and observed in the frozen arm,
the expected outcome is the correct verdict (not merely current's behavior),
and every near variant of the `refs/replace` channel I could construct is still
handled correctly by the committed auditor. One sibling channel
(`info/grafts`) is *not* neutralized by `--no-replace-objects` but is covered
by a separate preflight refusal — consistent with its own grid row (F11).

## Row definition (245a37f6)

- `tests/report-audit/repo-state-grid.py:541` — `("F03-replace-hides-omission", "fault", f_replace_omission, 1, ["landed-omitted"])`
- Builder `f_replace_omission` (`:233-241`): lane gets `lc` "round-1: work" (@1000) then `x` "round-1: more" (@1200), both by `kama-shokunin`; fleet report cites only `lc` @2000. A raw commit `y` (same tree, parent `lc`, subject "unrelated", author `fixture`) is hashed and `git replace x y` is installed. Premise check: `git log -1 --format=%s` == "unrelated".

## Hand-built fixture (no grid import)

Built `/tmp/kama-r23w2/fix-f03` with `GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1` and explicit env identity:

- `LC=db796f8b820bf3825c58832419138cdba23206a7` "round-1: work" @1000
- `X=4312b0a582382d7dc45cae7c3ed22ab1a934add1` "round-1: more" @1200
- `Y=51b41482c707ea876aad9bcb1b76c4469f607e0a` "unrelated", `git replace X Y`
- Premise verified: `git log -1 --format='%H %s'` → `4312b0a5… unrelated`;
  `git --no-replace-objects log -1` → `round-1: more`; `for-each-ref refs/replace`
  shows the ref.

## (1) Frozen arm — premise real, omission hidden

`python3 frozen-audit.py` (blob `4fe9339f8fc3a4a4a479d9c938a850da12f1124d`,
sha256 `09ecd63b…`, contains no `no-replace-objects` — only `source_fixture.replace` in selftest):
exit **0**, `round_commits: 1`, `required: 1`, `status: "clean"`, zero defects.
The replace-honoring `git log` prints `X`'s OID with `y`'s subject, so the
subject matcher in `round_commits` never counts `X` and the omitted commit
disappears. Cross-check: `repo-state-grid.py --arm both --case F03…` →
`frozen … exit=0 NOT-MET`.

## (2) Expected outcome is correct

Ground truth: `X` is authored by `kama-shokunin`, subject `round-1: more`,
`atime` 1200 ≤ cutoff 2000, and its sha is uncited. `landed-omitted` is the
verbatim correct verdict, not merely current's convention. Current
(`tools/report-landing-audit.py`, sha256 `f228f174…`) exits **1** with
`landed-omitted` token=`X`, `round_commits: 2` — because `GIT_ISOLATION`
(`:93-96`) prepends `--no-replace-objects` to every `git` call via `git()`
(`:114`), the only subprocess path in the file.

## (3) Near variants — all still correct under current

| Variant | Frozen | Current |
|---|---|---|
| **V1** replace swaps *author* (`someone`), subject still `round-1: more` | exit 0, hides `x` (author filter drops it) | exit 1 `landed-omitted` |
| **V3** replace swaps *atime* → 5000 (> cutoff) | exit 0, `x` moved to `post_report` | exit 1 `landed-omitted` |
| **V5** replace *fleet* report commit, `atime`→1150 (cutoff shift; `report_cutoff` reads fleet `%at`) | exit 0, cutoff=1150, `x`→post | exit 1 `landed-omitted`, cutoff=2000 |
| **V2** `git replace --graft x` (drops parent; subject unchanged) | exit 1 `landed-omitted` (accidentally right — `x` still walked) | exit 1 `landed-omitted` |
| packed `refs/replace` (pack-refs) | replace still effective | flag still neutralizes |
| `GIT_REPLACE_REF_BASE=refs/notdefault/` | exit 1 (env stripped by `git_env`) | exit 1 |
| **V6** `.git/info/grafts` | exit 0 clean, `round_commits: 0` | **exit 2**: `could-not-evaluate: … .git/info/grafts rewrites history` |

Key proofs:

- `git -C lane --no-replace-objects log --format='%P'` with an `info/grafts`
  file present still shows the graft applied (empty parent list) — the flag
  does **not** cover grafts; the `check_history_repo` refusal
  (`tools/report-landing-audit.py:441-444`, `os.path.lexists` on
  `rev-parse --git-path info/grafts`) is a separate, load-bearing control.
  Frozen has no `check_history_repo` at all.
- `cat-file --batch-check` reports the *requested* OID under replacement
  (size is the replacement's, but the token still resolves to `found`), so
  the citation-lookup channel was never vulnerable even in frozen.
- `git_env` (`:99-105`, frozen `:79-84`) strips all `GIT_*`, so
  `GIT_REPLACE_REF_BASE` cannot smuggle a replacement through a nonstandard
  ref base in either arm.
- Replace targets not reachable from HEAD (e.g. `git replace HEAD` to a
  parentless foreign commit) are the same refs/replace channel — flag covers.

## Not verified / out of scope

- Full 26-row grid run (other rows belong to sibling reviewers).
- Replace refs on objects used only via `ls-tree`/`show` for
  `corpus/SOURCES.md` or errata: same flag, not separately exercised.
- `git cat-file --batch-check` *size/type* of a replaced commit differ from
  the original — the auditor never reads object bodies, so this cannot
  alter the verdict; noted, not weaponized.
- `git replace -d` mid-run races (auditor is a single short-lived process;
  `rev-parse`/`log` see a consistent-enough view).

## Artifacts

- Clone: `/tmp/kama-r23w2/RowF03ReplaceHides` (HEAD `245a37f6…` verified)
- Frozen blob: `/tmp/kama-r23w2/frozen-audit.py`
- Fixtures: `/tmp/kama-r23w2/{fix-f03,envfix,v1,v2,v3,v5}` + `*.json` outputs
- This report: `.ufo/waves/round-23/falsify/advice/RowF03ReplaceHides.md`

No installs were needed (git/python3 already present).
