# ScribeProvinceNote — round-16 advice (scribe, leaf)

Owned output: `.ufo/waves/round-16/build/drafts/province-note.md` (append-ready PROVINCE.md section). No other lane file was written. No subagent was dispatched.

## Behavior

Drafted an append-only PROVINCE.md section describing the ephemeral lane-owned llama.cpp runtime for C2: official release `b11755` under `~/.local/opt`, pinned tiny GGUF under `~/.cache/kama-shokunin`, an unregistered loopback port chosen by the harness, and teardown after one run. The section states what the runtime is and is not: not service restoration, registered consumers stay DEAD, no `~/.config`, `~/.omp`, or systemd writes.

## Verified facts (2026-10-20)

- Installed binary: `~/.local/opt/llama-b11755/llama-server --version` → `version: 0.7.0-dev (build 11755, commit 704366d76)`. Symlink `~/.local/bin/llama-server` → that path (created 10:17).
- Asset digest: GitHub release API `https://api.github.com/repos/ggml-org/llama.cpp/releases/tags/b11755`, asset `llama-b11755-bin-ubuntu-x64.tar.gz`, `"digest": "sha256:753bfa7327a75b477d4d14cde71e0e46a40acc3a1408c5504530b78c33a6e226"`. Local `sha256sum ~/.local/opt/llama-b11755-bin-ubuntu-x64.tar.gz` gives the same value.
- Release object carries `"prerelease": true`; `"target_commitish": "704366d76f8748cf9ad3df62a464bfcc8d1ae6ad"`.
- Model: local `sha256sum ~/.cache/kama-shokunin/models/stories260K.gguf` → `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d` (matches spec).
- Loading body: `https://raw.githubusercontent.com/ggml-org/llama.cpp/b11755/tools/server/server-http.cpp:307-325` (`middleware_server_state`): returns 503 `{"error":{"message":"Loading model","type":"unavailable_error","code":503}}` for non-frontend paths while `is_ready` is false. Line 312: "no endpoints are allowed to be accessed when the server is not ready".
- README: `https://raw.githubusercontent.com/ggml-org/llama.cpp/b11755/tools/server/README.md:479-487` — `GET /health` 503 body "Loading model"; "the model is still being loaded." Defaults `--host` 127.0.0.1 and `--port` 9931 at lines 193–194.
- Lane boundary: `PROVINCE.md:45` "kama never writes to `~/.config`, `~/.omp`, or systemd units."
- Registered consumer ports: `registry/endpoint-consumers.tsv:35-37` (8080; 34113). `ss -ltn` on 2026-10-20 shows no listener on 8080 or 34113.
- Unit absence: `~/.config/systemd/user/qwen-coder.service` → "No such file or directory" (2026-10-20).
- KQ5 wording: `corpus/QUALITY.md:13`: a training admission "requires enabling services, repointing consumers, installing timers" is rejected.

## Findings for L1

1. The harness `tools/kama-llamacpp-live.py` does not exist yet (glob, 2026-10-20). The draft describes it as planned and does not claim any observed harness behavior or teardown proof.
2. The draft says "not a standing service" and "lifetime is one harness run". This is consistent with KQ5 only if the harness never enables a unit, timer, or config. The draft says so; the sentinel item should confirm.
3. The 8080 / 34113 status is from the round-5 snapshot plus today's `ss -ltn`. The draft cites both and does not claim the registered rows are fixed.
4. Source-line numbers were taken from `curl` fetches to `/tmp` (`grep -n`), not from viewer output, because the viewer elides lines.

## Unknowns (stated in the draft)

- Upstream provenance of `stories260K.gguf` (HF repo, redirect, license) was not checked; only the local digest was observed. A separate scout item covers this.
- Whether the server's `is_ready` flip is traced in source beyond the middleware check.
- Whether the release `prerelease` flag matters for lane reliance.

## Install / update record

None. No package or tool was installed or updated by this seat. The pacman guard is in force; nothing was attempted.

## Out of scope / not touched

No edits to PROVINCE.md, registry, probe, tests, MANIFEST.json, `.ufo/state`, or sibling lanes. No gate, harness, or test was run. The `/tmp/kama-r16-b11755-*` fetch copies are outside the lane and may be removed.

## Artifact paths

- Draft: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-16/build/drafts/province-note.md`
- Report: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-16/build/advice/ScribeProvinceNote.md`
