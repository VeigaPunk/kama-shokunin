## Round 34 - capability repertoire and instrument-registry claims (draft)

This block is a draft for later insertion; it does not modify `SCORECARD.md`. Every **PENDING** cell must be filled from the actual round-34 receipts before landing. The frozen expectations below are not measurements made by this seat.

| Claim | Axis, score | Before -> after (measured) | Counting command | Measured commit | Evidence |
|---|---|---|---|---|---|
| C1 — complete the canonical capability repertoire | calibration 7 -> 7 | **PENDING** — before counter line/exit -> after counter line/exit; do-nothing-control line/exit | `python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/capability-repertoire-audit.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --tip <full-commit> --out <receipt.json>` | **PENDING** — full commit recorded by the after-run receipt | **PENDING** — before/after receipt paths and do-nothing-control receipt path |
| C2 — register every tracked round-scoped counter | operability 8 -> 8 | **PENDING** — before counter line/exit -> after counter line/exit; do-nothing-control line/exit | `python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/gate-registry-check.py --rev <full-commit>` | **PENDING** — full commit recorded by the after-run receipt | **PENDING** — before/after receipt paths and do-nothing-control receipt path |

Frozen acceptance reminders, not observed results:

- C1's counter line has the form `listed L observed O missing M unsubstantiated U met B`. Before requires `M > 0`, `met False`, exit 1; after requires `M == 0`, `U == 0`, `met True`, exit 0. A capability row counts only when its evidence cell contains a resolving repo-relative path.
- C2's before result must show the two round-33 counters unregistered and exit 1; its after target is `registered 12 unregistered 0 defective 0`, exit 0.
- Each claim needs its own do-nothing control: skipping the claimed work must not reach that claim's target. Keep the two claims' receipts and controls causally separate; evidence for one does not satisfy the other.

**Capabilities - canonical list as of round 34**

| Capability | What it can now do | Evidence pointer | First-working round |
|---|---|---|---|
| sources-registry | Curate where kama learns with opened, tier-scoped, revision-anchored source rows and contract-v1 census validation | `corpus/SOURCES.md` | 10 |
| ollama-offline-evidence-replay | Reconcile caller-supplied `/api/tags` and `/api/ps` captures using exact names/digests and fail-closed remote/unknown/invalid classifications; readiness remains unknown | `tools/kama-ollama-evidence.py`; `.ufo/waves/round-14/acceptance.json` | 14 |
| live-llamacpp-lifecycle | Start the pinned llama.cpp b11755 server with a pinned GGUF on an unregistered loopback port, capture loading and ready surfaces, grade them with the probe, tear the server down, and re-derive receipt checks; not consumer health, model quality, or timing | `.ufo/waves/round-16/live/receipt.json`; `tests/llamacpp-live/check-receipt.py`; `SKILL.md` | 16 |
| gguf-declared-identity-replay | Decode bounded local GGUF metadata offline, bind the file SHA to a captured v3 receipt, and compare declared training/embedding/vocabulary metadata; not loaded-weight authentication or arbitrary scalar-value recovery | `tools/gguf-identity.py`; `.ufo/waves/round-18/live-recovery/receipt-1.json`; `.ufo/waves/round-20/runs/0957ce61/gguf-receipt.stdout` | 20 |
| context-capacity-receipt | Run the 14 registered context-capacity cells sequentially on the lane-owned llama.cpp fixture and emit a receipt binding per-slot values, slot count, KV-pool/log/request outcomes, and raw-file hashes; a cell counts only after its child is reaped and its port closed | `tools/kama-context-capacity.py`; `.ufo/waves/round-25/final/context-capacity-receipt.json`; `.ufo/waves/round-25/count-c2.py` | 25 |
| instrument-agreement | Run a lane instrument N times over one tree in isolated temp dirs, normalize only declared volatile fields, and emit per-run exit/normalized-output digests with an `IA runs=N agree=A disagree=D` counter; refuse always-agree stubs and undeclared deviations | `tools/instrument-agreement.py`; `.ufo/waves/round-30/c2/receipt-a.json`; `tools/error-verdict-census.py` | 30 |

Round 34 adds no capability row in this draft: C1 reconciles the demonstrated repertoire and C2 repairs instrument registration; neither declaration is a new serving operation.
