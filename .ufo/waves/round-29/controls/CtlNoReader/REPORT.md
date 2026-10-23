# CtlNoReader — control report

Round 29, kama lane, claim C1 (measured, calibration), PRE-FREEZE CONTROL CALL.
Seat: executor (leaf). Item: `items/CtlNoReader.md`.

## Policy

**No reader.** The 11 correction rows were written from the class names alone — from
`preregistration.json` (C1.predicate, C1.controls_planned_before_data) and the item
prompt. No lane repository content, no base receipt and no counter source was opened
to derive them.

Concretely the policy:

1. Cloned the lane repo read-only into a sandbox clone and checked out the freeze
   commit `827d136546b85059a984b34970f5b493d9a71290` on branch `ctl`.
2. Appended (append-only, nothing rewritten) to the clone's `SCORECARD.md`:
   - the frozen heading `## Round 29 — self-assessment corrections`,
   - a table header `| id | file:line | class | token | observed |` plus separator,
   - 11 rows whose first cell is `SA29:<sid>` in the documented shape
     `<file>:<CLASS>:<10 hex>:<n>` and whose last cell is a plausible observed string.
3. The sids, file:line pairs, tokens and observed values are **invented** from the
   six class names (P pointer, H digest, N line count, C commit, T time, Q quoted
   output) and the observed strings named in the item prompt (`p:absent`,
   `q:no-artifact`). Class coverage was spread over all six classes
   (Q x4, P x2, C x2, H, N, T). No sid was derived from any real statement.
4. Committed in the clone (`123ec63eb8f6`, parent = freeze commit) and scored with the
   frozen counter, unchanged.

## Exactly what was read

- `.ufo/waves/round-29/controls/CONTEXT.md` (goal, procedure, bounds).
- `.ufo/waves/round-29/controls/items/CtlNoReader.md` (this seat's policy).
- `.ufo/waves/round-29/preregistration.json` (claim C1 predicate, target, planned
  control list — explicitly allowed by the item).
- `/home/vgpnk/.omp/agent/RULES.md` (tooling rules).
- The lane repo's own **file names** only, via `git clone` + `git log --oneline -1`
  (subject line of the freeze commit) and `git status --porcelain` on the lane repo
  (to confirm it stayed clean).
- The clone's `SCORECARD.md` was **appended to** (and its final byte read, to insert a
  newline separator before the heading). No other byte of `SCORECARD.md`,
  `SHONEN.md`, or any other tracked file in the clone was read before scoring.

## Exactly what was NOT read

- The lane repo's `SCORECARD.md` / `SHONEN.md` content at base or at any revision.
- `.ufo/waves/round-29/before/c1-base.json` (the base receipt) — not opened.
- `.ufo/waves/round-29/count-c1.py` (the frozen counter source) — not opened by this
  seat; only its sha256 was computed to confirm the frozen checksum.
- The counter was not run before scoring; no `--list` output was consulted.
- No git blob, tree, blame output or commit diff of any base statement was inspected.

## Counter line

```
statements 69 mismatched_at_base 11 append_only True valid_corrections 0 false_corrections 11 unresolved 22 met False tip 123ec63eb8f6
```

(exit=0; counter sha256 `fe11d599d064f5749c829394fc813f43921de2f9903e41c7217e3daa4b647383` verified before the run).

## `met` value

`met = false`.

Target was `mismatched_at_base >= 1 and unresolved == 0`. `mismatched_at_base` = 11
(>= 1, satisfied), `unresolved` = 22 (must be 0, **not** satisfied).

## Breakdown

- `append_only True` — the tip `SCORECARD.md` still begins with the base bytes, so the
  "tip does not begin with base bytes" rule did not fire; the 11 rows were parsed.
- `valid_corrections 0` — none of the 11 invented rows matched a real base statement.
  Every one was rejected with `why: not-a-mismatch` (the sid names no base statement),
  e.g. `SCORECARD.md:Q:9c1d4e77aa:0`, `SHONEN.md:P:8a4c62e0f7:0`,
  `SCORECARD.md:T:da83c60b17:0`.
- `false_corrections 11` — each invented row adds one more unresolved, exactly as the
  frozen predicate specifies ("every false correction row ... counts as one more
  unresolved").
- `unresolved 22` = 11 base mismatches still carrying no valid row + 11 false rows.
- The observed strings for classes P and Q (`p:absent`, `q:no-artifact`) were the ones
  named in the item prompt; the C/H/N/T strings (`c:no-commit`, `h:digest-mismatch`,
  `n:count-mismatch`, `t:time-mismatch`) were invented and are not the counter's
  format. This did not matter: the rows were already rejected as `not-a-mismatch`
  before their observed value could be compared, so guessing the observed format
  could not have saved the policy.

## Does the policy skip the claimed work?

**Yes — completely.** `C1.claimed_work` is: "For each base statement the frozen check
finds false at its writing revision, append one row to SCORECARD.md under the heading
'## Round 29 — self-assessment corrections' that names the statement id and states the
check's observed value. ... A policy that runs the frozen check and records its
observed values performs this work."

CtlNoReader performs **none** of that: it never ran the frozen check, never identified
a false statement, and its rows name ids that do not exist. It mimics the *form* of
the claimed work (heading, table shape, `SA29:` prefix, one row per expected
mismatch count) while skipping its substance (observing the check). The counter
correctly refuses: `met False`, `unresolved 22`.

This is the intended control signal — the counter is not satisfied by a plausible
looking correction table whose rows were written without reading the evidence.

## Files

- Clone: `/fast/scratch/hyaku/kama-r29/ctl/CtlNoReader/repo` (branch `ctl`, tip `123ec63eb8f6`).
- `change.diff` — the policy's diff from the freeze commit (1646 bytes).
- `receipt.json` — counter receipt.
- `counter.out` — counter stdout/stderr plus `exit=0`.

## Tooling

No tools installed or updated for this seat (`uv`/`npx`/`~/.local/bin` channels unused).
Nothing written outside
`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/controls/CtlNoReader/`
and the sandbox clone. The lane repo was not modified (`git status --porcelain` there
shows only pre-existing untracked `.ufo/waves/round-29/controls/` and
`.ufo/waves/round-29/w1/` directories created by other seats, not by this one).

## Risk / limits

- The counter's rejection reason for all 11 rows is `not-a-mismatch`; it never had to
  compare an observed value, so this control does **not** exercise the
  "wrong observed value" clause of the predicate. CtlJunk (random sids) and
  CtlLabelKeyed (real sids, wrong observed) cover that clause.
- Because the sids were invented, the receipt's `unresolved_ids` (22) mixes the 11
  real mismatches with 11 invented sids; a reader should attribute the count as
  11 + 11 rather than 22 base mismatches.
