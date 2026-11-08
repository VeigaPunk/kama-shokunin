# Round 94 — per-file GGUF parse deadline; every port/slot setter named per entry point; census self-check

L1 `KamaR94` (attempt 1). Base `e6f1dcce`; freeze `285f17832d0e26364366bbf19888d68f1838249b`;
C1 measured `a27656a454b1a2364f8b6e55f42fbca8c2e86ee4`; C2 measured at tip (see plan).
Plan: `plans/round-94-claims.md`. Previous closure: `round-93-verifier-spotcheck.md` (rejected;
R1–R7 routed to this round).

## Gate

Rows opened this round come from the pinned llama.cpp `b12177` codeload archive
(sha256 `f50a52f4ba45dd5b4b906db97cf230ce2e3b1117a0b9017411322ecba63eea13`), fetched 2026-11-07
and extracted under `/fast/scratch/hyaku/kama-r94/l1-controls/src`. Each new `corpus/SOURCES.md`
row names its per-file raw URL
(`https://raw.githubusercontent.com/ggml-org/llama.cpp/b12177/<path>`), the file sha256, and a
≤25-word quote with line; the file bytes are the archive members byte for byte. The wave-1 seats
re-open the same rows through the counter's `SETTER_SWEEP`/`ROUTER_BUDGET` receipts.

| Candidate | Decision | URL / access date | Located quote (≤25 words) and location | Reason |
|---|---|---|---|---|
| S604 `common/preset.cpp` @ b12177 | **admit** (A, code, mined) | raw URL — 2026-11-07, sha256 `793ad2c7…cbb25` | `opt.handler_string(params, val);` (line 150, inside `apply_to_params`) | Grounds the config.ini/`--models-preset` mechanism rows (P-rows on 142/285, preset.h 47/70). |
| S605 `common/common.cpp` @ b12177 | **admit** (A, code, mined) | raw URL — 2026-11-07, sha256 `1b41b361…985e` | `config_directory = common_get_env("XDG_CONFIG_HOME");` (line 1009) | Grounds the user config.ini path (`fs_get_config_directory`, line 1001). |
| S606 `tools/cli/cli-server.h` @ b12177 | **admit** (A, code, mined) | raw URL — 2026-11-07, sha256 `d463b06b…205d` | `port = common_http_get_free_port();` (line 35) | Grounds the llama-cli embedded-server entry point (lines 13/35/44). |
| S607 `tools/server/server-common.cpp` @ b12177 | **admit** (A, code, mined) | raw URL — 2026-11-07, sha256 `b686729e…0ddb` | `return std::getenv(SERVER_ENV_ROUTER_PORT) != nullptr;` (line 2236) | Grounds router-child detection (`is_managed_by_router`). |
| S608 `tools/server/server-common.h` @ b12177 | **admit** (A, code, mined) | raw URL — 2026-11-07, sha256 `335a09e6…ba1b` | `#define SERVER_ENV_ROUTER_PORT "LLAMA_SERVER_ROUTER_PORT"` (line 765) | The env var name that marks a router child. |
| S609 `tools/server/server-models-sched.cpp` @ b12177 | **admit** (A, code, mined) | raw URL — 2026-11-07, sha256 `b786ea09…dd54a` | `child_env.push_back(std::string(SERVER_ENV_ROUTER_PORT) + "=" + std::to_string(models.base_params.port));` (line 423) | The measure child also gets the router-port env. |
| S610 `common/arg.h` @ b12177 | **admit** (A, code, mined) | raw URL — 2026-11-07, sha256 `42f21df7…261b` | `return strcmp(args[0], other.args[0]) < 0;` (line 95) | Preset argv ordering decides which setter is parsed last. |
| S611 `common/preset.h` @ b12177 | **admit** (A, code, mined) | raw URL — 2026-11-07, sha256 `ec0f5014…32f3` | `common_presets load_from_ini(const std::filesystem::path & path, common_preset & global) const;` (line 70) | Declarations of the preset apply/load mechanism. |
| S612 `tools/cli/cli-context.h` @ b12177 | **admit** (A, code, mined) | raw URL — 2026-11-07, sha256 `e1ae9fc6…c8c04` | `#include "cli-server.h"` (line 6) | cli-context pulls in the embedded-server helper. |
| S613 `tools/imatrix/imatrix.cpp` @ b12177 | **admit** (A, code, mined) | raw URL — 2026-11-07, sha256 `a1be01b2…b8ab` | `params.n_parallel = n_seq;` (line 1869) | imatrix's own slot count, not llama-server. |
| S614 `tools/perplexity/perplexity.cpp` @ b12177 | **admit** (A, code, mined) | raw URL — 2026-11-07, sha256 `42a39345…88c0` | `params.n_parallel = std::max(4, params.n_parallel);` (line 2009) | perplexity clamps n_parallel; a different tool. |
| S615 `tools/rpc/rpc-server.cpp` @ b12177 | **admit** (A, code, mined) | raw URL — 2026-11-07, sha256 `0bef2241…53ba0` | `int                      port        = 50052;` (line 80) | rpc-server's own port default and argv parser. |
| S593, S596–S603 @ b12177 | **re-opened**, admitted for the P-rows that cite them | the rows' URLs — 2026-11-07, digests equal the archive members | `params.port = 8011;` (S596 line 4613) | Every P-row's text cell is the archive line byte for byte (`measured/c2.out` B2). |
| The codeload archive itself as a SOURCES row | **reject** (input, not a teaching source) | https://codeload.github.com/ggml-org/llama.cpp/tar.gz/refs/tags/b12177 — 2026-11-07, sha256 `f50a52f4…ea13` | n/a (binary archive) | The archive is the counter's pinned population input (`TARBALL_SHA256`); what kama learns is cited per file through the raw rows above. Flip: GitHub stops serving per-file raw URLs for the tag. |

`status`/`recheck`/`used-by` changes on existing rows: none. S604–S615 are new rows (`mined`,
recheck `on-release`, used-by `SKILL.md`). Census before→after: 343 → 355 rows,
`scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama` exit 0.

Assimilation: none (no `merge/kama/` theme taken this round; `considerthese/` not mined).

## Mistakes

**M1 — a counter drafted from scratch instead of extending the proven one.** Class: reinventing a
frozen counter. Evidence: the first `tools/round94-setter-sweep.py` draft carried B4/B5 derived
checks (value-cell and arg-block env/example rules) that contradicted the round-93 counter's
actual semantics; it reported 155 mismatches on a correct section
(`/fast/scratch/hyaku/kama-r94/l1-controls/` early run, `SETTER_SWEEP ... 155`). Captured-by: the
pre-freeze control run against the just-authored section, before commit. Fix: discarded the draft
and re-based the counter on `tools/round93-setter-rows.py`'s `grade_p`/`arg_block`/`split_cells`,
extending only the population patterns, the entry cell, and the R18/R19 decision model; the
re-based counter then bound 92/92 with `derived_disagree=0`. Shown able to fail: mutant line-edit
(35→36) → `SETTER_ROW P50 unbound fabricated`, `met=False`; base rev (no section) → `met=False`.

**M2 — the population pattern silently omitted the router-port env route.** Class: pattern list
treated as complete. Evidence: the first population computation (POP_RE + config-route +
entry-anchors, without `SERVER_ENV_ROUTER_PORT`/`LLAMA_SERVER_ROUTER_PORT`) yielded 88 lines and
missed `server-common.cpp:2236`, `server-common.h:765`, `server-models.cpp:1235`,
`server-models-sched.cpp:423` — the very child-detection rows the round-93 verifier routed here
(R6/SC02). Captured-by: re-deriving the population with the env names added before freeze, not by
a seat. Fix: added both env tokens to the config-route pattern; population 88 → 92, and the four
rows are now P-rows with SOURCES S607–S609. Shown able to fail: the base-rev run lists all 92 as
`SETTER_MISSING`.

**M3 — scope cells authored as prose, not the block's `set_examples`.** Class: derived cell filled
by intent rather than by the archive. Evidence: 18 rows went `unbound derived` because the scope
cell read `llama-server`/`llama-server, llama-cli` while `arg_block` extracts the literal
`set_examples` names (`LLAMA_EXAMPLE_SERVER`, `LLAMA_EXAMPLE_CLI, LLAMA_EXAMPLE_SERVER`, …);
`derived_checked=47 derived_disagree=18`. Captured-by: the pre-freeze control run. Fix: scope
cells set to the exact comma-separated `set_examples` names per block (builder constants
`SV`/`CS`/`EG`); `derived_disagree=0`. Shown able to fail: reverting one scope cell re-opens a
`derived` disagreement.
