# SC01Sources — source row, Gate block and census receipts (kama round 79, w1)

Role: scribe (leaf; no subagent dispatch). Axis: coverage.
Lane tip at seat start: `f7442dea53bd8f474293a2252437b5d869801f49`
(`git -C /home/vgpnk/Projects/shokunin/kama-shokunin rev-parse master`). The L1 advanced it to
`d6408a63f4ac4efd1d7161180aa62bf10f6f591a` ("round-79: lesson …, S553, census entry, coverage row,
pre-correction receipt") while this seat was measuring; receipts name the tip they were taken at.
Scratch root `$S` = `/fast/scratch/hyaku/kama-r79/SC01Sources/` — removed before yield.

## Behavior delivered

1. Opened the frozen URL myself this round and recorded status, bytes, sha256, line count and the
   located ≤25-word quote with its line number in a `## Gate` block.
2. Drafted the single round-79 SOURCES append row (`S553`) in the registry's 11-column shape, with
   the dispatch's frozen `scope`, `anchor`, `kind`, `tier`, `status`, `opened`, `recheck` and
   `used-by` values.
3. Ran the duplicate-id and duplicate-URL collision sweep with the 0–3-leading-space row pattern and
   reported the next free id.
4. Validated the row against the fleet census parser in a lane-shaped scratch fixture (both with and
   without the used-by target on disk) and recorded the census deltas.
5. Recorded the round-79 census **before** and **after** counts, each with its command and exit —
   the after leg measured once the sibling census tool landed at `06:48:12` (see §Census).

`corpus/SOURCES.md` was not edited — the L1 appends.

## Gate (frozen for the L1 to quote-check)

- URL: `https://raw.githubusercontent.com/ggml-org/llama.cpp/39febd2adb947b70da35e95f9351b3bf58ad170a/tools/server/README.md`
- HTTP `200`, **135608** bytes, `text/plain; charset=utf-8`, **sha256 `8fd5abde2fb52de3b30f30a170631d4c0d92febecc8da44d0541e48b132b35c6`**, 2616 lines
- Opened **2026-11-04** by this seat (live fetch, repeated; not copied)
- Located quote, **line 2227**, 16 words:

  > If a model is not running, it will be added or updated according to the source

  Note 1 opens at line 2225; the located line is its second bullet, so the frozen anchor
  `§Router mode, GET /models note 1, line 2227` resolves exactly. No literal heading containing
  "Router mode" exists at this commit — the anchor names the router README region whose section is
  `### GET /models: List available models` (line 2197). That discrepancy is recorded, not papered
  over.
- `status.value` support for the scope's second clause: `loaded` (2206–2208, 2285–2289), `unloaded`
  (2264–2266, 2276–2282 with `failed`/`exit_code`), `loading` (2269–2273), `sleeping` (2292–2296),
  `downloading` named at line 2299; line 2230 states the router computes the arrays offline and
  "does not load the model, download files, or run inference".

## Row drafted

`S553` — see `.ufo/waves/round-79/w1/SC01Sources/sources-append.md` for the full Markdown row
(819 bytes, 11 cells, single physical line). Column values:

| column | value |
|---|---|
| id | `S553` |
| kind | `docs` |
| tier | `A` (scoped to this row's `scope` only) |
| scope | `router model list is an inventory: unloaded models are listed and each carries status.value` |
| anchor | `§Router mode, GET /models note 1, line 2227` |
| status | `mined` |
| opened | `2026-11-04` |
| recheck | `on-release` |
| used-by | `corpus/knowledge/unregistered-listener-census.md` |

## Collision findings

- **Next free id: `S553`.** 292 rows, 292 unique ids, max `S552`; `S553` absent from
  `corpus/SOURCES.md` and from the fleet census (`file rows 292`, `FLEET rows 292`, `missing 0`).
- **Duplicate URL: none.** The exact URL is absent (0 rows carry `39febd2adb…`). Same-file
  neighbours pin other commits and other surfaces: `S001` (blob/master; health, direct-server
  `/v1/models`, `/metrics`), `S035`/`S112`/`S134`/`S526` (blob/`704366d76`; `/health` load state,
  `n_ctx` text, context/KV-pool options, `/v1/completions` request surface), `S494`
  (raw/`caa8191d`; `/tokenize` + `/detokenize`). None holds the router-mode list or `status.value`.
- **Nearest scope neighbour:** `S479` (code, `server-models.cpp` @ `704366d76`, router listing's
  declared-capacity key) — different file, kind, commit and claim; not a duplicate. Ollama's
  inventory-vs-running distinction (`S011`/`S012`/`S031`) is a different engine and cannot supply
  the llama.cpp router surface C3 rests on.
- **Validator confirmation:** in the fixture, the appended registry keeps `W04` at **105** — exactly
  the base lane's count — so the row adds no duplicate-URL warning.

## Census receipts (coverage axis)

### Before (measured this seat)

- `bash tools/kama-probe.sh listeners` (cwd = lane) → **exit 0**
- `probed=33 model_endpoints=7 foreign_service=24 unauthorized_service=0 dead=2 not_http=0 model_loading=0`
- 33 port rows; columns `port|bind|owner|verdict|reason|served_model`; **no** `registered` column
  and **no** `governed`/`unregistered` summary keys — the base state the plan describes.
- Byte-identical summary to the frozen pre-freeze receipt
  `.ufo/waves/round-79/measured/before/c3-listeners-base.out` (rev `ee53f1a2`, `EXIT=0`), so the
  live host did not drift between freeze and this run.
- Receipt: `.ufo/waves/round-79/w1/SC01Sources/receipts/listeners-before.txt`.

### After (measured once the sibling tool landed)

- `tools/round79-unregistered-census.py` landed at `06:48:12` local (18 × 30 s polls).
- `cd $S && TMPDIR=$S python3 <lane>/tools/round79-unregistered-census.py --repo <lane>` →
  **exit 0**:
  - `UNREGISTERED_CENSUS port=40299 unregistered=1 governed=1 class_missing=0 rows=35`
  - `UNREGISTERED_CENSUS_LIVE model_endpoints=8 governed=0 unregistered=8 ports=1234,8788,8789,8790,8791,8793,8795`
- `bash tools/kama-probe.sh listeners` (cwd = lane) → **exit 0**:
  `probed=33 model_endpoints=7 foreign_service=24 unauthorized_service=0 dead=2 not_http=0 model_loading=0 governed=0 unregistered=7 registry=ok`;
  header now carries `evidence` and `registered`; per-port `registered` = 26 × `-`, 7 × `no`,
  0 × `yes`.
- Deltas: `registered` column and `governed`/`unregistered`/`registry` keys are new; `unregistered=7`
  for 7 model endpoints, `governed=0`. The counter's informational live leg printed 8 endpoints over
  7 ports in its own run a minute earlier than the standalone probe's 7 — reported verbatim, not
  reconciled (the plan scopes that leg as informational; the runs are different instants with the
  counter's fixture child live).
- Receipts: `.ufo/waves/round-79/w1/SC01Sources/receipts/{census-after.txt,listeners-after.txt}`.

### Registry census deltas (measured by proxy in a scratch fixture)

`bash <fleet>/scripts/sources-census.sh census <fixture>` → `rows 292→293`, `tier.A 277→278`,
`status.mined 263→264`, `tier.invalid 0`, `status.invalid 0`, `missing 0`, exit 0.

## Gates exercised

| gate | command | result |
|---|---|---|
| URL fetch | `curl -sS … raw.githubusercontent.com/…39febd2adb…/tools/server/README.md` | 200, 135608 B, sha256 `8fd5abde…`, exit 0 |
| quote location | `sed -n '2225,2228p'` + exact assert on line 2227 | exact match, 16 words |
| live build pin | `curl -sS http://127.0.0.1:1234/props` | 200, `build_info=b1-39febd2`, exit 0 |
| base listeners probe | `bash tools/kama-probe.sh listeners` | exit 0, `probed=33 model_endpoints=7 …` |
| registry validate, base lane | `scripts/sources-census.sh validate --root <fleet> kama` | `kama ok …`, exit 0, 105 W04 |
| registry validate, fixture + row, used-by absent | `scripts/sources-census.sh validate <fixture>` | one `E11 S553 missing used-by corpus/knowledge/unregistered-listener-census.md`, exit 1 |
| registry validate, fixture + row, used-by present | same | `ok`, exit 0, 105 W04 |
| registry census, fixture + row | `scripts/sources-census.sh census <fixture>` | rows 293, tier.A 278, mined 264, exit 0 |
| registry validate at `d6408a63` (L1's row) | `scripts/sources-census.sh validate --root <fleet> kama` | `kama ok …`, exit 0, 105 W04, no `S553` finding |
| tree README identity | `sha256sum ~/src/llama.cpp/tools/server/README.md`; `git -C ~/src/llama.cpp rev-parse HEAD` | `8fd5abde…`, HEAD `39febd2adb…`, file unmodified, exit 0 |
| census class counter | `python3 tools/round79-unregistered-census.py --repo <lane>` | exit 0, `UNREGISTERED_CENSUS port=40299 unregistered=1 governed=1 class_missing=0 rows=35` |
| listeners probe, after class | `bash tools/kama-probe.sh listeners` | exit 0, `… governed=0 unregistered=7 registry=ok`; `registered` column present |

## Touched surfaces

- `kama-shokunin/.ufo/waves/round-79/w1/SC01Sources/sources-append.md` (new)
- `kama-shokunin/.ufo/waves/round-79/w1/SC01Sources/receipts/fetch-url.txt` (new)
- `kama-shokunin/.ufo/waves/round-79/w1/SC01Sources/receipts/listeners-before.txt` (new)
- `kama-shokunin/.ufo/waves/round-79/w1/SC01Sources/receipts/live-listener-build.txt` (new)
- `kama-shokunin/.ufo/waves/round-79/w1/SC01Sources/receipts/census-after.txt` (new)
- `kama-shokunin/.ufo/waves/round-79/w1/SC01Sources/receipts/listeners-after.txt` (new)
- `kama-shokunin/.ufo/waves/round-79/w1/SC01Sources/receipts/local-tree-readme.txt` (new)
- `kama-shokunin/.ufo/waves/round-79/w1/SC01Sources.md` (this report, new)
- Scratch: `$S/fix/kama-shokunin-79/` (symlink fixture + patched registry copies) — deleted before yield.
- No tracked lane file was edited; no git write; no `corpus/SOURCES.md` change; nothing outside the
  lane and my seat dir.

## Out of scope / not done by design

- Appending the row to `corpus/SOURCES.md` — the L1 appends.
- Admitting the row in `corpus/QUALITY.md`, and writing the knowledge entry — other seats.
- Running `tools/pre-report-gate.py` in scored mode — L1 only.
- Deciding whether the counter's informational live-leg difference (8 endpoints / 7 ports vs the
  standalone probe's 7) is drift or a counting difference — reported verbatim, not adjudicated.

## Findings for the L1

1. **Ordering constraint, and it was honoured:** the row and
   `corpus/knowledge/unregistered-listener-census.md` must land together. In the fixture the row
   alone flips the lane from `ok` (exit 0) to `E11 S553` (exit 1); nothing else about the row fails
   validation. The L1 committed both at `d6408a63`, and the registry there validates `kama ok`
   (exit 0, 105 W04, no `S553` finding) with `rows 293`, `tier.A 278`, `status.mined 264`.
2. **The committed row is the L1's variant, not this draft.** Same id `S553`, same URL, same
   `sha256` in the anchor cell, same `status`/`opened`/`recheck`/`used-by`; the source label, scope
   tail ("not served-identity normalization (S001/S016/S526) and not model quality"), anchor suffix
   and `teaches` cell are the L1's wording. Every frozen fact of this seat's Gate (HTTP 200,
   135608 bytes, `8fd5abde…`, line-2227 quote) reappears in the committed row and in the lesson
   §Gate; nothing in the committed row contradicts the measurement. Draft-vs-committed cell diffs
   are recorded in the append block, not applied to the registry.
3. **Anchor wording:** the README at this commit has no heading containing "Router mode". The
   frozen anchor is still *locatable* (its line 2227 is exact); if the L1 needs a literal heading,
   the honest one is `### GET /models: List available models` at line 2197. The frozen text should
   not be rewritten to hide this; it is recorded here instead.
4. **Pin substantiated three ways, not assumed:** the live listener at `127.0.0.1:1234` answers
   `build_info=b1-39febd2`; `~/src/llama.cpp` is at HEAD `39febd2adb947b70da35e95f9351b3bf58ad170a`
   with an unmodified `tools/server/README.md` whose sha256 (`8fd5abde…`) equals the fetched bytes.
   The source text, the tree and the running build agree. That same listener is the round's
   *unregistered* subject; this is identity evidence, never a governance claim.
5. **Full `status.value` set, including the lesson's extra:** `loaded`, `unloaded` (with
   `failed`/`exit_code`), `loading`, `sleeping` (lines 2206–2296), `downloading` (line 2299) and
   `incomplete` (lines 2314–2319, 2470). The lesson §Gate's "downloading and incomplete" is grounded
   in the fetched text — my draft's teaches cell listed one value fewer.
6. `measured/control/` is empty on disk (the plan cites `measured/control/c3-base-probe.out`); that
   control receipt was not produced pre-freeze as the plan's text expects. Not this seat's file —
   recorded as observed.
7. **C3 after-line observed green:** the counter prints the frozen target shape with the fixture
   port filled (`port=40299 … rows=35`, exit 0); the probe's summary carries
   `governed=0 unregistered=7 registry=ok` and a `registered` column (26 × `-`, 7 × `no`, 0 ×
   `yes`). Timeline: the L1 committed the knowledge entry at `06:47`; the census tool landed at
   `06:48:12`; this seat measured both legs after that. The counter's live leg (`model_endpoints=8
   … unregistered=8`) and the standalone probe (`model_endpoints=7 … unregistered=7`) disagree by
   one endpoint; both are reported verbatim and neither is used as a gate here.
8. Tooling: no installs or upgrades were needed or made this seat (no pacman, `uv`, npm or binary
   download).

## Artifact paths (absolute)

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-79/w1/SC01Sources/sources-append.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-79/w1/SC01Sources/receipts/fetch-url.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-79/w1/SC01Sources/receipts/listeners-before.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-79/w1/SC01Sources/receipts/live-listener-build.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-79/w1/SC01Sources/receipts/census-after.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-79/w1/SC01Sources/receipts/listeners-after.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-79/w1/SC01Sources/receipts/local-tree-readme.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-79/w1/SC01Sources.md`

Checks the main agent may re-run: `bash scripts/sources-census.sh validate --root <fleet> kama`
(observed `ok`, exit 0, 105 W04 at `d6408a63`) and `python3 tools/round79-unregistered-census.py
--repo .` (observed exit 0 at `f7442dea`).
