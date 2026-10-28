# KR07Routed62 — closure audit of the three round-62 routed defects (kama, round 63)

Seat: KR07Routed62, leaf (no dispatch). Judged on: operability, calibration. Milestone: attack the claims.
Tip under test: `03a6a1d850902a66a13dfad33f89cf3a8b759a09` (amendment-1 tip; lane HEAD equals it).
Advisory only: no verdict on C1 or C2, no commit, no edit to lane source. Evidence: `.ufo/waves/round-63/w1/out/KR07Routed62/`.
Installs/upgrades: none. No pacman. Scratch `/fast/scratch/hyaku/kama-r63/w/KR07Routed62/` (clones `clone-c1`, module copies, run dirs) removed before yield; every mutant was committed only inside that clone, toplevel asserted before each mutation.

## Status summary

| # | Routed defect (source: corpus/lessons/round-62-verifier-spotcheck.md) | Closure status | One-line basis |
|---|---|---|---|
| 1 | Vacuous C2 sensitivity, `tools/round62-c2-counter.py:269-271` | **CLOSED** (residual calibration notes in §1.4) | Old expression is gone from the r63 decision path; r63 sensitivity fails on planted verdict defects and on a counter with the old expression re-inserted (`sens_selftest=0/4 met=False`). |
| 2 | C1 falsification never settled; provisional green | **OPEN** | Re-claim is structurally separate (own predicate, counter, schema v2, not in the canonical list), but the r63 falsification wave has not settled and already reports SURVIVED mutants at the same tip where the counter prints `met=True`. |
| 3 | Lane worktree untracked paths (r62: 122) | **OPEN** | `git status` now shows 775 untracked paths and growing (round-63 wave still writing); a pre-close-out nested stray draft is still present; the committed SCORECARD sentence "the lane worktree now has no lane-authored untracked paths" is false. Nothing was swept. |

---

## 1. C2 sensitivity (routed defect 1)

### 1.1 The defect site (unamended round-62 record)
Command: `git -C /home/vgpnk/Projects/shokunin/kama-shokunin show 03a6a1d8:tools/round62-c2-counter.py | sed -n '268,272p'`
```
    verdict = (not dead and tpl['pattern'] in out and rc == 0)
    # sensitivity: blank out every occurrence of the pattern's matched text
    mut = out.replace(tpl['pattern'], MUT)
    sensitive = not (tpl['pattern'] in mut and rc == 0 and not dead)
    if not sensitive:
```
The removed pattern is searched for in the text it was just removed from. `pat in mut` is false for any MUT token that lacks the pattern, so `sensitive` is always true on real output. Vacuous by construction (as the lesson says).

### 1.2 The repair, run by me on the tip
Counter module copied from the tip blob (`git show 03a6a1d8:tools/round63-c2-counter.py`) and the four planted defects run through `is_sensitive` (`scripts/sens.py`, output `sens.out`):
```
selftest total = 4 expect 4
P1 always-true is_sensitive= False -> rejected
P2 rc-only (no pattern) is_sensitive= False -> rejected
P3 pattern-only (no exit) is_sensitive= False -> rejected
real verdict_fn is_sensitive(out)= True
real verdict on exit-2 output= False
P4 r62_formula(a,a)= False  is_sensitive(a,a)= True
```
P1–P3 are verdict functions (always true; ignores exit code; ignores pattern). P4 is the round-62 expression itself.

Non-vacuity was also tested on the real counter, not only on the self-test:
- **C2-V mutant** (clone commit `926ca9b0`): `is_sensitive` body replaced by `return r62_formula(out, rc, dead, pat)`, i.e. the round-62 vacuity re-inserted into the round-63 counter. Command: `cd $CLONE/tools && python3 round63-c2-counter.py --repo $CLONE --tip 926ca9b0c8407a138d8ff73a1543cd984004dd6e --work $S/work-c2v`
```
population=12 rows=12 covered=12/12 bound=12 eval_lines=12 sensitive=12/12 dead=0 host_busy=1 mismatches=0 canonical=63 selfdesc_mismatches=8 sens_selftest=0/4 controls_rejected=12/12 errors=0 met=False
```
exit 1. The in-run column still reads `sensitive=12/12` (blind, as expected); the self-test is what rejects it (`0/4`). Result: KILLED.

Unmutated tip, same counter (`c2-tip.out`):
```
population=12 rows=12 covered=12/12 bound=12 eval_lines=12 sensitive=12/12 dead=0 host_busy=1 mismatches=0 canonical=63 selfdesc_mismatches=8 sens_selftest=4/4 controls_rejected=12/12 errors=0 met=False
```
exit 1. `met=False` is the known `selfdesc_mismatches=8` (the freeze states the reconciler stays at 8 at this tip on purpose until the L1 re-derives the SCORECARD head). Everything else on the C2 predicate line is green, including `sens_selftest=4/4`.

### 1.3 What the repair does and does not prove
- Proved: the round-62 expression is no longer on the decision path, and the sensitivity conjunct flips on defective verdict functions (P1–P3) and fails the whole counter when the vacuity is re-inserted (C2-V → `sens_selftest=0/4`).
- Not proved by the in-run column: for the shipped `verdict_fn` (`pat in out and rc == 0`), `is_sensitive(out)` equals `verdict_fn(out)` for every output, because the strip and exit-flip conjuncts are implied by the verdict's own structure. The `sensitive=12/12` column therefore restates the verdict column; its teeth come entirely from the self-test.

### 1.4 Residual calibration findings (logged, do not reopen the routed item)
- **R1.1 — the fourth "planted defective verdict function" is not one, and passes by accident.** P4 requires `is_sensitive('a') and not r62_formula('a')`. `r62_formula` returns "insensitive" only because the replacement token `__kama_mut__` contains the letter `a`. Output of `scripts/p4.py` (`p4.out`):
```
pattern='a'      in-token=True  r62_sensitive=False r63_sensitive=True  P4_witness_fires=True
pattern='b'      in-token=False r62_sensitive=True  r63_sensitive=True  P4_witness_fires=False
pattern='ok=1'   in-token=False r62_sensitive=True  r63_sensitive=True  P4_witness_fires=False
pattern='ok'     in-token=False r62_sensitive=True  r63_sensitive=True  P4_witness_fires=False
```
So the freeze's "all 4 planted defective verdict functions" is 3 verdict-function plants plus one token-collision witness. The round-62 expression is still "sensitive" on every pattern not contained in the token. P1–P3 carry the real detection (C2-V shows that).
- **R1.2 — per-row sensitivity is tautological for the shipped verdict.** See §1.3. Suggested fix for the L1 to decide: replace P4 with a fourth verdict-function plant (e.g. one that ignores `rc` only), and state in the freeze that the per-row column is structural.

Verdict for item 1: **CLOSED** (the vacuous expression is removed; the repaired check fails on defective verdict functions and on the counter with the defect re-inserted). R1.1/R1.2 are residual calibration notes.

---

## 2. C1 falsification / re-claim (routed defect 2)

### 2.1 What is structurally closed
- The r62 C1 claim was labelled "Awaiting falsification wave; provisional" (SCORECARD r62 table). The r63 round section keeps that record and states the new claim is separate: `live-completion-request-plane` "is not in this twelve-row frozen population (it is claimed separately by C1 and enters only if C1 verifies)" (SCORECARD round-63 canonical list, committed at tip).
- Separate instruments exist: freeze predicate `C1-r63` (`.ufo/waves/round-63/controls/freeze.txt`), `tools/kama-completion-live.py` schema v2, `tools/round63-c1-counter.py`; the r62 counters are unamended.
- The SCORECARD round-63 "Claim rows" are not yet filled: "Claim rows are filled in `### Round-63 measured results` ... once measured"; `.ufo/waves/round-63/measured/` is empty at tip.

### 2.2 What is not closed: the tip green is provisional
Command: `cd /home/vgpnk/Projects/shokunin/kama-shokunin && python3 tools/round63-c1-counter.py --repo <lane> --tip 03a6a1d8… --work <scratch>` (run from the lane root; `c1-tip.out`):
```
tool_present=1 live_ok=1/1 controls_targeted=44/44 eval_selftest=3/3 errors=0 met=True families[digest=1/1 fake=2/2 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 predead=1/1 ptok=2/2 reqbind=2/2 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 tamper=8/8 timing=4/4 trunc=2/2 witness=6/6]
```
exit 0. This is the same shape as the r62 provisional green: a green counter with a falsification wave that has not settled. The wave is still running (`w1.ready.dispatched` present; the wave has no WAVE-DONE or measured results in the lane).

Survivors already reported by the wave's seats at this tip (seat-reported; each has its own report and counter lines in `.ufo/waves/round-63/w1/`):

| Seat report | Survivor | Counter says |
|---|---|---|
| MT01ToolHeaders.md | M1 pinned headers; M3 canned fake behind real server | `met=True` 44/44, 3/3 |
| MT02ToolTruncation.md | M1 `body_truncated` forced False; M3 Content-Length dropped | `met=True` |
| MT03ToolChoiceShape.md | counter-side c-BOOL (`False == 0` bool index guard) | `met=True` |
| MT05ToolTimings.md | X1 NaN in ungraded key; CM1 `predicted_n` bool guard; CM2 `prompt_n` negative | `met=True` |
| MT06ToolPromptTokens.md | A fabricated `/tokenize` capture (length-only); C receipt `usage.prompt_tokens` 8→9 with matching fabricated capture (genuine server count 8) | `met=True` |
| MT07ToolRequestBound.md | M1b same-token-count different prompt; M2 request-body key order | `met=True` |
| MT11C1DropPid.md | M3 `live_port` has no naming control | `met=True` |
| MT12C1HollowExpect.md | H1 `ENVELOPE_CAP` 30→99; H3 self-test plant pinned; H4 combined | `met=True` |
| MT13C1NoRehash.md | B2 duplicate passing family keeps total 44; M5 composition | `met=True` |

I reproduced one survivor myself, H1 (`c1-mutant-H1-envelope-cap-99.out`): clone commit `1ab91752`, one line `ENVELOPE_CAP = 99`, scored from `clone/tools` with `--repo clone --tip 1ab91752… --work …`:
```
tool_present=1 live_ok=1/1 controls_targeted=44/44 eval_selftest=3/3 errors=0 met=True families[… tamper=8/8 …]
```
exit 0. The other survivors are seat-reported and were not re-run by me.

Relevance to the freeze's kill rule ("any control not rejected by its named check … a receipt the counter accepts without its own live contact"): MT06 A and C, if the seat's probe is right, are receipts with a fabricated `/tokenize` capture accepted at `met=True`, contrary to the predicate's "the server's own /tokenize prompt count … bound". The MT06 probe re-scores the mutant receipt against a fresh outside witness for a different prompt (witness count 19, receipt count 9); the receipt's own prompt is therefore not re-tokenized by the counter [INFERENCE from the probe output; not re-run by me]. That is a claim-level question for the L1, not a closure call from me.

Verdict for item 2: **OPEN.** The claim is re-claimed under a new predicate and counter, which closes the "provisional green" routing as a structure. The new claim has no settled falsification, and its falsification wave already reports survivors on the same tip where the counter prints `met=True`. The admission decision belongs to the L1.

---

## 3. Lane worktree untracked paths (routed defect 3)

### 3.1 Commands and output
`git -C /home/vgpnk/Projects/shokunin/kama-shokunin status --porcelain` (snapshot ~19:47–19:49 -03):
```
 M PROVINCE.md
 M corpus/SOURCES.md
 M corpus/knowledge/completion-request-plane.md
?? .ufo/waves/round-63/source/
?? .ufo/waves/round-63/w1.ready
?? .ufo/waves/round-63/w1.ready.dispatched
?? .ufo/waves/round-63/w1/
?? kama-shokunin/
```
`git status --porcelain -uall | grep -c '^??'` over the snapshot sequence: **148** (first check) → **391** → **775** (last). The count is still rising because the round-63 wave is writing. The final snapshot is in `untracked-by-dir.txt`:
```
      1 kama-shokunin/.ufo/waves/round-62
      2 .ufo/waves/round-63/source
    770 .ufo/waves/round-63/w1
      1 .ufo/waves/round-63/w1.ready
      1 .ufo/waves/round-63/w1.ready.dispatched
```
(775 total.) Lane HEAD is `03a6a1d8`; `git ls-tree` shows no `kama-shokunin/` path at `7ee8cbdf` or `03a6a1d8`.

### 3.2 Who authored what
Authorship is by self-identifying content, path naming and mtime (all files are owned by the same user; git has no authorship for untracked files).

| Group | Count | Author | Basis | Closure disposition (for L1) |
|---|---|---|---|---|
| `.ufo/waves/round-63/w1/out/<Seat>/…` and `w1/<Seat>.md` | ~770 | Round-63 wave seats (EX*, KR*, MT*, RV*, WR* named dirs) | out-dir names match seat IDs in `w1-spec.json`; reports self-identify; mtimes 19:39–19:49 | in-progress evidence; land or exclude at closure; not settled yet |
| `.ufo/waves/round-63/w1/{w1-dispatch,w1-spec,swarm-registry}.json` | 3 | L1 KamaR63 (dispatch artifacts) | `w1.ready` names `"l1":"KamaR63"` and the dispatch path | L1 artifacts; `swarm-registry.json` is mode 0600 while others are 0644 (noted, not changed) |
| `.ufo/waves/round-63/w1.ready`, `w1.ready.dispatched` | 2 | L1 KamaR63 | marker JSON names the L1 | L1 marker |
| `.ufo/waves/round-63/source/server-{common,task}.cpp.704366d76` | 2 | [INFERENCE] L1 (or its scribe) | upstream llama.cpp snapshots at 704366d76, cited by the uncommitted SOURCES rows S527/S528; mtimes 19:10, same minute as the `SOURCES.md` edit (19:10:58); no self-identifying header | L1 to land with S527/S528 or delete |
| `kama-shokunin/.ufo/waves/round-62/w1/A04C1SchemaFuzz.md` | 1 | round-62 seat A04C1SchemaFuzz, pre-landing draft written with a doubled `kama-shokunin/` prefix (a write from the lane root) | mtime 2026-10-28 09:26:49, earlier than the round-62 close-out commit `7ee8cbdf` (10:43:47); not in any committed tree; the tracked `.ufo/waves/round-62/w1/A04C1SchemaFuzz.md` is a later revision (`diff`: wording at lines 3, 13, 18–25, 55; same content) | superseded duplicate at a wrong path; delete or keep is the L1's decision; not touched |

Tracked but dirty (not untracked; listed because they are part of the same uncommitted state):
- `PROVINCE.md` (+2 lines, a round-63 note), `corpus/SOURCES.md` (+2 rows S527 `server-task.cpp` and S528 `server-common.cpp` at 704366d76), `corpus/knowledge/completion-request-plane.md` (+47 lines, round-63 v2 section). mtimes 19:10–19:13. Author [INFERENCE]: L1 KamaR63 or its scribe; uncommitted. Not touched.

### 3.3 Self-description contradiction (calibration)
The committed round-63 SCORECARD section says: "the lane worktree now has no lane-authored untracked paths" (round-62 close-out), and the r62 spot-check counted 122 untracked paths. At this audit the worktree has 775 untracked paths. The nested stray predates the `7ee8cbdf` close-out by mtime, so the sentence was already false when committed, unless the stray was created after the commit (mtime and the nested dir's 09:26:49 create time argue against that). This is a self-description mismatch of the kind C2 measures.

Verdict for item 3: **OPEN.** Not closed until the L1 (a) lands or deliberately excludes the round-63 wave outputs, (b) removes or lands the nested stray, (c) corrects the SCORECARD sentence, and (d) re-runs `git status`. I swept nothing and committed nothing.

---

## 4. Other facts observed (informational, not routed)
- `round42-selfdesc-reconcile` reports `mismatches=8` at the tip (C2 `selfdesc_mismatches=8`), as the freeze expects until the L1 re-derives the SCORECARD head after measurement.
- C2 at the tip reports `host_busy=1` (context-capacity-receipt declared `host-busy` outcome) — the bound outcome was accepted as declared.
- C1 counter ran in ~2 s with `live_ok=1/1` (the live server was launched and torn down by the lane tool on an unregistered loopback port). No registered consumer port and no foreign llama-server (1234, 45669) was touched.

## 5. Commands run (all read-only against the lane; mutations only inside `clone-c1`)
1. `git -C <lane> show 03a6a1d8:tools/round62-c2-counter.py | sed -n '268,272p'`
2. `git -C <lane> show 03a6a1d8:tools/round63-c2-counter.py` (+ round62 counter, saved to scratch) → `sens.py`, `p4.py`
3. `python3 tools/round63-c2-counter.py --repo <lane> --tip 03a6a1d8… --work <S>/run-c2-tip` → exit 1, `met=False` (selfdesc 8)
4. `python3 tools/round63-c1-counter.py --repo <lane> --tip 03a6a1d8… --work <S>/run-c1-tip` → exit 0, `met=True`
5. C1 mutant H1 (clone commit `1ab91752`) → exit 0, `met=True` (survivor)
6. C2 mutant C2-V (clone commit `926ca9b0`) → exit 1, `sens_selftest=0/4`, `met=False` (killed)
7. `git -C <lane> status --porcelain`, `status --porcelain -uall`, `ls-tree`, `diff` of the nested stray vs the tracked copy, `mtime` listings.

Scratch removed: `/fast/scratch/hyaku/kama-r63/w/KR07Routed62/` (receipts and outputs copied to `.ufo/waves/round-63/w1/out/KR07Routed62/` first).

Counter tallies (one line each, for the L1):
- C2 at 03a6a1d8: `population=12 rows=12 covered=12/12 bound=12 eval_lines=12 sensitive=12/12 dead=0 host_busy=1 mismatches=0 canonical=63 selfdesc_mismatches=8 sens_selftest=4/4 controls_rejected=12/12 errors=0 met=False` (exit 1)
- C2-V killed: `... sensitive=12/12 dead=0 host_busy=1 mismatches=0 canonical=63 selfdesc_mismatches=8 sens_selftest=0/4 controls_rejected=12/12 errors=0 met=False` (exit 1)
- C1 at 03a6a1d8: `tool_present=1 live_ok=1/1 controls_targeted=44/44 eval_selftest=3/3 errors=0 met=True` (exit 0)
- C1 mutant H1 (survivor): `tool_present=1 live_ok=1/1 controls_targeted=44/44 eval_selftest=3/3 errors=0 met=True` (exit 0)
