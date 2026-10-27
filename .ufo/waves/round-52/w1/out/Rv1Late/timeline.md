# Round-51 late-seat defect (closure D1/D2): reconstructed timeline and the count that drifted

Seat: Rv1Late (revenger, leaf). Round 52, wave w1.
Lane: `/home/vgpnk/Projects/shokunin/kama-shokunin` (read-only for this seat).
Fleet root: `/home/vgpnk/Projects/shokunin`.
All commands below were run read-only (`git ls-tree`, `git log`, `git show`, `python3` over committed bytes);
no lane file was written; the only writes are under `.ufo/waves/round-52/w1/out/Rv1Late/`.

**Verdict in one line.** The report of record was filed 77 s before the driver logged `complete`, with a
seat count (`50` in hand, `16` still running) that no committed tree supports; the count was correct under one
rule at one moment and was never re-derived against the bytes it cites, and the family's own recovery move
(an appended erratum when WAVE-DONE lands) was never taken — so the number is still wrong at fleet HEAD.

---

## 1. Evidence base

| # | Source | What it fixes |
|---|---|---|
| E1 | `.ufo/waves/round-51/a2w1/a2w1-results.json` (lane, committed `9ff76b1f`) | the orchestrator's post-hoc seat record: 66 entries |
| E2 | fleet `39877b17:.ufo/reports/round-51/kama.md` (the report of record) | the `50 of 66` / 16-running sentence (line 16) |
| E3 | lane `9ff76b1f` (salvage commit, 01:28:32) | which seat outputs were written after the report landed |
| E4 | `.ufo/waves/round-51/a2w1/out/X6Hygiene/late-sample.txt` (`### 4c. report count`) | the only in-wave seat-count receipt |
| E5 | `.ufo/watchdog.log:1625-1655` | launch / dead / relaunch / complete lines |
| E6 | `templates/round-prompt.md` §4, kama prompt §6 (lines 225-234) | the report contract and the WAVE-DONE protocol |
| E7 | `scripts/hyaku/inline.sh:176` | the driver's `complete` has no WAVE-DONE gate |

Receipts reproduced by this seat: `counts.txt` (same directory), sections R1-R4.

## 2. Timeline (all times `-03:00`, the lane's local clock)

| Time | Event | Evidence |
|---|---|---|
| 2026-10-26 23:50:04 | attempt 1 launch | E5:1625 |
| 23:57:36 | attempt 1 L1 dies in the orchestrator session exit (SIGHUP); no lane writes | E5:1628 |
| 2026-10-27 00:16:15 | watchdog: `lane-dead-no-report kama round=51` | E5:1628 |
| 00:16:23-24 | attempt 2 prompt committed (`646f4348`); launch | E5:1635 |
| 00:39:06 | build `b6bed925`; 00:41-00:46 build-fixes `73bf2a7a`, `138af25b` | lane log |
| 00:46:01.304Z | wave `a2w1` dispatch JSON created (66 seats) | quoted in `out/Sen4Policy.md`; `dispatch_created_at` |
| 00:46:10.903 | `a2w1.ready` written | `ls -l --time-style=full-iso` |
| 00:49:47.588 | `a2w1.ready.dispatched` (orchestrator took the wave) | idem |
| 01:01:35 | integration commit `c5ec93d5` | lane log |
| 01:04:27 | seat X6Hygiene's final sample — M2Live's C1 counter still running (pid 2609182), 13 seat clones on disk | `out/X6Hygiene/late-sample.txt` §1c, §2b |
| **01:04:32** | **X6Hygiene's counter: `landed=52/66`, 14 missing, exit 1** | `late-sample.txt` `### 4c`, E4 |
| 01:07:36 | post-wave fixes `be8169a6` (V2Review LOW-1, M5Digest) | lane log |
| **01:09:47** | **`1ab1de39` — measured results + the seat-output sweep: 80 `.md` files, 51 top-level seat reports** | `git show --name-only 1ab1de39`, `counts.txt` R1 |
| 01:10:06 | `b1d7b7ae` end census, misroot sweep | lane log |
| **01:11:05** | **fleet `39877b17` — the report lands: `50 of 66`, 16 named as running** | E2, E5:1648 (complete is later) |
| 01:12:23 | driver logs `complete kama round=51`; closure prompt `781824f8` dispatched | E5:1648; fleet log |
| 01:27:15 | closure spot-check committed (`9c603f39` in-lane) — writes D1 and D2 | `corpus/lessons/round-51-verifier-spotcheck.md` §1, §6 |
| **01:28:32** | **salvage `9ff76b1f`: +`M1Ctr.md`, `M2Live.md`, `V3Review.md` (54 reports) + `a2w1-results.json`** | E3 |
| 01:28:32 / 01:42:07 | round-52 freeze `8551ba7f` authored (same second as the salvage) / committed — still 54 top-level | `git log -1 --format='%ai %ci'` |
| 01:56:49 / 02:05:19 | round-52 wave spec `34d82600` (70 seats) authored / committed — still 54 top-level / 58 by-content | idem |
| 02:18 | round-52 wave `w1` running (70 seats); no `w1-results.json` yet | `ls .ufo/waves/round-52/` |

Gaps: report → driver `complete` **77 s** (report first); report → salvage **17 min 27 s**; driver `complete`
→ salvage **16 min 09 s**. WAVE-DONE was never sent for `a2w1`; `a2w1-results.json` exists only because the
orchestrator wrote it during the salvage, after the closure had already published D1.

## 3. Seat count at filing: three numbers, one tree

`counts.txt` R1 applies the two candidate rules to the exact commit the report cites:

| Commit | top-level `<Seat>.md` | any `.md` in the seat's dir |
|---|---|---|
| `1ab1de39` (cited by the report) | **51 / 66** (15 missing) | **55 / 66** (11 missing) |
| `b1d7b7ae` (tip at filing) | 51 / 66 | 55 / 66 |
| `9ff76b1f` (salvage) | 54 / 66 | 58 / 66 |
| `34d82600` (round-52 spec) | 54 / 66 | 58 / 66 |

- The report's sentence: `50 of 66 seat reports` in hand, 16 named still running (E2 line 16).
- The 16 names are **exactly** the commit's 15 reportless seats plus `V1Review`:
  `Sen1Exe M1Ctr M2Live V1Review K2Design V3Review Rev2Arow Sen3Ledger L6Slice T1Lesson T4Quality T6Skill X3R41 X5Census Sim1 X8Restore`.
- `V1Review.md` (11,579 B) is **in** `1ab1de39`. X6Hygiene's 01:04:32 receipt lists `V1Review` as missing, so it
  landed in the ~5 min window between the L1's count and the commit. **That single arrival is the difference
  between 50 and 51**: the count was taken before the commit and never re-derived after it.
- Four of the sixteen (`K2Design`, `T4Quality`, `T6Skill`, `Sim1`) never write `<Seat>.md`; their deliverable is
  inside the seat dir (`K2Design/design.md` — "C2 design critique"; `T4Quality/criteria.md` — "Criteria added —
  round 51"; `T6Skill/skill.md` — "Round-51 instrument registry"; `Sim1/Sim1.md` — verdict). All four are in
  `1ab1de39`. So by the wave's own counting rule (X6Hygiene's `count_reports.py`: top-level `.md`, else any
  `.md` under the seat dir) **55 seats had filed at the commit** — 5 more than the report claims in hand.
- The wave already had a count instrument and it disagreed with the report: `out/X6Hygiene/count_reports.py`
  (committed in the same tree, `exit 1` unless ≥ 60) printed `landed=52/66` at 01:04:32 with its own missing
  list. The report cites no receipt for its number.

### Fate of the 66 seats (committed bytes, `34d82600`)

| Class | n | Seats |
|---|---|---|
| top-level report in `1ab1de39` | 51 | (list in `counts.txt`) |
| added by the salvage | 3 | `M1Ctr`, `M2Live`, `V3Review` |
| deliverable only inside the seat dir, never `<Seat>.md` | 4 | `K2Design`, `T4Quality`, `T6Skill`, `Sim1` |
| **no report at all at round-52 tip** | **8** | `Sen1Exe`, `Rev2Arow`, `Sen3Ledger`, `L6Slice`, `T1Lesson`, `X3R41`, `X5Census`, `X8Restore` |
| total | 66 | |

Of the 8 reportless, four carry substantive product in the tree (`Sen1Exe`: 4 battery JSONs + a proposed
`proposed-exe-read-failure-fix.diff`; `Rev2Arow`: an 11-case A-row evidence tree + `append-only-audit-patched.py`;
`Sen3Ledger`: ~30 ledger fixtures; `X5Census`: 8 census receipts + `rowcounts.out`). Four (`L6Slice`,
`T1Lesson`, `X3R41`, `X8Restore`) have **no bytes at all**. So "no seat has been reported dead" is true only in
the sense that nobody reported them; seven of them had produced or were producing work.

## 4. What the record cannot answer, and why

`a2w1-results.json` (E1) has top-level keys `lane, round, wave, seats=66, results`, and **every one of the 66
entries has exactly the keys `name, agent, output, note`** (`counts.txt` R4). The prompt that specifies this
file requires "per seat: name, agent, **id**, **status**, final output" (E6, kama prompt line 231). Consequences:

- The file cannot distinguish a settled seat from a dead one. Round 65 hit the same gap and recorded it:
  "the file carries no per-seat status field, so this is not an `inline-dispatch-evidence` run"
  (fleet `.ufo/reports/round-65/kumitate.md`, Erratum). It is a fleet-wide schema gap, not a kama defect.
- 8 of the 66 `output` strings are **raw transcript, not results**: they contain `<think>` blocks and stop
  mid-thought (`Sen1Exe`, `Rev2Arow`, `T1Lesson`, `X3R41`, `X5Census`, `X8Restore`, `T4Quality`, `J8OneClass`).
  Another (`Sen3Ledger`) starts "Now move to documentation. Need the formal sources…". Four of these are seats
  with no report — the record presents a truncated monologue where the prompt promises a status.

So even a compliant L1 reading `results.json` would not learn that 8 seats filed nothing; the only trustworthy
signal in round 51 was the tree (`git ls-tree`), and the report did not use it after committing.

## 5. The procedure that would have prevented it

Each step is one command that existed at filing time.

1. **Count from the commit, after the commit.** The number in the report must be computed over the bytes it
   cites, not over a directory listing taken while composing. Both rules, run by this seat against the trees
   (outputs in `counts.txt` R1):
   ```sh
   # rule A — top-level <Seat>.md only
   git -C <lane> ls-tree --name-only <rev> .ufo/waves/round-51/a2w1/out/ | grep -cE '\.md$'
   # rule B — any .md under the seat's own dir (the wave's own count_reports.py rule)
   git -C <lane> ls-tree -r --name-only <rev> .ufo/waves/round-51/a2w1/out/ | sed 's#.*/out/##' \
     | awk -F/ '{ if ($0 ~ /\.md$/) { if (NF==1) print substr($1,1,length($1)-3); else print $1 } }' \
     | sort -u | comm -12 - <(jq -r '.items[].name' .ufo/waves/round-51/a2w1/spec.json | sort) | wc -l
   ```
   Measured: rule A `1ab1de39` → **51**, `9ff76b1f` → 54; rule B `1ab1de39` → **55**, `9ff76b1f` → 58,
   `34d82600` → 58. Either rule is defensible **if it is stated**; `50` is reproducible at no commit.
2. **State the rule.** "Report present" means top-level `<Seat>.md` *or* any `.md` under the seat dir — the wave's
   own `out/X6Hygiene/count_reports.py` already implements the second and is committed; cite its output
   (`late-sample.txt ### 4c`) or re-run it. It prints the missing names, so the "still running" list comes from
   the same receipt as the number, and the two cannot drift apart.
3. **Do not call a seat "running" without a liveness receipt.** Round 51 had one (`pgrep`/scratch/clone census at
   01:04:27, `late-sample.txt` §1c/§2b) and the report cites none. Three of the sixteen (`M1Ctr`, `M2Live`,
   `V3Review`) did keep writing for another 19 min, which is the part of D1 that is real; four of the sixteen had
   already filed.
4. **If the budget forces an early filing, file the number as of a named commit with its command and timestamp**,
   e.g. `51/66 top-level at 1ab1de39 (cmd …)`, and put the wave state in the "Honest status" line — never a naked
   integer that the commit can falsify.
5. **Append an erratum when WAVE-DONE or late output arrives; never rewrite.** This is established family
   practice: `round-37/kasegi.md` §"WAVE-DONE addendum (appended after filing)" and
   `round-65/kumitate.md` §"Erratum (appended after filing; supersedes …)". Round 51 took neither: the report has
   exactly one commit (`39877b17`, 01:11:05) and no erratum/addendum section, so the `50 of 66` sentence is still
   wrong at fleet HEAD ~55 min after the salvage proved otherwise. (A round-51 seat that rewrote its own
   committed report in place is D1's other half; the lane's round-52 build restored those bytes — `X7Regen.md`,
   late rewrite filed as `X7Regen.late-rewrite.md`. That fix covers the rewrite, not the count.)

## 6. What the round-52 L1 instructions actually do about it

Checked rather than assumed: `diff` of the dispatched round-51 prompt (`646f4348`) against the round-52 prompt
(`.ufo/prompts/kama-round-52.md`, sha256 `3290322c…`) is **76 diff lines, 40 changed lines, every one a
round-number / date / path substitution** (51→52, `round-51`→`round-52`, `kama-r51`→`kama-r52`,
`round-50-verifier-spotcheck`→`round-51-verifier-spotcheck`). No new completion gate, no new count rule, no
prohibition on filing early. Specifically:

- **Unchanged** (kama prompt lines 225-234): the orchestrator writes `<wave>-results.json` and messages
  `WAVE-DONE`; "Seat counts, dead seats and role mix come from results.json". Existed in round 51 verbatim.
- **Unchanged** (`scripts/hyaku/inline.sh:176`): the driver logs `complete` unconditionally — round 51 was marked
  complete 77 s after a report that said WAVE-DONE had not arrived. Nothing gates on results.json.
- **New, and the only structural lever**: §Inherited state (round-52 prompt lines 452-455) now points at
  `corpus/lessons/round-51-verifier-spotcheck.md` and requires "turn every disagreement or routed defect into a
  lesson-backed `QUALITY.md` criterion or fix, or say in the report why not". D1 and D2 are in that routed list,
  so the round-52 L1 is *obliged* to close the count defect (a superseding QUALITY row + the corrected number in
  the round-52 report) instead of repeating it. That is compliance, not enforcement: the prompt supplies no
  command, no commit-derived count, and no gate.
- The round-52 wave is already dispatched (70 seats, `w1.ready` at `.ufo/waves/round-52/`), and no
  `w1-results.json` exists at 02:18. If the request budget cuts this round the way it cut round 51, the same
  defect recurs unless the L1 follows step 1-5 above; nothing in the instructions blocks it.

**Assessment (`[INFERENCE]`, stated as such):** the defect class is "free-text status written before the evidence,
never reconciled to it". Round 51's own instrument (X6Hygiene) and the family's erratum practice both existed and
would have caught or repaired it within minutes. Round 52 routes the repair (D2 → superseding QUALITY row) but
adds no gate, so prevention still depends on the L1 doing a counted, commit-derived, receipted status line —
and on appending rather than rewriting when the wave finally settles.

## 7. Confidence

- **High** (committed bytes, and two independent rules agree on the ordering): the 50/51/55/54/58 numbers; the
  exact identity of the 16-name list with the commit's missing set + V1Review; the 77 s ordering between report
  and `complete`; the 17 min 27 s gap to the salvage; the absence of any erratum commit.
- **High**: the results.json schema gap (`id`/`status` absent on all 66) and the 8 raw-transcript outputs.
- **Medium**: *why* the L1's snapshot missed V1Review. The window is bounded (after X6Hygiene's 01:04:32 receipt,
  before the 01:09:47 commit) and the +1 arithmetic is exact; the momentary liveness of the 16 named seats is not
  recoverable from committed bytes. Marked `[INFERENCE]` where it is asserted.
- **Not claimed**: that any seat was "dead" in the orchestrator's sense. `results.json` has no status field, so
  "dead" is not evidenced either way; what is evidenced is that 8 seats filed no report and 4 of them left no
  bytes.
