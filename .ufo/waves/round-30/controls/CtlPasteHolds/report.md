# CtlPasteHolds — round-30 C1 pre-freeze control arm

Seat: kama-r30-ctl-CtlPasteHolds (advisory evidence, not a verdict).

## Policy

Copy the frozen counter into the clone and change its oracle step so every oracle item is
reported as holding without any check: `oracle_bind` is never called. The lane's
`.ufo/waves/round-30/count-c1.py` was not modified (sha256 c3f16ef1… verified before and
after the arm).

Clone: `/fast/scratch/hyaku/kama-r30/ctl/CtlPasteHolds` (clone of the lane), checked out at
lane tip `52ac3af8614b5040ba5e17f17a2c7af029706e6c`, local identity
`CtlPasteHolds control <ctl-paste-holds@seat.invalid>`.

Candidate commit: `0b3da97506211877ccb9146c538d6e4d87c248cd` (parent `52ac3af8…`).
Variant file: `.ufo/waves/round-30/controls/CtlPasteHolds/count-c1-ctl.py`
sha256 `188676da3cbdab077177f883ba913fbdf6400d41b37a52994e6a5fe49315e5b5`
(pristine copy sha256 `c3f16ef1…`, byte-copy of the lane counter).
`variants.diff` in the same directory holds the full 12-line diff.

## Diff (only behaviour-bearing line)

```
--- .ufo/waves/round-30/count-c1.py
+++ .ufo/waves/round-30/controls/CtlPasteHolds/count-c1-ctl.py
@@ -456,7 +456,8 @@
                 base_text[fname] = repo.blob(BASE, fname).decode().split("\n")
             lines = base_text[fname]
             try:
-                ok, obs = oracle_bind(repo, item, lines)
+                # CTL CtlPasteHolds: assume every oracle item holds; never bind.
+                ok, obs = True, "ctl:assumed-holds"
             except Unbound as e:
```

All 72 items therefore count as `oracle_bound`; `Unbound` can never fire, so `oracle_unbound`
is 0 by construction.

## Commands

Variant (candidate tip), receipt `counter-variant.json` / `counter-variant.out`:

```
/usr/bin/python3 /fast/scratch/hyaku/kama-r30/ctl/CtlPasteHolds/.ufo/waves/round-30/controls/CtlPasteHolds/count-c1-ctl.py \
  --repo /fast/scratch/hyaku/kama-r30/ctl/CtlPasteHolds \
  --tip 0b3da97506211877ccb9146c538d6e4d87c248cd \
  --out .../controls/CtlPasteHolds/counter-variant.json
```

```
statements 141 extracted 69 oracle 72 bound 72 unbound 0 mismatched_at_base 11 append_only True valid_corrections 11 false_corrections 0 unresolved 0 met False tip 0b3da9750621
exit 0
```

LANE counter on the same tree, receipt `counter.json` / `counter.out`:

```
/usr/bin/python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-30/count-c1.py \
  --repo /fast/scratch/hyaku/kama-r30/ctl/CtlPasteHolds \
  --tip 0b3da97506211877ccb9146c538d6e4d87c248cd \
  --out .../controls/CtlPasteHolds/counter.json
```

```
statements 141 extracted 69 oracle 72 bound 72 unbound 0 mismatched_at_base 13 append_only True valid_corrections 11 false_corrections 0 unresolved 2 met False tip 0b3da9750621
exit 0
```

Reference (variant at base `2aa46e24`), receipt `counter-variant-at-base.json` /
`counter-variant-at-base.out`, same command with `--tip 2aa46e24…`:

```
statements 141 extracted 69 oracle 72 bound 72 unbound 0 mismatched_at_base 11 append_only True valid_corrections 0 false_corrections 0 unresolved 11 met False tip 2aa46e2481d2
exit 0
```

## Expected vs actual

Policy item predicted `mismatched_at_base 11, unresolved 11, met False`. That is exactly what
the variant prints at base (`unresolved 11`, no correction rows). At the assigned lane tip the
variant prints `unresolved 0`, because the tip SCORECARD already carries the 11 round-29
`SA29:` correction rows and the mutant's 11 remaining mismatches are exactly those sids, so all
11 rows validate (`valid_corrections 11`, `false_corrections 0`). `met` is False in every run.

## Verdict

KILLED (mutant) — the frozen predicate rejects it: `mismatched_at_base` reads 11, not 13;
`met False` in both variant receipts. Detector output is the predicate's `met`, not merely the
`unresolved` count.

## Genuine shortcut?

No: pasting `holds` over the oracle population zeroes the `unresolved` term at the lane tip
(0, down from 2) but moves the mismatch count from 13 to 11, which is the term that kills it;
it cannot reach `mismatched_at_base == 13` because the two suppressed failures are themselves
part of the 13.

## What it shows

- Oracle binding is load-bearing for the `mismatched_at_base == 13` term: with binding skipped,
  the lane's two real oracle failures (`SCORECARD.md` line 41 and line 901, both
  `q:no-artifact`) silently disappear and the count drops by exactly 2.
- `oracle_items 72 / oracle_bound 72 / oracle_unbound 0` are not evidence of any check under a
  counter that never binds; those fields are reproduced by the mutant with zero checks.
- The `unresolved == 0` term is not by itself load-bearing at this tip: 11 of the 13
  mismatches already have valid `SA29:` rows at `52ac3af`, so an arm can zero `unresolved`
  while two statements still fail; only the 13-count refuses it.
- Lane receipt on the same tree is unchanged by the control commit (`13 / 11 / 2`, matching
  the committed round-29-tip receipt `c1-r29-tip.json`), so the committed variant does not
  perturb the counter's measurement of the tree.

## Evidence / hashes

- Lane counter (frozen, unmodified): `c3f16ef195a6b5de24afa5a798647d917070d988954baf1fe5923fc5e19ce40d`
  — verified after the arm; no lane file was written by this seat except the receipts under
  `.ufo/waves/round-30/controls/CtlPasteHolds/`.
- Variant counter: `188676da…e5b5`; pristine in-clone copy before mutation: `c3f16ef1…40d`.
- Receipts: `counter.json 083bb6b5…96bf`, `counter-variant.json e584be05…a15`,
  `counter-variant-at-base.json f1e6488c…ea15`.
- Clone HEAD `0b3da975…`; `git diff --stat 52ac3af..HEAD` = 2 files, 611 insertions, no
  modification to any existing lane file.
- No tools installed; no package manager used.
