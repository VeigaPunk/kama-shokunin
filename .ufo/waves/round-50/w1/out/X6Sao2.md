# X6Sao2 — census + SOURCES append-only at the round-50 build

**Verdict:** at the build tip `97c864bead3ee4a2f629574e77263d33834ec98a` the census delta is exactly the three new tier-A `mined` rows S496–S498 plus their three dangling `used-by corpus/lessons/round-50.md` names (E11 ×3, the known integration item; zero new warning classes, W04/W01 sets byte-identical to `census/start.out`), **but `tools/sources-append-only.py` refuses the build registry — exit 2, `corpus/SOURCES.md:251` (S498) "unterminated table row (no closing pipe)"** — so round-50's source rows are *not* append-only-graded at the build; the append-only property itself holds (independent row/cell diff: 0 removed, 0 immutable-cell edits, 3 added) and the build's own battery recorded the same exit 2; the tick-parity defect is remediated downstream at `3d42897b` (guard then exits 0, added S496–S498), leaving the latent parser trap and a bisect hazard for the build tip.

Scratch `S=/fast/scratch/hyaku/kama-r50/X6Sao2`, clone `$S/lane` (`git clone --shared`), trees `$S/tree97` (97c864b) and `$S/treef` (601c8889) via `git -C lane archive | tar -x`. System date 2026-10-27T00:55Z. Full command log: `out/X6Sao2/commands.md`.

## 1. Census, whole-fleet invocation (required command)

```
$ bash /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama
exit=1
```
Whole output: `out/X6Sao2/census-root-kama.out` (97 lines) — 93 × W04, 1 × W01, 3 × E11; no E01–E10/E12, no usage error. (The fleet run reads the lane worktree, which at integration HEAD `3b79eadd` differs from the 97c864b blob only in the S498 `teaches` cell — see §4; census output is unaffected.)

## 2. Census `--file` on a scratch copy at the build

```
$ bash scripts/sources-census.sh validate --file $S/tree97/corpus/SOURCES.md
exit=1        -> out/X6Sao2/census-file-build.out (97 lines, same code set as §1)
$ bash scripts/sources-census.sh census   --file $S/tree97/corpus/SOURCES.md
exit=0        -> out/X6Sao2/census-aggregates-freeze-build.out
rows 239  tier.A 228  tier.B 7  tier.C 4  status.mined 220  status.queued 8  status.rejected 11  invalid 0  missing 0
```
Freeze for comparison (`--file $S/treef/corpus/SOURCES.md`, `exit=0`): `rows 236 tier.A 225 tier.B 7 tier.C 4 mined 217 queued 8 rejected 11`. Delta build−freeze = +3 rows, +3 tier A, +3 mined; queued/rejected/invalid/missing unchanged.

### Findings by code, with the rows they name

| code | n | rows |
|---|---|---|
| `E11` used-by path missing on disk (`scripts/sources-census.sh:566`) | 3 | `S496` (SOURCES.md:249), `S497` (:250), `S498` (:251) — each names `corpus/lessons/round-50.md`, absent at the build (verified: `test -e $S/tree97/corpus/lessons/round-50.md` false). Their other target, `corpus/knowledge/llamacpp-loading-lifecycle.md`, exists, so no additional E11. |
| `W01` tier-C mined with non-`—` used-by | 1 | `S481` (unchanged from start.out) |
| `W04` same URL across scopes | 93 | `S031, S043, S056, S060, S064, S065, S067, S071, S077–S088, S093, S097, S100, S103, S105, S108–S110, S112, S114–S125, S127, S129–S135, S137, S141–S173, S181–S189, S191` (93 ids, gaps as listed; full lines in `census-file-build.out`); pre-existing — set-identical to start.out |

Exit 1 is caused by the E11 findings only; W-codes never change status.

### Comparison with `census/start.out`

```
$ diff <(cat .ufo/waves/round-50/census/start.out) out/X6Sao2/census-root-kama.out
95,96c95,97
< kama  ok   .../corpus/SOURCES.md
< exit=0
> kama  E11  S496 missing used-by corpus/lessons/round-50.md
> kama  E11  S497 missing used-by corpus/lessons/round-50.md
> kama  E11  S498 missing used-by corpus/lessons/round-50.md
```
- W04 set identity: `comm -3` over sorted W04 lines = **0 lines**. W01 line md5 `c193b779771caccf1d83b6433cc41fcf` on both.
- start.out is a faithful freeze snapshot: `validate --file $S/treef/corpus/SOURCES.md` reproduces it exactly, the only diff being the recorded path label (`out/X6Sao2/census-file-freeze.out`).
- So the round-50 census delta is *only* the three new rows and their three pending lesson links; status went clean (`ok`, exit 0) → 3 E-findings (exit 1) for that one reason.

## 3. SOURCES append-only guard (required command) — DEFECT at the build tip

```
$ python3 tools/sources-append-only.py --from 26ecba64ad6fb571d09074b07202d1618a46ecd1 --to 97c864bead3ee4a2f629574e77263d33834ec98a --repo $S/lane --json
{"error": "97c864bead3ee4a2f629574e77263d33834ec98a:corpus/SOURCES.md:251: unterminated table row (no closing pipe)", "violations": null}
exit=2                                    -> out/X6Sao2/append-only-build.json
```
Control pairs with the same tool blob (`f269ef0d5dfa…` at 26ecba6, 601c8889, 97c864b, 3d42897b, 3b79eadd):
`base→base` exit 0; `base→601c8889` exit 0; `base→3d42897b` exit 0 `{violations: [], added: [S496,S497,S498]}`; `base→3b79eadd` exit 0 same. So the refusal is localized to the build tip's registry.

**Cause (exact):** `corpus/SOURCES.md:251` (row `S498`) carries **7 backticks** — an odd count because the `teaches` cell quotes the CommonMark text ``"…at least three consecutive backtick characters (`) or tildes (~)."``. `tools/sources-append-only.py:112-116` toggles a single `in_code` flag on every backtick, so after the last tick `in_code` stays true, every following `|` is treated as code content, and `split_cells` returns `None` at `:127-131`, raised as the `unterminated table row` ParseError at `:257`. `has_bare_pipe` (`:135-148`) has the same parity assumption.

**This is a parse refusal, not an append-only violation.** An independent tolerant-parse diff of the two blobs (scratch script, `commands.md` §5) gives:
```
base rows 236  build rows 239 ; removed: [] ; added: ['S496','S497','S498']
no IMMUTABLE CHANGE lines ; no mutable-cell change lines
odd-backtick rows: build = S498 (7) only ; base = none
```
Rows are unique (239 ids, 0 duplicates), the three new rows are appended after `S495` at lines 249–251; the only two id-order inversions (lines 222/223, 226/227) exist identically at the base, so round-50 added none.

**It was already measured, not missed:** the build battery's own receipt is `git show 3b79eadd:.ufo/waves/round-50/measured/sao-build.out` — same error line, `exit=2` — and the remediation is commit `3d42897b` "build-fix - S498 row markdown tick parity so sources-append-only row parser accepts it", which rewrites the S498 `teaches` cell (drops the quoted glyph pair `` (`) `` / `(…)`). Consequences to record:
1. The build tip `97c864b` cannot be graded by this guard at all (exit 2), so any bisect or re-measure at the build tip reproduces the refusal rather than a clean grade.
2. `measured/` at `3b79eadd` holds only `*-build.out`; there is **no post-fix `sao` receipt**. My runs at `3d42897b`/`3b79eadd` supply that measurement (`exit=0`, `added: S496,S497,S498`, `violations: []`).
3. The corpus-side fix is a rewrite of an immutable `teaches` cell (allowed here because the pair graded by the guard is base→tip and S498 is *added*, but it means the shipped quote no longer carries the literal backtick/tilde glyphs it quotes); the latent trap stays: any future row that quotes a lone backtick re-breaks the guard, and such a row cannot be repaired without another `teaches` rewrite.

### Proposed fix (advisory; lane file not edited)

`out/X6Sao2/proposed-sources-append-only-code-span.diff` — replace the parity toggle with CommonMark 0.31.2 §6.2 run matching: a backtick run of N opens a code span only when a run of exactly N closes it; an unpaired run is literal text and does not hide the delimiter after it. Touches `split_cells` (`:91-132`) and `has_bare_pipe` (`:135-148`) via one new `code_span_end` helper; docstrings updated to state the rule. Validated on a scratch copy of the build's tool (`$S/prop/sources-append-only-patched.py`):

```
$ python3 $S/prop/sources-append-only-patched.py --selftest              -> 45/45 selftest cases passed, exit=0
$ ... --from 26ecba64a --to 97c864bea --repo $S/lane --json              -> {"violations": [], "added": ["S496","S497","S498"], "ok": true}, exit=0
$ ... --from 26ecba64a --to 3d42897b  --repo $S/lane --json              -> exit=0, no violations
$ ... --from 26ecba64a --to 26ecba64a --repo $S/lane                     -> "no append-only violations", exit=0
```
i.e. the patched guard grades the build tip clean *without* needing the corpus rewrite, keeps every existing selftest case (including "pipe inside backticks" and "escaped pipe"), and still refuses genuine malformations by cell count. Evidence copy: `out/X6Sao2/append-only-build-patched.json`.

## 4. Cross-tool observations (no fix required)

- `scripts/sources-census.sh` is backtick-agnostic (gawk, `-F'|'`): it accepts the S498 row the append-only guard refuses. Consequence: a clean census is not evidence that the registry is append-only-gradeable; round 50 shows the two guards disagreeing at the build. Registration evidence needs both.
- `scripts/sources-census.sh:502` labels `--file` output rows with lane `file`, not the lane id, so `--file` receipts cannot be diffed against a lane run without normalizing the first column (I did; §2 comparison). Cosmetic, not a grading defect.
- No E08 on S498's `opened 2026-10-27`: today at run time is 2026-10-27 (UTC), i.e. present, not future; the row's date is consistent with the build clock (commit `3d42897b` is dated 2026-10-26 21:28 −0300 = 2026-10-27 00:28 UTC).

## 5. Files written

- `kama-shokunin/.ufo/waves/round-50/w1/out/X6Sao2.md` (this report)
- `kama-shokunin/.ufo/waves/round-50/w1/out/X6Sao2/commands.md`
- `kama-shokunin/.ufo/waves/round-50/w1/out/X6Sao2/census-root-kama.out` (whole fleet-root validate output, 97 lines)
- `kama-shokunin/.ufo/waves/round-50/w1/out/X6Sao2/census-file-build.out`
- `kama-shokunin/.ufo/waves/round-50/w1/out/X6Sao2/census-file-freeze.out`
- `kama-shokunin/.ufo/waves/round-50/w1/out/X6Sao2/census-aggregates-freeze-build.out`
- `kama-shokunin/.ufo/waves/round-50/w1/out/X6Sao2/append-only-build.json` (exit 2 at the build)
- `kama-shokunin/.ufo/waves/round-50/w1/out/X6Sao2/append-only-build-patched.json` (exit 0 with the proposed parser)
- `kama-shokunin/.ufo/waves/round-50/w1/out/X6Sao2/s498-row-build.txt` (exact S498 line bytes at 97c864b)
- `kama-shokunin/.ufo/waves/round-50/w1/out/X6Sao2/proposed-sources-append-only-code-span.diff`

No lane, fleet, or shokuknow file was modified; no git mutation outside the scratch clone/export; no tool installs; no services started (no `llama-server` was run, so nothing to tear down).
