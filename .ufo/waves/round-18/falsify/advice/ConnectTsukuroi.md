VERDICT: partial — the host boundary holds (zero package/service commands, pacman pause intact, preexisting artifacts unmodified), but the delivered four-pin gate binds only the 17,864-byte `llama-server` loader stub, not the 7,671,544-byte `libllama-server-impl.so` that implements the lifecycle; three fresh consistent-swap receipts print VALID.

Seat: KamaR18.ConnectTsukuroi-3. Clone `/tmp/kama-r18-falsify-ConnectTsukuroi-3` at `1c325b2e58fcfdc6761f645b44cedfb1d65243e6`. Scope: `tsukuroi-shokunin/SKILL.md`, `tsukuroi-shokunin/corpus/README.md` (+ `corpus/knowledge/package-state-plane.md` for the foreign definition), kama round-18 lesson/SCORECARD/runs/live/tools. No pacman, service, boot or update command; no install; no listener. Scratch removed before finish.

## Axes

- **Operability (C1, 8):** subject identity of the live preexisting-install capability. The move makes "the installed b11755 tree is the subject" checkable instead of prose; no new engine, no score inflation.
- **Calibration (C2, 7, lowest):** the statement→mutant→detector relationship for the lane's own install-identity claim. A named mutant (`install-tree-sha-tampered`) exists but is weaker than its name implies.
- **Host constraint:** pacman paused / no agent package action (tsukuroi `SKILL.md:1853`, `corpus/README.md:116–117`), preexisting install read-only. The move must not repair, install, or measure the host.

## Evidence

### 1. The host boundary itself is respected

- Official commands: `python3 -c` over `.ufo/waves/round-18/runs/commands.json` → `commands 32`, `host-mutating/package commands: []` (no `pacman`, `systemctl`, `sudo`, `mkinitcpio`, `yay` in any argv).
- `tsukuroi-shokunin/SKILL.md:1851–1853`: "No agent install, upgrade, downgrade or service action is authorized. … all pacman transactions remain paused under the current operator ruling."
- `tsukuroi-shokunin/corpus/README.md:116–117`: "`BLOCKED_FOR_AGENT_PACKAGE_ACTION`: the pending partial-upgrade assessment is operator-only, no agent package or service action is authorized".
- The preexisting subject is outside tsukuroi's measured plane: `corpus/knowledge/package-state-plane.md:42–45` defines the host inventory as `pacman -Q`/`-Qe`/`-Qm`/`-Qme`; `pacman -Qm` cannot see `~/.local/opt/llama-b11755` (51 files). So kama's receipt digest is the only machine-checkable identity of the C1 subject; tsukuroi cannot supply one.
- Read-only verification of the subject (executed):
  ```
  sha256sum ~/.local/opt/llama-b11755/llama-server
  b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804  /home/vgpnk/.local/opt/llama-b11755/llama-server
  sha256sum ~/.local/opt/llama-b11755/libllama-server-impl.so
  e404b91a81c9ab65756b6a57b97b42115a5f429c5060c4b7f0d717ca595b59ed  /home/vgpnk/.local/opt/llama-b11755/libllama-server-impl.so
  sha256sum ~/.cache/kama-shokunin/models/stories260K.gguf
  270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d  /home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf
  stat: 17864 launcher (0755), 7671544 impl (0755), both vgpnk:vgpnk — "read-only" is procedural, not mode-enforced.
  ```
  No modification was made. All three committed receipts record the same launcher, impl and model digests and `outcome: pass`.

### 2. The pin stops at the loader stub

- `readelf -d ~/.local/opt/llama-b11755/llama-server`:
  ```
  (NEEDED) Shared library: [libllama-server-impl.so]
  (RUNPATH) Library runpath: [$ORIGIN]
  ```
  The 17,864-byte pinned file is a loader; the lifecycle checks (`/health` body, `/v1/models` 503 envelope, graceful exit) are compiled into the 7.67 MB impl.
- Producer: `tools/kama-llamacpp-live.py:1008–1014` exposes `--server` and an expected `--model-sha256` only; `:1208–1214` raises `SetupError('model-digest-mismatch')` for a model mismatch, then `:1216–1234` records `server.sha256`, `install_tree`, `install_tree_sha256`, `server_impl_sha256` with no expected-value comparison. Model identity is a precondition; server identity is not.
- Gate: `tests/llamacpp-live/check-receipt.py:349–352` compares `--expect-server-sha256` to `server.sha256` only; `:372–380` recomputes `install_tree_sha256` over the receipt's *own* members; `:381–383` only shape-checks `server_impl_sha256` (`check_digest(..., allow_none=True)`).
- Official runner: `.ufo/waves/round-18/runs/run.py:45` passes exactly four pins — model, `sha(server)` (launcher), probe, tool. No impl or tree pin exists in the runner or in `c1/measure.py`/`c2/survivors.py` (grep: no `server_impl`/`install_tree` matches).

### 3. Fresh mutants survive the exact official gate invocation (executed)

Green pristine and three consistent forgeries, using the same flags as `live-gate-1` in `commands.json`:

```
$ python3 tests/llamacpp-live/check-receipt.py .ufo/waves/round-18/live/<f>.json \
    --require-schema v3 \
    --expect-model-sha256 270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d \
    --expect-server-sha256 b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804 \
    --expect-probe-sha256 36b64978ee3a3aa29e1b73f04ca5c7ad04a9aee880e7032abfd894fa7b3a29d3 \
    --expect-tool-sha256 dc036d7dcfe2933827c07f8bc0dedba68a24f7b099309871f6cb25ccb811a04b

=== receipt-1.json ===      VALID .ufo/waves/round-18/live/receipt-1.json      exit=0
=== mutA-implonly.json ===  VALID .ufo/waves/round-18/live/mutA-implonly.json  exit=0
=== mutB-treeswap.json ===  VALID .ufo/waves/round-18/live/mutB-treeswap.json  exit=0
=== mutC-rpcswap.json ===   VALID .ufo/waves/round-18/live/mutC-rpcswap.json   exit=0
```

Mutants (launcher sha unchanged in all three; only the impl/tree identity changes):

```python
import json, hashlib, copy
def tree_sha(t):
    return hashlib.sha256(''.join(f'{n} {t[n]}\n' for n in sorted(t)).encode()).hexdigest()
src = json.load(open('.ufo/waves/round-18/live/receipt-1.json'))
# A: impl field only
a = copy.deepcopy(src); a['server']['server_impl_sha256'] = 'a'*64
# B: consistent swap of the implementation .so + recomputed combined digest
b = copy.deepcopy(src); b['server']['install_tree']['libllama-server-impl.so'] = 'b'*64
b['server']['install_tree_sha256'] = tree_sha(b['server']['install_tree'])
b['server']['server_impl_sha256'] = 'b'*64
# C: consistent swap of a different executable tree member
c = copy.deepcopy(src); c['server']['install_tree']['ggml-rpc-server'] = 'c'*64
c['server']['install_tree_sha256'] = tree_sha(c['server']['install_tree'])
```

- A survives because `server_impl_sha256` is shape-only.
- B survives because `--expect-server-sha256` is the launcher and the tree is self-recomputed; this is the genuine-run case too: swapping only the `.so` leaves the launcher digest at `b6a3…`, so a real run on a swapped install passes the official gate and is reported as a pinned-subject pass.
- C survives for the same reason; `ggml-rpc-server` is not lifecycle-relevant, so C is visible but bounded.
- Producer precondition pattern exists but only for the model: `python3 tools/kama-llamacpp-live.py … --model-sha256 000…0` → `exit=2`, `outcome setup-error`, `internal_fault None`, `checks 0`, `server.sha256 None` (raised before hashing the server and before `pick_port`; no spawn, no listener).

### 4. The gate's own named mutant is weaker than its name

`tests/llamacpp-live/check-receipt.py:1787–1788`:
```python
mut("install-tree-sha-tampered",
    lambda r: r["server"].update(install_tree_sha256="0" * 64))
```
This zeroes the recorded digest, so the `:378–379` self-recomputation rejects it. It never exercises a *consistent* swap. The fixture at `:1511–1517` already models the launcher/impl split (`SERVER_SHA`, `IMPL_SHA`), yet no case swaps `IMPL_SHA` consistently. The detector proves the receipt agrees with itself, not that the receipt names the lane's install.

### 5. Claim proximity

- `corpus/lessons/round-18.md:53` (S055): "Three v3 runs on the real pinned fixture evaluate and pass, with four-pin schema-floor validation". Literally four flags, but the server pin covers 1 of 51 tree members — the loader — so the "pinned fixture" reading is materially stronger for the model (one fully pinned 1.18 MB file) than for the server.
- `SKILL.md` round-18 gate row: "Pins identify bytes; the receipt is still self-reported, not authenticated execution." Accurate as written; the bytes identified for the server are not the implementing bytes.
- `corpus/knowledge/llamacpp-loading-lifecycle.md:107` says the 51-file tree is "hashed", not pinned — accurate; it is the gate's named mutant and the four-pin wording that overstate the binding.

## Affected axes

- **Calibration (C2) — improves.** Adds a named statement→mutant→detector row ("the receipt's subject is the lane-pinned implementation, not any self-consistent `llama-server`") and replaces the self-consistency-only reading of `install-tree-sha-tampered` with the consistent-swap witness actually executed above.
- **Operability (C1) — improves without new capability.** The preexisting-install boundary becomes machine-checkable; a swapped implementation can no longer be counted as a pass on the pinned subject. Same tool, same checks, same 11 evaluated checks.
- **No harm:** schema v3 unchanged; all three committed receipts already carry `server_impl_sha256 e404b91a…` and `install_tree_sha256 6c216313…` (verified for receipts 1–3), so the pins are green with no re-run; optional flags keep legacy/v1/v2 callers unchanged; no host action; no listener.

## Proposed move (one bounded)

Pin the implementing bytes at both ends, reusing values already committed:

1. **Gate** (`tests/llamacpp-live/check-receipt.py`): add optional `--expect-server-impl-sha256 HEX` with an exact-match `bad()` path beside `:349–352`, and cross-check `server.server_impl_sha256 == server.install_tree["libllama-server-impl.so"]` when both are present (`:381–383` currently shape-only). Strict variant: `--expect-install-tree-sha256` against `6c216313…`; prefer the impl pin as the stable one because a rebuild can change unrelated tree members.
2. **Runner** (`.ufo/waves/round-18/runs/run.py:45`): add `--expect-server-impl-sha256 e404b91a81c9ab65756b6a57b97b42115a5f429c5060c4b7f0d717ca595b59ed`, exactly as the launcher pin is passed.
3. **Selftest** (`:1787` block): add `impl-consistent-swap` (mutB) expecting exit 1 only when the impl pin is supplied; keep `install-tree-sha-tampered` as the self-consistency case.
4. **Producer** (recommended for the v3 tri-state): add `--server-impl-sha256` expect to `tools/kama-llamacpp-live.py`, raising `SetupError('server-impl-digest-mismatch')` at `:1216–1234` before `pick_port`, mirroring `:1208–1214`. A swapped subject then lands in the not-evaluated bucket (exit 2) instead of producing a pass the gate must later call INVALID.

## Risks

- **Genuine operator rebuild:** the impl digest changes and all three receipts become INVALID. That is a true subject change and must be reported as identity mismatch, not as a lifecycle failure; the producer-side precondition (item 4) preserves the KQ24 distinction (exit 2, not exit 1).
- **Strict tree pin:** `install_tree_sha256` covers all 51 files, so an unused backend change also flips it; use the impl pin by default, the tree pin only when the whole release identity is the claim.
- **Forgery limit unchanged:** a receipt can still claim the pinned impl; this binds a genuine run's subject, not provenance (`RevExactArgv.md` already states the self-reported limit).
- **Residual, not part of this move:** the tool records `model_sha256_post` but no post-run server/tree digest; the pin proves what was launched, not that the tree stayed unchanged during the run. Secondary, smaller asymmetry.

## Verification

- Pristine control executed: `receipt-1.json` → `VALID`, exit 0, with the exact `live-gate-1` pins.
- Pins are already green on the committed evidence (executed): for receipts 1, 2, 3 — `impl==pin True`, `impl==tree_member True`, `tree==pin True`, launcher `b6a31a8e97615a2a…`, `outcome pass`.
- After the move: mutB and mutA → exit 1 naming the impl/tree member; mutC remains visible as a non-lifecycle tree member; the four existing pins and 11 checks are unchanged; `controls.py --selftest`, `check-receipt.py --selftest` and the C1/C2 counters must stay green (new flags optional).
- Host: no `pacman`, `systemctl`, `sudo`, `mkinitcpio`, `yay`; no install; no seat-owned listener. `pgrep -af llama-server` → none; `pgrep -af kama-r18-falsify-ConnectTsukuroi-3` → none; receipt port 33769 absent from `ss -ltn`; other 33xxx listeners are not from this seat.
- Installs: none. Tool versions changed: none.

## Limits

- Fresh mutants are reported as a separate denominator; they are not folded into C2's named round-17 set and do not by themselves lower C2.
- No live run was performed against a swapped tree (that would launch an unverified binary); the forged-receipt arm plus the `NEEDED`/`RUNPATH` structure establishes the genuine-run path.
- tsukuroi's knowledge notes, SOURCES.md and l1-capture were not opened; only the two named files plus the foreign-definition note were read. No sibling message, no edit outside this report.
