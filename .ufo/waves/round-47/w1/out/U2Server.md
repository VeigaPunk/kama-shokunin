# U2Server report (round 47, w1)

Verdict: b11906 -> b11909 is 3 commits / 38 files, none in tools/server/, common/ or include/; no receipt statement can change; 5 of 91 registry rows (S107, S113, S130, S132, S135; src/llama-context.cpp and src/llama-kv-cache.cpp) need renumbering at the next freshness round, all text-equal.

Evidence (full detail in .ufo/waves/round-47/w1/out/U2Server/map.md):
- `git ls-remote`: b11906=4d71b42fd, b11907=4b851fbee, b11908=a4699400e, b11909=caa8191df (matches the assignment); b11906 is an ancestor of b11909.
- `git -C up log --format='%h %cI %s' 4d71b42..caa8191`: 3 commits (hexagon MUL_MAT_ID #31169; no_alloc out of llama_hparams #31141; model output structs #31142). `diff --stat`: 38 files, 641+/452-. `diff --stat -- tools common include ggml/include`: empty; tools/server tree bb7cdb4c71c9 and common/arg.cpp blob 9706b3ac58d5 identical at both tags.
- tools/server has 0 hits for hparams.no_alloc; the move is internal to src/.
- Receipt statement sites at b11909: get_health server-context.cpp ~5609, loading 503 server-http.cpp ~315, owned_by "llamacpp" server-context.cpp:5503, /metrics 501 server-context.cpp:5625, SIGTERM server.cpp 318-325 -> 645-648. All unchanged from b11906.
- Registry: all 91 release_blob values equal the b11906 blobs; only src/llama-context.cpp and src/llama-kv-cache.cpp changed; per-range text equality computed from hunk offsets (kv-cache 65-98 includes the signature edit).

Finding (not b11909-caused, low): receipt-1 `checks[].documented_by` for health_ready, loading_envelope_graded and teardown_graceful cite raw URLs at 704366d76f87 with L5288-5299 / L314-325 / L529-534; the server.cpp span is not present verbatim at b11909 (f3269ef96 refactored the entrypoint; SIGTERM install now server.cpp 318-325). Behaviour is the same, the citation is stale. Proposed fix in map.md section 3b.

Not run: no replay or live server by this seat. Tooling installed: none. Scratch removed.

Wrote:
/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/U2Server/map.md
/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/U2Server/commits.txt
/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/U2Server/stat.txt
/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/U2Server/changed-files.txt
/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/U2Server.md
