# CRT01ClaimsAttack — C1 (calibration) and C3 (freshness) attack, kama round 71 w1

Seat: critic/attack. Lane tip at first read `f3ee44f4`; tools `tools/pre-report-gate.py` and
`tools/round71-province-host-claims.py` **absent at 21:37**, present at 21:39/21:40 (bounded poll,
30 s steps). Everything below is measured on the bytes named; the lane worktree moved under me
(peers editing), so every receipt carries its tool/host sha.

| artifact | sha256 (at receipt time) |
|---|---|
| `tools/pre-report-gate.py` (lane) | `07cfc04fbba413f851034734bfee1122b12463ed5d65486762d6bd736cb3bd0b` (mtime 21:48:25) |
| `tools/round71-province-host-claims.py` | `1f6bb43aa9e9e0f0f43e096cfcce2b677dcaa0cdfab266bb1975dc90fea8b0ff` (mtime 21:42:22) |
| `PROVINCE.md` (worktree) | `7fa09fab3cb5179519a878d54b204322daab9f01e5c859965cb4bce52f78a592` (298 lines) |
| `SCORECARD.md` (worktree) | `df697ded650389934e5ab73e1b87c2d2ce2166b6c9f0efce46284fb3768c1718` |

No tool was installed, nothing was written to the lane, PROVINCE.md, the freeze, `~/.config`,
`~/.local/bin` or `.ufo/state`. All fixtures live under
`/fast/scratch/hyaku/kama-r71/CRT01ClaimsAttack/` (deleted at exit); receipts kept in
`.ufo/waves/round-71/w1/CRT01ClaimsAttack/`.

## C1 — verdict: kill rules HELD; the **target sentence is falsifiable** and the frozen counter cannot see it

### 1. SURVIVED — wrong `--round` yields `failed=0 uncommitted=0` with round-71 work uncommitted

Fixture `fx/case-wave-uncommitted` (a green tip; `?? .ufo/waves/round-71/w1/leak.md` added),
graded with the lane's current gate and the lane's instruments:

```
$ git -C F status --porcelain -uall -- .ufo/waves/round-71
?? .ufo/waves/round-71/w1/leak.md
$ python3 tools/pre-report-gate.py --repo F --tools-dir tools --round 71   --tip master
PRE_REPORT_ARM round-clean exit=0 FAIL files=1 first=?? .ufo/waves/round-71/w1/leak.md
PRE_REPORT round=71 arms=5 failed=1 uncommitted=1          EXIT=1      # correct
$ ... --round 70   --tip master
PRE_REPORT round=70 arms=5 failed=0 uncommitted=0          EXIT=0      # FALSIFIED
$ ... --round 9999 --tip master
PRE_REPORT round=9999 arms=5 failed=0 uncommitted=0        EXIT=0      # FALSIFIED
```

`--round 70` is the freeze's own counter value (plans §C1). On the green fixture every round name
(`71 70 9999 0 -1`) prints green (`c1_battery.txt`, "baseline"). The tool never checks that
`.ufo/waves/round-<N>` exists at the tip, nor that `<N>` is the round the tip belongs to, so the
cleanliness arm is vacuous for any name that is not the dirty round. This is the counter/target
mismatch in the freeze itself: the counter names round 70, the target names round 71.

### 2. SURVIVED — uncommitted round work outside the wave dir is invisible (scope)

```
$ git -C F status --porcelain -uall -- corpus/lessons/round-70.md
 M corpus/lessons/round-70.md
$ python3 tools/pre-report-gate.py --repo F --tools-dir tools --round 71 --tip master
PRE_REPORT round=71 arms=5 failed=0 uncommitted=0          EXIT=0
```
(`c1-current-bytes-confirmations.out`.) The cleanliness arm is `git status -- .ufo/waves/round-N`
(gate line 210) plus WLC's five declared paths; a round artifact in `corpus/lessons/`, `plans/`,
`tools/` or `.ufo/waves/round-71-notes.md` is ungraded. The predicate is literally scoped to the
wave dir, so this is a **scope mismatch with the target sentence** ("`uncommitted=0` at the report
tip"), not a coding error.

### 3. SURVIVED — two uncommitted files *inside* the wave dir, invisible to git

```
$ find F2/.ufo/waves/round-71/w1/scratch -type f
.../.ufo/waves/round-71/w1/scratch/.gitignore     # contains "*"
.../.ufo/waves/round-71/w1/scratch/leak.out
$ git -C F2 status --porcelain -uall -- .ufo/waves/round-71     # empty
$ python3 tools/pre-report-gate.py --repo F2 --tools-dir tools --round 71 --tip master
PRE_REPORT round=71 arms=5 failed=0 uncommitted=0          EXIT=0
```
Same result with `.git/info/exclude` and with `git update-index --assume-unchanged` on a tracked
wave file that is then byte-changed (`c1_battery.txt`, cases `hidden-ignored`, `hidden-exclude`,
`hidden-assume-unchanged`). The literal predicate — "no path under `.ufo/waves/round-<N>/` is
uncommitted" — is violated while the tool prints green: the arm defines "uncommitted" as
"git-visible", and git can be told not to see a path. Severity: the nested-`.gitignore` variant is
plausible (a seat's scratch dir), the other two need deliberate local config.

### 4. HELD — the four routes that the gate *does* close

| route | fixture | result |
|---|---|---|
| uncommitted file in the wave dir, right `--round` | `case-wave-uncommitted` | `round-clean exit=0 FAIL files=1`, exit 1 — names the arm |
| stale newest-closure pointer | `case-kill-stale-pointer` | `newest-closure exit=1 FAIL STALE_CALIBRATION …`, exit 1 |
| missing declared self-record path | `case-kill-missing-path` | `worktree-landing exit=1 FAIL … | MISSING PROVINCE.md`, exit 1 |
| dirty declared path | `case-kill-dirty-path` | `worktree-landing exit=1 FAIL … | DIRTY SCORECARD.md`, exit 1 |
| missing instrument binary | `case-missing-instrument` | `worktree-landing exit=2 FAIL … can't open file …round67-worktree-landing-check.py`, exit 1 |
| instrument failure masked by a pipe | by construction | arms are argv lists run by `_run` (gate:171), no shell, no pipe; red instruments propagate their exit (all rows above) |
| committed-but-CRLF declared path | `case-crlf-full` | WLC `clean=5` (byte-identity with HEAD, correct); exit 1 comes from the *reconciler* hash citation on SKILL.md, i.e. fail-closed in the right direction |
| `--tip` = round-start base while tip is HEAD | `case-tip-base` | `failed=2`, exit 1 (fail-closed; see note) |

Note: `--tip` is never compared with the branch tip; it is only forwarded to the three rev-taking
instruments, which fail closed on an unreconciled base (an ancestor tip *would* be graded as the tip
if it were reconciled — untested, the fixture base is not).

### 5. FALSIFIED (cross-cutting) — the self-record's own citation makes arm 1 unpassable

At the measured tip (`HEAD e2b860c8`) the calibration row carries this run fact (the worktree carried
it too at 22:02; a peer dropped it from the worktree by 22:09, so the landing commit decides):

```
run `python3 tools/pre-report-gate.py --repo . --round 71 --tip master` → `PRE_REPORT round=71 arms=5 failed=0 uncommitted=0` (exit 0)
```

`round41-scorecard-reconcile.py:68` (`RUN_RE`) parses exactly that shape and `run_fact` (:136) runs
it with `bash -c` in a clone of the tip. The gate now refuses re-entry
(`07cfc04f`, docstring lines 27–33; `_run` at :171 sets `PRE_REPORT_GATE_DEPTH`):

```
$ PRE_REPORT_GATE_DEPTH=1 python3 tools/pre-report-gate.py --repo . --round 71 --tip master
PRE_REPORT_RECURSION depth=1 refused: the scored gate is being re-entered through an executed
SCORECARD run fact (gate -> selfdesc reconciler -> round-41 run-fact harness -> gate);
cite `python3 tools/pre-report-gate.py --selftest` there instead
EXIT=3
```

Measured at HEAD `e2b860c8` (lane, read-only):

```
PRE_REPORT_ARM selfdesc exit=1 FAIL detail: r41 calibration run `python3 tools/pre-report-gate.py
  --repo . --round 71 --tip master` exit 3 != 0
PRE_REPORT round=70 arms=5 failed=3                          # 1 of the 3 is this clause
```

Isolation on fixtures (both tips reconciled to `mismatches=0` except for the clause): `fx/selfref`
(citation kept, tip `2355dac6`) → reconciler `met=False`, gate `failed=1`, sole detail the gate's own
run fact (nested exit 1 — pre-guard gate copy); `fx/nocite` (clause removed, tip `f20569bc`) →
reconciler `met=True mismatches=0`, gate `PRE_REPORT round=71 arms=5 failed=0 uncommitted=0`, exit 0
(`c1-selfref-isolation.out`). A line-only citation (no `(exit 0)`) is also red — the demanded literal
is the composed verdict itself. With the current lane gate (`07cfc04f`) the nested invocation exits 3.

**Consequence:** the frozen after-state ("`failed=0 uncommitted=0` at the report tip" **and** the
calibration row *executing* the gate) is unsatisfiable; the gate's own docstring prescribes the fix
(cite `--selftest` or a receipt path), which the 22:09 worktree already does but the tip does not. The tool's selftest cannot catch this: its green arm injects
stubs (`_STUB_SELFDESC`, gate:275) via `--tools-dir`, so the composed real path is never exercised.
Also note the r41 hash coupling: a *committed* CRLF SKILL.md is WLC-clean but reds the reconciler
(citation `cb8105da…` vs observed `182d19fc…`) — a self-record that treats a byte-identical commit as
drift.

### 6. Note — subdirectory `--repo` and stderr-as-record

`--repo .ufo`: the arm-5 pathspec resolves relative to the subdirectory (`warning: could not open
directory '.ufo/.ufo/waves/'`), so it matches nothing; and because `_run` returns `stdout+stderr`,
that **warning is counted as a porcelain record**: `round-clean exit=0 FAIL files=1 first=warning: …`.
Overall exit 1, so no false green — but the arm is wrong twice (relative pathspec; stderr
contamination inflates `uncommitted`, a false-red mechanism wherever git warns). Count stdout only.

## C3 — verdict: **target met at the tip** (`uncovered=0`, exit 0); predicate's rewrite clause is **not** enforced

Frozen counter, verbatim, 22:02 (`c3-frozen-counter.out`):
`PROVINCE_HOST_CLAIMS markers=11 tags=12 extra=4 contradicted=14 uncovered=0 exit=0`, exit 0; 16
correction lines (12 marker tags + 4 extras), one per tag. My independent host probes agree with
every correction verdict except one framing detail (`ufo-src`: present via the declared
`~/Projects/ufo-fsd-alpha` fallback while `UFO_SRC` is unset — the tool's own search order).

| route | fixture / command | result |
|---|---|---|
| (i) right tag, flipped verdict | 14 flipped fixtures (`c3-v2-cases/i_flip_*`) | `uncovered=1`, exit 1 — **HELD** (the two that stay 0 are `qwen-coder-unit`, `janitor-md`: claim and probe already agree, so coverage is `n/a`, not an evasion) |
| (i') wrong tag: superset/prefix/sibling/underscore/case | `i2_wrongtag_*` | `uncovered=1` each — **HELD** (kill rule ii) |
| (ii) correction dated before / same-day / far-before | `ii_date_*` | `uncovered=1` each — **HELD** (strictly later; string compare of ISO dates) |
| (ii') impossible calendar date `2026-99-99` | `ii2_date_impossible` | `uncovered=0`, exit 0 — **SURVIVED**: the date is never calendar-validated; any lexicographically larger string covers |
| (iii) false correction first, true after | `iii_false_then_true` | 0 — HELD per the predicate's existential wording ("carries a later … line") |
| (iii') true first, false correction later | `iii2_true_then_false_later` | 0 while a later **false** verdict line stays in the document — boundary: later contradictions are never graded |
| (iv) duplicated tag paragraph, inserted first with a later date | `iv_dup_marker_later_first` | `markers=12 tags=12`, `uncovered=1` — false red (claim date is `setdefault`-first); no duplicate/rewrite diagnostic |
| (v) delete a base marker paragraph | `v_delete_marker` | `PROVINCE_HOST_CLAIMS_REWRITTEN janitor-md`, exit 1 — **HELD** (kill rule iii) |
| (v') delete the paragraph **and re-add the same tag** in a new paragraph | `v2_delete_then_readd` | `markers=11 tags=12 … uncovered=0 exit=0`, `rewritten=[]` — **SURVIVED**: kill rule (iii) says a deleted base marker line exits 1; the check is tag-presence only (`round71-province-host-claims.py:460`) |
| (v'') rewrite a base marker line's body (tag kept) | `v3_rewrite_body` | exit 0 — **SURVIVED**: the predicate says "deleting **or rewriting** a base marker line exits 1 (`REWRITTEN`)" |
| (v''') rewrite a base marker's **date** (2026-10-31 → 2026-10-30) | `ix_marker_date_rewrite` | exit 0, no `REWRITTEN` — same gap, one-token edit |
| (vi) extra claim whose probe is a stub | source + `--json` | no stub: `probe_windows`/`probe_python3_alias`/`probe_ss_flock` spawn real commands, `probe_ntfs_path` does a real `git init/add/commit/checkout` of `pipe|name.txt` and removes it; evidence strings carry live output — **HELD** |
| (vi') unusable `--scratch` root | `--scratch <chmod 555 dir>`, `--scratch <regular file>` | uncaught `PermissionError` / `FileExistsError` traceback, **exit 1**, no pinned summary line — documented map says exit 2 could-not-evaluate ("an NTFS probe setup failure"). **SURVIVED** (exit map) |
| undeclared marker tag | `vi_undeclared_tag` | exit 2 fail-closed with a message — HELD, but no `PROVINCE_HOST_CLAIMS` line on that path |

Minor: `probe_ntfs_path` fails **open** (an OSError creating `pipe|name.txt` returns `"present"`);
a correction inside a fenced code block is still parsed (no fence awareness). Neither fires on a green run.

**Disagreement to report, not to edit:** C3's target holds, but the predicate's rewrite clause and
kill rule (iii) are narrower in the tool than in the freeze (tag presence vs. line identity). The
smallest safe correction: `--base` must compare the base marker **paragraph text** (tag, date, and
the marker line itself) against the tip, not the tag set — then delete+re-add and the date rewrite
both print `REWRITTEN`. For C1: (1) arm 5 must require the wave dir at the tip and tie `--round`
to it (or refuse when it does not exist) — otherwise `--round 70/9999` is a vacuous green; (2) run
the frozen counter with `--round 71`, not 70; (3) extend the cleanliness arm to the round's declared
write set (self-record + round-touched paths), not just the wave dir; (4) count stdout only; (5)
keep the calibration row from *executing* the scored gate (cite the receipt path or `--selftest`).
Each correction is a tool/plan edit and therefore outside this seat.

---

## Could not verify
- The lane never reached the C1 after-state while I reviewed it (peers in flight): at 22:02
  `--round 70` → `failed=3`, `--round 71` → `failed=4 uncommitted=61`, HEAD `e2b860c8`; the
  after-state claims are fixture-based (tips `2355dac6`, `f20569bc`, recorded).
- The pre-guard gate's exact recursion depth (it terminated in 43 s at the fixture); the post-guard
  refusal is deterministic (exit 3). `git` behaviour under NTFS: not reachable on this host.

## Receipts (under `.ufo/waves/round-71/w1/CRT01ClaimsAttack/`)
`environment.txt`, `final-lane-state.out`, `c1-b1-round71.out`, `c1-round-name-sweep-lane.out`,
`c1-current-bytes-confirmations.out`, `c1_battery.txt` (fixture gate copy `d0957e0b`, pre-guard; the
headline rows were re-run on lane `07cfc04f` in `c1-current-bytes-confirmations.out`),
`c1-selfref-isolation.out`, `c1-selftest.out`, `c3-frozen-counter.out`, `c3-selftest.out`,
`c3-v2-cases/*.out`,
`c3-cases/*.out`, `ix_marker_date_rewrite.out`, plus the drivers (`run_battery*.py`,
`selfref_probe.py`, `isolate_selfref.py`, `fix_citations.py`).
