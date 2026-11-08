# MT01ProbeMutants — settled dead (kama r94 w1)

Seat role: mutation-tester (attack). Spawned 2026-11-07T23:42:06 with the rest of wave `w1`; the
orchestrator's dispatcher lost its handle in a kernel restart mid-wave, so it was settled as dead at
the wave close (2026-11-08) rather than cancelled or timed out.

Evidence that it produced nothing:

- `.ufo/waves/round-94/w1/out/MT01ProbeMutants/` is empty (no files at any point after the spawn).
- No `MT01ProbeMutants.md` report was written in the wave dir; the wave holds 12 reports for 13 seats.
- `.ufo/waves/round-94/w1-results.json` carries an `MT01ProbeMutants` row whose output is
  `<output unavailable: FileNotFoundError('Output not found: MT01ProbeMutants-5…')>` — the handle the
  results blob would have copied from no longer exists.
- The orchestrator's settlement notice states the handle was `None` (lost on kernel restart), not a
  hung agent, so the seat could never settle on its own.

This is a dead seat in the round census, not a quality rejection and not a timeout. It had no artifact
to reconcile, so the pre-file falsification ledger cites this file for it. No replacement was spawned
(protocol: never replace a dead seat).
