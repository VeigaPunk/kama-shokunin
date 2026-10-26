author: hyaku closure (non-author integrator, @m_opus)

# kama round 47: non-author closure spot-check

Date: 2026-10-26. Base `172b8ad040d51ce8c011238c1408d4e0b6aa9595` (round-46 spot-check), freeze `bbcc6dc2fbd7fc04b1d91a97ffa239a6601cd5ba`, measured commit `383f1fc780573d46b6ea8bc1044b21f604e6ba3e`, post-measure fix `3442d707fdf926ec5ea3f34363cf2f0899cc79b5`, lane tip `6b7e6cf8d30b5794ed72fe97eb0e666f9b0572a9`. Both claims were re-measured by me with the frozen counters on a fresh local clone of the lane at the tip (and at the base for the before-state). I inspected committed bytes only; I did not run any lane gate other than the claim counters (the step-2 measurement) and the read-only regression checks below.

Driver digest (from `.ufo/watchdog.log`, mutable):
`2026-10-26T18:00:16-03:00 launch kama round=47 pgid=2438931 driver=hyaku-inline attempt=1`
`2026-10-26T18:51:10-03:00 complete kama round=47; hyaku-inline attempt=1`
No `lane-dead-no-report kama round=47` line.

Verdict: **admitted** (status `ok`, admitted `true`).
- Both claims verify on their frozen predicates and on my own independent re-measurement at the tip.
- No axis is harmed (SCORECARD diff: no score dropped; capabilities 10→11).
- The spot-check agrees with the Gate on the admits and rejects I sampled.
- The lane disclosed the counter weaknesses in the report and in SCORECARD §Round 47; they are routed below.

## 1. Conformance (step 1)

| Check | Observed | Result |
|---|---|---|
| Report committed by the lane identity | `git log --format='%an %H' -- .ufo/reports/round-47/kama.md` → `kama-shokunin d0012618894c7154683d97bb594b2dd5abbed013 round-47: kama report` | pass |
| `SHONEN` heading, one line per box | `## SHONEN` has 4 box lines, all `[~]`, each with a pointer; SHONEN.md has 4 boxes | pass |
| Cited lane commits exist and are ancestors of the branch | `git merge-base --is-ancestor <h> master` holds for all 8 cited hashes (base `172b8ad0`, freeze `bbcc6dc2`, build `3a09a1d9`, wave `46a924e0`, measured `383f1fc7`, fix `3442d707`, results `76a7aaff`, tip `6b7e6cf8`) | pass |
| Lane pushed and clean | `jj-lane.sh state` → `branch=master local=6b7e6cf8… remote=6b7e6cf8… ahead=0 behind=0 head=detached tracked=0 untracked=0`. `git status --porcelain` printed nothing. `ls-remote origin refs/heads/master` → `6b7e6cf8…` | pass |
| Prompt carries the template contract | `.ufo/prompts/kama-round-47.md` lines 1–140 render `templates/round-prompt.md` with `{{LANE}}`→kama, `{{ROUND}}`→47, `{{FLEET_ROOT}}`→/home/vgpnk/Projects/shokunin, `{{AXES}}`→operability + calibration; lines 141+ are the hyaku addendum (run 9 etc.). All five child-lane items are present: report path/filename (§4), commit-before-report ordering (§5 + addendum §4), `SHONEN` heading requirement (§4 + addendum §4 pre-report grep), commit-hash citation rule (§4 + addendum §4 `landed <hash>`), lane write scope (addendum §3). The quoted L2 route map matches the current `~/.omp/agent/config.yml` `agentModelOverrides` (task/main/planner @m_opus, reviewer/mutation-tester/security-reviewer @m_zfl, scout @m_sonnet, distiller/seance @m_haiku, connector/critic @m_kfc, executor/labrat/scribe/sonic/simplifier/revenger/sentinel @m_flash) | pass |
| Counters frozen before data | preregistration `frozen_at_utc` 21:12:52Z precedes the freeze commit; controls all `met=False` (base, v1+contract, v1-numstat, r46-relabel); tip sha256 of `tools/round47-append-audit-v2-check.py` = `a180ab84…` and `tools/round47-live-replay-audit.py` = `15408dce…`, equal to `claims[*].counter_sha256` | pass |
| L2 floor role split | One v2 wave `kama-r47-w1`, 65 seats (dispatch.json `spawn 65`): critic 12, reviewer 11, executor 15, scribe 10, scout 6, mutation-tester 4, connector 4, simplifier 1, sentinel 1, revenger 1. m_flash roles 40/65 (≥50%); attack roles (reviewer+critic+mutation-tester) 27/65 (≥25%). `seat-yield-w1.out`: `seats=65 status=unknown:65 reports=65 missing=0`, exit 0; no dead seats. No `planner`/`labrat` seats — the policy-v2 validator rejects them; the L1 holds the planner seat (already carried as L0 `kama \| round-39`) | pass (planner-seat note carried) |
| No uncommitted round work | Lane state clean; fleet root has one modified orchestrator-owned file `.scratch/goal-20261026-hyaku-run9.md` (untouched) | pass |

Not a marker: the round left real lane commits and evidence. Status `ok`.

## 2. Claims (step 2) — re-measured with my own runs

Both claims were re-measured by running the frozen counters on a fresh clone of the lane (`git clone /home/vgpnk/Projects/shokunin/kama-shokunin /fast/scratch/hyaku/kama-r47-closure/lane`) at `6b7e6cf8` (after) and at `172b8ad0` (before). Command: `python3 tools/round47-append-audit-v2-check.py --repo <clone> --tip <commit> --scratch <dir>` and `python3 tools/round47-live-replay-audit.py --repo <clone> --tip <commit> --scratch <dir>`.

### C1: calibration 7→7 (append-only-audit v2 vs git numstat + declared contract)

- Base `172b8ad0`: `selftest=1 contract=0 lane=0 fixture=0 stable=0 met=False` (exit 1).
- Tip `6b7e6cf8`: `selftest=1 contract=1 lane=1 fixture=1 stable=1 files=86 lane_events=5 lane_mismatch=0 fixture_mismatch=0 met=True` (exit 0).
- Exactly equals the report's measured values (`c1-after.out` at `383f1fc7`, `c1-fix.out` at `3442d707`). The fixture leg constructs a separate test tree with CRLF, `--`, `---`, duplicate and no-final-newline lines; the lane leg re-derives the contract-declared file set from history (86 files, including `corpus/lessons/*.md`).

### C2: operability 8→8 (replayable b11909 live evidence)

- Base `172b8ad0`: `receipts=0 replay=0 tamper=0 newrow=0 met=False` (exit 1).
- Tip `6b7e6cf8`: `receipts=1 replay=1 tamper=1 newrow=1 rerun_checks=11 met=True` (exit 0).
- The replay leg extracts `git archive` of the tip under scratch with HOME/XDG_CACHE_HOME/TMPDIR inside scratch, runs `tools/kama-live-replay.py` on receipt-1 (real network acquisition from github.com and huggingface.co; rerun receipt verified: schema v4, outcome pass, started_utc after counter start, server/model sha256 equal to receipt-1, inputs inside scratch, all 11 checks equal) — so the met=True is a genuine network replay, not a cache artifact. The tamper leg refuses a wrong recorded digest; the newrow leg finds the S488/S489 b11909+commit row.

### Regression checks at the tip (read-only, my runs)

- gate `tools/gate-registry-check.py` → `registered 40 unregistered 0 defective 0`, exit 0.
- capability census `tools/capability-repertoire-audit.py` → `listed 11 observed 11 missing 0 unsubstantiated 0 met True`, exit 0.
- `tools/hexrun-census.py scan --repo . --rev master` → `unknown=0 ledger_bad=0`, exit 0 (report: 22 unknown at base → 0).
- `tools/digest-ledger.py scan --repo . --rev master` → `unknown=0 ledger_bad=0`, exit 0.
- `tools/kama-live-replay.py --selftest` → `KLR_SELFTEST pass=13 fail=0`; `tests/llamacpp-live/check-receipt.py --selftest` → 14 VALID + 1 NOT-EVALUATED accepted, 103 mutations + unreadable rejected; `tools/gguf-identity.py --selftest` → passed.

Verdicts: C1 verified (re-measured), C2 verified (re-measured). Neither is exploratory; no named non-author reviewer is needed.

## 3. Per-axis verdicts

| Axis | Verdict | Basis |
|---|---|---|
| calibration | improved | C1 re-measured above; v2 audit now matches `git diff --numstat` ground truth (incl. `--`-prefixed lines), audits a machine-readable contract incl. `corpus/lessons/*.md`, and restoration is a window-max multiset (D1/D2 closed). Score held 7 |
| operability | improved | C2 re-measured above; live evidence is re-runnable from committed bytes (provenance + replay tool), D5/D3 closed; capability `live-receipt-replay` entered the table with passing demonstrations. Score held 8 |
| freshness | unchanged | score 8; no freshness claim this round; r41–r43 regression checks met at tip |
| depth | unchanged | score 7; SKILL.md changed only by registry/how-to lines |
| coverage | unchanged | score 9; PROVINCE.md changed only in its instrument cell |
| adjacency | unchanged | score 7; sibling scans N1Overlap/N3Fleet reported, not absorbed |

`git diff 172b8ad0 6b7e6cf8 -- SCORECARD.md`: no score changed; capabilities 10→11 (`live-receipt-replay`, first-working round 47); the only removed lines are head re-anchors.

## 4. Discernment spot-check (step 3)

| Item | Decision | Re-opened source | Agree / disagree | Reason |
|---|---|---|---|---|
| S491 (git-diff `--numstat` definition) | admit | live `https://git-scm.com/docs/git-diff` §OPTIONS `--numstat` — page text contains verbatim "shows number of added and deleted lines in decimal notation and pathname without abbreviation" (also present in committed `out/S1Numstat/git-diff.html`) | agree | Quote located and exact; 14 words ≤ 25; supports C1's deleted=numstat rule and the binary `-` skip |
| S488 (b11909 release identity) | admit | committed freeze copy `.ufo/waves/round-47/c2/release-b11909.json`: `tag_name b11909`, `target_commitish caa8191df159f764fb0160e3d2fc6be008948aee`, asset `llama-b11909-bin-ubuntu-x64.tar.gz` 22475032 bytes sha256 `bf94332a…695b` | agree | Matches the frozen ASSET_URL/ASSET_SHA the C2 counter checks; scope restricted to identity of the Linux x64 CPU archive, not behaviour |
| S490 (model resolve URL) | admit | receipts' `provenance.model.url` = `https://huggingface.co/ggml-org/models-moved/resolve/main/tinyllamas/stories260K.gguf`; `x-linked-etag 270cba1b…` equals S039's LFS sha256 and size 1185376 matches S039 | agree | Admit scoped to artifact identity at the resolve URL the replay fetches; the moving-`main` limit is disclosed (X2Revision) and guarded by the digest |
| R1 — provenance URL verified at record time | reject | `out/K2Design.md` F1: `kama-llamacpp-live.py --server-asset-url not-a-url …` parses (exit 0) and would emit a pass receipt with recorded provenance; only a replay that downloads and digest-checks verifies | agree | The live tool records what it was told; verification is the replay. The Gate wording (locator) matches the evidence |
| R2 — host path as artifact locator | reject | `out/K2Cheat.md` V1/V2: host-cache copies byte-identical to provenance pass the frozen counter (the symlink variant is blocked by the `realpath`-inside-scratch check); round-46 D5 evidence shows the scratch path no longer exists | agree | A one-host path is the same dead-pointer class; not a durable locator |
| R3 — `teardown.term_wait_ms` as a b11909 property | reject | receipts `-{1,2,3}.json`: `term_wait_ms` 3, 3, 3; round-45 receipts 15, 9, 7; round-46 lesson records 3, 3, 3 at b11906 | agree | Three samples across three releases vary 5×; an observation, not a property |

`scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama` → exit 0, with 93 `W04`, 1 `W01` (S481) and 0 `E` — equals the report's end census. SOURCES rows 228 → 232 (S488–S491 added, all mined, opened 2026-10-26). Every new row's Gate quote ≤ 25 words (S488: 1 token; S489: 1 token; S490: 1 token; S491: 14 words).

Discernment: the spot-check agrees with the Gate on all sampled admits (3) and rejects (3).

## 5. Trend verdicts

| Trend | Verdict | Evidence |
|---|---|---|
| expansion | improved | Capability `live-receipt-replay` entered SCORECARD with passing demonstrations (capability census `listed 11 observed 11 met True`; C2 counter replay/newrow legs; my re-measurement ran the replay leg). `corpus/lessons/*.md` is newly inside the audited append-only set (C1 `files=86`) |
| quality | improved | hexrun unknowns 22→0 (re-verified `unknown=0` at tip); receipt validators accept v4 (check-receipt/gguf-identity selftests); KLR member-digest fix (`pass=13`); C1 numstat equality re-measured. No admitted entry failed its re-check |
| discernment | improved | The non-author spot-check (this file) agrees with the Gate on the sampled admits and rejects, satisfying KQ61's wait condition |

## 6. Routed defects (lane fixes next round unless marked)

- **D1 (lane, C2 counter sufficiency).** `out/K2Cheat.md`: a host-cache copy (V1), a fabricated 0-byte rerun (V3) and a forged `started_utc` (V4b) all still meet the frozen counter. Next freeze: cross-hash the actual files at `server.realpath`/`model.path`, require `J.inputs.archive` non-null and hashing to `archive_sha256`, fingerprint the replay/live tools at the measured tip, bind `started_utc` to a counter-supplied nonce/instant.
- **D2 (lane, C2 replay scope).** The replay leg exercises receipt-1 only; receipts 2 and 3 are trusted on structure alone (`out/K2Design.md` F3). Loop replay over all three receipts next round.
- **D3 (lane, C2 record-time provenance).** The live tool accepts unverifiable provenance at record time (`out/K2Design.md` F1): require all four provenance flags, `^https://` schemes, member shape, and optionally bind the archive digest to the installed member.
- **D4 (lane, C2 comparison depth).** Replay agreement is check pass/fail, not captured surfaces (`out/K2Design.md` F2). Semantic compare of stable fields (props.fields, slots.element_count, health/models content), exempting run-varying fields.
- **D5 (lane, C1 counter gaps).** 13/44 counter mutants survive; `max(0)` clamp and merge-first-parent untested; contract leg accepts any line containing `append` (V1Ctr); fixture-playback/selftest-stub cheats reach `met=True` (K1Cheat).
- **D6 (lane/operator, URL drift).** The model URL names the moving `main` (S490 limit); the pinned `resolve/499bc882…` URL is planned as a v5 provenance field (round 48) — never a rewrite of filed receipts (K2Design F4/X2Revision).
- **D7 (lane, prerelease cliff).** b11909 is a GitHub prerelease; if the tag is pruned the replays permanently refuse. Consider a digest-verified `--cache-dir` hardening.
- **D8 (lane, sources guard).** `tools/sources-append-only.py` has graded no SOURCES transition since round 45 (exit 2 on row-like lines outside the parsed registry; lesson Mistakes row). Parser fix pending.
- **D9 (lane, evidence receipts precision).** The report says the r41/r42/r43/pointer checks were "re-run at the final tip `6b7e6cf8`", but the committed `*-fix.out` receipts show `tip=3442d707`. I re-verified all of them at `6b7e6cf8` myself (gate/cap/hexrun/digest clean), so the content holds; next round either re-run and commit tip-level receipts or phrase the claim as re-run at the fix commit.
- **Operator/L0.** Planner seat impossible under the policy-v2 validator (`kama | round-39`); MISSION axes pair (`kama | round-35`); parked worktree (`kama | round-41..43`). Fleet root `.scratch/goal-20261026-hyaku-run9.md` modified by the orchestrator (untouched).
- **Operator, promotion.** The four `SHONEN` boxes are `[~]` and look checkable by a non-author (box 1: gate registry `registered 40 … defective 0`; box 2: live receipts + replays re-opened above; box 3: SKILL replay how-to + KLR selftest; box 4: PROVINCE instrument-cell only). Promotion is operator-owned; nothing was marked here.
