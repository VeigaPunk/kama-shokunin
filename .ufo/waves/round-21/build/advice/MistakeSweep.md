# MistakeSweep — named mistakes without a fail-capable fix (rounds 15–20)

Seat `KamaR21.MistakeSweep-6` (leaf, build wave). Pin: lane `a29bb84abbb8b4d328f5970a89e448330a3a42ac`, read as committed bytes from a scratch clone. The lane working tree also holds a concurrent uncommitted change to `tools/kama-llamacpp-live.py` (run R41); this seat did not read or use it. Run ledger with exits: `out/MistakeSweep/RUNS.md` (IDs R01–R43 below). Scripts and fixtures: `out/MistakeSweep/`. No lane tracked file written; scratch `/tmp/kama-r21-MistakeSweep` removed at the end.

**Top 3:** MS-01 seat boundary violations · MS-02 copied and quoted counts not bound to a revision · MS-04 KQ22 guard exit path and comparator unpinned by its selftest. Thirteen candidates in total (§3). Seven have a checker demonstrated to exit 1 on a witness and 0 on a control (MS-01, 02, 03, 04, 05, 07, 09); MS-11 has a demonstrated comparator inequality (R39); the rest are not demonstrated.

## 0. Method and ranking

- **Candidate** = a mistake named in a round Mistakes table, routed defect, disclosure, or deferred debt in rounds 15–20 or the round-15..19 spot-checks.
- **Captured-by** = the QUALITY criterion (KQ) or rule the lesson cites; `none` if no criterion, rule or check is cited.
- **Named, no fail-capable fix** = the record's fix is prose, a context clause, disclosure, an appended correction, or "open"; no checker exits 1 on a witness of the mistake.
- **Shown able to fail** = in scratch, the fix exits 1 on a witness and 0 on a control (run IDs given).
- **Ranking** [INFERENCE, judgement]: (1) impact on safety or evidence integrity, (2) recurrence across rounds while open or prose-only, (3) a demonstrated failing fix.

## 1. Top 3

### 1. MS-01 — Seat boundary violations: forbidden roots and prohibited commands (recurs R15–R20)

- **Class:** safety and process. Seats read session stores, sibling-lane files and no-enumerate roots, ran prohibited commands, or launched a wildcard listener.
- **Evidence (recurrence):**
  - R15: `corpus/lessons/round-15-verifier-spotcheck.md:60-61` (grep matched `.ufo/interactive-sessions/`; `LedgerR1` evaluated the guard in-process; `GuardHarness` used AST parsing despite instructions); `corpus/lessons/round-15.md:94-99`.
  - R16: `corpus/lessons/round-16.md:72` (M5 sibling-lane reads, "context bounding clause"); `:169` (M6 seats ran `measure.py` and `check-receipt.py --selftest`); `:170` (M7 `find ~/.config ~/.omp`; "open … no fail-capable fix exists yet"); `:78-81` (routed item 3: "No QUALITY criterion: this is dispatch hygiene"); `corpus/lessons/round-16-verifier-spotcheck.md:187` (M7 "remain open").
  - R17: `corpus/lessons/round-17.md:90` (M6: recursive grep printed `interactive-sessions` lines; "still no mechanical guard"); `:121-125` (routed item 6: "no mechanical guard stops a seat running a measurement").
  - R18: `corpus/lessons/round-18.md:187-191` (seat requested `--host 0.0.0.0`; a wildcard listener existed 14.2 ms).
  - R20: `corpus/lessons/round-20.md:107-113` (count-only traversal of no-enumerate roots, "out of bounds").
- **Captured-by:** context clauses (`round-16.md:72`, `:169`, `:170`); disclosure (`round-17.md:90`); QUALITY `none` (`round-16.md:80-81`).
- **Mechanical coverage today: none.** `grep -rln "interactive-sessions" tools tests SKILL.md AGENTS.md corpus/QUALITY.md corpus/README.md` → exit 1 (R12); `grep -rniE "reread|load order|protocol-load|load receipt" tools tests` → exit 1 (R11).
- **Fix, shown able to fail:** `out/MistakeSweep/bound_scan.py` flags command lines that name a forbidden root (`interactive-sessions`, `~/.omp`, `~/.config`, `~/.ssh`, another seat's `/tmp/kama-r…`) or a prohibited command (`measure.py`, `check-receipt.py --selftest`, `check.py --selftest`, `kama-llamacpp-live.py`, `llama-server`, `strace`). The exclusion flag `--exclude-dir=interactive-sessions` is stripped before matching, so the form the R16 lesson prescribes is not access.
  - Positive fixture, four commands taken from the R15–R17 incidents: 4 violations, exit 1 (R14).
  - Negative fixture, the exclusion form plus two ordinary reads: 0 violations, exit 0 (R15).
- **Limits** [INFERENCE]: the scanner needs a complete export of each seat's tool calls, including `read`, `grep` and `glob` arguments, not only bash. The L1 may obtain these from `history://<agent>`; not tested here. It detects command shapes, not reads that were never logged.
- **Integration obligation:** run the same scanner over each wave context (context text is also a command list) and over each seat's export before its report is accepted. Exit 0, or a disclosed exception row.

### 2. MS-02 — Copied and quoted counts drift; no count is bound to a revision (recurs R17–R20)

- **Class:** numeric provenance. Rounds R17, R18 and R19 each recorded a wrong count when written; R20 found and corrected R19's stale copies (M3); `corpus/lessons/round-19.md:11` is wrong now.
  - R17: `corpus/lessons/round-17.md:87` (M3, summary 36/41/2 against strict 34/40/0).
  - R18: `corpus/lessons/round-18.md:316-317` and `LOG.md:1122` ("five confirm, two partial") against committed verdicts 4/3 (`corpus/lessons/round-18-verifier-spotcheck.md:130-132`).
  - R19: `corpus/lessons/round-19-verifier-spotcheck.md:184-187` (routed item 2: `required=3`, `selftest 5 cases`, `missing=3`, "three registry-row digests" against the four-row registry); `SCORECARD.md:823-824`; `corpus/lessons/round-19.md:103-106` (selftest 15, not 5); `:121-123` (76 against 77 mutations).
  - R20: `corpus/lessons/round-20.md:77` (M3 "copied counts stale"; fix = appended corrections, prose; criterion KQ20). `round-20.md:151` records the registry grown to 17 rows.
  - Now wrong: `corpus/lessons/round-19.md:11` describes `python3 tools/citation-provenance.py` as printing `required=4 found=4 verified=4`. At `a29bb84` it prints `required=17 … verified=17 missing=0`, exit 0 (R08); the registry has 17 rows (R29). The round-19 corrections are revision-bound to `028235e`, which had 4 rows (R28).
- **Captured-by:** KQ20 numeric provenance (`round-20.md:77`); KQ27 (`corpus/QUALITY.md:144`: "Every quoted count is tied to the measured revision and independently enumerated"). Both are criteria; no checker implements either.
- **Fix, shown able to fail:** `out/MistakeSweep/count_sweep.py`. Rule: each `required=N` token must carry `@<rev>` on its own line, and N must equal the registry row count at that revision.
  - Fixture of four tokens: line 1 `required=17@a29bb84` passes; line 3 `required=4@028235e` passes; line 2 unbound fails; line 4 `required=3@a29bb84` fails against 17 rows. Exit 1, 2 violations (R26).
  - Live round-19 set (four documents): 11 tokens, all unbound on their own line, exit 1 (R27).
- **Limits:** strict same-line binding gives false positives for historical lines whose revision sits in the paragraph (`round-19.md:103` names `028235e` in its paragraph). Those need an adjudication column or `@028235e` on the line. The checker covers `required=` only; `selftest N cases` and `N mutations` need the same mechanism (not demonstrated).

### 3. MS-04 — KQ22 guard: exit path and comparator unpinned by its selftest (named R18 survivors)

- **Class:** detector fail-open. The guard's own verdict path is not tested.
- **Evidence:**
  - Code (`tools/sources-append-only.py` at `a29bb84`): `:265` cell comparison `if old[c] != new[c]`; `:350` `run_check` exit `return 1 if violations else 0`; `:525-531` the selftest computes its own verdict (`got_exit = 1 if violations else 0`) and never calls `run_check`.
  - Named survivors: `corpus/lessons/round-18.md:296-297` (deferred as named debt: "AppendCells (comparator-normalisation and exit-mapping survivors)"); `.ufo/waves/round-18/falsify/advice/AppendCells.md` lines 37–51 and 61–62 (mut-ci, mut-normws and mut-exit each pass the selftest byte-identically and misgrade real pairs).
  - Closed: the R17 survivor "drops the opened cell" (`corpus/lessons/round-17-verifier-spotcheck.md:249-254`) is killed now (R05).
- **Captured-by:** KQ22 (`corpus/QUALITY.md:123`). Its "shown able to fail" evidence is a one-off manual run on `b8e485c..ccc4bb3`, not a selftest case.
- **Demonstrated:**
  - Base selftest 42/42, exit 0 (R02). mutA (`run_check` returns 0) selftest 42/42, exit 0 (R03): survives. mutB (casefold comparison) 42/42, exit 0 (R04): survives.
  - On the pair KQ22 cites, `b8e485c..ccc4bb3`: base exit 1 (R06); mutA prints `VIOLATION S041 … anchor changed in place` and exits 0 (R07). A round-end KQ22 run under mutA would pass silently.
- **Fix, shown able to fail:** `out/MistakeSweep/kq22_killer.py` builds three throwaway git repos and runs the guard CLI (`run_check`).
  - base 3/3, exit 0 (R16). mutA 1/3, exit 1 (R17). mutB 2/3, exit 1 (R18). mutC 3/3, exit 0 (R19): the killer does not over-kill, and mutC is caught by the in-suite selftest (R05).
  - Proposed integration [INFERENCE, not run]: add the same git-backed cases to the guard's `run_selftest` and route its verdicts through `run_check`. The lane is read-only for this seat.

### Paste-ready rows for `corpus/lessons/round-21.md ## Mistakes` (top 3)

| Class | Evidence pointer | Captured-by | Fix / failure obligation |
|---|---|---|---|
| Seat boundary: forbidden roots and prohibited commands recur | `round-16.md:170`; `round-17.md:90`; `round-15-verifier-spotcheck.md:60-61`; `round-20.md:107-113` | context clauses; disclosure; QUALITY none (`round-16.md:80-81`) | `out/MistakeSweep/bound_scan.py` over exported seat commands and wave contexts: incident fixtures 4/4 exit 1; allowed forms 0/3 flagged, exit 0 (R14, R15) |
| Copied and quoted counts not bound to a revision | `round-17.md:87`; `round-18-verifier-spotcheck.md:130-132`; `round-19-verifier-spotcheck.md:184-187`; `round-20.md:77` | KQ20; KQ27 (prose only) | `out/MistakeSweep/count_sweep.py`: fixture exit 1 on unbound and mismatched tokens (R26); live round-19 set 11/11 unbound, exit 1 (R27) |
| KQ22 guard exit path and comparator unpinned by its selftest | `round-18.md:296-297`; `tools/sources-append-only.py:265,350,531` | KQ22 (`QUALITY.md:123`) | `out/MistakeSweep/kq22_killer.py`: base exit 0 (R16); mutA exit 1 (R17); mutB exit 1 (R18) |

## 2. Why the top three

- MS-01 has the highest impact (KQ5 boundary: session stores and credential-shaped material). It has recurred in four rounds. R16's own record says "open … no fail-capable fix exists yet" (`round-16.md:170`), and no mechanical check exists (R11, R12).
- MS-02 has produced wrong copied counts in each round from R17 to R20, each caught by an outside check or the author. KQ20 and KQ27 exist, but nothing checks them. The present-tense command claim is now wrong (R08).
- MS-04 is the one fail-capable gate whose verdict path is unpinned. The current guard is correct on the cited pair (R06); the defect is that a regression of its exit mapping or comparator would pass its selftest (R03, R04, R07).

## 3. Ranked backlog (4–13) and all candidates

| Rank | ID | Class | Evidence | Captured-by | Fix; shown able to fail? |
|---|---|---|---|---|---|
| 4 | MS-03 | In-place rewrite of filed prose outside SOURCES | `git show 30ed378 -- corpus/lessons/round-18.md` rewrites line 42 (R09); `round-18.md:427-438`; `round-19-verifier-spotcheck.md:56-58, 192-193`; SHONEN in-place extensions `round-16-verifier-spotcheck.md:42`, `round-17-verifier-spotcheck.md:155` | PROTOCOL §Evidence standard (prose); KQ26 `QUALITY.md:143`; KQ22 covers SOURCES only | `out/MistakeSweep/append_only_lines.py` (numstat deletions, per-file allowlist for SHONEN checkboxes): `30ed378` exit 1 (R20); `33a6777` +57 −0 exit 0 (R21). **Yes** |
| 5 | MS-12 | Named detector survivors deferred as debt | `round-18.md:288-302`; `FreshGate.md` (FG1–FG4 survive the built-in gate selftest); `FreshAppend.md` (AP2, PV1, PV2 survive). Sites still pristine at `a29bb84`: `tests/llamacpp-live/check-receipt.py:919, 1030, 1056, 2347` (R36), no `201` case (R37); `.ufo/waves/round-18/dispatch-provenance.py:362, 430` (R38); `tools/sources-append-only.py:110` | none (deferred) | One selftest case per survivor, from the seats' distinguishing witnesses. **Not demonstrated**; sites re-verified only |
| 6 | MS-05 | Pointer rot: line-range pointers into growing files | `LOG.md:1231-1237` (210-215, 217-222), `round-20.md:82, 187, 206`, `round-18.md:285, 447` (209-213). Current S051 clarification at `corpus/SOURCES.md:218-223` (R13) | KQ7 (`QUALITY.md:29`), KQ13 (`:52`); prose "refer to heading" (`round-18.md:447-451`) | `out/MistakeSweep/pointer_check.py`, anchor = the claim's final clause: 210-215 exit 1 (R22); 217-222 exit 1 (R23); 218-223 exit 0 (R24). A heading-only anchor passes 217-222 (R25), so anchors must be final clauses. **Yes** |
| 7 | MS-06 | Protocol order: canonical reread after dispatch | `round-18.md:184-186` ("No exemption is claimed"); `round-20.md:95-98` ("does not satisfy … retrospectively") | none | [INFERENCE] protocol-load receipt (file sha256 and read time) that must precede the first dispatch. No tool or token exists (R11). **Not demonstrated** |
| 8 | MS-07 | Harness hang on a non-serving stub (round-16 M3) | `round-16.md:70`, `:173-177` ("M3 stays open as a harness design gap"); `round-16-verifier-spotcheck.md:187`; `round-17.md:121-124`. Root cause now patched: `tests/probe-verdicts/check.py:459-461`; no selftest mutant pins it (R43) | none; 30 s and 600 s timeouts are backstops | `out/MistakeSweep/hang_stub.py` (no serve_forever): exit 124 (R30). `hang_bounded.py` (3 s join): exit 2 (R31); control `--serve`: exit 0 (R32). Mechanism demonstrated; the mutant for check.py still needs adding. **Yes (mechanism)** |
| 9 | MS-08 | Seat misroot: reports written at fleet root, then moved | `round-16.md:71, 177-179`; `round-17.md:90` | round-prompt absolute-path clause; manual L1 sweep (a command, not a gate) | [INFERENCE] gate comparing fleet-root `git status` with a round-start snapshot; exit 1 on new paths. **Not demonstrated** |
| 10 | MS-09 | Scratch residue after round close | `round-19-verifier-spotcheck.md:120-123, 208-210` (67 dirs, 5.95 GiB); `round-20.md:80, 99-105` | seat cleanup rule (prose) | `out/MistakeSweep/residue_gate.py`: 48 `kama-r*` dirs at run time, exit 1 (R33); empty root exit 0 (R34). **Yes**. Scope must be the round's own prefix |
| 11 | MS-10 | "Falsify wave" claimed for a wave that spawned nothing | `round-19.md:113` (spawned 0, 66 refused); `round-19-verifier-spotcheck.md:188-190`; `round-20.md:79` | disclosure rule (prose) | [INFERENCE] validator refuses a falsify claim unless the validation receipt shows spawned ≥ 1. **Not demonstrated** |
| 12 | MS-11 | Whole-output agreement inferred from equal summaries | `round-20.md:81` (M7); `round-18/runs/c2-survivors.json` vs `.stdout`: top-level keys equal, `results` lengths 5/5, `results` equal: False (R39) | KQ14 (`QUALITY.md:41`), KQ17 (`:72`); no comparator | Comparator over canonical full `results` returns unequal on this pair (R39). **Yes (comparator)**; a summary check alone does not catch it |
| 13 | MS-13 | Wave premises not re-checked before dispatch | `round-17.md:89` (M5: `.lock` ignore claim; impossible "36/43/0 + 5") | none; procedure "run its check and paste output" | [INFERENCE] premise block in the wave context with command and output digest. **Not demonstrated** |

## 4. Routed items in the round-15..19 spot-checks (status)

- **R15:** items 1–2 resolved (`round-15-verifier-spotcheck.md:165-166`); item 3 → MS-01; item 4 (environment bindings) resolved by `round-16.md:82-84`; items 5–6 are prose appends, not re-verified.
- **R16:** items 1–2 resolved in R17 (`round-17.md:95-105`); item 3 → MS-01; items 4–5 prose appends (`round-16-verifier-spotcheck.md:185-186`); item 6 → MS-07, MS-12, MS-01.
- **R17:** R1–R4 addressed in R18 (`round-18.md:95-99`; not re-verified); R5 (KQ21: six v2 checks lack retained bad controls, `round-17-verifier-spotcheck.md:236-238`) not re-verified; R6 (receipt-gate trust boundary) partly addressed in R18, not re-verified; R7 (detector survivors): the opened-cell survivor is killed (R05), fault-control survivors deferred (`round-18.md:293-294`) → MS-12; R8 is orchestrator-owned.
- **R18:** items 1–3 corrected by erratum in R19 (`round-19-verifier-spotcheck.md:48-50`); item 4 (residual role split without dispatch record) is an appended label (`round-18.md:443-445`), not ranked; item 5 (named residuals) → MS-12 and TreeCap.
- **R19:** item 1 registered (commit `7a6bc91`); item 2 → MS-02; item 3 → MS-10; item 4 → MS-03; item 5 census receipts moved to `build/out/CensusR19Retro/` (`round-19.md:116-119`); item 6 (residual provenance label) not ranked; item 7 carried list: crash-as-rejection (`round-20.md:75`) and observed-branch regression (`round-19.md:107-108`) addressed in R20; 13 citations registered (`round-20.md:151`); S051 line anchor → MS-05; TreeCap (symlinked soname pin) is being closed by this round's C2 and is excluded here to avoid double counting; TreeDeterminism, GridDefaults, SentinalSecrets and SCORECARD §Planned not re-verified; item 8 → MS-09; item 9 is operator-owned.

## 5. Excluded (fixed with evidence, or not reviewed)

- Fixed with a fail-capable check and not carried: R16 M1 (KQ19), M2 and M8; R17 M1 (KQ22 for SOURCES), M2 (KQ20/21), M3 (`count-verdicts.py`), M4 (`dispatch-provenance.py`; residual closed by R18 M5); R18 M1–M7 and M9; R19 M1–M3 (selftests); R20 M1 and M2 (KQ25). The R17 opened-cell survivor is confirmed killed (R05). Fix claims beyond these were not re-run.
- R18 M8 (publication gap): the counter output is digest-bound (`round-18-verifier-spotcheck.md`, output-binding row). Not ranked.

## 6. Limits and [INFERENCE] marks

- No lane gate, official counter, measurement tool or live probe was run. The citation counter was run only in the scratch clone (R08). The round-18 falsify reports were read, not re-run.
- Demonstrations test each proposed checker on fixtures and on committed bytes. They do not show that seat transcripts can be exported in the required form (MS-01), or that the L1 will run the checkers.
- Ranking and the design of unexercised fixes (MS-06, MS-08, MS-10, MS-13) are [INFERENCE].
- The lane tree is dirty (`tools/kama-llamacpp-live.py`, R41). Analysis used committed `a29bb84` only.

## 7. Install and cleanup record

- Installs or updates: none. Tools used: git (host), python3 3.14.8 (host), coreutils `timeout`, `pgrep`.
- Processes: the hang demonstrations ran under `timeout` and exited; `pgrep` found none afterward (R35).
- Lane: no tracked file written. This report sits at the assigned advice path; `out/MistakeSweep/` holds scripts, fixtures and `RUNS.md`.
- Scratch `/tmp/kama-r21-MistakeSweep` removed after the final checks.
