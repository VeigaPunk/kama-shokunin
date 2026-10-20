source: S048 (Linux v7.2 tcp6 row printer), S049 (proc_net_tcp documentation, not an IPv6 encoding authority), S050 (RFC 4291); own-work `.ufo/waves/round-18/build/advice/ProbeTcp6Format.md` (raw bind/procfs/fd experiments), `tools/kama-llamacpp-live.py` `_listen_inodes` and `port_owned_by`
verified-at: 2026-10-20 — kernel source, RFC and loopback probes opened in round 18 on kernel 7.2.11-arch1-1, x86-64
recheck: on-release — reopen the kernel row printer and rerun `python3 tools/kama-llamacpp-live.py --selftest` after kernel, Python or ownership-parser changes; this is mechanism evidence, not current service state

# Loopback listener ownership on Linux

## Address encoding

S048's `get_tcp6_sock` prints four `%08X` words from `src->s6_addr32[0..3]`
(`net/ipv6/tcp_ipv6.c` v7.2:2172-2179). Their type is `__be32`
(`include/uapi/linux/in6.h`:38). There is no byte swap before printing.
On this little-endian host each four-byte word consequently appears reversed,
not the whole 16-byte address. S049 names this implementation but does not
specify IPv6 byte order; do not cite its IPv4 example as authority for tcp6.

| Bind address | Observed procfs local-address hex | Lane ownership policy |
|---|---|---|
| `127.0.0.1` | tcp `0100007F` | allow 127/8 |
| `::1` | tcp6 `00000000000000000000000001000000` | allow exact loopback |
| `::ffff:127.0.0.1` | tcp6 `0000000000000000FFFF00000100007F` | allow mapped 127/8 |
| `::` | tcp6 `00000000000000000000000000000000` | refuse wildcard |

All four forms were observed with freshly bound ephemeral sockets in
`ProbeTcp6Format.md`; `127.1.2.3` and its mapped form were also exercised.
RFC 4291 (S050) defines `::1` as the exact loopback address and the mapped
form as 80 zero bits, 16 one bits and the IPv4 address. Thus mapped 127/8 is
`::ffff:127.0.0.0/104`, not the whole mapped /96.

A suffix test for `01000000` alone is insufficient: it also accepts
`2001:db8::1` and `fe80::1`. Decode all words according to host endianness,
then test the whole address (or its `ipv4_mapped` address); do not reverse the
entire hex string. Big-endian output is not observed by this round.

## Ownership join — observed mechanism

The loopback bind address does not identify the process. The lane joins a
LISTEN row on the selected port (state `0A`) to its inode (split-field index 9),
then reads only its child PID's fd symlinks and matches `socket:[inode]`.
`ProbeTcp6Format.md` retains the raw rows, function results, experiment source
and final listener audit. On the frozen tool IPv4 matched its child's inode;
`::1` and mapped 127/8 returned no inode and ownership `None` even though
HTTP through the mapped listener answered 200. The v3 parser corrects that
false negative and its selftest checks real loopback sockets as well as
literal procfs rows.

Wildcard sockets can answer loopback connections. Excluding `0.0.0.0` and
`::` is the harness's loopback-only safety policy, not a claim that the child
cannot own their inodes. Unknown/no readable matching listener is not proof
of a foreign service. The parser's caller distinguishes `True`, `False` and
`None`; missing procfs evidence must not be turned into proven ownership.

## Limits

Linux procfs only; one little-endian host and one network namespace. The
address and child-fd reads are not atomic: a process/socket can change between
reads [INFERENCE]. No container namespace, inode reuse, cross-user permission,
SO_REUSEPORT or big-endian experiment was performed. Kernel docs call these
interfaces deprecated in favour of tcp_diag (S049); the retained parser is a
bounded harness mechanism, not a general socket-discovery API.

The pre-round predicate at `e75cf680` tested `endswith('00000001')` for `::1`
and compared a 24-character prefix against a 22-character literal for mapped
addresses. Both errors are mined in `lessons/round-18.md`; that old description
is historical, not the current v3 predicate.
