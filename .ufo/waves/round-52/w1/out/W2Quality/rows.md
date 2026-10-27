# Round 52 — proposed `corpus/QUALITY.md` rows (seat W2Quality)

Verdict: **the ten remaining lesson-citation rows are drafted and ready to append; the four rows
this seat was asked to draft for (a) KQ86/KQ87 and (b)/(c) the round-52 criteria were already
landed in the lane's working tree by a concurrent integration while this seat was scanning, so for
those the deliverable is a review with five concrete defects and their fixes.**

State read: lane HEAD `34d8260051bbab8859485e8209fcf4be19dc9a2b`; `corpus/QUALITY.md` is
**modified in the working tree** (uncommitted) — `git diff --stat corpus/QUALITY.md` → `1 file
changed, 12 insertions(+)`. At the build `5dacf2c70f947ca6dc5fbbca6d45b8db5b0390c8` the file was
454 lines with 88 criteria rows `KQ1`–`KQ88` and `diff <(git show 5dacf2c7:corpus/QUALITY.md)
corpus/QUALITY.md` was empty; the working tree is now 466 lines and ends at `KQ93`.
Snapshots taken by this seat (so the review is reproducible against fixed bytes):
`.ufo/waves/round-52/w1/out/W2Quality/landed-round52-rows.txt`
(sha256 `95cb18167592a4f020a948da347980bd1afa238a232aaa4931c0453f32281432`) and
`.ufo/waves/round-52/w1/out/W2Quality/quality-worktree.diff`
(sha256 `88e3bd1e1957399e5066e07a8d35d09b4ba821a364327d9e43c75c4d3f80197d`).

Because those five rows are **uncommitted**, they can still be corrected in place; once committed,
`corpus/QUALITY.md` is A-corr and every correction is a new appended row. Both routes are spelled
out below.

Proposed append point for everything here: end of file (after the landed round-52 section), which
keeps the `## Restored lines (round 52)` fence bytes untouched — the C2 counter's lane leg reads
`corr_lost=0` at the build and appending does not change it.

Numbering: next free id. The working tree ends at `KQ93`, so the ten citation rows below are
KQ94–KQ103. If integration lands other rows first, renumber in landing order and keep every
`(supersedes KQnn…)` cell — the parenthetical, not the number, carries the supersession.

Evidence discipline: this seat ran **no** counter. The `met=True` lines quoted below are read from
the L1's receipts `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/measured/c1-build.out`
and `c2-build.out` at the build; they are the L1's observations, not this seat's.

---

## 1. Review of the rows already in the working tree (`corpus/QUALITY.md:456-466`)

Landed there, uncommitted: `KQ89 (supersedes KQ86)`, `KQ90 (supersedes KQ87)`,
`KQ91 (narrows KQ85)` — the C1 criterion, `KQ92` — the C2 criterion, and `KQ93` (producer/consumer
receipt fields, from seat V2Review). Row identity, supersession form and the `C1`/`C2`/`round-52.md`
anchors are right. Five defects:

**RV1 — `KQ89` and `KQ90` cite a section the lesson does not have.**
Both rows end `…; \`corpus/lessons/round-52.md\` Errata D7`.
`corpus/lessons/round-52.md` has exactly two headings:

```
$ grep -c '^## ' corpus/lessons/round-52.md
2
$ grep -n '^## ' corpus/lessons/round-52.md
9:## Claims
16:## Gate
```

There is no `## Errata` and no `D7` in that file; `D7` is **round-51's** closure item
(`corpus/lessons/round-51-verifier-spotcheck.md:117`, `:150`). Fix (apply to both last cells):

```diff
-…; `corpus/lessons/round-52.md` Errata D7
+…; `corpus/lessons/round-52.md` (this round's lesson); `corpus/lessons/round-51-verifier-spotcheck.md` D7
```

**RV2 — `KQ93` cites `corpus/lessons/round-52.md` Mistakes; that section does not exist either**
(same two-heading file). The defect it records is real and is filed at the seat report. Fix:

```diff
-| C1; `corpus/lessons/round-52.md` Mistakes |
+| C1; `.ufo/waves/round-52/w1/out/V2Review.md:5,9` (`LD_LIBRARY_PATH` added to `child_env`, recorded in `child_env_keys`, rejected by the unchanged `tests/llamacpp-live/check-receipt.py`); `corpus/lessons/round-52.md` C1 |
```

(or, at integration, append a `## Mistakes` section to `corpus/lessons/round-52.md` — the file is
A-corr, so appending is allowed — and keep the citation as it stands).

**RV3 — `KQ91` drops two legs the C1 counter actually checks and all but two preregistered limits.**
The counter requires the opened image's bytes to hash to the frozen server digest and the recorded
`seals` to be compared with its own `F_GET_SEALS`; the landed admit cell requires only dev and inode
to be recorded, and names no digest. It also carries no `Check:` command, unlike the round-48/49
rows (`corpus/QUALITY.md:411-426`), and its limits stop at "libraries load by path" and the host
memfd. Counter contract: `tools/round52-replay-memfd-audit.py:36-45` ("its bytes hash to the frozen
server digest"; "`server_exe` has … the same dev and inode, and seals including those four"), and the
build receipt's own detail lines say `seals 15 is a sealed memfd with the frozen digest, recorded in
server_exe and own_server` (`measured/c1-build.out:6,8,10`). Proposed replacement line for `:464`
(pre-commit) — if the row is already committed, file this as a new row
`KQ9x (supersedes KQ91)` instead:

```markdown
| KQ91 (narrows KQ85; round-52 C1) | A replay's server is the replay's own only when its running image, opened by the counter itself through `/proc/<pid>/exe` (S499) and never read as a path, is an anonymous memfd (S500: a `/memfd:` link, `st_nlink` 0) whose `F_GET_SEALS` holds `F_SEAL_SEAL\|SHRINK\|GROW\|WRITE` = 15 (S501: seals are a property of the inode, so every open sees them), filled by the replay from its verified archive member's stream and hashing to the frozen server digest, with that same dev, inode and seals recorded in the rerun receipt's `server_exe` and in the replay's `own_server`, while every round-50 bind and teardown leg still holds and the anchoring surface is a registry row (S500). Check: `python3 tools/round52-replay-memfd-audit.py --repo <clone> --tip <tip> --scratch <dir>` prints `bind=1 sealed=1 teardown=1 newrow=1 bound=3/3 sealedruns=3/3 met=True` and exits 0 at the measured tip, and every ablation is `met=False` — the replay execs the extracted path with no memfd, a memfd left unsealed, a byte-identical host copy at the member path (the round-51 J3CopyDecoy shape), a hardlink at that path (the round-51 J4Hardlink shape). | A path's dev and inode accepted as identity (round-51 seats J3CopyDecoy and J4Hardlink: a byte copy or a hardlink at the member path met that rule); a digest, a receipt field or `readlink` text accepted as the running image; an unsealed or linked memfd called sealed; the receipt trusted for seals it does not carry; an unsealed memfd whose descriptor is held across `exec` and rewrites the running image (round-52 seat J2Unsealed). Limits (preregistered): a memfd filled from the host's byte-identical install still matches (seat J5HostMemfd) — that the replay downloaded and read the archive is not observed; libraries load from the extracted tree by path (`LD_LIBRARY_PATH`), so only the server image is sealed; the round-50 carried limits stand (probe PATH execution, model bytes rewritten in place after mapping, kills during download or readiness); rename-over-member provenance remains an `[INFERENCE]`. | C1; `corpus/lessons/round-52.md` Claims C1; `corpus/lessons/round-51-verifier-spotcheck.md` D5 |
```

**RV4 — `KQ92` carries neither a `Check:` command nor the preregistered simpler-`exempt=` limit.**
The row's only limit is the HTML-comment cheat (seat K4Cheat). Preregistration
`.ufo/waves/round-52/preregistration.json` `limits[3]` says the counter's `exempt=` rule is simpler
than the tool's, so in `SCORECARD.md` the counter may grade fewer lines than the tool and the tool
leg holds the stricter rule; `limits[4]` says re-appended lines are historical bytes, superseded
where later text says so. Proposed replacement line for `:465` (or a `KQ9x (supersedes KQ92)` row):

```markdown
| KQ92 (round-52 C2) | In a file whose contract rule is A-corr (corrections appended), a line lost in place is restored by re-appending it verbatim at the end of that same file, fenced and attributed to its deleting commit, never disclosed; a disclosure row is admitted only for an A or A-row file whose verbatim re-append would duplicate a registry id or an errata key. The counter recomputes graded and unheld lines with its own fence-aware section logic and its own `exempt=`/`only=` rule, not the tool's. Check: `python3 tools/round52-append-restore-check.py --repo <clone> --tip <tip> --scratch <dir>` prints `fixture=1 lane=1 scenarios=8/8 corr_lost=0 row_lost=10 disclosed=10 met=True` and exits 0, and the tip's `tools/append-only-audit.py` exits 0 with no `--threshold`. | An A-corr ledger row; a restored line that is reworded, prefixed or moved to another file (the counter's `corr_lost` and the tool both fail it: seats J7Prefix, M6Restore); a restored block hidden from readers (an HTML comment passes the byte checks: seat K4Cheat; limit); a restored block that re-asserts a superseded fact without saying so. Limits (preregistered): the counter's `exempt=` rule is simpler than the tool's — a deleted line whose parent section is an exempt title is ungraded, while the tool also requires the line's origin to hold an exempt title and the section not to be gutted — so in `SCORECARD.md` the counter may grade fewer lines than the tool, and the tool leg (exit 0, no A-corr ledger rows) holds the stricter rule; re-appended lines restore the declared invariant as historical bytes, not re-asserted facts. | C2; `corpus/lessons/round-52.md` Claims C2; `corpus/lessons/round-51.md` C2 and Mistakes #3 |
```

**RV5 — `KQ89` states "101 of 106" without its measurement point.** The 101/106 arithmetic is
round-51's: `corpus/lessons/round-51.md` Claims C2 says v5 "graded only events of 20+ lines: 5 of
106 events"; round-50 closure R6 records a different population at a different tip ("the sub-20
threshold hides 97 events"). The landed row does cite `round-51.md` Claims C2 in the same cell, so
the figure is traceable and this is a wording note, not a defect: it is the one figure in the new
rows whose value moves with the revision. Optional tightening:
`a policy constant (20 lines) that graded 5 of the 106 events v5 could see, so it hid 101, the real \`LOG.md\` loss at \`ed135b3c\` among them`.

---

## 2. Remaining deliverable — the ten lesson-citation rows (append verbatim)

`corpus/QUALITY.md` still has ten live rows whose last cell names no lesson file (§3). None of them
is in the landed section; all ten are D7-class citation defects. Numbering assumes the working tree
ends at `KQ93`; digits may shift at landing, the `(supersedes …)` cell may not. Every row cites
`corpus/lessons/round-52.md` (this round's lesson) beside the lesson that produced the criterion.

Rows KQ94–KQ97 restate the criterion's operative clauses in condensed form and say explicitly that
the original admission/reject cells stand; KQ98–KQ103 restate nothing and carry the closure letter
into a file name.

```markdown
| KQ94 (supersedes KQ39's citation; the criterion itself is unchanged) | KQ39's admission cell stands as written at `corpus/QUALITY.md:289`: each checkable self-assessment statement is evaluated against repository state and history at its writing revision W, identified for its line by `git blame --line-porcelain`; false at W is a calibration mismatch, true at W but false later is drift and belongs to freshness; a correction preserves the original statement and is a newly appended row carrying the observed value. | KQ39's reject cell stands unchanged: a statement checked only at base or tip, later drift called a writing-time error, an in-place rewrite substituting for an appended correction, or a named shortcut/tampering control passing. | `corpus/lessons/round-29.md` §Claims C1 (six statement classes against the repo at the commit that wrote each line, `git blame --line-porcelain`, S174); the controls and ruling KQ39 already cites (`SCORECARD.md:1278-1291`; `.ufo/waves/round-29/controls/SUMMARY.md:11-45`); `corpus/lessons/round-52.md` (citation repair, round-51 closure D7) |
| KQ95 (supersedes KQ41's citation and restores its missing fourth cell) | A correction table keyed by a population row's own label declares that label's uniqueness first — as a precondition checked by the instrument (duplicate ids counted, not silently merged) or as a round-qualified composite key — and the instrument reports every failing row it cannot express instead of dropping it. | A predicate whose validity depends on labels that are not unique: three distinct failing rows sharing the cell `C1` (rounds 11-13) make one correction row silently resolve three dispositions, and the frozen predicate becomes unreachable while the counter still reports a tidy `unresolved` count. | `corpus/lessons/round-31.md` §Claims C2 (the `(row, class)` key collides on three rows whose Claim cell is `C1`; `valid 10 false 3 unresolved 3`, `met False`) and Mistakes #2 (both copies of a duplicate population row uncounted); `corpus/lessons/round-52.md` (citation repair, round-51 closure D7) |
| KQ96 (supersedes KQ42's citation; the criterion itself is unchanged) | KQ42's admission cell stands as written at `corpus/QUALITY.md:309`: a cell whose text is graded by a counter only for shape is admitted as evidence only after a counterexample search on the same pinned fixture — one request the cell's literal reading forbids per prose cell, its outcome recorded, the probe receipt committed with the row — and a falsified cell is narrowed by an appended correction, never by rewriting the counted bytes. | KQ42's reject cell stands unchanged: counting a prose cell as verified because the counter accepted its shape — the round-31 C1 table counted all eighteen rows while six `meaning` cells asserted behaviour the pinned fixture contradicts. | `corpus/lessons/round-31.md` Mistakes #7 (K31-02, -05, -08, -09, -11, -12 falsified by the `w2/out/RevRow{A..E}/` counterexample probes); `corpus/lessons/round-52.md` (citation repair, round-51 closure D7) |
| KQ97 (supersedes KQ47's citation; the criterion itself is unchanged) | KQ47's admission cell stands as written at `corpus/QUALITY.md:334`: a round's report names the attempt count and, when it is not the first attempt, the reason each earlier attempt closed without work and the launch at which the round's work actually landed, with the watchdog line for each attempt; the lane records per-round attempts and restarts in `SCORECARD.md` and `LOG.md`. | KQ47's reject cell stands unchanged: a round hides a restart, reports the first attempt as its only attempt, or names the reason without the watchdog evidence. | `corpus/lessons/round-38.md` §Frontier (proposal 4 adopted as KQ47, in the round that itself ran as attempt 2); `.ufo/watchdog.log` lines 1293-1294; `.ufo/waves/round-38/assimilation/attempts-receipt.txt`; `considerthese/2026-10-24.md` proposal 4; `corpus/lessons/round-52.md` (citation repair, round-51 closure D7) |
| KQ98 (supersedes KQ45's citation; the criterion itself is unchanged) | KQ45's admission cell stands as written at `corpus/QUALITY.md:322`: every new SOURCES row's located quote is checked against the source bytes at its cited anchor in the round that writes the row; a `verbatim` quote is checked byte-exact; a quote that drops a word, strips markup or sits at a line other than the one its anchor names is a defect corrected by an appended superseding row, never by editing the quoted cell; a source the check cannot reach records its access route and is marked unverifiable-by-fetch, which is not drift. | KQ45's reject cell stands unchanged: a quote a reader cannot find at the cited anchor, a `verbatim` quote that is a paraphrase with markup stripped, or an unfetchable source recorded as drift. | `corpus/lessons/round-30.md` Mistakes #3 (S174 `teaches` verbatim mislabel, corrected by an appended decision record) and `corpus/lessons/round-32-verifier-spotcheck.md` §6 item 3 (S193 quote at line 15, 17 words, not the lesson's line 22/16 words); the round-36 measurement of all three drifts (S174, S193, S192 — unverifiable-by-fetch) is recorded only in the fleet report `.ufo/reports/round-36/kama.md:216-221`, not in `corpus/lessons/round-36.md`; `considerthese/2026-10-24.md` proposal 2; `corpus/lessons/round-52.md` (citation repair, round-51 closure D7) |
| KQ99 (supersedes KQ80's citation; KQ80 narrows KQ76, criterion unchanged) | KQ80's admission cell stands as written at `corpus/QUALITY.md:435`: a replay counts as having run a server under outside observation only when the observer is not the replay and derives four facts itself — a LISTEN socket on the announced port belonging to a pid whose `/proc/<pid>/exe` hashes to the receipt's server digest, that pid's descent from the replay by the `/proc` ppid chain (up to 64 hops), a fresh nonce the observer invents answered through the recorded model's own tokenizer surface with every returned piece equal to the observer's own GGUF vocabulary decode, and the pid gone with the port refusing after release. | KQ80's reject cell stands unchanged: the observer trusts the replay's own receipt, argv or any self-reported state, or a decoy replay that execs the host binary in place of the replay passes. | `corpus/lessons/round-49-verifier-spotcheck.md` R1 (the counter never joined the observed pid with the rerun receipt's `child_pid`, so a decoy replay that starts the host's b11909 binary and copies the receipt met `met=True`; seats K1Cheat, K1Design, R0Controls) and R5 (carried limits); `corpus/lessons/round-52.md` (citation repair, round-51 closure D7) |
| KQ100 (supersedes KQ81's citation; the criterion itself is unchanged) | KQ81's admission cell stands as written at `corpus/QUALITY.md:436`: a live observation is process-bound evidence only where the pid the observer watched is the pid the replay's own rerun receipt names (`child_pid == observed pid`) and the model file the server mapped is the receipt's model — `model_mapping` from `/proc/<pid>/maps` (dev, inode, pathname), re-opened `O_NOFOLLOW`, `fstat`-checked, hashed. | KQ81's reject cell stands unchanged: a record without the mapping, a mapping whose sha256 differs, or a dev/inode mismatch (btrfs fails closed). | `corpus/lessons/round-49-verifier-spotcheck.md` R1 (pid/`child_pid` join missing; the loaded model bytes not bound); `corpus/lessons/round-52.md` (citation repair, round-51 closure D7) |
| KQ101 (supersedes KQ82's citation; the criterion itself is unchanged) | KQ82's admission cell stands as written at `corpus/QUALITY.md:437`: a teardown claim is admitted only when the observer kills the process that started the replay — not the replay — and then sees every process of a snapshot taken during the hold gone within a bounded wait (30 s here) and the port refuse, with the replay and live child arming their own parent-death signals. | KQ82's reject cell stands unchanged: teardown proven only from the live tool to the server, or a surviving reparented child. | `corpus/lessons/round-49-verifier-spotcheck.md` R2 (a killed counter still left replay, live tool and server up; seat X1Kill); `corpus/lessons/round-52.md` (citation repair, round-51 closure D7) |
| KQ102 (supersedes KQ83's citation; the criterion itself is unchanged) | KQ83's admission cell stands as written at `corpus/QUALITY.md:438`: an append-only audit's verdict must not depend on the order git lists sibling commits, on content that only looks like a heading, or on a moved line's line ending — `origin(l)` is the union over every birth of the line's key of the titles holding it, keys drop one trailing CR, and sections ignore CommonMark fenced `## ` lines. | KQ83's reject cell stands unchanged: `rev-list`-order origin, fence-blind sections, or byte-exact keys. | `corpus/lessons/round-49-verifier-spotcheck.md` R3 (origin `git rev-list`-order dependent, fence-blind, CRLF-sensitive; seats K2Origin, X2Fixtures, K2Cheat, V2Ctr); `corpus/lessons/round-52.md` (citation repair, round-51 closure D7) |
| KQ103 (supersedes KQ84's citation; the criterion itself is unchanged) | KQ84's admission cell stands as written at `corpus/QUALITY.md:439`: an append-only audit's accounting is complete — `graded + ungraded == deleted` for every event, `deleted` equals `git diff --numstat` on the same first-parent range, and no leg accepts the tool's self-reported ungraded as the whole story. | KQ84's reject cell stands unchanged: a tool whose counts do not add up, or a counter that mirrors the tool's own rule instead of recomputing it. | `corpus/lessons/round-49-verifier-spotcheck.md` R3 (the lane leg only upper-bounded the tool's self-reported `ungraded`, and the counter's binder copied the tool's rule); `corpus/lessons/round-52.md` (citation repair, round-51 closure D7) |
```

Integrator notes:

- Every row is one physical line, as the file's rows are. `\|` appears only in RV3's seals
  expression, escaped so it does not split a cell; a cell-count check over the block in §2 returns
  `10 rows, all 4 cells`.
- If the L1 prefers an erratum to a supersession for KQ94–KQ98, D7 allows it ("append a superseding
  row or an erratum that names the lesson file"); the erratum route leaves the row text untouched.
- KQ98 is the only citation that cannot be completed inside `corpus/lessons/` — see F3.

---

## 3. Scan — every live KQ row whose last cell names no lesson file

Method (`scan-rows.py` in this directory): parse `| KQ<n>` table lines **outside** fenced blocks —
the `## Restored lines (round 52)` block that closes the file is a fence, and its restored `KQ46`
row is historical bytes, not a live criterion — split on `|`, and require the last cell to match
`lessons/<name>.md` or `round-<n>…md`.

```
$ python3 .ufo/waves/round-52/w1/out/W2Quality/scan-rows.py corpus/QUALITY.md
total rows 93
== rows whose last cell names no lesson file == 12
289  KQ39   cells=4  `SCORECARD.md:1278-1291` (round-25 axis-fit ruling); `.ufo/waves/round-29/preregistration.json:14-20`; `.ufo/waves/round-29/controls/SUMMARY.md:11-45`
303  KQ41   cells=3  A predicate whose validity depends on labels that are not unique: …
309  KQ42   cells=4  `.ufo/waves/round-31/w2/out/RevRow{A..E}/`; appended corrections in `SKILL.md` §Round-31 attempt-2 …
322  KQ45   cells=4  `considerthese/2026-10-24.md` proposal 2, opened 2026-10-24; the drift measured this round on S174 …
334  KQ47   cells=4  `considerthese/2026-10-24.md` proposal 4, opened 2026-10-24; `.ufo/watchdog.log` lines 1293–1294 …
435  KQ80 (narrows KQ76)  cells=4  C1; round-49 R1/R5
436  KQ81   cells=4  C1; round-49 R1
437  KQ82   cells=4  C1; round-49 R2
438  KQ83   cells=4  C2; round-49 R3
439  KQ84   cells=4  C2; round-49 R3
441  KQ86   cells=4  C2; round-50 R6; `considerthese/2026-10-26.md` proposal 1
442  KQ87   cells=4  C2; KQ22
lesson refs 58 missing []
```

(93 rows now includes the five uncommitted round-52 rows. Line numbers are the working tree's.)

**F1 — twelve rows lacked a lesson citation, not two.** Round-51 closure D7 names KQ86 and KQ87;
the scan found ten more, and KQ41 has **no fourth cell at all**, so its "Motivating lesson" column
is empty in the rendered table:

```
$ awk 'BEGIN{FS="|"} /^\| *KQ[0-9]/{ if (NF-2 != 4) printf "%d\t%s\tcells=%d\n", NR, $2, NF-2 }' corpus/QUALITY.md
303	 KQ41 	cells=3
```

KQ41 cannot be repaired in place under the file's own append-only rule, so KQ95 is both the
citation repair and the shape repair.

**F2 — KQ39, KQ42, KQ45, KQ47, KQ80–KQ84 cite a receipt, a closure letter, a `considerthese`
proposal or another criterion where D7 asks for a lesson file.** All ten now have an identified
lesson and a drafted row in §2.

**F3 — KQ45's motivating measurement is recorded only in the fleet report.** The rule rests on
three drifts measured in round 36 (S174 verbatim mislabel, S193 quote location, S192
unverifiable-by-fetch). They are at `.ufo/reports/round-36/kama.md:216-221` (fleet root, read-only)
and **not** in `corpus/lessons/round-36.md`, whose §Gate lists S200/S202/S206/S210/S211/S224/S230
instead:

```
$ grep -c "S174\|S192\|S193" corpus/lessons/round-36.md
0
```

The per-row corrections do exist in the lane (`corpus/lessons/round-30.md` Mistakes #3 for S174;
`corpus/lessons/round-32-verifier-spotcheck.md` §6 item 3 for S193), which is what KQ98 cites. If a
lesson-file citation for the whole proposition is required, the append-only route is a round-36
lesson correction appended at integration — never an edit to `corpus/lessons/round-36.md`.

**F4 — `corpus/lessons/round-52.md` has two headings (Claims, Gate) and no Errata/Mistakes
section, while three of the five uncommitted round-52 rows cite `round-52.md` Errata D7 or
`round-52.md` Mistakes.** That is RV1 and RV2: the cited sections do not exist, and `D7` is
round-51's label. Fixing the cells is cheaper than inventing the sections; if the L1 prefers the
sections, the lesson is A-corr and may be appended to.

**F5 — no other table defect.** All 93 rows have four cells except KQ41; no id is duplicated; all
58 distinct `lessons/*.md` references resolve to committed files.

---

## 4. What this seat did not do

- Did not run `tools/round52-replay-memfd-audit.py` or `tools/round52-append-restore-check.py`; the
  `met` values quoted here are read from the L1's `measured/*-build.out` receipts.
- Did not write, commit or edit anything in the lane. The five round-52 rows reviewed in §1 were
  found already modified in the working tree (a concurrent integration); this seat snapshotted
  their bytes and left them untouched, so `git status --porcelain corpus/QUALITY.md` still shows
  ` M` with the same 12-line diff (sha256 recorded at the top).
- Did not decide row numbers, the append order, or whether RV3/RV4 are amended pre-commit or filed
  as supersessions; those are integration choices named above.
