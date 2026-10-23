source: S136 (RFC 8259 §7, JSON string escapes), S137 (llama.cpp tools/server/server-common.cpp:1375 @ 704366d76, the response_format echo site); lane evidence `lessons/round-26-verifier-spotcheck.md:98-116` (the round-26 base-tree shortcut) and `.ufo/waves/round-27/count-c1.py` (sha256 49491b80e4f4ed2a85ab822a52f0b1a0fdb1dee53423e3d43b60ee25d1bf2765, landed 1471f67659917cc0823caf6e08303a3a26977d66)
verified-at: 2026-10-23 — both sources opened this round (raw sha256 in the SOURCES rows); the code lines quoted below re-read from the committed files at the named revisions
recheck: on-release — reopen S137 when the installed llama.cpp build changes; S136 180d

# Echo-discriminating error-signature counters

Round-27 exploratory entry (axis: calibration — the lane's claim-measurement
method). It records how a counter that credits an observed server error with
"new error knowledge" must be built so that the server cannot be made to say
the signature back. It is method knowledge for this lane's counters. It is
not a new llama-server error signature, and it does not establish that any
particular counter discriminates on data.

## The failure it answers

Round 26 froze a counter that credited a row when the live error message held
the signature and the signature was "not echoed". The echo check compared the
signature with the **raw request bytes**
(`git show eb09e742:.ufo/waves/round-26/count-c1.py`, line 384:
`c["e_not_echoed"] = sig not in req_bytes`). After data, a critic met the
frozen target from the base tree with 12 rows. Each was one generic message
plus a string the request supplied: every request body spelled the value with
a leading `\u00XX` escape, so the raw bytes never held the signature, while
the server's message did (`lessons/round-26-verifier-spotcheck.md:98-116`).

## Two facts the rule rests on

1. **One JSON string value has many byte spellings.** RFC 8259 §7: "Any
   character may be escaped." Any character can be a six-character `\uXXXX`
   sequence (S136). A raw-byte substring test therefore says nothing about
   whether the decoded value holds the signature.
2. **llama-server b11755 puts decoded request values into error text.**
   `server-common.cpp:1375` (S137) throws
   `"response_format type must be one of \"text\" or \"json_object\", but got: " + response_type`,
   where `response_type` is read with `json_value` from the parsed body. The
   message is one fixed frame plus whatever string the caller chose, after
   JSON decoding. One frame of this kind serves any number of "signatures".

## The rule

A counter that credits a live error signature must refuse it when either
holds:

- **Echo.** The signature occurs, case-folded or with all whitespace
  removed, in the request path, in any **JSON-decoded** key or value of the
  request body at any depth, or in either serialisation of the decoded body
  (ASCII-escaped and UTF-8). Raw bytes alone are never the comparison set.
- **Shared frame.** With the signature cut out of the message, the
  remainder (case-folded, not blank) equals the remainder of a row already
  credited. One message frame earns one row, whatever is spliced into it.

The round-27 counter implements both (`count-c1.py` clause (f) via
`request_surfaces`/`json_strings`/`occurs` at lines 343-372 and the check at
line 586; clause (h) `h:same-message-frame` at lines 708-709).

## What this does not establish

- It is a necessary condition, not a sufficient one. Echo through channels
  other than the request body (file or model content read by the server,
  server logs, help text) and transformed echoes (detokenised ids, case or
  schema rewriting) are separate classes; the round-27 counter names them in
  its preregistration (`controls_required`), and their pre-data control
  receipts under amendment A3 were never committed (the attempt-2 control
  seats died with the orchestrator, `.ufo/waves/round-27/w1-controls/`).
- The round-27 measured claim C1 was not run on data, so no count here shows
  that the rule discriminates genuine faults from shortcuts on real rows.
- Other servers and other llama.cpp builds may echo at other sites; S137 is
  scoped to 704366d76.
