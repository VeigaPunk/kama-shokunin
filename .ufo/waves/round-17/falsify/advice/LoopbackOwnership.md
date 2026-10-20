VERDICT: partial — IPv4 and foreign-listener checks hold; the tcp6 loopback-owner predicates false-fail.

## Attacked
Round-17 change to `tools/kama-llamacpp-live.py::_listen_inodes` / `port_owned_by`: IPv4 loopback, wildcard binds, `/proc/net/tcp6`, and foreign-listener rejection.

## Findings

### MEDIUM — Native and IPv4-mapped tcp6 loopback listeners are not recognized
`tools/kama-llamacpp-live.py:331-335` checks `addr_hex.endswith('00000001')` for `::1`, and compares `addr_hex[:24]` with `'0000000000000000FFFF00'` for IPv4-mapped loopback. On this host, fake listeners owned by child processes produced `/proc/net/tcp6` local addresses `00000000000000000000000001000000` (`::1`) and `0000000000000000FFFF00000100007F` (`::ffff:127.0.0.1`); the current code returned `None` for both while the frozen function returned `True`. The mapped-prefix literal is 22 characters, so it cannot equal the 24-character slice. [INFERENCE] The `::1` mismatch is a proc-format byte-order assumption: the observed encoding ends `01000000`, not `00000001`.

`tools/kama-llamacpp-live.py:351-352` maps an empty filtered inode set to unknown (`None`); `:634-638` turns that into `port-listener-ownership-unproven`. For an IPv4-mapped listener that can answer the tool's IPv4 loopback connection, this can reject the real child after a successful response. A native `::1`-only listener would not answer the tool's IPv4-only HTTP client, so its startup may fail earlier at readiness rather than reaching this ownership check. The canonical launch currently supplies `--host 127.0.0.1` (`:1088-1092`), so no tcp6 bind is requested in the checked-in path; this is a latent false-fail if that bind path is used, not an observed failure of the pinned normal launch.

### Confirmed behavior — wildcard self-listeners are intentionally fail-closed
For child-owned `0.0.0.0` and `::` listeners, the frozen function returned `True` and the changed function returned `None`. The implementation documents that wildcard addresses “are not counted as the loopback-port owner — fail-closed” (`tools/kama-llamacpp-live.py:317-318`). This does false-fail if a child actually binds a wildcard despite the requested host, but is consistent with the loopback-only ownership contract and the current fixed `--host 127.0.0.1` launch argument (`:1091`). No finding against the intended fail-closed behavior.

### Confirmed non-finding — foreign IPv4 loopback listeners remain refused
A separate fake HTTP listener returned a 503 while an unrelated target PID was supplied. `port_owned_by` returned `False`; `verify_live` returned `('review:port-listener-not-our-child', 'foreign')`; `readiness_loop` returned `failure='port-listener-not-our-child'`, `ownership=False`, `ready=False`, with `loading_503=None` and the transition body cleared. This matches `readiness_loop`'s first-response ownership gate (`tools/kama-llamacpp-live.py:516-519`, `:546-552`).

## Commands and results
- `git clone -q /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/KamaR17.LoopbackOwnership-clone && git -C /tmp/KamaR17.LoopbackOwnership-clone checkout -q 54a29268e2083caa2b1e0d54ee1e7d90961302f3 && git -C /tmp/KamaR17.LoopbackOwnership-clone log --oneline -1 && echo CLONE_OK` — exit 0; clone checked out the assigned round commit.
- `PYTHONDONTWRITEBYTECODE=1 python3 loopback-ownership-check.py` in `/tmp/KamaR17.LoopbackOwnership-clone` — final run exit 0. It compared frozen/current ownership for child-held fake IPv4 loopback, IPv4 wildcard, `::1`, IPv6 wildcard, and IPv4-mapped loopback sockets, then exercised foreign `verify_live` and a foreign fake HTTP 503 through `readiness_loop`. The first scratch run exited 1 because the test assertion expected a list while `verify_live` returned a tuple; the assertion was corrected, then the complete probe passed.
- `ss -H -ltnp '( sport = :42830 or sport = :35569 or sport = :47188 or sport = :32836 or sport = :34294 or sport = :50716 or sport = :36664 )'` — exit 0, no rows; all fake listeners were closed.

## Residual risk and verification gaps
The tested Linux `/proc/net/tcp6` observations establish the false negatives on this host; no llama-server binary was launched. The checked-in launch pins IPv4 loopback, limiting the tcp6 issue to alternate/future bind behavior. No LSP device was mounted, so `lsp` status/references/definition/diagnostics were unavailable; source definitions and callsites were read directly, and grep was used only to locate them. No tools were installed or updated.