# ExecPreregTimeCheck — advice report (round-26 wave 1)

**Verdict:** built `prereg-time-check.py`; it fails (exit 1) on the two wrong-time
round-26 preregistration revisions, passes (exit 0) on the two corrected ones, and
shows the same false-timestamp class in every round-25 amendment the lesson cites —
plus the original round-25 preregistration and amendment 1, which the lesson's row
53 does not list as instances.

## Files written
- `.ufo/waves/round-26/w1-build/out/ExecPreregTimeCheck/prereg-time-check.py`
  (tool, executable).
- `.ufo/waves/round-26/w1-build/out/ExecPreregTimeCheck/RUNS.txt`
  (full receipt log: selftest + every lane run, with exit codes).

## Tool behavior
`prereg-time-check.py --repo <lane> --path <repo-relative path> --rev <rev>`
reads every ISO-8601 UTC time (`YYYY-MM-DDTHH:MM[:SS]Z`) in the file at that
revision and compares it with the committer time of the commit that introduced
that version (`git log -1 --format=%cI <rev> -- <path>`):
- exit 0: no timestamp later than the committer time;
- exit 1: at least one timestamp later;
- exit 2: could not evaluate (bad rev/path, git failure).

Horizon: a later timestamp is flagged only when it is within `--max-future`
(default 86400 s) after the commit. This is required for the round-26 frozen tip:
`preregistration.json:33` holds a provider 429 quota-reset `resets` time
(`2026-10-25T14:27:28Z`, ~48 h after its commit) — scheduled future data, not a
false timestamp. `--strict` disables the horizon and flags any later timestamp
(the literal reading; it does fail the tip on the quota reset).

## Acceptance receipts (lane repo `/home/vgpnk/Projects/shokunin/kama-shokunin`, read-only git)
round-26 `preregistration.json`:
- `a4a159c39967e88a89b0808dcd201c79c474efd1` → exit 1: line 6 `2026-10-23T03:45Z`
  later than commit `03:18:51Z` by 1569 s.
- `a12850c5cbc1013e60cc5bba2d6800d1cd634499` → exit 1: line 6 `03:45Z` (+1517 s)
  and line 29 `2026-10-23T03:55Z` (+2117 s).
- `f071209a0f956680b5722e09242e784a1644e216` → exit 0: `03:18:51Z`/`03:19:43Z`
  both at/before commit `03:20:14Z`.
- `a23c0e042114016a909eb15173aa6df74b5b7eb0` → exit 0: `03:18:51Z`/`03:19:43Z`
  before commit `03:32:54Z`; quota reset `2026-10-25T14:27:28Z` beyond horizon.
- `--strict` at the tip → exit 1 (quota reset flagged).

round-25 sweep (all at the commits that introduced each file):
- `preregistration.json` @ `efe58e96` → exit 1: `2026-10-22T08:31:00Z` +76 s.
- `preregistration-amendment-1.json` @ `efe58e96` → exit 1: `08:30Z` (+16 s)
  and `08:31:00Z` (+76 s).
- `preregistration-amendment-2.json` @ `5388b7cf` → exit 1: `09:30Z` +76 s
  (matches lesson row 53).
- `preregistration-amendment-3.json` @ `c808ba07` → exit 1: `09:40Z` +75 s
  (matches lesson row 53).
- `preregistration-amendment-4.json` @ `46fb04bd` → exit 0
  (matches lesson row 53: fixes the class).
- `errata-attempt-2.json` @ `fa3b62ae` → exit 0 (`09:38:45Z` before commit).

## Finding beyond the lesson text
Lesson `corpus/lessons/round-25.md:53` says "the same class amendment 1 corrected".
The tool shows amendment 1 itself carried the class at introduction (`written_utc
08:30Z` committed at `08:29:44Z`, +16 s), as did the original round-25
`preregistration.json` (`08:31:00Z` at the same commit, +76 s). Amendment 4 and
`errata-attempt-2.json` are the revisions where every timestamp is ≤ commit time.
This is exactly the mined mistake class: handwritten "now" guesses drift ahead of
the real commit time, and the fix (name observed `date -u` output / defer to the
commit) is only verifiable mechanically — which is what this tool adds.

## Selftest
10 case + 2 error cases run in a temp repo under
`/fast/scratch/hyaku/kama-r26/ExecPreregTimeCheck/ptc-selftest-btkilz7s`
(all commits use controlled committer dates): all PASS, `SELFTEST PASS`, rc 0.
Cases cover: clean past time; minute/second-precision guesses after commit → 1;
far-future data beyond horizon → 0; `--strict` flags far-future → 1; boundary
`==` time; no timestamps; malformed `2026-13-40T03:45Z` skipped; missing path → 2;
bad revision → 2. Full output in `RUNS.txt`.

## Risks / notes
- The horizon is a heuristic (default 24 h). A genuinely wrong guess more than
  24 h ahead would pass unless `--strict` is used; L1 should prefer `--strict`
  for claims files that must not hold future scheduled data, and keep the default
  for files that legitimately may.
- The check reads file text, not parsed JSON; the regex accepts only the exact
  Z-suffix shape requested, so JSON strings and prose both match.
- No servers started, no subagents spawned, no lane/index/roster mutation;
  all lane git use was read-only. No tools installed (python3 3.14.8 and git
  2.56.0 were present).
