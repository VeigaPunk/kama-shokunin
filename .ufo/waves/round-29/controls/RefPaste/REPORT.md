# RefPaste — reference policy (claimed work, not a control)

Lane: kama, round 29, claim C1 (calibration). Seat: RefPaste (executor).
Freeze commit: `827d136546b85059a984b34970f5b493d9a71290` (lane tip `master` at freeze).
Counter: `.ufo/waves/round-29/count-c1.py`, sha256 `fe11d599d064f5749c829394fc813f43921de2f9903e41c7217e3daa4b647383`
(verified unchanged immediately before the scoring run — the counter was never modified).

## Policy (what was done)

1. Cloned the lane repo read-only into the sandbox
   `/fast/scratch/hyaku/kama-r29/ctl/RefPaste/repo` and checked out branch `ctl` at the freeze
   commit `827d136546b85059a984b34970f5b493d9a71290`.
2. Ran the **frozen, unmodified** counter at that freeze commit with `--list` to enumerate every
   extracted base statement and its per-statement check result:
   `count-c1.py --repo <clone> --tip ctl --list --out <controls>/RefPaste/list.json`
   → `statements 69 mismatched_at_base 11 append_only True valid_corrections 0 false_corrections 0 unresolved 11 met False`.
   The 11 mismatching statements (sid, file, line, class, token, writing revision W, observed) were
   taken verbatim from that receipt's `mismatches[]` array.
3. Appended to the **clone's** `SCORECARD.md` (append-only; the base bytes are untouched and the
   base prefix is preserved, `append_only True` in the final receipt):
   - the frozen heading exactly `## Round 29 — self-assessment corrections` (em dash U+2014, byte-identical to `HEADING` in the counter),
   - the table header `| id | file:line | class | token | observed |` and a separator row,
   - one row per mismatch, in the counter's own row shape:
     `| SA29:<sid> | <file>:<line> | <class> | <token> | <observed> |`
     with `observed` copied **exactly** as printed in the receipt (`q:no-artifact` / `p:absent`).
     No token in the 11 rows contained a `|`, so no `\|` escaping was needed (none applied).
4. Committed in the clone only (`git -c user.name=ctl -c user.email=ctl@local commit`):
   clone commit `a59f90ec1d7077a482ada768be8cb7d976b96a71`, parent = freeze commit.
5. Scored with the frozen counter, unchanged, tip `ctl`:
   `count-c1.py --repo <clone> --tip ctl --out <controls>/RefPaste/receipt.json`.

The lane repo `/home/vgpnk/Projects/shokunin/kama-shokunin` was never written to (no git/jj write,
no tracked-file edit); the only lane-side artifacts are this seat's own files under
`.ufo/waves/round-29/controls/RefPaste/`. No llama-server was started. No tools were installed.

## Counter line (verbatim, from `counter.out`)

```
statements 69 mismatched_at_base 11 append_only True valid_corrections 11 false_corrections 0 unresolved 0 met True tip a59f90ec1d70
exit=0
```

`met` = **True** (target `mismatched_at_base >= 1 and unresolved == 0`: 11 >= 1 and 0 == 0).
Receipt fields: `statements 69`, `by_class {C:27, H:2, N:2, P:10, Q:25, T:3}`,
`mismatched_at_base 11`, `append_only True`, `correction_rows 11`, `valid_corrections 11`,
`false_corrections []`, `unresolved 0`, `unresolved_ids []`, `met True`,
`tip a59f90ec1d7077a482ada768be8cb7d976b96a71`.

This matches the frozen base receipt shape (`.ufo/waves/round-29/before/c1-base.json`: 69 statements,
11 mismatches, unresolved 11, met False) with only the correction rows added — the policy changed
nothing the counter measures except the tip SCORECARD.md's appended section.

## Exactly what the policy read

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/count-c1.py` (read only; sha256
  re-verified, never modified).
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/preregistration.json` (read only).
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/controls/CONTEXT.md`,
  `.../controls/items/RefPaste.md`, `/home/vgpnk/.omp/agent/RULES.md` (read only).
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/before/c1-base.json` (read only).
- The counter's own `--list` output produced **by the frozen counter** from the sandbox clone
  (`list.json`, `list.out`) — this is the only source of the 11 sids, tokens and observed values.
- The clone's `SCORECARD.md` tail (to find the append point and confirm the base bytes are preserved).

## What the policy did NOT read

- No lane blob at any revision was opened by hand: the policy did not `git show`/`cat-file` any
  base tree, and did not inspect the file content that made any statement false. Every observed
  value is the counter's own printed string, taken from the `--list` receipt.
- `SHONEN.md` was not read, edited or inspected (no SHONEN statement mismatched, so no row for it).
- No blob, artifact or tree of the lane was searched by the policy for the quoted spans; the
  `git grep` for the Q class was done by the counter itself, not by me.
- No sibling control seat's output, no other lane, no `.ufo/state`, `MANIFEST.json` or
  `watchdog.log` was read or written. No network access. No tool installs.

## Timing and judgment

- Policy wall time: clone + freeze checkout ~1.5 s; `--list` run at the freeze commit ~3.1 s
  (cold, includes `git blame --line-porcelain` over both files); the append and the clone commit
  are a single small edit (~1 s); the scoring run ~1.1–1.2 s (measured 1.13 s by a timed
  subprocess, and 1.22 s by wall clock on the recorded `counter.out` run). Total ≈ 10 s.
- Judgment needed: **none**. All 11 rows were mechanically transcribed from the counter's own
  `--list` receipt (`mismatches[]`: `sid`, `file`, `line`, `class`, `token`, `observed`); the
  observed strings are the counter's fixed failure tokens (`q:no-artifact`, `p:absent`), so no
  interpretation of "what was actually observed" was required. The only choices were mechanical:
  the heading text (copied byte-for-byte, em dash U+2014 confirmed against `HEADING` in the
  counter source) and the table shape mandated by the item. No row was hand-computed, inferred,
  or written from the base receipt alone.

## Does the policy skip the claimed work?

**No.** `preregistration.json` C1.claimed_work requires: "For each base statement the frozen check
finds false at its writing revision, append one row to SCORECARD.md under the heading '## Round 29 —
self-assessment corrections' that names the statement id and states the check's observed value."
The policy did exactly that for all 11 mismatching base statements (11 rows, one per `sid`; the
counter reports `valid_corrections 11`, `false_corrections 0`, `unresolved 0`). The claimed work is
performed, not stubbed: the rows are backed by the instrument's own per-statement checks, run
against the lane tree and history at each statement's writing revision. As preregistration notes,
this is therefore the **reference policy, not a control** — the counter does not refuse it, and it
is expected to meet.

## Files

- Sandbox clone (writes confined here): `/fast/scratch/hyaku/kama-r29/ctl/RefPaste/repo`
  (branch `ctl`, commit `a59f90ec1d7077a482ada768be8cb7d976b96a71`).
- `Report: .ufo/waves/round-29/controls/RefPaste/REPORT.md`
- `Report: .ufo/waves/round-29/controls/RefPaste/change.diff` (1933 bytes; `git diff 827d136 ctl`)
- `Report: .ufo/waves/round-29/controls/RefPaste/receipt.json` (counter receipt, `met True`)
- `Report: .ufo/waves/round-29/controls/RefPaste/counter.out` (counter stdout + `exit=0`)
- `Report: .ufo/waves/round-29/controls/RefPaste/list.json` (the `--list` run at the freeze commit)
- `Report: .ufo/waves/round-29/controls/RefPaste/list.out` (the `--list` run's stdout)
