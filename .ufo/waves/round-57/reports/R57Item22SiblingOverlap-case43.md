# R57Item22SiblingOverlap — case 43 (cross-claim / sibling overlap scan, C1 stale count and C2 row-content target)

Role: connector, leaf seat, read-only. No commits, pushes, or writes to tracked files. Scratch: `/fast/scratch/hyaku/kama-r57/R57Item22SiblingOverlap/` (removed after receipts were copied). Receipts: `.ufo/waves/round-57/reports/R57Item22SiblingOverlap-case43.receipts/`.

Report path: the dispatch names no explicit `Report:` trailer for this seat. I used the path convention sibling seats already write to (`.ufo/waves/round-57/reports/<Seat>-case<N>.md`). Tell the planner if a different path is wanted.

Installs/updates: none. Every tool used is in-repo Python 3 (`python3`); no package was installed or upgraded.

## 0. Tip moved during the scan (read first)

| Moment | HEAD | Notes |
|---|---|---|
| first reads | `7c873d7b round-57: correct frozen claim targets before data` | working tree had uncommitted edits to `SCORECARD.md` and `tools/round56-prereg-check.py` |
| later reads | `7b74e2f2 round-57: bind prereg roster to executed calls` | sibling commit; touches `LOG.md`, `SCORECARD.md` (calibration 42→43), `corpus/lessons/round-57.md`, `tools/round56-prereg-check.py` (+13/−2); tracked tree clean afterward |
| frozen base | `b89bdab2cc114735ec5d331c6c610134258f7864` | base for every "before" receipt |

Every "tip" result below is at `7b74e2f2515a6f598918488fa5144658ff29925f`. Whoever landed `7b74e2f2` is not identified here; the commit is the one that carries the C1 and C2 repairs, so any later repair seat is editing already-changed code.

## 1. Overlap map (who reads what)

| Shared surface | C1 (stale calibration count, per `freeze-amendment`: calibration axis) | C2 (no-op roster gate, per `freeze-amendment`: operability axis) | Other readers |
|---|---|---|---|
| `SCORECARD.md` calibration cell (line 18) | yes: states the glob count `43` | — | `tools/round41-scorecard-reconcile.py` (via round42 `r41` fact, run output must equal the stated number); `tools/round43-registry-audit.py` spot leg (regex `` `(\d+)` \(outside closures on record\) ``) |
| `SCORECARD.md` `## Round 46` measured block (line 2676) | — | — | source of the literal `maxN=46` that both no-op fixtures copy (see F2) |
| `tools/round42-selfdesc-reconcile.py` | the counter | — | imports `tools/round41-scorecard-reconcile.py` |
| `tools/round56-prereg-check.py` | — | the gate | none in `tools/` (battery and prereg are read only by round-56 `.ufo/waves` files) |
| `tools/round56-env-leg-battery.py`, `.ufo/waves/round-56/preregistration.json` | — | roster source | `.ufo/waves/round-56/*` artifacts |
| `tools/capability-repertoire-audit.py` + SCORECARD canonical list (round 49, 11 rows) | — | the "canonical-row content" surface (see F4) | `tools/round41-pinwatch-audit.py`, `tools/round42-digest-audit.py`, `tools/round43-hexrun-audit.py`, `tools/round42-selfdesc-reconcile.py` (`caps`, `province` facts) |
| `registry` gate (`tools/round43-registry-audit.py` "gate") | — | — | lists `tools/round56-env-leg-battery.py`, `round56-env-leg-test.py`, `round56-prereg-check.py`, `round56-replay-code-audit.py` as unregistered |

Overlap conclusions:
- C1's repair cell is also the input of round 43. Changing it can green round 41 and leave round 43 red (F1).
- C2's repair edits only the checker. It does not touch the canonical list or any counter that reads it. The canonical list is therefore not a C2 overlap in practice; the only shared object is the roster file pair.
- C1 and C2 do not share a file. Their collision is in the SCORECARD round-57 narrative and in the sibling tree state, not in a counter.

## 2. Commands and exact outputs

All tools run from archived committed bytes (`git archive <rev> tools` into scratch), with `--repo` pointing at the real repo. Nothing was written into the repo. `git rev-parse --show-toplevel` = `/home/vgpnk/Projects/shokunin/kama-shokunin`.

Round-42 self-description counter (C1 target):
```
$ python3 round42-selfdesc-reconcile.py --repo <repo> --tip b89bdab2   # exit 1
tip=b89bdab2cc114735ec5d331c6c610134258f7864
r41=1 banner=0 planned=0 retired=0 saturation=0 caps=0 receipts=0 readme=0 province=0 rel=0 mismatches=1 maxN=56 met=False
detail: r41 calibration run `python3 -c "import glob;print(len(glob.glob('corpus/lessons/*verifier-spotcheck.md')))"` no stdout line == '42' (exit 0)

$ python3 round42-selfdesc-reconcile.py --repo <repo> --tip 7b74e2f2   # exit 0
tip=7b74e2f2515a6f598918488fa5144658ff29925f
r41=0 banner=0 planned=0 retired=0 saturation=0 caps=0 receipts=0 readme=0 province=0 rel=0 mismatches=0 maxN=56 met=True
```

Round-43 registry audit (also reads the calibration cell):
```
$ python3 round43-registry-audit.py --repo <repo> --tip b89bdab2   # exit 1
unreg=4 defect=0 flags=0 pins=0 selftest=1 dc=0 spot=1 hidden=0 pop=58 registered=54 mismatches=6 met=False
detail: gate unregistered tools/round56-env-leg-battery.py
detail: gate unregistered tools/round56-env-leg-test.py
detail: gate unregistered tools/round56-prereg-check.py
detail: gate unregistered tools/round56-replay-code-audit.py
detail: selftest: documented 'GATE_SELFTEST pass=6 fail=0', run printed 'GATE_SELFTEST pass=5 fail=1' exit 1
detail: spot: calibration row states none, tree holds 43

$ python3 round43-registry-audit.py --repo <repo> --tip 7b74e2f2   # exit 1
(identical six mismatches; spot detail unchanged: "calibration row states none, tree holds 43")
```

Capability repertoire (C2 row-content surface):
```
$ python3 capability-repertoire-audit.py --selftest                    # exit 0
CAP_SELFTEST pass=2 fail=0
$ python3 capability-repertoire-audit.py --repo <repo> --tip 7b74e2f2  # exit 0
listed 11 observed 11 missing 0 unsubstantiated 0 met True
$ python3 capability-repertoire-audit.py --repo <repo> --tip b89bdab2  # exit 0
listed 11 observed 11 missing 0 unsubstantiated 0 met True
```

C2 roster gate on fixtures (each fixture is a fresh `git init` repo in scratch; `git rev-parse --show-toplevel` checked before commit; each contains the frozen `preregistration.json` roster and one battery file):

| Fixture | Battery content | base `b89bdab2` checker | tip `7b74e2f2` checker |
|---|---|---|---|
| genuine | `tools/round56-env-leg-battery.py` from `7b74e2f2` (runs `run("base-old-counter"…)`, `run("round56-counter"…)`, `run("m-drop-ldaudit"…)` at top level) | `present=1 roster_match=1 kills=1 controls=2 met=True` exit 0 | `present=1 roster_match=1 kills=1 controls=2 met=True` exit 0 |
| noop | `ROSTER = {…}` literal only, `main` prints and runs nothing | `present=1 roster_match=1 kills=1 controls=2 met=True` exit 0 (false green) | `present=1 roster_match=1 kills=1 controls=2 met=False` exit 1 (fixed) |
| deadcode | same ROSTER, plus `def _never_called():` containing the three `run("…")` calls; nothing calls that function | `met=True` exit 0 | `present=1 roster_match=1 kills=1 controls=2 met=True` exit 0 (survives) |

Real repo, committed checker:
```
round56-prereg-check.py --repo <repo> --tip b89bdab2  → present=1 roster_match=1 kills=1 controls=2 met=True  exit 0
round56-prereg-check.py --repo <repo> --tip 7b74e2f2  → present=1 roster_match=1 kills=1 controls=2 met=True  exit 0
```

Provenance of literal `maxN=46` (C1 "expected 46"):
- `SCORECARD.md:2676` (tip) — "Regressions at `4340cf2f` (`.ufo/waves/round-46/measured/`): … round-42 self-description counter `mismatches=0 maxN=46 met=True`".
- `.ufo/waves/round-57/controls/c1-noop.py:3` — `print("mismatches=0 maxN=46 met=True")`.
- `.ufo/waves/round-57/controls/noop-c1.out:3`, `noop-c2.out:4` — same literal.
- `maxN` in the counter is `max` over `^## Round (\d+)` headings; at tip the highest heading is `## Round 56`, so `maxN=56` is derived from the tree. The counter never compares `maxN` to 46 or any other number (`evaluate()` in `round42-selfdesc-reconcile.py`).

## 3. Findings

**F1 (C1, overlap, unresolved).** The calibration cell that C1 repairs is read by two counters. Round 41 (via round 42) is now green at the tip (`r41=0`). Round 43 spot is still red at the tip. Cause, exact: round 43 matches `` `(\d+)` \(outside closures on record\) `` (`tools/round43-registry-audit.py:207`); the tip cell reads `` `43` (outside closures on record, including round 56; … ``, with a comma after "record", so the regex misses and reports `spot: calibration row states none, tree holds 43`. Base had the same failure (`…including round 54 and 55`). The round-46 SCORECARD note records this exact breakage ("the re-anchored calibration row broke its `(outside closures on record)` pattern"). A C1 repair that ends at `43` does not clear round 43. Any repair seat must keep the cell matching both `\(outside closures on record\)` and the round-42 needle, or update round 43 under its own freeze.

**F2 (C1 "expected 46" is a fixture literal, not a tree value).** The only derivation of `46` in the tree is the historical round-46 measured line (`SCORECARD.md:2676`, measured at `4340cf2f`). The no-op controls copy that literal. The tree's real `maxN` is `56`, and the counter never compares to 46. So the statement "counter reports maxN=56 instead of expected 46" conflates a stale fixture with a real defect. The defect the counter actually reports at base is `r41=1` (calibration run stdout `43` ≠ stated `42`). The task's "canonical capability row count" wording is not observed: the round-49 canonical list has 11 rows, `caprep` lists 11, and the Retired and Capabilities sections both say 11 (tip).

**F3 (C2, repair holds for literal no-op, not for dead code).** `7b74e2f2` makes the literal no-op go from `met=True` (base, exit 0) to `met=False` (tip, exit 1), and keeps the genuine battery at `met=True`. The gate tests syntactic presence of `run("<label>")` calls anywhere in the AST, not execution. A battery whose calls sit in an uncalled function passes at the tip (`deadcode` → `met=True`, exit 0). This is a residual C2 falsifier that survives the sibling's repair.

**F4 (C2 row-content surface, no current overlap defect).** The canonical capability list at the tip is unchanged from round 49 and bound by `capability-repertoire-audit.py` (listed=observed=11, unsubstantiated 0). This check binds names and path tokens, not execution. The round-41/42/43 counters, `caps`, and `province` depend on that same table; any row-content change ripples to all of them. No seat should change canonical-row semantics without re-running those four.

**F5 (frozen-claim ordering conflict, not resolved here).** `freeze.txt` and `w1-spec.json` label C1 = calibration count, C2 = operability no-op. The committed `freeze-amendment.txt` (commit `7c873d7b`) labels C1 = round-56 no-op (operability) and C2 = round-42 calibration count. The amendment says it supersedes "the claim ordering only." The overlap analysis above is label-independent: whichever label wins, the repairs are the same two surfaces. Planner decision needed; I did not resolve it.

**F6 (gate registration, shared).** Round-43's gate lists the four `round56-*` tools as unregistered at both base and tip. This is outside the two claims, but it is the same files C2 edits; a C2 repair that touches `tools/round56-prereg-check.py` also touches an unregistered file, so the gate counts will not move until the registry is updated.

## 4. Verification the main agent should run

These are the checks I did not run as a repair step, but they are what should gate the wave:
1. `python3 tools/round42-selfdesc-reconcile.py --repo . --tip 7b74e2f2` → expect `mismatches=0 met=True`.
2. `python3 tools/round43-registry-audit.py --repo . --tip <tip>` → currently `spot=1` (F1); expect this to need a repair seat.
3. `python3 tools/round56-prereg-check.py` against the three fixtures in `.ufo/waves/round-57/reports/R57Item22SiblingOverlap-case43.receipts/fixtures/` (build as in §2) → noop `met=False`, deadcode `met=True` (F3).
4. `python3 tools/capability-repertoire-audit.py --selftest` and `--repo . --tip <tip>` → `CAP_SELFTEST pass=2 fail=0`, `met True`.

## 5. Limits

- Read-only. I did not edit SCORECARD, tools, registry, LOG, or any sibling output.
- I did not reproduce `freeze.txt`'s "no-op C2 met=True" on the committed `round-57/controls/noop-c2.out` as an executed tool (that file is a printed literal); I used my own fixtures instead.
- Fixture commits were made in scratch repos only; no repo object was created.
- Sources: none opened by this seat (S515 belongs to R57Item06/13).

## 6. Addendum: HEAD moved again during the write-up

- HEAD is now `8640e34c round-57: record measured counter outcomes` (after `7b74e2f2`). It changes `SCORECARD.md` (+18/−2: a `## Round 57` section and the Authority/Planned lines) and the `.ufo/waves/round-57/{census,measured}` receipts. `tools/` is unchanged between `7b74e2f2` and `8640e34c`, so every counter result in §2 still applies to the tools.
- The calibration cell at `8640e34c` still reads `` `43` (outside closures on record, including …`` with a comma after "record". F1 therefore still holds: round 43's spot leg matches `(outside closures on record)` only.
- Tracked edits by siblings are present in the working tree at write time (`corpus/SOURCES.md`, `corpus/lessons/round-57.md`). I did not read or use them.
- Scratch removed (`/fast/scratch/hyaku/kama-r57/R57Item22SiblingOverlap/`); receipts kept under `.ufo/waves/round-57/reports/R57Item22SiblingOverlap-case43.receipts/`.
