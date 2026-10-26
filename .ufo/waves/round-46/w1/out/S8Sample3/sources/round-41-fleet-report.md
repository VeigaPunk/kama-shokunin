# kama round 41 report

author: kama L1 (agent `KamaR41`)
date: 2026-10-25
attempt: 1 of 1 (watchdog: `2026-10-25T16:50:00-03:00 launch kama round=41 pgid=134737 driver=hyaku-inline attempt=1`; no `lane-dead-no-report kama round=41` line, so no earlier attempt and nothing inherited from one)
base: `8893b89466250c4d542912a867392698d2da00ce` (round-40 verifier spot-check, the lane remote tip at launch)
lane tip: `aa960577c1bff891d37bbf3ad7914745ff3aaa7a` (`git ls-remote origin refs/heads/master` prints this hash)
Stale-lane: progressing. The current mission is kama round 41 (respawn-per-round driver), and no other lane mission is open. The parked worktree `/home/vgpnk/Projects/shokunin/kama-shokunin` is still detached on the mutation-sandbox lineage (round-40 D5), so every measurement and commit used a fresh clone of the lane remote, `/fast/scratch/kama-r41/clone`. The parked path served only as the seats' report directory and the `.ready` handoff.

## Work performed

Declared claims: **C1 calibration 7→7.** The SCORECARD head `## Axes` table, the lane's standing self-assessment, now matches observed repository state. Calibration is the lowest assigned non-retired axis (operability 8) and the stagnation nudge is inactive. **C2 operability 8→8, capability acquisition `pin-watch`.** A runnable tool reports, for each pinned serving engine, whether newer upstream releases exist. C2 is the sourced claim (S475, opened this round) and mines `considerthese/2026-10-25.md` proposal 2. The two claims write disjoint files; separability is shown by the `pos-c1only`/`pos-c2only` controls and by seat R41B17.

- **Protocol load:** `skill://shokunin` is not installed on this host. The L1 read the fleet `MISSION.md`, `AXES.md`, `CORPUS.md` and `LEARNING.md`, `skill://swarm`, `skill://godspeed`, and the lane `SCORECARD.md`, `SHONEN.md`, `PROVINCE.md`, `corpus/README.md` `## Frontier`, `corpus/lessons/round-40.md`, `corpus/lessons/round-40-verifier-spotcheck.md` and `considerthese/2026-10-25.md`.
- **Freeze before data:** commit `6fec0c4cd7b63ac733f2ae47fe73d1366b40c6dd` holds `.ufo/waves/round-41/preregistration.json`, the counters `tools/round41-scorecard-reconcile.py` and `tools/round41-pinwatch-audit.py`, and controls `.ufo/waves/round-41/controls/` (builder `build_controls.py`). The controls are: base and freeze (both claims fail); positive controls `pos-c1only`, `pos-c2only` and `pos-both` (each claim meets only with its own work); and six shortcut controls that each fail (`junk-c1-hollow`, `junk-c1-scoresonly`, `junk-c1-falserun`, `junk-c2-stub`, `junk-c2-nocap`, `junk-c2-unsourced`). The census start receipts landed in the same commit.
- **C1 work, commit `24aa1d3485c107f88b8b838892d43ea7587befcf`:** the head table was replaced with one whose hashes, line counts, run lines and paths re-derive at the tip (`SCORECARD.md` §Axes). The round-3 table is kept byte-intact below it (seat R41A07: cmp exit 0, numstat `36 0`).
- **C2 work, commit `24aa1d34`:** adds `tools/pin-watch.py`, `registry/engine-pins.tsv`, `corpus/knowledge/engine-pin-watch.md` and rows S475–S477. It adds a round-41 canonical capability list with a `pin-watch` row (`SCORECARD.md` §Round 41) and a coverage row (`corpus/README.md` §Coverage map — round 41 addition). Tag evidence: `.ufo/waves/round-41/c2/ls-remote-{sglang,vllm,llama.cpp}.txt` and `git-scm-docs-git-ls-remote.html`.
- **Routed round-40 defects, commit `4fe239a479bd86478912f3d79d42ec036ac9ae04`:**
  - D1: QUALITY criterion KQ48, `corpus/QUALITY.md` §Criterion added — round 41.
  - D2: package reject named per theme with flip conditions, `corpus/lessons/round-41.md` §Gate — round-40 package reject, named.
  - D3: append-only pointer at the end of `corpus/lessons/round-38.md`.
  - D4: `SCORECARD.md` §Round-40 record corrections (N3 dead pointer, N2 39-hex quote).
  - D5: refreshed L0 question, fleet commit `786b085e7c5cbb2af0358e083b3d18be2e4a13ee`.
- **Own mistake mined:** the head table had been stale since round 10. Seat R41A15 measured mismatches of 13 at round 10 and 16 at rounds 20–40. KQ49 now makes that table a re-derived artifact. `corpus/lessons/round-41.md` §Mistakes carries six rows.
- **Wave integration, commit `4fe239a4`:**
  - `tools/pin-watch.py` hardened per the security seat R41B08. It refuses option-shaped repo cells, path-unsafe engine names and quantified regex groups; it caps tag length, requires ASCII digit groups and closes the child's stdin. Selftest is now `selftest pass=9 fail=0`.
  - Entry limits were added per R41B10 (final `.postN` and four-part tags are dropped) and R41B22 (the prior one-engine SGLang check is credited).
  - The dead `PROVINCE.md` §Adjacent pointer in the adjacency row was fixed (R41A03).
  - Summary of all findings: `corpus/lessons/round-41.md` §Wave-1 findings.
- **Wave:** one validated v2 wave, `kama-r41-w1`: 64 seats in one inline handoff. Validator: `ufo-swarm-wave.mjs` with `ufo-wave-policy-v2.json`, counts `spawn 64 total 64`. Dispatch: `.ufo/waves/round-41/w1/dispatch.json`. Results: `.ufo/waves/round-41/w1/kama-r41-w1-results.json`, with 64 final outputs.
- **Tooling:** the L1 installed nothing. Seat R41B23 installed CPython 3.11.17, 3.12.15 and 3.13.16 via `uv python install` (uv 0.13.0, official uv-managed builds) for its interpreter matrix. No pacman was used.

## Landed changes

Each change maps to an `LOG.md` entry and to the commit that carries it.

| Change | LOG entry | Lane commit |
|---|---|---|
| Freeze: preregistration, both counters, control builder and 22 control receipts, census start | `LOG.md` §Round 41, freeze bullet | `6fec0c4cd7b63ac733f2ae47fe73d1366b40c6dd` |
| C1 reconciled head table; C2 pin-watch tool, pins, entry, S475–S477, capability list, coverage row; lesson Gate; tag evidence | `LOG.md` §Round 41, C1 and C2 bullets | `24aa1d3485c107f88b8b838892d43ea7587befcf` |
| Integration: D1–D4, KQ48/KQ49, named package reject, pin-watch hardening, entry limits, README frontier disposition, LOG entry, 64 seat reports and results, candidate receipts | `LOG.md` §Round 41, integration and wave bullets | `4fe239a479bd86478912f3d79d42ec036ac9ae04` |
| Measured receipts at `4fe239a4`, end census, SCORECARD §Round-41 measured results and §Planned (round 42) | `LOG.md` §Round 41, last bullet (points to the measured section) | `aa960577c1bff891d37bbf3ad7914745ff3aaa7a` |

Fleet repo: L0 question `786b085e7c5cbb2af0358e083b3d18be2e4a13ee`. This report is committed through `fleet-commit.sh --as kama`.

Round shape: **one v2 wave of 64 seats** (`kama-r41-w1`), no residual call, round total 64.

| Role | Seats |
|---|---|
| executor | 18 |
| scribe | 13 |
| reviewer | 11 |
| critic | 7 |
| mutation-tester | 4 |
| scout | 4 |
| connector | 4 |
| simplifier | 1 |
| revenger | 1 |
| sentinel | 1 |

- Executor, scribe and simplifier seats: 32 of 64 (50%).
- Attack seats (reviewer, critic, mutation-tester): 22 of 64 (34%).
- §3 L2 floor mapping: the planner seat is held by the L1 (the validator rejects `planner`), and the bounded planning data walk rode the freeze controls. The wave carried 4 connector, 18 executor, 13 scribe, 4 scout, 11 reviewer and 7 critic seats.
- Dead seats: **0**. All 64 settled with a final output.
- Exception: seat R41D07 wrote no report file. The L1 recovered its first yield verbatim from its session transcript into `.ufo/waves/round-41/w1/out/R41D07.md`, with the source named. This is recorded as a `landing` mistake.
- Answering models were not recorded; no claim depends on a seat's model.

Inherited state: the parked worktree's 105 porcelain lines (round-35/36 carry plus the mutation-sandbox jj lineage) were neither authored nor touched by this round. They are named, not resolved; that is operator-owned (L0). Nothing inherited came from an earlier attempt of round 41.

## Before → after measurements

- **C1, calibration 7→7.**
  - Command: `python3 tools/round41-scorecard-reconcile.py --repo <fresh clone> --tip <full commit> --out <receipt>`.
  - Base `8893b894`: `axes=6 facts=13 hash_bad=2 lines_bad=2 run_bad=0 dead=6 score_bad=2 hollow=4 mismatches=16 met=False` (exit 1), receipt `.ufo/waves/round-41/controls/base.c1.out`.
  - Measured commit `4fe239a479bd86478912f3d79d42ec036ac9ae04`: `axes=6 facts=24 hash_bad=0 lines_bad=0 run_bad=0 dead=0 score_bad=0 hollow=0 mismatches=0 met=True` (exit 0), receipt `.ufo/waves/round-41/c1/after.out`. A re-run at the final tip `aa960577` gives the same line.
  - Kill rule met: False→True. Predicate, counter and vector are unchanged since the freeze.
  - Limit: the counter checks that facts are true, not that they are relevant. Seat R41A03 judged four of six rows weak evidence for their axis. Seat R41A06 showed two cheap edits that meet the counter. So `met=True` is necessary but not sufficient; relevance is left to the outside closure.
- **C2, operability 8→8, capability `pin-watch`.**
  - Command: `python3 tools/round41-pinwatch-audit.py --repo <fresh clone> --tip <full commit> [--seed N] --out <receipt>`.
  - Base: `tool=0 contract=0 live=0 sourced=0 capability=0 met=False` (exit 1), receipt `.ufo/waves/round-41/controls/base.c2.out`.
  - At `4fe239a4`: `tool=1 contract=1 live=1 sourced=1 capability=1 met=True`, exit 0, with seed 788600741 and with seed 41. Receipts: `.ufo/waves/round-41/c2/after.out`, `after-seed41.out`.
  - The receipt's live reference shows three real statuses with `error=0`: `engine=llama.cpp pin=b11755 newest=b11887 newer=115 status=behind`, SGLang and vLLM `current`. That rules out the degenerate network-off agreement that seat R41B20 demonstrated against the frozen `live` leg.
  - Capability census: base `listed 6 observed 6 missing 0 unsubstantiated 0 met True` → `listed 7 observed 7 missing 0 unsubstantiated 0 met True` (`.ufo/waves/round-41/c2/capability-audit.out`).

## Sources & frontier

Registry rows went from **215 to 218** (`/home/vgpnk/Projects/shokunin/scripts/sources-census.sh census --file corpus/SOURCES.md`, exit 0 both times; `.ufo/waves/round-41/census-{start,end}-counts.out`).

| Measure | Start | End |
|---|---|---|
| Tier A | 205 | 208 |
| Tier B | 7 | 7 |
| Tier C | 3 | 3 |
| Status mined | 196 | 199 |
| Status queued | 8 | 8 |
| Status rejected | 11 | 11 |
| Missing | 0 | 0 |

Rows added, all tier A and `mined`, opened 2026-10-25:

| Row | Kind | Source |
|---|---|---|
| S475 | docs | https://git-scm.com/docs/git-ls-remote |
| S476 | own-work | vLLM tag inventory |
| S477 | own-work | llama.cpp tag inventory |

- Rows touched old→new: none.
- Frontier rows advanced: S475, S476 and S477, now cited by the new entry `corpus/knowledge/engine-pin-watch.md`.
- S475 located quote (22 words, §OUTPUT): "two such lines are shown: one with the refname for the tag itself as <ref>, and another with <ref> followed by ^{}". Seat R41B14 re-opened the page and reproduced its digest `296a3d5c…5f74` byte-for-byte.
- Lesson Gate: `corpus/lessons/round-41.md` §Gate (URLs, access dates, quotes).
- Mirror validate (`sources-census.sh validate --root <mirror of the tip clone> kama`): exit 0 at start and at end, 93 W04 and 0 E both times. The fleet-root validate also exits 0 at start and end, but it reads the parked worktree's registry, not the tip. Seat R41A19 confirmed this, and it is round-40 N4.

Assimilation: none adopted from `merge/kama/`. The package is rejected by named theme with flip conditions (the D2 fix); the ground is that no frozen claim consumes any theme. The 27 held / 81 not held / 34 no-URL counts were re-derived independently. The id-collision check and staged-row transformation were not needed, because nothing was appended from the package. Quarantine slice: 7 rows (S200, S202, S206, S210, S211, S224, S230), all with prior hand-check verdicts (seat R41F01). considerthese: `considerthese/2026-10-25.md` proposal 2 was mined into C2. Its scope cut and pointer-not-evidence grounding are recorded in the lesson §considerthese.

Mined mistake: six `## Mistakes` rows (stale-premise, vacuous ×2, reference-drift, provider, landing). Sourced claim: C2 (S475).

### Census transcripts

Start: `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama`. Its complete output follows, with the exit code appended; it is also committed as `.ufo/waves/round-41/census-start-fleetroot.out` (94 lines: 93 W04, 0 E).

```text
kama	W04	S031 duplicate url docs.ollama.com/api/tags across scopes
kama	W04	S043 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server.cpp across scopes
kama	W04	S056 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/common/arg.cpp across scopes
kama	W04	S060 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
kama	W04	S064 duplicate url docs.python.org/3.14/library/subprocess.html across scopes
kama	W04	S065 duplicate url docs.python.org/3.14/library/sys.html across scopes
kama	W04	S067 duplicate url man7.org/linux/man-pages/man8/ld.so.8.html across scopes
kama	W04	S071 duplicate url git-scm.com/docs/git-cat-file across scopes
kama	W04	S077 duplicate url docs.python.org/3.14/library/os.html across scopes
kama	W04	S078 duplicate url man7.org/linux/man-pages/man8/ldconfig.8.html across scopes
kama	W04	S079 duplicate url man7.org/linux/man-pages/man8/ld.so.8.html across scopes
kama	W04	S080 duplicate url nix.dev/manual/nix/2.34/protocols/nix-archive across scopes
kama	W04	S081 duplicate url go.googlesource.com/mod/+/refs/tags/v0.42.0/sumdb/dirhash/hash.go across scopes
kama	W04	S082 duplicate url git-scm.com/docs/gitrevisions across scopes
kama	W04	S083 duplicate url git-scm.com/docs/git-cat-file across scopes
kama	W04	S084 duplicate url docs.jj-vcs.dev/latest/cli-reference across scopes
kama	W04	S085 duplicate url git-scm.com/docs/git-log across scopes
kama	W04	S086 duplicate url tldp.org/HOWTO/Program-Library-HOWTO/shared-libraries.html across scopes
kama	W04	S087 duplicate url docs.python.org/3.14/builtins/functions.html across scopes
kama	W04	S088 duplicate url docs.python.org/3.14/library/os.html across scopes
kama	W04	S093 duplicate url git-scm.com/docs/git-log across scopes
kama	W04	S097 duplicate url docs.python.org/3.14/library/subprocess.html across scopes
kama	W04	S100 duplicate url git-scm.com/docs/git-config across scopes
kama	W04	S103 duplicate url git-scm.com/docs/partial-clone across scopes
kama	W04	S105 duplicate url docs.python.org/3.14/builtins/stdtypes.html across scopes
kama	W04	S108 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server.cpp across scopes
kama	W04	S109 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
kama	W04	S110 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/common/arg.cpp across scopes
kama	W04	S112 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/README.md across scopes
kama	W04	S114 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
kama	W04	S115 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
kama	W04	S116 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
kama	W04	S117 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
kama	W04	S118 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
kama	W04	S119 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
kama	W04	S120 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
kama	W04	S121 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
kama	W04	S122 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
kama	W04	S123 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
kama	W04	S124 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
kama	W04	S125 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
kama	W04	S127 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp across scopes
kama	W04	S129 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/ggml/src/gguf.cpp across scopes
kama	W04	S130 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/src/llama-context.cpp across scopes
kama	W04	S131 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/common/fit.cpp across scopes
kama	W04	S132 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/src/llama-context.cpp across scopes
kama	W04	S133 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
kama	W04	S134 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/README.md across scopes
kama	W04	S135 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/src/llama-kv-cache.cpp across scopes
kama	W04	S137 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp across scopes
kama	W04	S141 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
kama	W04	S142 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
kama	W04	S143 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
kama	W04	S144 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
kama	W04	S145 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
kama	W04	S146 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
kama	W04	S147 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
kama	W04	S148 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
kama	W04	S149 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
kama	W04	S150 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
kama	W04	S151 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
kama	W04	S152 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
kama	W04	S153 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
kama	W04	S154 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
kama	W04	S155 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
kama	W04	S156 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
kama	W04	S157 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
kama	W04	S158 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
kama	W04	S159 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
kama	W04	S160 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
kama	W04	S161 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
kama	W04	S162 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
kama	W04	S163 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
kama	W04	S164 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
kama	W04	S165 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
kama	W04	S166 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
kama	W04	S167 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
kama	W04	S168 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
kama	W04	S169 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
kama	W04	S170 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
kama	W04	S171 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
kama	W04	S172 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
kama	W04	S173 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
kama	W04	S181 duplicate url raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp across scopes
kama	W04	S182 duplicate url raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp across scopes
kama	W04	S183 duplicate url raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp across scopes
kama	W04	S184 duplicate url raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp across scopes
kama	W04	S185 duplicate url raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp across scopes
kama	W04	S186 duplicate url raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp across scopes
kama	W04	S187 duplicate url raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp across scopes
kama	W04	S188 duplicate url raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp across scopes
kama	W04	S189 duplicate url raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp across scopes
kama	W04	S191 duplicate url raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
kama	ok	/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md
exit=0
```

End: the same command, complete output (`.ufo/waves/round-41/census-end-fleetroot.out`, 94 lines: 93 W04, 0 E):

```text
kama	W04	S031 duplicate url docs.ollama.com/api/tags across scopes
kama	W04	S043 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server.cpp across scopes
kama	W04	S056 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/common/arg.cpp across scopes
kama	W04	S060 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
kama	W04	S064 duplicate url docs.python.org/3.14/library/subprocess.html across scopes
kama	W04	S065 duplicate url docs.python.org/3.14/library/sys.html across scopes
kama	W04	S067 duplicate url man7.org/linux/man-pages/man8/ld.so.8.html across scopes
kama	W04	S071 duplicate url git-scm.com/docs/git-cat-file across scopes
kama	W04	S077 duplicate url docs.python.org/3.14/library/os.html across scopes
kama	W04	S078 duplicate url man7.org/linux/man-pages/man8/ldconfig.8.html across scopes
kama	W04	S079 duplicate url man7.org/linux/man-pages/man8/ld.so.8.html across scopes
kama	W04	S080 duplicate url nix.dev/manual/nix/2.34/protocols/nix-archive across scopes
kama	W04	S081 duplicate url go.googlesource.com/mod/+/refs/tags/v0.42.0/sumdb/dirhash/hash.go across scopes
kama	W04	S082 duplicate url git-scm.com/docs/gitrevisions across scopes
kama	W04	S083 duplicate url git-scm.com/docs/git-cat-file across scopes
kama	W04	S084 duplicate url docs.jj-vcs.dev/latest/cli-reference across scopes
kama	W04	S085 duplicate url git-scm.com/docs/git-log across scopes
kama	W04	S086 duplicate url tldp.org/HOWTO/Program-Library-HOWTO/shared-libraries.html across scopes
kama	W04	S087 duplicate url docs.python.org/3.14/builtins/functions.html across scopes
kama	W04	S088 duplicate url docs.python.org/3.14/library/os.html across scopes
kama	W04	S093 duplicate url git-scm.com/docs/git-log across scopes
kama	W04	S097 duplicate url docs.python.org/3.14/library/subprocess.html across scopes
kama	W04	S100 duplicate url git-scm.com/docs/git-config across scopes
kama	W04	S103 duplicate url git-scm.com/docs/partial-clone across scopes
kama	W04	S105 duplicate url docs.python.org/3.14/builtins/stdtypes.html across scopes
kama	W04	S108 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server.cpp across scopes
kama	W04	S109 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
kama	W04	S110 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/common/arg.cpp across scopes
kama	W04	S112 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/README.md across scopes
kama	W04	S114 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
kama	W04	S115 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
kama	W04	S116 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
kama	W04	S117 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
kama	W04	S118 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
kama	W04	S119 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
kama	W04	S120 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
kama	W04	S121 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
kama	W04	S122 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
kama	W04	S123 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
kama	W04	S124 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
kama	W04	S125 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
kama	W04	S127 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp across scopes
kama	W04	S129 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/ggml/src/gguf.cpp across scopes
kama	W04	S130 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/src/llama-context.cpp across scopes
kama	W04	S131 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/common/fit.cpp across scopes
kama	W04	S132 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/src/llama-context.cpp across scopes
kama	W04	S133 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp across scopes
kama	W04	S134 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/README.md across scopes
kama	W04	S135 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/src/llama-kv-cache.cpp across scopes
kama	W04	S137 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp across scopes
kama	W04	S141 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
kama	W04	S142 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
kama	W04	S143 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
kama	W04	S144 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
kama	W04	S145 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
kama	W04	S146 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
kama	W04	S147 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
kama	W04	S148 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
kama	W04	S149 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
kama	W04	S150 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
kama	W04	S151 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
kama	W04	S152 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
kama	W04	S153 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
kama	W04	S154 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
kama	W04	S155 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
kama	W04	S156 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
kama	W04	S157 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
kama	W04	S158 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
kama	W04	S159 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
kama	W04	S160 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
kama	W04	S161 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
kama	W04	S162 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
kama	W04	S163 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
kama	W04	S164 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
kama	W04	S165 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
kama	W04	S166 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
kama	W04	S167 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
kama	W04	S168 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
kama	W04	S169 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
kama	W04	S170 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
kama	W04	S171 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
kama	W04	S172 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
kama	W04	S173 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
kama	W04	S181 duplicate url raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp across scopes
kama	W04	S182 duplicate url raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp across scopes
kama	W04	S183 duplicate url raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp across scopes
kama	W04	S184 duplicate url raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp across scopes
kama	W04	S185 duplicate url raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp across scopes
kama	W04	S186 duplicate url raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp across scopes
kama	W04	S187 duplicate url raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp across scopes
kama	W04	S188 duplicate url raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp across scopes
kama	W04	S189 duplicate url raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp across scopes
kama	W04	S191 duplicate url raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
kama	ok	/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md
exit=0
```

Tip mirror (`--root /fast/scratch/kama-r41/mirror`), start → end: `kama	ok	/fast/scratch/kama-r41/mirror/kama-shokunin/corpus/SOURCES.md` / `exit=0` → `kama	ok	/fast/scratch/kama-r41/mirror/kama-shokunin/corpus/SOURCES.md` / `exit=0` (`.ufo/waves/round-41/census-{start,end}-mirror.out`).

## Trend verdicts

- **expansion: improved.**
  - One admitted entry on ground the coverage map did not hold: `corpus/knowledge/engine-pin-watch.md`. It covers per-pin newer-release status for vLLM and llama.cpp and the release-counting rules, citing mined S475–S477.
  - One capability entered the table: `pin-watch`.
  - Seat R41B22 found the SGLang leg and the trigger concept already partly held; the entry now credits them.
  - Pending the outside spot-check.
- **quality: improved.**
  - The stale head table was superseded by a re-derived one, with the history kept.
  - The round-38 wrong-digest line now points to its correction (D3), and the round-40 N2/N3 citations are corrected append-only (D4).
  - No admitted entry was found false and left unmarked.
  - Stale surfaces outside C1's population (seat R41A10: SCORECARD banner, §Planned, §Saturation, head capability counts) are recorded in the lesson and routed to round 42 as the planned calibration claim.
- **discernment: improved.** This rests on two criteria:
  - The round-40 closure's D1 disagreement-class finding became KQ48, citing `corpus/lessons/round-40.md`.
  - The D2 caveat became a named per-theme reject with flips. KQ49 cites this round's mined mistake.
  - The verdict is subject to this round's outside spot-check: admit S475, reject the staged package.

## SHONEN

- [~] SKILL.md contains real decision tables, error patterns, checklists, cited sources. Pointer: `SKILL.md` (sha256 `151023b9…`, 1375 lines, re-derived by C1). No named non-author verifier.
- [~] At least one end-to-end domain task executed and logged in LOG.md. Pointers: `LOG.md` §round 16 and `.ufo/waves/round-16/live/receipt.json`; this round's `pin-watch` live run, `.ufo/waves/round-41/c2/after.out`. No named non-author verifier.
- [~] Instructions executable by an agent without oral context. Pointers: `SKILL.md` §Checklist; `tools/pin-watch.py` docstring and `selftest`. No independent execution review.
- [~] No cross-domain bleed (PROVINCE.md still accurate). Pointers: `PROVINCE.md` paragraph "Out of province → report, never absorb"; the entry's scope note leaves the generic tag-pinning method to chousa. Seat R41A10 notes that `pin-watch` is not yet named in PROVINCE.md "Owns (surfaces)"; this is routed to round 42.

Open L0 questions: `kama | round-41 | …` (parked-worktree disposition; refreshes the round-36 L0, fleet commit `786b085e`). Earlier kama L0s, round-35 (MISSION.md axes pair) and round-39 (validator band and planner), still have no recorded answer and were routed around.
