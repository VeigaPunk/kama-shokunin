# CodeGitBoundary — production subprocess callsites / GIT_ISOLATION falsification (kama round 24, pinned `2e254a17`)

**Verdict: HOLDS for the assigned slice.** The r24 candidate (`2e254a1763a9c08aa07fc53081287f506c447d84`)
does not weaken the global Git isolation contract and does not weaken the 20-second deadline at
**any** production subprocess callsite of the audited artifact
`tools/report-landing-audit.py` (`ea51bc35…`). Every git invocation in that file — including the
four new round-24 callsites — is issued through the single `git()` wrapper that carries
`GIT_ISOLATION` (`--no-replace-objects`, `--no-lazy-fetch`, `i18n.logOutputEncoding=UTF-8`,
`log.follow=false`, `log.showRoot=true`, `log.showSignature=false`, `log.mailmap=false`) plus the
scrubbed environment and `timeout=GIT_TIMEOUT` (20 s). The isolation tuple and the deadline are
**byte-identical** to the r23 base `0df800e8…`. No transport, program or signature channel was
introduced; the new walk is transport-inert even with the flag removed.

Five findings are reported below. **None of them falsifies the round-24 claim.** F1–F3 are
*inherited* weaknesses in **other** `tools/` programs that the round-24 delta did not touch (the
delta under `tools/` is exactly one file: `tools/report-landing-audit.py`); they are recorded so
the "global" wording of the isolation contract is not read as covering the whole `tools/` tree.
F4 is an inherited deviation with no observed impact; F5 is a mutation-coverage gap on the new
argument vector. F6–F9 are informational.

Lane: leaf member (no subagent dispatch). Read-only production; no suite was run.

---

## 1. Pinned base (observed)

| item | value |
|---|---|
| clone | `/fast/scratch/hyaku/kama-r24/falsify/CodeGitBoundary/repo` (`git clone --no-hardlinks` from `/home/vgpnk/Projects/shokunin/kama-shokunin`, detached) |
| HEAD | `2e254a1763a9c08aa07fc53081287f506c447d84` (`git status --porcelain` empty) |
| base for comparison | `0df800e896f6bce285a81e794ad4ae1d1e6c3a71` (r23 frozen auditor) |
| `tools/report-landing-audit.py` @ head | sha256 `ea51bc35b71ac09f4c233e21a16be49af555e1333004a0fe166234de79edd220` (matches the assignment's "source tool ea51bc35…") |
| `tools/report-landing-audit.py` @ base | sha256 `da5041a8191e0e6ec385adc7c659ddc7544a835aff65dd45b34de623c5765af1` (equals the oracle snapshot's `frozen_auditor_sha256`) |
| round-24 delta under `tools/` | `tools/report-landing-audit.py` **only** (verified by `git diff --stat 0df800e8… 2e254a17… -- tools/`) |
| environment | git 2.56.0, python3 3.14.x; `TMPDIR=/fast/scratch/hyaku/kama-r24/falsify/CodeGitBoundary/tmp`; **no tool installed or updated**; no network, transport or execution payload used |

Production was not modified. Only append-only artifacts under
`.ufo/waves/round-24/falsify/{advice,out}/CodeGitBoundary/` were written. `production/.jj/index`,
the fleet, sibling lanes, operator config, routing, services and real object stores were untouched.
PM08 was **not** executed (static only).

---

## 2. Attack surface — every production subprocess callsite of the audited artifact

`tools/report-landing-audit.py` contains **exactly one** `subprocess` use
(`grep -n "subprocess\."` → lines 162 and 166 only; no `Popen`). Everything else is `git()`.

```python
# tools/report-landing-audit.py:138-141  (identical at base 0df800e8…, lines 93-96)
GIT_ISOLATION = ("--no-replace-objects", "--no-lazy-fetch",
                 "-c", "i18n.logOutputEncoding=UTF-8",
                 "-c", "log.follow=false", "-c", "log.showRoot=true",
                 "-c", "log.showSignature=false", "-c", "log.mailmap=false")

# :144-150
def git_env(**extra):
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1", **extra)
    return env

# :153
GIT_TIMEOUT = 20

# :156-165
def git(repo, *args, stdin=None, env=None, errors="strict"):
    proc = subprocess.run(["git", *GIT_ISOLATION, "-C", str(repo), *args],
                          input=None if stdin is None else stdin.encode(),
                          capture_output=True, env=env or git_env(),
                          timeout=GIT_TIMEOUT)
```

Consequences that were checked one by one:

* **argv shape** — the isolation flags are *global* options and precede the subcommand, as
  `git(1)` requires (`GIT_ISOLATION` is spliced in immediately after `"git"`, before `-C`).
  `-C <repo>` is therefore always applied to the same repository the caller names, and the
  caller's own `-c` override (`-c core.commitGraph=false`, `:672`) is still a global option
  (it precedes `rev-list`).
* **env** — every `GIT_*` variable of the parent is dropped; `GIT_CONFIG_GLOBAL=/dev/null` and
  `GIT_CONFIG_NOSYSTEM=1` remove user/system config; `GIT_OPTIONAL_LOCKS`/`GIT_TERMINAL_PROMPT`
  are not set, which is inherited r23 behaviour (neither is a transport or program channel).
* **deadline** — `timeout=GIT_TIMEOUT` (20 s) on the single subprocess site; `TimeoutExpired` is
  converted into `EvalError` (`:166-170`), i.e. a hang is *never* a verdict, and `OSError`
  likewise (`:171-172`). A non-zero git exit is also `EvalError` (`:173-175`).

### The four round-24 git callsites (new code)

| # | callsite | command | isolation | deadline |
|---|---|---|---|---|
| 1 | `present_roots` `:635-649` | `git cat-file --batch-all-objects --batch-check=%(objectname) %(objecttype)` | via `git()` | 20 s |
| 2 | `missing_reachable` walk 1 `:672-673` | `git -c core.commitGraph=false rev-list --objects --missing=print --no-object-names --stdin` | via `git()` | 20 s |
| 3 | `missing_reachable` walk 2 `:678` | same **plus** `--filter=blob:none` | via `git()` | 20 s |
| 4 | `root_tree` `:266-275` | `git log -1 --format=%T <root>` | via `git()` | 20 s |
| (+5) | `lookup` second probe `:242-250` | `git cat-file --batch-check` with `^{}` peel | via `git()` | 20 s |

None of them uses `subprocess` directly; none of them can therefore escape `GIT_ISOLATION`,
`git_env()` or the deadline.

### Round-24 delta in the *negative* direction (a strict improvement)

`check_history_repo` in the r23 base read the repository-local config
(`git config --null --list`, base line 458) to classify promisor metadata. The round-24
candidate **removed that read**: in the pinned head the only `git config` call left is inside the
self-test (`:1187`, writing fixture config). A repo-local config read is an `include.path` /
FIFO channel; one such read fewer is strictly less repo-local exposure than r23.
`grep -n "promisor|partialclone|partial clone"` in the pinned head finds only doc text
(`:58-59`, `:134`, `:619`, `:660`) and the self-test (`:1176-1195`) — **no production read of
promisor metadata exists**, so no metadata channel can influence a verdict.

---

## 3. Exact commands and exit codes (all offline, benign fixtures)

```
# A) identity of the isolation tuple and the deadline, base vs head
git -C …/repo show 0df800e8…:tools/report-landing-audit.py | grep -n "GIT_ISOLATION = |…"
git -C …/repo grep -n  "GIT_ISOLATION = |…" tools/report-landing-audit.py
diff <(base lines) <(head lines)
# exit 1 — the only differing lines are two docstring sentences; every code line is identical
#   A-isolation-identity.txt

# B) callsite enumeration (static)
grep -n "subprocess\." tools/report-landing-audit.py        # → 162, 166 only
grep -n '"config"' tools/report-landing-audit.py            # → 1187 only (self-test)
grep -n "promisor\|partialclone" tools/report-landing-audit.py
# exit 0 — B-callsites.txt

# C) promisor-marked fixture, production isolation vs control (no --no-lazy-fetch)
git init -q -b master . ; …commit… ; rm -f .git/objects/<xx>/<rest>   # one missing blob
git config remote.origin.promisor true ; git config extensions.partialclone origin
git config remote.origin.url /nonexistent-absent-remote.git
git --no-replace-objects --no-lazy-fetch -c … -C . cat-file blob <oid>   # C1 → exit 128, "bad file"
git --no-replace-objects              -C . cat-file blob <oid>          # C2 → exit 128, 3× remote attempt
git --no-replace-objects --no-lazy-fetch -c … -C . show HEAD:b.txt      # C3 → exit 128, "bad object"
git --no-replace-objects              -C . show HEAD:b.txt             # C4 → exit 128, 3× remote attempt
git --no-replace-objects --no-lazy-fetch -c … -C . log -1 --format=%T HEAD  # C5 → exit 0
git --no-replace-objects --no-lazy-fetch -c … -C . ls-tree HEAD -- b.txt  # C6 → exit 0
… | git <isolation> -C . -c core.commitGraph=false rev-list --objects --missing=print \
      --no-object-names --stdin                                         # C7 → exit 0, "?f719efd4…"
… | git <control>    -C . -c core.commitGraph=false rev-list --objects --missing=print \
      --no-object-names --stdin                                         # C8 → exit 0, byte-identical output
… | git <isolation> … --filter=blob:none --stdin                        # C9 → exit 0, blob absent
# exit 0 overall — C-promisor-isolation-ab.txt

# D) scale vs the 20 s deadline on the pinned repository
git cat-file --batch-all-objects --batch-check="%(objectname) %(objecttype)" | wc -l   # 7355 objects
… | awk '$2=="commit"||$2=="tree"||$2=="tag"' | wc -l                                # 2348 roots
… | git <isolation> … rev-list --objects --missing=print --no-object-names --stdin    # real 0m0.011s
# exit 0 — D-scale-deadline.txt

# E) git floor for every flag the r24 candidate introduces
git --version                                  # git version 2.56.0
git rev-list --objects --missing=print --stdin </dev/null    # accepted by the host
# release-note anchors (plain HTTPS reads, no payload):
#   2.45.0 "git --no-lazy-fetch cmd allows to run cmd while disabling lazy fetching …"
#   2.45.0 "git rev-list --missing=print has learned to optionally take --allow-missing-tips"
#   2.23.0 "git rev-list --objects" learned the "--no-object-names" option
#   2.20.0 "The rev-list --filter feature learned to exclude all trees via …"
# exit 0 — E-git-floor.txt

# F) isolation/timeout audit of the other tools/ programs
grep -n "subprocess.run\|subprocess.Popen\|timeout=\|GIT_\|\"git\"" tools/sources-append-only.py \
     tools/citation-provenance.py tools/error-verdict-census.py
# exit 0 — F-other-tools.txt

# G) mutant applicability of the isolation elements (static, no grid run)
python3 -c "count each isolation-mutant literal in the pinned head"
# M01,M02,M03,M04,M05,M06,M07,M31 → count = 1 each
# exit 0
```

---

## 4. Findings

### F0 — NO DEFECT (holds): the global isolation contract and the 20 s deadline are preserved at every production callsite of the audited artifact

* `GIT_ISOLATION` (`:138-141`) and `GIT_TIMEOUT = 20` (`:153`) are **byte-identical** to the r23
  base (`A-isolation-identity.txt`: the only differing lines are two docstring sentences).
* All seven isolation elements are still present and still ordered as *global* options:
  `--no-replace-objects`, `--no-lazy-fetch`, `-c i18n.logOutputEncoding=UTF-8`,
  `-c log.follow=false`, `-c log.showRoot=true`, `-c log.showSignature=false`,
  `-c log.mailmap=false`. The log/signature/mailmap quartet still rides on every call, including
  the new `git log -1 --format=%T` (`:274`) and `git log -z --format=…%an…` (`:291`).
* The deadline rides on the new callsites too: the single `subprocess.run` site (`:162-165`)
  carries `timeout=GIT_TIMEOUT`, so `cat-file --batch-all-objects`, both `rev-list` walks and
  `log -1` are each bounded at 20 s and each timeout becomes `EvalError` → exit 2, never a
  verdict.
* **Empirical proof that the no-lazy-fetch element is load-bearing and preserved** (C1–C4): in a
  promisor-marked store with one missing blob, the production flag set makes the read fail
  *locally* (`bad file` / `bad object`, exit 128, **no transport**), while the same command
  without `--no-lazy-fetch` performs **three** transport attempts against the configured remote
  (`'/nonexistent-absent-remote.git' does not appear to be a git repository`). A promisor remote
  that *is* reachable would therefore have been materialised by the control run — i.e. without
  the flag the auditor's own reads would silently destroy the "unavailable evidence" premise.
  This is the same mechanism the sibling lane `KamaR23-2.CaseFleetBlobless` observed from the
  fixture side (F1 in that report): the premise is held by the flag, not by the fixture.
* **The new walk adds no transport channel** (C7 vs C8): `rev-list --objects --missing=print`
  produces byte-identical output with and without `--no-lazy-fetch` and never contacts the
  remote — `--missing=print` already suppresses the on-demand fetch. The isolation flag is
  therefore *belt and braces* on that callsite, and removing it would not open a transport.
* **No replace-ref, signature or mailmap channel is opened by the new code**: the new callsites
  are `cat-file --batch-all-objects`, `cat-file --batch-check`, `rev-list --objects` and
  `log -1 --format=%T`; none of them resolves a replace ref (blocked by `--no-replace-objects`),
  none displays a signature (`log.showSignature=false`), none rewrites an author by mailmap
  (`log.mailmap=false`), and none reads the worktree `.mailmap`.
* **The Git floor is not raised** (E): the candidate introduces `--missing=print` (≤ 2.22),
  `--filter=blob:none` (≤ 2.20), `--no-object-names` (= 2.23) and `-c core.commitGraph=false`;
  all are ≤ 2.45, and the forbidden `--missing=print-info` / `--missing-only` are **not** used.
  The inherited `git >= 2.45` prerequisite (still open at L0, because `--no-lazy-fetch` was
  introduced in 2.45) is unchanged by round 24.
* **Mutation applicability survives the edit** (G): the eight isolation/deadline mutants of
  `tests/report-audit/isolation-mutants.py` (M01–M07 flags, M31 deadline) each match the pinned
  head **exactly once**, so the round-24 edit did not silently break the isolation mutation
  contract (no "literal no longer matches" → whole-run could-not-evaluate).
* **Scale vs the deadline** (D): the pinned repository holds 7 355 objects and 2 348
  commit/tree/tag roots; the full production walk (roots + `rev-list --objects --missing=print`)
  takes ~11 ms, so the 20 s bound is not binding at this scale (see F7 for the extrapolation).

### F1 — MEDIUM (inherited, outside the r24 delta): `tools/sources-append-only.py` has an unbounded, unisolated git read

`tools/sources-append-only.py:287-290`:

```python
proc = subprocess.run(
    ["git", "-C", repo, "show", f"{rev}:{path}"],
    capture_output=True,
)
```

* **no timeout at all** → a FIFO at `.git/config`, an `include.path` target, a `.git/shallow`
  file or a ref file blocks the read forever (the exact hazard the auditor's `git()` documents
  at `:167-169`);
* **no `--no-lazy-fetch` / `--no-replace-objects`** → in a promisor store the read can perform a
  transport, and replace refs can substitute the bytes;
* **no env scrub** → an inherited `GIT_DIR`/`GIT_OBJECT_DIRECTORY`/`GIT_ALTERNATE_OBJECT_DIRECTORIES`
  redirects the read to another store.

Not introduced by round 24 (`git diff 0df800e8… 2e254a17… -- tools/` touches only
`tools/report-landing-audit.py`), and this tool is not part of the round-24 measurement path.
Minimal correction (not applied; production is read-only for this lane): route the read through
the auditor's `git()`-equivalent — `["git", "--no-replace-objects", "--no-lazy-fetch", "-c",
"log.showSignature=false", "-c", "log.mailmap=false", "-C", repo, "show", …]`, `env=` a
`GIT_*`-scrubbed dict with `GIT_CONFIG_GLOBAL=os.devnull`/`GIT_CONFIG_NOSYSTEM=1`, and
`timeout=20`.

### F2 — MEDIUM (inherited, outside the r24 delta): `tools/citation-provenance.py` — isolation-free read plus two un-timed calls

* `:41-44` `git -C <lane> cat-file blob <rev>:<path>` — has `timeout=60` but **no isolation
  flags and no env scrub**: replace refs are honoured, a promisor store may lazy-fetch, and an
  inherited `GIT_DIR`/`GIT_OBJECT_DIRECTORY` redirects the read.
* `:72-73` `git -C <lane> rev-parse --git-dir` — **no timeout** (unbounded).
* `:105-108` `git -C <lane> merge-base --is-ancestor <rev> origin/master` — **no timeout** and
  no isolation; this call also names a remote-tracking ref, so it is the one place in `tools/`
  where the *remote* is referenced by name (it does not contact it, but it does depend on the
  local ref).

Same minimal correction as F1. Not round-24-introduced.

### F3 — LOW (inherited, outside the r24 delta): `tools/error-verdict-census.py` — env-scrubbed but not flag-isolated

`:140-146` `git -C <lane> show <rev>:<path>` runs with `env_for(...)` (`:66-72`: fresh `PATH`,
`HOME`, `TMPDIR`, `GIT_CONFIG_NOSYSTEM=1`, `GIT_CONFIG_GLOBAL=os.devnull`,
`GIT_OPTIONAL_LOCKS=0`) and `timeout=60`, but **without** `--no-replace-objects` and
`--no-lazy-fetch`: a replace ref can substitute the frozen source bytes, and a promisor store can
lazy-fetch the blob it is trying to compare. This tool pins `FROZEN_SOURCE_SHA256`, so a
substituted blob is caught by digest — but only after the substituted read happened. Not
round-24-introduced.

### F4 — LOW (inherited): the auditor's `git()` does not set `stdin=DEVNULL` for calls that pass no input

`subprocess.run(..., input=None)` leaves the child's stdin **inherited** from the parent. The
round-12/13 reference method explicitly used `stdin=subprocess.DEVNULL` (see the round-12
`fidelity.py` / round-13 `measure.py` references in
`.ufo/waves/round-12/advice/AttackSourceAnchor.md:94-96` and
`.ufo/waves/round-13/advice/Measure.md:40-41`). *No current callsite reads stdin*: of the git
commands used by the auditor, only `cat-file --batch-check` (`:212`, `:242`) and
`rev-list --stdin` (`:672`) consume stdin, and both pass `stdin=`/`input=`. So there is **no
observed impact** and no verdict-affecting path. Minimal correction (one line, not applied):
`stdin=subprocess.DEVNULL if stdin is None else None` — or simply
`stdin=subprocess.DEVNULL` plus `input=` as today. Inherited from r23, unchanged by round 24.

### F5 — LOW (coverage gap, not a source defect): no mutant pins the new argument vector

`tests/report-audit/isolation-mutants.py` still pins the seven isolation elements and the
deadline (F0), but nothing pins the **new** callsite's argv (`-c core.commitGraph=false`,
`--missing=print`, `--no-object-names`, `--filter=blob:none`). The isolation-relevant
consequence: `--filter=blob:none` is what keeps missing **blobs** out of the "opaque" set; if it
were dropped, every blob hole would be treated as an opaque (name-hiding) hole and *any*
unresolved citation in such a store would refuse with exit 2 instead of reporting a proved
absence — i.e. the flag set of the new walk is behaviour-determining but unpinned. The
semantics owner for that effect is the opaque-diagnosis seat; I record the boundary fact only
(no mutation was run: "no full grid").

### F6 — INFORMATIONAL: the new walk sees only objects *referenced* by present objects

`missing_reachable` (`:651-677`) roots the walk at every present commit/tree/tag
(`present_roots`, `:635-649`). A missing object that **no present object references** is
invisible to it: in a fixture where the *child* commit was deleted from a promisor-marked store,
the deleted commit did **not** appear as `?oid` in either walk (its tree remained present, but
nothing present pointed at the commit). Same for a dangling tag whose target is missing (that one
*is* visible, because the tag object is present and references it — verified: `?b34bb3…`).
This is a property of the diagnosis scope, not of the isolation/deadline boundary, and it is
reported for the opaque-diagnosis lane rather than as a defect here.

### F7 — INFORMATIONAL: the 20 s deadline is a per-call bound that can turn a proved absence into "could not evaluate" at scale

Each git call is bounded at 20 s (`:153`, `:165`), and `TimeoutExpired` becomes `EvalError`
(`:166-170`) → the audit refuses (exit 2) instead of reporting a verdict. The new walk is
O(objects in the store): at the pinned repository's scale (7 355 objects / 2 348 roots) it takes
~11 ms (D). On a store orders of magnitude larger the bound could bite, converting a *proved
absence* into a *could-not-evaluate* — a conservative direction (never a false verdict), and the
inherited r23 semantics, not a round-24 regression. Recorded so the 20 s number is read as a
deliberate ceiling rather than as "fast enough everywhere".

### F8 — INFORMATIONAL (harness, not production): the grid's generic git helper is fetch-capable and un-timed

`tests/report-audit/promisor-grid.py:99-104` — the helper `git()` runs
`subprocess.run(["git", "-C", str(repo), *args], input=data, capture_output=True, env=env(...))`
with **no timeout and no `--no-lazy-fetch`**; only `git_nofetch` (`:109-111`) and the three
probes that use it (`missing_objects` `:293-298`, `object_exists` `:300-307`,
`object_inventory` `:310-314`) are safe. The sibling lane `KamaR23-2.CaseFleetBlobless` reported
the concrete consequence: on the blobless fixture (`remote.origin.url` still pointing at the
reachable local `file://` origin) one fetch-capable probe materialises the missing report blob
and flips the correct exit 2 into a false exit 0 "clean". This is the measurement instrument, not
the audited artifact; the auditor's own reads are protected by `GIT_ISOLATION` (F0). No grid
change proposed or made here.

### F9 — INFORMATIONAL: repository-local config is still honoured (explicitly disclaimed, and one read was removed)

`git_env()` (`:144-150`) scrubs `GIT_*` and user/system config but not **repository-local**
config; the docstring states this (`:145-147`). Repo-local channels that could matter for the
audited reads are: `core.sshCommand` / `remote.*.promisor` (transport — unreachable because
`--no-lazy-fetch` blocks the on-demand fetch), `gpg.program` (signature — irrelevant because no
call displays a signature), `core.commitGraph` (mitigated: the new walk passes
`-c core.commitGraph=false`, `:672`), `diff.external` / `diff.<driver>.command` (only relevant to
a diff-producing call: `report_cutoff` `:316-323` uses `git log --diff-filter=A --format=%at --
<path>`, which is an r23 callsite, unchanged by round 24) — the external-diff driver is only
consulted with `--ext-diff`/`GIT_EXTERNAL_DIFF` **[INFERENCE]**: no local `git-config` manual
page was installed on this host (`/usr/share/man/man5/git-config.5.gz` absent), so this rests on
the documented semantics of `diff.external`, not on an executed probe. Round 24 *reduced* this
exposure by one read (the removed `git config --null --list`, see §2).

---

## 5. Residual risk and verification gaps

* **No full grid, no auditor self-test, no mutation run, no historical gate** — by assignment
  ("do not run a full grid"; this seat's bounded measurement is static source checking plus
  benign offline fixtures). The mutant-applicability result (F0) is a *static* count of literal
  occurrences, **not** a run of `tests/report-audit/isolation-mutants.py`; whether each mutant is
  still *killed* by the grid is unverified here.
* The A/B in §3 C uses a **synthetic promisor-marked store** whose remote is an unreachable
  local path. It proves *that a transport would be attempted* without `--no-lazy-fetch`; it does
  not exercise a reachable remote, a `file://` transport, or the sibling lane's "materialised
  blob ⇒ false clean" flip (that observation is the sibling lane's, cited here as corroboration
  only).
* The Git-floor conclusion rests on upstream release notes read over plain HTTPS
  (2.20.0/2.22.0/2.23.0/2.45.0). I did not verify the flags against an actual 2.45 binary (only
  the host's 2.56.0 accepts them); the inherited `git >= 2.45` prerequisite therefore remains
  **open at L0** and is not discharged by this seat.
* `diff.external` behaviour (F9) is **[INFERENCE]**, not observed; no program was configured or
  executed to probe it (the assignment forbids program probes).
* The deadline extrapolation in F7 is arithmetic from one measured scale (7 355 objects), not a
  measurement on a large store.
* The three `tools/` findings (F1–F3) were read statically; no program from those tools was
  executed, and their behaviour under a promisor store was not measured.

---

## 6. Files written

Production (append-only; nothing else in the lane was touched):

* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/advice/CodeGitBoundary.md` — this report
* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/out/CodeGitBoundary/A-isolation-identity.txt`
  — base-vs-head isolation/deadline identity diff (exit 1: only docstring lines differ)
* `…/out/CodeGitBoundary/B-callsites.txt` — subprocess/callsite enumeration (single `subprocess.run`; promisor/config reads)
* `…/out/CodeGitBoundary/C-promisor-isolation-ab.txt` — C1–C9 production-isolation vs control on a promisor-marked fixture
* `…/out/CodeGitBoundary/D-scale-deadline.txt` — object/root counts and the production walk's wall time on the pinned repo
* `…/out/CodeGitBoundary/E-git-floor.txt` — host git version and the release-note anchors for every flag the candidate introduces
* `…/out/CodeGitBoundary/F-other-tools.txt` — isolation/timeout audit of the other `tools/` programs (F1–F3)

Scratch (outside the repo, heavy/temporary):
`/fast/scratch/hyaku/kama-r24/falsify/CodeGitBoundary/` — `repo/` (`--no-hardlinks` clone, detached at `2e254a17…`),
`tmp/` (benign offline fixtures `fx/`, `pfx/`, `pfx2/`, `tagfx/`, `mcommit/`, `ev-promisor/`), `evidence.sh`.

**No tool was installed or updated** in this seat (no pacman/uv/cargo/npm action; the assignment
forbade system changes, and none was needed: git 2.56.0 and python3 were already present).

---

Report: .ufo/waves/round-24/falsify/advice/CodeGitBoundary.md
