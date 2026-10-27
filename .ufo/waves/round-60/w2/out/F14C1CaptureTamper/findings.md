# F14C1CaptureTamper — C1 capture status/body/hash tamper matrix

Attack target: frozen claim C1-r60 predicate + tools/round60-c1-counter.py `verify()` (tip HEAD 8f5f4e334fbecc2251c331f7301a0e8c01805391; worktree byte-identical, `git status --porcelain` clean on tools/registry; note: freeze.txt `base=ec3b0d58` predates the tools — that is the do-nothing control tip, not the measured tip).

## Method
- Fresh lane-owned live run with the tip's `tools/kama-ollama-live.py` (git archive of HEAD into scratch; fixture `~/.cache/kama-shokunin/models/stories260K.gguf`, nonce `f14cap01`, port 49143): exit 0, verdict MODEL_OK, 11 captures all status 200, teardown returncode 0, no stray process. Disk guard before heavy work: /fast 593.7G free, 27% used. TMPDIR under scratch; scratch removed after copying. No installs. Lane read-only except my out dir.
- Baseline `verify(receipt, run_dir, nonce)` = `[]` (accepted), so every verdict below is measured against a genuinely accepted receipt.
- 109 deepcopy-mutated receipts probed through the frozen `verify()`; "EVADES" = verify returns `[]` (receipt accepted unchanged as a green C1 receipt).

## Result matrix (per-capture probes, 11 captures × 9 kinds = 99; + 6 receipt-level; + 4 digest)

| Mutation (applied to a copied receipt) | tags | ps-after | ps-before | version | other 7 | total |
|---|---|---|---|---|---|---|
| `status` → 404 | EVADES | EVADES | EVADES | EVADES | EVADES | 11/11 |
| `status` → 500 | EVADES | EVADES | EVADES | EVADES | EVADES | 11/11 |
| `status` → `"200"` (string) | EVADES | EVADES | EVADES | EVADES | EVADES | 11/11 |
| `status` → None / key removed | EVADES | EVADES | EVADES | EVADES | EVADES | 11/11 |
| body edit, no rehash | reject | reject | reject | reject | reject | 0/11 (`capture-sha:<name>`) |
| body edit + sha256 recomputed | EVADES | EVADES | EVADES | EVADES | EVADES | 11/11 |
| `sha256` corrupted only | reject | reject | reject | reject | reject | 0/11 |
| inner `name` field mutated | EVADES | EVADES | EVADES | EVADES | EVADES | 11/11 |
| capture deleted | reject | reject | reject | reject | **EVADES** | 7/11 evade (`capture-parse` only on the 4 parsed) |

Receipt-level:
- `status` set to 404 / `"200"` on ALL captures at once: EVADES. Status key deleted from all: EVADES.
- Add attacker capture `{"attacker": {status 200, body+sha consistent}}`: EVADES — the capture set is not pinned to any name list.
- Delete all 7 semantically-free captures (root, show, generate, tags-empty, v1-model-single, v1-models, v1-models-empty): EVADES — a receipt holding only the 4 parsed captures still verifies.
- Swap version capture body/status/sha with root's: reject (`capture-parse`).

Semantic body tamper with consistent rehash:
- **tags + ps-after `digest` both → 64×`a`, both rehashed: EVADES.** The verifier's model-identity join (`tags.digest == ps-after.digest`, 64-hex shape) is intra-receipt only; it is never bound to the manifest/blob checks (`manifest`/`manifest-layer`/`blob-sha` compare the work dir against FROZEN_MODEL_SHA independently). A receipt claiming a different nonce-model digest verifies green alongside an untouched frozen-model manifest. Single-sided digest swap: reject (`ps-digest`) — the cross-check catches inconsistency, not falsehood.
- version body → `{"version":"9.9.9"}` rehashed: reject; ps-before body → one model rehashed: reject (the only two semantic body checks that bite).

## Is capture status bound to predicates? — NO
- `grep -c status tools/round60-c1-counter.py` = 0 occurrences: `verify()` never reads `status` (or inner `name`). Capture protection = body↔sha256 equality + JSON semantics of exactly 4 captures.
- C2: `receipt_caps()` (tools/round60-c2-counter.py:163-172) also checks body-sha only; its own tamper control mutates body with a trailing space (line 278). The W1 registry row artifacts (.ufo/waves/round-60/w1/out/*/rows.tsv) contain no predicate reading capture `status` — the two grep hits are prose in not-observable reasons.
- The lane's own documented statement DOES assert status: corpus/knowledge/ollama-live-lifecycle.md:23-30 ("`root` | status 200", "`generate` | status 200 and `done: true`", …). So the documented surface includes per-capture status codes, but no instrument binds them: a receipt whose every capture claims 404/None verifies green against both C1 and C2.
- Runtime-only binding: kama-ollama-live.py binds status at receipt-write time (`ready` requires HTTP 200 + exact body), but `verify()` trusts `checks[].passed` booleans without re-derivation (W1 seats MT03/A09 established the boolean-trust gap; this seat shows the status field specifically is outside even the tamper controls' reach — the frozen 3 tampers touch only body-no-rehash, binary_sha256, port).

## Verdict
C1-r60's "independent verifier re-derives … the nonce-named model from the capture bodies" and the tamper control family do NOT survive this axis: 79 of 109 mutations evade verify(). Highest-impact: (1) wholesale capture-status unbinding vs the lane's own documented "status 200" statements; (2) intra-receipt-only model digest join admits a consistent fake model identity; (3) capture set unpinned (add/delete of non-parsed captures accepted). Attack-only; no lane files touched.

Evidence: fresh honest receipt copy `receipt-f14cap01.json` (MODEL_OK, port 49143) in this dir; harness/mutations reproduced from it + tip counter against a scratch work dir (serve.log + models/manifests + blobs required for the run_dir checks; not reproducible from the committed receipt alone since its run dir is gone — only receipt.json + serve-lines.txt remain in .ufo/waves/round-60/live/).
