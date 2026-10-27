# F2 — stale battery receipts (observed at audit time, fixed mid-audit)

## Observed

At the time of this audit (lane HEAD `8abadfed`), the frozen battery receipt dir
`.ufo/waves/round-55/c1/battery/` contained 7 `*.out` files, but the committed
`.ufo/waves/round-55/c1/battery/run-battery.py` produces only 5 receipts
(control + 4 `MUTANTS` keys: m-ldpreload, m-text-flip, m-ldaudit-foreign,
m-member-flip). Two receipts had no producing code anywhere in the committed
runner:

- `m-ldaudit-writable.out` — met=True, all legs passing, envnames=5 (its LD_AUDIT
  never reached the server env; the committed LD_AUDIT mutant shows 6).
  Server pids 1333468-1359821 — an earlier battery iteration epoch (committed
  runner's own receipts run at pids 1525580-1639512).
- `m-extra-in-tree.out` — met=True, envnames=6, server pids 225464-256725 —
  a different pid-allocation era entirely (pid_max=4194304; every other receipt
  ran at 1.1M-1.6M pids). Referenced only in a run-battery.py comment as past
  evidence — the receipt itself is not producible by the committed script.

Under the frozen kill rule "any battery mutant prints met=True", these two
indistinguishable-from-live `met=True` receipts in the frozen receipt_dir also
tripped the rule.

## Fixed mid-audit

Commit `c2c05e30` (round-55 w1 integration; HEAD advanced past it to `bf336baa`)
removed both files (`D .ufo/waves/round-55/c1/battery/m-ldaudit-writable.out`,
`D .../m-extra-in-tree.out`), and the lesson's Mistakes row now names them as
history (`corpus/lessons/round-55.md:99-104`).

## Evidence preservation

The removed receipts are recovered verbatim from commit `8abadfed` into
`.ufo/waves/round-55/w1/out/V4Receipts/receipts/attic-8abadfed/` for audit
completeness.
