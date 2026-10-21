# ConnClosure — routed-disagreement map from MANIFEST rounds[428] (kama r23 closure) into round 24

Seat `KamaR23-2.ConnClosure-2` (connector, leaf member; no dispatch, no production edits).
Read read-only: `/home/vgpnk/Projects/shokunin/MANIFEST.json` `rounds[428]`
(`kama`, `round 23`, `type closure`, `admitted false`, `verdict rejected-harmed`,
`closed_at 2026-10-21T17:44:26Z`, reviewer `CloseMori22`) and the filed prior report
`/home/vgpnk/Projects/shokunin/.ufo/reports/round-23/kama.md` (fleet commit `410b511`).
Lane base for the round: `kama-shokunin@0df800e896f6bce285a81e794ad4ae1d1e6c3a71`
(`preregistration.json:3`). Observed lane tip during this seat: `ed1cc3a`
("round-24: restore local promisor verdicts with required-object diagnosis,
independent oracle, mutation contract, and no-trade learning").
Host: git 2.56.0, Python 3.14.8, linux x86_64. Tools installed/updated: none.
All fixtures below are local and synthetic; no network transport was used or attempted.

---

## Verdict

**Partially.** The r23 closure's four named routes are individually traceable and
three are discharged in the pinned r24 tree; **one route (R23-H2, the Git
prerequisite) is carried but not discharged**, and one *unrouted* disagreement is
still open in the r24 lesson surface (below, §5). The lane therefore still owes
the closure one thing it has not yet done, and the *quality* trend the closure
harmed is restored in code but not yet in the written carry.

---

## 1. Every routed disagreement, and where r24 stands

The closure's `notes` field names four routes (`MANIFEST.json` `rounds[428].notes`).
Each is quoted below with its exact wording, followed by the r24 state **as
observed in the pinned tree**, not as claimed.

### R23-H1 — "restore correct ordinary complete-promisor/filtered-clone cases
without re-enabling lazy fetching, or seek an explicit operator-approved mission
change; do not silently reclassify them out of no-harm controls."

**r24 state: DISCHARGED (verified by re-running the closure's own witness).**
The closure's harm witness is `MANIFEST.json` `rounds[428].verification.harm_ruling`:
a `git clone --filter=blob:none --no-local file://…/kama-shokunin` whose server
ignores the filter (complete objects, promisor metadata present), audited at
rounds 10-22, gave `rc2` under the r23 base where the frozen r22 auditor gave
`rc0` with *exactly the same JSON verdict* as on the full lane clone.

Reproduced here from the pinned tree (`out/ConnClosure/`):

| arm | lane clone | exit | summary JSON |
|---|---|---|---|
| r23 base `0df800e` | promisor-marked, complete | **2** `partial clone (promisor pack)` | — |
| r22 frozen `4fe9339` | promisor-marked, complete | 0 | identical to full clone |
| r23 base `0df800e` | full clone | 0 | reference |
| **r24 candidate `ed1cc3a`** | **promisor-marked, complete** | **0** | **identical to full clone** |

The r24 candidate's summary and all nine finding tuples
(`kind`, `token`, `corrected_by`) are byte-identical across all four arms
(measured in `out/ConnClosure/probe-result.json` companion `grid3.json` run and
the JSON comparison in §3). No lazy fetch is possible: `--no-lazy-fetch` is
retained in `GIT_ISOLATION` (`tools/report-landing-audit.py:91-95`), and the
r23 legacy grid's own execution-sensitive rows still report
`commands_executed 0`, `tracebacks 0`, `timeouts 0` (see §3).

The clause "do not silently reclassify them out of no-harm controls" is met:
`T01-blobless-partial-clone` is no longer an ungraded `tradeoff` row — it is a
graded `control` row expecting exit 0 (`tests/report-audit/repo-state-grid.py:689-690`,
diff `0df800e..ed1cc3a`), and the r24 grid grades the amended view
(`tests/report-audit/promisor-grid.py:851`).

### R23-H2 — "document/support the new Git floor as an operator-approved
environment prerequisite, not an unchanged axis; T01 alone suffices for rejection."

**r24 state: CARRIED, NOT DISCHARGED — and this is the gap that remains.**
The lane is explicit and honest about it, which is the correct posture but is
not the route being discharged:

- `corpus/lessons/round-24.md:83-84`: "The Git>=2.45 prerequisite is explicitly
  not approved or repaired: R23-H2 is carried as the round24 L0 question."
- `SKILL.md:852-854`: "Git>=2.45 remains an inherited prerequisite, not restored
  older-Git support or operator approval; R23-H2 is carried in the round24 L0
  question."

The route asks for an *operator-approved environment prerequisite*. A lane-side
L0 question is the correct mechanism for obtaining that decision, so the
mechanism is right; but the r24 tree carries no evidence that the question was
*asked and answered* — no L0 ruling exists. The closure's wording is precise:
"document/**support** the new Git floor as an operator-approved environment
prerequisite, not an unchanged axis." A carry with no ruling is still an
unchanged axis. **This remains open and is the single largest un-discharged
route.**

### R23-C1 — "report falsify 69 lane reports rather than 68 (68 final session
replies plus RowC03 durable lane output); 141 seats and 5 missing reports
otherwise correct."

**r24 state: DISCHARGED, and independently re-verified here.**
Counted directly from the r23 wave directory (read-only):

| wave | spec items | advice reports | missing |
|---|---|---|---|
| build | 68 | 67 | `RevClaimScope` |
| falsify | 73 | **69** | `RowC01Clean`, `RowF07LogFollow`, `RowF09SignatureProgram`, `CritOpenHonesty` |
| total | 141 | 136 | 5 |

(`.ufo/waves/round-23/build/spec.json` / `falsify/spec.json` `items[].name`;
`build/advice/*.md`, `falsify/advice/*.md`.) This reproduces the closure's
"69 … 141 seats and 5 missing reports" exactly.

The r24 tree carries the correction in the right place: `LOG.md:1417-1420`
records the 69/68 correction, and `LOG.md:1432-1444` (appended after
`CritEvidence`) refines its *provenance*: the literal "68 reports" is at
`corpus/lessons/round-23.md:178`, not in the filed fleet report (whose 73 seats
minus 4 missing already implies 69). That is the same conclusion
`out/CritEvidence/r23-corrections-append.md` reached, and it is the honest
form: the filed r23 bytes are immutable and the correction is appended.

**One qualifier the r24 tree states correctly and this seat re-checked:** the
"56 killed FIFO-process" claim is narrowed, not restated. `LOG.md:1438-1444`
records 56 as a *matching-process count* while a different listing pattern kept
40 truncated identity rows (38 `git`, one `gpg-agent`, one `scdaemon`), of which
only 19 tie to FIFO fixtures. The retained rows are in
`out/CritEvidence/r23-ps-listing-line156.txt` and
`out/CritEvidence/r23-ps-classification.txt`; the classification (`by program
{'git': 38, 'gpg-agent': 1, 'scdaemon': 1}`) is consistent with the claim.
`corpus/lessons/round-24.md:52` carries the same narrowing.

### R23-C2 — "fixture builders must assert actual repo top-level before `.git`
writes, keep own PID inventory before cleanup, retain timeout group-kill
controls."

**r24 state: DISCHARGED on the builder half (asserted top-level), and the
timeout/PID half is inherited unchanged from r23's already-landed fix.**

- The r24 grid's fixture builders resolve every repository path through a
  `fresh_root`/`under` pair that refuses to write outside the fresh root
  (`tests/report-audit/promisor-grid.py:116-137`), so a builder that resolved its
  pack directory by upward discovery (the r23 `RowF06LazyFetch` fleet
  contamination) cannot write into the fleet's `.git`.
- The r23 timeout/session-kill fix is inherited unchanged: the r23 lesson records
  that `run_case` starts each auditor in its own session and kills the session
  on timeout (`corpus/lessons/round-23.md:174`, M7), and the r24 grid reuses
  that harness shape.

---

## 2. The unrouted-but-binding disagreements inside the closure row

The closure row contains more than four routes; three of its
`verification.*` fields carry obligations that bind r24 even though `notes`
does not label them.

1. **`verification.rechecks` — the historical ledger and the auditor's byte
   identity.** The closure re-ran the historical ledger and required it
   byte-identical: rounds 10-21 and 10-22, with and without `--no-errata`,
   all four `(returncode, stdout, stderr)` triples byte-equal. r24 must not
   change the auditor's bytes in a way that moves the ledger, and must not
   edit any filed r23 report (append-only). r24 keeps the ledger in the
   retained r23 grid plus the new `promisor-grid`, and the r23 lesson and
   report bytes are untouched.
2. **`verification.routed_checks` — fleet conformance debt.** The closure
   records the four zero-byte `.promisor` markers written into the *real
   fleet* by `RowF06LazyFetch`'s upward discovery
   (`.ufo/waves/round-23/falsify/fleet-contamination/promisor-markers.txt`) and
   that the markers are now absent. r24's rule is to keep them absent; the
   top-level assertion in R23-C2 is what prevents recurrence.
3. **`verification.harm_ruling` — "the old verdict is correct, not merely an
   unsafe false verdict being replaced by refusal."** This is the reason the
   r24 repair is a *restore*, not a re-decision: r22's verdict on the marked
   clone was the right answer, and r24's obligation is to reproduce it
   exactly. §1's table is that obligation, measured.

---

## 3. Verification performed by this seat (bounded, local, offline)

| # | check | command | result |
|---|---|---|---|
| V1 | closure witness reproduced | `python3 auditors/base.py --lane-repo lane-marked --fleet-repo <fleet> --rounds 10-22 --json` (lane-marked = `git clone --filter=blob:none --no-local file://…/kama-shokunin`, detached `0df800e`) | r23 base → **exit 2** `partial clone (promisor pack)`; r22 frozen → exit 0; r24 candidate → **exit 0** |
| V2 | verdict identity across arms | JSON comparison of `summary` + all nine `(kind, token, corrected_by)` tuples | **identical** for r24-candidate/marked, r24-candidate/full, r22-frozen/marked, r23-base/full |
| V3 | r23 legacy grid, pinned tree | `python3 tests/report-audit/repo-state-grid.py --arm current --json` | `faults 26/26`, `contracts 4/4`, `controls 14/14`, `violations 0`, `tracebacks 0`, `commands_executed 0`, `timeouts 0`; only the two ungraded `open` rows (O01/O02) are unmet, as designed (`out/ConnClosure/grid-full.json`) |
| V4 | r23 closure-witness rows on the pinned tree | `… --arm current --case F06-lazy-fetch-command --case F23-promisor-pack-without-config --case T01-blobless-partial-clone --json` | F06 exit 1 `['landed-unresolved','unresolved-full-hash']` met; F23 exit 2 met; T01 exit 0 `[]` met (`out/ConnClosure/grid3.json`) |
| V5 | r24 promisor grid, r23-frozen arm | `python3 tests/report-audit/promisor-grid.py --arm current --case PG31… --case PG44… --case PG46… --case PG47… --case PG48… --json` | 5/5 graded rows met, 0 violations, 0 tracebacks, 0 timeouts, 0 harness leaks (`out/ConnClosure/pgrid-allroots.json`) |
| V6 | missing-object set M is **not transitively closed** | `probe5_6_7_closure.py` | a blob reachable only through a deleted ancestor commit is **absent locally and absent from M** while the missing commit is in M: `blob_in_M false`, `missing_commit_in_M true`, `M_is_closed false` |
| V7 | the **root set** of the missing-object walk decides the answer | `probe_roots_divergence.py` | with a present-but-ref-unreachable commit naming a missing blob: `--all` roots → `M=[]` (blob invisible); every-present-object roots → `M={blob}` |
| V8 | auditor A/B on the V7 shape | candidate vs. an `--all`-rooted variant of the same file | candidate → **exit 2** "unavailable required object: … is referenced by the history"; `--all` variant → **exit 1** `unresolved-full-hash` (a guessed absence) |
| V9 | no-harm direction of the same rule | candidate vs. `--all` variant, citation = fabricated hash, missing blob uncited | **both exit 1** `unresolved-full-hash` — an unrelated unavailable object is not a blanket precondition |
| V10 | cost of the diagnosis on the real repositories | `cat-file --batch-all-objects` + `rev-list --missing=print --stdin` | lane: 2224 roots, 0.021 s + 0.007 s, 0 missing; fleet: 5420 roots, 0.015 s + 0.024 s, 0 missing |

The lane and fleet both hold **present-but-ref-unreachable** commits (lane 1,
fleet 84, counted by `cat-file --batch-all-objects` minus `rev-list --all`), so
the V7 shape is not hypothetical for the audited repositories.

---

## 4. One bounded move (godspeed connector)

**Move: make the missing-object traversal's ROOT SET an explicit, tested
invariant of the r24 repair, and pin the `M`-closure fact in the grid.**

**Why this and not something else.** Every r24 proposal I read (CritUnknown's
candidate patch, ConnNoHarm's policy rows, CritBounds' conditions, CritNoTrade's
P/M/N formulation) agrees on *what* must be refused — a required object that
cannot be served — and disagrees only on *how the store's missing set is
computed*. `CritUnknown`'s patch roots the walk at `--all` (refs only);
`CritUnknown`'s own candidate output `out/CritUnknown/candidate.patch:157-159`
shows `rev-list --objects --no-object-names --all --missing=print`. The **landed**
candidate (`tools/report-landing-audit.py:635-677`, `present_roots`) roots it at
*every present commit, tree and tag* instead. V7/V8 show this is not a stylistic
difference: with `--all` roots, a citation to a blob that a present-but-
ref-unreachable commit names is **absent from M**, so a membership test reports a
**proved absence** (exit 1) where the truth is **unknown** (exit 2) — exactly
the r23 harm the closure ruled on, re-entering through a different door. The
landed candidate is correct here because it also refuses whenever a missing
tree or commit exists at all, so the opaque-hole fallback catches the shape V7
exposes.

**Proposed bounded move (one row, one assertion, no production behaviour
change):** add one grid case whose fixture holds a *present but
ref-unreachable* commit naming a *missing, cited* blob, with expected exit 2
and a reason class of "unavailable"; and add one assertion that the missing-set
computation is rooted at present objects rather than at refs. This pins the
distinction the current 47-row grid does not yet discriminate, and it makes V6
(M is not transitively closed) a stated, testable premise instead of an
unstated accident of implementation.

**Affected axes.**
- *Calibration* (the assigned axis, 7→7): improves — the repair's central
  claim ("never a guessed absence") becomes grid-enforced rather than
  implementation-dependent.
- *Operability* (the harmed axis, being repaired): unchanged-to-improved — the
  new row adds no refusal to any case the r23 base accepted; it only forbids a
  *wrong verdict* on a shape where the truth is unknown.
- *Quality* (the trend the closure harmed): improves — the round's evidence
  chain gains one row that closes a gap its own successor could otherwise
  reopen.
- *Coverage, depth, freshness, adjacency*: unchanged.

**Risks.**
1. The new fixture must keep the missing blob *cited* and the dangling commit
   *present*; a fixture that also removes the tree would be caught by the
   existing opaque-hole path (PG46/PG47) and would not discriminate the root
   set. I have the working fixture (`probe_roots_divergence.py`,
   `cites_the_missing_blob`).
2. The row must be paired with a no-harm twin that cites a *fabricated* hash in
   the same store and expects exit 1 (V9), or the grid could be satisfied by a
   blanket refusal. V9 shows the landed candidate already behaves this way.
3. Writing into the r24 grid or expectations file is an L1 production
   decision, not this seat's; this seat changed no production file.

**Verification the L1 would run.** `python3 tests/report-audit/promisor-grid.py
--arm both --json` plus the one new case, and the r23 legacy grid
`--arm current --json` for the no-harm half.

---

## 5. Missing route learning — one item not yet carried anywhere

The r23 lesson carried a fenced "Reported open, not claimed" list
(`corpus/lessons/round-23.md:185-208`): the near variants `RowF12, RowF21,
RowF22, RowF23, RowF26, RowC04`, `ExecSecondLanded`, `ExecAmbiguityFixture`,
`RevengeGitfile`, `CritTradeoffHarm H2`, `SentinelDoSW2`, the unisolated
sibling tools, and the surviving detector-coverage mutants `N01/N02/N03/D02/D03`.
**None of those tokens appears in the r24 lesson** (checked: every one of
`RowF12 RowF21 RowF22 RowF23 RowF26 RowC04 ExecSecondLanded ExecAmbiguityFixture
RevengeGitfile CritTradeoffHarm SentinelDoSW2 ConnSiblingTools` is absent from
`corpus/lessons/round-24.md`, `corpus/knowledge/error-is-not-a-verdict.md` and
`SKILL.md`). The *substance* is partly carried in prose in `SKILL.md:855-858`
("Gitfile/alternates identity, prefix ambiguity overwrite, duplicate Landed
sections, errata CR/FIFO handling, memory ceilings, live serving and
sibling-tool isolation remain unclaimed") — so the classes are not lost, but the
**row identifiers and the mutant survivors (`N01/N02/N03/D02/D03`) are not
carried anywhere in the r24 surfaces**, and the r23 lesson was the artifact that
held them.

This is not a new defect: it is the *same* carry gap the r23 falsify wave
recorded for r20/r21 (`ConnClosureRoutes` G1–G4, and r23's own
`corpus/lessons/round-23.md` fence). It is listed here because the closure's
`notes` says "Open near variants listed by author remain debt, not claims
resolved" — the r24 lesson must carry that debt forward explicitly, or the
debt is dropped a second time. The r24 lesson's own fence
(`corpus/lessons/round-24.md`) has no equivalent "carried prior debt" block.

Also unrouted but visible: the r23 lesson's weak selftest assertions —
`uncommitted-draft-uses-now` (`tools/report-landing-audit.py:1143-1144`, asserts
only `rc == 0 and not report_committed`) and `inherited-GIT_DIR-untouched`
(`:1282-1283`, asserts only that the decoy's object list is unchanged) — are
**still weak in the pinned r24 tree** (same two forms). The r21 route that named
them (`R21-SELFTEST-DEBT`) was never carried into the r23 lesson either, so this
is a three-round-old carry gap, not an r24 regression. It is out of r24's
preregistered scope (`preregistration.json:17` `not_claimed`), so it must not
be silently fixed — but it should be *named*.

---

## 6. Artifacts written by this seat

All under `.ufo/waves/round-24/build/out/ConnClosure/` (relative to the lane):

| path | what it is |
|---|---|
| `advice/ConnClosure.md` | this report (the only file under `build/advice/` written by this seat) |
| `auditors/{base,frozen,cand,cand_allroots,cand_pm07}.py` + `auditors/README.md` | read-only auditor blobs used for the A/B, with their provenance and sha256 |
| `probe.py`, `probe2.py`, `probe3.py`, `probe4.py` | the missing-set probes: blob vs. tree vs. commit in M; `--filter=blob:none` separation; no-fetch witness under a promisor store; `batch-all-objects` inventory |
| `probe5_6_7_closure.py` | the M-closure test (probe 7 is the corrected form; probe 6's first form was invalid and is superseded) |
| `probe_roots_divergence.py` | the root-set divergence test (V7) |
| `crosstest.py`, `holetest.py` | the cross-store and opaque-hole auditor A/Bs |
| `probe-result.json`, `probe2-result.json` … `probe7-result.json`, `probe5_6_7_closure-result.json`, `probe_roots_divergence-result.json`, `crosstest-result.json`, `holetest-result.json`, `shape-result.json` | their raw outputs |
| `grid3.json`, `grid-full.json`, `pgrid-allroots.json` | the three bounded grid runs (V3, V4, V5) |

Scratch (not part of the deliverable, heavy): `/fast/scratch/hyaku/kama-r24/ConnClosure/`.

## 7. What this seat did not do

- No production file, grid, expectations file, lesson, registry row or report was
  edited by this seat. All writes are under
  `.ufo/waves/round-24/build/advice/ConnClosure.md` and
  `.ufo/waves/round-24/build/out/ConnClosure/`.
- No fleet, sibling-lane, operator-config or `.jj` write; no commit; no push.
- No build, full-suite or falsification-wave run. The grid runs above were
  bounded to the closure-witness rows and five promisor rows.
- The 64-seat r24 falsification wave has not run; its results are not in this
  seat's evidence and are not characterized here.
- The V6/V7/V8 findings are **measured on local synthetic fixtures** and on the
  pinned candidate's bytes; they are not claims about a candidate that does not
  exist yet.
- `CritEvidence`'s session-transcript evidence (`out/CritEvidence/`) lives
  outside the lane; this seat read the derived classification file and the
  committed `LOG.md` text, not the transcript itself.
