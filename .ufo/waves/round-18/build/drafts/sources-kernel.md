# Draft: SOURCES rows S048-S050 and round-18 `## Gate` lines (ScribeSourcesKernel)

Status: append-ready draft for L1. Not applied to `corpus/SOURCES.md`, not applied to any lesson.
All sources opened 2026-10-20. Provisional ids S048-S050; L1 renumbers if the registry moved.
Row shape copies S042-S047: 11 cells (`id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by`).

## Registry rows (append after S047)

| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |
|---|---|---|---|---|---|---|---|---|---|---|
| S048 | Linux kernel `get_tcp6_sock` and `tcp6_seq_show` @ v7.2 (tag commit 8d3ae59288f1e7d58d76558a6ee96d533bc5019f) — https://github.com/torvalds/linux/blob/v7.2/net/ipv6/tcp_ipv6.c | code | A | how `/proc/net/tcp6` prints each address in the v7.2 source: four `%08X` words of raw `s6_addr32`, no byte swap; not other kernel versions, not `/proc/net/tcp` (IPv4) | `get_tcp6_sock` 2126-2179 (format string 2173-2174, `src->s6_addr32[0..3]` 2176); `tcp6_seq_show` 2225-2246; header `local_address` 2233; raw `net/ipv6/tcp_ipv6.c` sha256 dd3f400b6d29c940d298e0b0a600a82b32368219aee5bc8f17981b00bd7b0558 (identical at the commit URL, fetched 2026-10-20); uapi `include/uapi/linux/in6.h` @ v7.2 sha256 4b70a42300079eee8dc3bc9d6c327a04cbd8eb75b2fa9d995d9f0a3306d6b27d, line 38 `__be32 u6_addr32[4];`, line 44 `#define s6_addr32 in6_u.u6_addr32` | Each IPv6 address field is printed as four 32-bit words with `%08X` from `__be32` values and no `htonl`. On a little-endian host `::1` therefore prints `00000000000000000000000001000000` (ends `01000000`), and `::ffff:127.0.0.1` prints `0000000000000000FFFF00000100007F`. [INFERENCE from C type and format semantics; the `::1` form is also observed on the host, see Gate.] | mined | 2026-10-20 | on-release | corpus/lessons/round-18.md (created by L1) |
| S049 | Linux kernel `Documentation/networking/proc_net_tcp.rst` @ v7.2 — https://github.com/torvalds/linux/blob/v7.2/Documentation/networking/proc_net_tcp.rst | docs | A | the documented meaning of `/proc/net/tcp` and `/proc/net/tcp6` entries and their deprecation; not the IPv6 address byte encoding | title and intro lines 4-12 (`deprecated in favor of tcp_diag` at line 8; implementing functions `tcp6_seq_show()` in `net/ipv6/tcp_ipv6.c` at line 12); IPv4 example `46: 010310AC:9C4C` at line 18; raw sha256 a4da3f43ee9dc52e626c437ff3ebca1338c75e2465706f444e76be06e3f7e67a | Names `tcp6_seq_show()` as the implementation and calls the interface deprecated in favour of tcp_diag. Its only address example is IPv4, so the IPv6 byte order must come from code (S048), not from this page. | mined | 2026-10-20 | on-release | corpus/lessons/round-18.md (created by L1) |
| S050 | RFC 4291 — IP Version 6 Addressing Architecture (Feb 2006, Standards Track) — https://www.rfc-editor.org/rfc/rfc4291 and https://www.rfc-editor.org/rfc/rfc4291.txt | spec | A | IPv6 text representation, the loopback address and the IPv4-mapped form; not `/proc` output format and not any kernel's printing | §2.2 text forms (`::FFFF:129.144.52.38` example); §2.5.3 "The Loopback Address" lines 472-474; §2.5.5.2 "IPv4-Mapped IPv6 Address" lines 548-552 with diagram `|0000..0000|FFFF|    IPv4 address     |` at line 570; raw .txt sha256 4d58dff6b432d5d524bf3a3b7f0337a4177fa65f92ed72f2a92e97b471de48b2 | `0:0:0:0:0:0:0:1` is the loopback address `::1`; an IPv4 node's address is represented as an IPv4-mapped address whose high 80 bits are zero, bits 80-95 are `FFFF`, and the low 32 bits are the IPv4 address. Standards Track; obsoletes RFC 3513. | mined | 2026-10-20 | 180d | corpus/lessons/round-18.md (created by L1) |

## Round-18 lesson `## Gate` rows (candidate for R1 and C1 claims)

All sources opened 2026-10-20. Quotes are verbatim and at most 25 words.

| Candidate | Decision | Source, location, quote |
|---|---|---|
| `/proc/net/tcp6` prints each address as four `%08X` words of raw `s6_addr32` | admit, scoped to v7.2 source (S048) | https://github.com/torvalds/linux/blob/v7.2/net/ipv6/tcp_ipv6.c line 2173 `"%4d: %08X%08X%08X%08X:%04X %08X%08X%08X%08X:%04X "`; line 2176 `src->s6_addr32[0], src->s6_addr32[1],`; type at https://github.com/torvalds/linux/blob/v7.2/include/uapi/linux/in6.h line 38 `__be32 u6_addr32[4];` |
| `::1` reads `00000000000000000000000001000000` in `/proc/net/tcp6` on this host | admit, scoped to this host at read time (observed, not a lane receipt) | `/proc/net/tcp6` line 1, read 2026-10-20 on kernel 7.2.11-arch1-1: `0: 00000000000000000000000001000000:0277 ...`; port 0x0277 is a host listener, not lane-owned; no port was bound by the scribe |
| `::ffff:127.0.0.1` reads `0000000000000000FFFF00000100007F` in `/proc/net/tcp6` | admit as [INFERENCE] only; not observed | derived from S048 (word order and `__be32` print) and S050 (IPv4-mapped form, https://www.rfc-editor.org/rfc/rfc4291.txt line 570). `grep -c 0000FFFF /proc/net/tcp6` on this host read 0 rows at read time, so no observation exists; a seat must bind an AF_INET6 `::ffff:127.0.0.1` listener to observe it |
| `::1` is the loopback address | admit (S050) | https://www.rfc-editor.org/rfc/rfc4291.txt line 474 "The unicast address 0:0:0:0:0:0:0:1 is called the loopback address." |
| IPv4-mapped addresses represent IPv4 nodes as IPv6 addresses | admit, scoped to address-text meaning (S050) | https://www.rfc-editor.org/rfc/rfc4291.txt lines 551-552 "This address type is used to represent the addresses of IPv4 nodes as IPv6 addresses." |
| `proc_net_tcp.rst` defines the IPv6 address byte order | reject | https://github.com/torvalds/linux/blob/v7.2/Documentation/networking/proc_net_tcp.rst lines 4-12 name `tcp6_seq_show()` and give only an IPv4 example at line 18 `46: 010310AC:9C4C`; the page has no IPv6 address format (S049) |
| The v7.2 tcp6 format is the same on every kernel release | reject as unobserved; unknown | S048 covers one tag, v7.2 (commit 8d3ae592, dated 2026-08-16 by the GitHub API). Earlier kernels were not opened |
| The lane tool recognises `::1` listeners in `/proc/net/tcp6` | reject; mined mistake (C1 owns the fix) | tools/kama-llamacpp-live.py line 332 `addr_hex.endswith('00000001')`; the observed `::1` ends `01000000`, so the test never matches. Line 333 `addr_hex[:24]` is compared to the 22-character literal `'0000000000000000FFFF00'` at line 333-334, which can never be equal |

## Unknown and not checked

- Whether Arch's shipped 7.2.11 kernel patches `get_tcp6_sock` or the seq_file format: not checked. Only the upstream v7.2 tag was opened.
- Whether `/proc/net/tcp6` output is identical on big-endian hosts: not checked; the byte-order claim is for this little-endian x86_64 host only.
- The `::ffff:127.0.0.1` row above is derived, not observed. It becomes a sourced observation only after a seat's receipt.
- The round-18 lesson file does not exist yet; the `used-by` cells name it as L1's creation.
- Recheck intervals (`on-release` for the kernel rows, `180d` for the RFC) are proposals copied from existing row vocabulary; L1 decides.

## Provenance

- Fetched 2026-10-20 with curl into /tmp (scratch, removed): tcp_ipv6.c, proc_net_tcp.rst, rfc4291.txt, in6.h; tag v7.2 resolved to commit 8d3ae59288f1e7d58d76558a6ee96d533bc5019f (annotated tag object 237a1c39e8dfd3e1c6f1f023eea37a48ec04cc63) via the GitHub API.
- Commit-URL raw copy of tcp_ipv6.c hashed identically to the tag copy (dd3f400b6d29c940d298e0b0a600a82b32368219aee5bc8f17981b00bd7b0558).
- Installs or updates: none.
