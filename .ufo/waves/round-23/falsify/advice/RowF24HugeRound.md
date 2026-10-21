# Falsify review — grid row F24-huge-round-number

Seat: `CloseKama22.RowF24HugeRound-2`
Lane base: `245a37f69628c2c6bb29bbf17897d8fb5946c857` (clone HEAD verified,
`/tmp/kama-r23w2/RowF24HugeRound-2`).
Arms: frozen blob `4fe9339f8fc3a4a4a479d9c938a850da12f1124d:tools/report-landing-audit.py`
(sha256 `09ecd63bdc3a5be5264e6d2966602a32e52ca0678dc89de99959318245ab3b3f`);
current committed file (sha256 `f228f17420134a4a4fb6d1f93b943f78647e7e60882f767e6cb7cba11d6928a7`).
Interpreter `3.14.8`, `sys.get_int_max_str_digits() == 4300`.
No external sources were used; nothing below depends on a web quote.

## Verdict: partially falsified

1. **Premise reproduces, but not as repository state.** The frozen arm does
   traceback (exit 1) on the exact fixture; the current arm exits 2 with the
   pinned string. However the fault is CPython's int-conversion digit cap
   applied to an *operator argument*; no repository object is read before the
   exception. With `PYTHONINTMAXSTRDIGITS=0` the frozen arm exits 2 with a
   clean, named refusal — one environment variable removes the "fault"
   without a code change.
2. **Exit code correct, expected reason wrong.** Exit 2 is the right class
   for an unusable `--rounds` item, but pinning
   `could-not-evaluate: internal: ValueError` certifies the blanket
   `except Exception` label, not a refusal. A copy that validates the token
   and raises `EvalError` (exit 2, no traceback, named reason) is graded
   NOT-MET by the grid. The row therefore fails a strictly better fix.
3. **Same-channel variant still wrong.** `--rounds 1-<bound>` materializes
   the whole range (`tools/report-landing-audit.py:414`) with no size guard:
   111 bytes/round measured; 10^8 rounds ≈ 11 GB, 10^9 ≈ 111 GB. Under a 2 GB
   address-space cap this dies as `internal: MemoryError`; uncapped it is an
   OOM/hang, never a refusal. Only the accidental 4300-digit cap covers F24's
   single token. Three repository-controlled routes reach the same
   `internal: ValueError` label and have no graded row.

---

## Fixture rebuilt by hand (no grid import)

`/tmp/f24-byhand/build.sh` — plain `git` only, isolated env
(`GIT_CONFIG_GLOBAL=/dev/null`, `GIT_CONFIG_NOSYSTEM=1`, explicit identity),
fresh `/tmp` repos:

```
git init -q -b master lane ; git init -q -b master fleet
lane:  printf 'round-1: work\n' > f ; git add f ; git commit -m 'round-1: work'   -> LC
fleet: .ufo/reports/round-1/kama.md = "# kama round 1\n\n## Landed changes\n\n- LC\n"
       git add .ufo/reports/round-1/kama.md ; git commit -m 'round-1: report'
```

Observed `LC=77811d8eb8f4634363c6a5d99de50b342f34240a`, fleet `9e090fa`.
Control (both arms, `--rounds 1 --no-errata --json`): exit 0, `defects: []`.

## (1) Is the fault premise real and observed in the frozen arm?

Yes, as run, and exactly as the grid claims (`repo-state-grid.py:448-451`,
row at `:567`, reason at `:589`):

```
$ python3 frozen.py    --lane-repo lane --fleet-repo fleet --rounds <5000 nines> --no-errata --json
exit=1  stdout_bytes=0
Traceback (most recent call last):
  File "/tmp/frozen-r23f24.py", line 847, in <module>
    sys.exit(main())
  File "/tmp/frozen-r23f24.py", line 368, in parse_rounds
    rounds.add(int(part))
ValueError: Exceeds the limit (4300 digits) for integer string conversion: value has 5000 digits
$ python3 current.py   ... same args
exit=2  stderr: could-not-evaluate: internal: ValueError: ValueError('Exceeds the limit (4300 digits) ...')
```

`tests/report-audit/repo-state-grid.py --arm both --case F24-huge-round-number
--current /tmp/kama-r23w2/RowF24HugeRound-2/tools/report-landing-audit.py`
reproduces it with `auditor_sha256 current=f228f174... frozen=09ecd63b...`:
`current met=True exit=2 traceback=False`; `frozen met=False exit=1
traceback=True` (grid exit 1, as declared). Frozen's current-file
equivalent is `tools/report-landing-audit.py:404`; the handler that converts
it to exit 2 is `:918-925`. Note: the lane working tree was concurrently
modified by other seats during this review (`git status` shows
`tools/report-landing-audit.py` modified); every current-arm result below was
produced from the committed blob at `245a37f6` in the clone, not from that
working tree.

But the premise is **not** C1's channel. The grid's own axis is
`repo-state-grid.py:17-18`: "Graded rows are `fault` (repository-local state
must not crash, flip or hijack the verdict)"; the lesson says
`corpus/lessons/round-23.md:11` "Repository-local git state in the audited
lane/fleet repositories still crashed it". This row passes a **CLI argument**.
Proof that no repository state participates:

```
$ current.py --lane-repo /nonexistent/lane --fleet-repo /nonexistent/fleet --rounds <5000 nines>
exit=2  could-not-evaluate: internal: ValueError: ... 5000 digits ...
$ frozen.py  --lane-repo /nonexistent/lane --fleet-repo /nonexistent/fleet --rounds <5000 nines>
exit=1  Traceback ... ValueError ...        # same crash, zero repos exist
```

And the fault is an interpreter default, not tool code:

```
$ PYTHONINTMAXSTRDIGITS=0 python3 frozen.py --lane-repo lane --fleet-repo fleet --rounds <5000 nines>
exit=2  could-not-evaluate: round 999...9: cannot read .ufo/reports/round-999...9/kama.md at fleet HEAD: ...
$ PYTHONINTMAXSTRDIGITS=0 python3 current.py ...
exit=2  could-not-evaluate: round 999...9: cannot read ...          # identical refusal
$ PYTHONINTMAXSTRDIGITS=0 python3 tests/report-audit/repo-state-grid.py --arm frozen --case F24-huge-round-number --json
frozen: exit=2 traceback=False met=False
```

The frozen arm already satisfies the no-crash property in that environment;
it is `met=False` **only** because `run_case` requires the literal internal
string (`repo-state-grid.py:627-630`, `REASONS` at `:589`). So the row
measures (CPython default int cap) × (presence of the catch-all), not a
property of the audited repositories.

## (2) Is the expected outcome the CORRECT one?

Exit code: yes. `tools/report-landing-audit.py:42-45` puts malformed input
and "empty round selection" in exit 2, and a round number with thousands of
digits cannot name any
real report (filesystem `NAME_MAX` is 255; no round can be that number).
`--rounds 999...9` (up to 4300 digits) is already refused cleanly today:
`exit=2 could-not-evaluate: round 999...9: cannot read ...` — measured for
4000- and 4300-digit tokens.

Pinned reason: no. The pin requires the *internal* label, i.e. the generic
handler. Evidence, all with `repo-state-grid.py --arm current --case
F24-huge-round-number --json`:

| auditor copy | exit | traceback | graded |
|---|---|---|---|
| committed current | 2 | no | met (by pin) |
| `/tmp/f24-byhand/patched-clean.py` — adds `if len(part) > 20: raise EvalError("--rounds: spec item too long (...)")` | 2 | no | **NOT-MET**, stderr `could-not-evaluate: --rounds: spec item too long (5000 chars)` |
| `/tmp/f24-byhand/nocatch.py` — catch-all block deleted (`:918-925`), nothing else changed | 1 | **yes** | NOT-MET |
| `/tmp/f24-byhand/nocatch.py` with `PYTHONINTMAXSTRDIGITS=0` | 2 | no | NOT-MET (reason pin only) |

The clean-refusal copy is the behavior a maintainer should prefer (and the
tool's own `--rounds: bad item` path at `:408` shows the intended refusal
style), yet the grid rejects it. The only way to satisfy the row is to let a
`ValueError` escape from `parse_rounds` into the catch-all. Consequence for
the mutant ledger: M24 (`isolation-mutants.py:67-68`) is "killed" partly by
this string pin, so its kill says "the catch-all printed the expected label",
not "without it the tool crashed in a way the grid detects as a verdict
failure" — under `PYTHONINTMAXSTRDIGITS=0` a no-catchall auditor still exits 2
without a traceback and is still killed only by the reason mismatch.

## (3) Near variant in the same channel that current still gets wrong

### 3a. `--rounds` range bound (same argument, same number token)

`parse_rounds` at `:409-414` accepts any under-limit `lo-hi` and does
`rounds.update(range(lo, hi + 1))`; there is no size or digit guard. Measured
on the same fixture (`/tmp/f24-byhand/measure.py`, child max RSS):

| spec | exit | wall | max RSS |
|---|---|---|---|
| `1-10000000` | 2 (clean path error) | 0.51 s | 1,119,284 KB |
| `1-20000000` | 2 (clean path error) | 0.97 s | 2,216,992 KB |
| `1-100000000`, `RLIMIT_AS=2 GB` | 2 `internal: MemoryError` | 0.61 s | 1,173,808 KB |
| `1-` + 4001-digit bound, `RLIMIT_AS=2 GB` | 2 `internal: MemoryError` | 6.46 s | 1,172,112 KB |
| `1-` + 4300-digit bound, `RLIMIT_AS=2 GB` | 2 `internal: MemoryError` | 7.02 s | 1,171,288 KB |

Linear at ~111 B and ~50 ns per round: 10^8 ≈ 11 GB, 10^9 ≈ 111 GB. This
happens **before any repository check** (`run()` calls `parse_rounds` at
`:471`, the `check_history_repo` loop at `:475-476`): with both repo paths nonexistent,
`1-<4000 nines>` still returned `internal: MemoryError` after 6.39 s. On an
unconstrained host `--rounds 1-999999999` is an OOM/hang, and on this host
(10 GB available) 10^8 alone would exceed available memory. The grid's 30 s timeout
would catch such a row only by timeout/OOM, and no row exists. The only thing
that stops the *single*-token case at 5000 digits is CPython's cap; one digit
lower (4300) the same code path is the range blow-up, and one digit lower
still (4000) the single token is refused cleanly.

Note the scope caveat: this is argv, exactly like F24, so a grid row for it
would be the same off-axis channel. It is listed because F24 is graded, which
admits argv as a fault channel.

### 3b. Repository-local routes to the same label (C1's literal axis)

All hand-built (`/tmp/f24-byhand/build-variants.sh`), current auditor:

| repo-local input | selection | observed |
|---|---|---|
| fleet `.ufo/reports/round-<5001 digits>/kama.md` | `--rounds 1-` | exit 2 `could-not-evaluate: internal: ValueError` (`:420` int()) |
| fleet commit that adds round-1 report, author time 5000 digits | `--rounds 1` | exit 2 `internal: ValueError` at `report_cutoff` (`:206` int()) — git prints the raw 5000-digit `%at` |
| lane commits `registry/report-landing-errata.tsv` with a 5001-digit round field | `--rounds 1` (default errata) | exit 2 `internal: ValueError` at `parse_errata` (`:356`) |
| fleet `.ufo/reports/round-<4000 digits>/kama.md` | `--rounds 1-` | exit 0, `reports=2` (round 1 and a 4000-digit round both "clean", `required=0`) |

These satisfy C1's letter (exit 2, no traceback, no hang, no program), so they
do not falsify "must not crash" — but they are the same unhandled-error class
F24 pins as correct, they are repository-controlled (unlike F24), and none is
covered by a graded row. Because F24's reason pin already accepts
`internal: ValueError`, adding rows for them would not distinguish the current
tool from a correct one either. The 4000-digit directory is additionally
accepted as a legitimate round.

## What I did NOT verify

- Uncapped 10^8 / 10^9 range runs (deliberately not run: 10 GB available,
  shared host with live peers). The 11 GB / 111 GB figures are linear
  extrapolation from the measured 10^7 and 2×10^7 points; only the capped
  2 GB runs are directly observed.
- Behavior on Python ≤ 3.10 was simulated with `sys.set_int_max_str_digits(0)`
  / `PYTHONINTMAXSTRDIGITS=0`, not run on an actual older interpreter.
- No other grid rows were executed beyond `--case F24-huge-round-number`; the
  full frozen/current arms and the mutant sweep were not rerun.
- No leading-zero round directory (`round-0001`), alternates, or gitfile
  variants were probed.
- No claim about git versions; this row never invokes a repo-reading git
  command before it fails.

## Files written

- Report: `.ufo/waves/round-23/falsify/advice/RowF24HugeRound.md` (this file).
- Fixture/evidence (all under `/tmp`, nothing in the lane checkout):
  `/tmp/f24-byhand/{build.sh,build-variants.sh,build-repostate.sh,measure.py,launch_nocap.py,patched-clean.py,nocatch.py}`,
  fixtures `fx`, `fx2`, `fx5001`, `fx4000`, `fxts`, `fxerr`, and captured
  stderr/JSON (`*.err`, `*.out`, `grid-f24-both.*`, `grid-*.out`,
  `single-*.err`, `time.err`).
- No tracked lane file, Git index, `.jj`, fleet root, sibling lane, domain
  source, global config or `~/.omp` was modified. No commits, pushes or jj
  commands. No tools installed or upgraded.
