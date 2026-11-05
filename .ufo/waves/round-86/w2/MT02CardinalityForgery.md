# MT02 — C2 cardinality forgery (round 86, wave w2, attack seat)

Author-side advisor. No claim admission. Measured revision: **67eddac89f44e768b670301ea0feff06e766f32d**
(lane HEAD at dispatch; unchanged by this seat — `git diff --stat -- tools .ufo/waves/round-86/count.py
plans/round-86-claims.md` is empty, `git status --porcelain -- tools` is 0 lines).

Instrument under attack: `tools/round86-mutant-owners.py` at that revision,
blob `7a0dd4b246bde0ddb996418f17a8d05033256569`,
sha256 `b7ee59ae1dbb955b27a467de8ed1163dec56c9b87b2370b41979cb4c23a2b5fd`
(scratch copy `evidence/mo.py`, byte-identical to the lane file).
Subject: `tools/round81-append-debt.py` at the same revision,
blob `e6c1dc696667fd3d0f8348ada395ba9cf91eeb3d`,
sha256 `3f366b0b27296b997bed8f91a80f2dc230174b5f97911ed87981bf1a031f96cb`.

Scratch `/fast/scratch/hyaku/kama-r86/MT02CardinalityForgery/` (fixture repo `fixture/`, toplevel asserted
equal to itself before every commit). No tool install was needed (python 3.14.8, git present; no pacman,
no uv, no service).

## Baselines (pristine, before any forgery)

| probe | command | exit | line |
|---|---|---|---|
| instrument control set | `python3 mo.py --selftest` | **0** | `DEBT_MUTANT_OWNERS_SELFTEST pass=10 fail=0` |
| real grade | `python3 mo.py --repo <lane> --rev 67eddac… --work …/work-real` | **0** | `DEBT_MUTANT_OWNERS mutants=5 killed=5 escaped=0 invalid=0 arms=34 cardinality=ok owners=5/5` |
| frozen counter c2 leg | `python3 .ufo/waves/round-86/count.py c2 --repo <lane> --rev 67eddac… --work …/counter-work` | **0** | same green line |

M5 `verdict=killed arms=33 != expected=34`, M6 `verdict=killed summary pass+fail=0 != arms=34`. The
round-85 survivors are genuinely killed at this revision; the finding below is not that the baseline is red.

## Attacks (each names what it attacks: one reconciliation clause)

Forgery mechanism: the clause engine `classify()` is invoked directly on forged bytes
(`evidence/probe.py`, `evidence/probe-classify.out`), **and** each forgery is also embedded in a committed
copy of the real `tools/round81-append-debt.py` inside my own fixture repo so the instrument's **real CLI
exit code** is measured (`evidence/cli-matrix.out`, per-variant `evidence/cli/<variant>.{out,err}`).

### (a) forge summary `pass=0 fail=0`, ARMS line intact — attacks `pass + fail == arms`

| encoding | verdict token | label | instrument exit | clause |
|---|---|---|---|---|
| `pass=0 fail=0 arms=34` (the declared M6 encoding) | `killed` | `summary-cardinality` | 0 (real grade) | `pass + fail == arms` |
| `pass=0 fail=0` (arms field dropped), ARMS `arms=34 expected=34 fail_lines=0` | **`escaped`** | — | **1** (`killed=4 escaped=1 owners=1/5`) | **DEFECT** |
| `pass=0 fail=0 arms=0`, ARMS intact | **`escaped`** | — | — | **DEFECT** |

CLI evidence, fixture rev `a39279f8614aafafcd547bcb5ad3bb601323e6d1`:

```
python3 mo.py --repo .../fixture --rev a39279f8… --work .../cli/a2-forged-summary-no-arms-field
EXIT=1
DEBT_MUTANT_OWNERS mutants=5 killed=4 escaped=1 invalid=0 arms=34 cardinality=ok owners=1/5
DEBT_MUTANT_OWNER M6 owner=summary-cardinality verdict=escaped green summary
DEBT_MUTANT_OWNER_PRISTINE APPEND_DEBT_SELFTEST pass=0 fail=0
```

The **pristine gate itself** (`verdict != "escaped"` → could-not-evaluate) accepts `pass=0 fail=0` as green:
`SUMMARY_RE` makes the `arms=` field optional, and the only arm-count clause is guarded by
`if arms is not None`. A forged summary that simply omits the field bypasses it; `arms=0` satisfies
`pass + fail == arms` arithmetically. The declared M6 mutant then escapes and the instrument still prints
`cardinality=ok`.

### (b) forge ARMS `arms=34` with a real dropped case (33 cases) — attacks `ARMS arms == expected`

| encoding | verdict token | label | instrument exit | clause |
|---|---|---|---|---|
| 33 cases, ARMS forged `arms=34`, summary `pass=33 fail=0 arms=33`, rc 1 | `invalid` | `arm-count` | 2 (pristine gate) | only the subject's own rc betrays it |
| same, rc forced 0 | **`escaped`** | — | **1** | **DEFECT** |
| 33 cases, ARMS `arms=34`, summary `pass=34 fail=0 arms=34` (consistent lie) | **`escaped`** | — | — | **DEFECT** |

CLI evidence, fixture rev `88c504ca6e75adbe7312230f829e920cd470ba0e` (one real `cases.append` arm removed,
ARMS print hardcoded `arms=34`, `len(cases) == EXPECTED_ARMS` check removed from the return):

```
EXIT=1
DEBT_MUTANT_OWNERS mutants=5 killed=4 escaped=1 invalid=0 arms=34 cardinality=ok owners=4/5
DEBT_MUTANT_OWNER M5 owner=arm-count verdict=escaped green summary
DEBT_MUTANT_OWNER_PRISTINE APPEND_DEBT_SELFTEST pass=33 fail=0 arms=33
```

`arms=34` is reported for a subject that ran 33 arms, and the M5 mutant — the round-85 survivor this claim
exists to kill — **escapes**. Cause: `arms == expected` compares the forged ARMS value with the ARMS line's
own `expected` field; nothing compares ARMS `arms` with the summary's `arms` (33 here), and `EXPECTED_ARMS`
is never read independently of the ARMS line it is meant to police. The docstring's "declared arm
population" is self-referential.

### (c) print an extra `APPEND_DEBT_SELFTEST_FAIL` line the summary does not count — attacks `fail_lines == summary fail == printed FAIL lines`

| encoding | verdict token | label | instrument exit | clause |
|---|---|---|---|---|
| well-formed extra FAIL line, ARMS `fail_lines=0`, summary `fail=0` | `killed` | `summary-cardinality` | 2 (pristine gate: `ARMS fail_lines=0 != 1 FAIL lines`) | `fail_lines == printed FAIL lines` |
| extra FAIL line, **no ARMS line at all**, summary `pass=34 fail=0` | **`escaped`** | — | — | **DEFECT** (clause is guarded by `if arms_lines`) |
| extra FAIL line with no name token (`APPEND_DEBT_SELFTEST_FAIL note-x`, no trailing space) | **`escaped`** | — | — | **DEFECT** (`FAIL_RE` requires `\S+ `) |

CLI evidence, fixture rev `64e8e8dd409383b68d53ca6da484e4db52ba787b`:
`EXIT=2`, stderr `could-not-evaluate: pristine selftest not green: ARMS fail_lines=0 != 1 FAIL lines`.
The frozen clause set allows **zero** ARMS lines ("at most one"), and with no ARMS line the failure-line
cardinality is not evaluated at all — a subject that prints five FAIL lines and a bare green summary grades
`escaped`.

### (d) print two summary lines — attacks "exactly one summary line"

`EXIT=2`, stderr `could-not-evaluate: pristine selftest not green: 2 summary lines`;
per-mutant verdict `invalid` (`evidence/probe-classify.out` P9). **Caught**, clause
`len(summaries) != 1`.

### (e) emit a traceback on stderr with exit 0 — attacks "empty stderr and no traceback"

| encoding | verdict token | instrument exit | clause |
|---|---|---|---|
| `Traceback (most recent call last):` on stderr, rc 0 | `invalid` | 2 (`pristine selftest not green: traceback on stderr`) | substring check |
| any other stderr output, rc 0, otherwise honest subject | **green** | **0** | **DEFECT — the declared "empty stderr" clause is not implemented** |

CLI evidence, fixture rev `294cf20c66946d483832fffb4cef8e7afa33f816` (honest subject plus
`sys.stderr.write("warning: internal diagnostic on stderr\n")`):

```
EXIT=0
DEBT_MUTANT_OWNERS mutants=5 killed=5 escaped=0 invalid=0 arms=34 cardinality=ok owners=5/5
```

The instrument prints its full green predicate line and exits 0 while the subject wrote to stderr. The
frozen clause list and the instrument docstring both promise "empty stderr"; `classify()` only searches
stderr for `"Traceback (most recent call last)"`. A subject that reports its own failures on stderr
(`APPEND_DEBT_SELFTEST_FAIL …` written to fd 2) is therefore invisible: only stdout is parsed.

## Secondary observations (not clause escapes, recorded for the integrator)

1. **Owner attribution is not per-mutant.** Clause-kills are labelled with the literal strings `arm-count`
   and `summary-cardinality`, which are also M5's and M6's declared owner names. In the (a) fixture the run
   was `killed=4 owners=1/5`: M2/M3/M4 were killed by the ARMS-vs-summary clause and are counted as owners
   of nothing. `owners=5/5` is reachable only for the exact declared encodings.
2. **A crash is misattributed.** An unhandled `SyntaxError` on stderr carries no
   `Traceback (most recent call last):` header, so it is reported as `0 summary lines`
   (fixture rev `445a1775e9f22e3c530e5b9d7a2f87b122cc432f`, exit 2). Still refused, wrong reason.
3. **Every clause is a self-consistency test on the subject's own text.** `pass + fail == arms`,
   `arms == expected`, `fail_lines == summary fail`, `fail_lines == printed FAIL lines` are all satisfiable
   by a forger who edits the two print statements coherently; nothing binds the reported population to arms
   actually executed. Probe x1 (`33 real cases reported as pass=34 fail=0 arms=34`) grades `escaped`.
4. The frozen control set (`--selftest`, 10 arms) contains only the *caught* encoding of each forgery
   (`forged-summary` uses `pass=0 fail=0 arms=34`; `dropped-arm` keeps `expected=34` honest and never forges
   `arms`). It therefore stays green while the escaping encodings above go untested — a control-coverage
   finding, not a control failure.

## Verdicts

| item | attacks | verdict |
|---|---|---|
| (a) summary `pass=0 fail=0`, ARMS intact | `pass + fail == arms` | **DEFECT** — accepted (`escaped`) when the arms field is dropped or forged to 0; only the exact declared M6 encoding is killed |
| (b) ARMS `arms=34`, real 33-case drop | `ARMS arms == expected` | **DEFECT** — `escaped`, `arms=34` reported for 33 executed arms |
| (c) uncounted FAIL line | `fail_lines` chain | **caught** with an ARMS line present (killed / pristine exit 2); **DEFECT** without an ARMS line or without a name token |
| (d) two summary lines | exactly one summary | **caught** (`invalid`, exit 2) |
| (e) traceback on stderr, exit 0 | empty stderr, no traceback | traceback **caught** (`invalid`, exit 2); the "empty stderr" half is **unimplemented** — non-traceback stderr grades fully green, exit 0 |

Frozen C2 kill rule includes "any cardinality clause that a forged summary can satisfy". Items (a), (b) and
the (c)/(e) variants are cardinality clauses satisfied by forged summaries while the instrument prints
`cardinality=ok` and, for (e), the exact predicate line with exit 0. The claim does not survive as frozen;
remediation would need (i) a required summary `arms=` field cross-checked against the ARMS `arms` value,
(ii) an independent population check that does not read its own answer from the ARMS line, (iii) a required
ARMS line (zero is currently legal), (iv) `FAIL_RE` tolerance for lines without a name token or an explicit
rejection of any line beginning `APPEND_DEBT_SELFTEST_FAIL`, and (v) an actual `stderr == ""` assertion.

## Evidence index (`out/MT02CardinalityForgery/evidence/`)

- `mo.py`, `debt.py` — committed bytes at 67eddac (sha256 in `HASHES.txt`)
- `selftest.out` — control set, exit 0
- `real-grade.out` — real grade at 67eddac, exit 0
- `counter-c2.out` — frozen counter c2 leg, exit 0
- `probe.py`, `probe-classify.out` — clause engine fed forged bytes (11 probes + JSON)
- `fivefail.out` — five uncounted FAIL lines, no ARMS line → `escaped`
- `failstderr.out` — five FAIL lines on stderr with an honest green stdout → `escaped`
- `build_fixture.py`, `fixture-build.out` — fixture commits and their revs
- `cli-matrix.out`, `cli/<variant>.{out,err}` — real CLI exit code per forgery
- `a2.py`, `a2.out`, `a2.err` — the intermediate malformed fixture kept as the crash-misattribution probe

## Exact commands

```
python3 mo.py --selftest                                                     # exit 0
python3 mo.py --repo <lane> --rev 67eddac89f44e768b670301ea0feff06e766f32d \
        --work /fast/scratch/hyaku/kama-r86/MT02CardinalityForgery/work-real  # exit 0
python3 .ufo/waves/round-86/count.py c2 --repo <lane> --rev 67eddac… \
        --work /fast/scratch/hyaku/kama-r86/MT02CardinalityForgery/counter-work # exit 0
python3 probe.py                                                             # exit 0 (prints verdicts)
python3 build_fixture.py                                                     # exit 0
python3 mo.py --repo …/fixture --rev <variant rev> --work …/cli/<variant>     # per variant: 0/1/2
```
