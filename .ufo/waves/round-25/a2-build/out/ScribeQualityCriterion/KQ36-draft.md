# Draft criterion row KQ36 — registered counting command re-run at the landed tip

Seat: ScribeQualityCriterion (kama round 25, attempt 2, wave 1 build).
Target file: `corpus/QUALITY.md` (appended as a new row; no existing line moves).
Routed defect: registered M-series mutation source is stale at the measured auditor.

## Row text (exact table format of QUALITY.md, four columns)

| ID | Admit only when | Reject or limit when | Motivating lesson |
|---|---|---|---|
| KQ36 | A counting command cited by a SCORECARD row is re-run, with the registered command pasted, at the round's landed tip before the row's value stands; an instrument that cannot evaluate (its unique-match guard aborts, exit 2) is reported as stale and the row is unverified at that tip — never a pass. | A SCORECARD row keeps its value while its cited counting command is stale at the landed tip; a could-not-evaluate or exit-2 abort is recorded as a pass, hidden, or counted as zero defects; the re-run happens at any revision other than the landed tip. | `lessons/round-24-verifier-spotcheck.md` §2 (registered M-series mutation source stale at the measured auditor); `preregistration.json` C1 (count command `registered 27 stale 2` at efe58e96 → `registered 28 stale 0` at 1fc41e34); `SCORECARD.md:1166` (registers `python3 tests/report-audit/isolation-mutants.py --json`) |

Scope: this rule covers only counting commands cited by a SCORECARD row. It adds
no universal claim about mutation-testing scores or any other instrument class.

## Red/green demonstration plan (C1 command at efe58e96 versus the tip)

Both commands run from the repo root of a sandbox clone pinned to the commit.
Count command (preregistration.json C1.command):

```
python3 -c "import importlib.util as u;s=u.spec_from_file_location('m','tests/report-audit/isolation-mutants.py');m=u.module_from_spec(s);s.loader.exec_module(m);src=m.AUDIT.read_text();bad=[n for n,o,_ in m.MUTANTS if src.count(o)!=1];print('registered',len(m.MUTANTS),'stale',len(bad),bad)"
```

SCORECARD-registered command (SCORECARD.md:1166):
```
python3 tests/report-audit/isolation-mutants.py --json
```

Red (efe58e96, pre-repair):
- Count command: `registered 27 stale 2 ['M11-listing-surrogates', 'M17-ref-shadow']`, exit 0.
- Registered command: exit 2, `could-not-evaluate: M11-listing-surrogates: pattern matches 0 times`, no mutant run.

Green (tip 1fc41e34, repair landed):
- Count command: `registered 28 stale 0 []`, exit 0.
- Registered command: exit 0, all 28 mutants evaluated (killed/surviving listed).

## Evidence pointers (all observed this round, fresh)

- `preregistration.json` C1 (registered command, before/after target, proof-narrowing rules).
- `preregistration-amendment-2.json` C1.before_reverified (`registered 27 stale 2` at efe58e96, exit 0).
- `corpus/lessons/round-24-verifier-spotcheck.md` §2 lines 80-82.
- `corpus/SCORECARD.md:1166` (counting command registered for the isolation row).
- Commits: efe58e96 (red) and 1fc41e346853afd98cbd7010af5db4e54dc877f7 (green tip).
