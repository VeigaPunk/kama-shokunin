# R57Item14ProposalAudit — distinct case 35 (independent test of the assigned case)

Assigned case 35 is this seat's case: the considerthese 2026-10-26 proposal 3 instrument,
`tools/shortcut-tally.py` v2. The main `R57Item14ProposalAudit.md` records its disposition and relevance;
this file tests the instrument independently, without trusting its self-report, in scratch git fixtures
(no shared write, no lane edit). `<S>` = `/fast/scratch/hyaku/kama-r57/R57Item14ProposalAudit/case35`;
receipts copied to `R57Item14ProposalAudit.receipts/case35/` before scratch removal.

## Method

Four fixture repositories, each `git init`-ed under `<S>` and each proven to be its own toplevel before
the commit (`git -C <fixture> rev-parse --show-toplevel` printed the fixture path; `fixture-revs.txt`).
Each fixture holds only `SCORECARD.md` and one `.ufo/waves/round-N/w1/` directory, committed with a
throwaway identity and `commit.gpgsign=false`. Every tally invocation pins `--rev` and `--rounds`.

| Fixture | Rev | Content | Question |
|---|---|---|---|
| A | `433abe69d4035868169ebefad1ac9938d82a004d` | round 10, disclosure naming `C1` and "a shortcut control met the frozen counter", no control ids | Does total omission of ids certify? |
| B | `456509dbc8d117cd20412d4611981ea7e23c2668` | round 10, no disclosure block at all | Does a silent round certify? |
| C | `2a4d46d3f786bd65254ddbe0fc2a206e70bd5da4` | round 11, disclosure naming one benign seat `X9SourcesGuard` plus "two unnamed shortcut controls also met the counter" | Does a benign id launder undeclared shortcuts? |
| D | `63a050f8cbe9c30501d6a7378c7585b8b066d2ef` | round 12, **no** disclosure block, one placeholder `out/K9Cheat.md` (contents: "placeholder cheat note") | Is the `--check` gate satisfiable by one file with no disclosure and no data? |

## Exact commands, output, exits

```
python3 tools/shortcut-tally.py --repo repoA --rev 433abe69… --rounds 10-10 --check 0
  → exit 1; row: 10  -  -  C1  0  -  none  ok
    latest=10 shortcuts=- limit=0 result=FAIL (latest round 10 cannot certify a shortcut count (ok))
python3 … --repo repoA --rev 433abe69… --rounds 10-10 --check 1
  → exit 1; latest=10 shortcuts=- limit=1 result=FAIL (… cannot certify …)
python3 … --repo repoB --rev 456509dc… --rounds 10-10 --check 0
  → exit 1; row status no-disclosure; latest=10 shortcuts=- limit=0 result=FAIL (… no-disclosure)
python3 … --repo repoC --rev 2a4d46d3… --rounds 11-11 --check 1
  → exit 0; row: 11  1  X9SourcesGuard  C1  0  -  none  ok; latest=11 shortcuts=1 limit=1 result=PASS
python3 … --repo repoC --rev 2a4d46d3… --rounds 11-11 --check 0
  → exit 1; latest=11 shortcuts=1 limit=0 result=FAIL (latest round 11 shortcuts=1 > limit 0)
python3 … --repo repoD --rev 63a050f8… --rounds 12-12 --check 1
  → exit 0; row: 12  1  K9Cheat  -  K9Cheat  -  yes(w1,folded)  no-disclosure
    latest=12 shortcuts=1 limit=1 result=PASS
python3 … --repo repoD --rev 63a050f8… --rounds 12-12 --check 0
  → exit 1; latest=12 shortcuts=1 limit=0 result=FAIL
python3 … --repo repoA --rev 433abe69… --rounds 10-10 --json           (before a worktree edit)
python3 … --repo repoA --rev 433abe69… --rounds 10-10 --json           (after appending an
  uncommitted "seat K9Cheat" line to the worktree SCORECARD)
  → both exit 0; shortcuts None → None; records_identical=True; ids [] → []
```

Receipts: `case35/A-check0.*`, `A-check1.*`, `B-check0.*`, `C-check0.*`, `C-check1.*`, `D-check0.*`,
`D-check1.*`, `A-before.*`, `A-after-worktree.*`, fixture `SCORECARD.md` copies, `fixture-revs.txt`.

## Results

1. **Total omission is refused (A, B): good.** A disclosure block that names `C1` but no control id gives
   `shortcuts=None` (`tools/shortcut-tally.py:532`: `rec["shortcuts"] = len(rec["ids"]) if rec["ids"] else
   None`), and `--check` fails "cannot certify". A round with no block is `no-disclosure` and also fails.
   This is the property the round-56 counter lacked: the no-op counter said `met=True`; the tally refuses.
2. **Committed-bytes binding holds (A edit): positive.** An uncommitted worktree line naming `K9Cheat`
   does not move the record (`records_identical=True`), so the tally grades the commit, not the checkout.
3. **A benign id launders undeclared shortcuts (C): negative.** Naming one non-cheat seat
   (`X9SourcesGuard`, matched by `X\d+[A-Z][A-Za-z]*`) yields `shortcuts=1` and `--check 1` **PASS** exit 0
   while the same text states "two unnamed shortcut controls also met the counter". The gate compares a
   disclosure-derived count with `N`; it cannot see omission. The docstring admits the id-family
   undercount (`:43`, `:89`), but `--check` is the gate, so the admitted weakness is gated, not merely
   printed.
4. **One placeholder file satisfies both the count and the falsify field (D): negative.**
   `out/K9Cheat.md` with the literal contents "placeholder cheat note", no disclosure block, no mutant
   report, no falsify content: `shortcuts=1`, `status=no-disclosure`, `falsify=yes(w1,folded)` (the
   wave's `reports` is a `*.md` count under `out/`), and `--check 1` **PASS** exit 0. Proposal 3's third
   field, "whether the falsify wave ran", is therefore satisfiable by a file name.
5. **Live-lane re-derivation, independent of the tool's table.** At `8640e34c`,
   `--rounds 40-57 --check 5` → exit 1 with `unreadable rounds [48, 49, 50, 51, 52, 53, 54]`; the default
   window → exit 0, `latest=47 shortcuts=4 limit=5 result=PASS`. Only rounds 42 (5), 43 (2), 44 (2),
   46 (8) and 47 (4) carry a numeric count; 55 is `ok` but `-` (no control id matched, `wide` names
   `K2Predicate,K4Sizing`); 56 and 57 are `no-disclosure`.

## Verdict for this case

The instrument is fail-capable where the round-56 counter was not (total omission and a silent round are
refused; it reads committed bytes only). But its `--check` gate is satisfiable by a single placeholder
artifact and by under-declaring shortcuts behind one named id, so a green `--check` certifies disclosure
bookkeeping, not shortcut resistance. For this wave, the consequence is concrete: the round-56 no-op
defect (the operability claim) has no round-56 disclosure block to be tallied, and round 57 adds none,
so proposal 3's trend cannot register this wave's repair even if someone extends the window.

No lane file was modified; no commit, push, or judgment was made. Installations: none.
