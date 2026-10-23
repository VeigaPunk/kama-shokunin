# Review: RepairEntryRevision (attacks: repairs 5 & 6, `corpus/knowledge/echo-discriminating-counters.md`)

Verdict: **holds** — every changed sentence in the diff `4179301f..e49b4cf7` for
`corpus/knowledge/echo-discriminating-counters.md` is true against its cited
files/evidence. No wrong, overstated or harmful change found. One additional
change beyond the named repairs 5/6 exists in the same diff; it is also true
(repair-2 disposition).

## Diff (3 hunks, 5+/2-)

```
git -C kama-shokunin diff 4179301f e49b4cf7 -- corpus/knowledge/echo-discriminating-counters.md
```
1. Line 3 `recheck:` line rewritten (repair 6).
2. Lines 132-134: boundary-probe scope sentence appended (repair 5).
3. Line 161: "The round-27 counter is retired, and no signature counter has
   run KQ37 on data." appended (repair-2 disposition; the one "anything else"
   hunk). Single commit `e49b4cf` touches the file in this range.

## Check 1 — recheck line (repair 6): HOLDS

Grounding: `tools/echo-recheck.py` (sha256 `ced0ee8976ca0c03e31d17d72d99c7df5b7a6fa315b19f33d873144ca9df2d28`
= `tool_sha256` in every receipt; file is new since base). Each claim verified
against code and receipts:

- "starts the pinned b11755 on a free port in 48231-48233 or --port" —
  `PORT_CANDIDATES=(48231,48232,48233)` + `--port` (lines 73, 361-378);
  PINS checked via `check_pins()` (280-289). Receipts: run1 auto 48231,
  run2 explicit 48232.
- "replays the six live-probe requests byte-for-byte" — ORDER of 6;
  `REQ[name]` sha compared to baseline `request_sha256` before server start
  (351-357).
- "prints 'echo-recheck same 6/6' exit 0" — line 473-474; run1/run2:
  `same 6`, `differing []`, `exit 0`.
- "'echo-recheck drift <ids>' exit 1" — 475-476; falsifier-drift.json:
  `differing ["req1-plain"]`, `exit 1` (baseline = mutated scratch copy).
- "'echo-recheck cannot-evaluate <reason>' exit 2" — 477-478; also used for
  existing `--out` (443-444, 466-468).
- "proves the port closed" — `terminate` + `port_closed_proof` (405-417);
  run1/falsifier-drift `shutdown.port_closed = {closed: true, connect_exit: 111,
  ss_ltnp_listeners: []}`.
- "refuses an existing --out so committed receipts are never overwritten" —
  `lexists` check + `open(out,"x")`; `refuse-exists.json` still contains only
  its sentinel `{"sentinel":"do not overwrite"}` (not overwritten).
- Registered in SKILL.md gate/probe registry row "Echo recheck" (SKILL.md:1222).

Minor note (not a defect): refusal also triggers on the derived `.server.log`
existence (line 337-338) — broader than stated, harmless. run1/run2 share
`observed_at_utc 08:37:21Z` (ran concurrently, separate ports); consistent.

## Check 2 — boundary scope sentence (repair 5): HOLDS

`residual/out/CriticBoundaryLegProbe/boundary-leg.receipt.json:10-14` states
verbatim: predicate `exact decoded-body-string occurrence of length >= 4`;
semantics `JSON-decoded body keys and string values at every depth; length >= 4;
no path/headers/argv`; comparisons `exact case-sensitive strings; no extra
whitespace or case normalization`. Harness implements exactly that
(`harness.py:73-92`: only decoded body dict keys/string values with `len >= 4`,
exact `str.find` spans; no path/headers/argv; `deny_live` audit hook). The
entry sentence matches the citation word-for-word. QUALITY.md round-28
qualification item 3 states the same scope.

## Check 3 — "round-27 counter is retired..." hunk: HOLDS (and is the "anything else")

QUALITY.md round-28 qualification item 4: "The round-27 signature-counter
attempt is retired without data: round-27 C1 was withdrawn before data, no data
seat was dispatched, A3 tip records registered 0 counted 0 target 15 met False."
SKILL.md registry row 1219 marks the counter "(retired) ... do not use ... last
run exit 0, registered 0 counted 0 target 15 met False ... none (retired)".
"no signature counter has run KQ37 on data": round-27 never ran on data;
round-26's counter predates KQ37 and failed its echo requirement (routed defect
2, 12/12 flagged); qualification 4 requires an F3 leg + named-class control
receipts before data for any future signature counter, and explicitly states
round-28 C1 is not a signature counter. Sentence is accurate under the only
coherent reading (no counter qualifying under KQ37 has been exercised on data).

## Residual risk / verification gaps

- Exit codes themselves (stdout/returncode) are not persisted as transcripts;
  they are reconstructed from `doc["exit"]` and the code paths. Consistent
  across receipts, code, and lesson claims.
- `prefix-drift-run1/run2.json` were not inspected (not cited by any changed
  sentence; redundant drift evidence).
- No tool installs or updates were performed (nothing needed). No server
  started; no lane/flleet writes beyond this report.
