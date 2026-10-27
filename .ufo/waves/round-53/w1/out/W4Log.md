# W4Log — round-53 LOG.md draft

Verdict: drafted and grounded — the append-ready round-53 entry is at `.ufo/waves/round-53/w1/out/W4Log/log.md`; every hash, leg, count and line anchor in it was re-read from the lane's committed objects and receipts, and the one count that differs from the dispatch brief (ledger rows) is reported below as F1 rather than smoothed into the draft.

## Deliverable

| Path | What |
|---|---|
| `.ufo/waves/round-53/w1/out/W4Log/log.md` | the round-53 entry, shaped like the round-52 block (`LOG.md:2424`–end): C1, C2, the R1 closure, freeze, build, wave, re-verification, measured pointer, routed defects, lesson |
| `.ufo/waves/round-53/w1/out/W4Log/{c1-build.out,c2-build.out,base.c1.out,base.c2.out,prereg-time-check.out}` | byte copies of every receipt the draft cites |

Measured values are a pointer to `SCORECARD.md` §Round-53 measured results, as the seat spec requires; the draft carries no measured number for either claim.

## Evidence

All commands run read-only against the lane at `/home/vgpnk/Projects/shokunin/kama-shokunin`; no counter was run (the entry cites the L1's build receipts, and re-running a counter was not this seat's task).

1. **Claim / freeze / build anchors.** `git log --oneline -1 d01b2b6d…` → `d01b2b6d round-53: freeze - preregistration, C1/C2 counters, base controls, start census`; `git log --oneline d01b2b6d..c22602bd` → one commit, `c22602bd round-53: build - per-mapping code identity (C1), cited-path corrections (C2), S506-S509, lesson` (exit 0). `git show --stat c22602bd` → 12 files, +2980/−2 (`tools/kama-llamacpp-live.py` +105, `tools/kama-live-replay.py` +93, `corpus/SOURCES.md` +4, `registry/cited-path-corrections.tsv` 27, `SCORECARD.md` +4, `SKILL.md` 4 (+2/−2), `corpus/lessons/round-53.md`, the four `c1/` copies, the freeze receipt).
2. **Counters are the frozen bytes.** `git show d01b2b6d:tools/round53-replay-code-audit.py | sha256sum` → `1a7a1442…75d8f`; `…round53-cited-path-check.py` → `1afb8b9d…e3080`; both equal the preregistration's `counter_sha256` (`grep -o '"counter_sha256": …' preregistration.json`).
3. **Freeze time.** `.ufo/waves/round-53/freeze/prereg-time-check.out`: `committer_time=2026-10-27T03:02:49-03:00`, `ok line 6: 2026-10-27T06:02:12Z (at/before commit)`, `RESULT pass`, `exit=0`.
4. **Base controls** (`controls/base.c1.out`, `controls/base.c2.out`, both at `--tip 4229ea1b…`): `bind=1 sealed=1 code=0 teardown=1 newrow=0 bound=3/3 sealedruns=3/3 coderuns=0/3 met=False` exit 1, first failure `code: replay own_code 'None' is not verified with members`; `fixture=1 lane=0 scenarios=8/8 cited=679 unresolved=16 disclosed=0 undisclosed=16 bad=0 stale=0 dropped=0 met=False` exit 1, `grep -c '^detail: undisclosed'` = 16.
5. **Build receipts** (`measured/c1-build.out`, `measured/c2-build.out`, tip `c22602bd`): `bind=1 sealed=1 code=1 teardown=1 newrow=1 bound=3/3 sealedruns=3/3 coderuns=3/3 met=True` exit 0 with three `code bN: 8 archive files (8 executable ranges) byte-equal in /proc/<pid>/mem … 13 root-owned host files` lines, the eight `own_code` members, three sealed `/memfd:llama-server (deleted)` images (seals 15) and `newrow: 4 rows new since base; 1 name proc_pid_mem(5): ['| S506 |']`; `fixture=1 lane=1 scenarios=8/8 cited=682 unresolved=14 disclosed=14 undisclosed=0 bad=0 stale=0 dropped=0 met=True` exit 0.
6. **C2 build surface.** `git show c22602bd -- SKILL.md` → exactly the two in-place lines the brief names, `SKILL.md:113` (`scripts/local-helper.mjs` → `~/Projects/ufo-fsd-alpha/scripts/local-helper.mjs`) and `SKILL.md:895` (`tests/report-audit/…` → `tests/report-audit/`); `git show c22602bd -- SCORECARD.md` → `### Evidence-pointer corrections (round 53)` appended after the round-52 measured section (`SCORECARD.md:3027`). `awk -F'\t' 'NR>1 && NF>4 {print $3}' registry/cited-path-corrections.tsv | sort | uniq -c` → `7 never, 5 upstream, 1 deleted, 1 untracked, 1 fixed`.
7. **Replay reason codes** (used in the draft's C1 sentence): `grep -n 'code-mapping:' tools/kama-live-replay.py` → docstring `:81`–`:84` and raises at `:323`, `:327`, `:329`, `:333`, `:337` (`:digest`, `:not-a-member`, `:foreign`, `:unopened`, `:no-archive-library`).
8. **Motivating-evidence anchors:** `corpus/lessons/round-52-verifier-spotcheck.md:134` (R1), `:135` (R2), `:141` (R3), `:146` (R4); `SCORECARD.md:3018` `### Planned (round 53)`, `:3020` item 1, `:3021` item 2.
9. **Re-verification (freshness, no claim; my own run).** At 2026-10-27T06:15Z–06:16Z I fetched the four source URLs into scratch: the b11909 `ggml-backend-reg.cpp` is byte-identical to the committed copy (`sha256 1436b46bd1e8355345d454baa4b40069be73e9cb09a3a188d32426ea1e1037fe`); `grep -n` on it → comment at **491**, `get_executable_path()` at 401, `ggml_backend_load_best` at 480, `GGML_BACKEND_DIR` at 488–489; `awk 'NR==491' | wc -w` → 8 tokens including `//`, 7 words of quote. The three man7 pages carry the S506/S507/S508 quoted sentences (S506's HTML lays the link elements out with spaces — `open(2) , read(2) , and lseek(2) .`). `curl https://api.github.com/repos/ggml-org/llama.cpp/releases?per_page=5` → `b11913 2026-10-27T00:19:01Z prerelease=True`, then b11912/b11910/b11909 also prerelease: round-52's "b11913 upstream while b11909 stays a prerelease" still holds.

## Findings

**F1 (count wording, no defect).** The dispatch brief says the build lands 14 ledger rows; `registry/cited-path-corrections.tsv` carries **15** data rows (`awk -F'\t' 'NR>1 && NF>4' | wc -l` = 16 including the header). The counter explains the 14: `tools/round53-cited-path-check.py:239`–`:252` and `:354`–`:359` add a `fixed`-class row to neither `disclosed` nor `stale`, so the 14 disclosed tokens are the 14 non-`fixed` rows and the 15th (`tests/report-audit/…`, `fixed`) is the audit row for the in-place correction at `SKILL.md:895`, whose token is no longer cited at tip. The draft states it that way rather than as "14 rows". If the L1 prefers the brief's phrasing in `SCORECARD.md`, use: "14 disclosed citations in `registry/cited-path-corrections.tsv`, plus one `fixed` audit row for the in-place correction at `SKILL.md:895`". No file change proposed: the ledger and counter agree, the brief's number is the disclosed count.

**F2 (calibration stability, disclosed).** The two C2 runs were made against different fleet trees: `controls/base.c2.out` prints `fleet=bcc9bbd2ece8b659b7c5dd66802b4845fdedb434`, `measured/c2-build.out` prints `fleet=ee9f7341bd98de0fcd85f6c01f689301589b27e9`, and `git -C /home/vgpnk/Projects/shokunin merge-base --is-ancestor bcc9bbd2 ee9f7341` exits 0 (the fleet advanced with `ee9f7341 round-53: kama L0 question (ed135b3c restored history)`). So base and build were not resolved against the same fleet tree. This changes none of the observed numbers — the 16 base misses map one-for-one onto the 10 SCORECARD rows + 4 SKILL `upstream` rows + the `fixed` row + the no-row in-place fix — and the counter pins `fleet=` in every receipt, so the fact is disclosed rather than hidden. Worth one sentence in `SCORECARD §Round-53 measured results` ("the counter's fleet tip moved from `bcc9bbd2` at the base control to `ee9f7341` at the build; each receipt records it").

**F3 (observation, not a defect).** `pgrep -af llama-server` shows live servers under peers' scratch (`/fast/scratch/hyaku/kama-r53/K2Design/…` pid 2827397, `…/J4OmitLib/…` pid 2887411). None is mine; this seat started no server, ran no counter and opened no port.

## Out of scope here (L1 integration items)

- `SCORECARD.md` §Round 53 (attack results, "what `met=True` does not show") and §Round-53 measured results — the draft points at the latter and deliberately carries no value.
- The `**Round-53 integration:**` paragraph, the wave's routed defects and any `QUALITY`/`README`/`SKILL` registry rows.
- The wave's own seat results: at draft time `kama-r53-w1` (66 seats, spec `bc8e6e7f`) had nine seat output directories and was still running. The draft names the wave and leaves its findings to the L1.

## Scratch

`S=/fast/scratch/hyaku/kama-r53/W4Log` held the four fetches and a release-API response; `rm -rf "$S"` run before finishing. No clone was created, no `git` mutation anywhere, no tool installed.
