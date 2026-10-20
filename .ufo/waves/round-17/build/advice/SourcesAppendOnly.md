VERDICT: confirm — tools/sources-append-only.py built; flags the round-16 S041 in-place anchor/teaches edit (exit 1) and passes ccc4bb3→master (exit 0).

## Files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/sources-append-only.py`
  sha256 `c477a172cd5ae1512a9f75456da216a7df8cfde1df7c28fd09e60b76054b1e05` (mode 755)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/build/advice/SourcesAppendOnly.md` (this report)

## What it does

`--from REV --to REV [--repo …] [--path corpus/SOURCES.md] [--json]` reads both
blobs via `git -C REPO show REV:PATH` (read-only; never touches worktree or
index), parses the `## Registry` table by `id`, and reports:

- **removed rows** → violation (exit 1)
- **cell changes outside {status, recheck, used-by}** → violation, printed per
  cell as old→new
- **added rows** → allowed, listed as `added S### (allowed)`
- **row re-ordering** → ignored (comparison is by id, not position)

Exit 0 = clean, 1 = violations, 2 = unreadable blob or unparseable registry
(missing `## Registry`, missing header/separator, row width ≠ header width,
duplicate id, missing required column). The guard refuses to grade a table it
cannot fully parse rather than silently skipping mangled rows.

## Verification performed (sanctioned runs only)

```
$ python3 tools/sources-append-only.py --from b8e485c --to ccc4bb3
VIOLATION S041: cell `anchor` changed in place
  old: receipt `kama-llamacpp-live/v1` 2026-10-20T13:49:38.040Z–13:49:38.170Z, port 32845, 10 checks
  new: receipt `kama-llamacpp-live/v1` 2026-10-20T14:06:27.859Z–14:06:27.974Z, port 37527, tool sha256 b8c5e8d4…, 10 checks
VIOLATION S041: cell `teaches` changed in place
  old: A real llama-server on the pinned build answers `/health` 200, ...
  new: A real llama-server on the pinned build answers `/v1/models` 503 with the exact loading envelope while loading, ...
1 append-only violation(s)          EXIT=1

$ python3 tools/sources-append-only.py --from ccc4bb3 --to master
no append-only violations           EXIT=0
```

`--json` emits `{from, to, path, violations, added, ok}`; `--selftest` runs
14 in-memory cases (identical, status-only ok, teaches violation, removed row,
added row, reordering ignored, pipe-inside-backticks literal, escaped `\|`
literal, recheck+used-by ok, anchor violation, malformed width → exit 2,
duplicate id → exit 2, missing registry → exit 2, source-cell violation) —
14/14 pass. `python3 -m py_compile` clean. `git diff b8e485c ccc4bb3 --
corpus/SOURCES.md` confirms the flagged cells are exactly the S041 `anchor`
and `teaches` edits ScribeQualityKQ22 independently located.

## Design choices

- **Pure detector, no exception mechanism.** Contract rule 2 (CORPUS.md:116:
  "Only `status`, `recheck` and `used-by` change in place") is enforced
  literally. A named/dated amendment exception (ScribeQualityKQ22's
  quality-kq22 draft) is caller/L1 policy applied after the checker reports;
  baking a whitelist into the guard would make it grade itself.
- **Column-driven comparison.** Immutable columns = header minus `id` minus
  the mutable three, so a contract-v2 column would automatically be graded as
  immutable unless added to `MUTABLE_CELLS`.
- **Forgiving cell splitter.** `|` inside a backtick code span and `\|`
  escapes are treated as literal content (GFM formally requires `\|` inside
  code spans; being more permissive avoids false positives on prose cells
  like S001's `§GET \`/health\`` anchors). Cells compare verbatim after
  leading/trailing strip, so re-escaping a cell registers as a change.
- **Parse failures exit 2, not 1.** A mangled table is a tooling/hygiene
  defect distinct from a rule-2 violation; callers can distinguish "violation
  found" from "couldn't grade".

- **Rev selectors validated before subprocess.** `git_show` rejects any rev
  starting with `-` or containing `:` (option-injection e.g.
  `--from=--output=/x`, or a corrupted `rev:path` spec); verified:
  `--from=--output=/tmp/x` exits 2 with `invalid revision selector` and no
  file is written.

## Known limitations

- Row content is compared verbatim per cell; whitespace-only rewrites inside a
  cell (e.g. double space) flag as violations. Deliberately strict — [INFERENCE]
  a rule-2 violation is the likelier cause of any non-mutable-cell byte change.
- Non-`S###` pipe lines inside the Registry section are tolerated unless they
  look like mangled data rows (id cell starting with `S` but not matching
  `S[0-9]{3,}`); a truly malformed non-S line with correct width is skipped
  rather than erroring.
- Compares exactly two revisions; multi-commit ranges need a caller loop
  (`git rev-list` + consecutive pairs) to attribute a violation to one commit.
- No `--fix`, no working-tree mode, no network access — all out of scope.

## Coordination

- ScribeQualityKQ22 confirmed checker-as-detector + caller-side named S041
  exception in `.ufo/waves/round-17/build/drafts/quality-kq22.md`; the two
  sanctioned ranges fit that framing.
- RevengerS041Edit-2 reported the pre-fix crash at line 156; fixed before the
  flag run above (tuple→set union, two `r"""` docstrings for `\|`).
- SentinelSeatWrites-2 flagged (a) a `tools/__pycache__/*.pyc` side effect of
  `py_compile` — removed; syntax now validated via `ast.parse` — and (b) the
  unguarded argv rev reaching `git show` — fixed with the selector validation
  above. Both re-verified after the fix.

## Installs

None. Python 3 stdlib only (`argparse`, `json`, `re`, `subprocess`, `sys`).
No pacman transactions (host pause respected).
