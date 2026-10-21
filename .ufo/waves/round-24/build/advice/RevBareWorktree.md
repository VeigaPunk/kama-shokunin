# RevBareWorktree — bounded static review

**Round 24 / C1 calibration 7→7, lane: bare and linked-worktree Git paths —
object-store and promisor-marker detection via `rev-parse`.**

Base audited: `0df800e896f6bce285a81e794ad4ae1d1e6c3a71` (lane HEAD is this
commit; at lane start `git status --porcelain` showed only the untracked
`.ufo/waves/round-24/`). The only files this lane wrote are under
`.ufo/waves/round-24/build/` (`advice/RevBareWorktree.md` and
`out/RevBareWorktree/`); `LOG.md` and `.ufo/waves/round-24/preregistration.json`
changed in the lane during the session but are not this lane's work.
Audited tool: `tools/report-landing-audit.py`
(sha256 `da5041a8191e0e6ec385adc7c659ddc7544a835aff65dd45b34de623c5765af1`).
No production file was modified. No subagent was dispatched (leaf lane).
No network transport, no repo-configured program, no fetch was executed by any
fixture: every "promisor" marker in the fixtures was written by hand into a
local config file or next to a local pack.

## Axes

| # | axis | what was checked |
|---|---|---|
| A1 | layout parity | plain worktree / bare / linked worktree / linked-worktree-of-bare give the same verdict for the same content |
| A2 | object-store resolution | where `git rev-parse` says the packs live, and whether the tool follows that pointer |
| A3 | promisor detection | every channel that makes a repository promisor-backed, in every layout |
| A4 | path/repo identity | whether the same repository reached through two paths yields the same verdict |
| A5 | r24 semantics fit | whether the base code's structure can express "missing ⇒ unknown (exit 2), but only for promisor-backed repos" |
| A6 | no-harm | the base's non-promisor verdicts (exit 0 / exit 1 / refusal reasons) must not change |

## Measured matrix (base tool, r23 semantics)

Fixture: lane commits `round-1: work`@1000, `round-1: measure`@1100,
`checkpoint(r1) save`@1150, `round-1: late advice`@1300 (author times);
fleet report committed at author time 1200 (the cutoff) citing only the first
two. `checkpoint(r1) save` is therefore a genuine pre-cutoff omission
(expected defect `landed-omitted`); the 1300 commit is post-report.

| layout (lane/fleet) | base exit | defect |
|---|---|---|
| plain worktree | 1 | `landed-omitted 56296c2f…` |
| bare | 1 | `landed-omitted 56296c2f…` |
| linked worktree (`worktree add`) | 1 | `landed-omitted 56296c2f…` |
| linked main clone path | 1 | `landed-omitted 56296c2f…` |
| linked worktree of a **bare** repo | 1 | `landed-omitted 56296c2f…` |
| plain, promisor-marked (config + `.promisor` pack marker) | **2** | `could-not-evaluate: … partial clone (promisor pack)` |
| bare, promisor-marked | **2** | `could-not-evaluate: … partial clone (promisor pack)` |
| linked worktree, promisor-marked | **2** | `could-not-evaluate: … partial clone (promisor pack)` |

Clean-pair control (report cites every required commit): plain / bare / linked
worktree / linked main → **exit 0** in all four.

So the r23 blanket refusal is layout-independent: the base refuses every
promisor-marked repository, in every layout, whether or not it holds every
required object locally. That is exactly the harm the r24 claim names.

## Findings (severity ordered)

### HIGH-1 — promisor detection is path-scoped, so one repository yields two verdicts

`check_history_repo` reads the config with `git … config --null --list`
(`tools/report-landing-audit.py:458-465`). That lists the **common config plus
the scope of the audited path only**. A promisor remote declared in a linked
worktree's own scope (`<common>/worktrees/<name>/config.worktree`) is
invisible from a sibling worktree of the same repository.

Measured (`probe-pathsame.sh`, artifact `probe6.out`): one lane clone, one
linked worktree, `remote.origin.promisor=true` written with
`git config --worktree` into `.git/worktrees/lane-wt/config.worktree`:

```
-- config --list seen through the LINKED worktree:   remote.origin.promisor
-- config --list seen through the MAIN worktree:      (none)
audit through the MARKED path (linked worktree):   rc=2  partial clone (remote.origin.promisor)
audit through the UNMARKED path (main worktree):   rc=1  status=failed
```

Same object store, same content, two exits. Under r24 this stops being a
cosmetic refusal difference and becomes a **false verdict**: reached through the
unmarked path, a missing citation would be reported as *proved absent*
(exit 1 `unresolved-full-hash` / `landed-unresolved`) although the repository
is promisor-backed and the truth is *unknown* (exit 2). This directly
contradicts the prereg row "A missing citation in any promisor-backed
repository is unknown, not proved absent".

The repository-level channel (`.promisor` pack markers in the common store)
*is* path-independent; the config channel is not. The detection must be
repository-scoped: the union of

* `.promisor` markers in `git rev-parse --git-path objects/pack` (common dir
  for every worktree of the repository),
* the audited path's config scope,
* the **common** config (`extensions.partialclone`, `remote.*.promisor`),
* every sibling worktree scope `<common>/worktrees/*/config.worktree`.

### HIGH-2 — `lookup()` cannot express the r24 rule "exit 2 unless resolved locally by another audited repository"

`lookup()` (`:139-175`) collapses all repositories into one status dict
(`status[token] = "found"` / `"ambiguous"`, initial `"missing"`). A token
missing in the promisor repository but present in the fleet repository and a
token missing everywhere are indistinguishable after the call. The r24 rule
needs per-repository attribution: *missing in a promisor-backed repo AND not
found in any other audited repo ⇒ exit 2*. With the current structure that
rule is unimplementable without changing `lookup`'s contract (record the
repositories in which each token came back `missing`, then escalate).

Note that the base's `git cat-file --batch-check` is already the right probe:
under `--no-lazy-fetch` it answers `<oid> missing` with rc 0 for an object
that is absent from a promisor store (measured, `probe3.out` §2) — no fetch,
no error. The escalation point is therefore the *status*, not the subprocess.

### HIGH-3 — the promisor definition omits `remote.<name>.partialclonefilter`

`check_history_repo` recognises only `extensions.partialclone` and
`remote.*.promisor` (`:462-464`) plus `.promisor` pack markers (`:454-457`).
Git's own rule is broader: a remote that carries a `partialclonefilter` **is**
a promisor remote — the r23 grid fixture
`tests/report-audit/repo-state-grid.py:482-501` (`f_filter_promisor`) measures
that a filter-only remote triggers a lazy fetch, and its comment states
"`remote.<name>.partialclonefilter` alone makes a promisor remote".

Consequence for r24: with the base's key set, the F27 fixture's repository is
*not* promisor-backed, so a missing citation there is again reported as
*proved absent* (today exit 1 with `landed-unresolved` + `unresolved-full-hash`;
under r24 it must be exit 2, unknown). If the candidate keeps the base's key
set, the prereg row "a missing citation in any promisor-backed repository is
unknown" is unmet for the filter-only channel. `remote.*.partialclonefilter`
must join the detected key set (the base already carries the same idea in the
grid's `f_filter_promisor`, so this is a consistency repair, not new scope).

### MEDIUM-1 — abbreviated citations are not comparable between a full clone and a promisor clone

The prereg row "exact same substantive clean/failed findings as otherwise
identical full clones" is only true for **full 40-hex** citations.
`cat-file --batch-check` resolves a short token against the objects *visible
locally*; in a blobless/treeless partial clone that candidate set is smaller
than in a full clone, so

* `landed-ambiguous` for a 7..39-hex token is provisional (a remotely held
  object with the same prefix may exist), and
* even `found` for a short token is provisional in the same way (the token may
  name two objects once the promisor's objects are present).

kama reports cite *abbreviated* hashes inside `## Landed changes` (the tool's
own `landed-unresolved` / `landed-ambiguous` kinds exist precisely for those),
so this is the common case, not an edge case. Either

* escalate any abbreviated citation in a promisor-backed repository to exit 2
  (unknown), keeping only full-hash citations decidable, or
* narrow the prereg row to full-hash citations and add the limitation to the
  lesson/docstring.

The omission verdict itself is not affected: `round_commits` yields full
40-hex shas from `git log` (`:189-213`).

### MEDIUM-2 — the alternates channel is not covered by the detection

Measured (`probe-gaps.sh` §b, artifact `probe4.out`): a repository whose only
promisor pack is reachable through `objects/info/alternates` is **not**
detected — the base audits it normally and returns exit 1
(`landed-omitted`). Under the r24 rule "missing ⇒ unknown", a missing object
in a repository that borrows an alternate store is likewise not proved absent
**[INFERENCE]** — the fixture measures the detection gap; the missing-object
consequence follows from the r24 rule, it was not separately measured.
The base docstring explicitly leaves alternates unclaimed
(`tools/report-landing-audit.py:48-55`), which is sound for objects that
*are* found but not for objects that are *not*. Either escalate
missing-objects in alternates-bearing repositories to exit 2, or refuse such
repositories, or declare the hole in the r24 claim's "not_claimed" list.

### MEDIUM-3 — the refusal text is not stable across layouts, and the r24 grid will pin it

`check_history_repo` raises on the **first** matching key (`:462-465`), and
`git config --list` emits keys in file order. Measured refusals for the same
logical state: `partial clone (extensions.partialclone)` in the plain layout,
`partial clone (remote.origin.promisor)` in the bare and linked layouts
(`probe4.out` §a). The r23 grid pins refusal reasons by substring
(`REASONS` in `tests/report-audit/repo-state-grid.py:695-708`), so the r24 grid
must pin a *stable class* (`partial clone` / `promisor-backed`), not the first
key name — or the candidate must sort/collect the matching keys before
raising.

### LOW-1 — the sibling-`.pack` requirement in the pack scan is load-bearing; keep it deliberately

`:454-457` accepts a `.promisor` marker only when a sibling `.pack` exists
(`p.with_suffix(".pack").exists()`). Git keys promisor-ness on the `.promisor`
file next to the `.idx`, so the rule is narrower than git's. It must stay:
control **C10** (`tests/report-audit/repo-state-grid.py:545-549`) plants an
orphan `pack-deadbeef.promisor` with no pack and expects exit 0. Relaxing the
rule to "any `.promisor` file" would flip C10 to exit 2 — a control regression.
If the candidate changes this test, C10 must be updated in the same change and
the reason recorded.

### LOW-2 — `--is-bare-repository` is never consulted (not a defect; state it)

Every git call the tool makes (`log`, `ls-tree`, `show`, `cat-file`,
`rev-parse`, `for-each-ref`) is an object-store operation and works in a bare
repository; measured exit 1/exit 0 parity above confirms it. The docstring's
trust paragraph (`:48-55`) does not mention bare or linked-worktree
repositories at all; since r24 must *preserve* them, they belong in the
documented scope.

### LOW-3 — do not "simplify" the `--git-path` composition

`:451` composes `Path(repo, git(repo, "rev-parse", "--git-path", rel).strip())`.
Measured behaviour (artifacts `probe-layout.out`, `probe3.out`):

| layout | `--git-path objects/pack` | `--git-path info/grafts` | `--git-common-dir` |
|---|---|---|---|
| plain worktree | `.git/objects/pack` (relative) | `.git/info/grafts` | `.git` |
| bare | `objects/pack` (relative) | `info/grafts` | `.` |
| linked worktree | `<common>/.git/objects/pack` (absolute) | `<common>/.git/info/grafts` | `<common>/.git` |
| linked worktree of a bare repo | `<bare>/objects/pack` (absolute) | `<bare>/info/grafts` | `<bare>` |

`Path(base, absolute)` returns the absolute path, so the composition is
correct in all four layouts. Rewriting it as `repo / ".git" / "objects/pack"`
would break bare repositories (no `.git`) and linked worktrees (the store is
in the common dir). `--git-common-dir` is the pointer to add for the sibling
worktree scopes required by HIGH-1.

## Verified non-defects (do not "fix" these)

* **N1** — the object-store pointer is layout-correct in plain/bare/linked/
  bare+linked (table above); the promisor `.promisor` marker is found through
  it in every layout (the promisor-marked variants all refused with
  `partial clone (promisor pack)` — i.e. the marker branch fired, not only the
  config branch).
* **N2** — `info/grafts` resolves to the **common** dir from a linked
  worktree, which is where git reads grafts from; the graft refusal is
  therefore not bypassed by auditing through a linked worktree.
* **N3** — `git rev-parse --show-prefix` is empty in a bare repository and at
  a worktree root, so the "not a repository top level" refusal (`:447-448`)
  does not misfire on bare or linked layouts.
* **N4** — `cat-file --batch-check` under `--no-lazy-fetch` answers `missing`
  with rc 0 for an absent object in a promisor-marked repository (no fetch, no
  error): the exit-2 escalation can be built on the existing lookup.
* **N5** — layout parity holds for non-promisor repositories: identical exit
  codes and identical defect sets across plain/bare/linked/bare+linked, for
  both the omission fixture (exit 1) and the clean fixture (exit 0).
* **N6** — the existing isolation is intact and must survive: `--no-lazy-fetch`
  and `--no-replace-objects` in `GIT_ISOLATION` (`:93-95`), `GIT_CONFIG_GLOBAL=
  /dev/null` + `GIT_CONFIG_NOSYSTEM=1` + all inherited `GIT_*` stripped in
  `git_env` (`:99-106`), `GIT_TIMEOUT = 20` (`:108`).

## Acceptance points for the r24 candidate (concrete)

* **AP-1** — promisor-ness is computed **per repository**, not per path: union
  of `.promisor` markers under `git rev-parse --git-path objects/pack`, the
  audited path's config scope, the common config, and every
  `<common>/worktrees/*/config.worktree`. Grid row: the same repository
  audited through a marked worktree and through a sibling worktree must give
  the **same exit and the same defect set**.
* **AP-2** — bare repositories are audited, not refused: a bare lane+fleet
  pair holding every required object locally gives the same verdict as the
  plain pair (measured baseline: exit 1 + `landed-omitted`, or exit 0 for the
  clean pair).
* **AP-3** — linked worktrees are audited, not refused: the pack directory is
  taken from `--git-path objects/pack` (absolute, into the common dir), never
  from `<repo>/.git/objects/pack`.
* **AP-4** — a promisor-marked repository that holds every required object
  locally gives the **same substantive verdict** as its full clone (exit 0 or
  exit 1 with the same defect kinds/tokens), not exit 2.
* **AP-5** — a required object that is genuinely unavailable in a
  promisor-backed repository is **exit 2** (`could-not-evaluate`), never a
  clean or failed verdict; the same missing object in a non-promisor
  repository keeps today's exit 1 defect.
* **AP-6** — `lookup()` (or its replacement) records the repositories in which
  each token came back `missing`, so that "missing in a promisor-backed repo
  but found in another audited repository" stays decidable (no exit 2).
* **AP-7** — the detected promisor key set is
  `extensions.partialclone`, `remote.*.promisor` **and**
  `remote.*.partialclonefilter`; `remote.*.promisor=false` stays
  non-promisor (control C09), and an orphan `.promisor` file without a
  sibling pack stays non-promisor (control C10).
* **AP-8** — the r24 grid documents the policy-row expectation changes against
  the retained r23 grid: `F23` (promisor pack, no config) stays exit 2 with a
  new *availability* reason; `F27` (filter-only promisor remote) moves from
  exit 1 `[landed-unresolved, unresolved-full-hash]` to exit 2 (unknown, not
  proved absent); `F06` (lazy-fetch command) stays exit 2 with the reason
  re-worded; `T01` (blobless partial clone) becomes exit 0. Each change is
  recorded as a *policy* change, not a silent re-baseline.
* **AP-9** — detection adds no execution path: only `rev-parse`, `config`,
  `ls` and the existing `cat-file --batch-check` are used; `--no-lazy-fetch`,
  `--no-replace-objects`, the config/global isolation and the 20 s deadline
  are unchanged; a missing object in a promisor repository must never trigger
  a fetch (verified answer: `missing`, rc 0).
* **AP-10** — the refusal text is a stable class, not the first matching key;
  grid rows assert on the class.
* **AP-11** — the abbreviated-citation question (MEDIUM-1) is decided
  explicitly: either escalated to exit 2 in promisor-backed repositories, or
  excluded from the prereg row with the limitation recorded in the docstring
  and the round-24 lesson. It must not be left implicit, because kama reports
  cite abbreviated hashes.
* **AP-12** — the alternates channel (MEDIUM-2) is decided explicitly: escalated
  to exit 2 for missing objects, refused, or declared in `not_claimed`.
* **AP-13** — the r24 grid covers all four layouts for the same content
  (plain, bare, linked worktree, linked worktree of a bare repo) and asserts
  verdict equality across them, not merely per-row exits.

## Residual risk and verification gaps

* The r24 candidate does not exist at the base commit; every "must" above is a
  static/derived requirement from the base code plus the measured layout
  behaviour, not an observation of the candidate. **Unverified.**
* Only the *configuration* and *pack-marker* promisor channels were exercised.
  A genuine `git clone --filter=blob:none` over `file://` was **not** built
  (the lane forbids transports); the fixtures reproduce the same observable
  state (hand-written `remote.origin.promisor`, `extensions.partialclone`,
  `remote.origin.partialclonefilter`, `.promisor` marker next to a real pack)
  and the base tool's branch selection is identical, but the *real* clone's
  extra keys (e.g. `core.repositoryformatversion=1`,
  `remote.origin.partialclonefilter`) were only partly reproduced.
* The lazy-fetch/execution channel (`core.sshCommand` etc.) was not re-measured
  here; it stays covered by the r23 grid rows F06/F27 and the r23 advice
  (`ConnPlanningWalk.md`), and my fixtures never configured a command.
* Truncated promisor histories (an interrupted partial clone) are not
  distinguishable from complete ones by the tool: a locally complete branch
  tip with a shorter history would under-report `landed-omitted`. Low risk
  (a shallow boundary is refused at `:449-450`, and an interrupted clone fails
  `resolve_branch` → exit 2), but not measured here.
* SHA-256 object format, `objects/info/alternates` *as a source of found
  objects*, `commit-graph` tampering, `core.useReplaceRefs` and old-git
  versions are out of this lane and unverified here.
* Worktree-scoped `remote.*` keys were only exercised for
  `remote.origin.promisor`; other per-worktree keys were not enumerated.

## Files

* This report: `.ufo/waves/round-24/build/advice/RevBareWorktree.md`
* Artifacts (scripts + captured output):
  `.ufo/waves/round-24/build/out/RevBareWorktree/`
  (`probe-layout.sh`, `probe-layout.out`, `build-fixtures.sh`,
  `run-base-matrix.sh`, `base-matrix.out`, `probe-bare-linked.sh`,
  `probe3.out`, `probe-gaps.sh`, `probe4.out`, `probe-scoped.sh`,
  `probe5.out`, `probe-pathsame.sh`, `probe6.out`, `probe-clean.sh`,
  `probe7.out`)
* Heavy fixtures (not copied): `/fast/scratch/hyaku/kama-r24/RevBareWorktree/`
  (`fixtures/`, `fixtures2/`, `probe3/`, `probe4/`, `probe5/`, `probe6/`,
  `probe7/`, 4.1 MB total)
* No production file, `.jj` state, Git index, sibling lane or host config was
  touched. No tool was installed or updated (no install was needed; git 2.56.0
  and python3 were already present).

### Artifact digests (sha256 of the captured outputs)

```
842d438f7b343cc717823e6ec77d5a10b098c4adf75a9aafd9ac9a3da52e1fc9  base-matrix.out
d52e1eb47aa8ce8bb32abe61fdaf119f5b47278c2a7c11a1b7a46e2e794d505f  probe-layout.out
e79bc0391d7c4207b7bcbd4d0942c22ed65b793f820233150c62958823464199  probe3.out
ab5463d518e2c336b9887967ce2ccb251cc26aeb2774fc84bb8e3c4311a706b4  probe4.out
9095af5d4f62907daaf4855983619657f28158f2f15eced3ef89936100183862  probe5.out
633dad95dbbc7ac3e24ccb98b39791e9daec661ade91f180032c947ee6bd3c12  probe6.out
e4782033212b76df27488b4430ff378f8779c8640e65adbfd0c91b1a5c0cc78f  probe7.out
```

### Tooling

Nothing installed or upgraded: the lane used only `git 2.56.0` (pre-installed)
and `python3` (pre-installed). No package transaction, no host service, no
config mutation.
