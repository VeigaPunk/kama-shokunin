VERDICT: confirm - KQ22 guard exits 0 on all 3 consecutive SOURCES.md pairs in 8bf99cae..37bd4c5b (0 violations); 2 routed record defects the guard cannot see

Scope: KQ22 (`corpus/QUALITY.md:123` @37bd4c5b: "Round end runs `python3 tools/sources-append-only.py --from A --to B` over every consecutive commit pair touching `corpus/SOURCES.md` in the round … each exit 0."). Scratch clone `/tmp/kama-r20-SourcesGuardR19/lane` @37bd4c5b (deleted after the run). Guard `tools/sources-append-only.py` sha256 `4d786856…9c2d`, blob `cd26e6f7` at both 8bf99cae and 37bd4c5b (`git log 8bf99cae..37bd4c5b -- tools/sources-append-only.py` exit 0, empty). Python 3.14.8, git 2.56.0. Every command and its exit/stdout: `.ufo/waves/round-20/build/out/SourcesGuardR19/receipts.txt` (sha256 `44aae953…`), JSON `guard-pairs.json` (`c67d31a9…`), oracle `kq22-bytecheck.py` (`14a7aebf…`).

## Population
- `git log --format=%H 8bf99cae..37bd4c5b -- corpus/SOURCES.md` exit 0 -> `5b108c1a`, `7229fa95`; identical with `--full-history`; `git rev-list --merges --count` = 0 (linear).
- SOURCES.md blob: `1e09b779` (8bf99cae) -> `7cca031c` (7229fa95) -> `166268c6` (5b108c1a and all 11 later commits through 37bd4c5b).

## Guard exits (`--repo` scratch; the literal default-`--repo` form, read-only `git show` on the lane, gave the same three exits)
| pair | exit | stdout |
|---|---|---|
| 8bf99cae -> 7229fa95 | 0 | `added S057 (allowed)` / `no append-only violations` |
| 7229fa95 -> 5b108c1a | 0 | `no append-only violations` |
| 5b108c1a -> 37bd4c5b | 0 | `no append-only violations` (same blob) |
| span 8bf99cae -> 37bd4c5b | 0 | `added S057 (allowed)` |
- All 13 parent->child pairs `C^ -> C` in the range: exit 0 each.
- Fail-capability at these bytes: `--from b8e485c --to ccc4bb3` exit 1, `VIOLATION S041` on `anchor` and `teaches` (KQ22's named control). `--selftest` exit 0, `42/42 selftest cases passed`.
- `--json`: `violations: []` for all four; `added: ["S057"]` only on pairs that include 7229fa95.

## Independent oracle (not guard code: raw bytes, no strip, split on every `|` like the census)
- `python3 -B kq22-bytecheck.py --repo <scratch> 8bf99cae:7229fa95 7229fa95:5b108c1a 5b108c1a:37bd4c5b 8bf99cae:37bd4c5b` exit 0: rows 56 -> 57 -> 57 -> 57, removed none, immutable raw-byte changes 0, so no whitespace edit hid behind the guard's strip (docstring `:45-46`, "compared verbatim after leading/trailing whitespace strip").
- Its own controls: `b8e485c:ccc4bb3` exit 1 (S041 `anchor`, `teaches`, not whitespace-only); unreadable rev exit 2 (error, not a verdict).
- Only mutable change in the range: S057 `used-by` at 7229fa95 -> 5b108c1a.

## Routed defects (none is a guard violation)
R1 (medium, rule 2 logging half). `git diff -U0 7229fa95 5b108c1a -- corpus/SOURCES.md` exit 0 shows one line, `@@ -69 +69 @@`. S057 `used-by` changes ` corpus/lessons/round-19.md, registry/required-citations.json ` -> ` corpus/lessons/round-19.md, SCORECARD.md `.
- The cell is allowed to change, but `CORPUS.md:116-117` (fleet copy, read 2026-10-21) also requires: "each change is logged old→new in the round lesson".
- No such log exists. `git grep -n used-by 37bd4c5b -- corpus/lessons/round-19.md` exit 0 returns only `:33`. LOG.md's round-19 entry (`:1137-1174`) mentions S057 only at `:1153`. The verifier spot-check has no used-by record.
- The tip lesson still states the old value, `round-19.md:33-34`: "`used-by` is this lesson and `registry/required-citations.json` (the pin's identity boundary)." `git log -S` shows the line was added at 7229fa95 and never revised.
- This is KQ22's add-then-edit case: the span pair reports only `added S057`, and the oracle's span shows no mutable change.
- Fix: append an old->new line in the round-20 lesson. Never rewrite `:33`.

R2 (calibration, record gap). No committed record shows the round-19 KQ22 round-end run.
- `git grep -n -E 'sources-append-only|KQ22' 37bd4c5b -- corpus/lessons/round-19.md corpus/lessons/round-19-verifier-spotcheck.md .ufo/waves/round-19/evidence` exit 1 (no match).
- `git grep -n sources-append-only 37bd4c5b -- LOG.md SCORECARD.md` matches only `LOG.md:1015` and `:1064`, both before round 19.
- Round-19 advice had already routed it: `QualityCriteria.md:44` says "run sources-append-only over each committed SOURCES pair".
- [INFERENCE] The run was not performed at round-19 end. `receipts.txt` can be committed as the retrospective KQ22 receipt, labelled retrospective.

R3 (low, carried-item label). "S057 mid-table insert" is wrong.
- S057 was appended after S056 as the last row: hunk `@@ -68,0 +69 @@`, oracle `appended_after_all_carried_rows: true`, and at tip `:70` is blank and `:71` is `## Paths`.
- The S051 staleness is a +1 shift of the prose below the table. `round-18.md:285` cites `corpus/SOURCES.md:209-213`. That S051 text sits at 209-213 @8bf99cae and at 210-214 @37bd4c5b (sed reads).
- [INFERENCE] Every future row append shifts those anchors again.

## Residual risk / gaps
- The guard proves only cell immutability (stripped). It does not check rule 2's logging, row placement or raw bytes; the oracle covered raw bytes for this range only.
- No `lsp` device is mounted (`read xd://lsp` -> "No such tool"), but none was needed: no code diff was reviewed.
- Tools installed/updated: none. Lane not modified; writes were only this report and three new files in `out/SourcesGuardR19/`. No processes left running.
