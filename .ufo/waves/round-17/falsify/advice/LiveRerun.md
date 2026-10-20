VERDICT: confirm — C2's real-run leg reproduces independently at 54a29268: three fresh b11755 server runs, 11/11 checks each, four-pin gate VALID, nothing left listening; C2's controls/source-binding legs were not attacked here.

# Attack: C2 real-run claim (`corpus/lessons/round-17.md:171-173`)

Claim under attack: "three `tools/kama-llamacpp-live.py` runs on b11755, each exit 0,
11/11 checks, gate `VALID` with model, server, probe and tool pins"
(`corpus/lessons/round-17.md:171-173`). I re-derived it from scratch in a `/tmp` clone at
`54a29268e2083caa2b1e0d54ee1e7d90961302f3`, and then attacked the gate that produces the
word VALID.

## F1 — Three fresh real runs, distinct processes, 11/11 each

| run | child_pid | port | loading 503 responses | distinct bodies | receipt sha256 (first 16) |
|---|---|---|---|---|---|
| 1 | 2945456 | 46849 | 46 | 1 | df893edb0131561a |
| 2 | 2945703 | 43381 | 56 | 1 | f8be607130f79980 |
| 3 | 2945884 | 34499 | 32 | 1 | 21ed70a5b41631cc |

Each receipt is `kama-llamacpp-live/v2` (`tools/kama-llamacpp-live.py` schema constant), 11
checks, all `passed: true`, ids exactly `REQUIRED_CHECKS_V2`
(`tests/llamacpp-live/check-receipt.py:80-92`: `"health_ready", "models_alias_id", …,
"model_unchanged"`). `internal_fault` and `setup_error` are null in all three; server log
tails each show `model loaded` then `listening on http://127.0.0.1:<port>`; `props_alias`
reports `build_info: b11755-704366d76`, i.e. the pinned commit, not a lookalike build.
Distinct pids/ports/timestamps and non-identical 503 counts (46/56/32) show three real
executions, not replayed JSON; the receipt bytes differ pairwise.

## F2 — Gate VALID under all four pins, on my runs and on the lane's

Commands (clone cwd, `PYTHONDONTWRITEBYTECODE=1`), pins: model `270cba1b…256d`, server
`b6a31a8e…cd804`, probe `36b64978…a29d3`, tool `0efd1723…c46ac`:

- `check-receipt.py /tmp/KamaR17.LiveRerun-r{1,2,3}.json --expect-model-sha256 … --expect-server-sha256 … --expect-probe-sha256 … --expect-tool-sha256 …`
  → `VALID`, exit 0 each (3/3).
- Same four pins against the lane's own `.ufo/waves/round-17/live/receipt-{1,2,3}.json`
  → `VALID`, exit 0 each (3/3).

The lane's own receipts are also distinct real runs: ports 40089/43091/38545, child pids
1677834/1677955/…, 503 counts 42/45/45, `started_utc` 15:57:44.932Z / .131Z / .328Z.
Their equal 27262-byte size is coincidence of digit widths, not duplication (sha256 and
diff both differ).

Gap (not a refutation): `.ufo/waves/round-17/live/gate.txt:7` echoes only
`probe=36b64978… tool=0efd1723…`; the model and server pins the claim names are not in the
artifact. I supplied them myself and the lane receipts still pass, so the claim holds, but
the artifact alone cannot prove the pin set.

## F3 — Teardown fields: SIGTERM to a live child, rc 0, no SIGKILL, port refused after

All three runs (`teardown` object): `alive_at_teardown_start: true`,
`sigterm_sent: true`, `sigkill_sent: false`, `returncode: 0`, `term_wait_ms: 3`,
`port_refuses: true`, and top-level `port_listener_ownership: "child"`; the
`teardown_graceful` / `teardown_port_closed` checks carry the same values. That is exactly
the producer predicate (`tools/kama-llamacpp-live.py:1310-1326`, including
`receipt.get('port_listener_ownership') == 'child'`) and its documented killpg-only-on-live
guard at `tools/kama-llamacpp-live.py:780` ("F5: killpg only on a live child"). The gate
re-derives it from the stored teardown object, not from the check's `passed` flag
(`tests/llamacpp-live/check-receipt.py:847-880`, `:886-888`).

## F4 — Loading envelope graded over every captured 503 body, not vacuous

`loading_envelope_graded.observed` per run: `all_exact: true`, `exact: true`,
`distinct_bodies: 1`, `bodies_dropped: 0`, `loading_observed: true`, with
`total_503_responses` 46/56/32. Producer grades every stored body
(`tools/kama-llamacpp-live.py:231` `loading_envelopes_all`), gate recomputes every entry
with its own envelope parser (`tests/llamacpp-live/check-receipt.py:922-935`: "a stored
loading_503_bodies entry is not the exact envelope"). The loading window is short (model
loads in ~4-8 ms; run wall time 0.20 s) but was genuinely sampled 32-56 times per run.

## F5 — VALID is pin-sensitive and field-sensitive (gate is fail-capable here)

Negating single fields of a valid receipt, each gated with the four pins → `INVALID`, exit 1:
teardown.returncode 0→1; sigkill_sent→true; port_listener_ownership→"other";
`teardown_graceful.passed`→false; health capture body→`{"status":"degraded"}`; loading body
code 503→500 with `bodies_dropped` untouched; model_sha256_post→`f`*64; delete one check;
tool sha→`c`*64; probe sha→`c`*64; teardown.port_refuses→false. 11/11 rejected.
Pin arms: wrong model pin → `INVALID … 1 problem(s)`, exit 1; wrong server pin → same,
exit 1; no pins at all → `VALID`, exit 0 (pins are opt-in, as documented).
Producer refusals: wrong `--model-sha256` → exit 3, "refusing to launch" (no server
started); `--port 8080` → exit 2, `port-refused-registered:8080`.

## F6 — Nothing left listening

After run 3: `pgrep -af llama-server` empty; `ss -ltnp` (20 rows) contains no llama-server
line; the three ephemeral ports refuse connect (`/dev/tcp` arms: 46849, 43381, 34499).
`~/.local/bin/llama-server` and `~/.local/opt/llama-b11755/llama-server` are the same
sha256 `b6a31a8e…cd804` (symlink resolution `readlink -f`), so the two paths are one binary.

# Commands run (exit codes)

Clone: `git clone -q … /tmp/KamaR17.LiveRerun-clone && git -C … checkout -q 54a29268…`
→ exit 0; `rev-parse HEAD` = `54a29268e2083caa2b1e0d54ee1e7d90961302f3`; `git status
--porcelain` empty.

Per run (cwd clone, `PYTHONDONTWRITEBYTECODE=1`, `--server
/home/vgpnk/.local/opt/llama-b11755/llama-server --model
/home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf --model-sha256
270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d --out /tmp/KamaR17.LiveRerun-rN.json`):
`tools/kama-llamacpp-live.py` → exit 0, 0 bytes stderr, ~0.20 s wall; then
`tests/llamacpp-live/check-receipt.py <receipt> --expect-model-sha256 … --expect-server-sha256
b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804 --expect-probe-sha256
36b64978ee3a3aa29e1b73f04ca5c7ad04a9aee880e7032abfd894fa7b3a29d3 --expect-tool-sha256
0efd1723b02ef748d720a6036d3ac481b1d5fe9755110999d7c9acaf486c46ac` → `VALID`, exit 0.
Gate `--selftest` → "2 valid receipt(s) accepted; 39 mutations + unreadable case all
rejected", exit 0 (matches the lesson's 26 v1 + 13 v2 mutation count).

# Limitations

- The gate checks internal evidence consistency; it cannot prove a server process existed.
  My three independent live runs are the provenance evidence [INFERENCE]. A hand-written
  receipt with plausible fields could pass; "VALID" alone is not execution proof.
- `alive_at_teardown_start` is the harness's own kernel-free observation
  (`_child_running(proc)`); the gate re-reads that field, not the process state at signal
  time. Not contradicted by any artifact here, but it is the ceiling of what this gate can
  re-derive.
- [INFERENCE] `term_wait_ms: 3` is consistent with a ~1 MB model exiting promptly on
  SIGTERM; a slower model would exercise the TERM_GRACE path, which no run here reached.
- Port pick has a documented sub-second bind race (`port_pick_note`); not triggered (3/3
  distinct free ports) but not excluded by these runs.
- C2's other legs (controls 6→0, S042-S044 bonds, receipt-on-internal-fault) were not
  attacked by me; sibling seats own them. No installs or upgrades were made.
- Scratch: clone, receipts, mutation copies and per-run logs were removed before finishing;
  the lane was not modified.
