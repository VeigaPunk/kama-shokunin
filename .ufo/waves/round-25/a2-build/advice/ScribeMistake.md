# ScribeMistake — round-25 attempt-2 advice (frontier step: mine one mistake)

Verdict: draft `## Mistakes` entry for `corpus/lessons/round-25.md` produced with every pointer resolvable; the stale-count pair is verified — red at efe58e96 (`registered 27 stale 2`), green at 1fc41e346853afd98cbd7010af5db4e54dc877f7 (`registered 28 stale 0`), both exit 0.

## Behavior (what I did)

Read (all under the lane, `/home/vgpnk/Projects/shokunin/kama-shokunin`):
- `.ufo/waves/round-25/preregistration.json` — frontier_step.mistake (lines 57–61) says "captured-by none"; C1.command at line 16 is the registered counting command; C1.before at line 17 names `registered 27 stale 2 ['M11-listing-surrogates', 'M17-ref-shadow']` at 147f5bdd.
- `.ufo/waves/round-25/preregistration-amendment-1.json`, `preregistration-amendment-2.json` — amendment 2 (C1.before_reverified lines 15–18): `registered 27 stale 2` at efe58e96, exit 0, before the re-anchor edit; repair design M11/M17/M33.
- `.ufo/waves/round-25/count-c2.py`, `pilot.md`, `build/ATTEMPT-1-DISPOSITION.md`.
- `tests/report-audit/isolation-mutants.py` — round-25 re-anchor notes at lines 27–32; MUTANTS at 52–124; M11/M17/M33 entries (lines 63–72, 83–89, 115–124).
- `tools/report-landing-audit.py` — measured auditor (wrapped call at M11 site; peel-guarded refusal in `lookup()`; second call site in `bare_objects()`).
- `corpus/lessons/round-24-verifier-spotcheck.md:80–82` — the stale-instrument finding; `:151–152` — routed defect 2 (fix "only through separately authorized future work").
- `corpus/QUALITY.md` — KQ28–KQ35 rows plus KQ27 for comparison.
- `SCORECARD.md:1166` — isolation row names `python3 tests/report-audit/isolation-mutants.py --json` as its counting command.

Ran (in my own sandbox clone only; no lane/fleet git mutation, no jj, no llama-server child):
- Clone: `git clone --no-hardlinks /home/vgpnk/Projects/shokunin/kama-shokunin /fast/scratch/hyaku/kama-r25a2/ScribeMistake/clone` — exit 0; clone HEAD is the lane tip.
- `git rev-parse efe58e96` → `efe58e96e6cfbef88a0fba9d64505e18b7ad7356`.
- `git rev-parse 1fc41e346853afd98cbd7010af5db4e54dc877f7` → `1fc41e346853afd98cbd7010af5db4e54dc877f7`, subject `round-25: C1 re-anchor M11 and M17 to the measured auditor; second M17 call site registered as M33`.
- At efe58e96, the registered counting command (`preregistration.json` C1.command, via `run-counter.sh`): output `registered 27 stale 2 ['M11-listing-surrogates', 'M17-ref-shadow']`, exit 0.
- At 1fc41e346853afd98cbd7010af5db4e54dc877f7, same command: output `registered 28 stale 0 []`, exit 0.
- `git diff efe58e96 1fc41e346853afd98cbd7010af5db4e54dc877f7 -- tests/report-audit/isolation-mutants.py` — M11 literal widened to span the wrapped call; M17 literal widened to span the peel-guarded check plus comment in `lookup()`; new M33 for the second call site in `bare_objects()`; no id reused/retired. `git diff ... -- tools/report-landing-audit.py` — empty: the auditor was identical at both commits, i.e. the drift existed at efe58e96 purely as instrument-vs-auditor mismatch.

## Gates (acceptance checks)

- Draft text with every pointer resolvable: yes. `corpus/lessons/round-24-verifier-spotcheck.md:80–82` and `:151–152` resolve (verified by read); `preregistration.json:16` (C1.command) resolves; both commit hashes resolve and were observed; before/after counter outputs observed with exit codes.
- Fix shown able to fail: yes — same command prints `registered 27 stale 2` at efe58e96 and `registered 28 stale 0` at 1fc41e346853afd98cbd7010af5db4e54dc877f7, both exit 0.
- No llama-server child started: true.

## Touched surfaces (files I wrote)

- `corpus/lessons/` (production): none — draft is supplied for L1, the only writer of lane production files.
- `.ufo/waves/round-25/a2-build/out/ScribeMistake/mistakes-draft.md` — the draft `## Mistakes` entry (5 lines, table format matching `corpus/lessons/round-24.md:46–53`).
- `.ufo/waves/round-25/a2-build/advice/ScribeMistake.md` — this advice report.
- Scratch: `/fast/scratch/hyaku/kama-r25a2/ScribeMistake/run-counter.sh`, `driver.sh`, `clone/` (no-hardlinks clone used for the git-writing check).

## Findings

1. Class: stale-anchor — registered counting instrument drifted from the source it measures (M11 literal matched 0 times, M17 matched 2 times at the auditor as of round 24); nobody re-ran the registered count at landing.
2. Evidence pointer: `corpus/lessons/round-24-verifier-spotcheck.md:80–82` (finding), `:151–152` (routed defect); before output `registered 27 stale 2 ['M11-listing-surrogates', 'M17-ref-shadow']` at efe58e96, exit 0.
3. Captured-by: none among KQ28–KQ35 — KQ28 (landed-hash audit) governs report citations; KQ34 (isolation crosswalk/exit-class promise) governs how kills are credited, not instrument freshness; KQ35 (metadata controls) is unrelated; KQ29–KQ33 are unrelated (identity digest, I/O refusal, SOURCES supersession, trusted-repo scope, 40-hex classification). Nearest adjacent standing criterion is KQ27 (round 20): "Every quoted count is tied to the measured revision and independently enumerated after the artifact changes" — but its motivating lessons are report cardinalities (3→4, 76→77) and it did not fire here; the SCORECARD row kept citing the instrument without re-measuring. Hence the entry says captured-by none.
4. Fix (shown able to fail): the landing gate re-runs the registered counting command (`.ufo/waves/round-25/preregistration.json` C1.command) against the landed source; red at efe58e96 (stale 2), green at 1fc41e346853afd98cbd7010af5db4e54dc877f7 (stale 0), both exit 0.
5. Attempt-1 outputs reused: none as evidence — all observations above are my own runs/reads this session (per the attempt-2 standing-down rule).

## Out-of-scope items

- No production edits (no `corpus/lessons/round-25.md` write, no code changes), no commits/pushes, no jj, no git mutation of lane/fleet indexes (all git operations confined to the sandbox clone).
- No full mutant/grid run (`isolation-mutants.py --json`) — that supporting evidence belongs to the C1 executor seat; I ran only the counting command.
- No llama-server child started; no installs performed (no tools installed).

## Artifact paths

- Draft entry: `.ufo/waves/round-25/a2-build/out/ScribeMistake/mistakes-draft.md`
- Advice report: `.ufo/waves/round-25/a2-build/advice/ScribeMistake.md`
- Scratch: `/fast/scratch/hyaku/kama-r25a2/ScribeMistake/{run-counter.sh,driver.sh,clone/}`
