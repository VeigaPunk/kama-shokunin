author: hyaku closure (non-author integrator, @m_sonnet)

# kama round 42 — non-author closure spot-check

Date: 2026-10-25. Round measured: base `0b606b03bf0b2a87b791aa537f6c72c941624cf0` (round-41 spot-check) to lane tip `3e6fdbe9e0ca1ca5b633d0b312d5561301e924c4` (`git ls-remote origin refs/heads/master` on the lane's GitHub remote prints this hash). Every measurement ran in fresh clones of that remote (`/tmp/kama-r42-closure/{base,meas,tip}` at `0b606b03`, `2c018107`, `3e6fdbe9`); no lane command was run in the parked worktree.

Verdict: **admitted**. All three claims re-verify, no axis is harmed, the spot-check agrees on both admits and both rejects sampled. Several lane-disclosed limits and four defects (section 7) are routed.

## 1. Conformance (step 1)

| Check | Observed | Result |
|---|---|---|
| Report committed by lane identity | `git log --format='%an %H' -- .ufo/reports/round-42/kama.md` → `kama-shokunin af737dd1ba64a757f8414b8f1bc0ec70661c7d7e` | ok |
| `SHONEN` heading, one line per box | lane `SHONEN.md` has 4 boxes; report `## SHONEN` carries 4 `[~]` lines | ok |
| Cited lane commits exist and are on the branch | `0b606b03`, `0bfd47ab`, `dd9f5dc6`, `2793eb51`, `c8c92db4`, `3d9bd8d7`, `595b65f5`, `8bc8e375`, `2c018107`, `3e6fdbe9`: `git merge-base --is-ancestor <h> origin/master` → ancestor for all ten (local `master` is the stale parked ref `df61204c`, 22 commits behind, see D-A) | ok |
| Lane pushed, no leftover round work | `jj-lane.sh state` → `local=df61204c… remote=3e6fdbe9… ahead=0 behind=22 head=detached tracked=11 untracked=96`; `ahead=0` against a stale local view; the real tip is on the remote | ok, with defect D-A |
| Prompt carries template contract | `.ufo/prompts/kama-round-42.md` has §1 MISSION/AXES, §2 claims, §2b frontier, §3 L2 floor, §4 report contract, §5 commit scope, §6 hyaku addendum | ok |
| Marker report? | No: real report, 10 real commits, receipts, 64 seat report files (`ls .ufo/waves/round-42/w1/out/*.md \| wc -l` → 64) | not `failed` |
| Counters frozen | `git diff --stat 0bfd47ab 3e6fdbe9 -- tools/round42-selfdesc-reconcile.py tools/round42-digest-audit.py tools/round42-capacity-audit.py .ufo/waves/round-42/preregistration.json` → empty | ok |
| Append-only | `git diff --numstat 0b606b03 3e6fdbe9 -- corpus/SOURCES.md LOG.md corpus/lessons/round-38.md` → `6 0`, `10 0`, round-38 unchanged (correction lives in the round-42 lesson) | ok |

Driver digest (`.ufo/watchdog.log`, mutable): `2026-10-25T17:49:56-03:00 launch kama round=42 pgid=2295067 driver=hyaku-inline attempt=1`; `2026-10-25T19:59:12-03:00 complete kama round=42; hyaku-inline attempt=1`.

Conformance defects (status-neutral):

- **D-A (hyaku driver, not lane; repeat of round-41 D-A):** the closure prompt lists lane HEAD before/after as `df61204c8badac202f51335eb59d9289a67ef4b5`, the parked worktree's stale detached local `master`. The real base is `0b606b03`, the real tip `3e6fdbe9`. `git diff df61204c df61204c -- SCORECARD.md` is vacuously empty, so I diffed the real hashes (`git diff 0b606b03 3e6fdbe9 -- SCORECARD.md`). The parked worktree stays 107 porcelain lines dirty (operator-owned, round-40 D5, L0 `kama | round-41`, refreshed `kama | round-42`).
- **D-B (lane):** the lane did not use `jj-lane.sh` (it refuses the parked worktree's state) and committed with plain `git` in a fresh clone under the lane identity; disclosed in the report, and every commit landed on the remote branch. Not a barrier.
- **D-C (lane):** the `corpus/SOURCES.md` search-log row dated 2026-10-25 (line 259) says the staged S401 and S424 sources were "not opened this round", while the round-42 lesson `## Gate` and the report say both were re-opened and re-checked. One of the two statements is false; see section 7, item 1.

## 2. Claims

The lane's frozen counters are the claims' own definitions of the predicate (not registered sibling gates), as in round 41. I ran them in my own clones at fresh settings and re-derived the underlying facts with plain commands.

### C1 — calibration 7→7: SCORECARD head, README, PROVINCE match observed state (re-measured)

- Base: `python3 tools/round42-selfdesc-reconcile.py --repo /tmp/kama-r42-closure/meas --tip 0b606b03… --out …` → `r41=0 banner=4 planned=3 retired=4 saturation=3 caps=4 receipts=0 readme=11 province=5 rel=6 mismatches=40 maxN=41 met=False`, exit 1 (equals the report's base line).
- Measured `2c018107` and tip `3e6fdbe9`: `r41=0 banner=0 planned=0 retired=0 saturation=0 caps=0 receipts=0 readme=0 province=0 rel=0 mismatches=0 maxN=42 met=True`, exit 0 both (equals the report).
- Plain re-derivation, independent of the counter:
  - Stale phrases in the head (before the `### Historical axes table`): at base `operability and freshness` 1, `adds **zero** verified completed rounds` 1; at tip 0 for all six stale phrases.
  - Head table facts at the tip: a Python re-hash of every `` `path` sha256 `hex` (N lines) `` pair in the head → 7 ok, 0 bad (`PROVINCE.md` `1dc13fa6…` 183 lines, `kama-probe.sh` `36b64978…` 1138, `test-snapshot.sh` `236c23c1…` 194, `SKILL.md` `151023b9…` 1375, `endpoint-identity.md` `0100ac6d…` 218, `cross-lane-scope.md` `1801cb7f…` 87, `ls-remote-vllm.txt` `13388e48…`).
  - Run facts in the table re-executed by me: `grep -c '^## ' SKILL.md` → 30; recheck-cadence count over S001–S477 → 218; knowledge entries excluding `engine-sides` → 34; `*verifier-spotcheck.md` count → 28 (before this file); `cross-lane-scope.md` pipe-line count → 16; `bash tools/test-snapshot.sh` → `RESULT pass=30 fail=0`; `pin-watch.py selftest` → `pass=9 fail=0`; `report-landing-audit.py --selftest` → `cases=79 failed=0`; `sources-append-only.py --selftest` → `42/42`; `citation-provenance.py --selftest` → `ok (24 cases)`.
  - README names every non-hidden top-level entry (AGENTS.md, LOG.md, MINT.md, PROVINCE.md, README.md, SCORECARD.md, SHONEN.md, SKILL.md, considerthese, corpus, plans, registry, tests, tools: `grep -cF` ≥ 1 each); `.gitignore` and `.ufo` are not named (hidden entries, counter ignores them; minor, section 7 item 4). PROVINCE names every `tools/…` and `registry/…` path the capability list cites (pin-watch, digest-ledger, ollama-evidence, gguf-identity, context-capacity, instrument-agreement, engine-pins, digest-ledger.tsv: `grep -cF` ≥ 1 each).
  - Deleted head blocks preserved: every deleted non-blank line of `git diff 0b606b03 3e6fdbe9 -- SCORECARD.md` other than the six replaced `## Axes` rows and the old reconcile sentence exists verbatim in the tip (the round-5 banner, Planned, Retired, Saturation sit under `## Historical head sections`). Scores held 8/8/7/9/7/7.
- Relevance (the lane leaves this to the closure): I read the six axis rows. The run facts are on-topic for their axes (operability: the registered gate plus four selftests and a stated limit that registered endpoints are DEAD; freshness: recheck-cadence count, vLLM ls-remote evidence; depth: SKILL.md structure and the identity entry; coverage: held-entry count and surface list; calibration: outside-closure count and calibration instruments; adjacency: cross-lane-scope table). The lane's own wave found that the counter's needles are substring tests and that a degenerate edit can meet it (R42A05, R42A13); I found no such degeneration in the committed rows. I rule the claim verified at the scope it states ("matches observed repository state"); it is not proof that the scores are right.
- Note: my own spot-check file raises the `*verifier-spotcheck.md` count in the calibration row from 28 to 29 after the measured commit. The table is dated to the measured commit and states 28 there; not a defect, but the round-43 re-derivation must restate it.

### C2 — operability 8→8, capability `digest-ledger` (re-measured, one selftest evidence-verified)

- Base: `python3 tools/round42-digest-audit.py --repo … --tip 0b606b03… --seed 4242` → `tool=0 contract=0 live=0 hygiene=0 capability=0 met=False`, exit 1; details `tools/digest-ledger.py absent`, `hygiene: 2 leaked temp entries after the round-41 counters`, `no digest-ledger row in canonical list as of round 41`.
- Tip `3e6fdbe9`, fresh seed 4242 (the lane used 42, 7, 1337): `tool=1 contract=1 live=1 hygiene=1 capability=1 met=True seed=4242`, exit 0; live reference `tokens=97 blob=88 external_ok=5 external_absent=0 unverifiable=3 wrong_flagged=1 ledger_bad=0 wrong_unflagged=0 unknown=0`.
- `python3 tools/digest-ledger.py selftest` → `selftest pass=10 fail=0` (equals the report). `python3 tools/digest-ledger.py scan --repo … --rev 0b606b03…` → `tokens=94 blob=84 … wrong_unflagged=1 unknown=9`, exit 1; at the tip → `tokens=97 blob=88 … unknown=0`, exit 0 (equal to the report).
- Independent re-hash of the ledger's externals (bypassing the tool): `sha256sum` of the b11755 archive → `753bfa73…`, `libllama-server-impl.so` → `e404b91a…`, `shokuknow/merge/kama/SOURCES.append.md` → `3ad0df68…`, the round-35 `dockerfile.html` and `docker-dockerfile.html` → `bcc55c92…`, `~/.cache/kama-shokunin/models/stories260K.gguf` → `270cba1b…` — all six equal the ledger rows. The wrong row: `ls-remote-tags.txt` hashes to `5585f6027df2…` (the correct digest), and `5585f602f71c…` is flagged. The gzip unverifiable row reproduces: `zcat …/runs.json.gz | sha256sum` → `38e4ab05…` (equals the ledger's digest). A plain 64-hex census of tracked `.md/.tsv/.json` outside `.ufo/waves` moves 186 → 189 (+3, same delta as the tool's 94 → 97).
- Capability row: the `digest-ledger` row is in the round-42 canonical list with first-working round 42 (8 rows). Evidence-verified, not executed by me: the 64-seat wave and its hardening claims (R42B* seats) rest on committed seat reports and the selftest tally above.
- Limits (lane-disclosed, not repaired; the counter is frozen): a lazy ledger or counter-importing tool could meet `met=True` (R42B06); the `contract` leg mirrors the tool (R42B05 M3); the tool sees only exact 64-hex tokens, so the 65-character run at `corpus/lessons/round-38.md:51` (`3ad0df68e8423a3b…ce234ff`, length 65 by my count) is invisible to it and was corrected append-only in the round-42 lesson; `external_ok` is host-dependent by design (one ledger row points into the parked worktree, another into `~/.cache`, which is lane-owned and re-creatable from the S039 URL).
- Score held at 8. The gain is a new working, self-tested capability that classifies every cited digest, plus the round-41 counters' temp leak closed.

### C3 — coverage 9→9, assimilation from `merge/kama/` (re-measured; sourced on S478, S479)

- Base: `python3 tools/round42-capacity-audit.py --repo … --tip 0b606b03… --base 0b606b03…` → `entry=0 rows=0 coverage=0 gate=0 census=1 met=False`, exit 1. Tip: `entry=1 rows=1 coverage=1 gate=1 census=1 met=True`, exit 0.
- Coverage ground check, plain: `grep -rn kv_cache_size_tokens corpus SKILL.md` at base → 0 hits; at the tip it appears in `corpus/knowledge/context-capacity-engine-sides.md` and `corpus/lessons/round-42.md`. The entry sits on K05 ground the lane held only as measured llama.cpp cells.
- Both source files re-fetched by me today (see section 4): bytes equal the committed copies (`cmp` identical) and the rows' SHA-256s.
- Entry citations spot-read against the vLLM copy: `kv_cache_utils.py:1195-1227` (`get_max_concurrency_for_kv_cache_config`: per-group `cdiv(max_memory_usage_bytes, page_size_bytes)` summed over device groups, host groups on `hisparse_host_num_blocks`, `min(limits)`), `1230-1236` (`may_override_num_blocks`), `1616-1620` (HiSparse early return before line 1627), `1627`, `2308`, `2321-2322`, `2325-2328`, and `grep -n "kv_cache_size_tokens\|kv_cache_max_concurrency"` → only the two writes at 2321-2322 (so "nothing reads them back" holds). llama.cpp copy: `get_router_models` at 2329, guard at 2378-2379, `grep -o max_model_len | wc -l` → 0. The three corrections of the staged prose (hybrid/host-bound token figure, router-handler scope, dense-path-only override) are supported by that code.
- Limits (lane-disclosed): the coverage leg is not a sourcing test (R42C06); the counter fails KQ48 by positional cell indexing (R42C07); four counter mutants survive (R42C14). The entry is a source reading, not a measurement, and says so.
- Score held at 9. Admitted: one new entry on uncovered ground, two mined tier-A rows (S478, S479), README coverage and frontier blocks.

### Separability and SCORECARD

Each claim's file set alone scores `met=True` only on its own counter (receipts `controls/sep-c{1,2,3}-only.*.out`, regenerated at the measured commit); shortcut controls `junk-*.out` all read `met=False` (read, not re-run). `git diff 0b606b03 3e6fdbe9 -- SCORECARD.md` → 114 insertions, 31 deletions; the deletions are the superseded head blocks (preserved under §Historical head sections) and six `## Axes` rows rewritten with the same scores. No owned axis harmed.

## 3. Axis verdicts

| Axis | Verdict | Reason |
|---|---|---|
| operability | improved | new `digest-ledger` capability: selftest 10/10, audit `met=True` at a fresh seed, six external digests independently reproduced on this host, round-41 counters' leak closed; score held 8 |
| calibration | improved | head self-description: 40 mismatches → 0, re-measured, hashes and run facts re-derived; score held 7; relevance and sufficiency limits disclosed and judged here |
| coverage | improved | new admitted entry on K05 engine-side ground absent at base (`kv_cache_size_tokens` 0 hits → entry), two sources re-opened and byte-equal; score held 9 |
| freshness | unchanged | no claim; score 8 held; `recheck` figure 218 unchanged by design |
| depth | unchanged | no claim; `SKILL.md` byte-identical (sha256 `151023b9…`) |
| adjacency | unchanged | no claim; scope kept (`PROVINCE.md` out-of-province wording read, no absorption) |

## 4. Discernment spot-check (LEARNING.md)

Sample of `corpus/lessons/round-42.md` `## Gate`: two admits, two rejects.

| Item | Decision | Re-opened source | Agree? | Reason |
|---|---|---|---|---|
| S478 vLLM `kv_cache_utils.py` @ v0.32.0 (new `SOURCES.md` row) | admit | `curl -sSL https://raw.githubusercontent.com/vllm-project/vllm/v0.32.0/vllm/v1/core/kv_cache_utils.py` today | **agree** | 111612 bytes, SHA-256 `af4164bc…e57a` equals the row and the committed copy (`cmp` identical). The Gate quote "return int(max_concurrency * max_model_len), max_concurrency" is at line 2308 (5 words, ≤25) and "num_blocks = available_memory // bytes_per_block" at 1627. It grounds the row's headline claim (token figure derived from the declared length). Ground is new to the lane (0 hits at base). |
| S479 llama.cpp `server-models.cpp` @ 704366d7 (new row) | admit | `curl -sSL https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f…/tools/server/server-models.cpp` today | **agree** | 117111 bytes, SHA-256 `9c5a6f2c…8b4a` equals the row and copy. Lines 2378-2379: `if (meta.n_ctx_train > 0) {` / `model_info["context_length"] = meta.n_ctx_train;` in the `get_router_models` lambda (2329); `max_model_len` occurs 0 times. Quote 5 words, ≤25. |
| Staged r8 amendment (S401 llama-cpp-python settings, S405 llama.app docs) | reject this round, flip named | `curl` of `abetlen/llama-cpp-python v0.3.36 llama_cpp/server/settings.py` and `https://llama.app/docs/api` | **agree** | The quotes are true (settings.py SHA-256 `8cd8036d…6b36`, line 69 `n_ctx: int = Field(default=2048, ge=0, description="The context size.")`; the docs page still has "Model metadata (id, context size, parameters)"), so the Gate is right that this is a scope refusal, not a falsity one; `grep -c 'S40[15]' preregistration.json` → 0, no frozen leg consumes them, and the entry reads two engine-source files. A third server implementation and a docs-tier page do not fit one entry. |
| Staged r11 amendment (S424 own-work receipt) | reject this round, flip named | `/home/vgpnk/Projects/shokuknow/lanes/kama/round11/evidence/llamacpp-served-card.md` and the lane's `.ufo/waves/round-18/live-recovery/receipt-1.json` | **agree** | The staged file exists (5760 bytes), line 26 is "## The card as served", and `grep -c '"n_ctx":256,"n_ctx_train":2048'` → 1, so the Gate's account is accurate. The refusal rests on provenance (a campaign-repo-relative path absent from the lane and the package) and on duplication: the lane already holds its own receipt with `n_ctx_train` (2 hits in `receipt-1.json`). Sound reject with a flip (copy the receipt bytes in). |
| New `corpus/SOURCES.md` rows S478 and S479 (quote check) | admit | row text in the tip registry | **agree** | Both rows carry a located quote of 5 words naming a file line, a tag/commit, the raw SHA-256 and the evidence copy; opened date 2026-10-25; `scripts/sources-census.sh census` base → tip: rows 218 → 220, tier A 208 → 210, B 7, C 3, mined 199 → 201, queued 8, rejected 11, missing 0 (equals the report). |

Registry validate: `sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama` → `exit=0` (93 W04 + `ok`; the fleet root reads the stale parked registry, not the tip, round-40 N4). The same command on a full mirror of the tip clone (`--root /tmp/kama-r42-closure/mirror`) → exit 0, 93 W04, 1 `ok`, 0 `E`.

## 5. Trend verdicts

- **expansion: improved.** One admitted entry on ground the lane did not hold (`context-capacity-engine-sides.md`), two mined tier-A rows, registry 218 → 220, one new capability (`digest-ledger`). No admitted entry fails the bar it was admitted under (citations spot-read above).
- **quality: improved.** Superseded head sections re-derived with the old text kept; the S472 wrong digest and nine other unexplained digests classified; both round-41 counters stopped leaking temp dirs; the entry's own first draft was found false by wave seats and corrected before landing (I confirmed the corrected hybrid/host-bound wording against the code); the 65-character citation was corrected append-only. D-C (a search-log line contradicting the Gate) is a defect, but it does not fail an admitted entry.
- **discernment: improved.** The spot-check agrees on both admits and both rejects, the rejects name scope reasons and flips rather than falsity (fixing the round-40/41 pattern), the round-41 closure's four routed defects each became a fix or a named route (item 2 `pin-watch` in PROVINCE Owns is fixed, item 4 report no longer calls `skill://shokunin` uninstalled, item 1 narrowed and its limit disclosed, item 3 operator-owned and still open), and KQ50–KQ53 each cite a mined mistake.

## 6. SHONEN

All four boxes remain `[~]` in the report. None is fully checkable by a non-author from this round alone: box 2 (end-to-end task) gains a fresh independently re-runnable instance (the `digest-ledger` live scan, which I re-ran), box 3 (executable without oral context) is partly supported (selftests run clean on this host; the CPython matrix is a lane seat's claim). I do not write `[x]`; promotion is operator-owned.

## 7. Routed defects for round 43

1. **D-C, `corpus/SOURCES.md` line 259 versus the round-42 Gate:** the search-log row says S401 and S424 were "not opened this round"; the Gate says both were re-checked on 2026-10-25 (I re-checked both and the Gate is accurate). Append a correction entry (SOURCES is append-only) and sweep the lesson and README for the same sentence.
2. **Counters prove facts, not sufficiency (C1 relevance needles, C2 `contract` mirror and cheap mutants, C3 coverage leg not a sourcing test):** round 43 should add the counters that a do-nothing or low-cost-edit control fails, as the lane's own wave found (R42A05, R42A13, R42B05, R42B06, R42C06).
3. **Restate the head's `verifier-spotcheck` count** (28 at the measured commit, 29 with this file) in the round-43 re-derivation, and keep `Latest measured round` at 43.
4. README names no hidden top-level entries (`.gitignore`, `.ufo`); either name them or state that hidden entries are excluded.
5. Operator-owned and still open: the parked worktree `/home/vgpnk/Projects/shokunin/kama-shokunin` is detached on the stale `df61204c` lineage and 107 porcelain lines dirty (round-40 D5); fleet-root `validate` and the closure prompt's HEAD pins read that stale state, not the tip (D-A).
6. Planned (round 43) item 1, the S-id prose cross-check half of `considerthese/2026-10-25.md` proposal 1, stays the right next claim; it must cover the 65-character class the digest tool cannot see.
