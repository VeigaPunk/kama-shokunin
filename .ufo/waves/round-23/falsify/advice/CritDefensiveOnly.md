# CritDefensiveOnly — surviving mutants M02 / M20 (round 23 FALSIFY)

Base: 245a37f69628c2c6bb29bbf17897d8fb5946c857 (clone `/tmp/kama-r23w2/CritDefensiveOnly`,
`git rev-parse HEAD` = 245a37f6…, worktree clean). git 2.56.0. Seat: CloseKama22.CritDefensiveOnly-2.

## Verdict: PARTIALLY FALSIFIED

- **M02 (`--no-lazy-fetch`): the "defensive-only, superseded by promisor refusal" label is FALSIFIED.**
  A repo-local promisor remote created by `remote.<name>.partialclonefilter` alone passes every
  refusal in `check_history_repo`. A missing-object lookup then lazy-fetches and runs a
  repo-configured program. `--no-lazy-fetch` is the only thing that prevents this. M02 is
  load-bearing; the grid just has no row for it.
- **M20 (40-hex `%H` shape check): the "defensive-only" label HOLDS.** No repo-local state I built
  reaches it. The stated reason is wrong, though: `corpus/lessons/round-23.md:80` says "signature
  display is disabled", but the M06+M20 double mutant on F09 behaves exactly like M06 alone.
- The C1 calibration claim itself is **not** falsified. The pristine auditor meets both new
  faults: exit 1, `exec=0`, `tb=0`, `timeout=0`. Only the 22/24 kill decomposition and the
  lesson's rationale are wrong.

## M02 counterexample (P01 lane / P02 fleet)

Fixture, fresh `/tmp` repo with `GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1` and explicit
identity:

```
remote.evil.url                = ssh://example.invalid/x.git
remote.evil.partialCloneFilter = blob:none
core.sshCommand                = touch <marker>; false
```

The fixture adds no `remote.*.promisor`, no `extensions.partialclone` and no `*.promisor` pack;
the builder asserts all three are absent. The report cites a fabricated full hash `abcdef…abcd`
in `## Landed changes`.

Why it passes the refusal: `tools/report-landing-audit.py:445-448` only refuses
`extensions.partialclone` or `re.fullmatch(r"remote\..+\.promisor", name)`. `git config --list
--name-only` reports the key as `remote.evil.partialclonefilter`, which neither pattern matches.
The pack check at `:442-444` finds no `.promisor` file.

Why git still lazy-fetches: git v2.56.0 `promisor-remote.c:148-154`
(https://raw.githubusercontent.com/git/git/v2.56.0/promisor-remote.c, HTTP 200):
"`if (!strcmp(subkey, "partialclonefilter")) { … r = promisor_remote_lookup(config, remote_name, NULL); if (!r) r = promisor_remote_new(config, remote_name);`"

Observed directly:
- Plain `git cat-file -e abcdef…abcd`: "fatal: Could not read from remote repository.", rc=1,
  marker created.
- `git --no-lazy-fetch cat-file --batch-check`: "`abcdef… missing`", no marker.
- Same command without `--no-lazy-fetch`: marker created.

Graded with the grid's own `run_case` (same met criteria as F06), via
`python3 .ufo/waves/round-23/falsify/out/CritDefensiveOnly/probe.py /tmp/kama-r23w2/CritDefensiveOnly`
(probe_rc=0):

| arm | case | exit | kinds | exec | met |
|---|---|---|---|---|---|
| pristine | P01 lane | 1 | landed-unresolved, unresolved-full-hash | 0 | met |
| pristine | P02 fleet | 1 | same | 0 | met |
| **M02** | P01 lane | 1 | same | **1** | **NOT-MET** |
| **M02** | P02 fleet | 1 | same | **1** | **NOT-MET** |
| M20 | P01 / P02 | 1 | same | 0 | met |

So both the lane side and the fleet side kill M02.

Reproduced the L1 baseline: `isolation-mutants.py --only M02-lazy-fetch --only M20-log-sha-shape`
gives "M02-lazy-fetch survived grid=0", "M20-log-sha-shape survived grid=0", rc=0. The survival
comes from a gap in grid coverage, not from the code being redundant.

The pristine exit-1 verdict on P01/P02 is substantively right. With no promisor pack there are no
promisor objects, so absence is evidence. Refusing this repo is not required. Disabling the fetch
is.

Also checked, not a hole: an `includeIf "onbranch:master"` include that sets
`remote.evil.promisor=true`. `config --list --name-only`, run with the auditor's isolation flags,
lists `remote.evil.promisor`, so the refusal sees it. cat-file honours it too (lazy fetch ran
without `--no-lazy-fetch`).

## M20 attack: all vectors failed

The sha slot can differ from `%H` only if a field shift happens: an extra or missing NUL inside
`%an` or `%s`, while `fields % 4 == 0` and the atime field still passes `[0-9]{1,12}`. Every
probe gave exactly 4 NULs per record and a 40-hex first field:

- Commit `encoding` header re-encoding to UTF-8. UTF-7 with `+AAA-` (U+0000) in the author and in
  a subject carrying a forged record: not decoded, 4 NULs. UTF-16LE: fields blanked, 4 NULs.
  ISO-2022-JP: 4 NULs.
- `log.abbrevCommit=true`, `core.abbrev=4`, `log.decorate=full`, `color.ui=always`,
  `notes.displayRef=refs/notes/*` with a note present, `format.pretty=oneline`: clean 40-hex `%H`.
  These do not affect an explicit `%`-format.
- `extensions.compatObjectFormat=sha256` (repo format version 1): `--show-object-format` reports
  `sha1` and `%H` is 40 characters. sha256 repos are refused at `:431-433` (M15 / F15).
- Signature display: M06 on F09 gives exit 0, kinds [], exec 1. M06+M20 on F09 gives the same
  (probe rows). The shape check never fires even with showSignature on. Signature display also
  cannot exist without running `gpg.program`, which `exec` already grades as a violation.

What actually makes M20 unreachable [INFERENCE from the probes plus git semantics]: `%H` is the
object id printed in the repository's hash format, the format is pinned to sha1 by `:431-433`,
and `-z` fields cannot carry a NUL (F25 lineage plus the encoding probes above).

## Should they be deleted?

- **M02: no.** It is the only guard against program execution (axis 7: "run programs") for
  `partialclonefilter`-only promisor remotes. It costs one argv token and the declared git ≥ 2.45
  floor. Deleting it reintroduces a real violation.
- **M20: keep, but relabel.** It is not an isolation element. It is an assertion on
  subprocess-output shape. Unreachable is not the same as worthless here. If a future git or
  format change ever shifted fields, the malformed value would flow into `startswith` matching and
  into the `landed-omitted` token at `:332-336`, producing a verdict (exit 1) instead of an
  EvalError. That breaks the tool's own rule "Errors are never verdicts" (`:46`). The `% 4` and
  atime checks are only partial backstops. Deleting it is defensible under "delete dead weight",
  but it would trade a zero-cost invariant for a silent-verdict risk. Recommend keeping it.

## Impacted axes

- Axis 7 calibration claim accuracy. The C1 pass still holds, but "22 killed, 2 defensive-only"
  overstates redundancy: the real figure is one load-bearing element with no grid row and one
  invariant assertion.
- Provenance / false rationale: `corpus/lessons/round-23.md:79-81`.

## Smallest safe correction (L1-owned; this seat edited nothing tracked)

1. Add a grid fault row. The P01 builder (`_filter_only` in the probe) is a drop-in
   `repo-state-grid.py` case: kind `fault`, expect exit 1, kinds `["landed-unresolved",
   "unresolved-full-hash"]`, with a marker. It kills M02 on the pristine population (P02, the
   fleet variant, is optional). This changes the grid's `population_sha256`.
2. Do not widen the refusal regex to `partialclonefilter`. That would add a new refusal tradeoff
   for a repo where absence is evidence. If L1 wants it anyway, M02 becomes defensive-only again
   and needs its own row to stay honest.
3. Correct the lesson's defensive-only bullet, as an erratum, not a rewrite. Say `--no-lazy-fetch`
   is required for promisor remotes created by `remote.<n>.partialclonefilter`, which the refusal
   does not see. Say the `%H` check is unreachable because the format is pinned to sha1 and fields
   cannot carry NUL, not because signature display is disabled.
4. Optionally exclude M20 from the isolation-mutant population, or tag it `assertion` so it is not
   counted as an isolation element.

## Not verified

- I did not run the full grid (both arms) or the full 24-mutant suite; only the M02/M20 `--only`
  reproduction and the probe above.
- I did not check git versions other than 2.56.0. The git 2.45 floor and older git's
  `partialclonefilter` behaviour are untested.
- I did not test other promisor-creating config spellings beyond `partialclonefilter` and
  `includeIf onbranch`. That includes worktree config (`config.worktree`), `include.path` chains
  and `hasconfig:`. They are [INFERENCE] covered by `config --list`, but unrun.
- I did not test M20 against a git that emits NUL inside `%an`/`%s` via replace objects or mailmap
  (both are disabled by isolation); unrun.

## Tools installed

None.

## Files written

- `.ufo/waves/round-23/falsify/advice/CritDefensiveOnly.md` (this report)
- `.ufo/waves/round-23/falsify/out/CritDefensiveOnly/probe.py` (probe; imports the grid's
  `run_case` and the mutant table from the clone)
- Scratch outside the lane: `/tmp/kama-r23w2/CritDefensiveOnly` (clone),
  `/tmp/kama-r23w2/CritDefensiveOnly-fx*` (fixtures),
  `/tmp/kama-r23w2/CritDefensiveOnly-promisor-remote.c` (git source fetched for the citation)
