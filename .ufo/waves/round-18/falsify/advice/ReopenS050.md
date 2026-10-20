VERDICT: confirm — the S050 pin is byte-exact (`4d58…48b2`, 52897 B, remote re-fetch 200 identical today), `::1/128` is literal in the same RFC, the mapped 80+16+32 layout and `/104 = 127/8` are correct, knowledge/Gate quotes are verbatim, and the S050 row parses as 11 clean cells with no bare pipe.

# ReopenS050 — RFC 4291 source, knowledge and Gate quote audit

Seat: KamaR18.ReopenS050 (leaf). Head audited: `1c325b2e58fcfdc6761f645b44cedfb1d65243e6`
(lane `master`; clone `seat/ReopenS050` clean, worktree files identical to committed blobs — sha256
of `corpus/SOURCES.md`, `corpus/knowledge/loopback-listener-ownership.md`,
`corpus/lessons/round-18.md` match between the live checkout and the clone at head).
No production/fleet/evidence edits. No official counting commands run. No server bound.

## 1. Source bytes and pin identity

- `corpus/SOURCES.md:62` teaches-cell sha256 `4d58dff6b432d5d524bf3a3b7f0337a4177fa65f92ed72f2a92e97b471de48b2`.
- Pinned raw: `.ufo/waves/round-18/sources/raw/www.rfc-editor.org/rfc/rfc4291.txt`
  `sha256sum` → `4d58dff6b432d5d524bf3a3b7f0337a4177fa65f92ed72f2a92e97b471de48b2`, `wc -l` 1403.
- Second pin copy `.ufo/waves/round-18/build/out/SourcePins/raw/www.rfc-editor.org/rfc/rfc4291.txt`
  hashes identically; `cmp` → identical.
- `build/out/SourcePins/pins.json` `rfc4291`: `http_status 200`, `final_url https://www.rfc-editor.org/rfc/rfc4291.txt`,
  `sha256 4d58…48b2`, `bytes 52897`, `identity.title "IP Version 6 Addressing Architecture"`,
  `version "RFC 4291"`, `publication_date "February 2006"`.
- Live re-fetch (read-only, scratch only):
  `curl -sS --max-time 25 -o /tmp/rfc4291-remote.txt -w 'http=%{http_code} size=%{size_download}\n' https://www.rfc-editor.org/rfc/rfc4291.txt`
  → `http=200 size=52897`; `sha256sum` → `4d58dff6…48b2`. The pinned bytes are the current published bytes.
- Header confirms the row's "Feb 2006, Standards Track": RFC:9 `Obsoletes: 3513`, RFC:10
  `Category: Standards Track`, RFC:16 `IP Version 6 Addressing Architecture`.

## 2. Cited lines are exact (pinned file, `awk 'NR>=…{printf "%d: %s\n", NR, $0}'`)

- RFC:472 `2.5.3.  The Loopback Address`; RFC:474 `The unicast address 0:0:0:0:0:0:0:1 is called the loopback address.`
- RFC:548 `2.5.5.2.  IPv4-Mapped IPv6 Address`; RFC:550-552 define the form;
  RFC:568 `|                80 bits               | 16 |      32 bits        |`;
  RFC:570 `|0000..............................0000|FFFF|    IPv4 address     |`;
  RFC:571 closes the diagram (567-571 blank+diagram block).
- SOURCES anchor `§2.5.3 … line 474`, `§2.5.5.2 … lines 548-552`, `layout diagram at line 570` all resolve.

## 3. `::1` is literally an exact /128, not only a derivation

`RFC:303` (table in §2.4 Address Type Identification): `Loopback             00...1  (128 bits)   ::1/128         2.5.3`.
So the teaches cell's "(an exact /128)" is textually supported by the same RFC, in addition to
RFC:474 and the `::1` example at RFC:215. The SOURCES anchor does not cite line 303 — a precision
nit only, not a false statement (see §7).

## 4. Mapped layout and `/104 = 127.0.0.0/8`

Verified with Python stdlib (`python3 -` in /tmp, no repo execution):

```
network ::ffff:127.0.0.0/104  num_addresses 16777216
contains ::ffff:127.0.0.1 True ; ::ffff:127.255.255.255 True
contains ::ffff:128.0.0.0 False
127.0.0.0/8 endpoints map into the /104: True
::ffff:0.0.0.0/96 contains ::ffff:128.0.0.0 True
loopback ::1/128 num_addresses 1
```

2^24 addresses = exactly the 256×65536 IPv4 127/8 space, endpoints included, 126/128 excluded;
the whole mapped block is /96. This matches RFC:568-570 (80 zero bits, 16 one bits `FFFF`, 32-bit
IPv4) and the teaches cell `::ffff:127.0.0.0/104 is exactly 127.0.0.0/8 mapped.`

## 5. Knowledge entry

`corpus/knowledge/loopback-listener-ownership.md:25-27`:
"RFC 4291 (S050) defines `::1` as the exact loopback address and the mapped form as 80 zero bits,
16 one bits and the IPv4 address. Thus mapped 127/8 is `::ffff:127.0.0.0/104`, not the whole mapped /96."
Every clause checked against RFC:303/474/568-570; the `/96` contrast is correct arithmetic (see §4).
Line 19 table row (`::1` … "allow exact loopback") and line 20 (`::ffff:127.0.0.1` … "allow mapped
127/8") match the RFC and the delivered predicate (see §6). Entry source line 1 cites S050; the
file is the SOURCES row's declared `used-by` cell (`corpus/SOURCES.md:62` cell 12).
No stale RFC citation in the published entry (draft `.ufo/waves/round-18/build/drafts/knowledge-ownership.md`
was superseded; its old v6.12/e75cf680 content is not in the published entry).

## 6. Gate quotes and the delivered predicate

`corpus/lessons/round-18.md` Gate table (all rows 3 cells; no bare pipe):
- Line 45: `§2.5.3:474: "The unicast address 0:0:0:0:0:0:0:1 is called the loopback address."`
  Verbatim RFC:474, 9 words (≤25). "IPv6 loopback is exact ::1" also matches RFC:303.
- Line 46: `§2.5.5.2:551–552: "This address type is used to represent the addresses of IPv4 nodes as IPv6 addresses."`
  Verbatim across RFC:551-552 with one space at the line join, 15 words (≤25).
  "Layout at 570 has 80 zero bits, 16 ones, IPv4." matches RFC:570 (header labels at 568);
  it honestly tags "mapped 127/8 prefix is lane derivation".
- Line 46 does not overclaim S050 for the 127/8 IPv4 prefix itself; the derivation label is correct.

Delivered predicate at head (`tools/kama-llamacpp-live.py:311-338`) implements exactly the RFC
semantics: `_tcp6_is_loopback` accepts only `address == 15*0x00 + 0x01` (exact ::1) or
`address[:12] == 10*0x00 + ffff` with `address[12] == 0x7f` (mapped /104), i.e. 80 zero + 16 one
+ 127/8. `_proc_listener_inode` applies it only to `0A` LISTEN rows (`:339-348`), and `port_owned_by`
returns True/False/None with unknown preserved (`:370-392`).

Clone experiment (source exactly as run, `cd /tmp/kama-r18-falsify-ReopenS050`):

```python
import importlib.util, ipaddress, pathlib
def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
live = load('tools/kama-llamacpp-live.py', 'live')
def tcp6_hex(a):
    b = ipaddress.ip_address(a).packed
    return ''.join(bytes(b[i:i+4][::-1]).hex().upper() for i in range(0, 16, 4))
for a in ['::1','::','::2','::ffff:127.0.0.1','::ffff:127.255.255.255',
          '::ffff:128.0.0.0','::ffff:126.255.255.255','::ffff:0.0.0.0',
          '::127.0.0.1','2001:db8::1','fe80::1']:
    print(a, tcp6_hex(a), live._tcp6_is_loopback(tcp6_hex(a)))
```

Observed: `::1` True; `::ffff:127.0.0.1` True; `::ffff:127.255.255.255` True;
`::ffff:128.0.0.0` False; `::ffff:126.255.255.255` False; `::ffff:0.0.0.0` False;
`::` False; `::2` False; IPv4-compatible `::127.0.0.1` False; `2001:db8::1` False; `fe80::1` False;
`''`, `'00'`, 32×`z` and a 31-char hex all False. `_proc_listener_inode` returns inode `43210` for
the `::1` and mapped-127 rows, `None` for mapped-128, `::`, `2001:db8::1`, non-`0A` state, and for
tcp4 `00000080` (127.0.0.1 row returns `43210`). This confirms the SOURCES/knowledge assignment
"exact ::1 /128" and "mapped 127/8, not /96" is what the code does, including both /104 boundaries.

## 7. SOURCES cell integrity — no bare pipe

Using the lane's own parser `tools/sources-append-only.py:83-125` (`split_cells`, which honors
`\|` and backtick code spans), run in the clone over `corpus/SOURCES.md`:

- `split_cells` on the S050 line → 11 cells, last cell exactly
  `corpus/knowledge/loopback-listener-ownership.md`; the row ends in a closing pipe (no trailing content).
- All 55 `| S0NN |` rows → 11 cells each; zero `None`/malformed. Header and separator rows also 11
  (the parser validates width against `len(header)`, `tools/sources-append-only.py:199,208-210`).
- `awk -F'|'` cross-check: all table lines 13 raw fields (empty + 11 + empty); `grep -c '\\|'` = 0.
  No literal/escaped pipe inside any cell, including S050's backticked `::1`, `/proc`, and
  `::ffff:127.0.0.0/104` spans. Non-`S0NN` table lines are only the header (11 cells) and
  separator (11 cells), both at `corpus/SOURCES.md:11-12`.
- S050 id is unique; status `mined` and recheck `180d` are in-enum (registry uses `mined`,
  `queued`, `rejected`; `180d` already used by S045).

## 8. Adjacent S050 citations (consistency, no new claim)

- `PROVINCE.md:86-88`: "covers native ::1 and mapped 127/8 using sourced procfs decoding (S048/S050).
  Wildcards remain refused." Matches predicate; wildcard refusal is policy and disclosed.
- `SKILL.md:611`: "recognises exact ::1 and mapped 127/8, never wildcard addresses" — matches.
- `corpus/README.md:261`: "tcp6 host-word encoding of ::1 and mapped 127/8 (S048–S050)" — matches
  (encoding is S048, address forms are S050).
- `corpus/lessons/round-18.md:17`: "Sources S048/S050 determine the ownership predicate" — the
  address-form half is S050; the encoding half is S048. Accurate split.

## 9. Nits and residual unknowns (visible; none refutes S050)

- Anchor precision: the teaches cell's "(an exact /128)" is stated literally at `RFC:303`, which the
  anchor cell (`corpus/SOURCES.md:62` cell 7) does not cite; it cites §2.5.3:474 instead. The claim is
  true and in-source; adding `§2.4:303` would make the anchor direct.
- "layout diagram at line 570" points at the diagram's data row; the full diagram block is 568-571.
  Content at 570 (80 zeros, `FFFF`, IPv4) is exactly what the cell says.
- Shipped selftest `tools/kama-llamacpp-live.py:1038-1045` exercises mapped-127 positive, `::1`,
  `::2`, `::`, but no mapped `/104` boundary negative (e.g. `::ffff:128.0.0.1`). The predicate is
  correct at both boundaries (clone run §6); this is a test-coverage gap in C1's ownership hardening,
  not a sourcing or behavior defect.
- Not verified by me: big-endian hosts, other kernels, other namespaces (already listed as limits in
  `corpus/knowledge/loopback-listener-ownership.md:52-59`); RFC HTML rendering (raw `.txt` is the pinned artifact).

## 10. Limits, installs, cleanup

- Official counting commands (`c1/measure.py`, `c2/survivors.py`) were NOT run; no mutation, no
  production execution, no port binding. Repeated mutation-targeted tests are other seats' work.
- Tool installs/upgrades: none (no pacman/uv/npx; host pacman pause untouched).
- Scratch removed: `/tmp/kama-r18-falsify-ReopenS050` and `/tmp/rfc4291-remote.txt` deleted;
  `pgrep -af kama-r18-falsify-ReopenS050` → no output before removal; no seat-owned listener existed
  (only pure-function calls and one outbound HTTPS read).
