author: hyaku closure (non-author integrator, @m_opus)

# kama round 48: non-author closure spot-check

Date: 2026-10-26. Base `33e005827742b29772b153cda036ec9f27f653be` (round-47 spot-check), freeze `12284ba39fb1b46b43d43ee82423bebe08c700dc`, build `380bcdff9c8af06997c482f6eb03db926a794a2b`, measured commit `c4b2175d2ff9466beaed039dc8330176362e7d82`, results `1541a0dd1628225b838235fe2b7b3d69ad8f50de`, lane tip `4d8334af1c45bce74fa6a3904a7f6aa3a1ec630e`. I re-measured both claims myself with the frozen counters on a fresh local clone of the lane, at the tip (after) and at the base (before). Every other gate result below is evidence-verified from committed receipts; I did not execute any other lane gate.

Driver digest (from `.ufo/watchdog.log`, which is mutable):
`2026-10-26T19:05:04-03:00 launch kama round=48 pgid=3968099 driver=hyaku-inline attempt=1`
`2026-10-26T20:00:07-03:00 complete kama round=48; hyaku-inline attempt=1`

Verdict: **admitted** (status `ok`, admitted `true`).
- Both claims verify on their frozen predicates and on my own re-measurement at the tip.
- No axis is harmed. In the SCORECARD diff no score dropped and no capability was lost (11 → 11).
- The spot-check agrees with the Gate on both admits and on the three rejects I sampled.
- Conformance defects (section 6, R2–R4) are status-neutral.

## 1. Conformance (step 1)

| Check | Observed | Result |
|---|---|---|
| Report committed by the lane identity | `git log --format='%an <%ae> \| %H %ci %s' -- .ufo/reports/round-48/kama.md` → `kama-shokunin <kama@shokunin.local> \| 15710a2a8286bf12d55d943f17028178fe8d421a 19:58:24 -0300 round-48: kama report` and `… dcc079e7e56d3312ec70e0bd5b3c7f885b1242e8 19:59:22 -0300 round-48: kama report (fill tip, wave-done, yield, dead seats, misroot and last landed row)` | pass (defect R2) |
| Report filed after its commit | The first report commit `15710a2a` (authored 19:58:24) had `__TIP__`, `__WAVEDONE__`, `__YIELD__`, `__DEAD__` and `__LASTROW__` placeholders. It was filed before the lane tip `4d8334af` existed (committed 19:58:49). `dcc079e7` then rewrote 6 lines of the filed bytes in place (`git show dcc079e7 --word-diff=plain`) instead of appending an erratum | defect R2 (status-neutral) |
| `SHONEN` heading, one line per box | `## SHONEN` has 4 lines, all `[~]`, each with a pointer; `grep -c '^- \[' SHONEN.md` → 4 | pass |
| Cited lane commits exist and are ancestors of the branch | `git cat-file -e <h>^{commit}` and `git merge-base --is-ancestor <h> master` hold for all 8 cited hashes (base `33e00582`, freeze `12284ba3`, build `380bcdff`, wave `b85783e8`, measured `c4b2175d`, results `1541a0dd`, final receipts `f5c60787`, tip `4d8334af`) | pass |
| Lane pushed and clean | `jj-lane.sh state` → `branch=master local=4d8334af… remote=4d8334af… ahead=0 behind=0 head=detached tracked=0 untracked=0`; `git status --porcelain` printed nothing; `git ls-remote origin refs/heads/master` → `4d8334af…` | pass |
| Prompt carries the template contract | `.ufo/prompts/kama-round-48.md` (committed `2359d4bc` by the lane identity, 19:05:02). Lines 1–140 equal `templates/round-prompt.md` rendered with `{{LANE}}`→kama, `{{ROUND}}`→48, `{{FLEET_ROOT}}`→/home/vgpnk/Projects/shokunin, `{{AXES}}`→`operability + calibration (local model serving and endpoint health)`, and `<kama-repo>`→`kama-shokunin`; a difflib comparison showed no other difference. Lines 141+ are hyaku addendum §6 and §7. The five child-lane items are present. The text equals `kama-round-47.md` apart from the round numbers | pass |
| Quoted L2 route map vs the live map | The prompt quotes the run-8 map (line 176, confirmed by run 9 at line 150): critic `@m_flash`. `~/.omp/agent/config.yml` (mtime 18:14 -03, before launch) has `critic: "@m_kfc"`; `config.yml.pre-glm53critic-20261026` (17:45) still had `critic: "@m_flash"`. So the quoted map does not match the live one | defect R4 (status-neutral) |
| L2 floor and role split | One v2 wave `kama-r48-w1`, 69 seats (`dispatch.json`: connector 4, critic 16, executor 12, mutation-tester 5, revenger 1, reviewer 13, scout 5, scribe 11, sentinel 1, simplifier 1). `seat-yield-w1.out`: `seats=69 … reports=69 missing=0`, exit 0. Attack share 34/69 (49%). The m_flash share is 42/69 under the quoted map but 26/69 (38%) under the live map (R4) | pass (R4 noted) |
| Counters frozen before data | `sha256sum` of `tools/round48-append-audit-v3-check.py` at the tip = `92b0f9f1…2ac7` and of `tools/round48-live-replay-v5-audit.py` = `6bc16e25…0c09`, equal to `preregistration.json` `claims[*].counter_sha256`; `git diff --stat 12284ba3 4d8334af` over both counters is empty. Controls committed `met=False` (base, `junk-c1-v2-relabel`, `junk-c1-drop-scorecard`, `junk-c2-r47-relabel`) | pass |
| No uncommitted round work | The lane is clean. The fleet root has three untracked files, `=1239`, `=3900` and `T`. The report disclosed them, and none names kama | pass (operator note) |

This is not a marker report: the round left real lane commits and evidence. Status `ok`.

## 2. Claims (step 2): my re-measurement

Fresh clone `git clone /home/vgpnk/Projects/shokunin/kama-shokunin /fast/scratch/hyaku/kama-r48-closure/lane` (HEAD `4d8334af`). I copied the frozen counters out of the clone and ran `python3 <counter> --repo lane --tip <commit> --scratch <dir>`.

### C1: calibration 7→7 (append-only-audit v3 with bound regions)

- Base `33e00582`: `selftest=0 contract=0 lane=0 fixture=0 stable=0 rows=0 files=0 lane_events=0 lane_failures=NA ungraded_lines=0 fixture_fail=11 met=False`, exit 1. Details: `contract: header is not the v3 header`; all 11 fixtures `could-not-evaluate`.
- Tip `4d8334af`: `selftest=1 contract=1 lane=1 fixture=1 stable=1 rows=10 files=91 lane_events=5 lane_failures=0 ungraded_lines=89 fixture_fail=0 met=True`, exit 0 (4.5 s).
- This equals the report's `c1-after.out` at `c4b2175d` and `c1-final.out` at `1541a0dd` field for field.
- Content check of the build finding: at the tip `grep -c '^\*\*Current authority (round N):\*\*' SCORECARD.md` is 1 for each N in 42–48. The base banner line for round 47 is held byte-exact (`grep -Fxc` → 1). Banner lines went from 2 at the base to 8 at the tip.
- SCORECARD's line-6 promise ("replaced head text is kept verbatim") now holds for the authority banner.

### C2: operability 8→8 (v5 receipts, record-time provenance, 3/3 replay, sourced on S492/S493)

- Base: `receipts=0 recordcheck=0 replay=0 compare=0 tamper=0 urlswap=0 newrow=0 replayed=0/3 met=False`, exit 1. The base live tool rejects the v5 record-time flags; the pinned-URL row is absent.
- Tip: `receipts=1 recordcheck=1 replay=1 compare=1 tamper=1 urlswap=1 newrow=1 replayed=3/3 met=True`, exit 0 (13.0 s, network re-acquisition from github.com and huggingface.co).
- This equals `c2-after.out` and `c2-final.out`.
- The disclosed limit holds: `replayed=3/3` proves re-acquired, digest-verified inputs and projection comparison. It does not prove a server executed (seats K2Cheat and K2Urlswap).

### Evidence-verified (committed receipts, not executed by me)

- Tip-level receipts at `1541a0dd` (`measured/*-final.out`, each with a `tip=` line):
  - gate `registered 42 unregistered 0 defective 0`
  - capability census `listed 11 observed 11 … met True`
  - r41 `mismatches=0 met=True`; r42 `mismatches=0 maxN=48 met=True`; r43 `mismatches=0 met=True`; pointer `met=True`
  - hexrun `unknown=0`; digest-ledger `unknown=0`
- At `c4b2175d`:
  - `AOA_SELFTEST pass=28 fail=0`
  - `KLR_SELFTEST pass=22 fail=0`
  - check-receipt `16 VALID … 107 mutations + unreadable case rejected`
  - live selftest `ok`
  - `sources-append-only.py --from 33e00582` exit 0 with `added S492 (allowed)`
  - round-47 C2 counter `met=True`
- `git diff --name-only 1541a0dd 4d8334af` touches only `.ufo/waves/round-48/` (wave results, seat reports), so the `1541a0dd` receipts describe the tip's graded surfaces.
- Disclosed by the lane: the round-47 C1 counter now fails by construction because the v2 contract format was superseded (seat X2V4Compat).

Verdicts: C1 verified (re-measured); C2 verified (re-measured). Neither claim is exploratory.

## 3. Per-axis verdicts

| Axis | Verdict | Basis |
|---|---|---|
| calibration | improved | C1 re-measured. The append-only audit now grades the rule as declared: regions are bound, `regressed` reaches the exit code, and 11 constructed fixtures pass. It found five unkept SCORECARD banners (r42–r46), which the round restored byte-exact. Score held at 7 |
| operability | improved | C2 re-measured. Live evidence is pinned to a 40-hex model revision, provenance is verified at record time, all three receipts replay with a stable-projection compare, and swapped URLs and wrong digests are refused. Score held at 8 |
| freshness | unchanged | Score 8; row not in the SCORECARD diff; r41–r43 regressions met at `1541a0dd` |
| depth | unchanged | Score 7; SKILL.md +21/−0 (round-48 registry and the v5 how-to); evidence re-anchor only |
| coverage | unchanged | Score 9; PROVINCE.md +1/−1 (instrument cell) |
| adjacency | unchanged | Score 7; sibling scan N1Overlap reported, not absorbed |

`git diff 33e00582 4d8334af -- SCORECARD.md`: no score changed. The only removed lines are the round-47 head banner, which is kept verbatim below the head, plus head re-anchors and capability rows that were reworded, not removed (11 → 11). Numstat for the append-only files: LOG.md 11/0, SKILL.md 21/0, corpus/QUALITY.md 13/0, corpus/README.md 169/0.

## 4. Discernment spot-check (step 3)

| Item | Decision | Re-opened source | Agree / disagree | Reason |
|---|---|---|---|---|
| S492 (pinned HF resolve URL) | admit | `curl -sSI https://huggingface.co/ggml-org/models-moved/resolve/499bc8821c6b12b4e53c5bffcb21ec206f212d81/tinyllamas/stories260K.gguf` → `HTTP/2 302`, `x-repo-commit: 499bc8821c6b12b4e53c5bffcb21ec206f212d81`, `x-linked-etag: "270cba1b…bd256d"`, `x-linked-size: 1185376`. Revision API `.sha` = `499bc882…1d81`. `curl -sSL` download: sha256 `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d`, 1185376 bytes | agree | The quote is located in the response headers and exact (header tokens, ≤25 words). The served bytes equal S039's digest. Scope is limited to artifact identity |
| S493 (huggingface_hub download guide) | admit | `curl -sSL https://huggingface.co/docs/huggingface_hub/en/guides/download`: the page holds "From specific version" and the exact sentence "When using the commit hash, it must be the full-length hash instead of a 7-character commit hash." (17 words); the committed copy `c2/hf-hub-download-doc.txt` holds it too | agree | Verbatim, ≤25 words, under the cited section. It grounds the 40-hex pin rule only |
| `x-linked-etag` as proof of revision | reject | `curl -sSI …/resolve/main/tinyllamas/stories260K.gguf` returns the same `x-linked-etag "270cba1b…"` as the pinned URL | agree | The etag names the LFS object, which any revision holding it serves. The revision has to come from the `/resolve/<40-hex>/` segment and `x-repo-commit` |
| CDN redirect target as a locator | reject | `location:` of the pinned URL → `https://us.aws.cdn.hf.co/xet-bridge-us/…` with a signed query carrying `Expires=1793059391` | agree | A signed URL that expires is not a durable locator |
| Relabelled v2 tool / dropped SCORECARD row as C1 evidence | reject | Committed controls `junk-c1-v2-relabel.c1.out` (`selftest=0 contract=0 … met=False`) and `junk-c1-drop-scorecard.c1.out` (`rows=8 … met=False`) | agree | Both shortcuts fail the frozen counter, as the Gate says |

- `scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama` → exit 0 with 93 `W04`, 1 `W01` (S481) and 0 `E`. This equals the lane's `census/start.out` and `census/end.out`; the report's prose omits the W01 (R3).
- SOURCES rows 232 → 234 (`grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|'` at each revision). Only S492 and S493 were added (`git diff` shows `+` lines only), both with NF=13.

Discernment: the spot-check agrees with the Gate on all sampled admits (2) and rejects (3).

## 5. Trend verdicts

| Trend | Verdict | Evidence |
|---|---|---|
| expansion | unchanged | No new `knowledge/` entry; `llamacpp-loading-lifecycle.md` gained an appended paragraph (S492/S493). Capabilities 11 → 11 (two rows reworded). Agrees with the lane |
| quality | improved | Five lost SCORECARD banners restored, which I re-verified. The SOURCES guard grades transitions again (`sources-append-only.py` exit 0, `added S492 (allowed)`). The v5 readers were fixed (check-receipt selftest). Replay was hardened (KLR 22/22). No admitted entry failed its re-check: S492 and S493 re-opened clean |
| discernment | improved | This outside spot-check agrees with the Gate on the sampled admits and rejects. That meets the condition the lane left open under KQ61 (the lane self-graded `unchanged` pending it) |

## 6. Routed defects (the lane fixes these next round unless marked otherwise)

- **R1 (lane, operability, High availability, seat Sen2Live F1).** `verify_archive_member()` in `tools/kama-llamacpp-live.py` hashes a member of any declared size (GNU sparse passes `isfile()`). A 104-byte archive whose digest the operator declared makes record time read ~10^15 bytes before the server starts. Not an escape: the archive digest is checked first, so only an operator-declared archive reaches it. Cap the member size against the declared asset size before hashing, as the lane already routed for round 49.
- **R2 (lane, conformance).** The report was filed with placeholders before its cited tip existed and was then rewritten in place (`15710a2a` → `dcc079e7`). Land the final lane commit first, then file the report once. Any later correction is an appended erratum naming the superseded text (PROTOCOL §Round-robin, "A filed report is a record").
- **R3 (lane, report precision).** The Sources & frontier line says the end census is "93 W04, 0 E"; the receipt and my run also show 1 `W01` (S481). Quote the census output whole.
- **R4 (orchestrator/operator, prompt route map).** Prompt §6 (run-8 map, confirmed by run 9) quotes critic `@m_flash`. The live `agentModelOverrides` has routed critic `@m_kfc` since the 17:45 -03 config change. Under the live map, m_flash seats are 26/69 (38%), below the ≥50% directive. The lane's 42/69 follows the stale quote. `w1-results.json` records no per-seat model, so the actual routing is an [INFERENCE] from the config. The prompt addendum is operator-side; it needs the current map. Correction to `round-47-verifier-spotcheck.md` step 1: the round-47 prompt carries the same critic `@m_flash` quote, so its "quoted map matches" row was wrong on critic.
- **R5 (lane, carried counter gaps).** Disclosed by the lane and not yet closed:
  - replay never witnesses server execution (K2Cheat, K2Urlswap);
  - record time never fetches the URLs (K2Record);
  - surviving mutants: C1 counter 21/52, tool 15/55, C2 counter 6/27;
  - content-blind exemption and substring declaration binding (K1Regions, K1Binding);
  - sub-20-line deletions unwatched (L1Lowthr; the `LOG.md` loss at `ed135b3c` predates this round);
  - prerelease cliff (r47-D7).
- **Operator/L0.** Planner seat still impossible under the policy-v2 validator, which also rejects `labrat` (`kama | round-39`). Also open: MISSION axes pair (`kama | round-35`) and parked worktree (`kama | round-41..43`). Untracked fleet-root files `=1239`, `=3900`, `T` are unattributed to kama and were left untouched.
- **Operator, promotion.** The four `SHONEN` boxes are `[~]` and look checkable by a non-author:
  - box 1: gate registry `registered 42 … defective 0`, SKILL §Round-48 registry;
  - box 2: three v5 live receipts, which I replayed 3/3 above;
  - box 3: SKILL v5 how-to, re-run by seat K2Fresh;
  - box 4: PROVINCE changed only in its instrument cell.

  Promotion is operator-owned; nothing was marked here.
