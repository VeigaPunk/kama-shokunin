VERDICT: confirm — historical round16 v1 / round17 v2 receipts replay byte-identically through frozen and current gates with their own four recorded pins (10/10 exit 0 VALID, byte-equal to official stdout after path normalization), the frozen-probe mismatch negative control stays INVALID on both gates, and the schema floor is an explicitly intentional, selftest- and knowledge-documented v3-only flag whose absence on the frozen gate is a version boundary, not a hole.

# GateLegacy — legacy-receipt replay attack on the round-18 receipt gate

## Scope and axes

Attack: run historical round16 v1 and round17 v2 receipts against frozen and current
gates with identical four pins; require same exits/VALID text; frozen-probe mismatch
negative control stays INVALID; test the schema floor explicitly as intentional.

- A1 Replay fidelity: 5 legacy receipts × {frozen, current} gates × receipt-own four
  pins → exit and VALID text must match, and must match the official run evidence.
- A2 Negative-control integrity: frozen-probe receipt pinned against the current probe
  must stay INVALID (exit 1) on both gates.
- A3 Schema floor intentionality: `--require-schema v1/v3` behavior on v1/v2 receipts,
  frozen-gate absence of the flag, selftest rows, knowledge text, and downgrade boundary.
- A4 Determinism/drift: rerun matrix identity, official-vs-seat byte equality, gate
  drift between measured commit `c6dc46f` and checkout `1c325b2`, frozen-dir integrity.

## Environment, clone, installs

- Clone: `git clone -q /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/kama-r18-falsify-GateLegacy`
  then `git -C ... switch -q -c seat/GateLegacy 1c325b2e58fcfdc6761f645b44cedfb1d65243e6`;
  `git log --oneline -1` → `1c325b2 round-18: retain measured arms and repair counter classification seams`.
  `git status --short` empty (committed code and evidence only).
- Python: `python3 --version` → `Python 3.14.8`; official `runs/commands.json`
  `"python": "3.14.8 (main, Oct  2 2026, 10:23:31) [GCC 16.2.1 20260810]"` — same interpreter.
- No tools installed; no ports opened; no listeners or processes started. At finish:
  `ss -ltnp | grep -Ei "llama|kama|8080|34113"` → no match; `pgrep -af "llama-server|kama-llamacpp"`
  → no match. No seat-owned listener remains.

## Inputs verified before any gate run

- Legacy receipts byte-identical between clone and live lane
  (`sha256sum` both sides, all IDENTICAL): `round-16/live/receipt.json`
  `076865e5b2de909604c5783d48ec5bf691310763949439d333c42ee5bdbd4669`;
  `round-16/live/receipt-frozen-probe.json` `8dd144ff4cc4a564bffa4bde962218363907e8085b6e2fc78c0a6d66cb18ef8c`;
  `round-17/live/receipt-1.json` `f34afb545db28fc37b2df8179f5872d2e84a20a140a0f3367a9f60d1864702a4`;
  `receipt-2.json` `3df31ddb7aa3ac79b0b268d2f2a5dccba26fd769e81ffd549fda1a79dcc39ad9`;
  `receipt-3.json` `5e2c05114941269256fac353b95d83876e851484a99e47866026d02191e36d90`.
- Recorded four pins (read from each receipt's `model/server/probe/tool.sha256`):
  model `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d` and
  server `b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804` in all five;
  probe `36b64978ee3a3aa29e1b73f04ca5c7ad04a9aee880e7032abfd894fa7b3a29d3` in four
  receipts and `93ee4302718f97862135472411ecf7aa6d5a0dc5cf778cce2c8deefe97a2cd64`
  in the frozen-probe receipt; tool `b8c5e8d402595f3b919ea82f29c87f9a2b5d5c2d88bccffa48f1f8880c2f4fe4`
  (v1) vs `0efd1723b02ef748d720a6036d3ac481b1d5fe9755110999d7c9acaf486c46ac` (v2).
- Pins are real: `sha256sum` of `/home/vgpnk/.local/opt/llama-b11755/llama-server`
  → `b6a31a8e...` (matches), `/home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf`
  → `270cba1b...` (matches); clone `tools/kama-probe.sh` → `36b64978...` (matches).
  Schemas: `kama-llamacpp-live/v1` (round16) / `v2` (round17).
- Frozen gate `sha256 ad6801791f2ada896a7ee188609391aac86185c47320dbf415331869ca9cd2a5`
  (1403 lines); current gate `sha256 c5715641f34fb9bffaf33ca3e0391dd5485a0a914462bf6540e519b566c78335`
  (2115 lines). `.ufo/waves/round-18/frozen/SHA256SUMS` verifies ALL-10-OK in the clone;
  every frozen-dir file byte-identical to the live lane (no DIFFER lines).
- Gate drift: `git diff --stat c6dc46fabc51eb1dd0e91647f2e5e6b2b8ae4d6d 1c325b2e... -- tests/llamacpp-live/check-receipt.py`
  → empty; official `commands.json` `measured_commit: c6dc46fabc51eb1dd0e91647f2e5e6b2b8ae4d6d`.
  So official legacy outcomes were measured by the very bytes I replayed.

## A1 — replay fidelity (executed)

Driver: `falsify/replay.sh` (source at end). Each run:
`python3 <gate> <receipt> --expect-model-sha256 M --expect-server-sha256 S --expect-probe-sha256 P --expect-tool-sha256 T` with the receipt's own four pins. Results (exit / first stdout line):

| receipt | frozen gate | current gate |
|---|---|---|
| round-16 receipt.json | 0 `VALID .../receipt.json` | 0 `VALID .../receipt.json` |
| round-16 receipt-frozen-probe.json | 0 `VALID .../receipt-frozen-probe.json` | 0 `VALID .../receipt-frozen-probe.json` |
| round-17 receipt-1.json | 0 `VALID .../receipt-1.json` | 0 `VALID .../receipt-1.json` |
| round-17 receipt-2.json | 0 `VALID .../receipt-2.json` | 0 `VALID .../receipt-2.json` |
| round-17 receipt-3.json | 0 `VALID .../receipt-3.json` | 0 `VALID .../receipt-3.json` |

stderr empty for all ten (`r-frozen-3.stderr` shown empty; all others identical mode).
Frozen/current same exit and same VALID text per receipt.

Official cross-check (`.ufo/waves/round-18/runs/commands.json`): `legacy-frozen-0..4`
and `legacy-current-0..4` all `exit=0 want=0 ok=True`; my stdout equals official stdout
byte-for-byte after normalizing the clone path prefix to the lane path for all 10 pairs
(sha256 comparison, `byte-match-after-path-normalization=True` ×10).

## A2 — frozen-probe mismatch negative control (executed)

`python3 <gate> round-16/live/receipt-frozen-probe.json --expect-probe-sha256 36b64978...`:

- current gate: `exit=1`, stdout
  `INVALID .../receipt-frozen-probe.json: 1 problem(s)` /
  `  - probe.sha256 93ee4302718f97862135472411ecf7aa6d5a0dc5cf778cce2c8deefe97a2cd64 != expected 36b64978ee3a3aa29e1b73f04ca5c7ad04a9aee880e7032abfd894fa7b3a29d3`
- frozen gate: `exit=1`, same verdict and same single problem line.
- Official `legacy-wrong-probe-pin`: `exit=1 want=1 ok=True`; byte-match after path
  normalization `True`. My `a2-wrong-probe-pin-current.stdout` reproduces it exactly.

Negative control holds on both gates; the mismatch stays attributable to the targeted
probe-pin assertion (single problem, named conjunct).

## A3 — schema floor, explicitly intentional (executed)

Current-gate floor code: `tests/llamacpp-live/check-receipt.py:2088-2101`
(`minimum = {"v1":1,"v2":2,"v3":3}[args.require_schema]; ... problems.append("schema ... is below --require-schema ...")`),
flag declared at `:2063-2066`. Frozen gate `main()` starts at line 1358 with no
`--require-schema` option — the floor is a current-gate addition.

- `a3-r16-v1-require-v1-current` → exit 0 VALID (floor at v1 accepts its own v1 receipt).
- `a3-r16-v1-require-v3-current` → exit 1 INVALID: `schema 'kama-llamacpp-live/v1' is below --require-schema v3`.
- `a3-r17-v2-require-v2-current` → exit 0 VALID; `a3-r17-v2-require-v3-current` →
  exit 1 INVALID: `schema 'kama-llamacpp-live/v2' is below --require-schema v3`.
- `a3-frozen-no-flag` (`--require-schema v3` against frozen gate) → exit 2, stderr
  `check-receipt: error: unrecognized arguments: --require-schema` — version boundary
  of the frozen artifact, not a floor bypass; the frozen gate never claimed the flag.
- Official legacy replay (`run.py:48-55`) correctly passes no floor flag for the five
  historical receipts while the live v3 gates at `run.py:45` always pass
  `--require-schema v3` — consistent with the documented rule
  `corpus/knowledge/llamacpp-loading-lifecycle.md:246-247`:
  "The v3 gate accepts `--require-schema v3` to refuse a receipt declaring a weaker
  schema. Omit it only for intentional historical v1/v2 receipt verification."
- Intentionality evidence in the gate's own selftest:
  `tests/llamacpp-live/check-receipt.py:1874-1881` rows `v1-require-schema-v1` (want 0),
  `v1-require-schema-v2-rejects-v1` (want 1), `v2-require-schema-v3-rejects-v2` (want 1),
  `v3-require-schema-v3` (want 0); `checker-selftest.stdout` exit=0 in official runs.
- Downgrade boundary probe on the real v3 receipt `.ufo/waves/round-18/live/receipt-1.json`
  (pristine VALID under `--require-schema v3`, exit 0): relabel `schema` → v2 →
  without flag exit 0 VALID (documented compatibility lane for historical verification);
  with `--require-schema v3` exit 1 with exactly the floor problem. The floor is
  opt-in by design, and the official v3 invocation always sets it.
- Pin hex-format floor: `--expect-probe-sha256 zz` → exit 1 with
  `probe.sha256 36b649... != expected zz` and `--expect-probe-sha256 'zz' is not 64 lowercase hex chars`
  (validation at `tests/llamacpp-live/check-receipt.py:422-427`).

Verdict on the attack's own hypothesis "floor is not a real design act": refuted.
It is a declared, documented, selftest-pinned, opt-in v3 floor, and every intentional
use path matches the knowledge text.

## Targeted mutants over the legacy receipts (executed, separate fresh set)

All mutations applied in memory against the byte-verified receipts, written, gated,
then byte-exact restored (`assert p.read_bytes() == original` after each; no restore
failure). Green pristine baseline first (exit 0 VALID both receipts). Each mutant is
killed with the targeted conjunct named in the INVALID problem list:

| mutant | mutation | exit | on-target problem line |
|---|---|---|---|
| mut-model-pin | model.sha256 → f*64 | 1 | `model.sha256 ffff... != expected 270cba1b...` (+2 consistent re-derivations: model_unchanged) |
| mut-tool-pin | tool.sha256 → e*64 | 1 | `tool.sha256 eeee... != expected b8c5e8...` |
| mut-schema-unknown | schema → vX | 1 | `schema is 'kama-llamacpp-live/vX', want ... 'v1', 'v2' or 'v3'` (+3 schema-dependent check-set re-derivations) |
| mut-schema-id-changed | schema → v0 | 1 | same schema problem (v0 unknown) |
| mut-not-object | file replaced by `[1, 2, 3]` | 1 | `receipt is not a JSON object` |
| mut-alias-empty | alias → '' | 1 | `alias '' is not a non-empty string` (+8 consistent re-derivations) |
| mut-timestamp | ended_utc → 'not-a-timestamp' | 1 | `ended_utc 'not-a-timestamp' is not a parseable ISO timestamp` |
| mut-envkeys-bad | child_env_keys → `['SECRET_VALUE=1']` | 1 | `child_env_keys element 'SECRET_VALUE=1' is not a bare variable name` (allowlist, values never stored) |
| mut-argv0 | argv[0] → /nonexistent/llama-server | 1 | `argv[0] '/nonexistent/llama-server' != server.realpath ...` |
| mut-check-id | checks[0].id → nonexistent-check | 1 | `required check 'health_ready' is absent` + `unexpected check id 'nonexistent-check' (the schema names exactly 11)` |
| mut-probe-sha-short | probe.sha256 → 'deadbeef' | 1 | probe.sha256 not 64-hex problem |

Extra problems in wider mutants are downstream re-derivations (evidence consistency),
not noise; the targeted conjunct is always present. This is a fresh mutant set,
separate from the named round-17 survivor denominator; 11/11 killed, none survived.

## C1 M7 note (models-capture 200 guard), adjacent to my scope

Re-labeled-v3 variants of `round-17/live/receipt-1.json` with
`captures.models.status=503` (or status absent) and both models checks `passed=None`
are rejected exit 1 with `models_alias_id: captures.models.status 503 != 200 (round-18 RevTriStateDesign)`
(guard at `tests/llamacpp-live/check-receipt.py:905-908` and `:931-933`), matching
`lessons/round-18.md` M7 "v1/v2 unchanged": the same receipt as v2 keeps its v2 grading
semantics. The legacy-compat claim and the v3 tri-state hardening are mutually
consistent; no contradiction found.

## A4 — determinism and drift (executed)

- Full matrix rerun (`falsify/out2` vs `falsify/out`): all exits identical
  (`exits identical across reruns`); stdout differs only by the echoed receipt path
  (absolute vs relative invocation), verdict tokens byte-identical.
- Official-vs-seat byte equality for all 11 official legacy artifacts (A1/A2 above).
- Gate bytes unchanged between the official measured commit and my checkout (above).

## Findings by severity

No defect found in scope. Positive confirmations:

1. **A1 confirmed:** all five historical receipts replay exit 0 `VALID` on both gates
   with identical four pins; byte-equal to official evidence (11/11 artifacts).
2. **A2 confirmed:** frozen-probe mismatch stays INVALID (exit 1) on both gates with a
   single, correctly attributed problem.
3. **A3 confirmed as intentional design:** floor is opt-in `--require-schema v1|v2|v3`
   with versioned minimums at `check-receipt.py:2088-2101`, enforced only when the flag
   is passed, selftest-pinned at `:1874-1881`, documented at
   `corpus/knowledge/llamacpp-loading-lifecycle.md:246-247`, and the official driver
   applies `v3` exactly where the v3 receipts require it (`runs/run.py:45` vs `:48-55`).
4. **A4 confirmed:** rerun-stable; no gate drift between `c6dc46f` and `1c325b2`;
   frozen snapshot sums verified (`SHA256SUMS` ALL-10-OK); receipts byte-identical
   clone-vs-lane.

Residual risk / verification gaps (not findings):

- The compatibility lane (v3 receipt relabeled v2, no flag, still VALID) is intentional
  per the knowledge text, but means a caller who omits the floor flag can accept a
  weakened-schema receipt; the official v3 path never does. This is the documented
  trade-off, not a defect.
- Replay fidelity proves gate agreement on recorded evidence, not producer correctness;
  the receipts' own claims were graded by the round-16/17 official passes, and S055's
  limits already state the gate re-derives internal consistency, not an authenticated
  execution trace (`llamacpp-loading-lifecycle.md:249-251`).
- My 11 targeted mutants are a fresh set, separate from the named round-17 survivors;
  their kills say nothing about unseen mutants (per round-18.md C2 bounded claim).

## Conformance

- All reads/commands/writes used absolute paths or clone-anchored paths; runtime checks
  ran only inside `/tmp/kama-r18-falsify-GateLegacy` (plus read-only sha256sum on the
  installed read-only binary/model and the live lane's committed evidence files).
- No edits outside this report; no jj/git writes in the lane; no official counting
  commands executed; no ports/listeners; no installs (nothing needed beyond system
  python3 3.14.8).
- Receipt mutations were confined to the clone's evidence copies and byte-exact
  restored after each gate call (asserted); production and frozen evidence untouched.

## Experiment source (exact, as executed)

`falsify/replay.sh`:

```bash
#!/usr/bin/env bash
# GateLegacy falsify: replay historical receipts through frozen and current gates
# with each receipt's own four recorded pins (A1), then targeted A2/A3 controls.
set -u
CLONE=/tmp/kama-r18-falsify-GateLegacy
PY=python3
OUT=$CLONE/falsify/out
mkdir -p "$OUT"
run() { # name receipt gate extra...
  local name=$1 rec=$2 gate=$3; shift 3
  "$PY" "$gate" "$rec" "$@" >"$OUT/$name.stdout" 2>"$OUT/$name.stderr"
  local rc=$?
  echo "exit=$rc" >"$OUT/$name.exit"
  printf '%-30s exit=%s  %s\n' "$name" "$rc" "$(head -c 200 "$OUT/$name.stdout")"
}
REC16=$CLONE/.ufo/waves/round-16/live/receipt.json
REC16FP=$CLONE/.ufo/waves/round-16/live/receipt-frozen-probe.json
REC17_1=$CLONE/.ufo/waves/round-17/live/receipt-1.json
REC17_2=$CLONE/.ufo/waves/round-17/live/receipt-2.json
REC17_3=$CLONE/.ufo/waves/round-17/live/receipt-3.json
MODEL_SHA=270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d
SERVER_SHA=b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804
PROBE_CUR=36b64978ee3a3aa29e1b73f04ca5c7ad04a9aee880e7032abfd894fa7b3a29d3
PROBE_FROZEN=93ee4302718f97862135472411ecf7aa6d5a0dc5cf778cce2c8deefe97a2cd64
TOOL16=b8c5e8d402595f3b919ea82f29c87f9a2b5d5c2d88bccffa48f1f8880c2f4fe4
TOOL17=0efd1723b02ef748d720a6036d3ac481b1d5fe9755110999d7c9acaf486c46ac
FROZEN_GATE=$CLONE/.ufo/waves/round-18/frozen/tests_llamacpp-live_check-receipt.py
CURRENT_GATE=$CLONE/tests/llamacpp-live/check-receipt.py

echo "=== A1: five receipts x {frozen,current} gates, receipt-own pins ==="
i=0
for spec in "$REC16 $TOOL16 $PROBE_CUR" "$REC16FP $TOOL16 $PROBE_FROZEN" \
            "$REC17_1 $TOOL17 $PROBE_CUR" "$REC17_2 $TOOL17 $PROBE_CUR" \
            "$REC17_3 $TOOL17 $PROBE_CUR"; do
  set -- $spec; rec=$1; tool=$2; probe=$3
  run "r-frozen-$i" "$rec" "$FROZEN_GATE" \
      --expect-model-sha256 $MODEL_SHA --expect-server-sha256 $SERVER_SHA \
      --expect-probe-sha256 $probe --expect-tool-sha256 $tool
  run "r-current-$i" "$rec" "$CURRENT_GATE" \
      --expect-model-sha256 $MODEL_SHA --expect-server-sha256 $SERVER_SHA \
      --expect-probe-sha256 $probe --expect-tool-sha256 $tool
  i=$((i+1))
done

echo "=== A2: frozen-probe mismatch negative control stays INVALID ==="
run "a2-wrong-probe-pin-current" "$REC16FP" "$CURRENT_GATE" \
    --expect-probe-sha256 $PROBE_CUR
run "a2-wrong-probe-pin-frozen" "$REC16FP" "$FROZEN_GATE" \
    --expect-probe-sha256 $PROBE_CUR

echo "=== A3: schema floor, explicitly intentional ==="
run "a3-r16-v1-require-v1-current" "$REC16" "$CURRENT_GATE" --require-schema v1
run "a3-r16-v1-require-v3-current" "$REC16" "$CURRENT_GATE" --require-schema v3
run "a3-r17-v2-require-v2-current" "$REC17_1" "$CURRENT_GATE" --require-schema v2
run "a3-r17-v2-require-v3-current" "$REC17_1" "$CURRENT_GATE" --require-schema v3
run "a3-frozen-no-flag" "$REC16" "$FROZEN_GATE" --require-schema v3
```

`falsify/mutate.py` (targeted mutants; per-run byte-exact restore asserted):

```python
#!/usr/bin/env python3
"""GateLegacy targeted mutants: each mutation is expected to be killed by the
current gate exactly because of the targeted assertion."""
import json, subprocess, sys
from pathlib import Path
CL = Path('/tmp/kama-r18-falsify-GateLegacy')
GATE = CL / 'tests/llamacpp-live/check-receipt.py'
FROZEN_GATE = CL / '.ufo/waves/round-18/frozen/tests_llamacpp-live_check-receipt.py'
REC16 = CL / '.ufo/waves/round-16/live/receipt.json'
REC17 = CL / '.ufo/waves/round-17/live/receipt-1.json'
MODEL_SHA = '270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d'
SERVER_SHA = 'b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804'
PROBE_CUR = '36b64978ee3a3aa29e1b73f04ca5c7ad04a9aee880e7032abfd894fa7b3a29d3'
TOOL16 = 'b8c5e8d402595f3b919ea82f29c87f9a2b5d5c2d88bccffa48f1f8880c2f4fe4'
TOOL17 = '0efd1723b02ef748d720a6036d3ac481b1d5fe9755110999d7c9acaf486c46ac'
PINS16 = ['--expect-model-sha256', MODEL_SHA, '--expect-server-sha256', SERVER_SHA,
          '--expect-probe-sha256', PROBE_CUR, '--expect-tool-sha256', TOOL16]
PINS17 = ['--expect-model-sha256', MODEL_SHA, '--expect-server-sha256', SERVER_SHA,
          '--expect-probe-sha256', PROBE_CUR, '--expect-tool-sha256', TOOL17]
OUT = CL / 'falsify/out'; OUT.mkdir(exist_ok=True, parents=True)

def gate(gate, rec, pins, extra=None):
    argv = [sys.executable, str(gate), str(rec), *pins, *(extra or [])]
    p = subprocess.run(argv, capture_output=True, text=True, timeout=120)
    return p.returncode, p.stdout, p.stderr

# --- pristine baselines ------------------------------------------------------
prist16 = gate(GATE, REC16, PINS16)
prist17 = gate(GATE, REC17, PINS17)
print(f'pristine r16 current: exit={prist16[0]} head={prist16[1].splitlines()[0] if prist16[1] else ""}')
print(f'pristine r17 current: exit={prist17[0]} head={prist17[1].splitlines()[0] if prist17[1] else ""}')
if prist16[0] != 0 or prist17[0] != 0:
    print('INVALID PRISTINE BASELINE -> INCONCLUSIVE'); sys.exit(2)

original16 = REC16.read_bytes(); original17 = REC17.read_bytes()
results = []
def targeted(name, rec_path, original, mutate, pins, expect_exit, needle):
    p = Path(rec_path)
    d = json.loads(original)
    mutate(d)
    p.write_bytes(json.dumps(d, indent=1).encode() + b'\n')
    try:
        rc, out, err = gate(GATE, p, pins)
    finally:
        p.write_bytes(original)  # byte-exact restore
    assert p.read_bytes() == original, 'RESTORE FAILED ' + name
    verdict = out.splitlines()[0] if out else '(no stdout)'
    killed = rc != 0  # any non-zero exit for a targeted mutation
    ontarget = needle in (out + err)
    results.append((name, rc, verdict, killed, ontarget))
    print(f'{name:34s} exit={rc} killed={killed} on-target={ontarget} :: {verdict}')
    return ontarget and killed

# M1: model pin mismatch must be caught by model.sha256 assertion
targeted('mut-model-pin', REC16, original16,
         lambda d: d.__setitem__('model', {**d['model'], 'sha256': 'f' * 64}),
         PINS16, 1, 'model.sha256 ffff')
# M2: tool pin mismatch
targeted('mut-tool-pin', REC16, original16,
         lambda d: d.__setitem__('tool', {**d['tool'], 'sha256': 'e' * 64}),
         PINS16, 1, 'tool.sha256 eeee')
# M3: schema string corrupted -> unknown schema rejected
targeted('mut-schema-unknown', REC17, original17,
         lambda d: d.__setitem__('schema', 'kama-llamacpp-live/vX'),
         PINS17, 1, "schema is 'kama-llamacpp-live/vX'")
# M4: schema id changed to v0 (same mutation the gate's own selftest uses)
targeted('mut-schema-id-changed', REC17, original17,
         lambda d: d.__setitem__('schema', 'kama-llamacpp-live/v0'),
         PINS17, 1, 'kama-llamacpp-live/v0')
# M5: top-level array (not a JSON object) -> gate must reject; restore bytes
def targeted_bytes(name, rec_path, original, raw_bytes, pins, needle):
    p = Path(rec_path)
    p.write_bytes(raw_bytes)
    try:
        rc, out, err = gate(GATE, p, pins)
    finally:
        p.write_bytes(original)
    assert p.read_bytes() == original, 'RESTORE FAILED ' + name
    verdict = out.splitlines()[0] if out else '(no stdout)'
    killed, ontarget = rc != 0, needle in (out + err)
    print(f'{name:34s} exit={rc} killed={killed} on-target={ontarget} :: {verdict}')
    return killed and ontarget
targeted_bytes('mut-not-object', REC17, original17, b'[1, 2, 3]\n', PINS17,
               'receipt is not a JSON object')
# M6: alias emptied (scalar floor)
targeted('mut-alias-empty', REC17, original17,
         lambda d: d.__setitem__('alias', ''), PINS17, 1, 'alias')
# M7: started/ended timestamp corrupt
targeted('mut-timestamp', REC17, original17,
         lambda d: d.__setitem__('ended_utc', 'not-a-timestamp'),
         PINS17, 1, 'ended_utc')
# M8: child_env_keys allowlist violation
targeted('mut-envkeys-bad', REC17, original17,
         lambda d: d.__setitem__('child_env_keys', ['SECRET_VALUE=1']),
         PINS17, 1, 'child_env_keys element')
# M9: argv[0] detached from server.realpath
targeted('mut-argv0', REC17, original17,
         lambda d: d.__setitem__('argv', ['/nonexistent/llama-server', *d['argv'][1:]]),
         PINS17, 1, 'argv[0]')
# M10: check id outside schema-named set
targeted('mut-check-id', REC17, original17,
         lambda d: d['checks'].__setitem__(0, {'id': 'nonexistent-check', **{k: v for k, v in d['checks'][0].items() if k != 'id'}}),
         PINS17, 1, 'unexpected check id')
# M11: require-schema v3 floor vs v2 receipt (explicitly intentional floor)
rc, out, err = gate(GATE, REC17, PINS17, extra=['--require-schema', 'v3'])
floor_hit = rc == 1 and 'is below --require-schema' in (out + err)
print(f'{"a3-floor-v3-on-v2":34s} exit={rc} floor_hit={floor_hit}')
# same on frozen gate (flag must be unknown there -> argparse exit 2)
rc, out, err = gate(FROZEN_GATE, REC17, PINS17, extra=['--require-schema', 'v3'])
frozen_flag = rc == 2
print(f'{"a3-floor-flag-frozen":34s} exit={rc} frozen-argparse-reject={frozen_flag}')
# M12: probe sha absent -> not hex64 (floor on digest form)
targeted('mut-probe-sha-short', REC16, original16,
         lambda d: d['probe'].__setitem__('sha256', 'deadbeef'),
         PINS16, 1, 'probe.sha256')
print('=== end mutants ===')
```

Additional inline probes (schema-downgrade boundary, M7 guard, pin-format floor) were
single-purpose `python3 - <<EOF` snippets over the same gate/receipt paths, using the
same gate invocation pattern with per-run byte-exact restore; their full argv/stdout
are quoted in the A3/M7 sections above.
