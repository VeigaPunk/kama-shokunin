VERDICT: confirm — receipt v2 argv/env handling stays inside kama's province and matches its claims; one bounded gap: argv closedness is producer-only, gate-ungraded. Hand-off boundary named below.

# ConnectKagi-3 — receipt v2 argv/env handling vs kagi's secrets & vault ops ground

Read scope honored: kagi `SKILL.md`, `PROVINCE.md`, `corpus/QUALITY.md` only (read-only). Kama lane read at `54a29268e2083caa2b1e0d54ee1e7d90961302f3` (working tree == commit; only untracked `.ufo/waves/round-17/falsify/` differs). Tool runs in `/tmp/ConnectKagi-3-clone` at that commit.

## What I attacked

C2's receipt v2 argv/env handling (`tools/kama-llamacpp-live.py`, `tests/llamacpp-live/check-receipt.py`, `tests/llamacpp-live/controls.py`) against the ownership line kagi declares for kama: "kama refuses to hold credentials for authenticated health checks and would route that need here through L0" (`kagi-shokunin/PROVINCE.md:63`), where "kagi owns runtime auth and credential custody" (same line).

## Findings

1. **Env channel: closed at producer AND gate.** Producer allowlist `CHILD_ENV_KEYS = ('PATH','HOME','LANG','LC_ALL','TMPDIR')` (`tools/kama-llamacpp-live.py:84`), enforced at spawn (`:1103`), names-only in the receipt (`:1104`, docstring `:21-22` "Only argv is recorded from the launch environment — never env"). The probe subprocess inherits the same env, "no proxy vars can redirect it" (`:713`). Gate mirrors the allowlist (`check-receipt.py:65`) and grades it: measured — a v2 receipt with `LLAMA_API_KEY` appended to `child_env_keys` gets 2 problems ("outside the allowlist PATH/HOME/LANG/LC_ALL/TMPDIR"); selftest mutation `env-key-off-allowlist` already uses credential-shaped `AWS_SECRET` (`check-receipt.py:1240-1241`).
2. **Argv channel: closed at producer only.** The parser is fixed (`tools/kama-llamacpp-live.py:949-968`), `server_argv` is built internally (`:1088-1097`) — measured: `--api-key <placeholder>` exits 2 "unrecognized arguments" before any launch. But gate argv grading is flag-consistency only (`check-receipt.py:387-421`: argv[0]==realpath, `-m/--alias/--host/--port/-c/-t` values, tail `--no-webui --offline`) — no closedness rule. Measured: a v1 and a v2 selftest receipt with an extra `--api-key <placeholder marker>` element inserted mid-argv both validate with **0 problems**.
3. **Controls don't cover it either.** k0–k8 (`controls.py:297-330`) attack health/envelope/teardown shapes; the fake's shape rides argv because "the tool's child env allowlist would strip any env-var shape selector" (`controls.py:39-42`) — no control injects an unknown flag into the tool parser or an unknown element into server argv. So a producer regression (e.g. adding a `--server-arg` pass-through) would put any flag value — including a credential — into a committed receipt (`.ufo/waves/round-17/live/receipt-*.json`) with the gate still VALID.
4. **Why this is kagi-adjacent and not absorbed:** the landing never names the boundary — neither file contains the word "credential"; the invariant is implicit. Exposure if it regressed is double: argv is world-readable via `/proc` (kagi anti-pattern, `kagi-shokunin/SKILL.md:478`), and the receipt is a durable artifact — kagi's bar is "No credential material, ever" (`kagi-shokunin/corpus/QUALITY.md:24` QA5), and handoff vocabulary is `credentials_in_evidence: false` (`SKILL.md:441`).
5. **What kama owns (keep, do not hand off):** structural closedness — fixed argv builder, env-name allowlist, names-only recording. That is endpoint-serving operability (kama's domain per `tools/kama-llamacpp-live.py:3`), not vault ops. [INFERENCE from the two provinces' declarations; no kama doc states it]
6. **What kama must hand off rather than absorb:**
   - Any authenticated-health-check capability (llama-server `--api-key`/`--api-key-file`): the credential delivery mechanism — env-file ref discipline, `op run` resolution, custody evidence shape — is kagi's (`PROVINCE.md:63`; `SKILL.md` decision table "One-shot command with vault env"). Route through L0; the env allowlist widening that such delivery would need is an integrator decision with kagi sign-off, not a kama-side flag.
   - Secret-shape detection: if a gate rule ever rejects credential-shaped material in argv/receipts, the detector vocabulary is kagi's (`corpus/transcript-scan.sh` HIT shapes) — kama should not grow its own secret regex. [INFERENCE: kagi QUALITY.md:26 QA7 "contested ground is reported, not absorbed"]
   - Receipt claim scope stays "local receipt integrity only" (`SKILL.md:440`); no attestation widening.

## Proposed move (one, bounded)

**Complete the gate's argv grading into exact re-derivation.** The gate already re-derives every flag value from receipt fields; extend `check-receipt.py:387-421` to also require exact element count/order (no extra elements). Zero new constants (re-derived from receipt fields, no third producer/gate twin), version-agnostic — measured: today's v1-base and v2-base both pass the existing structural block, so exact-argv holds for both receipt versions. Add the symmetric selftest mutation (extra mid-argv element, mirroring `env-key-off-allowlist`). Effect: the credential-adjacent channel with the higher exposure (/proc + durable receipt) becomes graded, and a future closedness regression flips the gate instead of committing a secret-shaped receipt. This improves calibration-fail-capability of C2's gate and harms none: C1 untouched, probe untouched, no capability row added.

Rejected alternative: a credential-shape scan in the gate — absorbs kagi's detection ground and adds regex rot.

## Risks

- Any future legitimate server flag (e.g. `--metrics`) then requires a simultaneous gate edit — already true for every pinned flag today; fail-closed direction.
- Round-16 v1 receipts must be re-validated under the new rule before landing (they pass the current block; argv builder unchanged since round 16 per frozen manifest `tools_kama-llamacpp-live.py` `b8c5e8d4…`, but verify — main agent's run).

## Verification (commands, exit codes)

All in `/tmp/ConnectKagi-3-clone` @ `54a2926`, `PYTHONDONTWRITEBYTECODE=1`:
- `python3 tests/llamacpp-live/check-receipt.py --selftest` → "2 valid receipt(s) accepted; 39 mutations + unreadable case all rejected", exit 0.
- `python3 tools/kama-llamacpp-live.py --api-key DEMO-PLACEHOLDER --model /nonexistent.gguf --model-sha256 0*64 --probe tools/kama-probe.sh` → exit 2, "error: unrecognized arguments: --api-key DEMO-PLACEHOLDER".
- Adversarial driver (`/tmp/ConnectKagi-3-driver.py`, module-level `validate()` with the selftest's four pins): v1-base 0 problems; v2-base 0 problems; v1-extra-api-key **0 problems**; v2-extra-api-key **0 problems**; v2-env-off-allowlist 2 problems. Exit 0.

## Limitations

- Receipt-field reads at the working tree of `54a2926`; I ran no live llama-server and no controls.py run (out of slice scope; L1's three 11/11 runs stand).
- No round-16 v1 receipt was re-run under a hypothetical exact-argv rule (rule not implemented — advice only).
- Placeholder marker used in the argv probe is not real credential material and appears nowhere durable except this description's shape.

## Installs

None.

Scratch `/tmp/ConnectKagi-3-clone` and `/tmp/ConnectKagi-3-driver.py` removed after this write.
