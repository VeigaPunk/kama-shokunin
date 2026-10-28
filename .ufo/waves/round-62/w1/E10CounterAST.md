# E10CounterAST — hostile-env audit of the two round-62 counters' git usage

Seat: E10CounterAST (UFO-FSD fleet executor, advisory leaf).
Round 62 / kama / wave w1. Axes: operability + calibration.
Lane: `/home/vgpnk/Projects/shokunin/kama-shokunin` @ tip `65d7cad0fce90e34de37527cde22e97b63b118bf`
(freeze base `a959fd9022b1ac1f3cb4dc2475d9cded8b2b01c3`).
No verdict on C1/C2 is offered here; this is an instrument-invariance measurement.

Instruments audited (bytes, not intentions):

| instrument | source | sha256 |
|---|---|---|
| C1 counter, frozen tip blob | `git show <tip>:tools/round62-c1-counter.py` | `275610b51eb1be219cdaa3c3e15e3568b590f35e7a1b3ceb42ab0374243f4d8d` |
| C1 counter, lane worktree copy | `tools/round62-c1-counter.py` (uncommitted delta, not mine) | `a3498308938ed4715cfdf1ce5c9a2e4ddf9cb5f9befbba29857980721fe8c415` |
| C2 counter, frozen tip blob (== worktree) | `git show <tip>:tools/round62-c2-counter.py` | `15d11f1ce8f8cb85e002d83c50b40d2bd7e4dfa561d8dd2d453e2daa09c05929` |

Hostile target: decoy repo built in scratch (`git init`, head `6ac9b7c2395e8b4bf31f51200a2a77fdb21fea09`) whose paths collide with the
lane's but whose contents differ — `SCORECARD.md` has no canonical-capabilities section, `registry/capability-claims-r62.tsv`
is header-only, `tools/kama-completion-live.py` is absent. Any unscrubbed `git` call therefore produces a *visible* flip, not a
silent re-read of the same data.

Hostile env vector (the three named vars; `GIT_WORK_DIR` is not a git variable — I set both it and the real `GIT_WORK_TREE`):
`GIT_DIR=<decoy>/.git`, `GIT_WORK_TREE=<decoy>`, `GIT_WORK_DIR=<decoy>`, `GIT_INDEX_FILE=<scratch>/decoy-index`.

Arms: `clean` = ambient env with every `GIT_*` var removed, `TMPDIR` unset; `hostile` = same env + the four vars above. Every
arm got a fresh `--work` dir (the counters cache/reuse, see §6). Harness: `out/E10CounterAST/run_arm.py`, `out/E10CounterAST/audit_c2.py`.

---

## 1. Assigned question, answered per clause

**(a) “every `git()` call strips `GIT_*`” — TRUE for both counters' own calls.** One `git()` definition per counter, one
stripping expression, no bypass: C1 `tools/round62-c1-counter.py:45-48`, C2 `tools/round62-c2-counter.py:123-126`
(`env = {k: v for … if not k.startswith('GIT_')}`, passed as `env=` to `subprocess.run`). C2's second git touch,
`checkout_tip` (`:356-361`), uses the same stripped env for the `git archive` pipeline. Grep-verified: no other `git`
invocation exists in either counter.

**(b) `blob()` reads at `--tip` — TRUE.** C1 has exactly three call sites, all `blob(args.repo, args.tip, …)`: `:343`
(`tools/kama-completion-live.py`), `:355` (`tools/kama-llamacpp-live.py`), `:362` (`registry/endpoint-consumers.tsv`).
C2 has two, both `blob(repo, args.tip, …)`: `SCORECARD.md` and `REG`. No call site falls back to `HEAD`, `master`, or the
worktree.

**(c) “tip trees come from `git archive | tar`” — TRUE for C2 only, and correctly.** `checkout_tip` (`:352-366`) runs
`git -C repo archive <tip>` → `tar -x -C <work>/tip` under the stripped env, and returns the tree only when both exit 0.
C1 builds no tip tree at all — it materialises exactly the three blobs above into `<work>/tip`, which is consistent with its
predicate (it grades a single live lifecycle, not a tree).

**(d) “confirm identical output vs clean env” — TRUE for C1, FALSE for C2.** This is the finding. C1 is byte-identical;
C2's printed line and per-row facts move, because C2 does not scrub the env it hands to the *bound runs*, only the env it
uses for its own git reads.

Counter lines, verbatim:

```
C1 (worktree copy) clean run 1 : tool_present=1 live_ok=1/1 fake_rejected=2/2 stale_rejected=1/1 tamper_rejected=8/8 log_rejected=1/1 predead_rejected=1/1 sigterm_rejected=1/1 hold_rejected=1/1 outside_rejected=1/1 errors=0 met=True   rc=0
C1 (worktree copy) clean run 2 : (identical line) rc=0
C1 (worktree copy) hostile     : (identical line) rc=0
C1 (frozen tip bytes) clean    : rc=1, no line — AttributeError, see §4
C1 (frozen tip bytes) hostile  : rc=1, byte-identical stderr to clean

C2 clean   : population=12 rows=12 covered=12/12 bound=12 eval_lines=12 sensitive=12/12 dead=0 mismatches=4 canonical=62 controls_rejected=8/8 errors=0 met=False   rc=1  (906 s)
C2 hostile : population=12 rows=12 covered=12/12 bound=12 eval_lines=12 sensitive=12/12 dead=0 mismatches=9 canonical=62 controls_rejected=8/8 errors=0 met=False   rc=1
```

`canonical=62`, coverage, binding, sensitivity, dead, controls and errors are identical across C2 arms; only `mismatches`
moves, 4 → 9. Two independent clean C2 runs (CLI and instrumented) both produced `mismatches=4` with identical text, so the
delta is environmental, not run-to-run noise.

## 2. Mechanism — C2's children are unscrubbed

`run_bound` (`:257-262`) executes `bash -c <row run>` with `env=env`, and that `env` is built in `main` (`:379-382`) as
`dict(os.environ)` + `TMPDIR=<work>/run`, `PYTHONPATH` popped. No `GIT_*` strip. Every bound template therefore inherits the
parent's hostile git context, and several bound tools call `git` with no stripping of their own:

| bound tool | unscrubbed git call sites |
|---|---|
| `tools/digest-ledger.py` | `:190`, `:198` (`cat-file --batch`), `:240` |
| `tools/hexrun-census.py` | `:111`, `:149` (`cat-file --batch`) |
| `tools/append-only-audit.py` | `:192`, `:204`, `:288` |
| `tools/sources-append-only.py` | `:352` |
| `tools/pin-watch.py` | `:123` (`ls-remote`, `env={**os.environ, …}`) |

Direct measurement through the exact child env `run_bound` passes (`out/E10CounterAST/c2-child-env-leak.json`):

```
clean   digest-ledger  rc=0  pattern present  … ledger_bad=0 wrong_unflagged=0 unknown=0
hostile digest-ledger  rc=2  pattern ABSENT    digest-ledger: git rev-parse --verify 65d7cad…^{commit}: fatal: Needed a single revision
clean   hexrun-census  rc=0  pattern present  … wrong_flagged=3 ledger_bad=0 unknown=0
hostile hexrun-census  rc=2  pattern ABSENT    error: git rev-parse --verify 65d7cad…^{commit}: fatal: Needed a single revision
```

Per-row divergence, both arms (`out/E10CounterAST/c2-per-row-arms.tsv`, full table in the two `c2-rows-*.json`):

| capability | clean live | hostile live | cause |
|---|---|---|---|
| `digest-ledger` | True | **False** | child git reads the decoy → tip rev absent |
| `hexrun-census` | True | **False** | same |
| `append-only-audit` | True | **False** | hostile observed output truncated to `AOA_SELFTEST pass=` (selftest fixture git redirected) |
| `context-capacity-receipt` | False | False | `TIMEOUT` in both arms — burned the full 900 s bound timeout (host never idle while peer seats ran live tools); env-independent |
| `live-ollama-lifecycle` | False | False | evidence JSON with `argv_child: null` in both arms; env-independent |
| other 7 | True | True | unaffected |

So the hostile vector does not merely change the aggregate: it flips three rows that are green in a clean env, and each flip
is exactly a row whose bound tool spawns `git` itself.

## 3. Instrument defect found at the tip (independent of env)

The frozen C1 tip bytes **crash before printing**, in both arms, identically:

```
File ".../c1-tip.py", line 440, in main      s = score(ctl, witness)
File ".../c1-tip.py", line 191, in score     recomputed, inconsistent = grade(receipt)
File ".../c1-tip.py", line 130, in grade     u = cj.get('usage') or {}
AttributeError: 'NoneType' object has no attribute 'get'
```

Trigger: the `tamper` control family re-writes `captures.completion.body` without re-hashing it, so `cap()` returns `None`,
`cj` is `None`, and `grade()` dereferences it unconditionally at `:130` (`completion_fingerprint` and
`completion_model_id` short-circuit; `usage`/`timings` do not). This fires on every run whose live leg succeeds — i.e. the
frozen tip instrument cannot reach `met=True` at all; it exits 1 with a traceback instead of a counter line.

The lane worktree copy (`a3498308…`) carries an uncommitted 3-hunk fix that is exactly this defect
(`cj.get` → `(cj or {}).get` ×2, and the `hold` check keyed on `hold_released`), and that copy does report
`… errors=0 met=True` identically in 3 runs. Nothing was edited by this seat; recording it so the L1 knows the C1
`met=True` measurement cannot have been produced by the tip bytes, and so the fix must land before the instrument is judged.

## 4. Residual env vector outside the three named vars (calibration risk)

The `GIT_*` prefix strip is necessary but not sufficient for the archive path: `git archive` also honours `HOME` /
`XDG_CONFIG_HOME` git config. A hostile `HOME` carrying

```
[core]
	attributesFile = <home>/attrs
```
with `*.md export-ignore` + `tools/*.py export-ignore`

changes the archive for the *same* tree and the *same* tip, with no `GIT_*` var in play. Measured through C2's own
`checkout_tip()` (`out/E10CounterAST/c2-checkout-tip-envs.json`):

| arm | files | `tools/*.py` | `SCORECARD.md` | canonical section | `tree_returned` |
|---|---|---|---|---|---|
| clean | 33772 | 88 | present | round 62, 12 rows | True |
| hostile `GIT_*` (three named vars) | 33772 | 88 | present | round 62, 12 rows | True |
| hostile `HOME` (attrs export-ignore) | 28659 | 0 | absent | none | True |

Two notes for the L1, both structural and cheap to close:
1. `checkout_tip` returns a *truncated* tree with rc 0 — the truncation is silent; the counter would report `dead=12` /
   `mismatches` rather than an environment error, mislabelling an env fault as a calibration fault. Hashing the extracted
   tree (or refusing a tree whose `tools/` lacks every bound target) would make the failure legible.
2. `git show` (C1's blob path) is immune to attributes — the residual is specific to the archive path in C2.

Also structural: `checkout_tip` returns an existing `<work>/tip` unchanged (`:353`) and `_EXEC_CACHE` is keyed only on
`(tip, cap)`. Re-using a `--work` dir across envs would mask exactly the archive sensitivity measured above; all arms here
used fresh work dirs.

## 5. What the C1 live chain touches

`witness_run` (`:229-235`) starts the tip-pinned tool with the parent env inherited (no `env=`), so `GIT_*` does reach it —
but that chain is git-free: `tools/kama-completion-live.py` contains no `git` invocation, and the `llama-server` child it
spawns gets an explicit whitelist env (`PATH`, `HOME`, `LANG`, `LC_ALL`, `LD_LIBRARY_PATH`, `LLAMA_ARG_THREADS`,
`XDG_CACHE_HOME`, `kama-completion-live.py:231-233`), so the vectors cannot propagate further. That is why C1 is invariant
while C2 is not.

## 6. Operability cost observed

A clean C2 run costs **906 s**, because the `context-capacity-receipt` bound run consumes its full 900 s timeout whenever the
host is not idle — which is the normal state while peer seats run live tools on the same box. Both C2 arms paid it. Any
concurrent round-62 work that expects a green `context-capacity-receipt` row will not get one; that row's timeouts are a
scheduling property, not evidence about the lane.

## 7. Receipts (all under `.ufo/waves/round-62/w1/out/E10CounterAST/`)

| file | contents |
|---|---|
| `c1-clean.json`, `c1-hostile.json` | frozen C1 tip bytes, clean/hostile: rc 1 both, stdout empty, stderr byte-identical |
| `c1wt-clean-1.json`, `c1wt-clean-2.json`, `c1wt-hostile-1.json` | C1 worktree copy: 3 runs, identical line, rc 0, `met=True` |
| `c2-clean-1.json` | C2 CLI, clean arm, 906 s |
| `c2-rows-c2x-clean.json`, `c2-rows-c2x-hostile.json` | C2 instrumented arms: printed line + per-cap live verdict/sens/dead/observed + registry rows + facts |
| `c2-per-row-arms.tsv` | 12-row clean-vs-hostile diff |
| `c2-child-env-leak.json` | bound scans run under the exact `run_bound` child env, both arms |
| `c2-checkout-tip-envs.json` | `checkout_tip()` under clean / hostile `GIT_*` / hostile `HOME` |
| `run_arm.py`, `audit_c2.py`, `probe_child_env.py`, `probe_checkout_tip.py` | the harnesses, re-runnable as committed |

Reproduction (scratch root `S`; decoy `D=$S/decoy` built with the three colliding paths and
`git init` / `add -A` / `-c user.name=decoy -c user.email=decoy@invalid commit` inside it, as described in the header):

```
git -C $LANE show <tip>:tools/round62-c1-counter.py > $S/bin/c1-tip.py
git -C $LANE show <tip>:tools/round62-c2-counter.py > $S/bin/c2-tip.py
python3 run_arm.py <tip> c1  hostile            # frozen C1 bytes, hostile
python3 run_arm.py <tip> c1wt hostile           # worktree copy, hostile (c1wt-tip.py = worktree copy)
python3 run_arm.py <tip> c2  clean
python3 audit_c2.py hostile c2x-hostile
python3 probe_child_env.py <tip> $D
python3 probe_checkout_tip.py <tip> '{"GIT_DIR":"…","GIT_WORK_TREE":"…","GIT_WORK_DIR":"…","GIT_INDEX_FILE":"…"}'
```

Bounds honoured: read-only git only (`show`, `archive`, `rev-parse`, `ls-tree`, `cat-file`); the sole write fixture is the
decoy repo in scratch; lane source untouched (the C1 worktree delta pre-existed this seat); no commits, no push, no
pacman/uv/npx installs (nothing needed — zero tools installed, so nothing to record); scratch
`/fast/scratch/hyaku/kama-r62/w/E10CounterAST/` deleted after the receipts above were copied.

TALLY: C1 own-git-strip PASS · C1 blob@tip PASS · C1 tip-tree n/a · C1 hostile-vs-clean output identical 3/3 (worktree copy) and 2/2 (tip bytes, crash) · C2 own-git-strip PASS · C2 blob@tip PASS · C2 archive@tip PASS · C2 hostile-vs-clean output DIFFERS (mismatches 4→9, 3 rows flipped) · C2 child-env unscrubbed · C1 tip bytes crash on own tamper control · residual HOME-attrs vector measured (33772→28659 files, 88→0 tools, silent).
