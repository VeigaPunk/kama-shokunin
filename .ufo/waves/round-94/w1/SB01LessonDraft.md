# SB01LessonDraft — round 94 w1 (kama)

Seat `SB01LessonDraft` (leaf, calibration axis). Lane `/home/vgpnk/Projects/shokunin/kama-shokunin`.
Out dir `.ufo/waves/round-94/w1/out/SB01LessonDraft/`; scratch `/fast/scratch/hyaku/kama-r94/SB01LessonDraft/`
(removed at yield). Host load 129–200 this session (`uptime` 23:42–23:56). Revisions: base `e6f1dccecbad6dea44a129dabc928822c458e824`; freeze `285f17832d0e26364366bbf19888d68f1838249b`; C1 `a27656a454b1a2364f8b6e55f42fbca8c2e86ee4`; C2+C3 `6aa5fa6bd9bbf44c4b2ca3f1e2158e7d5aa92623`; tip at read time `11d2770b5e61e997245dce74eadeff8b3ce9ea1f`. Archive re-fetched: sha256 `f50a52f4…ea13` = pin.

## Scope

Draft candidate `## Mistakes` rows and `## Gate` admit/reject entries for `corpus/lessons/round-94.md`; audit the committed Mistake rows' "shown able to fail" arms. Read-only in the lane except my out dir and this report. No delegation, no live endpoint, no git mutation in the lane. Full per-finding detail in my out-dir candidate file (Part D there); this report carries the claims and their evidence pointers.

## Commands and outputs (exit codes)

| # | command | exit | result |
|---|---|---|---|
| 1 | `scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama` | 0 | `kama ok …/corpus/SOURCES.md`; only pre-existing W04 dups + W01/S481, none on S604–S615 |
| 2 | `git show <rev>:corpus/SOURCES.md \| grep -cE '^\| S[0-9]{3,} '` (base/M2/tip) | 0 | **343 → 355 → 355** — the committed census claim |
| 3 | `curl -sfL …/tar.gz/refs/tags/b12177` + `sha256sum`; 12 members vs 12 raw-URL fetches | 0 | `f50a52f4…ea13` = pin; all 12 equal each other and to the SOURCES digests |
| 4 | `sed -n '<line>p'` for all 12 new + 9 re-opened quotes | 0 | 20/21 exact; **S604 off by one** (DEFECT-1) |
| 5 | `python3 tools/round94-setter-sweep.py --repo . --rev 6aa5fa6b --work <scratch> --archive <tarball>` | **0** | **byte-identical** to committed `measured/c2.out` (`diff` empty); `SETTER_SWEEP 92 92 2 92 0 0 0 0 derived_checked=47 derived_disagree=0 decisions=2/2 pop=92 met=True` |
| 6 | same counter at base `e6f1dcce` | 1 | 92 × `SETTER_MISSING`; `met=False` (M2's arm) |
| 7 | mutant P50 line 35→36 (`--skill-file` on a copy) | 1 | `SETTER_ROW P50 unbound fabricated`; `met=False` (M1's arm) |
| 8 | mutant P12 scope cell → `llama-server` | 1 | `SETTER_ROW P12 unbound derived`; `derived_disagree=1`; `met=False` (M3's arm) |
| 9 | rescope all 34 `common/arg.cpp` rows to `llama-server` | 1 | `derived_disagree=23`, 23 `unbound derived` — **not 18** (M3's figure) |
| 10 | re-derive population with the two env tokens removed from `CFG_SUBSTR` | 0 | **88**; the 4 added lines are exactly the 4 M2 names → **M2 arithmetic reproduces** |
| 11 | `git diff --stat 6aa5fa6b 11d2770b -- tools/round94-setter-sweep.py` (and M1..tip) | 0 | empty — counters byte-stable to tip |
| 12 | `git show --stat 285f1783`; `git log --all -- .ufo/waves/round-94/controls/…` (7 named receipts) | 0 | freeze = `plans/round-94-claims.md` **only** (NOTE-4); **0 commits** for each named control receipt (NOTE-8) |
| 13 | `git diff --stat e6f1dcce 6aa5fa6b -- SCORECARD.md` | 0 | empty — SCORECARD untouched (NOTE-3) |
| 14 | `git show a27656a4:tools/kama-probe.sh \| sha256sum`; `sed -n '299p'` (M1) | 0 | per-`gguf_parse` `DEADLINE` reset; `timeout 60` wrapper; probe sha `27065a5c…` = `c1.out`'s `probe_sha256` |

## Findings

**DEFECT-1 — the S604 quote's line number is wrong in two committed files.** `corpus/SOURCES.md:359` (M2 row S604) and `corpus/lessons/round-94.md:20` place `opt.handler_string(params, val);` at **line 150** of `common/preset.cpp` @ b12177; line 150 is `if (opt.handler_string) {`, the quoted statement is at **line 151** (`awk 'NR>=149&&NR<=152'`; `grep -n` → 151). The other 11 new and 9 re-opened quotes are exact — an isolated off-by-one. `sources-census.sh validate` still exits 0: the census checks row shape, not quote line numbers, so the round's own check cannot see it. Fix: 150 → 151 in both files.

**DEFECT-2 — the frozen C2 predicate's printed fields do not match what the counter prints, and `entry_points=<e>` is printed by nothing.** The plan freezes `SETTER_SWEEP population=<n> rows=<n> bound=<n> unbound=0 missing=0 duplicates=0 fabricated=0 derived_disagree=0 entry_points=<e> decisions=<d> decisions_bound=<d> …` (`plans/round-94-claims.md:58-60`); the counter prints **positional** numbers (`tools/round94-setter-sweep.py:354`): `SETTER_SWEEP 92 92 2 92 0 0 0 0 derived_checked=47 derived_disagree=0 decisions=2/2 pop=92 met=True`. None of `population=`/`rows=`/`bound=`/`unbound=`/`missing=`/`duplicates=`/`fabricated=` is printed; `decisions=2/2` is one token, not `decisions=<d> decisions_bound=<d>`; and **`entry_points=<e>` appears nowhere** in counter, receipt or lane file — a repo-wide `grep -rn entry_points` over the fleet finds it only in the plan (plus unrelated chousa-lane scripts). The round's headline new dimension (the per-row `entry` cell) therefore has **no counter metric**: it is graded only per-row by `entry-enum`, never aggregated. The C2 predicate as frozen is literally unmet; the substance (92/92 bound, 0/0/0/0, decisions 2/2, `met=True`, exit 0) does hold. Round 93's counter printed the matching named fields (`SETTER_ROWS population=48 rows=48 … decisions=2 decisions_bound=2`), so this is a regression against the previous round's receipt convention.

**DEFECT-3 — six committed P-rows violate the frozen counter's own documented B4 pairing.** The docstring (`tools/round94-setter-sweep.py:13-16`) states parameter `port`/`n_parallel` pairs with effect in {default, overrides, copies, unrelated} — `declares` excluded. Six committed rows use `declares` with a real parameter: P12, P14, P15, P17 (`n_parallel`), P18, P20 (`port`). The counter's **code** does not enforce the documented pairing (`tools/round94-setter-sweep.py:241-246` rejects only `param=="-"` with default/overrides and `param!="-"` with `unrelated`), so they bind silently. Round 93 enforced a strict iff (`tools/round93-setter-rows.py:250`), so the rule was **loosened between rounds** with no record of the change. The six rows are exactly the r93 KQ151 twins (2515/2523/2526/2531, 3318/3323) — so the twins are now *consistent with each other* (r93 M4 closed), but the fix was made by *not* using the label the section was to define: `plans/round-94-claims.md:63-64` requires "P05–P07 relabelled under a `declares-unregistered`-class label **the section defines**", and the round-94 section defines no such class.

**NOTE-1 — the round-94 section has no Effect glossary.** It defines the Entry vocabulary inline (`SKILL.md:2085-2087`) but never the Effect vocabulary its own table uses; round 93's section had one (`SKILL.md:1978`). KQ151's question — "does this label agree with the section's own vocabulary?" — is unanswerable for the effect column.

**NOTE-2 — the committed `## Gate` URL column says "raw URL", not the URL.** All 12 new rows read `raw URL — 2026-11-07, sha256 …` (`corpus/lessons/round-94.md:20-31`); round 93's Gate spelled them out. C3 requires "URL, access date and ≤25-word located quote per row" (`plans/round-94-claims.md:99-101`) — the artifact records a pointer, not a URL. The URLs are recoverable from `corpus/SOURCES.md`, so nothing is lost.

**NOTE-3 — the lesson has no `## Dispositions` section for the r93 closure's R1–R7, and R3 is unaddressed.** Round 93's lesson ended with "## Dispositions of the round-92 closure (R1–R6)"; round 94's has only `## Gate` and `## Mistakes`. R3 ("stale capability rows … `SCORECARD.md:296`/`6163` still name the four-field key … and evidence `fe5f031c`") is addressed nowhere: `SCORECARD.md` is unchanged base→M2, both rows still read `device, inode, size, mtime` and cite `fe5f031c`, `grep -c 'round-94' SCORECARD.md` → `0`.

**NOTE-4 — "the counter's bytes identical to this freeze commit" is not checkable as written.** The freeze commit `285f1783` contains only `plans/round-94-claims.md`; neither counter existed at it. Round 93 committed its counters *with* the freeze (`0f272a37`: counters + 16 control files in one commit), so round 94's freeze is structurally weaker and C2's kill rule "K1 the counter changes after this commit" has no counter-at-freeze to compare against. What *is* checkable holds: both counters are byte-identical at their landing commits and at the tip.

**NOTE-5 — C1's counter `BASE` is round 93's base, not round 94's.** `tools/round94-router-budget.py:105` sets `BASE = "5af79495…"` (r93's base); `c1.out`'s `base_sha256=36631d49…` is that revision's probe (verified), whereas round 94's own base `e6f1dcce` has probe sha `1e21c1fb…`. Defensible (the last revision before the per-file deadline) but undocumented in the counter and not the revision the claim's base names.

**NOTE-6 — the receipts do not record exit codes.** `measured/c1.out` has no `exit=` line; `measured/c2.out` has neither `exit=` nor `rev=` (contrast round 93's `measured/c2.out`, ending `… rev=ee19acbd… skill=rev` / `exit=0`). My re-run reproduces `c2.out` byte-identically and exits 0, so the substance holds; the receipts are not self-describing.

**NOTE-7 — the C1 synthetic load is CPU-only, not "CPU+IO".** The plan says "one synthetic `stress-ng`/`yes`-class CPU+IO load" (`plans/round-94-claims.md:30-31`); the burners are 96 pure-CPU busy loops (`tools/round94-router-budget.py:239-247`, `DEFAULT_BURNERS = 96`). The receipt's `load1_nat=232.08 burners=96` is honest about what was applied, and the load effect is visible (R08: 8.59 s/9.13 s natural vs 13.93 s/15.01 s loaded, a 1.6× within-run ratio) — the behaviour C1 is about, measured under load and reported with the load. Good practice.

**NOTE-8 — the control receipts the plan names are not in the lane.** `controls/c1-base.out`, `c1-forgeries.py/.out`, `c2-base.out`, `c2-forgeries.py/.out`, `sources-opened.out`, `census-start.out` and `measured/gate-final.out`: `git log --all` finds **0 commits** for each. Only `controls/c2-build-candidate.py`, `measured/c1.out`, `measured/c2.out` exist. Round 93 committed 16 control files at its freeze. This weakens M1's and M3's evidence pointers and C3's "the report pastes both census outputs" claim, whose "before" receipt is uncommitted.

**NOTE-9 — all three committed "shown able to fail" arms are present and correct; the *evidence pointers* are not.** Re-run at M2 with the committed counter: **M1** — mutant 35→36 → `SETTER_ROW P50 unbound fabricated`, `met=False`, exit 1; base rev → `met=False`, exit 1 — both reproduce exactly. **M2** — base rev lists all 92 as `SETTER_MISSING`, exit 1 — reproduces; the population arithmetic also reproduces (88 → 92, same four lines). **M3** — reverting one scope cell re-opens a `derived` disagreement (`derived_disagree=1`, `met=False`, exit 1) — reproduces. **No committed Mistake row has a missing or wrong failure demonstration.** What is wrong is adjacent: M1's "155 mismatches" receipt is in no committed or scratch file (`grep -rl 155` over `/fast/scratch/hyaku/kama-r94/l1-controls/` finds only upstream llama.cpp files; the counter prints no field named `mismatches` at all); M3's "18 rows / `derived_disagree=18`" belongs to an uncommitted partial draft — the closest reconstruction (all 34 arg.cpp rows rescoped) gives **23**; and M2 attributes the omission to "R6/SC02", but the r93 closure's **R6** is "read SC02ProbeVerdictSweep's output … grade it against C1" (SC02 was the *probe-verdict* seat) — the setter-sweep routing was **R2** (M6/M8), and the config.ini gap was **SC01**.

## Deliverables (in my out dir)

- `.ufo/waves/round-94/w1/out/SB01LessonDraft/lesson-candidate.md` — candidate `## Gate` rows for S604–S615 + the S593/S596–S603 re-open row + the archive reject (each with URL, access date, located quote, line, reason); the S604 line correction; candidate `## Mistakes` M1/M2/M3 with class · evidence · captured-by · fix · shown-ability, each followed by this seat's re-run; the audit table of the three committed arms; Part D, the defects/notes above.
- `.ufo/waves/round-94/w1/out/SB01LessonDraft/receipts/c2-rerun-M2.out` — my C2 counter re-run at M2, byte-identical to the committed `measured/c2.out`.
- `.ufo/waves/round-94/w1/out/SB01LessonDraft/receipts/c2-base-rev.out` — C2 counter at base `e6f1dcce`: 92 × `SETTER_MISSING`, `met=False`, exit 1.
- `.ufo/waves/round-94/w1/out/SB01LessonDraft/receipts/archive.sha256` — pinned archive digest.

## Recommendations to the L1 (calibration axis)

1. Fix the S604 line number in `corpus/SOURCES.md` and `corpus/lessons/round-94.md` (150 → 151).
2. Disclose the C2 predicate/output mismatch with a dated note (the plan is frozen and the counter must not change, so a note is the available remedy), and record that `entry_points=<e>` has no implementation.
3. Give the round-94 section an Effect glossary, and record the B4 relaxation (r93 strict iff → r94 one-sided) in the lesson.
4. Record the r93 closure's R1–R7 dispositions in the lesson, as round 93 did; R3 is unaddressed and `SCORECARD.md` still carries the falsified four-field key and `fe5f031c`.
5. Correct M2's attribution from "R6/SC02" to R2/SC01, and note that M1's "155" and M3's "18" receipts are uncommitted (as round 93's M1 correction did for its v0 counter).

VERDICT: partial — the three committed Mistake rows' failure arms all reproduce, but S604's quote line is wrong in two committed files, the frozen C2 predicate names a metric nothing prints, six committed rows rest on a between-round B4 loosening the section never declares, and two of the three Mistake evidence pointers are uncommitted.
