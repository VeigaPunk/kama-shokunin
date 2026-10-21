# RowC02RealOmission — C02-real-omission (control)

VERDICT: **holds**. The fault premise is real and observed in the frozen arm, and the
expected outcome (exit 1, exactly `landed-omitted`) is the correct one on the documented
criterion, not merely what current happens to do. Independently re-checked at
`245a37f69628c2c6bb29bbf17897d8fb5946c857` with a hand-built fixture (no grid import).
Five residuals are named in §3: one false clean in the same channel (bare `round-N`
subject), one false defect in the same channel (citation only in the section heading), and
three axis/adjacent items (empty `info/grafts`, defeated promisor refusal, local-config
include hang).

## 0. Base and method

```
git clone --no-hardlinks /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/kama-r23w2/RowC02RealOmission
git -C /tmp/kama-r23w2/RowC02RealOmission rev-parse HEAD
  -> 245a37f69628c2c6bb29bbf17897d8fb5946c857
sha256sum tools/report-landing-audit.py
  -> f228f17420134a4a4fb6d1f93b943f78647e7e60882f767e6cb7cba11d6928a7  (committed/current arm)
git cat-file blob 4fe9339f8fc3a4a4a479d9c938a850da12f1124d:tools/report-landing-audit.py | sha256sum
  -> 09ecd63bdc3a5be5264e6d2966602a32e52ca0678dc89de99959318245ab3b3f  (frozen arm)
```

All behavior below ran the clone's HEAD blobs, not the lane checkout. **The lane checkout was
dirty and changing during this seat**: `git status --porcelain` in the lane listed `M
tools/report-landing-audit.py`, `M tests/report-audit/repo-state-grid.py`,
`M tests/report-audit/isolation-mutants.py` and four others (mtimes 12:55-12:58; worktree
auditor `3fc567ab...`, worktree grid `6303c6ec...` vs HEAD `f228f174...`/`72c1e53...`).
Line citations here are HEAD lines; the worktree grid put the same C02 row at line 609
instead of HEAD's 529. Re-running the grid from the lane worktree now exercises different
code than the pinned revision.

## 1. Is the premise real and observed in the frozen arm? YES

Hand-built fixture (plain git, `GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1`, explicit
identity), matching HEAD `tests/report-audit/repo-state-grid.py:112-118` (`base`) plus
`:133-136` (`c_omission`): lane commit 1 `round-1: work` @1000, lane commit 2
`round-1: more` @1500, fleet report adds `## Landed changes` with only commit 1 at @2000.

```
git -C lane log --format='%H %an %at %s'
  29e8ea69cc44bbb72af22255c5231a7d13b577e0 kama-shokunin 1500 round-1: more
  db796f8b820bf3825c58832419138cdba23206a7 kama-shokunin 1000 round-1: work
fleet report commit ebcb436228cc3c28fd415f5afcce3312e1151be4, author time 2000
```

Both arms, same command (`--lane-repo lane --fleet-repo fleet --rounds 1 --no-errata --json`):

| arm | exit | defects | required | cutoff | post_report | traceback |
|---|---|---|---|---|---|---|
| frozen (09ecd63b) | 1 | `landed-omitted 29e8ea69cc44bbb72af22255c5231a7d13b577e0` | 2 | 2000 | [] | no |
| current (f228f174) | 1 | `landed-omitted 29e8ea69cc44bbb72af22255c5231a7d13b577e0` | 2 | 2000 | [] | no |

The grid's own row, both arms (`repo-state-grid.py --arm both --case C02-real-omission
--json`, population `83a84702...`): frozen `exit=1 kinds=['landed-omitted'] met=true`;
current identical, `traceback=false executed=false timed_out=false`. So the frozen arm does
observe the real omission; the control is not passing vacuously.

## 2. Is the expected outcome the correct one? YES (not merely what current does)

The criterion is written independently in two places and the fixture satisfies every clause:

- HEAD `corpus/QUALITY.md:151` (KQ28): "A round report's `## Landed changes` names every
  lane commit of the round (subject `round-N:`/`checkpoint(rN)`, authored before the
  report's first fleet commit) by hash" (24-word quote).
- HEAD `tools/report-landing-audit.py:21-25`: "not cited in `## Landed changes` by a
  >=7-hex prefix"; the kind is defined as an author-time cutoff at the fleet commit that
  "first added the report".

The omitted commit `29e8ea6...` is authored `kama-shokunin`, subject starts `round-1:`,
author time 1500 <= cutoff 2000, is an ancestor of the audited branch tip, and the full
40-hex token appears nowhere in the report. Exit 1 with exactly `landed-omitted` (and
nothing else: the cited full hash resolves, no section defect) is therefore the documented
verdict, and the grid's exact-kind expectation (`:529`) is right.

Edge controls run on the same fixture support that reading rather than merely recording
current behavior:

| variant | current | frozen | judgment |
|---|---|---|---|
| omitted subject `checkpoint(r1) save` | exit 1 `landed-omitted` | exit 1 | correct (second allowed form) |
| omitted commit author time == cutoff 2000 | exit 1 `landed-omitted` | exit 1 | correct (`no later than`) |
| second commit author `someone` | exit 0, required 1 | exit 0 | correct (author predicate) |
| second commit author `fixture`, committer `kama-shokunin` | exit 0, required 1 | exit 0 | correct (author-time rule; rebases rewrite committer) |

## 3. Near variants current still gets wrong

### 3a. Same channel, false clean: subject `round-1` (no colon) — **not in the declared open list**

HEAD `tools/report-landing-audit.py:190` matches `^(?:round-{rnd}:|checkpoint\(r{rnd}\))`.
A lane commit by `kama-shokunin` with subject exactly `round-1` and no colon is never
required. Hand fixture identical to §1 except the omitted commit's subject is `round-1`:

```
current exit 0 kinds [] required 1
frozen  exit 0 kinds [] required 1
(omitted commit dda1c9230d5f..., author kama-shokunin @1500, uncited)
```

This is a real shape in this lane, not hypothetical: `git log --all` at HEAD contains
`83bee7faf5a733ac7a7bc47cde29cba23c6cefb7 kama-shokunin 1790656456 round-2`, reachable from
`master`. Round-21 advice already recorded the class: "has subject exactly `round-2` ...
required=0 (true count 1" (`.ufo/waves/round-21/build/advice/AuditEarlyRounds.md:34`,
"Silent false negative"). HEAD `corpus/lessons/round-23.md:85-92` does not list it among
open/tradeoff items. Caveat: KQ28's literal wording requires the colon, so this is as much
a contract-versus-intent gap as a code gap; the report text and the rule should be decided
one way.

### 3b. Same channel, false defect: citation only in the `## Landed changes` heading

Report cites commit 1 in the body and commit 2 in the section heading
(`## Landed changes (round-1: more <sha2>)`):

```
current exit 1 landed-omitted 29e8ea69... cited_elsewhere=true
frozen  exit 1 landed-omitted 29e8ea69... cited_elsewhere=true
```

`landed_match` (HEAD `:168-170`) captures only `group(1)` (the body), so a heading token
neither counts as a citation nor is checked as `landed-unresolved`. The auditor's own
`cited_elsewhere=true` shows it sees the token and still fails the report. This is the same
artifact round-21 recorded for the r6-9 heading form
(`.ufo/waves/round-21/build/advice/AuditEarlyRounds.md:33`: "the heading hash is never seen;
JSON shows `cited_elsewhere=true`", judged a false positive under the heading-inclusive
reading). It is latent for the current bare-heading template, but it is a compliant report
flipped to exit 1. If headings are deliberately excluded, KQ28 should say "body of".

### 3c. Same fixture + harmless repo state: empty `.git/info/grafts` becomes a refusal

```
C02 fixture + : > lane/.git/info/grafts
current exit 2  could-not-evaluate: .../lane/.git/info/grafts rewrites history
frozen  exit 1  landed-omitted 29e8ea69...
git -C lane log --oneline   -> rc 0
```

HEAD `:440` uses `os.path.lexists`, so any file — including an empty one git ignores —
turns a correct C02 verdict into exit 2. Fail-closed, but the message ("rewrites history")
is false and the grid's F11 premise ("graft effective") is not met by an empty file. The
mirror case exists for promisor markers (3d).

### 3d. Adjacent declared channel: the promisor refusal is marker-based and defeatable

Grid F23 removes the promisor config but keeps the `.promisor` sidecar and expects exit 2.
Remove the sidecar too (blobless clone, `--no-local`, all three config keys unset):

```
git -C clone rev-list --objects --all --missing=print  -> ?6e98d181389d343031fd578c6a775ce0889a8b0d
current exit 1  unresolved-full-hash 6e98d181...   (report's Notes cite that blob)
frozen  exit 1  unresolved-full-hash 6e98d181...
```

The object is provably missing, so per F23's own premise ("absence there is not evidence")
the declared outcome is exit 2; current instead emits a false defect. Conversely a complete
repo with a zero-byte `*.promisor` sidecar (`rev-list ... --missing=print` -> 0 missing) is
refused: `current exit 2 partial clone (promisor pack)`, frozen exit 1. The check at HEAD
`:442-444` tests file existence, not missing objects; `rev-list --objects --all
--missing=print` is a cheap content-based check that distinguishes both directions.

### 3e. Axis-level, explicitly unclaimed: local-config include FIFO hangs the audit

```
printf '\n[include]\n\tpath = <fifo>\n' >> lane/.git/config
timeout 5  git -C lane log -1                                  -> exit 124
timeout 10 python3 <current auditor> ... --json                -> exit 124
timeout 10 python3 <frozen auditor>  ... --json                -> exit 124
```

HEAD `:93-96` neutralizes specific `log.*` keys and strips `GIT_*`, but nothing bounds a
`git()` call (HEAD `:108-127`), so repository-local `.git/config` `include.path` can hang
every invocation before any verdict. The round-23 docstring says "other repository-local
channels are not claimed", so this is a non-claim, not a contradiction — but it is the
calibration axis's "hang" outcome, and a subprocess timeout in `git()` would convert it to
EvalError without touching verdicts.

## 4. What I did NOT verify

- The other 25 fault rows, the other 7 controls, the L1's frozen 0/26 and current 26/26
  totals beyond C02, the 50/50 selftest, the 24-mutant run (22 killed, M02/M20 survivors),
  the rounds 10-22 ledger byte-identity and `--no-errata` exit-1/9-defect claim. Not re-run.
- The lane's dirty worktree provenance (who is editing tracked files during the wave).
- No REA devices, no network fixtures, no installs or upgrades (none needed).

## 5. Files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-23/falsify/advice/RowC02RealOmission.md` (this report).
- Scratch only, not deliverables: `/tmp/kama-r23w2/RowC02RealOmission` (clone),
  `/tmp/kama-r23w2/c02/{build.sh,build.out,frozen.py,*.out,*.err,grid-c02.json,variants.py,
  omit_variants.py,near.py}` and fresh fixture repos under `/tmp/kama-r23w2/c02/{work,omit,
  near,bare,fifo}`.
