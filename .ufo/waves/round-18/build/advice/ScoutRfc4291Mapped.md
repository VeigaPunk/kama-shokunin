VERDICT: confirm — RFC 4291 §2.5.5.2 is 80 zero bits ‖ 16 one bits (FFFF) ‖ IPv4; §2.5.3 is 0:0:0:0:0:0:0:1 (`::1`); `::ffff:127.0.0.0/104` is exactly 127.0.0.0/8 mapped; and this host proves `/proc/net/tcp6` prints each 32-bit word byte-reversed, so the frozen `_listen_inodes` predicates match neither encoding.

Axes: A1 provenance (C1's encoded `[INFERENCE]` becomes sourced), A2 false-failure of the good-mapped-server control, A3 fix precision (a naive fix adds a false-accept).

## Observed — the RFC text

- https://www.rfc-editor.org/rfc/rfc4291 §2.5.5.2 — "A second type of IPv6 address that holds an embedded IPv4 address is defined." (14 words). The layout table reads
  `|                80 bits               | 16 |      32 bits        |`
  `|0000..............................0000|FFFF|    IPv4 address     |`
  i.e. 80 zero bits, then 16 one bits (`FFFF`), then the 32-bit IPv4 address. Preceded by "The format of the "IPv4-mapped IPv6 address" is as follows:" (10 words).
- https://www.rfc-editor.org/rfc/rfc4291 §2.5.3 — "The unicast address 0:0:0:0:0:0:0:1 is called the loopback address." (11 words). §2.4 lists it as `Loopback             00...1  (128 bits)   ::1/128         2.5.3`, i.e. an exact `/128`, not a prefix.
- §2.2 item 3 allows the mixed text form and shows `::FFFF:129.144.52.38`; §2.5.5.1's IPv4-compatible form (all-zero 80+16 bits) is deprecated and is not the mapped form.

## Observed — the /104

- `::ffff:127.0.0.0/104` = 80 zeros ‖ 16 ones ‖ `01111111` (127). Bit counts measured on Python 3.14.8 with `ipaddress`: bits 0-79 all zero, bits 80-95 all one, bits 96-103 `01111111`, 80+16+8 = 104. Canonical form is `::ffff:127.0.0.0/104` (input `::ffff:127.0.0.1/104` normalises to it); it is a subnet of `::ffff:0:0/96`, covers `::ffff:127.0.0.0`–`::ffff:127.255.255.255`, and excludes `::ffff:128.0.0.1`.
- Answer to the recon question: **`::ffff:127.0.0.0/104` is the unique IPv6 prefix equal to IPv4 127.0.0.0/8 mapped.** `::1` is a separate `/128` and is *not* inside it.

## Observed — `/proc/net/tcp6` packing on this host

- Kernel formatter: https://raw.githubusercontent.com/torvalds/linux/v6.12/net/ipv6/tcp_ipv6.c:2207-2213, `get_tcp6_sock` prints `"%4d: %08X%08X%08X%08X:%04X %08X%08X%08X%08X:%04X "` over `src->s6_addr32[0]…[3]`. Those words are `__be32` (https://raw.githubusercontent.com/torvalds/linux/v6.12/include/uapi/linux/in6.h:38, `__be32		u6_addr32[4];`), so on a little-endian host each 4-byte group is printed byte-reversed.
- Host endianness observed: `sys.byteorder == 'little'`, `platform.machine() == 'x86_64'`.
- Empirical, `/proc/net/tcp6` (accessed 2026-10-20), listening (state `0A`) rows captured live: `::1` bound on port 0x9511 → `00000000000000000000000001000000:9511`; `::ffff:127.0.0.1` bound on port 0xB617 → `0000000000000000FFFF00000100007F:B617`. Both match the ticket's suspected strings exactly.
- The mapped bind appeared **only** in `/proc/net/tcp6` (zero rows in `/proc/net/tcp`), so a child bound that way is invisible to the tool's IPv4 branch.
- General rule confirmed on a real non-mapped address: host address `2804:14d:5c56:36ef:2ed8:aeff:0:2c0` (`ip -6 addr`, 110 tcp6 rows) renders `4D010428EF36565CFFAED82EC0020000`; reversing each 4-byte group decodes back to `2804:014d:5c56:36ef:2ed8:aeff:0000:02c0` exactly. This rules out a `::1`-only coincidence.

## Observed — why the frozen predicates fail

`.ufo/waves/round-18/frozen/tools_kama-llamacpp-live.py:331-336`:

- `:332 addr_hex.endswith('00000001')` — `::1` renders `…01000000`, so the suffix test is false. The literal is right only for a big-endian host (there `%08X` of word 3 would be `00000001`); on this LE host it can never match.
- `:334 addr_hex[:24] == '0000000000000000FFFF00'` — the literal is **22** characters, the slice is **24**; `str` equality is length-exact, so this is unconditionally false. Correct 96-bit prefix in the packed rendering is `0000000000000000FFFF0000` (24 chars).
- I extracted `_listen_inodes` (frozen lines 311-342) via `ast` and executed it unmodified against fixtures using the real 14-column layout with inode in `parts[9]`: it returned only the IPv4 inode; the `::1` row (222) and the mapped row (333) were both dropped.
- `:315-318` docstring repeats the same two wrong claims ("::1 ends 00000001", "v4-mapped prefix 0000000000000000FFFF00"); it must be corrected with the code or it re-seeds the bug.
- `:337` `elif not addr_hex.endswith('7F')` for plain IPv4 is **correct** on this host: 127.0.0.1 packs to `0100007F`, so the first octet is the last two hex digits. No change needed.

Consequence for the frozen tool (code path read directly, no inference): an empty inode set makes `port_owned_by` return `None` (`:348-351`), which becomes `'port-listener-ownership-unproven'` (`:549-552`, `:637`) and then `raise SetupError(...)` after the readiness loop (`:1158-1163`), while `teardown_graceful` and `teardown_port_closed` additionally require `receipt.get('port_listener_ownership') == 'child'` (`:1317`, `:1330`). A good server on `::ffff:127.0.0.1` is therefore classified unproven/setup-error, not accepted — precisely the false failure C1 forbids. `[INFERENCE]` that llama-server itself accepts `--host ::ffff:127.0.0.1`; the kernel-level packing above was verified with a Python AF_INET6 socket, not llama-server. Note `:1091` hardcodes `'--host', '127.0.0.1'`, so a live mapped-good-server control needs an argv override or a socket-level stub.

## Advice for the C1 executor (A3: no false-accept)

Decode, do not pattern-match endianness-specific literals. Minimal host-correct predicate:

```python
raw = bytes.fromhex(addr_hex)
if sys.byteorder == 'little':
    raw = b''.join(raw[i:i+4][::-1] for i in range(0, 16, 4))
a = ipaddress.IPv6Address(raw)
loopback = a == ipaddress.IPv6Address('::1') or (
    a.ipv4_mapped is not None
    and a.ipv4_mapped in ipaddress.IPv4Network('127.0.0.0/8'))
```

- Pure-hex equivalent if a decoder is unwanted: `addr_hex == '00000000000000000000000001000000'` **or** (`addr_hex.startswith('0000000000000000FFFF0000')` and `addr_hex.endswith('7F')`). Verified: accepts `::ffff:127.0.0.1` and `::ffff:127.255.255.255`, rejects `::ffff:128.0.0.1` and `::`.
- **Do not** "fix" `::1` with `endswith('01000000')`: `2001:db8::1` renders `B80D0120000000000000000001000000` and would be falsely accepted as loopback. `::1` must be an exact 32-character match.
- Keep the `::` wildcard excluded (fail-closed); with a decoder it is excluded automatically.
- Cheap local checks for the controls seat: a mapped-good-server fixture must yield `port_listener_ownership == 'child'`; a stranger on `::1`/mapped must be `foreign` (not `unproven`), since the current code collapses both to the empty-set/`None` case.

## Prior coverage

Round-17 already observed both encodings and flagged the 22-vs-24 literal (`.ufo/waves/round-17/falsify/advice/LoopbackOwnership.md:8-11`) but left the byte order as `[INFERENCE]` (`.ufo/waves/round-17/falsify/advice/RevengerToolGrowth.md:117`, "I did not exercise IPv6 or validate kernel byte-order representations"). This seat closes that gap with the kernel formatter at a pinned tag, the `__be32` declaration, and three live `/proc/net/tcp6` samples including a global address. Note that `LoopbackOwnership.md:9` says "the frozen function returned `True`" for a mapped listener; executing the round-18 frozen copy as-is returned neither tcp6 inode, so that sentence should not be cited as baseline validation.

## Limitations

- No LSP device is mounted in this session (no `lsp` entry in the available tools), so definitions were read directly; `grep` was used only to locate line numbers, never as semantic proof.
- Byte-order demonstration is x86-64 little-endian only; on a big-endian host the frozen `::1` literal would be correct and the mapped literal would still be 22-vs-24. Any fix must stay endianness-aware.
- llama-server was not launched; no port from `registry/endpoint-consumers.tsv` was bound. All test sockets were loopback-only, one at a time, closed in-process; `ss -ltn` confirmed none of the test ports (46615, 38161, 35389) remain listening.
- No tools installed or updated (pacman paused host-wide; nothing needed).
