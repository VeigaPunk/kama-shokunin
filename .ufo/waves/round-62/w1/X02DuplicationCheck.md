# X02DuplicationCheck — C1/shared lifecycle duplication

## Evidence

Read-only inspection at `master` tip `65d7cad0fce90e34de37527cde22e97b63b118bf`; the frozen C1 predicate requires a byte-pinned live POST lifecycle, unregistered loopback port, pdeathsig child, held outside observation, and receipt/counter agreement (`.ufo/waves/round-62/controls/freeze.txt:11-27`). No tools were installed and no live server was run.

`tools/kama-completion-live.py` dynamically loads `tools/kama-llamacpp-live.py` as `_live` and delegates these lifecycle primitives:

- `_utc_now`, `sha256_file`
- `refused_ports`, `pick_port`
- `prepare_witness_dir`, `hold_for_witness`
- `_FORKED_PPID` and `_preexec_pdeathsig`
- `http_get`, `port_owned_by`, `_listen_inodes`

C1-specific implementations include `http_post` (POST response capture), `wait_ready` (simple `/health` poll), request/capture grading in `run`, and its teardown. The shared harness has `readiness_loop` (keep-alive `/v1/models` loading-window and health capture), `verify_live`, and `teardown`; C1 does not call these broader lifecycle functions.

## Non-obvious move

Keep the existing split of request-plane semantics from reusable lifecycle mechanics, but define a narrow shared lifecycle boundary for the duplicated readiness/ownership/teardown sequence: one primitive should provide child launch with pdeathsig, readiness polling, first-answer listener ownership, and ownership-gated cleanup as a coherent operation, with policy/capture hooks or explicit result fields for each caller. This improves calibration of what “same lifecycle” means without forcing C1's POST grading into the inventory harness.

## Drift risks / contradictions

- **Port selection:** delegated to `refused_ports` + `pick_port`, so registry parsing/refusal and allocation behavior currently have one source. However pick-then-launch has an intentional release/rebind race; neither caller reserves the socket through server bind. Keep the existing disclosed race rather than treating shared selection as race elimination.
- **Ownership:** C1 waits only for `/health` 200, then checks `port_owned_by` before grading other surfaces. The shared readiness loop proves ownership at the first successful HTTP response (any status) and discards observations if ownership is false/unproven. These are different temporal guarantees; a foreign server could answer earlier and disappear before C1's later check. Consolidating must preserve the stronger first-response gate, not merely share the helper name.
- **pdeathsig:** both use the same `_preexec_pdeathsig` and parent PID global. That centralizes the kernel primitive, but the child env and launch setup remain caller-local; C1 sets `_FORKED_PPID` before `Popen`, so any future launch refactor must preserve that ordering.
- **Hold protocol:** C1 correctly reuses `prepare_witness_dir` and `hold_for_witness`, then adds a separate `hold.json` with alias/model/server/prompt bindings and removes it after wait. The shared witness's `ready.json`/`release` protocol alone does not carry those request bindings. Preserve the distinction and ensure both documents continue to identify the same run/child.
- **Teardown:** materially different today. C1 sends SIGTERM to the direct child, waits 15s then `proc.kill()`, and probes procfs for any listener after checking child ownership. The shared teardown signals the process group, waits its configured grace, may SIGKILL the group, and records TCP refusal. A shared operation must not silently weaken group cleanup or conflate “child no longer owns listener” with “port has no listener.”

## Affected axes and verification

- **Calibration (primary):** explicit semantic boundary prevents future edits from making the two “live lifecycle” tools drift while appearing equivalent.
- **Operability:** only improves if shared cleanup/readiness preserves each tool's stricter guarantees; careless unification could leave a child/grandchild or accept a foreign listener.

Verify any follow-up by exercising (in sandbox/isolated unregistered loopback only): occupied and refused ports; foreign listener answering before child bind; child exit during readiness/hold; parent death; release handshake with matching hold/ready identity; and child-plus-descendant teardown. Compare generated receipts and assert no unrelated listener survives. This is a proposal only; no source was changed.
