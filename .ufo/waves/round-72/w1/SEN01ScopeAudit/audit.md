# SEN01ScopeAudit — kama round 72, wave 1

Sentinel seat (adjacency). Read-only over the lane plus my own scratch.
Snapshot: **2026-11-03T22:51:09-03:00**, lane HEAD/master/origin-master `a3cc39f08f4692e990921cf938d0269f6c25fc93`,
freeze file base `090a0b25a71298ed1a58e1f81315d850f4932e74`, wave `kama-r72-w1` (13 seats, live while audited).
Lane status at snapshot: 199 porcelain records (`-uall`), all worktree/untracked, none staged.
Post-snapshot writes by still-running seats are not covered; the two audited modules were re-hashed last at
22:51:09 (`round72-round-scope.py 45321056…`, `round72-receipt-tip-binding.py a9a4e8d3…`).

## Verdicts

| # | Surface | Verdict |
|---|---|---|
| a | Secret sweep over new round-72 bytes | **PASS** — zero credential-shaped matches |
| b | Write boundary | **No seat breach found**; 1 fleet-root file outside the lane (pre-wave run15) + 3 lane paths outside any seat assignment (orchestrator-owned) |
| c | No mutating git/jj in the lane | **FAIL, literal** — one git commit landed mid-wave (driver, not a seat); freeze control now false; no seat mutation |
| d | Modules execute nothing from the graded tree; write only under `--work` | **PASS (static)**; one residual `core.fsmonitor` exec vector in C1, proven by probe |
| e | `.ufo/state/` + `.ufo/watchdog.log` untouched | **PASS** — host-owned, clean, ignore-ruled, no lane reference |

---

## (a) Secret sweep — PASS

Population (round-72 bytes only): `tools/round72-round-scope.py`, `tools/round72-receipt-tip-binding.py`,
`tools/pre-report-gate.py`, all of `.ufo/waves/round-72/`, `plans/round-72-claims.md`,
`corpus/lessons/round-72.md`, `corpus/knowledge/receipt-tip-binding.md`, `corpus/SOURCES.md`,
`corpus/README.md`, `corpus/QUALITY.md`, `SKILL.md`, `LOG.md`.

```
$ date -Is
2026-11-03T22:51:09-03:00
$ grep -RInE --binary-files=without-match \
  'AKIA[0-9A-Z]{16}|ASIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{36}|github_pat_[A-Za-z0-9_]{60,}|xox[abprs]-[A-Za-z0-9-]{10,}|sk-[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{35}|-----BEGIN [A-Z ]*PRIVATE KEY-----|eyJhbGciOi[A-Za-z0-9_-]{10,}|Authorization:[[:space:]]*[A-Za-z]|Bearer [A-Za-z0-9._-]{12,}|[a-z]+://[^/@[:space:]]+:[^/@[:space:]]+@' \
  tools/round72-round-scope.py tools/round72-receipt-tip-binding.py tools/pre-report-gate.py \
  .ufo/waves/round-72 plans/round-72-claims.md corpus/lessons/round-72.md \
  corpus/knowledge/receipt-tip-binding.md corpus/SOURCES.md corpus/README.md corpus/QUALITY.md SKILL.md LOG.md
SWEEP_EXIT=1          # 1 = no match
$ find .ufo/waves/round-72 tools corpus/lessons corpus/knowledge -maxdepth 3 \
  \( -iname '*.pem' -o -iname '*.key' -o -iname 'id_rsa*' -o -iname '.env*' -o -iname '*secret*' -o -iname '*credential*' \)
(none)
```

Out-of-population notes (not round-72 findings): `corpus/knowledge/listener-census.md:225` contains the word
`token:` only inside a `sed` redaction example; `tools/test-snapshot.sh:80` contains the literal
`api_key=fixture-secret` in a pre-existing test fixture. Neither is credential-shaped and neither is
round-72 bytes.

## (b) Write boundary — no seat breach; named non-seat writes

```
$ git -C /home/vgpnk/Projects/shokunin status --porcelain
 M .scratch/goal-20261103-hyaku-run15.md
 M .scratch/run15-state.json
?? .scratch/run13-state.json
?? .scratch/run15-kernel.py
?? after

$ git -C /home/vgpnk/Projects/shokunin/kama-shokunin status --porcelain -uall | wc -l
199
```

Fleet root (`/home/vgpnk/Projects/shokunin`), outside the lane:
- `after` — 24 B, mtime **20:05** (3 h before the 22:34:21 kama launch), content `== SCORECARD diff base-`;
  a run15 redirect artefact, not a kama seat write, but it is a file outside the lane.
- `.scratch/run15-state.json` (M, 22:41), `.scratch/run15-kernel.py`, `.scratch/run13-state.json`,
  `.scratch/goal-20261103-hyaku-run15.md` — run15/hyaku orchestrator state, pre-existing, not seats.
- `MANIFEST.json` mtime advanced to 22:37 but `git status` is clean for it: no content write.

Lane paths outside every seat write scope (no seat item names them; content/timing identify the
orchestrator; authorship is inferred, not process-accounted):
- `plans/round-72-claims.md` — modified **twice** after the freeze commit (see adjacency 1–2).
- `.ufo/waves/round-72/measured/before/populations.out` (22:41:41, header `# base a3cc39f0…`).
- `.ufo/waves/round-72/measured/report-draft.md` (22:44, L1 report draft).
- Dispatch machinery, also outside seat scope: `.ufo/waves/round-72/w1-spec.json`,
  `w1/w1-dispatch.json`, `w1/swarm-registry.json`, `w1/validate.err`, `w1.ready`, `w1.ready.dispatched`.

Every other path in the 199-record snapshot maps to a seat assignment:
`tools/round72-round-scope.py` (EX01), `tools/round72-receipt-tip-binding.py` (EX02),
`tools/pre-report-gate.py` (EX03), `corpus/SOURCES.md` (SCR01), `corpus/knowledge/receipt-tip-binding.md`
+ `corpus/README.md` + `corpus/QUALITY.md` (SCR02), `SKILL.md` + `LOG.md` + `corpus/lessons/round-72.md`
(SCR03), and `w1/<Seat>/…` plus, where the harness had already written them, the `w1/<Seat>.md`
Report-trailer files for the seats (SCT01, CON01, LAB01, RVW01, CRT01, MT01, SEN01). No seat wrote another seat's directory and no seat
edited `plans/` or `measured/`.

## (c) Mutating git/jj — literal FAIL, no seat mutation

```
$ git -C <lane> rev-parse HEAD; git -C <lane> rev-parse master
a3cc39f08f4692e990921cf938d0269f6c25fc93
a3cc39f08f4692e990921cf938d0269f6c25fc93
$ git -C <lane> log --oneline -3
a3cc39f0 round-72: amend C1 case-A anchor to the lane-owned freeze plan (pre-score) and dispatch wave 1
090a0b25 round-72: freeze two claims (C1 calibration round-scope, C2 operability receipt-tip binding) with controls
d30a8696 round-71 verifier spot-check (integrator, hyaku): non-author admit/reject
$ git -C <lane> show -s --format='%H%n%cI%n%an <%ae>%n%s' a3cc39f0
a3cc39f08f4692e990921cf938d0269f6c25fc93
2026-11-03T22:41:23-03:00
kama-shokunin <kama@shokunin.local>
round-72: amend C1 case-A anchor to the lane-owned freeze plan (pre-score) and dispatch wave 1
$ git status --porcelain -uall | grep -E '^[MADRC][MADRC]? '
NONE_STAGED
$ jj --ignore-working-copy log -r '::@' --limit 2
@  xwnuootw kama@shokunin.local 2026-11-03 22:41:23 89a8beeb
│  (empty) (no description set)
◆  vunwomvw kama@shokunin.local 2026-11-03 22:41:23 master a3cc39f0
```

- One commit (`a3cc39f0`) landed in the lane **mid-wave** (wave spawn 22:34:21 / dispatch 22:40:51; commit
  22:41:23) under the driver identity `kama-shokunin <kama@shokunin.local>`. It is the freeze amendment 1 +
  dispatch commit, not a seat write.
- `master`/`HEAD`/`origin/master` are all `a3cc39f0`; the frozen claims' own **Freeze control** —
  `git -C <lane> rev-parse master` == `freeze.txt` `base=` line (`090a0b25`) — is therefore **false**
  (`090a0b25 != a3cc39f0`).
- The index is untouched: every record is ` M`/`??`, none staged, so no seat ran `git add`.
- jj: `@` is an empty working-copy bookkeeping commit at 22:41:23, parent `a3cc39f0`; no jj
  commit/describe/new/squash evidence. A jj read ran without `--ignore-working-copy` at 22:41:23 and
  snapshotted an empty working copy.
- Wave reports contain no lane-mutation claim. Fixture commits named in reports are scratch-scoped:
  `LAB01Probes.md` `D4=$F/h4` with `git -C "$D4" add`; EX01/EX02 selftests `git init`/`add`/`commit`
  inside `--work` fixtures after a `rev-parse --show-toplevel` assertion, with `-c user.name=fixture
  -c user.email=fixture@invalid`.

## (d) Modules vs the graded tree — PASS (static) + one residual vector

Static primitives (final bytes; hashes above):
```
$ grep -nE 'subprocess|os\.system|os\.popen|eval\(|exec\(|compile\(|__import__|importlib|shell\s*=|socket|urllib|requests|http' \
    tools/round72-round-scope.py tools/round72-receipt-tip-binding.py
round72-round-scope.py:72: import subprocess
round72-round-scope.py:99: def _git(...): subprocess.run(argv, ...)   # argv list, no shell=
round72-receipt-tip-binding.py:99: import subprocess
round72-receipt-tip-binding.py:134: subprocess.run(["git", "-C", repo, *args], ...)
```
No `os.system`, no `eval(`/`exec(`/`compile(`, no `shell=True`, no network module.

Git verbs — scored/audit paths are read-only; mutations exist only inside fixtures:
- C1: `rev-parse`, `cat-file`, `status` (scored path); `init`, `add`, `commit`, `mv` only on
  `--work` fixture roots, after `toplevel == root` assertion.
- C2: `rev-parse`, `cat-file`, `ls-tree`, `merge-base`, `rev-list`, `diff-tree` (audit path);
  `init`, `add`, `commit` only on `_Fixture(scratch, …)` roots, `toplevel == path` asserted.

Writes only under `--work`:
- C1 fixtures write `work/<case>/…`; `--work` must be absent/empty for `--selftest`; on success
  `shutil.rmtree(work)` removes the work dir itself; on failure it prints `…_WORK_KEPT` and keeps it.
- C2 writes `--work/selftest-<pid>/…` (or a `mkdtemp`), deletes only that scratch subdir; the
  caller-supplied `--work` root is not removed.

Residual exec vector (C1 only), proven in scratch (`S=/fast/scratch/hyaku/kama-r72/SEN01ScopeAudit`):
```
$ git -C "$D" config core.fsmonitor "$S/probe/fsmon2.sh"   # fixture repo, fsmon script touches MARKER2
$ python3 tools/round72-round-scope.py --repo "$D" --round 72 --tip HEAD
ROUND_SCOPE round=72 cases=3 findings=0
module_exit=0
marker=PRESENT
```
`git status` (the scored path) executes a command named by the graded repo's `core.fsmonitor`. The
module never execs tree *bytes*, and the claim's grep-level test passes, but "executes nothing derived
from the tree it grades" is not absolute. Smallest remediation: add `-c core.fsmonitor=false` to
`_git` argv in `round72-round-scope.py`. C2 has no equivalent path (none of its verbs run hooks).

## (e) `.ufo/state/` and `.ufo/watchdog.log` — PASS

The lane has no `.ufo/state/` and no `.ufo/watchdog.log` (`ls` returns ENOENT). The host copies live at
the fleet root:
```
$ git -C /home/vgpnk/Projects/shokunin status --porcelain -uall -- .ufo/state .ufo/watchdog.log
(empty)
$ git -C /home/vgpnk/Projects/shokunin ls-files .ufo/state
.ufo/state/.gitkeep                     # only tracked path; 25 MB of live state is ignored
$ git -C /home/vgpnk/Projects/shokunin check-ignore -v .ufo/state/kama.report-baseline .ufo/watchdog.log
.gitignore:8:.ufo/state/*   .ufo/state/kama.report-baseline
.gitignore:10:.ufo/watchdog.log   .ufo/watchdog.log
$ cat .ufo/state/kama.report-baseline
72 e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
$ tail -1 .ufo/watchdog.log
2026-11-03T22:41:22-03:00 complete kengaku round=71; hyaku-inline attempt=1
```
Live-file mtimes line up with host events, not lane activity: `kama.report-baseline` 22:34:19 vs watchdog
`launch kama round=72` 22:34:21; `inline-dispatcher.log` 22:41:24 vs `spawned kama 72 w1 13` 22:40:51;
`watchdog.log` 22:41:22 vs the kengaku completion line. No file in `tools/` or the wave dir names
`.ufo/state` or `watchdog.log` (grep hits only the embedded seat-prompt text in `w1-spec.json`).

---

## Adjacency findings (reported, freeze untouched)

1. **Freeze control is false at the audited tip.** `freeze.txt` `base=090a0b25…`; `rev-parse master`
   = `a3cc39f0…`. The amendment commit necessarily moved master off the frozen base, so the plan's
   stated control can no longer pass as written.
2. **The frozen plan changed twice while seats were running, and its amendment timestamps are wrong.**
   `plans/round-72-claims.md` mtime 22:40 (amendment 1 note says `22:45 -03`; committed 22:41:23) and
   mtime **22:42:21** (amendment 2 note says `22:50 -03`; **still uncommitted** at snapshot). The wave
   spawned 22:40:51. Hash pins: `HEAD:plans/round-72-claims.md` = freeze pin `39f4ddb…`; the working-tree
   amendment-2 plan = `c656e66b…` — unpinned by `freeze.txt`. Amendment 2 changes C2's exit map
   (`cited=0` → exit 2) after EX02 was dispatched.
3. **The draft lesson fails its own C2 counter.** `corpus/lessons/round-72.md` (22:48) cites, in backticks:
   two `.html` source captures, `freeze.txt`, `round-scope-control-old.out`, and shorthand `fetch.out` /
   `quote.txt` / `w1/SCR03RegistryLog/selftests.out`. Reproduced on a scratch fixture carrying the real
   lane files:
   ```
   RECEIPT_TIP_BINDING_UNREADABLE cited path is not a receipt file (.html):
     .ufo/waves/round-72/w1/SCR01SourceRow/source/git-check-ignore.html (corpus/lessons/round-72.md:24)
   exitA=2
   # after removing only the .html backtick tokens:
   RECEIPT_TIP_FINDING unbound .ufo/waves/round-72/controls/freeze.txt :: no tip=/rev= header among the first 5 lines
   RECEIPT_TIP_FINDING stale  .ufo/waves/round-72/fetch.out :: absent at <tip>
   RECEIPT_TIP_FINDING unbound .ufo/waves/round-72/measured/before/round-scope-control-old.out :: no tip=/rev= header among the first 5 lines
   RECEIPT_TIP_FINDING stale  .ufo/waves/round-72/quote.txt :: absent at <tip>
   RECEIPT_TIP_FINDING unbound .ufo/waves/round-72/w1/SCR03RegistryLog/selftests.out :: no tip=/rev= header among the first 5 lines
   RECEIPT_TIP_BINDING round=72 cited=5 bound=0 unbound=3 shifted=0 stale=2
   exitC=1
   ```
   If landed as-is (and once `SCORECARD.md` gains a `## Round 72` section), C2 exits 2; without the
   `.html` tokens it exits 1. The shorthand `fetch.out`/`quote.txt` resolve against the wave root by the
   tool's declared section-relative rule, but the files live under `w1/SCR01SourceRow/`.
4. **Base-headered receipts are `shifted` at the amended tip.** `git diff --name-only d30a8696 a3cc39f0`
   includes `plans/round-72-claims.md`, a C2 instrument input (default record paths exclude `plans/`).
   Therefore every receipt headered `tip=d30a8696…` — EX01's `real-base-*`, all EX02 receipts — is
   `shifted` when cited at `a3cc39f0`. Only EX01's `real-amend-a3cc39f0.out`,
   `predicate-committed.out`, `real-worktree-master*.out`, `selftest.out` carry the current tip. EX03,
   SCR01, SCT01 and the measured receipts have **no** `tip=`/`rev=` header in their first five lines
   (scan of every `.out`/`.md` under the wave dir): they are `unbound` if cited.
5. **Gate docstring is not the frozen sentence, and the arm ordinal is ambiguous.** The plan says the
   same sentence is the module `PREDICATE`, the gate's arm-6 docstring and the receipt label.
   `PREDICATE` is byte-equal to the plan blockquote (472 chars, verified by AST + plan extraction), but
   `GATE_HAS_FULL_C1_SENTENCE False` — `tools/pre-report-gate.py` paraphrases it and contains only the
   fragment `ROUND_SCOPE round=<N> cases=3 findings=<f>`. The gate also executes `round-scope` fifth
   (`ARM_ORDER = ARM_SPECS + ["round-clean"]`) while the plan calls it "arm 6"; the verdict `arms=6` is
   correct.
6. **`EX03GateArm6/live-scored.out` is not a live six-arm run.** It records
   `ls: cannot access 'tools/round72-round-scope.py'` and `round-scope exit=2` because it was taken before
   EX01 landed; its red verdict is environmental, not a grading result. Do not cite it as the C1 live
   evaluation.
7. Minor: `EX01RoundScope/kill-prompt.out` retains the pre-amendment case name, while its content is
   `ROUND_SCOPE_FINDING label …status=absent` — the receipt body is correct, the filename is stale.

## Files written

- `.ufo/waves/round-72/w1/SEN01ScopeAudit/audit.md` (this file)
- `.ufo/waves/round-72/w1/SEN01ScopeAudit.md` (Report-trailer copy, same bytes)

Scratch `/fast/scratch/hyaku/kama-r72/SEN01ScopeAudit/` held the fsmonitor probe and the C2 citation
fixture; it is deleted before yielding. No lane file was edited by this seat. No tools installed.
