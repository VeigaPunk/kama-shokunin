VERDICT: confirm — on this host (kernel 7.2.11, x86_64 little-endian) /proc/net/tcp6 prints addresses as four host-order 32-bit words, so the FROZEN `_listen_inodes` misses `::1` and `::ffff:127/104` (`port_owned_by` returns None); IPv4 127/8 works (True).

Seat KamaR18.ProbeTcp6Format-2, experiment seat (advice only, not a verdict), 2026-10-20. Lane tip `git -C … rev-parse master` = `e75cf680b53484a61709ee1b2787d8dbc6419f74` (unchanged). FROZEN tool `.ufo/waves/round-18/frozen/tools_kama-llamacpp-live.py` sha256 `0efd1723b02ef748d720a6036d3ac481b1d5fe9755110999d7c9acaf486c46ac` (= SHA256SUMS row 8). I hashed it before and after both runs, and again at the end: unchanged. No lane file was written except this report. Scratch was only under `/tmp/kama-r18-ProbeTcp6Format/`, and I deleted it at the end. No installs.

Axes walked: correctness (what the kernel prints vs. what the predicate tests), evidence (real sockets, the frozen functions themselves, kernel source pinned by sha256), harm (only loopback listeners on ephemeral-range ports 40000-60999, never 8080/34113; everything torn down).

## Result: what the FROZEN functions return (run 1; run 2 gave the same verdict for every case on fresh ports)

| case | listener (python child, own pid) | raw state-0A row: table, `local_address` | `_listen_inodes(port)` | `port_owned_by(listener_pid)` | `port_owned_by(stranger_pid)` | `verify_live(proc,port,'probe')` | frozen `http_get(port,'/health')` (dials 127.0.0.1) | C1 contract | frozen vs contract |
|---|---|---|---|---|---|---|---|---|---|
| A | AF_INET `127.0.0.1` | tcp `0100007F:CB1E` | `['201382834']` | **True** | False | `(None, 'child')` | 200 | owned | ok |
| B | AF_INET6 `::1` (V6ONLY default, reads back 1) | tcp6 `00000000000000000000000001000000:ECFF` | `[]` | **None** | None | `('probe:port-listener-ownership-unproven', 'unproven')` | ConnectionRefusedError | owned | **FALSE-REJECT** |
| C | AF_INET6 `::ffff:127.0.0.1`, V6ONLY=0 | tcp6 `0000000000000000FFFF00000100007F:AAFD` | `[]` | **None** | None | `('probe:port-listener-ownership-unproven', 'unproven')` | **200** | owned | **FALSE-REJECT** |
| D | AF_INET6 `::` dual-stack, V6ONLY=0 | tcp6 `00000000000000000000000000000000:DCA3` | `[]` | None | None | `('probe:port-listener-ownership-unproven', 'unproven')` | 200 | not owned (wildcard stays fail-closed) | ok (by design) |
| E (extra) | AF_INET `127.1.2.3` | tcp `0302017F:C1A8` | `['201382867']` | True | False | `(None, 'child')` | refused (nothing listens on .0.1) | owned | ok |
| F (extra) | AF_INET6 `::ffff:127.1.2.3`, V6ONLY=0 | tcp6 `0000000000000000FFFF00000302017F:B688` | `[]` | None | None | `('probe:port-listener-ownership-unproven', 'unproven')` | refused | owned | **FALSE-REJECT** |

No AF_INET6 listener appeared in /proc/net/tcp, and no AF_INET listener appeared in /proc/net/tcp6, in either run. Every listener's own fd table holds `socket:[<inode>]`, and that inode equals column 10 of its row. In cases B, C and F, `None` therefore means "the frozen function did not recognise the row", not "no listener".

## Findings

1. **The byte order is now proven on this host.** For each non-zero bound address, the probe encoded the address two ways and compared each with the observed hex:
   - Per-32-bit-word host order matched every time (`equals-observed=True`).
   - Network order never matched (`equals-observed=False`).
   - Examples: `::1` is observed as `…01000000` (network order would be `…00000001`). `::ffff:127.0.0.1` is observed as `0000000000000000FFFF00000100007F` (network order `00000000000000000000FFFF7F000001`). `127.0.0.1` is observed as `0100007F`.
   - The `::` case cannot tell the two orders apart (all zeros).
   - `ss` decodes the same sockets independently over netlink: `[::1]:60671`, `[::ffff:127.0.0.1]:43773`, `*:56483`.
   - This turns the mapped form, which ScoutProcNetTcpDoc.md L66-67 left as "[INFERENCE]", into an observation (cases C and F).
2. **Kernel source agrees.** I downloaded the raw v7.2 files and hashed them: tcp_ipv6.c `dd3f400b6d29c940d298e0b0a600a82b32368219aee5bc8f17981b00bd7b0558`, tcp_ipv4.c `bdf50d980735746844c3b5ffea3d62794378572c62f69fda8ec821afb448c4d8`, af_inet6.c `e3092591ae3e0a1e7db5675b630e4a155eab4a90fffcbe27223b616d71eea938`. The first two digests match ScribeSourcesKernel.md L10 and ScoutProcNetTcpDoc.md L100/L103.
   - https://raw.githubusercontent.com/torvalds/linux/v7.2/net/ipv6/tcp_ipv6.c:2173 `"%4d: %08X%08X%08X%08X:%04X %08X%08X%08X%08X:%04X "`
   - Same file, lines 2176-2177: `src->s6_addr32[0], src->s6_addr32[1],` / `src->s6_addr32[2], src->s6_addr32[3], srcp,`
   - https://raw.githubusercontent.com/torvalds/linux/v7.2/net/ipv4/tcp_ipv4.c:2779 `__be32 src = inet->inet_rcv_saddr;`
   - Same file, line 2813: `seq_printf(f, "%4d: %08X:%04X %08X:%04X %02X …`
   - Each `__be32` word is printed with `%08X`, so on a little-endian CPU every 4-byte group comes out byte-reversed. The host reports `sys.byteorder == 'little'` and machine `x86_64`.
3. **Frozen defect 1: `::1` is never matched.** frozen:332 `if not (addr_hex.endswith('00000001')` and the docstring at frozen:315 `::1 ends 00000001` are both wrong here. The observed `::1` text ends `01000000`. Sub-term printed: `"addr_hex.endswith('00000001')": false` (case B).
4. **Frozen defect 2: the mapped arm is dead code.** frozen:333-334 `addr_hex[:24]` / `== '0000000000000000FFFF00'` compares strings of different lengths. The probe printed `"len(addr_hex[:24])": 24` and `"len('0000000000000000FFFF00')": 22`, so the comparison is always false. Cases C and F are rejected even though their `endswith('7F')` term is `true`. Even at the right length, the prefix would be wrong: the observed 24-character prefix is `0000000000000000FFFF0000`.
5. **The IPv4 arm is correct on this host.** frozen:337 `elif not addr_hex.endswith('7F'):` accepted `127.0.0.1` and `127.1.2.3` (cases A and E). In the synthetic rows it rejects `1.2.3.127` (`7F030201`), `10.0.0.127` and `0.0.0.0`.
6. **Consequence: a false failure for the contract's must-ACCEPT server, observed through the frozen functions.**
   - The frozen `http_get` reaches the v4-mapped listener in case C: status 200, and the listener logged peer `::ffff:127.0.0.1`.
   - The frozen `verify_live` still returns `('probe:port-listener-ownership-unproven', 'unproven')`.
   - The first-contact gate runs the same code: frozen:548 `owned = port_owned_by(proc.pid, port)`, then frozen:551-552 return `'port-listener-not-our-child' if owned is False else 'port-listener-ownership-unproven'`.
   - [INFERENCE: a full tool run against such a server would end as that setup error. I did not run it, because the tool launches llama-server itself with frozen:1091 `'--host', '127.0.0.1',`.]
7. **Case B never reaches the ownership check inside the frozen tool.** A `::1` listener does not answer the tool's IPv4 dials (frozen:397 `url = f'http://127.0.0.1:{port}{path}'`; the `http_get` result was ConnectionRefusedError). The kernel makes a specific-address IPv6 bind v6-only regardless of `net.ipv6.bindv6only=0`, which explains the read-back `V6ONLY=1`: af_inet6.c:386-387 `if (addr_type != IPV6_ADDR_ANY && addr_type != IPV6_ADDR_MAPPED)` / `sk->sk_ipv6only = 1;`. The `::1` defect is still a predicate-contract violation, but in the tool it only shows up if a future server binds `::1` and is dialled over v6.
8. **Case D (`::`) is fail-closed by design.** frozen:317-318 reads "A child bound to 0.0.0.0 or :: still answers loopback connects but is not counted as the loopback-port owner — fail-closed." Observed: `http_get` returns 200 and ownership is None.
9. **The frozen predicate also false-accepts (synthetic rows).** I ran the frozen `_listen_inodes` with `open` patched in its own module namespace. It accepts:
   - `::ffff:1.0.0.0` (`0000000000000000FFFF000000000001`)
   - `2001:db8::100:0` (`B80D0120000000000000000000000001`)

   The `endswith('00000001')` test matches any address whose last 32 bits are 1.0.0.0, so it is a suffix test, not a loopback test. [INFERENCE: these cannot occur on this host unless it owns such an address.]
10. **Candidate fixes compared over 20 rows** (6 real-shaped, 14 synthetic). Ground truth comes from `ipaddress` network membership: `127.0.0.0/8`, `::1` and `::ffff:127.0.0.0/104`. Full table under Raw outputs.

    | predicate | errors | which rows |
    |---|---|---|
    | FROZEN | 6 | rejects `::1` and all three `::ffff:127.*`; accepts `::ffff:1.0.0.0` and `2001:db8::100:0` |
    | one-token edit (`'00000001'` → `'01000000'`) | 6 | rejects all three `::ffff:127.*` (mapped arm still dead); accepts `::ffff:0.0.0.1`, `2001:db8::1`, `fe80::1` |
    | RevOwnershipCode.md drop-in (L42-47: exact `::1` equality, then the `0000000000000000FFFF0000` prefix plus a `7F` tail) | 0 | none |
    | decode to bytes, then `ipaddress` with `ipv4_mapped.is_loopback` | 0 | none |

    Python docs, https://docs.python.org/3.14/library/ipaddress.html#ipaddress.IPv6Address.ipv4_mapped: "For addresses that appear to be IPv4 mapped addresses in the range ::FFFF:0:0/96 as defined by RFC 4291, this property reports the embedded IPv4 address." On 3.14.8, plain `IPv6Address.is_loopback` also returned True for `::ffff:127.*`. However, the 3.14 docs entry for `IPv6Address.is_loopback` says nothing about mapped addresses, so a fix should test `ipv4_mapped` explicitly rather than rely on that behaviour.

## Advice for the C1 controls (not implemented here; C1 owns the files)
- **Good-server fixture.** An AF_INET6 listener on `::ffff:127.0.0.1` with `IPV6_V6ONLY=0` answers the tool's 127.0.0.1 dials (case C: HTTP 200). That makes it a deterministic fixture for the required must-ACCEPT control. Against the frozen tool it reproduces `port-listener-ownership-unproven`.
- **Socket-free rows that kill weak fixes** (they test `_listen_inodes` with `open` patched in its namespace):
  - `::ffff:1.0.0.0` and `2001:db8::100:0` kill the frozen suffix test.
  - `::ffff:0.0.0.1`, `2001:db8::1` and `fe80::1` kill the one-token edit.
  - `::ffff:0.0.0.0`, `::7f00:1`, `::ffff:1.2.3.127` and `10.0.0.127` kill a prefix-only or tail-only fix.
  - The `local_address` hex for each of these is in the predicate-comparison output below.

## Mined mistake (candidate for L1)
The URL reader's numbered text view of the kernel files drifted from the raw file lines: +1 for the tcp_ipv6.c format line (2174 vs raw 2173), +4 for tcp_ipv4.c `__be32 src` (2783 vs 2779), and +6 for af_inet6.c (220 vs 214). Every line number in this report comes from the downloaded raw files listed above, with their sha256. Rule: cite kernel `path:line` only from a downloaded, sha256-pinned raw copy, never from a reader view.

## Limitations
- One host, little-endian only. [INFERENCE: on a big-endian host both the frozen IPv4 arm and the per-word fix would be wrong, since `%08X` of a `__be32` then prints in network order.] Not tested.
- The kernel citations are tag v7.2; the running kernel is 7.2.11-arch1-1. I did not fetch the stable-branch file. The observed rows match the v7.2 format exactly.
- No full tool or llama-server run, so the setup-error outcome in Finding 6 is [INFERENCE] from the frozen call sites plus the observed `verify_live` result.
- The synthetic rows in Findings 9-10 go through the real frozen function, but not through real sockets. Only the six address shapes in cases A-F were bound for real.
- Stray bytecode in the frozen directory. `.ufo/waves/round-18/frozen/__pycache__/` holds `tools_kama-llamacpp-live.cpython-314.pyc` (mtime 16:56:59.86 -0300) and `tests_llamacpp-live_check-receipt.cpython-314.pyc` (18:02:05.28 -0300). Both predate this seat's first run (18:04:49) and were unchanged after every run. Another importer wrote them; they are not listed in SHA256SUMS.
  - Run 1 may have loaded the cached `.pyc`, which is checked only by source mtime and size.
  - Run 2 used `-X pycache_prefix=` to rule this out. https://docs.python.org/3.14/library/sys.html#sys.pycache_prefix: "Any `__pycache__` directories in the source code tree will be ignored". With `-B` set, no prefix tree was created.
  - Run 2 gave identical verdicts. L1 may want that `__pycache__` removed or ignored; I did not touch it.
- In the transcriptions below, I trimmed the trailing kernel padding spaces from the pasted /proc/net/tcp (IPv4) rows. Everything else is verbatim.

## Installs
None.

## Raw outputs

Transcription integrity: before deleting scratch, an eval cell compared these blocks with the captured files.
- The run-1 block below equals `probe.stdout` line for line, after trimming trailing whitespace: `True`.
- The run-2 block equals the human-readable part of `probe2.stdout`, with the documented synthetic-row abbreviation applied: `True`.
- The two runs' SUPPLEMENTARY sections are byte-identical: `True`.
- With ports, inodes and pids dropped, every case's verdict fields and raw hex match across the runs' JSON summaries: `[True]*6`. The synthetic verdicts also match: `True`.

### Run 1
Command (run as a subprocess from an eval cell; stdout, stderr and exit code captured separately):
```
$ python3 -B /tmp/kama-r18-ProbeTcp6Format/probe.py
exit 0
stderr: (empty; sha256 e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855)
stdout: 22890 bytes, sha256 2d9debae164db5d883d265500fe83cde313832e6000ba64232378984f976ef5e, finished 18:04:57.95 -0300
```
stdout:
```
kernel 7.2.11-arch1-1; python 3.14.8; byteorder little; machine x86_64
ip_local_port_range ['32768', '60999']
net.ipv6.bindv6only 0
frozen sha256 before 0efd1723b02ef748d720a6036d3ac481b1d5fe9755110999d7c9acaf486c46ac matches-SHA256SUMS=True
/proc/net/tcp header:   sl  local_address rem_address   st tx_queue rx_queue tr tm->when retrnsmt   uid  timeout inode
/proc/net/tcp6 header:   sl  local_address                         remote_address                        st tx_queue rx_queue tr tm->when retrnsmt   uid  timeout inode
frozen module loaded from /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/frozen/tools_kama-llamacpp-live.py; SCHEMA='kama-llamacpp-live/v2'
=== CASE A (assigned): AF_INET bind ('127.0.0.1', 51998); port hex CB1E ===
  listener pid=3105362 fd=3 inode=201382834 sockname=['127.0.0.1', 51998]
  pre-bind 0A rows on port: {'/proc/net/tcp': [], '/proc/net/tcp6': []}
  raw /proc/net/tcp 0A rows for port 51998:
       4: 0100007F:CB1E 00000000:0000 0A 00000000:00000000 00:00000000 00000000  1000        0 201382834 1 000000007c957634 100 0 0 10 0
      local-address hex 0100007F (len 8), inode column 201382834
      decode as per_32bit_word_host_order  = 127.0.0.1
      decode as network_byte_order         = 1.0.0.127
      bound '127.0.0.1' encoded per_32bit_word_host_order  = 0100007F  equals-observed=True
      bound '127.0.0.1' encoded network_byte_order         = 7F000001  equals-observed=False
      frozen sub-terms: {"addr_hex.endswith('7F')": true}
  raw /proc/net/tcp6 0A rows for port 51998:
    (none)
  $ ss -Hltnp 'sport = :51998'  (exit 0)
    LISTEN 0      8      127.0.0.1:51998 0.0.0.0:* users:(("python3",pid=3105362,fd=3))
  listener socket fds (readlink /proc/3105362/fd/*): {3: 'socket:[201382834]'}
  FROZEN _listen_inodes(port)                  -> ['201382834']
  FROZEN port_owned_by(listener pid 3105362, port) -> True
  FROZEN port_owned_by(stranger pid 3105361, port) -> False
  FROZEN verify_live(listener proc, port, 'probe') -> (None, 'child')
  FROZEN http_get(port, '/health')             -> {'status': 200, 'error': None, 'body': '{"status":"ok"}'}
  raw connect 127.0.0.1                        -> 'connected'
  raw connect ::1                              -> 'ConnectionRefusedError(errno=111)'
  listener exit rc=0; listener stderr: ['accepted peer 127.0.0.1 port 51606', 'accepted peer 127.0.0.1 port 51610']
  post-teardown 0A rows on port: {'/proc/net/tcp': [], '/proc/net/tcp6': []}
=== CASE B (assigned): AF_INET6 bind ('::1', 60671) IPV6_V6ONLY=default(getsockopt=1); port hex ECFF ===
  listener pid=3105364 fd=3 inode=201413180 sockname=['::1', 60671]
  pre-bind 0A rows on port: {'/proc/net/tcp': [], '/proc/net/tcp6': []}
  raw /proc/net/tcp 0A rows for port 60671:
    (none)
  raw /proc/net/tcp6 0A rows for port 60671:
       0: 00000000000000000000000001000000:ECFF 00000000000000000000000000000000:0000 0A 00000000:00000000 00:00000000 00000000  1000        0 201413180 1 000000007f3b858e 100 0 0 10 0
      local-address hex 00000000000000000000000001000000 (len 32), inode column 201413180
      decode as per_32bit_word_host_order  = ::1
      decode as network_byte_order         = ::1.0.0.0
      bound '::1' encoded per_32bit_word_host_order  = 00000000000000000000000001000000  equals-observed=True
      bound '::1' encoded network_byte_order         = 00000000000000000000000000000001  equals-observed=False
      frozen sub-terms: {"addr_hex.endswith('00000001')": false, "len(addr_hex[:24])": 24, "len('0000000000000000FFFF00')": 22, "addr_hex[:24] == '0000000000000000FFFF00'": false, "addr_hex.endswith('7F')": false}
  $ ss -Hltnp 'sport = :60671'  (exit 0)
    LISTEN 0      8      [::1]:60671 [::]:* users:(("python3",pid=3105364,fd=3))
  listener socket fds (readlink /proc/3105364/fd/*): {3: 'socket:[201413180]'}
  FROZEN _listen_inodes(port)                  -> []
  FROZEN port_owned_by(listener pid 3105364, port) -> None
  FROZEN port_owned_by(stranger pid 3105361, port) -> None
  FROZEN verify_live(listener proc, port, 'probe') -> ('probe:port-listener-ownership-unproven', 'unproven')
  FROZEN http_get(port, '/health')             -> {'status': None, 'error': 'ConnectionRefusedError', 'body': ''}
  raw connect 127.0.0.1                        -> 'ConnectionRefusedError(errno=111)'
  raw connect ::1                              -> 'connected'
  listener exit rc=0; listener stderr: ['accepted peer ::1 port 44082']
  post-teardown 0A rows on port: {'/proc/net/tcp': [], '/proc/net/tcp6': []}
=== CASE C (assigned): AF_INET6 bind ('::ffff:127.0.0.1', 43773) IPV6_V6ONLY=0(getsockopt=0); port hex AAFD ===
  listener pid=3105366 fd=3 inode=201424137 sockname=['::ffff:127.0.0.1', 43773]
  pre-bind 0A rows on port: {'/proc/net/tcp': [], '/proc/net/tcp6': []}
  raw /proc/net/tcp 0A rows for port 43773:
    (none)
  raw /proc/net/tcp6 0A rows for port 43773:
       1: 0000000000000000FFFF00000100007F:AAFD 00000000000000000000000000000000:0000 0A 00000000:00000000 00:00000000 00000000  1000        0 201424137 1 00000000467e6656 100 0 0 10 0
      local-address hex 0000000000000000FFFF00000100007F (len 32), inode column 201424137
      decode as per_32bit_word_host_order  = ::ffff:127.0.0.1
      decode as network_byte_order         = ::ffff:0:100:7f
      bound '::ffff:127.0.0.1' encoded per_32bit_word_host_order  = 0000000000000000FFFF00000100007F  equals-observed=True
      bound '::ffff:127.0.0.1' encoded network_byte_order         = 00000000000000000000FFFF7F000001  equals-observed=False
      frozen sub-terms: {"addr_hex.endswith('00000001')": false, "len(addr_hex[:24])": 24, "len('0000000000000000FFFF00')": 22, "addr_hex[:24] == '0000000000000000FFFF00'": false, "addr_hex.endswith('7F')": true}
  $ ss -Hltnp 'sport = :43773'  (exit 0)
    LISTEN 0      8      [::ffff:127.0.0.1]:43773 *:* users:(("python3",pid=3105366,fd=3))
  listener socket fds (readlink /proc/3105366/fd/*): {3: 'socket:[201424137]'}
  FROZEN _listen_inodes(port)                  -> []
  FROZEN port_owned_by(listener pid 3105366, port) -> None
  FROZEN port_owned_by(stranger pid 3105361, port) -> None
  FROZEN verify_live(listener proc, port, 'probe') -> ('probe:port-listener-ownership-unproven', 'unproven')
  FROZEN http_get(port, '/health')             -> {'status': 200, 'error': None, 'body': '{"status":"ok"}'}
  raw connect 127.0.0.1                        -> 'connected'
  raw connect ::1                              -> 'ConnectionRefusedError(errno=111)'
  listener exit rc=0; listener stderr: ['accepted peer ::ffff:127.0.0.1 port 40970', 'accepted peer ::ffff:127.0.0.1 port 40984']
  post-teardown 0A rows on port: {'/proc/net/tcp': [], '/proc/net/tcp6': []}
=== CASE D (assigned): AF_INET6 bind ('::', 56483) IPV6_V6ONLY=0(getsockopt=0); port hex DCA3 ===
  listener pid=3105368 fd=3 inode=201409022 sockname=['::', 56483]
  pre-bind 0A rows on port: {'/proc/net/tcp': [], '/proc/net/tcp6': []}
  raw /proc/net/tcp 0A rows for port 56483:
    (none)
  raw /proc/net/tcp6 0A rows for port 56483:
       2: 00000000000000000000000000000000:DCA3 00000000000000000000000000000000:0000 0A 00000000:00000000 00:00000000 00000000  1000        0 201409022 1 0000000018da1200 100 0 0 10 0
      local-address hex 00000000000000000000000000000000 (len 32), inode column 201409022
      decode as per_32bit_word_host_order  = ::
      decode as network_byte_order         = ::
      bound '::' encoded per_32bit_word_host_order  = 00000000000000000000000000000000  equals-observed=True
      bound '::' encoded network_byte_order         = 00000000000000000000000000000000  equals-observed=True
      frozen sub-terms: {"addr_hex.endswith('00000001')": false, "len(addr_hex[:24])": 24, "len('0000000000000000FFFF00')": 22, "addr_hex[:24] == '0000000000000000FFFF00'": false, "addr_hex.endswith('7F')": false}
  $ ss -Hltnp 'sport = :56483'  (exit 0)
    LISTEN 0      8      *:56483 *:* users:(("python3",pid=3105368,fd=3))
  listener socket fds (readlink /proc/3105368/fd/*): {3: 'socket:[201409022]'}
  FROZEN _listen_inodes(port)                  -> []
  FROZEN port_owned_by(listener pid 3105368, port) -> None
  FROZEN port_owned_by(stranger pid 3105361, port) -> None
  FROZEN verify_live(listener proc, port, 'probe') -> ('probe:port-listener-ownership-unproven', 'unproven')
  FROZEN http_get(port, '/health')             -> {'status': 200, 'error': None, 'body': '{"status":"ok"}'}
  raw connect 127.0.0.1                        -> 'connected'
  raw connect ::1                              -> 'connected'
  listener exit rc=0; listener stderr: ['accepted peer ::ffff:127.0.0.1 port 55926', 'accepted peer ::ffff:127.0.0.1 port 55942', 'accepted peer ::1 port 60204']
  post-teardown 0A rows on port: {'/proc/net/tcp': [], '/proc/net/tcp6': []}
=== CASE E (extra): AF_INET bind ('127.1.2.3', 49576); port hex C1A8 ===
  listener pid=3105370 fd=3 inode=201382867 sockname=['127.1.2.3', 49576]
  pre-bind 0A rows on port: {'/proc/net/tcp': [], '/proc/net/tcp6': []}
  raw /proc/net/tcp 0A rows for port 49576:
       4: 0302017F:C1A8 00000000:0000 0A 00000000:00000000 00:00000000 00000000  1000        0 201382867 1 000000000e9a132f 100 0 0 10 0
      local-address hex 0302017F (len 8), inode column 201382867
      decode as per_32bit_word_host_order  = 127.1.2.3
      decode as network_byte_order         = 3.2.1.127
      bound '127.1.2.3' encoded per_32bit_word_host_order  = 0302017F  equals-observed=True
      bound '127.1.2.3' encoded network_byte_order         = 7F010203  equals-observed=False
      frozen sub-terms: {"addr_hex.endswith('7F')": true}
  raw /proc/net/tcp6 0A rows for port 49576:
    (none)
  $ ss -Hltnp 'sport = :49576'  (exit 0)
    LISTEN 0      8      127.1.2.3:49576 0.0.0.0:* users:(("python3",pid=3105370,fd=3))
  listener socket fds (readlink /proc/3105370/fd/*): {3: 'socket:[201382867]'}
  FROZEN _listen_inodes(port)                  -> ['201382867']
  FROZEN port_owned_by(listener pid 3105370, port) -> True
  FROZEN port_owned_by(stranger pid 3105361, port) -> False
  FROZEN verify_live(listener proc, port, 'probe') -> (None, 'child')
  FROZEN http_get(port, '/health')             -> {'status': None, 'error': 'ConnectionRefusedError', 'body': ''}
  raw connect 127.0.0.1                        -> 'ConnectionRefusedError(errno=111)'
  raw connect ::1                              -> 'ConnectionRefusedError(errno=111)'
  listener exit rc=0; listener stderr: []
  post-teardown 0A rows on port: {'/proc/net/tcp': [], '/proc/net/tcp6': []}
=== CASE F (extra): AF_INET6 bind ('::ffff:127.1.2.3', 46728) IPV6_V6ONLY=0(getsockopt=0); port hex B688 ===
  listener pid=3105372 fd=3 inode=201422911 sockname=['::ffff:127.1.2.3', 46728]
  pre-bind 0A rows on port: {'/proc/net/tcp': [], '/proc/net/tcp6': []}
  raw /proc/net/tcp 0A rows for port 46728:
    (none)
  raw /proc/net/tcp6 0A rows for port 46728:
       0: 0000000000000000FFFF00000302017F:B688 00000000000000000000000000000000:0000 0A 00000000:00000000 00:00000000 00000000  1000        0 201422911 1 000000001c2a6987 100 0 0 10 0
      local-address hex 0000000000000000FFFF00000302017F (len 32), inode column 201422911
      decode as per_32bit_word_host_order  = ::ffff:127.1.2.3
      decode as network_byte_order         = ::ffff:0:302:17f
      bound '::ffff:127.1.2.3' encoded per_32bit_word_host_order  = 0000000000000000FFFF00000302017F  equals-observed=True
      bound '::ffff:127.1.2.3' encoded network_byte_order         = 00000000000000000000FFFF7F010203  equals-observed=False
      frozen sub-terms: {"addr_hex.endswith('00000001')": false, "len(addr_hex[:24])": 24, "len('0000000000000000FFFF00')": 22, "addr_hex[:24] == '0000000000000000FFFF00'": false, "addr_hex.endswith('7F')": true}
  $ ss -Hltnp 'sport = :46728'  (exit 0)
    LISTEN 0      8      [::ffff:127.1.2.3]:46728 *:* users:(("python3",pid=3105372,fd=3))
  listener socket fds (readlink /proc/3105372/fd/*): {3: 'socket:[201422911]'}
  FROZEN _listen_inodes(port)                  -> []
  FROZEN port_owned_by(listener pid 3105372, port) -> None
  FROZEN port_owned_by(stranger pid 3105361, port) -> None
  FROZEN verify_live(listener proc, port, 'probe') -> ('probe:port-listener-ownership-unproven', 'unproven')
  FROZEN http_get(port, '/health')             -> {'status': None, 'error': 'ConnectionRefusedError', 'body': ''}
  raw connect 127.0.0.1                        -> 'ConnectionRefusedError(errno=111)'
  raw connect ::1                              -> 'ConnectionRefusedError(errno=111)'
  listener exit rc=0; listener stderr: []
  post-teardown 0A rows on port: {'/proc/net/tcp': [], '/proc/net/tcp6': []}
=== SUPPLEMENTARY (synthetic table; frozen _listen_inodes with open() patched in its module namespace) ===
  /proc/net/tcp     0: 0100007F:BEEF 00000000:0000 0A 00000000:00000000 00:00000000 00000000  1000        0 9001 1 0000000000000000 100 0 0 10 0
  /proc/net/tcp     1: FEFFFF7F:BEEF 00000000:0000 0A 00000000:00000000 00:00000000 00000000  1000        0 9002 1 0000000000000000 100 0 0 10 0
  /proc/net/tcp     2: 7F030201:BEEF 00000000:0000 0A 00000000:00000000 00:00000000 00000000  1000        0 9003 1 0000000000000000 100 0 0 10 0
  /proc/net/tcp     3: 00000000:BEEF 00000000:0000 0A 00000000:00000000 00:00000000 00000000  1000        0 9004 1 0000000000000000 100 0 0 10 0
  /proc/net/tcp6    0: 00000000000000000000000001000000:BEEF 00000000000000000000000000000000:0000 0A 00000000:00000000 00:00000000 00000000  1000        0 9101 1 0000000000000000 100 0 0 10 0
  /proc/net/tcp6    1: 0000000000000000FFFF00000100007F:BEEF 00000000000000000000000000000000:0000 0A 00000000:00000000 00:00000000 00000000  1000        0 9102 1 0000000000000000 100 0 0 10 0
  /proc/net/tcp6    2: 0000000000000000FFFF0000FEFFFF7F:BEEF 00000000000000000000000000000000:0000 0A 00000000:00000000 00:00000000 00000000  1000        0 9103 1 0000000000000000 100 0 0 10 0
  /proc/net/tcp6    3: 00000000000000000000000000000000:BEEF 00000000000000000000000000000000:0000 0A 00000000:00000000 00:00000000 00000000  1000        0 9104 1 0000000000000000 100 0 0 10 0
  /proc/net/tcp6    4: 0000000000000000FFFF000000000001:BEEF 00000000000000000000000000000000:0000 0A 00000000:00000000 00:00000000 00000000  1000        0 9105 1 0000000000000000 100 0 0 10 0
  /proc/net/tcp6    5: B80D0120000000000000000000000001:BEEF 00000000000000000000000000000000:0000 0A 00000000:00000000 00:00000000 00000000  1000        0 9106 1 0000000000000000 100 0 0 10 0
  /proc/net/tcp6    6: 0000000000000000FFFF00007F00000A:BEEF 00000000000000000000000000000000:0000 0A 00000000:00000000 00:00000000 00000000  1000        0 9107 1 0000000000000000 100 0 0 10 0
  FROZEN _listen_inodes(48879) -> ['9001', '9002', '9105', '9106']
  127.0.0.1                inode 9001 contract-loopback=True  frozen-accepts=True  ok
  127.255.255.254          inode 9002 contract-loopback=True  frozen-accepts=True  ok
  1.2.3.127                inode 9003 contract-loopback=False frozen-accepts=False ok
  0.0.0.0                  inode 9004 contract-loopback=False frozen-accepts=False ok
  ::1                      inode 9101 contract-loopback=True  frozen-accepts=False FALSE-REJECT
  ::ffff:127.0.0.1         inode 9102 contract-loopback=True  frozen-accepts=False FALSE-REJECT
  ::ffff:127.255.255.254   inode 9103 contract-loopback=True  frozen-accepts=False FALSE-REJECT
  ::                       inode 9104 contract-loopback=False frozen-accepts=False ok
  ::ffff:1.0.0.0           inode 9105 contract-loopback=False frozen-accepts=True  FALSE-ACCEPT
  2001:db8::100:0          inode 9106 contract-loopback=False frozen-accepts=True  FALSE-ACCEPT
  ::ffff:10.0.0.127        inode 9107 contract-loopback=False frozen-accepts=False ok
frozen sha256 after 0efd1723b02ef748d720a6036d3ac481b1d5fe9755110999d7c9acaf486c46ac unchanged=True; frozen/__pycache__ exists=True
=== SUMMARY (JSON) ===
{
 "cases": [
  {
   "bind": "127.0.0.1",
   "case": "A",
   "connect_127": "connected",
   "connect_v6_loopback": "ConnectionRefusedError(errno=111)",
   "expected": true,
   "family": "AF_INET",
   "frozen_http_get_error": null,
   "frozen_http_get_status": 200,
   "frozen_listen_inodes": [
    "201382834"
   ],
   "frozen_port_owned_by_child": true,
   "frozen_port_owned_by_stranger": false,
   "frozen_verify_live": [
    null,
    "child"
   ],
   "listener_inode": "201382834",
   "listener_rc": 0,
   "mismatch_vs_contract": false,
   "port": 51998,
   "post_teardown_rows": {
    "/proc/net/tcp": [],
    "/proc/net/tcp6": []
   },
   "rows": {
    "/proc/net/tcp": [
     {
      "addr_hex": "0100007F",
      "inode": "201382834",
      "network_order_match": false,
      "per_word_host_order_match": true
     }
    ]
   },
   "scope": "assigned",
   "v6only": null
  },
  {
   "bind": "::1",
   "case": "B",
   "connect_127": "ConnectionRefusedError(errno=111)",
   "connect_v6_loopback": "connected",
   "expected": true,
   "family": "AF_INET6",
   "frozen_http_get_error": "ConnectionRefusedError",
   "frozen_http_get_status": null,
   "frozen_listen_inodes": [],
   "frozen_port_owned_by_child": null,
   "frozen_port_owned_by_stranger": null,
   "frozen_verify_live": [
    "probe:port-listener-ownership-unproven",
    "unproven"
   ],
   "listener_inode": "201413180",
   "listener_rc": 0,
   "mismatch_vs_contract": true,
   "port": 60671,
   "post_teardown_rows": {
    "/proc/net/tcp": [],
    "/proc/net/tcp6": []
   },
   "rows": {
    "/proc/net/tcp6": [
     {
      "addr_hex": "00000000000000000000000001000000",
      "inode": "201413180",
      "network_order_match": false,
      "per_word_host_order_match": true
     }
    ]
   },
   "scope": "assigned",
   "v6only": 1
  },
  {
   "bind": "::ffff:127.0.0.1",
   "case": "C",
   "connect_127": "connected",
   "connect_v6_loopback": "ConnectionRefusedError(errno=111)",
   "expected": true,
   "family": "AF_INET6",
   "frozen_http_get_error": null,
   "frozen_http_get_status": 200,
   "frozen_listen_inodes": [],
   "frozen_port_owned_by_child": null,
   "frozen_port_owned_by_stranger": null,
   "frozen_verify_live": [
    "probe:port-listener-ownership-unproven",
    "unproven"
   ],
   "listener_inode": "201424137",
   "listener_rc": 0,
   "mismatch_vs_contract": true,
   "port": 43773,
   "post_teardown_rows": {
    "/proc/net/tcp": [],
    "/proc/net/tcp6": []
   },
   "rows": {
    "/proc/net/tcp6": [
     {
      "addr_hex": "0000000000000000FFFF00000100007F",
      "inode": "201424137",
      "network_order_match": false,
      "per_word_host_order_match": true
     }
    ]
   },
   "scope": "assigned",
   "v6only": 0
  },
  {
   "bind": "::",
   "case": "D",
   "connect_127": "connected",
   "connect_v6_loopback": "connected",
   "expected": null,
   "family": "AF_INET6",
   "frozen_http_get_error": null,
   "frozen_http_get_status": 200,
   "frozen_listen_inodes": [],
   "frozen_port_owned_by_child": null,
   "frozen_port_owned_by_stranger": null,
   "frozen_verify_live": [
    "probe:port-listener-ownership-unproven",
    "unproven"
   ],
   "listener_inode": "201409022",
   "listener_rc": 0,
   "mismatch_vs_contract": false,
   "port": 56483,
   "post_teardown_rows": {
    "/proc/net/tcp": [],
    "/proc/net/tcp6": []
   },
   "rows": {
    "/proc/net/tcp6": [
     {
      "addr_hex": "00000000000000000000000000000000",
      "inode": "201409022",
      "network_order_match": true,
      "per_word_host_order_match": true
     }
    ]
   },
   "scope": "assigned",
   "v6only": 0
  },
  {
   "bind": "127.1.2.3",
   "case": "E",
   "connect_127": "ConnectionRefusedError(errno=111)",
   "connect_v6_loopback": "ConnectionRefusedError(errno=111)",
   "expected": true,
   "family": "AF_INET",
   "frozen_http_get_error": "ConnectionRefusedError",
   "frozen_http_get_status": null,
   "frozen_listen_inodes": [
    "201382867"
   ],
   "frozen_port_owned_by_child": true,
   "frozen_port_owned_by_stranger": false,
   "frozen_verify_live": [
    null,
    "child"
   ],
   "listener_inode": "201382867",
   "listener_rc": 0,
   "mismatch_vs_contract": false,
   "port": 49576,
   "post_teardown_rows": {
    "/proc/net/tcp": [],
    "/proc/net/tcp6": []
   },
   "rows": {
    "/proc/net/tcp": [
     {
      "addr_hex": "0302017F",
      "inode": "201382867",
      "network_order_match": false,
      "per_word_host_order_match": true
     }
    ]
   },
   "scope": "extra",
   "v6only": null
  },
  {
   "bind": "::ffff:127.1.2.3",
   "case": "F",
   "connect_127": "ConnectionRefusedError(errno=111)",
   "connect_v6_loopback": "ConnectionRefusedError(errno=111)",
   "expected": true,
   "family": "AF_INET6",
   "frozen_http_get_error": "ConnectionRefusedError",
   "frozen_http_get_status": null,
   "frozen_listen_inodes": [],
   "frozen_port_owned_by_child": null,
   "frozen_port_owned_by_stranger": null,
   "frozen_verify_live": [
    "probe:port-listener-ownership-unproven",
    "unproven"
   ],
   "listener_inode": "201422911",
   "listener_rc": 0,
   "mismatch_vs_contract": true,
   "port": 46728,
   "post_teardown_rows": {
    "/proc/net/tcp": [],
    "/proc/net/tcp6": []
   },
   "rows": {
    "/proc/net/tcp6": [
     {
      "addr_hex": "0000000000000000FFFF00000302017F",
      "inode": "201422911",
      "network_order_match": false,
      "per_word_host_order_match": true
     }
    ]
   },
   "scope": "extra",
   "v6only": 0
  }
 ],
 "synthetic": [
  {
   "address": "127.0.0.1",
   "contract": true,
   "frozen_accepts": true,
   "inode": "9001",
   "verdict": "ok"
  },
  {
   "address": "127.255.255.254",
   "contract": true,
   "frozen_accepts": true,
   "inode": "9002",
   "verdict": "ok"
  },
  {
   "address": "1.2.3.127",
   "contract": false,
   "frozen_accepts": false,
   "inode": "9003",
   "verdict": "ok"
  },
  {
   "address": "0.0.0.0",
   "contract": false,
   "frozen_accepts": false,
   "inode": "9004",
   "verdict": "ok"
  },
  {
   "address": "::1",
   "contract": true,
   "frozen_accepts": false,
   "inode": "9101",
   "verdict": "FALSE-REJECT"
  },
  {
   "address": "::ffff:127.0.0.1",
   "contract": true,
   "frozen_accepts": false,
   "inode": "9102",
   "verdict": "FALSE-REJECT"
  },
  {
   "address": "::ffff:127.255.255.254",
   "contract": true,
   "frozen_accepts": false,
   "inode": "9103",
   "verdict": "FALSE-REJECT"
  },
  {
   "address": "::",
   "contract": false,
   "frozen_accepts": false,
   "inode": "9104",
   "verdict": "ok"
  },
  {
   "address": "::ffff:1.0.0.0",
   "contract": false,
   "frozen_accepts": true,
   "inode": "9105",
   "verdict": "FALSE-ACCEPT"
  },
  {
   "address": "2001:db8::100:0",
   "contract": false,
   "frozen_accepts": true,
   "inode": "9106",
   "verdict": "FALSE-ACCEPT"
  },
  {
   "address": "::ffff:10.0.0.127",
   "contract": false,
   "frozen_accepts": false,
   "inode": "9107",
   "verdict": "ok"
  }
 ]
}
```

### Run 2: replicate; source compiled with the frozen `__pycache__` ignored
```
$ python3 -B -X pycache_prefix=/tmp/kama-r18-ProbeTcp6Format/pycache /tmp/kama-r18-ProbeTcp6Format/probe.py
exit 0
stderr: (empty; sha256 e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855)
stdout: 22890 bytes, sha256 9e960998eba7be2abda4c6a245d1264389cef3e551b4990c4671c80da8a6110d, finished 18:05:40.61 -0300
pycache prefix exists: False   (checked after the run: nothing written)
```
The human-readable part of stdout follows. The JSON tail re-serialises the same fields with run-2 ports and pids, so I did not reproduce it.
```
kernel 7.2.11-arch1-1; python 3.14.8; byteorder little; machine x86_64
ip_local_port_range ['32768', '60999']
net.ipv6.bindv6only 0
frozen sha256 before 0efd1723b02ef748d720a6036d3ac481b1d5fe9755110999d7c9acaf486c46ac matches-SHA256SUMS=True
/proc/net/tcp header:   sl  local_address rem_address   st tx_queue rx_queue tr tm->when retrnsmt   uid  timeout inode
/proc/net/tcp6 header:   sl  local_address                         remote_address                        st tx_queue rx_queue tr tm->when retrnsmt   uid  timeout inode
frozen module loaded from /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/frozen/tools_kama-llamacpp-live.py; SCHEMA='kama-llamacpp-live/v2'
=== CASE A (assigned): AF_INET bind ('127.0.0.1', 52280); port hex CC38 ===
  listener pid=3110517 fd=3 inode=201442494 sockname=['127.0.0.1', 52280]
  pre-bind 0A rows on port: {'/proc/net/tcp': [], '/proc/net/tcp6': []}
  raw /proc/net/tcp 0A rows for port 52280:
       3: 0100007F:CC38 00000000:0000 0A 00000000:00000000 00:00000000 00000000  1000        0 201442494 1 000000008703a5cd 100 0 0 10 0
      local-address hex 0100007F (len 8), inode column 201442494
      decode as per_32bit_word_host_order  = 127.0.0.1
      decode as network_byte_order         = 1.0.0.127
      bound '127.0.0.1' encoded per_32bit_word_host_order  = 0100007F  equals-observed=True
      bound '127.0.0.1' encoded network_byte_order         = 7F000001  equals-observed=False
      frozen sub-terms: {"addr_hex.endswith('7F')": true}
  raw /proc/net/tcp6 0A rows for port 52280:
    (none)
  $ ss -Hltnp 'sport = :52280'  (exit 0)
    LISTEN 0      8      127.0.0.1:52280 0.0.0.0:* users:(("python3",pid=3110517,fd=3))
  listener socket fds (readlink /proc/3110517/fd/*): {3: 'socket:[201442494]'}
  FROZEN _listen_inodes(port)                  -> ['201442494']
  FROZEN port_owned_by(listener pid 3110517, port) -> True
  FROZEN port_owned_by(stranger pid 3110466, port) -> False
  FROZEN verify_live(listener proc, port, 'probe') -> (None, 'child')
  FROZEN http_get(port, '/health')             -> {'status': 200, 'error': None, 'body': '{"status":"ok"}'}
  raw connect 127.0.0.1                        -> 'connected'
  raw connect ::1                              -> 'ConnectionRefusedError(errno=111)'
  listener exit rc=0; listener stderr: ['accepted peer 127.0.0.1 port 38882', 'accepted peer 127.0.0.1 port 38896']
  post-teardown 0A rows on port: {'/proc/net/tcp': [], '/proc/net/tcp6': []}
=== CASE B (assigned): AF_INET6 bind ('::1', 50177) IPV6_V6ONLY=default(getsockopt=1); port hex C401 ===
  listener pid=3110537 fd=3 inode=201437464 sockname=['::1', 50177]
  pre-bind 0A rows on port: {'/proc/net/tcp': [], '/proc/net/tcp6': []}
  raw /proc/net/tcp 0A rows for port 50177:
    (none)
  raw /proc/net/tcp6 0A rows for port 50177:
       1: 00000000000000000000000001000000:C401 00000000000000000000000000000000:0000 0A 00000000:00000000 00:00000000 00000000  1000        0 201437464 1 00000000fbff931f 100 0 0 10 0
      local-address hex 00000000000000000000000001000000 (len 32), inode column 201437464
      decode as per_32bit_word_host_order  = ::1
      decode as network_byte_order         = ::1.0.0.0
      bound '::1' encoded per_32bit_word_host_order  = 00000000000000000000000001000000  equals-observed=True
      bound '::1' encoded network_byte_order         = 00000000000000000000000000000001  equals-observed=False
      frozen sub-terms: {"addr_hex.endswith('00000001')": false, "len(addr_hex[:24])": 24, "len('0000000000000000FFFF00')": 22, "addr_hex[:24] == '0000000000000000FFFF00'": false, "addr_hex.endswith('7F')": false}
  $ ss -Hltnp 'sport = :50177'  (exit 0)
    LISTEN 0      8      [::1]:50177 [::]:* users:(("python3",pid=3110537,fd=3))
  listener socket fds (readlink /proc/3110537/fd/*): {3: 'socket:[201437464]'}
  FROZEN _listen_inodes(port)                  -> []
  FROZEN port_owned_by(listener pid 3110537, port) -> None
  FROZEN port_owned_by(stranger pid 3110466, port) -> None
  FROZEN verify_live(listener proc, port, 'probe') -> ('probe:port-listener-ownership-unproven', 'unproven')
  FROZEN http_get(port, '/health')             -> {'status': None, 'error': 'ConnectionRefusedError', 'body': ''}
  raw connect 127.0.0.1                        -> 'ConnectionRefusedError(errno=111)'
  raw connect ::1                              -> 'connected'
  listener exit rc=0; listener stderr: ['accepted peer ::1 port 56802']
  post-teardown 0A rows on port: {'/proc/net/tcp': [], '/proc/net/tcp6': []}
=== CASE C (assigned): AF_INET6 bind ('::ffff:127.0.0.1', 47859) IPV6_V6ONLY=0(getsockopt=0); port hex BAF3 ===
  listener pid=3110541 fd=3 inode=201391531 sockname=['::ffff:127.0.0.1', 47859]
  pre-bind 0A rows on port: {'/proc/net/tcp': [], '/proc/net/tcp6': []}
  raw /proc/net/tcp 0A rows for port 47859:
    (none)
  raw /proc/net/tcp6 0A rows for port 47859:
       2: 0000000000000000FFFF00000100007F:BAF3 00000000000000000000000000000000:0000 0A 00000000:00000000 00:00000000 00000000  1000        0 201391531 1 000000009967e24f 100 0 0 10 0
      local-address hex 0000000000000000FFFF00000100007F (len 32), inode column 201391531
      decode as per_32bit_word_host_order  = ::ffff:127.0.0.1
      decode as network_byte_order         = ::ffff:0:100:7f
      bound '::ffff:127.0.0.1' encoded per_32bit_word_host_order  = 0000000000000000FFFF00000100007F  equals-observed=True
      bound '::ffff:127.0.0.1' encoded network_byte_order         = 00000000000000000000FFFF7F000001  equals-observed=False
      frozen sub-terms: {"addr_hex.endswith('00000001')": false, "len(addr_hex[:24])": 24, "len('0000000000000000FFFF00')": 22, "addr_hex[:24] == '0000000000000000FFFF00'": false, "addr_hex.endswith('7F')": true}
  $ ss -Hltnp 'sport = :47859'  (exit 0)
    LISTEN 0      8      [::ffff:127.0.0.1]:47859 *:* users:(("python3",pid=3110541,fd=3))
  listener socket fds (readlink /proc/3110541/fd/*): {3: 'socket:[201391531]'}
  FROZEN _listen_inodes(port)                  -> []
  FROZEN port_owned_by(listener pid 3110541, port) -> None
  FROZEN port_owned_by(stranger pid 3110466, port) -> None
  FROZEN verify_live(listener proc, port, 'probe') -> ('probe:port-listener-ownership-unproven', 'unproven')
  FROZEN http_get(port, '/health')             -> {'status': 200, 'error': None, 'body': '{"status":"ok"}'}
  raw connect 127.0.0.1                        -> 'connected'
  raw connect ::1                              -> 'ConnectionRefusedError(errno=111)'
  listener exit rc=0; listener stderr: ['accepted peer ::ffff:127.0.0.1 port 54378', 'accepted peer ::ffff:127.0.0.1 port 54388']
  post-teardown 0A rows on port: {'/proc/net/tcp': [], '/proc/net/tcp6': []}
=== CASE D (assigned): AF_INET6 bind ('::', 40909) IPV6_V6ONLY=0(getsockopt=0); port hex 9FCD ===
  listener pid=3110570 fd=3 inode=201423688 sockname=['::', 40909]
  pre-bind 0A rows on port: {'/proc/net/tcp': [], '/proc/net/tcp6': []}
  raw /proc/net/tcp 0A rows for port 40909:
    (none)
  raw /proc/net/tcp6 0A rows for port 40909:
       2: 00000000000000000000000000000000:9FCD 00000000000000000000000000000000:0000 0A 00000000:00000000 00:00000000 00000000  1000        0 201423688 1 000000005327ecba 100 0 0 10 0
      local-address hex 00000000000000000000000000000000 (len 32), inode column 201423688
      decode as per_32bit_word_host_order  = ::
      decode as network_byte_order         = ::
      bound '::' encoded per_32bit_word_host_order  = 00000000000000000000000000000000  equals-observed=True
      bound '::' encoded network_byte_order         = 00000000000000000000000000000000  equals-observed=True
      frozen sub-terms: {"addr_hex.endswith('00000001')": false, "len(addr_hex[:24])": 24, "len('0000000000000000FFFF00')": 22, "addr_hex[:24] == '0000000000000000FFFF00'": false, "addr_hex.endswith('7F')": false}
  $ ss -Hltnp 'sport = :40909'  (exit 0)
    LISTEN 0      8      *:40909 *:* users:(("python3",pid=3110570,fd=3))
  listener socket fds (readlink /proc/3110570/fd/*): {3: 'socket:[201423688]'}
  FROZEN _listen_inodes(port)                  -> []
  FROZEN port_owned_by(listener pid 3110570, port) -> None
  FROZEN port_owned_by(stranger pid 3110466, port) -> None
  FROZEN verify_live(listener proc, port, 'probe') -> ('probe:port-listener-ownership-unproven', 'unproven')
  FROZEN http_get(port, '/health')             -> {'status': 200, 'error': None, 'body': '{"status":"ok"}'}
  raw connect 127.0.0.1                        -> 'connected'
  raw connect ::1                              -> 'connected'
  listener exit rc=0; listener stderr: ['accepted peer ::ffff:127.0.0.1 port 39508', 'accepted peer ::ffff:127.0.0.1 port 39514', 'accepted peer ::1 port 41562']
  post-teardown 0A rows on port: {'/proc/net/tcp': [], '/proc/net/tcp6': []}
=== CASE E (extra): AF_INET bind ('127.1.2.3', 49322); port hex C0AA ===
  listener pid=3110572 fd=3 inode=201428356 sockname=['127.1.2.3', 49322]
  pre-bind 0A rows on port: {'/proc/net/tcp': [], '/proc/net/tcp6': []}
  raw /proc/net/tcp 0A rows for port 49322:
       3: 0302017F:C0AA 00000000:0000 0A 00000000:00000000 00:00000000 00000000  1000        0 201428356 1 00000000443d8b7a 100 0 0 10 0
      local-address hex 0302017F (len 8), inode column 201428356
      decode as per_32bit_word_host_order  = 127.1.2.3
      decode as network_byte_order         = 3.2.1.127
      bound '127.1.2.3' encoded per_32bit_word_host_order  = 0302017F  equals-observed=True
      bound '127.1.2.3' encoded network_byte_order         = 7F010203  equals-observed=False
      frozen sub-terms: {"addr_hex.endswith('7F')": true}
  raw /proc/net/tcp6 0A rows for port 49322:
    (none)
  $ ss -Hltnp 'sport = :49322'  (exit 0)
    LISTEN 0      8      127.1.2.3:49322 0.0.0.0:* users:(("python3",pid=3110572,fd=3))
  listener socket fds (readlink /proc/3110572/fd/*): {3: 'socket:[201428356]'}
  FROZEN _listen_inodes(port)                  -> ['201428356']
  FROZEN port_owned_by(listener pid 3110572, port) -> True
  FROZEN port_owned_by(stranger pid 3110466, port) -> False
  FROZEN verify_live(listener proc, port, 'probe') -> (None, 'child')
  FROZEN http_get(port, '/health')             -> {'status': None, 'error': 'ConnectionRefusedError', 'body': ''}
  raw connect 127.0.0.1                        -> 'ConnectionRefusedError(errno=111)'
  raw connect ::1                              -> 'ConnectionRefusedError(errno=111)'
  listener exit rc=0; listener stderr: []
  post-teardown 0A rows on port: {'/proc/net/tcp': [], '/proc/net/tcp6': []}
=== CASE F (extra): AF_INET6 bind ('::ffff:127.1.2.3', 55254) IPV6_V6ONLY=0(getsockopt=0); port hex D7D6 ===
  listener pid=3110575 fd=3 inode=201415554 sockname=['::ffff:127.1.2.3', 55254]
  pre-bind 0A rows on port: {'/proc/net/tcp': [], '/proc/net/tcp6': []}
  raw /proc/net/tcp 0A rows for port 55254:
    (none)
  raw /proc/net/tcp6 0A rows for port 55254:
       0: 0000000000000000FFFF00000302017F:D7D6 00000000000000000000000000000000:0000 0A 00000000:00000000 00:00000000 00000000  1000        0 201415554 1 000000005327ecba 100 0 0 10 0
      local-address hex 0000000000000000FFFF00000302017F (len 32), inode column 201415554
      decode as per_32bit_word_host_order  = ::ffff:127.1.2.3
      decode as network_byte_order         = ::ffff:0:302:17f
      bound '::ffff:127.1.2.3' encoded per_32bit_word_host_order  = 0000000000000000FFFF00000302017F  equals-observed=True
      bound '::ffff:127.1.2.3' encoded network_byte_order         = 00000000000000000000FFFF7F010203  equals-observed=False
      frozen sub-terms: {"addr_hex.endswith('00000001')": false, "len(addr_hex[:24])": 24, "len('0000000000000000FFFF00')": 22, "addr_hex[:24] == '0000000000000000FFFF00'": false, "addr_hex.endswith('7F')": true}
  $ ss -Hltnp 'sport = :55254'  (exit 0)
    LISTEN 0      8      [::ffff:127.1.2.3]:55254 *:* users:(("python3",pid=3110575,fd=3))
  listener socket fds (readlink /proc/3110575/fd/*): {3: 'socket:[201415554]'}
  FROZEN _listen_inodes(port)                  -> []
  FROZEN port_owned_by(listener pid 3110575, port) -> None
  FROZEN port_owned_by(stranger pid 3110466, port) -> None
  FROZEN verify_live(listener proc, port, 'probe') -> ('probe:port-listener-ownership-unproven', 'unproven')
  FROZEN http_get(port, '/health')             -> {'status': None, 'error': 'ConnectionRefusedError', 'body': ''}
  raw connect 127.0.0.1                        -> 'ConnectionRefusedError(errno=111)'
  raw connect ::1                              -> 'ConnectionRefusedError(errno=111)'
  listener exit rc=0; listener stderr: []
  post-teardown 0A rows on port: {'/proc/net/tcp': [], '/proc/net/tcp6': []}
=== SUPPLEMENTARY (synthetic table; frozen _listen_inodes with open() patched in its module namespace) ===
  (identical 11 synthetic rows and verdicts as run 1)
  FROZEN _listen_inodes(48879) -> ['9001', '9002', '9105', '9106']
frozen sha256 after 0efd1723b02ef748d720a6036d3ac481b1d5fe9755110999d7c9acaf486c46ac unchanged=True; frozen/__pycache__ exists=True
```
Note: in run 2 I abbreviated the eleven synthetic rows and verdict lines, which were byte-identical to run 1, to the single "(identical …)" line above.

### Predicate comparison (eval cell; pure computation, no sockets)
I imported the frozen module with `sys.dont_write_bytecode = True` and `sys.pycache_prefix` set to scratch; afterwards `pycache prefix dir created: False`. `frozen` below is the real frozen `_listen_inodes` run over a one-row table per address (`open` patched in its module namespace). The other three columns implement the candidate predicates as written in Finding 10.
```
address                 proc hex                          contract frozen            one-token         RevOwnership      decode+ipaddress
127.0.0.1               0100007F                          True     True ok           True ok           True ok           True ok
127.1.2.3               0302017F                          True     True ok           True ok           True ok           True ok
127.255.255.254         FEFFFF7F                          True     True ok           True ok           True ok           True ok
1.2.3.127               7F030201                          False    False ok          False ok          False ok          False ok
0.0.0.0                 00000000                          False    False ok          False ok          False ok          False ok
10.0.0.127              7F00000A                          False    False ok          False ok          False ok          False ok
::1                     00000000000000000000000001000000  True     False FALSE-REJECTTrue ok           True ok           True ok
::ffff:127.0.0.1        0000000000000000FFFF00000100007F  True     False FALSE-REJECTFalse FALSE-REJECTTrue ok           True ok
::ffff:127.1.2.3        0000000000000000FFFF00000302017F  True     False FALSE-REJECTFalse FALSE-REJECTTrue ok           True ok
::ffff:127.255.255.254  0000000000000000FFFF0000FEFFFF7F  True     False FALSE-REJECTFalse FALSE-REJECTTrue ok           True ok
::                      00000000000000000000000000000000  False    False ok          False ok          False ok          False ok
::ffff:1.0.0.0          0000000000000000FFFF000000000001  False    True FALSE-ACCEPT False ok          False ok          False ok
2001:db8::100:0         B80D0120000000000000000000000001  False    True FALSE-ACCEPT False ok          False ok          False ok
::ffff:10.0.0.127       0000000000000000FFFF00007F00000A  False    False ok          False ok          False ok          False ok
::ffff:0.0.0.1          0000000000000000FFFF000001000000  False    False ok          True FALSE-ACCEPT False ok          False ok
2001:db8::1             B80D0120000000000000000001000000  False    False ok          True FALSE-ACCEPT False ok          False ok
fe80::1                 000080FE000000000000000001000000  False    False ok          True FALSE-ACCEPT False ok          False ok
::ffff:0.0.0.0          0000000000000000FFFF000000000000  False    False ok          False ok          False ok          False ok
::7f00:1                0000000000000000000000000100007F  False    False ok          False ok          False ok          False ok
::ffff:1.2.3.127        0000000000000000FFFF00007F030201  False    False ok          False ok          False ok          False ok
{'frozen': (6, ['::1', '::ffff:127.0.0.1', '::ffff:127.1.2.3', '::ffff:127.255.255.254', '::ffff:1.0.0.0', '2001:db8::100:0']), 'one-token': (6, ['::ffff:127.0.0.1', '::ffff:127.1.2.3', '::ffff:127.255.255.254', '::ffff:0.0.0.1', '2001:db8::1', 'fe80::1']), 'RevOwnership': (0, []), 'decode+ipaddress': (0, [])}
pycache prefix dir created: False
```
The candidate predicates in that cell, verbatim:
```python
def one_token_edit(addr):   # '00000001' -> '01000000' only (mapped arm still dead)
    h = enc(addr)
    if len(h) == 32: return h.endswith('01000000')
    return h.endswith('7F')

def revownership_dropin(addr):  # RevOwnershipCode.md corrected predicate
    h = enc(addr)
    if len(h) == 32:
        return h == '00000000000000000000000001000000' or (h[:24] == '0000000000000000FFFF0000' and h.endswith('7F'))
    return h.endswith('7F')

def decode_ipaddress(addr):     # decode words in host order, then classify
    h = enc(addr)
    a = ipaddress.ip_address(b''.join(int(h[i:i+8], 16).to_bytes(4, sys.byteorder) for i in range(0, len(h), 8)))
    if a.version == 6 and a.ipv4_mapped is not None: return a.ipv4_mapped.is_loopback
    return a.is_loopback if a.version == 4 else a == ipaddress.ip_address('::1')
```
`enc(addr)` is the per-32-bit-word host-order encoder that matched every real row (`'%08X' % struct.unpack('=I', packed[i:i+4])[0]` per word). `truth(addr)` is `ipaddress` membership in `127.0.0.0/8`, `== ::1`, or `::ffff:127.0.0.0/104`.

### Teardown
- All 12 listeners (6 per run) exited with rc=0 after a `quit` on stdin. The `killpg` SIGKILL fallback was never needed. The post-teardown 0A rows were empty for every port (see the stdout above).
- `pgrep -af 'kama-r18-ProbeTcp6Format'` printed nothing (exit 1).
- `ss -Hltn '( sport = :51998 or sport = :60671 or sport = :43773 or sport = :56483 or sport = :49576 or sport = :46728 or sport = :52280 or sport = :50177 or sport = :47859 or sport = :40909 or sport = :49322 or sport = :55254 )'` printed nothing (exit 0).
- Final `ss -ltnp`, run after every listener had been torn down. None of the python3 listeners below is mine: their pids are 3120508, 3134461 and 3133284, all started after my runs, and they use backlog 5 where my listeners used 8.
```
State  Recv-Q Send-Q Local Address:Port  Peer Address:PortProcess
LISTEN 0      4096       127.0.0.1:631        0.0.0.0:*
LISTEN 0      4096      127.0.0.54:53         0.0.0.0:*
LISTEN 0      512        127.0.0.1:36381      0.0.0.0:*    users:(("omp",pid=3092,fd=98))
LISTEN 0      5          127.0.0.1:37407      0.0.0.0:*    users:(("python3",pid=3120508,fd=3))
LISTEN 0      4096       127.0.0.1:40443      0.0.0.0:*
LISTEN 0      10         127.0.0.1:39017      0.0.0.0:*    users:(("chromium",pid=2082972,fd=77))
LISTEN 0      5          127.0.0.1:58872      0.0.0.0:*    users:(("python3",pid=3134461,fd=3))
LISTEN 0      4096      172.17.0.1:53         0.0.0.0:*
LISTEN 0      5          127.0.0.1:8796       0.0.0.0:*    users:(("python3",pid=1511,fd=3))
LISTEN 0      5          127.0.0.1:8795       0.0.0.0:*    users:(("python3",pid=1512,fd=3))
LISTEN 0      512        127.0.0.1:8793       0.0.0.0:*    users:(("python3",pid=1516,fd=3))
LISTEN 0      512        127.0.0.1:8791       0.0.0.0:*    users:(("python3",pid=1515,fd=3))
LISTEN 0      5          127.0.0.1:8790       0.0.0.0:*    users:(("python3",pid=1517,fd=3))
LISTEN 0      5          127.0.0.1:8789       0.0.0.0:*    users:(("python3",pid=1513,fd=3))
LISTEN 0      5          127.0.0.1:8788       0.0.0.0:*    users:(("python",pid=1518,fd=3))
LISTEN 0      256        127.0.0.1:8787       0.0.0.0:*    users:(("python3",pid=1514,fd=3))
LISTEN 0      4096   127.0.0.53%lo:53         0.0.0.0:*
LISTEN 0      4096         0.0.0.0:5355       0.0.0.0:*
LISTEN 0      5          127.0.0.1:45200      0.0.0.0:*    users:(("python3",pid=3133284,fd=3))
LISTEN 0      4096           [::1]:631           [::]:*
LISTEN 0      4096            [::]:5355          [::]:*
```
- Frozen tool sha256 at the end: `0efd1723b02ef748d720a6036d3ac481b1d5fe9755110999d7c9acaf486c46ac`. The frozen `__pycache__` listing was unchanged: both mtimes are still 16:56:59.86 and 18:02:05.28 -0300.

## Scripts (verbatim, so L1 can re-run them; deleted from /tmp afterwards)
`/tmp/kama-r18-ProbeTcp6Format/listener.py`, sha256 `4c41645c9eb2a04d977ddd6b56bf12eeec7fb0ad8386f02de7f2f17fce3fb65f`:
```python
#!/usr/bin/env python3
"""Scratch loopback listener for seat KamaR18.ProbeTcp6Format-2.

argv: family(inet|inet6) address port v6only(default|0|1)
Binds and listens, prints ONE JSON line (fd, inode, sockname, v6only),
answers any request from a loopback peer with HTTP 200 {"status":"ok"},
closes non-loopback peers unanswered, and exits on stdin 'quit'/EOF,
parent death (PR_SET_PDEATHSIG) or after DEADLINE seconds."""
import ctypes
import json
import os
import select
import signal
import socket
import sys
import time

DEADLINE = 60.0
BODY = b'{"status":"ok"}'


def is_loopback(host):
    return (host == '::1' or host.startswith('127.')
            or host.lower().startswith('::ffff:127.'))


def main():
    fam_name, addr, port, v6only = (sys.argv[1], sys.argv[2],
                                    int(sys.argv[3]), sys.argv[4])
    try:
        ctypes.CDLL(None, use_errno=True).prctl(1, signal.SIGKILL, 0, 0, 0)
    except Exception:
        pass
    fam = socket.AF_INET6 if fam_name == 'inet6' else socket.AF_INET
    lsock = socket.socket(fam, socket.SOCK_STREAM)
    if fam == socket.AF_INET6 and v6only != 'default':
        lsock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, int(v6only))
    try:
        lsock.bind((addr, port))
    except OSError as exc:
        print(json.dumps({'ok': False, 'errno': exc.errno,
                          'error': str(exc)}), flush=True)
        return 3
    lsock.listen(8)
    info = {'ok': True, 'pid': os.getpid(), 'fd': lsock.fileno(),
            'inode': os.fstat(lsock.fileno()).st_ino,
            'sockname': list(lsock.getsockname()[:2])}
    if fam == socket.AF_INET6:
        info['v6only'] = lsock.getsockopt(socket.IPPROTO_IPV6,
                                          socket.IPV6_V6ONLY)
    print(json.dumps(info), flush=True)
    end = time.monotonic() + DEADLINE
    while time.monotonic() < end:
        ready, _, _ = select.select([lsock, sys.stdin], [], [], 0.25)
        if sys.stdin in ready:
            line = sys.stdin.readline()
            if not line or line.strip() == 'quit':
                break
        if lsock in ready:
            conn, peer = lsock.accept()
            with conn:
                print(f'accepted peer {peer[0]} port {peer[1]}',
                      file=sys.stderr, flush=True)
                if not is_loopback(peer[0]):
                    continue
                conn.settimeout(2.0)
                data = b''
                try:
                    while b'\r\n\r\n' not in data and len(data) < 65536:
                        chunk = conn.recv(4096)
                        if not chunk:
                            break
                        data += chunk
                    if data:
                        conn.sendall(
                            b'HTTP/1.1 200 OK\r\n'
                            b'Content-Type: application/json\r\n'
                            b'Content-Length: ' + str(len(BODY)).encode()
                            + b'\r\nConnection: close\r\n\r\n' + BODY)
                except OSError as exc:
                    print(f'peer io error {type(exc).__name__}',
                          file=sys.stderr, flush=True)
    lsock.close()
    return 0


if __name__ == '__main__':
    sys.exit(main())
```

`/tmp/kama-r18-ProbeTcp6Format/probe.py`, sha256 `3cfe707926afb59a86f92516750ff75d8e6b75c6ea6544727bf0bc932927e750`:
```python
#!/usr/bin/env python3
"""Scratch experiment for seat KamaR18.ProbeTcp6Format-2 (kama-shokunin r18).

Binds python loopback listeners on ephemeral-range ports (never a registered
port), prints the raw /proc/net/tcp{,6} LISTEN (state 0A) rows for each port,
and reports what the FROZEN tool's _listen_inodes / port_owned_by /
verify_live / http_get return. Supplementary: the frozen _listen_inodes over
a synthetic table (open() patched in the module namespace only).
Advice only; never a lane verdict or measurement."""
import hashlib
import importlib.util
import io
import json
import os
import random
import select
import signal
import socket
import struct
import subprocess
import sys

sys.dont_write_bytecode = True  # never write __pycache__ beside FROZEN

FROZEN = ('/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/'
          'frozen/tools_kama-llamacpp-live.py')
FROZEN_SHA256 = ('0efd1723b02ef748d720a6036d3ac481b1d5fe9755110999d7c9acaf'
                 '486c46ac')
LISTENER = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        'listener.py')
REFUSED = {8080, 34113}          # registry/endpoint-consumers.tsv pins
PORT_LO, PORT_HI = 40000, 60999  # inside ip_local_port_range; excludes REFUSED
PROC_NET = ('/proc/net/tcp', '/proc/net/tcp6')

# id, family, bind address, IPV6_V6ONLY to set (None = leave default), scope,
# contract-expected ownership (C1: 127/8 in tcp; ::1 and ::ffff:127/104 in
# tcp6 are loopback-owned; a wildcard bind stays fail-closed = None).
CASES = [
    ('A', socket.AF_INET, '127.0.0.1', None, 'assigned', True),
    ('B', socket.AF_INET6, '::1', None, 'assigned', True),
    ('C', socket.AF_INET6, '::ffff:127.0.0.1', 0, 'assigned', True),
    ('D', socket.AF_INET6, '::', 0, 'assigned', None),
    ('E', socket.AF_INET, '127.1.2.3', None, 'extra', True),
    ('F', socket.AF_INET6, '::ffff:127.1.2.3', 0, 'extra', True),
]
FAMILY = {socket.AF_INET: 'AF_INET', socket.AF_INET6: 'AF_INET6'}


def sha256(path):
    with open(path, 'rb') as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def load_frozen():
    spec = importlib.util.spec_from_file_location('frozen_kama_live', FROZEN)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def listen_rows(port):
    """Verbatim state-0A rows whose local port == port, per table."""
    out = {}
    for path in PROC_NET:
        rows = []
        with open(path, encoding='ascii') as fh:
            next(fh, None)
            for line in fh:
                parts = line.split()
                if len(parts) < 10 or parts[3] != '0A':
                    continue
                if int(parts[1].rsplit(':', 1)[1], 16) == port:
                    rows.append(line.rstrip('\n'))
        out[path] = rows
    return out


def kernel_hex(family, address):
    """The local-address column an address would print as, per hypothesis."""
    packed = socket.inet_pton(family, address)
    return {
        'per_32bit_word_host_order': ''.join(
            '%08X' % struct.unpack('=I', packed[i:i + 4])[0]
            for i in range(0, len(packed), 4)),
        'network_byte_order': packed.hex().upper(),
    }


def decode(addr_hex):
    raw = bytes.fromhex(addr_hex)
    fam = socket.AF_INET if len(raw) == 4 else socket.AF_INET6
    words = b''.join(struct.pack('=I', int(addr_hex[i:i + 8], 16))
                     for i in range(0, len(addr_hex), 8))
    return {'per_32bit_word_host_order': socket.inet_ntop(fam, words),
            'network_byte_order': socket.inet_ntop(fam, raw)}


def frozen_terms(table, addr_hex):
    """The frozen predicate's sub-terms (tool lines 331-338), evaluated."""
    if table.endswith('tcp6'):
        return {
            "addr_hex.endswith('00000001')": addr_hex.endswith('00000001'),
            'len(addr_hex[:24])': len(addr_hex[:24]),
            "len('0000000000000000FFFF00')": len('0000000000000000FFFF00'),
            "addr_hex[:24] == '0000000000000000FFFF00'":
                addr_hex[:24] == '0000000000000000FFFF00',
            "addr_hex.endswith('7F')": addr_hex.endswith('7F'),
        }
    return {"addr_hex.endswith('7F')": addr_hex.endswith('7F')}


def socket_fds(pid):
    out = {}
    for fd in sorted(os.listdir(f'/proc/{pid}/fd'), key=int):
        try:
            target = os.readlink(f'/proc/{pid}/fd/{fd}')
        except OSError:
            continue
        if target.startswith('socket:['):
            out[int(fd)] = target
    return out


def raw_connect(host, port):
    fam = socket.AF_INET6 if ':' in host else socket.AF_INET
    try:
        with socket.socket(fam, socket.SOCK_STREAM) as sock:
            sock.settimeout(1.0)
            sock.connect((host, port))
            return 'connected'
    except OSError as exc:
        return f'{type(exc).__name__}(errno={exc.errno})'


def ss_rows(port):
    cmd = ['ss', '-Hltnp', f'sport = :{port}']
    res = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
    return (f"ss -Hltnp 'sport = :{port}'", res.returncode,
            res.stdout.rstrip('\n'), res.stderr.rstrip('\n'))


def stop_listener(proc):
    try:
        proc.stdin.write('quit\n')
        proc.stdin.flush()
        proc.stdin.close()
    except (OSError, ValueError):
        pass
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        os.killpg(proc.pid, signal.SIGKILL)
        proc.wait(timeout=5)
    err = proc.stderr.read()
    proc.stdout.close()
    proc.stderr.close()
    return proc.returncode, err


def start_listener(family, address, v6only):
    fam = 'inet6' if family == socket.AF_INET6 else 'inet'
    for _ in range(32):
        port = random.randint(PORT_LO, PORT_HI)
        if port in REFUSED:
            continue
        pre = listen_rows(port)
        if any(pre.values()):
            continue  # someone already listens on this port in either table
        proc = subprocess.Popen(
            [sys.executable, '-B', LISTENER, fam, address, str(port),
             'default' if v6only is None else str(v6only)],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, text=True, start_new_session=True)
        ready, _, _ = select.select([proc.stdout], [], [], 10.0)
        line = proc.stdout.readline() if ready else ''
        info = json.loads(line) if line else {'ok': False,
                                              'error': 'no-ready-line'}
        if info.get('ok'):
            return proc, port, info, pre
        rc, err = stop_listener(proc)
        if info.get('errno') != 98:  # only EADDRINUSE retries another port
            raise RuntimeError(f'listener failed: {info} rc={rc} err={err}')
    raise RuntimeError('no free port found')


def show(label, value):
    print(f'  {label:<44} -> {value!r}')


def run_case(mod, case):
    cid, family, address, v6only, scope, expected = case
    proc, port, info, pre = start_listener(family, address, v6only)
    v6txt = ('' if family == socket.AF_INET else
             f" IPV6_V6ONLY={'default' if v6only is None else v6only}"
             f"(getsockopt={info.get('v6only')})")
    print(f'=== CASE {cid} ({scope}): {FAMILY[family]} bind '
          f'({address!r}, {port}){v6txt}; port hex {port:04X} ===')
    print(f"  listener pid={info['pid']} fd={info['fd']} "
          f"inode={info['inode']} sockname={info['sockname']}")
    print(f'  pre-bind 0A rows on port: {pre}')
    summary = {'case': cid, 'scope': scope, 'family': FAMILY[family],
               'bind': address, 'port': port, 'v6only': info.get('v6only'),
               'listener_inode': str(info['inode']), 'expected': expected}
    try:
        rows = listen_rows(port)
        summary['rows'] = {}
        for table in PROC_NET:
            print(f'  raw {table} 0A rows for port {port}:')
            if not rows[table]:
                print('    (none)')
            for row in rows[table]:
                print(f'    {row}')
                parts = row.split()
                addr_hex = parts[1].rsplit(':', 1)[0]
                hyp = kernel_hex(family, address)
                print(f'      local-address hex {addr_hex} '
                      f'(len {len(addr_hex)}), inode column {parts[9]}')
                for key, val in decode(addr_hex).items():
                    print(f'      decode as {key:<26} = {val}')
                for key, val in hyp.items():
                    print(f'      bound {address!r} encoded {key:<26} = '
                          f'{val}  equals-observed={val == addr_hex}')
                print(f'      frozen sub-terms: '
                      f'{json.dumps(frozen_terms(table, addr_hex))}')
                summary['rows'].setdefault(table, []).append(
                    {'addr_hex': addr_hex, 'inode': parts[9],
                     'per_word_host_order_match':
                         hyp['per_32bit_word_host_order'] == addr_hex,
                     'network_order_match':
                         hyp['network_byte_order'] == addr_hex})
        cmd, rc, out, err = ss_rows(port)
        print(f'  $ {cmd}  (exit {rc})')
        print(f'    {out}' + (f'\n    stderr: {err}' if err else ''))
        print(f'  listener socket fds (readlink /proc/{proc.pid}/fd/*): '
              f'{socket_fds(proc.pid)}')
        inodes = mod._listen_inodes(port)
        owned_child = mod.port_owned_by(proc.pid, port)
        owned_stranger = mod.port_owned_by(os.getpid(), port)
        live = mod.verify_live(proc, port, 'probe')
        http = mod.http_get(port, '/health')
        http_view = {'status': http.get('status'), 'error': http.get('error'),
                     'body': http.get('body', b'')[:64].decode(
                         'utf-8', 'replace')}
        show('FROZEN _listen_inodes(port)', sorted(inodes))
        show(f'FROZEN port_owned_by(listener pid {proc.pid}, port)',
             owned_child)
        show(f'FROZEN port_owned_by(stranger pid {os.getpid()}, port)',
             owned_stranger)
        show("FROZEN verify_live(listener proc, port, 'probe')", live)
        show("FROZEN http_get(port, '/health')", http_view)
        c4 = raw_connect('127.0.0.1', port)
        c6 = raw_connect('::1', port)
        show('raw connect 127.0.0.1', c4)
        show('raw connect ::1', c6)
        summary.update({
            'frozen_listen_inodes': sorted(inodes),
            'frozen_port_owned_by_child': owned_child,
            'frozen_port_owned_by_stranger': owned_stranger,
            'frozen_verify_live': list(live),
            'frozen_http_get_status': http.get('status'),
            'frozen_http_get_error': http.get('error'),
            'connect_127': c4, 'connect_v6_loopback': c6,
            'mismatch_vs_contract': owned_child != expected,
        })
    finally:
        rc, err = stop_listener(proc)
    post = listen_rows(port)
    print(f'  listener exit rc={rc}; listener stderr: {err.splitlines()}')
    print(f'  post-teardown 0A rows on port: {post}')
    summary['post_teardown_rows'] = post
    summary['listener_rc'] = rc
    return summary


SYN_PORT = 0xBEEF  # 48879: synthetic rows only, never bound
SYN_HEAD = {
    '/proc/net/tcp': ('  sl  local_address rem_address   st tx_queue rx_queue'
                      ' tr tm->when retrnsmt   uid  timeout inode'),
    '/proc/net/tcp6': ('  sl  local_address                         '
                       'remote_address                        st tx_queue '
                       'rx_queue tr tm->when retrnsmt   uid  timeout inode'),
}
SYN_ROWS = [
    # table, address, inode, contract says loopback-owned?
    ('/proc/net/tcp', '127.0.0.1', '9001', True),
    ('/proc/net/tcp', '127.255.255.254', '9002', True),
    ('/proc/net/tcp', '1.2.3.127', '9003', False),
    ('/proc/net/tcp', '0.0.0.0', '9004', False),
    ('/proc/net/tcp6', '::1', '9101', True),
    ('/proc/net/tcp6', '::ffff:127.0.0.1', '9102', True),
    ('/proc/net/tcp6', '::ffff:127.255.255.254', '9103', True),
    ('/proc/net/tcp6', '::', '9104', False),
    ('/proc/net/tcp6', '::ffff:1.0.0.0', '9105', False),
    ('/proc/net/tcp6', '2001:db8::100:0', '9106', False),
    ('/proc/net/tcp6', '::ffff:10.0.0.127', '9107', False),
]


def run_synthetic(mod):
    """Frozen _listen_inodes over rows encoded the way this host prints
    them (per-32-bit-word host order, as the real rows above show)."""
    text = {path: [SYN_HEAD[path]] for path in PROC_NET}
    for table, address, inode, _ in SYN_ROWS:
        fam = socket.AF_INET6 if table.endswith('tcp6') else socket.AF_INET
        addr_hex = kernel_hex(fam, address)['per_32bit_word_host_order']
        zero = '0' * len(addr_hex)
        text[table].append(
            f'   {len(text[table]) - 1}: {addr_hex}:{SYN_PORT:04X} '
            f'{zero}:0000 0A 00000000:00000000 00:00000000 00000000  1000'
            f'        0 {inode} 1 0000000000000000 100 0 0 10 0')

    def fake_open(path, *args, **kwargs):
        if path in text:
            return io.StringIO('\n'.join(text[path]) + '\n')
        raise FileNotFoundError(path)

    mod.open = fake_open  # shadows builtins.open for this module only
    try:
        got = mod._listen_inodes(SYN_PORT)
    finally:
        del mod.open
    print('=== SUPPLEMENTARY (synthetic table; frozen _listen_inodes with '
          'open() patched in its module namespace) ===')
    for table in PROC_NET:
        for row in text[table][1:]:
            print(f'  {table:<15}{row}')
    print(f'  FROZEN _listen_inodes({SYN_PORT}) -> {sorted(got)}')
    out = []
    for table, address, inode, want in SYN_ROWS:
        have = inode in got
        verdict = ('ok' if have == want else
                   'FALSE-REJECT' if want else 'FALSE-ACCEPT')
        print(f'  {address:<24} inode {inode} contract-loopback={want!s:<5} '
              f'frozen-accepts={have!s:<5} {verdict}')
        out.append({'address': address, 'inode': inode, 'contract': want,
                    'frozen_accepts': have, 'verdict': verdict})
    return out


def main():
    print(f'kernel {os.uname().release}; python {sys.version.split()[0]}; '
          f'byteorder {sys.byteorder}; machine {os.uname().machine}')
    with open('/proc/sys/net/ipv4/ip_local_port_range') as fh:
        print(f'ip_local_port_range {fh.read().split()}')
    with open('/proc/sys/net/ipv6/bindv6only') as fh:
        print(f'net.ipv6.bindv6only {fh.read().strip()}')
    before = sha256(FROZEN)
    print(f'frozen sha256 before {before} '
          f'matches-SHA256SUMS={before == FROZEN_SHA256}')
    for path in PROC_NET:
        with open(path, encoding='ascii') as fh:
            print(f'{path} header: {next(fh).rstrip()}')
    mod = load_frozen()
    print(f'frozen module loaded from {mod.__file__}; '
          f'SCHEMA={mod.SCHEMA!r}')
    summaries = [run_case(mod, case) for case in CASES]
    synthetic = run_synthetic(mod)
    after = sha256(FROZEN)
    pycache = os.path.exists(os.path.join(os.path.dirname(FROZEN),
                                          '__pycache__'))
    print(f'frozen sha256 after {after} unchanged={after == before}; '
          f'frozen/__pycache__ exists={pycache}')
    print('=== SUMMARY (JSON) ===')
    print(json.dumps({'cases': summaries, 'synthetic': synthetic},
                     indent=1, sort_keys=True))
    return 0


if __name__ == '__main__':
    sys.exit(main())
```
