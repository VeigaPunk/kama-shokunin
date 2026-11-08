# RV02WordingC2 — adversarial wording review of C2

Seat: RV02WordingC2 (godcode). Frozen claims: plans/round-100-claims.md §C2;
SKILL.md §Round 100 `/props` status rule (lines 1837-1860); decision row
line 1773; corpus/knowledge/router-props-autoload.md §Round 100 (lines 51-70).
Code: tools/kama-probe.sh router_autoload() lines 898-928 at 2e27e6f1
(M); counter tools/round100-props-status.py lines 67-83 (CELLS).
Receipts: measured/c2.out, controls/c2-base.out, c2-candidate.out,
c2-mutant-blanket.out, c2-regression-r99.out.
Own evidence: .ufo/waves/round-100/w1/out/RV02WordingC2/harness.out (19 raw-
socket cases), harness2.out (7 shim/plain-call cases); drivers harness.py,
harness2.py in the same dir. Stub = raw-socket HTTP on 127.0.0.1 ephemeral
port, /v1/models 200 with one unloaded not-failed entry whose args[0] is the
72-byte GGUF fixture file, /props answer per case; probe run as
`bash probe-tip.sh check --port <p> --expect fixture-model --id r100 --json`
(mirroring the counter's verdict_reason). Command:
`python3 /fast/scratch/hyaku/kama-r100/RV02WordingC2/harness.py`
(exit after 19 cases; results in harness.out).

## 1. Every curl outcome for the /props fetch: graded vs code-line-only

The new line (kama-probe.sh:901-904):

    pcode=$(curl -sS --noproxy '*' --connect-timeout "$CONNECT_TIMEOUT"
      --max-time "$TIMEOUT" --max-filesize "$MAX_BODY" -o "$pbody"
      -w '%{http_code}' "http://127.0.0.1:$port/props" 2>/dev/null) || return 2
    [ "$pcode" = 200 ] || return 2

`%{http_code}` is the *final* status of the exchange (post-redirect, post-
interim). Without `-L`, curl makes exactly one request and never follows a
3xx. A curl *error* (nonzero exit) leaves `%{http_code}` as 000/empty and
takes `|| return 2` before the `[ = 200 ]` test. The nine cells
(`tools/round100-props-status.py:73-83`) grade only complete, cleanly-framed,
Content-Length responses with statuses 401/403/500/503/202/302/200. My raw
harness results (reason `router-autoload-unread` / exit 2 in every non-200
case, `router-unloaded-autoload` / exit 0 where marked):

| Outcome | Cell? | Observed probe answer | Cover |
|---|---|---|---|
| 401/403/500/503, router-shaped body | S1/S2/S3/S4 | `MODEL_UNLOADED/router-autoload-unread/2` | GRADED (c2.out:10-16) |
| 202, router-shaped body | S5 | same | GRADED |
| 302 + Location, body not followed | S6 | same | GRADED |
| 200 off/on, router body | P1/P2 | `router-unloaded` / `MODEL_OK router-unloaded-autoload` | GRADED |
| 200, non-router doc (llama.cpp 401 doc shape) | S7 (at 401) | `router-autoload-unread/2` | GRADED |
| Other 2xx (201, 204) w/ router body | none | `router-autoload-unread/2` (X-201, X-204) | line-only: `[ = 200 ]` rejects |
| Other 3xx (301, 304) w/ router body | none | `router-autoload-unread/2` (X-301, X-304) | line-only |
| Other 4xx/5xx (400, 404, 418, 501, 502) | none | `router-autoload-unread/2` (X-400, X-404, X-418, X-501, X-502) | line-only |
| Off-body under non-200 (500 + `false`) | none (cells use on-body S2) | `router-autoload-unread/2` (X-500-router-off) | line-only, but symmetric — same `[ = 200 ]` gate rejects before body is read |
| Interim 100 then final 200 | none | `MODEL_OK/router-unloaded-autoload/0` (X-100-then-200-on) | line-only; `%{http_code}` is the final status, so "final HTTP 200" in the wording is exact |
| Interim 100 then silence | none | `router-autoload-unread/2` (X-100-then-hang) | line-only (rc 28) |
| Chunked 200 | none (cells always Content-Length) | `MODEL_OK/router-unloaded-autoload/0` (X-200-chunked-on) | line-only; status gate passes, body parsed |
| Close-delimited 200 (no length) | none | `MODEL_OK/.../0` (X-200-close-delimited-on) | line-only |
| Chunked oversize (>4 MiB) | none here | `router-autoload-unread/2` (X-200-chunked-oversize) | Line-only here; covered by r99 U2 (c2-regression-r99.out:10) at the wc-c re-check. curl rc 63 also lands in `|| return 2` — see below. |
| Transfer failure: close with no bytes (rc 52) | none | `router-autoload-unread/2` (X-empty-reply) | transport, covered by `|| return 2` |
| HTTP/0.9-style: body bytes, no status line | none | `router-autoload-unread/2` (X-http09-body) | transport: curl rejects (rc 56/1-class) -> `|| return 2` |
| Malformed status line | none | `router-autoload-unread/2` (X-malformed-statusline) | transport |
| Partial transfer (CL=100, 40 bytes, RST) | none | `router-autoload-unread/2` (X-partial-transfer) | transport (rc 18) |
| curl exit 28/63/52/56/7 via shim (prints 000, exits rc) | none | `router-autoload-unread/2` for rc 7, 28, 52, 56, 63 (harness2.out) | ALL via `|| return 2`; the `[ = 200 ]` test never sees them |

Disclosed-limit check: claims §C2 limit (d) says "The cells cover the nine
statuses/bodies listed; other non-200 statuses follow the same
`[ "$pcode" = 200 ]` line but are not each graded." That is literally true —
and my probes confirm the line behaves uniformly for every other status. The
wording that needs care is the *claim headline* (see §2): "the probe reads
the router's bare `/props` body only on a final HTTP 200" is a universal
sentence; the counter grades nine (status, body) pairs. Limit (d) already
discloses exactly this gap, so this is a disclosed narrowing, not a hidden
one. The `|| return 2` transport arm (rc 7/18/28/52/56/63, malformed,
partial, HTTP/0.9) is *not* graded on the /props path by either round's
counter — but every rc lands in the same `return 2` as a non-200, and the
round-99 cells U1 (slow -> rc 28) and U2 (oversize -> rc 63/wc-c) exercised
that arm on the same function, still green after the change
(c2-regression-r99.out:9-16, `cells=8 mismatches=0`).

## 2. Does the SKILL wording claim anything the counter does not grade?

SKILL.md:1845-1846: "So `router_autoload()` reads the bare `/props` body only
when curl's final `%{http_code}` is exactly `200`; any other status is
unread, whatever the body says." Code-true for every status (verified above,
20 raw-shim cases incl. 201/204/301/304/400/404/418/501/502 — all unread),
but counter-graded for exactly six non-200 statuses. The adjacent sentence
(SKILL.md:1854-1857) bounds the counter claim precisely: "Nine live cells
on loopback stubs grade (verdict, reason, exit): six router-shaped non-200
answers (401 off, 500 on, 503 off, 403 on, 202 on, 302 on)..., the exact
llama.cpp 401 document..., and two 200 positive controls..." — no overclaim
there. The `...(401, 403, 500, 503, 202, 302, ...)` table row
(SKILL.md:1852) with `...` is the same universal sentence; the `...` is doing
un-disclosed work unless read with §C2 limit (d) and SKILL.md:1858-1860
"Limits: stub-fed, not a live router; a 200 answer from a non-router
intermediary is still read as the router's document; /v1/models statuses
are graded by the existing classify() rules". Same status for the plan
headline and claims.json C2 name ("the probe reads the router's bare /props
body only on a final HTTP 200: six router-shaped non-200 answers ... on nine
live stub cells" — the colon clause enumerates the grade). Verdict: the
universal sentences are code-true and the grade scope is stated in the same
paragraphs; the only true soft spots are:

  (a) SKILL.md:1852 row's `...` — symbols beyond the six graded statuses
      are asserted by pattern, not by cell. This is the disclosed limit (d)
      shape, but the `...` itself is not footnoted at that row. Cosmetic,
      not a hidden narrowing, because the very next paragraph enumerates
      exactly what was graded.
  (b) SKILL.md:1859 limit "a 200 answer from a non-router intermediary is
      still read" — this IS an explicit disclosure of the residual false-
      green, present and correctly bounded.
  (c) The knowledge doc §Round 100 (corpus/knowledge/router-props-autoload.md:55)
      says round-99 "graded a router-shaped body under 500/403/202/302 as
      autoload-on" — accurate per c2-base.out:2,4,5,6.

No sentence claims: a live router/proxy was tested (explicitly disclaimed,
plan limit (a)); /v1/models is covered (explicitly disclaimed, plan limit
(c)); a slow 200 is covered (explicitly disclaimed, plan limit (e)).

## 3. `pcode=$(curl …) || return 2` under `set -euo pipefail` — every caller

The script runs `set -euo pipefail` (kama-probe.sh:93). In
`router_autoload()`, the assignment `pcode=$(curl ...) || return 2` is an
`||`-list statement: a nonzero curl exit cannot trip `set -e`, and the
function returns 2 cleanly. Empty `pcode` cannot occur on the success path
(curl with `-w '%{http_code}'` always prints digits on exit 0), so line 904
`[ "$pcode" = 200 ] || return 2` is also a safe comparison under `set -u`
(`pcode` is always bound by the assignment or the function has returned).

Call graph (single caller of router_autoload): router_refine() lines 961-966:

    if router_autoload "$port"; then ra=0; else ra=$?; fi

The call sits inside an `if`-condition, so `set -e` is already
context-suppressed regardless of the function's return code — the round-99
amendment-1 comment at lines 962-964 records exactly this. Then
`router_refine` itself is called only from classify() line 1100
(`router_refine "$FBODY" "$expected" "$port"` — a bare statement, not in a
condition). router_refine's *implicit return status* is the status of its
last executed command — the final `if/elif` chain at lines 978-990. When
`ra=2` (any unread incl. new non-200), the `down` branch (line 983-989)
sets RT_VERDICT/RT_REASON and the branch's last assignment returns 0. When
autoload is `on`, line 979 sets and `return 0` explicitly. When the entry
is `sleeping`, `return 0` at 960. Trailing case: if none of loading/down/
unloadable fire, the `if` returns 0 (bash rule: `if` with no executed
branch and no else returns 0). Every path returns 0, so classify()'s bare
call at line 1100 cannot abort. My probes confirm: under shim rc 28 on
/props, `listeners` and `consumers` both exited 0 with
`MODEL_UNLOADED/router-autoload-unread` (harness2.out:6-7), and `check`
exited 2 (drift) as intended. The round-99 plain-call control
(.ufo/waves/round-99/controls/c3-plaincall.out, cited in the knowledge
doc verified-at line) covers the off/on sides; the unread side now also
verified live.

One latent asymmetry worth naming (not a defect): `[ "$pcode" = 200 ]`
is a *string* comparison and 200-for-the-price-of-one `|| return 2` means
any curl *warning class* that makes curl exit nonzero while still writing
a 200 body (e.g. a write error on -o after a complete transfer — disk full
on $TMP_ROOT) reads unread rather than `on`. That is fail-closed and
matches the claimed rule; no wording claims otherwise.

## 4. Base behaviour: "four false MODEL_OK cells at base" — exact match?

Plan §C2 says: base "a router-shaped body under 401/503 read as explicit
off and under 500/403/202/302 as autoload-on — a false MODEL_OK cold
start, exit 0". SKILL.md:1854-1856 says "that the round-99 probe read as
explicit states (four as a false MODEL_OK cold start)". Verified cell by
cell from controls/c2-base.out (tip pass at base rev):

- S2-500-router-on: `MODEL_OK/router-unloaded-autoload/0` (c2-base.out:11) — false MODEL_OK ✓
- S4-403-router-on: `MODEL_OK/router-unloaded-autoload/0` (c2-base.out:13) — false MODEL_OK ✓
- S5-202-router-on: `MODEL_OK/router-unloaded-autoload/0` (c2-base.out:14) — false MODEL_OK ✓
- S6-302-router-on: `MODEL_OK/router-unloaded-autoload/0` (c2-base.out:15) — false MODEL_OK ✓
- S1-401-router-off: `MODEL_UNLOADED/router-unloaded/2` (c2-base.out:10) — explicit off ✓
- S3-503-router-off: `MODEL_UNLOADED/router-unloaded/2` (c2-base.out:12) — explicit off ✓
- S7-401-llamacpp: `router-autoload-unread/2` (c2-base.out:16), P1/P2 stable ✓

Exactly four false MODEL_OK (S2, S4, S5, S6); exactly two wrong-off (S1,
S3). `mismatches=6 base_mismatches=6 flips=0 stable=9 met=False ... exit=1`
(c2-base.out:25-26) matches the plan's "Base: mismatches=6, exit 1"
(plan:92-93) and the summary. The blanket mutant
(c2-mutant-blanket.out:21, `mismatches=2`) and the r99 regression
(c2-regression-r99.out:17, `cells=8 mismatches=0`) match their cited
numbers. The measured receipt (measured/c2.out:19-20,
`cells=9 mismatches=0 base_mismatches=6 flips=6 stable=3 met=True rev=
2e27e6f1... exit=0`) matches the predicate. Nothing here is off by a
number.

## 5. Required narrowing sentences

No `falsifies-*` defect found. The code is exactly as worded; the cells
grade a disclosed subset; every receipt number matches its prose. If the
pre-file gate wants zero soft `...`s, the honest narrowings are already in
the text (plan §C2 limits (a)-(e); SKILL.md:1858-1860) and only need to be
*pointed at* from the two universal sentences:

  N1. SKILL.md:1845-1846 ("only when curl's final %{http_code} is exactly
      200; any other status is unread, whatever the body says") — re-read
      with the cells sentence at SKILL.md:1854-1857 and limit (d): the
      six-status enumeration, not the `...`, is what the counter proves;
      all other statuses follow the same single `[ "$pcode" = 200 ]` line,
      additionally verified now by out/RV02WordingC2/harness.out (201, 204,
      301, 304, 400, 404, 418, 501, 502 → unread; 100→200 → read).

  N2. claims.json C2 `v name` / plan headline "only on a final HTTP 200" —
      same scope reading: code-true universal, nine-cell grade; the plan's
      own limit (d) is the narrowing sentence and it is sufficient.

  N3. knowledge doc verified-at header (router-props-autoload.md:2) still
      cites only the round-99 eight cells and the round-98 19-cell
      regression; the §Round 100 body (lines 69-70) carries the round-100
      receipts, so the header is stale-as-a-header but not false. A
      one-line header refresh would make the two sections symmetric. Cosmetic.

NOT wordings that need narrowing (checked, accurate): SkILL.md:1773
decision row "a final HTTP status other than 200" (the word "final" is
exactly the %{http_code} semantics — shim case X-100-then-200-on confirms
an interim 100 followed by 200 reads the body); plan §C2 "S7 ... (stable)"
(measured/c2.out:7,16 — base already unread because no router role);
knowledge doc base/tip table rows (all 9 rows match c2.out:1-18);
"four as a false MODEL_OK" (verified above); "exits 0" claims (c2.out:20).

VERDICT C2 neutral Counter is code-true and cell-accurate; every stated receipt number matches, the uncovered outcome classes are covered by the disclosed limit (d) plus the same failing line (verified with 26 extra stub cases), and no wording sentence claims more than the nine-cell grade plus that disclosed line.
