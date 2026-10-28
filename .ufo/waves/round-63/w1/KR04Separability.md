# KR04Separability — round 63 (kama): separability and counted surfaces

Seat: KR04Separability (attack item, leaf). Judged on operability + calibration.
Tip under test: `03a6a1d850902a66a13dfad33f89cf3a8b759a09` (freeze amendment 1).
Base: `7ee8cbdf160f8c945954e4737e7a2f797e3b2987`. Evidence copies: `.ufo/waves/round-63/w1/out/KR04Separability/` (see `fixtures.txt`, `*.out`, `*.stderr`, `dbg_rows.py`, `ollama-probe2.out`).
Method: scratch clone `git clone --shared` (my scratch only; lane untouched, lane git index untouched). Fixture commits built in the clone; counters run from the clone path with `--repo <clone> --tip <rev>`; each commit's `git archive` tree is what the counter executes. Python 3 stdlib only; no installs; no pacman.
Rule-9 reference: the text of "fleet-lesson rule 9" is not in this lane's tree (grepped corpus/ and .ufo/waves/round-62). I used the lane's own operational test recorded in `corpus/lessons/round-19.md` (lines 20-23): a claim is separable when "neither counter reads the other claim's inputs (CritSeparability 2x2 toggle)". I applied that test plus a counted-surface test (which numbers move when a file that the other claim owns moves).

## 1. Measurements (verbatim counter output)

| Run | Tree (commit) | Output line (verbatim) | Exit |
|---|---|---|---|
| T-C2 | tip `03a6a1d8` | `population=12 rows=12 covered=12/12 bound=12 eval_lines=12 sensitive=12/12 dead=0 host_busy=1 mismatches=0 canonical=63 selfdesc_mismatches=8 sens_selftest=4/4 controls_rejected=12/12 errors=0 met=False` | 1 |
| T-C1 | tip `03a6a1d8` (fresh work) | `tool_present=1 live_ok=1/1 controls_targeted=44/44 eval_selftest=3/3 errors=0 met=True families[digest=1/1 fake=2/2 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 predead=1/1 ptok=2/2 reqbind=2/2 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 tamper=8/8 timing=4/4 trunc=2/2 witness=6/6]` | 0 |
| F-C1only | base + C1 files only (`f3e12f39`) | same as T-C1 (`controls_targeted=44/44 eval_selftest=3/3 errors=0 met=True`) | 0 |
| F-C2only | base + C2 files only (`8da6e9aa`) | byte-identical to T-C2 (`... selfdesc_mismatches=8 ... met=False`) | 1 |
| S-shared | C1 run first, then C2, same `--work` | `population=12 rows=12 covered=12/12 bound=12 eval_lines=12 sensitive=0/12 dead=11 host_busy=0 mismatches=23 canonical=63 selfdesc_mismatches=None sens_selftest=4/4 controls_rejected=0/12 errors=0 met=False` | 1 |
| M1-cached | tip + exit-1 insert in `tools/sources-append-only.py` (`f40e0340`), `--work` already holding the tip tree | `population=12 rows=12 covered=12/12 bound=12 eval_lines=12 sensitive=11/12 dead=0 host_busy=1 mismatches=2 canonical=63 selfdesc_mismatches=9 sens_selftest=4/4 controls_rejected=0/12 errors=0 met=False` | 1 |
| M1-fresh | same M1, fresh `--work` | `population=12 rows=12 covered=12/12 bound=12 eval_lines=12 sensitive=11/12 dead=0 host_busy=1 mismatches=2 canonical=63 selfdesc_mismatches=9 sens_selftest=4/4 controls_rejected=0/12 errors=0 met=False` | 1 |
| E1 | tip + 13th canonical row `live-completion-request-plane` added to the round-63 list only (`2d1ed24e`) | `population=12 rows=12 covered=12/12 bound=12 eval_lines=12 sensitive=12/12 dead=0 host_busy=1 mismatches=0 canonical=63 selfdesc_mismatches=9 sens_selftest=4/4 controls_rejected=12/12 errors=0 met=False` | 1 |
| M2 | tip + `tools/sources-append-only.py` replaced by a 2-line stub that prints the bound pattern and exits 0 (`57270248`), fresh `--work` | `population=12 rows=12 covered=12/12 bound=12 eval_lines=12 sensitive=12/12 dead=0 host_busy=1 mismatches=0 canonical=63 selfdesc_mismatches=8 sens_selftest=4/4 controls_rejected=12/12 errors=0 met=False` | 1 |
| R-tip | `round42-selfdesc-reconcile.py --tip 03a6a1d8` | `r41=1 banner=1 planned=2 retired=1 saturation=1 caps=1 receipts=0 readme=0 province=1 rel=0 mismatches=8 maxN=63 met=False` | 1 |
| R-E1 | same, E1 | `r41=1 banner=1 planned=2 retired=1 saturation=1 caps=1 receipts=0 readme=0 province=2 rel=0 mismatches=9 maxN=63 met=False` | 1 |

Reading the table: M1-cached reports `census` verdict `true` on a tool that now exits 1 (see D2); its 2 mismatches are a live-ollama flake (D3), not the mutant. M1-fresh correctly flags the census row (`census false`, `dbg_rows` below) but still prints the same tally. M2 is the hollow-verifier survival (D4).

Per-row check on M1 (`dbg_rows.py`, fresh tree): `sources-registry census false sensitive=False`; all other rows unchanged. On M1 with the cached tip tree: `sources-registry census true sensitive=True`. The mutant is invisible to the bound row when the cached tree is used.

## 2. Per-question verdicts

### Q1. Can C1 verify without C2 landed, and vice versa?

**C1 without C2: YES.** F-C1only (base + only C1 files) prints `met=True` with 44/44 controls and 3/3 self-test. The C1 counter reads exactly three blobs at the tip: `tools/kama-completion-live.py`, `tools/kama-llamacpp-live.py`, `registry/endpoint-consumers.tsv` (`round63-c1-counter.py` lines 642-666). It never reads SCORECARD.md, `registry/capability-claims-r63.tsv`, the reconciler, or any round-63 canonical list. Re-running C1 in the same `--work` also stays `met=True` (C1 rewrites its three tree files from blobs each run).

**C2 without C1: YES at the counter level.** F-C2only (base + only C2 files) prints a line byte-identical to T-C2. The C2 counter reads `SCORECARD.md`, `registry/capability-claims-r63.tsv`, the 12 bound tools, and the reconciler; none of these is a C1 file.

**C2 verdict vs C1 acceptance: COUPLED through SCORECARD.** C2's met is not invariant to whether C1 enters the list. E1 (one 13th canonical row, no other edit) leaves C2's own counts (`mismatches=0 covered=12/12`) untouched, but the reconciler conjunct moves 8 → 9 (`caps=1`, `province` 1 → 2: `PROVINCE.md lacks tools/kama-completion-live.py (capability live-completion-request-plane)`). The minimal coherent L1 edit (add the row, restate "13 capabilities", add the first-working round to the saturation statement, add the PROVINCE token) is what the reconciler needs to return to 0. So the closing C2 result depends on C1's outcome through a document both claims' surfaces share. The freeze says C1 "enters only if C1 verifies"; that makes C2's met conditional on C1's verdict even though C2 never reads C1.

Verdict Q1: C1 is separable from C2 (both directions for the counters' verdicts). C2's closing metric is not separable from C1's acceptance because both write-paths land on SCORECARD.md.

### Q2. Does C2 count anything C1 changed?

- **SCORECARD canonical list:** C1 did not change it at the tip (the round-63 list is the round-62 list, 12 rows; the freeze's text says the C1 row is excluded). C2 counts it. Shared, and not currently moved by C1. Once C1 lands, C2's count moves (Q1, E1).
- **tools/kama-completion-live.py:** not read by C2 and not in any C2 scan. C2's digest-ledger and hexrun-census scans enumerate `.md` and `.tsv` only (`digest-ledger.py` line 81; `hexrun-census.py` line 97); the C1 `.py`/`.txt` files are outside those scans. Confirmed by F-C2only = T-C2.
- **Shared runtime dependency, not a shared file:** `tools/kama-llamacpp-live.py` is imported by the C1 tool (`kama-completion-live.py` line 61-64) and executed as C2's `live-llamacpp-lifecycle` row. Both claims move together if that harness changes. Not changed this round, but the two verdicts are not independent on that file.
- **Latent, not yet at the tip (the largest real surface):** the freeze requires a C1 frontier SOURCES row and a corpus/knowledge document. At the tip, `git diff 7ee8cbdf 03a6a1d8 -- corpus/` is empty. In the lane working tree right now (read-only check, `git diff --stat`, not touched by me) there are uncommitted edits to `corpus/SOURCES.md` (S527, S528), `PROVINCE.md`, and `corpus/knowledge/completion-request-plane.md`. Once committed they enter C2's digest-ledger and hexrun-census scans (every `.md`/`.tsv`), the r41 coverage fact (`corpus/knowledge/*.md` count, expected 36, currently failing at the tip), and the SOURCES census conjunct if the head ever states counts. The counters read git blobs, so the working-tree edits are invisible to a tip measurement; the moment they are committed the measured surface changes. A C1 claim that carries its own corpus edits is therefore not separable from C2 at the closing tip unless both are re-measured there.

Verdict Q2: at 03a6a1d8, C2 counts nothing C1 changed (proved by F-C2only identity). C2 counts one surface C1 will change (SCORECARD canonical list and head), and C1's frontier corpus step will enter C2's scans when committed. Both need a re-measurement at the closing tip.

### Q3. Is the C2 reconciler conjunct a second claim on one axis, or a count of the same surface?

It is a count of the same surface, not an independent second calibration claim. Evidence (`tools/round42-selfdesc-reconcile.py`):

1. **Same canonical list counted twice.** C2's `canon_problems` checks the round-63 list's frozen prefixes (MANIFEST). The reconciler's `caps` conjunct checks that the head Capabilities table names equal the same list's names. One defect in that list (e.g. a renamed row) moves both counters. Current tip: `caps=1` (head names ≠ canon names) is already counted.
2. **Same score vector copied in three places.** SCORECARD `## Axes` table; `tools/round41-scorecard-reconcile.py` line 57 `EXPECTED = {"operability": 8, "freshness": 8, "depth": 7, "coverage": 9, ...}`; the `## Saturation` statement `operability 8, freshness 8, ...` checked by `saturation`. The check confirms the three copies agree. It never checks any score against evidence: the r41 `score` fact compares the table to the constant the lane typed in the counter.
3. **Circular evidence.** The SCORECARD calibration row's evidence (`## Axes`, row `calibration`) cites `tools/round41-scorecard-reconcile.py` and `tools/round42-selfdesc-reconcile.py` as "this table's counters". The reconciler that C2 counts is a piece of the calibration axis's own evidence.
4. **Non-assigned axis inside the count.** The tip's first mismatch is `r41 coverage run ... no stdout line == '36'` (`reconcile-tip.out`). Coverage is not an assigned axis (assigned: operability + calibration per the head banner). So C2's selfdesc 8 includes a coverage fact.
5. **Red at the measured tip by design.** Banner (`Latest measured round: 63`), Planned (round 64), Retired (`12 capabilities`), Saturation (`first-working rounds ...`) are all stale at 03a6a1d8 (head still says round 61). The freeze says the head is re-derived "AFTER measurement". So C2 cannot be met at the measured tip, and the closing tip will differ from the measured one. The reconciler's 0 at the closing tip is a claim about a commit nobody has measured with C2.

Verdict Q3: the reconciler conjunct is a count of SCORECARD head consistency (one surface, partly on an unassigned axis, partly circular). It is not a second calibration claim on a different surface. As a C2 conjunct it should be disclosed as such, or moved out of the C2 number.

### Q4. Naming: does operability = request plane and calibration = self-assessment vs repo match the surface changed?

- **Operability (C1).** The surface changed is `tools/kama-completion-live.py` and the counter. What is measured: one POST `/v1/completions` against a lane-spawned llama.cpp child on an unregistered loopback port, with the counter's own outside request during a hold window. The operability row in SCORECARD `## Axes` says the registered endpoints "sample DEAD ... so no model-readiness verdict is evidenced", and the tool's own domain line says "local model serving & endpoint health". The name suggests endpoint operability; the measured thing is a fixture's request plane that the claim itself spawns. Verdict: the name overstates the scope. "Operability" should read "lane-fixture request plane" in the freeze and the SCORECARD row, or the registered-consumer limit must be kept next to the number. The number ("44/44 controls") reports the counter's controls, not the surface.
- **Calibration (C2).** The surface changed is the registry, the counter, the canonical list section, one hexrun-ledger row, and the SCORECARD head. The calibration axis's own evidence (`## Axes` calibration row) points at `registry/verdict-ledger.tsv` (self vs outside, `agreement=69/87`), `registry/claim-outcome-ledger.tsv`, and `tools/round59-c2-counter.py`. None of these is touched by C2; the axis's score 7 is still backed by the round-59 evidence. C2's 12 rows are tool outputs matched against strings the lane typed in the registry. That is a self-assessment check of claim strings, not a calibration check of predictions against outcomes. Verdict: the name "calibration" matches the freeze's definition ("self-assessment vs repo") only in the narrow sense of string agreement. The reconciler part is head consistency. Neither matches the calibration evidence the axis cites.
- **Number vs surface (both claims):** C2's `covered=12/12` counts `context-capacity-receipt` at `host-busy` (`host_busy=1`), i.e., a capability whose K1 cell was refused and not run. `is_met` does not check `host_busy`. The 12/12 therefore reads as "12 capabilities exercised" when 11 were exercised. On this host the operator's llama-servers (ports 1234, 45669) keep K1 at host-busy, so the row is refused by construction.

## 3. Defects found in the counted surfaces (rule-9 relevant)

**D1 — C1 and C2 collide on the shared `--work` (confirmed).** Both counters place the tip tree at `<work>/tip` (`round63-c1-counter.py` line 650; `round63-c2-counter.py` `checkout_tip`, line 480). C1 writes only three files there; C2's `checkout_tip` returns an existing directory without checking it is a full archive of `--tip`. Run C1 then C2 with the same `--work` and C2 reports `dead=11 sensitive=0/12 selfdesc_mismatches=None controls_rejected=0/12 errors=0 met=False` (S-shared). Note `errors=0` while `dead=11`: the errors field does not count dead rows. The recipe in the seat brief passes the same `--work $S/work` to every run, so this is the default path, not an edge case.

**D2 — C2 scores a cached tree, not `--tip` (confirmed).** `checkout_tip` (C2 line 479-481) reuses `<work>/tip` whenever it exists, regardless of `--tip`. Tool code therefore comes from whichever tip first populated the directory, while SCORECARD, registry and the reconciler's inputs come from `--tip`. M1-cached: `dbg_rows.py` on the cached tree reports `sources-registry census true sensitive=True` although the bound tool now exits 1 at line 2. The mutant is invisible to its own row. For mutation work this means: every mutant run that reuses a `--work` is scored on the first mutant's (or the first tip's) tool code. This is a defect of the counter and of the mutation recipe; it can make a SURVIVED result look like a KILL or vice versa.

**D3 — C2's live-ollama row is one-shot per scratch (confirmed).** `kama-ollama-live.py --work <work>/run/ollama` fails on any second run in the same directory: `checks[7] tags-empty-before-create passed=false` (the model store from the first run persists; `ollama-probe2.out`, verdict `FAIL`, rc 1). A fresh directory passes (`verdict MODEL_OK`). Within C2 this shows up as `mismatches` +2 (`ok` and `sensitive`), exactly the pattern in M1-cached. C1 is not affected (re-run `met=True`). Any L1 re-measurement after the planned head re-derivation must use a fresh `--work` or the live row will fail for a reason unrelated to the claim.

**D4 — C2's control set does not catch a hollow bound tool (SURVIVED, prominent).** M2 replaces `tools/sources-append-only.py` with a stub that prints `45/45 selftest cases passed` and exits 0. Result: `census` verdict `true`, `sensitive=12/12`, `mismatches=0`, `controls_rejected=12/12`; the counter line is identical to T-C2. The only remaining blocker is `selfdesc_mismatches=8`. Once the reconciler reads 0, C2's `met` would be True for a tool that checks nothing. The 12 controls mutate the registry strings (`drop`, `rename`, `binding`, `verdict`, `quote`, `free`, `weak`, `notobs`, `hostbusy`, `duprow`, `observed`, `canon-drop`); none mutates or hashes the bound tool. The sensitivity test (`is_sensitive`, `verdict_fn`) re-applies the verdict to the output string and exit code, so it certifies the string, not the verifier. M2 is a counted-surface defect of the calibration claim.

**D5 — C2 accepts a canonical capability with no binding (confirmed).** `canon_problems` requires the 12 frozen slugs to be present once (subset), not the list to equal the bound set. E1 (13 rows, one unbound) gives `canonical=63 covered=12/12 mismatches=0`. A capability can enter the canonical list without any executed verifier and C2's own counts do not notice; only the reconciler notices, and only through its text conjuncts.

**D6 — host-state coupling of the K1 row (inference; partly confirmed).** `pgrep_foreign()` lists every `llama-server` process (`pgrep -x llama-server`, C2 line 337). It cannot tell a C1 counter's child from an operator process, and the K1 cell accepts `host-busy` whenever a foreign server is listed before and after. A concurrent C1 run therefore can move K1 between "run" and "host-busy" on an otherwise idle host. [INFERENCE] from code: not reproduced, because the operator's llama-servers on 1234 and 45669 keep this host busy at all times. Observed: `host_busy=1` at tip with those processes present.

**D7 — reconciler tip baseline includes stale, unrelated facts (observed).** Tip mismatches 8: r41 coverage (`36`), banner (head still round 61), planned (round 64 missing), retired (`12 capabilities` not stated; head says `11 capabilities`), saturation (first-working list not stated), caps (head names ≠ canon), province (`PROVINCE.md lacks registry/ollama-live-claims-r61.tsv`). These are the surfaces the freeze says the L1 re-derives after measurement. Nothing in them is C1 or C2 evidence.

## 4. Smallest safe corrections (for the planner; not applied by me)

1. Key the tip tree by the tip hash (e.g. `<work>/tip-<sha>` plus a marker file) or refuse an existing `<work>/tip` that is not an exact archive of `--tip`. Recipe: use a fresh `--work` per run until fixed. (D1, D2)
2. Give live-ollama a fresh subdirectory per run (`--work %S/ollama-<nonce>`) or clean it before the run. (D3)
3. Add a control family that mutates the bound tool's content (or pins the tool's blob sha256 in the registry and rejects any other) so a hollow verifier fails its row. (D4)
4. Make the canonical-list rule set equality with the bound rows, and let `errors` count dead rows. (D5, minor)
5. Move the coverage fact and the score-vector copies out of C2's number, or name them as SCORECARD-consistency facts; keep C2's number to the twelve bound rows if "calibration" is kept. (Q3, D7)
6. Rename operability to "lane-fixture request plane" (freeze, SCORECARD row, PROVINCE if cited), keep the registered-consumer DEAD limit next to it, and rename C2 to "capability-claim binding" unless the calibration ledgers (verdict-ledger, claim-outcome-ledger, round59 counter) are added to its count. (Q4)
7. Measure the closing tip: re-derive the head, then run C2 at that new commit with a fresh work dir. The number printed at 03a6a1d8 is 8, and that is the measurement the freeze reports.

## 5. Tools, installs, cleanup

- No installs or upgrades. No pacman. Python 3 stdlib as provided on the host.
- Mutating git was confined to the scratch clone `/fast/scratch/hyaku/kama-r63/w/KR04Separability/clone` (commits f3e12f39, 8da6e9aa, f40e0340, 2d1ed24e, 57270248; each commit asserted with `git rev-parse --show-toplevel`). The lane was only read (`git show`, `git diff`, `git status`, `git log`, `git clone --shared` source).
- The lane working tree shows uncommitted edits by another party (PROVINCE.md, corpus/SOURCES.md, corpus/knowledge/completion-request-plane.md, untracked .ufo/waves/round-63/source/ and w1.ready). I did not read or change them beyond `git diff --stat`/`git diff` on the SOURCES rows named in Q2.
- Live processes spawned by my runs were the counters' own children on unregistered loopback ports; no registered consumer port was contacted. I did not signal any process.
- Scratch root removed after the receipts were copied to `.ufo/waves/round-63/w1/out/KR04Separability/`.

## 6. Verdict summary

- Q1 C1 separable from C2 (counter inputs): YES. C2's closing number coupled to C1 acceptance via SCORECARD: YES (E1 8→9).
- Q2 C2 counts anything C1 changed at the tip: NO (F-C2only identical). Latent: SCORECARD canonical list/head; C1 frontier corpus edits once committed.
- Q3 reconciler is a second claim: NO, a count of the same SCORECARD surface (canonical list counted twice, score vector copied three times, circular with the calibration row, includes unassigned coverage).
- Q4 naming: operability overstates (fixture request plane); calibration matches only string agreement, not the calibration ledgers the axis cites; 12/12 includes one host-busy row that was never run.
- Counted-surface defects: D1 shared `--work` collision (C1 then C2 → met=False, dead=11); D2 cached tip tree (mutant invisible); D3 live-ollama one-shot per dir; D4 hollow verifier survives (SURVIVED, prominent); D5 unbound canonical row accepted.

Counter line (requested tally, tip, C2): `population=12 rows=12 covered=12/12 bound=12 eval_lines=12 sensitive=12/12 dead=0 host_busy=1 mismatches=0 canonical=63 selfdesc_mismatches=8 sens_selftest=4/4 controls_rejected=12/12 errors=0 met=False` (exit 1).
Counter line (requested tally, tip, C1): `tool_present=1 live_ok=1/1 controls_targeted=44/44 eval_selftest=3/3 errors=0 met=True` (exit 0).
