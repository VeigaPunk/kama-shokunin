# CR01Records — round-100 w1 — critique of C1 (calibration)

Scope: C1 only (`plans/round-100-claims.md` §C1; `.ufo/waves/round-100/claims.json` C1). Read-only against the lane. Scratch fixtures under `/fast/scratch/hyaku/kama-r100/CR01Records/` (removed). Receipts copied to `.ufo/waves/round-100/w1/out/CR01Records/`.

Commands used (all `git show` / `git grep` / `git diff --stat` read-only; one `git clone --shared` fixture, toplevel asserted before commits):

```
python3 tools/round100-record-audit.py --repo . --rev 2e27e6f1e6b2514ec8ac5d6344998b3db61e16d6   # RECORD_AUDIT100 checks=9 mismatches=0 met=True, exit 0
python3 tools/round100-record-audit.py --repo . --rev 6776c667372a0da8635ebfbda6cbc92d8fb17304   # mismatches=9 met=False, exit 1
git show 2e27e6f1:SCORECARD.md | sed -n '6538,6559p'   # correction block (SCORECARD)
git show 2e27e6f1:LOG.md      | sed -n '4100,4125p'   # correction block (LOG)
```

## 1. Sentence-by-sentence truth against committed round-99 evidence

Evidence sources checked: `.ufo/waves/round-99/w1-spec.json` (roles), `w1-results.json`, `claims.json`, `measured/c1.out` (C1 exit=0 line), `corpus/lessons/round-99-verifier-spotcheck.md`.

| # | Sentence (SCORECARD block; LOG twin is parallel) | Verdict | Evidence |
|---|---|---|---|
| S1 | "Routed by … defects 1, 2 and 4." | TRUE | spot-check §Defects lists 5 items; C1 addresses 1, 2, 4 (see §3 below). |
| S2 | "every line pointer below is bound to the revision it was read at" | TRUE | counter `bound=10 resolved=10 unbound=0` at M (`measured/c1.out`). |
| S3 | "Round-99 wave 1 had 12 seats, 0 dead (`w1-results.json`: 12 results, every output non-empty)" | TRUE | `python3` over `w1-results.json` at 6776: `seats 12 n 12 empty [] status_fields []`. (0-dead is derived: no empty output, no status field; the file has no status field, so "dead" is definitionally empty output. Acceptable, and the counter D1 documents this.) |
| S4 | "policy attack roles (reviewer, critic, mutation-tester, labrat) were 4 of 12 (33%): RV01Wording, RV02Counter, CR01Records, MT01Mutants" | TRUE | spec roles: RV01 reviewer, RV02 reviewer, CR01 critic, MT01 mutation-tester; no labrat seat exists in round 99 (the set is defined, not populated). 4/12 = 33%. |
| S5 | "ledger attack roles (adding sentinel and connector) were 6 of 12 (50%): the four above plus SN01Bounds and CN01Overlap" | TRUE | spec: SN01Bounds=sentinel, CN01Overlap=connector. 6/12 = 50%. Independently corroborated by `corpus/lessons/round-99-verifier-spotcheck.md:27` `attack_seats=6` (prefile ledger). The correction does NOT cite that line. |
| S6 | "The round-99 sentence `SCORECARD.md@6776c667:6500` ("58% attack") is arithmetic-wrong under either set" | TRUE | line 6500 at 6776 reads "…6 building seats (…), 58% attack if the connector counts". 58% = 7/12, which is neither 4/12 nor 6/12. |
| S7 | "the LOG's list `LOG.md@6776c667:4065` ("CN01Overlap (attack)") is the ledger set and stays correct" | TRUE BY CROSS-REFERENCE, NOT ON THE CITED LINE | `LOG.md:4065` (6776) is `MT01Mutants, SN01Bounds, CN01Overlap (attack) + SC01Recon, …`. Only CN01 carries "(attack)"; SN01 and the other attack seats are not labelled on that line, and no count is stated. "is the ledger set" holds only if the reader joins it to S5/`attack_seats=6`. The quoted phrase does not show it. Not a wrong record; the anchor is weaker than the sentence. |
| S8 | "The round-99 correction blocks cite the round-98 wave sentence as an unbound `SCORECARD.md` line 6431." | TRUE, LABEL CONFUSING | `SCORECARD.md:6466` (6776) "(`SCORECARD.md:6431`; the same sentence is `LOG.md:4040`)" sits under `## Round 99 correction — round-98 wave accounting` (heading at 6464). The block is a round-99 record correcting round-98, so "round-99 correction block" is accurate but reads as if it corrects round 99. |
| S9 | "It was there at the measured commit, `SCORECARD.md@00394f3b:6431` ("10 reported, 2 dead")" | TRUE | `git show 00394f3b:SCORECARD.md` line 6431 = "Wave 1 (12 dispatched seats, 10 reported, 2 dead — …". |
| S10 | "had moved by the round-99 tip, `SCORECARD.md@6776c667:6446` ("10 reported, 2 dead"), when the round-100 plan block was inserted above it." | TRUE ON LINES; CAUSE PARTLY UNTRACED | 6446 at 6776 = "Wave 1 (12 dispatched seats, 10 reported, 2 dead". Net +15 above it. `### Planned (round 100)` is at line 65 at 6776 and at line 6521 at 00394f3b (`grep -n`), so the plan section was relocated, not only inserted. The net +15 above 6431 is consistent with the relocation, but the sentence's causal account ("inserted above it") is the spot-check's, not re-traced here. |
| S11 | "The LOG twin did not move: `LOG.md@6776c667:4040` ("10 reported, 2 dead")." | TRUE | `LOG.md:4040` at 6776 and 00394f3b both = "**Wave.** 12 seats dispatched …; 10 reported, 2 dead". |
| S12 | "`.ufo/waves/round-99/claims.json` still carries `"measured": "pending"` for C1, C2 and C3 (frozen bytes, not rewritten)." | TRUE, NAME COLLISION | `grep -n measured` at 6776: lines 12, 21, 30 all `"pending"`. But "C1, C2 and C3" here are round-99 IDs (C1 operability, C2 calibration, C3 depth) inside a round-100 block where C1 = calibration and C2 = depth. Same labels, different claims. |
| S13 | "The measured predicate lines, byte-equal to the first predicate line of c1.out, c2.out and c3.out (each exit=0), are recorded in `.ufo/waves/round-100/r99-measured.json`." | TRUE (by counter check 9) | counter check 9 passes at M; `r99-measured.json` keys are `C1/C2/C3` (round-99 names) with the same collision as S12. I did not independently diff each line byte-for-byte; the counter does. |

Block-level "Round 100 correction" LOG twin: same sentences, same pointers (`LOG.md@6776c667:4065`, `:4040`, `SCORECARD.md@6776c667:6500`/`:6446`); all pass the counter.

Numbers not in the correction but present in the round-99 records (completeness check, `git show 6776:SCORECARD.md | sed -n 6468,6530p`, LOG 4050–4100): only the wave line (5+1+6 split, "58% attack if the connector counts" = S6), "12 seats, 0 dead" (S3), and round-99 C2 forge-matrix "14 of 15 forged variants caught" (LOG). The last is not graded by C1 and is not checked here (it is C2-round-99 evidence, outside C1's nine checks).

## 2. Did the correction introduce a new wrong record, stale pointer or misstatement?

No new wrong number found. All 10 bound pointers resolve at their stated revisions (counter check 8, `bound=10 resolved=10`). Pointer re-check by hand: `LOG.md@6776c667:4040`, `LOG.md@6776c667:4065`, `SCORECARD.md@6776c667:6500`, `SCORECARD.md@6776c667:6446`, `SCORECARD.md@00394f3b:6431` all contain their quoted phrases at the stated line.

Two new soft defects, neither a wrong number:
- Label collision C1/C2/C3 (S12, S13): the block reuses round-99 claim IDs inside the round-100 section. A reader of "C2" in this file will read depth; in the block it means round-99 calibration.
- S7 anchor: "is the ledger set" is supported by the spec and by spot-check `attack_seats=6`, not by the cited LOG line, which does not carry the count or the SN01 label.

## 3. Which of the five round-99 spot-check defects does C1 address?

Spot-check §Defects (`corpus/lessons/round-99-verifier-spotcheck.md`, at 6776: `## Defects` line 115, items 117–124): 1 stale `SCORECARD.md:6431` pointer; 2 "58% attack if the connector counts"; 3 S628 wrong upstream path (re-file `tools/server/tests/unit/test_router.py`); 4 `claims.json` still `"measured": "pending"`; 5 carried pre-report arms (newest-closure, round75/round78) red as disclosed.

- Addressed by C1: 1 (S8–S11, pointer rebound to 00394f3b/6776 with phrases), 2 (S6, S4–S5), 4 (S12–S13, via `r99-measured.json`; claims.json itself not rewritten, disclosed in plan §C1(c)).
- Not addressed by C1: 3 (a SOURCES/corpus re-file, out of C1's surface) and 5 (carried red pre-report arms, not a record).

Honesty of the plan: the plan's "Before" lists defects 1, 2 and 4 only, and the block says "Routed by … defects 1, 2 and 4". That is an honest statement of what was routed. It does not say 3 and 5 are open, and no disclosed-limit bullet in §C1 (a–f) or in §C2 mentions them. A reader who opens only the plan will not learn that 3 and 5 remain. Minor, but it is a silent gap, not a stated one.

## 4. Would a do-nothing control reach the target, and is C1 thin?

Do-nothing control: `--rev 6776c667` → `mismatches=9 met=False` (receipt `controls/c1-base.out`). Confirmed by my run. But that red is mostly the absence of the block, not a graded mismatch. Checks 1 and 2 fail outright; 3, 4, 6 and 7 fail because there is no block to read; 8 and 9 fail on absence and `pending`. The do-nothing control therefore separates "block exists" from "block is right" only weakly. The real sensitivity evidence is the freeze-time forgeries F1–F7 (`controls/c1-forgeries.out`, each a one-defect insertion into the correct block). I confirmed the forgery receipt is consistent with the counter on re-run only at the level of P0 (`checks=9 mismatches=0`) and base (`mismatches=9`); I did not re-execute F1–F7 (their fixtures are not committed as scripts I could re-derive, beyond the receipt).

Seat-name forgeries (my own, scratch fixture, commits on detached M clones, counter run with `--repo <fixture> --rev <new>`; receipt `.ufo/waves/round-100/w1/out/CR01Records/seat-name-forgeries.out`):

```
P0-control-copy           rc=0 :: RECORD_AUDIT100 checks=9 mismatches=0 met=True
FA-scorecard-seat-swap    rc=0 :: RECORD_AUDIT100 checks=9 mismatches=0 met=True   # CR01Records -> SC01Recon (critic -> scout) in SCORECARD block
FB-log-seat-swap          rc=0 :: RECORD_AUDIT100 checks=9 mismatches=0 met=True   # CR01Records -> SC02Sources in LOG block
FC-both-ledger-misnamed   rc=0 :: RECORD_AUDIT100 checks=9 mismatches=0 met=True   # "SN01Bounds and CN01Overlap" -> "SB01Entry and CN01Overlap" in both blocks
```

All three forgeries are false against `w1-spec.json` (SC01Recon, SC02Sources, SB01Entry are scouts/scribes, not critics/sentinels). The counter stays green. Seat membership of the attack set is therefore ungraded. The block asserts it, the spec contradicts the forged version, and nothing in the nine checks reads seat identity.

Is C1 thin relative to the §9 rule ("a calibration claim must count mismatches between self-assessment and observed repo state", `.ufo/prompts/kama-round-25.md:347-348`)? Partly. It counts mismatches between the correction's numeric self-assessments (fractions, seat count, dead count, pointers) and committed state, which is the right kind of count. It does not count the round-99 records' own self-assessments beyond the wave share (for example the round-99 axis verdicts, which the round-99 spot-check had to re-derive by hand, and seat-role lists the correction asserts). The check set is a bookkeeping set, as C1 says in its disclosed limits. That is honest, but it is thinner than the §9 phrase reads.

## Verdict per claim sentence (summary)

- S1 TRUE (routing statement accurate; silent on defects 3 and 5)
- S2 TRUE
- S3 TRUE
- S4 TRUE (seat names correct; not graded — see FA)
- S5 TRUE (corroborated by spot-check `attack_seats=6`, not cited)
- S6 TRUE
- S7 TRUE BY CROSS-REFERENCE; the cited LOG line does not carry the count (weak anchor)
- S8 TRUE; "round-99 correction block" is a round-98 correction (label confusing)
- S9 TRUE
- S10 TRUE on lines; causal wording partly untraced
- S11 TRUE
- S12 TRUE; C1/C2/C3 label collision with round-100 claims
- S13 TRUE by counter check 9; label collision as S12

## Verdict

VERDICT C1 falsifies-wording The counter is green on seat-identity forgeries (FA/FB/FC above, `met=True` with SC01Recon/SC02Sources/SB01Entry in the attack lists) that contradict `.ufo/waves/round-99/w1-spec.json`. The narrowing sentence is the claim headline's "agrees with the committed round-99 wave evidence on nine enumerated checks"; the nine checks grade fractions, seat and dead counts, pointer binding and r99-measured bytes, not the seat lists the correction asserts. Severity low: no wrong number, all pointers resolve, and the correction's assertions are true at M. No number-level falsification found (`falsifies-number` not triggered).

No verdict on C2; not assigned to this seat.

## Tooling
No tools installed. Used only `git`, `python3` (stdlib), and the lane's own counter (read-only).

## Cleanup
Scratch fixture removed (`shutil.rmtree`); scratch dir `/fast/scratch/hyaku/kama-r100/CR01Records/` removed after the write. No tracked lane file edited; no `git add/commit/stash/checkout` in the lane (fixture clone only).
