# S8Sample1 — KQ65 hand-read claim-outcome sample (round-46 w1, calibration)

**Verdict: sample complete — 125 hand-labeled claim-outcome rows for rounds 10–23 (59 self / 66 outside), every row's text re-read byte-exact from `git show <rev>:<path>` at the cited revision (125/125, 0 mismatches), and the labels agree 37/37 on every overlapping row of the committed `registry/claim-outcome-ledger.tsv`. No claim-outcome reader was written, run, or invoked.**

## 1. What was sampled

Assigned inputs, all read-only: fleet reports `.ufo/reports/round-N/kama.md` for N=10–21; lane closures `corpus/lessons/round-N-verifier-spotcheck.md` for N=10–19; the kama closure entries in fleet `MANIFEST.json` for N=20–23.

| Source class | Path pattern | Revision cited in the sample | Lines |
|---|---|---|---|
| Fleet report (self side) | `.ufo/reports/round-N/kama.md` | `9b676be886e1e2a428fa81321a05a16363ca68ac` (fleet HEAD at read time) | 10–21 |
| Lane closure (outside side) | `corpus/lessons/round-N-verifier-spotcheck.md` | `4a2a4d55d09dfacf83dc62d1b3fddae5f6d2a050` | 10–19 |
| Fleet manifest closure (outside) | `MANIFEST.json` | `9b676be886e1e2a428fa81321a05a16363ca68ac` (26,385 lines) | 20–23 |

Evidence for the 20/21 fallback to `MANIFEST.json` (the lane spotcheck files genuinely do not exist at the frozen lane rev):

```console
$ git -C /home/vgpnk/Projects/shokunin/kama-shokunin show 4a2a4d55...:corpus/lessons/round-20-verifier-spotcheck.md
fatal: path 'corpus/lessons/round-20-verifier-spotcheck.md' does not exist in '4a2a4d55...'
$ echo $?
128
```
(same for round-21; the loop printed `round-20 spotcheck exit=128`, `round-21 spotcheck exit=128`.)

Provenance note: the fleet repo moved under the seat. `git -C /home/vgpnk/Projects/shokunin rev-parse HEAD` returned `9b676be8…` at first read, `cbc532b1508bda29db1de40130593f0658db9a32` later, `25e118f8b2e89fb77fb38c21ea3c6e85a457d705` at the end. All sample rows are pinned to `9b676be8…`, which still resolves and is an ancestor of current HEAD (`merge-base --is-ancestor` exit 0). Line numbers quoted below are therefore valid only at that rev.

## 2. Inclusion rule (what makes a line a claim-outcome line)

A line is in the sample when it satisfies at least one of:

- **I1 — verdict**: it assigns an outcome word (`improved` / `unchanged` / `harmed` / `met` / `refuted` / `verified` / `no axis harm`) to a claim declared in that round, either by claim id (`C1`, `C2`, `C3`) or, in a per-claim verdict block/table, by the claim's axis name.
- **I2 — claim measurement**: it is the row/line of that round's claim measurement (before→after count, exit transition, absent→present) for the instrument the claim rests on.
- **I3 — manifest field**: for rounds 20–23 the JSON field that carries the claim/axis verdict, the claim-scoped recheck, or the closure note naming a claim outcome.

Excluded, and listed in §5: claim declarations without an outcome, "landed changes" bullets, wave/seat accounting, evidence pointers, per-control detail, harness-wide exit tallies, trend verdicts (expansion/quality/discernment), and SHONEN notes.

Conventions used in `sample.tsv`:

- `side=self` = the lane's own report; `side=outside` = the non-author closure (lane spotcheck or fleet manifest entry).
- `claim` is the declared claim id. A single line that gives *one shared* outcome to several claims is one row with a combined token (`C1+C2`, `C1+C3`). A JSON field that gives *different* outcomes per claim is split into one row per claim at the same line (round 23, line 12065).
- Rounds 22 and 23 manifest entries carry no per-claim id for the axis verdicts (22 has a `claims` object with `C1` only; 23 has none), so those two claims are recorded by axis name (`operability`).
- `line` is the first physical line of the sentence/bullet that carries the outcome. `text` is that physical line verbatim; where the outcome numbers continue on the next line this is recorded in §5 (anchor drift).
- `path` is repo-relative; `rev` is the full 40-hex commit the text was read at. Repo is implied: `.ufo/…` and `MANIFEST.json` are fleet, `corpus/…` is the lane.

Label distribution (from `sample.tsv`):

| Dimension | Counts |
|---|---|
| Rows | 125 (header + 125 in a 126-line file) |
| Rounds | 10,11,12,13,14,15,16,17,18,19,20,21,22,23 |
| Side | self 59, outside 66 |
| Outcome | met 119, not-met 5, partial 1 |
| Phrasing class | table-row 44, measurement-only 26, outcome-word 18, manifest-field 18, multi-claim-line 14, other 3, qualified-met-not-admitted 2 |
| Claim token | C1 74, C2 25, C1+C2 16, C3 4, C1+C3 3, operability 3 |

Note on `outcome`: the assignment says a claim is *met* (or not) — it is not the axis-movement field. Kama's rounds are almost all "score held" rounds (7→7, 8→8), so `met` here means "the claim as declared was supported at its declared scope", including the `delta 0` form; it never means "score improved". `partial` is used once (round-14 closure: R1 duplicate-rejection generality "not admitted" while C1's fixed result stands) and `not-met` five times (r19 declared 7→8 refuted ×2; r23 operability harmed ×3).

## 3. Verification (what was actually run)

Every row was re-read from git at its cited rev and compared against the `text` column:

```console
$ python3 - <<'EOF'
# for each row: git -C <repo> show <rev>:<path>, compare line N (stripped) with text
EOF
rows 125 mismatches 0
```

Exit 0. The retained assembler (`sample-assemble.py`) does the same thing with an assertion per row and exits non-zero on any anchor mismatch:

```console
$ python3 .ufo/waves/round-46/w1/out/S8Sample1/sample-assemble.py .ufo/waves/round-46/w1/out/S8Sample1/sample.tsv
rows 125
$ echo $?
0
$ sha256sum sample.tsv
6e7b1efb55d0ee8581d86940a713c6340cb3290649919716d97665ff97a523b4  sample.tsv
```

The assembler contains **no classification logic**: it holds the hand-assigned table and joins it to verbatim bytes; it fails closed if a line is where the table says it is not.

Cross-check against the committed ledger `registry/claim-outcome-ledger.tsv` (127 lines, rounds 10–44, last touched by lane commit `21945c6125c2fae531be94d7652ee058c68e5f83`, "round-45: C2 claim-outcome ledger"):

```console
$ python3 <overlap script>   # match on (round, side, path, line), claim id or token contains ledger claim
ledger 10-23 rows 44
matched 37 agree 37 disagree 0
unmatched ledger rows: [('10','C1','outside',round-10-verifier-spotcheck,'-','absent'),
                        ('16','C1','self',round-16,90,'met'), ('16','C2','self',round-16,103,'met'),
                        ('17','C1','self',round-17,65,'met'), ('17','C2','self',round-17,70,'met'),
                        ('22','C1','self',round-22,5,'met'), ('23','C1','self',round-23,74,'met')]
```

The 7 unmatched rows are explained in §5 (anchor drift; one rule conflict; rounds 22–23 fleet reports are outside this seat's assigned range 10–21). Outcome agreement on the 37 overlapping pairs is 37/37, at different revs than the ledger used (ledger round-10 revs: fleet `6105c587…`, lane `6b8ccfb3…`).

## 4. Findings

### F1 — Defect (pre-existing, already dispositioned): a full hash in the round-20 report is spliced and resolves nowhere

- File/line: `.ufo/reports/round-20/kama.md:7` at fleet `9b676be8…` — "…original measurement at `0957ce619789d13d894ef21bc863486bcb35b56c`".
- Command showing it:
  ```console
  $ git -C /home/vgpnk/Projects/shokunin/kama-shokunin cat-file -e 0957ce619789d13d894ef21bc863486bcb35b56c^{commit}
  fatal: Not a valid object name 0957ce619789d13d894ef21bc863486bcb35b56c^{commit}
  $ echo $?
  128
  $ git -C /home/vgpnk/Projects/shokunin/kama-shokunin cat-file -e 0957ce619789d13bb5779606078fa1498114d2c7^{commit}; echo $?
  0
  ```
- Already recorded, verbatim, at `registry/hexrun-ledger.tsv:45` and `registry/report-landing-errata.tsv:3` (first 15 hex of the measured tree spliced with the last 25 hex of `33a6777866d0f63d894ef21bc863486bcb35b56c`).
- Proposed fix: none in place — the report is frozen and the lane contract is append-only; the correction row already exists. For the future reader the actionable mitigation is **resolve every 40-hex token against the cited repository before scoring a line**, never treat a textual full hash as a resolved object. My sample keeps the line's failing hash verbatim (it is not an outcome row, so it is not in `sample.tsv`; it is reported here).

### F2 — Claim ids are round-local: round 18 swaps them against rounds 16/17/19

- `.ufo/reports/round-18/kama.md:7` declares "**C1 — operability, 8 → 8**" and `:12` "**C2 — calibration, 7 → 7**"; `corpus/lessons/round-18-verifier-spotcheck.md:44-45` repeats "C1 operability 8→8" / "C2 calibration 7→7".
- Rounds 16, 17 and 19 declare the opposite binding (`.ufo/reports/round-16/kama.md:13` C1 calibration / `:17` C2 operability; `round-17:11,13`; `round-19:7,16`), and round 10 declares `C1` freshness plus `C3` coverage with **no C2** (`round-10:8-9`); round 15 says explicitly "No second claim" (`round-15:5`).
- Consequence for the future reader: a claim id is not a stable axis key. Any scoring that maps `C1=calibration` globally will mislabel rounds 10, 18 and any round with a different claim count. My sample therefore carries the claim id **and** the axis context in the row (`16/17/19` C1=calibration; `18` C1=operability).

### F3 — Round 17's self report states no outcome word for either claim

- `.ufo/reports/round-17/kama.md:63` (C1) and `:69` (C2) give measurements only (`3 of 8` → `0 of 8`; `6 accepted-bad` → `0`; 11/11). The words "improved" appear only in trend bullets (`:97`, quality), never for C1/C2. The only per-claim verdict words for round 17 are outside: `corpus/lessons/round-17-verifier-spotcheck.md:11` ("C1 … improved, bounded") and `:16` ("C2 … improved").
- Consequence: a reader keyed on verdict words returns "no outcome" for the self side of round 17. The sample records these three lines as `measurement-only` / `met`, and the round's no-harm line `:75` as `multi-claim-line`.

### F4 — Outside closures state claim outcomes in axis names, not claim ids (rule conflict, not an error)

- `corpus/lessons/round-10-verifier-spotcheck.md:17` reads "Per-axis: freshness improved (… score 7→8), coverage improved (… score 8→9 …)" — no `C1`/`C3` token. Round-10's claim binding is `.ufo/reports/round-10/kama.md:8-9` (C1 = freshness, C3 = coverage), so under I1 this is C1's and C3's outside outcome.
- The committed ledger takes the opposite reading: `registry/claim-outcome-ledger.tsv:3` records round-10 `C1 / outside / absent / line -` with the note "the round-10 closure … names only C3; no line gives C1 an outcome", while its `:5` records `C3 / outside / met / line 17` for the same line.
- Both readings are internally consistent under different rules (id-token rule vs axis-binding rule). The sample uses the axis-binding rule and labels line 17 `C1+C3 / met`. A future reader must declare which rule it implements; otherwise this row alone will disagree with the round-45 ledger. I did not change the ledger.

### F5 — Anchor drift on wrapped bullets (self vs ledger line numbers)

The outcome numbers of several self bullets sit on the *second* physical line, so "the line" is ambiguous:

| Round/claim | Sample anchor (bullet start) | Ledger anchor (numbers line) |
|---|---|---|
| 16 C1 | `.ufo/reports/round-16/kama.md:88` | `:90` (`55 pass / 17 fail … 72 / 0 …`) |
| 16 C2 | `:99` | `:103` (`10/10 checks`) |
| 17 C1 | `:63` | `:65` (`3 of 8 … → 0 of 8 … 7/8 → 10/10`) |
| 17 C2 | `:69` | `:70` (`6 accepted-bad (+1 inconclusive) → 0 … 11/11`) |

Outcomes agree; only the anchor differs. A reader must pin its anchor convention (sentence start vs value line) or accept multi-line statements — and must not treat a non-anchor line as a second, independent outcome.

### F6 — "refuted" in round 19 is about the score aspiration, not the claim's measurement

- Self: `.ufo/reports/round-19/kama.md:11` ("The declared 7 → 8 was **refuted** … and the score is held at 7") beside `:7` ("C1 — calibration, 7 → 7 …") and the pair table `:84` (`found=0` exit 1 → `found=4 verified=4` exit 0).
- Outside: `corpus/lessons/round-19-verifier-spotcheck.md:62` ("declared 7 → 8, then refuted and held") beside `:74` ("The result is 0/4 → 4/4 verified") and `:136`.
- The sample labels `:11` and `:62` `not-met` (the declared numeric improvement) and `:74`/`:84` `met` (the claim's instrument). A reader that treats "refuted" as claim failure would contradict `:74`; one that treats `:74` as covering the score would contradict `:11`. These are two different objects in one round and must be separated by object, not by keyword.

### F7 — The manifest entries for rounds 22–23 do not carry the round's full claim set

- `MANIFEST.json:11355-11374` (round 22) has `claims` with `C1` only (`"axis": "calibration"`, `"verdict": "improved"`, `scalar_before/after` 7/7, components 0→18 refusals, 1→0 false citations); the operability claim has no entry. `MANIFEST.json:12027-12066` (round 23) has **no** `claims` key at all — only axis `verdicts` (`:12038` calibration improved, `:12039` operability harmed), `harm_ruling` (`:12062`) and `notes` (`:12065`, "REJECTED-HARMED despite verified bounded C1 …").
- Consequence: rounds 20–23 outcomes can only be bound to claim ids by reading the fleet report (out of range for this seat for 22–23) or by trusting the axis mapping. The sample records round-23 axis verdicts by axis name; see the `operability` claim tokens in `sample.tsv`.

### F8 — Provenance: the fleet repo moved during the seat

`rev-parse HEAD` on `/home/vgpnk/Projects/shokunin` returned `9b676be8…`, then `cbc532b1…`, then `25e118f8…`. The sample is pinned to the first; the rev still exists and is an ancestor of the last (`merge-base --is-ancestor` exit 0). Any later re-run of the line numbers must use the pinned rev, not `HEAD`.

## 5. Lines I could not label (boundary calls, recorded so the next reader is not surprised)

These were read and deliberately left out of `sample.tsv`; each is a rule boundary, not an unread line:

1. `.ufo/reports/round-10/kama.md:47` — no-harm table row; no claim id and no per-claim verdict.
2. `.ufo/reports/round-11/kama.md:225` — "Frontier advanced: K02 … now held": frontier, not claim-keyed (a C2-only reading is possible).
3. `.ufo/reports/round-12/kama.md:42-47`, `round-14:40-42`, `round-15:48,50,51` — per-control/mutant rows of the claim's instrument table; outcomes agree with the claim's own row but they are control detail.
4. `.ufo/reports/round-16/kama.md:13-19` and `round-17:11-17` — declarations that state the intended change, not an outcome. The declaration clauses inside `round-20:5` and `round-21:5` were excluded the same way, but those whole lines are in the sample because their trailing clause ("Both claims are supported …" / "Both are author-supported …") is the round's verdict.
5. `.ufo/reports/round-20/kama.md:28` and `round-21:8,10` — harness/recipe tallies ("21/21 declared exits", "28/28", "33/33"): recipe accounting; no claim verdict, although `:28` carries a C2 scope limit.
6. `corpus/lessons/round-11-verifier-spotcheck.md:204` — "none changes the two verified claim deltas": the two deltas are unnamed at that point; ambiguous referent.
7. `corpus/lessons/round-13-verifier-spotcheck.md:131` — SOURCES row/tier counts (32→33): coverage bookkeeping; round 13 declared only C1.
8. All `## Trend verdicts` bullets in every source (expansion/quality/discernment): trend axes, not claims — e.g. `round-10:91-93`, `round-11:240-254`, `round-12:106-108`.
9. `MANIFEST.json` round-22 `report_commit`/`commit`/`swarm`/`tools_installed` fields and round-23 `routed_checks` — conformance/accounting, no claim outcome.
10. Multi-line sentences: `.ufo/reports/round-19/kama.md:11-14` (refutation) and `:7-15` (declaration) — recorded at their first physical line only.

Unlabelable in the strict sense (no outcome content to label): none. Every line encountered that mentions a claim either carries an outcome (sampled) or falls in one of the ten boundary classes above.

## 6. Deliverables and hygiene

- No claim-outcome reader was written, executed, or invoked. The retained script is a label→byte joiner with per-row assertions and contains no classification.
- No lane file, index, jj state, frozen counter, preregistration, or control was modified; no commit, push, or fetch; no service action; no tool install or update.
- Scratch `/fast/scratch/hyaku/kama-r46/S8Sample1` was used only for source dumps and removed after `sample.tsv` was regenerated in place from git; no `/tmp` path is cited as evidence.

Absolute paths written:

- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/S8Sample1/sample.tsv
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/S8Sample1/sample-assemble.py
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/S8Sample1.md
