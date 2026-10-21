VERDICT: confirm - census and validate reproduce the round-18 end state (56 rows, exit 0, W04 S031/S043/S056 documented); the lane's S057 row moves census to 57 (A 54, mined 46), exit 0, with no new W04.

# CensusPrefetch - round 19 census and validate

Axes: count parity with census-after, validate exit and warnings, W04 provenance.
Scope: `sources-census.sh census` and `validate --root /home/vgpnk/Projects/shokunin kama`, compared with `.ufo/waves/round-18/sources/census-after.txt`. Lane read-only. Receipts: `/tmp/kama-r19-CensusPrefetch/out/` (`receipt.txt`; re-run `out/run-census.sh`). Installs or updates: none.

## Executed commands and exits
Script: `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh` (806 lines, sha256 3fb72615...4d64e30).

| Command | Exit | Observed |
|---|---|---|
| `census --root /home/vgpnk/Projects/shokunin kama` | 0 | rows 57; tier A 54, B 0, C 3, invalid 0; mined 46, queued 5, rejected 6, invalid 0; missing 0 |
| `validate --root /home/vgpnk/Projects/shokunin kama` | 0 | `W04` S031, `W04` S043, `W04` S056, `ok` |
| Same two on private copy (`--file`, sha 791e630e...) | 0 / 0 | identical counts and W04 set |
| `validate` on committed HEAD `8bf99ca` tree | 0 | same three W04, ok |
| `census --file` on round-start tip `1b85a24` blob | 0 | rows 56, A 53, C 3, mined 45, queued 5, rejected 6 |
| `census --file` on committed tip `7229fa9` blob (read-only `git fetch`) | 0 | rows 57, A 54, mined 46 |
| `validate` on `7229fa9` tree | 0 | same three W04, ok |
| `selftest` | 0 | 96 killed, 0 SURVIVED |

Lane bracket: `corpus/SOURCES.md` sha256 932475538be7...739a7 before and after the lane runs (stable).

## Against census-after (sha256 adf3649f...)
- census-after equals the census at `1b85a24` and at HEAD `8bf99ca` (diff exit 0). The round-start count of 56 is confirmed.
- The lane differs by one row only: rows 56 to 57, tier.A 53 to 54, status.mined 45 to 46 (diff exit 1; FLEET mirror lines move identically).
- The new row is S057 (`man7.org ld.so(8)`, tier A, docs, mined, opened 2026-10-21, recheck on-release). Its used-by paths `corpus/lessons/round-19.md` and `registry/required-citations.json` exist. Against `8bf99ca`, SOURCES.md is +7 lines: the S057 row and an appended S055 paragraph.
- Committed tip `7229fa9` (reflog 03:34:47 -0300; subject "round-19: citation provenance, install-tree pin, r18 defect corrections") holds the same SOURCES bytes as the lane.

## Three W04s: expected
W04 is a same-URL, different-scope pair. An independent gawk pass over the 57 Registry rows found 0 malformed rows, 0 duplicate IDs, and exactly three URL groups of two, each with distinct scope labels.

| W04 row | Earlier row, same URL | Where the expectation is recorded |
|---|---|---|
| S031 | S011, `docs.ollama.com/api/tags` | `SCORECARD.md:273-274`; `corpus/lessons/round-11.md:44-45` |
| S043 | S037, llama.cpp `tools/server/server.cpp` @704366d | `corpus/SOURCES.md:179-180`; `corpus/lessons/round-17-verifier-spotcheck.md:190-192` |
| S056 | S054, llama.cpp `common/arg.cpp` @704366d | `corpus/lessons/round-18-verifier-spotcheck.md:114-116`; `LOG.md:1133-1134` |

- `census-after.txt` carries no validate lines. The expectation comes from the round-18 spotcheck and LOG entries above.
- The round-18 start receipt `.ufo/waves/round-18/sources-before-validate.txt` had two W04s (S031, S043). S056 is the round-18 addition.
- Script logic: W04 fires on any cross-scope URL repeat (`sources-census.sh:644-645`) and never reads `teaches`. The `supersedes S...` marker only exempts same-scope E04 (`:646-648`). The three are structural properties of the current scope labels, not suppressed errors. Exit stays 0 for warnings (`:16-17`).
- The round-19 addition introduces no new W04; S057's URL is unique.

## Caveats
1. The lane moved during the run. SOURCES.md was edited at 03:32:35 (+33 bytes). Only S057's teaches annotation changed: "(11 words)" and "(14 words)" became "(10 words)" and "(11 words, ...)". `wc -w` on the quoted strings gives 10 and 11, so the edit corrected real miscounts. Census and validate outputs are identical before and after. The author of the edit was not observed. The census does not check quote word counts.
2. Lane HEAD moved `8bf99ca` to `7229fa9` at 03:34:47. `1b85a24` to `8bf99ca` changed no SOURCES bytes.
3. E08 passes for S057 only because TODAY defaults to `date -u +%F` = 2026-10-21 (script `:661`). [INFERENCE: a validate run before that UTC date would flag S057; not executed.]
4. Not checked: S057 quotes against the man page (scout scope); behavior of the census script beyond its selftest.
