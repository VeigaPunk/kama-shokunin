source: S552 — the round-78 append-register counter (`python3 tools/round78-append-registers.py`), which extends the round-77 register accounting; the introduction-discovery mechanics it reuses are held by S073 (git-log `--diff-filter`) and S175 (`merge-base --is-ancestor`); lane policy: `plans/round-78-claims.md` §C2 and `tools/round78-append-registers.py`.
verified-at: 2026-11-04 -03 — measured on the lane at `c62ffd3a` and re-run at the round-78 work tip; no registered consumer or serving surface was sampled by this entry.
recheck: `python3 tools/round78-append-registers.py --repo . --to c62ffd3aea930b98375f805cc3dfb821a703148b`; it must print `unaccounted=0` with the six buckets summing to `events`, and a scratch clone with the three round-77 exempt rows removed must print `unaccounted=3` and exit 1.

# A register row is bound to an event the audited revision can see

The round-77 counter answered "is every audit event accounted exactly once" for a frozen base
revision, but read the registers from the worktree and graded every row against that population.
Two failure modes followed, both recorded by round 77's own critic: a later round's appended row
could move a frozen bucket, and a row committed together with the damage it blessed could reach
green. Round 78's counter fixes both by making the row set's two boundaries explicit.

| Rule | What it fixes | Mechanism | Failure class |
|---|---|---|---|
| An event is admissible when it is ancestral to `--to` | the audit population is the frozen revision's, not the tip's | `merge-base --is-ancestor <event> <to>` (S175) | `out-of-population` when a row names a later event |
| A row counts only if it exists in the committed register blob at `--commit-at` | a worktree-only row blessing its own tip | the row's text must appear in `git show <commit-at>:<register>` | `uncommitted` |
| A row's event must be ancestral to the commit that carries the row | same-commit growth | ancestry of the row's own commit to `--to`, plus the committed-blob check | `out-of-population` |
| Registers print their own sha256 prefixes | a reader cannot tell which row set was graded | `APPEND_REGISTERS_REGISTERS exempt=<hex12> accepted=<hex12>` | (transparency only) |

The pinned run at the frozen base prints
`events=248 accepted=53 exempt=59 permitted=28 out_of_region=4 restored=99 disclosed=5
unaccounted=0 introductions=1/1 rotation_safe=1` and exits 0; the three round-77 SCORECARD
deletions (`05a03980`, `0fca5e18`, `21458716`) sit in the contract's exempt-head regions and are
accounted by `exempt-head` rows whose `count` re-derives from the audit, not from the target.
What this entry does not claim: that a green line proves the register's *content* is honest, or
that a same-commit blessing is impossible in general — it is rejected only when the named event
is not ancestral to the row's commit.

## Boundary

This is lane-internal accounting method, not serving knowledge and not a claim about any
sibling's registers. The round-77 module stays byte-frozen; round 78 imports it rather than
copying its rules. Corrected by S552's receipts (`.ufo/waves/round-78/measured/after/`), not by
this prose.
