# K0Harm — no-harm attack on the round-46 planned edits

**Verdict: the planned edit set as assigned leaves four existing checks red and one of them green for a defect — `round42-selfdesc-reconcile.py` `met=False` (7 mismatches, all head-table rows the round's own edits stale), `sources-append-only.py` exit **2** on the lane's corpus (pre-existing since `052cb1e9`, so the round's SOURCES append is ungraded), `hexrun-census.py` unknown 21→24, `digest-ledger.py` exit 1 (already red, +1 if S486 cites a sha256) — while the frozen C2 counter reports `met=True` on a lane that just lost 29 lines of `corpus/QUALITY.md`. Three head-row re-anchors (depth ×5 facts, coverage ×1, calibration ×1) restore `met=True`; everything else is a one-line drafting rule or a tested 12-line guard patch.**

Measured on a single `git clone --shared` of the lane at `/fast/scratch/hyaku/kama-r46/K0Harm/lane`, checked out detached at `4a2a4d55d09dfacf83dc62d1b3fddae5f6d2a050`, with fixture commits made only there (`git rev-parse --show-toplevel` asserted before every commit; identity `K0Harm <k0harm@fixture.invalid>`). The lane repo, its jj state and its index were never written.

## 1. What was simulated

Planned edits, exactly as the wave assigns them (seats S1Row/S1Section, S9Skill, S2Cap, S9Readme/S9Quality, plus the C1 flag rule):

| # | Edit | Simulated as |
|---|---|---|
| 1 | `registry/release-recheck-b11906.tsv` | 13-column header + 91 rows, blobs re-derived from `/fast/scratch/hyaku/kama-r46/L1/llama.git` at `4d71b42f` |
| 2 | `corpus/SOURCES.md` new row + `## Round-46 release re-verification` section | S486 row for `tools/server/server-context.cpp` @ `4d71b42f`, `mined`/`on-release`, used-by = ledger + two knowledge entries; section with a 4-column preview table |
| 3 | Flags in used-by entries | one line naming the row id + `b11906` in `endpoint-identity.md`, `context-capacity.md`, `gguf-declared-identity.md`, `llamacpp-loading-lifecycle.md` |
| 4 | `SKILL.md` §Round-46 instrument registry | three table rows (both counters + `append-only-audit.py`) |
| 5 | 10th capability | mirror row in `## Capabilities`, `**Capabilities — canonical list as of round 46**` (10 rows), `§Retired` "6 axes and 10 capabilities", `§Saturation` first-working rounds `…, 46`, banner "round 46"/"Latest measured round: 46", `## Round 46` section, `### Planned (round 47)` |
| 6 | `PROVINCE.md` names `tools/append-only-audit.py` | one clause in the instruments row |

Commits: base `4a2a4d55` → **stage A `81bf5dfa`** (planned only) → **stage B `46a664b6`** (planned + 3 head-row re-anchors). Raw receipts: `.ufo/waves/round-46/w1/out/K0Harm/{base,stageA,stageB}.*`.

## 2. Check matrix (commands verbatim; exits measured)

| check | base `4a2a4d55` | planned `81bf5dfa` | + re-anchors `46a664b6` |
|---|---|---|---|
| `python3 tools/round42-selfdesc-reconcile.py --repo . --tip HEAD` | exit 1 `r41=1 … mismatches=1 met=False` | exit 1 **`r41=7 … mismatches=7 met=False`** | exit 0 **`mismatches=0 met=True`** |
| `python3 tools/gate-registry-check.py --repo . --rev HEAD` | exit 1 `registered 36 unregistered 2` | exit 0 `registered 38 unregistered 0` | exit 0 |
| `python3 tools/capability-repertoire-audit.py --repo . --tip HEAD` | exit 0 `listed 9 … met True` | exit 0 `listed 10 … met True` | exit 0 |
| `python3 tools/hexrun-census.py scan --repo . --rev HEAD` | exit 1 `unknown=21` | exit 1 **`unknown=24`** | exit 1 `unknown=24` |
| `python3 tools/digest-ledger.py scan --repo . --rev HEAD` | exit 1 `unknown=2 external_absent=1` | exit 1 same | exit 1 same |
| `sources-census.sh validate kama` (clone dir) | exit 0 (`W04`=93, `W01`=1, `E`=0) | exit 0 (93/1/0) | exit 0 (93/1/0) |
| `python3 tools/sources-append-only.py --from 4a2a4d55 --to HEAD --repo .` | — | **exit 2** | **exit 2** |
| `python3 tools/append-only-audit.py --repo . --to HEAD --json` | exit 1, 5 events (3 restored, 2 partial) | exit 1, 5 events | exit 1, 5 events |
| `python3 tools/round46-append-audit-check.py --repo . --tip HEAD` | exit 1 `table=0 met=False` (controls/base.c2.out) | exit 0 `met=True`, `lane_events=5` | exit 0 `met=True` |

Stage-A detail lines (`.ufo/waves/round-46/w1/out/K0Harm/stageA.selfdesc.out`), all seven:

```
detail: r41 depth sha256 SKILL.md cited 3046955b… observed 1f431ea8…
detail: r41 depth sha256 corpus/knowledge/endpoint-identity.md cited 0100ac6d… observed 85cca20a…
detail: r41 depth lines SKILL.md cited 1432 observed 1442
detail: r41 depth lines corpus/knowledge/endpoint-identity.md cited 218 observed 220
detail: r41 depth run `grep -c '^## ' SKILL.md` no stdout line == '33' (exit 0)
detail: r41 coverage sha256 PROVINCE.md cited 36d6bb3a… observed 9fffc811…
detail: r41 calibration run `python3 -c "import glob;print(len(glob.glob('corpus/lessons/*verifier-spotcheck.md')))"` no stdout line == '31' (exit 0)
```

## 3. Six axes — how the round can harm each

### 3.1 Operability — the SOURCES guard is already dead and the third tool is outside the gate

**(a) `tools/sources-append-only.py` cannot grade the lane's own corpus.** The guard fails closed on any "row-like line outside the parsed registry" (`tools/sources-append-only.py:76` regex, `:228` loop). The round-45 re-verification section added at `052cb1e9` has an id-first preview table (`corpus/SOURCES.md:514`, `| \`S010\` | ollama …`) whose first cell matches that regex, so every invocation exits 2:

```
$ python3 tools/sources-append-only.py --from 4a2a4d55 --to 4a2a4d55 --repo <clone>
error: 4a2a4d55:corpus/SOURCES.md:514: row-like line outside the parsed registry table; refusing to drop it
exit=2
$ python3 tools/sources-append-only.py --from 052cb1e9^ --to 052cb1e9^ --repo .
no append-only violations          exit=0        # before the section landed
$ python3 tools/sources-append-only.py --from 052cb1e9^ --to 052cb1e9 --repo .
error: 052cb1e9:corpus/SOURCES.md:514: …            exit=2   # the section is what broke it
```
Its `--selftest` still prints `42/42 selftest cases passed` exit 0 — that is the only evidence the operability row cites (`SCORECARD.md` operability row), so the row is green while the contract it names never runs on the corpus. Round 46 adds a *second* id-first table (my simulated section), keeping the guard dead and making every round-46 SOURCES edit ungradeable: a seat that relocates or drops a registry row while restructuring the section produces exit 2, not exit 1, and no diff line.

*Smallest safe correction (tested):* `.ufo/waves/round-46/w1/out/K0Harm/proposed-sources-append-only.patch` — a row-like line outside the registry is an error only when it belongs to a table whose header is the contract's eleven columns, or when it stands alone (no header above it); an id-first preview table with a non-contract header cannot hide a registry row. Measured on the patched copy: `42/42 selftest cases passed` exit 0, real pair `4a2a4d55 → 46a664b6` prints `added S486 (allowed)` / `no append-only violations` exit 0, and the guard's own fail-closed arm (`sources-append-only.py:493`) still exits 2. Interim drafting rule if the tool is not patched: never put a bare id in the first cell of a round section (`` `S037` b11755 → b11906 `` passes both guards).

**(b) The gate grades two of the three new tools, never the third.** Population regex `tools/gate-registry-check.py:70` is `.ufo/waves/round-*/count-*.py | tools/round<N>-*.py`; `tools/append-only-audit.py` matches neither. Removing its `SKILL.md` row entirely still prints `registered 38 unregistered 0 defective 0` (`.ufo/waves/round-46/w1/out/K0Harm/variants/V8-third-tool-invisible.out`). So S9Skill's expected receipt "unregistered 0" is a false green for the round's capability tool, and a future reader cannot find it through the gate.

**(c) Registration must be a table row.** Writing the C1 row as a prose bullet returns `unregistered tools/round46-append-audit-check.py`, `unregistered tools/round46-release-recheck-audit.py`, exit 1 (`variants/V9-prose-registration.out`). The gate's docstring says prose does not register; the seat must use the five-column table.

**(d) The SKILL.md edit itself re-stales the depth row** (three `r41` facts, §3.3).

### 3.2 Freshness — the new ledger is scanned as a document, and the read list is wrong

**(a) `hexrun-census.py` grows redder.** `registry/release-recheck-b11906.tsv` is a `.tsv` document; its 40-hex tokens must be classified. Three are new and unclassified: `4d71b42f…` (release), `9043fa2c…` (server-context.cpp @ b11906), `57514013…` (server-models.cpp @ b11906). Measured unknown **21 → 24** (`base.hexrun.out` vs `stageA.hexrun.out`). (`b6ebf752…`, server.cpp at b11906, lands as `lane_oid` because the lane's history already holds that blob as `.ufo/waves/round-41/w1/out/R41F09/b11887-server.cpp` — not red.) The token `57514013…` enters only through S479's row — the same row the read list omits (§3.2c).

**(b) A sha256 in S486's anchor adds an unexplained digest.** Following S060's anchor pattern (which carries `sha256 dd1de0f2…`), a citation of the new file's sha256 `61c1afcf…` moves `digest-ledger.py` unknown 2 → 3, exit 1 (`variants/V4-sha256-anchor.out`). Either cite no sha256 for S486 or add a `registry/digest-ledger.tsv` row.

**(c) The brief's read list is not what the bytes say, and S479 is carried unread.** Measured over the 91 b11889 ledger rows (`c1-population-readlist.txt`): **73** files are byte-identical between b11889 and b11906, not 71; **18** changed in the window (17 × `server-context.cpp`, 1 × `server-models.cpp`). The brief's 20-row list is exactly the frozen counter's carry-forward failure set (`c1-carried-forward.out`: `valid=71 unverified=20 unchanged=6 holds=65`, the 20 being S037 S042 S043 S060 S108 S109 S114–S125 S133 S138) — and it **omits S479**, the only `server-models.cpp` row, whose file changed at b11906 in the function its `teaches` cell rests on:

```
diff b11889..b11906 -- tools/server/server-models.cpp   (e1e006f1 → 57514013)
-        // same rule as mtmd_helper_model_can_chat()
+        // same rule as mtmd_helper_get_capabilities()
     …
         n_ctx_train       = info.n_ctx_train;        # line 540, S479's cited statement
```
The anchored ranges (2329, 2378-2379) are untouched, so the counter files S479 `valid` without reading — a text-equality blind spot against the lane's own round-44 rule ("each `holds` row was read for the code its `teaches` cell depends on"). The statement survives, the note's "same rule as `mtmd_helper_model_can_chat()`" framing does not.

**(d) `unchanged-file` does not mean "identical since b11889".** The counter's `changed` compares the b11906 blob with the **b11755 pin** (85 rows differ; only 6 rows are `unchanged-file`). Filing the 73 byte-identical-since-b11889 rows as `unchanged-file` yields `valid=7 unverified=84` (`c1-unchanged-file-misread.out`). The brief's "71 rows byte-identical" sentence invites exactly that.

**(e) A new row numbered ≤ S477 breaks the freshness run fact.** The head row runs `… int(…[1:])<=477 …` → `218`; my S486 keeps 218, renaming it S192 gives `no stdout line == '218'` → `r41=1` (`variants/V12-rowid-le477.out`).

### 3.3 Depth — the round's own required edits stale five anchored facts

`SKILL.md` and `corpus/knowledge/endpoint-identity.md` are the depth row's anchored blobs, and both are edited by the plan for reasons outside depth:
- the §Round-46 instrument registry (operability, §3.1c) adds 10 lines and one `##` heading → sha256 + 1432→1442 + `grep -c '^## '` 33→34 (three facts);
- S037's used-by is `corpus/knowledge/endpoint-identity.md`, so C1's flag rule appends there → sha256 + 218→220 (two facts).

That is **5 of the 7** stage-A mismatches. Any later flag edit to `SKILL.md` (S114–S125 are used-by `SKILL.md`) re-stales the row again: the re-anchor must be the **last** edit in the round, or it must be done twice. `rel` (one axis-specific run fact per row) passes throughout.

### 3.4 Coverage — PROVINCE must change, so its hash goes stale; counts must not be restated

The 10th capability's evidence cell (`tools/append-only-audit.py`) must appear in `PROVINCE.md` — that is the `province` fact of `tools/round42-selfdesc-reconcile.py` and the reason `capability-repertoire-audit.py` finds the row substantiated. Editing `PROVINCE.md` (line 17's instruments clause) changes the coverage row's anchored digest: `r41 coverage sha256 PROVINCE.md cited 36d6bb3a… observed 9fffc811…`. One more forced re-anchor.

Two secondary traps, both measured:
- **Do not restate registry counts** in `## Capabilities` (it currently says "Registry counts are not restated here"). A restatement is graded against the census and my guessed numbers were wrong by 2×: `caps: states 478 mined; census 208`, `states 5 queued; census 8` (`variants/V10-restated-counts.out`, `caps=4`). A prose line inserted *inside* the capability table also ends the table for the counter (`table_rows` stops at the first non-pipe line), dropping every row after it — that is the name-set mismatch in the same receipt.
- **A capability evidence cell may name only committed paths.** Naming `registry/append-only-events.tsv` (not committed) leaves `capability-repertoire-audit.py` at `unsubstantiated 0 met True` — it only requires *some* resolving path — but fails `province` (`variants/V5-province.out`, `province=1`). So caprep cannot catch this class; the self-description counter can.

### 3.5 Calibration — the new capability passes on a lane that just violated it

**(a) C2's predicate measures agreement, not harm.** A single commit dropping the last 30 lines of `corpus/QUALITY.md` (a declared append-only file; truncation class of round 45) produces one new event `{file: corpus/QUALITY.md, deleted: 29, restored_at_tip: 11, status: partial}` and `append-only-audit.py` exits 1 — while the frozen counter reports

```
selftest=1 fixture=1 lane=1 table=1 lane_events=6 lane_unrestored=0 lane_partial=4 met=True   exit=0
```

(`variants/V6-truncation.out`). The lane leg compares the tool with an independent recomputation and requires the exit code to *agree*, so a round whose integration truncates a self-description file still satisfies claim C2. That is a trade-off the fresh claim must state (the prereg's `limits` covers line identity and the 20-line threshold, not this), or C2's lane leg must additionally require `lane_partial` not to exceed the base value (2) and `lane_unrestored == 0`. Recommend recording it as a limit/finding for the closure — do not re-freeze the counter after data.

**(b) The calibration head row is already stale at the round base.** `r41=1` at `4a2a4d55`: the row's run fact cites `31` spot-check closures but the tree has **32** (`corpus/lessons/round-45-verifier-spotcheck.md` exists), and the row's prose still names the round-44 closure as latest. The prereg's plan (C2 only) does not include this, so a round-46 measurement that claims calibration work while the calibration row's own run fact is false is a self-description regression by omission. Re-anchoring it (`32`, round-45 closure) is one line.

**(c) The 10th capability couples five surfaces** — mirror names must equal canon names, `§Retired` must count capabilities, `§Saturation` must list first-working rounds from the canon, the banner must read round 46 + `Latest measured round: 46`, and `### Planned` must move to round 47 once a `## Round 46` heading exists (maxN becomes 46). Measured: with all five the counter reads `caps=0 retired=0 saturation=0 banner=0 planned=0`; each omission fails independently (`caps` in V10, `planned` when the heading is not renamed). Any partial edit to only one of them is a net harm.

### 3.6 Adjacency — the natural reporting surface is the anchored file

The lane's out-of-province habit is to report, never absorb, and the natural place for N1Overlap/N3Fleet's fleet-wide append-only finding is `corpus/knowledge/cross-lane-scope.md` — which is the adjacency row's anchored blob. One appended report row:

```
detail: r41 adjacency sha256 corpus/knowledge/cross-lane-scope.md cited 1801cb7f… observed ee4e7e9b…
detail: r41 adjacency lines … cited 87 observed 88
detail: r41 adjacency run `… sum(1 for l in … if l.startswith(chr(124)))` no stdout line == '16' (exit 0)
```

(`variants/V7-adjacency.out`, `mismatches=3`). Reporting the finding costs a re-anchor; absorbing it (claiming the fleet default as lane scope) would also break `PROVINCE.md`'s "Out of province → report, never absorb" paragraph, which the adjacency row cites by name. Keep N3Fleet's output in the wave directory and, if a lane line is added, re-anchor the row in the same commit.

## 4. SOURCES census — what passes and what a drafting slip costs

`bash scripts/sources-census.sh validate <clone>` is **exit 0 before and after** the planned edits, with identical warnings (`W04`=93, `W01`=1 for S481 tier-C mined). The new row adds no warning (new URL, `mined` with a real used-by). The failure modes are all drafting slips, each measured:

| slip | output | exit |
|---|---|---|
| bare id in the section table's first cell (`\| S037 \| … \|`) | `E12 S037 row outside Registry section` | 1 (`variants/V1-bare-id.out`) |
| two seats each draft the S486 row | `E03 S486 duplicate id` + `E04 S486 duplicate url … within scope …` | 1 (`V2-dup-row.out`) |
| used-by cites a receipt not yet committed | `E11 S486 missing used-by .ufo/waves/round-46/c1/rows.json` | 1 (`V3-missing-usedby.out`) |
| section heading inserted before the last registry rows | `E12` ×3 (S484, S485, S486) | 1 (`V11-misplaced-section.out`) |

Note the contrast with §3.1a: a bare id trips the census, a backticked id trips `sources-append-only.py` — an id cell that carries more than the bare id (`` `S037` b11755 → b11906 ``) is the only form that satisfies both.

## 5. Defects found (with the command that shows them)

1. **`tools/sources-append-only.py` cannot grade the lane corpus** (`tools/sources-append-only.py:76` regex, `:228` loop): exit 2 on `corpus/SOURCES.md` since `052cb1e9` because a legal preview table's id-first row is treated as a hidden registry row. Command and output: §3.1a. Proposed fix: `.ufo/waves/round-46/w1/out/K0Harm/proposed-sources-append-only.patch` (12 added / 6 removed lines), tested: selftest 42/42, real pair exit 0, fail-closed arm (`sources-append-only.py:493`) still exit 2. *Ownership:* the tool is lane-owned and not frozen; the patch is a proposal only.
2. **The gate cannot see `tools/append-only-audit.py`** (`tools/gate-registry-check.py:70`): `registered 38 unregistered 0` with no row for it. Smallest correction: widen the population (or an explicit allow-list), or state in the round's report that the capability tool is outside the gate's contract; otherwise "unregistered 0" overstates coverage.
3. **The brief's C1 read list is wrong and omits S479** (§3.2c): 73 identical / 18 changed, and `server-models.cpp` changed at b11906 in `server_model_meta::update_caps`. Smallest correction: add S479 to the read list (21 rows of work) and correct 71→73 in the assignment; the ledger must carry S479's `release_blob 57514013…`.
4. **C2 is satisfiable on a violating lane** (§3.5a): `met=True` with `lane_partial=4` after a 29-line partial deletion. Report as a limit; the lane leg should not regress relative to the base's `lane_partial=2`.

## 6. Ordered integration checklist (smallest set that keeps every existing check green)

1. Land the ledger, SOURCES row (> S477, e.g. S486) and section; **id cells not bare**; used-by names only committed paths; no new sha256 in the anchor unless a digest-ledger row lands with it.
2. Land the knowledge flags for every holds-reworded/drifted row (S479 included once read).
3. Land the three SKILL rows as **table rows**; note that `append-only-audit.py` is outside the gate population (defect 2).
4. Land `PROVINCE.md`, the mirror row, the round-46 canon list (10 rows), `§Retired` 10, `§Saturation` `…, 46`, banner round 46, `### Planned (round 47)`, the `## Round 46` section.
5. **Last**, in one commit, re-anchor the three head rows: depth (`SKILL.md` sha256 / 1442 lines / `grep -c` = 34, `endpoint-identity.md` sha256 / 220 lines), coverage (`PROVINCE.md` sha256), calibration (`32`, round-45 closure). Verify `python3 tools/round42-selfdesc-reconcile.py --repo <clone> --tip <commit>` → `mismatches=0 met=True` (measured at `46a664b6`).
6. Optionally add the three hexrun-ledger rows (or record `unknown 21→24` as debt) and carry the guard patch.

## 7. Limits and tooling

Simulation fidelity: the ledger's verdicts/witnesses are shape-only (I did not read 91 upstream files) — the token, census, gate and self-description effects do not depend on verdict values; the C1 numbers reported here (valid/unverified) come from carried-forward and misread variants built on the real b11889 ledger plus real b11906 blobs, and are labelled as such. The fixture commits live only in my scratch clone; the lane working tree was not modified (`git -C kama-shokunin status --porcelain` shows only the wave's own untracked `round-46/` paths). No tools were installed (pacman untouched per the orchestrator pause), no services touched, no subagents spawned.

Receipts (absolute):
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/K0Harm.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/K0Harm/{base,stageA,stageB}.{selfdesc,gate,caprep,hexrun,digest,census}.out`, `{base,stageA,stageB}.aoa.json`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/K0Harm/c1-carried-forward.out`, `c1-unchanged-file-misread.out`, `c1-population-readlist.txt`, `sources-guard.out`, `proposed-sources-append-only.patch`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/K0Harm/variants/variants.tsv` and the V1–V12 raw outputs
