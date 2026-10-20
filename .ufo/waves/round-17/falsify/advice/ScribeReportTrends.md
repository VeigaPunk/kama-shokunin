VERDICT: partial — round-17 trend labels reproduce from committed artifacts (expansion unchanged, quality improved, discernment unchanged); three attacks stand: unequal mutant denominators in the C1 headline, tier A on self-produced own-work rows, and no non-author sample yet for round 17.

# Scribe report — Trend verdicts and SHONEN (round 17, falsify)

Lane: kama-shokunin. Measured commit attacked: `54a29268e2083caa2b1e0d54ee1e7d90961302f3` (pushed). Author claims read: `corpus/lessons/round-17.md` §Declared claims and §Measurements; `SCORECARD.md:645-708` (§Round 17, trend lines at 698-702). Scope: expansion, quality, discernment; SHONEN.md boxes. C1/C2 are attacked only where they feed a trend label.

## Trend verdicts

### Counted evidence (reproduced by me)

| Quantity | 1e41928 (r10) | 3285cdf (r11) | b8e485c (r16) | 54a2926 (r17 HEAD) | How counted |
|---|---|---|---|---|---|
| Registry rows `^| S\d{3}` in `corpus/SOURCES.md` | 30 | 31 | 41 | 46 | `git show <c>:corpus/SOURCES.md \| grep -cE '^\| *S[0-9]{3}'` |
| Tier A / C at HEAD | — | — | — | A 43, C 3 | python count of `corpus/SOURCES.md` registry column 4 |
| Status at HEAD | — | — | — | mined 36, queued 5, rejected 5 | python count of column 8 |
| `corpus/knowledge/*.md` | 12 | 13 | 15 | 15 | `git ls-tree --name-only <c> corpus/knowledge/ \| grep -c '\.md$'` |
| Criteria rows `^| KQ` in `corpus/QUALITY.md` | — | — | — | 22 | `grep -c '^| KQ[0-9]*' corpus/QUALITY.md` |
| Capabilities | sources-registry | +ollama-offline-evidence-replay (r14) | +live-llamacpp-lifecycle (r16) | unchanged (`SCORECARD.md:692-696`) | SCORECARD round sections |

The scorecard states A 38 → 43 and mined 31 → 36 for round 17 (`SCORECARD.md:689-690`). HEAD reproduces A 43 and mined 36. I did not recount the pre-round values; they are cited, not reproduced.

### Trend-label history (author label → outside label)

| Round | Expansion | Quality | Discernment | Author source | Outside source |
|---|---|---|---|---|---|
| r11 | improved | improved | unchanged (pending) | `SCORECARD.md:279-280` | `corpus/lessons/round-11-verifier-spotcheck.md:198`: discernment improved |
| r12 | unchanged | improved | unchanged (pending) | `SCORECARD.md:336` | `corpus/lessons/round-12-verifier-spotcheck.md:123`: discernment improved, "supersedes the author's … unchanged" |
| r13 | unchanged | unchanged | unchanged | `SCORECARD.md:394` | `corpus/lessons/round-13-verifier-spotcheck.md:242`: discernment unchanged, sample agrees |
| r14 | improved | unchanged | unchanged | `SCORECARD.md:469-470` | `corpus/lessons/round-14-verifier-spotcheck.md:136`: discernment improved |
| r15 | unchanged | unchanged | unchanged | `SCORECARD.md:552-553` | `corpus/lessons/round-15-verifier-spotcheck.md:159`: discernment improved |
| r16 | improved | improved | unchanged | `SCORECARD.md:632-636` | `corpus/lessons/round-16-verifier-spotcheck.md:173-174`: quality improved, discernment improved |
| r17 | unchanged | improved | unchanged | `SCORECARD.md:698-702` | none yet |

[INFERENCE] The author ledger was deliberately not rewritten when outside closures arrived (the outside files say so). The result is that `SCORECARD.md` trend lines for r12, r14, r15 and r16 read "unchanged" for discernment while the outside closures for the same rounds read "improved". Anyone reading the scorecard alone gets the stale label.

### Expansion — verdict: unchanged (agree with author)

- Rows went 41 → 46 (S042–S046, `corpus/SOURCES.md:54-58`). Knowledge entries stayed 15. No capability row was added (`SCORECARD.md:692-696`).
- The five new rows re-anchor surfaces the lane already covered: llama.cpp `/health` (S042), signal and shutdown path (S043), Python `Popen.returncode` (S044), PIT vocabulary (S045), and the lane's own receipts (S046). That is depth on existing entries, consistent with the author's own test at `SCORECARD.md:95` ("No new frontier knowledge or consumer surface admitted").
- [INFERENCE] Registry growth alone should not be read as expansion. Rows that only ground an existing entry add depth, not coverage.

### Quality — verdict: improved (agree, bounded; three attacks below)

Evidence that holds on re-read:
- Criteria: KQ20–KQ22 appended (`corpus/QUALITY.md`, 22 rows total).
- Fault-control detector on a fixed subject: `runs/fault-controls-frozen.json` accepted 3 (F5, F6, F8, each `detected: false`); `runs/fault-controls-current.json` accepted 0, detected 8 of 8.
- Live controls: `runs/controls-frozen.json` accepted_bad 6, inconclusive 1; `runs/controls-current.json` accepted_bad 0, inconclusive 0, good_ok true.
- Live receipts: `live/receipt-{1,2,3}.json` each carry 11 checks, all `true`; `live/gate.txt` prints `VALID` three times with exit 0.
- Process: `M1` (append-only violation, `corpus/lessons/round-17.md:85`) was found, and `tools/sources-append-only.py` plus KQ22 now guard it.
- Appended corrections: `PROVINCE.md` +12/−1 (round-17 note at line 70 on; `git show --numstat 54a2926`), `corpus/knowledge/llamacpp-loading-lifecycle.md` +63, `corpus/README.md` +17, `SKILL.md` +32 (`git show --stat 54a2926`).

Attacks that stand:

1. **Unequal mutant denominators in the C1 headline.** `SCORECARD.md:680` reads "frozen 7 of 8 applicable killed → current 10 of 10". The frozen check.py has `site_missing` 2 (M6 `ignore-served_model`, M7 `ignore-route-match`); the current check.py has 0 (`runs/mutants-grid.json`, cells `full/tests_probe-verdicts_check.py` vs `full/check.py`). Under KQ20, `site_missing` is "not applicable, never survived", so the rule is followed. But the two mutants that test the new grading are therefore absent from the frozen denominator, and the headline reads as like-for-like. [L1 fills after falsify: state the denominators beside the headline.]
2. **M8 frozen survivor is a crash, not a pass.** `runs/mutants-grid.json` frozen/full M8 `malformed-output-passes` = `survived`. `corpus/lessons/round-17.md:163` concedes "the frozen gate crashes on that input either way". A traceback with exit 1 is indistinguishable at exit-code level from a graded failure, so "survived" measures the detector's inability to tell crash from pass, not an accepted-bad. Recorded, not hidden; it does not change the 3 → 0 fixed-detector count.
3. **Own-work rows carry tier A.** Every own-work row is tier A: S030 (`corpus/SOURCES.md:42`), S034 (:46), S041 (:53), S046 (:58). No tier definition is visible in `corpus/SOURCES.md`; a grep for a definition returns only the scoped-tiers sentence (line 5). [INFERENCE] A lane's own receipt graded tier A sits on the same footing as vendor code. S046's teaches cell describes the pinned build ("On the pinned build the ready `/health` body is exactly"), supported only by the three lane-owned runs. Scope cell is honest; tier is not. Route to the tier-definition owner before the pattern becomes precedent.

### Discernment — verdict: unchanged (agree with author; pending non-author sample)

- No round-17 outside spot-check exists: `corpus/lessons/` contains `round-17.md` and no `round-17-verifier-spotcheck.md`. Author seats are not credited: `corpus/lessons/round-12-verifier-spotcheck.md:97` states "author-dispatched round seats are not credited as outside review".
- [INFERENCE — not credited] Upstream re-open by this seat. Fetched llama.cpp `704366d7…` `server-context.cpp`, `server.cpp` and Python 3.14 `subprocess.html` to scratch and matched the admitted quotes: `server-context.cpp:5289` "error and loading states are handled by middleware"; `:5297` `res->ok({{"status", "ok"}});`; `server.cpp:33-34` "Received second interrupt, terminating immediately."; `:575` "this call blocks the main thread until queue_tasks.terminate() is called"; `:590` `return 0;`; `subprocess.html:364` "A negative value -N indicates that the child was terminated by signal". All agree with S042–S044. This does not sample the rejected candidates, so it is not an admit/reject sample.
- [L1 fills after falsify: non-author round-17 admit/reject sample, or the explicit statement that none exists.]

## SHONEN

- [~] SKILL.md contains real decision tables, error patterns, checklists, cited sources → Author assertion, unchanged this round: `SKILL.md:125` §Decision table, `SKILL.md:191` §Checklist; round 17 appends §Round-17 gate grading (`SKILL.md`, +32). No outside verifier file cites these sections: `grep -ln 'Decision table\|Error signatures' corpus/lessons/*verifier*` exit 1. Stays `[~]`.
- [~] At least one end-to-end domain task executed and logged in LOG.md → Round 17 adds `.ufo/waves/round-17/live/receipt-{1,2,3}.json` (11/11 `kama-llamacpp-live/v2` checks each; `live/gate.txt` `VALID` ×3, exit 0). Lane-owned unregistered loopback fixture only: `registry/history/latest.tsv` still lists 3 `DEAD` rows (grep count 3); `PROVINCE.md:70-76` says the fixture is "still **pending L0 ratification**". Stays `[~]`.
- [~] Instructions executable by an agent without oral context → `SKILL.md:191` §Checklist and `corpus/knowledge/snapshot-history.md` §Run it. Counter-evidence: round-17 records two seat-level instruction failures despite written rules, M6 (fleet-root misroot and out-of-bound read, `corpus/lessons/round-17.md:90`) and M7 (invocation error with relative paths, `:91`), with no mechanical guard. Stays `[~]`.
- [~] No cross-domain bleed (PROVINCE.md still accurate) → `PROVINCE.md:70-76` round-17 note keeps the fixture exception open; `corpus/lessons/round-16-verifier-spotcheck.md:7` "does not ratify the PROVINCE fixture exception, which is pending L0". Stays `[~]` until L0 rules.

## Commands run (exit codes)

- `git clone -q /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/ScribeReportTrends-clone && git -C … checkout -q 54a29268…` → exit 0; `rev-parse HEAD` returned `54a29268e2083caa2b1e0d54ee1e7d90961302f3`.
- Python stdlib JSON and registry-count reads of `runs/*.json`, `live/receipt-*.json`, `corpus/SOURCES.md` → exit 0 (one first attempt on a wrong `cells[0]` index raised TypeError, exit 1; re-run on `cells[1]`/`cells[3]` exit 0).
- `git show <c>:corpus/SOURCES.md | grep -cE …`, `git ls-tree --name-only <c> corpus/knowledge/ | grep -c …` for c in 1e41928, 3285cdf, b8e485c, cff9e62, 54a2926 → exit 0.
- `git show --stat 54a2926`, `git show --numstat 54a2926 -- PROVINCE.md`, `git show 54a2926 -- PROVINCE.md SHONEN.md SKILL.md` → exit 0 (read-only).
- `curl -sfL` ×3 to `/tmp/ScribeReportTrends-scratch/` (raw.githubusercontent.com llama.cpp 704366d76 ×2; docs.python.org 3.14 subprocess) → exit 0 each.
- `grep` reads of quotes in scratch and lane → exit 0; `grep -ln 'Decision table\|Error signatures' corpus/lessons/*verifier*` → exit 1 (no matches, the result itself).
- No lane tool or gate was executed; no lane file was written except this report.

## Installs

None. Tools used were already present: `git`, `curl`, `python3` (stdlib), `grep`. `pacman` was not invoked (host pause in effect).

## Limitations

- I verified stored artifacts and upstream quotes; I did not re-run `fault-controls.py`, `controls.py` or `mutants.py` (not needed for trend labels, and the lane rule forbids in-lane runs).
- The discernment note is an upstream re-open by a seat that is not outside review; it is labelled [INFERENCE] and not credited.
- Pre-round counts (r10, r11, r16) are reproduced from git history; the scorecard's own intermediate figures (r16 A 38, mined 31) were cited, not reproduced.

## Scratch

`/tmp/ScribeReportTrends-clone` and `/tmp/ScribeReportTrends-scratch` are removed at the end of this run (see the final command).
