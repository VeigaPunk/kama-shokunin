# Advice — ReopenS110 (kama r25 a2 w2, falsify SOURCES row S110)

Verdict: **holds** — row S110 and its Gate line survive every check; one minor provenance defect found in the entry's use of S110 (`common.h 580` has no registered row). Smallest correction is one entry-side edit; the row itself needs nothing.

## Per-check verdicts

1. **Fresh fetch + anchor sha256: PASS.** Fresh curl of common/arg.cpp @ 704366d76 (2026-10-22) hashes to `bf4c58c189a774f2308acfe88e4ec5cebb0c43f60cf05cef4c5b2b9affd5822d`, exactly the anchor cell of corpus/SOURCES.md line 122. File is 4833 lines.
2. **Cited line ranges: PASS.** All six ranges verified line-by-line with grep line numbers: 1405–1406 (server `n_parallel = -1` auto default), 1641–1659 (`-c/--ctx-size` handler incl. comment 1647 + `fit_params_min_ctx = UINT32_MAX` 1648, plus `--kv-unified-per-slot` 1651–1658), 1727–1734 (`--kv-unified`), 2545–2556 (server `--parallel`, exactly bracketed), 2881–2894 (`--fit`), 2934–2940 (`--fit-ctx`). Only blemish: 1659 is the next handler's `add_opt(` opener — one-line bracket overshoot, no claim affected. Scope guard "not allocated capacity or live serving" respected.
3. **Gate quote (corpus/lessons/round-25.md line 26): PASS.** Text is character-exact against arg.cpp:1647 (`// disable context reduction in llama_params_fit if the user explicitly requests the full context size:`), the line number 1647 is correct (grep-proven; comment sits above the sentinel assignment at 1648), and the quote is 14 words ≤ 25.
4. **Teaches cell: PASS.** Every clause is supported: `-c 0` writes only the sentinel `fit_params_min_ctx` (1648), never `fit_params`; `--fit` (2881–2894) and `--fit-ctx` (2934–2940) are separate handlers; `--kv-unified` help 1730 declares the shared buffer, `--parallel` help 2549 declares server slots.
5. **Entry use of S110: PASS on substance, DEFECT on provenance.**
   - context-capacity.md lines 95–96 (`-c 0` disables fit's context reduction, arg.cpp 1646-1649): substance verified against the implementation — default `fit_params_min_ctx = 4096` (common.h:485), plumbed at common.cpp:1274, floor `n_ctx_min_total` in fit.cpp (266–268, 394, 414, 426–430) with explicit no-change branch at fit.cpp:447–448; server.cpp:181 consumes the same sentinel. Honest hedge ("fit never reduces anything on this fixture") present at lines 96–97.
   - context-capacity.md lines 59–60 cite `common.h 580` inline: the line exists verbatim (`bool kv_unified = false;`, fresh fetch sha256 `8bcc5708…`) and the claim "giving `-np` keeps the default split cache" is true, but **no SOURCES row registers common/common.h** — the entry therefore rests on an unregistered file:line, and the errata claim that the entry rests on S106–S113 is incomplete by exactly this citation.

## Smallest correction

Entry-side, one edit at corpus/knowledge/context-capacity.md line 60: either register a SOURCES row for common/common.h @ 704366d76 (sha256 `8bcc5708c856653b0094ba312030df9c2f43ec2703e8ad78474fd4339d2540a9`, default-value line 580) or reword the citation to S108's server.cpp 169–174 auto branch plus S110's declaration at 1730 and drop the bare `common.h 580`. No change to the S110 row, its anchor, its teaches cell, or the Gate line.

## Residual risk and verification gaps

- I verified parser-level semantics and the fit consumer by source reading only; no runtime `-c 0` run was performed (out of my item's scope, and no server was started). The behavioral claim's fixture hedge is the entry's own, already marked as unobserved there.
- `llama_params_fit` in the arg.cpp:1647 comment is the legacy name; at this commit the implementation is `common_params_fit_impl`/`common_fit_params` (fit.cpp:179/879; fit.cpp:184's own error string still says "llama_params_fit"). No row asserts the name, so this is a note, not a defect.
- preregistration files name no S110-specific expectation (grep exit 1), so there is no preregistered prediction for me to falsify beyond the C2 "rests on S106–S113" scope statement.

## Files written

- kama-shokunin/.ufo/waves/round-25/a2-falsify/out/ReopenS110/findings.md (evidence detail)
- kama-shokunin/.ufo/waves/round-25/a2-falsify/advice/ReopenS110.md (this report)
- Scratch only (outside repo): /fast/scratch/hyaku/kama-r25a2w2/ReopenS110/{arg.cpp, common.h, fit.cpp, llama.cpp-704366d7.tar.gz, extracted tree}

Tooling directive: no installs or upgrades were needed (curl/grep/tar/sha256sum sufficed).
