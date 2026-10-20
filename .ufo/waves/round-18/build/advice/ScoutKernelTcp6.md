VERDICT: confirm — v7.2 `get_tcp6_sock` prints four `%08X` of `__be32 s6_addr32[]`, so on LE x86_64 `/proc/net/tcp6` is byte-reversed per 32-bit word; `::1` = `00000000000000000000000001000000`, `::ffff:127.0.0.1` = `0000000000000000FFFF00000100007F`, and the shipped `_listen_inodes` predicate rejects every loopback IPv6 form.

# Host

- `uname -r` → `7.2.11-arch1-1`; `uname -m` → `x86_64`. Host Python `3.14.8`.
- Source baseline: tag **v7.2** exists (fetched 200). Because the host runs **7.2.11**, I additionally fetched the stable tree at `v7.2.11` and diffed the whole function: **byte-identical** to v7.2 (`get_tcp6_sock` starts at stable line 2127, tag line 2126). No fallback to a different v7.x tag was needed.
- Documentation sanity check: `Documentation/networking/proc_net_tcp.rst` at v7.2 documents **only the IPv4** layout (`010310AC:9C4C` examples, "local IPv4 address", lines 18-24) and says the interfaces are "deprecated in favor of tcp_diag" (line 8). It gives **no** tcp6 byte-order rule — do not cite it as authority for tcp6.

# 1. The printing code (observed)

https://github.com/torvalds/linux/blob/v7.2/net/ipv6/tcp_ipv6.c#L2172-L2179

```
2172	seq_printf(seq,
2173		   "%4d: %08X%08X%08X%08X:%04X %08X%08X%08X%08X:%04X "
2174		   "%02X %08X:%08X %02X:%08lX %08X %5u %8d %llu %d %pK %lu %lu %u %u %d\n",
2175		   i,
2176		   src->s6_addr32[0], src->s6_addr32[1],
2177		   src->s6_addr32[2], src->s6_addr32[3], srcp,
2178		   dest->s6_addr32[0], dest->s6_addr32[1],
2179		   dest->s6_addr32[2], dest->s6_addr32[3], destp,
```

Quote (format string, line 2173): `"%4d: %08X%08X%08X%08X:%04X %08X%08X%08X%08X:%04X "`

`src` is the **local** address: line 2140-2141 set `dest = &sp->sk_v6_daddr; src = &sp->sk_v6_rcv_saddr;`, and `%5` (first quad) is printed from `src`. So column 2 of the line (`parts[1]`) is local, matching the header `local_address`.

The TIME_WAIT sibling at **tcp_ipv6.c:2212-2219** uses the same address format (truncated tail: no `rto ato quick cwnd ssthresh`). It prints `tw_substate`, so TIME_WAIT rows carry state `06`, not `0A` — irrelevant to a LISTEN-only reader, but it confirms the address encoding is identical.

# 2. Why it is byte-reversed on little-endian x86_64 (derivation)

- `include/uapi/linux/in6.h:33-44`: `struct in6_addr { union { __u8 u6_addr8[16]; ... __be32 u6_addr32[4]; } ... }`, with `#define s6_addr32 in6_u.u6_addr32`. So the same 16 bytes are viewable as four 32-bit words.
- `include/uapi/linux/types.h:39`: `typedef __u32 __bitwise __be32;` — `__be32` is a **plain scalar `__u32`**, annotated `__bitwise` only for sparse. It is **not** a struct with accessors, so `%08X` takes its numeric value directly; **no `ntohl()` is applied** anywhere in the print path.
- Consequence: for a word whose on-wire (network-order) bytes are `b0 b1 b2 b3`, the CPU loads them little-endian into a register as `b3<<24 | b2<<16 | b1<<8 | b0`, and `%08X` then prints `b3 b2 b1 b0`. **The four bytes of each 32-bit word appear in reversed order.**

General decoding rule for `/proc/net/tcp6`, column `parts[1]` before `:`:

```
print  =  w0 w1 w2 w3            (each wi = b3 b2 b1 b0 of its wire word)
decode =  for each 8-char group, reverse the 4 bytes
```

# 3. Exact hex strings (asked for explicitly)

| address | wire bytes (16) | per-word `%08X` | `/proc/net/tcp6` local field |
|---|---|---|---|
| `::` (unspecified) | `00…00` | `00000000` ×4 | `00000000000000000000000000000000` |
| `::1` | `00000000000000000000000000000001` | w3: bytes `00 00 00 01` → `01000000` | `00000000000000000000000001000000` |
| `::ffff:127.0.0.1` | `00000000000000000000FFFF7F000001` | w2: `00 00 FF FF` → `FFFF0000`; w3: `7F 00 00 01` → `0100007F` | `0000000000000000FFFF00000100007F` |
| `::ffff:127.0.0.2` | `00000000000000000000FFFF7F000002` | w3 → `0200007F` | `0000000000000000FFFF00000200007F` |
| `::ffff:8.8.8.8` | `…0000FFFF` + `08 08 08 08` | w3 → `08080808` | `0000000000000000FFFF000008080808` |

Note the two rows of interest are **different shapes**: `::1` is the fourth word `01000000` with three zero words; the v4-mapped form keeps the `::ffff:` marker as `FFFF0000` in word 2 and pushes the reversed IPv4 tail into word 3.

# 4. Empirical proof on this host (observed, not inferred)

Ran one AF_INET6 loopback listener at a time on an ephemeral port, read `/proc/net/tcp6` state `0A` for that port, and compared against the prediction `''.join('%08X' % w for w in struct.unpack('<4I', inet_pton(AF_INET6, addr)))`. All exact matches:

```
bind('::1')            port=58695  predicted/observed 00000000000000000000000001000000  MATCH True
bind('::ffff:127.0.0.1') port=41817 predicted/observed 0000000000000000FFFF00000100007F  MATCH True
bind('::ffff:127.0.0.2') port=42935 predicted/observed 0000000000000000FFFF00000200007F  MATCH True
```

Independent live corroboration needing no listener of mine — the host already had (row 0 of `/proc/net/tcp6`, a cupsd listener):

```
0: 00000000000000000000000001000000:0277 00000000000000000000000000000000:0000 0A ...
```

`:0277` = 631, and the address is exactly the `::1` string above. Also live: one row with `00000000000000000000000000000000:14EB` (`::`, port 5355, resolved/LLMNR) — confirming the `::` all-zeros form the tool deliberately treats as not-loopback-owned.

# 5. The shipped predicate is broken for both IPv6 loopback forms (observed)

`tools/kama-llamacpp-live.py:311-342`. Docstring at **:315** asserts `"::1 ends 00000001"` — that is factually wrong; it ends `01000000`. The tcp6 branch **:331-336**:

```
331  if proc_net.endswith('tcp6'):
332      if not (addr_hex.endswith('00000001')
333              or (addr_hex[:24]
334                  == '0000000000000000FFFF00'
335                  and addr_hex.endswith('7F'))):
336          continue
```

Evaluating exactly these expressions against the host-observed fields:

```
::1                  field=00000000000000000000000001000000 accepted=False
::ffff:127.0.0.1     field=0000000000000000FFFF00000100007F accepted=False
::ffff:127.0.0.2     field=0000000000000000FFFF00000200007F accepted=False
```

Two independent defects:

1. **:332** `endswith('00000001')` tests the wrong end. With four `%08X` words, a loopback `::1` word is `01000000`. This literal would only match an address whose last word is bytes `01 00 00 00`, i.e. `...:100:0:0:0`-shaped — never `::1`.
2. **:333-335** is **dead code**: `addr_hex[:24]` yields a 24-character string, but `'0000000000000000FFFF00'` is **22 characters** (verified: `len(literal)=22`, `len(slice)=24`). Two strings of unequal length are never equal, so the mapped branch can never fire. Even at the intended length the prefix is wrong: the correct 24-char prefix of `::ffff:127.0.0.1` is `0000000000000000FFFF0000` (the `FFFF0000` is the `::ffff:` marker word); the literal instead stops mid-word at `...FFFF00`.

Causal consequence, traced through the call graph (observed):

- `_listen_inodes` returns an empty set for any loopback IPv6 listener → `port_owned_by` hits `if not inodes: return None` at **:350-352**.
- `readiness_loop` **:548-552** assigns `ownership = None` and, because `owned is not True`, returns `'port-listener-ownership-unproven'`; the docstring at :348 names `None` "no listener yet, or /proc unreadable (ownership unknown)".
- **:1145-1147** maps `None → 'unproven'` in the receipt, and **:1155** `raise SetupError(fail)` aborts the run.

Net effect: a **healthy** llama-server bound to `::1` or `::ffff:127.0.0.1` is reported as a setup error — a false failure, exactly the C1 `good-rejected` counter. The default gateway (`--host 127.0.0.1`) stays on the IPv4 branch and is unaffected.

# 6. Fix guidance, and the over-acceptance trap

The obvious one-token edit (`'00000001'` → `'01000000'`) **is unsafe**. Verified:

```
::1          00000000000000000000000001000000  endswith('01000000')=True
2001:db8::1  B80D0120000000000000000001000000  endswith('01000000')=True   <-- global unicast
fe80::1      000080FE000000000000000001000000  endswith('01000000')=True   <-- link-local
::2          00000000000000000000000002000000  endswith('01000000')=False
```

`endswith('01000000')` would accept `2001:db8::1` and `fe80::1` as loopback owners — a new `accepted-bad` defect that the R5/R7 controls would need to catch. `::1` must be matched by **exact equality** with the full 32-character field.

Minimal correct predicate, verified against a hostile set:

```python
_LOOPBACK6_V4MAPPED = '0000000000000000FFFF0000'   # ::ffff: marker, reversed words
if not (addr_hex == '00000000000000000000000001000000'
        or (addr_hex.startswith(_LOOPBACK6_V4MAPPED) and addr_hex.endswith('7F'))):
    continue
```

Results: `::1` True, `::ffff:127.0.0.1` True, `::ffff:127.0.0.2` True, and `2001:db8::1` False, `::2` False, `fe80::1` False, `::ffff:8.8.8.8` False, `::` False.

Why `endswith('7F')` **is** correct for the mapped 127/8 case: the printed last word is `c b a 7F` in hex-digit order (octets 4,3,2,1), so the trailing `7F` is precisely the first IPv4 octet. Checked at both ends of the range: `::ffff:127.0.0.0` → `0000007F` (ends `7F`, accept), `::ffff:0.0.0.127` → `7F000000` (reject).

# 7. IPv4 sibling branch is correct (do not "fix" it)

`/proc/net/tcp` prints `%08X` of the single `__be32 s_addr` with the same reversal, so 127/8 really does end in `7F`. Observed by binding `127.0.0.5` on an ephemeral port: `/proc/net/tcp` gave `0500007F:A8C5` → `endswith('7F')` True. The branch at **:337** is sound as written.

# 8. Field index used by the tool

`parts[9]` is the inode in both files. Verified against the v7.2 argument list (:2175-2195: `i`, 4 addr words, `srcp`, 4 addr words, `destp`, `state`, `write_seq-snd_una`, `rx_queue`, `timer_active`, `tm_when`, `retransmits`, `uid`, `probes_out`, `sock_i_ino`, `refcnt`, `sp`, …) → whitespace split gives `0:sl 1:local 2:remote 3:st 4:tx:rx 5:tr:when 6:retrnsmt 7:uid 8:timeout 9:inode`. Matches the live row (`... 8151 1 ...` with inode 8151) and the `len(parts) < 10` guard at :326.

# Limitations

- No llama-server was started; no receipt was produced. Ports 8080/34113 and every port in `registry/endpoint-consumers.tsv` were avoided; each test listener was a single ephemeral AF_INET6 bind, closed in `finally`, and `ss -ltn` confirmed 58695/41817/42935/43205 absent afterwards.
- All scratch files under `/tmp/kama-r18-ScoutKernelTcp6-*` were removed.
- The claim that a good `::ffff:127.0.0.1` server is *classified* setup-error rather than merely unowned follows the observed code path (:548-552 → :1155) but was **not** executed end-to-end [INFERENCE on the exit code only; the `None`/`'unproven'` mapping itself is observed].
- I did not read `tests/llamacpp-live/controls.py` or `check-receipt.py`; which retained control *should* cover this shape is the controls seat's call.
- No installs or upgrades; nothing in `~/.local/bin` was touched.

# What C1/controls should take from this

- `::1` and `::ffff:127.0.0.1` are **two distinct strings**, and neither is a suffix of the other; a control that only covers one leaves the other unguarded.
- A retained control for the good-IPv6 shape must assert the *acceptance* side (exit 0), otherwise the predicate can regress to `return False` and every control still passes.
- Add the `2001:db8::1` / `fe80::1` addresses as negative controls so the `endswith('01000000')` shortcut cannot be reintroduced.
