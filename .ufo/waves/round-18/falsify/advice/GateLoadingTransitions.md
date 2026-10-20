VERDICT: partial — a body-only mutation is rejected, but repeat/dedup rewrites can still pass.

# GateLoadingTransitions — Round 18 FALSIFY

## Findings, by severity

### P2 — Gate accepts adjacent duplicate transition signatures as distinct rows, enabling repeat/dedup rewriting

`tests/llamacpp-live/check-receipt.py:1219-1221,1262-1265` sums counts for repeated transition digests but does not reject two adjacent rows with the same `(path,status,error,body_sha256)` signature. The producer does coalesce adjacent equal signatures in `tools/kama-llamacpp-live.py:566-570` before it retains distinct loading bodies (`:580-594`). Consequently the gate accepts a non-canonical, tool-impossible representation if the repeat/body mirrors are rewritten together.

Executed compound-forgery experiment (not the strict one-field mutation): the green baseline contained two distinct byte encodings of the same exact JSON envelope, two corresponding transition rows, and two retained bodies. It was `VALID`. The forged copy rewrote the second row to the first row's body/hash, removed the second retained-body entry, raised the remaining body's repeats from 44 to 45, and updated the mirrored total/distinct counts. It left two adjacent identical transition signatures rather than the producer's single coalesced row. The forged copy was also `VALID` (exit 0). This proves the gate accepts the repeated-row representation; it does **not** directly demonstrate concealment of a non-exact second body, because the green baseline's two bodies were both exact. `[INFERENCE]` The same unchecked rewrite could relabel an unretained distinct response as a repeat if a forger rewrote all receipt mirrors consistently.

Reproduction source and observed outputs are included below. Relevant source anchors: producer coalescing `tools/kama-llamacpp-live.py:566-570`; gate accumulation and count-only cross-check `tests/llamacpp-live/check-receipt.py:1219-1221,1262-1274`.

### P3 — Repeat totals are self-consistent receipt data, not independently authenticated observations

A separate mutation inflated both the transition-row and retained-body repeats from 44 to 100, and updated `observed.total_503_responses` from 45 to 101. The gate returned `VALID` (exit 0). Conversely, zeroing both repeat values and the mirrored total also returned `VALID`. One-sided repeat changes are rejected by the count/mirror checks, but coordinated changes have no independent request-count source in the receipt. This limits confidence in reported response totals; it does not falsify the envelope predicate itself.

### P3 — Additional recorded transition metadata is not re-derived by this gate

Independent receipt mutations of the 503 row's `headers`, `t_ms`, `phase`, and `error` each returned `VALID` (exit 0); e.g. `Server: llama.cpp` → `nginx`, `t_ms` → 999999, phase `models` → `health`, or error `null` → `ConnectionRefusedError`. The gate's v3 loading path validates 503-row body/envelope, body digest, repeats type/count, truncation flags, path/status consistency, and first-body matching, but does not check these metadata fields (`check-receipt.py:1195-1287`). It also accepts a corrupted non-503 transition body/hash (row 0 ConnectionRefused or row 2 HTTP 200) while leaving the ready captures unchanged. These are receipt-integrity gaps adjacent to, but outside, the assigned 503-body-only mutation; none of these mutations altered the gate's loading-envelope pass decision.

## Confirmed kills for the assigned attack

- **Strict single-field attack:** starting from the real green `receipt-1.json`, changed only `transitions[1].body` to `{"error":{}}`. The stored transition SHA, `loading_503`, and `loading_503_bodies` were verified unchanged. The gate returned `INVALID` (exit 1): `transitions /v1/models 503 row 0 does not carry the exact loading envelope`; `loading transition 0 body_sha256 does not match its stored body`; `loading_503 does not match the first /v1/models 503 transition`; and `check 'loading_envelope_graded' passed True != re-derived False`.
- **Two-row control:** built a separate green receipt with two distinct exact-envelope encodings. It returned `VALID`. Mutating only its second 503 transition body while the retained-body list stayed unchanged returned `INVALID` both with the old SHA (exact-envelope and digest mismatch) and with a recomputed SHA (exact-envelope and transition/body coverage mismatch). This confirms every selected `/v1/models` 503 row is graded, not only the first.
- **SHA:** SHA-only tampering on a transition row returned `INVALID` (`loading transition 0 body_sha256 does not match its stored body`); a body-only mutation with stale SHA was rejected as above. Updating a changed body and its row SHA while leaving retained bodies exact was also rejected by the exact-envelope/coverage checks.
- **Over-cap/truncation:** setting either `body_over_cap: true` or `body_read_truncated: true` on a 503 transition row returned `INVALID`, with `transitions /v1/models 503 row 0 is truncated` and the derived-check mismatch.
- **Drop-257:** a receipt with 257 distinct `/v1/models` 503 transition digests, 256 retained bodies and `loading_bodies_dropped: 1` returned `INVALID`, including `loading_envelope_graded cannot pass with an unretained loading body`. The silent-drop variant (`dropped: 0`) also returned `INVALID` because the gate re-derived an omission count of 1. The built-in selftest contains `v3-silently-dropped-257th-loading-body` (`check-receipt.py:1967-2000`) and passed.
- **Retained-body mutation:** changing a retained loading-body entry to a non-envelope and recomputing its digest returned `INVALID`; duplicate retained-body digests were also rejected.
- **Tool retention check (bounded synthetic):** a direct `readiness_loop` exercise with two distinct 503 bodies had exact transition/body digest-count equality on the pristine module. A copied mutant retained only the first body without incrementing `dropped`; the transition counts still had both digests, the retained-body counts only one, so the coverage equality failed. This was a function-level synthetic loopback exercise (ownership predicate stubbed true), not a full producer run.

## Reproduction source and exact commands

Scratch clone was made at commit `1c325b2e58fcfdc6761f645b44cedfb1d65243e6`. No tracked source file in the clone was changed. The input receipts and all mutated JSON were read/written only under `/tmp/kama-r18-falsify-GateLoadingTransitions`; the original receipt files were untouched.

### Strict one-field body mutation

Exact source used to generate the strict mutant:

```python
import json, pathlib, copy
root = pathlib.Path('/tmp/kama-r18-falsify-GateLoadingTransitions')
r = json.loads((root / '.ufo/waves/round-18/live/receipt-1.json').read_text())
mut = copy.deepcopy(r)
mut['transitions'][1]['body'] = '{"error":{}}'
out = root / '.ufo/waves/round-18/falsify/seat/m53-one-body-field-only.json'
out.write_text(json.dumps(mut, separators=(',', ':')))
print('transitions[1].body changed; sha retained:',
      mut['transitions'][1]['body_sha256'] == r['transitions'][1]['body_sha256'])
print('loading_503 unchanged:', mut['loading_503'] == r['loading_503'])
print('loading_503_bodies unchanged:',
      mut['loading_503_bodies'] == r['loading_503_bodies'])
```

Observed source assertions:

```text
transitions[1].body changed; sha retained: True
loading_503 unchanged: True
loading_503_bodies unchanged: True
```

Exact gate command (pins are unchanged from the official invocation):

```sh
python3 /tmp/kama-r18-falsify-GateLoadingTransitions/tests/llamacpp-live/check-receipt.py \
  /tmp/kama-r18-falsify-GateLoadingTransitions/.ufo/waves/round-18/falsify/seat/m53-one-body-field-only.json \
  --require-schema v3 \
  --expect-model-sha256 270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d \
  --expect-server-sha256 b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804 \
  --expect-probe-sha256 36b64978ee3a3aa29e1b73f04ca5c7ad04a9aee880e7032abfd894fa7b3a29d3 \
  --expect-tool-sha256 dc036d7dcfe2933827c07f8bc0dedba68a24f7b099309871f6cb25ccb811a04b
```

Output/exit:

```text
INVALID .../m53-one-body-field-only.json: 4 problem(s)
  - transitions /v1/models 503 row 0 does not carry the exact loading envelope
  - loading transition 0 body_sha256 does not match its stored body
  - loading_503 does not match the first /v1/models 503 transition
  - check 'loading_envelope_graded' passed True != re-derived False
exit=1
```

### Repeat/dedup survivor experiment source

The following reproduces the green two-body baseline and the compound repeat/dedup rewrite. `B` differs only in JSON formatting, so both baseline bodies parse to the same exact envelope while their byte hashes differ.

```python
import json, hashlib, copy, pathlib
root = pathlib.Path('/tmp/kama-r18-falsify-GateLoadingTransitions')
out = root / '.ufo/waves/round-18/falsify/seat'
r = json.loads((root / '.ufo/waves/round-18/live/receipt-1.json').read_text())
def sha(s): return hashlib.sha256(s.encode()).hexdigest()
def check(x): return next(c for c in x['checks']
                         if c['id'] == 'loading_envelope_graded')
A = r['transitions'][1]['body']
B = json.dumps(json.loads(A), separators=(', ', ': '))
rowB = copy.deepcopy(r['transitions'][1])
rowB.update(t_ms=r['transitions'][1]['t_ms'] + 1,
            body=B, body_sha256=sha(B), repeats=0)
base = copy.deepcopy(r)
base['transitions'].insert(2, rowB)
base['loading_503_bodies'] = [
    {'path':'/v1/models','body_sha256':r['transitions'][1]['body_sha256'],
     'body':A,'repeats':44},
    {'path':'/v1/models','body_sha256':sha(B),'body':B,'repeats':0}]
check(base)['observed'].update(distinct_bodies=2,
                               total_503_responses=46,
                               all_exact=True, exact=True)
(out/'m49a-two-exact-bodies-pristine.json').write_text(
    json.dumps(base, separators=(',',':')))
mut = copy.deepcopy(base)
mut['transitions'][2]['body'] = A
mut['transitions'][2]['body_sha256'] = sha(A)
mut['loading_503_bodies'] = [
    {'path':'/v1/models','body_sha256':sha(A),'body':A,'repeats':45}]
check(mut)['observed'].update(distinct_bodies=1,
                              total_503_responses=46,
                              all_exact=True, exact=True)
(out/'m49b-repeat-launder-second-body.json').write_text(
    json.dumps(mut, separators=(',',':')))
```

Both files were run through the same pinned gate command as above, substituting the receipt path:

```text
m49a-two-exact-bodies-pristine: VALID ... exit=0
m49b-repeat-launder-second-body: VALID ... exit=0
```

A separate coordinated repeat inflation (`transitions[1].repeats=100`, `loading_503_bodies[0].repeats=100`, observed total=101) also returned `VALID` exit 0. Uncoordinated edits were rejected (e.g., changing only the transition repeats to 45 returned `INVALID`; changing both repeat fields while leaving observed total at 45 returned `INVALID: observed.total_503_responses 45 != re-derived 46`).

### Drop-257 receipt construction

The receipt-level experiment created 257 distinct body encodings, inserted 257 corresponding 503 transition rows, retained the first 256, and set `loading_bodies_dropped=1`. The mutation loop was:

```python
first = copy.deepcopy(r['transitions'][1])
rows, bodies = [], []
for i in range(257):
    body = ENVELOPE + (' ' * i)
    digest = hashlib.sha256(body.encode()).hexdigest()
    row = copy.deepcopy(first)
    row.update(t_ms=10+i, body=body, body_sha256=digest, repeats=0,
               body_read_truncated=False, body_over_cap=False)
    rows.append(row)
    if i < 256:
        bodies.append({'path':'/v1/models','body_sha256':digest,
                       'body':body,'repeats':0})
receipt['transitions'] = [old[0], *rows, old[2], old[3]]
receipt['loading_503_bodies'] = bodies
receipt['loading_bodies_dropped'] = 1
```

The gate rejected this with `loading_503_bodies digests/repeats do not cover...`, `loading_envelope_graded cannot pass with an unretained loading body`, and `check 'loading_envelope_graded' passed True != re-derived False` (exit 1). Changing only the dropped field to 0 was also rejected: `loading_bodies_dropped 0 != re-derived omission count 1` (exit 1).

## Verification and limits

- Re-gated the three official v3 receipts in the clone with the exact four pins and `--require-schema v3`: receipts 1, 2, and 3 each printed `VALID` and exited 0. Official raw `runs/commands.json` records the same server `/home/vgpnk/.local/opt/llama-b11755/llama-server`, model `stories260K.gguf`, model SHA `270cba…d256d`, alias `kama-r18-live`, and live/gate exit 0 for all three. This verifies one canonical runtime identity from retained evidence; I did not launch the canonical server in this seat.
- Gate selftest in clone: `selftest: 5 VALID and 1 NOT-EVALUATED receipts accepted; 61 mutations + unreadable case rejected` (exit 0). It contains the non-exact transition and drop-257 mutations. Tool selftest: `selftest: ok; closed tcp6 listeners ::1:45261, ::ffff:127.0.0.1:46537` (exit 0).
- C1 measure selftest in clone: `selftest: 38/38 cases passed` (exit 0). Also ran the clone's C1 measure command with controls/frozen/current inputs: exit 0, no warnings, both arms no timeout/no leaked processes; after-arm counts: accepted_bad=0, good_rejected=0, misclassified=0, uncontrolled_checks=0, inconclusive=0. Before arm retained accepted_bad=5, good_rejected=1, misclassified=1; not silently erased. This is supplementary to the assigned gate attack.
- Synthetic readiness-loop check exercised two distinct 503 encodings; pristine had two transition/body digests with equal count maps, while a copied mutant retaining only one body without incrementing dropped had unequal count maps. It was not a full CLI run and stubbed `port_owned_by=True`; it does not verify real cap-257 tool behavior.
- LSP verification unavailable: `read xd://lsp` returned `No such tool` (the mounted device list did not include LSP). Source inspection here is direct text evidence, not LSP semantic proof.
- No port 8080, 34113, or registered consumer port was used. Gate/mutation receipt checks were offline. Tool selftest used its own ephemeral IPv6 listeners and reported closure; the synthetic loopback server was stopped in the same command. C1 measure reported `leaked_processes: []` on both arms. Final process/listener scan found no seat-path process or listener match. Other seats' unrelated listeners were not touched.
- No tools installed or updated.
- No production or frozen files edited. Mutated receipts and the mutant tool copy were confined to the seat clone; the clone's tracked `kama-llamacpp-live.py` SHA remained identical to `HEAD`. The clone and scratch are removed after report publication.
- Not exercised: a real canonical runtime emitting >256 distinct 503 bodies (impractical with the fixed b11755 server); direct same-identity rerouting beyond the retained controls; byte-authentication of tool-attested repeats/timing/headers. The gate's selftests establish fail-closed receipt grading for the specified body/sha/truncation/drop attacks, not a general receipt-authentication oracle.

## Evidence hashes

- Pinned commit: `1c325b2e58fcfdc6761f645b44cedfb1d65243e6`
- `tools/kama-llamacpp-live.py`: `dc036d7dcfe2933827c07f8bc0dedba68a24f7b099309871f6cb25ccb811a04b`
- `tests/llamacpp-live/check-receipt.py`: `c5715641f34fb9bffaf33ca3e0391dd5485a0a914462bf6540e519b566c78335`
- `tools/kama-probe.sh`: `36b64978ee3a3aa29e1b73f04ca5c7ad04a9aee880e7032abfd894fa7b3a29d3`
- Server binary: `b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804`
- Model: `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d`
- Official receipts 1/2/3: `e616f67e2e2bec196402f56ed3a45fb68f78c9f4e927f0ea7d8acd170caf6d75`, `86233de314e202c57b738867cfe5a46f7f1680d0fa11c826f315320ea492ba91`, `5c414178af616969a28fb8ac0bb970f505af722fb8388bf3c7ba10f6d8bfeff0`
- Strict one-body mutant receipt: `1ddbee535d285f8da8c2f253533b60d726769e115adab80cc8a0d86c43a51eea`
- Repeat-launder baseline / mutant receipts: `00414951ce7ba18b4d27f1e3be3c8d043370a4488c1f7acffd4e720653605a6d` / `e10fc2316704a0bf94bacf1f986a1a68c35140706dad2f11b4666cf6cd878175`
- Clone C1 measure stdout/stderr: `77387032a16531c394978c21b99860404f86eccea75e9a5d20f783cdf61a26d7` / empty-output SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
