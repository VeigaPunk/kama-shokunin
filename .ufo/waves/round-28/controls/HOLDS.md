# Round-28 pre-freeze control call — dispatch record and holds

Dispatched 08:14:5xZ as one `task` call of 10 seats (seat gate `kama-r28-ctl` granted 10 at 08:14:33Z), counter sha256 e6a706bb2e15aec288924b9aec863ff0b1ffdd7e588e78250c0f642565c0540c frozen at d8bf1804.

| seat | role | outcome | status as evidence |
|---|---|---|---|
| CtlDoNothing | executor | does-not-meet, counted 0 (base, freeze, empty registry) | receipt |
| CtlJunk | executor | does-not-meet, counted 0 of 30 | receipt |
| CtlLabelKeyed | executor | does-not-meet, counted 12 of 41 | receipt |
| CtlSourceBlind | mutation-tester | does-not-meet, counted 14 of 38 | receipt |
| CtlDuplicateField | executor | does-not-meet, counted 0 of 26 | receipt |
| CtlNoReader | mutation-tester | provider refusal, 9.7 s: `Codex error event: This content was flagged for possible cybersecurity risk. ... (code=cyber_policy)` | HOLD — no receipt; never retried |
| CtlObjectStore | mutation-tester | provider refusal, 27.3 s: `Refusal (cyber): This request triggered restrictions on violative cyber content and was blocked under Anthropic's Usage Policy.` | HOLD — no receipt; never retried |
| CtlAllFalse | mutation-tester | provider refusal, 1m41s: `Refusal (cyber): This request triggered restrictions on violative cyber content and was blocked under Anthropic's Usage Policy.` | HOLD — no receipt; never retried |
| CtlEcho | executor | returned `does-not-meet, counted 1 of 21`, but its output ends `Claude Opus 5.5 hit a safety filter, and the conversation was automatically switched to Claude Opus 4.8` | HOLD — automatic model switch after a safety filter; its files stay committed as a record, its findings are NOT evidence |
| CtlSourceMisuse | executor | returned `does-not-meet, counted 2 of 12` (the 2 pilot rows), output ends with the same automatic-switch notice | HOLD — same rule; files kept as a record, not evidence |

Classes of preregistration.json `controls_required` with no evidential receipt this round: no-reader, object-store, all-false, echo, source-misuse. Their counter clauses are unchanged from the round-27 A3 hardening (no-reader, object-store) or exercised by the evidential receipts above (CtlJunk and CtlDuplicateField hit clauses b and d; CtlLabelKeyed and CtlSourceBlind hit d and e). This is disclosed, not repaired: refused items end and are never re-sent.

Margins: the strongest evidential shortcut, CtlSourceBlind, reached 14 against target 18; CtlLabelKeyed reached 12. Neither meets the target, so the counter and target stand unchanged (no amendment). Both receipts record live truths for the rows they reached; a writer who copies live outcomes does the claimed work (preregistration.json not_counted_boundary).

Findings reported by evidential seats (not counter changes): `excluded_fields` (n_cache_reuse, xtc_threshold) is not enforced by code (CtlLabelKeyed); round-28 data excludes both fields and the closure can check the registry. Clause (a) matches SKILL cells by substring.
