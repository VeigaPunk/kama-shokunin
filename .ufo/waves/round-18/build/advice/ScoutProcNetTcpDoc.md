VERDICT: confirm — v7.2 proc_net_tcp.rst labels the local_address, state and inode columns but documents no state codes, no byte order and no IPv6 layout; `0A` is not in it.

# Scope
- Read-only recon; nothing written but this report. No lane file, frozen copy, receipt or lesson edited. No install; no package transaction; no server started; no socket bound (I used listeners already present on the host).
- Source opened 2026-10-20 by raw fetch at git tag v7.2:
  https://raw.githubusercontent.com/torvalds/linux/v7.2/Documentation/networking/proc_net_tcp.rst
  (blob: https://github.com/torvalds/linux/blob/v7.2/Documentation/networking/proc_net_tcp.rst)
  sha256 `a4da3f43ee9dc52e626c437ff3ebca1338c75e2465706f444e76be06e3f7e67a`, 57 lines.
- Tag identity: v7.2 -> commit `8d3ae59288f1e7d58d76558a6ee96d533bc5019f`, committer date 2026-08-16T21:32:26Z
  (api.github.com/repos/torvalds/linux/commits/v7.2).
- Staleness: this path's only history entry at v7.2 is commit `832619012c97`, 2020-04-30, "docs: networking: convert proc_net_tcp.txt to ReST".
  The file has not changed in ~6.5 years. Line numbers below are file lines of that raw file.

# Findings

## 1. local_address column — a label and nothing more
- L18 example row: `46: 010310AC:9C4C 030310AC:1770 01`.
- L23 labels the first hex field: "local IPv4 address"; L22 labels its port "local TCP port number"; L24 labels
  `46:` "number of entry".
- The doc never uses the live header name `local_address`; that name exists only in the /proc header itself
  (`sl  local_address rem_address   st tx_queue rx_queue tr tm->when retrnsmt   uid  timeout inode`, /proc/net/tcp line 1 here).
- It never states the numeric base: no occurrence of "hex", "hexadecimal", "base 16" or "decimal" anywhere.
  `9C4C` is 40012 and `1770` is 6000 only by convention.

## 2. state `0A` — not documented at all
- The doc's only label is L19 "`|--> connection state`", pointing at the example's `01`.
- The string `0A` occurs only as a substring of `010310AC` / `030310AC` on L18. There is no state code `0A` in the file.
- No state table exists. The file's single table, L48-57, is headed `timer_active:` with values 0-4 — a different column
  (`tr`, index 5), not `st`.
- L14-15 states only ordering, not codes: "It will first list all listening TCP sockets, and next list all established
  TCP connections."
- So `0A = LISTEN` cannot be sourced to this doc; the authority is code: include/net/tcp_states.h:13 `TCP_ESTABLISHED = 1,`
  through :22 `TCP_LISTEN,` — LISTEN is the tenth enumerator, value 10 = 0x0A. (The doc's own example `01` and the live
  rows' `0A` are consistent with that enum, but the doc never says so.)

## 3. inode column — named, unqualified
- L44: "`|          |    |-----------------------------> inode`", distinct from L42 "`location of socket in memory`"
  (the `%pK` sock pointer, index 11).
- The diagram's field order makes inode the 10th printed field, i.e. 0-based index 9; the live header agrees
  (`... uid  timeout inode`), so `parts[9]` in the frozen tool is the right index. Caveat: the doc and the live header
  label index 8 differently (doc: "unanswered 0-window probes"; header: `timeout`), so alignment should be taken from the
  live header, not from the doc's prose.
- The doc does not say the inode is decimal, does not define it, and never connects it to `socket:[inode]` fd symlinks.
  Source: `sock_i_ino(sk)` printed with `%llu` (net/ipv4/tcp_ipv4.c:2823), and `sock_i_ino` returns `sk->sk_ino`
  (include/net/sock.h:2156-2160). Open-request rows print 0 ("open_requests have no inode", tcp_ipv4.c:2756 comment).

## 4. Byte order — NOT documented
- Zero occurrences of endian / byte order / network order; no statement of numeric base (see §1).
- The example is only self-consistent under host-little-endian rendering: `010310AC` decodes to 172.16.3.1 little-endian
  and 1.3.16.172 big-endian; the peer `030310AC` likewise gives 172.16.3.3, a plausible pair. [INFERENCE that the example
  was captured on a little-endian host]
- Code ground (not the doc): net/ipv4/tcp_ipv4.c:2779 `__be32 src = inet->inet_rcv_saddr;` printed at :2813-2814 by
  `"%4d: %08X:%04X %08X:%04X %02X ..."` with no `ntohl` on the addresses (ports are `ntohs`'d at :2780-2781). The printed
  word is therefore the host's numeric interpretation of a big-endian integer, i.e. text is byte-reversed per 32-bit word
  on a little-endian host.

## 5. IPv6 — named, never specified
- `/proc/net/tcp6` appears at L4, L7 and L12 ("`and tcp6_seq_show() in net/ipv6/tcp_ipv6.c, respectively.`"); that is all.
- The example block is IPv4 only: no 32-hex-digit token, no `::` (the file's only `::` is the ReST literal marker at L16),
  no IPv4-mapped note, no word grouping, no separate tcp6 example.
- Code ground: net/ipv6/tcp_ipv6.c:2173-2179 prints `"%4d: %08X%08X%08X%08X:%04X %08X%08X%08X%08X:%04X "` from
  `src->s6_addr32[0..3]`, again without `ntohl`; include/uapi/linux/in6.h:38 `__be32 u6_addr32[4];` and :44
  `#define s6_addr32 in6_u.u6_addr32`. Each of four words is thus rendered by the host's numeric interpretation of
  big-endian bytes.
- Consequence on a little-endian host: `::1` renders `00000000000000000000000001000000`; `::ffff:127.0.0.1` renders
  `0000000000000000FFFF00000100007F` (word2 `FFFF0000`, word3 `0100007F`). The `::1` form is observed in §6; the mapped
  form is [INFERENCE] from the two code rows plus little-endian arithmetic.
- The doc is a weak authority by its own text, L8: "Note that these interfaces are deprecated in favor of tcp_diag."

## 6. Observed on this host, read-only, 2026-10-20 (no server started, nothing bound)
- `/proc/net/tcp` first row: `0: 0100007F:0277 00000000:0000 0A ... 8152 ...` = 127.0.0.1:631, state 0A, inode 8152.
- `/proc/net/tcp6` first row: `0: 00000000000000000000000001000000:0277 00000000000000000000000000000000:0000 0A ... 8151 ...`
  = [::1]:631; `ss -ltn6` independently reports `LISTEN 0 4096 [::1]:631 [::]:*`.
- A second tcp6 listener, `[::]:5355`, renders `0000000000000000000000000000000000000000`-style all-zero address with
  `:14EB` (0x14EB = 5355), state 0A.
- So the four-word little-endian rendering is not merely derived: the host's own kernel prints it, and the doc says
  nothing about it.

## 7. Direct relevance to C1's listener-ownership requirement
- Frozen `.ufo/waves/round-18/frozen/tools_kama-llamacpp-live.py:321-327` accepts a tcp6 address only if
  `addr_hex.endswith('00000001')` or `addr_hex[:24] == '0000000000000000FFFF00'`.
- Against the observed `::1` text `00000000000000000000000001000000`, `endswith('00000001')` is False; and the slice
  comparison is 24 characters against a 22-character literal, False by construction (verified: literal length 22,
  correct prefix length 24).
- Correct forms: `::1` -> `addr_hex == '00000000000000000000000001000000'`; `::ffff:127.0.0.0/104` ->
  `addr_hex[:24] == '0000000000000000FFFF0000' and addr_hex.endswith('7F')`. Note the mapped prefix literal must end
  `FFFF0000`, not `FFFF00…` — that is exactly the local word-order consequence of §5.
- Therefore every IPv6-loopback listener is invisible to `_listen_inodes` today, and a good server bound to
  `::ffff:127.0.0.1` (the contract's mandatory ACCEPT control) would be reported as not owning its port. That the control
  then fails/reports `None` is [INFERENCE] from code reading; the end-to-end demonstration belongs to the controls run.
- The v4 branch `addr_hex.endswith('7F')` is correct on this host (`0100007F` = 127.0.0.1 observed, and it accepts
  exactly 127.0.0.0/8) but is little-endian-specific [INFERENCE for big-endian hosts].

## 8. Anchors offered for new SOURCES rows (scribe/L1 decide; I did not edit SOURCES.md)
- Doc row: blob URL above + access 2026-10-20; quotes L23 "local IPv4 address", L19 "|--> connection state", L44 "... inode";
  scope "column labels only — no state codes, no byte order, no IPv6 layout"; sha256 `a4da3f43ee9dc52e626c437ff3ebca1338c75e2465706f444e76be06e3f7e67a`;
  caveat L8 deprecation and 2020-04-30 last change.
- Code row (tcp6 rendering): https://github.com/torvalds/linux/blob/v7.2/net/ipv6/tcp_ipv6.c lines 2173-2179 plus
  https://github.com/torvalds/linux/blob/v7.2/include/uapi/linux/in6.h lines 38, 44; sha256
  `dd3f400b6d29c940d298e0b0a600a82b32368219aee5bc8f17981b00bd7b0558` and
  `4b70a42300079eee8dc3bc9d6c327a04cbd8eb75b2fa9d995d9f0a3306d6b27d`.
- Code row (v4 rendering): https://github.com/torvalds/linux/blob/v7.2/net/ipv4/tcp_ipv4.c lines 2779, 2813-2814, 2823;
  sha256 `bdf50d980735746844c3b5ffea3d62794378572c62f69fda8ec821afb448c4d8`.
- Code row (state codes): https://github.com/torvalds/linux/blob/v7.2/include/net/tcp_states.h lines 13-22;
  sha256 `8a41dab66aa79bd0b185da5bbb9b4c72ad7f3efb11bf75d894a80f4273f9766c`.
- Census: no existing SOURCES row covers /proc/net/tcp{,6}. A grep of `corpus/SOURCES.md` for
  `proc/net|tcp6|IPv4-mapped|4291|tcp_states|LISTEN` matches only S037's server.cpp URL. Documentation/networking at v7.2
  has 129 entries; the only /proc tcp doc is `proc_net_tcp.rst` (others: dctcp, mptcp, tcp-thin, tcp_ao — unrelated).

# Limits
- The mapped-address rendering is derived, not observed: no host listener is bound to `::ffff:127.0.0.1` and I did not bind
  one (read-only seat). §7's correct-prefix literal follows from include/uapi/linux/in6.h:38/44 and tcp_ipv6.c:2173-2179.
- Big-endian host behaviour is [INFERENCE] from the same `%08X`-of-`__be32` rule; untested.
- I did not open rendered kernel.org HTML; the raw bytes at tag v7.2 are authoritative and digest-pinned above.
- Not checked: whether tcp_diag/`ss` reports addresses in a byte-order-agnostic way (out of scope), or any drift between
  this host's kernel 7.2.11-arch1-1 and tag v7.2.
- §7's end-to-end tool failure needs a control run; this seat only grounds the text format and the predicate arithmetic.

# Installs
None. No packages installed or upgraded; no pacman invocation; nothing added to the environment.

# Artifacts
- This report: `.ufo/waves/round-18/build/advice/ScoutProcNetTcpDoc.md`.
- Scratch fetches lived under /tmp only and were removed after digesting.
