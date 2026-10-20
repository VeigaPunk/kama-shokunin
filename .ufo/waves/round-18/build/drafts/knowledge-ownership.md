source: S048 (Linux kernel v6.12 `net/ipv6/tcp_ipv6.c` lines 2213-2218 and `net/ipv4/tcp_ipv4.c` lines 2932-2934 row printers, and `include/net/tcp_states.h` lines 12-22 state enum; sha256 in the S048 row); S049 (man-pages 6.19 `proc_pid_net(5)` and `proc_pid_fd(5)`, fetched 2026-10-20); S050 (RFC 4291 §2.5.3 and §2.5.5.2); own-work host probe 2026-10-20 (kernel 7.2.11-arch1-1, x86-64, Python 3.14.8; scratch script `/tmp/r18-kco/listener_probe.py`, not yet a lane artifact); lane predicate `tools/kama-llamacpp-live.py` lines 326-339 at the e75cf680 tree
verified-at: 2026-10-20 — kernel, RFC and man-page text opened this session; the five-listener probe and the `::1` / `::ffff:127.0.0.1` hex were observed on this host in the same session
recheck: on-release — re-read the kernel row printers and re-run the probe when the host kernel, Python or the harness predicate changes; the table below is a dated observation, not service state

# Loopback listener ownership on Linux

## Claim

A Linux harness can prove that a TCP listener on a loopback port belongs to
its own child process by matching one kernel socket inode in two places: the
LISTEN row in `/proc/net/tcp` or `/proc/net/tcp6`, and a `socket:[inode]` link
in the child's `/proc/<pid>/fd`. The row's local address decides whether the
listener is on loopback; the inode decides whether it is the child's. Both
parts are needed. The address hex is host-byte-order dependent and is easy to
misread, and the current `tools/kama-llamacpp-live.py` `_listen_inodes`
predicate misreads the IPv6 loopback form (see below).

## Mechanism

1. **Rows.** `/proc/net/tcp` (IPv4) and `/proc/net/tcp6` (IPv6) list one row
   per TCP socket. Fields are `sl`, `local_address`, `rem_address`, `st`, …,
   `uid`, `timeout`, `inode`. The state is hexadecimal; LISTEN is `0A`
   (S048: `include/net/tcp_states.h` enum starts `TCP_ESTABLISHED = 1` and
   lists `TCP_LISTEN` tenth, so 10 = `0x0A`). The inode is field 10 (index 9
   after splitting on whitespace).
2. **Ports.** The port is printed as plain `%04X` (S048: `"%4d: %08X:%04X %08X:%04X"`
   in the IPv4 printer). Probe: a socket bound to port 36057 appeared as
   `0100007F:8CD9`, and 0x8CD9 = 36057.
3. **Child fd table.** `readlink /proc/<pid>/fd/<n>` for a socket returns
   `socket:[<inode>]`; S049 (`proc_pid_fd(5)`): "For sockets, that inode can be
   used to find more information in one of the files under /proc/net/." The
   probe confirmed the same inode for the fd and the LISTEN row for all five
   bind kinds below.
4. **Namespace.** S049 (`proc_pid_net(5)`): "these files and directories now
   expose information for the network namespace of which the process is a
   member." A reader sees the tables of its own network namespace, not those of
   a container the child may run in.
5. **Permission.** S049 (`proc_pid_fd(5)`): "Permission to dereference or read
   (readlink(2)) the symbolic links in this directory is governed by a ptrace
   access mode PTRACE_MODE_READ_FSCREDS check." A harness that cannot read the
   child's fd links cannot prove ownership; it must report unknown, not
   "foreign".

## Address encoding (exact hex)

- **IPv4 (`/proc/net/tcp`).** One `%08X` of the 32-bit address (S048,
  `tcp_ipv4.c` 2932: `"%4d: %08X:%04X %08X:%04X"`). The address is an integer
  read in host order, so on x86-64 the printed octets are reversed. 127.0.0.1
  prints as `0100007F`; 0.0.0.0 as `00000000`. The high-order octet is therefore
  the last two hex digits: an address is in 127/8 iff it ends in `7F`
  (observed; the code path at `tools/kama-llamacpp-live.py:337` relies on this
  and it is correct for IPv4).
- **IPv6 (`/proc/net/tcp6`).** Four `%08X` words, one per `s6_addr32[i]`
  (S048, `tcp_ipv6.c` 2213-2217: `"%4d: %08X%08X%08X%08X:%04X …"` with
  `src->s6_addr32[0]` … `[3]`). Each 4-byte group is printed as a native
  (little-endian on x86-64) integer, so the bytes of each group appear reversed.
  Observed on this host (2026-10-20):

  | Listener bound to | `/proc/net/tcp6` local address (exact) |
  |---|---|
  | `::1` | `00000000000000000000000001000000` |
  | `::ffff:127.0.0.1` (IPv4-mapped) | `0000000000000000FFFF00000100007F` |
  | `::` (wildcard) | `00000000000000000000000000000000` |

  Check against RFC 4291 (S050): the loopback address is "0:0:0:0:0:0:0:1"
  (§2.5.3), and the IPv4-mapped form is "0000..............................0000|FFFF|    IPv4 address"
  (§2.5.5.2). The byte-reversal is a host-endianness fact, not a property of
  the address: a big-endian host would print the network order.

  Consequence: `::1` is the 32-character string ending `01000000`, not
  `00000001`. The IPv4-mapped 127/8 form is the 32-character string whose first
  24 characters are `0000000000000000FFFF0000` and whose last two characters
  are `7F`.

## Wildcard listeners (`0.0.0.0` and `::`)

- A wildcard listener's row carries the all-zero address (`00000000:…` in
  `/proc/net/tcp`, the all-zero 32-character string in `/proc/net/tcp6`).
  The address alone does not say which loopback address it serves.
- Observed: a `0.0.0.0` listener accepted a client connect to `127.0.0.1`, and
  a `::` listener accepted a connect to `::1` (probe, 2026-10-20). A wildcard
  listener therefore answers on loopback and is reachable through it.
- Ownership is still decided by the inode, which does not depend on the bind
  address. A wildcard listener whose inode is in the child's fd table is the
  child's listener. The lane's `_listen_inodes` discards wildcard rows
  (`tools/kama-llamacpp-live.py:337-338`, fail-closed); that is a harness
  policy, not a kernel fact. Under that policy a child bound to `0.0.0.0` is
  reported as having no proven loopback owner.
- Unknown: whether a specific-address LISTEN and a wildcard LISTEN on the same
  port can coexist on the pinned kernel; not tested here.

## What the current lane predicate gets wrong

`tools/kama-llamacpp-live.py` lines 331-336 accept an IPv6 row (fragments below are verbatim; the `[:24]` test spans two source lines)
if `addr_hex.endswith('00000001')` or if `addr_hex[:24] == '0000000000000000FFFF00'`
and it ends in `7F`. The first test fails for `::1` (the observed string ends in
`01000000`); the second compares a 24-character slice with a 22-character
literal and cannot be equal. The docstring at lines 314-315 repeats the wrong
`::1 ends 00000001` form. Python on the observed strings: `endswith('00000001')`
is False for `::1`; the slice/literal lengths are 24 and 22. A correct test is the
full 32-character equality for `::1` and the 16-zero / `FFFF0000` / `7F`-ending
test for the IPv4-mapped 127/8 form. Fixing the predicate is the C1 lane's
decision; this entry records the table only.

## Limits

- Linux only. The `/proc/net` and `/proc/<pid>/fd` formats are kernel-specific
  text interfaces. The row printers were read at kernel tag v6.12 (S048); the
  host runs 7.2.11 and the format matched the probe there, but the 7.2 source
  was not read [INFERENCE that the printers are unchanged between 6.12 and 7.2].
- Namespaces: the tables show only the reader's network namespace (S049). A
  listener in a container or another netns is invisible to a harness outside it.
  Not tested.
- Byte order: the hex above was observed on x86-64 little-endian only. A
  big-endian host is not tested and the byte-reversal does not hold there.
- Race: `/proc/net` and `/proc/<pid>/fd` are read at different instants. A
  listener can exit and its inode be reused between the two reads [INFERENCE
  from the kernel's per-read snapshots; no reuse was induced]. A harness should
  re-read both after a match.
- Probe scope: five listeners on loopback ephemeral ports, one process,
  IPv4 and IPv6 only; no non-loopback address, no `SO_REUSEPORT`, no
  IPV6_V6ONLY=0 wildcard versus v4 coexistence test.

## Unknown

- Whether the 7.2 host kernel's printers match v6.12 byte for byte (only the
  observed output was compared).
- Whether a non-root harness can read another user's `/proc/<pid>/fd`
  (S049: governed by PTRACE_MODE_READ_FSCREDS; not tested with a second user).

## Sources (provisional rows S048-S050; access 2026-10-20)

- **S048** — Linux v6.12 `net/ipv6/tcp_ipv6.c` lines 2212-2218 (`get_tcp6_sock`
  row format), `net/ipv4/tcp_ipv4.c` lines 2931-2934, and
  `include/net/tcp_states.h` lines 12-22.
  URLs: https://raw.githubusercontent.com/torvalds/linux/v6.12/net/ipv6/tcp_ipv6.c ,
  https://raw.githubusercontent.com/torvalds/linux/v6.12/net/ipv4/tcp_ipv4.c ,
  https://raw.githubusercontent.com/torvalds/linux/v6.12/include/net/tcp_states.h .
  sha256 (fetched 2026-10-20): tcp_ipv6.c `197f0783…`, tcp_ipv4.c `116196ff…`,
  tcp_states.h `8a41dab6…`. Located quote, tcp_ipv6.c:2213: `"%4d: %08X%08X%08X%08X:%04X %08X%08X%08X%08X:%04X "`.
- **S049** — man-pages 6.19 `proc_pid_net(5)` and `proc_pid_fd(5)`, fetched
  2026-10-20: https://man7.org/linux/man-pages/man5/proc_pid_net.5.html ,
  https://man7.org/linux/man-pages/man5/proc_pid_fd.5.html . Located quotes:
  proc_pid_fd(5) "For sockets, that inode can be used to find more information in one of the files under /proc/net/."; proc_pid_net(5) "these files and directories now expose information for the network namespace of which the process is a member."
- **S050** — RFC 4291 (Feb 2006) §2.5.3 and §2.5.5.2:
  https://www.rfc-editor.org/rfc/rfc4291.txt . Located quotes: §2.5.3 "The unicast address 0:0:0:0:0:0:0:1 is called the loopback address."; §2.5.5.2 "A second type of IPv6 address that holds an embedded IPv4 address is defined."
