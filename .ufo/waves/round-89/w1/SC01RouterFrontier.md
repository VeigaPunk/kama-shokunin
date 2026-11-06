# SC01RouterFrontier — frontier recon on lane-owned b12177 router children

Seat: SC01RouterFrontier (leaf, no delegation). Lane: kama-shokunin. Wave: round-89 w1. Scope: (1) router `aliases`, (2)
`--models-memory-margin`, (3) per-request `?autoload=false`. Read-only in the lane except this out dir and this report.

## Scope

- Revisions: master `21b9e36d6192e0a691550b32e0e6c38412227f4c` (C2 M2); probe blob `39584b81e80fd83c498c38df86ec99940c8a131b`
= C1 M `4f9eacf720aa59ed806b31b758571e364658179b`. Base B `56174a1fa6a27faa91d3664ef4730b48dd3149c0` blob `5eb1368d…`. -
Binary `~/.local/opt/llama-b12177/llama-server` sha256 `ba272ee3446d9b98c9150c79667e6a8b217f25ee58ce0c6156cc96d2b5b362b0`
(matches the pin); model `~/.cache/kama-shokunin/models/stories260K.gguf`. Sources @ `6c01da62`: S583 `server-models.cpp`;
plus `README.md`, `server-models-sched.{h,cpp}`, `common/arg.cpp`, `server-http.cpp`. - Children lane-owned on free ports,
killed by process group. Port 1234 touched only with `GET /v1/models`/`GET /props`; no tools installed or upgraded (nothing
to record).

## Commands and outputs

``` $ git -C <scratch>/wt checkout --detach 21b9e36d6192e0a691550b32e0e6c38412227f4c   # HEAD now at 21b9e36d $ git rev-parse
21b9e36d:tools/kama-probe.sh -> 39584b81e80fd83c498c38df86ec99940c8a131b $ sha256sum ~/.local/opt/llama-b12177/llama-server
ba272ee3446d9b98c9150c79667e6a8b217f25ee58ce0c6156cc96d2b5b362b0 $ ~/.local/opt/llama-b12177/llama-server --list-devices
# exit 0 Available devices: (none)                                # CPU-only build: no cuda/vulkan/hip libs in the dir, ldd
shows none $ curl -sS http://127.0.0.1:1234/props   # exit 0, GET only
{"role":"router","max_instances":2,"models_autoload":true,...,"build_info":"b1-39febd2",...} $ curl -sS
http://127.0.0.1:1234/v1/models  # GET only; 4 entries, all status "unloaded", aliases [] on each ```

Five live harnesses (`frontier.py`…`frontier5.py`, in the out dir) ran against lane-owned children; all 61 records (every
HTTP answer, probe verdict/reason, listing body, log tail) are in `frontier-evidence.jsonl`, the decisive label→result lines
in `frontier-evidence.txt`. Headlines: an alias entry `kama-alias-x` is served with HTTP 200 (A-completion-kama-alias-x)
while `probe check --expect kama-alias-x` prints **exit 2 MODEL_MISMATCH / served-id-mismatch**
(A-probe-expect-kama-alias-x); the 500 for an alias request names the canonical id (J-completion-alias-unloadable);
`--models-memory-margin 512` reports `memory.status:"measured"` for the good model and `"failed"` for the broken one while
the C1 rule still fires (H-probe-expect-gone → `router-model-missing`, H-probe-expect-badhdr → `router-model-invalid`);
`?autoload=false` turns the 500 into a 400 `model is not loaded` for the *unloadable* model
(C-completion-badhdr-autoload-false) and `?autoload=true` makes a `--no-models-autoload` router answer 200
(F-m1-autoload-true).

Source cross-checks (pinned `6c01da62`): S583 `server-models.cpp:2169` emits `{"aliases", meta.aliases`; `:1949-1963`
`router_validate_model` resolves an alias via `get_meta` (`:1114-1118`) and sets `name = meta->name` (canonical), then
`!models_autoload && !is_running()` → 400 `model is not loaded`; `:1968-1975` `is_autoload` lets `?autoload=true|false`
override `params.models_autoload`; `:1641` throws `"model name=" + name + " failed to load"` with the **canonical** name.
`server-models-sched.cpp:312-314` `memory_enabled()` ⇔ `models_memory_margin > 0`; `:578-593` `deficit()` skips non-`device`
rows ("host" skipped, host RAM unlimited); `README.md:2181` "On a build without GPU devices the memory limit has no effect";
`README.md:2165` documents the per-request `?autoload`.

## Findings

**F1 — DEFECT (false red on a healthy endpoint): the probe cannot resolve a router alias; `--expect <alias>` is graded
`MODEL_MISMATCH`.** The router lists an alias per entry (`server-models.cpp:2169`) and serves it — `POST
/v1/chat/completions` with `"model":"kama-alias-x"` answers **HTTP 200** (A-completion-kama-alias-x, N-completion-alias) —
yet `check --port P --expect kama-alias-x` → **exit 2, MODEL_MISMATCH, reason `served-id-mismatch`**
(A-probe-expect-kama-alias-x, N-probe-expect-alias). Cause: `tools/kama-probe.sh:410-425` `model_matches` compares the
expected id only against the served **ids** (`served_ids`, `:400-407`, greps `"id" keys); the `aliases` array in the same
body is never consulted — exactly the false red C1's rule tries to avoid ("a false red is worse than the known false green").
Aliases exist only via a preset key (`alias = ...` in the preset INI, or a `[<model-id>]` preset section for a models-dir
model); a router-level `--alias` creates none (B-models-list `aliases: []`; B-completion-kama-alias-cli → 400 not found). The
operator's live router has no aliases on its four entries, so the C1/C2 counters and the operator harm baseline are
unaffected today — the defect is latent and bites any router using a preset alias. The C1 file-state rule is right: it still
fires for the canonical id of an alias-bearing entry (E-probe-expect-kama-alias-model → MODEL_UNLOADED
`router-model-missing`).

**F2 — NOTE (C2 depth gap): a wire answer captured through an alias carries the canonical id, so the C2 `<id>` substitution
cannot bind such a receipt.** The 500 names the **canonical** model, not the id the client sent: requesting
`"model":"kama-alias-bad"` for a preset entry `canon-bad` answers `model name=canon-bad failed to load`
(J-completion-alias-unloadable). The C2 counter substitutes `<id>` with the **requested** model
(`tools/round89-signature-rows.py`: `want = message.replace("<id>", str(request["model"]))`), so an alias-captured receipt
leaves the row unbound. Machine-proven on a scratch fixture repo: the committed receipt binds `rows=8 bound=8 unbound=0`
(exit 0); the same receipt with the 500 captured through an alias binds `rows=8 bound=7 unbound=1` (exit 1, `SIGNATURE_ROW
unbound POST /v1/chat/completions 500 'model name=<id> failed to load'`). The committed receipt uses canonical ids, so C2 is
unaffected; the gap is the table's implicit assumption that `<id>` is echoed verbatim. Note the asymmetry: `POST
/models/unload`, `POST /models/load` and the 400 `model not found` **do** echo the requested alias (I-unload-unknown-alias,
I-load-unknown-alias, C-completion-unknown-autoload-false); only the 500 substitutes the canonical name.

**F3 — NOTE (blind spot): `?autoload=false` makes an unloadable file indistinguishable from a healthy unloaded model, and it
flips the C1 oracle's HTTP code.** On an autoload router the 500 `failed to load` is what distinguishes "the file cannot
load" from "merely not loaded". With `?autoload=false` the router never attempts the load and answers **400 `model is not
loaded`** for the *unloadable* `badhdr` as well as for the healthy `m1` (C-completion-badhdr-autoload-false,
C-completion-m1-autoload-false). Both map to `MODEL_UNLOADED` in the frozen oracle, so the C1 verdict class is unchanged —
but the C2 row "500 `model name=<id> failed to load`" has no counterpart for a `?autoload=false` client, whose diagnostic is
the 400 row. Conversely `?autoload=true` on a `--no-models-autoload` router answers **200** and loads the model
(F-m1-autoload-true), so a client-side `?autoload=true` defeats the server flag. The probe sends no `?autoload`, so the C1
cells are unaffected; but a consumer pinning `?autoload=false` sees 400 on a router the probe grades `MODEL_OK`
(L-wire-autoload-false-valid vs L-probe-autoload-valid = MODEL_OK `router-unloaded-autoload`): a probe-vs-consumer
divergence, not a probe bug.

**F4 — NOTE (operability): `--models-memory-margin` is inert on this CPU-only build yet adds a measurement child per model.**
The b12177 build has no CUDA/Vulkan/HIP (`--list-devices` → `(none)`), so per `README.md:2181` and
`server-models-sched.cpp:578-593` (host rows are not `is_device()`, host RAM assumed unlimited) the margin cannot cause an
unload: `deficit()` is always empty. Observed: the router still measures and reports `memory:{"status":"measured",...}` with
a single `kind:"host"` device, and the model loads and serves normally (D-completion-margin → 200). The real cost is a
**measurement child per model**: the router spawns a short-lived `llama-server` per model to read its metadata
(`server-models-sched.cpp:316-318`, `:382-396`), which for a broken GGUF **fails to load** and is reported as
`memory.status:"failed"` while the entry stays `unloaded` (D-models-list-margin, H-models-list). So: (a) the margin is not
free on CPU-only hosts — it multiplies short-lived model opens at startup and on every reload, and the measurement child does
open the broken file; (b) the measurement failure does **not** set `failed:true` (H-models-list: `failed=None`,
`exit_code=None`), so the C1 file-state rule still fires under the margin (H-probe-expect-gone → `router-model-missing`,
H-probe-expect-badhdr → `router-model-invalid`).

**F5 — NOTE (harm-surface check, positive): the C1 file-state rule does not misfire on the operator's real model files,
including its `--mmproj` paths.** The operator router lists four `unloaded` entries with absolute `--model` paths and, for
`LFM3-Omni-2B` and `LFM3-VL-2B`, absolute `--mmproj` paths; all six files exist and are regular files. The probe's own header
checker (extracted verbatim from `tools/kama-probe.sh:487-666`) over those six files returns `ok` for every one — no
`router-model-invalid` false red. This matches the operator harm baseline (`measured/harm-M.out`: four × `MODEL_OK
router-unloaded-autoload`). The operator router runs a different build (`build_info "b1-39febd2"`); `status.args[0]` is
local, so the C1 rule applies to it too, grading `MODEL_OK`.

## Deliverables

- `.ufo/waves/round-89/w1/out/SC01RouterFrontier/frontier-evidence.jsonl` — 61 records (every HTTP answer, probe
verdict/reason, listing body, log tail); `frontier-evidence.txt` — the decisive label→result lines. -
`.ufo/waves/round-89/w1/out/SC01RouterFrontier/frontier.py`…`frontier5.py` — the five harnesses (lane-owned children on free
ports, killed by process group, `TMPDIR`-driven, no hardcoded `/tmp`); this report is the third file.

No lane tracked file was modified; scratch `/fast/scratch/hyaku/kama-r89/SC01RouterFrontier` removed after copying receipts;
no stray `llama-server` child left (only the operator's own 1234 router).

VERDICT: partial — the alias surface is a real probe false red (F1) and the C2 `<id>` substitution cannot bind an alias-captured receipt (F2); `--models-memory-margin` and `?autoload=false` produced no harm to C1/C2 but two documented blind spots (F3, F4).
