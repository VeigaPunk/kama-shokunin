# V0Census — census baseline and append-only guard for integration (round 47)

**Verdict: census validate reproduces the recorded `start.out` byte-for-byte
(95 TSV rows identical; the only extra line in `start.out` is the harness
trailer `exit=0`) and exits 0 with W04 ×93 (29 distinct duplicated URLs) +
W01 (S481) warnings; the append-only guard `tools/sources-append-only.py`
exits 2 on the frozen pair `172b8ad0… → 3a09a1d9…` because the base blob
contains row-like rows outside the `## Registry` section (line 516, Round-45
appendix table) — so the round's planned 3–4 SOURCES appends cannot reach exit 0
until that guard is fixed (proposed diff in this out dir); the patched guard
then exits 0 (`no append-only violations`, selftest 43/43).**

## 1. Evidence — runs (all against my own `git clone --shared` of the lane at
`/fast/scratch/hyaku/kama-r47/V0Census/lane`; lane/fleet roots never written)

| # | Command | Result |
|---|---|---|
| C0 | `git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin $S/lane`; `git -C $S/lane rev-parse 172b8ad0… 3a09a1d9…` | both revisions resolve; `172b8ad0…` is an ancestor of `3a09a1d9…` (2 commits between: freeze `bbcc6dc2`, build `3a09a1d9`) |
| C1 | `TMPDIR=$S /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama > census-validate.out 2> err` | exit **0**; 95 TSV lines; no E-codes; ok line `kama ok …/corpus/SOURCES.md` |
| C2 | `head -n 95 …/census/start.out \| cmp - census-validate.out` | `FIRST-95-IDENTICAL`; `start.out` line 96 = `exit=0` (script prints only TSV; trailer was appended by the harness) → **start.out equals my run** |
| C3 | `python3 …/tools/sources-append-only.py --from 172b8ad0… --to 3a09a1d9… --repo $S/lane` | exit **2**: `error: 172b8ad040d51ce8c011238c1408d4e0b6aa9595:corpus/SOURCES.md:516: row-like line outside the parsed registry table; refusing to drop it` |
| C4 | same, reversed (`--from 3a09a1d9… --to 172b8ad0…`) | exit **2**, same message for `3a09a1d9…` — both blobs unparseable for the guard |
| C5 | `git show <rev>:corpus/SOURCES.md` row-like count (regex `^\s*\|?\s*[`*_[]*[Ss][0-9]+[`*_]]*\s*\|`) | 27 row-like lines in **both** blobs; first at line 516 in each |
| C6 | `git diff 172b8ad0… 3a09a1d9… -- corpus/SOURCES.md` | empty — SOURCES.md untouched between base and build; no append landed yet (`newrow=0` at build, matching `controls/base.c2.out`) |

## 2. Census warnings by code, with the rows they name (full listing: `w04-by-url.txt`)

- **W04 — duplicate URL across scopes: 93 occurrences, 29 distinct URLs.**
  Implicated rows (suffix = row id): S031 (docs.ollama.com/api/tags),
  S043, S056, S060, S064, S065, S067, S071, S077, S078, S079, S080, S081,
  S082, S083, S084, S085, S086, S087, S088, S093, S097, S100, S103, S105,
  S108, S109, S110, S112, S114–S125, S127, S129–S135, S137, S141–S173,
  S181–S189, S191. Largest groups: `github.com/ggml-org/llama.cpp/blob/704366d7…/tools/server/server-schema.cpp` (many rows, S141–S173) and
  `…/tools/server/server-context.cpp` (S114–S125), plus
  `raw.githubusercontent.com/ggml-org/llama.cpp/704366d7…/tools/server/server-common.cpp`
  (S181–S189).
- **W01 — S481 tierC mined** with `used-by=corpus/knowledge/runtime-health-surface-processes.md, corpus/lessons/round-43.md, corpus/knowledge/runtime-health-surface-matrix.md, corpus/knowledge/endpoint-health-probe-conventions.md, corpus/knowledge/served-model-id-resolution.md, corpus/knowledge/engine-pin-watch.md`.
- No E-codes; exit 0. W-codes do not affect exit.

## 3. Planned SOURCES appends and what they must satisfy for exit 0

Planned rows (from `w1/dispatch.json`, S1Rows (a)(b)(c) + S1Numstat; ids
S4NN assigned by L1): b11909 release binary row, b11909 live-receipts row,
stories260K model row, git numstat/docs row. Full constraint list for both
gates (census validate per-row E-checks; append-only rule 2 immutable/mutable
cells): `planned-rows-constraints.md`.

The decisive constraint: **exit 0 for the append-only guard is currently
unreachable for any append** (§4).

## 4. Findings (severity order)

### F1 (blocker) — `tools/sources-append-only.py` cannot grade any SOURCES transition whose blobs contain non-registry row-like tables
- File/line: `tools/sources-append-only.py` — final scan in `parse_registry`:
  `for idx, line in enumerate(lines):` at lines 227–232 (after parse), regex
  `ROWLIKE_RE` at line 79; it inspects the **whole blob**, not the
  `## Registry` section. Docstring lines 26–31 promise this whole-blob rule.
- Command that shows it: C3/C4 — exit 2 (`row-like line outside the parsed
  registry table`) for `172b8ad0…:corpus/SOURCES.md:516` (and the same for
  `3a09a1d9…`). Line 516 is the Round-45 re-verification appendix row
  `| `S010` | ollama …` (introduced by commit `052cb1e9`; Round-44 tables by
  `ef76777e`).
- Consequence: the lane's own append-only gate is dead for this pair and for
  every transition whose base carries the round-44/45/46 appendix tables; C2's
  planned `newrow` (b11909 row) lands with no append-only verification at
  integration. It also blocks the first census-style transition check with
  `--from <base>` anywhere ≥ round 44.
- Proposed fix (unified diff: `proposed-fix-sources-append-only.diff`):
  scope the row-like refusal to the registry section `[start, section_end)`
  (record `section_end` at the first same/higher-level heading) instead of the
  whole blob; keep every inside-section shape check unchanged; update the
  docstring and the two selftest cases (`row-like line outside the registry`
  now wants exit 0; new `row-like line before the registry` case). Patched
  tool: `python3 … --selftest` → **43/43, exit 0**; on the pair → **exit 0,
  `no append-only violations`, JSON `{"violations": [], "added": [], "ok": true}`**.
  (The tool is a gate, not a round counter; if its semantics change, the
  contract row `SOURCES.md` → gate `SKILL.md:578` wording should be kept in
  sync at integration.)

### F2 (observation) — `start.out` equality
- `census/start.out` = my validate run + one trailer line `exit=0`; the script
  itself does not print it (C1/C2). No drift in warnings between freeze and
  build (SOURCES.md unchanged, C6).

## 5. Hygiene
- No tools installed (python3/git only; no pacman/uv/npx). No lane/fleet
  writes; no services started; no network calls beyond git-local reads.
  `TMPDIR=$S` for every run. Scratch `S=/fast/scratch/hyaku/kama-r47/V0Census`
  removed after copying artifacts (see below).

## 6. Absolute paths written
- Report: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/V0Census.md`
- Out dir `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/V0Census/`:
  `census-validate.out`, `start.out-equality.txt`, `w04-by-url.txt`,
  `append-only-forward.out`, `append-only-reversed.out`,
  `planned-rows-constraints.md`, `proposed-fix-sources-append-only.diff`,
  `selftest.patched.out`, `lane-patch.patched.json`.
