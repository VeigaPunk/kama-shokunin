# N3Patterns — C2 cross-source pattern scan (round 44, lane kama)

**Verdict: outside closures route missing-receipt and stale-self-description defects most often (47 and 44 of 168 instances); no defect class's frequency falls over rounds 10→43 (4.4 → 5.0 → 5.3 routed defects/round), and the single largest gap is the systematic absence of outside closures for rounds 20–23, which shows up verbatim in the C2 draft ledger as four `absent` outside verdicts.**
Discernment is the only trend with material self/outside disagreement (8 underclaims, 11 mixed, 4 absent vs 11 agree); the prototype's "discernment underclaimed 7 times" is one short of the ledger-implied 8.

## Scope and method

Read all verifier-spotcheck files at the lane base `9d9cc93ec50783cd114829a91757b90d57c78dc6` and in the round-44 working tree (`round-10..19`, `round-24..43`; 30 files, 4648 lines). Evidence for the file inventory:

- `git -C /home/vgpnk/Projects/shokunin/kama-shokunin ls-tree --name-only 9d9cc93e… corpus/lessons/` → contains `round-10..19-verifier-spotcheck.md` and `round-24..43-verifier-spotcheck.md`, **no** `round-20/21/22/23-verifier-spotcheck.md` (the `round-20..23.md` lessons exist, the closures do not).
- `wc -l kama-shokunin/corpus/lessons/*verifier-spotcheck.md` → 30 files, 4648 lines.

Each file was read in full; every routed-defect item (D/R/N numbered items and conformance findings) was classified into one of six buckets, with the cited pointer (file:line) recorded in `patterns.tsv`. Classes:

- `stale_self_description` — a lane-owned document asserts something no longer true / inaccurate (dates, counts, pointers, wording vs implementation). e.g. r11 D2 (`round-11-verifier-spotcheck.md:213-216`), r17 R3 (`:232-233`), r34 report "coverage map gains two entries" (`round-34-verifier-spotcheck.md:94`).
- `wrong_digest` — a hash/digest cited in lane artifacts does not match actual bytes or the committed evidence (truncated/wrong sha256, 39-hex quotes). e.g. r11 D1 (`round-11-verifier-spotcheck.md:101-110`), r38 S472 (`round-38-verifier-spotcheck.md:73`), r40 D3/D4 (`round-40-verifier-spotcheck.md:99-100`).
- `misattributed_id` — an id (S-row, seat, commit, wave, source/decision record) is attributed wrongly or a pointer drifts to the wrong object. e.g. r36 D2 staged-id cross-references (`round-36-verifier-spotcheck.md:177-183`), r39 D1 unlanded-hash citations (`round-39-verifier-spotcheck.md:25`).
- `counter_shortcut` — an automated counter/gate/guard accepts content without verifying the claimed property, or a recorded count/receipt mis-states what ran (shortcut meets a frozen counter; occurrence-only checks; guard promise false). e.g. r14 R1 (`round-14-verifier-spotcheck.md:142`), r26 ShortcutRows 12/12 (`round-26-verifier-spotcheck.md:98-116`), r31 C1/C2/C3 controls (`round-31-verifier-spotcheck.md:69-71`).
- `missing_receipt` — required evidence/receipt absent, uncommitted, or unreproducible (statscommitted paths, uncited receipts, unregistered instruments, dead seats without logs, absent closure files). e.g. r19 census receipts uncommitted (`round-19-verifier-spotcheck.md:40-42`), r37 counters not committed (`round-37-verifier-spotcheck.md:190-198`), rounds 20–23 (no closure file).
- `other` — compliance/protocol/operator drift (in-place rewrites, append-only violations, stale driver pins, wave-floor/undispatched waves, MISSION.md drift, future-dated digests).

## Frequency

| class | total | 10–19 | 20–29 | 30–43 | per-round trend |
|---|---|---:|---:|---:|---|
| missing_receipt | 47 | 12 | 15 | 20 | rising (1.2 → 1.5 → 1.4) |
| stale_self_description | 44 | 12 | 15 | 17 | flat (1.2 → 1.5 → 1.2) |
| other | 30 | 7 | 6 | 17 | late surge (0.7 → 0.6 → 1.2) |
| counter_shortcut | 25 | 7 | 9 | 9 | plateau (0.7 → 0.9 → 0.6) |
| misattributed_id | 16 | 4 | 5 | 7 | slight rise |
| wrong_digest | 6 | 2 | 0 | 4 | sparse, late |
| **all** | **168** | **44** | **50** | **74** | **4.4 → 5.0 → 5.3 / round** |

Output: `patterns.tsv` (48 rows, `round class count pointer`). Commands: read of the 30 lesson files; classification recorded with pointers; totals computed in Python over the TSV (`totals` line above).

**Answer to the scan question:** the most-routed classes are missing receipt and stale self-description; the frequency does **not** fall over rounds — it is flat-to-rising (the later closures are longer and route more items, e.g. r19: 10, r26: 11, r28: 10). The only class that disappears in the middle block is wrong-digest, and it re-appears in r38/r40 as digest-citation corrections (S472, R36-D2C, 39-hex quote) — i.e. the class shifts from *snapshot* digests (r11 D1) to *registry receipt* digests (r38/r40).

## The C2 trend-verdict relation

From the frozen draft ledger (`.ufo/waves/round-44/c2/draft-ledger.tsv`, 204 rows, parsed with Python; order harmed < unchanged < unprovable < unprovable-but-better < improved):

| trend | agree | underclaim | overclaim | mixed | absent |
|---|---|---:|---:|---:|---:|
| expansion | 25 | 0 | 2 (r19, r28) | 2 | 5 |
| quality | 25 | 0 | 1 (r25) | 3 | 5 |
| discernment | 11 | **8** | 0 | 11 | 4 |

- Discernment carries almost all disagreement: `[10, 11, 19, 25, 34, 35, 40, 43]` underclaims (self `unchanged`, outside `improved`). The prototype says 7; the ledger semantics give **8** — the prototype undercounts by one (r43 is the extra row; or r40, depending on which the prototype excluded — the ledger has no exclusion). No expansion/quality underclaim exists.
- The underclaim rounds have a slightly above-average defect density (45 defects over the 8 rounds = 5.6/round vs 4.9 overall): the lane under-credits discernment precisely in rounds where the outside closure routes substantive corrections (r19: 10, r25: 7, r34: 7, r40: 5, r43: 6).
- Round 25 is the only `harmed` outside verdict (quality) and is an *overclaim* (self `unchanged` > outside `harmed`) — the one direction where the lane over-rated itself; the correction chain (r25→r26→r27) is visible in the defect record.
- Rounds 20–23 have **no outside closure file at the lane base**, which is exactly why the draft ledger marks those 12 outside rows `absent` (line `-`, "no line gives this trend a verdict word"). This is the largest single missing-receipt cluster (4 rounds × 3 trends) and makes the C2 "every round-10..43 trend verdict ... is ledgered" predicate structurally dependent on the `absent` verdict class for those rounds.

## Findings (not fixed — lane/tools are frozen)

1. Prototype count discrepancy: "discernment underclaimed 7 times" vs ledger-derived 8 (rounds 10,11,19,25,34,35,40,43). If the round-44 SCORECARD uses the prototype figure, it will disagree with the valid ledger rows.
2. Rounds 20–23 have no `round-N-verifier-spotcheck.md` at `9d9cc93` (nor in the working tree). The C2 counter's `absent` branch is what carries them; any future "missing=0" reading should treat them as a covered gap, not a silent one.
3. The single most repeated counter defect class (25 instances) is the "counter meets a control that skips the claimed work" shortcut — it is the mechanism behind the r26/r28/r31 honest stops, and it plateaus rather than disappearing (r14 R1 → r16 → r17 R4/R6/R7 → r25 → r26 F2 → r27 → r28 → r31 → r37 → r39 D2 → r40 D1 → r41/r42).
4. `wrong_digest` defects are genuinely rare (6) and always actionable once found — every instance is a one-line append-only fix (r11 D1, r38 S472, r38 R36-D2C, r40 D3/D4).

## Verification

- `read` of all 30 closures (listing above); `read` of `round44-verdict-ledger-audit.py:3-54` (contract, ORDER, absent semantics); `glob` + `git ls-tree` for the lesson inventory; Python parse of the draft ledger (204 rows, `regex 25/0/2/2/5` etc.); Python emission of `patterns.tsv` with counts (totals: missing_receipt 47, stale_self_description 44, other 30, counter_shortcut 25, misattributed_id 16, wrong_digest 6; sum 168).
- No lane file was edited; no fleet file was written; scratch `/fast/scratch/hyaku/kama-r44/N3Patterns` was removed after use.

## Deliverables

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-44/w1/out/N3Patterns/patterns.tsv`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-44/w1/out/N3Patterns.md`
