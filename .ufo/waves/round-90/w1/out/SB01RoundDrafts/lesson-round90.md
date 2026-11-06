# Round 90 — lesson (kama)

Base `99cdb4d6270455494dd27901efe84a0f3b342062`; freeze `6f6d7873dac936ba407398ce81b464d77d0fcf32`
(`plans/round-90-claims.md`); C1 measured commit `f968fb19bb2a0c2afe271bfe606f11b52d10823f`; C2 measured
commit `2ee0b55f4d3fd0cb3157d26b03280c1d21e27b2d`. Closure history read before declaring:
`corpus/lessons/round-89-verifier-spotcheck.md` (r89 **admitted**; routed R1–R5) and
`round-88-verifier-spotcheck.md` (r88 rejected-honest-stop: a frozen expectation written from lane prose).
Both claims grade by observable output of real runs, never by canned expectations copied from lane text.

## Claims

- **C1 operability (sourced S587/S588):** a listener's answer is written by whatever holds the port. The base
  probe accepted a 64 MiB `/v1/models` answer as `MODEL_OK` (H1/H2) and a 64 MiB `/props` answer as autoload
  (H3), widened its table to 9 columns on an id carrying a tab (H4), left `--json` unparsed on a U+0001 id and
  on an ESC in the `Server:` header or router status (H5/H7/H8), and printed raw ESC in table mode (H6–H8).
  Counter `tools/round90-hostile-answers.py` (13 cells: H1–H8 hostile, P1–P5 positive; no canned expectation —
  each pass condition is in the counter docstring). Base `mismatches=8 positive_mismatches=0`; forgeries F1
  (blanket refusal) `6/5`, F2 (ASCII-only ids) `9/1`, F3 (64 KiB cap) `7/1`; M `0/0`
  (`.ufo/waves/round-90/measured/c1.out`).
- **C2 depth (lowest axis, 7):** SKILL §"Probe reason codes", 24 rows: the 23 reason codes the base probe can
  print (`C_REASON=`/`RT_REASON=`, base lines 770–911; `dns-failure` excluded because `fetch` always targets
  the literal 127.0.0.1) plus `body-too-large`. Counter `tools/round90-reason-rows.py`; receipt producer
  `tools/round90-reason-capture.py` (one stub cell per reason, every receipt line naming the probe's sha256).
  Base `documented=0 missing=23`; forgery battery `rows=5 bound=2 unbound=3 duplicates=1`, stale
  `bound=0 receipt=stale`, prose-only `documented=23 bound=0 unbound=23` (`controls/c2-forgeries.out`); M2
  `documented=23 rows=24 bound=24 unbound=0 missing=0 duplicates=0 additional=1` (`measured/c2.out:26`).

## Gate

| Candidate | Decision | URL / access date | Located quote (≤25 words) and location | Reason |
|---|---|---|---|---|
| S587 curl `docs/cmdline-opts/max-filesize.md` @ `curl-8_23_0` | **admit** (A, docs, mined) | https://raw.githubusercontent.com/curl/curl/curl-8_23_0/docs/cmdline-opts/max-filesize.md — 2026-11-06, sha256 `4bbc00ec37d8cab75479a7803a80552019e0bca6d83f68ecddf9feb893ea038f` | "Starting with curl 8.4.0, this option aborts the transfer if it reaches the threshold during transfer." (lines 34-35) | The doc at the exact tag of the host's curl (8.23.0, `curl --version`), so the abort-at-threshold behaviour the C1 cap relies on is the installed one; the doc's pre-8.4.0 caveat for unknown-length bodies is why the probe also re-checks the written size. |
| S588 RFC 8259 §7 | **admit** (A, spec, mined) | https://www.rfc-editor.org/rfc/rfc8259.txt — 2026-11-06, sha256 `61a5378f4255c720beb2a4b4a63b29540147c140f36988bf086291989b4cd2d7` | "except for the characters that MUST be escaped: quotation mark, reverse solidus, and the control characters (U+0000 through U+001F)." (lines 429-431) | The normative rule the old `jstr` broke (it escaped `\ " \t \n \r` and left the other control characters raw); the probe's own validator (`emit_json`) is a conforming parser and refused the output (cell H5 at base). |
| `corpus/knowledge/probe-answer-bounds.md` | **admit** | cites S587, S588 + own receipts | — | Own-corpus sweep first (KQ143): `git grep -n -i -E 'max-filesize\|control char\|U\+001F' 99cdb4d6 -- corpus/knowledge SKILL.md` → one hit, `corpus/knowledge/snapshot-history.md:51` ("Control characters are stripped." — the `snapshot` persistence path only), and no hit for a size cap. That rule and the r89 seat findings (SN01 F3/F4) are cited as prior art; the new ground is the live `check`/`listeners` output and the transfer cap. |
| REJECT candidate from SC01 | **pending** | — | — | L1 fills from the SC01 seat report (not landed at draft time). |

`status` / `recheck` / `used-by` changes on existing rows: none.

## Mistakes

**M1 — a hostile-answer cell the do-nothing control already passed.** Class: non-discriminating control cell
in a frozen counter. Evidence: the first H4 cell checked only `no stdout line starts with FORGED-ROW`; `check`
joins served ids with commas (`tools/kama-probe.sh:901`, `tr '\n' ','`), so the newline in the forged id never
starts a line, while the tabs still widen the table (base `header_cols=9 empty_header_cols=2`,
`controls/c1-base.out` H4). Captured-by: running the base control before freeze
(`plans/round-90-claims.md:5-6`: every control named was executed before the file was committed). Fix: H4 also
requires every header cell non-empty (`tools/round90-hostile-answers.py:24-27`); base `ok=0`, M `ok=1
header_cols=7 empty_header_cols=0` (`measured/c1.out` H4). Shown able to fail: the base H4 row.

**M2 — a forgery battery whose printed expectation miscounted its own duplicate.** Class: control-label
arithmetic written from intent, not from the counter's rule. Evidence: `controls/c2-forgeries.out:1` records
the first draft label `bound=1 unbound=4`, corrected before freeze to `bound=2 unbound=3` (T1 and its duplicate
T4 both bind; the duplicate fails through `duplicates=1`); the battery's actual summary is `rows=5 bound=2
unbound=3 duplicates=1` (line 7). Captured-by: the battery's own pre-freeze run. Fix: the corrected label and
the counter's duplicate rule (a duplicate row binds like its original and is counted in `duplicates`);
`controls/c2-forgeries.sh` is the frozen battery. Shown able to fail: the battery exits 1 on the fixture
(`controls/c2-forgeries.out:8`).

## Corrections (appended)

- `measured/c2.out` was untracked at draft time; the C2 after-number is quoted from its line 26 and was
  independently re-derived read-only at M2 by this draft's author. The L1 commits the receipt.
- `corpus/SOURCES.md` S587/S588 rows, `corpus/knowledge/probe-answer-bounds.md` and the `corpus/README.md`
  round-90 coverage/frontier block were in the working tree, not at `2ee0b55f`, when this draft was written.
- The Gate row's own-corpus sweep is written inside a table, so its `\|` is literal in the cell (the r89 RV02
  DEFECT repeated); the command as run is `git grep -n -i -E 'max-filesize|control char|U\+001F' 99cdb4d6 --
  corpus/knowledge SKILL.md`.

## Dispositions of the round-89 closure (R1–R5)

| Routed defect | Round-90 disposition | Evidence |
|---|---|---|
| R1 `round75-instruments` red (`bad_rows=19`) | open, not claimed; the register-only fix still waits for the L0 ruling | `plans/round-90-claims.md` §carried; `corpus/lessons/round-89-verifier-spotcheck.md` R1 |
| R2 `bc` missing in r89 `harm-final.out` | wave item (EX02HarmLatency); no committed outcome at draft time | `plans/round-90-claims.md` §carried |
| R3 no pinned latency/step budget | wave item (EX02HarmLatency); C1 adds no budget — the cap bounds bytes, not CPU | `plans/round-90-claims.md` §carried; `corpus/knowledge/probe-answer-bounds.md` §Limits |
| R4 SN01 F3/F4 (unbounded body, unsanitised ids) | C1 claim; verified at M | `measured/c1.out`; `controls/c1-base.out` |
| R5 held-out LIMIT cells / FIFO INDETERMINATE / SC01 alias `MODEL_MISMATCH` | not claimed; still frontier | `plans/round-90-claims.md` §carried; `corpus/README.md` round-90 frontier |

Round-90 wave-1 seat dispositions are appended by the L1 from `.ufo/waves/round-90/w1/`; no seat report had
landed when this draft was written.
