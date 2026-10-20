VERDICT: partial — S048-S050 opened and drafted; the `::1` byte order in /proc/net/tcp6 is confirmed by v7.2 source and this host, the `::ffff:127.0.0.1` form is derived only.

# ScribeSourcesKernel report (round 18, build wave)

## Behavior
Drafted append-ready SOURCES rows S048-S050 and round-18 `## Gate` rows in
`.ufo/waves/round-18/build/drafts/sources-kernel.md` (sha256 821684505f0520adda4d7038369c67755583a57970f9abc2ac6a0d7d6ee00022). Nothing applied to `corpus/SOURCES.md`, lessons or lane code. Access date for every source: 2026-10-20.

## Sources opened this session
- Linux v7.2 `net/ipv6/tcp_ipv6.c`, https://raw.githubusercontent.com/torvalds/linux/v7.2/net/ipv6/tcp_ipv6.c, sha256 dd3f400b6d29c940d298e0b0a600a82b32368219aee5bc8f17981b00bd7b0558. Identical bytes at commit 8d3ae59288f1e7d58d76558a6ee96d533bc5019f (https://raw.githubusercontent.com/torvalds/linux/8d3ae59288f1e7d58d76558a6ee96d533bc5019f/net/ipv6/tcp_ipv6.c). Tag v7.2 resolved via the GitHub API (annotated tag object 237a1c39e8dfd3e1c6f1f023eea37a48ec04cc63).
  - line 2173 quote: `"%4d: %08X%08X%08X%08X:%04X %08X%08X%08X%08X:%04X "`
  - line 2176 quote: `src->s6_addr32[0], src->s6_addr32[1],`
  - line 2233 quote: `"local_address                         "`
- Linux v7.2 `Documentation/networking/proc_net_tcp.rst`, sha256 a4da3f43ee9dc52e626c437ff3ebca1338c75e2465706f444e76be06e3f7e67a.
  - line 8 quote: "Note that these interfaces are deprecated in favor of tcp_diag."
  - line 12 quote: "and tcp6_seq_show() in net/ipv6/tcp_ipv6.c, respectively."
  - line 18 has the only address example, IPv4 `46: 010310AC:9C4C`.
- Linux v7.2 `include/uapi/linux/in6.h`, https://raw.githubusercontent.com/torvalds/linux/v7.2/include/uapi/linux/in6.h, sha256 4b70a42300079eee8dc3bc9d6c327a04cbd8eb75b2fa9d995d9f0a3306d6b27d.
  - line 38 quote: `__be32		u6_addr32[4];`
- RFC 4291, https://www.rfc-editor.org/rfc/rfc4291.txt, sha256 4d58dff6b432d5d524bf3a3b7f0337a4177fa65f92ed72f2a92e97b471de48b2.
  - line 474 (§2.5.3) quote: "The unicast address 0:0:0:0:0:0:0:1 is called the loopback address."
  - lines 551-552 (§2.5.5.2) quote: "This address type is used to represent the addresses of IPv4 nodes as IPv6 addresses."
  - line 570 diagram: `|0000..............................0000|FFFF|    IPv4 address     |`
- Lesson format: `corpus/lessons/round-17.md` lines 54-66 (`## Gate` table shape). Registry shape: `corpus/SOURCES.md` lines 54-59 (S042-S047, 11 cells, verified by awk).
- Lane tool, read only: `tools/kama-llamacpp-live.py` lines 331-335.
- Host, read only: `/proc/net/tcp6` rows 0-5 and `/proc/net/tcp` rows 0-2 (`uname -r` = 7.2.11-arch1-1).

## Findings
1. The `::1` byte order is supported. Source: the `%08X` words come from `__be32` values with no byte swap (in6.h line 38), so the host-order print of `::1` is `...01000000`. Host row 0 of `/proc/net/tcp6` shows `00000000000000000000000001000000:0277` [observed, port 631 host listener]. [INFERENCE] for the general rule, observed for this host.
2. The lane tool's tcp6 branch cannot match `::1`. tools/kama-llamacpp-live.py line 332 tests `addr_hex.endswith('00000001')`, but the real value ends `01000000`. Line 333 compares `addr_hex[:24]` to the 22-character literal `'0000000000000000FFFF00'` (line 334), which can never be equal. Recorded as a mined mistake; C1 owns the fix.
3. `::ffff:127.0.0.1` reads `0000000000000000FFFF00000100007F` by derivation (S048 + S050). Not observed: `grep -c 0000FFFF /proc/net/tcp6` read 0 on this host. [INFERENCE]; needs a seat's observation.
4. `proc_net_tcp.rst` does not define IPv6 address byte order. Rejected as a Gate candidate.

## Gate candidates
Written in the draft, round-18 `## Gate` table: admit S048 scoped; admit `::1` observed on host; admit `::ffff` as [INFERENCE]; admit S050 `::1` and IPv4-mapped text; reject the doc-defines-byte-order claim; reject "same on every kernel" as unobserved; reject the lane tool's `::1` match as a mined mistake.

## Limitations and unknowns
- Arch's shipped 7.2.11 kernel is not compared with upstream v7.2. Arch patches to `get_tcp6_sock` are not checked.
- Only v7.2 was opened. Earlier and later kernels were not checked, so the format is not shown stable.
- The big-endian case is not checked.
- The round-18 lesson file does not exist yet; `used-by` names it as L1's creation.
- The recheck periods are proposed using the registry's existing vocabulary.
- Provisional ids S048-S050 need L1 renumbering against the current registry (last id S047).
- The host observations are read-only `/proc` reads, not lane receipts; no port was bound and no lane measurement was run.

## Installs and updates
None. Used curl (already present) and the GitHub API for ref resolution.

## Files
- Written: `.ufo/waves/round-18/build/drafts/sources-kernel.md` (sha256 821684505f0520adda4d7038369c67755583a57970f9abc2ac6a0d7d6ee00022).
- Written: `.ufo/waves/round-18/build/advice/ScribeSourcesKernel.md` (this report).
- Scratch `/tmp/r18-sk` created and removed.
- Not touched: lane tracked files, frozen copies, `corpus/SOURCES.md`, any lesson, `.ufo/state/`, and `interactive-sessions/`.
