# F11-grafts-lane — falsification report

**Verdict: HOLDS.** Fault premise real and observed in the frozen arm; the exit-2
"rewrites history" refusal is the correct outcome; no near variant of the
hidden-history channel defeats the current auditor at git 2.56.0.

Reviewer: CloseKama22.RowF11GraftsLane-2. Lane HEAD verified
`245a37f69628c2c6bb29bbf17897d8fb5946c857` before work. Fixture rebuilt by hand
(raw shell git, no import of the grid) at `/tmp/f11`; frozen arm = blob
`4fe9339f8fc3a4a4a479d9c938a850da12f1124d:tools/report-landing-audit.py` extracted
to `/tmp/frozen-audit.py`. Tools: git 2.56.0, Python 3.14.8; nothing installed.

## Row under test

`tests/report-audit/repo-state-grid.py:552` —
`("F11-grafts-lane", "fault", f_grafts, 2, None)`; builder `f_grafts` at
`repo-state-grid.py:355-360` (writes `<lc>\n` to `.git/info/grafts` over the
`_hidden_history` fixture at `:339-345`: omitted round commit X@900, cited tip
LC@1000, fleet report citing LC only); pinned reason `"rewrites history"` at
`repo-state-grid.py:583`. Detection in the auditor:
`tools/report-landing-audit.py:441-444` — `rev-parse --git-path info/grafts` +
`os.path.lexists` → `EvalError`, applied to both repos at `:491-492`.

## (1) Premise real and observed in frozen arm — CONFIRMED

Hand-built fixture (two `git commit` with `@900`/`@1000` stamps, fleet report
`.ufo/reports/round-1/kama.md` citing LC, `.git/info/grafts` = `LC`):

    $ git -C /tmp/f11/lane rev-list --count HEAD        → 1   (graft hides X)
    $ python3 /tmp/frozen-audit.py --lane-repo /tmp/f11/lane --fleet-repo \
        /tmp/f11/fleet --json --rounds 1 --no-errata
    exit=0; "status": "clean"; required_commits=1; defects: []

Frozen walks `git log` (`/tmp/frozen-audit.py:148`), honors the graft, sees only
LC, and reports the omitted-commit repo **clean** — a verdict flip exactly as the
C1 claim describes (0 exit parity, not a crash).

    $ python3 tools/report-landing-audit.py (same args)
    exit=2; stderr: "could-not-evaluate: /tmp/f11/lane:
                     /tmp/f11/lane/.git/info/grafts rewrites history"

Current refuses with the pinned reason substring. Both observed on my
independent fixture, matching the grid's claimed arms.

## (2) Exit-2 refusal is the CORRECT outcome — CONFIRMED

Unlike replace refs, **grafts have no opt-out flag**: measured
`git --no-replace-objects -C <lane> rev-list --count HEAD` still returns 1 with a
graft active (the file is still honored). So no `GIT_ISOLATION` flag can make git
show true history under grafts; every verdict emitted while the file exists is
computed over rewritten history and could flip either direction (hide an omitted
commit, or graft a fabricated parent chain). Refusal is the only outcome that is
never wrong; the axis-7 contract ("must not crash, flip, hang or run programs")
is satisfied — no traceback, bounded, side-effect-free (the check is a metadata
`lexists`, no repo mutation). The `lexists` granularity (any graft file, even
inert/empty/same-parent) is conservative but uniformly honest.

## (3) Near variants of the channel — all defended

| # | Variant | Setup | Observed on current |
|---|---------|-------|---------------------|
| A | `GIT_GRAFT_FILE` env pointing outside `.git` | ext graft file, `.git/info/grafts` absent | exit 1 `landed-omitted` — `git_env` strips `GIT_*` (`:103`), true history audited |
| B | commit-graph baked under graft | `commit-graph write --reachable` with graft on | **git writes no file** (rc 0, no `objects/info/commit-graph`); graft removed → count 2 → exit 1 correct. Graph never persists grafted parents |
| B2 | true-parent graph, graft added later | write graph clean, then add graft | rev-list 1 (graft applies over graph); auditor exit 2 refused |
| C | `git replace --graft LC` (refs/replace channel) | replace ref, no graft file | exit 1 `landed-omitted` — `--no-replace-objects` neutralizes |
| G | replace graft packed (`pack-refs --all`, no loose ref) | packed-refs only | exit 1 `landed-omitted` — flag covers packed refs |
| D | linked worktree, graft in **commondir** | `worktree add --detach`, graft at `main/.git/info/grafts` | `--git-path` resolves common dir → exit 2 refused |
| E | grafts path is symlink→/dev/null, directory, FIFO | `lexists` each | exit 2 refused all three (no hang on FIFO) |
| M | grafts in the **fleet** repo | graft on fleet HEAD | exit 2 refused (`check_history_repo` runs on both repos `:491-492`) |
| N | shallow + grafts combined | `.git/shallow` + grafts | exit 2 `shallow repository` (first refusal wins, pinned reason differs but still refused) |
| O | graft restating same parent (inert rewrite) | `LC X` graft line | exit 2 refused — any graft file is refused, conservative |
| P | graft file + replace ref on same commit | both present | exit 2 refused; and `--no-replace-objects` does **not** disable the graft (count stays 1), so existence check is load-bearing |
| bare | grafts in a bare lane clone | `clone --bare`, `info/grafts` | exit 2 refused with same reason |

No variant produced exit 0, a traceback, a timeout, or program execution.

## Not verified / residual risk

- Older git (< the build wave's declared 2.45 floor) or non-git tools
  (jgit/libgit2) writing commit-graphs with grafted parentage — declared floor
  makes this out of scope; on 2.56.0 git simply omits the graph under grafts.
- Evidence destruction before audit: `gc` under grafts honors grafted
  reachability (observed: X survived `gc --prune=now` at 2.56.0, no graph
  written); a git that pruned X would leave the auditor correctly reporting
  post-mutation truth — pre-audit destruction, not an auditor defect.
- Git-side deprecation: grafts are deprecated (git prints
  `advice.graftFileDeprecated` hints); if a future git drops graft support the
  refusal becomes conservative-only. Harmless direction.
- `commondir` file crafted to point `--git-path` outside the repo: refusal
  still triggers only if the resolved path exists; a `commondir` redirect is a
  broader gitfile-class attack (adjacent to declared-open O02), not probed
  exhaustively here.
- Frozen arm observed only on this one fixture shape (single graft line hiding
  the tip's parent edge), consistent with grid's frozen 0/26 claim.

## Files written

- `.ufo/waves/round-23/falsify/advice/RowF11GraftsLane.md` (this report)
- Scratch only under `/tmp/f11*`, `/tmp/frozen-audit.py` (fixtures + extracted blob)
