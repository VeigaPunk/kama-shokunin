# F05-replace-fleet-report — falsify advice

**Verdict: HOLDS.** Fault premise real and reproduced on an independently
hand-built fixture; expected outcome (exit 1, `landed-omitted`) is the
semantically correct verdict; 12 same-channel near variants found no residual
misbehavior in current (git 2.56.0, python 3.14.8, linux).

Row: `tests/report-audit/repo-state-grid.py:545-546` → builder
`f_replace_report` (`:254-268`), expect `("fault", f_replace_report, 1,
["landed-omitted"])`, no pinned REASON.

## 1. Fault premise — real and observed in frozen arm

Hand-rebuilt fixture (no import of the grid; retyped helpers + raw git) in
`/tmp/kama-r23w2/fix-f05/`:

- lane: `lc` commit `round-1: work` @1000 (author `kama-shokunin`), `x` commit
  `round-1: more` @1500.
- fleet: committed report at `HEAD:.ufo/reports/round-1/kama.md` cites `[lc]`
  only (commit `real`, %at 2000).
- decoy: rootless raw commit (author `fleet`, %at 2000) whose only file is the
  same report path citing `[lc, x]`; `git replace <real> <decoy>`.
- Premise verified at git level: `git -C fleet show HEAD:<rel>` shows 2 cites
  (decoy consulted); `git --no-replace-objects -C fleet show HEAD:<rel>`
  shows 1 cite (original). Also cross-verified inside my clone:
  `decoy blob/tree` plumbing via `hash-object -w` + `mktree` + `hash-object
  -t commit -w`.

Arm results on the hand-built fixture (argv `[py, auditor, --lane-repo,
--fleet-repo, --json, --rounds, 1, --no-errata]`, env scrubbed of `GIT_*`,
`GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1`, timeout 30):

```
F05 frozen   exit=0 kinds=[]                   tb=0 to=0
F05 current  exit=1 kinds=['landed-omitted']   tb=0 to=0
```

Independent cross-check on the real grid (read-only run):
`python3 tests/report-audit/repo-state-grid.py --case
F05-replace-fleet-report --arm both` → `frozen ... exit=0 kinds=[] NOT-MET`,
`current ... exit=1 kinds=['landed-omitted'] met`, grid exits 1. Identical to
my replica — my fixture is faithful.

Why frozen flips: frozen blob `4fe9339f:tools/report-landing-audit.py`
(sha256 `09ecd63b…`, verified via `cat-file` in my clone) calls
`subprocess.run(["git", "-C", repo, ...])` with no isolation flags
(`frozen-audit.py:89`), so `git show HEAD:<rel>` (`:266`) reads the decoy
report citing both commits → no defects → exit 0. The `landed-omitted` truth
is silenced by a repository-local ref. That is exactly the declared fault
class (repo-local state flipping the verdict).

## 2. Expected outcome — correct, not merely current's behavior

The semantic contract (auditor docstring `tools/report-landing-audit.py:48-55`)
is: audit the *committed* fleet bytes at HEAD vs lane history; repo-local
substitutions are adversarial, not evidence. Under the true object graph:
report cites `[lc]`, cutoff %at=2000 (first add), lane round-1 commits ≤2000
are `{lc, x}` → `x` is required-but-uncited → exactly one
`landed-omitted(x)`, exit 1. The pinned expectation is the true verdict.

Alternatives considered and rejected: exit 0 would bless a report that omits
a required citation; exit 2 (refuse refs/replace wholesale, grafts-style) is
defensible but weaker — replace refs are fully neutralizable by git itself,
so the auditor can still compute the true verdict rather than punting. The
pinned exit-1 choice is the better contract and is consistent with F03/F04
(same channel, lane side).

Current achieves it because the single subprocess site
(`tools/report-landing-audit.py:114`, the only `subprocess`/exec call in the
file) always prefixes `GIT_ISOLATION` (`:93-96`) which includes
`--no-replace-objects`; `git_env()` (`:99-104`) strips inherited `GIT_*` so
`GIT_REPLACE_REF_BASE`/`GIT_NO_REPLACE_OBJECTS` cannot be injected, and
repository config cannot re-enable replacement (there is no config knob;
only `--no-replace-objects`/`GIT_NO_REPLACE_OBJECTS`/`GIT_REPLACE_REF_BASE`
exist). `--no-replace-objects` disables all replace lookups regardless of
ref base.

## 3. Near-variant sweep (same channel, hand-built, both arms)

13 variants in `/tmp/kama-r23w2/f05_variants.py`, fixtures under
`/tmp/kama-r23w2/fix-variants/`. "honored" = observed with plain git
(replace applied); each row ran frozen then current:

| variant | honored git semantics | frozen | current | current correct? |
|---|---|---|---|---|
| V1 decoy *hides* a cite (orig cites [lc,x], decoy [lc]) | show→decoy | exit1 omitted | exit0 | yes — committed report is complete |
| V2 decoy %at=2500 (later cutoff) | cutoff→2500 | exit1 (omits y@2200) | exit1 (omits x@1500) | yes — same kind, correct token |
| V3 `refs/replace/<report-blob>` → decoy blob [lc,x] | blob substitution confirmed | exit0 | exit1 omitted | yes |
| V4 blob decoy w/o `## Landed changes` | section replaced | exit1 {omitted, section-missing} | exit1 {omitted} | yes |
| V5a lane `replace x` → decoy author `fixture` | `%H` keeps orig oid, `%an` decoy | exit0 | exit1 omitted | yes |
| V5c lane `replace x` → decoy subject `note unrelated` | round filter drops x | exit0 | exit1 omitted | yes |
| V5d lane `replace x` → decoy %at 2500 | x becomes post-report | exit0 | exit1 omitted | yes |
| V6 `refs/replace/<HEAD-root-tree>` → decoy tree | tree substitution confirmed | exit0 | exit1 omitted | yes |
| V7 decoy %at=1200 (earlier cutoff) | cutoff→1200 | exit0 | exit1 omitted | yes |
| V8 `refs/replace/<HEAD>` → blob (type mismatch) | `HEAD^{commit}` rc=128 | exit2 | exit1 omitted | yes |
| V9 `refs/replace/<HEAD>` → decoy whose parent is `<HEAD>` (cycle) | `git log` terminates, shows 1 commit | exit2 "no fleet commit" | exit1 omitted | yes |
| V11 chained `refs/replace/<real>`→d1, `refs/replace/<d1>`→d2 | **transitive**: honored show = d2 | exit0 | exit1 omitted | yes |
| V12 lane `refs/replace/<x>` → blob; report cites [lc,x] | `cat-file x^{commit}`→"missing" (batch) | exit2 batch-parse | exit0 | yes — committed report cites both |

Key findings beyond the pinned row:

- Replace substitution is **not commit-only**: blob (V3/V4) and tree (V6)
  objects are substituted on read, and chains are followed transitively
  (V11). `--no-replace-objects` covers all of them — verified empirically,
  current immune in every row.
- Lane-side replace (V5a/c/d, V12) is the same channel through a different
  repo argument; isolation covers both repos.
- Malformed replace state (type mismatch V8, self-cycle V9) degrades frozen
  to exit2 or wrong verdicts; current is indifferent because it never reads
  replaced objects.
- No variant produced a traceback, timeout, or program execution under
  current; no residual wrong verdict found on this channel.

## Not verified / out of scope

- Real production lanes (fixtures only, as assigned); coexistence with the
  other declared-open channels (alternates, gitfile, etc.) not combined.
- Non-Linux git / git <2.45 (floor is declared; not exercised).
- Whether `--no-replace-objects` also suppresses *writing* replace refs —
  irrelevant, auditor never writes.
- Full grid re-run on both arms (ran only `--case F05`; other rows are
  sibling scopes).

## Evidence index

- Hand-built replica + sweep: `/tmp/kama-r23w2/f05_handbuild.py`,
  `/tmp/kama-r23w2/f05_variants.py`; fixtures `/tmp/kama-r23w2/fix-f05/`,
  `/tmp/kama-r23w2/fix-variants/`.
- Frozen blob: `/tmp/kama-r23w2/frozen-audit.py`, sha256
  `09ecd63bdc3a5be5264e6d2966602a32e52ca0678dc89de99959318245ab3b3f`
  (= `4fe9339f8fc3a4a4a479d9c938a850da12f1124d:tools/report-landing-audit.py`).
- Current auditor sha256 `f228f17420134a4a4fb6d1f93b943f78647e7e60882f767e6cb7cba11d6928a7`.
- Clone `/tmp/kama-r23w2/RowF05ReplaceFleet` @ `245a37f69628c2c6bb29bbf17897d8fb5946c857`.

## Files written

- `Report: .ufo/waves/round-23/falsify/advice/RowF05ReplaceFleet.md` (this file)
- `/tmp/kama-r23w2/f05_handbuild.py`, `/tmp/kama-r23w2/f05_variants.py`,
  `/tmp/kama-r23w2/frozen-audit.py` (scratch, outside the lane)

No installs; stock git 2.56.0 / python 3.14.8 sufficed.
