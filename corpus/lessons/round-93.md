# Round 93 — router model-file verdict repeat-invariant; every port and slot-count setter named

L1 `KamaR93` (attempt 1). Base `5af794958b0fc08f574aa2e67650282269549b02`; freeze `0f272a3773be25a6cbdaf75f1a7a3ec293b60f8d`;
C1 measured `fe5f031cb1b9d33e1160360d892149b8ac3c7771`; C2 measured `ee19acbdabc8ac572e82ae56459c364457895b06`.
Plan: `plans/round-93-claims.md`. Previous closure: `round-92-verifier-spotcheck.md` (rejected-honest-stop; R1–R6).

## Gate

Rows opened by the L1 (`curl -sfL --max-time 60`, receipt `.ufo/waves/round-93/controls/sources-opened.out`, fetched
2026-11-07T02:33:36Z = 2026-11-06 23:33 -03; the new rows carry the UTC date 2026-11-07). Each fetched digest equals
the digest of the same path inside the pinned codeload archive (sha256 `f50a52f4…ea13`) and, for re-opened rows, the
digest in its `corpus/SOURCES.md` row.

| Candidate | Decision | URL / access date | Located quote (≤25 words) and location | Reason |
|---|---|---|---|---|
| S600 llama.cpp `common/http.h` @ `b12177` | **admit** (A, code, mined) | https://raw.githubusercontent.com/ggml-org/llama.cpp/b12177/common/http.h — 2026-11-07 UTC, sha256 `949e44f9c592d1f894818765d8bf433e3cfd183430696464e4965447643d2de1` | `int port = ntohs(serv_addr.sin_port);` (line 324; the socket is bound to port 0 at line 301) | Grounds P27–P30: the free-port helper a router uses for children, and three client-side URL lines that are not a listen port. |
| S601 llama.cpp `tools/server/server-connect.cpp` @ `b12177` | **admit** (A, code, mined) | https://raw.githubusercontent.com/ggml-org/llama.cpp/b12177/tools/server/server-connect.cpp — 2026-11-07 UTC, sha256 `2a505b295d649e6e0e70840d0f949a66b06d18269282294e5fb804e0460cc9df` | `"--port", std::to_string(port),` (line 208, inside `server_connect::start`) | Grounds P31: `--connect` passes the bound port to a separate binary and sets no port in llama-server. |
| S602 llama.cpp `tools/server/server-http.h` @ `b12177` | **admit** (A, code, mined) | https://raw.githubusercontent.com/ggml-org/llama.cpp/b12177/tools/server/server-http.h — 2026-11-07 UTC, sha256 `29c53f7ffde226edf3e6f48463e4807f7e554ca12e476099f90e0ff18142978d` | `int port    = 9931;` (line 92, member of `server_http_context`) | Grounds P38: a second 9931 that `init()` overwrites (S598 line 116) before any bind. |
| S603 llama.cpp `tools/server/server-models.h` @ `b12177` | **admit** (A, code, mined) | https://raw.githubusercontent.com/ggml-org/llama.cpp/b12177/tools/server/server-models.h — 2026-11-07 UTC, sha256 `304c013601e1a5abfc9bcc42173b3ec2db23e65e065a8249532c4ddda6a5a6a1` | `int port = 0;` (line 80, member of `server_model_meta`) | Grounds P46: the router's per-model port before spawn. |
| S593, S596–S599 @ `b12177` | **re-opened**, admitted for the P-rows that cite them | the rows' URLs — 2026-11-07 UTC, digests equal (`sources-opened.out`) | `params.port = 8011;` (S596 line 4613) | Every P-row's text cell is the archive line byte for byte (`measured/c2.out` B2). |
| `tools/server/server-models-sched.cpp` line 423 as a listen-port setter | **reject** (names another port) | https://raw.githubusercontent.com/ggml-org/llama.cpp/b12177/tools/server/server-models-sched.cpp — read in the archive 2026-11-07 UTC | `child_env.push_back(std::string(SERVER_ENV_ROUTER_PORT) + "=" + std::to_string(models.base_params.port));` (line 423) | It hands the **router's** port to a child's environment; the child's listen port is set by S599 lines 316/1218 (P41, P43). Not in the frozen population (no pattern token). Flip: a later pin reads `SERVER_ENV_ROUTER_PORT` as the child's listen port. |
| The codeload archive itself as a SOURCES row | **reject** (input, not a teaching source) | https://codeload.github.com/ggml-org/llama.cpp/tar.gz/refs/tags/b12177 — 2026-11-07 UTC, sha256 `f50a52f4ba45dd5b4b906db97cf230ce2e3b1117a0b9017411322ecba63eea13` | n/a (binary archive) | The archive is the counter's pinned population input (`TARBALL_SHA256` in `tools/round93-setter-rows.py`); what kama learns is cited per file through the raw rows above, whose digests equal the archive members. Flip: GitHub stops serving per-file raw URLs for the tag. |

`status` / `recheck` / `used-by` changes on existing rows: none (S593, S596–S599 byte-identical). S600–S603 are new
rows (`mined`, recheck `on-release`, used-by `SKILL.md`).

Assimilation: none (no `merge/kama/` theme taken; `considerthese/` not mined this round).

## Mistakes

**M1 — a held-out cell sized below the threshold of the forgery it was meant to kill.** Class: discriminating cell
chosen before its forgery existed. Evidence: the first counter draft's R05 named the slow file through 4 path strings
(`.ufo/waves/round-93/controls/c1-base-v0.out`); a probe whose memo is keyed by the path string parses it 4 times
(≈1.4 s at load 21), under the shared 4 s deadline, so that forgery (F2) passes every cell of the v0 counter:
`.ufo/waves/round-93/measured/m1-v0-alias-F2.out` — `ROUTER_REPEAT cells=10 mismatches=0 positive_mismatches=0
probe=override`, exit 0. Captured-by: the pre-freeze forgery battery (plan §9 "build the cheapest control … before
freezing"), only because F2 was written before the freeze; no criterion required running each forgery against the
final counter. Fix: R05 widened to 33 path strings before the freeze (F2 red in `controls/c1-forgeries.out`); new
QUALITY KQ150. Shown able to fail: the v0 receipt above.

**M2 — a range shorthand hid ids from a decision's named-set rule.** Class: prose compression where the rule needs
enumerated tokens. Evidence: the first R16 draft wrote "P13-P18 the FIM presets"; the counter requires every
overriding id by name and printed `SETTER_DECISION R16 unbound decision-names`
(`.ufo/waves/round-93/measured/m2-range-decision.out`, exit 1). Captured-by: the counter's decision rule through the
pre-freeze positive control P0. Fix: R16 names P13, P14, P15, P16, P17, P18 (`controls/c2-candidate-section.md`).
Shown able to fail: the reproduction receipt above.

**M3 (carried, from the round-92 closure R1) — append-debt events grow with every probe-bound receipt re-capture.**
Class: a by-design rewrite counted as an unaccepted deletion. Evidence: the gate's `APPEND_DEBT` reads `events=100
unaccepted=21` at the round-93 record (r92: 97/18); this round's deletion events are the KQ148 re-capture of
`.ufo/waves/round-90/measured/reason-cells.jsonl` (`995fe905`, 24 lines replaced by 24 identical triples) and the
SCORECARD head-row updates. Captured-by: `round75-instruments` (red since r87; L0 r87/r89 open). Fix: none this
round — the register cannot accept rows without the operator ruling the L0 asks for; stated, not claimed.

**M4 — row labels contradicted the section's own vocabulary (C2 not verified).** Class: a label chosen for the
decision's convenience instead of by the glossary the section defines. Evidence: P05, P06, P07 (`common/arg.cpp`
2526, 2529, 2531: the non-server `--parallel` declaration, its `params.n_parallel = value;` and its env declaration)
carry parameter `-` and effect `unrelated`, which the section defines as "another variable, or text"; their twins
P02, P03 (and P04) carry `n_parallel` / `declares` / `overrides` (wave-1 RV02 finding 1, CR02 DEFECT-2;
`.ufo/waves/round-93/measured/kq151-twins.out`: `TWIN_LABEL_DIFF` on P02/P05 and P03/P06, exit 1). The vocabulary
had no label for "a setter the pinned program never registers", so the author bent `unrelated` to keep P06 out of
R17's overriding set. Captured-by: none — the counter checks label membership, not meaning; KQ149 asks that a setter
be named or excluded, not that the label be consistent. Fix: dated correction under the section (rows unchanged),
new QUALITY KQ151. Shown able to fail: the twin receipt above (P40/P46 also differ and are legitimate: different
structs, reasons stated in their condition cells — the check flags, the reviewer reads).

**M5 — a file-identity key without a mutation control (C1, repaired in round).** Class: an identity key chosen from the
fields that change on an ordinary write, not from the fields a hostile writer cannot restore. Evidence: wave-1 RV01
DEFECT-1 — the memo key `(dev, ino, size, mtime)` served a stale state when a file was rewritten in place to the same
size with its mtime restored between two candidates of one call: `.ufo/waves/round-93/measured/c1-ctime-rewrite.out`
at `fe5f031c` entry 2 `-` (loadable) 3/3. Captured-by: none in the frozen plan (the counter never mutates a file).
Fix: `st_ctime_ns` added to the key (`b3765799`; utime() cannot set ctime); same receipt at `b3765799` entry 2
`invalid` 3/3; C1 counter 10/10 0/0 and harm unchanged at `b3765799` (`measured/c1-M1b.out`, `harm-M1b.out`).

**M6 — R16's router-child clause is defeated by a later-sorting preset option (K2, second clause).** Class: a
decision states a port for a start that another population row changes. Evidence: `common/preset.cpp:44-51` renders a
child's argv by iterating a `std::map` keyed by `strcmp(args[0], …)` (`common/arg.h:91-96`), so `--port` precedes
`--vision-gemma-4b-default`, whose lambda sets `params.port = 8014;` (`common/arg.cpp:4753`, P23/P24) after P41's
`--port`; `unset_reserved_args(preset, false)` (`server-models.cpp:268-286`, called at 314) does not remove preset
options. Such a child listens on 8014, not on the free port the router chose. Non-author read: wave-1
`w1/RV02SetterRows.md` DEFECT-2. Captured-by: K2 (fired). Fix: `SKILL.md` §Round 93 correction states the argv-order
rule; superseding rows planned (round 94). Not run on a live child (the claim is the source read).

### Corrections to M1–M4 (appended after wave-1 SB01; the rows above stand as written)

- M1: "≈1.4 s at load 21" is not a receipt token. The receipt is `measured/m1-v0-alias-F2.out`: R05 2.64 s / 2.96 s /
  2.64 s at load 73 for four parses; the frozen R05's 33 strings put the path-string memo past the 4 s deadline.
  The v0 counter bytes are not committed (the receipt names `<scratch>/v0-counter.py`, rebuilt from the frozen
  counter by one line); v0 is not presented as replayable.
- M2: captured by the counter's `decision-names` arm; the receipt `measured/m2-range-decision.out` is a reconstruction
  after the freeze (`--skill-file` override at `4c4adc63`), not the original P0 run.
- M3: the numbers are those of the terminal gate receipt `.ufo/waves/round-93/measured/gate-final.out` (committed at the
  end of the round), not a hand-copied line.
- M4: Captured-by is K2 (fired, wave-1 RV02); no QUALITY criterion existed, hence KQ151.
- Gate: the re-opened rows S596, S598, S599 are admitted for their files; their anchor cells name narrower line
  ranges than the P-rows cite (P08–P24 at 3318–4764, P37 at 512, P39–P45) — read them through `SKILL.md` §Round 93
  correction. The `server-models-sched.cpp` reject was read in the pinned archive, not fetched as a raw URL.
- The C1 rule prose in `plans/round-93-claims.md` names a four-field key; the tip's key has five fields
  (`st_ctime_ns`, `b3765799`, M5). The plan stays frozen; this is the dated note.

## Dispositions of the round-92 closure (R1–R6)

- **R1** carried, not claimed (M3; L0 r87/r89 open). This round's own deletion events are the two KQ148 re-captures of
  `.ufo/waves/round-90/measured/reason-cells.jsonl` (24 identical triples each, at `995fe905` and `8e9ecd63`) and the
  SCORECARD head-row updates.
- **R2** answered in form (R16/R17 supersede R01/R08 with every population setter named), **C2 not verified** (M4, M6).
- **R3** done for the R01/R08 class: `controls/c2-forgeries.out` V1 (the round-92 decisions) → `decisions_bound=0`;
  the broader battery is thin (wave-1 CR02 20/38 forgeries bind, MT02 16/26 counter mutants survive) — routed.
- **R4** routed to round 94 (SCORECARD §Planned (round 94) item 1).
- **R5** the round-93 report is authored after the final lane push; its author date is checked against the tip
  before filing.
- **R6** carried (R03 wording untouched).

**M7 — a frozen control's named expectation is load-sensitive.** Class: control receipt that names *which* cell a
forgery fails, where the failing cell depends on parse speed. Evidence: the replay of the frozen battery at
`487e5b15` (`.ufo/waves/round-93/measured/c1-forgeries-replay.out`, load ~70, 0.8 s per slow parse) rejects F4
(first-8 cap) with `mismatches=5` on R02–R06, but its named cell P02 is green — eight capped parses outlast the 4 s
deadline, the uncapped valid file is never reached and stays loadable — so `as_expected=0`, `C1_CONTROLS 4/5`; the
pre-freeze run at load 38 failed F4 on P02 (`controls/c1-forgeries.out`). The forgery is rejected either way; the
receipt's label is not reproducible. Captured-by: KQ150's sibling rule (forgery run against the frozen counter), which
holds, but nothing required the named cell to be load-independent. Fix (round 94): a control names the predicate it
must fail (`mismatches>0`), and any named cell is checked for load sensitivity by a replay at a second load.

Wave-1 adjacency read (CN01, `w1/CN01SiblingOverlap.md`): kama's own consumer rows
`registry/endpoint-consumers.tsv:35-37` pin 8080 and 34113 without naming which setter (R16) the unit uses — routed
to round 94 (R16 is not verified); kagi's `SKILL.md:9-10` keeps a stale 8080 model pin — reported, not absorbed.

**M8 — a mechanical population taken as the setter sweep (K2, wave-1 SC01).** Class: "every line matching a pattern"
read as "every setter". Evidence: a `config.ini` sets the pinned llama-server's port (18099) and slot count (7)
through the option handlers, and no line of that route matches `POP_RE`
(`.ufo/waves/round-93/w1/SC01SetterSweep.md` F1, receipts `out/SC01SetterSweep/prec*.log`, `cfg-parallel.log`); the
embedded `llama-cli` server runs 1 slot on a free port (F2). R16/R17 named neither, so they state a port and a count
for starts another setter changes. Captured-by: K2 (fired). The plan's limit paragraph disclosed data-flow setters
for the *counter*; it did not stop the *decision* from claiming completeness. Fix: decisions scoped to the entry
point they were swept for and to the setters a live run of the pinned binary confirms (config file, env, argv,
presets, AIP, router child), routed to round 94 (SCORECARD §Planned item 5).

**M9 — a claim about a time-bounded verdict measured only at natural load (C1 not verified, wave-1 SC02).** Class:
load-invariance asserted from runs that never varied the load. Evidence: `w1/SC02ProbeVerdictSweep.md` F1 — the frozen
C1 counter at M1 under synthetic load prints `positive_mismatches=1`, exit 1 (K1); the shared 4 s `DEADLINE` decides
(F2). The round's own M7 (a control's named cell moving with load) was the same signal. Captured-by: K1 (fired under a
non-author reproduction). Fix (round 94): any counter over a deadline-bounded verdict runs its cells at two loads, one
synthetic, before freezing.
