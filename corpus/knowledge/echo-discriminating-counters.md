source: S136 and S139 (RFC 8259 §7, JSON string escapes; S139 supersedes S136's escape-length wording), S137 (llama.cpp tools/server/server-common.cpp:1375 @ 704366d76, the response_format echo site); lane evidence `lessons/round-26-verifier-spotcheck.md:98-116` (the round-26 base-tree shortcut), `.ufo/waves/round-27/count-c1.py` (sha256 49491b80e4f4ed2a85ab822a52f0b1a0fdb1dee53423e3d43b60ee25d1bf2765, landed 1471f67659917cc0823caf6e08303a3a26977d66) and the round-27 wave receipts under `.ufo/waves/round-27/w1a3/out/`
verified-at: 2026-10-23 — sources opened this round (raw sha256 in the SOURCES rows); live probe of b11755 at 07:11:54Z (`w1a3/out/ExecLiveEchoProbe/receipt.json`); code lines re-read at the named revisions
recheck: on-release — reopen S137 and re-run the live probe when the installed llama.cpp build changes; S136/S139 180d

# Echo-discriminating error-signature counters

Round-27 exploratory entry (axis: calibration — the lane's claim-measurement
method). It records how a counter that credits an observed server error with
"new error knowledge" must be built so that the server cannot be made to say
the signature back. It is method knowledge for this lane's counters. It is
not a new llama-server error signature, and it does not establish that any
particular counter discriminates on data.

What is new here and what is not: the round-26 preregistration already named
"request-echo" and "one message split into several rows" as shortcut
classes (`.ufo/waves/round-26/preregistration.json:26,29`), and the round-26
outside spot-check prescribed comparing signatures with JSON-decoded request
strings (routed defect 2, `lessons/round-26-verifier-spotcheck.md:234`).
Those were round evidence and a routed defect, not lane knowledge or an
admission criterion. This entry adds the primary sources for why, the
message-minus-signature frame test and the boundary leg, live and offline
evidence on this build, the conditions under which the decoded-string
comparison is actually reached, and the limits.

## The failure it answers

Round 26 froze a counter that credited a row when the live error message held
the signature and the signature was "not echoed". The echo check compared the
signature with the request text as stored in the registry
(`git show eb09e742:.ufo/waves/round-26/count-c1.py`, lines 371-374 and 384:
`c["e_not_echoed"] = sig not in req_bytes`; a string body was kept verbatim).
After data, a critic met the frozen target from the base tree with 12 rows.
Each row stored its body as a JSON **string** whose `response_format.type`
value began with a `\u00XX` escape; the counter sent those bytes, the server
decoded them and put the decoded value into one generic message, and the
stored bytes never held the signature
(`lessons/round-26-verifier-spotcheck.md:98-116`). Replayed offline this
round, the round-26 test flags 0 of the 12 as echoes
(`w1a3/out/ExecOfflineEchoReplay/replay.receipt.json`).

## Two facts the rule rests on

1. **One JSON string value has many byte spellings.** RFC 8259 §7: "Any
   character may be escaped." A character in the Basic Multilingual Plane can
   be written as a six-character `\uXXXX` sequence; a character outside it as
   a twelve-character UTF-16 surrogate pair (S139, superseding S136's
   wording). Absence of the signature from the raw request bytes therefore
   does not rule out a decoded echo.
2. **llama-server b11755 puts decoded request values into error text.**
   `server-common.cpp:1375` (S137) throws
   `"response_format type must be one of \"text\" or \"json_object\", but got: " + response_type`.
   `json_value` (`server-common.h:43-56` at the same commit) returns the
   already-parsed string; for a nonempty type other than `text`,
   `json_object` or `json_schema`, the throw appends it to one fixed prefix,
   and the HTTP layer returns it as a 400 (`server.cpp:62-65`,
   `server-common.cpp:95-97`). The same frame carries any number of distinct
   caller-supplied "signatures"; they are not distinct faults. Live on the
   pinned b11755 binary, a plain spelling, a first-character `\u0065` spelling
   and a fully escaped spelling of one value returned byte-identical 400
   bodies holding the decoded value, and two different values shared one
   frame (`w1a3/out/ExecLiveEchoProbe/receipt.json`, requests req1-req6).
   S137 is one of at least 12 such frames in the pinned snapshot (others:
   `chat.cpp:324` tool_choice, `chat.cpp:874` reasoning_format, file and data
   URI paths at `server-common.cpp:1216,1221,1234`, model names in
   `server-models.cpp`), plus 14 throws that dump request JSON into the
   message (`w1a3/advice/ScoutEchoSitesSnapshot.md`).

## The rule

A counter that credits a live error signature must refuse it when either
holds:

- **Echo.** The signature occurs, case-folded or with all whitespace
  removed, in the request path, in any **JSON-decoded** key or value of the
  request body at any depth, or in either serialisation of the decoded body
  (ASCII-escaped and UTF-8). Raw bytes alone are never the comparison set,
  and a body the counter does not parse itself (a stored string) is either
  refused or decoded before the comparison.
- **Shared frame.** With the signature cut out of the message, the
  remainder (case-folded, not blank) equals the remainder of a row already
  credited. One message frame earns one row, whatever is spliced into it.
- **Boundary.** The signature is not wholly inside text the server owns:
  it is not a substring of one string literal on its cited source line, or
  it overlaps a span of the message that a decoded request string occupies.
  Without this leg, a signature made of the frame's tail plus the caller's
  value passes the other two (12/12 on the captured S137 messages,
  `w1a3/out/CriticKQ37Wording/frame_boundary_probe.json`).

The echo rule is conservative: text in an unrelated request field that
happens to equal a genuine, server-owned signature also rejects the row.
Overlap shows that the request could have supplied the text, not that the
server echoed it.

## How the round-27 counter implements it, and where it falls short

- Echo: clause (f) (`count-c1.py` `request_surfaces`/`json_strings`/`occurs`,
  lines 343-372, check at 585-587) walks decoded keys and string values of a
  dict or list body and adds both `json.dumps` serialisations; scalars other
  than strings are covered only through the serialisations. It does not
  parse a string body. Such bodies never reach it: the request-shape check
  (lines 576-581, `e:bad-*`) refuses any body that is not a dict, list or
  none, and the counter serialises accepted bodies itself. On the 12 round-26
  rows, clause (f) as written flags 0/12, the shape check refuses 12/12, and
  clause (f) on the decoded bodies flags 12/12
  (`w1a3/out/ExecOfflineEchoReplay/`). On the five live-probe requests it
  refuses 5/5, where the round-26 test would credit 3/5
  (`w1a3/out/ExecLiveEchoProbe/replay-function-level.json`).
- Shared frame: clause (h) `h:same-message-frame` (lines 707-709) replaces
  the signature with a NUL placeholder and lowercases. On the 12 round-26
  rows it leaves 1 row; with the frame check removed, 12 rows survive the
  other clause-(h) checks (`w1a3/out/MutFrameLoadBearing/`).
- Boundary: clause (d) requires the signature to be a substring of a C
  string literal on the cited line and of no literal on any other line
  (lines 565-571), which the frame-tail signatures above are not shown to
  meet; no clause checks overlap with request-supplied spans of the message.
- Shortfalls against the rule's wording (`w1a3/advice/CriticEntryRuleVsCode.md`):
  `lower()` is not Unicode case folding (`straße`/`strasse` are not matched);
  the placeholder keeps the cut position, so two messages whose remainders
  agree after deletion but differ in position count as two frames; a
  remainder of only tabs is not treated as blank. The counter therefore
  meets the rule for ASCII signatures and positional frames only.

## What this does not establish

- It is a necessary condition, not a sufficient one. Echo through channels
  other than the request body and transformed echoes are separate classes.
  The round-27 preregistration names the log/help/warning and
  transformed-request classes (`.ufo/waves/round-27/preregistration.json`,
  `controls_required`); file and model content was assigned to an attempt-2
  control seat (`.ufo/waves/round-27/w1-controls/spec.json`, CtlFileEcho).
  No control receipt for any of these classes under amendment A3 was ever
  committed: the attempt-2 orchestrator died, and the dispatched control wave
  left no committed receipts.
- The counter excludes `--help`/`--version` output and the log and responses
  of one default-profile healthy run (`count-c1.py` lines 480-503, 652-656);
  warning paths that only other profiles or requests reach are unsampled.
- The round-27 measured claim C1 was not run on data, so no count here shows
  that the rule discriminates genuine faults from shortcuts on real rows.
- Other servers and other llama.cpp builds may echo at other sites; S137 and
  the live probe are scoped to 704366d76 and ASCII signatures.
