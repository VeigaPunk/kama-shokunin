# Proposed lane text for the two S043 drift flags (NOT applied; lane is read-only for K1J07)

Required by tools/round44-release-recheck-audit.py (flags loop): a valid `drifted` row needs
(a) a line inside the `## Round-44 release re-verification` section of corpus/SOURCES.md that
matches `\bS043\b`, and (b) a line in corpus/knowledge/llamacpp-loading-lifecycle.md matching
`\bS043\b` and containing `b11889`.

## (a) corpus/SOURCES.md, inside the round-44 section

- S043 drifted at b11889 (d854d98bae598388ecea1ed84396587e5edc326d): `signal_handler` 26-38 and
  `start_loop` are unchanged and a single-model teardown still ends in `return 0` (684); the anchor's
  `sigaction` block moved into `server_install_signal_handlers()` (server.cpp:318-332) and is installed
  at 651-653 after `load_model` (633) and `is_ready` (641), gated by `opts.install_signal_handlers`,
  with a router-only install at 544-546; `shutdown_handler` 519-523 is now 645-649. The row's second
  file anchor, `tools/server/server-queue.cpp` `terminate()` 132-136, is unchanged at 132-136. Statement
  intact; the ledger row is `drifted` because a cross-file cite cannot be mapped inside server.cpp.

## (b) corpus/knowledge/llamacpp-loading-lifecycle.md (append; do not rewrite b11755 text)

**Round-44 release recheck (S043, b11889).** Re-read at d854d98bae598388ecea1ed84396587e5edc326d:
the graceful-teardown ordering above still holds for a single-model `llama-server` - `signal_handler`
is byte-identical, the instance `shutdown_handler` now sits at `server.cpp:645-649`, `start_loop` at
671 and `return 0` at 684 - but the `sigaction` block moved into `server_install_signal_handlers()`
(318-332) and is now gated by `opts.install_signal_handlers` (651-653), with a second install site for
the router (544-546); the router's `shutdown_handler` (525-532) stops `ctx_http`, not `ctx_server`.
`tools/server/server-queue.cpp` `terminate()` is unchanged (132-136). The b11755 line numbers above are
historical, and S047's static-ordering correction still governs what was reproduced.
