# P02 — alias, copy and case identity on live Ollama v0.40.11 (round 60, wave w1)

Advisory seat output. No lane source was edited; every capture is my own lane-owned server, killed by PID in
the same shell invocation that started it. Raw bodies are in `captures.jsonl` (clean run) and
`captures-run1.jsonl`, `captures-run2.jsonl`, `captures-case.jsonl`; replay exits in `replay-matrix.jsonl`
and `replay-reasons.json`; drivers `capture2.py`, `replay.py`, `run3.sh` are copied here for reproducibility.

## Provenance and environment

| item | value |
|---|---|
| server | `~/.local/opt/ollama-v0.40.11/bin/ollama serve` |
| binary sha256 | `b0a4becfaf872e3ad5d2e9051244e0dfe55409f03d6e2cd9bd9c34400e201b4c` |
| `/api/version` | `{"version":"0.40.11"}` (capture #1) |
| fixture | `~/.cache/kama-shokunin/models/stories260K.gguf`, sha256 `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d` |
| isolation | `env -i`, `HOME`/`OLLAMA_MODELS` inside my scratch, `OLLAMA_NO_CLOUD=1`, `OLLAMA_NOPRUNE=1`, CUDA/HIP/Vulkan devices `-1` |
| ports | ephemeral loopback only: 33657 (run1), 51163 (run2), 52453 (run3, `captures.jsonl`), 48039 (case re-probe), 44441 (case probe), 39039 (digest probe); never 8080/34113/11434 |
| teardown | every port re-probed `refused` after its PID was killed; `server_alive=0`; one inline-launched server survived its shell and was killed by exact PID 2334804, another by 2462173 after identification by its `HOME` env, never by process name |
| lane edits | none; this out dir and `.ufo/waves/round-60/w1/out/P02AliasAndCopy.md` only |
| date | 2026-10-27 |

Runs: run1 = 3 names + cp + 33 captures (headers lost to a key-case bug in the driver; bodies intact, generate
ran 20480 tokens — see F6); run2 = repeat on a store already holding run1 manifests (9 names, all digest
`8cf91c71…`); run3 = clean five-name store, the primary evidence; case probe = case-variant `cp` on a fresh
store; digest probe = same GGUF imported from a renamed copy.

## Raw captures — clean run (`captures.jsonl`, sha256 `9203adac75c246b5928d7137ca4280c20f640f26e8109ff031a644de84e726fe`)

| # | route (method) | status | content-type | body excerpt | reading |
|---:|---|---:|---|---|---|
| 1 | `/api/version` (GET) | 200 | application/json; charset=utf-8 | `{"version":"0.40.11"}` | server version string |
| 2 | `/api/tags` (GET) | 200 | application/json; charset=utf-8 | `{"models":[]}` | fresh store |
| 3 | `ollama create kama-p02b-43f9adcc -f …/Modelfile-captures.jsonl.txt` (CLI) | - | - | `exit=0 … copying file sha256:270cba… using existing layer sha256:270cba…` | first import; GGUF stored as layer blob |
| 4 | `ollama cp kama-p02b-43f9adcc kama-p02b-43f9adcc-alias` (CLI) | - | - | `exit=0 stdout="copied 'kama-p02b-43f9adcc' to 'kama-p02b-43f9adcc-alias'\n"` | cp of unqualified source/target |
| 5 | `ollama create kama-p02b-43f9adcc-b -f …` (CLI) | - | - | `exit=0 … using existing layer sha256:270cba…` | second import, blob reused, new manifest |
| 6 | `ollama cp kama-p02b-43f9adcc P02UPPER` (CLI) | - | - | `exit=0 … to 'P02UPPER'` | case probe inside the main run |
| 7 | `ollama cp kama-p02b-43f9adcc:latest kama-p02b-43f9adcc-q` (CLI) | - | - | `exit=0 … to 'kama-p02b-43f9adcc-q'` | qualified source accepted |
| 8 | `/api/tags` (GET) | 200 | application/json; charset=utf-8 | `{"models":[{"name":"kama-p02b-43f9adcc-q:latest","model":"…-q:latest","size":1185492,"digest":"8cf91c71…"},…5 entries…]}` | five names, one digest |
| 9 | `/v1/models` (GET) | 200 | application/json | `{"object":"list","data":[{"id":"kama-p02b-43f9adcc-q:latest",…,"owned_by":"library"},…5…]}` | ids equal tags names |
| 10 | `ollama list` (CLI) | - | - | `exit=0` five rows, ID `8cf91c7109e7` | short-id form is the same manifest digest prefix |
| 11 | `/api/show` (POST, `kama-p02b-43f9adcc`) | 200 | application/json; charset=utf-8 | `{"modelfile":"…# FROM kama-p02b-43f9adcc:latest\n\nFROM …/blobs/sha256-270cba…","template":"{{ .Prompt }}","details":{"parent_model":"stories260K.gguf",…}}` | body names the canonical `:latest` form |
| 12 | `/api/show` (POST, `…:latest`) | 200 | application/json; charset=utf-8 | same shape | qualified request, same body |
| 13–16 | `/api/show` (POST, `-alias`, `-alias:latest`, `-b`, `-b:latest`) | 200 | application/json; charset=utf-8 | same shape, canonical name in the modelfile header | alias/b show resolve, no digest field |
| 17–18 | `/api/show` (POST, `P02UPPER`, `P02UPPER:latest`) | 200 | application/json; charset=utf-8 | `# FROM P02UPPER:latest` | uppercase stored, uppercase resolves |
| 19–20 | `/api/show` (POST, `p02upper`, `p02upper:latest`) | 200 | application/json; charset=utf-8 | `# FROM P02UPPER:latest` | lowercase request resolves to the uppercase entry and is echoed canonicalized |
| 21 | `/api/show` (POST, `KAMA-P02B-43F9ADCC`) | 200 | application/json; charset=utf-8 | `# FROM kama-p02b-43f9adcc:latest` | uppercase request for a lowercase-stored name resolves |
| 22–23 | `/api/show` (POST, `P02NoSuchModel`, `kama-p02b-missing:latest`) | 404 | application/json; charset=utf-8 | `{"error":"model 'P02NoSuchModel:latest' not found"}` | absent names 404, and the error text itself completes `:latest` |
| 24 | `/api/ps` (GET) | 200 | application/json; charset=utf-8 | `{"models":[]}` | nothing loaded before generation |
| 25 | `/api/generate` (POST, `model=…-alias`, `stream:false`, `options.num_predict=4`) | 200 | application/json; charset=utf-8 | `{"model":"kama-p02b-43f9adcc-alias","response":" upon a time,","done":true,"done_reason":"length","eval_count":4,…}` | request echo is **unqualified**, unlike tags/ps |
| 26 | `/api/ps` (GET) | 200 | application/json; charset=utf-8 | `{"models":[{"name":"…-alias:latest","model":"…-alias:latest","size":6312427,"digest":"8cf91c71…","expires_at":…,"size_vram":0,"runner":"llamacpp"}]}` | exactly one entry, canonical `:latest` |
| 27 | `/api/generate` (POST, `model=…-b`) | 200 | application/json; charset=utf-8 | `{"model":"kama-p02b-43f9adcc-b","eval_count":4,…}` | same digest, different name |
| 28 | `/api/ps` (GET) | 200 | application/json; charset=utf-8 | name still `…-alias:latest`, digest unchanged, later `expires_at` | ps did **not** switch to `…-b` |
| 29 | `/api/generate` (POST, `model=p02upper`) | 200 | application/json; charset=utf-8 | `{"model":"p02upper","eval_count":4,…}` | lowercase accepted; echo preserves request case |
| 30 | `/api/ps` (GET) | 200 | application/json; charset=utf-8 | name still `…-alias:latest` | ps still sticky |
| 31 | `/api/tags` (GET) | 200 | application/json; charset=utf-8 | same five entries as #8 | generation changes no tag |
| 32 | `/v1/models` (GET) | 200 | application/json | same five ids as #9 | — |
| 33 | `ollama ps` (CLI) | - | - | `…-alias:latest  8cf91c7109e7  6.3 MB  100% CPU  2048  llamacpp  4 minutes from now` | CLI agrees with /api/ps |
| 34 | `ollama list` (CLI) | - | - | five rows, one ID | — |

Case probe (`captures-case.jsonl`, sha256 `4a7317cc45c1a9300439b16310e6cd430ef54adb2a645e3a94c3877003d876c2`):
`create caseprobe` → `cp caseprobe CASEPROBE` → tags still `["caseprobe:latest"]`; `create UPPERFIRST` →
`cp UPPERFIRST upperfirst` → tags `["UPPERFIRST:latest","caseprobe:latest"]`; show 200 for both cases of both
names; `generate {"model":"CASEPROBE"}` → 200, echo `CASEPROBE`, ps `["caseprobe:latest"]`; store dirs after
both cps: `caseprobe`, `UPPERFIRST` only.

Digest probe (`digest-probe.json`): same GGUF imported as `orig` from its original path gives digest
`8cf91c7109e77999ac0ae6e6eab27dfea00d9f83ffbe4559a3f26266e455c792`; imported as `renamed` from a byte-identical
copy named `stories260K-copy.gguf` gives `cef1ee2435e1edbbe6999691c93f78239d37e1d7dd411de53d37d595cf1bebc9`
(manifest 480 bytes vs 475; the only difference is `"from":"stories260K-copy.gguf"`).

## Store-level facts (read-only inspection of my scratch store)

- `models3/blobs/sha256-8cf91c71…` is a 475-byte manifest whose `sha256` equals the name `…/blobs/sha256-8cf91c71…`
  and equals the `digest` in `/api/tags` and `/api/ps`. Its single layer is
  `sha256:270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d`, size 1185376 = the GGUF file size.
- `tags.size` 1185492 = layer 1185376 + config blob 116; `ps.size` 6312427 is the resident size (`size_vram` 0).
- Each name is a symlink `manifests-v2/ollama.com/library/<name>/latest -> ../../../../blobs/sha256-8cf91c71…`;
  five names, one target, no second blob. `cp` therefore copies a manifest link, not weights.

## Replay through `tools/kama-ollama-evidence.py`

Exact form (paths were my scratch, since removed; capture rows are the `captures.jsonl` rows named):

```
python3 tools/kama-ollama-evidence.py --tags <tags-all.json> --ps <ps.json> --expect <NAME>
```

56 calls = 14 name forms × 4 ps states (`ps-before`, `ps-after-alias`, `ps-after-name2`,
`ps-after-upper-lower`), all recorded in `replay-matrix.jsonl` (sha256 `6f5fb19d…`). Distinct results:

| expect | ps-before | ps-after-alias | ps-after-name2 | ps-after-upper-lower |
|---|---|---|---|---|
| `NAME` (unqualified) | unknown 2 | unknown 2 | unknown 2 | unknown 2 |
| `NAME:latest` | available_not_loaded 1 | available_not_loaded 1 | available_not_loaded 1 | available_not_loaded 1 |
| `ALIAS` | unknown 2 | unknown 2 | unknown 2 | unknown 2 |
| `ALIAS:latest` | available_not_loaded 1 | **loaded_same_digest 0** | **loaded_same_digest 0** | **loaded_same_digest 0** |
| `NAME2:latest` | available_not_loaded 1 | available_not_loaded 1 | available_not_loaded 1 | available_not_loaded 1 |
| `P02UPPER:latest` | available_not_loaded 1 | available_not_loaded 1 | available_not_loaded 1 | available_not_loaded 1 |
| `p02upper:latest` | unknown 2 | unknown 2 | unknown 2 | unknown 2 |
| `KAMA-P02B-43F9ADCC:latest` | unknown 2 | unknown 2 | unknown 2 | unknown 2 |
| `P02NoSuchModel`, `kama-p02b-missing:latest` | unknown 2 | unknown 2 | unknown 2 | unknown 2 |

Case probe replay: `--expect caseprobe:latest` over its tags+ps → `loaded_same_digest` exit 0;
`--expect CASEPROBE:latest` over the *same bytes* → `unknown` exit 2 with reason
`no_tags_entry_matches_expected_name`, although `POST /api/generate {"model":"CASEPROBE"}` returned 200 on
that same server.

## Findings (each names the clause attacked and the observed command result)

**P02-F1 — every live listing canonicalizes to `:latest`, and the lane's "no `:latest` completion" policy
makes the server's own accepted name unclassifiable.**
Clause: `corpus/knowledge/ollama-evidence-replay.md:143-146` ("No trimming, basename, `.gguf` stripping,
`:latest` completion, case folding…"), and `SKILL.md:451` ("absent under that exact name").
Command: the 56 replay calls above; `curl -s /api/tags` rows #8/#31.
Observed: creating/copying/generating as `kama-p02b-43f9adcc` produces only `kama-p02b-43f9adcc:latest` in
tags/v1/ps, while `/api/generate` echoes the unqualified string. Every unqualified `--expect` is `unknown`
exit 2 in all four ps states; the qualified form classifies. The server itself accepts the unqualified form
on generate, show and cp (200/exit 0).
Reading: the rule is a deliberate policy, and the doc already says an actual server may resolve aliases
differently (`:241-244`) — so this is not a contradiction of a server claim, it is an unrecorded calibration
gap: a caller who names the model the way the server does gets exit 2 "expected model absent". Advisory: the
next amendment should state that tags/ps names are canonical `<name>:latest` and that replay callers must
use the listed form; no change to the classifier is implied by this observation alone.

**P02-F2 — the server's identity key is case-insensitive; the lane's case-sensitive rule is safe but yields
`unknown` for names the server resolves and loads.**
Clause: same clause, "case folding" / "case-sensitive identity"; `SKILL.md:450`.
Commands: `ollama cp caseprobe CASEPROBE` (exit 0), then `/api/tags` → `["caseprobe:latest"]` only;
`ollama cp UPPERFIRST upperfirst` (exit 0) → `["UPPERFIRST:latest","caseprobe:latest"]`;
`POST /api/show {"model":"p02upper"}` → 200 `# FROM P02UPPER:latest`;
`POST /api/generate {"model":"CASEPROBE"}` → 200, echo `CASEPROBE`, ps `caseprobe:latest`;
replay `--expect CASEPROBE:latest` → exit 2 `unknown`, `--expect caseprobe:latest` → exit 0.
Reading: a case-variant `cp` does not create a second entry — the request folds onto the stored spelling, and
the store holds one directory. [INFERENCE] the fold happens at name lookup, since no lowercase directory or
second tags entry exists. Consequence: a case-sensitive classifier cannot report a match for `CASEPROBE`,
which is correct (it must not match a different stored string) but reads to an operator as "model absent"
when the server would serve it. Advisory: record the server's case-insensitive resolution and the
"listing preserves the first stored spelling" fact beside the policy clause.

**P02-F3 — `/api/ps` lists exactly one entry and keeps the first-loaded alias; it does not follow the alias
that served the last request, and it never lists two names for one digest.**
Clause: `SKILL.md:451` (`available_not_loaded` … "another alias may list the same digest") and the
`loaded_same_digest`/`available_not_loaded` split at `:450-451`.
Commands: rows #25-#30; `/api/ps` after generating through ALIAS → `[ALIAS:latest]`; after generating
through NAME2 (same digest, 200, `eval_count=4`) → still `[ALIAS:latest]`; after a lowercase `p02upper`
generate → still `[ALIAS:latest]`; replay `--expect NAME2:latest` on tags+ps-after-name2 → exit 1
`available_not_loaded`, reasons `["tags_digest_local_no_matching_ps_entry", …]`.
Reading: the tool's verdict is correct for its own definition (the ps capture has no `NAME2` entry), and the
doc warns that absence at one sample must not be concluded either way. But the live demonstration is
sharper than the doc: the alias that was *just used to serve a 200 generation* is reported
`available_not_loaded` while an equal-digest alias is reported loaded. Advisory: any consumer of exit 1 must
read it as name-level absence from one snapshot, and a ps-name→requested-name join is invalid for
cp-aliases.

**P02-F4 — the digest in `/api/tags` and `/api/ps` is the manifest digest, not the GGUF digest, and it binds
the source filename.**
Clause: the digests-equal reading used by `loaded_same_digest` (`SKILL.md:450`) and the lane's habit of
pinning the GGUF sha256 (`registry/ollama-live-pin.tsv`).
Commands: `sha256sum blobs/sha256-8cf91c71…` = `8cf91c71…`, file size 475, layer `sha256:270cba…` size
1185376 = fixture size; digest probe: original filename `8cf91c71…`, renamed copy `cef1ee24…`, same bytes,
same layer.
Reading: equal digests across NAME/ALIAS/NAME2 hold because the manifests are byte-identical (same layer,
same template, same `from` filename), not because the weights alone determine the digest. Comparing a tags
digest to the pinned GGUF sha256 (270cba…) mismatches by design; a renamed GGUF changes the tags digest with
identical weights. [INFERENCE] `from` is the only differing manifest field between the two probe manifests,
observed by size and content. Advisory: state the manifest-vs-layer distinction where the lane treats digest
equality as correspondence.

**P02-F5 — id forms differ per surface.**
Clause: `SKILL.md:450-451` identity wording; `endpoint-identity.md` served-id normalization.
Commands: rows #8/#9/#11-#23/#25.
Observed: tags and ps use `name == model == "<name>:latest"`; `/v1/models` ids are the same strings with
`owned_by:"library"` and one shared `created` integer; `/api/generate` echoes the **request string verbatim**
(`kama-p02b-43f9adcc-alias`, `p02upper`, `CASEPROBE` — case preserved); `/api/show` carries **no name or
digest at all** (keys `capabilities, details, model_info, modelfile, modified_at, template,
template_source`), its modelfile header canonicalizes to `<name>:latest`, and its `details.parent_model` is
the source filename (`stories260K.gguf`) for every alias; its `modelfile` FROM exposes the server's store
blob path (`…/models/blobs/sha256-270cba…`).
Reading: show cannot be joined by identity; tags are the only name→digest map; a probe that compares a
generate echo to a tags name will mismatch on qualification and case. Advisory note only.

**P02-F6 — two capture traps observed (probe hygiene, not a lane defect).**
Commands: run1 `POST /api/generate {"model":"<alias>","prompt":"Once upon a time","num_predict":4}` (no
`stream`) → 200, 20471 NDJSON lines, `done_reason:"length"`, `eval_count:20480`, final `response:""`;
run3 `{…,"stream":false,"options":{"num_predict":4}}` → 200, one JSON object, 349 bytes, `eval_count:4`.
Reading: `num_predict` at the top level was not applied [INFERENCE: the difference is the `options`
nesting]; the default stream is NDJSON, so `json.loads(body)` fails on a streamed capture. A check that only
asserts `done:true` would pass on a 20480-token generation. `tools/kama-ollama-live.py:381-386` already uses
`stream:false` + `options.num_predict`, so C1 is unaffected; this is recorded so later live instruments do
not regress to the top-level form.

## Limits

One fixture model, one server version, CPU-only, one lane-owned server per run on an ephemeral loopback port,
all torn down before this report; every capture is historical after teardown, so nothing here is readiness,
liveness or registered-consumer health. `ps` stickiness is observed for three requests on one server
lifetime; eviction/reload order was not varied. The case-fold mechanism is [INFERENCE] over the store layout;
the measured facts are the entry counts and directory names. No lane registry, claim, counter or SKILL text
was modified; the advisory amendments are suggestions for the parent, not applied.
