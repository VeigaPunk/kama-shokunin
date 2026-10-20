VERDICT: confirm — all four stale-statement classes exist in tracked lane docs; 19 exact sites named, and the `::1` recognition claim is disproved by this host's own `/proc/net/tcp6` bytes.

# Scout — stale statements that need appended corrections after C1

Read-only seat. Question: every lane statement that (A) says a run observing no
loading 503 fails / exits 1, (B) presents receipt schema **v2** as current,
(C) says `::1` listeners are recognised, or (D) cites `docs.python.org/3/`.

## Method

- Targeted greps over the named surfaces only (`SKILL.md`, `corpus/README.md`,
  `corpus/knowledge/*.md`, `SCORECARD.md`, `PROVINCE.md`, `tools/`,
  `tests/`), plus `AGENTS.md`, `LOG.md`, `README.md`, `SHONEN.md`, `MINT.md`,
  `corpus/QUALITY.md`, `corpus/lessons/round-17*.md` to catch duplicates.
- One recursive sweep with `--exclude-dir=.ufo --exclude-dir=.git
  --exclude-dir=.jj` for `kama-llamacpp-live/v[123]` and for
  `docs.python.org/3<not-a-dot>`.
- Read-only `/proc/net/tcp6` on this host (no port bound, no server started,
  no process killed) to test the `::1` recognition claim.
- No gate, harness, measurement, or live tool was run. No lane write except
  this report. No `jj`. No installs.

## A. "No loading 503 observed ⇒ FAIL / exit 1"

| # | Site | Quote (≤25 words) | Status |
|---|---|---|---|
| A1 | `SKILL.md:573` | "`loading_envelope_graded` (503s observed and every stored body exact; none observed fails)" | stale after C1 |
| A2 | `SKILL.md:573` | "0 all 11 checks pass, 1 a check failed, 2 setup error or internal fault…, 3 model digest mismatch" | exit map has no not-evaluated class |
| A3 | `corpus/knowledge/llamacpp-loading-lifecycle.md:198-199` | "`loading_envelope_graded` fails when no 503 was observed or when any stored 503 body is not exact" | stale after C1 |
| A4 | `corpus/README.md:243` | "and fails a run that observed none" | stale after C1 |
| A5 | `corpus/knowledge/llamacpp-loading-lifecycle.md:225-228` | "1 of 60 real runs at 32x `stress-ng` load observed no 503 and failed `loading_envelope_graded`" | historical observation, but reads as current contract |
| A6 | `corpus/lessons/round-17.md:251-253` | "the honest next move is to classify zero observation as could-not-evaluate (exit 2)" | already names the fix; needs a closure note, not a correction |
| A7 | `tools/kama-llamacpp-live.py:140-141` | "Grades EVERY distinct captured 503 body; no 503 observed -> fail" | C1-owned `documented_by`; must become null/not-evaluated |
| A8 | `tests/llamacpp-live/check-receipt.py:909-913` | "a run with nothing to grade cannot pass it" (`bad("no loading_503 body stored, nothing graded")`) | C1-owned gate predicate; must become exit 3 |
| A9 | `tools/kama-llamacpp-live.py:19-24` | "1 at least one check failed (server ran; receipt written)" / "2 setup error (…receipt write failure)" | exit map has no zero-observation class |
| A10 | `tests/llamacpp-live/check-receipt.py:43-45` | "Exit: 0 receipt valid, 1 receipt invalid …, 2 receipt unreadable / not JSON." | exit 3 NOT-EVALUATED absent |
| A11 | `SKILL.md:591-593` | "exit 1 can also come from a model rehash `OSError`, and a `BaseException` … can escape without a receipt" | false-by-design after C1 (R4/R6) |

Observed predicates behind A1/A7/A8 (current code): `tools/kama-llamacpp-live.py:1343-1346`
computes `receipt.get('loading_observed') is True and loading_envelopes_all(bodies) is True`;
a falsey `loading_observed` therefore yields `passed: false` → exit 1. The gate at
`tests/llamacpp-live/check-receipt.py:912-914` calls `bad(...)` when `want_lef is None`,
so a stored "nothing graded" run is INVALID, never NOT-EVALUATED.

[INFERENCE] A11's rehash clause is the one site whose *future* class is not fixed by the
declared v3 contract: an `OSError` during the post-teardown rehash currently makes
`model_unchanged` false (exit 1); whether C1 reclassifies it as could-not-evaluate (exit 2)
or keeps it as a failed check should be decided in C1 and the SKILL note rewritten to match.
Do not silently "correct" it to exit 2 without that decision.

## B. Receipt schema presented as v2 (current)

| # | Site | Quote (≤25 words) | Status |
|---|---|---|---|
| B1 | `SKILL.md:564-565` | "the tool now emits `kama-llamacpp-live/v2` with 11 checks" | current-contract claim |
| B2 | `SKILL.md:573` | row name "Live llama.cpp lifecycle v2"; "0 all 11 checks pass" | current-contract claim |
| B3 | `SKILL.md:574` | "v1 receipts validate exactly as in round 16; v2 re-derives every check from stored evidence" | gate row is v1+v2 only |
| B4 | `PROVINCE.md:73-75` | "The tool now emits `kama-llamacpp-live/v2`: … every loading 503 graded … loopback-only listener ownership" | current-contract claim |
| B5 | `corpus/README.md:238` | "three v2 live runs (S046)" | historical evidence line; see note |
| B6 | `corpus/README.md:241-243` | "receipt v2 grades every observed loading 503 body (42–45 per run)" | current-contract claim |
| B7 | `corpus/knowledge/llamacpp-loading-lifecycle.md:194` | "**The v1 limits above are superseded for receipt v2** (`kama-llamacpp-live/v2`)" | current-contract claim |
| B8 | `SCORECARD.md:666` | "receipt v2 checks fail on the misbehaviour they name" | current-contract claim |
| B9 | `SCORECARD.md:694` | "`live-llamacpp-lifecycle`, whose evidence pointer is now receipt v2" | current-contract claim |
| B10 | `tools/kama-llamacpp-live.py:21` | "Receipt schema: ``kama-llamacpp-live/v2``." | C1-owned docstring |
| B11 | `tools/kama-llamacpp-live.py:50` | `SCHEMA = 'kama-llamacpp-live/v2'` | C1-owned constant |
| B12 | `tools/kama-llamacpp-live.py:947` | "kama-llamacpp-live/v2 receipt." (argparse description) | C1-owned text |
| B13 | `tests/llamacpp-live/check-receipt.py:2` | "Independent validator for kama-llamacpp-live/v1 and /v2 receipts." | C1-owned docstring |
| B14 | `tests/llamacpp-live/check-receipt.py:58-59` | `RECEIPT_SCHEMA = …/v1`; `RECEIPT_SCHEMA_V2 = …/v2` | no v3 constant |
| B15 | `tests/llamacpp-live/check-receipt.py:1360` | "Validate a kama-llamacpp-live/v1 or /v2 receipt." | C1-owned description |

Do **not** rewrite these as history: they are current-contract statements and need an
appended correction (or, for B10–B15, an in-band edit by C1).

## C. "`::1` / IPv4-mapped listeners are recognised"

| # | Site | Quote (≤25 words) | Status |
|---|---|---|---|
| C1 | `tools/kama-llamacpp-live.py:313-317` | "127/8 is little-endian xxxxx7F? …; ::1 ends 00000001; an IPv4-mapped 127/8 is … 0000000000000000FFFF00" | **disproved** (below) |
| C2 | `PROVINCE.md:75` | "and loopback-only listener ownership" | claim broader than code |
| C3 | `SKILL.md:573` | "`teardown_port_closed` (child ownership proven and port refused)" | scope unspecified; imply all loopback |
| C4 | `corpus/knowledge/llamacpp-loading-lifecycle.md:197` | "`teardown_port_closed` fails unless child ownership was proven" | same |

Observed on this host (2026-10-20, read-only `cat /proc/net/tcp6`):

- `::1` is printed as `00000000000000000000000001000000` (32 chars, four 32-bit
  host-order words). The code's test `addr_hex.endswith('00000001')` is **False**
  on that string; the real tail is `01000000`.
- A live `::1` LISTEN row exists in the same file:
  `00000000000000000000000001000000:0277 … 0A` — `0x277` = 631 (CUPS). So this is a
  real, current listener shape, not a hypothetical.
- The mapped branch compares `addr_hex[:24]` (24 chars) with
  `'0000000000000000FFFF00'`, which is **22 chars** — never equal, so a mapped
  `127/8` can never match even after the `::1` fix. The 24-char prefix of the
  expected mapped form `0000000000000000FFFF00000100007F` is
  `0000000000000000FFFF0000`.

Consequence chain (code read, not executed): `_listen_inodes` returns an empty set for
such a listener → `port_owned_by` returns `None` (`tools/kama-llamacpp-live.py:349-360`)
→ `verify_live` maps `None` to `unproven` and raises
`SetupError('…:port-listener-ownership-unproven')` **before** the ready captures
(`:634-638`). A healthy server bound only to `::ffff:127.0.0.1` would therefore be a
false failure at the liveness gate, not merely a teardown-check failure.

Coverage gap makes C1–C4 untested: `grep -rn -E 'AF_INET6|INET6|::ffff' tools tests`
returns **no matches**. `tests/llamacpp-live/controls.py:300-327` has K0–K8 only; none
binds an AF_INET6 socket. The item's required "good server via `::ffff:127.0.0.1` must
be ACCEPTED" control does not exist yet.

## D. `docs.python.org/3/` citations

| # | Site | Quote | Status |
|---|---|---|---|
| D1 | `tools/kama-llamacpp-live.py:60-61` | `POPEN_RETURNCODE_DOC = 'https://docs.python.org/3/library/subprocess.html#subprocess.Popen.returncode'` | stale; must be `/3.14/` |
| D2 | round-17 receipts (`documented_by` of `teardown_graceful`) | same URL serialized (e.g. `.ufo/waves/round-17/live/receipt-1.json:174`) | historical/frozen; do not edit |

The lane's own rule already exists: `corpus/lessons/round-17-verifier-spotcheck.md:179`
rejects "Cite the `/3/` Python docs page"; `corpus/lessons/round-17.md:66` admits the
`/3.14/` form; `corpus/SOURCES.md:56` (S044) notes `/3/` serves 3.15. D1 contradicts all
three and is the only tracked code citation still on `/3/`.

## Correctly historical — do not "correct"

These read as dated records and should keep their bytes:

- `corpus/SOURCES.md:53` (S041, `kama-llamacpp-live/v1`) and `:58` (S046,
  `kama-llamacpp-live/v2`) — append-only registry rows. A v3 run needs a **new** row
  (S048+) or a knowledge note, per KQ22.
- `corpus/knowledge/llamacpp-loading-lifecycle.md:101`, `:135-137`, `:147`
  (v1 receipt, "passes all 10 checks", "`loading_envelope_exact` is recorded, not graded").
- `corpus/knowledge/llamacpp-loading-lifecycle.md:189` ("11/11 checks" for the three
  round-17 runs) and `corpus/lessons/round-17.md:172`.
- `SCORECARD.md:611` ("receipt 10/10 checks, `VALID`" — round-16 row).
- `SHONEN.md:8` ("Round 17 adds graded v2 receipts … 11/11") and `LOG.md:1013`
  ("`tools/kama-llamacpp-live.py` receipt v2") — round-17 log/assertion history.
- `.ufo/waves/round-17/**` receipts, gates and advice — frozen.

## Suggested appended corrections (paste-ready, after C1 lands)

Append, do not rewrite, in each file; keep the historical sentence and add the pointer.

**`SKILL.md`** (after the round-17 falsify-corrections paragraph, `:597`):

> Round-18 correction (appended; receipt `kama-llamacpp-live/v3`). The v2 rows above are
> historical: the tool now emits v3 and the gate accepts v1, v2 and v3 under
> `--require-schema`. Two v2 statements are superseded: "none observed fails" — a run that
> observes no `/v1/models` 503 now grades `loading_envelope_graded` `passed: null`
> (`observed.not_evaluated_reason` `"no-loading-503-observed"`) and exits 2; the gate reports
> it as NOT-EVALUATED (exit 3), never INVALID. "A `BaseException` … can escape without a
> receipt" — v3 catches `BaseException` in teardown/finally, still writes the receipt and
> exits 2. `::1` and `::ffff:127.0.0.0/104` listeners are recognised as loopback ownership;
> a good server bound only to a mapped address is accepted. The Python citation is
> `https://docs.python.org/3.14/…` (host Python 3.14.8), not `/3/`.

**`PROVINCE.md`** (`:75`, after "loopback-only listener ownership"):

> Round-18 correction (appended): the tool now emits `kama-llamacpp-live/v3`; listener
> ownership recognises `127.0.0.0/8`, `::1` and `::ffff:127.0.0.0/104` as read from
> `/proc/net/tcp{,6}`. Zero observed loading 503 is a not-evaluated outcome (exit 2), not a
> failed check.

**`corpus/README.md`** (`:243`, after the frontier paragraph):

> Round-18 correction (appended): "fails a run that observed none" describes receipt v2.
> Under v3 a run that observes no loading 503 is NOT-EVALUATED (tool exit 2, gate exit 3)
> with `observed.not_evaluated_reason` `"no-loading-503-observed"`; grading still requires
> every observed 503 to be the exact envelope. The current receipt schema is
> `kama-llamacpp-live/v3`; S046 remains the v2 evidence row.

**`corpus/knowledge/llamacpp-loading-lifecycle.md`** (after the round-17 falsify correction):

> Round-18 correction (appended): the sentence "`loading_envelope_graded` fails when no 503
> was observed" holds for receipt v2 only. Under v3 that check is `passed: null` /
> `evaluated: false` with `observed.not_evaluated_reason`
> `"no-loading-503-observed"`, and the tool exits 2 (gate exit 3). The falsify observation
> at the end of this section ("1 of 60 … failed") stays as a v2 record; under v3 the same run
> would be not-evaluated. Also appended: `::1` and `::ffff:127.0.0.0/104` listeners count as
> child ownership, so `teardown_port_closed` no longer fails a mapped-address good server.

**`SCORECARD.md`** (only if a round-18 section is added; do not edit the round-17 rows):
state that the v2 rows at `:666` and `:694` are the round-17 evidence pointer and that the
capability's pointer moves to the round-18 v3 receipt.

**`corpus/lessons/round-17.md:251-253`** — leave the debt text; a round-18 line should record
that the debt was paid (zero observation → exit 2), with the control that proves it.

**`corpus/SOURCES.md`** — new rows only (S048+): the kernel `/proc/net/tcp6` format source,
RFC 4291 IPv4-mapped, Python 3.14 `BaseException` docs, test-runner "nothing observed"
exit conventions, and an S048+ own-work row for the v3 run. Never edit S041/S046.

## Answer-key for C1's own docstrings (in-band, not appended)

C1 must land these in its files or the corrections above will contradict the code:
`tools/kama-llamacpp-live.py` module docstring `:19-28` (add exit 2 could-not-evaluate and
exit 3; state v3; drop the blanket "any exception … still writes a receipt" unless
`BaseException` is truly covered), `:50` `SCHEMA`, `:140-141` `documented_by`, `:313-317`
listener docstring; `tests/llamacpp-live/check-receipt.py` `:2`, `:43-45`, `:909-914`,
`:58-59`, `:1360`; `tests/llamacpp-live/controls.py` `:7` ("K0 … MUST be accepted; K1–K8
each corrupt exactly one behaviour"), `:55` ("Every serving fake answers >=3 loading 503s")
— v3 needs the zero-loading good control that is expected NOT-EVALUATED, so the binary
accept/reject framing is incomplete.

Adjacent defect found in the same docstring, not in the four classes:
`tools/kama-llamacpp-live.py:19-24` lists exits 0/1/2 but `main()` returns **3** on model
digest mismatch (`:1023`, and `--model-sha256` help says "mismatch -> exit 3"). Any v3
docstring rewrite must include it.

## Limitations and unknowns

- All quotes are from the tracked working tree at the round-18 start state; no round-18 C1
  delivery exists yet (`ls .ufo/waves/round-18/build/out` is empty), so "stale" means
  "stale relative to the declared v3 contract", not relative to landed code.
- The `::1` finding is **observed** (`/proc/net/tcp6` bytes, `len()` of the literals).
  The mapped-address display form is [INFERENCE] from the same host-order word layout plus
  the assignment's stated form; no mapped listener existed on this host to observe directly.
- I did not run the tool or any control, so the false-failure consequence is a code-read
  inference, not a reproduction. C1's new AF_INET6 control is the reproduction.
- No claim made here about `_listen_inodes` on other kernels; this is this host's Linux
  7.2.11 encoding as read at 2026-10-20.
- Not checked: `registry/` prose, `corpus/knowledge/listener-census.md` (it documents `ss`
  census output, not `/proc/net/tcp6` parsing) and `MINT.md`; greps matched none of the four
  classes there.

Installs/upgrades: none (no package, binary or tool was installed or updated).
