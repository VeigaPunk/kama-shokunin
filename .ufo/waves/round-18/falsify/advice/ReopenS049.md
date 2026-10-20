VERDICT: confirm — S049's committed row matches the pinned v7.2 bytes: verbatim deprecation quote at line 8 (10 words), `tcp6_seq_show()` at line 12, IPv4-only example at line 18, no IPv6 literal, no state-code table; Gate access re-verified live. Residuals are cosmetic/registry, not attributions to S049.

# Assignment
Open S049 `proc_net_tcp.rst`; verify (a) the narrower teaching/deprecation scope, (b) the negative IPv6-format scope, (c) the Gate row's quote/location/access, (d) that no unsupported state-code attribution is made to S049. Read-only; no production edit; no gate/runtime command on the live lane; no clone needed because no runtime experiment was assigned.

# Artifact under test
- Row: `corpus/SOURCES.md:61` (committed at `1c325b2e58fcfdc6761f645b44cedfb1d65243e6`), scope cell `not the IPv6 address byte encoding, not state codes`.
- Gate row: `corpus/lessons/round-18.md:44`, `.../proc_net_tcp.rst:8: "Note that these interfaces are deprecated in favor of tcp_diag." The only address example is IPv4.`
- Pinned bytes: `.ufo/waves/round-18/sources/raw/linux/v7.2/Documentation/networking/proc_net_tcp.rst` (57 lines, 2908 bytes, sha256 `a4da3f43ee9dc52e626c437ff3ebca1338c75e2465706f444e76be06e3f7e67a`). The build copy `.ufo/waves/round-18/build/out/SourcePins/raw/linux/v7.2/Documentation/networking/proc_net_tcp.rst` is byte-identical (md5 `f3fdc5ca5c474bafb57dc550113043ac` both).

# Findings

## F1 — quote is verbatim, at the claimed line, within the word limit
Executed `nl -ba <pinned file> | sed -n '1,20p'` and a Python exact-match scan:
- line 8 is exactly `Note that these interfaces are deprecated in favor of tcp_diag.` — `q_line8_exact True`, `occurrences 1`, `words 10` (Gate limit ≤25).
- line 12 is `and tcp6_seq_show() in net/ipv6/tcp_ipv6.c, respectively.` — matches the row's "`tcp6_seq_show()` named at line 12".
- line 18 is `   46: 010310AC:9C4C 030310AC:1770 01` — contains the row's cited `46: 010310AC:9C4C`.
The anchor's backticked fragments (`deprecated in favor of tcp_diag`, `tcp6_seq_show()`, `46: 010310AC:9C4C`) are all exact substrings. The SOURCES hash cell matches the file and the pin (`a4da3f43…`, 2908 bytes).

## F2 — access is recorded and independently re-verified
- Pin record `.ufo/waves/round-18/sources/pins.json` → `sources.linux_proc_net_tcp`: `status: fetched`, `http_status: 200`, `redirects: []`, `final_url https://raw.githubusercontent.com/torvalds/linux/v7.2/Documentation/networking/proc_net_tcp.rst`, `sha256 a4da3f43…`, `bytes 2908`; `pinned_at_utc 2026-10-20T21:29:29+00:00`. This satisfies the lesson Gate's "opened 2026-10-20" statement.
- Independent live re-fetch (this seat, 2026-10-20): `curl -sS https://raw.githubusercontent.com/torvalds/linux/v7.2/Documentation/networking/proc_net_tcp.rst` → `http=200 bytes=2908`, sha256 `a4da3f43ee9dc52e626c437ff3ebca1338c75e2465706f444e76be06e3f7e67a` — byte-identical.
- The exact URL cited in the Gate row (`github.com/.../blob/v7.2/...`) also serves the sentence: `curl -sSL` → `http=200 bytes=232986`, and the literal quote matched twice in the page body.
- The pins file's own locator checks corroborate line ranges: `pins.proc_net_tcp_fields` = span lines 10–15 with all quotes `matched: true`; `pins.proc_net_tcp_example` = span lines 18–24 with all quotes `matched: true`.

## F3 — negative IPv6-format scope is accurate
- The page contains no IPv6 address literal. Regex `(?:[0-9A-Fa-f]{0,4}:){3,}[0-9A-Fa-f]{0,4}` over the whole file returned `[]`; the only `::` is the ReST literal marker on line 16.
- No byte-order vocabulary: `grep -niE 'endian|byte order|network order|hexadecimal|base 16|decimal'` exited 1 (no match).
- Exactly one address example exists, and it is labeled IPv4: line 18 is the example, and lines 21 and 23 label the fields `remote IPv4 address` / `local IPv4 address`. The other hex pair (line 26, `00000150:00000000 01:00000019 00000000`) is the transmit/receive queue and timer block, not an address.
- Therefore the row's "its only address example is IPv4, so the IPv6 byte order comes from code (S048), never from this page" is supported, and the knowledge file's `S049 ... does not specify IPv6 byte order; do not cite its IPv4 example as authority for tcp6` (`corpus/knowledge/loopback-listener-ownership.md:13-14`) is accurate.

## F4 — negative "state codes" scope is accurate as written; no attribution to S049
- No standalone `0A` token exists: `grep -nw "0A"` on the file exited 1. The only match for the substring is inside `010310AC` on line 18 (the earlier non-word grep matched only that line).
- The page names the field but not its codes: line 19 says `|--> connection state`; there is no state table and no `0A`. The only table (lines 48–57) is headed `timer_active:` and lists 0–4 for the `tr` column; its entry `3` mentions `TIME_WAIT state` but that is the timer column, not the socket-state code.
- Production/knowledge use of `0A` is not attributed to S049: `grep -rn S049 corpus/` yields only (i) the registry row, (ii) the Gate reject row, (iii) the knowledge file's negative/deprecation cites at lines 13 and 58. No delivered text says S049 defines state codes. `grep -n "S049\|proc_net_tcp" SCORECARD.md` returned no match (exit 1, count 0), and the wave's C1 statement as given to this seat names S048/S050/S051/S054 (none is S049), so S049 carries no positive C1 weight.

## F5 — the committed scope is narrower than the build draft, as the lesson claims
Draft `.ufo/waves/round-18/build/drafts/sources-kernel.md:12` scope: `... deprecation; not the IPv6 address byte encoding` (no state-code exclusion). Committed `corpus/SOURCES.md:61` adds `, not state codes`. The draft Gate row (`sources-kernel.md:26`) rejected only `defines the IPv6 address byte order`; the committed lesson row (`round-18.md:44`) rejects `IPv6 byte order or 0A state codes`. Both additions are factually correct on the pinned bytes (F3, F4), so the narrowing is real and sound.

# Residuals (visible; none is a kill)

R1 (low) — Gate evidence covers only one disjunct. `round-18.md:44` adds `or 0A state codes` to the rejected reading, but its displayed evidence (the deprecation quote plus "The only address example is IPv4") addresses only the byte-order half. The state-code half is true — I verified the absence directly (`grep -nw 0A` exit 1; no state table; the 0–4 table is `timer_active`) — but the Gate cell does not show that check. Suggested one-line addition for L1: "no `0A` token anywhere; the only table is `timer_active` (tr column)". This edits the lesson, not the S049 row.

R2 (low, registry completeness) — `0A = LISTEN` has no SOURCES row. The committed S048 scope is the tcp6 row printer only; the committed S049 explicitly excludes state codes; no `tcp_states` mention remains in `corpus/`. The fact is used at `corpus/knowledge/loopback-listener-ownership.md:37` (`state 0A`) and in code at `tools/kama-llamacpp-live.py:331`, and it is empirically supported: `ProbeTcp6Format.md` records real `0A` rows for the `::1`, mapped and wildcard listeners (e.g. lines 141–142, 167, 192, 215) alongside `ss` LISTEN confirmations (lines 125, 150, 175, 200, 225), and the tool's literal fixture at line 1045 uses `0A`. The prior scout had recommended a code row for `include/net/tcp_states.h:13-22` (`.ufo/waves/round-18/build/advice/ScoutProcNetTcpDoc.md:32,104-105`), and the provisional draft carried it (`build/drafts/knowledge-ownership.md:1,23,135-140`), but the committed registry dropped it. This is a provenance gap for the enum, not a misattribution to S049: the knowledge file's own-work clause (line 1) covers the raw observation. If L1 wants the enum in the registry, append a new code row (e.g. S056) citing `include/net/tcp_states.h`; do not widen S049.

R3 (cosmetic) — wording. The SOURCES teaches cell says "the interface deprecated in favour of tcp_diag" (British spelling, singular) while the page says "these interfaces are deprecated in favor of tcp_diag" (US spelling, plural) at line 8. This is a paraphrase, not a quote — the Gate quote itself is exact and US-spelled — so it is not a misquote, but a registry that quotes primary text should prefer the source's spelling/number.

R4 (cosmetic, build-only) — stale pre-integration drafts still assign S049 to man-pages: `.ufo/waves/round-18/build/drafts/knowledge-ownership.md:1` ("S049 (man-pages 6.19 …)") and `.ufo/waves/round-18/build/advice/ScribeKnowledgeOwnership.md:7` (provisional rows). The delivered registry assigns S049 to `proc_net_tcp.rst`. These are build-stage artifacts, not corpus, and were not edited; a reader must not treat them as the registry. They also explain why the delivered knowledge file cites v7.2 lines while the draft cited v6.12.

# What would flip this
- Any IPv6 address literal or byte-order statement in the pinned file (would refute the negative scope).
- A standalone `0A` or any state-code table for the `st` column (would refute the state-code exclusion).
- A byte difference between the pin, the SOURCES sha256 cell, and the live v7.2 URL (would make the Gate quote/location unreliable).
- A delivered sentence attributing state codes to S049 (none found).

# Limits
- Scope of this seat is S049 only; S048's tcp_ipv6.c line numbers, S050's RFC lines, and C1/C2 counters are other seats' subjects.
- The blob URL was fetched once; GitHub serves the tag's current bytes, and the pin + SOURCES hash both match the raw fetch, so the citation is stable at this instant.
- Big-endian and non-x86 behaviour were not tested (not needed: S049 documents neither byte order).
- No rendered kernel.org HTML was opened; the tag's raw bytes are the cited authority.

# Commands run (exact; all read-only)
- `sha256sum .ufo/waves/round-18/sources/raw/linux/v7.2/Documentation/networking/proc_net_tcp.rst` → `a4da3f43ee9dc52e626c437ff3ebca1338c75e2465706f444e76be06e3f7e67a`; `wc -l -c` → `57 2908`.
- `nl -ba … | sed -n '1,20p'` → lines 8, 12, 18 as quoted.
- Python scan (exact match + regex) → `bytes 2908 sha256 a4da3f43…`, `q_line8_exact True occurrences 1 words 10`, `tcp6_seq_show line12 …`, `line18 '   46: 010310AC:9C4C 030310AC:1770 01'`, `word0A False`, `ipv6-like literals []`, `hexpair line 26` (queues/timers).
- `grep -nw "0A" <file>` → exit 1.
- `grep -niE 'endian|byte order|network order|hexadecimal|base 16|decimal' <file>` → exit 1.
- `curl -sS -o /tmp/r18s049-live.rst -w 'http=%{http_code} bytes=%{size_download}\n' <raw v7.2 URL>` → `http=200 bytes=2908`; sha256 identical.
- `curl -sSL -o /tmp/r18s049-blob.html -w … <blob v7.2 URL>` → `http=200 bytes=232986`; `grep -c "deprecated in favor of tcp_diag"` → `2`; exact sentence printed.
- `python3 -c` reading `pins.json` → `sources.linux_proc_net_tcp` fields above; `pins.proc_net_tcp_fields`/`…_example` status `located`, quotes `matched: true`.
- `grep -rn "S049" corpus/`, `grep -n "S049\|proc_net_tcp" SCORECARD.md`, `grep -rn "tcp_states"` (repo, excluding `.git`) → only the citations and build drafts noted above.
- Read-only inspections: `ProbeTcp6Format.md` lines 113–225; `build/drafts/sources-kernel.md:12,26`; `build/drafts/knowledge-ownership.md:1,23,135-140`; `build/advice/ScoutProcNetTcpDoc.md:32,104-105`; `corpus/knowledge/loopback-listener-ownership.md:1,13-14,37,58`; `tools/kama-llamacpp-live.py:331,1045`.

# Installs, scratch, listeners, writes
- Installs/upgrades: none (no pacman, uv, npm, cargo or binary download). The only network operations were two read-only HTTPS GETs of the cited source.
- Scratch `/tmp/r18s049-live.rst` and `/tmp/r18s049-blob.html` were created and removed; `/tmp/kama-r18-falsify-ReopenS049` was not needed and does not exist.
- No listener was started or bound by this seat; no registered port (8080/34113 or any consumer port) was contacted. The 14 Python listeners visible in `ss -ltnp` belong to other live seats.
- Files written: this report only, at `.ufo/waves/round-18/falsify/advice/ReopenS049.md`. No production, fleet, corpus, frozen-evidence or lesson file was edited; no git/jj state was touched.
