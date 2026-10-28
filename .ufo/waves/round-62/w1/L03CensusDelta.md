# L03CensusDelta — SOURCES census delta inputs (round 62, kama)

Scope: compute the `corpus/SOURCES.md` row-count delta inputs for the round-62 report —
count at the frozen base `a959fd90` vs at `master`, with the command, plus the supporting
CORPUS.md §Census outputs. Read-only git (`show`/`rev-parse`/`log`/`diff`/`status`) and
grep/awk only. No file outside this report and `.ufo/waves/round-62/w1/out/L03CensusDelta/`
was written; no commit, push, or mutating git/jj command anywhere; no lane source edited
(the in-flight `corpus/SOURCES.md` memoisation below is a sibling's edit, observed only).

- measured: 2026-10-28T12:31:03Z (`date -u`), host Linux 7.2.11-arch1-1 x86_64
- lane root: `/home/vgpnk/Projects/shokunin/kama-shokunin`
- base: `a959fd9022b1ac1f3cb4dc2475d9cded8b2b01c3` (round-61 closure, do-nothing tip)
- master at measurement: `65d7cad0fce90e34de37527cde22e97b63b118bf` (`git rev-parse master`;
  `HEAD` is detached at the same oid)
- tools: none installed or upgraded (nothing needed — no pacman transaction was attempted,
  which also satisfies the host-wide pause)

## Answer — the two counts and the command

Pattern, copied from the fleet-root `CORPUS.md` §Census (line 135), pinned by file hash
`88556402940e7a0f1dbbed3abef9e00c87a90db6f80eaed03269e371f50050b8`
(`sha256sum /home/vgpnk/Projects/shokunin/CORPUS.md`); its line text hashes to
`7d08d3c54878da5dbe250717458ef10f402e1b0021ca9817cf9e101dcb504b30`:

```sh
grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md
```

Run from the lane root, once per revision (the file is piped, so the pattern is unchanged
and only the input source differs):

```sh
git show a959fd90:corpus/SOURCES.md | grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|'
# 265
git show 65d7cad0:corpus/SOURCES.md | grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|'
# 265
```

- **base `a959fd90`: 265 rows**
- **master `65d7cad0`: 265 rows**
- **delta base → master: 0 rows**

Both numbers are single-run at 2026-10-28T12:31Z; re-running the two commands reproduces
them (receipt `out/L03CensusDelta/census-delta.out`, driver `receipt.sh`, exit 0).

## Why the delta is 0 — the file did not move between base and master

| check | command | result |
|---|---|---|
| blob id identical | `git rev-parse a959fd90:corpus/SOURCES.md` / `git rev-parse 65d7cad0:corpus/SOURCES.md` | `811232efec582c1cacfdb9a4553fb8fffb21b708` both |
| bytes identical | `git show <rev>:corpus/SOURCES.md \| sha256sum` | `ace517940bfdd0cb30dec99289695664724a62ba0dc03d4d80d7b09646fce0dd` both |
| no diff | `git diff --stat a959fd90..master -- corpus/SOURCES.md` | empty (exit 0) |
| no touching commit | `git log --oneline a959fd90..master -- corpus/SOURCES.md` | empty (the range holds 2 commits, neither touches SOURCES.md) |
| row-id set | id extract + `diff` per revision (`out/L03CensusDelta/{base,master}.ids`) | 265 = 265, diff empty |
| last commit touching the file | `git log -1 --format='%h %ci %s' master -- corpus/SOURCES.md` | `9df34a78 2026-10-28 03:22:24 -0300 round-61: SOURCES S525 Ollama OpenAPI row`, 265 rows there too |

So the registry has been at 265 rows since round-61's S525 commit, and round 62's two
commits (`round-61 verifier spot-check`, `round-62: live request-plane tool, …`) added no
source row. **A round-62 report that states a per-round SOURCES row growth must state 0 for
the committed tip** (0 at base, 0 at master; "265 → 265").

## Supporting CORPUS.md §Census outputs (base / master worktree-free comparison)

Every other command of the same frozen §Census block, evaluated against the two committed
blobs (exact commands in `receipt.sh`; output in `census-delta.out`):

| metric | base `a959fd90` | master `65d7cad0` | worktree (in flight) |
|---|---|---|---|
| rows (frozen pattern) | 265 | 265 | 266 |
| rows (maintained 0–3-space variant `^ {0,3}\|…`) | 265 | 265 | 266 |
| malformed rows (NF≠13) | 0 | 0 | 0 |
| duplicate ids | none | none | none |
| tier histogram | A=251 B=10 C=4 | A=251 B=10 C=4 | A=252 B=10 C=4 |
| status histogram | mined=239 queued=8 rejected=18 | mined=239 queued=8 rejected=18 | mined=240 queued=8 rejected=18 |
| enum violations + tier inflation | 0 | 0 | 0 |
| mined rows with a dead `used-by` path | 0 | 0 | 0 |

The frozen (`^\|`) and maintained (`^ {0,3}\|`) row patterns agree at all three states, so no
S-row in this file is indented and the choice of pattern does not move the count.

## Working-tree caveat — the only place a "+1" exists, and it is uncommitted

The lane working tree is not clean for this file: `M corpus/SOURCES.md`
(`git status --porcelain -- corpus/SOURCES.md`), `1 0 corpus/SOURCES.md`
(`git diff --numstat`), worktree sha256 `f9ff8176e4d45ab8cab3026209fbacac21bd79a1cc5f86efc7d3a34798382e27`.
The in-flight change is the single row **S526** (llama.cpp server README @ 704366d76 /
b11755, `/v1/completions` request surface), inserted at line 278, well formed (NF=13),
`status=mined`, `opened=2026-10-28`, and its `used-by` cells point at
`corpus/knowledge/completion-request-plane.md, corpus/lessons/round-62.md` — both of which
are themselves untracked in the lane (`git status --porcelain`). It is the doc row backing
C1's request plane, not a calibration row: `S526` appears nowhere in
`registry/capability-claims-r62.tsv`, `tools/round62-c1-counter.py` or
`tools/kama-completion-live.py`.

Consequences for the report, stated so the number is not misattributed:

1. The tip's row count is **265**. A census run from the working tree during this wave reads
   266, which is the wave's uncommitted S526 cluster, not the base→master delta.
2. If the L1 lands the S526 / `completion-request-plane.md` / `round-62.md` cluster in the
   round commit, the *committed* delta becomes base 265 → round-62 tip 266 (+1, S526 only),
   with tier A 252, mined 240, everything else unchanged. Whether it lands is the L1's
   decision; both endpoints are measured here.
3. The do-nothing base cannot be distinguished from master by this file at all — byte
   identical — so the C1/C2 claims cannot lean on any SOURCES movement as evidence of work.

## Cross-checks and limits

- The wave's own census artifact `.ufo/waves/round-62/census/start.out` (08:01, exit=0,
  `kama ok …/corpus/SOURCES.md`) is a `validate` run, not a row count: it prints duplicate-URL
  and tier-C warnings plus `ok`, and records no total. It is consistent with a clean registry
  but does not independently state 265; it also predates the S526 insertion, since it does not
  list S526.
- The maintained `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh` was **not run** by
  this seat: the lane carries no `scripts/` directory, and the round-end rerun of that fleet
  script plus the full manual census is sibling seat S01CensusRerun's item. Nothing here
  contradicts its output; the only overlap is the row count.
- `LOG.md:2481` records "`SOURCES.md` remains 259 rows" at that earlier round; the 265 here is
  the current committed state and is not a restatement of that line (six rows S520–S525 landed
  after it, per `git log -1 master -- corpus/SOURCES.md` = 9df34a78).
- An empty untracked nested directory `kama-shokunin/.ufo/` exists in the lane
  (`?? kama-shokunin/`); it holds no `SOURCES.md` (checked with `find kama-shokunin -maxdepth 3
  -name 'SOURCES.md'` → nothing) and does not affect any census count run from the lane root.
  Left untouched — not this seat's file.
- One failed read was corrected during work, not hidden: an early id-extraction pipeline
  concatenated the trailing `\|` of the pattern with a second `S…` matcher and returned 0 ids;
  the corrected extraction (`grep -oE '^\|[[:space:]]*S[0-9]{3,}' | grep -oE 'S[0-9]{3,}'`)
  is what the receipts use.

## Tally

```
SOURCES rows: base=265 master=265 delta=0; worktree=266 (+S526 uncommitted); malformed=0 dups=0 enum=0 missing-usedby=0 at all three states
```
