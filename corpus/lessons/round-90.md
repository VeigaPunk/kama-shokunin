# Round 90 — hostile listener answers bounded; the probe's reason codes as a bound table

L1 `KamaR90`. Base `99cdb4d6270455494dd27901efe84a0f3b342062`; freeze `6f6d7873dac936ba407398ce81b464d77d0fcf32`;
C1 measured `f968fb19bb2a0c2afe271bfe606f11b52d10823f`; C2 measured `2ee0b55f4d3fd0cb3157d26b03280c1d21e27b2d`.
Plan: `plans/round-90-claims.md`. Previous closure: `round-89-verifier-spotcheck.md` (admitted).

## Gate

| Candidate | Decision | URL / access date | Located quote (≤25 words) and location | Reason |
|---|---|---|---|---|
| S587 curl `docs/cmdline-opts/max-filesize.md` @ `curl-8_23_0` | **admit** (A, docs, mined) | https://raw.githubusercontent.com/curl/curl/curl-8_23_0/docs/cmdline-opts/max-filesize.md — 2026-11-06, sha256 `4bbc00ec37d8cab75479a7803a80552019e0bca6d83f68ecddf9feb893ea038f` | "Starting with curl 8.4.0, this option aborts the transfer if it reaches the threshold during transfer." (lines 34-35) | The doc at the exact tag of the host's curl (8.23.0, `curl --version`), so the abort-at-threshold behaviour the C1 cap relies on is the installed one; lines 30-32 (no effect before 8.4.0 for unknown sizes) are why the probe also re-checks the written size. |
| S588 RFC 8259 §7 | **admit** (A, spec, mined) | https://www.rfc-editor.org/rfc/rfc8259.txt — 2026-11-06, sha256 `61a5378f4255c720beb2a4b4a63b29540147c140f36988bf086291989b4cd2d7` | "except for the characters that MUST be escaped: quotation mark, reverse solidus, and the control characters (U+0000 through U+001F)." (lines 429-431) | The normative rule the old `jstr` broke (it escaped three of the 32 control characters); the probe's own validator (`emit_json`) is a conforming parser and refused the output (cell H5 at base). |
| `corpus/knowledge/probe-answer-bounds.md` | **admit** | cites S587, S588 + own receipts | — | Own-corpus sweep first (KQ143): `git grep -n -i -E 'max-filesize|control char|U\+001F' 99cdb4d6 -- corpus/knowledge SKILL.md` → one hit, `corpus/knowledge/snapshot-history.md:51` ("Control characters are stripped." — the `snapshot` persistence path only, `tools/kama-probe.sh` `tr -d '[:cntrl:]'` before `latest.tsv`), and no hit for a size cap. Both that rule and the r89 seat findings (SN01 F3/F4) are cited as prior art in the entry; the new ground is the live `check`/`listeners` output and the transfer cap. |

| S589 RFC 8259 §8.1 | **admit** (A, spec, mined) | https://www.rfc-editor.org/rfc/rfc8259.txt — 2026-11-06, same sha256 as S588 | "JSON text exchanged between systems that are not part of a closed ecosystem MUST be encoded using UTF-8 [RFC3629]." (lines 485-486) | Found by wave seat SC01, re-opened by the L1: the rule the round-90 M probe broke when a non-UTF-8 `Server:` byte reached `jstr` (RV01 DEFECT-2); cited by the entry for the 0x80-0xFF header drop. |
| S590 curl `lib/sendf.c` @ `curl-8_23_0` | **admit** (A, code, mined) | https://raw.githubusercontent.com/curl/curl/curl-8_23_0/lib/sendf.c — 2026-11-06, sha256 `deb44efc2947f106138d42946330144e2b6d51f07d7dc57c0cd5d640ca8bfb51` | `return CURLE_FILESIZE_EXCEEDED;` (line 291) | SC01 lead, re-opened by the L1: the code behind S587's in-transfer abort in the installed release. |
| S591 curl `max-filesize.d` @ `curl-8_3_0` | **reject** (C) | https://raw.githubusercontent.com/curl/curl/curl-8_3_0/docs/cmdline-opts/max-filesize.d — 2026-11-06, sha256 `c9e9489b4be81f634fa9af856d0e60287511262a2adab0fefe0591181b418a2b` | "for such files this option has no effect even if the file transfer ends up being larger than this given limit." (lines 22-23) | Describes curl before 8.4.0, the opposite of the host's 8.23.0 for unknown-length bodies; kept only as the reason the probe re-checks the written size. Flip: the lane must support a curl older than 8.4.0. |
| SC01 proposals not appended (RFC 8259 §6 ABNF, curl `lib/http.c`, `curl.h`, 8.4.0 RELEASE-NOTES, RFC 8259 errata page, floating curl.se manpage) | **not appended** | `.ufo/waves/round-90/w1/out/SC01SourceCheck/SOURCES-candidates.md` | — | No admitted entry cites them (CORPUS rule 4). SC01's errata finding (erratum 7673 to add U+007F and C1 to §7's MUST set, recorded Rejected) is noted in the entry's wording: DEL escaping is permitted, not required. |

`status` / `recheck` / `used-by` changes on existing rows: none.

## Mistakes

**M1 — a frozen-counter cell that the do-nothing control already passed.** Class: non-discriminating cell in a
counter draft. Evidence: the first H4 cell (`no stdout line starts with FORGED-ROW`) scored `ok=1` on the base
probe — `check` joins served ids with commas, so a newline in an id never starts a line, while the tabs still
shift the table's columns (header widened to 9 cells, 2 empty). Captured-by: §9 claim sizing ("build the
cheapest control that skips the claimed work, score it with the frozen counter") — it fired because the base
control ran before freeze. Fix: H4 now also requires every header cell to be non-empty (no row carried more
fields than the header names); base `ok=0 header_cols=9 empty_header_cols=2` (`controls/c1-base.out`), M
`ok=1 header_cols=7` (`measured/c1.out`). Shown able to fail: the base row in `controls/c1-base.out`.

**M2 — a counter instrument that was itself broken, caught only by its positive cells.** Class: stub/fixture
fault mistaken for a probe verdict. Evidence: the first base run of `tools/round90-hostile-answers.py` (L1
scratch, pre-freeze) printed `NOT_HTTP no-http-response` for all 13 cells: the stub wrote its status line
through `send_response_only` into a header buffer it never flushed, so the probe received headers without a
status line. Hostile cells H1-H8 "passed" (`verdict != MODEL_OK`, nothing sent); only the five positive cells
went red (`positive_mismatches=5`). Captured-by: the positive cells (KQ144's discipline: every branch also
has a cell where the probe must say yes). Fix: the stub writes `HTTP/1.0 <code> OK` itself; the frozen base
control then shows `positive_mismatches=0` and real hostile mismatches (`controls/c1-base.out`). Shown able to
fail: the blanket-refusal forgery F1 reproduces the same shape (`controls/c1-f1-blanket-refusal.out`:
`mismatches=6 positive_mismatches=5`).

**M3 — a control expectation miscounted before the run.** Class: control label written from intent, not from
the counter's rule. Evidence: `controls/c2-forgeries.sh` first printed `expect … bound=1 unbound=4`; the counter
binds the duplicate row like its original and fails it through `duplicates=1` (`bound=2 unbound=3`). Captured-by:
none (the expectation was mine and unreviewed). Fix: label corrected before freeze, the correction itself
recorded in the label and in the plan, so the receipt shows both values.

**M4 — a sanitizer that dropped what it could not print changed the verdict.** Class: sanitize-by-dropping on a
parsed input. Evidence: at M `f968fb19` `router_entries` skipped every router entry whose id held a control
character; with one entry `{"id":"bad\u001bid","status":{"value":"loading"}}` and `--expect '*'` the router
refinement saw no status and the probe printed `MODEL_OK expected-wildcard`, where base printed
`MODEL_LOADING router-loading` (wave-1 RV01 BLOCKER-1; L1 re-run
`.ufo/waves/round-90/repair/rv01-matrix-base-M-Mprime.out`, rows `router-ctlid-loading`, `router-ctlid-unl`).
Captured-by: the plan's held-out rule ("a held-out cell where base is right and M wrong is reported as harm")
— it fired through a wave reviewer, not through a frozen cell; no QUALITY criterion. Fix: the id is kept and
escaped like `served_ids` does (`a09effae`); KQ145. Shown able to fail: the M column of that matrix.

**M5 — a header filter that let non-UTF-8 bytes through, and a cap branch placed before the auth branch.**
Class: new branch ordered without checking the verdicts it shadows. Evidence: RV01 DEFECT-2 (`Server:
llama.cpp\xff\xfe` made M's `--json` exit 1, base exit 0) and DEFECT-3 (a 401 with a 5 MiB body graded
`FOREIGN_SERVICE body-too-large` at M, `UNAUTHORIZED_SERVICE http-401` at base); same matrix, rows
`badutf8server`, `big401`. Captured-by: the held-out rule again; none in QUALITY. Fix (`a09effae`):
`strip_ctl` drops bytes 0x80–0xFF from header evidence; exit 63 with 401/403 keeps the auth verdict. Shown able
to fail: the M column of those rows.

## Dispositions of the round-89 closure (R1–R5)

- **R1** `round75-instruments` `bad_rows=19`: open; the L0 question stays unanswered; no claim depends on the arm.
- **R2** r89 `harm-final.out` timing column lost to `bc`: wave seat EX02HarmLatency.
- **R3** latency budget: wave seat EX02HarmLatency.
- **R4** SN01 F3/F4: C1 (this round).
- **R5** held-out LIMIT cells and alias pins: not worked; carried to §Planned (round 91).
