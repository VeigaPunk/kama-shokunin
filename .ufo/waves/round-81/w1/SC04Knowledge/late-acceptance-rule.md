source: S559 — git-merge-base, `--is-ancestor` as a one-parameter exit-status ancestry test, the binding a late-acceptance row is graded with; S560 — git-diff-tree, the `-z` NUL-delimited record contract the append-only audit's deletion reading is built on (`git diff --numstat -z --no-renames` for counts, `-U0` hunk headers for the byte-exact lines); lane policy: `plans/round-81-claims.md` §C2 and `tools/round81-append-debt.py`.
verified-at: 2026-11-04 — read from `tools/append-only-audit.py` (definition v6, schema `append-only-audit/v3`), `tools/round75-append-accepted.py` (the frozen rule, verbatim), `registry/append-only-contract.tsv`, `registry/append-only-late.tsv` (88 rows over 10 events, introduced at `f6cb5303`), `corpus/lessons/round-81.md`, and the receipts `.ufo/waves/round-81/measured/{before/debt-base,after/debt-green}.out`. The counter was executed by this seat at lane `f6cb5303`: the worktree module printed the target line with `pending=0`, while the committed blob extracted from that revision printed `accepted=63` — the tally the after-receipt then carried; at the lane tip `88b35ea5` the `accepted` repair is committed, the same command prints `accepted=53 late=10 pending=0` and exits 0, and the regenerated `measured/after/debt-green.out` carries that line. No serving surface was sampled.
recheck: `python3 tools/round81-append-debt.py --repo . --round 81` must print `APPEND_DEBT round=81 base=e7d2fd729cf8 events=63 accepted=53 late=10 pending=<p> unaccepted=0 bad_rows=0 bad_declarations=0 out_of_population=0` and exit 0 — `accepted` counts frozen-register events only; the retained before-receipt `measured/before/debt-base.out` shows the empty-late-register run (`late=0 unaccepted=10`, exit 1), and `python3 tools/round81-late-rows.py --repo . --round 81 --check` re-derives every late cell (`LATE_ROWS check=ok rows=88` at `88b35ea5`).

# Acceptance may come from a later round, never from the same one

## The population the audit keys

`tools/append-only-audit.py` (v6) reports one **event** per `(commit, file)` whose first-parent diff deletes at least one line of a contract-declared file — `threshold 1` — over the eleven rows of `registry/append-only-contract.tsv`; the deleted lines are read out of the commit diff, never out of a worktree file (S560). Inside an event, the deleted lines not held at the audited revision are `undisclosed`: entries keyed by `line_sha256` (the line bytes minus one trailing carriage return), each carrying an exact `count` and a `classes` list drawn from `in-place-edit`, `removal` and `revert`. Three contract rows declare a narrower region than `*` (one `exempt=`, two `only=`), so an event can carry zero graded lines and still appear.

Two committed ledgers key that population with the same six columns `commit  file  line_sha256  count  class  note`:

| Ledger | Introduced | Rows at the base | What a row means |
|---|---|---|---|
| `registry/append-only-accepted.tsv` | `10f37171` (round 75) | 389 | the event's undeclared deletion is accepted history |
| `registry/append-only-disclosures.tsv` | `b6bed925` (round 51) | 10 | the deleted bytes are disclosed as lost, not accepted |

The population round 81 grades is the audit's pending set — events with `undisclosed` lines whose status is not `restored` — and at base `e7d2fd72` it is 63 events: 53 accepted by the frozen register, 10 that the frozen register cannot accept.

## Why the round-75 cutoff cannot be repaired by appending

`tools/round75-append-accepted.py` binds each row to the register's own introduction: its `precedes()` returns true only when the row's commit is a **strict ancestor of the commit that first added** `registry/append-only-accepted.tsv` (`commit != intro` and `merge-base --is-ancestor commit intro`, S559). A row appended for a later event commits after that introduction, so it is a descendant of it, never an ancestor: every event created once the register existed is permanently unacceptable under the frozen rule, however honest the row.

That is round 51's intent, not a defect to patch — the audit's disclosure rule says a ledger that accepts new rows would bless any later damage (round-51 seats K2Cheat, K2Design), and the disclosure ledger carries the same pre-introduction bound. The lane has paid for this once: the round-79 event at `5785cdff` deleted 38 rows from the accepted register, and the late register carries that event's subject — “restore the accepted-history register (the 38 post-introduction rows added by mistake are disclosed, not accepted)” — so the rows were removed, not made to bind.

## The late-acceptance rule

`registry/append-only-late.tsv` is a third register, same six columns, committed by the round that accepts and graded by `tools/round81-append-debt.py`. A row covers a line of an event only when all of the following hold:

- **Later round**: the note carries `round-<N> accepts round-<M>` with `N > M`; `M` is the deletion round parsed from the event commit's subject (`^round-<n>: …`); `N == M` is `same-round`, a `bad_rows` finding.
- **Strict descendant**: the register's own introducing commit must be a strict descendant of the event commit (`event != row_commit` and `merge-base --is-ancestor event row_commit`, S559).
- **Exact binding**: `line_sha256` equals the event's undisclosed digest, `count` its exact count (short or excess is `count-short`), `class` one of its computed classes, and the note keeps the frozen `; `-separated acceptance reason.
- **In population**: an event or row outside the base population lands on `out_of_population` and moves no bucket.

With those rows the round-81 run prints `events=63 accepted=53 late=10 pending=0 unaccepted=0`; at the base, with an empty late register, it prints `late=0 unaccepted=10`, exit 1.

## What `pending` is

`pending` counts population events whose commit is **not ancestral to the round's declared base** — the graded round's own record edits (in-place `SCORECARD.md` / `LOG.md` writes after the base). They are visible in the audit at the tip and the graded round cannot accept them: its late register is introduced by that same round, and rows introduced by the graded round accept only events ancestral to the base. The next round's late register repays them.

## The limit

A late row never restores bytes. `restored` is computed from held lines only, a `restored` event is rejected as a row, and no row moves the audit's `unrestored` count. Acceptance is the accounting of a loss the round admits, not repair of it — `late`, `pending` and `accepted` are the counter's buckets over the audit's population, never the audit's own summary. A green line says the losses are named and dated, not that the lane got its bytes back.
