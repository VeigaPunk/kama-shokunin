# SC02Sources — round-80 w1: SOURCES rows, knowledge entry, coverage row, KQ criterion

Status: complete. The four deliverables are drafted in the seat directory, and the L1 has already
filed S554–S556 from `sources-rows.md` — they are committed at `dea7c269` (`git show
master:corpus/SOURCES.md`, lines 309–311). Nothing was committed by this seat. The C1 target line
is reachable only with the tool change staged uncommitted by another seat — see Finding 1.

Base read: lane tip `fe7b978013bd1aa6d67a7e0fbf6369b8d7a9b023` (`git -C … rev-parse master`),
not the `c45fc7d1` base named in the dispatch. The dispatch's base is a round-start constant; the
lane has moved twice during this seat: round-79's lesson/S553/census entry were already in
`fe7b9780`, and `dea7c269` ("the three claim instruments, the pin-relation and class-engine
registers, and the round lesson with the round-79 corrections") landed the round-80 instruments,
the lesson, and this seat's rows while I worked.

## Behavior

1. `sources-rows.md` — three 11-column contract-v1 rows, header reproduced only for shape
   (verified: every table line splits into exactly 11 cells, no embedded `|`).
   - **S554** Ollama `docs/api.md` at `v0.40.11`, kind docs, tier A, status `mined`, opened
     2026-11-04, recheck `on-release`, used-by `corpus/knowledge/unregistered-class-second-engine.md`.
     Anchor: `## List Local Models` line 1352, `GET /api/tags` line 1355, definition line 1358,
     raw sha256 `96db0308…d0f5`, 54614 bytes.
   - **S555** llama.cpp server README @ `39febd2a`, kind docs, tier A, `mined`, opened 2026-11-04,
     `on-release`. `teaches` opens literally `supersedes S553 —` and is anchor-correction only.
     Anchor: heading `### GET /models: List available models` line 2197, note 1 line 2225, the
     unloaded-model bullet line 2227; raw sha256 `8fd5abde…35c6`, 135608 bytes (identical to
     S553's recorded hash, so the file did not change between the two reads).
   - **S556** llama.cpp `docs/preset.md` @ `39febd2a`, kind docs, tier A, status `rejected`,
     opened 2026-11-04, `on-release`, used-by `—`. Reason: the round's class reads a model list
     and the probe parses no preset file, so the row would scope ground no claim reads. Flip: a
     round that grades preset-inherited parameters on a lane-owned fixture.
2. `knowledge-unregistered-class-second-engine.md` — 43 lines, opens with `source: S554`,
   `verified-at: 2026-11-04`, `recheck:`. Covers: `/api/tags` is an inventory of locally available
   models; the probe actually reads `/v1/models` (with `MODEL_OK`'s model-array rule); the
   `registered` class is engine-agnostic because `classify_registration` takes only the verdict
   class and the ports parsed from each registry row's `declared_baseurl`; and the limit — an
   inventory is neither a loaded-model nor a readiness claim. It asserts no census run.
3. `readme-row.md` — one 3-column coverage-map row (`|\`corpus/knowledge/…\`|covers|80|`) plus the
   section-heading filing note.
4. `quality-criterion.md` — `KQ132` in the existing 4-column shape, after the KQ131 section:
   a self-record fact is stated only in the form its receipt prints it, and a claim whose own
   cited receipt disagrees is unverified regardless of intent. Check line cites the round-80
   counter, its `--enumerate` pre-correction output and the value-bound correction form.

## Gates (all read-only; nothing committed, nothing installed)

- Sources opened with `curl -sS -o … -w '%{http_code}'`: three URLs, all **HTTP 200**; bytes,
  lines, sha256 and md5 recorded in `curl.txt`. `git ls-remote --tags` over the Ollama repo used
  for tag identity only (read-only network, no clone).
- Read-only git only: `rev-parse`, `show`, `ls-tree`, `ls-remote`. No `add`/`commit`/`push`/
  `stash`/`checkout`/`reset`/`pull`, no jj call, no fixture repo created (the F2 replay reads the
  lane's objects directly, so no clone was needed).
- Scratch: `S=/fast/scratch/hyaku/kama-r80/SC02Sources` (mkdir -p, `TMPDIR=$S`), deleted before
  yield; all receipts were written into the wave seat dir, not into `$S`.
- Writes stayed inside the lane; no fleet-root file, no `~/.local/bin`, no sibling repo touched.
- No tool installation was needed or performed.

## Touched surfaces (all new, inside the seat dir)

- `…/.ufo/waves/round-80/w1/SC02Sources/sources-rows.md`
- `…/.ufo/waves/round-80/w1/SC02Sources/knowledge-unregistered-class-second-engine.md`
- `…/.ufo/waves/round-80/w1/SC02Sources/readme-row.md`
- `…/.ufo/waves/round-80/w1/SC02Sources/quality-criterion.md`
- `…/.ufo/waves/round-80/w1/SC02Sources/curl.txt`
- `…/.ufo/waves/round-80/w1/SC02Sources/c1-counter.out`
- `…/.ufo/waves/round-80/w1/SC02Sources/f2-collision.out`
- `…/.ufo/waves/round-80/w1/SC02Sources/filed-vs-draft.diff`
- `…/.ufo/waves/round-80/w1/SC02Sources.md` (this report)

`corpus/SOURCES.md`, `corpus/QUALITY.md`, `corpus/README.md` and `corpus/lessons/round-80.md` were
read only; no row was inserted by this seat.

## Findings

1. **C1's F2 fact was broken by the round's own corpus rows; confirmed red at the landed tip and
   already fixed in the working tree (uncommitted).** `tools/round80-selfrecord-round79.py` derives
   F2 as "source rows in `corpus/SOURCES.md` at the revision" plus "knowledge blobs under
   `corpus/knowledge/` at the revision, minus names containing `engine-sides`/`processes`", and
   scores a fact fresh only when `declared == sealed == tip`. I predicted the collision from the
   code before the rows landed (293→296, 52→53); the L1 then landed S554–S556 and the round lesson
   at `dea7c269`, and the committed counter now prints exactly that:
   `FACT F2 … tip=population=sources:296,knowledge:53 status=stale` →
   `SELFRECORD_R79 claims=6 mismatches=1 corrected=3 unbacked=0`, exit 1. A fourth correction for
   F2 would print `corrected=4`, also missing the frozen target. **The fix is already staged
   uncommitted by another seat** — `SEALED_BOUND = {"F2"}` with
   `seen_tip = (sealed_facts[fact]["observed"] if fact in SEALED_BOUND else tip_facts[fact]["observed"])`
   — and the worktree counter prints `SELFRECORD_R79 claims=6 mismatches=0 corrected=3 unbacked=0`,
   exit 0. Action for the L1: **commit that tool change with the round's record**, otherwise C1 is
   red at its own tip. I did not edit the counter or the plan; both runs are in
   `f2-collision.out`.
2. **R79V6 is grounded and the supersession is anchor-only.** The re-opened README is byte-identical
   to S553's recorded hash, and `grep -c '^#.*[Rr]outer'` over the fetched file is **0** — no
   heading carries S553's `§Router mode` label. The heading that holds note 1 is
   `### GET /models: List available models` (line 2197); note 1 is line 2225 and the "not running
   … still added or updated" bullet is line 2227, exactly the line S553 cited.
3. **S554 is a different artifact from S011/S031 and the Gate block must say so.** At `v0.40.11`
   the repo file is Markdown (`docs/api.md`, 1872 lines, no OpenAPI `info.version`), and its tags
   section is a plain `## List Local Models` heading — there is no `### GET /api/tags` heading in
   this artifact. S011 and S031 anchor the docs-site OpenAPI 3.1.0 page (`info.version 0.1.0`). A
   Gate quote citing an OpenAPI heading or "the page's summary" would not be locatable in
   `docs/api.md`; the locatable quote there is line 1358, "List models that are available
   locally." (7 words), which is what `sources-rows.md` §Gate-block handoff carries.
4. **Ollama tag identity.** `refs/tags/v0.40.11` → `675150d6ad2747df1e218ef59de9194bc4a7e538`;
   `refs/tags/v0.40.11-rc0` points at the **same** commit, so the round should not describe rc0 as
   a distinct release or a later artifact.
5. **C1 was red at my start for the expected pre-correction reason, and F4/F5/F6 have since been
   corrected.** At `fe7b9780` with `corpus/lessons/round-80.md` absent, the counter printed
   `SELFRECORD_R79 claims=6 mismatches=3 corrected=0 unbacked=0`, exit 1 (F4/F5/F6 stale,
   `reasons=unanswered`); `--enumerate` printed `SELFRECORD_R79_ENUM claims=6 stale=3 corrected=0`,
   exit 1; `--no-corrections` printed the same `mismatches=3` line, exit 1. At `dea7c269` the lesson
   carries the three corrections and F4/F5/F6 read `status=corrected`; only F2 remains stale, per
   Finding 1. This seat graded nothing. Evidence: `c1-counter.out` and `f2-collision.out`.
6. **used-by consistency to check at filing.** S555's used-by lists both
   `unregistered-listener-census.md` (inherited from S553) and the new
   `unregistered-class-second-engine.md`, because the entry cites S555 for the inventory limit; if
   the L1 prefers one-hop used-by only, drop the new entry from S555 and from the entry's `source:`
   line together. S556 has no used-by by design (rejected).
7. **No id collision.** `S554`/`S555`/`S556` do not exist in `corpus/SOURCES.md` at the tip; the
   highest row is `S553`.
8. **The filed knowledge entry is one edit behind this seat's draft.** At `dea7c269`
   `corpus/knowledge/unregistered-class-second-engine.md` matches my draft except lines 34–35,
   which still carry the pre-tightening sentence "…with the registry, which is all the round-80 C3
   audit asks the engine register to carry." The seat-dir draft now reads "…with the registry —
   which is what the round-80 C3 engine register records, one row and one receipt per engine."
   The live sentence overstates the audit (it verifies each register row's receipt exists, prints
   `class_missing=0` and names the same engine; it does not "ask the register to carry" the class
   move). Re-filing from the seat dir picks the tightened text up; otherwise replace those two
   lines verbatim. SOURCES S554–S556, the README row and `KQ132` are byte-identical to the drafts
   (verified by `diff` against `git show master:…`).

## Out of scope (not done, not claimed)

- No census or engine run: C3's Ollama child, `tools/round80-ollama-census.py` and
  `registry/unregistered-class-engines.tsv` are other seats' work; the knowledge entry explicitly
  asserts no engine result.
- No grade of C1/C2/C3, no `pre-report-gate.py`, no SCORECARD/LOG/SKILL/PROVINCE edit, no
  `corpus/lessons/round-80.md` write (its Gate block needs this seat's quote — handoff included in
  `sources-rows.md`).
- No installs, no service restarts, no fleet-root or sibling-repo reads beyond the lane.

## Receipts (absolute path → command → exit)

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-80/w1/SC02Sources/curl.txt` →
  `curl -sS -o <name> -w '%{http_code}' '<url>'` ×3 (ollama `docs/api.md` @ v0.40.11;
  llama.cpp `tools/server/README.md` @ 39febd2a; llama.cpp `docs/preset.md` @ 39febd2a) →
  HTTP 200, 200, 200; sha256 `96db0308…`, `8fd5abde…`, `3e664354…`; plus
  `git ls-remote --tags <ollama>` exit 0.
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-80/w1/SC02Sources/c1-counter.out` →
  `python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round80-selfrecord-round79.py --repo
  /home/vgpnk/Projects/shokunin/kama-shokunin [--enumerate|--no-corrections]` → exit 1, 1, 1
  (read-only; the counter writes nothing).
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-80/w1/SC02Sources/f2-collision.out`
  → part 1: `python3 - <lane> <seat-dir>` derivation replay over
  `git show <tip>:corpus/SOURCES.md` and `git ls-tree -r --name-only <tip> corpus/knowledge/` →
  exit 0, prints `sources:293→296, knowledge:52→53`; part 2 (addendum, after the rows landed):
  `git -C <lane> show master:tools/round80-selfrecord-round79.py > $S/counter-at-master.py` then
  `python3 $S/counter-at-master.py --repo <lane>` → `SELFRECORD_R79 claims=6 mismatches=1
  corrected=3 unbacked=0`, exit 1, `F2 … tip=population=sources:296,knowledge:53 status=stale`;
  `python3 <lane>/tools/round80-selfrecord-round79.py --repo <lane>` (worktree, with the staged
  `SEALED_BOUND`) → `SELFRECORD_R79 claims=6 mismatches=0 corrected=3 unbacked=0`, exit 0.
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-80/w1/SC02Sources/filed-vs-draft.diff`
  → `git -C <lane> show master:corpus/knowledge/unregistered-class-second-engine.md | diff -
  <seat>/knowledge-unregistered-class-second-engine.md` → exit 1 (two-line wording delta, Finding 8);
  same comparison for SOURCES S554–S556, the README row and `KQ132` → `IDENTICAL`.
