VERDICT: partial - C1 calibration risk and C2 install-topology rejection boundary

Review boundary: read-only clone of draft `a29bb84`; no lane, fleet, sibling, host-config, or live-runtime mutation. No tools installed.

## Axis sweep
- **Operability:** C2 can make a new receipt invalid for a resolvable non-basename link (below); not observed in the current install tree.
- **Calibration:** C1's errata matcher can hide a real `landed-omitted` defect with an unrelated but valid commit (below). This is a confirmed detector gap; the checked-in rows do not exercise it.
- **Freshness:** no endpoint/runtime freshness is claimed or measured here. The audit is historical and defaults to rounds 10–20; omitting the required current-report override leaves round 21 unaudited.
- **Coverage:** C2 expands link coverage for the current flat tree but does not cover relative links escaping the server directory; C1's declared historical population is finite. No broader coverage claim is justified.
- **Depth:** no removal or weakening of existing domain guidance found in the draft diff; no depth harm observed. The C2 grid does not exercise a valid `../` target.
- **Adjacency:** fleet-repo access is read-only and limited to each `kama` report path plus git object-existence/cutoff queries; it does not sweep sibling report bodies or edit fleet state. This is not a cross-lane absorption finding.

## Findings

1. **C2 — bounded operability compatibility risk [INFERENCE for real llama-server support].** Producer `install_links()` records every symlink beside the resolved server (`tools/kama-llamacpp-live.py:205–226, 1292–1310`); the gate rejects any target containing `/` and requires the chain to end at a member of the immediate-directory regular-file tree (`tests/llamacpp-live/check-receipt.py:181–198, 441–467`). A scratch filesystem with `bin/libllama.so.0 -> ../lib/libllama.so.0.7.0` resolves to a regular file and is captured by the producer, but the gate reports `target '../lib/libllama.so.0.7.0' leaves the pinned directory`. Thus a resolvable install layout can yield a receipt the new gate rejects after the run. This does **not** demonstrate a failure on the present host: its nine observed links all target same-directory basenames. Existing receipts without the new fields remain compatible: round-18 v3 receipt passed the current gate (`VALID`, exit 0). Smallest safe correction: either preflight and report unsupported link topology before launching the server, or support normalized in-root relative targets and pin their bytes; removing the slash guard alone would leave target bytes unpinned.

2. **C1 — confirmed errata false-green path (calibration).** `apply_errata()` joins on `(round, kind, token)` and only checks that the replacement for resolvable kinds is *some* commit (`tools/report-landing-audit.py:166–181`). Targeted scratch probe supplied a `landed-omitted` defect for `33a677…` with unrelated valid commit `7a6bc9…`; result was `unmatched=0 invalid=0 corrected_by=[99] token_matches_correction=False`, exit 0. It therefore suppresses this defect although the proposed correction does not name the omitted commit. Current ledger rows for `landed-omitted` do use identical token/correction values; no current bad row was found. Smallest safe correction: require `correction == token` for `landed-omitted`; retain explicit evidence for cases where an unresolved citation legitimately maps to a different commit.

3. **C1 — bounded recurring maintenance debt.** Default `--rounds` is hard-coded `10-20` (`tools/report-landing-audit.py:377–400`); a round-21 draft is included only via `--report 21=<draft>`, as the assignment states. If a caller repeats the bare default in later rounds, current reports silently leave the audited population. Smallest safe correction: keep the current explicit override in the official measurement command and advance/document the historical range at each round boundary (or derive it from the declared report population).

## Executed evidence (commands and observed exits)
- `git -C /tmp/kama-r21-NoHarmCritic-6/lane diff --name-only 7a6bc911f9eb7dbea9e3b81f5f2449ecda10096d a29bb84abbb8b4d328f5970a89e448330a3a42ac` — exit 0; seven changed paths are lane-local; no `SCORECARD.md`, fleet report, sibling-lane, or host-config path changed.
- `find /home/vgpnk/.local/opt/llama-b11755 -maxdepth 1 -type l -printf '%f -> %l\n' | sort` — exit 0; nine symlinks, each target is a basename; no observed out-of-directory target.
- `python3 tests/llamacpp-live/check-receipt.py .ufo/waves/round-18/live-recovery/receipt-1.json` — exit 0, `VALID` (legacy v3 compatibility sample).
- `python3 tools/report-landing-audit.py --selftest` — exit 0, `selftest cases=15 failed=0`; existing cases cover unmatched/invalid errata but not an unrelated-yet-resolvable correction.
- Scratch C2 producer/gate fixture (`install_tree`, `install_links`, `link_chain_problem`) — exit 0; baseline selftest receipt errors 0; synthetic relative link resolves, and the gate returns the rejection quoted above. No server was launched.
- Scratch C1 `apply_errata()` probe — exit 0; unrelated valid replacement marked the omitted-commit defect corrected (result above).
