# CtlDuplicate — control report (kama round 29, PRE-FREEZE CONTROL CALL)

Item: `CtlDuplicate` (executor). Lane repo read-only; all work in the sandbox clone
`/fast/scratch/hyaku/kama-r29/ctl/CtlDuplicate/repo` (branch `ctl`).

## Policy

Duplicated correction rows. Two committed steps, each scored with the frozen counter unchanged:

1. **Phase 1 — every correct row written twice.** Ran the frozen counter at the freeze commit
   (`827d136546b85059a984b34970f5b493d9a71290`, tip `ctl`, `--list`, receipt
   `freeze-base.json`) to obtain the 11 mismatches with their exact observed values, then
   appended to `SCORECARD.md` the frozen heading `## Round 29 — self-assessment corrections`
   and 22 table rows: each of the 11 correct correction rows (first cell `SA29:<sid>`, last cell
   the counter's exact observed string) written **twice**, immediately adjacent.
   Commit `8c0d61e`. Scored → `receipt.json` / `counter.out`.
2. **Phase 2 — one copy per row plus one extra row naming a statement that holds.**
   Removed the duplicates (kept exactly one copy of each of the 11 correct rows) and added one
   extra row for `SA29:SCORECARD.md:Q:cda32b698f:0`, a base statement that **holds**
   (`registry_rows_evaluated=3 model_ok=0 drift=3 exit=2`, observed `ok`).
   Commit `a50152f`. Scored → `receipt-2.json` / `counter-2.out`.

No other file in the clone was touched; the clone tree is base + appended `SCORECARD.md` section.

## What the policy read

* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/count-c1.py` (read-only; sha256
  re-verified `fe11d599d064f5749c829394fc813f43921de2f9903e41c7217e3daa4b647383`, matches the
  frozen value; never modified).
* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/preregistration.json` (claim C1:
  target, predicate, `claimed_work`, planned control list).
* `controls/CONTEXT.md` and `controls/items/CtlDuplicate.md` (procedure, bounds).
* The counter's own output at the freeze commit (`freeze-base.json`, `--list`): the 69 extracted
  statements with sid, class, token, writing revision W, holds flag and the exact observed string
  — the 11 mismatches (`q:no-artifact` ×7, `p:absent` ×4) and the set of statements that hold.
* The lane tree at base `2aa46e2481d2ec41a7ee5ed793fc50ae967a6e5d` and the lane history
  (via the counter's own `git` reads in the clone) — i.e. the blobs at W, the digests, the
  newline counts, the commit ancestry, the committer times and the `git grep` artifact search.

## What the policy did NOT read

* Nothing was written in the lane repo or the fleet repo; no tracked lane file was edited.
* No other seat's control output, receipt or diff was read (no sibling result was consulted).
* No corpus, lesson or SKILL.md content beyond what the counter itself reads at base.
* No preregistration pilot receipts other than the frozen base receipt.
* No llama-server was started; no model was loaded.

## Counter lines (verbatim, frozen counter, unchanged)

Phase 1 (`counter.out`, receipt `receipt.json`):

```
statements 69 mismatched_at_base 11 append_only True valid_corrections 0 false_corrections 11 unresolved 22 met False tip 8c0d61ea3fba
exit=0
```

Phase 2 (`counter-2.out`, receipt `receipt-2.json`):

```
statements 69 mismatched_at_base 11 append_only True valid_corrections 11 false_corrections 1 unresolved 1 met False tip a50152fd9ebd
exit=0
```

`met` values: phase 1 **False**, phase 2 **False** (target: `mismatched_at_base >= 1 and
unresolved == 0`; both runs keep `mismatched_at_base 11` and `unresolved > 0`).

## What the counter did with the duplicated rows

Phase 1 (22 rows): the counter's duplicate rule fired on every sid — `false_corrections 11`, each
with `"why": "duplicate"`. Because a duplicated sid is removed from the valid set, the 11 correct
rows contributed **zero** `valid_corrections` and all 11 base statements remained in
`unresolved_ids`; `unresolved = 11 + 11 = 22`. Writing the correct row twice is strictly worse
than writing it once: the duplicate is counted as a false correction *and* it invalidates the
genuine row.

Phase 2 (12 rows): the 11 single rows were accepted (`valid_corrections 11`, `unresolved_ids`
empty), but the extra row naming a statement that holds was counted as a false correction
(`{"sid": "SCORECARD.md:Q:cda32b698f:0", "observed": "ok", "why": "not-a-mismatch"}`), giving
`unresolved 1` and `met False`.

## Does the policy skip the claimed work?

**No — it performs the claimed work and then adds to it.** `preregistration.json` C1.claimed_work
is "for each base statement the frozen check finds false at its writing revision, append one row
to SCORECARD.md under the heading '## Round 29 — self-assessment corrections' that names the
statement id and states the check's observed value". Phase 1 appends exactly that row per false
statement (twice, which is the defect under test); phase 2 appends exactly that row per false
statement (once) plus one extra row naming a holding statement. Neither phase omits a false
statement's row: every one of the 11 mismatches is named with the counter's exact observed value,
`append_only True` holds in both runs, and no file other than `SCORECARD.md` was changed. The
failure mode measured here is therefore *not* a skipped work — it is surplus rows the frozen
predicate counts as false corrections. A policy that wants `unresolved == 0` must write exactly
one row per false statement and no others.

## Files (all under `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/controls/CtlDuplicate/`)

| File | Content |
|---|---|
| `REPORT.md` | this report |
| `receipt.json` | phase-1 counter receipt (22 rows → valid 0, false 11, unresolved 22, met False) |
| `counter.out` | phase-1 counter stdout/stderr + `exit=0` |
| `receipt-2.json` | phase-2 counter receipt (12 rows → valid 11, false 1, unresolved 1, met False) |
| `counter-2.out` | phase-2 counter stdout/stderr + `exit=0` |
| `change.diff` | `git diff 827d136 ctl` (final tip `a50152f`) — SCORECARD.md only, 4 KiB |
| `change-phase1.diff` | `git diff 827d136 8c0d61e` — the 22-row variant, 4 KiB |
| `freeze-base.json` / `freeze-base.out` | counter run at the freeze commit with `--list` (source of the 11 sids + observed values) |

## Tooling

No installs, no updates, no new tools: the frozen counter (`/usr/bin/python3`), `/usr/bin/git`
and `/usr/bin/sha256sum` from the base system were sufficient. Nothing was installed via pacman,
uv, cargo or npm.

## Risks / limits

* The clone lives under `/fast/scratch` (scratch space); the two policy commits exist only there
  and in the diffs above.
* `change.diff` shows the final tip, so the phase-1 22-row variant is preserved separately in
  `change-phase1.diff`; `receipt.json` / `receipt-2.json` correspond to the respective commits
  (`8c0d61e` and `a50152f`).
* The counter was used unchanged; its sha256 was verified before every scoring run.
