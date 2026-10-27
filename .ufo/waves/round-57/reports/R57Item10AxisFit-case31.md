# R57Item10AxisFit — case 31 (axis attribution and claim separability, read-only)

Seat: `R57Item10AxisFit` (simplifier), kama round 57, wave `kama-r57-w1`. No shared/source edits, no
commits in the lane, no tool installs. Everything below is a read or a scratch-clone measurement.

Pinned references:

- Lane tip at clone time: `8640e34cad02adcd247ba0862da63f6fb2aab0df`; lane tip at final measurement:
  `3d2d5d4d6cba3028ec5358832a67f192cc0e41ec` (three commits landed after the fixture clone; each
  measurement below names its own revision).
- Frozen base: `b89bdab2cc114735ec5d331c6c610134258f7864`.
- Fixture clone (scratch, now removed): `/fast/scratch/hyaku/kama-r57/R57Item10AxisFit/cloneA`.
- Case-31 separate evidence: `.ufo/waves/round-57/reports/R57Item10AxisFit-case31-evidence.md`;
  machine receipts in `.ufo/waves/round-57/reports/R57Item10AxisFit-case31-receipts/`.

## 1. Axis authority: live config vs MISSION (not resolved, as instructed)

Live assignment (one line, exact):

```
$ sed -n '52p' /home/vgpnk/Projects/shokunin/shokunin.conf
kama|kama-shokunin|operability + calibration (local model serving and endpoint health)
```

MISSION disagreement (inside a block the file itself marks non-current):

```
$ sed -n '16,17p' /home/vgpnk/Projects/shokunin/MISSION.md
Historical example — the upstream fleet's initial nine-lane config, not the
current roster (axes preserved):
$ sed -n '29p' /home/vgpnk/Projects/shokunin/MISSION.md
  kama:       { cwd: kama-shokunin/,   axes: "operability + freshness (local model serving/endpoints)" }
$ sed -n '50p' /home/vgpnk/Projects/shokunin/MISSION.md
`SCORECARD.md` with the reason. Axis assignments in `shokunin.conf` are initial;
```

The dispute is filed, not silently resolved: `.ufo/l0-questions.md:145` (kama, round-35) asks
“Which pair is the assigned authority?”, and `SCORECARD.md:6` records it as “an open L0 question
since round 35”.

Verdict on attribution: the two claims as recorded by the lane (`corpus/lessons/round-57.md:9-10`)
sit inside the live pair — C1 on operability, C2 on calibration — and calibration (7) is the lowest
assigned axis, so `AXES.md:31-33` (“causally separable … distinct axes … at least one claim works
the lane's lowest-scoring non-retired axis”) is satisfied against `shokunin.conf`. Under the
historical MISSION pair, calibration would not be an assigned axis; that reading is left open here.

## 2. Separability, measured (case 31)

Six fixtures in a scratch clone, each running each claim's own checker at its own revision. The
checker blobs are materialised per variant so the script under test is the variant's file, not the
worktree file (an earlier run in this seat mixed the two and is discarded, not reported).

| fixture | C1 `tools/round56-prereg-check.py` | C2 `tools/round42-selfdesc-reconcile.py` |
|---|---|---|
| V0 both repairs (`8640e34c`) | `met=True` exit 0 | `mismatches=0 maxN=57 met=True` exit 0 |
| C2-only: prereg checker at `b89bdab2`, count corrected (`45787c30`) | `met=True` exit 0 | `mismatches=0 maxN=57 met=True` exit 0 |
| C1-only: checker repaired, SCORECARD at `b89bdab2` (`2e3a79e4`) | `met=True` exit 0 | `mismatches=1 maxN=56 met=False` exit 1 |
| no-op battery + repaired checker (`cfc3b367`) | `met=False` exit 1 | `mismatches=0 maxN=57 met=True` exit 0 |
| no-op battery + pre-repair checker (`7984b4c5`) | `met=True` exit 0 | `mismatches=0 maxN=57 met=True` exit 0 |
| C1-only + no-op battery (`cce4199d`) | `met=False` exit 1 | `mismatches=1 maxN=56 met=False` exit 1 |

Read-out:

- C2 verifies with C1's repair absent (`45787c30`: `mismatches=0`, exit 0) and fails with C2's repair
  absent (`2e3a79e4`: `mismatches=1`, exit 1). C2 is independent of C1.
- C1's predicate verifies with C2's repair absent (`cce4199d`: no-op rejected, `met=False` exit 1)
  and its before-state reproduces the false green (`7984b4c5`: no-op accepted, `met=True` exit 0).
  C1 is independent of C2.
- Verdict: **causally separable in substance, on distinct axes.** This matches the amended mapping
  (C1 operability / C2 calibration), not the packet mapping.

## 3. The labels are not separable: frozen controls are cross-bound

Quoted from committed blobs (`89dc4f52`/`8640e34c`). At report time the lane working tree deletes
`controls/c1-noop.py`, `controls/noop-c1.out` and `controls/noop-c2.out` — a sibling round-57 repair,
not this seat's action.

- `diff controls/base-c1.out controls/base-c2-frozen.out` → only `4d3 < base_c1_exit=1`. Both files
  carry the *same* r41 calibration face:
  `r41=1 … mismatches=1 maxN=56 met=False` with
  `detail: r41 calibration run … no stdout line == '42' (exit 0)`.
- `controls/c1-noop.py` is a three-line stub whose entire body is
  `print("mismatches=0 maxN=46 met=True")`; `controls/noop-c1.out` is that output.
  `controls/noop-c2.out` prints `canonical_table_reads=0`, `self_description_reads=0`,
  `summary=mismatches=0 maxN=46 met=True`.
- Therefore neither `base-c2-frozen.out` nor either `noop-*.out` can discriminate C1 from C2: the two
  “base” receipts are one calibration measurement, and the two “no-op” receipts are a stub declaring
  green. The genuine C1 before-state is recorded in
  `.ufo/waves/round-56/measured/c2-noop-control.out` (`present=1 roster_match=1 kills=1 controls=2
  met=True`, exit 0), which the amendment cites rather than duplicating; the round-57
  `measured/noop-c1.out` records the after-state (`met=False`, exit 1).

## 4. Claim-ordering conflict across four surfaces

| surface | C1 | C2 |
|---|---|---|
| `controls/freeze.txt` (`89dc4f52`) | calibration — stale canonical-table count | operability — canonical-row execution binding |
| `controls/freeze-amendment.txt` (`7c873d7b`) | operability — round-56 prereg no-op defect | calibration — stale count 42→43 |
| `w1-dispatch.json` context / this seat's packet (`89dc4f52`) | calibration — “stale canonical capability row count … maxN=56 instead of expected 46” | operability — canonical-row execution/content binding, no-op `met=True` |
| `corpus/lessons/round-57.md:7-8` (final lesson) | operability — bind roster to executed call sites | calibration 7→7 — count 42→43 |

The amendment says it “supersedes the earlier round-57 freeze's claim ordering only”. The dispatch
packet was committed with the freeze at 14:42:40 (`89dc4f52`) and the amendment at 15:05:51
(`7c873d7b`), so all 64 seats were dispatched with the superseded IDs and targets. Any seat report
that says “C1 calibration” is using the superseded mapping; the authoritative mapping in the round
record is C1 operability / C2 calibration.

## 5. The packet's stated C1 target is not a measured quantity

- `maxN` is the greatest `^## Round (\d+)` heading (`tools/round42-selfdesc-reconcile.py:167-168`):
  measured `56` at `b89bdab2` and `57` at `8640e34c` (a `## Round 57` heading was added). It is not
  a canonical capability row count.
- The canonical capability table (`canon()`, same file:120-127) has **11 rows** at canonical round
  49, at both tips.
- Within round 57's files committed at `8640e34c`, `46` occurs as the packet's expected value, in `controls/c1-noop.py`'s
  hardcoded print, and in `noop-c1.out` / `noop-c2.out`. It is the round-46 `maxN` recorded in
  `.ufo/waves/round-46/measured/r42-final.out` (`mismatches=0 maxN=46 met=True`), reused by the
  do-nothing fixture. The packet's “expected 46” is therefore the stub's own number.
- The actual base failure is the r41 calibration literal: the row expected `'42'`, while
  `git ls-tree b89bdab2 corpus/lessons/ --name-only | grep -c verifier-spotcheck` → `43`
  (`git ls-tree 8640e34c …` → `43`). This is the defect the amendment names (42→43), not `maxN`.

## 6. Predicate strength: content binding, not execution binding (corroboration)

The landed C1 checker binds *textual call-site inventory*, not execution. Three battery variants,
each carrying the preregistered `ROSTER` literal, run against the repaired checker:

| variant | result |
|---|---|
| roster calls present normally (`8640e34c`) | `present=1 roster_match=1 kills=1 controls=2 met=True` exit 0 |
| all three roster labels as string first args of `run()` calls **after `return` in `main()`** (`e77179ad`) | `present=1 roster_match=1 kills=1 controls=2 met=True` exit 0 |
| unreachable calls whose third label is not a roster name (`a483db24`) | `present=1 roster_match=1 kills=1 controls=2 met=False` exit 1 |

The middle row reproduces, independently, the limit reported by sibling seat
`R57Item30AxisFit` (`R57Item30AxisFit-case51.md` §4): the `executed` term is
`expected <= invoked` over an `ast.walk` inventory, so unreachable calls satisfy it. The third row
shows the boundary — the binding is over label values, not reachability.

Consequence for attribution: the operability claim's predicate is a content/declaration binding. The
lesson's phrase “so a no-op harness cannot satisfy the counter” (`corpus/lessons/round-57.md:7`) holds
only for the call-free no-op; `SCORECARD.md` §Round 57 discloses the narrower limit. This does not
change separability (both claims stay separable), but it qualifies the operability verdict's scope.

## 7. Final-tip state (informational, not a claim)

At lane tip `3d2d5d4d`:

```
$ python3 tools/round56-prereg-check.py --repo . --tip 3d2d5d4d
present=1 roster_match=1 kills=1 controls=2 met=True        exit 0
$ python3 tools/round42-selfdesc-reconcile.py --repo . --tip 3d2d5d4d
r41=0 banner=0 … mismatches=0 maxN=57 met=True              exit 0
```

Both land green. This seat claims neither verdict; it reports the separable predicates.

## 8. Advisory spot-checks (seats are lane authors; advice only)

- **S515 re-opened** 2026-10-27 at
  `https://git-scm.com/docs/git-config#Documentation/git-config.txt-GITCONFIGCOUNT`
  (page metadata “git-config last updated in 2.56.0”). Located quote, verbatim, **18 words**:
  “all environment pairs GIT_CONFIG_KEY_<n> and GIT_CONFIG_VALUE_<n> up to that number will be added
  to the process’s runtime configuration”. The page's sentence begins “If GIT_CONFIG_COUNT is set to
  a positive number,” — adding it would make 26 words (>25 cap), so the 18-word excerpt is the right
  choice; the conditional is already in the row's topic cell. Advise: keep as recorded.
- **Admit/reject spot-check — S513 REJECT.** Both registry quotes verify live: S512 `rtld-audit(7)`
  (“the environment variable LD_AUDIT must be defined to contain a colon-separated list of shared
  libraries”, 15 words) and S513 `ld.so(8)` §LD_AUDIT (“A list of user-specified, ELF shared objects
  to be loaded before all others in a separate linker namespace”, 18 words). S512 names LD_AUDIT for
  the needed fact and S513's quoted sentence does not; the reject carries a flip condition. Advise:
  reject upheld; no registry cell changed.

## 9. Scope and side effects

- Writes by this seat: only the three new paths under `.ufo/waves/round-57/reports/` (this report,
  the case-31 evidence file, and the `-receipts/` directory). This seat modified no tracked lane
  file. The working tree does show sibling round-57 edits at report time (`D` on the three no-op
  controls, `M corpus/lessons/round-57.md`); those are not this seat's and were left untouched.
- Scratch: `/fast/scratch/hyaku/kama-r57/R57Item10AxisFit/` (removed after receipts were copied to
  the lane wave path). `TMPDIR` was pointed into that scratch for the counters' git-archive exports.
- Installs: none. Tools used: system `python3` and `git`.
- Limit: three lane commits landed after the fixture clone while this seat ran; measurements are pinned to the
  revisions named above, and the four-surface ordering table was read from the committed blobs at
  `89dc4f52`/`7c873d7b` plus the final lesson at `3d2d5d4d`.
- Independent cross-check: sibling seat `R57Item30AxisFit` (`R57Item30AxisFit-case51.md`) reaches the
  same attribution verdict from text evidence; this seat adds the measured six-variant matrix and
  reproduces its content-binding limit independently (§6). No divergence found in the verdicts.

Report: .ufo/waves/round-57/reports/R57Item10AxisFit-case31.md
