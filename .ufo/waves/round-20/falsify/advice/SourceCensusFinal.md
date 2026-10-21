VERDICT: confirm - The rerun reports the pinned 64-row census and exits 0; validation also exits 0 while preserving five W04 warnings.

## Evidence

- Ran `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama`.
  - Exit: `0`.
  - Output: W04 warnings for S031 (`docs.ollama.com/api/tags`), S043 (`github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server.cpp`), S056 (`github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/common/arg.cpp`), S060 (`github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp`), and S064 (`docs.python.org/3.14/library/subprocess.html`); then `kama ok /home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md`.
- Ran `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh census --root /home/vgpnk/Projects/shokunin kama`.
  - Exit: `0`; `kama rows 64`, `FLEET rows 64`, `FLEET missing 0`.
  - Full census stdout matches `.ufo/waves/round-20/runs/0957ce61/sources-census.stdout` (pinned lines 1–16), including tier and status totals.
- The pinned stdout contains census data, not process-exit metadata; exit 0 above is directly observed for both reruns.
- Source evidence: `scripts/sources-census.sh:31-33` documents W04 as a warning; `:645` emits cross-scope W04; `:742-745` prints E/W findings while allowing `ok` absent lane errors; `:803-806` selects exit status. Both reruns observed the documented warning/clean behavior.
- No sources were edited. No tools were installed.
