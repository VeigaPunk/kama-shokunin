VERDICT: confirm — S048's v7.2 printer lines, `__be32` word type and per-32-bit-word little-endian printing reproduce byte-exactly against a fresh fetch, the retained pin and five real ephemeral binds; the knowledge entry matches the sources on every claim. Three non-killing correspondence defects (in6.h bytes unpinned, a 404 Gate URL, and an observation pointer narrower than the full strings) lower the evidence-trail grade but do not falsify the claim.

Seat `KamaR18.ReopenS048`, falsify wave, 2026-10-20. Lane tip under test `1c325b2e58fcfdc6761f645b44cedfb1d65243e6` (`git -C /tmp/kama-r18-falsify-ReopenS048/clone rev-parse HEAD` → exact, `status --porcelain` → 0 lines). Read-only against the lane; the only runtime experiment is the ephemeral bind re-derivation named in this item, run from the separate clone. No production, fleet, frozen-evidence or registry file was edited.

# Axes

- **Claim truth**: does `net/ipv6/tcp_ipv6.c` at v7.2 print four `%08X` words of `s6_addr32` with no byte swap, as S048 says?
- **Byte-level provenance**: do the retained raw pins hash to the live v7.2 bytes, and do the cited line numbers land on the cited tokens?
- **Derivation**: do `::1` and mapped 127/8 produce the hex strings taught, on this host and running kernel?
- **Correspondence**: does `corpus/knowledge/loopback-listener-ownership.md` say only what S048/S049/S050 and its own-work probe support?
- **Harm**: loopback-only ephemeral listeners, no registered-consumer port, full teardown.

# Sources opened (2026-10-20)

| artifact | sha256 | bytes |
|---|---|---|
| retained `.ufo/waves/round-18/sources/raw/linux/v7.2/net/ipv6/tcp_ipv6.c` | `dd3f400b6d29c940d298e0b0a600a82b32368219aee5bc8f17981b00bd7b0558` | 65016 |
| live `raw.githubusercontent.com/torvalds/linux/v7.2/net/ipv6/tcp_ipv6.c` (curl, exit 0) | `dd3f400b6d29c940d298e0b0a600a82b32368219aee5bc8f17981b00bd7b0558` | 65016 |
| live `.../v7.2/include/uapi/linux/in6.h` | `4b70a42300079eee8dc3bc9d6c327a04cbd8eb75b2fa9d995d9f0a3306d6b27d` | 7593 |
| live `.../v7.2/include/linux/in6.h` (wrapper: `#include <uapi/linux/in6.h>` at :20) | `40ddb27f4fa4f4526cdaedcbb6611133448b66fac8830b055ee6a6b11a116a42` | 1861 |
| live `.../v7.2/include/uapi/linux/types.h` | not recorded (text checked only) | 2035 |
| live `.../v7.2/include/uapi/asm-generic/int-ll64.h` | not recorded (text checked only) | 879 |

The retained and live `tcp_ipv6.c` are the same bytes, not merely the same nominal tag: equal sha256 and equal byte count. `pins.json` (`6f5623975d68c95bd65dd5abb067cffdab3c296e26caba06d3915ba97161a26d`, identical in `sources/` and `build/out/SourcePins/`) records `linux_tag.tag = v7.2`, `commit = 8d3ae59288f1e7d58d76558a6ee96d533bc5019f`. GitHub API agrees: `refs/tags/v7.2` → annotated tag object `237a1c39e8dfd3e1c6f1f023eea37a48ec04cc63` (`type: tag`) → `object.type = commit`, `object.sha = 8d3ae59288f1e7d58d76558a6ee96d533bc5019f`. Matches `corpus/SOURCES.md:60` exactly.

# 1. The four-word printer (observed, retained file)

`net/ipv6/tcp_ipv6.c` v7.2, raw line numbers:

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

`get_tcp6_sock` starts at **2126** (`static void get_tcp6_sock(struct seq_file *seq, struct sock *sp, int i)`) and the pinned block 2126–2198 ends on the function's closing `}` (the next line 2199 is blank). The retained pin `pins.json` key `tcp6_socket_row` has range `[[2126, 2198]]`; its `verbatim` string is byte-equal to the raw slice (`verbatim_matches_raw_range True`, `verbatim_sha256 6a9f31352a57c645f74981135506600581246914d5f555dcf74acb02cd263a6d`). The locator is unique: `grep -n "^static void get_tcp6_sock"` → only `2126`.

The local address is the first quad: lines 2140–2141 set `dest = &sp->sk_v6_daddr; src = &sp->sk_v6_rcv_saddr;`, and 2176–2177 print `src` before `destp`. No `ntohl`/`ntohs` touches the address words; the only swaps in the function are the ports, `destp = ntohs(inet->inet_dport)` and `srcp = ntohs(inet->inet_sport)` at 2142–2143. `tcp6_seq_show` begins at 2225, its header row has `local_address` at 2233, and it dispatches non-TIME_WAIT/non-NEW_SYN_RECV rows to `get_tcp6_sock` at 2246 (LISTEN is such a row).

# 2. Type, and why "no byte swap" is right

`tcp_ipv6.c:31` includes `<linux/in6.h>`, which includes `<uapi/linux/in6.h>` at `:19`. In the pinned v7.2 header:

```
38			__be32		u6_addr32[4];
44	#define s6_addr32		in6_u.u6_addr32
```

`__be32` is a plain scalar in normal builds, not an accessor type: `types.h` has `#ifdef __CHECKER__ / #define __bitwise __attribute__((bitwise)) / #else / #define __bitwise / #endif` (27–31) and `typedef __u32 __bitwise __be32;` (39); `asm-generic/int-ll64.h:27` is `typedef unsigned int __u32;`. So `%08X` consumes the numeric value of a 32-bit unsigned word with zero conversion. On a little-endian CPU the four wire bytes `b0 b1 b2 b3` load as `b3<<24|b2<<16|b1<<8|b0` and print `b3 b2 b1 b0` — each 4-byte group reversed, the 16-byte address not reversed as a whole. This is exactly S048's claim and exactly the knowledge entry's sentence at `corpus/knowledge/loopback-listener-ownership.md:12`.

# 3. Hex re-derivation with real ephemeral binds

Experiment source is embedded verbatim at the end. Run from `/tmp/kama-r18-falsify-ReopenS048/clone` (cwd) with `python3 -B`; exit 0. One listener at a time, `bind(...,0)`, closed in `finally`; every assigned port was asserted outside `{8080, 34113}`.

| bind | port | observed `/proc` local hex | predicted per-word `<4I` | network-order encoding | per-word match | network match |
|---|---|---|---|---|---|---|
| AF_INET6 `::1` | 59199 | `00000000000000000000000001000000` | same | `00000000000000000000000000000001` | true | false |
| AF_INET6 `::ffff:127.0.0.1` (V6ONLY=0) | 45091 | `0000000000000000FFFF00000100007F` | same | `00000000000000000000FFFF7F000001` | true | false |
| AF_INET6 `::ffff:127.1.2.3` (V6ONLY=0) | 49235 | `0000000000000000FFFF00000302017F` | same | `00000000000000000000FFFF7F010203` | true | false |
| AF_INET6 `::` (V6ONLY=0) | 51143 | `00000000000000000000000000000000` | same | same (cannot distinguish) | true | true |
| AF_INET `127.0.0.1` | 45211 | `0100007F` | `0100007F` | `7F000001` | true | false |

These reproduce the knowledge-entry table rows `:18-21` and probe cases A–D (`build/advice/ProbeTcp6Format.md:136,161`, etc.). Host: `uname -r 7.2.11-arch1-1`, `uname -m x86_64`, Python 3.14.8, `sys.byteorder little`.

Shape predictions (no bind) confirm the knowledge entry's trap at `:29-31`: `::1` → `…01000000`; `2001:db8::1` → `B80D0120000000000000000001000000`; `fe80::1` → `000080FE000000000000000001000000` — the last two also end `01000000`, so a one-token `endswith('01000000')` fix would accept global/link-local addresses. The correct mapped-prefix test is also exact: `::ffff:127.0.0.0` → `…FFFF00000000007F` (accept), `::ffff:127.255.255.255` → `…FFFF0000FFFFFF7F` (accept), `::ffff:0.0.0.127` → `…FFFF00007F000000` (reject), `::ffff:255.0.0.127` → `…FFFF00007F0000FF` (reject), `::7f00:1` → `0000000000000000000000000100007F` (reject on prefix), `::` zeros (reject), and `::ffff:1.0.0.0` → `…00000001` (the frozen `endswith('00000001')` would accept it).

The v3 parser matches the taught mechanism: `tools/kama-llamacpp-live.py:311 _tcp6_is_loopback` reverses each 4-byte group of the 32-char field, then accepts only `address == b'\0'*15 + b'\1'` or (`address[:12] == b'\0'*10 + b'\xff\xff'` and `address[12] == 127`); `:348 _listen_inodes` reads `/proc/net/tcp` and `/proc/net/tcp6`; `:354` states wildcards are deliberately fail-closed. `tools/kama-llamacpp-live.py:1037-1051` tests the literal rows `::1`, `::ffff:127.0.0.1`, `::2`, `::`; `:1053-1082` binds real `::1` and `::ffff:127.0.0.1` listeners and checks both `_listen_inodes` membership and `_tcp6_is_loopback(local_hex)`.

# 4. Retained-pin comparison

- `sources/raw/linux/v7.2/net/ipv6/tcp_ipv6.c` == live v7.2 fetch (sha256 and size above).
- `pins.json` `documents.linux_tcp6` = `{saved_as: raw/linux/v7.2/net/ipv6/tcp_ipv6.c, format: text, sha256: dd3f400b…, bytes: 65016, identity: {title: TCP over IPv6, version: Linux v7.2}}`.
- `pins.json` `pins.tcp6_socket_row` range 2126–2198, verbatim equals raw slice, start anchor matches the unique signature, end is `}`.
- The duplicate copies under `build/out/SourcePins/` are byte-identical to `sources/` for both `pins.json` and `tcp_ipv6.c`.

Line-number verdict: the lesson's "format at 2173" and the registry's "format at 2172-2174, `src->s6_addr32[0..3]` at 2176-2177" are both exact against the raw file. The earlier probe's mined mistake — the URL reader view drifting +1 on this file — did not leak into the delivered S048 text.

# 5. Running-kernel bridge (v7.2 vs host 7.2.11)

The registry scopes S048 to v7.2 ("not other kernel versions"), while the knowledge entry is dated against host `7.2.11-arch1-1`. `raw.githubusercontent.com/torvalds/linux/v7.2.11/...` returns 404 (and v7.2.10 too), but `gregkh/linux` stable tag `v7.2.11` returns 200 for both files. Extracted and compared:

- `get_tcp6_sock` v7.2 vs v7.2.11: identical, 2403 bytes, sha256 `6a9f31352a57c645f74981135506600581246914d5f555dcf74acb02cd263a6d` (stable function starts at line 2127, tag at 2126; format line therefore 2174 vs 2173 — a +1 line shift, body byte-identical).
- `include/uapi/linux/in6.h` v7.2.11 sha256 `4b70a42300079eee8dc3bc9d6c327a04cbd8eb75b2fa9d995d9f0a3306d6b27d` — identical to v7.2.
- Whole `tcp_ipv6.c` differs (`cc8f8c48c4b9008f52ee66901df04555090c94638278b448bc8b2b3d68ed0fc4`, 65043 bytes) at file level, but not inside the function that carries the claim.

Arch's own patch set was not inspected; the host observation (sections 3) is the direct evidence for 7.2.11 behavior, and it matches the v7.2 source exactly.

# 6. Knowledge-entry source correspondence

`corpus/knowledge/loopback-listener-ownership.md` (`source:` line cites S048/S049/S050 + own-work probe + the two lane functions):

| entry claim | check | verdict |
|---|---|---|
| `:9-10` four `%08X` words from `src->s6_addr32[0..3]`, v7.2:2172-2179 | raw lines 2172–2179 above; pin block 2126–2198 | holds |
| `:11` type `__be32` at `include/uapi/linux/in6.h`:38 | line 38 exact; include chain `tcp_ipv6.c:31 → linux/in6.h:20 → uapi` | holds |
| `:11-12` no byte swap; per-four-byte-word reversal on this little-endian host | `types.h:27-31,39`, `int-ll64.h:27`; five binds match per-word and reject network order except all-zero `::` | holds |
| `:18` `127.0.0.1` → `0100007F` | bind 45211 | holds |
| `:19` `::1` → `00000000000000000000000001000000` | bind 59199 | holds |
| `:20` `::ffff:127.0.0.1` → `0000000000000000FFFF00000100007F` | bind 45091 | holds |
| `:21` `::` → all zeros, refuse wildcard | bind 51143; `_tcp6_is_loopback` rejects zeros | holds |
| `:23-24` all four forms plus `127.1.2.3` and its mapped form exercised in the probe | `ProbeTcp6Format.md` cases A–F (`:136,161,180` case D etc.); my bind `::ffff:127.1.2.3` matches | holds |
| `:25-27` RFC 4291 mapped = 80 zero bits, 16 ones, IPv4; mapped 127/8 = `::ffff:127.0.0.0/104` | raw `rfc4291.txt:568-572`; loopback `:474` | holds |
| `:29-31` suffix `01000000` also accepts `2001:db8::1`, `fe80::1` | shape table above; probe Finding 10 | holds |
| `:31-32` decode all words, test whole address/`ipv4_mapped`, never reverse whole string | v3 parser `:311-326`; shape table | holds |
| `:37` state `0A` and inode index 9 | `_proc_listener_inode` `:328-346`; raw rows observed | holds |
| `:39-41` probe retains raw rows, function results, experiment source, final listener audit | `ProbeTcp6Format.md:86-1316`, source at `:944`, audit at `:824` | holds |
| `:41-42` frozen IPv4 matched its child; `::1`/mapped returned None although mapped HTTP answered 200 | probe cases A–C (`:97-180`) | holds |
| `:43-44` v3 parser corrects it; selftest checks real sockets and literal rows | `tools/kama-llamacpp-live.py:1037-1082` | holds |
| `:46-50` wildcard exclusion is lane safety policy; `True`/`False`/`None` distinction | `_listen_inodes` `:354`; `port_owned_by` `:370` | holds |
| `:54-59` procfs-only, one LE host/namespace, no container/inode-reuse/big-endian experiment | my run is also single-host LE; big-endian untested | holds as a limit |
| `:61-63` pre-round predicate `endswith('00000001')`, 24-char slice vs 22-char literal | frozen `tools_kama-llamacpp-live.py:315-316,332-336`, sha256 `0efd1723b02ef748d720a6036d3ac481b1d5fe9755110999d7c9acaf486c46ac` = `SHA256SUMS:8` | holds |

`corpus/knowledge/llamacpp-loading-lifecycle.md:254` ("S048/S050 ground the fixed IPv6 listener-ownership parser") is a fair summary of the above.

# Defects found (non-killing, for the append-only correction queue)

**D1 — `include/uapi/linux/in6.h` bytes are not retained and not pinned, though S048 cites its sha256.** `find .ufo/waves/round-18 -iname '*in6*'` returns nothing; `sources/raw/linux/v7.2/` holds only `net/ipv6/tcp_ipv6.c`, `net/ipv4/tcp_ipv4.c`, `Documentation/networking/proc_net_tcp.rst`; `pin.py`'s `DOCS` lists 10 documents (one, `automake_html`, is the unevaluated/source-unavailable entry), `pins.json` holds 9 raw artifacts, none is in6.h; `runs/source-pins-selftest.stdout` says `SELFTEST PASS checks=7 failed=0` and "9 raw documents re-derived", exit 0. The lesson's blanket sentence at `corpus/lessons/round-18.md:33-34` — "source bytes/pins and opening reports are under `.ufo/waves/round-18/`" — is therefore not true for the second source in the S048 row. The cited sha256 is nonetheless correct: today's live fetch of both torvalds v7.2 and gregkh v7.2.11 gives `4b70a423…`. Fix (advice only): add a `linux_in6` document plus an `in6_addr_words` pin (lines 33–44) to `sources/pin.py`, or narrow the lesson sentence. This is a coverage/retention gap, not a false claim.

**D2 — the Gate row's URL form 404s.** `corpus/lessons/round-18.md:43` cites `https://github.com/torvalds/linux/blob/v7.2/net/ipv6/tcp_ipv6.c:2176`; `curl -s -o /dev/null -w '%{http_code}'` gives **404**, while the same path with `#L2176` gives **200** (`include/uapi/linux/in6.h#L38` also 200). The registry's plain blob URL at `corpus/SOURCES.md:60` resolves. Fix: use `#L2176` or plain URL + text line. Small, but the row's purpose is an openable pin, and the same wave already mined reader-view drift on this file.

**D3 — observation pointer is narrower than the claim.** `corpus/SOURCES.md:60` teaches cell says both full strings were "observed on this host 2026-10-20, `lessons/round-18.md` §Gate", but the Gate row records only the suffixes (`01000000`, `0100007F`) and the frozen-parser counterexample. The full 32-char strings and function results are in `build/advice/ProbeTcp6Format.md` cases B/C. The claim is true and re-derived here; the pointer should name the probe as well.

**Precision notes (not defects):** (i) `lessons/round-18.md:17-18` says "Sources S048/S050 determine the ownership predicate"; they determine the address classification, while wildcard fail-closed is lane policy — the knowledge entry gets this split right at `:46-48`. (ii) `loopback-listener-ownership.md:2` says the kernel source was opened "on kernel 7.2.11-arch1-1"; the pinned source is the v7.2 tag (host is 7.2.11). The substance holds because the v7.2.11 stable function and in6.h are byte-identical (section 5), but naming both versions would be exact.

# Limits

- One host (`7.2.11-arch1-1`, x86_64, little-endian), one network namespace; big-endian output is unobserved and out of S048's stated scope.
- No llama-server and no full tool run; the parser was read, not executed, except my own bind experiment. The v3 receipt behavior is other seats' evidence.
- Arch's patch set relative to upstream stable v7.2.11 was not inspected; the host behavior is direct, the source bridge is to upstream stable.
- The shape table is derivation/`ipaddress` truth only, not bound sockets, for the non-local addresses.
- `ProbeTcp6Format.md` itself was read, not re-executed.

# Teardown / installs

- All five listeners were closed in `finally`; `ss -ltn` after the run: no rows for 59199, 45091, 49235, 51143, 45211 (`no seat listeners remain`), and no 8080/34113 listeners. No process group, service, or file outside `/tmp/kama-r18-falsify-ReopenS048` and this report.
- No installs or upgrades. Scratch `/tmp/kama-r18-falsify-ReopenS048` (clone + four fetched sources + `rederive.py`) removed after writing this report.

# Experiment source (verbatim, `rederive.py`)

```python
import socket, struct, sys, ipaddress, json

def hexes(addr):
    packed = socket.inet_pton(socket.AF_INET6, addr)
    words = struct.unpack('<4I', packed)
    per_word = ''.join('%08X' % w for w in words)
    net_order = packed.hex().upper()
    return per_word, net_order

def row_hex(path, port):
    out=[]
    with open(path, encoding='ascii') as fh:
        next(fh)
        for line in fh:
            p=line.split()
            if len(p)<10: continue
            loc=p[1]; st=p[3]
            if st!='0A': continue
            ph=int(loc.rsplit(':',1)[1],16)
            if ph==port:
                out.append((loc.rsplit(':',1)[0], p[9]))
    return out

cases=[
 ('AF_INET6','::1',None,'/proc/net/tcp6'),
 ('AF_INET6','::ffff:127.0.0.1',0,'/proc/net/tcp6'),
 ('AF_INET6','::ffff:127.1.2.3',0,'/proc/net/tcp6'),
 ('AF_INET6','::',0,'/proc/net/tcp6'),
 ('AF_INET','127.0.0.1',None,'/proc/net/tcp'),
]
res=[]
for fam_s,addr,v6only,proc in cases:
    fam=socket.AF_INET6 if fam_s=='AF_INET6' else socket.AF_INET
    s=socket.socket(fam, socket.SOCK_STREAM)
    try:
        if v6only is not None:
            s.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, v6only)
        s.bind((addr,0))
        s.listen(1)
        host,port=s.getsockname()[:2]
        assert port not in (8080,34113), port
        rows=row_hex(proc,port)
        got=rows[0][0] if rows else None
        if fam==socket.AF_INET6:
            pred,net=hexes(addr)
        else:
            pred=socket.inet_pton(socket.AF_INET,addr)[::-1].hex().upper()
            net=socket.inet_pton(socket.AF_INET,addr).hex().upper()
        res.append(dict(family=fam_s, bind=addr, v6only=v6only, sockname=[host,port],
                        proc=proc, observed=got, predicted_per_word=pred,
                        network_order=net, match_per_word=(got==pred),
                        match_network=(got==net), inode=rows[0][1] if rows else None))
    finally:
        s.close()
print(json.dumps(res, indent=1))

# hostile/shape predictions only (no bind): predicate equivalence checks
mapped_prefix='0000000000000000FFFF0000'
cands=['::1','::2','2001:db8::1','fe80::1','::ffff:127.0.0.1','::ffff:127.0.0.2',
       '::ffff:127.0.0.0','::ffff:127.255.255.255','::ffff:0.0.0.127','::ffff:255.0.0.127',
       '::ffff:8.8.8.8','::ffff:1.0.0.0','::','::7f00:1','::ffff:1.2.3.127']
print('SHAPES')
for a in cands:
    h,_=hexes(a)
    exact = h=='00000000000000000000000001000000'
    mapped = h.startswith(mapped_prefix) and h.endswith('7F')
    ip=ipaddress.IPv6Address(a)
    truth = ip==ipaddress.IPv6Address('::1') or (ip.ipv4_mapped is not None and ip.ipv4_mapped.is_loopback)
    print(a, h, 'exact::1' if exact else '', 'mapped127' if mapped else '', 'truth', truth)
```

Report: .ufo/waves/round-18/falsify/advice/ReopenS048.md
