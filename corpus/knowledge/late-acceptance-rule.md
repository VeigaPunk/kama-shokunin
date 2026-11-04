source: S559 (git-merge-base `--is-ancestor`) and S560 (git-diff-tree `-z --name-status`); the rule itself is the lane's own re-runnable instrument `tools/round81-append-debt.py`
verified-at: 2026-11-04 (lane base `e7d2fd729cf8204c89c32534303bc9f2a97fcee4`, sealed record `a2af1af59faf6cf66fe854559293c4e4b441aff3`)
recheck: `python3 tools/round81-append-debt.py --repo . --round 81` prints `APPEND_DEBT … unaccepted=0 bad_rows=0` and `python3 tools/round81-append-debt.py --selftest` prints `APPEND_DEBT_SELFTEST pass=16 fail=0`

# Late acceptance: a register row may be introduced by a later round, never by the same one

The lane's append-only audit grades a deletion event per (commit, path) pair and lists the deleted
lines no restoration or disclosure accounts for. Two ledgers can answer an event:

- `registry/append-only-accepted.tsv` — the frozen acceptance register (round 75). A row is
  `commit, file, line_sha256, count, class, note`, and its commit must be an ancestor of the
  register's **own introduction commit** (the round-51 sentinel: a ledger that accepts new rows would
  bless any later damage).
- `registry/append-only-disclosures.tsv` — the disclosure ledger, which declares lines *lost*, not
  accepted, and has the same pre-introduction cutoff.

## Why the frozen rule is unsatisfiable after its introduction

The cutoff is by construction: `precedes(commit)` requires the deletion commit to precede the commit
that first added the register, so every event created *after* that commit — which is every record edit
of every later round, because the SCORECARD contract re-anchors head rows in place — can never carry an
accepted row. The frozen counter's own `post-introduction` finding is the proof: a perfect row appended
today for a round-79 deletion still reads `APPEND_ACCEPTED_FINDING post-introduction`.

That is the state round 81 inherited: `APPEND_ACCEPTED events=63 accepted=53 unaccepted=10` and a
pre-report gate whose acceptance arm could never be green again.

## The late-acceptance rule

A row in `registry/append-only-late.tsv` (same six columns) accepts an event only when all of these
hold, which is what `tools/round81-append-debt.py` grades:

1. the row's `commit`, `file` and `line_sha256` name an event the audit reports, and its `count` and
   `class` equal that event's own undisclosed `count` and mechanical class (exact, never a prefix);
2. the register's **own introducing commit** is a strict descendant of the event commit — checked with
   `git merge-base --is-ancestor <event> <row-intro>` and `event != row-intro` (S559), so a row can
   never be co-resident with the damage it accepts;
3. the row's note names `round-<N> accepts round-<M>` with `N > M`, `N` being the round that files the
   row and `M` the round parsed from the event commit's subject — a round cannot accept its own edits;
4. the event is at or before the graded round's **declared base**. A row naming a later event is
   `out_of_population` and changes no bucket.

`pending=<p>` reports the graded round's own undeclared events — visible, never accepted: the next
round must repay them with its own late rows. `accepted` counts frozen-register acceptances, `late`
counts the additional events only a late row accepts, and `accepted + late + unaccepted == events` over
the base population.

## What the rule does not do

- It does not restore a byte. The audit's `unrestored` count and every deleted line stay as the audit
  computed them; acceptance is a dated statement that the deletion was a record edit whose round is
  superseded, not a rewrite of history.
- It puts no cap on how much a later round may accept. The bound is procedural (a later round must
  declare it) and visible (the arm line prints `late` and `pending` every round); a round that accepts
  hundreds of lines is declaring hundreds of in-place edits, which the SCORECARD contract already makes
  auditable. Round 81's own acceptance is 88 lines over ten events (rounds 79–80).
- `pending` is not a free pass: it is the debt line the next round's base makes graded.

## Round-81 evidence

- base, red: `APPEND_DEBT round=81 base=e7d2fd729cf8 events=63 accepted=53 late=0 pending=0
  unaccepted=10 bad_rows=0 bad_declarations=0 out_of_population=0`, exit 1
  (`.ufo/waves/round-81/measured/before/debt-base.out`).
- tip, green: `APPEND_DEBT round=81 base=e7d2fd729cf8 events=63 accepted=53 late=10 pending=1
  unaccepted=0 bad_rows=0 bad_declarations=0 out_of_population=0`, exit 0 at `1b96317f`
  (`.ufo/waves/round-81/measured/after/debt-green.out`); `pending=1` is the round's own first
  post-base record edit, which round 82 must accept. 88 rows re-derived by
  `tools/round81-late-rows.py --check` → `LATE_ROWS check=ok rows=88`.
