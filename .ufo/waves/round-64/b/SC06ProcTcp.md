# SC06ProcTcp — re-open held row S049 (`proc_net_tcp.rst` @ v7.2) vs `tools/round64-c1-counter.py`

Round 64, wave b, seat SC06ProcTcp. Scope: source verification only — no verdict on C1/C2,
no counter run (none in scope), no edits outside this report and `out/SC06ProcTcp/`.

## Method and pin receipts

- Fetched the pinned bytes on **2026-10-28 (UTC)** from the registry URL
  `https://github.com/torvalds/linux/blob/v7.2/Documentation/networking/proc_net_tcp.rst`
  via its raw endpoint; 57 lines, RST.
- sha256 of fetched file:
  `a4da3f43ee9dc52e626c437ff3ebca1338c75e2465706f444e76be06e3f7e67a`
  — **byte-exact match** with the hash registered in S049's located column
  (registry/capability-claims… row S049, corpus/SOURCES.md line 61). The row's registered
  quotes re-verify: deprecation at line 8, `tcp6_seq_show()` at line 12, IPv4 example
  `46: 010310AC:9C4C` at line 18. S049's facts are still true at v7.2.
- Code side read at the freeze tip: lane HEAD = `f6a4ea9a8b5a876d685b08e7e582ec0723412a4a`;
  `git diff --stat f6a4ea9a..HEAD -- tools/round64-c1-counter.py corpus/SOURCES.md` is
  empty, so the `listeners()` / `_hex_loopback()` I quote is the frozen instrument.
- Evidence copies: `out/SC06ProcTcp/proc_net_tcp.rst` (fetched bytes) and
  `out/SC06ProcTcp/SOURCES-frozen.md` (SOURCES.md exported from the freeze tip).

## Line map of the doc (all 57 lines inspected)

| lines | content |
|---|---|
| 7 | scope sentence naming both `/proc/net/tcp` and `/proc/net/tcp6` |
| 8 | deprecation note |
| 10-12 | implemented by `tcp4_seq_show()` / `tcp6_seq_show()` |
| 14-15 | "listening TCP sockets" listed first, then established |
| 18-24 | IPv4 example `46: 010310AC:9C4C 030310AC:1770 01` + field arrows (state 19, remote addr/port 21/20, local port/addr 22/23, entry 24) |
| 26-31 | tx:rx / tr:tm->when / RTO segment arrows |
| 33-46 | third-segment example `1000  0 54165785 4 cd1e6040 25 4 27 3 -1` + arrows (inode at 44, uid 46) |
| 48-57 | `timer_active` table (0-4) — about timer_active, **not** `st` |

## Target 1 — the `st` value 0A (LISTEN)

- Quote (lines 18-19): example state `01` with the arrow label
  `|--> connection state`.
- Prose nearest to LISTEN (lines 14-15, 15 words): "It will first list all listening TCP
  sockets, and next list all established TCP connections."
- **Finding: the doc never enumerates state codes.** No `0A`, no LISTEN token, no state
  table anywhere in the file (case-insensitive search for `0A`/LISTEN-state codes: 0 hits
  outside the hex examples). The `timer_active` table (48-57) is a different column.
- Counter rule affected: `listeners()` keeps only rows with `f[3] != '0A'` filtered out —
  the entire LISTEN filter hangs on a literal this page does not document. The registry row
  itself already declares "not state codes" out of S049's scope; that exclusion is accurate.

## Target 2 — the inode column

- Quote (line 44): arrow label `-----------------------------> inode`; example value
  `54165785` at line 33.
- Field-position check against the doc's own 17-field example line (line 18 + 26 + 33
  concatenated, as real output is one line): `46:`(0) local(1) remote(2) `01`(3)
  tx:rx(4) tr:when(5) retrnsmt(6) uid(7) 0-window-probes(8) **inode(9)** refcount(10)
  mem-loc(11) rto(12) tick(13) quickack(14) cwnd(15) ssthresh(16).
- **Finding: SUPPORTED.** `listeners()` takes `int(f[9])` — index 9 is exactly the column
  the doc labels `inode`. Caveat: the doc labels positionally (arrow + example) and never
  numbers indices; index 9 is derivable from the example, not stated.

## Target 3 — the address byte order

- Quote (lines 18, 23): example `010310AC:9C4C` with the arrow label
  `---------------------------> local IPv4 address`. That is all the page offers: it
  nowhere states a byte order (searches for byte/hex/endian wording: 0 hits; the radix of
  ports, e.g. `9C4C` = 40012, is likewise never stated).
- **Finding: NOT documented — and this is the one genuinely unsourced parse rule.**
  `_hex_loopback()` hard-codes `'0100007F'` as the loopback test for 8-char
  `/proc/net/tcp` addresses, i.e. 127.0.0.1 printed as one little-endian `%08X` word
  (bytes `7F 00 00 01`). Nothing in S049 licenses that decoding; S048 covers only
  `/proc/net/tcp6` ("not `/proc/net/tcp` (IPv4)" is in its own scope note) and S050 is the
  RFC address layout, not a printing rule. The 32-char branch (`…01000000` for `::1`,
  `…FFFF00000100007F` for the IPv4-mapped form) is covered by S048 (four `%08X` words of
  raw `s6_addr32`, no byte swap) + S050 (mapped layout) — S049 contributes nothing there,
  has no tcp6 example line at all, and its row explicitly excludes "the IPv6 address byte
  encoding".

## Target 4 — the deprecation note

- Quote (line 8, 10 words): "Note that these interfaces are deprecated in favor of
  tcp_diag."
- **Finding: verified verbatim at line 8**, matching the registered located column. With
  lines 10-12 (implementors `tcp4_seq_show()` / `tcp6_seq_show()`) this grounds the
  counter's stance of reading procfs as a diagnostic plane, not a contract — consistent
  with how the C1 predicate words "from procfs and its own code alone".

## Secondary mechanics in `listeners()` not sourced by S049 (minor, for completeness)

- Header skip (`next(fh, None)`): the doc shows no header line; its example starts at the
  `46:` entry. Conventional, not documented.
- `len(f) < 10` guard: the doc's example implies ≥10 fields (17 shown); never stated as a
  minimum.
- `int(p, 16)` port radix: positions documented (line 22), radix not.

## Verdict for the re-open question

**S049 does not already support every parse rule in the code — a new row is needed.**

What S049 does support: the two-interface scope (line 7), that listener rows exist and come
first (14-15), the state column's position (18-19), the local address/port positions (18,
20-23), the inode column's position and meaning (33, 44), and the deprecation note (8).
All registered quotes re-verify byte-exact at the pinned sha256, so the row itself remains
sound at v7.2.

What it does not support (and its registered scope explicitly excludes):
1. `st` == `0A` (LISTEN) — the code's listener filter literal; no state codes in the doc.
2. Address byte order — the IPv4 little-endian word rule (`0100007F` for 127.0.0.1 in
   `/proc/net/tcp`) is sourced by no current row; the IPv6 word printing is already covered
   by S048 + S050.

Suggested sourcing (L1's call, not mine): a sibling-of-S048 code row on the v7.2 IPv4
printer (`tcp4_seq_show` / `get_tcp4_sock` in `net/ipv4/tcp_ipv4.c`) would cover both gaps
at once — the `%02X` state print (TCP_LISTEN == 0x0A) and the `%08X` little-endian word of
the IPv4 address. Widening S049's scope instead would contradict its own registered
exclusions; a new row is the cleaner fix.

## Housekeeping

- Tools installed/upgraded: none (no new tooling needed; pacman untouched).
- Scratch `/fast/scratch/hyaku/kama-r64/b/SC06ProcTcp` removed after evidence copy.
- No live server started; no ports touched; no git mutation anywhere.
