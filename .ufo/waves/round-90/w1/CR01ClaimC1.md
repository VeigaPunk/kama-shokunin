# CR01ClaimC1 — attack on C1 (hostile listener answers stay bounded, output unbroken)

## Scope
C1 as frozen in `plans/round-90-claims.md` (counter `tools/round90-hostile-answers.py`, sha256
`345b12b386bfa8258e9cd7f75c8838107da3c809781069e99f3b721bd741dde5` at 6f6d7873, f968fb19 and 2ee0b55).
Read-only on the lane; all probes are `--probe-file` copies in scratch. No tool installed. No POST/load
to 1234; no lane file edited. M probe sha256 `c197912f8b3b5567e3ffd38178cb3a6e87187d7fb13136308c9a461ba8d2ef97`.

## Commands and outputs (true exit codes)
All counters: `python3 tools/round90-hostile-answers.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --rev <R> --work <scratch>/w-<tag> [--probe-file <f>]`, TMPDIR=<scratch>.
- M f968fb19 ×3 (M1/M2/M3): rc 0, `cells=13 mismatches=0 positive_mismatches=0 probe=rev …rev=f968fb19…`.
  sent H1/H2/H3 = 72 / 5,832,776 / 6,094,900 (M1); 131,144 / 7,995,464 / 7,733,300 (M2); 2,621,512 / 7,340,104 / 7,405,620 (M3).
- base 99cdb4d6: rc 1, `mismatches=8 positive_mismatches=0`, sent H1/H2/H3 = 67,108,864 / 28,180,552 / 59,703,348 (H2 truncated by `--max-time 5`, verdict DEAD).
- G1 `g-strip-cap.sh` (base + 1 MiB cap + boundary `tr -d '\000-\037\177'` on C_*): rc 0, `mismatches=0 positive_mismatches=0`, `probe=override probe_sha256=7a5da891…` — **0/0**.
- G2 `m-clean-off.sh` (M minus `clean()`): rc 1, H4 `header_cols=9 empty=2`, H5 `c0=1`, H6 `esc=1`.
- G3 `m-jstr-off.sh` (M minus jstr U+0001–U+001F/DEL loop): rc 0, 0/0.
- G4 `m-maxbody-1048575.sh` (MAX_BODY = P2 body size): rc 0, 0/0.
- G5 `m-rc63-dead.sh` (rc 63 → DEAD instead of FOREIGN_SERVICE/body-too-large): rc 0, 0/0; H1/H2 verdict DEAD.
- G6 `m-noprops.sh` (`router_autoload` returns 1; /props never fetched): rc 0, 0/0; H3 sent=0.
- G7 `g-narrow-strip.sh` (strips only \n, \t, U+0001, ESC, DEL): rc 0, 0/0.
- F2 control rerun: rc 1, `mismatches=9 positive_mismatches=1` (P3 served-id-mismatch).
- `drive_slow.py` (held-out slow-drip 64 MiB close-delimited): base rc 2 `verdict=DEAD reason=timeout sent=5,308,497 h2_pass=1`; M rc 2 `FOREIGN_SERVICE body-too-large sent=4,259,921 h2_pass=1`.
- `drive_cr.py` (held-out id `a\rb`): base table raw_ctl=`0xd`; M table none, JSON `served='good,a\\u000db'`; G7 table raw_ctl=`0xd`.
- Counter bytes identical at 6f6d7873/f968fb19/2ee0b55 (sha above); measured `c1.out` probe sha matches M probe.

## Findings
1. **BLOCKER (counter)** — a materially different probe scores 0/0: G1 = base probe + 1 MiB cap + boundary
   `tr -d` of C_*; it has no `MAX_BODY=4194304`, no rc-63 `FOREIGN_SERVICE body-too-large`, no jstr C0
   escaping, no `served_ids clean()` textualisation, no `strip_ctl` on Content-Type/curl text. Evidence:
   `c1-G1.out` (`cells=13 mismatches=0 positive_mismatches=0`, rc 0). The counter's only provenance gate is
   the printed label (`--probe-file` ⇒ `probe=override`; source `main()` sets `mode="rev"` for any git rev),
   so the same bytes committed at a rev print the predicate line and exit 0. The safety property still holds
   under G1; what is not certified is the claim's named implementation (4 MiB, rc 63, jstr, `\uXXXX` text).
2. **DEFECT (calibration)** — the positive population tops out at exactly the cap boundary: P2 body is
   1,048,575 bytes (`MIB-1`, recomputed from the counter), and G4 with `MAX_BODY=1048575` scores 0/0. Any cap
   in [1,048,575, ~16 MiB] passes; the frozen 4,194,304 is not verified. G1's 1 MiB cap would falsely reject a
   legitimate listing of 1,048,576 bytes (NOT_HTTP, rc 63 path) — a false red no positive cell detects.
   Evidence: `c1-G4.out`, `c1-G1.out` H1/H2 `verdict=NOT_HTTP`.
3. **DEFECT (predicate vs rule, S588)** — H5 rejects RFC 8259-compliant escaping. G2 keeps M's jstr
   `\u0001` escaping but removes `clean()`: JSON parses, rc 0, verdict MODEL_OK, yet `c0=1` because `has_c0`
   runs on the *decoded* document. The rule says ids "lose **or escape**"; the counter permits only loss
   (M textualises to literal `\u0001` text). A maintainer implementing the cited S588 rule fails C1.
   Evidence: `c1-G2.out` H5; counter `has_c0(parse_row(so)[0])`.
4. **DEFECT (unverified rule clause)** — the jstr U+0001–U+001F/DEL loop is never exercised: G3 removes it and
   still scores 0/0. All listener C0 reaches `served_ids clean()` / `strip_ctl` first. Evidence: `c1-G3.out`.
5. **DEFECT (under-specified oversize verdict)** — H1/H2 require only `verdict != MODEL_OK`; G5 (rc 63 → DEAD)
   scores 0/0. The plan's rule says only "never MODEL_OK" (so G5 is plan-compliant), but the wave's C1
   description says FOREIGN_SERVICE `body-too-large` (rc 63); the counter cannot tell the two apart.
   Evidence: `c1-G5.out`.
6. **DEFECT (H3 is sent-only)** — H3 passes if `/props` is never fetched: G6 scores 0/0 with `sent=0`. The
   claim "an oversize /props means not autoload" is unverified; only K2's operator control (harm-M.out:
   `MODEL_OK router-unloaded-autoload`) would catch removing autoload detection. Evidence: `c1-G6.out`.
7. **DEFECT (population narrower than the claimed F4 range)** — the rule claims U+0000–U+001F/U+007F, but the
   cells test only \n+\t (H4), U+0001 (H5), ESC (H6–H8). G7 strips only those five bytes and scores 0/0, while
   a lone CR id still emits a raw 0x0d in table mode (`drive_cr.py`: G7 `raw_ctl=['0xd']`; M none). This is
   exactly SN01 F4's "\r survives into reason/served_model". Other C0, DEL, U+0080–U+009F and U+0001 in a
   status value have no cell. Evidence: `c1-G7.out`, `cr-cell.out`.
8. **DEFECT (sent proxy unsound in both directions)** — (i) `sent` counts bytes handed to the kernel, so a
   4 MiB cap measures 5.8–8.0 MB (M H2/H3, 3 runs; ~2× the cap) and BOUND=16 MiB leaves only ~2× margin;
   (ii) `--max-time 5` truncates the count: against a slow-drip 64 MiB close-delimited answer the **uncapped**
   base probe sent 5,308,497 bytes and returned DEAD timeout, satisfying H2's condition (`h2_pass=1`,
   `slowdrip.out`). Under host load 39 base H2 already sent only 28 MB (1.75× BOUND), so a slower/loaded host
   can turn H2 into a false pass for a probe with no cap. The proxy verifies "not 64 MiB on this host", not
   "bounded at 4 MiB".
9. **NOTE (coverage)** — the counter invokes only `check --port`; `listeners` and `snapshot` modes are not
   exercised (shared `classify`/`jstr` path, but separate table renderers; `persist_clean` already strips
   `[:cntrl:]` at base). F1 (unbounded CPU), F2 (listener-chosen file paths) and F5 (TOCTOU) are not claimed
   by C1 (plan routes only F3/F4) and the r90 diff does not touch `gguf_state`/`file_state`, so they remain
   live. The `probe_short` cap, Content-Type strip and curl-error-text strip are unexercised: G1 omits all
   three and passes. Held-out items (gzip bomb, BOM, DEL/U+0085/U+2028) are by design outside the predicate.
10. **NOTE (predicate reproduces)** — at M the frozen predicate holds 3/3 (0/0, rc 0, probe=rev, same probe
    sha); base reproduces 8/0 rc 1; counter bytes unchanged; K2 at M green (`measured/harm-M.out`: 77/77,
    30/0, 11/0, operator 1234 `MODEL_OK router-unloaded-autoload`). C1's headline is not falsified; the
    defects above are about what the counter certifies.

## Deliverables
`.ufo/waves/round-90/w1/out/CR01ClaimC1/`: `c1-M{1,2,3}.out`, `c1-BASE.out`, `c1-G{1..7}.out`, `c1-F2.out`,
`slowdrip.out`, `cr-cell.out`; forgery probes `g-strip-cap.sh`, `g-narrow-strip.sh`, `m-clean-off.sh`,
`m-jstr-off.sh`, `m-maxbody-1048575.sh`, `m-rc63-dead.sh`, `m-noprops.sh` with `*.diff`; drivers
`drive_slow.py`, `drive_cr.py`, `slowdrip.py`.

VERDICT: partial — the frozen predicate reproduces at M (3/3, 0/0, rc 0; counter bytes unchanged; K2 green), but the counter is forgeable at 0/0 by a 1 MiB-cap/boundary-strip probe, rejects RFC-compliant escaping, leaves the jstr/rc-63/4 MiB clauses unverified, and its H2 `sent<=16 MiB` proxy is satisfied by `--max-time` alone under a slow answer.
