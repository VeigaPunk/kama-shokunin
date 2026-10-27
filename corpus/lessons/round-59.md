# Round 59 — falsified battery outcome binding and calibration counter

Author: KamaR59. Base: `8f7f58cd161f2b7dfa1709450c3ae79599c12833`. Frozen controls: `.ufo/waves/round-59/controls/freeze.txt`, committed `5d957d24e77bef5cb2e7c658060b2d98a37c96c5` before any seat result. C1 measurement: lane tip `aca8d0067ea25627c5015c2193c843965148bc8e`. C2 measurement: lane tip `2c7443abb8d6edb8a5b0f91dfee9f81b824f6d35`, fleet ref `0f99f606120d0c884656c6e7a290f0e8f33c2181` (current at the wave's final replay; the `3f3dd973` read earlier in the wave was superseded by a fleet commit).

## Claims and verdicts

- **C1 — operability 8→8, sourced on S517.** The finite frozen counter prints `genuine=1/1 benign=3/3 noop_rejected=16/16 errors=0 met=True`, exit 0. The frozen predicate nevertheless fails: R04's one-call battery routed to `python3 other-script --counter ...` also passes the checker (`runs=5 passed=5/5 errors=0 met=True`, exit 0), and R15's checker keyed only to fixture directory names passes the same counter. The checker also synthesizes its observations from `BAD_ENV` source text rather than observing the leg's actual child result (K02). **Not verified; no operability score increase.**
- **C2 — calibration 7→7.** The scorecard replaced the literal spot-check count and pinned fleet hash with a command that resolves the lane tip and an explicit fleet ref. The frozen counter measured 3 mismatches at base and 0 at the edited row, but K05's one-line static-assertion control and M12's eight one-clause counter mutations all still met. The frozen sentence also requires an external S517/S518 admit/reject spot-check; no such non-author record exists and MANIFEST still has kama r57 as its latest closure. **Not verified; no calibration score increase or discernment progress.**

Scores remain operability 8 and calibration 7. No capability is acquired; no round claim is admitted. The counter outputs below are measurements, not independent confirmation of the frozen semantics.

## Gate — sources opened and decisions offered for outside sampling

**S517 — ADMIT candidate, tier A, mined.** Re-opened this round at https://docs.python.org/3/library/sys.html#sys.setprofile, 2026-10-27 (Python 3.15.2 documentation; page title checked). Located quote, 18 words: “only on call and return, but the return event is reported even when an exception has been set”. This supports call/return event semantics only; it does not establish per-line execution, a child process's actual output, or a leg's consumption of a return value. C1 cites S517 for the profile hook only. Existing SOURCES row S517 `used-by`: `tools/round58-battery-exec-check.py, corpus/knowledge/battery-execution-evidence.md, corpus/lessons/round-58.md` → `tools/round58-battery-exec-check.py, corpus/knowledge/battery-execution-evidence.md, corpus/lessons/round-58.md, corpus/lessons/round-59.md`; status, recheck and all other cells unchanged.

**S518 — ADMIT candidate, tier A, mined.** Re-opened this round at https://man7.org/linux/man-pages/man8/ld.so.8.html, 2026-10-27. Located quote, 6 words: “LD_AUDIT is ignored in secure-execution mode.” Live response SHA-256 `d9b7737e6c9a38f6c7ce11a4feec834704d6ad5139dc790afa9798faf0379f83` matches the committed round-56 snapshot. It adds secure-execution/token scope beyond S513's narrow name-only claim.

**S513 — REJECT retained, claim-scoped.** The narrow name-presence claim remains covered by S512; the S512 snapshot lacks `secure-execution` and `$ORIGIN` while the opened `ld.so(8)` source has them. S518 records that delta; it does not retroactively change S513's row.

**Quarantine slice — all seven IDs re-opened at their cited URLs; no new knowledge entry or SOURCES row admitted.** `S200` quote absent; `S202` quote present but no admitted lane entry cites the generic Compose dependency semantics, so held/not appended; `S206` quote present and already held as mined row S206; `S210` “Page Not Found” absent; `S211` `still-live` absent (source reachable); `S224` compound “render-only … always return 200” quote not located (the page does contain `check_health()` and a 503 path); `S230` quote present and already covered by mined S329. Detailed URLs, locations and per-row dispositions: `.ufo/waves/round-59/w1/out/S05Quarantine.md`. This round adds no quarantine-derived corpus entry.

**Non-author sample requested, not recorded:** admit candidates S517 and S518; reject candidates S513 and S200/S210/S211/S224. The wave seats are lane authors; no outside reviewer verdict exists at filing. Do not call discernment improved. S517 was opened this round and C1 cites its registry row; no new source IDs were added.

Assimilation: none from `shokuknow/merge/kama/`; the opened payload-absent register slice was hand-checked, but its only in-scope present entries were already represented by S206/S329. `considerthese/2026-10-26.md` was opened; proposal 3 does not match the frozen claims, and no proposal was implemented.

## Census before → after

Start: `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --file corpus/SOURCES.md` from the lane root → exit 0, 259 rows (`.ufo/waves/round-59/census/start.out`, `start.exit`). Counting command over the frozen base: `git -C /home/vgpnk/Projects/shokunin/kama-shokunin show 8f7f58cd161f2b7dfa1709450c3ae79599c12833:corpus/SOURCES.md | grep -cE '^ {0,3}\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|'` → 259.

End: `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama` → exit 0; final line `kama\tok\t/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md` (`.ufo/waves/round-59/census/end.out`, `end.exit`). Same row-count command over the final lane tip → 259. Added by tier: none; added by status: none; touched row: S517 `used-by` old→new as above; status/recheck unchanged; frontier rows advanced: none. Start and end registry count remains 259.

## Mistakes

| class | evidence | captured-by | fix / disposition |
|---|---|---|---|
| unlisted-runner-decoy | R04's D1 one-call `other-script` battery is accepted by the measured checker, exit 0 and `met=True` (`.ufo/waves/round-59/w1/out/R04DecoyArgv.md:46-62`). | none: N16 tests a second invocation, not a one-call runner substitution. | No fix shipped under the frozen round-59 counter. KQ99 records the required future bar; the current C1 claim remains unverified. |
| fixture-name-oracle | R15's checker that predicts accept/reject from `N*` directory names passes the frozen C1 counter (`.ufo/waves/round-59/w1/out/R15CounterGaming.md`, F1). | none: counter judges exit patterns on names that reveal the expected class. | No fix shipped under the frozen counter. A future counter must use non-oracular fixture names/identity and reject a name-keyed checker before this can count. |
| calibration-counter-static-assertion | K05's scorecard-only fixture appends a literal assertion that count/pointer are static; C2 still returns `mismatches=0 met=True`, exit 0 (`.ufo/waves/round-59/w1/out/K05C2Noop.md:19-35`). M12 drops each of the eight mismatch clauses individually and all eight mutants still return met=True (`M12C2Clauses.md:15-28`). | none: C2 recognizes row strings rather than proving their semantic derivation, and all mismatch clauses are zero in the genuine case. | No fix shipped under the frozen counter. KQ99 is a C1-specific criterion only; C2's corresponding control set must be designed and frozen before next-round data. |
| ambient-git-environment | X12's `GIT_DIR`/`GIT_WORK_TREE` controls change C1 from a clean pass to false `met=False` with `errors=0`, and C2 to could-not-evaluate exit 2 (`.ufo/waves/round-59/w1/out/X12Portability.md:132-176`). | none: C1's nested `real_run` and C2's `git()` inherit ambient GIT_* variables. | No fix shipped in this frozen round. Future tool change must scrub GIT_* for every nested Git process and re-run clean/hostile environment controls. |
| missing-lesson-target | After adding S517 `used-by` for this lesson but before the lesson existed, canonical validate returned exit 1, `E11 S517 missing used-by corpus/lessons/round-59.md` (`census/end-prelesson.out`, `end-prelesson.exit`). | SOURCES E11. | Wrote this lesson before the final census; canonical end validator then returned exit 0. |
| incomplete-seat-evidence | `w1-results.json` has 64 result entries/null notes, but M08AlwaysReject output is unfinished instructions and no `w1/out/M08AlwaysReject.md` exists. | wave result/artifact inventory. | Not repaired or misrepresented; counted as an incomplete/unverifiable seat, not a dead-seat count. |

**New criterion — KQ99** was appended to `corpus/QUALITY.md` after R04/R15 demonstrated the missing runner-path and name-keyed controls. It is a future admission bar, not a repair or a retroactive C1 pass. The observed D1 is the falsifying before-state; no claim that KQ99's requested checks have been implemented.

## SHONEN assessment

The four boxes remain author assertions `[~]`; no outside verifier checked these criteria this round. See the fleet report's `## SHONEN` lines for the box-by-box pointers.
