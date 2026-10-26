# X1SelftestV2 — selftest power (round 47, lane kama)

**Verdict:** 6/6 — every v2 case added for D1/D2/K2Design fails on v1, and each of those six is a
unique kill switch: reverting exactly its v2 mechanism in a scratch copy of the frozen tool turns
exactly that one case red (7/7 targeted mutations). No other v2 case fails on v1. Separately, the
frozen C1 counter's `selftest` leg (`n >= 10`, `tools/round47-append-audit-v2-check.py:342`) accepts
v1's 10-case selftest, so that leg cannot separate v1 from v2; six further mechanisms of the tool
have no selftest case at all (measured: six mutations that change them leave all 15 cases green).

## Measured bytes

| object | bytes | sha256 | size |
|---|---|---|---|
| v1 tool, `bbcc6dc2:tools/append-only-audit.py` | `inputs/v1-append-only-audit.py` | `793dab9ffe0c41c7a5427324fd6f8bf0c3b40b0f9083d417e38d5e5792a7227f` | 325 lines, 10 cases (list at :283-288) |
| v2 tool, `3a09a1d9:tools/append-only-audit.py` (= `46a924e0`) | `inputs/v2-append-only-audit-3a09a1d9.py` | `5d47bc77e9bde41a1af1fcba449e60fd027d9ed30fbf2770a5a53f177856f874` | 500 lines, 15 cases (list at :450-457) |
| frozen C1 counter | lane `tools/round47-append-audit-v2-check.py` | `a180ab84cc642731a6bd5fca92e5218dfaa6c074279e2f001110b348d73755ed` | matches prereg `counter_sha256` |
| lane working tree at measurement time | `inputs/tree-snapshot-a7feae03.py` | `a7feae03eaf97122fe73433c7c8524b4d5d5ac562bfc5f6938b9f5ef5891217d` | 604 lines, 19 cases (uncommitted, sibling seats) |

The lane working tree moved mid-wave: `git status --porcelain` in the lane lists
` M tools/append-only-audit.py`, ` M SKILL.md`, ` M corpus/QUALITY.md`, ` M corpus/SOURCES.md`,
` M tools/kama-live-replay.py`, ` M tools/gguf-identity.py`, ` M tests/llamacpp-live/check-receipt.py`
plus untracked `.ufo/waves/round-47/w1/out/`. The frozen build blob `5d47bc77` is what this seat
measures (it is the commit the item names); the working-tree snapshot is run only as a secondary
check and is labelled as such below.

## Method

- `port_v2_cases_to_v1.py`: loads the tool under test from a path (no imports from the lane) and
  ports all 15 frozen v2 case bodies verbatim. Changed only: (a) the audit call — v1 is
  `audit(repo, to, threshold, files)` and has no contract argument; (b) field name — `restored_max`
  is read from v1's `restored_at_tip`. The fixture is v1's own `Fixture` subclassed only to add
  v2's `raw=True` byte writes (needed for the CRLF/no-final-newline fixture).
- v1 has no `restored_best` key at all (v1 event dict at `inputs/v1-append-only-audit.py:116`:
  `commit, file, deleted, restored_at_tip, status, restored_by`). An assertion on `restored_best`
  is recorded as `skipped` and each case is scored twice: `ok` (every v1-expressible assertion) and
  `strict_ok` (`ok` and no v2 field was unavailable).
- Control: the same harness pointed at the frozen v2 passes **15/15** both ways
  (`port_control_v2.txt`), i.e. it reproduces v2's own selftest; pointed at the working-tree snapshot
  it passes 15/15 for the same 15 bodies (`port_control_tree.txt`). So a failing case is v1's
  behaviour, not the harness.

Command (exit 0):

```
python3 port_v2_cases_to_v1.py \
  --v1-tool inputs/v1-append-only-audit.py \
  --v2-tool inputs/v2-append-only-audit-3a09a1d9.py \
  --scratch $S --json port_v1.json
```

```
X1_V1_PORT cases=15 fail=6 fail_cases=dashdash-lines,crlf-and-eof,multiset,window-max,relocation,contract
X1_V1_PORT_STRICT fail=9 fail_cases=exact-threshold-unrestored,restored-later,partial,dashdash-lines,crlf-and-eof,multiset,window-max,relocation,contract
X1_CASE_LIST v2_schema=append-only-audit/v2 ported=15 missing_from_v2_selftest=-
```

Native selftests on the same bytes (exit 0 each): v1 `AOA_SELFTEST pass=10 fail=0`
(`v1-native-selftest.txt`), v2 `AOA_SELFTEST pass=15 fail=0` (`v2-native-selftest.txt`).

## Which v2 cases v1 fails

All 15 ported cases, v1 observed (`port_v1.json`, `port_v1.txt`):

| # | v2 case | v1 observed (events / deleted / restored_at_tip / status / witness) | v1 verdict |
|---|---|---|---|
| 1 | no-deletion | 0 events, exit 0 | pass |
| 2 | below-threshold | 0 events, exit 0 | pass |
| 3 | exact-threshold-unrestored | 1 / 20 / 0 / unrestored / by None | pass (strict: `restored_best` absent) |
| 4 | restored-later | 1 / 40 / 40 / restored / by r | pass (strict: `restored_best` absent) |
| 5 | partial | 1 / 40 / 20 / partial / by None | pass (strict: `restored_best` absent) |
| 6 | undeclared-file | 0 events, exit 0 | pass |
| 7 | declared-file-removed | 1 / 25 / 0 / unrestored | pass |
| 8 | merge-first-parent | 1 / 30 / 30 / restored, event ≠ merge | pass |
| 9 | **dashdash-lines** | **0 events** (19 counted, below threshold 20) | **FAIL** |
| 10 | **crlf-and-eof** | **1 / 27 / 26 / partial** | **FAIL** |
| 11 | **multiset** | **1 / 23 / 23 / restored, exit 0** | **FAIL** |
| 12 | **window-max** | **1 / 25 / 20 / partial** | **FAIL** |
| 13 | **relocation** | **1 / 25 / 25 / restored, restored_by None** | **FAIL** |
| 14 | **contract** | **files = the five v1 names, 0 events** | **FAIL** |
| 15 | threshold-flag | 1 / 5 / 0 / unrestored, exit 1 | pass |

Exactly the six cases the item predicts, and no seventh. Failure detail, with the v1 code that
causes it (line numbers into `inputs/v1-append-only-audit.py`) and the v2 mechanism that guards it:

1. **dashdash-lines** — D1. v1's deleted-line filter `:102`
   (`x.startswith("-") and not x.startswith("---")`) also drops *content* lines whose text begins
   with `--`: the fixture's `--out x`, `---`, `--- y` all render with a leading `---` in the diff.
   v1 counts 19 of 22, below the threshold, so no event at all. v2 counts by hunk-header lengths
   (`inputs/v2-append-only-audit-3a09a1d9.py:117-163`) and requires equality with
   `git diff --numstat` (`:202-203`).
2. **crlf-and-eof** — D1 byte identity. v1 reads git through `text=True`
   (`inputs/v1-append-only-audit.py:51`) and blobs by `str.split("\n")` after universal-newline
   folding (`:77`), so the deleted CRLF line and the LF copy at the tip compare equal. The deleted
   count is right (27, same as v2); the restoration is **26 vs v2's 25**: the CRLF line is counted as
   held by its LF copy, and the case rejects 26.
3. **multiset** — K2Design. v1's restoration is set membership counted per deleted occurrence
   (`:106` `k = sum(1 for x in dele if x in tip_lines)`), so 3 deleted `dup` lines are "restored"
   by the single kept copy: **23 of 23, restored, exit 0**; v2's multiset measure yields 21, partial
   (v2 `:212` `h = sum(min(n, max(0, M[l] - K[l])) ...)`).
4. **window-max** — D2. v1 measures restoration only at the audited tip (`:91`, `:105-106`), so the
   later re-trim to `a[:35]` lowers it to **20, partial**; v2 maximises over the event's window
   (`:210-218`) and keeps 25/restored with witness r.
5. **relocation** — v1 searches `restored_by` only in commits *after* the event (`:108-113`), so a
   block moved inside one commit restores the count (25) but has **restored_by None**; v2's window
   starts at the event commit, so `restored_by == c`.
6. **contract** — v1's file set is the hard-coded five (`:43` `FILES`), so `corpus/lessons/r1.md` is
   never audited: **files = the five, 0 events**, and v1 has no `parse_contract` to reject the
   malformed header. v2 expands the contract's patterns (`:183-184`).

The three `strict`-only failures (#3, #4, #5) are a field gap, not a behaviour gap: v1 cannot report
which commit attained the maximum, so a verbatim port of those v2 assertions is impossible; the
nine passing cases are v1's own cases (v2's list is v1's ten minus `to-earlier-rev` plus the six
new ones).

## Mutation power of the six new cases

`v2_mutation_power.py` reverts one v2 mechanism at a time in a scratch copy of the frozen tool
(each edit asserted to apply exactly once) and runs the tool's own selftest (exit 0). Frozen build:

| mutation | reverts to v1 | cases killed | evidence from the mutant's own FAIL line |
|---|---|---|---|
| M0 identity | — | none, 15/15 pass | control |
| M1 dashdash-v1 | drop `--`-starting deleted lines **and** drop the numstat check | `dashdash-lines` only | `deleted=19`, 0 events |
| M1b dashdash-filter-only | drop `--` lines, keep the numstat check | `dashdash-lines` only | `AuditError: hunk count 19 != numstat 22` |
| M2 newline-normalised | fold CRLF/CR on both the diff and blob read | `crlf-and-eof` only | `restored_max=26` |
| M3 multiset→set | set membership | `multiset` only | `restored_max=23, restored` |
| M4 tip-only-max | report the audited tip's figure | `window-max` only | `restored_max=20, partial` |
| M5 later-only-witness | witness search after the event commit only | `relocation` only | `restored_max=0, unrestored` |
| M6 hard-coded-files | v1's five-file set instead of the contract expansion | `contract` only | `files = [the five]` |

`X1_MUTATION_POWER mutations=7 targets_killed=7/7 identity_green=True`. Each of the six new cases is
the sole case that observes its mechanism, and each mechanism is observed by exactly one case — no
new case is redundant with another and none is a re-test of a v1 case. M1b is a bonus fact: with the
numstat equality check left in place, a `--`-blind parser does not silently undercount, it stops with
`could-not-evaluate` (exit 2); the check is the second line of defence behind the hunk-header parse.

Secondary run on the in-flight working-tree snapshot (19 cases, `mutation_vs_tree.txt`): M1, M1b,
M2, M3, M4, M5 each still kill exactly their case with the same signature, identity 19/19 green;
M6 no longer anchors (the contract expansion was refactored) → harness exit 2, `could-not-evaluate`,
so that snapshot is not measured further here.

## Mechanisms no selftest case covers (measured)

Same harness, probe residues that change a mechanism and leave **all 15 cases green** — i.e. the
selftest has no power over them:

| probe | mechanism changed | v2 site | cases killed |
|---|---|---|---|
| P1 binary numstat | a binary change (`numstat` `-`) counted as 0 deletions instead of skipped | `:165-172` | none |
| P2 threshold guard | removed `--threshold < 1` → exit 2 | `:482-484` | none |
| P3 rule validation | any rule accepted in a contract row | `:97` | none |
| P4 declared_at validation | any `declared_at` accepted (no `<path>:<line>` shape) | `:97` | none |
| P5 schema string | `schema` no longer `append-only-audit/v2` | `:70` | none |
| P6 earlier `--to` | `--to` resolved as HEAD (ignoring the requested rev) | `:178` | none |

`X1_PROBE_GAPS probes=6 no_case_covers=6`. P6 confirms dynamically what the case-name diff shows:
v1's `to-earlier-rev` case (v1 list `:283-288`) was dropped in v2, and v2's list
(`inputs/v2-append-only-audit-3a09a1d9.py:450-457`) has no case that audits a revision other than
the last commit of the fixture. Both tools still handle an earlier `--to` correctly
(`to_earlier_probe.txt`: v1 and v2 both `events=0 commits=2 exit=0`), so this is lost coverage, not
lost behaviour.

Note for integration: the working-tree 19-case snapshot appears to add `vanished-and-paths`, which
asserts `binary_changes`/`vanished`/`unmatched_patterns`, and rejects a CRLF contract header — that
would close P1 and part of P3/P4 on the new bytes. Those bytes are not the frozen build and were not
measured as the contract target.

## Instrument power: the C1 counter's `selftest` leg

`leg_selftest` (`tools/round47-append-audit-v2-check.py:335-345`) accepts
`returncode == 0 and fail == 0 and pass >= 10` (`:342`; docstring `:60-61`). Evaluated against the
two captured native runs (`selftest_leg_power.txt`, exit 0):

```
v1(b)bcc6dc2 pass=10 fail=0 cases=10 leg_selftest_ok=True
v2(3a09a1d)  pass=15 fail=0 cases=15 leg_selftest_ok=True
```

So `selftest=1` in the C1 receipt is satisfied by the pre-v2 tool. This matches the frozen controls:
`controls/base.c1.out:1` (v1 unchanged) is `selftest=1 contract=0 lane=0 fixture=0 stable=0`, and
`controls/junk-c1-v1-contract.c1.out:1` (v1 + a contract file, v2 skipped) is
`selftest=1 contract=0 lane=0 fixture=0 stable=0`. The discriminating legs are `contract`, `lane` and
`fixture` (`controls/junk-c1-v1-numstat.c1.out:1` shows a partial v1+v2 hybrid at
`selftest=0 ... fixture=0 stable=1`, i.e. its own selftest caught it before the fixture leg did).
The in-flight 19-case snapshot would also pass the `n >= 10` floor.

## Defects and proposed fixes (frozen instruments — reported, not edited)

**D-a — C1 counter's selftest leg has no power over the claim's mechanisms.**
`tools/round47-append-audit-v2-check.py:342` (`int(m.group(1)) >= 10`), docstring `:60-61`.
Shown by: `selftest_leg_power.txt` (v1 → `leg_selftest_ok=True`) and `controls/base.c1.out:1`.
Proposed fix (round 48, bumps `counter_sha256` and re-cuts the prereg): require `n >= 15` **and** a
`pass` line for each of the six case names. Full proposed text in `proposed-selftest-leg.md`.

**D-b — six tool mechanisms have no selftest case.**
`tools/append-only-audit.py` at `3a09a1d9`: binary skips, CLI threshold guard, contract rule and
`declared_at` validation, schema string, earlier `--to`. Shown by probes P1-P6 (all leave 15/15
green; `mutation.txt`). Proposed cases for round 48 (the selftest is frozen at the measured commit,
so this is a proposal, not an edit):
1. `binary-change`: commit `corpus/lessons/bin.md` with NUL bytes twice; assert no event, exit 0 and
   the path in `binary_changes`.
2. `threshold-guard`: call `main(["--repo", D, "--threshold", "0"])` in-process; assert exit 2.
3. `contract-rule`: `parse_contract` row with rule `B` → `AuditError`.
4. `contract-declared-at`: row with `declared_at` = `AGENTS.md` (no `:line`) → `AuditError`.
5. `schema-string`: assert `res["schema"] == "append-only-audit/v2"`.
6. `to-earlier-rev`: v1's case, ported unchanged (both tools pass it today).

**D-c — v2 dropped v1's `to-earlier-rev` case while keeping the behaviour.**
v1 list `:283-288` vs v2 list `:450-457`; `to_earlier_probe.txt`. Covered by proposal 6 above.

Not defects, recorded so they are not mistaken for them:
- the EOF half of `crlf-and-eof` (the unterminated final line counted among the 27 deletions) is not
  v1-discriminating — v1 also reports 27 — it is shared regression coverage; only the CRLF half kills.
- M1b's `could-not-evaluate` is the intended second line of defence, not a silent failure.

## Reproduce

```
S=/fast/scratch/hyaku/kama-r47/X1SelftestV2; mkdir -p "$S"; export TMPDIR="$S"
git -C /home/vgpnk/Projects/shokunin/kama-shokunin show bbcc6dc2fbd7fc04b1d91a97ffa239a6601cd5ba:tools/append-only-audit.py \
  > inputs/v1-append-only-audit.py
git -C /home/vgpnk/Projects/shokunin/kama-shokunin show 3a09a1d93dcc16799cf6c4b48786e6440af134c4:tools/append-only-audit.py \
  > inputs/v2-append-only-audit-3a09a1d9.py
python3 port_v2_cases_to_v1.py --v1-tool inputs/v1-append-only-audit.py \
  --v2-tool inputs/v2-append-only-audit-3a09a1d9.py --scratch "$S" --json port_v1.json
python3 port_v2_cases_to_v1.py --v1-tool inputs/v2-append-only-audit-3a09a1d9.py \
  --scratch "$S"                     # control: 15/15
python3 v2_mutation_power.py --v2-tool inputs/v2-append-only-audit-3a09a1d9.py \
  --scratch "$S" --json mutation.json
```

Fixtures are ephemeral repos under `--scratch` created by the tool's own `Fixture` (git init +
commits with a throwaway identity in that directory, toplevel asserted); they are removed on exit.
No lane file, index or jj state was touched; the lane was read only through `git show` / file reads.

## Risks and limits

- The port's `restored_best` skip is the only substantive adaptation beyond the call signature and
  field name; it cannot be avoided because v1 has no witness field. Both scorings are reported.
- Fixture contents are random per run, but every assertion is on counts/status/commit identity, and
  the control run passes 15/15, so the verdicts do not depend on the random draws.
- The lane working tree is being edited by sibling seats while this ran (`a7feae03`, 19 cases). All
  primary numbers are on the frozen blob `5d47bc77`; the secondary snapshot run is labelled.
- The probes prove "no case observes this change"; they do not claim the counter's own `fixture` leg
  ignores the same mechanisms (it does exercise binary/dup/CRLF/relocation/window-max: see
  `round47-append-audit-v2-check.py` `build_fixture` and `controls/junk-c1-v1-numstat.c1.out:1`).
- No tool installs were needed; no services started; no network used.

## Files written

All under `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/X1SelftestV2/`:
`port_v2_cases_to_v1.py`, `v2_mutation_power.py`, `port_v1.txt`, `port_v1.json`,
`port_control_v2.txt`, `port_control_tree.txt`, `port_v1_vs_tree.txt`, `mutation.txt`,
`mutation.json`, `mutation_vs_tree.txt`, `v1-native-selftest.txt`, `v2-native-selftest.txt`,
`selftest_leg_power.txt`, `to_earlier_probe.txt`, `proposed-selftest-leg.md`, `inputs/`
(three tool blobs with the sha256s above). Report: this file.
`/fast/scratch/hyaku/kama-r47/X1SelftestV2` is removed after the copy.
