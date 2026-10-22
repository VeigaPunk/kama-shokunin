# DocLog — kama r24 fresh falsification: LOG.md round-24 append chronology and the r23 evidence corrections

Leaf seat, read-only. No production file was edited; no suite, grid, network, transport or
execution payload was run. Only static source reads, git object reads and one offline
JSON/CSV measurement of already-filed bytes.

## Snapshot under test

| Item | Value |
|---|---|
| Pinned revision | `2e254a1763a9c08aa07fc53081287f506c447d84` (`2e254a1`, 2026-10-21 16:45:11 -0300) |
| Scratch clone | `/fast/scratch/hyaku/kama-r24/falsify/DocLog/repo` (own clone, `--no-hardlinks`, detached at the pinned revision) |
| `LOG.md` blob @ pinned | `52b62c07075d2e04836c6cd0e66c19ded8efe167` (sha256 `589419717296653e76af655ae826c3c4a2c7cc22dfd2e61d35245873a03fdd73`) |
| `LOG.md` blob @ r23 base `0df800e` | `4f85ca6816c4425dfe734dcde9d4308b9095958b` |
| Auditor @ pinned | sha256 `ea51bc35b71ac09f4c233e21a16be49af555e1333004a0fe166234de79edd220` |
| Frozen/base auditor | sha256 `da5041a8191e0e6ec385adc7c659ddc7544a835aff65dd45b34de623c5765af1` (= `frozen_auditor_sha256` in the oracle) |
| r23 lesson `corpus/lessons/round-23.md` | sha256 `379a8677783ebf81058b79fb8510a7f0eaa717f3634f341d75fc205c3c786e69` |
| r24 lesson `corpus/lessons/round-24.md` | sha256 `a1950674df72352ad4ee0d2b250075e986b390654f62916cf744709d11d1ee45` |
| Fleet filed r23 report | `/home/vgpnk/Projects/shokunin/.ufo/reports/round-23/kama.md`, fleet `410b511`, blob `6dbb1a2f1f5bdc159b8326f5b89cadd863d0b671`, sha256 `5ef3f66d4596ae528ca4f1fe7717db3c336ba43579df8dbba2a608ef1015f0dd` |

No tool was installed or updated in this seat (nothing needed; the task was pure read-only
inspection). Nothing was written outside the lane's `falsify/` output paths; the fleet repo
was touched only with `git --no-optional-locks` read commands.

## Verdict summary

**Holds (8):** LOG.md round-24 entries are append-only and in commit order; the "69 durable
lane reports" count is correct and its stale "68" literal is correctly relocated to the
lesson; the 56/40/19/16 process accounting in the landed refinement reproduces exactly from
in-lane bytes; r23 filed bytes are immutable; the oracle artifacts are byte-immutable and
were all written before candidate inspection; the "background-job cap then respawn" claim is
exactly evidenced; the cited auditor contract lines 12–19 are identical in base and pinned.

**Falsified / not falsified by the pinned tree (2 defects, both already corrected in place
by the pinned LOG.md itself):** the "Correction to filed `.ufo/reports/round-23/kama.md`"
provenance and the "40 of the 56 killed FIFO-process identities" overclaim. Both superseded
texts remain in the file (append-only) and both are corrected by the refinement at
`LOG.md:1432-1447`. No relabelling as passed.

**Partial (7 findings below):** five wording/traceability gaps in the landed LOG.md, one
open oracle-level carry, one unlogged commit.

## Exact falsifiable claims (claim → verdict → command/exit → evidence)

| # | Claim (verbatim locus) | Verdict | Bounded check (exit code) | Evidence |
|---|---|---|---|---|
| C1 | `LOG.md:1417-1418` "falsify wave has 69 durable lane reports, not 68" | **HOLDS** | `ls .ufo/waves/round-23/falsify/advice/*.md \| wc -l` (0) → 69; `python3 -c` over `falsify/spec.json` (0) → spec items 73, advice 69, report-less set exactly `{CritOpenHonesty, RowC01Clean, RowF07LogFollow, RowF09SignatureProgram}`, no report outside the spec | 73−4=69; the lesson's own "73 seats dispatched (68 reports" is internally inconsistent (`corpus/lessons/round-23.md:178`) |
| C2 | `LOG.md:1417` the correction targets filed `.ufo/reports/round-23/kama.md` | **FALSIFIED as provenance (corrected at `LOG.md:1434-1438`)** | `ls .ufo/reports/` (0) → lane holds only `round-5`; `git --no-optional-locks log/diff` on the fleet file (0) → fleet `410b511` file has no falsify report count | Fleet report `:143` "Wave 1 build: 68 seats", `:148` "Wave 2 falsify: 73 seats", `:151` "Dead: 4"; the only "68 reports" literal is `corpus/lessons/round-23.md:178` |
| C3 | `LOG.md:1419-1420` "40 of the 56 killed FIFO-process identities were retained" | **FALSIFIED (corrected at `LOG.md:1440-1447`)** | `python3` over `r23-ps-classification.txt` (0) → rows 40; programs `{git:38, gpg-agent:1, scdaemon:1}`; FIFO-tied = `current/21`×2 + `frozen/21`×15 + `frozen/37`×1 + `kama-r23w2`×1 = 19; 5 at rows 20/00 (non-FIFO); 14 truncated; 3 `NOT-IN-COUNT-PATTERN` | The 40 retained rows disprove "56 killed FIFO-process identities": 2 of the 40 are gnupg daemons; only 19 tie to FIFO fixtures |
| C4 | `LOG.md:1441-1445` "56 was a matching-process count … a different listing pattern kept 40 truncated identity rows (38 git, gpg-agent, scdaemon) … only 19 … 16 counted identities were not retained … the matching count became zero after cleanup" | **HOLDS** | `grep -nE` on `out/CritEvidence/r23-ps-listing-line156.txt` (0) → line 41 is the standalone count `56`; `sha256sum` (0) → `96c21f6f…15bc` (= value claimed in CritEvidence); `cat provenance.txt` (0) → exact two patterns, line 154/156/157/159 timestamps, transcript sha256 `114ffef5…60db` | 40+16=56; the count and the 40 rows are both retained in-lane (no out-of-lane dependency for the numbers) |
| C5 | `LOG.md:1420` "Filed round-23 bytes remain immutable" | **HOLDS** | `git diff --stat 0df800e..2e254a1 -- .ufo/reports/ .ufo/waves/round-23/ corpus/lessons/round-23.md` (0, empty); `git log 0df800e..2e254a1 -- <same paths>` (0, empty); `git --no-optional-locks diff --stat 410b511 -- .ufo/reports/round-23/kama.md` (0, empty) | No r23 filed byte changed in round 24; the fleet r23 report worktree is byte-identical to fleet `410b511` |
| C6 | round-24 LOG chronology: entries appended, never rewritten, in commit order | **HOLDS** | `git show --numstat --format='' <c> -- LOG.md` for all 7 round-24 commits (0) → `d1b9d95 +21`, `123640b +34`, `f66b226 +8`, `aacbd52 +9`, `ed1cc3a +27`, `f1e755e +11`, `2e254a1 +0`; insertions only, zero deletions | File order matches commit order: 1411 prereg → 1432 refinement → 1449 prospective oracle correction → 1483 implementation |
| C7 | `LOG.md:1462-1464,1466-1472,1474-1481` "written before L1 inspected, measured or integrated any candidate"; the 44-case snapshot is frozen; the supplement does not change it | **HOLDS** | `git log --format='%h %ad' --date=iso` (0) → amendment `123640b` 15:04:12, snapshot `f66b226` 15:04:12, supplement `aacbd52` 15:12:55, candidate integration `ed1cc3a` 15:14:18 | Blob identity checks: prereg `5be9998b…`, amendment `29c73635…`, snapshot `8939cf49…`, supplement `8fa1f95e…` — each identical at its introducing commit and at pinned |
| C8 | `LOG.md:1427-1429` "Build wave validated at 64 seats; first call refused by background-job cap, unchanged payload spawned on the next attempt" | **HOLDS (text) / PARTIAL (timing, see F3)** | `cat .ufo/waves/round-24/build/dispatch-attempts.json` (0) → attempt1 `2026-10-21T17:50:07.442257+00:00` spawned 0, error "Background job limit reached (100)"; attempt2 `17:53:07.855854+00:00` spawned 64, error null; `ls build/advice/*.md \| wc -l` (0) → 64; `spec.json` items 64, name sets identical, no missing/extra | The gloss is exactly evidenced by the filed dispatch attempts |
| C9 | `LOG.md:1453` original tool contract `tools/report-landing-audit.py:12-19` | **HOLDS** | `git show 0df800e:tools/report-landing-audit.py` (0) vs pinned (0) | Lines 12–19 byte-identical in base and pinned; base sha256 `da5041a8…` = oracle `frozen_auditor_sha256` |

## Findings by severity

### F1 — MEDIUM — the pinned integrated commit is not represented in LOG.md
`2e254a1` ("land completed 64-seat build evidence and explicitly carry residual closure
debt", 2026-10-21 16:45:11 -0300) added 100+ files, including all 64
`.ufo/waves/round-24/build/advice/*.md` seat reports and every `build/out/**` evidence
directory, and added **0 lines** to `LOG.md` (`git show --numstat --format='' 2e254a1 -- LOG.md`
→ empty). The pinned LOG.md therefore ends at the `f1e755e` state (16:39:10 -0300) and
records nothing about the landing of the build evidence that the commit message claims to
carry, including the "residual closure debt" the message says is explicitly carried.
Observable in the pinned tree; not corrected by any later entry.
*Minimal correction (append-only, L1):* append one dated paragraph to the round-24 section
naming `2e254a1`, the 64 build advice files, the two dispatch attempts
(`.ufo/waves/round-24/build/dispatch-attempts.json`), and that the fresh-falsification
measurement stage is still pending — i.e. record the landing, not the promise.

### F2 — MEDIUM — the uncorrected overclaim survives in the immutable registration, and no oracle artifact extends the amendment to it
`preregistration.json` `expected_after[6]` still reads "69 falsify-wave lane reports, not
68; 40 of 56 killed FIFO-process identities retained, not full identity evidence" — the
same two defects C2/C3 found. The file is byte-immutable by design (blob `5be9998b…` at
`d1b9d95` = pinned), and `oracle-amendment-1.json` declares
`"supersedes_expectation_only": "preregistration.json expected_after[3]"` — so
`expected_after[6]` is neither amended nor annotated anywhere in the oracle layer.
Mitigating observation (falsified-as-harmless): the graded oracle file
`tests/report-audit/promisor-grid-expectations.json` (47 cases, last written `ed1cc3a`
15:14:18) contains **no** r23-count row (`grep -n "56\|68\|69\|FIFO\|killed"` → only
`sha256` digits and one `historical witness` line), so no grader consumes the bad wording.
CritEvidence's own condition — "If L1 keeps the prereg wording, the r24 report should still
carry this qualification" — is only partly discharged at pinned: the qualification exists
in `LOG.md:1432-1447` and `corpus/lessons/round-24.md:51-52` (mistakes table, verbatim
"r23 lesson:178 says68 reports; actual69 durable reports" and "only19 retained rows tied to
FIFO fixtures"), but the r24 filed report does not exist yet (the lane has only
`.ufo/reports/round-5/kama.md`; the fleet has rounds 10–22), so the obligation is still open.
*Minimal correction (no edit to the prereg):* in the r24 filed report, carry the
qualification explicitly and cite `LOG.md:1432-1447`; optionally add a new
`.ufo/waves/round-24/oracle-amendment-2.json` (new file, append-only) recording that
`expected_after[6]`'s wording is superseded by that refinement, so a reader of the oracle
layer alone cannot mistake it for current truth.

### F3 — LOW/MEDIUM — the preregistration entry forward-references evidence that was not in the tree, and "validated" is ambiguous
`LOG.md:1427-1430` states "Build wave validated at 64 seats" and "Evidence in
`.ufo/waves/round-24/build/`". At the writing commit `d1b9d95` (14:53:46 -0300 = 17:53:46Z)
the tree contained **no** build directory at all:
`git ls-tree -r d1b9d95 -- .ufo/waves/round-24/` → only `preregistration.json`; the same
listing at `123640b`, `f66b226`, `aacbd52`, `ed1cc3a`, `f1e755e` → no `build/`. The
successful 64-seat spawn was 39 seconds old at commit time (17:53:07Z), and the 64 seat
reports did not land until `2e254a1` (16:45:11 -0300 = 19:45:11Z), ~1h51m later. Under the
"dispatch-level" reading ("the wave was validated as 64 seats") the sentence is supported by
`dispatch-attempts.json`; under the "results-level" reading it is not supported at its
commit time. The same paragraph's "no actual round-24 improvements claimed yet" shows the
dispatch reading was intended, but the wording does not say so.
*Minimal correction (append-only):* one clause — "dispatched at 17:53:07Z with 64 seats;
the seat reports and their evidence land with commit `2e254a1`" — appended to the round-24
section; the existing entry stays byte-unchanged.

### F4 — LOW/MEDIUM — the landed refinement does not locate the superseded claims
`LOG.md:1440-1447` corrects the process overclaim but names no source location for it, and
the drafted correction (`build/out/CritEvidence/r23-corrections-append.md`) did. The
overclaim lives in three immutable places: fleet `410b511`
`.ufo/reports/round-23/kama.md:33-34` ("56 orphaned FIFO-blocked git processes from this
round were killed"), lane `corpus/lessons/round-23.md:109-110` ("56 such processes from
this round were killed") and `:174` (M7, "56 blocked `git` processes under
`/tmp/repo-state-grid-*` / `/tmp/kama-r23w2/`"), plus `:178` for the "68" literal. A reader
of the pinned LOG.md cannot locate what was corrected without re-deriving it.
*Minimal correction (append-only):* append the four pointers (two files, four line spans) to
the round-24 section.

### F5 — LOW — "narrower" inverts the direction of the supersession
`LOG.md:1440` "The old process claim is also narrower than the retained record proves".
CritEvidence's own analysis of the same text calls it the opposite ("It repeats an
overclaim"), and on the plain reading the old claim is **broader** than the record proves:
it asserts 56 killed FIFO-process identities, whereas the record shows 40 retained rows of
which only 19 tie to FIFO fixtures (2 of the 40 are `gpg-agent`/`scdaemon`). "Narrower" is
defensible only in the different sense that the old gloss's retained-identity evidence is
narrower than what the transcript shows about the kill — the sentence supports both readings
and cites neither.
*Minimal correction (append-only):* one clause — "the superseded gloss over-claims the FIFO
scope (CritEvidence's term); 'narrower' was meant in the retained-identity sense only".

### F6 — LOW — "the filed fleet report" is not identified
`LOG.md:1436` refers to "the filed fleet report" without path, fleet commit or blob id, so
the parenthetical "(whose 73 seats minus 4 missing reports already implies 69)" is not
checkable from the LOG text alone (the fleet path `.ufo/reports/round-23/kama.md` does not
exist inside the lane tree; only `.ufo/reports/round-5/kama.md` does).
*Minimal correction (append-only):* name it — "fleet `410b511` `.ufo/reports/round-23/kama.md`
:143, :148-155".

### F7 — LOW — "support S105" is terse against S105's own ledger status
`LOG.md:1516-1517` "Freshly reopened bytes.decode docs support S105". `corpus/SOURCES.md:117`
gives S105 status `rejected` — it is the explicit superseding **rejection** record for
S095's cross-API inference (the docs are the evidence for that rejection, not an admission).
The count claim in the same sentence holds: `grep -c "^| S[0-9]" corpus/SOURCES.md` → 105,
last row S105. The row's own `used-by` cell and the lesson
(`corpus/lessons/round-24.md:94`, `:151`) carry the reject status, so this is wording
density, not a ledger defect. (Note: the source-census final verification is L1-owned; this
seat did not re-census the ledger.)
*Minimal correction (append-only):* "the reopened docs are the evidence for the S105
rejection record" — optional, wording only.

## Observed vs inferred

**Observed (directly read bytes / git objects at the pinned revision):** every count, line
number, blob id, sha256, file listing, commit timestamp and diff emptiness cited above;
the 69/4/73 report arithmetic; the 38/1/1 program split and the 19/5/14/3/16 row
partition; the two dispatch attempts; the byte-identity of the four oracle artifacts; the
emptiness of every r23 diff; the fleet report's line contents and its identity with fleet
`410b511`.

**Inferred (not directly observed here):** that the 40 retained rows and the `56` count
were produced by the single command recorded in `provenance.txt` (the count's source
transcript `~/.omp/agent/sessions/…/KamaR23-2.jsonl` sha256 `114ffef5…60db` is **outside**
the lane and was not re-read or re-hashed by this seat — the in-lane copies are the
verbatim listing and the derived classification); that the "68" lesson count excluded
RowC03 rather than miscounting it (RowC03's file mtime claim of 16:10:15Z is not
reproducible from git, which stores no mtimes); that the build seats' own 64 outputs were
"validated" in any sense beyond dispatch (not checked — out of this lane's assignment).

## Files written (this seat)

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/advice/DocLog.md` — this report.
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/out/DocLog/commands.txt` — the exact commands, exit codes and key outputs behind every row above.
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/out/DocLog/claims.tsv` — the C1–C9 claim/verdict table in machine-readable form.
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/out/DocLog/log-chronology.txt` — per-commit `LOG.md` numstat and `git ls-tree` of `.ufo/waves/round-24/` per round-24 commit.

Scratch (not part of the lane): `/fast/scratch/hyaku/kama-r24/falsify/DocLog/repo` (own
clone, `--no-hardlinks`, detached at the pinned revision). No production file, no fleet
file, no `.jj/index`, no service and no config was modified.

## Unverified / verification gaps

1. The out-of-lane session transcript behind the `56` count was not re-read or re-hashed
   (lane boundary + read-only discipline); only its in-lane verbatim copy and the derived
   classification were checked.
2. The per-PID FIFO wait state is not observable after the fact; "19 tie to FIFO fixtures"
   is a path/argv/grid-row correspondence, not a kernel-level blocking proof.
3. `RowC03FabricatedFull.md` mtime (16:10:15Z) and the closure's "68 final session replies"
   were not re-verified (mtimes are not in git; session replies were not counted).
4. The 47-cell expectations file was only structurally spot-checked for the absence of the
   r23-count row and for its write time; full 44+3 equivalence with
   `oracle-snapshot-before-inspection.json` is L1/GridOracle-owned, not re-verified here.
5. `corpus/SOURCES.md` row census was not re-run (L1-owned final verification after this
   stage).
6. No r24 filed report exists yet, so F2's open obligation could not be discharged or
   falsified against a filed artifact.

Report: .ufo/waves/round-24/falsify/advice/DocLog.md
