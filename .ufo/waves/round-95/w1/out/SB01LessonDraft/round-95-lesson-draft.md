# Round 95 — the router file-state verdict is byte-decided; the setter table decides per entry point

L1 `KamaR95` (attempt 1). Base `2011161d5e5612fa953708cf54084b7f10ce99b1`. Plan `plans/round-95-claims.md`
(freeze `c798e831`); amendments 1–3 narrow the filed properties; previous closure
`corpus/lessons/round-94-verifier-spotcheck.md` (rejected-honest-stop; C1 wording narrowed, C2 not verified,
routed D2/D3).

## Gate

Rows opened this round come from the pinned llama.cpp `b12177` codeload archive
(sha256 `f50a52f4ba45dd5b4b906db97cf230ce2e3b1117a0b9017411322ecba63eea13`, verified by `sha256sum` in this seat's
scratch), fetched 2026-11-08. Each row names its per-file raw URL and the file sha256; the raw bytes are the archive
members byte for byte (`cmp` clean, this seat's own check, recorded in
`.ufo/waves/round-95/controls/sources-opened.out`).

| Candidate | Decision | URL / access date | Located quote (≤25 words) and location | Reason | Flip condition |
|---|---|---|---|---|---|
| S616 `tools/server/server-context.cpp` @ b12177 | **admit** (A, code, mined) | https://raw.githubusercontent.com/ggml-org/llama.cpp/b12177/tools/server/server-context.cpp — 2026-11-08, sha256 `e0e43f22…a973` | `for (int i = 0; i < params_base.n_parallel; i++) {` (line 1489) | The realisation of the slot count: one slot per `n_parallel`, plus its log (1486), speculative hand-off (1496), second loop (1522) and batch floor (1587) — five rows that consume the value and choose none. | The pinned file stops containing the `params_base.n_parallel` loop, or the realised slot count stops being derived from `params_base.n_parallel`. |
| S617 `tools/server/server-schema.cpp` @ b12177 | **admit** (A, code, mined) | https://raw.githubusercontent.com/ggml-org/llama.cpp/b12177/tools/server/server-schema.cpp — 2026-11-08, sha256 `7f4d7c35…6b54` | `->set_hard_limits(1, params_base.n_parallel)` (line 65) | The schema publishes the slot count as the upper hard limit of the per-request slot field, so a resolved 0 or 1 clamps the published limit. | The schema stops publishing `params_base.n_parallel` as a hard limit, or the slot field is renamed away from the slot count. |
| `tools/cli/README.md` @ b12177 | **reject** (docs, C-class lead only) | https://raw.githubusercontent.com/ggml-org/llama.cpp/b12177/tools/cli/README.md — 2026-11-08, sha256 `a5544e6c…c008` (234 lines) | "`-np, --parallel N` … (default: 1)" (line 56) | The page states a default of 1 for `--parallel`, which round-94's measurement falsified for the embedded server (measured 1/4/5/6/0 slots; `-1` auto → 4). It is the source of the overstatement, not authority for the CLI's served slot count. | The page documents the embedded server's resolution instead of the flag default. |
| `tools/server/README.md` @ b12177 | **reject** (docs, C-class lead only) | https://raw.githubusercontent.com/ggml-org/llama.cpp/b12177/tools/server/README.md — 2026-11-08, sha256 `eafc1b53…a137` (2620 lines) | "`total_slots` - the total number of slots for process requests (defined by `--parallel` option)" (line 1019) | Opened and read for the slot-count question: the page ties `total_slots` to the `--parallel` *flag*, and its own `/props` example prints `"total_slots": 1` (line 1005) — the count of one server, not the resolved rule. It documents no per-entry-point precedence and cannot decide `R20`/`R21`; the code rows (S593/S596/S606/S616/S617) do. | The page documents the resolved slot count per entry point (server, cli, router-child) instead of the flag it is derived from. |

`status`/`recheck`/`used-by` changes on existing rows: none. S616 and S617 are new rows (`mined`, recheck
`on-release`, used-by `SKILL.md`; `corpus/SOURCES.md:371-372`, each 11 cells). Census before → after: 355 → 357 rows
(`git show c798e831:corpus/SOURCES.md | grep -c "^| S[0-9]"` → 355; `grep -c "^| S[0-9]" corpus/SOURCES.md` → 357);
`scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama` exit 0, last line
`kama ok /home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md`.

## Mistakes

**M1 — a discriminator that did not discriminate, discovered only by running the control.**
Class: `vacuous`. Evidence: the first C1 control run against the round-94 probe (`--allow-clock`, 20 distinct slow
files) graded `W03 ok=1` — twenty files cost less than the base's constant 60 s wrapper, so the pass was never
truncated and the "red before" did not exist. Re-measured this round by the same route
(`tools/round95-router-budget.py --rev a27656a454b1a2364f8b6e55f42fbca8c2e86ee4 --allow-clock --slow-files 20
--skip-load --burners 0`): `W03-slow-x40 ok=1 … run1=…/46.30s run2=…/58.35s` and
`cells=10 mismatches=0 positive_mismatches=0 … w03_seconds=58.3` — the base probe was **green** at twenty files,
confirming the population was the only reason the control failed to bite. Captured-by: the plan's do-nothing control,
which is why it ran before the freeze. Fix: `SLOW_FILES` 20 → 40 and a margin guard in the counter — the honest pass
must cost ≥ 1.25 × the base constant or nothing is claimed
(`tools/round95-router-budget.py:90`; guard receipt `.ufo/waves/round-95/controls/c1-discriminator-guard.out`,
`could-not-evaluate: W03 natural pass 16.6s < 1.2 x 60s`, exit 2). Shown able to fail: at 8 files the M1 probe
refuses the same way (this seat's receipt `m1-guard-8-files.out`, exit 2).

**M2 — the plan's own cell list and the counter's committed bytes disagree.**
Class: `scope`. Evidence: `plans/round-95-claims.md:46` says "W03 twenty distinct slow" and the disclosed limit at
:65 prices W03 at "~50 s of CPU at 20 distinct slow files", but the frozen counter's bytes carry `SLOW_FILES = 40`
(`tools/round95-router-budget.py:88`) and its docstring prices W03 at "40 x ~2.0 s = ~82 s" (line 49). The measured
W03 pass is 81.7–99.7 s (`measured/c1.out` `w03_seconds=82.5`, `measured/c1-m1b.out` `w03_seconds=99.7`), never the
~50 s the plan claims. Captured-by: the wave-1 C1 review (`w1/RV01ProbeDiff.md` NOTE-6) — the frozen C3 token arm
cannot see prose, only backticked metric names. Fix: recorded in `plans/round-95-amendment-3.md` NOTE-6 rather than
repaired, because the plan is frozen; the lesson and the counter carry the measured 40-file/82 s numbers instead.

**M3 — a control receipt whose named files never existed.**
Class: `evidence trail asserted, not written`. Evidence: the frozen plan's K2 kill rule names "the base harm receipt
the M1 commit carries" (`plans/round-95-claims.md:58`) and the measurement-time receipt list names `harm-base.out`,
`harm-tip.out`, `measured/c1.out`, `measured/c2.out`, `census-end.out` (:28) — of those, `harm-base.out` and
`harm-tip.out` exist at **no** revision: `git log --all --name-only -- '.ufo/waves/round-95/**' | grep -i harm`
yields only `controls/harm-pair.out` (7db1c54a) and `controls/harm-tip2.out` (ed3bd05f), and `git ls-tree -r
--name-only HEAD -- .ufo/waves/round-95/` lists those two, not the two named in the plan. This is round-94's M5
defect repeated one class down: the freeze-time receipts (7) are all present at `c798e831`, but the measurement-time
half of the same sentence was never committed under the names it claims. Captured-by: the wave-1 C3 control
(`w1/EX01FreezeAuditControl.md` F4) and `plans/round-95-amendment-2.md`. Fix: the wave's `EX02HarmSuites` seat
produced the pair under the names `controls/harm-pair.out` and `controls/harm-tip2.out`; the plan's names are corrected
by the amendment rather than satisfied by them.

**M4 — the freeze audit's own "status not rejected" arm reads the wrong column.**
Class: `instrument reads a different field than its predicate names`. Evidence: `tools/round95-freeze-audit.py:76-77`
stores `cells[8]` while the SOURCES table's status is `cells[7]` (`corpus/SOURCES.md:11` header: `id | source | kind
| tier | scope | anchor | teaches | status | opened | recheck | used-by`), so `sources_status` returns the access date
and the `rejected` test at :128 can never fire: `sources_status(repo,'HEAD')['S027']` → `'2026-10-19'` while S027
carries `| rejected |`. Re-verified this round by forging a plan that cites two rejected rows (S027, S591): the audit
answers `cited=16 unresolved=0 met=True`. A plan may cite the lane's rejected rows and pass. Captured-by: the wave-1
C3 control (`w1/EX01FreezeAuditControl.md` F1) with the same reproduction. Fix: the counter is frozen (K2), so
`plans/round-95-amendment-2.md` narrows the filed C3 property to presence + token names and routes the arm fix to
round 96.

**M5 — the token arm checks a metric's name, never its value.**
Class: `predicate weaker than its sentence`. Evidence: `tools/round95-freeze-audit.py:118-121` tests only
`name not in blob`, so the quoted values are never compared. Re-verified this round: doctoring every value on the
amendment-1 C2 predicate line (`population=999 rows=999 bound=999 … decisions=2 decisions_bound=2 met=False`) still
answers `tokens=24 matching=24 met=True` with `token_missing: []`. The arm is also line-scoped — it fires only on a
line that also holds a backticked `python3 tools/<tool>.py`, which is why every shipped plan reports `tokens=0` at its
own freeze (`.ufo/waves/round-95/measured/c3.out`: `tokens=0 matching=0`). Captured-by: the wave-1 C3 control
(`w1/EX01FreezeAuditControl.md` F2). Fix: `plans/round-95-amendment-2.md` states the filed property as "metric
**name** present"; value equality is routed to round 96.

**M6 — the rejected-row and value arms are dead on a plan that cites rejected rows.**
Class: `predicate not reachable at the frozen commit`. Evidence: the frozen C3 predicate is `FREEZE_AUDIT …
unresolved=0 met=True` at the freeze commit F, but at F the plan cites S616/S617, whose rows land at M2 — the run
answers `receipts=7 present=7 missing=0 tokens=0 matching=0 cited=17 unresolved=4 met=False`, exit 1
(`.ufo/waves/round-95/measured/c3.out`). The frozen wording was unreachable because the freeze precedes its own
sourced work. Captured-by: the round's own C3 run at F. Fix: `plans/round-95-amendment-1.md` narrows C3 to the
property the frozen counter enforces — at the landed tip
`FREEZE_AUDIT receipts=9 present=9 missing=0 tokens=24 matching=24 cited=14 unresolved=0 met=True`, exit 0
(`.ufo/waves/round-95/measured/c3-amended.out`).

**M7 — a receipt committed while its producer was still writing it.**
Class: `landing`. Evidence: `719214fa` committed `.ufo/waves/round-95/measured/c1.out` with two lines — the running
counter had created the file but not yet finished; `git show 719214fa:…c1.out | wc -l` → 2 against the finished
receipt's 22 lines, and the predicate it was meant to carry (`ROUTER_BUDGET95 cells=…`) was absent. Captured-by:
nothing — the plan's own C3 audit checks that a *path* exists, not that its bytes contain the predicate (that limit
is disclosed in the plan). Fix: `ca531563` commits the complete receipt; the freeze-time/measurement-time split now
says a measurement receipt is committed only after its producer exits. Shown able to fail: the same file at
`719214fa` has no `ROUTER_BUDGET95 cells=` line, at `ca531563` it does.

**M8 — two new registry rows written outside the table and with seven cells.**
Class: `scope`. Evidence: appending the S616/S617 rows at end of file put them after the round-92 correction prose,
and the census answered `E12 S616 row outside Registry section` / `E01 S616 fields=7` — the rows had omitted
`status | opened | recheck | used-by`. Captured-by: `scripts/sources-census.sh validate --file corpus/SOURCES.md`,
which is exactly the gate for this class. Fix: rows inserted after S615 inside the Registry and completed to 11 cells
(`corpus/SOURCES.md:371-372`, 11 cells each); census re-run exit 0.

**M9 — a digest tail invented before it was measured.**
Class: `attribution` (fabricated citation digits). Evidence: the first S616/S617 rows carried 16 true hex characters
and 48 characters written from pattern, not from `sha256sum`; the measurement gives
`e0e43f22fd2357a1e76ad6b8996b099d62615dd973de33feaa02fa0ee1a2a973` and
`7f4d7c35a10d0deb6eef8a02a222a0ecf3295b7ec6c65b512e3f241b47df6b54` — re-derived this round from the raw downloads
(`sha256sum`) and confirmed byte-for-byte against the pinned archive members (`cmp` clean). Captured-by: nothing in
the round — the census does not check a digest's digits, only the row shape; a non-author re-fetch would have caught
it. Fix: both rows replaced with the measured digests, and the Gate table above quotes them from `sha256sum` output.

## Dispositions of the round-94 closure (D2/D3)

- **D3 C1 residuals.** The per-file wall clock (SC02 F2/MT01 NOTE-3) is removed from the decision, not relocated; the
  constant wrapper (SC02 F3/M10) is replaced by a count-derived limit; the counter's sanity gate (SC02 F1) is a
  byte-level fixture oracle that no host load can perturb. The slow `/props` verdict (SC02 F4) is **not** claimed and
  is disclosed in the plan and in `plans/round-95-amendment-3.md`: the honest verdict for an unread autoload flag is a
  vocabulary question this round does not settle.
- **D3 C2 residuals.** R20/R21 replace R18/R19 with one row per entry point; the whole-struct carrier and the
  realisation reads are population rows; `[default]`/`[*]` scoping is graded by a decision token. The prose truth of
  the nine decision rows stays a non-author read (`w1/RV02SetterRows.md`), never the counter.
- **D2** carried, not claimed: `round75-instruments` (`APPEND_DEBT … bad_rows=19`) and the host Ollama listener on
  8080 that keeps `round78-instruments` red.
