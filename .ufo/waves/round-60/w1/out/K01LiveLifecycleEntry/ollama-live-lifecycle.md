source: S519 https://github.com/ollama/ollama/releases/tag/v0.40.11 (asset `ollama-linux-amd64.tar.zst`, 1508659610 bytes, plus the release's `sha256sum.txt` — its `./ollama-linux-amd64.tar.zst` line); S520 https://docs.ollama.com/faq §"How do I configure Ollama server?", §"How can I expose Ollama on my network?", §"Where are models stored?", §"How do I disable Ollama's cloud features?", §"How do I keep a model loaded in memory or make it unload immediately?"; S521 https://docs.ollama.com/import §"Importing a GGUF model" (a `FROM <file.gguf>`-and-`ollama create` scope extension of S013); S522 https://docs.ollama.com/api/openai-compatibility §"/v1/models" and §"/v1/models/{model}" Notes (a notes-only scope extension of S010); S523 own-work — `tools/kama-ollama-live.py` (lifecycle harness), `tools/kama-ollama-evidence.py` (offline captures replay), `registry/ollama-live-pin.tsv` (pins), `tools/round60-c1-counter.py` (independent verifier with 7 controls), committed receipt `.ufo/waves/round-60/live/receipt.json` sha256 `49d06600521ce766488f4941b24a3f245883bf6744d0b214c21201f24090c2a6`
verified-at: 2026-10-27, lane commit 8b9f3060966c22bede3094d748974caf041b4c33 — this seat re-opened the receipt committed there and re-derived every quoted value with `.ufo/waves/round-60/w1/out/K01LiveLifecycleEntry/receipt-facts.py` (exit 0); the release `sha256sum.txt` was re-fetched 2026-10-27 and its `./ollama-linux-amd64.tar.zst` line compared with the pin (`[ "$PIN" = "$REL" ]` exit 0); the counter was re-run at lane tip `11f2d667f8bd89d127a4fb81dab44007c4c86c7f` (exit 0, `met=True`)
recheck: `python3 tools/round60-c1-counter.py --repo <repo> --tip <rev>` — a fresh-nonce live run at `<rev>` plus the 7 controls; exit 0 with `met=True` re-verifies this entry's captures. on-release — re-run when the pinned Ollama release or the fixture GGUF changes.

# Ollama v0.40.11 live lifecycle — pinned binary, nonce import, six HTTP surfaces

## Claim

A digest-pinned **official Ollama v0.40.11 release binary** can be started as a
lane-owned child on an **unregistered loopback port** with a lane-owned `HOME`
and model store, importing the lane's fixture GGUF with `ollama create` under a
caller-supplied nonce, and then answers a fixed set of HTTP surfaces whose
**exact bytes** are capturable and replayable offline. In the observed run
(nonce `b61c98ad5747`, port 58921): `/api/version` reports `0.40.11`; the empty
store answers `/api/tags` and `/api/ps` with the same bytes `{"models":[]}`, and
`/v1/models` with `{"object":"list","data":null}` (a JSON **null**, not `[]`);
after `ollama create kama-b61c98ad5747` the model appears in `/api/tags` with a
manifest digest, `/api/ps` lists it **only after** one `/api/generate` with the
same digest, and the OpenAI-compatible route lists the **qualified**
`kama-b61c98ad5747:latest` id while `GET /v1/models/kama-b61c98ad5747` returns
the **unqualified** `kama-b61c98ad5747`. Listening on `/` and listing models is
therefore inventory, not residency: the loaded state is visible only on
`/api/ps`, and it is unloaded state that the pre-generation `/api/ps` body shows.

This is the lane's first **live non-llama.cpp engine** sample. It is one CPU run
of one version on one 293K-parameter toy model, and it says nothing about the
registered consumers.

## Source status — read before citing

S519–S523 are the rows this entry requires and they were **not yet open** at the
measured tip: `grep -cE '^\| S[0-9]{3}' corpus/SOURCES.md` → `259` rows with
`S518` the highest, and `grep -c 'S519' corpus/SOURCES.md` → `0` (exit 1, no
match). They must land in the same integration step as this entry; until their
lane rows exist these ids are unresolved, and the entry is not citable on them.
Draft row content (URL, kind, tier, scope, anchor, teaches) is in
`.ufo/waves/round-60/w1/out/K01LiveLifecycleEntry/sources-rows.md`; the registry
row is authoritative once opened.

## Run recipe — `tools/kama-ollama-live.py`, in order

Invocation: `python3 tools/kama-ollama-live.py --work <dir> --out <receipt.json>`
(schema `kama-ollama-live/v1`; optional `--nonce`, `--ollama-bin`,
`--model-gguf`, `--no-generate`). Exit `0` all evaluated checks passed
(`MODEL_OK`), `1` a check failed (`FAIL`), `2` setup error or not evaluated,
including `BINARY_DIGEST_MISMATCH` and `MODEL_DIGEST_MISMATCH`.

1. **Pins.** Read `registry/ollama-live-pin.tsv`; keys `version`, `bin_sha256`,
   `archive_sha256`, `model_sha256`, `default_home`, `default_model` are
   mandatory — a missing key is `SETUP_ERROR`/exit 2. Pinned values:
   version `0.40.11`, archive `7bedab90dd122661be78798e9f0edf37fccf0cccf2699d2c58ea1a3afdc04b6d`
   (the release's `sha256sum.txt` line, re-compared above), binary
   `b0a4becfaf872e3ad5d2e9051244e0dfe55409f03d6e2cd9bd9c34400e201b4c`, model
   `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d`.
2. **Nonce.** `--nonce` or `secrets.token_hex(6)`, must match
   `^[a-z0-9]{8,32}$`; otherwise `SETUP_ERROR`. The model name is
   `kama-<nonce>` and the qualified name `kama-<nonce>:latest`.
3. **Binary digest, before anything starts.** Hash the default
   `~/.local/opt/ollama-v0.40.11/bin/ollama` (`--ollama-bin` overrides) and
   compare to `bin_sha256`; mismatch ends the run at exit 2 with no child.
4. **Model digest.** Hash the default
   `~/.cache/kama-shokunin/models/stories260K.gguf` (`--model-gguf` overrides)
   and compare to `model_sha256`.
5. **Port.** `bind(('127.0.0.1', 0))`, refusing `{8080, 34113}` and any port
   already listening (`/proc/net/tcp`, `/proc/net/tcp6`); up to 50 attempts.
6. **Child environment.** Exactly `PATH=/usr/bin:/bin`, `HOME=<work>/home`,
   `OLLAMA_HOST=127.0.0.1:<port>`, `OLLAMA_MODELS=<work>/models`,
   `OLLAMA_NO_CLOUD=1`, `OLLAMA_NOPRUNE=1`, `CUDA_VISIBLE_DEVICES=-1`,
   `HIP_VISIBLE_DEVICES=-1`, `GGML_VK_VISIBLE_DEVICES=-1`.
7. **Start.** `Popen([<binary>, 'serve'])` with `cwd=<work>`,
   `start_new_session=True`, output to `<work>/serve.log`; poll `GET /` for up
   to 90 s until status 200 and body exactly `Ollama is running`.
8. **Prove the child.** `GET /api/version` must parse to the pinned version;
   `sha256(/proc/<child pid>/exe)` must equal `bin_sha256`; the listening socket
   inode for the port (from `/proc/net/tcp*`) must appear in `/proc/<child
   pid>/fd`, i.e. the child owns the listener.
9. **Empty store.** `GET /api/tags` must be 200 with `models == []`; `GET
   /v1/models` is captured and its empty form is recorded, not graded.
10. **Import.** Write `<work>/Modelfile` containing `FROM <gguf path>` (S521's
    recipe), then run `[<binary>, 'create', 'kama-<nonce>', '-f', <work>/Modelfile]`
    in the same environment with a 180 s timeout; exit 0 is required.
11. **Post-import surfaces.** `GET /api/tags` (exactly one entry whose `name`
    and `model` both equal `kama-<nonce>:latest` and whose `digest` is 64 hex),
    `GET /v1/models` (the qualified id must be present), `GET
    /v1/models/kama-<nonce>` (captured; single id recorded as an observation),
    `POST /api/show {"model": <qualified>}`, `GET /api/ps`.
12. **Evidence before load.** Write the just-captured `/api/tags` and `/api/ps`
    bytes to `<work>/evidence-before-tags.json` and
    `<work>/evidence-before-ps.json` and run
    `python3 tools/kama-ollama-evidence.py --tags … --ps … --expect <qualified>`;
    the finding must be `available_not_loaded` with exit 1.
13. **One generation, then residency.** `POST /api/generate` with
    `{"model": <qualified>, "prompt": "Once", "stream": false, "options":
    {"num_predict": 4}}` (180 s timeout) must return `done: true` and a string
    `response`; then `GET /api/ps` must list the model with the digest
    `/api/tags` reported, and the replay over `<work>/evidence-after-{tags,ps}.json`
    must be `loaded_same_digest` exit 0.
14. **Teardown.** `SIGTERM` to the child's process group, wait up to 30 s,
    `SIGKILL` only if needed; sleep 0.5 s; the graded check needs a refused port
    and no SIGKILL. An `Exception` raised inside the try becomes `fault` in the
    receipt and exit 2; the `finally` reaps the child either way. A
    `BaseException` subclass (`KeyboardInterrupt`, `SystemExit`) is not caught
    by that handler, so it propagates past it after teardown and writes no
    receipt — a limit of this harness rather than a graded state.

The tool never deletes `<work>`; the caller owns cleanup. It writes no
`~/.config`, `~/.omp` or systemd file, contacts no registered consumer, and
records no environment value (only the child's key names are in the code).

## HTTP surfaces observed — 2026-10-27, nonce `b61c98ad5747`, port 58921

Bodies are the receipt's captured bytes; a trailing LF is written `\n`. Short
bodies are quoted verbatim; long ones are quoted as their observed fields, whose
order in this table is this table's, not the body's — the sha256 identifies the
exact bytes the receipt holds.

| Request (capture) | Status | Body, as captured | body sha256 |
|---|---|---|---|
| `GET /` (`root`) | 200 | `Ollama is running` | `afea168799b6bcdb259676a41b211bc7cef67ff4ff09d31e8c9e477449eaa8af` |
| `GET /api/version` (`version`) | 200 | `{"version":"0.40.11"}` | `63f2fd8d6986831e7655600d9ba0dcba9b39582159cac5a84c6f5ba71c706fea` |
| `GET /api/tags`, before create (`tags-empty`) | 200 | `{"models":[]}` | `a6fe9ec6e26a38d99fca418b69826e0238b7a2bb319ff05eb153a6fcfd1fa28d` |
| `GET /v1/models`, before create (`v1-models-empty`) | 200 | `{"object":"list","data":null}` + LF | `da0b0172b9c61281c1e49286cff39dd4f75bceeb0a4e01672daa401640ab9749` |
| `GET /api/tags`, after create (`tags`) | 200 | one entry: `name` = `model` = `kama-b61c98ad5747:latest`, `size` 1185492, `digest` `8cf91c7109e77999ac0ae6e6eab27dfea00d9f83ffbe4559a3f26266e455c792`, `details` = `{parent_model: "stories260K.gguf", format: "gguf", family: "llama", families: ["llama"], parameter_size: "293K", quantization_level: "unknown", context_length: 2048, embedding_length: 64, runner: "llamacpp"}`, `capabilities` `["completion"]`, `modified_at` `2026-10-27T18:29:10.137112591-03:00` | `5c5f8691fccc1e9d2b93432f497762778e45ac147a90092645004cc33a2918ab` |
| `GET /v1/models` (`v1-models`) | 200 | `{"object":"list","data":[{"id":"kama-b61c98ad5747:latest","object":"model","created":1793136550,"owned_by":"library"}]}` + LF | `1b67009557f3a9b907fac76858ae3514e0bfc6cc644752e957fff2a961b5049c` |
| `GET /v1/models/kama-b61c98ad5747` (`v1-model-single`) | 200 | `{"id":"kama-b61c98ad5747","object":"model","created":1793136550,"owned_by":"library"}` + LF | `4a741b1a9841cfeb2c6573218793cab2b03b463bb6cc53bb836aa91592b7869a` |
| `POST /api/show {"model":"kama-b61c98ad5747:latest"}` (`show`) | 200 | `modelfile` begins `# Modelfile generated by "ollama show"` and holds `FROM /fast/scratch/hyaku/kama-r60/live1/models/blobs/sha256-270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d` and `TEMPLATE {{ .Prompt }}`; `details.parent_model` `stories260K.gguf`; `model_info` `general.parameter_count` 292800, `general.architecture` `llama`, `llama.block_count` 5, `llama.context_length` 2048, `llama.embedding_length` 64; `capabilities` `["completion"]` | `18d84a02699ecf97c27ed9569dcaca93495aabf6fdc09adeff06b5daa722c5f7` |
| `GET /api/ps`, before generate (`ps-before`) | 200 | `{"models":[]}` — byte-identical to `tags-empty` | `a6fe9ec6e26a38d99fca418b69826e0238b7a2bb319ff05eb153a6fcfd1fa28d` |
| `POST /api/generate` (`generate`) | 200 | `done` `true`, `done_reason` `"length"`, `model` `kama-b61c98ad5747:latest`, `response` `" upon a time,"`, `created_at` `2026-10-27T21:29:10.424782727Z`, `eval_count` 4, `prompt_eval_count` 2, `load_duration` 252730421, `total_duration` 254512669 (`context` token array present, not interpreted) | `caf85965eb0fa8d5f8f0cd256aca45ca359742b2aef78ab5be8b115bcb1b547c` |
| `GET /api/ps`, after generate (`ps-after`) | 200 | `{"models":[{"name":"kama-b61c98ad5747:latest","model":"kama-b61c98ad5747:latest","size":6312427,"digest":"8cf91c7109e77999ac0ae6e6eab27dfea00d9f83ffbe4559a3f26266e455c792","details":{"parent_model":"","format":"gguf","family":"llama","families":["llama"],"parameter_size":"293K","quantization_level":"unknown"},"expires_at":"2026-10-27T18:34:10.425205706-03:00","size_vram":0,"context_length":2048,"runner":"llamacpp"}]}` | `7fe035ecdaf7d8faccb8775543f9ddd5d3a1cff9b9ac4432ce1693b0d87a5531` |

Receipt-level values: schema `kama-ollama-live/v1`, verdict `MODEL_OK`,
`elapsed_s` 1.35, 16 checks, 16 evaluated true, 0 failed, 11 captures,
`teardown` `{returncode: 0, sigkill_needed: false, port_closed: true}`.

**The empty `/v1/models` body form is `data: null`.** `{"object":"list","data":null}`
is what an empty store answers, not `{"object":"list","data":[]}`; a client that
does `for m in body["data"]` fails on this body, and one that treats `data` as a
list of length 0 without a null check crashes. The harness records the form as
an observation (`observations.v1_models_empty_data_form` → `null`) and its own
reader uses `… .get("data") or []`.

**Two id shapes on one model.** `/v1/models` advertises
`kama-b61c98ad5747:latest`; `GET /v1/models/kama-b61c98ad5747` (requested with
the unqualified name) answers `"id":"kama-b61c98ad5747"` — the tag is dropped.
The receipt records `observations.v1_single_id` = `kama-b61c98ad5747` and
`observations.v1_single_id_equals_list_id` = `False`. An exact-string equality
between the two routes' ids therefore fails on a healthy server, and an exact
name matcher (the offline replay's policy, S523 `kama-ollama-evidence.py`) must
be given the shape it will actually compare rather than one canonical id.
Whether the single route also accepts the qualified name is **not observed**
[INFERENCE].

Other observed shape differences that a joiner can trip on:

- `/api/tags` entry `details.parent_model` is `stories260K.gguf`; the
  `/api/ps` entry's `details.parent_model` is the **empty string** for the same
  digest. A digest join survives this; a `parent_model` join does not.
- `size` differs on the same digest: `/api/tags` reports 1185492, `/api/ps`
  reports 6312427. The GGUF file itself is 1185376 bytes
  (`stat -c '%s' ~/.cache/kama-shokunin/models/stories260K.gguf`), i.e. 116
  bytes fewer than the `tags` figure. That the `tags` figure tracks the stored
  weights blob while the `ps` figure is the loaded footprint is [INFERENCE];
  the three byte counts are observed.
- The digest `/api/tags` and `/api/ps` report (`8cf91c71…c792`) is **not** the
  GGUF file digest (`270cba1b…256d`). The `show` `modelfile` names the imported
  file as `<store>/blobs/sha256-270cba1b…256d`, so the store keeps the weights
  blob under the file digest while the model inventories report a different
  digest. That the reported value is a model/manifest digest rather than the
  weights digest is [INFERENCE] — the receipt observes both strings but no
  manifest document.

## Documented versus observed

- **S522 notes predict two fields exactly.** `owned_by` "corresponds to the
  ollama username, defaulting to `library`" → observed `library`; `created`
  "corresponds to when the model was last modified" → observed 1793136550,
  which is 2026-10-27T21:29:10Z, the second of `modified_at`
  `2026-10-27T18:29:10.137112591-03:00`. The page documents neither the empty
  `data: null` form nor the unqualified single-route id.
- **S520's keep-alive default matches the observed expiry.** The FAQ says models
  are kept in memory "for 5 minutes" by default; `ps-after.expires_at` minus
  `generate.created_at` is 300.000423 s. That is consistent with the documented
  default, not proof that any unload happened — no unload was waited for.
- **S520's documented default context is not what `/api/ps` reports here.** The
  FAQ names 4096 tokens by default; this model's `/api/ps`
  `context_length` is 2048, equal to the GGUF's `llama.context_length` in the
  `show` capture. Which rule wins when a model declares more than 4096 was not
  observed [INFERENCE]; this run only shows a 2048-context model reporting
  2048 without any `OLLAMA_CONTEXT_LENGTH` in the child environment.
- **S521's recipe is the one that worked.** `Modelfile` with `FROM <abs path to
  .gguf>`, then `ollama create <name> -f <Modelfile>`; the CLI exits 0 and the
  model is immediately visible in `/api/tags`. The page's `ollama create
  my-model` without `-f` was not tried.
- **S519's asset digest is what the pin claims.** The release's
  `sha256sum.txt` line for `./ollama-linux-amd64.tar.zst` is
  `7bedab90…4b6d`, equal to `archive_sha256` in
  `registry/ollama-live-pin.tsv`. The `bin_sha256` is the digest of
  `bin/ollama` **as extracted on this host**, not an upstream-published value:
  no upstream line publishes a per-member digest, so the binary pin rests on the
  archive digest plus this host's extraction [INFERENCE beyond the archive].

## Numbers and their commands

One command carries the whole receipt-derived set
(`python3 .ufo/waves/round-60/w1/out/K01LiveLifecycleEntry/receipt-facts.py`,
exit 0, output `.ufo/waves/round-60/w1/out/K01LiveLifecycleEntry/receipt-facts.out`):
16 checks / 16 evaluated true / 0 failed / 11 captures / `elapsed_s` 1.35 /
nonce / port / teardown triple / every body above / `expires_minus_created_s`
300.000423 / sizes 1185492 and 6312427 / both digests / `size_vram` 0 /
`context_length` 2048 / `general.parameter_count` 292800.

| Number | Command | Output |
|---|---|---|
| receipt identity | `sha256sum .ufo/waves/round-60/live/receipt.json` | `49d06600521ce766488f4941b24a3f245883bf6744d0b214c21201f24090c2a6` |
| binary digest | `sha256sum ~/.local/opt/ollama-v0.40.11/bin/ollama` | `b0a4becf…1b4c` (matches pin) |
| GGUF digest | `sha256sum ~/.cache/kama-shokunin/models/stories260K.gguf` | `270cba1b…256d` (matches pin) |
| GGUF size | `stat -c '%s' ~/.cache/kama-shokunin/models/stories260K.gguf` | `1185376` |
| release asset digest | `curl -fsSL https://github.com/ollama/ollama/releases/download/v0.40.11/sha256sum.txt` then compare the `./ollama-linux-amd64.tar.zst` line with the pin | line `7bedab90…4b6d`; comparison exit `0`; saved as `.ufo/waves/round-60/w1/out/K01LiveLifecycleEntry/sha256sum-release.txt` (1472 bytes) |
| live re-run + 7 controls | `python3 tools/round60-c1-counter.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --tip 11f2d667f8bd89d127a4fb81dab44007c4c86c7f` | exit `0`; `tool_present=1 live_ok=1/1 fake_rejected=2/2 stale_rejected=1/1 tamper_rejected=3/3 log_rejected=1/1 errors=0 met=True` (saved as `…/K01LiveLifecycleEntry/c1-counter.out`) |
| registered consumer rows | `grep -c DEAD registry/history/latest.tsv`; `sed -n '2,4p' registry/history/latest.tsv` | `3`; `omp-llama-cpp-default DEAD connection-refused - 8080 inherited`, `ufo-fsd-thetick DEAD connection-refused - 34113 yes`, `ufo-fsd-local-helper DEAD connection-refused - 34113 yes`, under `#@snapshot_id 20261014T124232Z` |
| sources rows | `grep -cE '^\| S[0-9]{3}' corpus/SOURCES.md`; `grep -c 'S519' corpus/SOURCES.md` | `259`; `0` (exit 1) |

## What a green receipt proves

For that one run, and only that run:

- The process that served the port was the file whose sha256 is the pin: the
  `binary-digest` check hashes the file before start, and `running-exe-digest`
  hashes `/proc/<child pid>/exe` **after** start. `listener-owned` adds that the
  listening socket inode belongs to that pid, and `port-unregistered` that the
  port was neither 8080/34113 nor already listening.
- The model input was the pinned GGUF (`model-digest`), and the import produced
  one model: `create` exited 0 and `tags-lists-model` required exactly one entry
  with `name` == `model` == `kama-<nonce>:latest` and a 64-hex digest.
- The advertised id reached the OpenAI-compatible route
  (`v1-models-lists-model`) and `/api/version` reported the pinned version
  string.
- Residency changed in the graded direction: the replay over the pre-generation
  captures is `available_not_loaded` (exit 1) and over the post-generation
  captures `loaded_same_digest` (exit 0), with the `/api/ps` digest equal to the
  `/api/tags` digest.
- The child was reaped by the harness's own SIGTERM without SIGKILL, and the
  port refuses afterwards (`returncode 0`, `sigkill_needed false`,
  `port_closed true`).
- Those 16 checks are shown able to fail: the counter's 7 controls were all
  rejected in the re-run above — a fake server binary and a one-byte-patched
  copy of the real binary (`BINARY_DIGEST_MISMATCH`), a stale nonce, three
  receipts tampered with (edited `tags` body, zeroed `binary_sha256`, port set
  to 8080) and a receipt whose server log was removed.

Failure-path status codes are **not** part of this sample: no 4xx/5xx was
captured, so nothing here establishes how this server answers a bad request, an
unknown model, or a request during load.

## What it does not prove

- **Registered consumers stay DEAD, unsampled.** 8080 and 34113 were excluded
  from port selection and never contacted. Their last recorded state is
  `registry/history/latest.tsv` `#@snapshot_id 20261014T124232Z`, three
  `DEAD`/`connection-refused` rows; this entry adds no new sample of them and
  does not restore, repoint or probe any consumer. A green receipt here is a
  lane-owned fixture, not service restoration.
- **CPU only, on one host.** The child environment forces
  `CUDA_VISIBLE_DEVICES=-1`, `HIP_VISIBLE_DEVICES=-1`,
  `GGML_VK_VISIBLE_DEVICES=-1`, and `/api/ps` reports `size_vram: 0`. No GPU
  placement, backend selection or performance claim follows (the FAQ's CLI
  `PROCESSOR` column was not captured).
- **One version, one model.** `/api/version` `0.40.11`; one 293K-parameter
  fixture at `context_length` 2048. Nothing here compares 0.40.x builds, larger
  models, quantized weights, or a model whose GGUF declares more context.
- **No loading state was observed.** The harness waits for `GET /` to answer then
  captures; it polls no loading window, so it says nothing about what Ollama
  answers *while* a model loads. The empty `/v1/models` `data: null` was captured
  against an **empty store**, not a loading server, and the older lead that
  Ollama lists models with 200 "whatever the load state" remains a lead here.
- **No headers, no HTTP metadata.** Captures hold `{status, sha256, body}` only:
  no `Content-Type`, no `Server`, no transfer-encoding, no timing per request.
  Nothing here supports a header-based identity or content-negotiation claim.
- **No byte check on the served weights.** The GGUF source file is hashed before
  import; the store blob is never hashed. `show`'s `FROM` path carries the file
  digest as a *name*, which is a naming fact, not proof that the blob holds those
  bytes.
- **No expiry enforcement, concurrency, streaming or unload.** `expires_at` was
  read once; `stream: false` was used for the only generation; no second request
  ran while a model was loaded; no unload was waited for.
- **Not model quality.** The generation returned `done: true` with
  `done_reason: "length"` after `num_predict: 4`; `" upon a time,"` is a token
  artifact of the toy model, not a quality sample, and quality is outside this
  lane.
- **Not a property of Ollama in general.** One release, one platform asset
  (`ollama-linux-amd64.tar.zst`), one CPU host, one ephemeral unregistered
  loopback port, one `HOME` and model store under the caller's work dir.

## QUALITY clearance applied

- **KQ1** — every endpoint statement is about a child this tool started, with the
  command, the nonce, the port and the counter's exit pasted; no configured URL,
  listener or `/health` answer is offered as served-model identity.
- **KQ2** — pin provenance (archive digest from the release asset), endpoint
  verdict (per-check results) and effective runtime selection (the pinned binary
  plus `/proc/<pid>/exe`) are separate claims; no environment value is read to
  fill a gap.
- **KQ3** — external anchors name the release tag or docs page plus section; the
  registered-consumer rows are quoted at their snapshot id as historical, and no
  old corpus bytes are rewritten.
- **KQ4** — freshness scope is explicit: one dated sample, not monitoring; a
  fixture child is not runtime integration for the registered consumers.
- **KQ5** — no service, config or credential was touched; child environment keys
  are named, values are paths under the caller's work dir, and no secret, config
  body, session or journal is quoted.
- **KQ6** — each vendor statement names its engine, page, section and access
  date; observed bytes are kept separate from documented behaviour, and the one
  place where the documented default (4096) differs from observation (2048) is
  recorded rather than smoothed over.
- **KQ8** — nothing is recorded as `UNDECIDABLE`; the single-route acceptance of
  a qualified name is marked not observed instead of answered.
- **KQ9** — counts come from a full read of the receipt through a committed
  script and from whole-file greps; the source-row census states its count and
  its maximum id rather than sampling.
- **KQ11** — the provenance trio opens the entry; the source rows' unresolved
  state is declared instead of being presented as refreshed evidence.
- **KQ13** — available inventory (`/api/tags`), loaded residency (`/api/ps`),
  advertised identity (`/api/tags` names/digest, `/v1/models` ids) and inference
  readiness (not measured) stay separate, and the tags/ps digest join is marked
  [INFERENCE].
- **KQ24** — the unobserved loading window and unobserved headers are stated as
  not observed; they are not scored as failures or as passes, and no
  not-evaluated state is turned into a green check.
- **KQ27** — every quoted count names the revision it was measured at (lane
  commit `8b9f3060…` for the receipt, tip `11f2d667…` for the counter re-run) and
  its command; an uncommitted worktree is not attributed to a commit.
- **KQ46** — S519–S523 are ids this artifact requires but does not yet carry;
  S519 was re-derived as the next free id (`grep -c 'S519'` → 0, highest row
  S518) rather than copied from a plan, and the entry states that the ids are
  unresolved until the registry rows land.
