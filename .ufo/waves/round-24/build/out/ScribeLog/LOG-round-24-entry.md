## round 24 — r23 report, closure row 428 and the filed-evidence corrections (2026-10-21, appended)

- Motivation, taken from the filed round-23 record and the outside closure,
  not from the author verdict. The round-23 closure is MANIFEST row
  `/home/vgpnk/Projects/shokunin/MANIFEST.json` `rounds[428]` (round 23,
  lane `kama`, type `closure`, `admitted: false`, `verdict: rejected-harmed`,
  `verdicts.operability: harmed`, `trends.quality: harmed`,
  `rejection_streak_impact: 1`, `closed_at: 2026-10-21T17:44:26Z`, reviewer
  CloseMori22, who never authored or touched this lane). The filed report it
  rules on is `/home/vgpnk/Projects/shokunin/.ufo/reports/round-23/kama.md`
  (fleet commit `410b511`; lane tip `0df800e896f6bce285a81e794ad4ae1d1e6c3a71`;
  measured code `e876b953e9da28d2dffd29c923052bc626148c27`). The author's own
  "calibration 7 → 7, verified on the graded population" stands as the
  author's claim; admission was the closure's decision, and it rejected the
  round as harmed.
- Why that rejection binds round 24 (closure harm ruling, quoted in substance):
  a complete blobless partial clone (T01) and a paired promisor pack without
  promisor config (F23) turned a correct frozen exit-0 verdict into exit 2,
  and git ≥ 2.45 became a new requirement; disclosing a trade does not waive
  the no-trade rule, and fail-closed does not restore lost function. Routes
  kama-R23-H1 (restore correct ordinary complete promisor/filtered-clone cases
  without re-enabling lazy fetching) and kama-R23-H2 (treat the Git floor as an
  operator-approved environment prerequisite) are therefore open obligations.
  The round-24 repair is exactly H1: a promisor *metadata marker* alone must
  not make a complete local repository unevaluable; unavailable evidence must
  stay exit 2.
- Correction to the filed falsify-wave accounting: the wave produced 69
  durable lane reports, not 68. Re-observed at the lane:
  `ls .ufo/waves/round-23/falsify/advice/*.md | wc -l` → 69 (the directory
  holds 70 entries, one of them `swarm-registry.json`); 73 falsify seats minus
  the 4 dead seats (RowC01Clean, RowF07LogFollow, RowF09SignatureProgram,
  CritOpenHonesty — none of them left an advice file) = 69; the build wave
  shows the same seat-versus-report arithmetic (68 seats, 1 dead,
  `ls .ufo/waves/round-23/build/advice/*.md | wc -l` → 67). The miscount sits
  in `corpus/lessons/round-23.md:178-180` ("73 seats dispatched (68 reports;
  dead: …)") and in the closure's own routed check R23-C1 ("report falsify 69
  lane reports rather than 68 (68 final session replies plus RowC03 durable
  lane output)"); the filed report itself states seats and dead counts
  (73 falsify seats, 4 dead), from which 69 follows. The missing report is
  RowC03FabricatedFull, whose lane file
  `.ufo/waves/round-23/falsify/advice/RowC03FabricatedFull.md` (6618 bytes,
  mtime 2026-10-21 13:10:15 -03 = 16:10:15Z) was written before its final
  response was aborted with the host session at 16:10:50Z. Corroborated from the
  seat transcripts themselves: the round-23 session directory holds 141 seat
  `.jsonl` files, and RowC03's session summary file is 0 bytes (its last record is
  2026-10-21T16:10:51.353Z, type `custom`, with no assistant text) while its
  durable lane report exists — 68 final session replies plus RowC03's durable
  lane output = 69 lane reports. The filed
  round-23 bytes are not edited; this entry is the correction of record.
- Correction to the filed process-cleanup evidence: identity rows were
  retained for 40 of the 56 counted processes, not for all 56. The round-23
  lesson M7 (`corpus/lessons/round-23.md:174`) and the filed report (`:34`)
  say 56 blocked `git` processes were left by the grid timeout and were
  killed. The primary transcript
  `/home/vgpnk/.omp/agent/sessions/-Projects-shokunin/2026-10-21T16-10-39-768Z_01a15f3a-9f17-7238-ae23-4fe77ffa6530/KamaR23-2.jsonl`
  shows, at 2026-10-21T16:33:38.655Z, one command
  `ps -eo pid,lstart,args | grep -E 'repo-state-grid-|kama-r23|refusal' | grep -v grep | cut -c1-200 | head -40`
  whose result is 40 identity rows (pid, lstart, args) followed by the count
  `56` from the second command in the same line
  (`ps -eo pid,args | grep -E 'repo-state-grid-|/tmp/kama-r23' | grep -v grep | wc -l`);
  the kill at 16:33:46.620Z (`pkill -f -- '-C /tmp/repo-state-grid-'`,
  `pkill -f -- '/tmp/kama-r23w2/'`) is followed by a count of `0` at
  16:33:47.911Z. The 56 is therefore a count, not an identity inventory: 16
  of the 56 have no retained pid/start-time/argv row, so all 56 individual
  identities cannot be independently proved. The 40 retained rows match this
  round's `/tmp/repo-state-grid-*` and `/tmp/kama-r23w2/` fixture paths and
  start times inside the round, so no unrelated victim is evidenced — and none
  is proved absent. The closure's routed check records the same limit
  ("no complete 56-PID inventory was retained").
- Round-24 claim boundary for this entry: motivation and two status-neutral
  corrections only. No round-24 outcome is claimed or measured here — the
  promisor completeness repair, its grid, its mutants and the historical
  parity are unrun in this entry. The preregistered expected outcomes and
  the base are in `.ufo/waves/round-24/preregistration.json`
  (base `0df800e896f6bce285a81e794ad4ae1d1e6c3a71`; lane tip at the time of
  this entry `d1b9d956a0beda9ac32a1a2cf6ced875faeada0d`, the preregistration
  commit). Measured results, when they exist, belong in a later appended
  entry, not in this one.
