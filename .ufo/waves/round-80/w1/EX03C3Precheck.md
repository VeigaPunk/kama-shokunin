# EX03C3Precheck — Ollama v0.40.11 fixture precondition and capture

Round: kama 80, wave 1. Axis: operability (C3 fixture leg). Verdict: **PASS**.

## What was proven

The lane-owned pinned Ollama child (v0.40.11) runs on this host from the lane
fixture GGUF, under a scratch HOME and scratch model store, on port 40917 — a
port that is **neither** a registry-declared consumer port (**8080**, **34113**
are the only two in `registry/endpoint-consumers.tsv`) **nor** listening. One
model (`ex03c3p-6f2e91:latest`) was created from
`$HOME/.cache/kama-shokunin/models/stories260K.gguf` (blob sha256
`270cba1b…256d` re-derived by `ollama create`). All four census-facing GETs
returned 200 with the exact bodies captured under `captures/`. The child was
torn down and port 40917 proven closed (ss, curl exit 7, ps).

`/v1/models` verdict: **answers with a model array** — HTTP 200,
`{"object":"list","data":[{"id":"ex03c3p-6f2e91:latest",…}]}` — an array of
length 1 under `data`, not a llama.cpp loading envelope, not a foreign body.
`tools/kama-probe.sh listeners` reads `/v1/models` via its `fetch()`; against
this child it sees a well-formed OpenAI-style model list, so the fixture
satisfies what the census class reads.

## Lifecycle (times -03:00)

1. 07:40:41 — prereq checks: binary present (40779408 bytes, mode 755,
   `--version` tail "client version is 0.40.11"); gguf present (1185376 bytes,
   sha256 `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d`).
2. 07:44:47.923 — `ollama serve` started as named service `ollama-ex03c3p`
   (pid 1951437); readiness on 127.0.0.1:40917 confirmed; server log:
   `Listening on 127.0.0.1:40917 (version 0.40.11)`.
3. 07:48:47 — `ollama create ex03c3p-6f2e91 -f Modelfile` → exit 0, "success".
4. 07:51:35 — four GET captures (status/bytes/sha256/verbatim in `EX03.json`).
5. 07:51:43 — service killed; port-closed proof recorded below.

Lane tip observed at seat start: `fe7b978013bd1aa6d67a7e0fbf6369b8d7a9b023`
(`git -C … rev-parse master`; base per plan is
`c45fc7d1a8427e9c98a9dd7befa542c7b5caed38` — tip already advanced when I read
it; recorded, not graded).

## Command lines and exit codes

- Start:
  `env HOME=/fast/scratch/hyaku/kama-r80/EX03C3Precheck/home OLLAMA_MODELS=/fast/scratch/hyaku/kama-r80/EX03C3Precheck/models OLLAMA_HOST=127.0.0.1:40917 TMPDIR=/fast/scratch/hyaku/kama-r80/EX03C3Precheck /home/vgpnk/.local/opt/ollama-v0.40.11/bin/ollama serve`
  — service, killed at teardown (no exit code).
- Create:
  `env HOME=…/home OLLAMA_MODELS=…/models OLLAMA_HOST=http://127.0.0.1:40917 TMPDIR=… /home/vgpnk/.local/opt/ollama-v0.40.11/bin/ollama create ex03c3p-6f2e91 -f /fast/scratch/hyaku/kama-r80/EX03C3Precheck/Modelfile`
  — **exit 0**.
- Captures (all curl, `-m 10`, each **exit 0**):
  - `curl -sS -o …/captures/version.json -w … http://127.0.0.1:40917/api/version` → 200, 21 B
  - `curl -sS -o …/captures/tags.json -w … http://127.0.0.1:40917/api/tags` → 200, 469 B
  - `curl -sS -o …/captures/models.json -w … http://127.0.0.1:40917/v1/models` → 200, 117 B
  - `curl -sS -o …/captures/ps.json -w … http://127.0.0.1:40917/api/ps` → 200, 13 B
- Port-closed proof:
  - `ss -ltn | grep ':40917 '` → no match (grep exit 1)
  - `curl -sS -o /dev/null -m 3 http://127.0.0.1:40917/api/version` → **exit 7**
    "Failed to connect … Could not connect to server"
  - `ps -eo pid,cmd | grep 'ollama serve' | grep -v grep` → no match (exit 1)

## Receipts (absolute paths)

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-80/w1/EX03C3Precheck/EX03.json` — lifecycle, command lines, exit codes, verdict.
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-80/w1/EX03C3Precheck/captures/version.json` — `{"version":"0.40.11"}`, body sha256 `63f2fd8d…`
- `…/captures/tags.json` — one model `ex03c3p-6f2e91:latest`, digest `8cf91c71…e455c792`, sha256 `0411d572…`
- `…/captures/models.json` — `data:[{"id":"ex03c3p-6f2e91:latest",…}]`, sha256 `a4811cb5…`
- `…/captures/ps.json` — `{"models":[]}` (nothing loaded; no generate was run — an inventory, per the sourced claim), sha256 `a6fe9ec6…`

## Boundaries kept

No git writes (read-only `rev-parse` only); no installs (named item); nothing
written under `~/.config`, `~/.omp`, systemd, `~/.local/bin`, or any lane path
outside this seat dir. All child state (id key, blobs, manifests, metadata)
lived under the scratch root and was deleted when this seat yielded.

## Notes and risks

- `GET /api/ps` returning an empty list is expected, not a defect: the census
  class consumes the tags-style inventory, and the C3 sourced claim records
  that a tags listing is an inventory of models available locally.
- The lane tip advanced past the plan's base before my run (`fe7b9780…`); my
  seat grades no commits and only records the observation.
- No blockers. No sibling files touched.
