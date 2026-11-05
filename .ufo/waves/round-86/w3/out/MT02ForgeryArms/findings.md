# MT02ForgeryArms — round-86 w3 — C2 input forgeries against the committed classifier

Seat: mutation-tester, lane `kama-shokunin` (L1 KamaR86). Target: terminal record tip
`bafae7afb41843564ac2468d28beb8e0bb98e8e6`, read as committed bytes into
`/fast/scratch/hyaku/kama-r86/MT02ForgeryArms/copy` (one `git archive`/`tar -x` copy).
Scratch copy hashes equal the committed blobs (below), so every probe ran on the record's own bytes.
Nothing was repaired; no lane file was written.

## 0. Baseline (the instrument is healthy before it is attacked)

```
$ python3 copy/tools/round86-mutant-owners.py --selftest
DEBT_MUTANT_OWNERS_SELFTEST pass=13 fail=0                      [exit 0]

$ python3 copy/tools/round86-mutant-owners.py --repo <lane> \
      --rev bafae7afb41843564ac2468d28beb8e0bb98e8e6 --work <scratch>/work/live
DEBT_MUTANT_OWNERS mutants=5 killed=5 escaped=0 invalid=0 arms=34 cardinality=ok owners=5/5   [exit 0]

$ python3 .ufo/waves/round-86/count.py c2 --repo . --rev bafae7af… --work <scratch>/work/counter
DEBT_MUTANT_OWNERS mutants=5 killed=5 escaped=0 invalid=0 arms=34 cardinality=ok owners=5/5   [exit 0]
```

Both lanes (direct instrument, frozen counter) reproduce `measured/terminal/c2.out` line for line.

Byte identity (so the probes are against the record, not a stray copy):

```
f20279c6874bc4f6ff44dd810257dce87028dd140d43786ae93a257c2befeb73  tools/round86-mutant-owners.py
3d3b3a07f6efcd02f9a8ebcdbc477afcb291ef91d7e0d25f2166cd7af8228019  tools/round81-append-debt.py
```

Record/plan delta (reconciled, not a defect): the frozen plan says C2's selftest has **10 arms** and
`measured/before/c2-selftest.out` ends `DEBT_MUTANT_OWNERS_SELFTEST pass=10 fail=0`; the committed
instrument prints **pass=13**. The three added arms (`stderr-noise`, `summary-without-arms-field`,
`no-arms-line-disclosed-limit`) are the post-freeze repair disclosed in
`corpus/lessons/round-86.md` §M6 and counted as `13/0` in the SCORECARD row. The plan text is
frozen and is not rewritten; the lesson carries the correction.

## 1. The four forgeries

Fixtures are byte-exact mutant copies of `tools/round81-append-debt.py`
(`evidence/fixtures/*.py`); each was executed, its real stdout/stderr/exit fed to the committed
`classify()`, and for the (a) class also to the committed CLI over a scratch git repo whose
`tools/round81-append-debt.py` is the fixture.

### (a) Fully consistent forgery — summary, ARMS line and exit code agree on a population the source does not have

| probe | subject | printed | real | classify | instrument (CLI) |
|---|---|---|---|---|---|
| `a1` | `A1_forged34.py`: 4 arms deleted, 4 duplicates padded in | `arms=34 expected=34 fail_lines=0` / `pass=34 fail=0` / rc 0 | 30 distinct arms (`probe: real_cases=30`) | `escaped` | `mutants=5 killed=5 escaped=0 invalid=0 arms=34 cardinality=ok owners=2/5` **exit 1** |
| `a2` | `A2_forged40.py`: same, claims 40 | `arms=40 expected=40 fail_lines=0` / `pass=40 fail=0` / rc 0 | 30 | `escaped` | `… arms=40 … owners=2/5` exit 1 + `DEBT_MUTANT_OWNERS_FINDING population arms=40 != declared=34` |
| `F` | `F_forged_green.py`: 4 arms deleted, population padded to 34, owning FAIL lines derived by string-matching its own source | green when pristine, one *reconcilable* owning FAIL line per mutant | 30 | `killed` (per mutant, on the declared owner) | `DEBT_MUTANT_OWNERS mutants=5 killed=5 escaped=0 invalid=0 arms=34 cardinality=ok owners=5/5` **exit 0** |
| `a3` | fabricated kill: owning FAIL line, no arm executed | `arms=34 expected=34 fail_lines=1` / `pass=33 fail=1` / rc 1 | 0 | `killed` | n/a |

**Survives:** `a1`, `a2` (classifier), and **`F` completely — the instrument prints its exact frozen
target line on a subject with 30 distinct arms, four deleted arms and no real failure semantics.**
`a1` is only one field away: `killed=5 escaped=0 invalid=0 arms=34 cardinality=ok` is printed
verbatim, and the sole surviving guard is `owners=2/5`; `F` closes that column too. `a2` is stopped
only by the hardcoded `DECLARED_POPULATION = 34` pin, i.e. **a forgery at exactly 34 is invisible
while any other number is caught** — the pin constrains the value, not the provenance.

### (b) ARMS line naming an owning arm that never printed

Grammar fact first: `ARMS_RE = ^APPEND_DEBT_SELFTEST_ARMS arms=([0-9]+) expected=([0-9]+) fail_lines=([0-9]+)$`
carries **no arm-identity field**, so "names an owning arm" is not representable inside the frozen
shape; the nearest instantiations are the failure count and an extended (hence unparseable) line.

| probe | run | classify |
|---|---|---|
| `b1` | ARMS `fail_lines=1`, summary `fail=1`, **no FAIL line printed**, rc 1 | `killed` `summary-cardinality` — `ARMS fail_lines=1 != 0 FAIL lines` |
| `b2` | ARMS `fail_lines=0`, one owning FAIL line printed, rc 0 | `killed` `summary-cardinality` — `ARMS fail_lines=0 != 1 FAIL lines` |
| `b3` | **no ARMS line**, owning FAIL line printed, `pass=34 fail=0`, rc 0 | `escaped` |
| `b4` | ARMS `fail_lines=1`, FAIL line names a foreign arm, rc 1 | `invalid` — `exit 1 without the declared owning arm (['other-arm'])` |
| `b5` | consistent fabricated kill; owning arm never executed | `killed` (on the declared owner) |
| `b6` | ARMS line extended with `owner=note-deletion-equals-subject` (unparseable), claims 1 owning failure, none printed, rc 0 | `escaped` |
| `b7` | same unparseable ARMS line, owning FAIL line printed, rc 1 | `killed` (owner) |
| `b8` | same unparseable line, 2 FAIL lines vs `fail=1`, rc 1 | `killed` (owner; the cardinality lie is never reported) |
| `b9` | unparseable ARMS + summary carries `arms=34`, rc 0 | `escaped` |

**Survives:** `b3`, `b6`, `b9`. An ARMS line printed in a shape outside the frozen regex is treated
as *absent*, so every reconciliation clause silently stops applying — a forgery does not have to be
fully consistent to escape, only unparseable.

### (c) Printed FAIL lines exceed the summary fail

| probe | run | classify |
|---|---|---|
| `c1` | ARMS `fail_lines=1`, summary `fail=1`, **2 FAIL lines**, rc 1 | `killed` `summary-cardinality` — `ARMS fail_lines=1 != 2 FAIL lines` |
| `c2` | **no ARMS line**, summary `fail=0`, 2 FAIL lines, rc 0 | `escaped` |
| `c3` | no ARMS line, summary `fail=1`, 2 FAIL lines, rc 1 | `killed` (owner) — the excess is not reported |
| `c4` | ARMS `fail_lines=2`, summary `fail=2`, 2 FAIL lines, **rc 0** | `invalid` — `exit 0 with fail=2` |

**Survives:** `c2` (only when the ARMS line is absent, which the instrument already pins as the
disclosed-limit arm). With an ARMS line present the clause holds.

### (d) Right population, mutant semantic effect absent

`D2_forged34_M2_nopad.py` — no arms dropped, no padding; M2 (`deletion != accepting`) applied; the
failure line suppressed and `fail` zeroed before the prints.

```
$ FORGE_PROBE=… python3 forge/D2_forged34_M2_nopad.py --selftest
APPEND_DEBT_SELFTEST_ARMS arms=34 expected=34 fail_lines=0
APPEND_DEBT_SELFTEST pass=34 fail=0                              [rc 0]
probe: cases=34 internal_failures=1        ← semantic effect present, invisible
classify(stdout,"",0,"note-deletion-equals-subject") -> ('escaped', 'note-deletion-equals-subject', 'green summary')
```

Contrast control, same M2 on un-forged bytes (`C_unforged_M2.py`): exit 1, owning FAIL line printed,
`classify -> killed`. **Survives: yes** — with the correct population, a single suppressed line makes
a real mutant look green.

Aggregate over the 18 classifier probes in `evidence/probe-classify.out` /
`evidence/classify-matrix.json` (plus `D2`, measured separately): 7 escape
(`a1 a2 b3 c2 d b6 b9`), 9 killed, 2 invalid.

## 2. Does the disclosed limit match observation?

`corpus/lessons/round-86.md` §M6: "*a consistent forgery of every line (summary, ARMS line and exit
code all agreeing on a population that the source does not have) is not distinguishable by a
text-only classifier; that is MT02's `b2` class and it is routed to round 87*".

**Yes — matched, and exceeded in two directions the disclosure does not state.**

1. Consistency is *sufficient*, not *necessary*. `b6`/`b9` escape with an ARMS line that is present
   but unparseable, and `b3`/`c2` escape with the owning FAIL lines visibly printed; the classifier
   only reconciles what it can parse, and "cannot parse" is silently equal to "not declared".
2. The limit reaches the certificate, not just the per-run verdict. `F` is a subject with 4 arms
   deleted and 4 duplicated, whose "owning" failures are string-matched from its own source, and the
   committed CLI prints `DEBT_MUTANT_OWNERS mutants=5 killed=5 escaped=0 invalid=0 arms=34
   cardinality=ok owners=5/5` and exits 0. So the frozen target line proves *the printer's output is
   reconcilable*, never that `tools/round81-append-debt.py` at the graded revision owns 34 live arms.
   The only non-textual leg in the instrument is `--rev` reading committed bytes (`GitTree.blob_at`);
   provenance of the *printed* line is out of its reach, exactly as disclosed.

Not claimed here: that the record's own terminal line is forged. It is not — the counter replay at
`bafae7af` is green on the committed bytes, and the before-receipt shows the same instrument red
(`killed=3 escaped=2 owners=3/5`) on the round-81 base. The finding is the *class*: this line is
reproducible from a non-source subject, so it cannot be cited as evidence of provenance.

## 3. Record audit against committed bytes (secondary)

- `measured/terminal/c2.out`, `measured/terminal/mutant-owners-selftest.out`: reproducible exactly
  (`killed=5 … owners=5/5` exit 0; `pass=13 fail=0` exit 0).
- `measured/after/c2.out` last line reads `DEBT_MUTANT_OWNER_PRISTINE APPEND_DEBT_SELFTEST pass=34 fail=0 arms=34`,
  which **cannot** be produced by the terminal bytes: the summary print lost `arms={len(cases)}` in
  `c5a32443` (pre-report-gate arm 11 fullmatch). The terminal receipt carries the correct
  `pass=34 fail=0`. Intermediate receipt, superseded — no correction made, recorded as a
  reproducibility caution.
- `grade()` fails closed on a subject that repeats a mutated literal twice: `could-not-evaluate:
  M6: mutation site count 2` (observed while building `D`, exit 2). Fail-closed is right; it does
  mean a legitimate subject that prints the summary twice is un-gradable rather than killed.

## 4. What was not done

No repair, no edit to any lane file, no git/jj mutation (scratch repos only, `git rev-parse
--show-toplevel` verified as `<scratch>/repo*`). Tools installed: none (no pacman, no uv/npx needed).
Scratch `/fast/scratch/hyaku/kama-r86/MT02ForgeryArms/` removed before yield; evidence copied to
`.ufo/waves/round-86/w3/out/MT02ForgeryArms/evidence/` (332 KB).
