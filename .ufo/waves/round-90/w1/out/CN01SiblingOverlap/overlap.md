# Sibling-overlap scan — kama round 90, wave 1 (CN01SiblingOverlap)

Read-only. Lane repo untouched; no sibling file edited. Siblings scanned: every
`/home/vgpnk/Projects/shokunin/*-shokunin` except `kama-shokunin`. Scope searched per seat:
each lane's `tools/`, `SKILL.md`, `corpus/` (`.ufo/` excluded — wave scratch is not a lane claim).
kama side read at `2ee0b55f4d3fd0cb3157d26b03280c1d21e27b2d` (master), probe sha256
`c197912f8b3b5567e3ffd38178cb3a6e87187d7fb13136308c9a461ba8d2ef97`.

Topics: (a) response-size caps on HTTP probes, (b) control-character / terminal-escape
sanitization of probe or tool output, (c) JSON escaping of untrusted strings, (d) reason-code
tables for health probes.

## Hits

| Lane | Path:line | What it covers | Classification |
|---|---|---|---|
| chousa | `tools/quote-reopen.py:54,28` | `MAX_BODY = 8 MiB`; docstring: "a cap of 8 MiB on **both the wire bytes and the inflated bytes**" | reusable rule |
| chousa | `tools/quote-reopen.py:313-336` | `_inflate_stream` inflates chunk-wise with `max_length = MAX_BODY + 1 - len(out)` and returns `over_cap`; gzip/deflate/zlib, unknown encoding → over-cap | reusable rule |
| chousa | `tools/quote-reopen.py:420-424` | wire over-cap and inflate over-cap both return `body over 8 MiB`, no parse, no verdict | corroboration |
| chousa | `SKILL.md:96` | `QUOTE_REOPEN_FETCH_BOUND_MATCH=27/27`, "before on the round-29 tool: 78/106, 12/27", "loopback harness only, no network" | corroboration |
| chousa | `corpus/evidence/round30/claims.md:148,162-164` | the 27-item fetch-bound counter's receipt label and its base reading `12/27` at the previous tool | corroboration |
| kotodama | `tools/reopen-row.py:139-142` | `MAX_BODY_BYTES = 4 MiB`, `GZIP_LIMIT = 64 MiB`, `READ_CHUNK = 64 KiB` | reusable rule |
| kotodama | `tools/reopen-row.py:541-567` | `_read_body` reads `read1` (not `read`) against a monotonic deadline; comment: "a buffered read blocks until `want` bytes or EOF, so a dripping body would outlive the budget (rev-hold-lift MEDIUM-1)" | reusable rule |
| kotodama | `tools/reopen-row.py:400-410` | `gunzip(raw, limit=GZIP_LIMIT)` decompresses with `limit + 1` and reports `cut` | reusable rule |
| kotodama | `tools/reopen-row.py:18-19,713-714` | `TRUNCATED` is a first-class verdict ("body was cut at the 4 MiB cap"), ranked like `ABSENT` (`:163`) | reusable rule |
| kotodama | `tools/check-advance-evidence.py:295-325` | refuses, by name, inside a verdict token: NBSP, VT, FF, LS/PS/FS, NEL, ANSI, any `Cc`, combining marks, any `Zs` (`VERDICT-NBSP/-VT/-FF/-LINESEP/-NEL/-ANSI/-CTRL/-COMBINE/-SEPARATOR`) | reusable rule |
| kotodama | `tools/check-advance-evidence.py:1972` | selftest table `NB1/VT1/FF1/LS1/NEL1/ANSI1/PS1/FS1-3` — the exact U+00A0/U+000B/U+000C/U+2028/U+0085/U+001B/U+2029/U+001C-U+001E classes | corroboration |
| souji | `tools/cand-b1-quarantine.sh:196-204` | `has_control_char` refuses C0/C1/DEL in a path or receipt field **before any parsing**: "a TAB in a path shifts every following field" (the engine record is TAB-separated) | reusable rule |
| souji | `tools/cand-b1-quarantine.sh:157-162` | `sanitize_field` replaces TAB/NL/CR with a space on emit (after the refusal gate) | corroboration |
| souji | `tools/cand-b1-quarantine.sh:454-456,694,717` | the gate is applied at the target name, the strict two-column schema and the receipt path | corroboration |
| tameshi | `tools/design-blob-audit.py:179-184` | `_line_safe` refuses C0/DEL in a verdict-bearing receipt path: "the path is interpolated verbatim, so an embedded newline could forge a verdict line (criterion-84 class)" | corroboration |
| kumitate | `corpus/knowledge/remaining-scripts-census.md:660` | fleet `scripts/ufo-mission-activity.mjs` `sanitizeDisplayText` strips C0/C1, **ANSI/OSC, bidi controls and tmux format tokens**, bounds by code points, `INVALID_ACTIVITY` for a non-string | reusable rule (fleet display surface) |
| kumitate | `corpus/knowledge/route-probe-cluster.md:225` | `FAILURE_CLASSES` (11) includes `output_overflow` — an over-cap answer is its own class, not `timeout` | reusable rule |
| kumitate | `corpus/knowledge/route-probe-cluster.md:522,563` | `spawnCollect` caps child output at `maxBuffer = 1 MiB` with separate `stdoutOverflow`/`stderrOverflow` flags; `tests/route-probes.test.js:1045` is a `spawn_failure / output_overflow` test section | corroboration |
| kumitate | `corpus/knowledge/route-probe-cluster.md:230-236` | route-health reason vocabulary: 4 statuses, live reasons (`expired`, `malformed_record`, `unknown_served`, …), rollup reasons; `:231` names `invalid_validity_window` as **unreachable through the validated caller** | reusable rule (population provenance) |
| kagi | `corpus/release-clock.py:32,768-775,810` | `MAX_BODY_BYTES = 8 MiB`, `read(MAX_BODY_BYTES + 1)`, "feed body is invalid or too large" | corroboration |
| kagi | `corpus/release-clock.py:1583-1596` | selftest shrinks `MAX_BODY_BYTES` to 8 and asserts `error == "response too large"` and `read_limit == 9` — the over-cap branch is proven reachable | reusable rule |
| mori | `tools/mori-ua-variance.py:97,125,143` | `MAX_BODY = 8 MiB`, `read(MAX_BODY + 1)`, over-cap → `"unavailable"` (same outcome as a transport failure) | NOTE (contrast) |
| kake | `SKILL.md:777-816` | "Citing-set reason-code registry": a `Reason code \| Fixture case(s) naming it` table, plus 12 codes the gate can emit that **no committed fixture names** — "uncovered behaviour, not regression coverage" | reusable rule |
| kake | `corpus/knowledge/stored-response-reuse.md:112` | a header value containing CR, LF or NUL → `invalid_input: control character in header value: X-N` | corroboration |
| kake | `corpus/knowledge/static-canonical-preflight.md:121` | raw C1 controls (U+0080–U+009F) in a URL are rejected, not percent-escaped | corroboration |
| kasegi | `corpus/knowledge/osv-post-v1-query-contract.md:53-55` | a **server's** documented 32 MiB HTTP/1.1 response-size limit (consumer-side fact) | NOTE (not probe-side) |

## Not found

- No sibling uses curl `--max-filesize`: `grep -rIn 'max-filesize' <all lanes> --exclude-dir=.ufo --exclude-dir=kama-shokunin` → no match. kama's C1 is the fleet's only curl-level answer cap; every sibling caps inside its own reader (Python `read(cap+1)`, Node `maxBuffer`).
- No sibling holds a hostile-answer stub-listener counter for a **model-serving** probe. The nearest is chousa's round-30 fetch-bound counter (27 loopback cells, base `12/27` → `27/27`), which grades its own quote verifier.
- No sibling holds a reason-code table for a local-model health probe. kumitate's is route health for omp routes; kake's is a citing-set gate.

## What this means for kama (one line each)

1. **A cap is one of three bounds.** chousa and kotodama both bound the *decoded* bytes separately from the wire bytes; kama has no decode path (`--compressed` is absent from `tools/kama-probe.sh:340,375,761`), so `MAX_BODY` is currently a true wire cap — and stays true only while `--compressed` stays absent.
2. **A drip is bounded by the clock, not the cap.** kotodama's `read1` note is the general form; kama's form is curl `--max-time` (default 5 s, `tools/kama-probe.sh:340`), which is why the probe needs no reader-level deadline.
3. **An over-cap answer must be its own verdict.** kumitate (`output_overflow`), kotodama (`TRUNCATED`), chousa (`body over 8 MiB`) and kagi (`response too large`) all keep it distinct; mori folds it into `unavailable`. kama's `body-too-large` (rc 63, `tools/kama-probe.sh:846`) is on the distinct side.
4. **Escape values, refuse keys.** kama escapes C0/DEL/C1 as `\uXXXX` in ids (identity preserved, cells P3/P4); souji and tameshi refuse control bytes in fields that are parsed as keys. Both are correct for their own surface.
5. **The class is a declared set.** kama's frozen class is C0+DEL+C1; kotodama's verdict-token class adds LS/PS/NEL/NBSP/combining/Zs and kumitate's display class adds bidi and OSC. A held-out cell outside kama's set is a scope finding, not a C1 falsification.
6. **Population provenance is a claim.** kama's C2 population is the 23 `C_REASON=`/`RT_REASON=` print sites at the freeze (plus the post-C1 `body-too-large` row); kumitate's is a declared vocabulary with one explicitly unreachable member; kake's is a fixture-bound table with 12 named-uncovered codes. None is wrong; none is the other's evidence.
