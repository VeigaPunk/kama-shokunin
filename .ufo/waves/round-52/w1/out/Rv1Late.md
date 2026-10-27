# Rv1Late — round-51 late-seat defect (D1/D2): timeline, count, and the missing reconciliation

Seat Rv1Late (revenger, leaf, round 52 wave w1). Lane `kama-shokunin` read-only; no lane file, no jj state,
no git index touched. All evidence is committed bytes re-read by command; nothing was run against the host's
llama install.

**VERDICT — the round-51 report was filed 77 s before the driver's `complete` with a seat count (`50 of 66`,
16 "still running") that no committed tree yields: at the commit the report cites there are 51 top-level seat
reports and 55 by the counting rule the wave's own X6Hygiene seat applied, 5 of the 16 named as running had already filed in that same
tree, and the family's recovery move (an appended erratum once the wave settled 17 min later) was never taken
— so the number is still wrong at fleet HEAD. Round-52's L1 prompt adds no gate; the only lever is the routed
D2 itself.**

## 1. Reconstructed timeline (times `-03:00`)

| Time | Event | Evidence |
|---|---|---|
| 10-26 23:50:04 → 23:57:36 | attempt 1 launched, L1 died in the orchestrator session exit; no lane writes | `.ufo/watchdog.log:1625,1628` |
| 10-27 00:16:24 | attempt 2 launched; prompt `646f4348` | `.ufo/watchdog.log:1635` |
| 00:46:01.304Z | wave `a2w1` dispatch created (66 seats) | `.ufo/waves/round-51/a2w1/out/Sen4Policy.md` (`dispatch_created_at`) |
| 00:46:10.903 / 00:49:47.588 | `a2w1.ready` / `a2w1.ready.dispatched` | `ls -l --time-style=full-iso` |
| 01:01:35 | integration `c5ec93d5` | lane log |
| **01:04:32** | seat X6Hygiene's counter: `landed=52/66`, 14 missing, **exit 1** — the only in-wave count receipt | `out/X6Hygiene/late-sample.txt` `### 4c` |
| 01:07:36 | post-wave fixes `be8169a6` | lane log |
| **01:09:47** | **`1ab1de39`: measured results + seat-output sweep — 51 top-level reports** | `git ls-tree` (`counts.txt` R1) |
| 01:10:06 | `b1d7b7ae` end census | lane log |
| **01:11:05** | **fleet `39877b17`: report lands, `50 of 66`, 16 running** | fleet `39877b17:.ufo/reports/round-51/kama.md:16` |
| 01:12:23 | driver `complete kama round=51` (+77 s); closure prompt `781824f8` | `.ufo/watchdog.log:1648` |
| 01:27:15 | closure spot-check `9c603f39` files D1/D2 | `corpus/lessons/round-51-verifier-spotcheck.md` |
| **01:28:32** | **salvage `9ff76b1f`: +`M1Ctr.md`, `M2Live.md`, `V3Review.md` → 54; +`a2w1-results.json`** | `git show --stat 9ff76b1f` |
| 02:05:19 | round-52 spec `34d82600`: still 54 top-level / 58 any-`.md` | `counts.txt` R1 |

WAVE-DONE never arrived for `a2w1`; the results record exists only because the orchestrator wrote it during the
salvage, after the closure had already published D1.

## 2. The count, three ways (the new detail D2's `51/66` does not carry)

Command (exit 0, `counts.txt` R1/R2):

```
git -C kama-shokunin ls-tree --name-only 1ab1de39 .ufo/waves/round-51/a2w1/out/ | grep -cE '\.md$'
→ 51                 # rule A: top-level <Seat>.md
<rule B pipeline, timeline.md §5.1>                                               → 55   # any .md in the seat dir
git -C kama-shokunin ls-tree ... 9ff76b1f ...                                     → 54 / 58
git -C kama-shokunin ls-tree ... 34d82600 ...                                     → 54 / 58
```

- The report's 16-name "still running" list is **exactly** `1ab1de39`'s 15 reportless seats **plus `V1Review`**,
  whose `V1Review.md` (11,579 B) is in that commit. X6Hygiene's 01:04:32 receipt lists `V1Review` missing, so
  the L1's count was taken in the (01:04:32, 01:09:47) window `[INFERENCE]` — the bounds are set-difference, not a
  timestamp (R5) — and never re-derived after the commit: **one seat
  arrived in between, and that single arrival is the whole 50-vs-51 difference.**
- Four of the sixteen (`K2Design`, `T4Quality`, `T6Skill`, `Sim1`) file inside their own dirs
  (`K2Design/design.md` "C2 design critique"; `T4Quality/criteria.md` "Criteria added — round 51";
  `T6Skill/skill.md` "Round-51 instrument registry"; `Sim1/Sim1.md`). All four are in `1ab1de39`. Under
  X6Hygiene's rule they had **filed**, so the report under-counts the wave by 5, not 1.
- `50` is reproducible at no commit. The wave shipped a counter (`out/X6Hygiene/count_reports.py`) that prints
  number *and* missing names together, so the two could not have drifted had it been cited.

Seat fate at the round-52 tip (`counts.txt` R1): 51 top-level in `1ab1de39` + 3 in the salvage + 4 dir-only = 58
seats with a deliverable; **8 with nothing** — `Sen1Exe`, `Rev2Arow`, `Sen3Ledger`, `L6Slice`, `T1Lesson`,
`X3R41`, `X5Census`, `X8Restore`. Four of those eight left substantial product without a report
(`Sen1Exe`: 4 battery JSONs + `proposed-exe-read-failure-fix.diff`; `Rev2Arow`: 11-case evidence tree +
`append-only-audit-patched.py`; `Sen3Ledger`: ~30 fixtures; `X5Census`: 8 census receipts). "No seat has been
reported dead" is therefore true only in the reporting sense.

## 3. What the record cannot answer — `a2w1-results.json`

`python3` census over the file (`counts.txt` R4): top keys `lane, round, wave, seats=66, results`; **all 66
entries have exactly `{name, agent, output, note}`** — no `id`, no `status`, though the prompt specifies "per
seat: name, agent, id, status, final output" (`.ufo/prompts/kama-round-52.md:231`, identical in the round-51
prompt at line 231). Eight `output` values are raw transcript (`<think>` blocks, mid-sentence):
`Sen1Exe J8OneClass Rev2Arow T1Lesson T4Quality X3R41 X5Census X8Restore`; a ninth (`Sen3Ledger`) begins "Now
move to documentation…". Consequence: a compliant L1 reading the file still cannot tell a settled seat from a
dead one, so the wave-status sentence is unfalsifiable from the record. Round 65 hit the same gap and said so in
its erratum (fleet `.ufo/reports/round-65/kumitate.md`), so this is a fleet-wide schema gap, not a kama defect —
but it is why the round-51 count had to come from the tree.

## 4. What procedure would have prevented it (commands taken from this round's bytes)

1. **Count over the evidence commit, after committing it** — rule A or rule B, with the rule stated
   (`timeline.md` §5.1; results in §2 above).
2. **Take the "still running" names from the same receipt as the number** — X6Hygiene's counter prints both;
   its 14-name list at 01:04:32 is falsifiable, the report's 16-name list is not.
3. **Never assert liveness without a receipt.** One existed (`late-sample.txt` §1c: M2Live's counter pid
   2609182 live at 01:04:27; §2b: 13 seat clones). Three seats (`M1Ctr`, `M2Live`, `V3Review`) did keep working
   19 min past the report — that part of D1 is real; thirteen of the sixteen were not working.
4. **If the budget forces early filing, file `N/66 at <commit> (cmd …, t=…)`** and keep the wave state in the
   honest-status line.
5. **Append an erratum when the wave settles; never rewrite.** Family practice exists
   (`round-37/kasegi.md` "WAVE-DONE addendum (appended after filing)"; `round-65/kumitate.md` "Erratum (appended
   after filing; supersedes …)"). Round-51's report has exactly one commit (`git log -- .ufo/reports/round-51/kama.md`
   → `39877b17` alone) and no erratum/addendum section (`git show 39877b17:… | grep -n 'Erratum\|addendum'` →
   exit 1), so the false number is still the report of record.

Recovery is therefore cheap and was available twice: at 01:12:23 (WAVE-DONE still absent, `complete` logged) and
at 01:28:32 (salvage proved three more reports). Neither was used; the closure wrote D1/D2 instead.

## 5. What the round-52 L1 instructions now do — and what they do not

Measured, not assumed: `diff <(git show 646f4348:.ufo/prompts/kama-round-51.md) .ufo/prompts/kama-round-52.md`
→ **76 diff lines, 40 changed lines, all substitutions** (51→52, `round-51`→`round-52`, `kama-r51`→`kama-r52`,
`round-50-verifier-spotcheck`→`round-51-verifier-spotcheck`, paths). Round-52 prompt sha256 `3290322c…`, 633 lines.

- **New and load-bearing:** §Inherited state (lines 452-455) now points at `corpus/lessons/round-51-verifier-spotcheck.md`
  and requires each disagreement or routed defect to become "a lesson-backed `QUALITY.md` criterion or fix, or
  say in the report why not". D1 and D2 are in that routed set, so the round-52 L1 is *obliged* to correct the
  number and land a criterion — this seat's `proposed-d2-closure.md` supplies both as paste-ready text (proposed
  `KQ94` plus the correction paragraph). That is compliance, not enforcement: the prompt names no command and no
  gate.
- **Unchanged:** the wave protocol (lines 231-234) still only says "Seat counts, dead seats and role mix come from
  results.json", and `results.json` cannot answer it (§3). `scripts/hyaku/inline.sh:176` still logs `complete`
  with no WAVE-DONE/results condition — round 51 was marked complete 77 s after a report that said WAVE-DONE had
  not arrived.
- **Consequence:** if this round's budget cuts the same way, the same defect recurs. Prevention rests on the L1
  filing a counted, commit-derived, receipted status line and appending rather than rewriting when `w1` settles
  (no `w1-results.json` at 02:18, 70 seats dispatched).

## 6. Confidence

- **High** (committed bytes; two rules agree on ordering): 50/51/55/54/58; the exact identity of the 16-name
  list with the commit's 15-reportless set + `V1Review`; the 77 s report→`complete`; the 17 min 27 s
  report→salvage; no erratum commit; the results.json key shape and the 8 transcript outputs.
- **Medium** (`[INFERENCE]`): the exact instant of the L1's count inside the (01:04:32, 01:09:47) window — the
  arithmetic is exact, the instantaneous liveness of named seats is not recoverable from committed bytes.
- **Not claimed:** that any seat was "dead" in the orchestrator's sense — `results.json` has no status field, so
  it is unevidenced either way; what is evidenced is 8 seats with no report, 4 of them with no bytes.

Scratch removed; no tool installed; no llama-server started; no subagents. Proof file: `counts.txt` (same
directory) — R1 seat counts per commit, R2 the report sentence, R3 X6Hygiene's counter receipt, R4 the
results.json census, R5 the set identity of the 16-name list and the count window.

Paths written:
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/Rv1Late.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/Rv1Late/timeline.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/Rv1Late/counts.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/Rv1Late/proposed-d2-closure.md`
