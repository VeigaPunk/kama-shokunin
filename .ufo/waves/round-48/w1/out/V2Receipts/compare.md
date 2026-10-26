# V2Receipts — round-48 v5 live receipts: audit + round-47 v4 comparison

**Verdict: no defect.** All three v5 receipts (`receipt-1..3.json`) satisfy every frozen receipts-leg condition of `tools/round48-live-replay-v5-audit.py` (schema v5, outcome pass, 11/11 checks evaluated and passed, `build_info` `b11909-caa8191df`, provenance equal to the frozen asset/model/commit/digests, `provenance.verified` at `record` with all three digests, `teardown.log_path` null), are byte-identical to the blobs committed at the lane build commit `380bcdff9c8af06997c482f6eb03db926a794a2b`, and differ from the round-47 v4 receipts **only** in the ways the v5 schema intends (pinned model URL + commit, record-time `verified` block, round alias, tool digest) plus instance fields. The scratch `model.path` is ephemeral but is **not** a round-46-D5-class dead pointer: the durable locator (pinned URL + sha256, verified at record time) is in the receipt and every counter leg re-acquires from it, never from the path.

All paths below are relative to `/home/vgpnk/Projects/shokunin/kama-shokunin` unless absolute. Receipt copies cited here are in `.ufo/waves/round-48/w1/out/V2Receipts/` (v5) and `.ufo/waves/round-48/w1/out/V2Receipts/round-47/` (v4).

## 1. Objects audited

| file | sha256 |
|---|---|
| `.ufo/waves/round-48/c2/live/receipt-1.json` | `164a4d9d232853deb35a64d9127382c7bb8ba8536b99f02c850eb2062f291344` |
| `.ufo/waves/round-48/c2/live/receipt-2.json` | `4a0041b3c10894cf28a80b5bb3690526af0504e4ab85b081455e3c7b5d450530` |
| `.ufo/waves/round-48/c2/live/receipt-3.json` | `7ab106135542a77986d547885363c79a2d0b1575a8b0d897a20adabb241dcb81` |
| `.ufo/waves/round-48/c2/live/install.txt` | `b029cd70e42fe53fe1a059387af40aadb399815f20fc3f901f06554941aaa666` |
| `.ufo/waves/round-47/c2/live/receipt-1.json` | `a4caf311ac030ce3c50373d7f2c37aa62895bcec5deb93bfa8bbd24e0706e80d` |
| `.ufo/waves/round-47/c2/live/receipt-2.json` | `d36d29417ce5cf7e2f9d1424a281e54b6ec44575f2b67be1acb3d8dec349eb49` |
| `.ufo/waves/round-47/c2/live/receipt-3.json` | `f3f961517711a18ccfce7db837d116e06b7a01ab046f404c95e83c64b2542b68` |

Committed-bytes check — `git show 380bcdff…:.ufo/waves/round-48/c2/live/<f> | sha256sum` equals the worktree file for receipt-1/2/3 and install.txt (`164a4d9d…`, `4a0041b3…`, `7ab10613…`, `b029cd70…`): the audited files are the committed bytes at the build tip.

## 2. Per-receipt audit against the frozen receipts leg

Programmatic check of every condition in the counter docstring's `receipts` leg (round48-live-replay-v5-audit.py:56-66), for each of the three receipts:

| condition | r1 | r2 | r3 |
|---|---|---|---|
| schema `kama-llamacpp-live/v5` | OK | OK | OK |
| outcome `pass` | OK | OK | OK |
| ≥10 evaluated checks, all passed | 11/11 | 11/11 | 11/11 |
| `provenance.server.asset_url` = frozen b11909 asset URL | OK | OK | OK |
| `provenance.server.asset_sha256` = `bf94332a…e695b` | OK | OK | OK |
| `provenance.server.member` non-empty (`llama-b11909/llama-server`) | OK | OK | OK |
| `provenance.model.url` = frozen pinned URL (`/resolve/499bc882…/`) | OK | OK | OK |
| `provenance.model.commit` = `499bc8821c6b12b4e53c5bffcb21ec206f212d81` | OK | OK | OK |
| `provenance.model.sha256` = `model.sha256` = frozen `270cba1b…256d` | OK | OK | OK |
| `provenance.verified.at` = `record` | OK | OK | OK |
| `verified.archive_sha256` = frozen asset digest | OK | OK | OK |
| `verified.member_sha256` = `server.sha256` = `35ac50fb…7ff0` | OK | OK | OK |
| `verified.model_sha256` = frozen model digest | OK | OK | OK |
| `build_info` starts `b11909-` (`b11909-caa8191df`) | OK | OK | OK |
| `teardown.log_path` null or committed repo-relative | null | null | null |

Result: `ALL-RECEIPTS-LEG: PASS`. The 11 check ids, identical in v4 and v5: `health_ready, models_alias_id, models_owned_by_llamacpp, metrics_not_enabled, props_alias, probe_model_ok, probe_mismatch, teardown_graceful, teardown_port_closed, loading_envelope_graded, model_unchanged` — all `evaluated: true, passed: true` in all six receipts.

`build_info` `b11909-caa8191df` matches the frozen release identity `b11909 = caa8191df159f764fb0160e3d2fc6be008948aee` (first 10 hex chars), and appears in both `captures.props.fields.build_info` and `checks[4].observed.fields.build_info`.

Run hygiene: the three v5 runs are sequential, non-overlapping (started 22:26:23.509Z / 23.935Z / 24.331Z; ended 23.879Z / 24.273Z / 24.676Z; r1 ends before r2 starts, r2 before r3), distinct ports (33779, 41891, 45023) and distinct child pids (611093, 612878, 615051).

## 3. Tool and probe digests recorded in the receipts

- v5 `tool.sha256` `1e5ea0fde985367d9d6335eae3825068e64063f032bbbc59fc8909e7b7f9a6d2` = `git show 380bcdff…:tools/kama-llamacpp-live.py | sha256sum`. ✓
- v5 `probe.sha256` `36b64978ee3a3aa29e1b73f04ca5c7ad04a9aee880e7032abfd894fa7b3a29d3` = `git show 380bcdff…:tools/kama-probe.sh | sha256sum`. ✓
- v4 `tool.sha256` `65301a3c76f925bf3316673d3774269f6d93ca22f4ccdb7c7139e6826b8ae65d` = `git show 33e0058…:tools/kama-llamacpp-live.py | sha256sum` (round-47 base). ✓
- The v4→v5 tool change is exactly the v5 feature: `git diff 33e0058… 380bcdff… -- tools/` = 134 insertions in `kama-llamacpp-live.py` (the four provenance flags now required together, https-only, pinned `/resolve/<40-hex>/` model URL, `--server-archive` selecting v5, `verify_archive_member()` hashing archive + member before the server starts, `provenance.model.commit` + `provenance.verified`) and 164 in `kama-live-replay.py` (v5 acceptance, stable projection, `--compare`).

## 4. Same binary, same model bytes

- Server: all six receipts record `server.sha256` `35ac50fb2cfd9c4f363720bb88ac17e799716595802c9105103593977d8d7ff0` (the round-47 install at `/home/vgpnk/.local/opt/llama-b11909/llama-server`; round-48 install.txt: "no new install this round").
- Model: I hashed both copies on disk — the v5 run input `/fast/scratch/hyaku/kama-r48/L1/live/stories260K.gguf` (still present at audit time) and the v4 run input `/home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf` — both `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d` = the frozen digest. Same 1,185,376-byte GGUF in both rounds; every stable capture that depends on model bytes is therefore expected to agree (it does, §6).
- Pin evidence: `.ufo/waves/round-48/c2/hf-revision-499bc882.txt` records `x-repo-commit: 499bc882…d81`, `x-linked-etag: "270cba1b…256d"`, `x-linked-size: 1185376`; `corpus/SOURCES.md:245` (S492, new at this tip) registers the pinned resolve URL with the same quote.

## 5. v4 → v5 receipt diff (what differs and why)

Recursive leaf diff of each v4 receipt against its v5 counterpart: **43 / 42 / 45** differing leaves (r1/r2/r3). Every leaf falls in one of these classes:

| class | fields | why |
|---|---|---|
| schema bump (intended) | `schema` v4→v5 | v5 = v4 + record-time-verified provenance |
| D6 fix — pinned model URL | `provenance.model.url` `…/resolve/main/…` → `…/resolve/499bc882…/…` | round-47 closure D6: `main` is a moving ref |
| D3 fix — new provenance fields | `provenance.model.commit` absent→`499bc882…`; `provenance.verified` absent→`{at: record, archive_sha256=bf94332a…, member_sha256=35ac50fb…, model_sha256=270cba1b…}` | record-time hashing of archive, member and model before the server starts |
| round naming | `alias`, `argv[4]`, `probes[*].expect`, `props.fields.model_alias`, `checks[1]/[4]` observed, models body `name`/`model`/`data[0].id`/`aliases` | `kama-r47-live` → `kama-r48-live` |
| run input location | `model.path`, `model.arg`, `argv[2]`, teardown `log_lines[0]` | v4: persistent host cache copy; v5: fresh fetch into the L1's scratch (install.txt: "removed after the round") |
| tool version | `tool.sha256` `65301a3c…`→`1e5ea0fd…` | the v5 tool itself |
| instance fields | `port` (37903/44883/39739 → 33779/41891/45023), `child_pid`, `started_utc`/`ended_utc`, `transitions[*].repeats`/`t_ms`, `loading_503.t_ms`, `checks[9].observed.total_503_responses` (18/34/29 → 23/42/25), `loading_503_bodies[0].repeats` (17/33/28 → 22/41/24), teardown `log_lines` timings, `captures.props.headers.Content-Length` (2067→2064, §7) | per-run facts, excluded from the stable projection by design |

Nothing else differs: top-level key sets of v4 and v5 are identical (the schema adds only nested provenance fields), all 11 check ids and `documented_by` strings are byte-identical, and `captures.slots.body_sha256`, `captures.health.body_sha256`, `captures.metrics.status`, `loading_503.body_sha256`, `loading_envelope_exact`, teardown stable fields, `port_listener_ownership`, `port_refusal_set`, `pdeathsig`, `child_env_keys`, `source_binding` are all unchanged.

## 6. Capture by capture: v4 r1 vs v5 r1

| capture | v4 (r47#1) | v5 (r48#1) | stable? | why different |
|---|---|---|---|---|
| props status | 200 | 200 | same | — |
| props fields | alias `kama-r47-live`, slots 4, sleeping false, build `b11909-caa8191df`, n_ctx 256 | alias `kama-r48-live`, rest identical | **differs (alias only)** | round naming |
| props body_sha256 | `fb5e3e82…` | `f6cb10aa…` | no (instance) | random `media_marker` per server start + 3-byte-shorter `model_path` (§7) |
| props Content-Length | 2067 | 2064 | no (instance) | `model_path` 55→52 chars (§7) |
| slots | element_count 4, body_sha256 `6d345b40…` | identical | same | same model, same ctx → deterministic slot body |
| health | status 200, body `{"status":"ok"}`, sha `a29ee2b1…` | identical | same | — |
| models status | 200 | 200 | same | — |
| models body | alias r47 + `created` 1793053583-era | alias r48 + own `created` | **differs (alias)**; `created` instance | alias embedded in body; `created` is per-request epoch seconds |
| models projection (id\|owned_by, names) | `kama-r47-live\|llamacpp` | `kama-r48-live\|llamacpp` | **differs (alias)** | round naming |
| metrics | status 501 | 501 | same | `--metrics` not passed in both |
| loading envelope | exact, 503 body sha `baa09177…`, total 18, repeats 17 | exact, same 503 body sha, total 23, repeats 22 | same (envelope + body sha); counts instance | scheduler timing |
| teardown | rc 0, sigterm T, sigkill F, port_refuses T, log_path null, term_wait 3 ms | identical | same | — |
| teardown log_lines | 3 lines, timings + cache path + port 37903 | 3 lines, timings + scratch path + port 33779 | no (instance) | log text is an instance fact |
| ownership | `child` | `child` | same | — |

## 7. Why `props.body_sha256` differs between receipts (and rounds)

The props capture stores only `fields` (5 keys) plus the raw body's sha256 (`kama-llamacpp-live.py:817-834`, `keep_body=False`). The raw `/props` body contains two per-run facts:

1. **`media_marker`** — `server-context.cpp:5253` (`{ "media_marker", get_media_marker() }`); `get_media_marker()` (upstream `server-common.cpp:189-197` at the pinned source commit `704366d7…`) returns `"<__media_" + random_string() + "__>"` from `std::random_device` unless `LLAMA_MEDIA_MARKER` is set — and the receipts' `child_env_keys` are exactly `HOME, LANG, PATH, TMPDIR` (no pin). So every server start gets a different marker → different body sha256 per receipt. This explains the within-round variance (v5 r1 `f6cb10aa…` vs r2 `83157a45…` vs r3 `b7dd8305…`; v4 likewise three distinct values).
2. **`model_path`** — `server-context.cpp:5247`; v4's cache path (55 chars) vs v5's scratch path (52 chars) = exactly the 3-byte Content-Length difference 2067→2064, constant within each round because all three receipts of a round share one model path.

The replay's stable projection deliberately compares `captures.props.fields`, not the raw body digest (`kama-live-replay.py:154-175`; docstring: "instance facts - ports, pids, times, paths, log text … - are excluded"), so this variance never fails a replay — confirmed empirically in §8.

## 8. `--compare` runs (the tool's own instance/stable separation, on real data)

`python3 <tip's tools/kama-live-replay.py> --compare A B` (tool bytes extracted from `380bcdff…`, sha256 `69837013…`; unchanged at the current lane head `b85783e8`):

| pair | result | exit |
|---|---|---|
| v5 r1 vs r2 | `compare match=True mismatches=0` | 0 |
| v5 r1 vs r3 | `compare match=True mismatches=0` | 0 |
| v5 r2 vs r3 | `compare match=True mismatches=0` | 0 |
| v4 r1 vs r2 | `compare match=True mismatches=0` | 0 |
| v4 r1 vs v5 r1 | 3 mismatches: `schema:v4->v5`, `projection:props` (model_alias), `projection:models` (alias) | 1 |
| v4 r1 vs v5 r2 | same 3 mismatches | 1 |

The three v5 receipts are mutually instance-only variants — exactly what the compare leg requires — and the v4↔v5 mismatches are precisely the intended schema + alias differences, nothing else.

Within-v5, the models body differs between receipts in exactly **one** leaf: `data[0].created` (1793053583 in r1 vs 1793053584 in r2/r3 — epoch seconds; r2/r3 started in the same second). The projection's `models` key takes `id|owned_by` and `models[].name`, so `created` is correctly treated as instance.

## 9. The model path: dead pointer?

`model.path` / `model.arg` / `argv[2]` = `/fast/scratch/hyaku/kama-r48/L1/live/stories260K.gguf` — the L1's scratch, which `install.txt` says is "removed after the round" and the operator reaper deletes. (At audit time the file still existed and hashed to the frozen digest; it is ephemeral by directive either way.)

**Not a round-46-D5-class defect:**

- Round-46 D5 (`corpus/lessons/round-46-verifier-spotcheck.md:141`) and the round-46 Mistakes "dead-pointer" row (`corpus/lessons/round-46.md:37`) are about `teardown.log_path` — a pointer to evidence with **no** alternative locator. That field is `null` in all six v4/v5 receipts, satisfying the rule the closure adopted (`tools/round47-live-replay-audit.py:172-178`: null, or repo-relative existing at tip; restated in the round-48 counter docstring).
- For run inputs the durability contract is the provenance block, which is exactly what v5 strengthened: `provenance.model.url` pinned to a 40-hex revision + `model.sha256` + `provenance.verified.model_sha256` hashed at record time, registered as source row S492 (`corpus/SOURCES.md:245`, with `x-linked-size: 1185376`). A later reader re-acquires from the URL, never from `model.path` — `kama-live-replay.py` downloads into `--work` and the counter's replay leg hashes the **rerun's** `model.path` inside its own scratch; no leg dereferences the original's path.
- The v4 receipts had the mirror-image weakness: a durable-looking cache path but a **moving** `resolve/main` URL (round-47 D6). v5 trades an ephemeral path for a pinned, digest-verified URL — the strictly stronger property for replayability.
- Corpus rows KQ66/KQ69 (`corpus/QUALITY.md:386,396`) are satisfied: URL + sha256 (+ member for the archive) are in the receipt; byte sizes are in committed sidecars (S039/S492 for the model, round-47 `install.txt` for the archive's 22475032 bytes).

Residual note (not a defect): `model.path`/`argv[2]` will not resolve for a later reader once the L1's scratch is reaped; the receipt is honest about this only via `install.txt`. If the lane ever wants path fields policed like `log_path`, that is a schema-v6 question, not a round-48 defect — the frozen contract does not require it.

## 10. `source_binding` verification (5 rows, receipt-1; identical in all six)

All five rows cite upstream commit `704366d76f8748cf9ad3df62a464bfcc8d1ae6ad`. I re-fetched the three cited files at that commit and recomputed:

| check | file | file_sha256 | span_sha256 (recomputed) |
|---|---|---|---|
| health_ready | tools/server/server-context.cpp L5288-5299 | OK (`dd1de0f2…`) | OK |
| loading_envelope_graded | tools/server/server-http.cpp L314-325 | OK (`24ede172…`) | OK |
| teardown_graceful | tools/server/server.cpp L529-534 | OK (`21439622…`) | OK |
| teardown_graceful | tools/server/server.cpp L519-523 | OK | OK |
| teardown_graceful | tools/server/server.cpp L575-590 | OK | OK |

Ancestry: `gh api repos/ggml-org/llama.cpp/compare/704366d7…caa8191df…` → `{"status":"ahead","ahead_by":154,"behind_by":0}` — the cited source commit **is an ancestor** of the built release commit `caa8191df…` (b11909).

At the release commit itself the spans for `server-context.cpp` and `server-http.cpp` are still present verbatim; the three `server.cpp` spans are not (the signal installation was refactored into `server_install_signal_handlers()`, L318-325, called at L652; `shutdown_handler` → `ctx_server.terminate()` now at L645-648; `start_loop()` at L671; `return 0` at L684). The documented semantics (SIGTERM installed, terminate unblocks the loop, graceful exit 0) all hold at `caa8191df`, and the receipt grounds the check by direct observation (`teardown.returncode = 0`). This citation convention is pre-existing — the v4 receipts cite the same commit — so it is an observation, not a round-48 finding.

## 11. Findings

**None in scope.** Every item of the seat assignment checks out: schema, outcome, 11 checks, `build_info`, provenance (url/sha256/commit/member/verified), teardown fields, model path, and the check-by-check / capture-by-capture v4 comparison. Observations with no action required this round: §9 residual note (ephemeral `model.path`, durable locator present) and §10 (upstream span drift at the release commit, semantics verified, pre-existing convention).

## Appendix — commands and exit codes

```
S=/fast/scratch/hyaku/kama-r48/V2Receipts
git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin $S/lane          # read-only use
git -C $S/lane show 380bcdff9c8af06997c482f6eb03db926a794a2b:tools/kama-live-replay.py > $S/replay-at-tip.py
python3 $S/replay-at-tip.py --compare <A> <B>          # §8 table; exits 0/0/0/0/1/1
python3 - <<EOF                        # §2 receipts-leg check → ALL-RECEIPTS-LEG: PASS
python3 - <<EOF                        # §5/§6 recursive diffs; §7 models-body single-leaf diff
sha256sum /fast/scratch/hyaku/kama-r48/L1/live/stories260K.gguf \
          /home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf   # both 270cba1b…256d
curl -sfL https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d7…/tools/server/{server-context,server,server-http}.cpp
                                        # §10 file_sha256 + span_sha256 recomputed, all OK
curl -sfL …/caa8191df…/tools/server/…   # §10 span presence at the release commit
gh api repos/ggml-org/llama.cpp/compare/704366d7…caa8191df…   # behind_by=0 → ancestor
```
