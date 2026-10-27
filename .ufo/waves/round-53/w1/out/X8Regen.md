# X8Regen — independent recomputation of the round-53 C2 cited-path misses

**Verdict: C2's measured numbers reproduce exactly under an independently written parser — 682 cited tokens (SCORECARD 471 / SHONEN 9 / SKILL 202), the same 14 miss keys at `c22602bd`, the same 16 at base `4229ea1b`, zero dropped SCORECARD citations — and every disclosure re-derives, except that the `untracked` row's note for `.ufo/watchdog.log` is factually wrong ("never committed": the fleet repo tracked it from `609ecb6e` until `7930399e`, 2026-10-26). The frozen class does not test history, so `met=True` is unaffected; the note is a documentation defect (finding X8-1).**

## 1. What I ran

All runs against my own shared clone (`$S=/fast/scratch/hyaku/kama-r53/X8Regen`), never the lane; the counter was imported read-only for comparison only.

```
git clone -q --shared /home/vgpnk/Projects/shokunin/kama-shokunin $S/lane      # exit 0
python3 regen-cited-paths.py --repo $S/lane \
  --tip c22602bd8d83ab26349d1087e916ca537ee4f9d1 \
  --fleet /home/vgpnk/Projects/shokunin --fleet-rev ee9f7341bd98de0fcd85f6c01f689301589b27e9 \
  --fleet-rev-secondary d2a6c59aaabcbde2d4a946c31d0276bb2c3d7887 \
  --base 4229ea1b9a789148dded1f159c20967d9a01373f \
  --counter $S/lane/tools/round53-cited-path-check.py \
  --json-out regen-build.json --channels-out regen-build-channels.txt     # exit 0
python3 regen-cited-paths.py --repo $S/lane \
  --tip 4229ea1b9a789148dded1f159c20967d9a01373f \
  --fleet /home/vgpnk/Projects/shokunin --fleet-rev bcc9bbd2ece8b659b7c5dd66802b4845fdedb434 \
  --json-out regen-base.json                                             # exit 0
```

Fleet revisions were taken from the receipts themselves (`c2-build.out` line 2: `fleet=ee9f7341…`; `base.c2.out` line 2: `fleet=bcc9bbd2…`), so the comparison is against the fleet the counter measured, not today's HEAD.

## 2. Parser rules (my own; written from the claim text, not from the counter)

| # | Rule |
|---|---|
| R1 | Surfaces `SCORECARD.md`, `SHONEN.md`, `SKILL.md` read with `git show <tip>:<surface>`. |
| R2 | A line whose `lstrip()` starts with ` ``` ` toggles a fence; fenced lines yield no citations (no unterminated fence occurred). |
| R3 | Every `` `…` `` span on a non-fenced line is a candidate; several per line are all checked. |
| R4 | Clean: strip whitespace, drop one leading `./`, drop trailing `,;`, cut `#fragment`, cut a trailing `:N` / `:N-M` / `:N,M` anchor (remember max N). |
| R5 | Path-like: non-empty, none of `` \t<>$=()|'" ``, and starts with a lane root (`.ufo/ tools/ tests/ corpus/ registry/ plans/ considerthese/`), a fleet root (`scripts/ templates/`) or equals a lane top-level file. |
| R6 | `{a,b}` expands recursively; a citation misses when any expansion misses. |
| R7 | *(extra)* zero-padded numeric ranges (`M01..11`) expand (`M01…M11`); checked as an advisory channel, not folded into R6. |
| R8 | Resolve against `git ls-tree -r --name-only` — glob (`* ? [`) via `fnmatch`, trailing `/` by prefix, plain file by membership, otherwise by dir-prefix; lane tree first, then fleet tree. |
| R9 | A resolved plain file with an anchor misses as `beyond-eof` when its blob has fewer lines than max anchor. |

Misses are raw (no ledger consulted). Two advisory channels look for forms R5 rejects: **A** spans rejected for syntax characters, with the embedded root-path re-tested; **B** path-like runs on non-fenced lines with every backtick span blanked out.

## 3. Reproduction, key by key

```
tip=c22602bd… fleet=ee9f7341… cited_tokens=682 miss_tokens=14
base=4229ea1b… base_miss_tokens=16
dropped SCORECARD tokens base->tip: 0 []
secondary fleet=d2a6c59… miss_tokens=14; only-at-primary=[]; only-at-secondary=[]
counter unresolved=14 only_mine=[] only_counter=[]
```

Full token-set equality, not just the misses (my module vs the counter's own `survey()`, same clone, same fleet revision):

```
SCORECARD.md mine 471 counter 471 only_mine [] only_counter []
SHONEN.md    mine   9 counter   9 only_mine [] only_counter []
SKILL.md     mine 202 counter 202 only_mine [] only_counter []
total        mine 682 counter 682
```

Base: my 16 miss keys equal the 16 `detail: undisclosed` keys of `controls/base.c2.out` (`equal=True`); `base − tip` is exactly the two in-place SKILL corrections (`` SKILL.md `scripts/local-helper.mjs` ``, `` SKILL.md `tests/report-audit/…` ``); `tip − base` is empty. The 14 also equal the ledger's 14 non-fixed rows exactly (`tip-not-in-ledger=[] ledger-not-in-tip=[]`). The ledger at the build has **15** data rows: 14 disclosure rows + 1 `fixed` row (the wave text's "14 ledger rows" counts disclosures).

My 14 (surface · line(s) · ledger class):

| # | Surface | Token | Lines | Class |
|---|---|---|---|---|
| 1 | SCORECARD.md | `.ufo/waves/round-14/frozen/before/tools/kama-ollama-evidence.py` | 491 | never |
| 2 | SCORECARD.md | `tools/server/server-schema.cpp` | 1471, 3029 | upstream |
| 3 | SCORECARD.md | `.ufo/waves/round-29/w1/out/ConfirmM01..11/` | 1503 | never |
| 4 | SCORECARD.md | `.ufo/waves/round-31/c2/c2-tip.json` | 1635, 1732 | never |
| 5 | SCORECARD.md | `.ufo/waves/round-31/sources/llama.cpp-704366d/utils.hpp` | 1741 | deleted `9874e455…` |
| 6 | SCORECARD.md | `.ufo/waves/round-999/count-c999.py` | 1844 | never |
| 7 | SCORECARD.md | `.ufo/waves/round-38/w1/out/FetchS352/` | 2136 | never |
| 8 | SCORECARD.md | `.ufo/waves/round-38/w1/out/ExecTagInventory/api-status.txt` | 2136 | never |
| 9 | SCORECARD.md | `.ufo/waves/round-40/c2/{base,after}.out` (`base.out` dead, `after.out` exists) | 2184, 2228 | never |
| 10 | SCORECARD.md | `.ufo/watchdog.log` | 2904 | untracked |
| 11 | SKILL.md | `tools/server/server-schema.cpp` | 1143, 1246 | upstream |
| 12 | SKILL.md | `tools/server/server-common.cpp` | 1245 | upstream |
| 13 | SKILL.md | `tools/server/server-task.cpp` | 1247 | upstream |
| 14 | SKILL.md | `tools/server/server-chat.cpp` | 1248 | upstream |

## 4. Every disagreement between the channels, explained

Advisory channel A: 414 embedded root-path candidates from the spans R5 rejects; 12 have a non-resolving embedded path (in 9 distinct spans). None is a dead path citation:

| Span (surface:line) | Why R5 rejects it | Why it is not a dead path |
|---|---|---|
| `defective .ufo/waves/round-29/count-c1.py: thin-row` (SCORECARD:1899), `…: empty-exit-map` (:1900), `…: missing-path:…` (:1901) | space | `/count-c1.py` in the lane tree at tip (1 hit); the trailing `:` is my extraction artifact, not the path |
| `` `defective … missing-path:.ufo/waves/round-999/count-c999.py` `` (:1901) | space | genuinely absent, but the same path as the disclosed row 6 (:1844) — covered |
| `.ufo/reports/round-<N>/kama.md` (SCORECARD:2351, 2414) | `<N>` placeholder | the family exists in the fleet at the named commit `b0fd7b7f…` (`.ufo/reports/round-1/kama.md`, `round-10/kama.md`, …) |
| `corpus/lessons/round-<N>-verifier-spotcheck.md` (SCORECARD:2351, 2414) | `<N>` placeholder | `corpus/lessons/round-10-verifier-spotcheck.md` … `round-12-…` at tip |
| `python3 tools/round45-claim-outcome-audit[-v2].py …` (SCORECARD:2440) | `[`, spaces | both `tools/round45-claim-outcome-audit.py` and `-v2.py` are at tip; my regex stopped at `[` |
| `~/Projects/ufo-fsd-alpha/scripts/local-helper.mjs` (SKILL:113) | `~`, no lane/fleet root prefix | the file exists in that checkout (`15065` B); not a lane/fleet path — exactly why the counter excludes it and line 113 was re-pointed |
| `tools/round<N>-*.py` (SKILL:1374) | `<`, `*` | placeholder; 42 `tools/roundNN-*` files at tip |
| `registry/release-recheck-<newest>.tsv` (SKILL:1418) | `<` placeholder | `registry/release-recheck-b11889.tsv`, `-b11906.tsv` at tip |

Span-with-space control that *does* name a live path: SCORECARD:1716 quotes an old counter message `` `cannot evaluate: .ufo/waves/round-31/sources/SNAPSHOT.json missing at tip` `` — the path exists at tip, and the quoted message names its own base commit `07794a4d`. So the space exclusion is not hiding a dead pointer here.

Advisory channel B: 45 path-like runs outside backticks; 4 do not resolve, none is a citation:

| Site | Text | Reading |
|---|---|---|
| SCORECARD:597 | “serving tools/registry, province and SHONEN remain byte-equal” | prose enumeration, not a pointer |
| SCORECARD:2171 | `` `Admit \`corpus/knowledge/...\`` `` | nested-backtick quotation of a lesson line, with an ellipsis |
| SKILL:654 | “2 could-not-evaluate (unusable registry/docs/git)” | three nouns separated by slashes |
| SKILL:785 | “manifest pins old script/registry/census blobs” | prose; my regex matched the `registry/census` substring |

**No citation form the counter's frozen parser skips is a dead path.**

One calibration nuance inside the 14: under R7 the range `ConfirmM01..11/` resolves to 11 existing directories (`ConfirmM01`…`ConfirmM11`; `ConfirmM06` carries only `verdict.json`). A range-aware parser would therefore report **13** literal misses; the counter's `missing` verdict is for the literal token, and the `never` row is literally true and its note (“each of which exists”) is accurate. Not a defect under the frozen predicate — but the one token in the 14 that is a shorthand rather than an absent path.

## 5. Independent re-derivation of the ledger classes

| Class | Rows | What I checked | Result |
|---|---|---|---|
| never | 7 | each token as an exact path in `git log --all --name-only` of lane and fleet | 0/0 for every one (round-14 evidence.py, `ConfirmM01..11/`, c2-tip.json, count-c999.py, FetchS352/, ExecTagInventory/api-status.txt, round-40 `base.out`) |
| deleted | 1 | `utils.hpp` in tree at `9874e455^` and at `9874e455` | 1 → 0: re-derives |
| untracked | 1 | `.ufo/watchdog.log` in fleet tree at bcc9bbd2 / ee9f734 / d2a6c59; on disk | absent from tree at all three; on disk (156,988 B) — **note false, finding X8-1** |
| upstream | 5 (4 files) | GET the pinned `raw.githubusercontent.com` URLs; compare sha256 to SKILL.md's pins | four `200`s; digests equal `1f9d7b73b436…`, `b4f4aae7eed9…`, `4c3f413b9b54…`, `91f48e09afc5…` |
| fixed | 1 | token cited at base SKILL:895, absent at tip; replacement `tests/report-audit/` cited at tip:895 | holds (5 files under `tests/report-audit/`) |

Other notes spot-checked and accurate: SCORECARD:491 says “Use absent …” (round-14 row), :1732 says `c2-tip.json` “does not exist” and the `c2-<hash>.json` receipts exist, :1741 says the committed `404: Not Found` body, :1844/:1901 carry the round-999 path, :2228 carries the round-40 `base.out` disclosure, and `controls/c2-base.out` exists.

Build claims verified: `git diff --stat 4229ea1b… c22602bd…` = `SCORECARD.md +2/-0` (append-only) and `SKILL.md 4 ++--` — exactly the two lines 113 and 895, which now read `~/Projects/ufo-fsd-alpha/scripts/local-helper.mjs` and `tests/report-audit/`.

## 6. Finding X8-1 — ledger row 21 asserts a history it can check

`registry/cited-path-corrections.tsv:21` (at `c22602bd`):

```
SCORECARD.md	.ufo/watchdog.log	untracked	-	the fleet driver's runtime log, kept on disk at the fleet root and never committed
```

“never committed” is false:

```
$ git -C /home/vgpnk/Projects/shokunin log --all --format='%h %ci %s' -- .ufo/watchdog.log | head -3
7930399e 2026-10-26 11:54:42 -0300 hyaku: restore run-7 driving pattern …, untrack driver runtime (.ufo/state, watchdog.log) …
02322ead 2026-10-26 11:54:27 -0300
858b1038 2026-10-26 11:54:27 -0300
$ git -C /home/vgpnk/Projects/shokunin log --all --format=%H -- .ufo/watchdog.log | wc -l
557
$ git -C /home/vgpnk/Projects/shokunin log --all --diff-filter=A --format='%h %ci %s' -- .ufo/watchdog.log | tail -1
609ecb6e 2026-09-28 17:38:25 -0300 fleet-2: AXES.md framework, MISSION.md SSOT, watchdog v4, …
$ git -C /home/vgpnk/Projects/shokunin ls-tree -r --name-only 7930399e^ | grep -c '^\.ufo/watchdog.log'
1
$ git -C /home/vgpnk/Projects/shokunin show 7930399e^:.ufo/watchdog.log | wc -c
127998
```

The frozen `untracked` class (counter docstring, “a fleet-root token absent from the fleet tree that exists on disk under --fleet”) never consults history, so the row still passes and C2's `met=True` stands. Proposed fix (validated with `patch -p1 --dry-run`, exit 0) is in `out/X8Regen/ledger-note-fix.diff`: replace the note, keep the class, do not delete the row. Residual calibration risk for a later round: the `untracked` class is history-blind, so a path deleted from the fleet repo could in future be disclosed as “untracked” and pass; worth a line in the round-53 lesson's Errata rather than a change to the frozen counter.

## 7. What this does and does not establish

Established: the C2 counter's parser is faithfully implemented against the frozen prose (same 682 tokens, per-surface, independent code; same 14/16 misses at build/base; append-only SCORECARD; `dropped=0`; fleet revision does not matter between `ee9f734` and current HEAD `d2a6c59`); all 14 disclosures re-derive from git history except one note text.

Not established: whether the C2 predicate is *sufficient* for calibration (it is an existence/disclosure check; it cannot tell a good disclosure from an honest one, as X8-1 shows). That is a design question for the judge, not a reclaim of this measurement.

## 8. Compliance

No write, index or jj mutation in the lane or fleet; no `git add/commit/checkout/stash/reset` anywhere; no counter edited in place; no tracer used; no `llama-server` started (only the C2 counter path was exercised, and it starts none); no pacman and no tool installs; scratch `/fast/scratch/hyaku/kama-r53/X8Regen` removed after copying the files above out of it.

## 9. Files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/X8Regen.md` (this report)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/X8Regen/regen-cited-paths.py`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/X8Regen/regen-build.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/X8Regen/regen-build.json`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/X8Regen/regen-build-channels.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/X8Regen/regen-base.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/X8Regen/regen-base.json`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/X8Regen/reconcile.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/X8Regen/c2-build.out.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/X8Regen/base.c2.out.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/X8Regen/cited-path-corrections-c22602bd.tsv`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/X8Regen/ledger-note-fix.diff`
