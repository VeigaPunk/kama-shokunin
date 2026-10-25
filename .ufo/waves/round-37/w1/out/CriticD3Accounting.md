# Critic — where the D3 correction must live (kama round 37, w1)

role: critic (leaf). Session wrote only this file. Read-only over the lane and fleet repos; no
git/jj mutation, no edits to any other path, no counter executed for scoring (only its pure
functions imported and given candidate rows).

Sources read this seat:
- `corpus/lessons/round-36-verifier-spotcheck.md` §1 (line 47), §6 item 3 (lines 184–187).
- `.ufo/waves/round-36/w3/out/seat-exit-codes.json` (32 entries).
- `.ufo/waves/round-36/w3/out/ScribeLog/seat.log`, `.ufo/waves/round-36/w3/out/ScribeLog.md`,
  `.ufo/waves/round-36/w3/out/RevQ206/seat.log`, `.ufo/waves/round-36/w3/out/RevQ206.md`,
  `…/RevQ206/{prompt.txt,fetch_meta.txt,headers.txt,page.html}`.
- `.ufo/waves/round-36/w3/dispatch-outcome.log`, `.ufo/waves/round-36/w3/spec.json`.
- `/home/vgpnk/Projects/shokunin/.ufo/reports/round-36/kama.md` (lines 8, 176, 249–271).
- `.ufo/prompts/kama-round-37.md` §4 and the host-mechanics clause at lines 216, 229.
- `tools/round37-statement-audit.py` (`forbidden_in` 84–100, `holds` 137–149, blobs 30–31).

## 0. Answer in two lines

The round-37 fleet report (`.ufo/reports/round-37/kama.md`) must name **both seats with their role,
`rc=1`, and the verbatim last-error sentence** for each, and must carry the **three-class wave-3
split (24 / 6 / 2 = 32)** with the corrected round total (**55**, not 53).
A lesson-only accounting is **not sufficient** — and a complete accounting is *impossible* in the
lesson row, because the frozen C1 counter scores any row containing `rc=0` or `rc=143` as a false
correction. Both artifacts are required; neither substitutes for the other.

## 1. What the report must name (minimum sufficient set)

Routing text, verbatim, `round-36-verifier-spotcheck.md:187`: *"Name them, with their last error
text, in the lane's next report."* The round-37 report contract repeats the obligation
independently (`kama-round-37.md:216` "Record the round shape, each wave's seat count, role mix and
dead seats, any residual call, and the round total in the report"; `:229` "Report every seat that
dies, with its last error text; a dead seat stays dead in the evidence").

Required content, as tokens a reviewer can grep:

| # | token / fact | value re-derived here |
|---|---|---|
| 1 | `ScribeLog` | seat, role `scribe`, `rc=1`, `timed_out: false`, `stdout_persisted: true` |
| 2 | `RevQ206` | seat, role `reviewer`, `rc=1`, `timed_out: false`, `stdout_persisted: true` |
| 3 | `rc=1` | exactly 2 of 32 seats (census below) |
| 4 | last error text | `error: failed to run prompt: provider.rate_limit: 429 Rate limit reached for requests`, then `See log: /home/vgpnk/.kimi-code/logs/kimi-code.log` — identical in both logs; it is the **whole** of `ScribeLog.md` (156 B, byte-identical to `ScribeLog/seat.log`) |
| 5 | the split | 24 exited 0, 6 killed at the 900 s bound, 2 rate-limited → 8 dead, 32 accounted |
| 6 | corrected total | round-36 dead seats `53` → `55` (report:8 and the `Waves` prose both carry 53; 18+29+6) |
| 7 | causal correction | w3's deaths are **not** all bound kills. The report (`report:266-269`) explains w3's 6 deaths as the 480 s bound being "too short for the working route" and presents the 900 s bound as the fix; the 2 `rc=1` seats falsify that as a complete account — no bound length fixes a provider rate limit |
| 8 | provenance of `RevQ206` | `RevQ206.md` is **not** a report: 4247 B, `cmp -s RevQ206.md RevQ206/seat.log` exits 0, i.e. byte-identical transcript ending in the 429 block, **no verdict** |
| 9 | counter semantics | `report_exists: true` (JSON, both seats) and `dispatch-outcome.log`'s `settled seats=32 reports=32 timed_out=6` count **files**, not seat-written verdicts |
| 10 | evidence pointers | `.ufo/waves/round-36/w3/out/seat-exit-codes.json`, `…/ScribeLog/seat.log`, `…/RevQ206/seat.log`, `…/RevQ206/{fetch_meta.txt,headers.txt,page.html}`, `…/w3/dispatch-outcome.log` — all **tracked** at `6a4afdfe` (`git cat-file -e <tip>:<p>` exits 0 for every one) |

Paste-ready paragraph for **Work performed** (or a `## Waves` block; the contract allows extra
sections and requires the six named ones in order):

> Dead-seat accounting carried from round 36 (R36-D3). `w3` had 32 seats: 24 exited 0, 6 were
> killed at the 900 s seat bound (`rc=143`: `CritC1Sound`, `MutLessonRow`, `MutRowPipe`,
> `ExecCounters`, `ScribeQual`, `SentFinal`), and 2 exited `rc=1` on a provider rate limit — both
> omitted from the round-36 wave table, which accounted for 30 of 32 and reported the round total
> as 53 dead seats (it is 55). The two `rc=1` seats are `ScribeLog` (scribe) and `RevQ206`
> (reviewer); both ended with the identical last error text `error: failed to run prompt:
> provider.rate_limit: 429 Rate limit reached for requests` / `See log:
> /home/vgpnk/.kimi-code/logs/kimi-code.log`, `timed_out: false`. That block is the whole of
> `ScribeLog.md` (156 B); in `RevQ206.md` (4247 B) it closes a transcript that is byte-identical to
> `RevQ206/seat.log`, so neither file is a seat-written report — `report_exists: true` in
> `seat-exit-codes.json` and `reports=32` in `dispatch-outcome.log` count files, not verdicts.
> `RevQ206` did fetch its target before dying (`fetch_meta.txt` `final_status=200 … bytes=40874`,
> `headers.txt` `HTTP/2 200`, `page.html` 40874 B) but wrote no verdict, so the round-36 S206
> "present, hand-checked" reading (`report:176`) rests on those tracked artifacts, not on a seat
> report. Evidence: `.ufo/waves/round-36/w3/out/seat-exit-codes.json`,
> `.ufo/waves/round-36/w3/out/ScribeLog/seat.log`, `.ufo/waves/round-36/w3/out/RevQ206/seat.log`,
> `.ufo/waves/round-36/w3/out/RevQ206/{fetch_meta.txt,headers.txt,page.html}`,
> `.ufo/waves/round-36/w3/dispatch-outcome.log`.

Items 8–10 are not decoration: item 8 is the sentence the spotcheck itself got wrong (§2 finding
C2), and items 9–10 are what make the correction falsifiable rather than a restatement.

## 2. Is `corpus/lessons/round-37.md` sufficient? No — three independent reasons

**R1 — the instruction names the report.** `round-36-verifier-spotcheck.md:187` is an imperative
with one destination: "the lane's next report". `corpus/lessons/round-37.md` is the lesson, a
different artifact (`kama-round-37.md` §2b.3 is the only consumer of the lesson, and it asks for a
*mined mistake* row, not for routed-defect accounting). The round contract's report clause
(`:216`, `:229`) is the second, independent authority for the same content. A lesson row does not
satisfy either.

**R2 — the C1 counter cannot see the report, so "met True" is not "routed".** The D3 arm
(`tools/round37-statement-audit.py:137-149`) reads `EXITCODES_PATH` and the two `SEATLOGS` and then
only the lesson text; the fleet report enters the counter solely as the pinned **r36** blob
(`REPORT_BLOB`, line 31). A lesson row alone can turn the counter green while the routed
instruction stays unmet. Verified by importing the counter's pure functions with candidate rows:

```
row: "| R36-D3 | ScribeLog RevQ206 429; the two rc=1 seats raise round-36 dead seats 53 -> 55;
      the report carries the split |"
forbidden_in -> None    holds -> True          # C1 arm satisfied, report untouched
```

The frozen predicate is lesson-scoped *by construction* ("...iff `corpus/lessons/round-37.md`
contains a correction row naming its id..."). So: the predicate measures the lesson; the routed
instruction measures the report. Passing C1 proves nothing about D3's own wording.

**R3 — the lesson row is *forbidden* to hold the accounting.** `forbidden_in("R36-D3", …)` returns
a violation when the row contains `rc=0` **or** `rc=143` (line 95–96), and `score()` counts that as
`false_corrections += 1`, which forces `met False` (lines 168–176). Measured against the real
frozen facts:

```
"| R36-D3 | ScribeLog RevQ206 429; six rc=143 seats |"   forbidden='rc=143' holds=True
"| R36-D3 | ScribeLog RevQ206 429; table 24 rc=0 |"      forbidden='rc=0'   holds=True
"| R36-D3 | ScribeLog RevQ206 429; the two rc=1 seats raise round-36 dead seats 53 -> 55 |"
                                                          forbidden=None      holds=True
```

So the *correct* fact content — a three-class split — is a scored defect in the lesson. The lesson
row can carry only: the two ids, `rc=1`, `429`, and a pointer to the report. A row that omits
`rc=143` cannot state the split; therefore the split has exactly one legal home: the report.

Consequence for governance: **do not** treat "C1 met True" as evidence D3 is closed, and do not let
a reviewer sign D3 off against the counter alone. The check for D3 is `grep` over the round-37
fleet report for tokens 1–6 of §1, recorded as a report-conformance item.

## 3. Counterexamples against the proposed approach

**C1 — "name them + last error text" alone still lets the table stay wrong.** The defect is a
32-seat reconciliation, not a missing footnote. If the round-37 report reprints the round-36 table
(`report:259`, "`32 | 24 | 6 (killed at the 900 s bound)`") or the `53 dead` total (`report:8`),
the omission survives verbatim inside the round that claims to correct it. The minimum is a table
whose dead column reads 8 **and** the split; a prose naming of two seats next to an unchanged
`6`-dead row is internally contradictory.

**C2 — the spotcheck's own D3 wording imports a false provenance claim.** `:185-186` says
`RevQ206` "had already fetched the S206 page and *shipped a 4247-byte report*". Measured:
`RevQ206.md` is byte-identical to `RevQ206/seat.log` (`cmp -s` exit 0, both 4247 B) and contains a
transcript, the fetch-meta line, and the 429 block — no verdict, no `## Findings`, nothing a
reviewer could score. Copying that sentence into the report contradicts the round-36 report's own
rule that "no killed seat is credited as a finished one" (`report:339-341`). The report must say
**transcript**, and must not let `report_exists: true` stand as "produced a report".

**C3 — the fetch happened, the verdict did not, and the report claims otherwise.** `report:176`
asserts "**S206 present, not appended** … hand-checked this round with direct fetches". The only
seat assigned S206 is `RevQ206` (`w3/spec.json:122`), and it exited `rc=1` before writing a verdict.
The claim is still *supportable* — `RevQ206/page.html` (40874 B, tracked) contains
`对于vLLM/SGLang` ×1, `模型列表接口` ×2, `EAS_ENDPOINT` ×14 — but only from the seat's artifacts, both
of which the round-36 report fails to cite. If round 37 restates the S206 verdict, it must
re-point to `RevQ206/{page.html,headers.txt,fetch_meta.txt}` or withdraw it. Secondary: the
lesson's "verbatim" S206 quote (`round-36.md:53`) is a rendered-text reconstruction — the page
carries `对于vLLM/SGLang，可通过模型列表接口<code …>&lt;EAS_ENDPOINT&gt;/v1/models</code>获取。`, i.e. no
space before the inline code and HTML-escaped angle brackets, so a byte-grep for the quoted string
returns 0. Same class as the S329 literal-concatenation anchor the round-36 lesson already records;
a recheck script must anchor, not grep the joined form.

**C4 — the r36 artifacts are frozen, so "put it in the report" means round 37's report only.**
`LESSON_BLOB`/`REPORT_BLOB` (lines 30–31) equal the current blobs: lane
`6a4afdfe:corpus/lessons/round-36.md` = `6fb1ec15…`, fleet `HEAD:.ufo/reports/round-36/kama.md` =
`8b7408e6…`. Editing either in place — the obvious "fix the account where it is wrong" move —
sets `lesson_unchanged`/`report_unchanged` to 0 and forces `met False`. D3 is append-only in round-37
artifacts; the erratum style is the same one D1/D2 already require.

**C5 — the routed source is itself uncommitted.** `corpus/lessons/round-36-verifier-spotcheck.md` is
untracked: `git status --porcelain` → `??`, `git cat-file -e HEAD:<path>` fails, no history. A
report that cites the routed defect by file:line alone has an unresolvable pointer if the lane is
committed without it. Every D3 pointer in the report must therefore resolve to a tracked path
(§1 item 10); citing the spotcheck is fine as attribution, never as evidence.

**C6 (boundary, not a defect)** — the two `rc=1` seats do not change the attack-role count or the
role mix: `reviewer 17` and `scribe 2` already include them, so §1's split changes only the dead
column and the total. Do not "correct" `report:259`'s role mix.

## 4. Impacted axes

- **calibration** — the axis C1 measures, and the only axis D3 touches. D3 sits inside claim C1
  (7 → 7); the lesson row is necessary for the counter, the report is necessary for the routing.
  Neither quadrant of this is a score move: the claim is "routed statements corrected", so a
  report-less D3 leaves the claim's own admission resting on a proxy.
- **quality** — at risk if the report copies C2/C3's false provenance ("shipped a report"),
  reproducing the `false-grounded-reason` class the round mined. Clean if §1 items 8–10 land.
- **discernment** — untouched; the 32-seat reconciliation is arithmetic against a committed JSON,
  not a taste call. No `unprovable` ruling needed.
- Not touched: operability, freshness, depth, adjacency.

## 5. Smallest safe correction

1. **Report** (`.ufo/reports/round-37/kama.md`, fleet): insert the §1 paragraph and, if a wave table
   is printed, one row for the carried round-36 w3 shape with dead = 8 and the split. No edit to
   `.ufo/reports/round-36/kama.md` (C4). Statement of the corrected total 55 belongs here, because
   the round-36 line cannot be edited and the lesson row must not carry the split.
2. **Lesson** (`corpus/lessons/round-37.md`): exactly one line, containing the literal `R36-D3:`,
   worded to satisfy the counter without the forbidden tokens — validated against the real frozen
   facts above:

   ```
   | R36-D3 | `ScribeLog` (scribe) and `RevQ206` (reviewer) both exited rc=1 on `provider.rate_limit: 429`; w3 was 24 finished / 8 dead, so the round-36 total of 53 dead seats is 55. Full three-class split and both error blocks: round-37 report, Waves |
   ```

   Keep it single-line (the counter matches per line and the **last** line containing the id wins)
   and keep the lesson free of a second `R36-D3:` mention.
3. **Do not** state the split in the lesson — `rc=0`/`rc=143` on that line flips C1 to
   `false_corrections 1, met False` (measured, §2 R3).
4. **Reviewer check for D3** (the counter cannot do it): grep the round-37 report for `ScribeLog`,
   `RevQ206`, `rc=1`, `provider.rate_limit: 429 Rate limit reached for requests`, and confirm the
   w3 dead column reads 8 while the round total reads 55. Record the result as a report-conformance
   line, not as a claim verdict.
5. If neither the S206 verdict nor the 53 total is restated in round 37, items 6 and C3 become
   optional — the mandatory core is §1 items 1–5 and 8–10.

## 6. Residual uncertainty

- Whether the lane's round-37 report will restate the round-36 S206 verdict or the 53 total; if it
  does not, C3 and §1 item 6 degrade from required to advisory. The seat/rc/error-text core does
  not degrade: `kama-round-37.md:216`/`:229` require dead-seat accounting in every round report.
- `RevQ206/prompt.txt` shows the spec's own trailer typo (`Report: .vof/waves/...`,
  `w3/spec.json:122`) against the dispatcher's appended `.ufo/...` trailer; the seat spent tokens on
  the discrepancy. Not part of D3's routing, but it is the second-order candidate for the round's
  mined mistake if the wave-3 seat dies again on a path dispute.
