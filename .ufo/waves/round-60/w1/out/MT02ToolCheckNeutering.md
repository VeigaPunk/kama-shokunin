# MT02ToolCheckNeutering — round 60, kama, w1 — tool-check neutering mutants (C1)

Axes: operability (judged) + calibration. Seat: mutation tester, advisory leaf. Attacked surface:
the 8 behavior-bearing checks of `tools/kama-ollama-live.py` and whether
`tools/round60-c1-counter.py::verify()` independently re-derives each one. No verdict on the lane
claim is issued; no lane source was edited.

## Method

Scratch tree `/fast/scratch/hyaku/kama-r60/MT02ToolCheckNeutering/tree/` holds byte-identical copies
of `tools/kama-ollama-live.py`, `tools/kama-ollama-evidence.py`, `registry/ollama-live-pin.tsv`
(`REPO` resolves there; evidence subprocess resolves inside the tree). Detector = `verify()` imported
from the lane counter (`importlib`, read-only). Every case ran the tool for real — the tool spawns
its own lane-owned ollama child on a fresh ephemeral port (never 8080/34113/11434); no seat-spawned
server, no port reuse, fresh nonce `mt02<8hex>` per case, fresh work dir, `TMPDIR` set to the scratch.

Per case: mutate the tree copy (exact-once anchor, mutation marker asserted in the bytes executed),
hash the executed bytes, run
`python3 <tree>/tools/kama-ollama-live.py --work <work> --nonce <n> --out <work>/receipt.json [extra]`,
then `verify(json.load(receipt), work, nonce)`, then restore exact pristine bytes and assert the hash.
Baseline gate: pristine run accepted by `verify()` (it was: `MODEL_OK`, `bad=[]`), so results below are
conclusive, not inconclusive.

Honesty note: pass 1 (archived under `runs-pass1-raced/`) ran 2 workers against the one shared tree
file and raced — `mut-ready`'s recorded hash was the empty-file hash `e3b0c442…`, proving concurrent
mutation. Pass 1 is discarded; the table is pass 2 (`driver2.py`), strictly sequential, with per-case
exec-time hash + restoration assertion. Pass-2 verdicts matched pass-1 everywhere both ran.

## Mutants (one check neutered per mutant: condition → `True`; world healthy)

Pristine `kama-ollama-live.py` sha256 `9d1c688bd2951485…50472aaf` (lane == tree copy, before and after).

| mutant (check neutered) | exec sha256 (16) | receipt | verify(receipt, work, nonce) | classification |
|---|---|---|---|---|
| baseline-pristine | 9d1c688bd2951485 | exit 0 `MODEL_OK` | `[]` accepted | gate passed |
| `ready` | 1290a7f72eb7d60b | exit 0 `MODEL_OK` | `[]` accepted | SURVIVED |
| `version` | fb4787e9ff37f75a | exit 0 `MODEL_OK` | `[]` accepted | SURVIVED (see probe note) |
| `running-exe-digest` | c16e7b1ae115107b | exit 0 `MODEL_OK` | `[]` accepted | SURVIVED |
| `listener-owned` | c0e9311687b82a68 | exit 0 `MODEL_OK` | `[]` accepted | SURVIVED |
| `tags-empty-before-create` | c3d0fb4e79f5e674 | exit 0 `MODEL_OK` | `[]` accepted | SURVIVED (violated-world proof below) |
| `evidence-before-load` | 56a3ec90b4de82b9 | exit 0 `MODEL_OK` | `[]` accepted | SURVIVED |
| `ps-lists-loaded` | cd0370bd7e624488 | exit 0 `MODEL_OK` | `[]` accepted | SURVIVED (re-derivation exists, see probe) |
| `teardown` | fa543b7cb255bfd9 | exit 0 `MODEL_OK` | `[]` accepted | SURVIVED |
| restored-pristine | 9d1c688bd2951485 | exit 0 `MODEL_OK` | `[]` accepted | restoration behaviorally green |

8/8 single-check neutering mutants survived: `verify()` takes every per-check boolean from the
receipt (`REQUIRED` loop: `passed is True and evaluated is True`) and re-derives none of the 8 check
computations themselves. Its independence lives entirely in artifacts: frozen constants
(`binary_sha256`), capture bodies (`version`, `tags`, `ps-before`, `ps-after`), `serve.log`, model
manifest, blob re-hash, post-run `listening_ports()`.

## Bad-world probes (where a false condition is reachable via tool inputs only)

| probe | world | receipt | verify bad |
|---|---|---|---|
| probe-ps-nogen | `mut-ps-lists-loaded` + `--no-generate`: model never loaded, `ps-after`/`generate` captures absent | exit 0 `MODEL_OK` | `['check:generate','check:ps-lists-loaded','check:evidence-after-load','capture-parse','log-generate']` → rejected |
| probe-bin-patched | appended-byte copy of the real binary (`--ollama-bin`), `binary-digest` AND `running-exe-digest` neutered; corrupted binary served (`ready`/`version 0.40.11`/`create`/`tags` all true), `/api/generate` → 500 (its llama-server runner not found) | exit 1 `FAIL`; `binary_sha256=aa970610…` | `['verdict','binary-sha','check:generate','check:ps-lists-loaded','check:evidence-after-load','ps-digest']` → rejected |
| probe-tags-seeded-pristine | pristine bytes, work `models/` pre-seeded with baseline run's manifest+blob → pre-create store NOT empty | exit 1 `FAIL` (tool's own honest check) | `['verdict','check:tags-empty-before-create']` → rejected |
| probe-tags-seeded-mut | same seeded world, `tags-empty-before-create` neutered | exit 0 `MODEL_OK` | `[]` → **accepted** |

## Findings

1. **Definitive coverage gap — `tags-empty-before-create` is not re-derived at all.** In
   probe-tags-seeded-mut the accepted receipt's own `captures['tags-empty'].body` lists a foreign
   model (`kama-mt0257b0608e:latest`, the baseline run's nonce) while the check claims
   `passed=true` — and `verify()` still returns `[]`. `verify()` never parses `captures['tags-empty']`;
   its nearest guard `ps-before-not-empty` proves only that nothing was *loaded* pre-generate, not
   that the store was *empty pre-create*. The pristine sensor does catch this world (seeded-pristine
   → `FAIL`), so the lane is guarded only by the tool's honesty here.
2. **`ready`, `running-exe-digest`, `listener-owned`, `evidence-before-load`, `teardown`: no
   independent re-derivation of the check substance.** `verify()` never reads `captures['root']`
   (`"Ollama is running"` is recorded but unused), has no `/proc/<pid>/exe` access post-run (only the
   self-reported `binary_sha256` vs `FROZEN_BIN_SHA`), cannot attribute historical listener ownership
   (post-run `listening_ports()` is a leftover-port proxy only), never reads the `evidence-*.json`
   artifacts or finding strings (only transitively guarded via `ps-before-not-empty`), and trusts the
   self-reported teardown block (`port_closed`/`returncode`/`sigkill_needed` consistency only; the
   post-run port closure is again the proxy).
3. **Re-derivations that do exist and fired:** `binary-sha` (frozen constant) rejects a wrong binary
   even with both tool digest checks neutered (probe-bin-patched); `capture-parse`/`ps-digest` demand
   the loaded-model captures; `log-generate` demands the server's own `POST "/api/generate"` line —
   so `ps-lists-loaded` substance is independently re-derived from captures + log even though the
   check id is not. `version` is re-derived from `captures['version']` body vs `FROZEN_VERSION`
   (code-verified; not fired in probe-bin-patched because the corrupted binary still reports
   `0.40.11` — version and binary-digest are partially redundant guards).
4. **Check `detail` strings are unverified prose**: the neutered `running-exe-digest` detail in
   probe-bin-patched says "sha256 … equals the pinned binary" while `binary_sha256` proves otherwise;
   the counter ignores details.

Fix-shaped suggestions (NOT applied to the lane): one line in `verify()` — reject unless
`json.loads(caps['tags-empty']['body']).get('models') == []` — closes finding 1; parsing
`captures['root']['body'] == 'Ollama is running'` would re-derive readiness from recorded evidence.

## Compliance and restoration evidence

- Lane tree untouched: lane file hashes before == after ==
  `9d1c688b…` (live), `38d1f5d2…` (evidence), `da0948f7…` (pin); tree copy restored to lane bytes
  after every case (`restoration2.json`; final `restored_ok=true`; restored-pristine run green).
- No git/jj commands anywhere; no installs (none needed); disk-guard checked before runs
  (591.3G free on /fast/scratch/hyaku); no writes outside the named out dir, scratch, and nothing in
  /tmp; no process killed (tool tears down its own child; residue scan of `/proc/*/environ` for my
  scratch found none); no credentials/`~/.config`/`~/.omp`/Kagi paths read.
- Evidence: `runs/<case>/{receipt.json,serve.log,result.json}` (pass 2), `results2.jsonl`,
  `driver2.py`, `restoration2.json`; superseded raced pass 1 in `runs-pass1-raced/`.
- Scratch `/fast/scratch/hyaku/kama-r60/MT02ToolCheckNeutering/` removed after archiving.
