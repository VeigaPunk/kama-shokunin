# SB01LessonDraft — round-93 lesson draft (calibration seat)

## Scope

Drafted the `## Gate` admits for S600–S603 and candidate `## Mistakes`/`## Dispositions` rows for
`corpus/lessons/round-93.md` from the round's own record: `plans/round-93-claims.md`, `controls/*.out`, the landed
wave-1 reports (`RV01`, `RV02`, `CR02`, `EX01`, `EX02`, `MT02`), the round-92 closure R1–R6 and the round-92 lesson
format. Lane tip at read: `54b8578f0effa249596947bfc1081da902dc4bec` (2026-11-06 23:56 -03); the L1 had already landed
lesson M1–M5 and the SKILL correction, so the draft keeps only what is still missing or misstated. Read-only in the
lane except this report and `w1/out/SB01LessonDraft/`; scratch under `/fast/scratch/hyaku/kama-r93/SB01LessonDraft/`.
No counter was run (the assignment says not to rerun work); every measured time cited is a token printed by a
committed receipt (the one derived figure, ~23 s, is labelled as such in the draft). Host load at read: `uptime`
93.43/71.70/59.10.

## Commands and outputs (exit codes)

1. `curl -sfL --max-time 60 …/b12177/<path>` for `common/http.h`, `common/arg.cpp`, `tools/server/{server-connect.cpp,
   server-http.h, server-models.h, server.cpp, server-http.cpp, server-models-sched.cpp}` — **exit 0** each.
2. `sha256sum` — `949e44f9…2de1`, `c69c0e07…6f67`, `2a505b29…c9df`, `29c53f7f…978d`, `304c0136…a6a1`, `d4d343db…08b`,
   `aad15b75…7ea`, `b786ea09…54a`; the first seven equal `sources-opened.out` (the four S600–S603 also their SOURCES
   rows); `sched.cpp` is not in that receipt (NOTE-4).
3. `diff` of `git show ee19acbd:SKILL.md` §"Listen port…" against `controls/c2-candidate-section.md` — **exit 0**,
   `SECTION_BYTE_IDENTICAL` (69 lines).
4. `git diff --stat 0f272a37 54b8578f -- tools/round93-router-repeat.py tools/round93-setter-rows.py
   plans/round-93-claims.md` — empty, **exit 0** (K1/K3 hold). `git diff --name-only 0f272a37 fe5f031c` →
   `tools/kama-probe.sh`; `fe5f031c ee19acbd` → `SKILL.md`, `corpus/SOURCES.md`.
5. `grep -c '^exit=' controls/{c1-base-v0,c1-base,c2-base,c1-forgeries,c2-forgeries}.out` → `0,1,1,1,1`.
   `grep -l 'counter_sha256' controls/*` → **0 files**.
6. `bash /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama`
   → **exit 0**, `kama ok` (W04 duplicate-url warnings only).
7. `diff` of the `REASON_CAPTURE_CELL` lines in `measured/r90-reason-recapture.out` vs `…-M1b.out` — empty,
   `TRIPLES_IDENTICAL` (24 cells; only `probe_sha256` differs: `159c80…` → `1e21c1fb…`).
8. `grep -rn 'APPEND_DEBT\|events=100' .ufo/waves/round-93/ --exclude-dir=SB01LessonDraft
   --exclude=SB01LessonDraft.md` → **no matches**; the `events=100` token exists only in
   `corpus/lessons/round-93.md:49` (outside the round tree) and in this seat's files.
9. Line reads (1-based): `common/http.h:324` `int port = ntohs(serv_addr.sin_port);`, `:301` `serv_addr.sin_port =
   htons(0);`; `server-connect.cpp:208` `"--port", std::to_string(port),`; `server-http.h:92` `int port    = 9931;`;
   `server-models.h:80` `int port = 0;`; `arg.cpp:4613` `params.port = 8011;`; `server.cpp:341`
   `connect_proc.start(params, ctx_http.port)`; `server-http.cpp:116` `port = params.port;`, `:512` `port = bound_port;`.
10. `git show b3765799 -- tools/kama-probe.sh` — memo key `(st_dev, st_ino, st_size, st_mtime_ns)` →
    `(…, st_ctime_ns)` (the key hunk; the other hunk is the comment). `git status --porcelain` — clean for `measured/`.

## Findings

**BLOCKER (C2; recorded at `54b8578f`, reproduced here).** K2 fired on two non-author findings. (a) P05–P07
(`common/arg.cpp:2526/2529/2531`) carry parameter `-`/effect `unrelated`; the lines are the `-np/--parallel`
declaration, `params.n_parallel = value;` and its env declaration, and their twins P02/P03/P04 carry
`n_parallel`/`declares`/`overrides`; the section defines `unrelated` as "another variable, or text". (b) R16's
router-child clause: `common/preset.cpp:44-50` renders a preset by `std::map` order keyed by
`strcmp(args[0],…)` (`common/arg.h:91-96`), so `--port` precedes `--vision-gemma-4b-default`, whose lambda sets 8014
(`arg.cpp:4753`, P23/P24), and `server-models.cpp:314-322` keeps the preset option — such a child listens on 8014,
not the free port. Evidence: `w1/RV02SetterRows.md` BLOCKER-1/DEFECT-2, `w1/CR02SetterCounter.md` DEFECT-2; the L1's
`SKILL.md` dated correction and lesson M4/M5. C2 is correctly marked not verified.

**DEFECT-1 — the lesson's M3 numbers have no round-93 receipt.** `events=100 unaccepted=21` is printed by the
lesson, not by any round-93 receipt; no `APPEND_DEBT` line exists under `round-93` outside this seat's files, and the
pre-report gate has not been committed (round 92's receipt prints `events=97 … unaccepted=18`). Fix:
`python3 tools/pre-report-gate.py --repo . --round 93` committed as e.g. `measured/gate-final.out`, then quote it;
otherwise write "not yet measured".

**DEFECT-2 — M1's "(≈1.4 s at load 21)" is not a receipt token and its arithmetic is wrong.** No receipt prints
1.4 s for the four-parse v0 cell; the only 1.4 s C1 timing I could open is `w1/out/EX01HeldOutRepeat/heldout.out`
`A-distinct-x2` at `load1=73.48` — two *distinct* files (`1.40s`/`1.46s`), a different shape and load. The 4-parse
v0+F2 run is `measured/m1-v0-alias-F2.out` R05 `2.64s/2.96s/2.64s` at `load1=73.48`; use that and the 33-string
margin (~23 s of parses at the receipt's own rate) instead of 1.4 s.

**DEFECT-3 — M2's `Captured-by` overstates P0.** `measured/m2-range-decision.out` is a post-freeze reconstruction
(`rev=4c4adc63`, `--skill-file` override); the committed P0 is green (`controls/c2-forgeries.out` P0
`decisions_bound=2`). No pre-freeze receipt of the range draft is retained. Say: captured by the counter's
`decision-names` arm; exercised by a reconstruction at `4c4adc63`.

**DEFECT-4 — M4's `Captured-by: none` contradicts its own commit.** `54b8578f` is titled "K2 fired (… P05–P07
labels, R16 router-child argv order)", and round-91 M1's convention is `Captured-by: K2 … fired`. The field should be
K2 (fired), with "no QUALITY criterion existed → KQ151" as the fix.

**DEFECT-5 — the lesson has no row for the second K2 hit.** The R16 argv-order finding lives only in the `SKILL.md`
dated correction, so "C2 not verified" rests on M4 alone for a lesson reader. Drafted as M6.

**DEFECT-6 (Gate) — the re-opened row still says "admitted for the P-rows that cite them" without the range caveat.**
S596's anchor names 1365–1380 and 2514–2522 but P08–P24 cite 3318–4764; S598's 93–125 does not cover P37 at 512;
S599's 1218–1235 does not cover P39–P45 at 69/90/316/866/1292/2157. The SKILL correction's "Limits" has it; the Gate
row a reader uses does not. KQ22 forbids an in-place anchor edit: add a row or point the Gate at the correction.

**NOTE-1 — v0 receipt provenance.** `controls/c1-base-v0.out` has no `exit=` line (the frozen counter prints none;
the wrapper appends it) and no control receipt carries the counter's own sha256. The v0 counter bytes are not
committed (the m1 receipt's `cmd` names `<scratch>/v0-counter.py`), so the "4 path strings" rests on the plan's
"four-alias R05" plus the receipt header. Do not present v0 as replayable.

**NOTE-2 — the R05 retune was not goal-seeking on the counted population.** R05 is red in both base controls (v0
`4.20/4.22/4.21s`, frozen `4.39/4.40/4.40s`); the 4→5 `mismatches` delta is R02's load flip (green at `load1=20.88`,
red at `48.05`), not the alias widening. The retune shows only against F2.

**NOTE-3 — access-date convention.** Round-92 uses the local date with the UTC instant printed; round-93 uses the UTC
date. Both pass the census (`TODAY=$(date -u +%F)`); keep printing both instants so 2026-11-07 cannot read as future.

**NOTE-4 — the `server-models-sched.cpp` reject is not in `sources-opened.out`** (nine raw-URL files). Its quote is
verified at line 423, but the lesson should add an open line or mark "archive read, no raw digest". K3 does not fire
(the reject cites no S-id).

**NOTE-5 — counter limits, routed.** CR02: 14/31 forgeries bind (20/38 with `forgeries2`); MT02: 16/26 mutants
survive, 13 false greens — they extend disclosed limit L1 and belong in the round-94 carry.

**NOTE-6 — the claims' C1 rule prose is now stale.** It names a four-field key (device, inode, size, mtime); the tip's
key is five fields (`+st_ctime_ns`). The lesson M5 records the fix but not the prose delta; add a dated note.

**Verified and unchanged.** S600–S603 quotes, line numbers and digests (fetched by this seat, equal to the receipt
and SOURCES); the two Gate rejects' quotes (sched line 423; codeload sha `f50a52f4…`); S593/S596–S599 byte-identical
base→tip; the frozen counters and plan unchanged F→tip; M1 only the probe, M2 only SKILL+SOURCES; the M2 section
byte-identical to the candidate; the r90 re-captures' triples identical at M1 and M1b; harm at M1b all arms exit 0;
census exit 0.

## Deliverables

- `.ufo/waves/round-93/w1/out/SB01LessonDraft/round-93-gate-draft.md` (verified Gate, range caveat, reject
  provenance); `…/round-93-mistakes-draft.md` (M1–M4 corrections, missing M6 row, notes);
  `…/round-93-dispositions-draft.md` (missing R1–R6 dispositions, wave-1 integration status).
- This report; `sources-reopen.out` (the eight fetched files' digests and quoted lines).

VERDICT: partial — the Gate admits verify byte-for-byte and the two K2 hits are recorded, but the lesson still needs the four `Captured-by`/number corrections, the M6 row and the R1–R6 dispositions drafted here.
