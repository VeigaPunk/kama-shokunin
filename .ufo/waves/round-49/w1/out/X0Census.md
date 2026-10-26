# X0Census — round 49, lane kama: census + append-only guard at the build

**Verdict:** the append-only guard is green at the build (`added S494 (allowed)`, `added S495 (allowed)`, `no append-only violations`, exit 0), but the census is **red at the measured commit 74558c71** — `validate` exits **1** with 2 × E11 for S494/S495 naming `corpus/lessons/round-49.md`, a path that exists only as an untracked scribe file in the lane worktree; the wave's own before/after census pair (`census/start.out` ≡ `S9Mistakes/census/end.out`, byte-identical) never samples that state, and E11 itself is existence-only, so a zero-byte stub clears it.

Measured at build `74558c71c38ceaeace15fd4cf8aa9d84977584b1`, base `438127bc01ff3b99f98468549d58046f932490ef`, from a `git clone --shared` at `/fast/scratch/hyaku/kama-r49/X0Census/lane` and a `git archive` tree extract of the tip.

## 1. Child's factual answers

### 1.1 `validate --root … kama` at the lane (whole output kept)

```
$ bash /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate \
    --root /home/vgpnk/Projects/shokunin kama
→ census-validate-worktree-2331.out   EXIT=0   (95 lines: 93×W04, 1×W01, ok)
```

Run at 23:31Z against the **worktree**, where the scribe's `corpus/lessons/round-49.md` now exists (6396 B, `git status --porcelain` → `?? corpus/lessons/round-49.md`). At 23:28Z the same command returned **exit 1** with the two E11 lines (`census-validate-74558c71.out`, 12777 B) — see §2 F1.

### 1.2 Same registry at the measured commit, `--file` on a scratch copy

The naive reading of "a scratch copy of `corpus/SOURCES.md`" is a defect trap: `--file` derives the used-by root from the **copy's** location (`scripts/sources-census.sh:495-503`), so a bare copy yields 441 phantom E11s:

```
$ git -C lane show 74558c71:corpus/SOURCES.md > $S/SOURCES-74558c71.md
$ bash scripts/sources-census.sh validate --file $S/SOURCES-74558c71.md
→ census-validate-file-74558c71.out   EXIT=1   (441×E11, 93×W04, 1×W01)
   e.g. "file E11 S001 missing used-by corpus/knowledge/runtime-health-surface-matrix.md"
```

Correct form — extract the tip tree, then `--file` the committed blob inside it (addresses F3):

```
$ git -C lane archive 74558c71 | tar -x -C $S/srccopy
$ bash scripts/sources-census.sh validate --file $S/srccopy/corpus/SOURCES.md
→ census-validate-file-mirror-74558c71.out   EXIT=1
   93 W04 · 1 W01 (S481) · 2 E11:
   file	E11	S494 missing used-by corpus/lessons/round-49.md
   file	E11	S495 missing used-by corpus/lessons/round-49.md
```

### 1.3 Append-only guard `--from 438127bc --to 74558c71`

```
$ python3 kama-shokunin/tools/sources-append-only.py \
    --from 438127bc01ff3b99f98468549d58046f932490ef \
    --to   74558c71c38ceaeace15fd4cf8aa9d84977584b1
added S494 (allowed)
added S495 (allowed)
no append-only violations
EXIT=0
```

Run from the fleet root **without `--repo`** (the seat's literal form; default resolves to the lane) and again with `--repo $S/lane`; identical output. Independent cross-check of the same claim without the tool:

```
$ git -C lane diff --numstat 438127bc 74558c71 -- corpus/SOURCES.md
2	0	corpus/SOURCES.md          # 2 added lines, 0 deleted
$ git -C lane diff --unified=0 438127bc 74558c71 -- corpus/SOURCES.md
@@ -246,0 +247,2 @@                 # one insertion hunk at corpus/SOURCES.md:247-248, no hunk removing anything
$ python3 tools/sources-append-only.py --selftest  → 45/45 selftest cases passed, EXIT=0
```

### 1.4 Warnings/errors by code, with the rows they name, versus `census/start.out`

| code | at 74558c71 (this seat) | `census/start.out` | delta |
|---|---|---|---|
| E11 | **2** — S494, S495 → `corpus/lessons/round-49.md` | 0 | **+2 (new, build-caused)** |
| W01 | 1 — S481 tier-C mined, 6 non-`—` used-by | 1 — S481 | 0 |
| W04 | 93 — S031 S043 S056 S060 S064 S065 S067 S071 S077 S078 S079 S080 S081 S082 S083 S084 S085 S086 S087 S088 S093 S097 S100 S103 S105 S108 S109 S110 S112 S114-S125 S127 S129-S135 S137 S141-S173 S181-S189 S191 | 93 | 0, **set-identical** (`diff` of the W04 lines → no output) |
| E01–E10, E12 | 0 | 0 | 0 |
| exit | **1** | 0 | **regressed** |

`census` (counts) at the build — `census-mode-74558c71.out`, EXIT=0: `rows 236; tier.A 225; tier.B 7; tier.C 4; status.mined 217; status.queued 8; status.rejected 11; missing 0`.
`overdue` — `census-overdue-74558c71.out`, EXIT=0: 236 symbolic cadences, incl. `S494 recheck=on-release opened=2026-10-26` and `S495 …`; nothing judged overdue.

`start.out` is reproducible: `validate --file` on the **base** blob (`438127bc:corpus/SOURCES.md`) inside the tip tree gives exactly `93 W04 · 1 W01 · ok · exit 0`. The base blob names no `round-49`/`round49` path (`grep -c` → 0), so the comparison is faithful.

### 1.5 Row provenance the census does not check (verified by hand)

- `corpus/SOURCES.md:247` S494, `:248` S495 (tip); both in `## Registry` (no E12), tier A, `mined`, `opened 2026-10-26`, recheck `on-release` (no E08/E09), unique ids (no E03), no new W04 (their URLs are commit-qualified `caa8191d…`, not the `704366d7…` set).
- S494 anchor `lines 686-735 of .ufo/waves/round-49/c1/server-README-caa8191d.md` resolves exactly: `### POST /tokenize` at copy line **686**, `### POST /detokenize` at **731**, block ends 735.
- S495 anchor resolves: `This symbolic link can be dereferenced normally; attempting` at `.ufo/waves/round-49/c1/proc_pid_exe.5.txt:75`; footer `Linux man-pages 6.19  2026-02-08` at line 123 — matches the row's "man-pages 6.19, page dated 2026-02-08".

## 2. Findings

**F1 (defect at the measured commit, build-caused).** The build commit's census is red: `corpus/SOURCES.md:247-248` cite `corpus/lessons/round-49.md`, which is not in 74558c71 (`git cat-file -e 74558c71:corpus/lessons/round-49.md` → rc 128) nor in the lane HEAD `122c4ee` (rc 128); it exists only untracked. `bash scripts/sources-census.sh validate --file $S/srccopy/corpus/SOURCES.md` → EXIT=1 with the two E11 lines. Controlled differential on the *same* blob and tree: copy the scribe's file to `$S/srccopy/corpus/lessons/round-49.md` and rerun → `census-validate-file-mirror-with-lesson.out`, **EXIT=0**, `ok`; the only diff is the removal of the two E11 lines. So the build's census exit status is decided by a file outside the commit — this is not a claim defect (neither C1 nor C2 reads census) but it is the lane's census gate failing at the revision the wave measures, and **no round-49 instrument runs census** (rounds 42 and 43 counters had `census=` legs — SKILL.md:1402, :1407; neither `tools/round49-replay-witness-audit.py` nor `tools/round49-append-audit-v4-check.py` mentions `sources-census`/`SOURCES.md` outside the newrow leg). Proposed fix: (a) land `corpus/lessons/round-49.md` in the same commit as the rows, or cite only paths existing at that commit; (b) give the wave a census leg as rounds 42/43 did, so `validate`'s exit status is observed at the build rather than only in the worktree.

**F2 (guard-strength, measured with fixtures).** E11 is existence-only — `sources-census.sh:567` tests `[ ! -e "$dir/$path" ]`. A zero-byte stub and a *directory* both satisfy it (`e11-guard-strength-fixtures.out`):

| fixture used-by cell | on-disk state | result |
|---|---|---|
| `corpus/lessons/round-49.md` | absent | `E11 S999 missing used-by …`, EXIT=1 |
| same | zero-byte file | `ok`, EXIT=0 |
| `corpus/lessons` | directory | `ok`, EXIT=0 |
| `corpus/knowledge/note.md` | zero-byte file | `ok`, EXIT=0 |

Consequence for integration: an empty `corpus/lessons/round-49.md` would silently turn F1 green. Today's untracked file is *not* such a stub — it is 6396 B and names both rows (`corpus/lessons/round-49.md:12`, `:21` S494, `:22` S495) with a `## Gate` section at line 17 — but nothing in the census verifies that. Proposed fix (fleet-level, `scripts/` is frozen to me): a distinct code for a used-by target that is empty/headless, or fold the check into the lesson-landing gate.

**F3 (tool mode hazard).** `--file` reinterprets the used-by root as `dirname(dirname(file))` (`scripts/sources-census.sh:497-503`) and emits no hint: a bare copy of the registry produces **441 E11s** that are all artifacts of the copy location (§1.2), with the same exit 1 a real dangling used-by produces. Documented correct form: `--file` a committed blob inside a `git archive` of the revision. Proposed fix: warn on stderr when `--file`'s derived dir lacks `corpus/`/`tools/` (or require `--root` with `--file` and validate used-by against it).

**F4 (append-only guard: green, and agrees with an independent instrument).** §1.3. Two additions, zero deletions; the tool's own 45/45 selftest passes at the build tip; `git diff --numstat`/`--unified=0` (git itself) reports the same 2/0 and a single insertion hunk — the guard and the raw diff agree, so the green result does not rest on the tool alone. `--repo` default resolution works from the fleet root.

**F5 (receipt fidelity, calibration).** The wave's before/after census receipts cannot show the build state: `diff .ufo/waves/round-49/census/start.out .ufo/waves/round-49/w1/out/S9Mistakes/census/end.out` → **identical** (both 12740 B, 96 lines), because the worktree is clean again once the scribe file lands — so the pair reports "clean → clean" across a wave whose build commit is red. Also, `start.out`'s trailing `exit=0` is not script output: `grep -c "exit=" scripts/sources-census.sh` → 0 (the script reports through its status only, `:803-806`), so the receipt's status is annotation, not evidence. Proposed fix: census receipts should record `rev-parse` of the evaluated tree and the tool's real status.

## 3. Retained evidence (in `…/w1/out/X0Census/`)

| file | what |
|---|---|
| `census-validate-74558c71.out` | real-lane `validate --root …/shokunin kama` at 23:28Z, EXIT=1, 2×E11 (pre-scribe) |
| `census-validate-worktree-2331.out` | same at 23:31Z, EXIT=0, `ok` (post-scribe) |
| `census-validate-file-74558c71.out` | bare-copy `--file`, EXIT=1, 441 phantom E11 (F3) |
| `census-validate-file-mirror-74558c71.out` | tip tree + tip blob, EXIT=1, 2×E11 (F1) |
| `census-validate-file-mirror-with-lesson.out` | same + scribe lesson, EXIT=0 (F1 differential) |
| `census-mode-74558c71.out`, `census-overdue-74558c71.out` | totals and cadence at the build |
| `sources-append-only-438127bc-to-74558c71.out` | append-only guard, EXIT=0 |
| `e11-guard-strength-fixtures.out` | four fixture cases (F2) |

Commands used: §1; plus `sha256sum` of both frozen counters = the preregistration's `counter_sha256` (C1 `86b4a40d…d6c1`, C2 `26c465a9…6945`). No lane/fleet file was modified; the lane's jj/Git state untouched; fixtures live only under `/fast/scratch/hyaku/kama-r49/X0Census` (removed); no tool installed; no server started.

## 4. Risks / blockers

- The build tip is not census-clean, and the only recovery path the guard accepts (F2) is a file whose content nothing checks. If integration lands `corpus/lessons/round-49.md` (as planned), F1 closes; if it lands empty, F1 closes vacuously.
- Nothing in round 49 re-runs census at integration either; F5's revision-blind pair is the whole record unless a census leg is added.
- Out of scope here (known integration items, not re-reported): round-49 counters absent from SKILL.md's instrument registry; SCORECARD/LOG/lesson/QUALITY/README entries pending.
