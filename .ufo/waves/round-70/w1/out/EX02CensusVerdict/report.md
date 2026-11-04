# report.md — EX02CensusVerdict, round 70, lane kama, claim C2 (operability)

Seat: repair the verdict accounting of `tools/round65-host-census.py` so that
"a census member that did not run is not a pass": the exit is derived from the
not-evaluated count; exit 0 only when `fail=0` AND every not-evaluated member
is named by an explicit repeatable `--waive <member-name>` (exact member
name). Member list, markers, tiers and budget unchanged;
`tools/round42-selfdesc-reconcile.py` untouched; lane untouched (read-only).

## Result

C2 counter met by the candidate bytes:
`REFUSED_MEMBER_CONTROL refused_fixture_exit=1 allpass_fixture_exit=0`, control exit 0
(base bytes scored `(0, 0)`, control exit 1 — fail-open).

## Deliverables (this directory)

| file | what |
|---|---|
| `round65-host-census.py` | full candidate bytes, sha256 `a82cad11d777aa4b34d8ae96b66250d52853ed880d4c2eaa510ea8b4bf37dc68` |
| `diff.patch` | unified diff vs base bytes; `git apply` from the lane root lands it |
| `demo.md` | exact commands + verbatim outputs for every acceptance behavior |
| `report.md` | this file |

## What changed in the candidate

Base sha256 `463899182af0d154859e86da785051760e4bc314f5489659ea32424c18374513`
(= tracked file = `measured/before/round65-host-census-base.py` at wave
start; verified by sha256 before editing). Diff hunks touch only the module
docstring and `main()`; imports, `LANE`, `BUDGET` and the entire `MEMBERS`
table (base lines 27–107) are byte-identical — member list, markers, tiers,
budget unchanged.

1. Docstring rewritten, dated round 70: `refused` now means "the census could
   not obtain a verdict from the member" (pinned refusal marker, census time
   budget, or a member that could not be spawned); refused members are
   counted in `not_evaluated`; stale round-65 parenthetical about the
   append-only-audit v6-revert-class arm removed (that arm passes today).
2. New `--waive <member-name>` parsing (repeatable, exact name; also accepts
   `--waive=<name>`). Parsing silently skips non-flag tokens it does not
   recognize — required so the frozen control can call `main()` in-process
   with its own `sys.argv` (an argparse-style hard error there would crash
   the control with SystemExit, which its `except Exception` does not catch).
3. All three did-not-run populations now flow through one `record_ne()`
   helper: marker refusals, `TimeoutExpired`, and `OSError` (spawn error,
   previously miscounted as a `fail` with tier attribution). Each becomes
   `not_evaluated`, never a pass; a waiver appends `[waived]` to the member's
   own line, which keeps its reason.
4. Verdict line per spec:
   `HOST_CENSUS pass=<p> fail=<f> not_evaluated=<n> waived=<w> total=<t> tierA_fail=<a> tierB_fail=<b>`.
   `tierA_fail`/`tierB_fail` count only members that ran and failed.
5. Exit rule: `return 0 if (failed == 0 and not unwaived_ne) else 1` — fail
   and not-evaluated-without-waiver both hold exit at 1. When unwaived
   not-evaluated members exist, an explanatory line names them
   (`HOST_CENSUS exit 1: <n> not-evaluated member(s) without a waiver: …`).
6. Waiver diagnostics on stderr: a `--waive` that names no census member, or
   names a member that was evaluated anyway, warns by name and changes
   nothing (a fail cannot be waived — kill rule).

## Commands executed, with exact outputs and exit codes

Full verbatim transcript in `demo.md`. Summary (all python3 3.14.8, host
plazir27, cwd = lane root unless noted):

| # | command | key output | exit |
|---|---|---|---|
| 1 | `python3 -m py_compile <candidate>` | — | 0 |
| 2 | `python3 .ufo/waves/round-70/controls/refused-member-control.py <candidate>` | `REFUSED_MEMBER_CONTROL refused_fixture_exit=1 allpass_fixture_exit=0` | 0 |
| 3 | real census via in-process load of candidate, `LANE` patched to lane root | `HOST_CENSUS pass=21 fail=1 not_evaluated=0 waived=0 total=22 tierA_fail=1 tierB_fail=0` | 1 (census `main()`) |
| 4 | same + `--waive "round42-selfdesc-reconcile selftest"` | same verdict; stderr `warning: --waive 'round42-selfdesc-reconcile selftest' unused: member was evaluated (fail); a waiver covers only not-evaluated members` | 1 |
| 5 | synthetic refused fixture + `--waive synthetic-refused` | `HOST_CENSUS pass=1 fail=0 not_evaluated=1 waived=1 total=2 tierA_fail=0 tierB_fail=0`, member line ends `[waived]` | 0 |
| 6 | control on an always-exit-1 shim (kill rule) | `REFUSED_MEMBER_CONTROL refused_fixture_exit=1 allpass_fixture_exit=1` | 1 (control rejects) |
| 7 | `diff -u base candidate` → `diff.patch`; `git apply --check` + `git apply` on a pristine base copy in scratch; sha256 compare | applied tree sha256 == candidate sha256 `a82cad11…` | 0 |

Also verified before editing: tracked `tools/round65-host-census.py` ==
`measured/before/round65-host-census-base.py` == my base copy
(sha256 `463899182af0…`), and lane HEAD is `0e14facd0c619f45a6461821d2bd80ddac9855b1`.

## What the L1 must land

1. `round65-host-census.py` (this dir) → `tools/round65-host-census.py`
   (equivalently: `git apply .ufo/waves/round-70/w1/out/EX02CensusVerdict/diff.patch`
   at the lane root). Expected landed sha256 `a82cad11d777aa4b34d8ae96b66250d52853ed880d4c2eaa510ea8b4bf37dc68`.
2. Post-landing checks (parent's gate): the C2 counter —
   `python3 .ufo/waves/round-70/controls/refused-member-control.py tools/round65-host-census.py`
   must print `refused_fixture_exit=1 allpass_fixture_exit=0` and exit 0; the
   real census `python3 tools/round65-host-census.py` needs no `LANE` patch.

## What I could NOT verify

- The landed-path invocation `python3 tools/round65-host-census.py` itself:
  the lane is read-only for this seat, so the real-census rows used an
  in-process load of the candidate with `LANE` patched to the lane root —
  the identical substitution the frozen control makes. After landing, the
  file derives `LANE` from its own location and needs no patch.
- The C2 green target `HOST_CENSUS pass=22 fail=0 not_evaluated=0 total=22`,
  exit 0: blocked on C1 (the reconciler arm is the one red member; its
  selftest `newest=69` arm fails while the lane tip still reads round 69).
  Per the freeze's separability note this is a population effect, not C2
  evidence. Everything C2 owns is verified above.
- Windows-host behavior (the round-65 adaptations): this host is Linux; the
  adaptation code paths are byte-identical to base and were not exercised.

## Hygiene / notes

- No tools installed or upgraded; pacman untouched; no tooling exceptions
  needed (reporting per host guard: none).
- Writes: only this out dir and `/fast/scratch/hyaku/kama-r70/EX02CensusVerdict/`
  (created for fixtures/drivers, deleted before yield). Nothing in /tmp
  persists (mktemp dirs were trap-deleted in the same command that made them).
  A `__pycache__/` that py_compile/import created next to the candidate was
  removed; the out dir holds exactly the four deliverables.
- No git mutations anywhere; fixtures ran `git apply` on scratch copies only.
- Findings also written to the Report trailer path
  `.ufo/waves/round-70/w1/out/EX02CensusVerdict.md` as instructed by the seat
  spec; that file sits beside `swarm-registry.json` directly under `w1/out/`.
  Flagging it because the goal text's "exactly ONE directory" bound and the
  Report trailer instruction point at two different locations; both writes
  are inside the round-70 wave tree.
