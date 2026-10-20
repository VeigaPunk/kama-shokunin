VERDICT: confirm — C1's four cited sources are load-bearing in shipped code, not decorative; new rows S048–S055 have Gate entries, opened dates, verbatim ≤25-word quotes and digest-verified anchors; the only S047 cell change is the declared used-by append. Two minor residuals found (legacy-schema argv first-vs-last mismatch; in6.h anchor digest without retained bytes; used-by index omissions), none fatal to the claim.

Scope: does C1 actually depend on opened S048/S050/S051/S054; are new Gate/access/quote cells complete; are immutable old cells unchanged. Lane at `1c325b2e58fcfdc6761f645b44cedfb1d65243e6`; all evidence below from the live checkout, read-only.

## Axis 1 — source dependence is real, not decorative

| Source | Load-bearing site | Verification |
|---|---|---|
| S048 (tcp6 `%08X` words of raw `s6_addr32`, no swap) | `tools/kama-llamacpp-live.py:311-325` `_tcp6_is_loopback` reverses each 4-byte host-endian word, not the 16-byte string | pinned `sources/raw/linux/v7.2/net/ipv6/tcp_ipv6.c` sha256 `dd3f400b…b0558` matches row; format at 2173, `src->s6_addr32[0]` at 2176 — row anchor exact |
| S050 (RFC 4291 `::1` exact; mapped 80z/16ones/IPv4) | `kama-llamacpp-live.py:323-325` tests `address == \0*15+\1` and `address[:12] == \0*10+\xff\xff and address[12]==127` (lane-derived 127/8 narrowing is disclosed as derivation, not RFC) | pinned `rfc4291.txt` sha `4d58dff6…de48b2` matches; quote text at lines 474, 551-552, layout ~570 — anchors exact |
| S051 (SystemExit/KI/GeneratorExit derive from BaseException) | 16 `except BaseException` sites in the tool (lines 1137-1586) funnel to `_record_internal` → `internal:<Exc>` → setup-error exit 2; selftest asserts `internal:KeyboardInterrupt` mapping (1095-1100) | pinned `exceptions.html` `766d785f…fcdd26`; §SystemExit text verbatim at HTML lines 854-856 (HTML splits the phrase — plain grep misses it) |
| S054 (duplicate flag warns, last wins; server never rejects) | gate `tests/llamacpp-live/check-receipt.py:506-515` re-derives *exact* argv for v3 rather than trusting recorded fields; knowledge doc `llamacpp-loading-lifecycle.md:250` cites S054 as the reason | pinned `llama-arg.cpp` sha `bf4c58c1…d5822d` matches; warn at 836, unknown-flag throw 830, `hostnames.clear()` 3338 — anchors exact |

**Frozen-vs-fixed contrast proven:** `git show e75cf680:tools/kama-llamacpp-live.py:311-343` shows the old predicate testing `endswith('00000001')` and `addr_hex[:24] == '0000000000000000FFFF00'` (24 vs the literal's 22 chars) — both unreachable for real `::1`/`::ffff:127/8`. M3's mined-mistake story checks out; the v3 rewrite is traceable to S048's format and S050's forms. Selftest (`_selftest`, lines 1037-1082) additionally binds real `::1`/`::ffff:127.0.0.1` sockets to `/proc/net/tcp6` rows.

**S052 not decorative — and correctly non-authoritative:** pytest exits are 1/5; the lane's table (`_outcome_exit`, 873-885) is pass 0 / fail 1 / not-evaluated 2. The lane borrows only the precedent that empty-observation ≠ failure while choosing its own numbers — exactly what the row and lesson declare ("precedent only, never authority for lane numbering"). No evidence S052's exit values leaked into the tool.

## Axis 2 — Gate rows, access dates, quotes (round-18.md:39-53)

All eight new registry rows have Gate entries. Every `opened` cell = 2026-10-20 and the Gate header records all sources opened that day. Quote audit (each verbatim against the pinned bytes, ≤25 words):

- S048: `src->s6_addr32[0], src->s6_addr32[1],` — line 2176 verbatim; format at 2173. Pass.
- S049: "Note that these interfaces are deprecated in favor of tcp_diag." — line 8 verbatim; only example IPv4 (`010310AC` line 18). Pass.
- S050: "The unicast address 0:0:0:0:0:0:0:1 is called the loopback address." — line 474 verbatim (14 words). Mapped quote at 551-552 verbatim. Pass.
- S051: "It inherits from BaseException instead of Exception so that it is not accidentally caught by code that catches Exception." — verbatim modulo HTML markup, 23 words. Pass.
- S052: "No tests were collected" / failure code 1 — verbatim at HTML lines 329-330,317. Pass.
- S053: "an exit status of 77 a skipped test, an exit status of 99 a hard error" — verbatim at automake.texi:9776-9777; rejection recorded honestly with the www.gnu.org timeout. Pass.
- S054: "DEPRECATED: argument '%s' specified multiple times, use comma-separated values instead (only last value will be used)" — verbatim at line 836 (21 words). Pass.
- S055: own-work row; Gate cites `receipt-1.json` `outcome:"pass"`, 11 checks, `VALID` — internally consistent with `runs/` artifacts.

## Axis 3 — immutable old cells

Cell-by-cell diff `e75cf680..1c325b2` over the parsed registry (python, split on `|`): 8 rows added (S048–S055), 0 removed, **exactly one cell changed in one old row**: S047 `used-by`: `corpus/lessons/round-17.md` → `corpus/lessons/round-17.md, corpus/knowledge/llamacpp-loading-lifecycle.md, corpus/lessons/round-18.md`. This is the declared old→new append (lesson lines 147-150). S047's status/recheck/scope/anchor/teaches/opened unchanged; S001–S046 byte-identical. Pass.

## Residual findings (non-fatal)

**F1 — legacy-schema `argv_flag` contradicts S054's "last wins" (minor, bounded).**
`check-receipt.py:233-240` returns the *first* occurrence: executed `argv_flag(['s','-m','m','--alias','a','--host','127.0.0.1','--port','1111','--port','2222','-c','1','-t','1','--no-webui','--offline'], '--port')` → `'1111'`, while arg.cpp's last-wins semantics mean the effective port is 2222. For v3 the exact-argv match (506-515) closes this; for v1/v2 receipts (which do carry `argv`, verified on `.ufo/waves/round-17/live/receipt-1.json`) a receipt whose recorded port matches the first `--port` while the smuggled last value differs would pass per-flag checks 481-486 — the same smuggle S054 teaches. Impact: consistency-with-own-source on the legacy path only. Smallest safe correction: make `argv_flag` return the last occurrence, or reject duplicate flags on pre-v3 receipts.

**F2 — S048 anchor cites an `in6.h` sha256 whose bytes are not retained.**
Row: "`__be32 u6_addr32[4];` at `include/uapi/linux/in6.h` line 38 (sha256 4b70a423…b27d)". `find .ufo/waves/round-18/sources -name 'in6.h'` → none; `pins.json` has no in6 entry (pins cover tcp6/tcp4/proc_net_tcp/rfc4291/exceptions/pytest/automake). The type claim is consistent with the row's own scope, but the digest is not locally re-verifiable like the others. Correction: pin `in6.h` under `sources/raw/linux/v7.2/include/uapi/` or drop the digest to a plain line anchor.

**F3 — used-by index omissions.**
S049 used-by lists only `loopback-listener-ownership.md` but the row is cited in `lessons/round-18.md:44`; S050 omits both `llamacpp-loading-lifecycle.md` (cited at line 254) and `lessons/round-18.md` — while S048 lists both correctly. Append `corpus/lessons/round-18.md` to S049/S050 and `corpus/knowledge/llamacpp-loading-lifecycle.md` to S050 (declared-append pattern, same as S047's).

## Checked and clean

- Big-endian tcp6 caveat is scoped out in the row ("not big-endian hosts") and the docstring, so word-reversal code is inside its declared scope — not a defect.
- `_child_running`'s `except Exception` (782) is nested under BaseException receipts at call sites (1433-1452); no uncontained escape found.
- Wildcard `::`/`0.0.0.0` fail-closed exclusion is disclosed as lane policy (knowledge doc:46-48), not smuggled as an RFC teaching.
- No runtime mutations performed; all checks read-only `git show`/`grep`/sha256sum/`argv_flag` import in-process.

Impacted axes: C1 sourced-operability stands; F1-F3 are bookkeeping/consistency repairs that strengthen the same claim. No install or tooling changes made.
