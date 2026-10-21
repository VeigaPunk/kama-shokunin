# Falsify: C05-shared-clone-clean (control)

**Verdict: HOLDS** — the row's premise is real, both arms produce the expected
exit 0 / no-defects, and exit 0 is the correct verdict under the auditor's own
contract. Near variants of the same channel do expose still-wrong behavior, but
every one routes through channels the round-23 build wave explicitly declared
Open (O01 alternates) or never claimed (sibling donor state invisible to
`check_history_repo`). No falsification of the scored claim.

Commit reviewed: `245a37f69628c2c6bb29bbf17897d8fb5946c857`
(clone at `/tmp/kama-r23w2/RowC05SharedClone`, `rev-parse HEAD` verified equal).

## Row under attack

`tests/report-audit/repo-state-grid.py:153-159` (`c_shared_clone`):
`base()` builds lane (one `round-1: work` commit by `kama-shokunin` at
@1000) + fleet (report `.ufo/reports/round-1/kama.md` citing it at @2000),
then `git clone -q --shared lane shared`; premise check requires
`shared/.git/objects/info/alternates` to exist. Row `repo-state-grid.py:534`:
`("C05-shared-clone-clean", "control", c_shared_clone, 0, [])` → expected
exit 0, zero defects, no traceback/execution/timeout.

## (1) Premise is real and independently reproduced

Hand-built fixture `/tmp/kama-r23w2/fixture-c05` (script
`/tmp/kama-r23w2/build-c05.sh`; NOT importing the grid). Stronger premise
check than the grid's: the shared clone has **0 loose objects and 0
packfiles** — every object including HEAD resolves through
`objects/info/alternates` → `…/lane/.git/objects`. Git 2.56.0.

Runs (auditor argv matching `run_case`: `--lane-repo shared --fleet-repo
fleet --json --rounds 1 --no-errata`, scrubbed env, timeout 30, cwd=tmp):

| arm | rc | defects | stderr |
|---|---|---|---|
| frozen blob `4fe9339f…:tools/report-landing-audit.py` (sha256 09ecd63b…) | 0 | `[]` | (empty) |
| current committed auditor (sha256 3fc567ab…) | 0 | `[]` | (empty) |

Both `summary.status == "clean"`, `required_commits=1`. Grid corroboration in
my clone: `repo-state-grid.py --arm both --case C05-shared-clone-clean` →
`frozen … met`, `current … met`, `violations=0` both arms.

## (2) Expected outcome is the CORRECT one

Exit 0 is right, not merely "what current does": the shared clone's HEAD
commit (round-1, `kama-shokunin`, author time ≤ fleet cutoff @2000) resolves
through alternates, the citation resolves, `round_commits` enumeration finds
the same one commit, nothing omitted. The auditor docstring
(`tools/report-landing-audit.py:53`) documents "Objects borrowed through
objects/info/alternates … still resolve as local" — for a clean fixture the
honest verdict is clean. Anything else (rc 1 or 2) would contradict the
tool's own contract.

## (3) Near variants of the alternates channel current still gets wrong

All fixtures in fresh `/tmp/kama-r23w2/v*` repos, `GIT_CONFIG_GLOBAL=/dev/null
GIT_CONFIG_NOSYSTEM=1`, explicit identity; ssh fixture uses `example.invalid`.

- **V3 — donor-only commit resolves as "landed" through alternates**
  (`/tmp/kama-r23w2/v3r`). `clone --shared`, *then* a new commit is made in
  the donor (never fetched into the clone's refs). Fleet report cites it.
  - shared clone: **rc=0, defects=[]** — `cat-file --batch-check` finds the
    object in the borrowed ODB.
  - non-shared `--no-local` twin, identical report+history: **rc=1,
    `landed-unresolved` + `unresolved-full-hash`** (both arms).
  A routine `clone --shared` flips the verdict on a citation not in the
  audited history. Frozen arm behaves identically → coverage gap, not a
  regression. This IS the declared-open O01 channel (foreign objects via
  alternates); the variant shows O01 needs no hand-edited alternates file —
  normal `--shared` use plus ordinary donor activity suffices.

- **V6b/V6c — `clone --shared` of a partial clone launders the promisor
  state** (`/tmp/kama-r23w2/v6b`, `v6c`). Donor = blobless `--filter=blob:none
  --no-checkout` clone with `remote.origin.promisor` + hostile
  `core.sshCommand` (`example.invalid`). The shared clone borrows
  `donor/.git/objects` but inherits **no** promisor config, **no** `.promisor`
  pack — all three detection layers in `check_history_repo`
  (`report-landing-audit.py:438-448`) see a "complete" repo whose ODB is
  actually partial.
  - Report citing a genuinely absent blob hash → shared clone: **rc=1,
    `unresolved-full-hash`** (a verdict where the policy "absence is not
    evidence in a partial clone" demands refusal). Direct donor: **rc=2
    "partial clone (promisor pack)"** — the T01 refusal is bypassed purely
    by the alternates indirection. Frozen arm identical (rc=1).
  - Plain (non-shared) clone of the same donor **does** carry a `.promisor`
    pack → current still refuses rc=2. Only `--shared` evades it.
  - Execution hazard: raw `cat-file --batch-check` in the shared clone
    (git's defaults) **triggered the donor's promisor fetch and EXECUTED the
    donor's `core.sshCommand`** — marker `donor-fetch-ran` created. The
    auditor's `--no-lazy-fetch` (GIT_ISOLATION, line 93) provably suppresses
    the cross-alternate fetch+exec (marker absent under isolation and under
    the audit). So "runs programs" does NOT recur through this door for the
    auditor itself — but only `--no-lazy-fetch` stands there.

- **V26 — `clone --shared` of a grafted repo drops `info/grafts`**
  (`/tmp/kama-r23w2/v26r`). Donor with `.git/info/grafts` (tip grafted to
  root; `rev-list --count HEAD` = 1 vs objects for 2). Direct: **frozen rc=1
  `landed-omitted` (the round-22 bug), current rc=2 "rewrites history"**
  (F11 refusal confirmed working). Shared clone sees the honest full history
  (count=2) → rc=1 `landed-omitted`, which is semantically *correct* for the
  audited repo's own history. Note ANY plain clone also drops grafts —
  generic clone behavior, not specific to this channel; reported for
  completeness only.

- **Refusal paths verified honest** (near variants that fail closed, not
  wrong): alternates → moved-away dir (`v2`): rc=2; alternates → empty
  objects dir (`v2` variant b): rc=2 `Needed a single revision`;
  relative-path alternates rejected by git 2.56 (`unable to normalize`) →
  rc=2 (`v8`); chained `--shared` then middle removed (`v11b`): rc=2;
  `.git/shallow` **does** propagate through `clone --shared` → rc=2
  "shallow repository" (`v5`, asymmetric with grafts/promisor).

## Not verified / out of scope

- No timing/race: donor mutated *during* an audit run.
- Alternates files with duplicate lines, comments, or a self-loop (git
  dedupes; expected no-op either way).
- `GIT_ALTERNATE_OBJECT_DIRECTORIES` env — `git_env()` strips `GIT_*`
  (`report-landing-audit.py:103`); not a repo-local channel.
- Whether the fleet-repo arm of `run_case` could equally host these fixtures
  (symmetric by code inspection, `check_history_repo` runs on both;
  not exercised).
- The exact o_alternates (O01) row itself — sibling reviewer owns it.

## Files written

- `/tmp/kama-r23w2/RowC05SharedClone/` — my clone of the lane (read-only use)
- `/tmp/kama-r23w2/frozen-audit.py` — extracted frozen blob
- `/tmp/kama-r23w2/build-c05.sh`, `variants{,2,3,4,5,6,7}.sh` — fixture scripts
- `/tmp/kama-r23w2/fixture-c05/`, `/tmp/kama-r23w2/v{2,3r,4,5,6b,6c,8,11,26r}/` — fixtures
- This report: `.ufo/waves/round-23/falsify/advice/RowC05SharedClone.md`

No installs performed or needed (git 2.56.0, python 3.14.8 already present).
