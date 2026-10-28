# SC04Considerthese — considerthese mining (round 64, wave b, kama)

Seat: SC04Considerthese · 2026-10-28 · milestone: mine considerthese · judged on operability.
Method: read all 8 files in `considerthese/` (2026-10-19 … 2026-10-26); census = 32 proposals
(4 per file). For each candidate I surveyed `tools/`, `tests/`, `registry/`, `corpus/` and took
git creation commits (`git log --diff-filter=A --follow`) as round evidence. Read-only lane
access; no code run, no scratch used, no installs, no live servers, no git mutations.

## The ONE still-unimplemented proposal

**`considerthese/2026-10-24.md:29`, proposal 2 — re-open every new SOURCES row's quote at its
cited line (a quote-anchor drift watch).** Verbatim:

> 2. **Re-open every new SOURCES row's quote at its cited line each day:** the closures keep
> finding small anchor problems: S174 labelled "verbatim" while dropping a word, S192 cited two
> lines off after the page moved, S193 citing line 22 for text at line 15, and a round-32
> receipt-lineage sentence contradicting its own receipt. I could, read-only, fetch each SOURCES
> row added in my window and report which quotes still sit at their cited location, so drift
> shows up the day it happens instead of a round later.

### Why it is still unimplemented (evidence)

No lane tool re-opens a `corpus/SOURCES.md` row's located quote at its cited anchor at the same
pin, either at row landing or between rounds. The full inventory of quote/line machinery:

- `tools/release-recheck.py` (round 44, `ef76777e`): does relocate quotes at cited lines
  (`release-recheck.py:11-13` rows it cannot relocate are emitted `TODO`, never judged; `:177-181`
  `unchanged-file` only when the file blob changed at a release) — but its population is only
  rows with recheck cell `on-release` whose source cell names `ggml-org/llama.cpp` URLs
  (`round44-release-recheck-audit.py:17-20`), and it fires only when a new llama.cpp release
  lands. Ledgers: `registry/release-recheck-b11889.tsv`, `-b11906.tsv`.
- `round44-release-recheck-audit.py:44-48` / `round46-…:63-66`: the STRONG/WEAK cited-line
  grammar (`#L<a>[-L<b>]`, `L<n>`, `line(s) <n>`, bare ranges) — reusable mechanics, same
  release-scoped population.
- `tools/round60-c2-counter.py:15-19`: quote-at-line over a *capture-claims* registry
  (repo-local capture bodies), not SOURCES doc rows.
- `round44/45-verdict-ledger-audit.py`, `round45-claim-outcome-audit*.py`: cited-line reads over
  SCORECARD/spotcheck files, not SOURCES.
- `tools/sources-append-only.py` (r17), `tools/append-only-audit.py` (r46): guard deletions of
  SOURCES.md bytes, never anchor positions. `tools/digest-ledger.py` (r42) classifies digests;
  `tools/citation-provenance.py` (r19) binds registry-row digests. `tools/round54-cited-path-check.py`
  (r54) checks that self-assessment-cited *paths* resolve, not that quotes sit at cited lines.

The round-64 rows are exactly the uncovered class: S529–S532 (`corpus/SOURCES.md:281-284`,
opened 2026-10-28, status `queued`) are man7.org proc man-pages with recheck cell `180d` — a
time trigger **no tool consumes** — and retained fetched bytes + sha256 in-repo
(`.ufo/waves/round-64/source/proc_pid_{fd,stat,environ,cmdline}.html`). No release trigger will
ever fire for them (man-pages have no releases; release-recheck only watches llama.cpp), so
their anchors are re-openable only by hand. The incidents the proposal cites are real and were
corrected a round later, every time: S174 "verbatim" dropping "given"
(`corpus/lessons/round-29-verifier-spotcheck.md:56,60,77`; correction `round-30.md:101`);
S192 "cites line 1008 — content moved by ~2 lines between fetches"
(`round-31-verifier-spotcheck.md:55`); S193 "lesson says line 22 … source … line 15"
(`round-32-verifier-spotcheck.md:65,81`, superseded by S194 per `round-33-verifier-spotcheck.md:43`).
Round-63 shows the lane already does this ad hoc by hand: the L1 re-fetched S210/S211/S224 and
refabricated rows were refused (`corpus/lessons/round-63.md:12`). The proposal mechanizes that
check for the registry population. Not routed for round 64: the freeze's inherited routed
defects (C1 provenance, stale calibration row, MT20/MT21 controls, self-certification, idle
outcome, reused --work, tally 56-63) do not include it; the "quote floor" in MT20 is the r63
C2 registry's 8-char quote rule (`round63-c2-counter.py:293-294`), a different object.

### Fit to this round and the lane province

- Axis: calibration — round-64 C2 counts "mismatches between the lane's self-description and
  observed repo state". A SOURCES row whose located quote no longer sits at its cited anchor is
  precisely that class, and with retained bytes it is checkable against **repo state alone**
  (no network, deterministic, host-safe).
- Province: the `sources-registry` capability (round 10) whose rows are local-serving /
  endpoint-health evidence (llama.cpp pinned code rows; now the procfs man-pages backing C1's
  request-plane claim).
- No collision with the frozen round-64 work: C1's delta is the v3 tool + `round64-c1-counter.py`;
  C2's fix set is the SCORECARD round-64 canonical list, `capability-claims-r64.tsv`, the
  reconciler conjunct, the shortcut-tally 56-63 reader and `round64-c2-counter.py`
  (`controls/freeze.txt`). An anchor re-open tool is in neither.

### What the lane would land

Following the r46 precedent (`4a2a4d55`: "append-only-audit tool (C2 capability,
considerthese 2026-10-26 proposal 1)"):

1. **Calibration capability + tool** (executor-seat work, e.g. `tools/sources-anchor-recheck.py`
   + counter): for every SOURCES row whose anchor cell retains fetched bytes (`retained at
   <path>` + sha256), re-derive the located quote from the retained bytes at the cited position
   using the existing STRONG/WEAK line grammar; verdicts `holds | drifted | todo` per row; `todo`
   rows never credited. Counter: a planted +2-line anchor shift in a scratch copy flips the row's
   verdict while the unmutated run stays true (printer control: a run that re-hashes bytes but
   never relocates the quote must be rejected). First population: S529–S532.
2. **QUALITY criterion** in `corpus/QUALITY.md`: a SOURCES row's located quote must sit at its
   cited anchor in the row's retained bytes; new rows re-open at landing and every recheck
   re-opens (extends KQ36, which re-runs only when the *source* changes, to anchor positions).
3. **Lesson** in `corpus/lessons/round-<N>.md` and the SKILL registry cell, citing
   `considerthese/2026-10-24.md` + 2026-10-24 — the file+date citation pattern the lane already
   used for the r46 tool.

## Proposals already implemented (grep/git evidence)

| File | Proposal | Landed as | Round (commit) |
|---|---|---|---|
| 10-19 #2 | served-id normalization negative fixtures | `tools/kama-probe.sh` `normalize_id`/`unresolvable-id` (round 1, `c6199a25`); `tests/probe-verdicts/ReadyControls.json`, `LoadingRace.json` (`expect-gguf-path-basename`, symmetric strip); graded fault controls round 17 | 1, 16–18 (`b8e485cc`, `54a29268`) |
| 10-19 #3 | FOREIGN_SERVICE fingerprint mini-corpus | `tests/probe-verdicts/ForeignControls.json`, `EnvelopeShapes.json`, `NonLoadingStatuses.json`, `NearMissTriple.json` (Jetty html-non-model, openmetrics, schema-unrecognized, non-2xx envelopes); hardened r17–18 | 16 (`b8e485cc`) |
| 10-19 #4 | inherited vs effective URL observation | **not implemented — adjudicated out of province**: hand-off rows `…/round-16/build/advice/ConnectKagi.md:118`, `round-17/.../ConnectKagi.md:116` ("effective `LLAMA_CPP_BASE_URL` requires kagi; kama reports the file-level pin only"); `registry/endpoint-consumers.tsv:35` note. Re-proposing would re-open settled arbitration | — |
| 10-21 #3 | K05 readiness note | withdrawn by author (`2026-10-22.md` note); substance landed via r25 C2 + r42 engine-side K05 entry | — (`dd9f5dc6`) |
| 10-22 #1 | author-vs-outside verdict tables | adopted inside `considerthese/` daily files from 2026-10-23 on (process-level, no lane surface) | — |
| 10-22 #3 | between-round drift watch for instruments | partial: KQ36 (r25), `tools/prereg-time-check.py` (r26), `tools/release-recheck.py` + `tools/pin-trigger-consumed.py` (r44), `tools/round54-cited-path-check.py` (r54) — landing-time + release-triggered only | 25, 26, 44, 54 |
| 10-23 #1 | shortcut-class ledger across rounds | `tools/shortcut-tally.py` + `corpus/knowledge/echo-discriminating-counters.md`; r64 freeze extends the tally reader to rounds 56–63 | 48 (`c4b2175d`) |
| 10-23 #2 | scoring-before-amendment timing | `tools/prereg-time-check.py` (receipt r45 D2) | 26 (`7f84cd0e`) |
| 10-23 #4 | mark in-flight rounds + tip read | adopted in daily files from 2026-10-24 on ("Tip read for this pass: …") | — |
| 10-24 #1 | outside verdicts vs score movement | `registry/verdict-ledger.tsv` + `tools/round44-verdict-ledger-audit.py`; `registry/claim-outcome-ledger.tsv` + `tools/round45-claim-outcome-audit*.py`; `tools/manifest-crosscheck.py` | 44–45 (`ef76777e`, `0718b6ab`) |
| 10-24 #3 | "prepared, not dispatched" ledger | partial: `tools/planned-pointer-check.py` (SCORECARD Planned-pointer + dangling measured-results refs); the prepared-waves ledger itself remains open (meta/process) | 44 (`ef76777e`) |
| 10-24 #4 | attempts/restarts per round | largely covered by `tools/seat-yield.py` (seats launched/landed/failure reasons) | 45 (`0718b6ab`) |
| 10-25 #1 | recompute cited digests / S-ids | `tools/digest-ledger.py`, `tools/hexrun-census.py` | 42–43 (`dd9f5dc6`, `c328cadf`) |
| 10-25 #2 | watch version pins for releases | `tools/pin-watch.py` ("is considerthese/2026-10-25.md proposal 2" per `2026-10-26.md` lesson 2) | 41 (`24aa1d34`) |
| 10-25 #3 | ledger of rejected staged items | `registry/staged-refusals.tsv` | 43 (`9651a4e0`) |
| 10-25 #4 | seat yield per wave | `tools/seat-yield.py` | 45 (`0718b6ab`) |
| 10-26 #1 | flag deletions in append-only files | `tools/append-only-audit.py` — commit cites "considerthese 2026-10-26 proposal 1"; counters `round46-append-audit-check.py`, hardened v2–v6 r47–52 | 46 (`4a2a4d55`) |
| 10-26 #3 | count counters a shortcut can satisfy | `tools/shortcut-tally.py` | 48 (`c4b2175d`) |
| 10-26 #4 | report pin gap (newest tag, releases above pin) | `tools/pin-watch.py` substance; the daily-file line is considerthese-side | 41 (`24aa1d34`) |

Not implemented and not picked (reflection-process proposals without a tools/corpus surface, or
weak fit to round-64 claims/province): 10-20 #1 window-completeness, 10-20 #2 stagnation tracker,
10-20 #3 promise-inventory-vs-tests (only per-tool kin `tests/report-audit/promisor-grid.py` r24,
KQ18 r15), 10-21 #1/#2/#4, 10-22 #2/#4, 10-23 #3 true-but-unadmitted count, 10-24 #3 remainder,
10-26 #2 proposal-outcome table (adopted only inline).

## Confidence and unknowns

- Observed: every path/line/commit cited above was read this pass at the working tree of
  `/home/vgpnk/Projects/shokunin/kama-shokunin` (near-freeze tip `f6a4ea9a` lineage); creation
  rounds from `git log --diff-filter=A`.
- Verified-by-absence: no SOURCES anchor re-open tool exists in `tools/` — survey covered all
  30 files matching `SOURCES.md|quote|cited` plus the full `tools/` listing. [INFERENCE] no
  fleet-level consumer of the `180d` recheck cell exists (fleet repo is out of my bounds).
- The pick does not touch the frozen C1/C2 instruments; it is advisory leaf output only.
- One-line summary: `considerthese/2026-10-24.md:29 proposal 2 — SOURCES quote-anchor drift
  watch — still unimplemented; nearest kin tools/release-recheck.py (r44) is llama.cpp
  release-scoped only; first uncovered population = S529-S532 (recheck=180d, retained bytes
  in-repo).`
