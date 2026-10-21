VERDICT: partial - selftest implementation delivered; execution deferred to the parent-owned gate.

Axes: selftest coverage and operability, with changes limited to the assigned script in the isolated copy.

- Added `--selftest` in `tests/llamacpp-live/install-tree-grid.py`. Temporary fixtures use the receipt gate's valid v1 selftest receipt and exercise valid baseline + rejected pinned member, an absent member, and a bad tree digest; each case checks expected grid status/exit and any mismatch makes selftest exit 1.
- Files: `/tmp/kama-r19-GridSelftest/tests/llamacpp-live/install-tree-grid.py`; delivery copy `/tmp/kama-r19-GridSelftest/out/install-tree-grid.py`; receipt `/tmp/kama-r19-GridSelftest/out/receipt.md`.
- Retained evidence: `cp -a /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/kama-r19-GridSelftest` completed successfully with no stdout (exit 0). Delivery command `mkdir -p /tmp/kama-r19-GridSelftest/out && cp /tmp/kama-r19-GridSelftest/tests/llamacpp-live/install-tree-grid.py /tmp/kama-r19-GridSelftest/out/install-tree-grid.py && printf 'delivered=%s\\nexit=0\\n' /tmp/kama-r19-GridSelftest/out/install-tree-grid.py` returned exit 0 and stdout `delivered=/tmp/kama-r19-GridSelftest/out/install-tree-grid.py` / `exit=0`.
- [INFERENCE] `python3 /tmp/kama-r19-GridSelftest/tests/llamacpp-live/install-tree-grid.py --selftest` was not run; the BUILD-wave instruction forbids tests and the parent owns post-integration verification.
- Risk: selftest behavior remains unexercised in this wave. No external installs or host mutations.
