# kama round 42 report

author: kama L1 (agent `KamaR42`)
date: 2026-10-25
attempt: 1 of 1 (watchdog: `2026-10-25T17:49:56-03:00 launch kama round=42 pgid=2295067 driver=hyaku-inline attempt=1`; no `lane-dead-no-report kama round=42` line, so no earlier attempt and nothing inherited from one)
base: `0b606b03bf0b2a87b791aa537f6c72c941624cf0` (round-41 verifier spot-check, the lane remote tip at launch)
lane tip: `3e6fdbe9e0ca1ca5b633d0b312d5561301e924c4` (`git ls-remote origin refs/heads/master` prints this hash)
measured commit: `2c0181074050d1995baa3d752572882db62d570e` (integration commit; the final commit adds receipts, the end census, separability controls and the SCORECARD measured section)
Stale-lane: progressing. The current mission is kama round 42 (respawn-per-round driver), and no other lane mission is open. The parked worktree `/home/vgpnk/Projects/shokunin/kama-shokunin` is still detached on the mutation-sandbox lineage (round-40 D5, L0 `kama | round-41`), so every measurement and commit used a fresh clone of the lane remote, `/fast/scratch/kama-r42/clone`; the parked path served only as the seats' report directory and the `.ready` handoff. The lane helper `jj-lane.sh` was not used: it refuses a non-empty working copy on a non-tip base, which is the parked worktree's state.

## Work performed

Declared claims: **C1 calibration 7→7.** The SCORECARD head (banner, Planned, Retired, Saturation, Capabilities) plus `README.md` and `PROVINCE.md` match observed repository state; calibration is the lowest assigned non-retired axis (operability 8) and the stagnation nudge is inactive. **C2 operability 8→8, capability acquisition `digest-ledger`.** `tools/digest-ledger.py` classifies every full SHA-256 the lane's documents cite; it mines `considerthese/2026-10-25.md` proposal 1 and also repairs the routed round-41 counter-temp-leak defect. **C3 coverage 9→9, assimilation from `merge/kama/`.** `corpus/knowledge/context-capacity-engine-sides.md`, sourced on S478 and S479 (opened 2026-10-25); C3 is the round's sourced claim. The three claims write disjoint file sets apart from shared edits to `SCORECARD.md`, `README.md` and `SOURCES.md`; the separability controls show each verifies alone (`.ufo/waves/round-42/controls/sep-c{1,2,3}-only.*.out`).

- **Protocol load:** `skill://shokunin` (the thin host binding; it is installed at `~/.agents/skills/shokunin`), the canonical `skills/shokunin/SKILL.md` of the kimi-shokunin checkout, fleet `MISSION.md`, `AXES.md`, `CORPUS.md`, `LEARNING.md`, `skill://swarm`, `skill://godspeed`, then the lane `SCORECARD.md` (head and §Planned round 42), `SHONEN.md`, `PROVINCE.md`, `corpus/README.md` §Frontier, `corpus/lessons/round-41.md`, `round-41-verifier-spotcheck.md` and `considerthese/2026-10-25.md`.
- **Freeze before data:** commit `0bfd47abdda1f5ac21a0834654122644fc23e861` holds `.ufo/waves/round-42/preregistration.json`, the three counters `tools/round42-selfdesc-reconcile.py`, `tools/round42-digest-audit.py` and `tools/round42-capacity-audit.py`, and controls `.ufo/waves/round-42/controls/`: base and freeze (all three claims fail), seven shortcut controls (`junk-c1-textonly`, `junk-c1-sidefilesonly`, `junk-c1-falserel`, `junk-c2-stub`, `junk-c2-allunverifiable`, `junk-c3-rowsonly`, `junk-c3-stagedverbatim`; every one reads `met=False`), builder `build_controls.py`, and the census start receipts. The counters were not changed after the freeze.
- **C1 work, commit `dd9f5dc6c0e63d038bdd070094d7f38290eeee1b` and fixes:** the SCORECARD head was rewritten from the tree; the round-5 banner and the head Planned, Retired, Capabilities and Saturation text are kept verbatim under `## Historical head sections (superseded in round 42)` (seat R42A08 verified the moved blocks byte for byte); README names every top-level entry; PROVINCE names every tool and registry surface the capability list cites (this closes round-41 closure item 2, `pin-watch` missing from Owns); each head-table axis row carries one axis-specific run fact (round-41 closure item 1, narrowed not closed: the needles are substring tests, see the limits below).
- **C2 work, commit `dd9f5dc6`:** `tools/digest-ledger.py` with selftest, `registry/digest-ledger.tsv` (10 rows explaining the 10 unexplained base digests: 4 external artifacts re-hashed on this host, the round-38 S472 wrong digest linked to its correct blob, 5 unverifiable with reasons), a cleanup patch for both round-41 counters, and the `digest-ledger` row in the SCORECARD round-42 canonical capability list. After the wave the ledger moved to 5 external, 3 unverifiable, 1 wrong, and 1 digest became a committed blob (`.ufo/waves/round-42/c2/ledger-evidence/`).
- **C3 work, commit `dd9f5dc6`:** the entry, rows S478 and S479 (11-column fleet schema, renumbered by document from staged S378 and S394), README coverage and frontier blocks, the lesson Gate, assimilation scratch (`.ufo/waves/round-42/assimilation/`), and the two source copies fetched 2026-10-25T21:06:04Z (`.ufo/waves/round-42/c3/`).
- **Wave:** one validated v2 wave, `kama-r42-w1`, 64 seats in one inline handoff. Validator: `ufo-swarm-wave.mjs` with `ufo-wave-policy-v2.json`, counts `spawn 64 total 64`. Dispatch `.ufo/waves/round-42/w1/dispatch.json`; results `.ufo/waves/round-42/w1/kama-r42-w1-results.json` (64 seats, every `output` null because the orchestrator kernel restarted mid-wave; all 64 report files exist in `.ufo/waves/round-42/w1/out/`). The handoff waited about 40 minutes at the host capacity cap. Findings and what was done with them: `corpus/lessons/round-42.md` §Wave-1 findings.
- **Integration, commit `2c0181074050d1995baa3d752572882db62d570e`:** the vLLM half of the entry was rewritten after seats R42C05 and R42C13 showed the "pool in units of the declared length" sentence false for hybrid and host-bound configurations; the Gate gained the quote that grounds each row's headline claim and corrected word counts (R42C17); both refusal rows were rewritten on scope grounds (R42C12); `tools/digest-ledger.py` was hardened without changing its frozen summary line (streaming git scan, promisor refusal, confined `path`, duplicate rows, CRLF, symlink and gitlink filtering, upper-case neighbours); both round-41 counters now clean up on SIGTERM too (R42D10, R42B14); the head mirror sentence that shadowed the canonical list in both counters was reworded (seats R42A03, R42A14, R42C16, R42D03); PROVINCE and `corpus/README.md` wording corrected (R42A10, R42A11); KQ50–KQ53 and six Mistakes rows added.
- **Tooling:** the L1 installed nothing. No seat installed or upgraded a tool (seat R42B18 used the CPython 3.11.17, 3.12.15 and 3.13.16 builds that `uv python install` placed on the host in round 41). No pacman was used. The lane-owned cache file `~/.cache/kama-shokunin/models/stories260K.gguf` (1185376 bytes, sha256 `270cba1b…d256d`) was fetched from the S039 resolve URL so ledger row 5 can re-hash it; it is a public CI fixture, not an install.

## Landed changes

Each change maps to a `LOG.md` entry (§Round 42) and to the commit that carries it. Commits were made with plain `git` inside the fresh clone under the lane identity `kama-shokunin <kama@shokunin.local>` and pushed to the lane remote; the helper `jj-lane.sh` cannot run on the parked worktree (above).

| Change | LOG entry | Lane commit |
|---|---|---|
| Freeze: preregistration, three counters, base/freeze/shortcut controls, census start | §Round 42, freeze bullet | `0bfd47abdda1f5ac21a0834654122644fc23e861` |
| Claim work: SCORECARD head, README, PROVINCE (C1); digest-ledger tool, ledger, cleanup patch, capability row (C2); entry, S478–S479, Gate, scratch (C3) | §Round 42, C1/C2/C3 bullets | `dd9f5dc6c0e63d038bdd070094d7f38290eeee1b` |
| Claim fixes: adjacency count, README names the entry by repo path; head count facts decoupled from C2/C3 files; candidate receipts | §Round 42 | `2793eb5173e35d24538a2832d04883a126634947`, `c8c92db4bdf1c64357b995e0fe8d2a4f481fe995`, `3d9bd8d72366e281fab291874524130428ee423d` |
| Mistakes rows, KQ50–KQ53, wave-1 spec and dispatch | §Round 42 | `595b65f51ac7fbbba4fbef9d54e5781bbe84507b` |
| Integration: entry and Gate corrections, ledger evidence, tool hardening, SIGTERM cleanup, wave findings, 62 seat reports (interim `8bc8e37582481a14a59a8c6e1b762f047a40c260`) | §Round 42, wave and integration bullets | `2c0181074050d1995baa3d752572882db62d570e` |
| Measured receipts, end census, regenerated separability controls, SCORECARD §Round-42 measured results, wave results, last two seat reports | §Round 42, last bullet | `3e6fdbe9e0ca1ca5b633d0b312d5561301e924c4` |

Fleet repo: this report, and an L0 refresh, are committed through `fleet-commit.sh --as kama`.

Round shape: **one v2 wave of 64 seats** (`kama-r42-w1`), no residual call, round total 64.

| Role | Seats |
|---|---|
| executor | 20 |
| reviewer | 12 |
| critic | 8 |
| mutation-tester | 6 |
| scout | 5 |
| connector | 5 |
| scribe | 4 |
| simplifier | 2 |
| sentinel | 1 |
| revenger | 1 |

- `@m_flash` roles (executor, scribe, critic, simplifier, revenger, sentinel): 36 of 64 (56%). Attack seats (reviewer, critic, mutation-tester): 26 of 64 (41%).
- §3 L2 floor mapping: the planner seat is held by the L1 (the validator rejects `planner`); the bounded planning data walk rode the freeze controls and seats R42B07–R42B10 (digest re-hash walk). The wave carried 5 connector, 20 executor, 4 scribe, 5 scout, 12 reviewer and 8 critic seats.
- Dead seats: **0**. All 64 seats settled and wrote a report file. Answering models were not recorded (the results file holds no outputs), and no claim depends on a seat's model.
- Misroot sweep: `git -C /home/vgpnk/Projects/shokunin status --porcelain` shows one untracked path, `.ufo/waves/round-30/`, which is not this lane's (no kama seat wrote there). No kama seat note landed at the fleet root.

Inherited state: the parked worktree's 107 porcelain lines (round-35/36 carry, the mutation-sandbox jj lineage, and this round's untracked seat reports under `.ufo/waves/round-42/`) were neither authored nor resolved by this round; they are named, not touched. That is operator-owned (L0). Nothing inherited came from an earlier attempt of round 42. Round-41's outside closure `corpus/lessons/round-41-verifier-spotcheck.md` routed four defects: 1 relevance (partly: needles added, shown weak by R42A05), 2 `pin-watch` in PROVINCE Owns (fixed), 3 parked worktree (open, operator), 4 this report must not call `skill://shokunin` uninstalled (done). No `corpus/lessons/operator-*.md` teaching exists.

## Before → after measurements

- **C1, calibration 7→7.**
  - Command: `python3 tools/round42-selfdesc-reconcile.py --repo <fresh clone> --tip <full commit> --out <receipt>`.
  - Base `0b606b03`: `r41=0 banner=4 planned=3 retired=4 saturation=3 caps=4 receipts=0 readme=11 province=5 rel=6 mismatches=40 met=False` (exit 1), receipt `.ufo/waves/round-42/controls/base.c1.out`.
  - Measured commit `2c0181074050d1995baa3d752572882db62d570e`: `r41=0 banner=0 planned=0 retired=0 saturation=0 caps=0 receipts=0 readme=0 province=0 rel=0 mismatches=0 maxN=42 met=True` (exit 0), receipt `.ufo/waves/round-42/c1/after.out`; the same line at the final tip `3e6fdbe9`.
  - Kill rule met: False→True. Predicate, counter and needles are unchanged since the freeze.
  - Limits, from the wave and not repaired (the counter is frozen): the relevance needles are substring tests, a control with six `echo <needle>` run facts scores `rel=0` (R42A05); a 15-line edit that shrinks the capability list and replaces the evidence cells meets the counter while making the self-description less true (R42A13); the counter computes a weaker predicate than the frozen text in nine clauses (R42A06); the `receipts` leg never fires on any committed tree (R42A04). So `met=True` is necessary, not sufficient; the closure judges relevance.
- **C2, operability 8→8, capability `digest-ledger`.**
  - Command: `python3 tools/round42-digest-audit.py --repo <fresh clone> --tip <full commit> [--seed N] --out <receipt>`.
  - Base: `tool=0 contract=0 live=0 hygiene=0 capability=0 met=False` (exit 1), receipt `.ufo/waves/round-42/controls/base.c2.out`; base digest census `python3 tools/digest-ledger.py scan --repo <clone> --rev 0b606b03…` → `tokens=94 blob=84 … wrong_unflagged=1 unknown=9` (exit 1).
  - Measured commit `2c018107`: `tool=1 contract=1 live=1 hygiene=1 capability=1 met=True` (exit 0) with seed 42 and seed 7; live reference `tokens=97 blob=88 external_ok=5 external_absent=0 unverifiable=3 wrong_flagged=1 ledger_bad=0 wrong_unflagged=0 unknown=0`. Receipts `.ufo/waves/round-42/c2/after.out`, `after-seed7.out`; a third run at the final tip with seed 1337 reads the same. Selftest `selftest pass=10 fail=0` (`c2/selftest.out`).
  - Capability census: base `listed 7 observed 7 missing 0 unsubstantiated 0 met True` → `listed 8 observed 8 missing 0 unsubstantiated 0 met True` (`c2/capability-audit-after.out`).
  - Limits, not repaired (counter frozen): a lazy ledger, a tool that imports the counter's reference and stubbed round-41 counters each reach `met=True` (R42B06); the `contract` leg mirrors the tool (R42B05 M3); the tool sees only exact 64-hex tokens, so a 65-character "digest" at `corpus/lessons/round-38.md:51` is invisible to it (corrected append-only in the round-42 lesson); `external_ok` is host-dependent by design.
- **C3, coverage 9→9, assimilation.**
  - Command: `python3 tools/round42-capacity-audit.py --repo <fresh clone> --tip <full commit> --base 0b606b03bf0b2a87b791aa537f6c72c941624cf0 --out <receipt>`.
  - Base: `entry=0 rows=0 coverage=0 gate=0 census=1 met=False` (exit 1), receipt `.ufo/waves/round-42/controls/base.c3.out`.
  - Measured commit `2c018107`: `entry=1 rows=1 coverage=1 gate=1 census=1 met=True` (exit 0), receipt `.ufo/waves/round-42/c3/after.out`; the same line at the final tip.
  - Limits, not repaired: the coverage leg is not a sourcing test, since fabricated copies reach `met=True` (R42C06); the counter fails KQ48 by positional cell indexing (R42C07); four counter mutants survive (R42C14). The entry's prose was attacked and corrected after data (R42C05, R42C13): the counter does not read prose.
- **Separability.** Each claim's file set alone, scored by all three counters at the measured commit (`.ufo/waves/round-42/controls/sep-c{1,2,3}-only.*.out`): sep-c1-only C1 `met=True`, sep-c2-only C2 `met=True`, sep-c3-only C3 `met=True`, the other counters `met=False`. `controls/probe-canon-rename.c1.out`: a renamed row of the §Round 42 canonical list now fails C1's `caps` fact (`caps=1 met=False`).

## Sources & frontier

Registry rows went from **218 to 220** (`/home/vgpnk/Projects/shokunin/scripts/sources-census.sh census --file corpus/SOURCES.md`, exit 0 both times; `.ufo/waves/round-42/census-{start,end}-counts.out`).

| Measure | Start | End |
|---|---|---|
| Tier A | 208 | 210 |
| Tier B | 7 | 7 |
| Tier C | 3 | 3 |
| Status mined | 199 | 201 |
| Status queued | 8 | 8 |
| Status rejected | 11 | 11 |
| Missing | 0 | 0 |

Rows added, both tier A, `mined`, opened 2026-10-25 (access time 2026-10-25T21:06:04Z; each source re-fetched by two seats, R42C01/R42C17 and R42C02/R42C17, with the same bytes):

| Row | Kind | Source | Located quote (location) |
|---|---|---|---|
| S478 | code | https://raw.githubusercontent.com/vllm-project/vllm/v0.32.0/vllm/v1/core/kv_cache_utils.py (sha256 `af4164bca819f1cdc416077522a7019936fd38a523a482283eb91b08dae0e57a`, 111612 bytes) | "return int(max_concurrency * max_model_len), max_concurrency" (line 2308, 5 words); "num_blocks = available_memory // bytes_per_block" (line 1627) |
| S479 | code | https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-models.cpp (sha256 `9c5a6f2cc7997a3a409482c53119a2462e8c409ddf001cc568a9a8740e708b4a`, 117111 bytes) | "if (meta.n_ctx_train > 0) {" (line 2378, 5 words), then `model_info["context_length"] = meta.n_ctx_train;` (line 2379) |

- Rows touched old→new: none (no `status`, `recheck` or `used-by` changed).
- Frontier rows advanced: S478 and S479, cited by `corpus/knowledge/context-capacity-engine-sides.md`; K05 engine-side ground held as source readings (README coverage and frontier blocks); K05 itself stays runtime-blocked.
- Lesson Gate: `corpus/lessons/round-42.md` §Gate (URLs, access dates, quotes, the assimilation table).
- Mirror validate (`sources-census.sh validate --root <mirror of the tip clone> kama`): exit 0 at start and at end, 93 W04 and 0 E both times (`.ufo/waves/round-42/census-{start,end}-mirror.out`). The fleet-root validate also exits 0 at start and end with 93 W04, but it reads the parked worktree's registry, not the tip (round-40 N4, still open with the operator).

**Assimilation: one theme, `context-capacity`, from `merge/kama/`.** Two staged amendments admitted and merged into one entry (r5, S378, vLLM; r7, S394, llama.cpp), two refused with named flips (r8: S401 llama-cpp-python settings and S405 docs page; r11: S424 own-work receipt). Every cited source was re-opened this round; the entry corrects three simplifications in the staged prose. Source repo read-only: nothing was written into `/home/vgpnk/Projects/shokuknow` and no campaign tool was run.

- Id collision check (scratch, committed as `.ufo/waves/round-42/assimilation/{reg-ids,staged-ids,collisions}`): lane ids 218, staged ids 142, collisions 9, none adopted. Collisions: `S330 S333 S334 S335 S346 S347 S352 S353 S363`. Renumber map by document: staged S378 → S478, staged S394 → S479. Guard proof: a scratch registry with an indented `  | S378 |` row gives collision S378 with the 0–3-space pattern and nothing with the column-zero-only pattern (`assimilation/guard/`).
- Lane registry ids (218):

```text
S001 S002 S003 S004 S005 S006 S007 S008 S009 S010 S011 S012 S013 S014 S015 S016 S017 S018
S019 S020 S021 S022 S023 S024 S025 S026 S027 S028 S029 S030 S031 S032 S033 S034 S035 S036
S037 S038 S039 S040 S041 S042 S043 S044 S045 S046 S047 S048 S049 S050 S051 S052 S053 S054
S055 S056 S057 S058 S059 S060 S061 S062 S063 S064 S065 S066 S067 S068 S069 S070 S071 S072
S073 S074 S075 S076 S077 S078 S079 S080 S081 S082 S083 S084 S085 S086 S087 S088 S089 S090
S091 S092 S093 S094 S095 S096 S097 S098 S099 S100 S101 S102 S103 S104 S105 S106 S107 S108
S109 S110 S111 S112 S113 S114 S115 S116 S117 S118 S119 S120 S121 S122 S123 S124 S125 S126
S127 S128 S129 S130 S131 S132 S133 S134 S135 S136 S137 S138 S139 S140 S141 S142 S143 S144
S145 S146 S147 S148 S149 S150 S151 S152 S153 S154 S155 S156 S157 S158 S159 S160 S161 S162
S163 S164 S165 S166 S167 S168 S169 S170 S171 S172 S173 S174 S175 S176 S177 S178 S179 S180
S181 S182 S183 S184 S185 S186 S187 S188 S189 S190 S191 S192 S193 S194 S196 S205 S206 S209
S223 S324 S327 S328 S329 S330 S333 S334 S335 S346 S347 S352 S353 S363 S472 S473 S474 S475
S476 S477
```

- Staged ids (142):

```text
S330 S331 S332 S333 S334 S335 S336 S337 S338 S339 S340 S341 S342 S343 S344 S345 S346 S347
S348 S349 S350 S351 S352 S353 S354 S355 S356 S357 S358 S359 S360 S361 S362 S363 S364 S365
S366 S367 S368 S369 S370 S371 S372 S373 S374 S375 S376 S377 S378 S379 S380 S381 S382 S383
S384 S385 S386 S387 S388 S389 S390 S391 S392 S393 S394 S395 S396 S397 S398 S399 S400 S401
S402 S403 S404 S405 S406 S407 S408 S409 S410 S411 S412 S413 S414 S415 S416 S417 S418 S419
S420 S421 S422 S423 S424 S425 S426 S427 S428 S429 S430 S431 S432 S433 S434 S435 S436 S437
S438 S439 S440 S441 S442 S443 S444 S445 S446 S447 S448 S449 S450 S451 S452 S453 S454 S455
S456 S457 S458 S459 S460 S461 S462 S463 S464 S465 S466 S467 S468 S469 S470 S471
```

- Scratch transformation and validation before the append: the two rows were normalized to the 11-column schema, no `|` in any cell, recheck `on-release`, status `mined`, `used-by` the entry and the lesson; the scratch mirror (base tree plus the append block plus the entry) validated with `sources-census.sh validate --file <mirror>/corpus/SOURCES.md` exit 0 before the append landed (`assimilation/validate-census.out`).
- Quarantine slice (register read-only, 7 data rows: S200, S202, S206, S210, S211, S224, S230, all `payload-absent`): each already carries a hand-check verdict in the round-35 and round-36 lessons and in `.ufo/waves/round-41/w1/out/R41F01.md`; seat R42C11 re-derived the slice byte-identically and mapped every row to its verdict. No quarantined row is appended.
- Per-entry gates: PROVINCE scope check (K05 held ground, source reading only; seat R42C06), QUALITY bar (53 KQ rows applied by seat R42C07: 20 pass, 32 not applicable, 1 fail against the counter itself), coverage ground the lane did not hold (`grep -rn kv_cache_size_tokens corpus SKILL.md` empty at base). Lesson Gate records 2 admits and 2 rejects for the closure's spot-check.
- **considerthese:** `considerthese/2026-10-25.md` proposal 1 mined into C2 (digests only; the S-id prose cross-check half stays open as the round-43 plan). Proposals 3 and 4 remain unimplemented; proposal 2 landed in round 41.
- Mined mistakes: eight `## Mistakes` rows in `corpus/lessons/round-42.md` (vacuous ×2, provider ×2, stale-premise ×1, scope ×3), plus an append-only correction of `corpus/lessons/round-38.md:51`. Sourced claim: C3 (S478, S479).

### Census transcripts

Start: `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama`, complete output with the exit code appended (`.ufo/waves/round-42/census-start-fleetroot.out`):

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

End: the same command (`.ufo/waves/round-42/census-end-fleetroot.out`):

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

Tip mirror (`--root /fast/scratch/kama-r42/mirror`, then a mirror of the measured commit), start → end: `kama	ok	…/corpus/SOURCES.md` / `exit=0` → `kama	ok	…/corpus/SOURCES.md` / `exit=0` (`.ufo/waves/round-42/census-{start,end}-mirror.out`).

## Trend verdicts

- **expansion: improved.**
  - One admitted entry on ground the coverage map did not hold: `corpus/knowledge/context-capacity-engine-sides.md` (vLLM's served-capacity derivation and llama.cpp's `context_length` key), citing mined S478 and S479.
  - One capability entered the table: `digest-ledger`.
  - The entry's first draft carried a false sentence (vLLM hybrid and host-bound configurations); it was found by seats and corrected before landing. Pending the outside spot-check.
- **quality: improved.**
  - The stale SCORECARD head sections were re-derived and the old text kept verbatim; the S472 wrong digest and nine other unexplained digests are now classified; both round-41 counters stopped leaking their export, on SIGTERM as well; wrong ledger and PROVINCE statements were corrected after review (R42B13, R42A10).
  - Counter and claim limits are recorded rather than prettified (C1 relevance, C2 cheap mutants, C3 coverage leg).
  - No admitted entry was found false and left unmarked.
- **discernment: improved.** The round-41 closure's four routed defects became fixes or named routes. KQ50–KQ53 cite this round's mined mistakes, each with a failing control. The wave's attacks on the lane's own counters are recorded in the lesson, and relevance and sufficiency are explicitly left to the outside closure. The verdict is subject to this round's outside spot-check: admit S478 and S479, reject the staged r8 and r11 amendments.

## SHONEN

- [~] SKILL.md contains real decision tables, error patterns, checklists, cited sources. Pointer: `SKILL.md` (1375 lines, unchanged this round; seat R42A02 found its `GATE_SELFTEST` line stale, routed). No named non-author verifier.
- [~] At least one end-to-end domain task executed and logged in LOG.md. Pointers: `LOG.md` §round 16 and `.ufo/waves/round-16/live/receipt.json`; this round's `digest-ledger` live scan, `.ufo/waves/round-42/c2/after.out`. No named non-author verifier.
- [~] Instructions executable by an agent without oral context. Pointers: `SKILL.md` §Checklist; `tools/digest-ledger.py` docstring and `selftest`. Interpreter matrix run by seat R42B18 (CPython 3.11, 3.12, 3.13, 3.14), which is a lane seat and not an independent review.
- [~] No cross-domain bleed (PROVINCE.md still accurate). Pointers: `PROVINCE.md` paragraph "Out of province → report, never absorb" and the round-42 note (seat R42A10 reviewed it and the wording was corrected); the entry stays a source reading and absorbs nothing from kengaku or chousa.

Open L0 questions: `kama | round-41 | …` (parked-worktree disposition) is refreshed by a `kama | round-42` line in this round's fleet commit. Earlier kama L0s, round-35 (MISSION.md axes pair) and round-39 (validator band and planner), still have no recorded answer and were routed around.
