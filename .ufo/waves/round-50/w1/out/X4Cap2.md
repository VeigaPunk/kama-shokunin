# X4Cap2 — round-50 capability census prerequisites (lane kama)

**Verdict:** the round-50 canonical capability table (11 rows: `append-only-audit` reworded for v5 at first-working round 46, `live-receipt-replay` reworded for the process-bound witness and the model mapping at 47) plus the `## Capabilities` mirror are drafted and demonstrated on a scratch clone at `97c864be` with the draft appended: the frozen `tools/capability-repertoire-audit.py` reports `listed 11 observed 11 missing 0 unsubstantiated 0 met True` (exit 0), and a one-row truncation control reads `missing 1 met False`, so the canonical resolution provably moved off the round-49 table. No lane file was edited; that commit is scratch-local and dies with the scratch.

## Deliverables (all under `.ufo/waves/round-50/w1/out/X4Cap2/`)

| File | What it is |
|---|---|
| `canonical-section.md` | the exact text to append at the end of `SCORECARD.md` (heading `**Capabilities — canonical list as of round 50**`, intro paragraph, 11-row table) |
| `mirror-replacement.md` | the exact replacement for the `## Capabilities` mirror block, `SCORECARD.md:117-131` at `97c864be` (intro line + 11 rows; header and separator unchanged) |
| `draft.diff` | `git diff 97c864be 2f0ae652 -- SCORECARD.md`: 3 hunks, `21 insertions(+), 3 deletions(-)` |
| `cap-before.json`, `cap-after.json`, `cap-control.json`, `cap-after-head.json` | census receipts: baseline, draft at the build commit, truncation control, draft at the lane tip |
| `cap-runs.out` | raw run record: every command, its output and exit code |

## What the draft says (and what it does not)

- No capability row is added; the 11 names are exactly the round-49 names in the same order, so `observed` stays 11 and `missing` stays 0.
- `append-only-audit` (first-working round **46** unchanged): the round-49 row text is kept clause for clause except the origin clause. It now states v5: a deleted line in an eligible exempt section stays ungraded only when its **origin** — the union, over every birth of the line's key (the line bytes with one trailing carriage return removed) among the commits reachable from the tip, of the section titles holding that key in the birth commit's blob — contains one of the file's exempt titles, "so it is a property of the commit graph and its blobs rather than of any `rev-list` listing order"; a section title is the last `## ` line that is not inside (nor itself) a CommonMark 0.31.2 §4.5 fenced block. Binding, threshold, restoration measures and exit semantics are byte-identical to round 49. Evidence pointer adds `.ufo/waves/round-50/measured/c2-build.out`.
- `live-receipt-replay` (first-working round **47** unchanged): the round-49 row text is kept except for the two round-50 mechanisms — the live child runs `python -I` with only the allow-listed environment names (`PATH`, `HOME`, `LANG`, `LC_ALL`, `TMPDIR` under the work directory) and a parent-death signal, and the replay sets the same signal on itself, so killing whatever started it takes replay, live tool and server down; and a rerun must record `model_mapping` for the file the running server maps (read from `/proc/<pid>/maps` as dev/inode/pathname, re-opened by pathname with `O_NOFOLLOW`, fstat-checked and hashed) with `mapped` true and the receipt's model sha256, else `model-mapping:<reason>` is a mismatch. Provenance verification, the witness hold, the sparse/size refusal, the stable projection and `--compare` are byte-identical to round 49. Evidence pointer adds `.ufo/waves/round-50/measured/c1-build.out`.
- Wording was taken from the landed tools, not from the assignment: `tools/kama-live-replay.py:96-115` (`set_own_pdeathsig`, `live_env` = `LIVE_ENV_KEYS` + `TMPDIR`), `:307-348` (`-I` argv, `preexec_fn` pdeathsig, `model-mapping:*` mismatches), `tools/kama-llamacpp-live.py:678-724` (`model_mapping`), `tools/append-only-audit.py:4-21` (v5 `key`/`fence`/`section`/`birth`/`origin`) and `tools/round50-append-audit-v5-check.py:19-36` (the same definitions from the frozen counter side).

## Evidence

Scratch clone: `git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin $S/lane`, `--show-toplevel` = `$S/lane`, then `checkout --detach 97c864be`. `git -C $S/lane diff --quiet HEAD 3b79eadd -- SCORECARD.md` exited 0, i.e. `SCORECARD.md` is byte-identical at the build commit and the lane tip, so the draft applies to either base.

The draft was applied in the clone only (`SCORECARD.md:117`, `:130-131` replaced; the section appended after line 2870) and committed as `2f0ae652` (parent `97c864be`): `git diff --numstat` → `21	3	SCORECARD.md`; file length 2870 → 2888 lines. Hunk ranges in `draft.diff`: `@@ -114,7 +114,7 @@` (mirror intro), `@@ -127,8 +127,8 @@` (the two reworded rows), `@@ -2868,3 +2868,21 @@` (the appended section).

| Run | Command (tool unmodified, from the lane) | Output | Exit |
|---|---|---|---|
| baseline at `97c864be` (unedited) | `python3 tools/capability-repertoire-audit.py --repo $S/lane --tip 97c864be… --out cap-before.json` | `listed 11 observed 11 missing 0 unsubstantiated 0 met True`, `canonical_line 2838`, `capability_tables 15` | 0 |
| draft at `2f0ae652` | same, `--tip 2f0ae652…` | `listed 11 observed 11 missing 0 unsubstantiated 0 met True`, `canonical_line 2876`, `capability_tables 16` | 0 |
| control: same draft, round-50 table's last row truncated | same, `--tip <control>` | `listed 10 observed 11 missing 1 unsubstantiated 0 met False`, `missing_names ["live-receipt-replay"]`, `canonical_line 2876` | 1 |
| draft cherry-picked onto lane tip `3b79eadd` | same, `--tip 0fd94d56…` | `listed 11 observed 11 missing 0 unsubstantiated 0 met True` | 0 |
| instrument selftest | `python3 tools/capability-repertoire-audit.py --selftest` | `CAP_SELFTEST pass=2 fail=0` | 0 |

The control is the load-bearing one: with the round-49 table still resolving, a truncated round-50 table would read `missing 0`; it reads `missing 1` while `canonical_line` stays at the round-50 header (2876), so the highest marker (50) and the first capability table after it are what the census reads. The baseline run shows the predicate is not vacuously true.

Pointer resolution was checked per row, not just per the tool's `any()` rule, at `0fd94d56`: all 11 rows resolve every path token they cite (`cap-runs.out` §4). `.ufo/waves/round-50/measured/c1-build.out` and `c2-build.out` are absent at `97c864be` and present from `3b79eadd` on (`cap-runs.out` §5); at `97c864be` the two reworded rows are still substantiated by `tools/append-only-audit.py` + `registry/append-only-contract.tsv` and `tools/kama-live-replay.py` + `tools/kama-llamacpp-live.py`, which is why `unsubstantiated` stays 0 there.

## Integration notes for the L1

1. **Land the two edits together.** The audit resolves the canonical table only; the mirror is human-facing and no counter reads it, so a stale mirror (still naming round 49, or still carrying the round-49 row text) passes silently.
2. **Keep the round-49 table byte-intact** and append `canonical-section.md` after the current last line (`SCORECARD.md:2870` at `97c864be`/`3b79eadd`, the "Survivors route to round 50…" paragraph). Line arithmetic: the mirror block keeps its 15 lines (3 lines change content, none added), the appended section adds 18 lines (2870 → 2888).
3. **Keep the canonical table immediately after the heading.** The audit takes the *first* capability-shaped table (4 columns, last header containing "First working round") after the highest `canonical list as of round N` marker; a round-50 measured-results table with a fifth column or a different last header is not capability-shaped and may sit below it, but another 4-column `First-working round` table placed between heading and table would take over.
4. **No `append-only-audit` event from either edit.** The mirror change is 3 changed lines in the re-derived head, whose line count is unchanged (exempt window maximum not below the parent); the appended section is 18 lines, below the 20-line threshold, and is a birth rather than a deletion. The round-50 C2 lane measurement (`.ufo/waves/round-50/measured/c2-build.out`: `ungraded_lines 89`, both events within their native exempt counts) therefore stays valid if integration lands the mirror + section after measurement; if it lands before, the same numbers hold because neither edit is a mass deletion.
5. **Pointers:** the two reworded rows cite `.ufo/waves/round-50/measured/c{1,2}-build.out` (committed at `3b79eadd`, the build battery). If integration prefers the measured receipts, re-point to `.ufo/waves/round-50/measured/c1.out`/`c2.out` — both are `.out` tokens and resolve; nothing else in the row changes.

## Defects and limits

No defect found in the draft path. Two audit-tool design limits matter for a future round, recorded here rather than patched (`tools/capability-repertoire-audit.py` is outside this seat's scope): `unsubstantiated` counts a row as substantiated when **any** repo-relative token in its evidence cell resolves (`evaluate()`, `tools/capability-repertoire-audit.py:139-149`, the predicate at `:148`), so one dead supplementary pointer in a multi-pointer cell is invisible; and canonical selection is positional (`:129-138`), so table ordering is the only thing that decides which list counts. The demonstration checks pointers per row precisely because of the first limit.

## Risks

- If a round-50 seat lands a new capability row anywhere in `SCORECARD.md`, the canonical table must carry it or the census goes red (`missing` names it).
- The scratch commit hashes `2f0ae652` and `0fd94d56` are local to the deleted scratch clone; the durable evidence is `draft.diff` + the four JSON receipts + `cap-runs.out`. Re-apply from `canonical-section.md` / `mirror-replacement.md`, not from those hashes.
- Pre-existing and known: the two round-50 counters are still unregistered in `SKILL.md`; not re-reported.

## Tooling, scope, cleanup

No tool installed or upgraded (no pacman transaction; nothing from `uv`/`npm`/`~/.local/bin`); only `git` and `python3` were used. The lane was never written to: all edits and commits are in `$S/lane`, a `--shared` clone, whose `--show-toplevel` was asserted before the first commit. This seat started no server, made no network request and killed no process; the `llama-server` processes visible during the seat belong to seats `Sen3Teardown`, `J4Decoy` and `R0Controls2`. Scratch `/fast/scratch/hyaku/kama-r50/X4Cap2` was deleted after the receipts were copied here.

## Paths written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/X4Cap2.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/X4Cap2/canonical-section.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/X4Cap2/mirror-replacement.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/X4Cap2/draft.diff`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/X4Cap2/cap-before.json`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/X4Cap2/cap-after.json`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/X4Cap2/cap-control.json`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/X4Cap2/cap-after-head.json`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/X4Cap2/cap-runs.out`
