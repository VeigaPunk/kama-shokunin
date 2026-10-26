# K1Pop — C1 population completeness at base `0163fea2`

Question: which registry rows of `corpus/SOURCES.md` at base cite a `ggml-org/llama.cpp` file at a
commit or release and fall **outside** the frozen population rule, and does release `b11906`
(`4d71b42fd87db24b8b7c808c151b713aa4459cfd`) change what each one teaches?

Short answer: the rule selects 91 rows and 91 rows only; the complement of llama.cpp-citing rows is
**10 rows** and none of them is silently mis-scoped inside C1. Their teaches cells are either dated
samples, per-release identities, or build-scoped receipts — `b11906` falsifies none of them, but it
moves one (S477) and it leaves three (`S482`, `S484`, `S485`) with a newer release in front of them
and no population that would ever re-open them.

## The rule as frozen (contract, not a proposal)

`tools/round46-release-recheck-audit.py:25-31` (docstring):

> Population: registry rows of corpus/SOURCES.md at base (0-3 leading spaces, `| S###`), 11 cells,
> recheck cell `on-release`, status `mined` or `queued`, source cell naming
> `https://github.com/ggml-org/llama.cpp/(blob|tree)/<ref>/<path>` or
> `https://raw.githubusercontent.com/ggml-org/llama.cpp/<ref>/<path>`; the pin is `<ref>` when it is
> 40-hex, else the first 40-hex run of the anchor cell; rows with neither are outside the
> population. Path drops any `#...` suffix.

So the exclusion clauses are, exhaustively: (1) leading indent > 3 or an id not shaped `S\d{3,}`;
(2) cells ≠ 11; (3) recheck ≠ `on-release`; (4) status ∉ {`mined`,`queued`}; (5) no
`llama.cpp/(blob|tree)`/`raw.githubusercontent.com/llama.cpp` URL; (6) ref not 40-hex **and** no
40-hex anywhere in the anchor cell. **Tier is not an exclusion clause** and the population happens to
be all tier A (90 `mined`, 1 `queued`).

## Method

`python3 classify.py` (scratch) and `python3 wide.py` re-use the counter's own `population()`,
`cells()`, `URL`, `HEX40` against `git show 0163fea2:corpus/SOURCES.md` (524 lines, 226 `S###` rows),
then scan every row for a llama.cpp URL of any shape plus every llama.cpp file-path token outside the
population. Results:

- `population size 91` — identical to the frozen list in `preregistration.json`
  (`frozen list n= 91 computed n= 91`, `computed-not-frozen: []`, `frozen-not-computed: []`).
- 226 rows, **all** 226 with `cells=11` and indent 0, so clause (1) and (2) exclude nothing.
- Rows citing a llama.cpp **file** through the rule's two URL forms: 91 — every one of them is in the
  population. No row outside the population cites a llama.cpp file by those URL forms.
- Rows citing llama.cpp by other forms (release page, release asset, pull request, issue, own-work
  receipt/inventory whose anchor carries the build commit): 10, listed below.
- A file-path-token sweep (`tools/server/*`, `src/llama*`, `common/*`, `ggml/src/*`,
  `gguf-py/*.py`) over all 135 non-population rows returns **no hit**: no off-population row cites a
  llama.cpp source file as bare text either.
- Incidental mentions, checked and discarded (they cite no llama.cpp file or release): S017, S040,
  S044, S327 (llama.cpp appears only in `used-by` paths or in a negative scope clause).

## Off-population llama.cpp rows

Upstream clone `/fast/scratch/hyaku/kama-r46/L1/llama.git`; `b11755=704366d76f8748cf9ad3df62a464bfcc8d1ae6ad`,
`b11889=d854d98bae598388ecea1ed84396587e5edc326d`, `b11906=4d71b42fd87db24b8b7c808c151b713aa4459cfd`.

| id | SOURCES.md:line | citation form | tier | status | recheck | outside because | does b11906 change what it teaches? |
|---|---|---|---|---|---|---|---|
| S026 | 38 | `llama.cpp/pull/18001` (add `/v1/metrics`) | A | rejected | on-release | clause 5 (PR, not a file) + clause 4 | **No.** `git grep 'v1/metrics' 4d71b42f` → exit 1 (no hit anywhere in the b11906 tree; same at b11889). The flip condition ("a released, versioned project source documents `/v1/metrics`") is still unmet; the rejection stands. |
| S028 | 40 | `llama.cpp/issues/4746` (health-check request) | C | rejected | 90d | clause 5 + clause 4 | **No.** Historical 2024 thread closed via PR #5548; the route it asked for exists at b11906 (`get_health`, server-context.cpp:5609) and the row is scoped as history, not as contract. |
| S038 | 50 | `llama.cpp/releases/tag/b11755` + asset record | A | mined | **on-release** | clause 5 (release page, no file path) | **No.** `git -C … rev-parse b11755^{commit}` → `704366d76f…`; the row teaches the b11755 tag→commit and asset digest, both per-release and immutable. It is nevertheless an `on-release` llama.cpp row that no recheck population will ever re-open. |
| S477 | 230 | own-work `git ls-remote --tags …/llama.cpp.git` | A | mined | 30d | clause 5 (own-work) | **Yes, in its current value.** Row records 2026-10-25T20:03:21Z: newest `b11887`, **115** bN tags above b11755. At the b11906 clone: newest `b11906`, **130** above (`115` at b11887, `121` at b11897, `123` at b11899, `130` at b11906 — verified by counting `git tag -l 'b*'` per bound). The dated claim survives; the number a reader would re-derive today does not. Not due (30d → 2026-11-24). |
| S482 | 235 | `llama.cpp/releases/tag/b11889` | A | mined | **on-release** | clause 5 | **No.** b11889's `target_commitish`/`published_at`/`prerelease` are per-release facts; `b11889^{commit}` is still `d854d98b…`. A newer release does not edit b11889's record — the release event instead wants the b11906 analogue, which nothing in the population asks for (see F1). |
| S484 | 237 | `llama.cpp/releases/download/b11889/llama-b11889-bin-ubuntu-x64.tar.gz` | A | mined | **on-release** | clause 5 | **No.** Asset size/digest and `llama-server` sha256 are per-release; scoped "kama ran in round 45". |
| S485 | 238 | own-work b11889 live receipts (anchor carries `build_info b11889-d854d98ba`) | A | mined | **on-release** | clause 5 | **No, by code reading; unexecuted at b11906.** `server.cpp`, `server-http.cpp`, `server-queue.cpp`, `server-common.cpp`, `server-schema.cpp` are byte-identical b11889..b11906; `server-context.cpp` changes 15 lines, all mtmd-capability plumbing (hunks at 1012/1397/1705/5127) and none in `server_routes::init_routes`; b11906:5609-5619 still returns `res->ok({{"status","ok"}})`, and `/metrics` still errors `ERROR_TYPE_NOT_SUPPORTED` when `--metrics` is absent (b11906:5620-5626) which `server-common.cpp:119` maps to 501 (unchanged file; upstream `tools/server/tests/unit/test_metrics.py:43` asserts 501 at b11906). No b11906 binary was run by this seat. |
| S041 | 53 | own-work b11755 receipts | A | mined | every round | clause 5 + clause 3 | **No.** Explicitly `b11755`; already carried forward by the round-45 b11889 receipts (S485). |
| S046 | 58 | own-work b11755 receipts v2 | A | mined | every round | clause 5 + clause 3 | **No**, same as S041. |
| S055 | 67 | own-work b11755 receipts v3 | A | mined | every round | clause 5 + clause 3 | **No**, same as S041. |

Round attribution of the rows added in rounds 44-45 (`git log --oneline 9d9cc93e..0163fea2 -- corpus/SOURCES.md`
→ `ef76777e` round-44, `052cb1e9`/`0718b6ab` round-45): S482, S483 in round 44; S484, S485 in round 45
(`opened` cells: S482/S483/S484/S485 all `2026-10-26`). Of these only S482/S484/S485 cite llama.cpp;
S483 is vLLM. None of them is reachable by the population rule as written, and only S479 (round 41,
`raw.githubusercontent.com/…/server-models.cpp`) is a round-4x file row that *is* inside it.

## Findings

### F1 — the release identity `b11906 → 4d71b42f` is assumed by a constant, not verified inside the measurement

`tools/round46-release-recheck-audit.py:102-103` freezes `RELEASE = "b11906"` and
`RELEASE_COMMIT = "4d71b42fd87db24b8b7c808c151b713aa4459cfd"`; `check_row()` never runs
`git rev-parse b11906^{commit}`. Every ledger row is scored against `4d71b42f`, so if the tag and the
constant ever disagreed the counter would report `met=True` while the statement "re-verified at
release b11906" was false. Today they agree (`git -C <upstream> rev-parse b11906^{commit}` →
`4d71b42f…`), and the preregistration's `release.observed` records the freeze-time `ls-remote`, so
nothing is wrong in this round. The gap is structural: the population's only release-identity rows
(S038 for b11755, S482 for b11889) are outside the rule, and the `newrow` leg
(docstring:78) accepts **any** new row containing both `b11906` and the commit string — a file row
satisfies it, so round 46 can close C1 without ever proving that the tag names that commit.
Smallest safe correction (next round's counter, not this one): add a `release_commit` guard to the
ledger header/derivation — `git rev-parse <RELEASE>^{commit}` from `--upstream` must equal
`RELEASE_COMMIT`, else exit 2 (could not evaluate) — and treat "one new row per release *of the
release-identity class*" as the sourced leg.

### F2 — `S477` teaches a moving count and is in no recheck population

S477 is the only row that teaches "how many bN tags sort above the pin" (115 at 2026-10-25). By
b11906 the derivable value is 130, and round 45 already recorded two different instants (121 at
b11897 in `registry/recheck-r45.tsv`; 123 at b11899 in
`corpus/lessons/round-45-verifier-spotcheck.md:149`) without the row changing. Its consumer
`corpus/knowledge/engine-pin-watch.md:51` still prints `| llama.cpp | b11755 | b11887 | 115 | behind |`
and `:54` still says "Whether b11887 changed the surfaces they describe … has not been checked" —
while the round-44 and round-45 sections of SOURCES.md did check exactly those surfaces (b11889,
b11906). Two authorities, one of them stale, and C1's flag rule
(docstring: "Flags: for each valid drifted/removed row…") cannot reach it because S477 is neither a
population row nor drifted. Not a C1 defect and not due (30d); smallest safe correction: extend the
`on-release`/30d cadence of the inventory row into the next population, and append one dated
supersession line to `engine-pin-watch.md` §Result naming b11889/b11906.

### F3 — behavioural freshness at the new release has no population at all

The 91 rows prove file-level freshness at b11906. The lane's behavioural evidence (`/health` body,
loading 503 envelope, `/metrics` 501, `/v1/models` identity) exists only in the own-work receipt rows
S041/S046/S055 (b11755) and S485 (b11889), all outside the rule. So after round 46 the lane will hold
`unverified=0` at b11906 for source text and **zero executed checks on any b11906 build**. Round 45
closed the analogous hole by hand (its ten-key population included the `live` class); round 46's
frozen claim has no equivalent. b11906 changes none of the taught statements (F3 evidence above), so
the miss costs nothing this round — but it recurs at every release, and the round-45 section already
carried "llama.cpp releases after b11889 (b11897 at this sample)" as frontier. Smallest safe
correction: next round adds a `live` key per release (run the pinned model + tool against the
official asset) or states in the claim that behavioural freshness trails the pinned binary
(`registry/engine-pins.tsv:4`, `pin=b11755`) by design.
