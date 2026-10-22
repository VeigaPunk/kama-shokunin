# ReopenS106 check log (round 25, attempt 2, wave 2, falsify)

Target: SOURCES row S106 (corpus/SOURCES.md:118) and its Gate line (corpus/lessons/round-25.md:22).
Pinned URL: https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/common/fit.cpp
Access date: 2026-10-22 (fetch at 10:07:05Z). Scratch copies: /fast/scratch/hyaku/kama-r25a2w2/ReopenS106/.
No llama-server started. No port opened. No git write, no commit, no jj mutation. No tool installed or upgraded.

| # | Check | Command (abridged) | Exit | Result |
|---|---|---|---|---|
| 1 | Fresh fetch | curl -sSfL -o fit.cpp <pinned raw URL> | 0 | HTTP 200, 52124 bytes, 1113 lines (wc -l) |
| 2 | sha256 against row anchor | sha256sum fit.cpp; grep -c <hash> corpus/SOURCES.md | 0 / 0 | 1f83da2a5dc460b893373365e07341695be80d6c662e53679032a138cce4dd58; found once, SOURCES.md:118 |
| 3 | Blob identity at the pinned commit | git hash-object fit.cpp; GET api.github.com/repos/ggml-org/llama.cpp/contents/common/fit.cpp?ref=704366d7... | 0 / 0 | Both give 7a03008295089f1d9e1a2c2f9666199ead03da12 |
| 4 | Commit exists | GET api.github.com/repos/ggml-org/llama.cpp/commits/704366d7... | 0 | HTTP 200 |
| 5 | Blob page in row URL | curl -sS -o /dev/null -w %{http_code} <github blob URL> | 0 | HTTP 200 |
| 6 | Gate quote exact and on line | grep -nF <quote> fit.cpp | 0 | One match, line 270 |
| 7 | Gate quote length | wc -w on quote text | 0 | 18 words (limit 25) |
| 8 | Row shape | tr -cd on SOURCES.md:118 and :11 | 0 | 12 pipes each (11 cells) |
| 9 | Census validate (read only, stdout only) | scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama | 0 | 30 lines: 1 ok, 29 W04, stderr 0 bytes; no S106 line. Copy: out/ReopenS106/census-validate.out |
| 10 | Lane tip | jj --ignore-working-copy log -r fa3b62ae... | 0 | fa3b62ae6475d111eb466d79af616aeebb08bbb9, round-25 commit |
| 11 | Writes to cparams->n_ctx in fit.cpp | grep for n_ctx assignments | 0 | Lines 216, 272, 414, 426, 430 only; 216 writes the extra (draft) model copy; the rest sit inside the auto branch (271, 393-394) |
| 12 | n_seq_max uses in fit.cpp | grep | 0 | Line 197 only (no per-slot division in fit.cpp) |
| 13 | Source of hp_nct | grep | 0 | fit.cpp:144 hp_n_ctx_train = llama_model_n_ctx_train(model); used at 192, 267 |
| 14 | Read cited ranges | read fit.cpp 29-63, 180-215, 254-288, 379-463, 879-908 | 0 | Lines 264 (first probe), 384, 414, 424, 441-444 read; see report |
| 15 | Entry uses of S106 | grep S106 corpus/knowledge/context-capacity.md | 0 | Lines 1, 74, 157, 166 |
| 16 | Every fit claim in entry | grep fit, read 59-103 and 145-185 | 0 | Read; see report section 5 |
| 17 | Pinned sibling sources (for default and call-site checks only) | curl common.h, arg.cpp, common.cpp, llama-context.cpp; sha256sum | 0 | common.h sha 8bcc5708c856653b0094ba312030df9c2f43ec2703e8ad78474fd4339d2540a9; arg.cpp sha bf4c58c189a774f2308acfe88e4ec5cebb0c43f60cf05cef4c5b2b9affd5822d; common.cpp sha d10ea1ff4253a1d6aedef3e73f16c3f2297975ca17254a82fac395aa2213ebd4; llama-context.cpp sha 2a25e556cb0d16725e01ce853fb1b76da91dcb41b803ce1a6bacec89bfb94aa5 |
| 18 | Default and mapping | grep common.h, arg.cpp, common.cpp | 0 | common.h:457 n_ctx = 0 (0 = trained context); common.h:485 fit_params_min_ctx = 4096; arg.cpp:1642-1649 (-c; 0 sets fit_params_min_ctx = UINT32_MAX); arg.cpp:2935-2938 (--fit-ctx); common.cpp:1243, 1245, 1270, 1274 (fit call site, cparams passed by pointer); common.cpp:1711-1714 (n_ctx copied) |
| 19 | X1 raw log construction order | grep constructing llama_context; read X1.server.log 280-286, 808-814, 1342-1346, 1606-1612 | 0 | Constructions at 281 (n_ctx 2048, log 283), 810 (n_ctx 8192, log 812), 1342 (n_ctx 8192, log 1344); load_model at 1610; slots n_ctx 2048 at 1612-1618 |
| 20 | Per-slot division in llama.cpp | grep n_seq_max llama-context.cpp | 0 | Line 382: cparams.n_ctx_seq = cparams.n_ctx / cparams.n_seq_max |
| 21 | Wave-1 seat report | read a2-build/advice/SrcFitCpp.md | 0 | Same omissions as the row: no 384 gate, no 414/441-444 floor path |
| 22 | Correction rule | read corpus/README.md 66-70 | 0 | "Correct still-live source anchors through new cited correction entries; historical corpus samples stay immutable." |
| 23 | Registry cites of common/common.h | grep -c common/common.h corpus/SOURCES.md | 0 | 0 rows |

Files written by this seat:
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-25/a2-falsify/out/ReopenS106/checks.md (this file)
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-25/a2-falsify/out/ReopenS106/census-validate.out (copy of scratch output)
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-25/a2-falsify/advice/ReopenS106.md (report)
- Scratch only (/fast/scratch/hyaku/kama-r25a2w2/ReopenS106/): fit.cpp, api-contents-fit.json, arg.cpp, common.cpp, common.h, llama-context.cpp, census-validate.out, census-validate.err
