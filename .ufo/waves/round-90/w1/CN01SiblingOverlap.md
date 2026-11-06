# CN01SiblingOverlap — kama round 90, wave 1

## Scope

Read-only sibling-overlap scan of every `/home/vgpnk/Projects/shokunin/*-shokunin` except
`kama-shokunin` (22 lanes), over each lane's `tools/`, `SKILL.md` and `corpus/` (`.ufo/` wave scratch
excluded — it is not a lane claim). Four topics: (a) response-size caps on HTTP probes, (b) control-
character/terminal-escape sanitization of probe or tool output, (c) JSON escaping of untrusted
strings, (d) reason-code tables for health probes. Classification vocabulary per seat: contested
scope / corroboration / reusable rule. No sibling gate was executed; every sibling statement below is
a file read, not a green/red claim. No lane repo was edited; no tool installed; no endpoint, listener
or network fetch was made.

kama side read at `2ee0b55f4d3fd0cb3157d26b03280c1d21e27b2d`; `tools/kama-probe.sh` sha256
`c197912f8b3b5567e3ffd38178cb3a6e87187d7fb13136308c9a461ba8d2ef97` (= the C1 measured M).

## Commands and outputs (true exit codes)

1. `ls -d /home/vgpnk/Projects/shokunin/*-shokunin` → 22 paths, rc 0.
2. `grep -rIn --include='*.py' --include='*.sh' --include='*.mjs' --include='*.js' --include='SKILL.md' 'max-filesize' . --exclude-dir=.git --exclude-dir=.ufo --exclude-dir=kama-shokunin` → 0 lines, **rc 1** (no sibling uses curl `--max-filesize`).
3. `grep -rIn … -E 'max-filesize|MAX_BODY|max_body|body.?cap|response.?size|body-too-large' <lane>/tools <lane>/SKILL.md <lane>/corpus` → hits in chousa, kagi, kake, kasegi, kotodama, mori (rc 0).
4. `grep -rIn … -E 'strip_ctl|control char|ANSI escape|terminal escape|\\x1b|u001b|sanitiz' <lane>/tools <lane>/SKILL.md <lane>/corpus/knowledge` → hits in chousa, kaidoku, kake, kasegi, kengaku, kotodama, kumitate, mado, mori, souji, tabi, tameshi, tsukuroi (rc 0).
5. `grep -rIn … -E 'reason.?code|REASON_ROWS|reason_codes|reason code' <lane>/tools <lane>/SKILL.md <lane>/corpus/knowledge` → kake `SKILL.md:777`, kumitate `route-probe-cluster.md:225-236`, mori `surfaces-r8.md:39` (rc 0).
6. `grep -n 'MAX_BODY\|max-filesize\|max-time\|compressed\|curl ' tools/kama-probe.sh` → `MAX_BODY=4194304` (:103), three curl calls at :340, :375, :761, `C_REASON=body-too-large` (:846); **no `--compressed`** (rc 0).
7. `sha256sum tools/kama-probe.sh` → `c197912f…d2ef97`, rc 0. `git rev-parse HEAD` → `2ee0b55f…27b2d`, rc 0.
8. `grep -n -E 'quote-reopen|reopen-row|mori-ua|release-clock|design-blob|cand-b1|route-health|probe-ufo' corpus/knowledge/cross-lane-scope.md` → 0 lines, **rc 1** (no existing row covers these instruments; `wc -l` → 148).
9. `git status --porcelain` in the lane → 13 entries, all the L1's own round-90 work (`M SCORECARD.md`, `M corpus/README.md`, `M corpus/SOURCES.md`, untracked wave dir and two new corpus files); none created by this seat.

## Findings

**NOTE F1 — kama's C1 cap is the fleet's only curl-level answer cap; its sourcing has no sibling
corroboration.** Command 2 returns nothing, so no sibling can corroborate S587's abort-at-threshold
semantics; every sibling bounds answers inside its own reader (chousa `_inflate_stream`,
`tools/quote-reopen.py:313-336`; kotodama `_read_body`, `tools/reopen-row.py:541-567`; mori
`resp.read(MAX_BODY + 1)`, `tools/mori-ua-variance.py:125`; kagi `read(MAX_BODY_BYTES + 1)`,
`corpus/release-clock.py:768-775`; kumitate `maxBuffer = 1024 * 1024`,
`corpus/knowledge/route-probe-cluster.md:522`). Consequence: the counter is the only evidence for the
curl path, which is what C1 already says. Evidence: command 2; `corpus/SOURCES.md:342` (S587).

**NOTE F2 — a size cap is one of three bounds; kama holds one and needs only one, for now.** chousa
documents "a cap of 8 MiB on both the wire bytes and the inflated bytes"
(`chousa-shokunin/tools/quote-reopen.py:28`, enforced `:313-336`, `:420-424`); kotodama pairs a 4 MiB
wire cap with a 64 MiB `GZIP_LIMIT` (`kotodama-shokunin/tools/reopen-row.py:139-142,400-410`); kagi
proves its over-cap branch by shrinking the cap to 8 bytes in a self-test
(`kagi-shokunin/corpus/release-clock.py:1583-1596`). kama's three curl calls carry no `--compressed`
(command 6), so `--max-filesize` bounds exactly the bytes written — the cap is a true wire cap today.
The constraint is negative and unrecorded: adding `--compressed` would make the cap bound received
bytes, not the decoded body, and `MAX_BODY` would stop bounding what is parsed. Evidence:
`tools/kama-probe.sh:340,375,761`; `corpus/knowledge/probe-answer-bounds.md` §Limits (silent on it).

**NOTE F3 — an over-cap answer must be its own outcome, and the fleet is not uniform.** kumitate
names `output_overflow` as a failure class and flags `stdoutOverflow`/`stderrOverflow` separately
(`kumitate-shokunin/corpus/knowledge/route-probe-cluster.md:225,522`, test section `:563`); kotodama
returns `TRUNCATED` ranked like `ABSENT` (`tools/reopen-row.py:18-19,163,713-714`); chousa returns
`body over 8 MiB` with nothing parsed (`tools/quote-reopen.py:420-424`); kagi returns
`response too large` (`corpus/release-clock.py:810`). mori folds an over-cap answer into
`unavailable`, the same outcome as a transport failure (`tools/mori-ua-variance.py:143`). kama's
`body-too-large` (rc 63, `tools/kama-probe.sh:846`) is on the distinct side — corroborated, not
novel; it should be described as a choice, not as the fleet norm.

**NOTE F4 — kama's control-character class is narrower than every sibling's, by design, and the
boundary needs stating.** kama escapes C0/DEL/C1 as `\uXXXX` in ids and drops them from headers and
status values (`corpus/knowledge/probe-answer-bounds.md` decision rows; `jstr` escapes U+0001–U+001F
and DEL). souji refuses C0/C1/DEL in a path or receipt field before parsing because a TAB shifts
every following TSV column, then space-replaces on emit
(`souji-shokunin/tools/cand-b1-quarantine.sh:157-162,196-204`); tameshi refuses C0/DEL in a
verdict-bearing receipt path because a newline forges a verdict line
(`tameshi-shokunin/tools/design-blob-audit.py:179-184`); kotodama refuses inside a verdict token by
name — NBSP, VT, FF, LS/PS/FS, NEL, ANSI, any `Cc`, combining marks, any `Zs`
(`kotodama-shokunin/tools/check-advance-evidence.py:295-325`, classes at `:86-97`, selftest table
`:1972`); the fleet display sanitizer strips C0/C1, ANSI/OSC, **bidi controls and tmux format
tokens** (`kumitate-shokunin/corpus/knowledge/remaining-scripts-census.md:660`). kake refuses CR/LF/
NUL in a header value (`kake-shokunin/corpus/knowledge/stored-response-reuse.md:112`) and raw C1 in a
URL (`static-canonical-preflight.md:121`). Consequence: bidi U+202A–U+202E, OSC and U+2028/U+2029 sit
outside kama's frozen set; a held-out cell in that class is a scope finding, not a C1 falsification.
The escape-preserves-identity choice is what keeps cells P3/P4 separable from the over-sanitizer
forgery F2 (`controls/f2-over-sanitizer.sh`).

**NOTE F5 — reason-code population provenance is a claim in its own right, and C2 already handles
it.** kumitate's route-health vocabulary is declared (11 `FAILURE_CLASSES`, 4 statuses, live and
rollup reasons) and names one member as unreachable through the validated caller
(`route-probe-cluster.md:225,230-236`, `:231`); kake's registry binds each code to fixture cases and
lists 12 codes "no committed fixture names yet — uncovered behaviour, not regression coverage"
(`kake-shokunin/SKILL.md:777-816`). kama's C2 population is print-site-derived (23
`C_REASON=`/`RT_REASON=` assignments at `99cdb4d6`) plus the post-C1 `body-too-large` row, with
`dns-failure` excluded by name. The three are complementary, not competing; C2's `additional` row and
exclusion note are the mechanism, so no cross-lane row is drafted for it.

**NOTE F6 — the C1 counter's shape has prior art in chousa, and C1 should cite it as such.** chousa's
round-30 fetch-bound counter grades its own verifier over 27 loopback cells, "loopback harness only,
no network", with a base reading `12/27` at the previous tool and `27/27` at the fixed one
(`chousa-shokunin/SKILL.md:96`; receipt label and base at
`corpus/evidence/round30/claims.md:148,162-164`). kama's `round90-hostile-answers.py` (13 stub cells,
base `mismatches=8`, M `0/0`) is the same species: a do-nothing base plus a per-cell fixed tool. This
is corroboration and prior art for the *instrument*, not a competing claim on the probe.

**NOTE F7 — the pre-8.4.0 fallback bounds the verdict, not the disk write.** The probe's re-check
fires only after curl has written the body (`tools/kama-probe.sh:345-346`: `rc -eq 0` then
`wc -c`), and S587 says the option had no effect on an unknown-length body before 8.4.0
(`corpus/SOURCES.md:342`, lines 30-32). On this host (curl 8.23.0) the transfer aborts at the cap, so
C1's measured cells are unaffected; on an older curl an unknown-length 64 MiB answer is written in
full to `TMP_ROOT` before `F_RC=63` is set — the verdict is still `FOREIGN_SERVICE body-too-large`,
but the disk cost is unbounded, which is the r89 SN01 F3 harm class. The knowledge entry says "older
curl needs a written-size check" but not that the write itself is unconstrained. Not a claim
falsification: the frozen predicate is measured on this host's curl.

## Deliverables

- `.ufo/waves/round-90/w1/out/CN01SiblingOverlap/overlap.md` — the hit inventory (lane, path:line, coverage, classification) plus the three "not found" results.
- `.ufo/waves/round-90/w1/out/CN01SiblingOverlap/candidate-rows.md` — two candidate rows for `corpus/knowledge/cross-lane-scope.md` in its `## Contested scope and arbitration` table shape, with a bold lead sentence for the rounds-71/72 bullet form, plus the notes on what was deliberately not drafted.

VERDICT: holds — no sibling lane holds a competing claim on kama's probe answer bounds or its reason-code rows; every overlap found is corroboration or a reusable rule, and the two drafted rows place C1/C2 against sibling prior art without absorbing sibling ground.
