# SC01 — round-79 SOURCES append block (draft; the L1 appends, this seat does not edit corpus/SOURCES.md)

Milestone: kama r79 w1. Axis: coverage. Lane tip when this seat started:
`f7442dea53bd8f474293a2252437b5d869801f49` (read with `git -C <lane> rev-parse master`).
Registry state read: `corpus/SOURCES.md` at that tip — 654 lines, 292 rows, 292 unique ids, max `S552`.

## Append block

Insert as a new row after `S552` (11 columns, same shape as `S548`–`S552`):

| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |
|---|---|---|---|---|---|---|---|---|---|---|
| S553 | llama.cpp router `GET /models` at commit 39febd2adb947b70da35e95f9351b3bf58ad170a — https://raw.githubusercontent.com/ggml-org/llama.cpp/39febd2adb947b70da35e95f9351b3bf58ad170a/tools/server/README.md | docs | A | router model list is an inventory: unloaded models are listed and each carries status.value | §Router mode, GET /models note 1, line 2227 | In router mode `GET /models` lists every model in the cache whatever its load state — a model that is not running “will be added or updated according to the source” — and every entry carries `status.value` (`loaded`, `unloaded`, `loading`, `sleeping`; a failed unload adds `failed` and `exit_code`). A router model list is therefore an inventory, not a readiness claim. | mined | 2026-11-04 | on-release | corpus/knowledge/unregistered-listener-census.md |

Row cell rules honoured: `scope` is the frozen string from the round-79 dispatch, `anchor` is the
frozen anchor string, `kind` `docs` (a rendered project README, not a code file), `tier` `A`
(first-party specification text pinned by commit), `status` `mined`, `recheck` `on-release`
(the file is repo master content pinned to a build; a new reader must re-pin).

## Gate

- **URL:** https://raw.githubusercontent.com/ggml-org/llama.cpp/39febd2adb947b70da35e95f9351b3bf58ad170a/tools/server/README.md
- **Commit:** `39febd2adb947b70da35e95f9351b3bf58ad170a` (the build the live listener runs)
- **Opened:** 2026-11-04, this round, by this seat (fetch repeated live; not copied from a receipt)
- **HTTP status:** `200`; **bytes:** `135608`; **content-type:** `text/plain; charset=utf-8`
- **sha256:** `8fd5abde2fb52de3b30f30a170631d4c0d92febecc8da44d0541e48b132b35c6`
- **Lines:** 2616 (`wc -l`)
- **Located quote (line 2227, 16 words, within the 25-word limit):**

  > If a model is not running, it will be added or updated according to the source

  This is note 1's second bullet under `### GET /models: List available models` (heading at
  line 2197). Note 1 begins at line 2225 — "Adding `?reload=1` to the query params will refresh
  the list of models. The behavior is as follow:" — and the located line is the anchor's
  `note 1, line 2227`. The quote states that a model absent from the running set is still
  listed, which is the inventory predicate the row scope claims.

- **Anchor resolution, verbatim:** the anchor's "Router mode" is the router README region
  (router sections `### Routing requests` line 2135, `### Memory-based unloading` line 2163,
  `### GET /models: List available models` line 2197); the file has no literal heading
  containing "Router mode" at this commit. The anchor's line number resolves exactly: line 2227
  is note 1's second bullet.
- **`status.value` spans actually present (supporting the scope's second clause):**
  line 2206–2208 `"value": "loaded"`; line 2264–2266 `unloaded`; line 2269–2273 `loading`;
  line 2276–2282 `unloaded` with `"failed": true, "exit_code": 1`; line 2285–2289 `loaded`;
  line 2292–2296 `sleeping`; line 2299 names a `downloading` state; lines 2314–2319 add an
  `incomplete` value with no instance, and line 2470 states a paused download is "listed as
  incomplete" until posted again. Line 2230 adds that the
  router computes the arrays offline and "does not load the model, download files, or run
  inference".
- **Receipt:** `.ufo/waves/round-79/w1/SC01Sources/receipts/fetch-url.txt` (command, status,
  bytes, sha256, line count, exit 0).

## Collision check (duplicate id, duplicate URL)

Run against `corpus/SOURCES.md` at `f7442dea`, rows matched with the 0–3-leading-space pattern
`^ {0,3}\|\s*S\d+\s*\|`:

- **Duplicate id:** none. 292 rows carry 292 distinct ids; the highest is `S552`; ids `S548`–`S552`
  are the round-76/77/78 own-work rows. `S553` is absent from the file and from the fleet census
  (`scripts/sources-census.sh census`, `file rows 292` / `FLEET rows 292`, `missing 0`, EXIT=0,
  frozen receipt `.ufo/waves/round-79/measured/before/census.out`). **Next free id: `S553`.**
- **Duplicate URL:** the exact URL is absent (0 rows contain `39febd2adb947b70da35e95f9351b3bf58ad170a`).
  Same-file neighbours, by pinned commit and scope:
  - `S001` — `blob/master/tools/server/README.md`; scope: health, direct-server `/v1/models`, `/metrics`
    @ c0fd78626405. No router-mode surface, no `status.value`.
  - `S035`, `S112`, `S134`, `S526` — `blob/704366d76…/tools/server/README.md`; scopes: `/health`
    load-state only; `n_ctx` option text; documented context/KV-pool options incl. `/metrics`;
    `/v1/completions` request surface only. None names router-mode `GET /models`.
  - `S494` — `raw/…/caa8191d…/tools/server/README.md`; scope: `/tokenize` + `/detokenize` shape.
  - Each of the above pins a different commit and a different surface; the dispatch's rule that
    the README "already held by S001 and S526 is not re-rowed for the same surface" is satisfied
    because this row's surface (router-mode list = inventory with `status.value`) is not theirs.
- **Scope-level near-neighbour (not a duplicate):** `S479` — `raw/…/704366d76…/tools/server/server-models.cpp`,
  kind `code`, scope "the declared-capacity key llama.cpp's router-mode model listing returns".
  Different file, kind, claim and commit; it does not hold the note-1 inventory statement or the
  `status.value` enumeration. The idea "a model list is an inventory, not proof of a loaded model"
  also exists for other engines (`S011`/`S012`/`S031`, Ollama); this row is the llama.cpp router
  surface C3's census class rests on, which none of those rows can supply.
- **Result:** collision-free on both keys; the row is drafted as `S553`. Admission stays with
  `corpus/QUALITY.md` — this seat does not admit.

### Row validation in a lane-shaped fixture (no lane file edited)

Fixture `$S/fix/kama-shokunin-79` (scratch only): the lane root symlinked item by item, `corpus/`
items symlinked except `SOURCES.md`, and a copy of `corpus/SOURCES.md` with the `S553` row
inserted after `S552`.

- Base lane, unchanged registry — `bash scripts/sources-census.sh validate --root <fleet> kama`
  → `kama ok …` exit 0, **105** `W04` warnings.
- Fixture with the row appended, knowledge path **absent** — `validate <fixture>` → exactly one
  finding, `E11 S553 missing used-by corpus/knowledge/unregistered-listener-census.md`, exit 1.
  No `E01`–`E10` and no `E12` fires, i.e. the row's shape, id, kind, tier, status, date, recheck
  and used-by syntax are valid.
- Fixture with a placeholder at that knowledge path — `validate <fixture>` → `ok`, exit 0,
  still **105** `W04` (the row introduces no duplicate-URL warning).
- Fixture census after append — `rows 292→293`, `tier.A 277→278`, `status.mined 263→264`,
  `tier.invalid 0`, `status.invalid 0`, `missing 0`, exit 0.

**Consequence for the L1:** appending `S553` before `corpus/knowledge/unregistered-listener-census.md`
exists turns a clean lane validate (`ok`, exit 0) into `E11 S553 …` (exit 1). The row and the
knowledge entry must land in the same commit, or the row waits.

## Census receipts (round 79, coverage axis)

### Before — base probe, no class column (verified live this seat, and against the frozen receipt)

- **Command:** `bash tools/kama-probe.sh listeners` (cwd = the lane) — **exit 0**
- **Summary line:**
  `probed=33 model_endpoints=7 foreign_service=24 unauthorized_service=0 dead=2 not_http=0 model_loading=0`
- **Columns:** `port | bind | owner | verdict | reason | served_model` — no `registered` column;
  no `governed`/`unregistered` summary keys. 33 port rows.
- **Receipt:** `.ufo/waves/round-79/w1/SC01Sources/receipts/listeners-before.txt` (per-port rows
  trimmed there; the full 33-row table is the frozen pre-freeze receipt
  `.ufo/waves/round-79/measured/before/c3-listeners-base.out`, rev `ee53f1a2`, `EXIT=0`, whose
  summary line is byte-identical to this run).
- Compared with the plan's before-state (`measured/before/c3-listeners-base.out`): same counts,
  so the live host has not drifted since the freeze.

### After — the census tool at the round-79 tip (measured once it landed)

`tools/round79-unregistered-census.py` landed at `06:48:12` local (18 × 30 s polls after this
seat started watching). Both legs were then measured:

- **Command:** `cd $S && TMPDIR=$S python3 <lane>/tools/round79-unregistered-census.py --repo <lane>`
  → **exit 0**, two lines:

  ```
  UNREGISTERED_CENSUS port=40299 unregistered=1 governed=1 class_missing=0 rows=35
  UNREGISTERED_CENSUS_LIVE model_endpoints=8 governed=0 unregistered=8 ports=1234,8788,8789,8790,8791,8793,8795
  ```

  The first line is the plan's frozen C3 target shape, with the fixture port filled in.
  Receipt: `.ufo/waves/round-79/w1/SC01Sources/receipts/census-after.txt`.
- **Command:** `bash tools/kama-probe.sh listeners` (cwd = the lane) — **exit 0**, after the class:

  ```
  probed=33 model_endpoints=7 foreign_service=24 unauthorized_service=0 dead=2 not_http=0 model_loading=0 governed=0 unregistered=7 registry=ok
  ```

  Header is now `port | bind | owner | verdict | reason | served_model | evidence | registered`;
  per-port `registered` distribution **26 × `-`, 7 × `no`, 0 × `yes`** (33 port rows).
  Before this round the same command printed no `registered` column and no `governed`/`unregistered`
  keys. Receipt: `.ufo/waves/round-79/w1/SC01Sources/receipts/listeners-after.txt`.
- **Counts that moved:** `governed` 0→0 (nothing governs these ports under the lane registry),
  `unregistered` absent→7, `registry=ok` is new, `class_missing` 0 on the counter. `model_endpoints`
  stayed 7 in the standalone probe; the counter's informational live leg printed 8 endpoints over
  7 listed ports in its own run a minute earlier. That difference is reported verbatim, not
  reconciled: the plan scopes the live leg as informational, and the two runs are different
  instants with the counter's own fixture child live.
- The `used-by` target `corpus/knowledge/unregistered-listener-census.md` was absent when this
  seat started; the L1 committed it at `d6408a63` together with its own `S553` row, so the pointer
  now resolves (verified: `kama ok`, exit 0 at that tip).
- **The L1 appended its own variant of `S553` at `d6408a63`**, not this draft. Same id, same URL,
  same `sha256` in the anchor cell, same `status`/`opened`/`recheck`/`used-by`, scope extended with
  "not served-identity normalization (S001/S016/S526) and not model quality"; source, scope wording,
  anchor suffix and `teaches` differ from the draft below. In the registry at `d6408a63` the row
  validates `ok` (exit 0) and the census reads `rows 293`, `tier.A 278`, `status.mined 264`.

## Provenance and limits

- **Local build tree matches the pin byte-for-byte:** `~/src/llama.cpp` `rev-parse HEAD` =
  `39febd2adb947b70da35e95f9351b3bf58ad170a`; `tools/server/README.md` there is 135608 bytes,
  sha256 `8fd5abde…` (identical to the fetch), and `git status --porcelain` on that file is empty,
  so the tree copy is unmodified. Receipt:
  `.ufo/waves/round-79/w1/SC01Sources/receipts/local-tree-readme.txt`.
- **Commit pin corroborated on the live host:** `GET http://127.0.0.1:1234/props` → HTTP 200,
  233 bytes, `build_info` = `b1-39febd2`, `model_path` = `none` (read-only GET; curl exit 0).
  The short hash `39febd2` is the pinned commit `39febd2adb947b70da35e95f9351b3bf58ad170a`, so the
  row's pin names the build the live listener actually runs, as the plan states. Receipt:
  `.ufo/waves/round-79/w1/SC01Sources/receipts/live-listener-build.txt`. This is identity evidence
  only — the same listener is the round's *unregistered* subject, not a registered consumer.
- Identity chain: the URL's bytes = the local tree's file bytes (sha256 equal) and the tree HEAD is
  the pinned commit; the running listener reports a `build_info` carrying the same short hash. The
  chain binds the *source text* to the served build; it says nothing about model behaviour.
- Fetched, hashed and quoted live in this seat; the pre-freeze receipt
  `.ufo/waves/round-79/measured/before/source-router-models.out` independently names the same
  URL, HTTP 200, 135608 bytes, sha256 `8fd5abde…` and the same line-2227 quote, so two
  independent opens of this URL agree byte-for-byte.
- The pre-freeze receipt's local-tree assertion was re-verified independently this seat (see the
  local build tree bullet above); the claim no longer rests on the receipt alone.
- The quote is the README's own wording, including its non-idiomatic "The behavior is as follow:"
  at line 2225; nothing was corrected in the quoted text.
- Tier `A` is scoped to this row's `scope` cell only: the README states the router list's
  inventory semantics; it is not evidence about any particular host, loaded model, or consumer,
  and it does not establish that a listener is healthy or governed.
