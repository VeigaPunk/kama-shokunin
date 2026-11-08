source: S587 (curl `docs/cmdline-opts/max-filesize.md` @ tag `curl-8_23_0`, the host's curl 8.23.0, lines 20-35), S588 (RFC 8259 §7 Strings, lines 424-431 of the rfc-editor text), S589 (RFC 8259 §8.1, lines 483-486), S590 (curl `lib/sendf.c` @ `curl-8_23_0`, `cw_download_write`, line 291); rejected S591 (the pre-8.4.0 doc); own-work receipts `.ufo/waves/round-90/controls/c1-base.out`, `.ufo/waves/round-90/measured/c1.out`, `.ufo/waves/round-90/measured/reason-cells.jsonl`. Prior art held before round 90: `corpus/knowledge/snapshot-history.md:51` (control characters stripped on the `snapshot` persistence path only), r89 wave seat SN01 findings F3/F4 (`.ufo/waves/round-89/w1/SN01ProbeSafety.md`), the probe's `jstr` (escaped `\ " \t \n \r` only) and `router_entries` id filter (`\t\r\n` only).
verified-at: 2026-11-06 — lane-owned stub listeners on free loopback ports, probe at `f968fb19bb2a0c2afe271bfe606f11b52d10823f` (sha256 `c197912f8b3b5567e3ffd38178cb3a6e87187d7fb13136308c9a461ba8d2ef97`), host curl 8.23.0; the operator router 127.0.0.1:1234 (GET only) still grades `MODEL_OK router-unloaded-autoload`.
recheck: on-release — on a curl upgrade re-read S587 for the abort semantics and re-run `python3 tools/round90-hostile-answers.py --repo . --rev master --work <scratch>` (must print `cells=13 mismatches=0 positive_mismatches=0 probe=rev`).

# Probe answers from an untrusted listener: size and control characters

## What was already held (not new in round 90)

The probe asks every loopback listener `GET /v1/models` (and, for a router, `GET /props`), so the answer is
written by whatever holds the port. Round 89's seat SN01 measured two consequences on the probe then in
use: a 1.5 GB streamed answer wrote 52 MiB into TMPDIR in five seconds and a 200 MB answer cost 598 MB RSS
(F3), and an id carrying a newline and tabs forged table columns while a U+0001 in an id made `--json` exit 1
with no output (F4).

## What round 90 adds

1. **A size cap is a transfer rule, not a parse rule.** `curl --max-filesize` refuses a body whose declared
   length is over the cap before it starts and, since curl 8.4.0, aborts a body of unknown length when it
   reaches the cap, exiting 63 (S587 lines 20-22 and 34-35; the in-transfer abort is `cw_download_write`
   returning `CURLE_FILESIZE_EXCEEDED`, S590 line 291). Before 8.4.0 the option had no effect on an
   unknown-length body (S587 lines 30-32), so the probe re-checks the written size as well; that re-check
   keeps the verdict right on an old curl (no `MODEL_OK` for an oversize answer) but cannot stop the bytes
   already transferred, so the wire bound below holds only on curl 8.4.0 or later (wave-1 MT01 D1, an
   inert-cap shim: 64 MiB transferred, verdict still `FOREIGN_SERVICE`). Measured: a 64 MiB
   close-delimited `/v1/models` answer now stops after 6.4-7.7 MB on the wire (kernel buffers included)
   instead of 64 MiB (`measured/c1.out` vs `controls/c1-base.out`, cell H2).
2. **An oversize answer gets no model verdict.** Nothing was parsed, so the probe prints `FOREIGN_SERVICE
   body-too-large`; before, a 64 MiB answer that listed the expected id graded `MODEL_OK` (cells H1, H2). An
   oversize `/props` is read as "router does not autoload", the conservative direction (an `unloaded` entry
   then grades `MODEL_UNLOADED router-unloaded`, cell H3).
3. **The cap must not refuse a real server's list.** 4 MiB is about 60 000 entries of `{"id":"m-00001",
   "object":"model"}`; a legitimate 1 MiB list still grades `MODEL_OK matched` (cell P2), and a 64 KiB cap
   fails that cell (`controls/c1-f3-tiny-cap.out`).
4. **JSON strings must escape every control character, not only the common five.** RFC 8259 §7 makes
   U+0000-U+001F MUST-escape characters (S588 lines 428-431); the old `jstr` escaped `\t \n \r` and left the
   rest raw, which made the probe's own JSON validator reject its output (cell H5 at base). DEL is escaped
   too, which §7 permits but does not require ("Any character may be escaped"). Separately, JSON text must be
   UTF-8 (S589), so a non-UTF-8 header byte is dropped from evidence rather than passed to `jstr`
   (wave-1 RV01 DEFECT-2, repaired at `a09effae`).
5. **Table output has no escaping, so listener text loses control bytes before it gets there.** Ids are
   printed with C0, DEL and C1 controls as `\uXXXX` text (an id stays recognisable and can never add a line,
   a column or a terminal escape); router ids with control characters are skipped and status values become
   `?`; the `Server:` and `Content-Type` headers and curl's error text drop control bytes. Non-ASCII text that
   is not a control character is kept verbatim (cell P3; an ASCII-only filter fails it,
   `controls/c1-f2-over-sanitizer.out`).

## Decision rows

| Answer | Probe verdict / reason | Why |
|---|---|---|
| `/v1/models` body over 4 MiB (declared or streamed) | `FOREIGN_SERVICE` / `body-too-large` | transfer aborted at the cap (curl rc 63); nothing parsed |
| `/props` body over 4 MiB | router treated as not autoloading | conservative: an `unloaded` entry is not promised a cold start |
| id with a control character | id shown with `\uXXXX` in `served_model`; matching unchanged for clean ids | output shape cannot be forged |
| router status value with a control character | value read as `?` → `MODEL_UNLOADED router-?` when nothing else matches | an unknown status is never ready |
| `Server:` / `Content-Type` with control bytes | bytes dropped in evidence | header text is listener-chosen |

## Limits (not covered by round 90)

The CPU cost of router file checks on crafted GGUF headers (r89 SN01 F1) and the listener's choice of which
local files the probe opens (F2) are not changed here. `listeners` and `snapshot` modes share `classify` and
`jstr`, so they inherit the fix, but the frozen cells run `check` only, always with python3 present: the
python-free fallback (grep ids) drops control bytes since the round-90 repair but still compares
JSON-escaped text, so a non-ASCII or quote-bearing id grades `MODEL_MISMATCH` without python3 (wave-1
EX03 F2, present at base).

## Round 91 correction (2026-11-06) — verified-at re-pointed

The `verified-at:` line above names the round-90 C1 measured probe `f968fb19…` (sha256 `c197912f…`). That
probe carried held-out harm the round-90 wave found (r90 lesson M4/M5); the shipped probe is M′
`a09effae1f3780797a4d706f469a1d2b33361aa4` (sha256 `b71c309ad849c25db9c33a2e1bde4c691c766d68073ed0378b5fc96f1e4b48d7`),
re-measured by the round-90 closure (`round90-hostile-answers.py` cells=13 mismatches=0 at M′ and tip).
Read the entry as verified at M′. The original line is kept (append-only); round-90 closure routed defect R2.

## Round 91 addition — the time bound (S592)

The round-90 cap bounds bytes, not time: a 4 MiB answer of 200 000 ids took 207 s (r89 SN01) and one 3.9 MB
id froze the probe in bash pattern expansion. Two causes, both measured on the base probe
(`.ufo/waves/round-91/controls/c1-base.out`): a `$(normalize_id …)` fork per served id (twice per router
entry), and `${C_SERVED%,}` on a 1.6 MB list, which alone took 38 s in a UTF-8 locale. The probe now applies
`normalize_id`'s rule to every id in one awk pass and joins the served list with `paste -sd,`; the
200 000-id, 80 000-entry router, 3.9 MB-id and 3.8 MB-slash cells finish in about 1-2 s
(`.ufo/waves/round-91/measured/c1.out`). The expected id reaches awk through `ENVIRON`, because a `-v`
assignment is read as an awk STRING token and its backslashes would be processed (S592, POSIX awk lines
107-108); ids compare as strings (`x ""`), because an ENVIRON element may be a numeric string (lines
796-797) and `1.0` would otherwise equal `1`.

## Superseded reading of the oversize `/props` row (appended round 100; the lines above are not rewritten)

Item 2's last sentence and the table row "`/props` body over 4 MiB | router treated as not autoloading" describe the
probe at `f968fb19` (this file's `verified-at`). Since round 99 an oversize `/props` reads `MODEL_UNLOADED` /
`router-autoload-unread` (an unread flag, not an autoload-off answer; `corpus/knowledge/router-props-autoload.md`, cell
U2, `.ufo/waves/round-99/measured/c3.out`), and since round 100 any `/props` answer whose final HTTP status is not 200
is read the same way (`SKILL.md` §Round 100 `/props` status rule; `.ufo/waves/round-100/measured/c2.out`). The verdict
(`MODEL_UNLOADED`, drift) is unchanged; only the reason differs.
