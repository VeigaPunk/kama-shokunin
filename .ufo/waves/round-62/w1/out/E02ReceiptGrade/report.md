# E02ReceiptGrade — independent re-grade of the round-62 C1 committed-measurement receipt

Lane: kama-shokunin · wave: round-62/w1 (v2, build & verify) · axes: operability, calibration
Lane tip at grade time: `65d7cad0fce90e34de37527cde22e97b63b118bf` (`git rev-parse master`)
Frozen controls: `.ufo/waves/round-62/controls/freeze.txt` (base `a959fd90…`, do-nothing receipts c1-base.txt/c2-base.txt)

## Target

- Receipt: `/fast/scratch/hyaku/kama-r62/measure/c1b/receipt.json`
  sha256 `568f762731d10a2465b39999ebbdb80b792e5d50aa42d1fdf9f63ae67ad650d6`, 9457 bytes,
  schema `kama-completion-live/v1`, verdict `REQUEST_OK`, nonce `r62-d4d183a95c`,
  `at` 2026-10-28T12:21:27.733Z, port 45081, child_pid 4103813, 6 captures, 17 checks.
- The receipt was present; no fresh live run was needed, so I did not start a server.

## Provenance (independent, read-only)

| artifact | sha256 | check |
|---|---|---|
| `measure/c1b/tip/tools/kama-completion-live.py` | `71ac4f2c45570a79cb1e80db91e85268609f28bf4dd421d628ffb9d10243771f` | equals `git show 65d7cad:tools/kama-completion-live.py` → MATCH |
| `measure/c1b/tip/tools/kama-llamacpp-live.py` (dependency) | `98d2e6bb48a90e60797df0d2bee895eac4a6cdd9859af2dc47b64bdb4a36fbe9` | equals tip blob → MATCH |
| `measure/c1b/tip/registry/endpoint-consumers.tsv` | `bf343625188d9f486a6f6d13c60c946e23c21d05ee1bef881204dfa14c62bc6c` | equals tip blob → MATCH |
| model `~/.cache/kama-shokunin/models/stories260K.gguf` | `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d` | equals tool `DEFAULT_MODEL_SHA` and receipt.model.sha256 |
| server `~/.local/opt/llama-b11755/llama-server` | `b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804` | equals tool `DEFAULT_SERVER_SHA` and receipt.server.sha256 |

The receipt carries no tip field, so the tip binding above rests on the byte-identity of the
pinned tool copy with the committed blob — the only provenance route the schema offers.

Port 45081 does not appear in `registry/endpoint-consumers.tsv` (grep rc=1): the run used an
unregistered loopback port as the predicate requires. argv is internally consistent with the
receipt (`--alias`, `--port`, `--model`, `--server[0]` match recorded fields; `--host 127.0.0.1`).

## Method

`regrade.py` (in `out/E02ReceiptGrade/`) — a ~330-line standalone stdlib script. It does **not**
import `tools/round62-c1-counter.py` or `tools/kama-completion-live.py`; it re-implements each
check predicate from the receipt schema and the frozen check reasons, re-hashes every captured
body, re-hashes the model/server files itself, reads the digest pins out of the pinned tool
source as text, stats the hold `release` file, and reads LISTEN sockets from `/proc/net/tcp{,6}`
(no `ss`). `probe.py` then mutates copies of the receipt to test that the re-grade is sensitive.

## Capture integrity

All six captured bodies re-hash to their recorded `body_sha256` byte-for-byte; none is truncated:

`bad_request · completion · completion2 · health · models · props` → 6/6 MATCH, 0 truncated.

## Per-check recomputation (recomputed vs stored `checks[name].passed`)

| check | recomputed | stored | how re-derived |
|---|---|---|---|
| completion_envelope | True | True | completion status 200, object=text_completion, choices[0].text is str |
| completion_finish_reason | True | True | `finish_reason` = "length" ∈ (length, stop) |
| completion_model_id | True | True | completion.model = "kama-completion-probe" = alias |
| completion_fingerprint | True | True | `b11755-704366d76` matches `^b\d+-[0-9a-f]{9,40}$` |
| completion_usage | True | True | 8 + 8 = 16, all ints ≥ 1 |
| completion_timings | True | True | predicted_n 8 = completion_tokens 8, predicted_ms 0.483 numeric |
| completion_deterministic | True | True | temperature 0 and completion2 text = completion text (" ground. She liked") |
| bad_request_graded | True | True | status 400, body has `error` object (missing `prompt`) |
| health_ready | True | True | body exactly `{"status":"ok"}`, status 200 |
| models_alias_id | True | True | `data[].id` = ["kama-completion-probe"] = alias |
| props_alias | True | True | `/props` `model_alias` = alias |
| model_digest | True | True | own sha256 of model file = pin = recorded |
| server_digest | True | True | own sha256 of llama-server = pin = recorded |
| hold_released | True | True | `hold.released=true`; `hold/release` exists, bytes `go\n`, mtime 12:21:27.942Z = at + 0.209 s (inside the 180 s default window) |
| teardown_clean | True | True | child_pre_dead false, returncode 0 ∈ {0, −15}; server.log ends "cleaning up before exit…" |
| teardown_port_closed | True | True | `port_closed=true` and port 45081 absent from `/proc` LISTEN now |
| listener_owned | **not recomputable** | True | see below |

Verdict recomputation: all 17 stored checks have `evaluated=true, passed=true` → expected
verdict `REQUEST_OK`; stored verdict `REQUEST_OK` → consistent.

Other derived consistency: recorded check names = tool's 17 distinct `check()` names (20 call
sites, 3 duplicates in conditional branches) — no missing, no unexpected entries. The receipt's
evidence for the second-request determinism shows warm-cache reuse (`completion2`: `cache_n=7`,
`prompt_n=1`) while `usage.prompt_tokens` stays 8; that is the server's expected accounting, not
a defect, and the graded text is identical.

## Finding: `listener_owned` is receipt self-attestation

`listener_owned` cannot be re-derived from captured bytes: the run-time proof
(`_live.port_owned_by(proc.pid, port)` for child 4103813 on port 45081) left no recorded
evidence, and `/proc/4103813` no longer exists (`child_pid` gone, port closed). Stored value is
`true`. Note that the counter's own `grade()` (tools/round62-c1-counter.py) also copies this
value straight from the receipt (`out['listener_owned'] = bool(stored…passed)`), so that field is
non-falsifiable in the counter's offline leg as well; the counter's independence for ownership
comes solely from its live witness (`witness['listener_owned']` via `port_owned_by` during the
hold). This is a calibration limitation of the artifact, not a mismatch: no stored value is
contradicted by anything I can observe.

## Sensitivity probe (10 mutations, 10/10 caught)

Mutated copies re-hashed at the body level unless noted, graded with the same script:

| mutation | expected mismatch | observed |
|---|---|---|
| completion text changed (+rehash) | completion_deterministic | completion_deterministic |
| models `data[0].id` changed (+rehash) | models_alias_id | models_alias_id |
| `usage.total_tokens` 16→17 (+rehash) | completion_usage | completion_usage |
| `system_fingerprint` garbage (+rehash) | completion_fingerprint | completion_fingerprint |
| bad_request status 400→200 (+rehash) | bad_request_graded | bad_request_graded |
| `hold.released`→false | hold_released | hold_released |
| teardown returncode 0→1 | teardown_clean | teardown_clean |
| completion2 choices emptied (+rehash) | completion_deterministic | completion_deterministic |
| health body edited **without** re-hash | health_ready | health_ready + integrity gate flags `health` |
| verdict flipped to FAIL | (none) | verdict-consistency false, rc 1 |

Every semantic mutation moved exactly its own check; the integrity gate is separately live.

## Operability / calibration notes for the L1

- The C1 receipt is internally consistent under a fully independent grader: 16/16 recomputable
  checks recompute true and agree with the stored verdicts, 0 mismatches, 0 errors.
- The one blind spot is `listener_owned` (self-attested). If the freeze wants byte-level
  re-derivation of ownership, a future schema revision should capture the listener-inode/pid
  binding in the receipt; today only the counter's live witness closes that gap.
- The receipt does not record the tip or the hold timeout; I bound the hold window with the
  tool default (180 s). The release mtime delta (+0.209 s) is well inside any plausible window.

## Tools installed

None. Existing `python3` (3.14) from the host was sufficient; no pacman or other transaction run.

## Evidence files (this directory)

- `regrade.py` — independent re-grader
- `probe.py` — mutation sensitivity harness
- `regrade-out.json` — full per-check recomputed/stored/evidence output for the real receipt
- `probe-out.json` — 10-mutation table

Tally: **E02 checks=17 recomputed=16 stored_true=17 agree=16 mismatch=0 non_recomputable=1 mutations=10/10 verdict=consistent**
