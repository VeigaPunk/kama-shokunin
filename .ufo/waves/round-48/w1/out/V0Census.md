# V0Census — round 48, lane kama (seat V0Census-2)

**Verdict: census at the build is clean apart from exactly two expected pre-integration E11s (S492, S493 → `corpus/lessons/round-48.md`, absent at 380bcdff, present on disk now); the mandated `sources-append-only.py` run fails closed with exit 2 — a known, already-routed defect (r47-D8 → seat X9SourcesGuard; K0Harm F1), to which I add: the mandated-pair reproduction, proof the append-only substance holds (+2 rows, 0 deletions), and a tested result that the round-46 K0Harm patch grades the mandated pair exit 0.**

Axes (godspeed): calibration (mandated item), evidence fidelity (every number below is from a run I executed), zero lane mutation (one `git clone --shared`, read-only git elsewhere).

Method: scratch `/fast/scratch/hyaku/kama-r48/V0Census-2` (`TMPDIR` pointed there); one `git clone --shared` of the lane at `$S/lane` (`git rev-parse --show-toplevel` asserted equal to the clone); all tools run against the clone or scratch copies. No tooling installed (nothing needed; pacman guard respected). Lane, fleet repo and siblings untouched.

## 1. Mandated runs — commands and exit codes

| # | Command | Exit | Result |
|---|---|---|---|
| 1 | `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama` | 0 | `kama	ok	/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md`; 94 W lines (93 W04 + 1 W01), 0 E lines |
| 2 | same, `--file` on a bare scratch copy of `corpus/SOURCES.md` at 380bcdff | 1 | 437 E11 + 94 W — **all 437 E11 spurious**, see §3 caveat |
| 3 | same, `--file` on a build-tree copy (full `git archive 380bcdff…` extracted, file at `<tree>/corpus/SOURCES.md`) | 1 | exactly 2 E11 (S492, S493) + 94 W — see §2 |
| 4 | `python3 tools/sources-append-only.py --from 33e0058… --to 380bcdff… --repo $S/lane` (human and `--json`) | 2 | `error: 33e005827742b29772b153cda036ec9f27f653be:corpus/SOURCES.md:520: row-like line outside the parsed registry table; refusing to drop it` — see §4 |
| 5 | control: same tool, `--from 6b7e6cf8d30b5794ed72fe97eb0e666f9b0572a9` (base^) `--to 33e0058…` | 2 | same error at base:520 — failure predates the build |
| 6 | control: `--selftest` | 0 | `42/42 selftest cases passed` — tool intact; the exit 2 is data-driven fail-closed |
| 7 | addition: round-46 K0Harm patch applied to a scratch copy of the tool, then run on the mandated pair | 0 | `added S492 (allowed)` / `added S493 (allowed)` / `no append-only violations`; patched `--selftest` still `42/42` exit 0 |

Raw outputs for every row: `out/V0Census/*.out` / `*.json` (paths at the end).

## 2. Census findings by code (build tree, `--file` mode, lane label `file`)

Errors (exit 1):
- `E11	S492 missing used-by corpus/lessons/round-48.md` — row at build `corpus/SOURCES.md:245` (status `mined`, opened 2026-10-26, recheck `every round`; its other used-by path `corpus/knowledge/llamacpp-loading-lifecycle.md` exists at the build and is not flagged).
- `E11	S493 missing used-by corpus/lessons/round-48.md` — row at build `corpus/SOURCES.md:246`.

Both are the **expected pre-integration state**: `git ls-tree 380bcdff… -- corpus/lessons/` contains no `round-48.md` (0 matches); the item itself notes the lesson "lands at integration". On the lane's current on-disk working copy both are already resolved — `corpus/lessons/round-48.md` exists on disk and the on-disk `corpus/SOURCES.md:245-246` carries the same two rows, which is why run #1 exits 0 with no E11. Not a defect; do not hold the build for it.

Warnings (identical set before and after the build; no new warnings from S492/S493):
- `W04` ×93 — duplicate URL across scopes. Full list in `out/V0Census/file-validate-buildtree.out` and `out/V0Census/summary-by-code.txt`. The two new rows add none: S492's pinned `/resolve/499bc8821c6b12b4e53c5bffcb21ec206f212d81/…` URL is distinct from S490's `/resolve/main/…` and S039's `/blob/…` URLs; S493's `huggingface.co/docs/huggingface_hub/en/guides/download` is new.
- `W01` ×1 — `S481 tierC mined used-by=corpus/knowledge/runtime-health-surface-processes.md, corpus/lessons/round-43.md, corpus/knowledge/runtime-health-surface-matrix.md, corpus/knowledge/endpoint-health-probe-conventions.md, corpus/knowledge/served-model-id-resolution.md, corpus/knowledge/engine-pin-watch.md` (pre-existing since round 43, unchanged).

No E01–E10, no E12 anywhere: both new rows are structurally valid registry rows inside `## Registry` (S492's recheck `every round` is a valid symbolic cadence; opened 2026-10-26 is not future).

## 3. Comparison with `.ufo/waves/round-48/census/start.out`

`diff start.out fleet-validate-live.out` → only difference is start.out's trailing `exit=0` capture line (my run recorded the exit separately). The live run reads the lane's on-disk working copy (git HEAD `b85783e8…` "round-48: wave spec kama-r48-w1", a descendant of the build; the jj working copy already carries the integration lesson), so: **live worktree == pre-wave baseline, byte-identical findings**; the build adds exactly +2 rows and +2 E11 (§2), both resolved on disk now.

`--file` mode caveat (method note, not a lane defect): `--file` resolves used-by paths against `dirname(file)/..` (`scripts/sources-census.sh:501`), so a bare scratch copy of the file alone flags every used-by path of every mined row (437 E11, all spurious). A meaningful `--file` validation needs the file at `<root>/corpus/SOURCES.md` with the surrounding tree present — I extracted the full build tree with `git archive 380bcdff… | tar -x` for run #3. Future seats: use the build-tree layout, not a bare copy.

## 4. Append-only guard — exit 2 (known defect; my additions only)

**Not a new finding** — already routed this round: round-47 closure D8 (`preregistration.json:66` "r47-D8: frontier: tools/sources-append-only.py parser repair by a wave seat, integrated if it lands (no claim)"), build seat `X9SourcesGuard` (build_spec.py:173-174), round-48 `K0Harm` F1, and the round-47 lesson Mistakes row. I report only what I add:

1. **Mandated-pair reproduction**: exit 2 on `33e0058… → 380bcdff…` (run #4) and on `base^ → base` (run #5). The round-48 SOURCES append therefore gets **no guard certification at all** — exit 2 is the fail-closed parse-error code, not a violation verdict.
2. **Root cause, pinned**: `ROWLIKE_RE` (`tools/sources-append-only.py:76`) matches markup-wrapped S-id first cells; the global sweep (`:227-232`) raises on any such line outside the parsed `## Registry`. The trigger is the round-45 re-verification ledger table: `corpus/SOURCES.md:520`@33e005 (`:522`@380bcdff) is `` | `S010` | ollama `c1737589` → main `66ab8482` | holds | … ``. Exactly **27** lines match ROWLIKE_RE outside the Registry at the build — 6 in the round-45 ledger (base :520, :521, :522, :525, :527, :528; :523/:524/:526 have a second backtick token or comma after the id, so the regex does not match them) and 21 in the round-46 ledger (base :565-585). Fixing one line would not unblock the tool; it stops at the first offender.
3. **Provenance**: introduced by `052cb1e9` (round-45 C1 evidence; `git log -L 520,520:corpus/SOURCES.md 33e0058…` traces the line there); the tool is unchanged since `c6dc46fa` (round-18; `git log -- tools/sources-append-only.py`). So the guard has graded no SOURCES transition since round 45, while `SKILL.md:578` (at the build) still declares it a gate "run over every consecutive commit pair of the round (KQ22)".
4. **Substance holds anyway** (independent confirmation of K0Harm F1): `git diff 33e0058…..380bcdff… -- corpus/SOURCES.md` = **2 insertions, 0 deletions** — S492 (:245) and S493 (:246), both inside `## Registry` (no E12), nothing else touched (`out/V0Census/sources-diff-base-to-build.txt`; sole commit in range touching the file: `380bcdff` "round-48: build …"). The round-48 change is append-only in substance; only machine certification is blocked.
5. **Patch test (integration input)**: the round-46 proposal `.ufo/waves/round-46/w1/out/K0Harm/proposed-sources-append-only.patch` applies cleanly to the current tool (`patch -p1`, no fuzz), keeps `--selftest` at 42/42 exit 0, and grades the mandated pair **exit 0** with `added S492 (allowed)` / `added S493 (allowed)` (`out/V0Census/append-only-patched.out`, `patched-selftest.out`). By contrast, round-48 K0Harm's F1 diff is prose-embedded in `findings.md` (ellipsis lines, F2 fragments mixed into the block; no standalone `.patch` in `out/K0Harm/`) — illustrative, not machine-applicable as written. **Integration should land exactly one fix** (X9SourcesGuard's dedicated diff when it lands, else the round-46 patch) and re-run the KQ22 consecutive-pair sweep; do not stack both.

## 5. Known items acknowledged, not re-reported

gate-registry-check's two unregistered round-48 counters; the round-41/42/43 counters' 33-vs-34 spot-check count; hexrun-census's one unknown (`d0012618`, round-47 fleet report commit). All outside this seat's item.

## 6. Residual risk / verification gaps

- Census modes `overdue` and `shared` were not run (not mandated).
- The E11 resolution on disk is integration's doing; I verified file existence and row presence on disk, not the lesson's content.
- The patched-tool run is scratch-only evidence of the round-46 proposal; the lane tool itself is untouched (frozen for this seat).

## Files written (absolute)

- Report: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/V0Census.md`
- Evidence: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/V0Census/{fleet-validate-live.out, file-validate-buildtree.out, file-validate-bare.out, append-only.out, append-only.json, append-only-pred.out, append-only-patched.out, patched-selftest.out, selftest.out, sources-diff-base-to-build.txt, summary-by-code.txt}`
