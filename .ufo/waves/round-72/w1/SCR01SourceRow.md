# SCR01SourceRow — round 72, wave 1 (frontier: open `git-check-ignore`, register the row, extend S175/S542)

Seat axes: **freshness**. Lane: `/home/vgpnk/Projects/shokunin/kama-shokunin` (master `a3cc39f0` at
seat start; freeze base `d30a8696`). Scratch: `/fast/scratch/hyaku/kama-r72/SCR01SourceRow` (deleted
before yield). Report written from observed command output only; no check is reported unrun.

## Behaviour delivered

1. **Opened `git-check-ignore` live** and retained the bytes at `w1/SCR01SourceRow/source/git-check-ignore.html`
   (38402 bytes, sha256 `bdee84a9b7207a7c5920d3e0967c36bb07c941efa5ce56abe8f3a9b15c373927`).
   Page revision line: `git-check-ignore last updated in 2.52.0`.
2. **Located quote (18 words, ≤25) grounding the ignored-path verdict**, anchor `§EXIT STATUS`
   (page section id `#_exit_status`):
   > `0 One or more of the provided paths is ignored. 1 None of the provided paths are ignored.`
   Third status on the same section: `128 A fatal error was encountered.`
3. **Registered S543** as the next unused id (registry max was S542; campaign staged set is
   S330–S471 — no overlap on S543). Status `mined` with `used-by corpus/knowledge/receipt-tip-binding.md`:
   that entry exists on disk and its `source:` line cites S543 with this quote and sha256, so the
   `mined` condition is satisfied at write time (not a planned-only citation).
4. **Extended two used-by cells in place** (rule 2: only `used-by` changed, logged here old→new).
5. **Gated a scratch mirror before the lane write**, then wrote the lane file and proved byte identity.

## Gates (commands and observed output)

| # | command | observed |
|---|---|---|
| 1 | `curl -sSL --fail -o source/git-check-ignore.html https://git-scm.com/docs/git-check-ignore` | exit 0; 38402 bytes; sha256 `bdee84a9…c373927` |
| 2 | `curl -sSL --fail -o source/git-status.html https://git-scm.com/docs/git-status` | exit 0; sha256 `22ff28ff73f83696c4a503e9c92e7a15f4ded2f91d96cc5668ee79db0a1b0180` |
| 3 | `curl -sSL --fail -o source/git-merge-base.html https://git-scm.com/docs/git-merge-base` | exit 0; sha256 `46d106b777754f7ec3072813ace57d2c5385d110181b8db1c56b7136cfb49644` |
| 4 | `git archive HEAD \| tar -x -C $S/validate` then `cp corpus/SOURCES.md $S/validate/corpus/SOURCES.md` | mirror built at HEAD `a3cc39f0` |
| 5 | `python3 apply_append.py $S/validate/corpus/SOURCES.md mined` (first pass, before peer files existed) | `OK … status=mined row_after_line=295`; **gate exit 1 with 4×E11** (see Finding 1) |
| 6 | `cp` peer files `corpus/knowledge/receipt-tip-binding.md` (sha256 `89e05e29…0c8a4cb`) and `corpus/lessons/round-72.md` (sha256 `88f7c750…6cb24`) into the mirror | mirror now resolves every used-by path |
| 7 | `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --file $S/validate/corpus/SOURCES.md` | **exit 0**, E-code count 0, W-codes only (W01, W04), final line `file\tok\t…/SOURCES.md` |
| 8 | `python3 apply_append.py /home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md mined` | exit 0; `row_after_line=295` |
| 9 | `cmp $S/validate/corpus/SOURCES.md corpus/SOURCES.md` | no output → `IDENTICAL` |
| 10 | `sources-census.sh validate --file corpus/SOURCES.md` (lane bytes) | exit 0, 0 E-codes, `file\tok` |
| 11 | frozen manual census: rows / malformed / dup ids / tier histogram | `rows=283`, `malformed=0`, `dups=` (empty), `A=269 B=10 C=4` |
| 12 | `grep -oE '^ {0,3}\|[[:space:]]*S[0-9]{3,}' corpus/SOURCES.md \| grep -oE 'S[0-9]+' \| sort -V \| tail -1` before the write | `S542` |
| 13 | id collision: registry ids vs `shoukuknow/merge/kama/SOURCES.append.md` ids (`comm -12`) | `reg=282 staged=142 collisions=9` |

Mirror census exit code: **0**. Lane census exit code: **0**.

## The new row (verbatim)

```
| S543 | Git git-check-ignore manual — https://git-scm.com/docs/git-check-ignore | docs | A | `git check-ignore` exit status as the ignored-path verdict C1's round-scope arm case C reads: 0 when at least one provided path is ignored, 1 when none is, 128 on a fatal error; git's own contract, not the arm's finding format | §EXIT STATUS (`#_exit_status`), sentences "0 One or more of the provided paths is ignored." and "1 None of the provided paths are ignored."; page is the Latest-version build, "git-check-ignore last updated in 2.52.0"; fetched bytes sha256 bdee84a9b7207a7c5920d3e0967c36bb07c941efa5ce56abe8f3a9b15c373927 retained at `.ufo/waves/round-72/w1/SCR01SourceRow/source/git-check-ignore.html` (accessed 2026-11-03) | status 0 is a positive ignored verdict and 1 a negative one, so a caller branches on the exit code instead of parsing output, and 128 is a fatal error rather than a verdict | mined | 2026-11-03 | on-release | corpus/knowledge/receipt-tip-binding.md |
```

NF=13 (11 cells); no `|` inside any cell (asserted by the applier before writing); inserted directly
after the S542 row, inside `## Registry`, before `## Paths`.

## used-by changes, old → new (rule 2 log)

| id | old cell | new cell |
|---|---|---|
| S175 | `corpus/knowledge/self-assessment-at-writing.md, .ufo/waves/round-29/count-c1.py` | `corpus/knowledge/self-assessment-at-writing.md, .ufo/waves/round-29/count-c1.py, corpus/lessons/round-72.md, corpus/knowledge/receipt-tip-binding.md` |
| S542 | `corpus/knowledge/pre-report-gate.md, corpus/lessons/round-71.md` | `corpus/knowledge/pre-report-gate.md, corpus/lessons/round-71.md, corpus/lessons/round-72.md` |

No other cell of any row changed; `status`, `recheck`, `opened`, `anchor`, `teaches` untouched.

## Re-open evidence (S175, S542 — freshness axis)

- **S175** `git-merge-base`, footer still `git-merge-base last updated in 2.43.0`; §OPTIONS `--is-ancestor`
  still reads: "Check if the first `<commit>` is an ancestor of the second `<commit>`, and exit with
  status 0 if true, or with status 1 if not. Errors are signaled by a non-zero status that is not 1."
  Row's teaches still grounded; row records no sha256, so no byte-drift comparison is possible.
- **S542** `git-status`, footer still `git-status last updated in 2.53.0`, changes list
  `2.54.0 → 2.56.0 no changes`; fetched sha256 is **byte-identical** to the sha256 recorded in the
  S542 anchor cell from round 71 (`22ff28ff…b0180`) — zero drift across rounds. §OUTPUT "Porcelain
  Format Version 1" sentence re-read verbatim.

## Findings

1. **E11 vs. same-round citations (ordering hazard, resolved by sequencing, not by editing rules).**
   The maintained census fails a `mined` row (and any row) whose `used-by` path is absent from the
   working tree (`[ -e "$dir/$path" ]` in `scripts/sources-census.sh:565`). Read literally, the
   round-72 frontier step requires used-by cells naming `corpus/lessons/round-72.md` and
   `corpus/knowledge/receipt-tip-binding.md` *before* those files exist, which is red by construction:
   first mirror pass printed exactly
   `E11 S175 missing used-by corpus/lessons/round-72.md`,
   `E11 S175 missing used-by corpus/knowledge/receipt-tip-binding.md`,
   `E11 S542 missing used-by corpus/lessons/round-72.md`,
   `E11 S543 missing used-by corpus/knowledge/receipt-tip-binding.md`, exit 1.
   I did not weaken the gate or pre-create placeholders. I sequenced the lane write after the two
   peer-owned files landed (SCR02 wrote the knowledge entry, SCR03 the lesson skeleton), copied the
   real bytes into the mirror, and the gate then exited 0. The lane's own practice matches: S542 and
   `corpus/lessons/round-71.md` were added in the same commit `e2b860c8`. **No rule was edited; the
   frozen plan was not touched.** Consequence for future rounds: a registry row can only cite an
   entry that already exists on disk, so the lesson/knowledge seats must land before the SOURCES seat.
2. **Collision check is clean for this round's row, dirty for the package.** Registry (282 ids) ∩
   `shoukuknow/merge/kama/SOURCES.append.md` (142 ids) = 9 ids: **S330, S333, S334, S335, S346,
   S347, S352, S353, S363**. Each collides on an *identical source title and URL* already adopted in
   the lane — the staged package re-stages rows the lane already holds, so the package is stale, not
   conflicting. No staged row covers `git-check-ignore`. Consistent with the plan's decision (no
   assimilation this round).
3. **Read-only observation, not this seat's file:** `plans/round-72-claims.md` is modified in the
   working tree by another seat — a `Freeze amendment 2, 2026-11-03T22:50 -03, before any seat
   returned a score` making `cited=0` exit 2 for C2. I did not touch it and take no position on it;
   reporting it so the canonical judge sees the freeze bytes changed after the round opened.
4. **S543's `opened` date** is 2026-11-03 (local -03); the fetch itself was `2026-11-04T01:42Z` UTC.
   The row uses the seat's local access date, matching the lane's convention for every other row.
5. `recheck: on-release` for S543 follows the other git-docs rows (S175, S542); no cadence was
   invented for a docs page whose revision line is `2.52.0`.

## Touched surfaces (exact)

Written by this seat:

- `corpus/SOURCES.md` — one row appended (S543), two `used-by` cells extended, nothing else.
- `.ufo/waves/round-72/w1/SCR01SourceRow.md` (this report).
- `.ufo/waves/round-72/w1/SCR01SourceRow/` — `fetch.out`, `quote.txt`, `reopen.out`,
  `validate-mirror.out`, `validate-mirror-preE11.out`, `validate-lane.out`, `reg-ids`, `staged-ids`,
  `collisions`, `source/git-check-ignore.html`, `source/git-status.html`, `source/git-merge-base.html`.

Not touched: `corpus/knowledge/**`, `corpus/lessons/**`, `SCORECARD.md`, `LOG.md`, `SKILL.md`,
`MANIFEST.json`, `tools/**`, `plans/**`, `.ufo/state/`, any sibling lane, the fleet repo. No git or jj
mutation was run anywhere; the only git calls were `rev-parse`, `log`, `status`, `diff`, `archive`,
`ls-files`.

## Out of scope

- No product/serving claim; the row grades a tool contract, not any instrument's behaviour.
- No search-log or Paths entry (the seat text asks for exactly one registry row; rule 4 — expansion is
  knowledge, not rows).
- No `corpus/QUALITY.md`, `corpus/README.md`, lesson or SKILL.md edit — peer-owned this wave.
- Scratch `/fast/scratch/hyaku/kama-r72/SCR01SourceRow` deleted after receipts were copied.
