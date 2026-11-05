# MT02ForgeryArms — C2 input forgeries (round 86, w3, attack seat)

Lane `kama-shokunin`, target tip **bafae7afb41843564ac2468d28beb8e0bb98e8e6** read as committed bytes
(`git archive | tar -x`) into `/fast/scratch/hyaku/kama-r86/MT02ForgeryArms/copy`; copy hashes equal
the committed blobs, so every probe ran on the record's bytes:

```
f20279c6874bc4f6ff44dd810257dce87028dd140d43786ae93a257c2befeb73  tools/round86-mutant-owners.py
3d3b3a07f6efcd02f9a8ebcdbc477afcb291ef91d7e0d25f2166cd7af8228019  tools/round81-append-debt.py
```

No repair, no lane write, no git/jj mutation (fixture repos only, each `git rev-parse --show-toplevel`
asserted to itself). Tools installed: none.

## Baselines

| probe | exit | line |
|---|---|---|
| `round86-mutant-owners.py --selftest` | 0 | `DEBT_MUTANT_OWNERS_SELFTEST pass=13 fail=0` |
| `… --repo <lane> --rev bafae7af… --work <scratch>/work/live` | 0 | `DEBT_MUTANT_OWNERS mutants=5 killed=5 escaped=0 invalid=0 arms=34 cardinality=ok owners=5/5` |
| `.ufo/waves/round-86/count.py c2 --repo . --rev bafae7af… --work <scratch>/work/counter` | 0 | same line (relays `measured/terminal/c2.out` exactly) |

Plan says "10 arms"; the committed instrument has 13. The three extra arms are the post-freeze `M6`
repair (`stderr-noise`, `summary-without-arms-field`, `no-arms-line-disclosed-limit`), disclosed in
`corpus/lessons/round-86.md` §M6 and counted `13/0` in the SCORECARD row. Reconciled, not a defect.

## (a) Fully consistent forgery — population the source does not have

| subject | printed | classify | instrument CLI |
|---|---|---|---|
| `A1`: 4 arms deleted, 4 duplicates padded (30 distinct arms) | `arms=34 expected=34 fail_lines=0` / `pass=34 fail=0` / rc 0 | `escaped` | `mutants=5 killed=5 escaped=0 invalid=0 arms=34 cardinality=ok owners=2/5` **exit 1** |
| `A2`: same, claims 40 | `arms=40 expected=40` / `pass=40 fail=0` / rc 0 | `escaped` | `arms=40 … owners=2/5` exit 1 + `DEBT_MUTANT_OWNERS_FINDING population arms=40 != declared=34` |
| `F`: 4 arms deleted, padded to 34, owning FAIL lines string-matched from its own source | green pristine, one reconcilable owning FAIL line per mutant | `killed` on declared owner | **`DEBT_MUTANT_OWNERS mutants=5 killed=5 escaped=0 invalid=0 arms=34 cardinality=ok owners=5/5` exit 0** |

**Survives: `A1`, `A2` at the classifier, and `F` outright — the instrument's exact frozen target line
and exit 0 are reproducible from a subject with 30 distinct arms and no real failure semantics.**
`A1` differs from a full certificate in one field (`owners=2/5`); `A2` is stopped only by the
hardcoded `DECLARED_POPULATION = 34` pin, so a forgery at exactly 34 is invisible. A consistent
*fabricated kill* (`a3`) is equally accepted (`killed` on the declared owner).

## (b) ARMS line naming an owning arm that never printed

`ARMS_RE` (`arms=`, `expected=`, `fail_lines=` only) carries no arm identity, so the nearest
instantiations were run:

- `b1` ARMS `fail_lines=1`, no FAIL line, rc 1 → `killed summary-cardinality` (`!= 0 FAIL lines`)
- `b2` ARMS `fail_lines=0`, owning FAIL line printed, rc 0 → `killed summary-cardinality`
- `b3` no ARMS line, owning FAIL line printed, green rc 0 → **`escaped`**
- `b4` FAIL line names a foreign arm → `invalid` (`exit 1 without the declared owning arm`)
- `b5` consistent fabricated kill, arm never executed → `killed`
- `b6` ARMS line extended with `owner=…` (unparseable), claims 1 owning failure, none printed, rc 0 → **`escaped`**
- `b7`/`b8` same unparseable line with real FAIL lines → `killed` on the owner; the cardinality lie is never reported
- `b9` unparseable ARMS + summary `arms=34`, rc 0 → **`escaped`**

**Survives: `b3`, `b6`, `b9`.** A printed ARMS line outside the frozen shape is treated as *absent*,
so every reconciliation clause silently lapses.

## (c) Printed FAIL lines exceed summary fail

- `c1` ARMS `fail_lines=1`, 2 FAIL lines, rc 1 → `killed summary-cardinality`
- `c2` no ARMS line, summary `fail=0`, 2 FAIL lines, rc 0 → **`escaped`**
- `c3` no ARMS, 2 FAIL lines vs `fail=1`, rc 1 → `killed` on the owner, excess unreported
- `c4` 2 FAIL lines == `fail=2` but rc 0 → `invalid` (`exit 0 with fail=2`)

**Survives: `c2` only**, i.e. only where the ARMS line is absent (already pinned as the
disclosed-limit arm). With an ARMS line present the clause holds.

## (d) Right population, mutant effect absent

`D2`: no arms dropped or padded (34 real arms), M2 (`deletion != accepting`) applied, failure line
suppressed, `fail` zeroed → `arms=34 expected=34 fail_lines=0`, `pass=34 fail=0`, rc 0,
probe `cases=34 internal_failures=1` → `classify -> ('escaped', …, 'green summary')`.
Contrast `C` (same M2, un-forged bytes): exit 1 with the owning FAIL line → `killed`.
**Survives: yes.**

Aggregate over the 18 classifier probes in `out/MT02ForgeryArms/evidence/probe-classify.out`
(plus `D2`, measured separately): 7 escaped (`a1 a2 b3 c2 d b6 b9`), 9 killed, 2 invalid.

## Disclosed limit vs observation

`corpus/lessons/round-86.md` §M6 says a consistent forgery is "not distinguishable by a text-only
classifier" and routes it to round 87. **Matched — and two things the disclosure does not say:**
(1) consistency is sufficient, not necessary: `b6`/`b9`/`b3`/`c2` escape with visibly inconsistent
output because unparseable means un-reconciled; (2) the limit reaches the certificate: `F` shows the
frozen `DEBT_MUTANT_OWNERS … owners=5/5` line proves the printer's output reconciles, not that the
graded revision owns 34 live arms. The instrument's only non-textual leg is `--rev` committed-byte
reading; provenance of the printed line is out of reach, as disclosed. Not claimed: that the record's
own terminal line is forged — the counter replay at `bafae7af` is green on committed bytes and the
before-receipt is red (`killed=3 escaped=2 owners=3/5`) on the same instrument.

## Record audit (secondary)

- `measured/terminal/c2.out` and `mutant-owners-selftest.out`: reproducible exactly.
- `measured/after/c2.out` PRISTINE line reads `APPEND_DEBT_SELFTEST pass=34 fail=0 arms=34`, **not
  reproducible** from terminal bytes (summary lost `arms={len(cases)}` in `c5a32443` for
  pre-report-gate arm 11). Intermediate receipt; terminal supersedes. Recorded, not corrected.
- `grade()` fails closed when a subject repeats a mutated literal twice (`could-not-evaluate: M6:
  mutation site count 2`, exit 2) — correct direction, but a legitimate subject printing the summary
  twice is un-gradable rather than killed.

Report: `.ufo/waves/round-86/w3/MT02ForgeryArms.md`
Evidence: `.ufo/waves/round-86/w3/out/MT02ForgeryArms/` (`findings.md`, `evidence/` incl. fixtures,
probe matrix, instrument runs).
