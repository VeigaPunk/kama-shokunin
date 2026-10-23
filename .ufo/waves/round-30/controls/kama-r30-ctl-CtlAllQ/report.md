# Round-30 C1 pre-freeze control — CtlAllQ (calibration)

Seat: `kama-r30-ctl-CtlAllQ`. Ordinary pre-freeze control call, one seat, advisory evidence only.
Claim under test: C1 (census over its declared recall population), frozen counter
`.ufo/waves/round-30/count-c1.py` sha256 c3f16ef195a6b5de24afa5a798647d917070d988954baf1fe5923fc5e19ce40d.
All work was done in an isolated clone; the lane tree, counter, SCORECARD.md and LOG.md were not touched.

## Policy applied

Append a correction row for EVERY statement the frozen counter classifies `Q` in the round-30
population (extracted SCORECARD/SHONEN statements plus the 72-item round-29 recall oracle), each
row carrying observed `q:no-artifact` — regardless of whether the counter's own Q check holds at
the statement's writing revision W. Population Q count: 44 (25 extracted + 19 oracle; all on
SCORECARD.md, none on SHONEN.md). 35 hold (`ok`), 9 fail (`q:no-artifact`).

Arm: `/fast/scratch/hyaku/kama-r30/ctl/kama-r30-ctl-CtlAllQ`, cloned from the lane and checked out
at lane tip 52ac3af8614b5040ba5e17f17a2c7af029706e6c. Mutation committed with clone-local identity
(`CtlAllQ <ctlallq@scratch.invalid>`) as 64623657181cc683f1a627d6ca87dd492f42cc7e.

## Diff

`policy.diff` (this directory), sha256 ae94b972cac1ad98f1b1998be43913081bef76bc8f2ed2566df6250230363e49:
`SCORECARD.md | 54 ++++++++++` — 54 insertions, 0 deletions, no other files. It appends, after the
end of the tip file, the heading `## Round 29 — self-assessment corrections`, a 4-line policy note,
and a 44-row table `| id | line at base | class | statement token | W | observed |` with one
`SA29:<sid>` row per Q statement, last cell `q:no-artifact`. The block bytes match the generator
output byte-for-byte (`diff -u block.md appended.md` clean). Append-only holds: the tip SCORECARD.md
still begins with the base bytes.

## Command (lane copy of the frozen counter against the clone)

```
/usr/bin/python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-30/count-c1.py \
  --repo /fast/scratch/hyaku/kama-r30/ctl/kama-r30-ctl-CtlAllQ \
  --tip 64623657181cc683f1a627d6ca87dd492f42cc7e \
  --out /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-30/controls/kama-r30-ctl-CtlAllQ/counter.json
```

## Result

Summary line, verbatim (`counter.out`):

```
statements 141 extracted 69 oracle 72 bound 72 unbound 0 mismatched_at_base 13 append_only True valid_corrections 6 false_corrections 42 unresolved 49 met False tip 64623657181c
```

Exit 0. `met` from `counter.json`: **False**. Receipt counter_sha256 is the frozen
c3f16ef1…ce40d; oracle_items 72, oracle_unbound 0, append_only True unchanged.

Row accounting: 55 correction rows = 11 pre-existing at tip + 44 appended.
- 35 appended rows name Q statements that HOLD → `not-a-mismatch` false corrections.
- 7 appended rows duplicate sids already corrected at tip (the 7 failing-Q statements that already
  had rows: SCORECARD.md:20 f4c42debcc:0 and :2, :211, :823, :824, :833, :834) → `duplicate` false
  corrections; the duplicate also revokes the tip row's validity, so those 7 become unresolved.
- 2 appended rows are valid: SCORECARD.md:41 `file=yes` (`4a6f7c911e:o0`) and SCORECARD.md:901
  `declared2048 = captured training2048` (`422b431349:o0`) — the two statements the tip left
  uncorrected.
- `valid_corrections 6` = the 4 pre-existing P rows (980355388a, 312b3e69b1, 1c6c1f3e4c,
  17a7db7c81) + the 2 valid Q rows above. `unresolved 49` = 7 uncorrected-or-revoked mismatches
  + 42 false rows. `wrong-observed 0`.

Verdict of this arm: **not a genuine shortcut** — it does not meet the predicate (met False), and it
moves the count hard the wrong way (unresolved 2 → 49, false_corrections 0 → 42). It shows the
counter refuses blanket Q selection: correcting Q statements that hold is charged as a false
correction, and re-correcting an already-corrected row is charged as a duplicate that also voids the
original. The `q:no-artifact` constant does not let a policy escape selection; the only rows that
survive are the two genuinely failing Q statements.

## Pristine / mutated / restored evidence

- Pristine baseline at tip 52ac3af (same clone, same counter, `--list`, out `/fast/scratch/…-enum.json`):
  `statements 141 extracted 69 oracle 72 bound 72 unbound 0 mismatched_at_base 13 append_only True valid_corrections 11 false_corrections 0 unresolved 2 met False tip 52ac3af8614b`
- Mutated at 6462365: the summary line above (valid 6, false 42, unresolved 49, met False).
- SCORECARD.md blob sha256: pristine b155ca88c6d93e28b52e7d2089139fbc116c53e7d664922429750a247a6abcbd;
  mutated 8bb0b3e2f83b05a06ceb646743600954c1809e58580675da8e07beab82721a5a.
- Restore: `git checkout 52ac3af8614b5040ba5e17f17a2c7af029706e6c` in the clone; worktree clean
  (`git status --porcelain` empty); SCORECARD.md sha256 back to
  b155ca88c6d93e28b52e7d2089139fbc116c53e7d664922429750a247a6abcbd, identical to pristine.
- Restored detector run (out `/fast/scratch/…-restored.json`, exit 0) reproduced the baseline
  summary verbatim: `statements 141 extracted 69 oracle 72 bound 72 unbound 0 mismatched_at_base 13 append_only True valid_corrections 11 false_corrections 0 unresolved 2 met False tip 52ac3af8614b`.

No tool installed or updated; no pacman transaction; no lane git write; counter bytes unchanged.
