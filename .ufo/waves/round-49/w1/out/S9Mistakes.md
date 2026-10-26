# S9Mistakes — round 49: make the R2 (placeholders) and R3 (census paraphrase) conformance defects checkable

**Verdict:** checkable — a 264-line stdlib checker (`report-precheck.py`, sha256 `a2030bcf…36c0a10`) reproduces both round-48 closure defects on the filed bytes (`15710a2a` → 6 findings, exit 1; R3 isolated at `dcc079e7` → 1 finding, exit 1), passes a corrected copy (exit 0) and the round-47 conforming control (exit 0), and its nine built-in tests pass 9/9.

## Contract read

`corpus/lessons/round-48-verifier-spotcheck.md` (round-48 closure, corpus file in the lane):

- `:22` — R2: the first report commit `15710a2a` had `__TIP__`, `__WAVEDONE__`, `__YIELD__`, `__DEAD__`, `__LASTROW__`; `dcc079e7` then rewrote 6 lines of the filed bytes in place.
- `:95` — the census run has 93 `W04`, **1 `W01`** (S481) and 0 `E`; "the report's prose omits the W01 (R3)".
- `:111`–`:112` — closure: file the final lane commit first, then the report once; later corrections are appended errata; "Quote the census output whole."

## What was built

`report-precheck.py` (stdlib only, Python 3.14.8), one report path plus one or more census receipts:

| Rule | Detection | Exit |
|---|---|---|
| R2 | every `__[A-Z][A-Z0-9_]*__` token anywhere in the file (superset of the spec's `__[A-Z]+__`, so `__LAST_ROW__` is caught too) | 1 |
| R3 | the `## Sources & frontier` section (`^##\s+(Sources\s*(&\|and)\s*frontier)$`, case-insensitive) must carry **every code the receipt has** with the receipt's own count; target line = section line naming the receipt's basename, else section lines carrying a `count CODE` claim, else the section; `count` may sit before or after the code, in backticks, `93 W04` / `93 `W04`` both parse | 1 |
| usage | missing file, unreadable receipt | 2 |

```
python3 report-precheck.py --report .ufo/reports/round-49/kama.md \
    --census .ufo/waves/round-49/census/end.out --census .ufo/waves/round-49/census/start.out
python3 report-precheck.py --selftest          # 9/9
```
`--allow TOKEN` (repeatable) suppresses a token the report quotes as repaired text; `--json` emits the findings object for a counter wrapper.

## Evidence

Every case below is a captured run; the `.out` files are in `evidence/` under the out directory named at the end. Reports cited from the fleet repo were extracted read-only with `git -C /home/vgpnk/Projects/shokunin show <rev>:<path>` into scratch, then copied to `reports/`.

| # | Report | Receipt | Exit | Findings (verbatim) | File |
|---|---|---|---|---|---|
| 1 | `15710a2a:.ufo/reports/round-48/kama.md` | `census/end.out` (r48, `W01=1 W04=93`) | **1** | `placeholder line 7: __TIP__`, `14: __WAVEDONE__`, `15: __YIELD__`, `16: __DEAD__`, `49: __LASTROW__`, `census: omits W01=1 (line(s) 65, receipt end.out carries 1 W01 line(s))` | `case1-r2-r3-15710a2a.out` |
| 2 | `dcc079e7:.ufo/reports/round-48/kama.md` (placeholders filled) | r48 `end.out` | **1** | `census: omits W01=1 (line(s) 65 …)` — R3 alone, isolates the paraphrase | `case2-r3-only-dcc079e7.out` |
| 3 | R3 line alone (`reports/r3-line-only.md`: heading + the `:65` bullet verbatim) | r48 `end.out` | **1** | `omits W01=1 (line(s) 5 …)` | `case3-r3-line.out` |
| 4 | corrected copy: `dcc079e7` with `:65` rewritten `(93 W04, 1 W01 (S481), 0 E; …)` | r48 `end.out` | **0** | `RESULT pass findings=0` | `case4-corrected-pass.out` |
| 5 | conforming control: `HEAD:.ufo/reports/round-47/kama.md` (`:105` already says `93 W04, 1 W01 S481, 0 E`) | r47 `end.out` | **0** | `RESULT pass findings=0` (also passes against r48's receipt) | `case5-r47-control-pass.out` |
| 6 | `HEAD:.ufo/reports/round-60/kumitate.md` | empty receipt (placeholder leg only) | **1** | `placeholder line 4: __TIP__`, `5/88/96/190: __MEASURED__`, `73: __COMMITS__` | `case6-r60-placeholders.out` |
| 7 | `HEAD:.ufo/reports/round-37/kotodama.md` | empty receipt | **1** | `placeholder line 42: __E3_PLACEHOLDER__` — false positive (see limits) | `case7-r37-quoted-placeholder.out` |
| 8 | same as 7 with `--allow __E3_PLACEHOLDER__` | empty receipt | **0** | `RESULT pass` | `case8-r37-allowed-pass.out` |
| 9 | mutant of case 4: `92 W04` instead of 93 | r48 `end.out` | **1** | `count W04: report says 92, receipt end.out carries 93 (line(s) 65)` — the fix cannot be satisfied by a wrong number | `case9-wrong-count-mutant.out` |
| 10 | `--selftest` | in-process fixtures | **0** | `selftest: 9/9` — pass-on-complete-line, omitted code, wrong count, missing section, backticked claims, placeholders, `--allow`, unnamed-receipt fallback, empty receipt | `selftest.out` |
| 11 | this seat report (it quotes the tokens) | empty receipt | **1** | 22 placeholder hits on the quoted tokens, lines 9/19/36/41–43/55–56/69 — the false-positive class in the raw | `case10-self-on-seat-report.out` |
| 12 | same with `--allow` for the nine quoted tokens | empty receipt | **0** | `RESULT pass findings=0` | `case11-self-report-allowed.out` |

Receipt counts are the counter's own: `cut -f2 .ufo/waves/round-48/census/end.out | sort | uniq -c` → `93 W04`, `1 W01`, plus the non-finding `exit=0`/`ok` lines the script ignores (`end.out` has 94 finding lines; `start.out` is byte-identical, `cmp` silent).

## Defects and findings

1. **R2, reproduced on the filed report.** `git -C /home/vgpnk/Projects/shokunin show 15710a2a:.ufo/reports/round-48/kama.md`, lines 7, 14, 15, 16, 49 — the five placeholders the closure names; case 1 flags exactly those lines and no others.
2. **R3, reproduced independently of R2.** Commit `dcc079e7` has no placeholders and still fails: line 65 reads `end exit **0** (93 W04, 0 E; …)`, the receipt has `W01=1`. The corrected line is `end exit **0** (93 W04, 1 W01 (S481), 0 E; …)` (case 4, exit 0). Round-47's report line 105 already had the whole quote, so R3 is a regression, not a standing template gap.
3. **Recurrence outside this lane (finding, not fixed).** `.ufo/reports/round-60/kumitate.md` is a *filed* report in the fleet tree at `HEAD` (last commit touching the path: `f47ad6ba8d306f8125597401cb2ce45c1297a593`) that still holds `__TIP__` at line 4, `__MEASURED__` at lines 5, 88, 96, 190 and `__COMMITS__` at line 73 — the same R2 defect class, unfilled in the fleet tree. Exit 1 on case 6. Not this lane's file; reported only.
4. **False positive to expect.** `.ufo/reports/round-37/kotodama.md:42` mentions `__E3_PLACEHOLDER__` as text it repaired; a mechanical scan cannot tell a quote from an unfilled slot. `--allow __E3_PLACEHOLDER__` clears it (case 8). Any wiring must let a reviewer pass `--allow`, or the check will cry wolf on reports that describe the defect.

## Proposed adoption (not applied — lane is read-only for this seat)

1. Copy `report-precheck.py` verbatim to `kama-shokunin/tools/report-precheck.py` (sha256 `a2030bcf…36c0a10`, 264 lines, stdlib only; the delivered file is the full proposed text).
2. Run it at the L1's filing step, before the report commit, against that round's census receipts:
   `python3 tools/report-precheck.py --report .ufo/reports/round-<N>/kama.md --census .ufo/waves/round-<N>/census/start.out --census .ufo/waves/round-<N>/census/end.out`
   Exit 1 blocks the filing; the message names the line and the missing code, which is exactly the R3 correction text.
3. Keep the census bullet's wording as the whole quote — `93 W04, 1 W01 (S481), 0 E` — so the R3 leg stays satisfiable by a single line.

## Limits (disclosed, not claimed as covered)

- **R2's second half is out of reach.** The checker reads one file; the in-place rewrite of filed bytes (`15710a2a` → `dcc079e7`, "report filed after its commit") needs the path's git history and a byte diff. A pre-filing check cannot see it at all — the closure's "land the final commit first, then file once" is the only lever there.
- **Placeholders are matched anywhere, including fenced code and backticks.** That is deliberate (round-60's `__TIP__` sits in backticks — masking would hide a real defect), and it is why `--allow` exists. This report itself trips the rule for the tokens it quotes (case 11: 22 hits, exit 1) and passes with the nine quoted tokens allowed (case 12).
- **Only codes the receipt carries are required.** A code family the receipt does not flag (here `E`, count 0) is never checked, so `0 E` passes whether or not `E` exists; and a code the report *invents* is not flagged. The check is "the receipt quoted whole", not "nothing but the receipt".
- **Counts are compared, not re-derived.** A receipt that is itself wrong passes; provenance of the receipt is the census script's business, not this checker's.
- **Target-line selection is a heuristic** (receipt basename → claim lines → whole section). A report that discusses census codes in a line that also holds the receipt name could hide a count on a sibling line; the finding text always names the lines it read, so the failure is auditable.
- **R4 (route map vs live config) and the `SHONEN`/ancestry checks are not covered** — they need config and git state.

## Scope, hygiene, provenance

- Wrote only `kama-shokunin/.ufo/waves/round-49/w1/out/S9Mistakes/` (deliverables) and `kama-shokunin/.ufo/waves/round-49/w1/out/S9Mistakes.md` (this report). No lane file, no fleet file, no `~/.local/bin`.
- Lane state observed, not touched: `git -C /home/vgpnk/Projects/shokunin/kama-shokunin status --porcelain` → ` M tools/append-only-audit.py` plus untracked `.ufo/waves/round-49/{measured/,w1.ready,w1.ready.dispatched,w1/out/}` and `corpus/lessons/round-49.md`; HEAD `122c4ee95701587cef7f4342c3d175622ec2f4ad`. The modification to `tools/append-only-audit.py` predates this seat and is not mine.
- No llama-server was started by this seat; `pgrep -af llama-server` at finish printed nothing.
- Tooling: no installs, no pacman. Python 3.14.8 (system).
- Scratch `/fast/scratch/hyaku/kama-r49/S9Mistakes` removed after the runs; every cited output is captured in `evidence/`.
- Not re-reported here (already known integration items): the round-49 counters' SKILL.md registry rows, and the round-49 SCORECARD/LOG/lesson/QUALITY/README entries.

## Artifacts (absolute)

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/S9Mistakes.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/S9Mistakes/report-precheck.py`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/S9Mistakes/census/end.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/S9Mistakes/census/end-r47.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/S9Mistakes/empty-receipt.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/S9Mistakes/evidence/` (12 captured runs: `case1`…`case11`, `selftest.out`, `empty-receipt.out`)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/S9Mistakes/reports/` (`kama-r48.md`, `kama-r48-filled.md`, `r3-line-only.md`, `corrected.md`, `mutated-count.md`, `k47.md`, `k60.md`, `k37.md`)
