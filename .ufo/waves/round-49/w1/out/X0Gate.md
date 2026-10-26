# X0Gate — round-49 integration prerequisites at `74558c71`

**Verdict:** the round-49 integration gate is **red at the build tip for two causes** — (1) neither round-49 counter is registered in `SKILL.md` (gate exit 1; it also drags round-43's `selftest` leg to 1), and (2) a **calibration anchor drift that predates the build** (SCORECARD states 34 spotcheck closures; the tree holds 35 since base `438127bc`) which fails round-41 C1, round-42 (`r41` leg) and round-43 (`spot` leg). Measured in a scratch clone: the two proposed registry rows plus a two-line SCORECARD re-anchor turn **all five prerequisites green** (`gate 0`, `r41 met=True`, `r42 met=True`, `r43 met=True`, `planned-pointer met=True`); a real `## Round 49` SCORECARD section additionally forces banner `Latest measured round: 49`, `### Planned (round 50)` and a `### Round-49 measured results` heading. One defect found in a **frozen** tool (gate cell splitting; not fixed, proposed only).

All runs are on a throwaway clone of the lane (`git clone --shared … /fast/scratch/hyaku/kama-r49/X0Gate/lane`), never the lane itself. Nothing was installed, no service was started, the clone and scratch were removed at the end.

## 1. What I ran at the build tip (`74558c71c38ceaeace15fd4cf8aa9d84977584b1`)

| # | Command (cwd = clone) | Exit | Line that matters |
|---|---|---|---|
| 1 | `python3 tools/gate-registry-check.py --repo <clone> --rev 74558c71…` | 1 | `registered 42 unregistered 2 defective 0` |
| 2 | `python3 tools/round41-scorecard-reconcile.py --repo <clone> --tip 74558c71…` | 1 | `axes=6 facts=36 hash_bad=0 lines_bad=0 run_bad=1 dead=0 score_bad=0 hollow=0 mismatches=1 met=False` |
| 3 | `python3 tools/round42-selfdesc-reconcile.py --repo <clone> --tip 74558c71…` | 1 | `r41=1 banner=0 planned=0 retired=0 saturation=0 caps=0 receipts=0 readme=0 province=0 rel=0 mismatches=1 maxN=48 met=False` |
| 4 | `python3 tools/round43-registry-audit.py --repo <clone> --tip 74558c71…` | 1 | `unreg=2 defect=0 flags=0 pins=0 selftest=1 dc=0 spot=1 hidden=0 pop=44 registered=42 mismatches=4 met=False` |
| 5 | `python3 tools/planned-pointer-check.py SCORECARD.md` (at tip) | 0 | ``pointer: ok (The live plan is `### Planned (round 49)` at the end of this file)`` … `met=True` |

Exact failures:

- (1) `unregistered tools/round49-append-audit-v4-check.py`, `unregistered tools/round49-replay-witness-audit.py`.
- (2)/(3) ``detail: calibration run `python3 -c "import glob;print(len(glob.glob('corpus/lessons/*verifier-spotcheck.md')))"` no stdout line == '34' (exit 0)``.
- (4) the two `gate unregistered …` lines; `detail: selftest: documented 'GATE_SELFTEST pass=6 fail=0', run printed 'GATE_SELFTEST pass=5 fail=1' exit 1`; `detail: spot: calibration row states 34, tree holds 35`.

Receipts: `out/X0Gate/baseline-gate.out`, `baseline-r41.out`/`.receipt`, `baseline-r42.out`/`.receipt`, `baseline-r43.out`/`.receipt`, `baseline-planned-pointer.out`.

Extra citation instruments (added text must not create digest/hexrun debt): `digest-ledger.py scan` exit 0, `tokens=127 … unknown=0`, and `hexrun-census.py scan` exit 1 with `unknown=2` (pre-existing, not this build's) at the tip; the `--details` output of both is **byte-identical** before and after the patch (`anchor-and-citation-checks.out`), so the rows add no new citation.

## 2. `gate-registry-check.py` — what the two round-49 counters need

Contract (`tools/gate-registry-check.py:6-58`, code `:69-121` population, `:148-176` registry rows, `:181-221` evaluation):

- population: every tracked `tools/round<N>-*.py` / `.ufo/waves/round-*/count-*.py`; both round-49 counters match, so both must appear **inside a cell of a data row** of a five-column table whose header passes `:168-175` (`Name | Kind / entry command | Exit map | Self-test / pinned values | Write scope`). A prose mention is `unregistered` (selftest arm `prose-only`).
- per row: `thin-row` (fewer than two non-empty cells), `empty-entry` (cell 1 empty), `empty-exit-map` (cell 2 empty), `missing-path:PATH` — every repo-relative path token in cells **1, 3 and 4** must exist at the evaluated revision (`:206-218`).
- Therefore: **do not cite `corpus/lessons/round-49.md` in a registry row before that file lands.** Measured: a five-cell row citing it yields `defective tools/round49-replay-witness-audit.py: missing-path:corpus/lessons/round-49.md`, exit 1 (`neg-pipefree-lesson-gate.out`). Keep the lesson pointer in the SCORECARD section, which these tools do not scan.

Placement and shape (precedent: `SKILL.md:1465` round-48 registry section, rows `:1471-1472`): a new `## Round-49 instrument registry (replay execution witness, append-only v4)` section appended after `### Re-running live evidence (v5, round 48)`, one lead paragraph, the five-column header, two rows. Full proposed text: `out/X0Gate/proposed-skill-rows.md`; unified diff against the build tip: `out/X0Gate/proposed-skill-rows.diff`.

**Deliberate shape choice: the rows are pipe-free.** The exit cell quotes the met-state line only (`witness=1 cap=1 newrow=1 witnessed=3/3 met=True` / `fixture=1 lane=1 scenarios=8/8 met=True`) instead of the tool's `a=0|1` template. Reason is finding **F1** below: an escaped `\|` breaks the gate's cell indexing, which silently disables the `missing-path` check for those rows and would also starve round-43's `pins` leg if the counters are ever added to it.

Result with the rows applied (commit `ea7ef566`, rows only): `registered 44 unregistered 0 defective 0`, **exit 0** (`draft1-gate.out`).

## 3. `round43-registry-audit.py` — what it needs beyond registration

Read of `tools/round43-registry-audit.py`: `unreg`/`defect` from the committed gate at TIP (`:109-131`), `flags` (`:132-150`), `pins` (`:151-170`), `selftest` (`:171-189`), `dc` (`:190-200`), `spot` (`:201-214`), `hidden` (`:215+`), `pop >= POP_MIN=28` (`:65`).

- **flags**: each registered counter's **entry cell** must name at least one `--flag`, and every flag it names must be declared by `add_argument("--flag"…)` in the counter source. Both counters declare exactly `--repo`, `--tip`, `--scratch`, `--out` (`tools/round49-replay-witness-audit.py:410-413`, `tools/round49-append-audit-v4-check.py:365-368`), and the drafted entry commands name only those. Negative control: adding `--witness-dir` to the C1 entry cell yields `flags=1 … detail: flags: tools/round49-replay-witness-audit.py row names no --flag or a flag absent from the source`, exit 1 (`neg-flags-r43.out`). Keep `--witness-dir`/`--witness-timeout` in the exit-map cell or prose only.
- **pins**: only `NEWSET` (round-35…43 counters). Round 49 is not in the frozen list, so **no sha256 pin is required**; my proposed rows cite the frozen counter sha256 as information (`86b4a40d…f0d6c1`, `26c465a9…066945`, both equal to `preregistration.json` `counter_sha256`). If a later round adds these paths to `NEWSET`, the pin must be in the 4th *physical* cell — another reason for pipe-free rows.
- **selftest**: `SKILL.md` documents `` `GATE_SELFTEST pass=6 fail=0` `` (`SKILL.md:1330`), and a real `--selftest` run at the tip must print exactly that and exit 0. At the build tip it prints `pass=5 fail=1` because arm 6 evaluates the lane's `master` and finds the two counters unregistered — i.e. registering them **is** the fix; with the rows applied the leg is `selftest=0` (`minimal-r43.out`).
- **spot**: the `| calibration |` row of `## Axes` must state `` `N` (outside closures on record) `` with `N` = number of `corpus/lessons/*verifier-spotcheck.md` blobs at the tip. At the tip: states 34, tree holds 35 → 1 mismatch.
- `dc`, `hidden`, `pop`: unaffected (`pop=44`, `registered=44`).

## 4. `round41-scorecard-reconcile.py` / `round42-selfdesc-reconcile.py` — what a round-49 SCORECARD section owes them

- **Frozen score vector**: `EXPECTED = {operability 8, freshness 8, depth 7, coverage 9, calibration 7, adjacency 7}` (`round41-scorecard-reconcile.py:57`). The round-49 claims (8→8, 7→7) keep it, so the `## Axes` table must **not** change scores; raising an axis would make r41 report `score_bad`.
- **Every SKILL.md edit forces the depth row re-anchor.** Adding the registry section changes three facts in the depth row (`SCORECARD.md:16`): measured at this tip — `sha256 d5ed2295…` → `108e941f…`, `(1484 lines)` → `(1493 lines)`, `grep -c '^## ' SKILL.md` `36` → `37`. Measured proof that rows alone are not enough: commit `ea7ef566` (rows, no re-anchor) gives r41 `hash_bad=1 lines_bad=1 run_bad=2 … met=False` with exactly those three `depth` details plus the calibration one (`draft1-r41.out`).
- **Calibration anchor**: the run fact and the `(outside closures on record)` figure must both equal the spotcheck-lesson count at the measured tip — 35 now (`SCORECARD.md:18`). This drift predates the build: at base `438127bc` the SCORECARD already said 34 while the tree held 35 (`anchor-and-citation-checks.out`). Fixing it also fixes r43 `spot`. If an outside `round-49-verifier-spotcheck.md` lands at integration, the figure becomes 36 and must be recomputed.
- **r42, once a `## Round 49` section exists** (`maxN` = greatest `^## Round (\d+)`, `round42-selfdesc-reconcile.py:117-131`):
  - head must say `Latest measured round: 49` (`:190`) while keeping `operability + calibration` (`:187`) and not reintroducing `operability and freshness` / `adds **zero** verified completed rounds` (`:188-189`);
  - the **first** `## Planned` section must name `### Planned (round 50)` and a line `### Planned (round 50)` must exist followed by a numbered item (`:192-206`);
  - `## Retired` must state `6 axes` and `11 capabilities` (canon unchanged) (`:208-213`);
  - `## Saturation` must state the derived vector in head-table order, `first-working rounds …`, and **`nudge inactive`** (min(operability 8, calibration 7) = 7 < 8) (`:215-220`);
  - `## Capabilities` names must equal the highest-numbered canon list, and any `N opened|mined|queued|rejected` in it must equal the SOURCES census at the tip (`:222-236`). The current head (§Capabilities) restates **no** census figures, and the build's `S494`/`S495` are `docs | A` rows, so nothing forces a head-caps edit; census at the tip is `11-cell rows 236 {opened 0, mined 217, queued 8, rejected 11}` if any is stated.
  - `receipts` scans only sections whose heading names round 40 or 41 (`RECEIPT_ROUNDS = (40, 41)`, `:75`, `:238-251`) — **round-49 receipts are not graded**, and round-40/41 sections must not lose receipts (corrections belong under a `record corrections` heading);
  - `readme` wants every non-dot top-level entry backticked in `README.md` (`:253-257`); `province` wants every `tools/`/`registry/` token in a canon evidence cell to appear in `PROVINCE.md` (`:258-264`) — if the round-49 canon row cites `tools/round49-*`, `PROVINCE.md` must name them;
  - `rel` needs each axis row to keep a `run` fact containing its needle; calibration's is `verifier-spotcheck` (`:70-74`, `:265-269`).
- Measured proof of the banner/planned coupling: with a `## Round 49` heading added and the banner untouched, r42 prints `banner=1 planned=1 … mismatches=2 maxN=49 met=False` with `detail: banner: head lacks 'Latest measured round: 49'` and `detail: planned: section does not name '### Planned (round 50)'`.

## 5. `planned-pointer-check.py`

Passes at the tip (`met=True`, pointer names round 49), so it is not currently red — but it constrains the scribe:

- the **first** `## Planned` section (`SCORECARD.md:51-53`) must keep the contiguous sentence ``The live plan is `### Planned (round <N>)` at the end of this file``; r42 forces `N = maxN + 1`, i.e. **round 50** once `## Round 49` exists;
- every `§Round-<N> measured results` reference anywhere in the file needs a line `### Round-<N> measured results`. Measured: adding `§Round-49 measured results` without the heading prints `measured: dangling reference §Round-49 measured results — no line '### Round-49 measured results'` and exits 1; adding both makes it `met=True` (`baseline-planned-pointer.out`, `minimal-planned-pointer.out`, `simulated-planned-pointer.out`).

## 6. The two-file patch, measured

`out/X0Gate/proposed-skill-rows.diff` (SKILL.md, +9 lines: heading, paragraph, header, separator, two rows) and `out/X0Gate/proposed-scorecard-reanchor.diff` (SCORECARD.md: depth row anchors, calibration 34→35). Applied on a clone of `74558c71` (commit `e81f2e4f`):

| # | Exit | Line |
|---|---|---|
| 1 `gate-registry-check.py --rev e81f2e4f` | 0 | `registered 44 unregistered 0 defective 0` |
| 2 `round41-scorecard-reconcile.py --tip e81f2e4f` | 0 | `axes=6 facts=36 … mismatches=0 met=True` |
| 3 `round42-selfdesc-reconcile.py --tip e81f2e4f` | 0 | `r41=0 banner=0 … mismatches=0 maxN=48 met=True` |
| 4 `round43-registry-audit.py --tip e81f2e4f` | 0 | `unreg=0 defect=0 flags=0 pins=0 selftest=0 dc=0 spot=0 hidden=0 pop=44 registered=44 mismatches=0 met=True` |
| 5 `planned-pointer-check.py SCORECARD.md` | 0 | `met=True` |

Receipts: `out/X0Gate/minimal-*.out` / `minimal-*.receipt`. Then a **simulated** round-49 section on top (commit `f2bed8b6`: banner → round 49, pointer → round 50, `## Round 49 — …`, `### Planned (round 50)` + item, `### Round-49 measured results`; diff `simulated-round49-section.diff`) keeps all five green with `maxN=49` (`simulated-*.out`). This is a shape demonstration, not proposed SCRIBE text.

The anchor arithmetic the L1 must redo after the **final** SKILL.md edit (my numbers are exact only for "rows appended after the round-48 block and nothing else changed"):

| fact | build tip | after proposed section |
|---|---|---|
| `SKILL.md` sha256 | `d5ed2295a6a9841b01adb53d4b411b64b784c9221856fe6a510669ee60e65183` | `108e941faf1fe5275bd456a2ce169bf689fe0078220788df75aa6a03f6eb4d21` |
| lines | 1484 | 1493 |
| `grep -c '^## ' SKILL.md` | 36 | 37 |

## 7. Findings

**F1 (defect, frozen tool — proposed only).** `tools/gate-registry-check.py:144-145` splits a row on *every* pipe including the escaped `\|`, then `:210` path-checks only `row[1], row[3], row[4]`. Any row that quotes a `0|1` output line (the round-46/47/48 pattern) therefore splits into 7–8 cells and its **Self-test** and **Write-scope** cells are silently never path-checked, contradicting the contract at `:44-52`. Measured pair on the same missing path `corpus/lessons/round-49.md`, same counter:
- escaped-pipe row (8 cells): `registered 44 unregistered 0 defective 0`, **exit 0** (`neg-escapedpipe-lesson-gate.out`);
- pipe-free row (5 cells): `defective tools/round49-replay-witness-audit.py: missing-path:corpus/lessons/round-49.md`, **exit 1** (`neg-pipefree-lesson-gate.out`).
Proposed fix (do not apply to the frozen counter in place): `cells()` → `re.split(r"(?<!\\)\|", line.strip().strip("|"))` with `\|` unescaped after split, or map physical cells back to the five markdown cells by counting unescaped pipes. Consequences avoided here by writing the rows pipe-free; a later `NEWSET` addition for these counters would also need pipe-free rows, because r43 `pins` reads `cells[2]`/`cells[3]` (`round43-registry-audit.py:165`).

**F2 (pre-existing drift, not caused by the build).** `SCORECARD.md:18` states `34 (outside closures on record)` while `corpus/lessons/*verifier-spotcheck.md` has held 35 blobs since base `438127bc` (counted 35 at `438127bc`, `36d5ed26`, `74558c71`; `anchor-and-citation-checks.out`). It fails r41 `run_bad`, r42 `r41`, r43 `spot`. Fix in the round-49 SCORECARD re-anchor (state 35, or the count at the integrated tip). The round-49 build touched neither `SKILL.md` nor `SCORECARD.md` (diff `438127bc..74558c71`: 16 files, none of them).

**F3 (coupling, not a separate defect).** Gate `--selftest` prints `pass=5 fail=1` at the tip against the documented `pass=6 fail=0` (`SKILL.md:1330`) purely because its lane arm evaluates `master` and finds the two unregistered counters; registering them restores `pass=6 fail=0` and r43's `selftest` leg to 0. Do not "fix" the documented number to 5.

**F4 (risk).** Any path cited in a registry row's entry/self-test/write-scope cells must exist at the measured revision. `corpus/lessons/round-49.md` lands only at integration, so it must stay out of the row (it may sit in the SCORECARD round-49 section, which none of these five tools scans) until the commit that lands the file.

## 8. Limits of this seat

- Only the five named prerequisite tools were run; the round-49 counters themselves were **not** re-run here (network + loopback llama-server; the L1 dry run covers them, and their frozen bytes match `preregistration.json`).
- The re-anchor numbers are valid for the exact proposed SKILL.md insertion; any other SKILL.md edit changes all three depth facts.
- `hexrun-census.py` exit 1 (`unknown=2`) is pre-existing at the tip and unchanged by the patch; out of this seat's scope, flagged for the L1.
- Every measurement names a committed revision (`74558c71`, or a scratch-clone commit built on it); the lane's working tree carried sibling wave edits (LOG.md, SCORECARD.md, SKILL.md, corpus/QUALITY.md, corpus/README.md) while this seat ran, and none of them entered a measurement. The lane itself was never written, committed or jj-mutated.
- No tool installed or upgraded (no pacman; nothing added to any PATH directory); no service started; no llama-server process was created, so no leftover to tear down (the two `llama-server` processes visible during the run belong to other seats' scratch dirs and were left alone).

## Files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/X0Gate.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/X0Gate/` — `proposed-skill-rows.md`, `proposed-skill-rows.diff`, `proposed-scorecard-reanchor.diff`, `simulated-round49-section.diff`, `baseline-*.out`, `baseline-*.receipt`, `draft1-*.out`/`.receipt`, `minimal-*.out`/`.receipt`, `simulated-*.out`/`.receipt`, `neg-flags-r43.out`/`.receipt`, `neg-pipefree-lesson-gate.out`, `neg-escapedpipe-lesson-gate.out`, `anchor-and-citation-checks.out`
