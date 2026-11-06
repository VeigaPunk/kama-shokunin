# SB01LessonDraft (round 91, w1a2, attempt 2) — lesson sections for `corpus/lessons/round-91.md`

## Scope

Drafted the round-91 `## Gate` (S592-S595 admits, GNU gawk manual pages and SGLang v0.5.22 `server_args.py` rejects)
and `## Mistakes` (the round-91 bound-dimension mistake, its 38 s attribution, the scratch collision, plus eight
mistakes mined from the round-86..90 lessons and verifier spot-checks), for the L1 to integrate. Every source quote was
re-fetched by this seat and every digest compared with the committed `corpus/SOURCES.md` row; the one timing analysis
was measured in this session. I did **not** execute the frozen counters (`round91-answer-time.py`,
`round91-threshold-rows.py`, the harm suites) — their committed receipts were read, not re-run, and are labelled as such.
Load during fetches and timings: 27-44 on 32 cores (`uptime` recorded in both receipts).

## Commands and outputs (exit codes)

| # | command (abridged) | exit | observed |
|---|---|---|---|
| 1 | `curl -sS -L --max-time 60` on the four S592-S595 URLs, then `sha256sum` + awk over each `SOURCES.md` row's `sha256 <64 hex>` | 0 | all four digests equal to the rows (S592 `6df7d077…`, S593 `c3010a3c…`, S594 `0b0ea669…`, S595 `e963af06…`); 144 111 / 58 830 / 16 343 / 118 996 bytes — `sources-recheck.out` §1 |
| 2 | read every quoted line (`awk NR==…`) for S592 107-108/185/796-797, S593 632/634/636/644/669/703/464, S594 21/23/128/130/148/150/277/281, S595 14/26/111/809-813/1142-1145 | 0 | quotes verbatim as drafted — `sources-recheck.out` §2 |
| 3 | SKILL 14-row literal check: `awk -F' *\| *' '/^\| T[0-9]+ \|/' SKILL.md` → `grep -nF <literal> <file>` | 0 | `rows_checked=14 literal_on_declared_line_yes=14` — `sources-recheck.out` §5 |
| 4 | `curl` gawk `Assignment-Options.html` (--max-time 45, then 60), `Command-Line-Options.html`, `https://www.gnu.org/` (-4 and -6) | 28 (all five attempts) | `http=000`, 0 bytes, `conn=0.000000`, `ttfb=45.00/60.00 s`; DNS resolves both families — `sources-recheck.out` §3 |
| 5 | `curl` SGLang `server_args.py` and `arg_groups/fields/serving.py` @ `v0.5.22` | 0 | 35 396 B `d1b9ffc7…` / 13 638 B `66a9ab45…`; class at 230 has no defaults, field modules hold them — §4 |
| 6 | suffix-removal bench under `/usr/bin/bash` 5.3.20 (the probe's interpreter): 0.4/0.8/1.6 MB unmatched, one matched control, one `LC_ALL=C` bash, join-equivalence check | 0 | 2 635 / 11 220 / 47 221 ms (repeat 43 849), matched 19 ms, C-locale 7 796 ms, `base_vs_paste=yes` — `bench-suffix-removal.out` |
| 7 | `grep -rn 'took 38'` over the lane (md/sh/py/out) | 0 | only prose: probe comment 933-934, `corpus/knowledge/probe-answer-bounds.md:79`, a seat draft — no receipt under `controls/` or `measured/` |
| 8 | read-only `git diff c06838c5 3decfa36 -- tools/kama-probe.sh`, `git log -1 --format=%B` on F/M/M2 | 0 | the round-91 probe change is the awk pass + `router_match` + `paste -sd,` (35+/16-); commits land in order |

## Findings

**NOTE 1 — C2's 14 rows bind on what the counter grades: digest, line, literal, value.** All four digests equal the
SOURCES rows; each T row's literal is on its declared line (14/14), and every value is in the literal. Evidence:
`sources-recheck.out` §1, §5. Two K2 nuances for the reviewer read (not graded by the counter): (a) S595 lines 26/111
sit inside `if TYPE_CHECKING:` (line 14; block runs to 337), so they are declaration mirrors — the executed defaults
are the getters at 811-813/1143-1145 and carry the same values; a row citing only line 26 cites a declaration
(`sources-recheck.out` §2). (b) I did not re-derive the flag/env spellings or the per-row probe decisions; that is
RV02's read (§6 says so).

**NOTE 2 — the GNU gawk reject is a fetch-time fact, not a content judgment.** TCP connect to www.gnu.org never
completes on either address family, at four paths (45 s and 60 s attempts, `conn=0.000000`), while DNS resolves; the
lane recorded the same host timing out on 2026-10-20 (S053, `corpus/SOURCES.md:65`). No bytes → no quote → no row; the
rule is already grounded at the spec by S592, and no admitted entry cites the manual (CORPUS rule 4).

**NOTE 3 — the SGLang reject is verified and has a concrete flip.** At v0.5.22 `server_args.py` declares
`class ServerArgs:` (line 230) with no field defaults and sends fields to `arg_groups/fields/` (233-234, 350-352); the
defaults are in `arg_groups/fields/serving.py` (line 65 `host` = `"127.0.0.1"`, line 66 `port` = `30000`, sha256
`66a9ab45…`). A row on `server_args.py` has no threshold literal to bind; mining the field modules is the flip.

**DEFECT 1 — the 38 s figure behind the round-91 probe comment and the admitted entry has no committed receipt.**
`tools/kama-probe.sh:933-934` and `corpus/knowledge/probe-answer-bounds.md:79` state it; no file under
`.ufo/waves/round-91/controls/` or `measured/` records a suffix-removal timing (command 7). My bench reproduces the
magnitude and settles the mechanism: 1.6 MB unmatched = 47 221 ms (repeat 43 849) at load 27-44, i.e. the same order as
38 s at lower load; matched trailing comma = 19 ms; doubling series 2 635 → 11 220 → 47 221 ms = 4.26× and 4.21× per
doubling, so "quadratic" is correct. The sentence still needs the unlike-pattern condition (the cost is a non-matching
removal) and a committed bench or the F1 residual (39.38 s on T1) as its pointer. `bench-suffix-removal.out`.

**NOTE 4 — the attempt-1 seat's draft contradicts itself on this and the L1 must not integrate its wording.** Its M2
(`.ufo/waves/round-91/w1/out/SB01LessonDraft/round-91-lesson-draft.md`, untracked) says the cost is "linear … not
quadratic" from a single 1.8 MB point; its 68.57 s agrees with my 66 s at the same size, but a single point cannot
separate linear from quadratic and my three-point series does. Reported, not edited (another seat's out dir).

**NOTE 5 — the time condition is the load-bearing half of C1's predicate, and the receipts show it.** On the base probe
`controls/c1-base.out` T3 is `MODEL_OK reason=matched seconds=75.71`: the right verdict, 3.8× over budget — a
verdict-only rule (round 90's shape) calls that green. F1 (`controls/c1-f1-count-cap.out`) has no normalization at all and
still spends 39.38 s on T1, isolating the join; F2's T1 is verdict-correct at 45.49 s and fails on time
(`controls/c1-f2-exact-match.out`). Harm is unchanged base→M: `tests=77/77`, `RESULT pass=30 fail=0`, `cells=11 0/0`,
`cells=13 0/0`, `MODEL_OK router-unloaded-autoload` in both `controls/harm-base.out` and `measured/harm-M.out` (read, not
re-run).

**NOTE 6 — two attempts of one seat shared one scratch path, and attempt 1's mandatory cleanup deleted attempt 2's work.**
At 20:26 `/fast/scratch/hyaku/kama-r91/SB01LessonDraft/` held both seats' files (`f/`, `t/` and mine); at 20:36 it was gone
mid-bench (`cd` → "i/o error", `ls` → not found); the peer `SB01LessonDraft` had been live in the same window (proc://
at 20:33, "Confirming suffix-removal scan mechanism"). The contract requires each seat
to `rm -rf` its scratch before yielding — [INFERENCE] that cleanup removed the shared directory. I lost the fetched sources
and id lists and re-fetched into `.../SB01LessonDraft-a2/` (digests identical). Recommend namespacing scratch per attempt.

**NOTE 7 — two errors of my own, recorded rather than hidden.** (a) My first "C locale" bench row set `LC_ALL` only on
the `tr` element, so the parameter expansion still ran under UTF-8; the corrected run sets the locale on the bash that
expands (`bench-suffix-removal.out`, CORRECTION section). (b) `tee /dev/stderr` inside a redirected block truncated my
`sources-recheck.out` (tee opens with O_TRUNC); the file was rewritten complete, with the provenance note.

**No BLOCKER.** Nothing I read contradicts a frozen predicate: C1's measured receipt (`measured/c1.out`, probe
`0aa43573…`, `probe=rev`, `mismatches=0 positive_mismatches=0`) and C2's (`measured/c2.out`, `rows=14 bound=14
unbound=0 duplicates=0 engines=3 fetch_failures=0`) are consistent with the files and sources I re-opened.

## Deliverables

- `.ufo/waves/round-91/w1a2/out/SB01LessonDraft/round-91-lesson-draft.md` — the Gate (4 admits, 2 rejects) and Mistakes
  (3 round-91, 8 mined) sections, each mistake with class, evidence pointer, captured-by, fix and its failing demonstration.
- `.ufo/waves/round-91/w1a2/out/SB01LessonDraft/sources-recheck.out` — digests, quoted lines, gawk failures, SGLang
  files, 14/14 literal checks, and the list of what was not verified (K2 spellings/decisions).
- `.ufo/waves/round-91/w1a2/out/SB01LessonDraft/bench-suffix-removal.out` — the suffix-removal bench, its correction,
  and the base-vs-`paste` join equivalence.

VERDICT: holds — every quote, digest and literal in the draft was re-fetched and checked in-session (14/14 SKILL rows, 4/4 digests), the timing sentence now rests on a measured doubling series, and the two disclosed gaps (no committed 38 s receipt; shared-scratch deletion) are reported rather than papered over.
