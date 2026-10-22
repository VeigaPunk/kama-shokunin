Verdict: defect found. The census and the old-row log hold (105 to 113 rows; validate and census exit 0 at the lane, at pinned fa3b62ae and at base 147f5bdd; selftest 96 killed, 0 survived), but the new rows and the knowledge entry carry one unregistered-source citation, one overstatement that the entry's own raw log contradicts, and contract-form gaps (F1 to F10; F11 and F12 are informational).

# RerunCensus — SOURCES census and contract, kama round 25, attempt 2, wave 2

## Scope and method

- Target: `corpus/SOURCES.md` at lane master tip fa3b62ae. Lane HEAD is 46be41c, which adds four wave files and no lesson or registry change. `git log fa3b62ae..46be41c -- corpus/SOURCES.md` is empty. The lane working-copy `corpus/SOURCES.md` is byte-identical to fa3b62ae (`cmp` exit 0).
- Base: round start 147f5bdd (registry 335 lines, sha256 9294b167...). Tip: fa3b62ae (343 lines, sha256 45810d49...).
- Contract: `CORPUS.md` lines 64 to 129 (SOURCES rules), 131 to 148 (census), 163 to 175 (kaika rules on knowledge provenance, mistake classes).
- Source re-open: curl fetched 9 files at llama.cpp 704366d76f8748cf9ad3df62a464bfcc8d1ae6ad from raw.githubusercontent.com (the 8 rows S106 to S113, plus `common/common.h`, which a knowledge line cites). All 9 exited 0.
- Pinned trees were extracted with `git archive` into scratch. No clone, no git write, no jj command.

## Census: commands and exit codes

Assigned commands, run at the lane root: `scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama` and `... census --root /home/vgpnk/Projects/shokunin kama`. The same commands also ran against pinned extractions (`--root` pointing at scratch trees with `kama-shokunin/` as the lane directory). The script ran with its default `--today`, which is the UTC date 2026-10-22.

| run | root | exit | output |
|---|---|---|---|
| validate (assigned) | lane `/home/vgpnk/Projects/shokunin` | 0 | 29 W04 lines and `kama ok` (30 lines), stderr 0 bytes |
| census (assigned) | lane | 0 | `kama rows 113`, tier A 108 / B 2 / C 3, mined 94 / queued 8 / rejected 11, missing 0 |
| validate | pinned fa3b62ae | 0 | identical to the lane run except the path on the `ok` line |
| census | pinned fa3b62ae | 0 | identical to the lane run (`diff` exit 0) |
| overdue | pinned fa3b62ae | 0 | 113 cadence lines, no overdue row |
| validate | base 147f5bdd | 0 | 25 W04 lines and `ok` (26 lines) |
| census | base 147f5bdd | 0 | `kama rows 105` (round-start count confirmed), tier A 100 / B 2 / C 3, mined 86 / queued 8 / rejected 11 |
| selftest | fleet script, TMPDIR in scratch | 0 | 96 killed, 0 SURVIVED, `selftest ok` |

No E-code and no W01 to W03 code appears. W04 (same URL, different scope) fires on S108, S109, S110 and S112 only. Those four warnings match the lesson's list and the earlier rows it names: S037/S043, S042/S060, S054/S056 and S035. The W04 list at base has 25 entries; tip adds exactly those four.

The fleet script sha256 was 3fb72615... at the time of the run. The script reads the lane working copy, which equals fa3b62ae for this file.

The frozen census in CORPUS.md (lines 131 to 148) was re-implemented in Python with the same regexes and column rules, because I did not run its shell awk one-liners verbatim. The re-implementation agrees with the script on every count: 105 rows base, 113 rows tip, 0 malformed rows, 0 duplicate ids, 0 enum violations, 0 missing mined `used-by` paths.

## Old-row changes (CORPUS rule 2)

- A full diff of base to tip has two blocks only. One is S060's `used-by` on `corpus/SOURCES.md:72`. The other is an 8-line insert at lines 118 to 125 (the new rows). Every other line of the file is byte-identical, including Paths, Search log, Leads and the round sections.
- S060 `used-by` changed from `corpus/knowledge/gguf-declared-identity.md, corpus/lessons/round-20.md` to the same list plus `corpus/knowledge/context-capacity.md`. Lesson lines 32 to 35 log the same old and new strings. The check passes exactly (`logged_old_new_match_census_change: true`).
- No `status`, `recheck` or other cell changed on any old row. The lesson's "No status or recheck cell changed" (lesson:35) holds. Tier and status counts moved only by the eight new rows (tier A 100 to 108; mined 86 to 94).

## New rows against the contract

Passed:

- Ids S106 to S113 are the next unused ids after S105, with no gap and no reuse. Each row has 11 cells and no stray `|`.
- `kind` is `code` for seven rows and `docs` for S112. Every tier is A, which is allowed for source code and official docs in scope. No community row sits at A.
- `opened` is 2026-10-22 on all eight rows. `recheck` is `on-release`, a valid symbolic cadence.
- `status` is `mined` on all eight. Each `used-by` path (`corpus/knowledge/context-capacity.md`) exists. The entry cites every new id: S106 4 times, S107 4, S108 3, S109 2, S110 3, S111 2, S112 3, S113 2 (and S060 4).
- All source URLs are canonical blob URLs pinned to 704366d76. For the four shared llama.cpp URLs (`server.cpp`, `server-context.cpp`, `arg.cpp`, `README.md`), every row that names the file carries the same sha256 (for example `server-context.cpp` is `dd1de0f2...` in S042, S060 and S109).
- The lesson Gate matches the registry: all eight Gate URLs equal the row URLs. The status sentence (lesson:31 to 35) matches the tip registry.

Gate re-open (non-author sample, all rows):

- All 8 anchor sha256 values equal the sha256 of the fetched bytes (S106 1f83da2a..., S107 2a25e556..., S108 21439622..., S109 dd1de0f2..., S110 bf4c58c1..., S111 d10ea1ff..., S112 714c067b..., S113 d0739eaf...).
- All 11 Gate quotes were found at the stated lines in the fetched bytes. Quote lengths run from 3 to 18 words (limit 25). The S108 quote joins source lines 172 and 173 into one string; the located lines are correct.
- Spot-checked the cited lines behind the teaches clauses: fit.cpp 195–198, 266–273, 393–394, 426–430 (S106); llama-context.cpp 219, 377–393, 409–417 (S107); server.cpp 169–174, 179–186 (S108); llama-kv-cache.cpp 84, 142–145, 301–304 (S113); README 50, 165, 169, 177, 671, 683, 927, 928, 999, 1064, 1304 (S112). The cited lines exist and say what the rows say. I did not check every condition in each clause (for example S108's non-router guard, or S112's full list of endpoint fields).

## Findings, by severity

### F1 — Medium: unregistered source cited under an unrelated row

- Evidence: `corpus/knowledge/context-capacity.md:60` reads "Giving `-np` keeps the default split cache (S110; common.h 580)". S110's anchor (`corpus/SOURCES.md:122`) covers `common/arg.cpp` only. `common.h` appears 0 times in `corpus/SOURCES.md`. The entry's `source:` header (line 1) does not list it. Fetched `common/common.h` line 580 reads `bool kv_unified        = false; // enable unified KV cache` (sha256 8bcc5708c856653b0094ba312030df9c2f43ec2703e8ad78474fd4339d2540a9). The claim is true; the attribution is not.
- Contract: CORPUS.md:163–166 (a knowledge entry cites the S### row for an external source); CORPUS.md:112–115 (a row is a claim, with a Gate quote).
- Smallest correction: either add a row for `common/common.h` (a new id, which append-only rule 2 allows, CORPUS.md:116–118) with a Gate row and the sha256 above, and list it in the `source:` header; or delete "common.h 580" from line 60 and keep the claim on arg.cpp lines.

### F2 — Medium: "only trace" overstated, contradicted by the entry's own raw log

- Evidence: `corpus/knowledge/context-capacity.md:49–51`: "K5 shows the cap: … and the only trace is a log warning `n_ctx_seq (4096) > n_ctx_train (2048)`". The cited raw log `.ufo/waves/round-25/final/raw/K5.server.log` contains that warning at lines 295 and 828, and also:
  - line 1083: `W srv load_model: the slot context (4096) exceeds the training context of the model (2048) - capping`. Source: `tools/server/server-context.cpp:1375` (SRV_WRN in the cap block at 1353–1378).
  - line 1084: `I srv load_model: initializing, n_slots = 1, n_ctx_slot = 2048, kv_unified = 'false'`. Source: `server-context.cpp:1392`.
  Neither 1353–1378 nor 1392 lies in any registry anchor. S060's anchor is 4654–4663, 5183–5188 and 5229–5245 (`SOURCES.md:72`).
- Contract: CORPUS.md:39–41 (a negative claim carries the search that produced the absence). No sweep is recorded.
- Smallest correction: delete "only", or list the traces with their lines. Citing the server-side lines properly needs a registry row (see F3).

### F3 — Low: S060 anchor does not cover lines the entry cites

- `context-capacity.md:45` cites `server-context.cpp 1437` (`slot.n_ctx   = n_ctx_slot();`, observed) under S060. The S060 anchor does not include 1437, nor the cap block (1353–1378) or 1392 from F2.
- Rule 2 (CORPUS.md:116–118) forbids editing the anchor of a row in place.
- Smallest correction: a new row for the same URL with a new scope covering 1353–1378, 1392 and 1437 (W04 warning only, no E04), or state those lines as unanchored in the entry.

### F4 — Low: S107 "never clamp" can be read as a claim about the served per-slot value

- `corpus/SOURCES.md:119` teaches: "per-slot values below or above n_ctx_train only log, never clamp." Observed: `llama-context.cpp` lines 409–417 only log, so the claim holds for that file. The served per-slot ceiling is capped at server level (`server-context.cpp:1353–1378`, K5.server.log:1083). [INFERENCE] A reader of the knowledge entry, which says the ceiling is capped by the training context, will see a contradiction.
- Smallest correction: say "llama_context only logs and never clamps." In-round this is an in-place edit; after landing it needs a supersedes row (CORPUS.md:116–118).

### F5 — Low: line range drift

- `context-capacity.md:168` cites "S107 4113-4117". The S107 anchor (`SOURCES.md:119`) gives 4114–4118. Observed: line 4113 is blank and 4118 (the closing brace) is outside the citation.
- Smallest correction: change the citation to 4114-4118. This is a knowledge-file edit, not a registry edit.

### F6 — Low: anchor cells omit the revision on 7 of 8 new rows

- `corpus/SOURCES.md:118, 119, 120, 121, 123, 124, 125` carry a raw sha256 but no commit or release. The commit appears only in the source cell's URL. S110 (line 122) names "at 704366d76…". The old-row precedent is S060's anchor ("… at 704366d76; sha256 …", line 72).
- Contract: CORPUS.md:99–100 (anchor = exact location plus revision: version, commit or publication date).
- Smallest correction: add "at 704366d76" to each of the seven anchor cells. If fa3b62ae counts as landed, this needs supersedes rows (CORPUS.md:116–118) and not in-place edits.

### F7 — Low: teaches cells run past "one grounded learner benefit"

- Word counts: S106 66 (line 118), S107 70 (119), S108 32, S109 51 (121), S110 30, S111 34, S112 170 (124), S113 53 (125). The eight old rows have a median of 25 words and a maximum of 50. S112 lists seven flags, fields and endpoints.
- Contract: CORPUS.md:101–102.
- Smallest correction: one benefit per cell, with the enumerations moved to the knowledge entry. Same landing rule as F6.

### F8 — Low: negative claims with no recorded sweep; no Search-log note

- `context-capacity.md:62–63` "S112 is the only README sizing promise"; `:135` "No field of `/props`, `/slots` or `/v1/models` carries the KV pool or the cache layout"; `SOURCES.md:124` teaches "The only pool-sizing promise in the README is …".
- Contract: CORPUS.md:39–41 (sweep), CORPUS.md:126–128 (rule 5: each bounded search goes in the Search log). The Search log section (`SOURCES.md:134–145`) has no round-25 note.
- My sweep, on the README fetched at 704366d76 with the pattern `kv|sized|pool`: the pool-sizing sentence is at README line 165 only. README line 50 sizes the prompt context and line 168 sizes the cache in MiB. The README and /props field claims hold for pool sizing, but "sizing" is ambiguous.
- Smallest correction: record the sweep command and its result in the Gate or a Search-log note, and say "pool-sizing" wherever the claim is meant.

### F9 — Low: lesson Gate has no spot-check result; access date is collective

- CORPUS.md:19–20 requires a lesson `## Gate` with candidates, admitted, rejected with reasons, and a spot-check result. The pinned lesson has the admitted table (lines 20 to 29) and one rejected reading (lines 40 to 42). It has no spot-check line.
- Lesson line 15 gives the access date collectively ("All eight rows were opened on 2026-10-22"). The `opened` cells agree (`SOURCES.md:118–125`).
- Smallest correction: add a spot-check line. This report can be cited for it: 8 of 8 anchor digests match the fetched bytes, and 11 of 11 quotes sit at the stated lines.

### F10 — Low: Mistakes classes outside the CORPUS vocabulary

- CORPUS.md:173–175 gives the vocabulary as `vacuous`, `survivor`, `stale-premise`, `reference-drift`, `number-drift`, `scope`, `attribution`, `landing`, `provider`.
- Pinned lesson (lines 48 to 52) uses "stale-anchor" (line 48), "survival" (49), a row with no class label ("counter accepted a wrong value", 50), "chronology" (51) and "false timestamp repeated" (52). The working copy adds "misroot" and "axis misfiled" (see F11).
- [INFERENCE] Closest vocabulary terms: stale-anchor to reference-drift; survival to survivor; false timestamp to number-drift; counter accepted a wrong value to vacuous. Chronology and axis misfiled need the L1's judgement.

### F11 — Info: uncommitted working-copy edits to the lesson

- `.ufo/waves/round-25/a2-falsify/out/RerunCensus/lesson-worktree.diff` (30 changed lines). Three hunks:
  - lines 21 to 27: the S108 Gate row splits its joined quote into three single-line quotes. This is an improvement over pinned lesson:24.
  - lines 48 to 53: the Mistakes table gains "misroot" and "axis misfiled" rows, and the chronology and false-timestamp rows are edited.
  - lines 85 to 100: the C1 axis-fit paragraph is rewritten.
- The Gate statements (lesson:15–17) and the old-row log (lesson:31–38) are unchanged. The census does not depend on the lesson text. If the working copy lands, F9 and F10 apply to the new text too.

### F12 — Info: `source:` header convention is mixed

- `context-capacity.md:1` lists S ids, file paths and the commit, but no URLs or anchors. CORPUS.md:163–166 asks for the S row "alongside the URL and anchor". `gguf-declared-identity.md:1` has the same shape, while `runtime-health-surface-matrix.md:2` gives URLs. Pick one convention.

## Residual risk and verification gaps

- Teaches claims were checked at the lines listed above, not for every clause. S109, S110, and S111 teaches were not checked beyond their quoted lines. Peer seats KamaR25a2.ReopenS109 and KamaR25a2.ReopenS113 are re-opening those two sources in parallel; I did not use their results.
- The K5 raw log was read only at its `n_ctx` and capping lines. The README sweep is my regex over the fetched 2402-line file, not a full read.
- The frozen CORPUS census was re-implemented in Python (same regexes and column rules); its shell awk one-liners were not run verbatim.
- `--today` was the default UTC date (2026-10-22) on every run.
- The lane working copy is still changing (F11). The results above are for committed fa3b62ae bytes; SOURCES.md is identical in both.
- The lesson's "fresh fetch" statement (lesson:15–17) is supported only by the digest match.

## Tools, installs, and boundaries

- No tools were installed or updated. RULES.md was read first.
- Versions used: gawk 5.4.1 (/usr/bin/gawk), Python 3.14.8 (/usr/bin/python3), bash 5.3.20, curl 8.23.0. `sha256sum --version` printed `sha256sum 0.8.0`; no recorded value comes from that binary (digests are Python hashlib SHA-256).
- No llama-server child was started. No port was opened. The only network use was the nine curl fetches from raw.githubusercontent.com listed above.
- Git was read-only against the lane: `archive`, `show`, `log`, `diff <rev> <rev>`, `merge-base --is-ancestor`, `rev-parse`, `cat-file -t`. No clone, add, checkout, reset, stash or commit. No jj command was run at the fleet root or in the lane.
- The fleet script was run from `/home/vgpnk/Projects/shokunin/scripts/` (read-only; writes only to stdout and the scratch TMPDIR). Nothing was written to the fleet root.

## Files written

Under `.ufo/waves/round-25/a2-falsify/out/RerunCensus/` (created by this seat):

- `lane-validate.out`, `lane-validate.err`
- `lane-census.out`, `lane-census.err`
- `tip-validate.out`, `tip-validate.err`
- `tip-census.out`, `tip-census.err`
- `tip-overdue.out`, `tip-overdue.err`
- `base-validate.out`, `base-validate.err`
- `base-census.out`, `base-census.err`
- `selftest.out`, `selftest.err`
- `contract_check.py` (the check script; reads scratch and lane files only)
- `contract-check.json` (its output: hashes, registry diff, frozen census, Gate checks, knowledge citations, fetched-source digests)
- `lesson-worktree.diff` (pinned fa3b62ae lesson against the lane working copy)

Also created: `.ufo/waves/round-25/a2-falsify/advice/` (this report).

Scratch, not artifacts: `/fast/scratch/hyaku/kama-r25a2w2/RerunCensus/` (`base/`, `tip/`, `src/`, `tmp/`, `fetch-manifest.json`).

Report: .ufo/waves/round-25/a2-falsify/advice/RerunCensus.md
