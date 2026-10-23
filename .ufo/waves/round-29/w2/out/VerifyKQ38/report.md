# VerifyKQ38 — round-28 routed defect / KQ38

## Verdict

KQ38 captures the substantive measurement-dependence rule and names both required shortcut classes, but **does not unambiguously capture every routed sub-item as written**. The remaining gap is the route’s strict freeze-before-any-seat ordering and durable pre-data receipts.

## Finding

**Low — ordering and receipt-evidence requirements are underspecified.** The routed item says the counter must be “frozen before any seat scores” and that pre-data “receipts must include” the type-only and declared-bounds controls (`/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/lessons/round-28-verifier-spotcheck.md:222-226`). KQ38 instead says a non-author “pre-freeze control call” scores the shortcuts and “those exact counter bytes are then frozen unchanged” (`/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/QUALITY.md:283`). This freezes after the control call, and does not say the call’s receipts must be retained/committed. KQ38 separately requires the controls precede *data* scoring, so it is unclear whether the control caller is outside “any seat”; if it is a seat, the order is contrary to the routed text. A future implementation could satisfy the explicit KQ38 sequence while lacking the routed freeze-before-any-seat evidence/order.

The rest of the routed core is present: exclude source-predictable outcomes; credit only outcomes requiring live measurement; test both type-guess and declared-bounds projection against the same counter, population, and target with a non-author before data scoring; freeze those same bytes; require both shortcuts to miss and a measurement-dependent positive control to meet. Thus no shortcut class or measurement-dependence condition is omitted.

## Evidence

- Lesson item 1 (`.../corpus/lessons/round-28-verifier-spotcheck.md:222-226`): requires freeze before any seat scores; pre-data type-only and declared-bounds projection receipts; counted property not predicted by `server-schema.cpp` alone.
- Working-tree criterion (`.../corpus/QUALITY.md:283`): contains “every outcome predictable from pinned source-declared bounds or type rules is excluded,” “value requires the live measurement,” and the same-counter/population/target non-author controls for both shortcut classes. Its sequence is control call → freeze; it specifies before any *data seat* scores, not before any seat scores. `QUALITY.md` is an uncommitted working-tree addition, so it has no landed commit hash.
- Type-control evidence: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-28/controls-A1/CtlA1Conversion/REPORT.md` records `A0 counted 20 registered 52`, target 18, and `A1 counted 0`; the report identifies tested lane commit `75b78bb4900aae1edcdb6b229bb8c572c20fcbce`. Its cited receipt `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-28/controls-A1/CtlA1Conversion/receipt-A0.json` records `counted: 20`, `registered: 52`, `met: true`, with `base: 4179301f7516ad667509d54b5ebfe0a70a002d5b`.
- Declared-bounds evidence: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-28/w2/out/ExecShortcutPostData/shortcut-receipt.json` records `counted: 20`, `registered: 20`, `target: 18`, `met: true`, and the same base `4179301f7516ad667509d54b5ebfe0a70a002d5b`. Its accompanying advice at `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-28/w2/advice/ExecShortcutPostData.md:63-72` records the 20/20 result and describes the source-declaration derivation. KQ38 correctly calls both receipts prior falsifiers rather than retroactive rescoring.

## Residual risk and verification gaps

This was a document/evidence review only; no code checks were in scope or run. The criterion’s substantive conditions are verified in the working tree, but its wording does not make the literal route ordering or durable-receipt requirement enforceable. No tools were installed or updated.
