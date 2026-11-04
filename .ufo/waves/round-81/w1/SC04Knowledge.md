# SC04Knowledge — round-81 w1 scribe report (knowledge entry, coverage row, KQ criterion)

Seat: SC04Knowledge (scribe, leaf — no dispatch). Milestone `kama r81 w1`. Axis worked: coverage.
Lane read at `git -C /home/vgpnk/Projects/shokunin/kama-shokunin rev-parse master`:
`f6cb5303171cc73dc570ace06f99125266e5b956` when the drafts were written, `88b35ea5adf59f908dd25d1a0a1f50209dbc02eb`
after the L1's receipt commit (`88b35ea5 round-81: re-point gate arm 8 at the late-acceptance counter,
add arm 11, land the measured receipts`). No production file was edited, no commit made, no gate run.
No tool install or upgrade was needed (or performed), so there is no tool/version/channel row.

## Artifacts (absolute paths)

| Path | What it is | Lines |
|---|---|---|
| `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-81/w1/SC04Knowledge/late-acceptance-rule.md` | the `corpus/knowledge/` entry (draft; `source: S559`, cites S560 in the body, `verified-at: 2026-11-04`, `recheck:` command) | 43 (≤70) |
| `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-81/w1/SC04Knowledge/readme-row.md` | one `corpus/README.md` coverage-map table row (appended-round style) | 5 |
| `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-81/w1/SC04Knowledge/quality-criterion.md` | one `KQ134` row for `corpus/QUALITY.md` + placement note | 20 |
| `…/SC04Knowledge/receipts/append-debt-worktree.out` | worktree counter at `f6cb5303` (repair uncommitted) — target tally | — |
| `…/SC04Knowledge/receipts/append-debt-committed-f6cb5303.out` | committed blob extracted from `f6cb5303` — `accepted=63` | — |
| `…/SC04Knowledge/receipts/append-debt-tip-88b35ea5.out` | committed module at `88b35ea5` — target tally | — |
| `…/SC04Knowledge/receipts/append-debt-selftest.out` | `--selftest` → `APPEND_DEBT_SELFTEST pass=16 fail=0` | — |
| `…/SC04Knowledge/receipts/late-rows-check.out` | `round81-late-rows.py --check` → `LATE_ROWS check=ok rows=88` | — |

## Commands, outcomes, exit codes

All run with `TMPDIR=/fast/scratch/hyaku/kama-r81/SC04Knowledge`, cwd
`/home/vgpnk/Projects/shokunin/kama-shokunin`.

1. `git rev-parse master` → `f6cb5303…` (later `88b35ea5…`), exit 0.
2. `python3 tools/round81-append-debt.py --repo . --round 81` at `f6cb5303` with the worktree module →
   `APPEND_DEBT round=81 base=e7d2fd729cf8 events=63 accepted=53 late=10 pending=0 unaccepted=0
   bad_rows=0 bad_declarations=0 out_of_population=0`, **exit 0** (`receipts/append-debt-worktree.out`).
3. `git show f6cb5303:tools/round81-append-debt.py > $S/committed-append-debt.py` then
   `python3 $S/committed-append-debt.py --repo . --round 81` → same line except `accepted=63`,
   **exit 0** (`receipts/append-debt-committed-f6cb5303.out`).
4. At `88b35ea5`: `python3 tools/round81-append-debt.py --repo . --round 81` → target line
   `accepted=53 late=10 pending=0 …`, **exit 0** (`receipts/append-debt-tip-88b35ea5.out`).
5. `python3 tools/round81-append-debt.py --selftest` → `APPEND_DEBT_SELFTEST pass=16 fail=0`,
   **exit 0** (`receipts/append-debt-selftest.out`).
6. `python3 tools/round81-late-rows.py --repo . --round 81 --check` → `LATE_ROWS check=ok rows=88`,
   **exit 0** (`receipts/late-rows-check.out`).
7. Read-only ledger counts at the base `e7d2fd72`: `git show <base>:registry/append-only-accepted.tsv`
   → 390 lines / 389 rows; `…append-only-disclosures.tsv` → 11 lines / 10 rows.
8. Introduction commits (`git log --diff-filter=A --format=%H`): accepted `10f37171fb696c542586cbee96ea4a509ab74afc`
   (round-75 commit, 2026-11-04 02:25:29 -0300); disclosures `b6bed925b032ac2c19b63ef4af358ebdd5922c26`
   (round-51); late register `f6cb5303…` (round-81, 08:45:44 -0300).

## Provenance opened for the entry (no claim beyond these)

- `tools/append-only-audit.py` — definition v6 / schema `append-only-audit/v3`; event shape,
  `threshold 1`, `undisclosed` entries, disclosure pre-introduction bound; `git diff -U0 --text
  --no-renames` at `:401`, `git diff --numstat -z --no-renames` at `:468`, `git ls-tree -r -z
  --name-only` at `:369`.
- `tools/round75-append-accepted.py` — `precedes()` (`commit != intro` and `merge-base --is-ancestor
  commit intro`), six-column header, `post-introduction` class.
- `tools/round81-append-debt.py` (committed at `f6cb5303` and `88b35ea5`, and worktree) — population
  split by base ancestry, `NOTE_RE`, `strict_descendant`, `out_of_population`, `pending`.
- `tools/round81-late-rows.py` — row generator docstring; `--check` path is read-only (`--write` is
  the only writer).
- `registry/append-only-contract.tsv` (11 rows; one `exempt=`, two `only=`),
  `registry/append-only-declarations.md`, `registry/append-only-late.tsv` (88 data rows over 10
  distinct `(commit,file)` events; 50 `in-place-edit` + 38 `removal`; the 38 removals are the
  round-79 `5785cdff` edit of `registry/append-only-accepted.tsv`),
  `registry/append-only-disclosures.tsv`, `corpus/QUALITY.md` tail, `corpus/README.md` tail.
- `corpus/lessons/round-81.md` (§Corrections F1-F6, §Mistakes `number-drift`, §Freeze divergences).
- `corpus/SOURCES.md:661-662` (S559, S560 — both name `corpus/knowledge/late-acceptance-rule.md` as
  used-by). I did not open the two git URLs; the entry cites the rows without quoting the pages.

## Findings and conflicts (verbatim where they conflict)

1. **The `accepted` tally was committed wrong, then repaired — timeline matters for any citation.**
   At `f6cb5303` the committed `tools/round81-append-debt.py` printed `accepted=63` (observed by
   extracting the blob and running it), and `.ufo/waves/round-81/measured/after/debt-green.out`
   carried the same `accepted=63`, against the frozen target `accepted=53`. At `88b35ea5` the repair
   (`frozen_keys`; `accepted = len(frozen_keys & graded_keys)`) is committed, the module prints
   `accepted=53 late=10 pending=0` exit 0, and the after-receipt was regenerated to that line. C2's
   predicate is met by committed bytes at `88b35ea5` only, not at `f6cb5303`.
2. **`corpus/lessons/round-81.md` §Freeze divergences 3 contradicted the receipt at `f6cb5303`.**
   The lesson says "the first implementation counted all accepted events in `accepted` and was
   corrected before any receipt was taken", while the then-retained `debt-green.out` printed
   `accepted=63`. After `88b35ea5` the sentence is true of the retained receipt again; the record of
   the earlier state is only in the git history and in this seat's receipts.
3. **S560's stated record shape does not match the audit's git calls (live).**
   `corpus/SOURCES.md:662` says "the audit's event population is `--name-status -z --no-renames`
   records", repeated in `corpus/lessons/round-81.md` Gate row 3 and in the `source:` line of the
   filed `corpus/knowledge/late-acceptance-rule.md` ("S560 (git-diff-tree `-z --name-status`)"). The
   audit never calls `--name-status`: deleted lines come from `git diff -U0 --text --no-renames`
   (`tools/append-only-audit.py:401`) and counts from `git diff --numstat -z --no-renames` (`:468`);
   `--name-status` appears nowhere in the file. S560's quoted `-z` sentence does cover `--numstat`,
   so the page grounds the `-z` contract. My draft's `source:` line says `--numstat` and does not
   repeat the shape claim.
4. **A filed entry exists at `corpus/knowledge/late-acceptance-rule.md`, written before this draft.**
   It is 67 lines (≤70) and covers the five required points; my seat artifact is the independent
   draft. Deltas the L1 should reconcile (I did not edit the filed file):
   - `source:` names "S560 (git-diff-tree `-z --name-status`)" (see finding 3); S560 is cited only in
     the `source:` line, never in the body, while the item asks for a body citation.
   - It gives neither the ledgers' row counts nor their introduction commits (389 rows / `10f37171`;
     10 rows / `b6bed925`); my draft does.
   - It asserts `accepted + late + unaccepted == events` as a rule; the counter does not enforce that
     identity — an event with one late-bound line and one unbound line lands in both `late` and
     `unaccepted`, so the sum would exceed `events`. It holds for this run (53 + 10 + 0 = 63).
   - It attributes the "a ledger that accepts new rows would bless any later damage" sentinel to the
     round-75 accepted register; the sentence's source is the audit's round-51 disclosure rule
     (`tools/append-only-audit.py`, disclosure paragraph; seats K2Cheat, K2Design). The accepted
     register adopted the same cutoff in round 75.
   - `recheck:` cites `--selftest` `pass=16 fail=0`, which I re-ran and confirmed at `88b35ea5`.
5. **The coverage row already landed.** `corpus/README.md:1768` carries `## Coverage map — round 81
   addition` with a row for `corpus/knowledge/late-acceptance-rule.md` and a frontier paragraph. It
   indexes the filed entry (finding 4). My `readme-row.md` is the item's artifact; filing it as-is
   would duplicate the section — the L1 should either replace the landed Covers cell (mine states the
   two ledgers, the pre-introduction cutoff, `N > M`, `pending` and the no-restore limit) or keep the
   landed one and drop mine.
6. **KQ numbering collision.** The item froze "next free number after KQ132", but `KQ133` had landed
   at `corpus/QUALITY.md:639` before this draft (it binds the self-record tally with
   `tools/round81-selfrecord-round80.py`, citing `corpus/lessons/round-81.md` §Mistakes `number-drift`
   and R80V1). I drafted `KQ134` as the continuation — same mined class, broadened from the
   self-record to any cited receipt, with this round's own instance (`accepted=63` receipt vs
   `accepted=53` target) and the `LATE_ROWS check=ok rows=88` leg. `quality-criterion.md` carries a
   placement note and a merge option.
7. **`pending=0` is the observed value.** Round-81's own record edits (`SCORECARD.md`/`LOG.md`
   in-place writes) were uncommitted at both tips I read, so no base-descendant event existed and the
   run printed `pending=0`; the entry states `pending=<p>` in its recheck line and reports the
   observed run honestly.
8. **First-person execution limit.** I executed the counter four times (worktree at `f6cb5303`,
   extracted committed blob at `f6cb5303`, committed module at `88b35ea5`, `--selftest`) and
   `round81-late-rows.py --check` once. I did not run the pre-report gate, did not audit the full
   event list independently, and did not open the S559/S560 URLs.

## Coverage the entry carries

Frozen audit population and the two keyed ledgers (six-column `commit file line_sha256 count class
note`; accepted 389 rows introduced `10f37171`, disclosures 10 rows introduced `b6bed925`); why the
round-75 pre-introduction cutoff makes every post-introduction event permanently unacceptable
(strict-ancestor requirement; round-51 intent; the 38 removed rows at `5785cdff`); the late-acceptance
rule (later round `N > M`, strict-descendant register introduction, exact hash/count/class,
`out_of_population` moves no bucket); what `pending` means; and the limit that a late row never
restores bytes and never changes the audit's `unrestored` count.

## Out of scope / not done

- C1 (calibration, `tools/round81-selfrecord-round80.py`) — not my seat; not run, not graded.
- Pre-report gate in scored mode, commits, production files, sibling repos, fleet root — untouched.
- No clone or fixture repo was created; no git write ran anywhere.

## Scratch

`$S = /fast/scratch/hyaku/kama-r81/SC04Knowledge/` was created, used for the extracted committed
module and as `TMPDIR`, and removed after the receipts were copied into the seat directory. Nothing of
mine remains outside the seat directory.
