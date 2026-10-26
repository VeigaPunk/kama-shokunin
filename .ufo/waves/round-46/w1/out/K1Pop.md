# K1Pop — C1 population completeness at base `0163fea2`

**Verdict: the frozen population is exactly right at the rule's edge — 91 selected, and no off-population row cites a llama.cpp file through the rule's URL shapes. Ten llama.cpp-citing rows sit outside it; `b11906` falsifies none of their teaches cells, but it moves S477's count and leaves the release-identity and behavioural-freshness modalities of a new release uncovered (F1-F3, frontier items, population stays frozen).**

## 1. Rule re-derived exactly (no drift between counter, prereg and base)

```
$ python3 - <<'PY'   # imports the counter's own population(), cells(), URL, HEX40
population size 91
frozen list n= 91 computed n= 91
computed-not-frozen: []
frozen-not-computed: []
```

`tools/round46-release-recheck-audit.py:25-31` (population clause), `:101-103` (`BASE`, `RELEASE`,
`RELEASE_COMMIT`), `:140` (`def population`). Base file:
`git show 0163fea2:corpus/SOURCES.md` → 524 lines, 226 `S###` rows, all 226 with `cells=11` and
indent 0 (so exclusion clauses 1 and 2 exclude nothing at this base). Population composition: tier A
91/91, status `mined` 90 + `queued` 1.

## 2. Sweep for llama.cpp-citing rows outside the rule

Three independent sweeps (`out/K1Pop/classify.py`, `wide.py`, `census.py`, transcripts
`out/K1Pop/census.out`, `out/K1Pop/wide.out`, both exit 0):

- every llama.cpp URL of any shape (blob/tree/raw/releases/pull/issues/`.git`), classified against
  the rule → **91 file-URL rows, all inside the population; 10 rows outside** (release page ×2,
  release asset ×1, PR ×1, issue ×1, own-work receipt/inventory ×5);
- file-path token sweep (`tools/server/*`, `src/llama*`, `common/*`, `ggml/src/*`, `gguf-py/*.py`)
  over all 135 non-population rows → **zero hits** (no row cites a llama.cpp file as bare text);
- `ggerganov/llama.cpp` legacy-org and `refs/tags/...` URL forms → zero occurrences
  (`grep -c 'ggerganov' SOURCES.base.md` → 0).

Rows and per-row `b11906` impact: `out/K1Pop/rows.md` (table, with evidence per row). Summary:
S026 (PR `/v1/metrics`, rejected) unchanged — `git grep 'v1/metrics' 4d71b42f` exit 1;
S028 (issue, tier C, rejected) unchanged; S038 (b11755 release) unchanged — `rev-parse b11755^{commit}`
= `704366d76f…`; **S477 (inventory) moves** — teaches 115 tags above b11755 at 2026-10-25T20:03Z,
derivable today 130 (`121` at b11897, `123` at b11899, `130` at b11906, each counted from
`git tag -l 'b*'`); S482/S484 (b11889 release + asset) unchanged; **S485 (b11889 live receipts)
unchanged by reading, unexecuted at b11906**; S041/S046/S055 (b11755 receipts) unchanged and already
carried by S485.

## 3. Evidence that b11906 does not falsify S485

```
$ git -C $U rev-parse b11906^{commit}
4d71b42fd87db24b8b7c808c151b713aa4459cfd
$ git -C $U rev-list --count d854d98b..4d71b42f
17
$ for f in tools/server/{server-http,server,server-queue,server-common,server-schema}.cpp; do …done
IDENTICAL tools/server/server-http.cpp
IDENTICAL tools/server/server.cpp
IDENTICAL tools/server/server-queue.cpp
IDENTICAL tools/server/server-common.cpp
IDENTICAL tools/server/server-schema.cpp
```

`tools/server/server-context.cpp` changes 15 lines (`git diff d854d98b 4d71b42f -- tools/server/`):
all mtmd-capability plumbing (hunks at 1012, 1397-1398, 1705-1708, 5127-5130), none inside
`server_routes::init_routes`. At b11906 the handler still reads
`res->ok({{"status", "ok"}})` (`server-context.cpp:5609-5619` in the release blob) and `/metrics`
still errors `ERROR_TYPE_NOT_SUPPORTED` without `--metrics` (`:5620-5626`), mapped to 501 at
`server-common.cpp:119` (byte-identical file); upstream `tools/server/tests/unit/test_metrics.py:43`
asserts 501 at b11906. `server-models.cpp`'s single change is a comment (`same rule as
mtmd_helper_get_capabilities()`).

## 4. Findings

**F1 — release identity is a constant, not a measurement.** `tools/round46-release-recheck-audit.py:102-103`
freezes `RELEASE="b11906"`, `RELEASE_COMMIT="4d71b42f…"`; `check_row()` (`:213`, blobs at `:220`/`:233`) scores every row
against `RELEASE_COMMIT` and never derives it from the tag; the only guard is an existence probe
`for c in (RELEASE_COMMIT,): git(a.upstream,"cat-file","-e",c+"^{commit}")` at `:305-306`, which
passes for any commit the clone holds, tag or not. The rule's release-identity rows (S038,
S482) are outside the population, and the `newrow` leg (docstring:78) is satisfied by *any* new row
containing `b11906` + the commit string — a file row suffices. Today the binding is true
(`rev-parse b11906^{commit}` = `4d71b42f…`) and the preregistration's `release.observed` recorded the
freeze-time `ls-remote`, so no verdict is wrong; but the receipt cannot catch a mis-bound tag.
*Fix (next round's counter, not this one):* ledger guard `git rev-parse <RELEASE>^{commit}` from
`--upstream` must equal `RELEASE_COMMIT`, else exit 2, and require one new row of the release-identity
class per release.

**F2 — S477 teaches a moving count and is in no recheck population.**
`corpus/SOURCES.md:230` records 115 tags above b11755 at 2026-10-25; the derivable number at b11906 is
130; round 45 already recorded 121 (`registry/recheck-r45.tsv`, S477 note) and 123
(`corpus/lessons/round-45-verifier-spotcheck.md:149`) without the row changing. Its consumer
`corpus/knowledge/engine-pin-watch.md:51` still prints `| llama.cpp | b11755 | b11887 | 115 | behind |`
and `:54` still says the surfaces "has not been checked", while SOURCES.md's round-44/45 sections did
check them at b11889 (and round 46 checks them at b11906). Two authorities, one stale; C1's flag rule
cannot reach S477 (not population, not drifted) and it is not due (30d → 2026-11-24).
*Fix:* put the inventory row in the next population and append one dated supersession line to
`engine-pin-watch.md` §Result.

**F3 — no behavioural evidence at the new release.** After round 46 the lane has `unverified=0` at
b11906 for source text and zero executed checks on any b11906 build: the behavioural rows
(S041/S046/S055 at b11755, S485 at b11889) are all outside the rule, and `registry/engine-pins.tsv:4`
still pins `llama.cpp … b11755`. Round 45 closed the same hole by hand with a `live` class; round 46's
frozen claim has no equivalent. Cost this round: none, because b11906's server diff leaves the taught
surfaces untouched (§3). *Fix:* add a per-release `live` key (pinned model + tool against the official
asset) to the next population, or state explicitly that behavioural freshness trails the binary pin.

## 5. Housekeeping

No tools installed or upgraded. Lane, fleet repo and upstream clone untouched (read-only git only; no
`git add/commit/checkout`). Scratch `/fast/scratch/hyaku/kama-r46/K1Pop` removed after copying the
three scripts and two transcripts into `out/K1Pop/`.

## Paths written

- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/K1Pop.md
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/K1Pop/rows.md
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/K1Pop/classify.py
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/K1Pop/census.py
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/K1Pop/wide.py
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/K1Pop/census.out
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/K1Pop/wide.out
