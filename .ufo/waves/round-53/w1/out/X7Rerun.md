# X7Rerun — round 53 C2 (calibration) independent measurement, lane kama

**Verdict:** C2 replicates exactly and independently — `met=False` at the round-53 base (`4229ea1b`, 16 undisclosed) and `met=True` at the build (`c22602bd`, 14 disclosed, `dropped=0`), body-identical to `measured/c2-build.out` and `controls/base.c2.out`; the fleet revision (`bcc9bbd2` / `ee9f7341` / `d2a6c59`) changes nothing at either tip. One instrument blind spot measured and priced (F1, upstream class re-derives reachability only), current ledger data verified correct, patch proposed in my out dir. No defect found in the measured claim.

## 1. Setup

```
S=/fast/scratch/hyaku/kama-r53/X7Rerun; export TMPDIR="$S"
git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin $S/lane   # exit 0
git -C $S/lane rev-parse --show-toplevel                                  # /fast/scratch/hyaku/kama-r53/X7Rerun/lane
```

Frozen instrument identity (checked, not assumed): the preregistration's C2 `counter_sha256` is
`1afb8b9d32fd0706d0625a4ea70270890039f93fc32635c28b12fa71b13e3080`, and `tools/round53-cited-path-check.py`
hashes to exactly that at `d01b2b6d`, at `c22602bd` and in the current worktree — the counter that
produced the build receipt is the frozen counter, unedited (`git show <rev>:tools/round53-cited-path-check.py | sha256sum`).
Counters were read, never modified; the repo was read-only (`git -C $S/lane status --porcelain` = 0 lines after all runs).

## 2. Measured — five runs, `--repo $S/lane`, `--out` into this directory

| receipt (`c2-*.out`) | tip | fleet rev | exit | counts |
|---|---|---|---|---|
| `c2-base-head` | 4229ea1b | d2a6c59a | **1** | fixture=1 lane=0 scenarios=8/8 cited=679 unresolved=16 disclosed=0 undisclosed=16 bad=0 stale=0 dropped=0 met=False |
| `c2-base-pinned` | 4229ea1b | ee9f7341 | **1** | same as above (fleet=ee9f7341) |
| `c2-build-head` | c22602bd | d2a6c59a | **0** | fixture=1 lane=1 scenarios=8/8 cited=682 unresolved=14 disclosed=14 undisclosed=0 bad=0 stale=0 dropped=0 met=True |
| `c2-build-pinned` | c22602bd | ee9f7341 | **0** | same as above (fleet=ee9f7341) |
| `c2-build-fleet-at-base-control` | c22602bd | bcc9bbd2 | **0** | same as above (fleet=bcc9bbd2) |

Exact exit codes are `exit=` lines inside the matching `c2-*.log` (the counter's own `--out` payload has no
exit line; I appended it in the `.log`, alongside the driver command line). Commands, verbatim:

```
python3 tools/round53-cited-path-check.py --repo $S/lane --tip <tip> --fleet /home/vgpnk/Projects/shokunin \
  --fleet-rev <HEAD|ee9f7341…|bcc9bbd2…> --scratch $S/sc-<name> --out <this dir>/c2-<name>.out
```

## 3. Equality with the frozen artifacts (`measured/c2-build.out`, `controls/base.c2.out`)

```
diff <(grep -v -E '^(\$ |tip=|exit=)' measured/c2-build.out)   <(grep -v -E '^(\$ |tip=|exit=)' c2-build-pinned.out)   # identical
diff <(grep -v -E '^(\$ |tip=|exit=)' controls/base.c2.out)    <(grep -v -E '^(\$ |tip=|exit=)' c2-base-pinned.out)    # identical
```

The build receipt is byte-identical to my rerun after dropping the driver's `$ …` line and the exit line; the base
control differs only in the `fleet=` field of its `tip=` line (it was recorded at fleet `bcc9bbd2`, the build at
`ee9f7341`) — and I removed that variable by running both tips at `bcc9bbd2` too (row 5 above, and base at both
`d2a6c59`/`ee9f7341`). All 14 build `detail:` lines and all 16 base `detail:` lines are identical, including the
per-token undisclosed list. Note that `.ufo/waves/round-53/measured/c2-build.out` and `controls/base.c2.out` are
present in the worktree/HEAD (`bc8e6e7f`, "wave kama-r53-w1 spec … and build receipts") but **not** in `c22602bd`
itself (`git cat-file -e c22602bd:.ufo/waves/round-53/measured/c2-build.out` → fatal, absent) — the receipts are
the wave's publication, not part of the measured commit.

## 4. Does the fleet revision change anything? No.

Same counts and same detail lines at all three revs, at both tips:

```
diff <(grep -v '^tip=' c2-build-head.out)                <(grep -v '^tip=' c2-build-pinned.out)                 # no delta
diff <(grep -v '^tip=' c2-build-fleet-at-base-control.out) <(grep -v '^tip=' c2-build-pinned.out)               # no delta
diff <(grep -v '^tip=' c2-base-head.out)                 <(grep -v '^tip=' c2-base-pinned.out)                   # no delta
```

Structural reason (measured, not inferred):

- The fleet moved 7 commits from `bcc9bbd2` (base-control) through `ee9f7341` (build receipt) to `d2a6c59a` (today's
  HEAD), but **none of them touches a resolution root**: `git -C /home/vgpnk/Projects/shokunin diff --name-only
  bcc9bbd2 d2a6c59a -- scripts templates` → 0 paths (5 paths changed overall).
- The only *fleet-root* citation that is unresolved at the base is SKILL.md `scripts/local-helper.mjs`; it is absent
  from the fleet tree at all three revs, absent from disk under the fleet root, and absent from all of the fleet's
  history (`git log --all --oneline -- scripts/local-helper.mjs` → 0 commits). Its status is therefore
  fleet-rev-independent, and the build removes it as a citation by in-place correction anyway (§5, fixed/113).
- Everything else unresolved is lane-root or a lane top-level file; the only rev-dependent reads for those are the
  lane tip and `git log --all` (rev-independent).

So a future C2 run at a newer fleet HEAD is not expected to move the verdict *unless* a fleet commit adds or removes a
path under `scripts/` or `templates/` matching a cited token — the counter does record the rev it used (`fleet=` in
the `tip=` line), which is the right hedge, but see R2.

## 5. Ledger rows re-derived independently

`registry/cited-path-corrections.tsv` at `c22602bd`: 15 data rows = 7 `never`, 1 `deleted`, 1 `untracked`,
5 `upstream`, 1 `fixed`; 14 of them disclose (the `fixed` row is not a disclosure), matching `disclosed=14`.

- **never (7)** — `git log --all --name-only -- <token>` on lane *and* fleet returns 0 hits for each:
  `.ufo/waves/round-14/frozen/before/tools/kama-ollama-evidence.py`,
  `.ufo/waves/round-29/w1/out/ConfirmM01..11/`, `.ufo/waves/round-31/c2/c2-tip.json`,
  `.ufo/waves/round-999/count-c999.py`, `.ufo/waves/round-38/w1/out/FetchS352/`,
  `.ufo/waves/round-38/w1/out/ExecTagInventory/api-status.txt`, `.ufo/waves/round-40/c2/base.out`.
  (`{base,after}.out` expands to `after.out`, which does exist at the build — `.ufo/waves/round-40/c2/after.out` —
  so only `base.out` is unresolved. Correct.)
- **deleted (1)** — `.ufo/waves/round-31/sources/llama.cpp-704366d/utils.hpp`: present at `9874e455^`
  (`git cat-file -e` exit 0), absent at `9874e455` (exit 128). Class re-derives.
- **untracked (1)** — `.ufo/watchdog.log`: 156,988 bytes on disk at the fleet root, `git cat-file -e
  HEAD:.ufo/watchdog.log` → *"exists on disk, but not in HEAD"*, absent from the fleet tree. Class re-derives.
  (The fleet does track 70 *nested* `watchdog.log` paths; the root one is not among them.)
- **upstream (5)** — fetched all five URLs: HTTP 200, and the bodies' sha256 **equal SKILL.md's own pins**
  (verified independently): `server-common.cpp b4f4aae7…d442`, `server-schema.cpp 1f9d7b73…4050`,
  `server-task.cpp 4c3f413b…3495`, `server-chat.cpp 91f48e09…263e`; the SCORECARD row's URL is the same file as
  SKILL's schema pin. The ledger's notes ("re-fetched 2026-10-27, equal to SKILL.md's pin") are true.
- **fixed (1)** — `tests/report-audit/…` → `tests/report-audit/`: base SKILL.md **line 895** reads
  `` `tests/report-audit/…` ``; build line 895 reads `` `tests/report-audit/` ``, which matches 5 files under
  `tests/report-audit/` at the build. The second in-place correction is **line 113** (`scripts/local-helper.mjs` →
  `~/Projects/ufo-fsd-alpha/scripts/local-helper.mjs`; that file exists, 15,065 bytes), with no ledger row because an
  absolute path is not a lane citation. Both are the only two hunks of the build's SKILL.md diff (`git diff
  4229ea1b c22602bd -- SKILL.md` = 2 deletions / 2 insertions), so the corrections are minimal and local.

## 6. Independent second parser (`indep-c2-probe.py`, written from the counter docstring)

Not a substitute for the frozen counter — a replication of its *survey* on a second implementation:

| revision | occurrences | unique (surface, path) pairs | unresolved pairs |
|---|---|---|---|
| build `c22602bd` | 1103 | 668 | **14** (same 14 tokens) |
| base `4229ea1b` | 1096 | 665 | **16** (same 16 tokens) |

The unresolved sets match the counter token-for-token, including the beyond-EOF cases (`ConfirmM01..11/`,
duplicate citations of `c2-tip.json` at L1635/L1732 and of `round-40/c2/base.out` at L2184/L2228, and the
round-53 section's own `tools/server/server-schema.cpp` at L3029). `cited` differs only in the **key**: the counter
counts `(surface, raw span including line anchor)`, so 14 anchor-variant keys are counted separately at both tips
(682−668 = 14, 679−665 = 14) and **both metrics move +3 base→build**. The +3 is honest: my own SCORECARD core-token
set is 438 at base and 442 at build, **dropped=0**, added exactly the four tokens of the appended block
(`.ufo/waves/round-53/controls/base.c2.out`, `SHONEN.md`, `registry/cited-path-corrections.tsv`,
`tools/round53-cited-path-check.py`).

## 7. Mutation probes — the counter discriminates at the measured revision

The built-in `fixture` leg only tests a constructed scratch repo; these five probes re-run the counter on fixture
clones of the **build** with one data mutation each (clone → `git checkout -B fx c22602bd` → one commit with
`-c user.name=fx -c user.email=fx@invalid`, toplevel asserted = fixture dir), `--fleet-rev ee9f7341`:

| probe | mutation | result | exit |
|---|---|---|---|
| `probe-a-row-deleted` | delete the `round-999/count-c999.py` ledger row | disclosed 13, **undisclosed=1**, met=False | 1 |
| `probe-b-stale-row` | append a row for a cited, resolving token | **stale=1**, met=False | 1 |
| `probe-c-dropped-citation` | delete SCORECARD line 491 | **dropped=1**, stale=1, met=False | 1 |
| `probe-d-forged-class` | `never` → forged `deleted <base commit>` | **bad=1**, undisclosed=1, met=False | 1 |
| `probe-e-upstream-ref-master` | upstream URL ref `704366d76…` → `master` | **met=True** (see F1) | 0 |

Four of five legs (disclosure, stale, dropped, class re-derivation) fire exactly and only on their own mutation; the
counter is a live instrument at the measured commit, not just a fixture simulator.

## 8. Findings

**F1 (limitation, not a defect against the frozen predicate; medium risk for future rounds).** `tools/round53-cited-path-check.py:300-311`
re-derives `upstream` by *HTTP 200 on a URL that ends in the token*, and never compares the body to a pin. Probe E
demonstrates the gap: pointing `server-task.cpp`'s evidence at `.../master/...` (body sha256
`d7901c9609a6fe8c859a3777d45a37148e335bb73984313ba08a339d558382ef`) still yields `met=True`, although it is a
different file from the pinned snapshot (`4c3f413b…3495`). Today's data is sound — I fetched all five URLs and the
digests equal SKILL.md's pins (§5) — so this is a blind spot for the *next* ledger row, not for this receipt. The
docstring defines the class as "the URL answers HTTP 200 when fetched here", so the frozen predicate is met as
written; do not change the counter in place. Proposed patch (extension, to be frozen in a later round):
`proposed-upstream-digest-check.diff` — keep the row's `note`, read the body once, and when the note carries a full
`sha256 <64 hex>` compare it (`import hashlib`). Caveat for that upgrade: the current upstream notes abbreviate the
digest (`sha256 1f9d7b73…`), so they would have to carry the full 64-hex value to activate the check.

**R2 (operational).** `--fleet-rev` defaults to the fleet's `HEAD`, so a C2 receipt is only reproducible with the fleet
rev it names; the freeze/build pair happened to straddle a fleet move (`bcc9bbd2` → `ee9f7341`). It changed nothing
here (§4), and the receipt records `fleet=`, but future measured waves should pass `--fleet-rev` explicitly.

**R3 (integration state, out of my scope).** The lane worktree is mid-integration while I measured: `git status
--porcelain` = 34 dirty paths, including `SKILL.md` and `registry/hexrun-ledger.tsv`. My measurements are at committed
tips (the counter reads only `git show`/`ls-tree`/`log`, never the worktree), so they are unaffected; but a C2 run at
the eventual integration commit will re-count SKILL.md citations and must be re-measured there, not inferred from
`c22602bd`.

## 9. Scope notes

No pacman, no installs, no package changes. No server started or stopped (the two `llama-server` processes visible are
peer `K2Design`'s, untouched); no writes outside this directory and `/fast/scratch/hyaku/kama-r53/X7Rerun`; the lane,
the fleet repo and `shokuknow` were read-only. Scratch (clone + five fixture clones + counter scratch dirs) removed
after copying every cited receipt here.

## Files in this directory

- `c2-matrix.txt` — the run table, exit codes, independent-parser numbers.
- `c2-{base-head,base-pinned,build-head,build-pinned,build-fleet-at-base-control}.{out,log}` — receipts (`--out` payload) and driver logs with `exit=`.
- `probe-{a..e}-*.out` — mutation-probe receipts.
- `indep-c2-probe.py`, `indep-build.txt`, `indep-base.txt` — independent second parser and its output.
- `proposed-upstream-digest-check.diff` — F1 proposal (not applied anywhere).
