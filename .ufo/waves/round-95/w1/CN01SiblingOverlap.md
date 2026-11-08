# CN01SiblingOverlap — sibling-lane adjacency & cross-lane overlap scan (kama round 95, wave 1)

Seat: CN01SiblingOverlap (connector, read-only). Lane: kama-shokunin, tip `ca531563`, base `2011161d`.
Read-only scan of 20 sibling repos under `/home/vgpnk/Projects/shokunin/*-shokunin`. Judged on: adjacency.

## Scope
1. Cross-lane scan for whole-struct-copy carriers and per-entry-point decision tables (`grep -rl "entry point\|per entry"`).
2. Sibling probe/consumer registry checks for claims about llama.cpp listen ports or slot counts contradicting R20/R21.
3. Precedence check on `AIP_HTTP_PORT`: does any lane's document assert the opposite (that `--port` wins)?
4. Contested scope identification and UFO-FSD connector synthesis (improving depth/adjacency without harming calibration).

## Commands and outputs (exit codes)
| # | Command (cwd) | Exit | Result |
|---|---|---|---|
| 1 | `bash scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama` | 0 | 118 W04 lines; clean exit 0 (`out/.../census-validate.out`) |
| 2 | `bash scripts/sources-census.sh shared --root /home/vgpnk/Projects/shokunin` | 0 | 36 shared sources; only 1 shared llama.cpp source across fleet (`b7200` README with kengaku) |
| 3 | `grep -rlE "entry point\|per entry" /home/vgpnk/Projects/shokunin/*/corpus/knowledge/*.md` | 0 | 56 matching files across fleet; 0 sibling files hold struct-copy or per-entry tables (F1) |
| 4 | `grep -rn "AIP_HTTP_PORT" /home/vgpnk/Projects/shokunin/ --exclude-dir=kama-shokunin` | 0 | 0 occurrences in any sibling repo (only in `.ufo/reports/round-94/kama.md` and MANIFEST) (F2) |
| 5 | Token scan (`9931`, `LLAMA_ARG_PORT`, `LLAMA_SERVER_ROUTER_PORT`, `AIP_HTTP_PORT`, `common_params`) over 20 sibling repos | 0 | 27,014 lines scanned; 0 semantic contradictions to R20/R21; tabi `common_params` is Chromium; kengaku matches 9931 (F3) |
| 6 | `awk` / `grep` inspection of `kama-shokunin/registry/endpoint-consumers.tsv` lines 34-37 | 0 | L36-L37 cite superseded `SKILL.md R18` instead of round-95 per-entry `R20 (server)` (F4) |

## Findings
- **F1 — NOTE (exclusive domain ownership).** No sibling lane's corpus holds the whole-struct-copy class (`common_params server_params = params; // copy` at `tools/cli/cli-server.h:43`) or a per-entry-point decision table. Sibling hits for "entry point" / "per entry" (`kaidoku`, `tabi`, `kake`, `tsukuroi`) refer strictly to ELF/PE symbols, URL routing, or test harness loops. `kama-shokunin` uniquely owns both (`SKILL.md:2256-2399`, `corpus/lessons/round-95.md:61`).
- **F2 — NOTE (unanimous AIP_HTTP_PORT precedence).** Zero sibling lanes mention `AIP_HTTP_PORT`. Within kama, b12177 source (`tools/server/server-http.cpp:96, 125`) and empirical measurement (`.ufo/reports/round-94/kama.md:74-77`) confirm that under `AIP_MODE=PREDICTION`, `AIP_HTTP_PORT` replaces `--port` and child free ports. No document in any lane asserts the opposite.
- **F3 — NOTE (sibling concordance on ports/slots).** No sibling probe/consumer registry contradicts kama's R20/R21 rows. `kengaku-shokunin` (`PROVINCE.md:14`, `corpus/evidence/round10-fleet/r10-scout-endpoint.md:33`) records `llama-server` on `127.0.0.1:34113` with `--parallel 2`, conforming to R20/R21 argv overrides. `kumitate-shokunin` (`corpus/knowledge/ops-watchers.md:402`) documents `the-tick` client connecting to `:34113/v1/chat/completions`. `kagi-shokunin` (`SKILL.md:43`) notes `:8080` was a Jitsi videobridge, distinguishing it from llama-server.
- **F4 — DEFECT (internal registry citation lag).** In `kama-shokunin/registry/endpoint-consumers.tsv:36-37`, rows `ufo-fsd-thetick` and `ufo-fsd-local-helper` cite `SKILL.md R18` (`--port 34113 ... P18/P19 route`). Round 95 superseded `R18` with per-entry rows `R20` (server/cli/router-child/shared/other) and `R21`. The citation must point to `R20 (server)` (P19 setter).
- **F5 — NOTE (contested scope: kengaku router slot attribution).** `kengaku-shokunin/PROVINCE.md:15` lists the `:1234` router alongside direct server `:45669` and quotes `slots 4` from `/props` (`endpoints.txt:15`). In llama.cpp b12177, router `/props` exposes a dummy object with no `total_slots` key; auto resolves to 4 only on the direct instance. Kengaku explicitly notes "flag authority is kama's (serving plane)" (`PROVINCE.md:15, 26`). Kama remains the sole authority that the router role resolves no slot count.
- **F6 — DEFECT (C2 counter blind spot on carrier rows).** `CR02SetterCounter` revealed that `tools/round95-setter-sweep.py:366-370` builds `want` sets from `default|overrides` rows only. The 14 new carrier rows (P93–P106, including P100 cli-server whole-struct copy) have effects `copies`, `declares`, or `realises` and enter no decision set. Consequently, mutating P100 Entry from `cli` to `server` still produces `met=True` (CR02 variant V4). Furthermore, `met` (`:410-412`) omits `entries == 7` from its exit check.

## Proposed Move (UFO-FSD Connector Synthesis)
- **Evidence:** `CR02SetterCounter` proved P100 (`tools/cli/cli-server.h:43`) is unverified by any decision set, and `tools/round95-setter-sweep.py` omits `entries == 7` from `met`. Meanwhile, `registry/endpoint-consumers.tsv:36-37` lags with stale citations to superseded `R18`.
- **Affected axes:** Depth (7 → 8) and Adjacency (7 → 8) without harming Calibration (7) or Operability (8).
- **Proposed move:** Synthesize cross-surface carrier binding:
  1. Bind cross-entry `copies` carriers into decision rows: R20 (cli) and R21 (cli) must explicitly require P100 in their carrier set, making P100's Entry cell load-bearing and killing survivor V4.
  2. Add `entries == 7` to the `met` boolean tuple in `tools/round95-setter-sweep.py:410-412`.
  3. Re-point `registry/endpoint-consumers.tsv:36-37` citations from `R18` to `R20 (server)` (P19 setter).
  4. Record an integrator note preserving kama's exclusive authority over router slot resolution vs kengaku `PROVINCE.md:15`.
- **Risks:** Restricting carrier binding to cross-entry `copies` prevents bloat from internal config.ini copies (P03-P10).
- **Verification:** Run `tools/round95-setter-sweep.py`; variant V4 must fail `met=False`. Run `grep R20 registry/endpoint-consumers.tsv`.

## Deliverables
- Report: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-95/w1/CN01SiblingOverlap.md`
- Out dir: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-95/w1/out/CN01SiblingOverlap/` (`census-validate.out`, `census-shared.out`, `sibling-token-scan.txt`)
- Scratch `/fast/scratch/hyaku/kama-r95/CN01SiblingOverlap/` removed before yield.

VERDICT: holds — sibling corpora clean and non-contradictory (F1-F3, F5); internal citation lag (F4) and carrier verification gap (F6) synthesized into one bounded move.
