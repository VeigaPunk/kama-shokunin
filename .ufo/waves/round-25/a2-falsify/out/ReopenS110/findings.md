# ReopenS110 — falsification evidence, SOURCES row S110

Seat: KamaR25a2.ReopenS110, kama round 25 attempt 2 wave 2. Date 2026-10-22.
Lane tip fa3b62ae6475d111eb466d79af616aeebb08bbb9. No llama-server started. No subagents. No tool installs needed.

## Fresh fetches (all 2026-10-22, raw.githubusercontent at 704366d76f8748cf9ad3df62a464bfcc8d1ae6ad)

| file | sha256 | note |
|---|---|---|
| common/arg.cpp | bf4c58c189a774f2308acfe88e4ec5cebb0c43f60cf05cef4c5b2b9affd5822d | 4833 lines |
| common/common.h | 8bcc5708c856653b0094ba312030df9c2f43ec2703e8ad78474fd4339d2540a9 | line 580 check |
| common/fit.cpp | 1f83da2a5dc460b893373365e07341695be80d6c662e53679032a138cce4dd58 | consumer check |
| repo tarball at pinned commit | (scratch only) | whole-tree grep for fit_params_min_ctx |

Scratch: /fast/scratch/hyaku/kama-r25a2w2/ReopenS110/ (arg.cpp, common.h, fit.cpp, extracted tree).

## Check 1 — anchor sha256: PASS

Row (corpus/SOURCES.md line 122, read :raw:122-122) anchor ends `raw sha256 bf4c58c189a774f2308acfe88e4ec5cebb0c43f60cf05cef4c5b2b9affd5822d`.
`sha256sum` of fresh curl of the same URL: `bf4c58c189a774f2308acfe88e4ec5cebb0c43f60cf05cef4c5b2b9affd5822d`. Exact match.

## Check 2 — cited line ranges: PASS (all six verified line-by-line)

From arg.cpp (grep -n line numbers, exact dumps):

- 1405–1406: `} else if (ex == LLAMA_EXAMPLE_SERVER) {` / `params.n_parallel = -1;     // auto by default` — server slot auto default. Matches.
- 1641–1659: `-c/--ctx-size` handler 1641–1650 (names 1641, help 1642, `params.n_ctx = value;` 1645, guard `if (value == 0) {` 1646, comment 1647, `params.fit_params_min_ctx = UINT32_MAX;` 1648, close 1649, env 1650) + `--kv-unified-per-slot` handler 1651–1658 (help 1653–1654, `params.kv_unified_per_slot = value;` 1657, env 1658). 1659 is the NEXT handler's `add_opt(common_arg(` opener — one-line bracket overshoot, no claim touched.
- 1727–1734: `--kv-unified` handler: names 1727–1729, help 1730 "use single unified KV buffer shared across all sequences (default: enabled if number of slots is auto)", `params.kv_unified = value;` 1732, env 1734. Matches.
- 2545–2556: exactly bracketed: 2545 `if (ex == LLAMA_EXAMPLE_SERVER) {`, 2548 `{"-np", "--parallel"}, "N",`, 2549 "number of server slots (default: %d, -1 = auto)", zero-reject 2551–2552, `params.n_parallel = value;` 2554, env 2556. Matches.
- 2881–2894: exactly bracketed `--fit` handler: names 2882, help 2883, `params.fit_params = true;` 2886 / `= false;` 2888, throw 2890–2891, env 2894. Matches.
- 2934–2940: exactly bracketed `--fit-ctx` handler: names 2935, help 2936 (default `%` PRIu32 of fit_params_min_ctx), `params.fit_params_min_ctx = value;` 2938, env 2940. Matches.

Scope cell ("parser assignments and help declarations …; not allocated capacity or live serving") is respected by every range.

## Check 3 — Gate quote (corpus/lessons/round-25.md line 26): PASS

Quote: `line 1647: "disable context reduction in llama_params_fit if the user explicitly requests the full context size:"`
- arg.cpp line 1647 (grep-proven): `// disable context reduction in llama_params_fit if the user explicitly requests the full context size:` — exact text after stripping the comment marker. Right line.
- Word count: 14 ≤ 25. PASS.

## Check 4 — teaches cell vs lines: PASS

Teaches (SOURCES.md line 122): "Explicit -c 0 sets the fit context-reduction sentinel, not the fit Boolean; fit and its minimum have separate handlers, while unified KV and parallel options declare shared-buffer and server-slot semantics."
- `-c 0` → `fit_params_min_ctx = UINT32_MAX` (1648), no write to `fit_params` anywhere in the handler. Sentinel, not Boolean. Confirmed.
- Separate handlers: `--fit` 2881–2894 writes only `fit_params`; `--fit-ctx` 2934–2940 writes only `fit_params_min_ctx`. Confirmed.
- Declaration-level semantics: 1730 (shared buffer), 2549 (server slots). Confirmed; nothing beyond help/assignment is claimed.

## Check 5 — entry use of S110 (corpus/knowledge/context-capacity.md): PASS with one provenance defect

Uses at lines 1 (source list), 59–60, 95–96 only (grep over entry).
- Lines 95–96: "An explicit `-c 0` is not the same as omitting `-c`: `-c 0` disables fit's context reduction (S110, arg.cpp 1646-1649)." Range 1646–1649 = guard + comment + sentinel + close. Effect verified implemented at this commit: common.h:485 default `int32_t fit_params_min_ctx = 4096;`; common.cpp:1274 passes it into `common_fit_params`; fit.cpp bounds reduction by `n_ctx_min_total` (266–268, 394, 414, 426–430) and has an explicit no-change branch `if (n_ctx_min == UINT32_MAX)` logging "user has requested full context size … no change" (fit.cpp 447–448); guard 394 `n_ctx_max > n_ctx_min_total` is false, so reduction cannot run. Server consumer consistent: server.cpp:181 `(uint32_t) params.fit_params_min_ctx != UINT32_MAX` in the pool auto-sizing predicate. Honest hedge line 96–97 present.
- Lines 59–60: "Giving `-np` keeps the default split cache (S110; common.h 580)." S110 half supported declaratively (1406 auto default, 1730 "default: enabled if number of slots is auto", 2549 "-1 = auto"). common.h:580 verified verbatim: `bool kv_unified = false; // enable unified KV cache` (fresh fetch sha256 8bcc5708…). DEFECT: no SOURCES row registers common/common.h (grep over corpus/SOURCES.md: no match), so the entry cites an unregistered file:line, and the claim "the entry rests on S106-S113" (errata-attempt-2.json correction 7) is incomplete by this one citation.

## Check 6 — Gate W04 note (round-25.md lines 36–38): PASS for S110

arg.cpp URL rows in SOURCES.md: S054 (line 66), S056 (line 68), S110 (line 122). Matches the claimed older-row pair S054/S056 for S110.

## Notes (not defects)

- arg.cpp:1647 comment names `llama_params_fit`; the implementation at this commit is `common_params_fit_impl` / `common_fit_params` (fit.cpp 179, 879). fit.cpp's own error string (line 184) still says "llama_params_fit is not implemented…", so the comment's name matches in-tree usage. The Gate/teaches cells only quote the comment; no row asserts the function name.
- preregistration.json and amendments 2–4 contain no S110 mention (grep exit 1); S110 matters to wave claims only through C2's "S106–S113" scope.

## Smallest correction

One edit, entry side: give the common.h citation a registered home — either add a SOURCES row for common/common.h @ 704366d76 (sha256 8bcc5708c856653b0094ba312030df9c2f43ec2703e8ad78474fd4339d2540a9, default-value line 580, plus fit_params_min_ctx default at 485 if wanted), or reword line 60 to rest on S108's server.cpp 169–174 auto branch plus the S110 declaration (1730) and drop the bare `common.h 580`. No change to the S110 row, anchor, teaches, or Gate line.
