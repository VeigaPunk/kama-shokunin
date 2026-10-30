# Draft — `corpus/lessons/round-64.md` §Mistakes rows and §Wave results (round 64, wave f)

Seat: SB05LessonAndLog (leaf, advisory; no subagent dispatch). Axis: calibration. Milestone: draft lesson and LOG.
Sources read: `.ufo/waves/round-64/controls/freeze.txt` (base `0c1eff3c`, freeze `f6a4ea9a`, AMENDMENT 1 / 1a / 1b),
`.ufo/waves/round-64/b/*.md` (42 reports), `.ufo/waves/round-64/b/b-results.json` (42 rows, all `note: null`),
`.ufo/waves/round-64/controls/` receipts, `corpus/lessons/round-64.md` (landed at `361c620c`), `LOG.md:2530-2537`,
`SCORECARD.md:3348-3389`, `corpus/QUALITY.md:520-537`, `corpus/SOURCES.md` (276 rows at tip).
Every pointer below is a path:line in the lane at `361c620c` unless stated. Nothing here was run; every counter line
quoted is a committed or on-disk receipt, re-read, not re-executed by this seat.

## 0. What this draft is, and what already exists at the tip

Four of the five requested rows already exist in the landed lesson, written by the L1 at `23f341c8` (`git show
23f341c8 -- corpus/lessons/round-64.md`): rows 1, 2, 3, 4 and 8 are the socket-bound counter, the over-strong kill
rule, the wrong idle rule, the cap-text/code mismatch and the `git add -N .` incident. This draft therefore does
not create them; it (i) re-derives each against the wave-b files, (ii) tightens every pointer to a path:line, and
(iii) corrects three statements in the landed text that the files no longer support — the MT06 report-file
sentence (`corpus/lessons/round-64.md:44`), the `tracked=1536` receipt gap (row 8) and the rows-11/12 placement
(detail in §3 and in the LOG draft's notes 1, 3 and 4).

Landed structure defect to repair when the rows are re-landed: rows 11 and 12 sit **after** the `## Wave results`
heading (`corpus/lessons/round-64.md:42` is the heading; `:47` and `:48` are rows 11 and 12), so two Mistakes rows
are not inside the Mistakes list.

## 1. `## Mistakes` — the five requested rows (draft text)

Format follows the landed convention: class · evidence pointer · captured-by · fix.

**M-A. vacuous/survivor (provenance)** · the round-63 C1 counter bound the socket and a self-reported pid, and loaded
its ownership helper from the tree under judgment; two forged tools passed 44/44 · evidence
`.ufo/waves/round-63/w1/out/MT15C1FakeConsistent/forge.out:1` and `sleeper.out:1` (both `met=True ... 44/44`,
`errors=0`), `corpus/lessons/round-63-verifier-spotcheck.md:38` (falsification row) and `:41` (ruling: the counter
satisfies "is the child" with an inherited socket fd and does not check that the process is llama-server), and
`corpus/lessons/round-63.md:25` (the attribution class) · captured-by KQ106 (`corpus/QUALITY.md:521`, admitted in
round 63 as "not yet shown able to fail") · fix: the round-64 counter replays both forgeries as controls
(`forge` family 3/3 in `controls/c1-final-prewave-runs.txt:2`) and the pre-wave mutants kill the hollowed binding
(`controls/c1-mutants-prewave.txt`); KQ107 (`corpus/QUALITY.md:529`).

**M-B. vacuous (kill rule)** · the freeze's C1 kill rule said "a v2-schema or schema-relabelled tool accepted";
wave-b CR03DoNothing K1c — a v2 file with the schema string changed and a hand-written holder block — is accepted
with `met=True`, because the held child in those runs really is the pinned server answering, so the process property
the claim names already held at the base tool · evidence `.ufo/waves/round-64/b/CR03DoNothing.md:27` (candidate
table row K1c, `61cfb6c9`), `:38` (the `met=True ... 76/76 ... errors=0` line), `:53-55` (§3.1 "The counter accepts a
schema-relabelled v2 tool with a hand-written block"), `:105-107` (§3.5, the kill-rule clause), `:128` (mutant table:
K1c, K2, K3, K5 **SURVIVED**); the frozen clause itself at
`.ufo/waves/round-64/controls/freeze.txt:44` and the amended reading with the honest disclosure at `:165-174` ·
captured-by none · fix: AMENDMENT 1 narrows the clause to "a tool whose receipt omits the holder bookkeeping
accepted" and the freeze states both readings (`freeze.txt:165-174`); KQ114 (`corpus/QUALITY.md:536`). **Not
repaired**: C1 verifies the process property the base tool already had, with an instrument that now proves it; the
tool-side bookkeeping is not a graded artifact (`freeze.txt:173-174`).

**M-C. scope (host-state rule)** · the freeze/brief rule "the refusal's own printed foreign-server pid set equals
the counter's pgrep set at the same moment" cannot hold: `other_pids_seen` is a union over the whole ~21 s polling
window, not a snapshot-bounded set, so the printed set contains pids that appear in neither the before nor the after
`pgrep` · evidence `.ufo/waves/round-64/b/X10EnvIdleProbe.md:22` ("Subset? NO. `other_pids_seen` is the union over
the whole ~21 s polling window ... Counter-examples to 'subset of before-union-after': runs 1 and 3"), the three
host-busy runs at `:15-17` (runs 1 and 3 carry the transient pids; run 2 was a subset), and `:26` (`all_ports_closed:
true` is printed in both outcomes, so stdout alone cannot distinguish "ran and closed" from "never ran"); the wrong
clause at `.ufo/waves/round-64/controls/freeze.txt:77-78` and the corrected rule disclosed at `:218-223` · captured-by
KQ105 only in part (`corpus/QUALITY.md:520`) · fix: the rule the counter implements — host-busy only when exit 2, receipt
error `host-not-idle-before-K1`, `host_idle.ok` false, and every pid present in **both** `pgrep -x` snapshots inside
`other_pids_seen` — stated in `freeze.txt:218-223`; KQ114.

**M-D. attribution/scope (credit rule)** · the freeze named caps 5/30/14 (`:39-41`) while `run_controls` credited the
seven live fake-tool scenarios at an undeclared cap of 99, so the printed `met=True` depended on a cap the freeze
never declared; the evaluator self-test's envelope case was refused on the cap, not on the named check ·
evidence `.ufo/waves/round-64/b/RV02CounterCode.md:34-37` (D3, including the instrumented failure-set sizes
`detach 2, proxy 6, canned 16, stale_old 21, stale_future 21, preload 1, pathcopy 4`, of which four exceed cap 5 and
would have escaped) and `:39-41` (D4) · captured-by none · fix: the amended cap rule states the rule exactly — a live
fake tool holding a genuine receipt copy has no cap but must show no receipt-level failure, "the earlier text
implied a cap for it; the code used 99" (`freeze.txt:161-164`) — and the evaluator grows from 3 to 8 planted cases
(`freeze.txt:141-142`, `controls/c1-mutants-a1.txt:37-38` mutant `veto_noop` → `eval_selftest=7/8`); KQ115
(`corpus/QUALITY.md:537`).

**M-E. landing (lane index)** · the L1 ran `git add -N .` in the lane while reading a patch; the lane index was
mutated in place and the incident was caught by `jj-lane.sh state` reporting `tracked=1536` — intent-to-add, nothing
committed · evidence `corpus/lessons/round-64.md:38` (the L1's own account) and `.ufo/reports/round-64/kama.md:13`
(fleet report: "`git add -N .` in the lane" among the mined mistakes) · **the number has no committed receipt**: a
lane-wide and fleet-wide search for `tracked=1536` returns only the lesson row itself and the wave-f item text; no
`jj-lane.sh state` output was committed. The mechanism is independently reproducible — `scripts/hyaku/jj-lane.sh:180`
counts `git status --porcelain` lines matching `^[ MADRCU][MADRCU ]`, and `git add -N .` emits exactly the ` A`
lines that pattern matches (reproduced in a scratch fixture: 20 intent-to-add paths → `tracked=20`; receipt
`.ufo/waves/round-64/f/out/SB05LessonAndLog/intent-to-add-mechanism.txt`) · captured-by the wave-context rule "never
`git add`/`git add -N` in the lane" (`.ufo/waves/round-64/gen-f.py:21`) · fix: none needed beyond naming it; all later
lane commits used named paths, and the lane index carries **no** intent-to-add entry today (0 index entries with the
empty blob `e69de29b` that are absent from the HEAD tree, checked against `git ls-files -s` and `git ls-tree -r HEAD`).

## 2. `## Wave results` — wave b (42 seats)

Roles from `b-results.json` (`agent` field): mutation-tester 13, executor 10, scout 6, critic 4, reviewer 3, scribe 3,
connector 2, sentinel 1 = 42; every row carries output and `note: null`, so no dead seat is inferable.
"Survivors" is the seat's own count at the freeze-commit instrument `f6a4ea9a`, not a re-run.

| Seat | Role | Survivors found at the freeze instrument | Disposition at the amended tip |
|---|---|---|---|
| MT01DumpableHide | mutation-tester | 2 of 4 (O3, O4: pre-started non-dumpable helper holding a dup of the listener) | **Not fixed** — acknowledged limit (`freeze.txt:176-177`) |
| MT02ReusePort | mutation-tester | 1 (V3 root dup + forwarder; V4 escaped live in 1 of 4 receipt-producing runs) | Class addressed in the instrument (any-uid unreadable grading, `freeze.txt:136-137`); the seat's own M1 counter mutant killed V3 via `bind_holders` alone (`.ufo/waves/round-64/b/MT02ReusePort.md:43`) — **no seat re-ran V3 against the amended counter** |
| MT03PidRace | mutation-tester | 2 binding (c, c1: SIGSTOPped real child, connection theft) | **Fixed** — `bind_state` S/R/D at both snapshots (`freeze.txt:122-123, 136`) |
| MT04ArgvSpoof | mutation-tester | 4 real (B4, B5, R1, E1: extra flag / alias / env key; C1 is an expected genuine pass) | **Fixed** — exact argv list + environ allowlist (`freeze.txt:120-121, 134-135`) |
| MT05EnvInject | mutation-tester | 6 (F1 bind-mount ns, F2 `/proc/<pid>/mem`, F3 extra env key, F5 HOME value, F6 ptrace tracer, F8 preload) | F1/F3/F5/F6/F8 **fixed** (`bind_ns`, `bind_trace`, `bind_state`, environ allowlist — `freeze.txt:121-122, 134-136`); **F2 not fixed** — acknowledged limit (`freeze.txt:177-178`) |
| MT06MapsLib | mutation-tester | 6 of 9 forgeries (model/lib identified by path + sha256 only) | **Fixed** — AMENDMENT 1a `bind_ref_files`; the seat's tally after the fix is "KILLED 9 of 9" (`freeze.txt:184-193`) |
| MT07RefAgree | mutation-tester | 1 (b2 root forwarder); 9/1200 probe text collisions = false-fail risk, not a bypass | Collisions **fixed** by the three-distinct-answers draw rule (`freeze.txt:139-140, 203-205`); b2 is the MT02 V3 class — not re-verified after the amendment |
| MT08HoldWindow | mutation-tester | 1 (f2 hidden listener holder); b survived as an equivalent, not a forgery | **Not fixed** — acknowledged limit (`freeze.txt:176-177`) |
| MT09ReceiptTamper | mutation-tester | 2 forgeries (T04b resealed completion text; T03b child swapped for a second pinned server) | T04b **fixed** by the receipt-request/answer binding (`freeze.txt:120, 131-134`); **T03b not killable by replay** (pinned servers are deterministic — seat's own recommendation, `.ufo/waves/round-64/b/MT09ReceiptTamper.md`) |
| MT10CopyModes | mutation-tester | 5 of 11 mutants (a2, d1, d2, e1, e2b) + 2 forgeries (F1 future-dated hold.json, F2 extra argv flag) | **Fixed** — structural forge/relabel builders, hold.json mtime upper bound, exact argv (`freeze.txt:121, 126-129, 137`) |
| MT11Selftest | mutation-tester | 4 of 7 evaluator mutants (M2, M3, M4, M5) | **Fixed** — evaluator self-test grows 3 → 8 planted cases (`freeze.txt:141-142`); the seat's tally at the freeze tip was "kills 3/7" (`.ufo/waves/round-64/b/MT11Selftest.md`) |
| MT12ProxyLeak | mutation-tester | 1 (F1: one extra env key after the allowlist) | Counter side **fixed** (environ allowlist); the seat's **tool-side** defect (the allowlist forwards `LD_LIBRARY_PATH`, `LLAMA_ARG_THREADS`, `XDG_CACHE_HOME` into the answering child) is **not fixed** — the tool is byte-identical to the freeze (`freeze.txt:130-131`) |
| MT13ProbeTokens | mutation-tester | 1 forgery (genuine child + replayed receipt) + 4 counter mutants (m03, m06, m07, m08) | **Fixed** — receipt bound to this run (`freeze.txt:119-120, 131-134`) |
| CR01PredicateCode | critic | 11 clause findings A–K on the freeze counter (A tool bytes not pinned; I "loading nothing from the tip"; K one-sided self-test) | B, D–H, J, K **fixed** by AMENDMENT 1; **A and I remain open at the measured tip** — the counter carries no digest of the tool and still reads the tool text and both forge patches from the tip blob (`tools/round64-c1-counter.py` at `23b3fdb1`, `blob(repo, tip, 'tools/kama-completion-live.py')`, `blob(repo, tip, '.ufo/waves/round-64/controls/forge-A-realchild.patch')`); not named in any amendment |
| CR02ControlTargeting | critic | 4 (V1, V2, V3 credit a wrong name; N1 no control names `live_server_sha`) | Work-dir reuse and the hold.json upper bound **fixed** (`freeze.txt:137-139`); "named-check presence, not causation" is narrowed by the credit rule but not made causal (`freeze.txt:161-164`) — **not fixed** as a class |
| CR03DoNothing | critic | 4 (K1c, K2, K3 accepted; K5 accepted) | K1c–K3 addressed by the narrowed kill rule with both readings stated (`freeze.txt:165-174`); **K5 not fixed** — acknowledged limit (`freeze.txt:178-179`) |
| CR04OwnershipScope | critic | 1 (S1 composed window-takeover forger: `met=True fails=[]` 4 of 4) | **Unknown** — CR04 is named in neither the amendment nor the limit list; the new `bind_state`/`bind_trace` checks bear on its parts but no receipt confirms a kill |
| RV01ToolDiff | reviewer | tool-side H1, H2 (holders scan blind to unreadable tables; scan placed before the hold window, never re-taken) + M1–M5, L1, L2 | **Not fixed** — instrument-only amendment, tool byte-identical (`freeze.txt:130-131`); H1's class overlaps the any-uid grading at the counter side only |
| RV02CounterCode | reviewer | 12 defects D1–D12 | D1–D6, D8–D12 **fixed** (`freeze.txt:119-129`); **D7 not fixed** — blanket `/usr/lib` exemption acknowledged (`freeze.txt:179`) |
| RV03SourcesGate | reviewer | S529 scope clause overreaches; rule-1 gate absent (`gate_present 0/4`) | Lesson Gate written (`corpus/lessons/round-64.md:5`ff) and S529–S534 added; rows stay `queued` with `used-by —` (`corpus/SOURCES.md`), so the knowledge entry is still not admitted |
| SN01Sandbox | sentinel | F1 (tool tampers the pinned fixture and restores it → `met=True`), F2, F3, F5 | F1 **fixed** by the uncached model digest + AMENDMENT 1a (`freeze.txt:126-127, 186-188`); **F3/F5 open** (writes outside `--work`; `patch`/`git` resolved via PATH) |
| SC01ProcFd | scout | 0 (S529 verified; two mild flags) | S529 admitted as a sourced row; flags carried in the lesson Gate |
| SC02ProcStat | scout | 0 (S530 confirmed, field numbering) | S530 admitted |
| SC03ProcEnvCmd | scout | 0 (S531/S532 verified, scope clauses incomplete) | S531/S532 admitted with the scope clauses carried in the Gate |
| SC04Considerthese | scout | 0 (proposal 2 unimplemented) | Landed as KQ113 + the checker under `.ufo/waves/round-64/b/out/SB01Knowledge/recheck-quotes.py` (`corpus/QUALITY.md:535`); **the checker is not in `tools/`** |
| SC05Quarantine | scout | 0 (slice unchanged 7/7; S200 re-fetched absent) | Nothing adopted |
| SC06ProcTcp | scout | 0 (S049 does not support the `st == 0A` rule) | Not adopted as a new admitted row; S536 rejected in the Gate |
| SB01Knowledge | scribe | 0 (draft entry; quotes 27/27) | Draft only, not admitted — no revision seat ran in attempt 1 (`corpus/lessons/round-64.md:3`); attempt-2 SB04 produced a revised draft, still unadmitted |
| SB02QualityDraft | scribe | 0 (3 draft mistake rows + KQ107–KQ111) | Landed as KQ107–KQ115 (`corpus/QUALITY.md:529-537`) |
| SB03LessonGate | scribe | 0 (Gate draft, 15/15 quotes located) | Landed in `corpus/lessons/round-64.md:5`ff |
| CN01CrossClaim | connector | 0 (3 contradictions K1–K3) | K1 **fixed** by the corrected idle rule (`freeze.txt:218-223`); K2 **fixed** by the distinct-answers draw (`freeze.txt:139-140`); **K3 open** (idle proof forgeable by a PATH-shadowed `pgrep`) |
| CN02SiblingOverlap | connector | 0 (13 sibling lanes with `/proc` hits; no sibling ships a pinned-binary verifier) | Nothing absorbed; 2 contested rows reported, not taken |
| X01C2Counter | executor | 0 survivors of 20 counter mutants after 2 first-version mutants (C11, C17) were fixed with 9 added controls; 8 tip-side mutants | Instrument built and integrated byte-exact (`freeze.txt:216`); C2 at the tip: `pinned=13/13 regress_flipped=12/12 printers_rejected=12/12 controls_rejected=120/120 errors=0 met=True` (`controls/c2-prewave-tip.txt:14`) |
| X02Regress1 | executor | 0 (3 one-line regressions) | Integrated into `registry/capability-regress-r64.tsv` (`freeze.txt:216`) |
| X03Regress2 | executor | 0 (3 regressions); risk flagged: the context-capacity row cannot be flipped by pattern absence | Integrated (`freeze.txt:216`); the counter classifies that row by exit code + `cc.json` error/`host_idle`, not by the pattern |
| X04Regress3 | executor | 0 (3 regressions); finding: the `hexrun-census` row's unmutated run was already false at the freeze tip (`unknown=1`) | Integrated; fixed by one `hexrun-ledger.tsv` row (`freeze.txt:217`) |
| X05Regress4 | executor | 0 (3 regressions); one planted `MUTABLE_COLS` edit survived the tool's own selftest (coverage gap, not used for the row) | Integrated (`freeze.txt:216`) |
| X06Reconciler | executor | 0 (`closure_ptr` conjunct + SCORECARD calibration-row patch, 5 planted fixtures) | Integrated byte-exact (`freeze.txt:217`) |
| X07Tally | executor | 0 (`shortcut-tally.py` rounds 56–63 reader: `tally_disclosed` 1/8 → 8/8, selftest 10/0, 6/6 mutants killed) | Integrated (`freeze.txt:217`) |
| X08StabilityC1 | executor | 1 flake in 5 runs (run 4: `runfield` 3/4) | **Fixed** — draw needs three distinct non-empty reference answers + redraw (`freeze.txt:128, 139-140, 203-205`); 3 of 3 pre-wave runs `met=True` (`controls/c1-final-prewave-runs.txt`) |
| X09ScansTip | executor | 0 (`digest-ledger` unknown=0; `hexrun-census` unknown=1) | Fixed by one ledger row (`freeze.txt:217`); `unknown=0` at `9549c0b9` (`measured/attempt2/digest-at-9549c0b9.out`, `hexrun-at-9549c0b9.out`) |
| X10EnvIdleProbe | executor | 0 (3 host-busy K1 runs; the rule itself was wrong) | Rule corrected and disclosed (`freeze.txt:218-223`) |

Wave-b totals as recorded by the L1: 10 survivor classes against the freeze-commit C1 counter and 12 code defects
(`RV02CounterCode.md` D1–D12) — `.ufo/reports/round-64/kama.md:13`; the seat-level breakdown is the table above and
is the more precise form.

## 3. Attribution note the L1 needs

The AMENDMENT section of the freeze names **21 of the 42** wave-b seats (20 by seat prefix, plus X03Regress2 inside
the range "X02-X05"): `freeze.txt:119-129` (the "Why" list), `:175-179` (the acknowledged limits), `:184`
(MT06MapsLib, AMENDMENT 1a), `:216-217` (the C2 build disclosure: X01, X02–X05, X06, X07, X04/X09), `:220`
(X10EnvIdleProbe) and `:128` (X08). The other **21** seats' findings reach the amended instrument only through the
amendment's generic clauses ("unreadable fd tables of ANY uid graded when the process started after the tool";
"the evaluator self-test grows from 3 to 8 planted cases"; "forge and relabel builders are structural").

Of those 21, the nine that carry a survivor are MT02ReusePort, MT07RefAgree, MT09ReceiptTamper, MT12ProxyLeak,
RV01ToolDiff, CR01PredicateCode, CR02ControlTargeting, CR04OwnershipScope and SN01Sandbox — the table in §2 marks
each one's disposition; the remaining twelve are source-verification, draft, scan and connector seats with no
survivor to disposition. Three further points of attribution: MT02's V3 is killed by the seat's own M1 counter mutant
by the very mechanism AMENDMENT 1 adopts ("unreadable fd tables of ANY uid", `freeze.txt:136-137`), but no seat
re-ran V3 against the amended counter, so its kill is a code-level inference, not a measurement; MT09's T03b and
CR04's S1 are named in neither the amendment nor the limit list; and RV01's H1/H2 are tool-side defects in a tool the
amendment explicitly left byte-identical (`freeze.txt:130-131`), so no amendment can have closed them.
