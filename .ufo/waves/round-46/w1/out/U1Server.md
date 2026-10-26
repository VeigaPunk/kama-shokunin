# U1Server: all predicted equal to the b11889 receipts except `/props.build_info` (b11889-d854d98ba -> expected b11906-4d71b42fd, build identity only)

Full source-cited prediction table (A = b11889, B = b11906, file:line at both): `.ufo/waves/round-46/w1/out/U1Server/prediction.md`.

Evidence in short:
- `git diff d854d98..4d71b42 -- tools/server/` is 81 lines in 3 files: server-context.cpp (mtmd capability refactor `mtmd_helper_get_capabilities`, B:1015-1026, :1401, :1711-1713, :5133), a comment in server-models.cpp, and tests/utils.py (test timeout).
- server-http.cpp, server.cpp, server-common.cpp, common/build-info.cpp.in and cmake/ are not in the diff. These hold the loading 503 envelope (server-http.cpp:308-327), the `/health` body (server-context.cpp A:5606 / B:5609), `/metrics` 501 (A:5619 / B:5622 with server-common.cpp:117-120), `/v1/models` `owned_by` and id/alias (A:5486-5500 / B:5489-5503), SIGTERM (server.cpp:26-38, :320-325, :645-649) and the `build_info` format (build-info.cpp.in:27-29).
- The refactor is equivalent when `mctx == nullptr`: `mtmd_helper_get_capabilities` returns chat=true and everything else false, matching the old null-mctx expressions. The b11889 receipt is text-only (stories260K, no mmproj).
- Unverified [INFERENCE]: the 9-char hash length of the release binary's `build_info`. Loading-window length is a runtime measurement.

Falsifiers: a live b11906 run with a different loading envelope, `/health` body, `/metrics` status, `owned_by`, id, or SIGTERM returncode != 0.

Paths written:
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/U1Server/prediction.md
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/U1Server.md
