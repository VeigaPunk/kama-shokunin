source: S519 https://github.com/ollama/ollama/releases/download/v0.40.11/sha256sum.txt §line 6; S520 https://docs.ollama.com/faq §§server bind/model storage; S521 https://github.com/ollama/ollama/blob/v0.40.11/docs/import.mdx §Importing a GGUF model; S523 own-work `tools/kama-ollama-live.py` + `.ufo/waves/round-60/live/receipt.json` at `8b9f3060966c22bede3094d748974caf041b4c33`
verified-at: 2026-10-27 — one fresh live v0.40.11 child, receipt nonce `b61c98ad5747`; the independent round-60 counter currently has W1 false-green falsifiers, so its self-test output is not an independent admission proof
recheck: `python3 tools/kama-ollama-live.py --work <scratch>/run --out <scratch>/receipt.json` then compare source bytes and tool checks to the receipt; on-release

# Ollama v0.40.11 — lane-owned live lifecycle observation

## Claim and scope

`tools/kama-ollama-live.py` can start the locally pinned Ollama v0.40.11 binary as a lane-owned child, assign an unregistered loopback port and private HOME/model store under `--work`, import a fixture GGUF through a Modelfile, capture Ollama HTTP responses, exercise `/api/tags` and `/api/ps` before and after one generation, then terminate the child. This is one observed run of one CPU fixture; it does not prove registered-consumer health, model quality, other versions, GPU placement, broad failure behavior, or false-green resistance of its counter.

The tool uses the locally installed binary (`~/.local/opt/ollama-v0.40.11/bin/ollama`), pin file `registry/ollama-live-pin.tsv` and fixture `~/.cache/kama-shokunin/models/stories260K.gguf`. It does not install, configure or start a system service. The installed process is an unregistered child; use is pending the existing operator ratification L0 item about lane-owned ephemeral serving.

## Run recipe

Run `python3 tools/kama-ollama-live.py --work <scratch>/run --out <scratch>/receipt.json`. It checks binary and model digests, selects a free loopback port excluding registered ports, starts `ollama serve` with an isolated HOME/model path and cloud/GPU-related environment switches, waits for `GET /`, verifies `/api/version` and listener ownership, imports `FROM <fixture.gguf>` using `ollama create kama-<nonce> -f <Modelfile>`, captures tags/models/show/ps, calls the lane's offline Ollama evidence classifier before and after one short generation, then SIGTERM-stops its child. The caller must retain the work directory long enough to inspect it and then clean it up. A normal return does not test parent-death behavior: a seat's SIGKILL probe observed that the child can outlive a killed tool process (W1 `A03OrphanOnKill`).

## Captured HTTP values

Numbers and body details below are from the committed receipt `.ufo/waves/round-60/live/receipt.json` at lane tip `8b9f3060966c22bede3094d748974caf041b4c33`; each is reproduced by reading that JSON and selecting `captures.<name>` (not a fleet-wide census).

| Capture | Observed response |
|---|---|
| `root` | status 200, `Ollama is running` |
| `version` | status 200, `{"version":"0.40.11"}` |
| `tags-empty` and `ps-before` | status 200, `{"models":[]}` |
| `v1-models-empty` | status 200, `{"object":"list","data":null}` — empty data is null here, not an empty array |
| `tags` | one `kama-b61c98ad5747:latest` entry; `name` and `model` are qualified and equal; digest is `8cf91c7109e77999ac0ae6e6eab27dfea00d9f83ffbe4559a3f26266e455c792` |
| `v1-models` / `v1-model-single` | list id is `kama-b61c98ad5747:latest`; single route requested with bare name returns bare id `kama-b61c98ad5747`. The tool records this difference as observation, not a graded invariant. |
| `ps-after` | after generation, `/api/ps` has the qualified name and same inventory digest as tags; `expires_at` and `size_vram` are returned |
| `generate` | status 200 and `done: true`; this is a lifecycle observation, not quality evidence |

Receipt-derived 16-check count and `MODEL_OK` are data fields from that receipt, not proof of the counter's frozen semantics. W1 found that patched replay behavior can still produce a receipt accepted by the independent C1 verifier; the result is not promoted as a verified capability until a later frozen round repairs that flaw.

## v2 harness (round 61) — hold-verified run

Round 61 promoted the same tool to schema `kama-ollama-live/v2`, closing the r60
falsification classes the non-author spot-check routed: a stub replay tool and a
post-capture child death both produced green-looking receipts. v2 changes:

- **`--hold-dir DIR`** writes `hold.json` (`{nonce, port, pid, qualified, work}`)
  after all captures complete, then blocks up to `HOLD_TIMEOUT` (300 s) waiting
  for `<hold-dir>/release` to appear. An outside verifier makes its own live HTTP
  contact during that window before releasing; `hold.released` and
  `hold.signalled` are graded (`hold-released`).
- **`pdeathsig`** arms `PR_SET_PDEATHSIG(SIGKILL)` on the serve child, so a parent
  death by *any* signal (SIGKILL included) kills it kernel-side; the receipt
  records the armed mechanism or a named unavailability reason.
- **`/api/show`** becomes a graded check (`show-model-info`); the receipt's
  `evidence` block records each replay's `finding_id` + `exit` for independent
  re-execution, and `teardown.child_pre_dead` records whether the child was
  already dead when teardown began (the r60 post-capture-death class).
- The fresh nonce `r61live01` receipt lives at
  `.ufo/waves/round-61/live/receipt.json`: verdict `MODEL_OK`, port 47887,
  `hold.released=true` after an outside GET on `/api/version` and `/api/ps`,
  clean SIGTERM teardown (`returncode 0`, `sigkill_needed=false`,
  `child_pre_dead=false`, `port_closed=true`). The counter
  `tools/round61-c1-counter.py` re-contacts the held child itself, re-runs the
  classifier on the receipt's capture bodies, re-hashes manifest+blob, and
  grades show; its claim-registry rows live in
  `registry/ollama-live-claims-r61.tsv` evaluated by
  `tools/round61-c2-counter.py`.

## Boundaries

The three registered consumers' last history remains `DEAD` / connection-refused on their registered ports; this tool does not query or repoint them. The actual release archive digest is published in S519; the extracted binary digest is the observed local file digest, not an upstream-published per-member digest. Captured values apply only to the one release, model, host and run. Unknown-model errors, concurrency, unload timing and other runtime states are outside this receipt unless separately captured. The `/v1/models` null data and differing list/single id forms show why a client must not assume one canonical ID shape from a single route.
