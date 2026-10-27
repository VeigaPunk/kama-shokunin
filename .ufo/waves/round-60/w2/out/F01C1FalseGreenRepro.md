# F01C1FalseGreenRepro — C1 H1

- Reproduced W1 H1 with scratch-only patched copy; gate paused after `ps-after`/`ps-lists-loaded`, before after-load evidence replay.
- Sent external `SIGTERM` to recorded child PID 3219514 during the gate.
- Tool: exit 0, `MODEL_OK`; teardown returncode 0, SIGKILL false, port closed; evidence-after-load passed.
- Frozen verifier `verify(receipt, run_dir, nonce)`: `bad=[]`, accepted.
- Thus external child death before replay completed still produces an accepted C1 false-green.
- Exact runner command, receipt, and server log are recorded in `findings.md` / `F01C1FalseGreenRepro/repro/`.
- Disk-guard status checked before execution; scratch removed; no installs or lane edits.