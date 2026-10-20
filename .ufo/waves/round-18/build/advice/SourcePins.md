VERDICT: partial — nine source documents were pinned; the requested GNU Automake HTML page timed out, so its citation basis is the official 1.19 release source.

## Delivered behavior

Created `pin.py`, `pins.json`, and byte-for-byte raw copies under `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/build/out/SourcePins/`. `pin.py` uses urllib GETs, records URL/redirect/status, SHA-256, byte length, page identity and dynamically located ranges; `--verify` re-fetches configured sources and compares recorded digests and pin records; `--selftest` is offline and re-derives the saved records. Line splitting uses LF (not `splitlines()`), because RFC 4291 contains 25 form-feed page breaks; this preserves the RFC's 1,403 LF-delimited line numbers.

All locator ranges below were produced by string/regex search, not literal line numbers in the locator table. Pin records and quote checks are in `.../build/out/SourcePins/pins.json`.

## Retained evidence

- Linux tag `v7.2` exists; `git ls-remote` observed peeled commit `8d3ae59288f1e7d58d76558a6ee96d533bc5019f`, so no newest-v7.x fallback was used. Captured titles/versions: `TCP over IPv6`, `IPv4 specific functions`, and `The proc/net/tcp and proc/net/tcp6 variables`; each records `Linux v7.2`.
  - `net/ipv6/tcp_ipv6.c:2126-2198`, `get_tcp6_sock`: “%08X%08X%08X%08X:%04X”; “src->s6_addr32[0], src->s6_addr32[1],”.
  - `net/ipv4/tcp_ipv4.c:2770-2832`, `get_tcp4_sock`: “%08X:%04X %08X:%04X”; “__be32 src = inet->inet_rcv_saddr;”.
  - `Documentation/networking/proc_net_tcp.rst:10-15`: “implemented by tcp4_seq_show() in net/ipv4/tcp_ipv4.c”. Example columns are pinned at `:18-24`, including “local IPv4 address”.
- RFC 4291 identity recorded as “IP Version 6 Addressing Architecture”, RFC 4291, February 2006. The mapped-address section is pinned at `rfc4291.txt:548-573` (“IPv4 nodes as IPv6 addresses.”; `|0000...|FFFF|`); loopback is pinned at `:472-486` (“0:0:0:0:0:0:0:1 is called the loopback address.”).
- Python's requested URL returned HTTP 301 to `https://docs.python.org/3.14/builtins/exceptions.html`; final title/version: “Built-in Exceptions — Python 3.14.8 documentation” / Python 3.14.8. Located evidence: `exceptions.html:307-313` BaseException (“The base class for all built-in exceptions.”), `:513-519` KeyboardInterrupt, `:852-863` SystemExit (“It inherits from BaseException instead of Exception”), and `:1402-1475` exception hierarchy.
- pytest page identity recorded as “Exit codes - pytest documentation”, pytest documentation 9.1 (from the page-linked `documentation_options.js`, `VERSION: '9.1'`); generator metadata says “Sphinx 9.1.0 and Furo 2025.12.19”. Exit-code list is pinned at `exit-codes.html:310-347`, including “Test execution was interrupted by the user”, “Internal error happened while executing tests”, and “No tests were collected”.
- `https://www.gnu.org/software/automake/manual/html_node/Scripts_002dbased-Testsuites.html` timed out. `pins.json` records it as unreachable, without fabricated bytes or digest, and marks “S053 rejected-as-basis”. The exit-status citation instead comes from the official `https://ftp.gnu.org/gnu/automake/automake-1.19.tar.xz` release (Automake 1.19; version metadata says updated 3 September 2026). The Texinfo source pin is `automake.texi:9775-9777`: “an exit status of 0 from a test script will denote a success”; “an exit status of 77 a skipped test”; “an exit status of 99 a hard error”; “any other exit status will denote a failure”. Its hard-error description is pinned at `:9732-9739`.

The downloaded Automake tarball was separately checked with `gpgv` against the GNU keyring; it returned exit 0 (“Good signature”). That signature/keyring are not part of the pin artifact, and `pin.py` itself does not perform signature verification.

## Commands and outcomes

- `python3 /tmp/kama-r18-SourcePins/.ufo/waves/round-18/build/out/SourcePins/pin.py` — exit 2 after capturing the available sources; the only remaining fetch-level shortfall was the GNU HTML page timeout (the corresponding pin is not evaluated). An earlier development run of this command exited 2 on a missing span delimiter; that implementation defect was corrected before the successful capture.
- `python3 -m py_compile /tmp/kama-r18-SourcePins/.ufo/waves/round-18/build/out/SourcePins/pin.py` — exit 0.
- `python3 /tmp/kama-r18-SourcePins/.ufo/waves/round-18/build/out/SourcePins/pin.py --selftest` — final exit 0: 7 checks passed, including offline re-derivation of 9 raw documents. An earlier selftest fixture incorrectly combined a duplicate-anchor rejection with the positive span case; fixed before the final passing run.
- `git ls-remote --tags https://github.com/torvalds/linux 'refs/tags/v7.*'` (with tag listing/sort) — the observed v7.2 tag and peeled commit are recorded above; v7.2 existed, no fallback was needed.
- `gpgv --homedir /tmp/kama-r18-SourcePins-scratch/gnupghome --keyring /tmp/kama-r18-SourcePins-scratch/gnu-keyring.gpg /tmp/kama-r18-SourcePins-scratch/automake-1.19.tar.xz.sig /tmp/kama-r18-SourcePins-scratch/automake-1.19.tar.xz` — exit 0.
- `pin.py --verify` was not run: that mode re-fetches every configured URL, and the parent reported the GNU host timeout and directed that it not be retried. The implementation's live re-fetch path therefore remains unexercised in this seat.

## Exact delivered files and SHA-256

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/build/out/SourcePins/pin.py` — `8213363b2ef9300df8015fe2369bf2eb9548661716ad7ea92d10d4fa3a91150c`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/build/out/SourcePins/pins.json` — `6f5623975d68c95bd65dd5abb067cffdab3c296e26caba06d3915ba97161a26d`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/build/out/SourcePins/raw/linux/v7.2/net/ipv6/tcp_ipv6.c` — `dd3f400b6d29c940d298e0b0a600a82b32368219aee5bc8f17981b00bd7b0558`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/build/out/SourcePins/raw/linux/v7.2/net/ipv4/tcp_ipv4.c` — `bdf50d980735746844c3b5ffea3d62794378572c62f69fda8ec821afb448c4d8`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/build/out/SourcePins/raw/linux/v7.2/Documentation/networking/proc_net_tcp.rst` — `a4da3f43ee9dc52e626c437ff3ebca1338c75e2465706f444e76be06e3f7e67a`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/build/out/SourcePins/raw/www.rfc-editor.org/rfc/rfc4291.txt` — `4d58dff6b432d5d524bf3a3b7f0337a4177fa65f92ed72f2a92e97b471de48b2`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/build/out/SourcePins/raw/docs.python.org/3.14/library/exceptions.html` — `766d785f3da3cded889c028a75e917fedca36d969627ef21cfb08ed5e6fcdd26`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/build/out/SourcePins/raw/docs.pytest.org/en/stable/reference/exit-codes.html` — `7a13d907eab973617f3390c39a39ac2887882859f4a11f0e1640e491ac353d4c`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/build/out/SourcePins/raw/docs.pytest.org/en/stable/_static/documentation_options.js` — `75fb20632739ec060954f24f469f33b668771822e0e77c665bb0d6d9d6e13fea`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/build/out/SourcePins/raw/ftp.gnu.org/gnu/automake/automake-1.19.tar.xz` — `e3e2c2e3abf37898138db5b6c1d1dc35c9160c5978be7947d2c741705251d445`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/build/out/SourcePins/raw/ftp.gnu.org/gnu/automake/automake-1.19/doc/automake.texi` — `6d34777affbbadfd7728b41873251768f5808691dac56f704189dec5fe53b6e6`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/build/out/SourcePins/raw/ftp.gnu.org/gnu/automake/automake-1.19/doc/version.texi` — `ba558fc251f18236f4d5ccaeaa4055e22027438a48e702991fa3258452d263a5`

Report path: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/build/advice/SourcePins.md`.

## Design choices, limitations, and blockers

- Pin mode keeps the requested Automake HTML URL and its timeout as explicit unevaluated evidence; it does not silently substitute another HTML host. The official release source is a separate, clearly named fallback pin. The HTML page itself has no saved bytes/hash.
- Raw SHA-256 is strict: mutable docs URLs such as pytest `stable` will need repinning after content changes. `--verify` compares content digests and derived pins; it does not normalize a page to hide harmless edits, validate semantic truth, or re-resolve the Linux tag's commit from Git on each run. The tag commit in `pins.json` is the observed snapshot.
- HTML quote extraction is a small tag/entity stripper, not a full HTML parser. SHA-256 identifies captured bytes but does not independently prove their source authenticity or that an excerpt supports a larger causal claim. The offline selftest proves locator/artifact consistency, not network verification.
- No tools were installed or updated. The only blocker is the unavailable requested GNU HTML endpoint; L1's supplied direction was followed without further retries.
