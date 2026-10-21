# ExecSecondLanded — second `## Landed changes` section (open item O: only first section read)

Seat: `CloseKama22.ExecSecondLanded-2`, round-23 falsify wave, lane kama-shokunin @ `245a37f69628c2c6bb29bbf17897d8fb5946c857` (verified: `git rev-parse HEAD` in `/tmp/kama-r23w2/ExecSecondLanded` returned exactly that hash). No lane-tracked file, index, or `.jj` touched.

## Verdict: FALSIFIED (item confirmed live in both arms)

The committed arm still reads only the first `## Landed changes` section. With a second such section it (a) keeps a false `landed-omitted` for a commit cited only there — annotated `cited_elsewhere: true`, i.e. the authors knew this class exists — (b) stays completely silent on an unresolvable checkable token cited only there (exit 0, clean), and (c) drops the `landed-unresolved` kind for a 40-hex fake token cited only there. The frozen arm (blob `4fe9339f8fc3a4a4a479d9c938a850da12f1124d`) behaves identically: `landed_match` is unchanged by the round-23 build wave. All three harm-none controls pass in both arms, so the fault is specific to the second section, not a broken omission/token detector.

## Fixture

`out/ExecSecondLanded/second-landed-grid.py` — grid-style builder functions (one per case), each building fresh /tmp scratch lane+fleet repos (`GIT_CONFIG_GLOBAL=/dev/null`, `GIT_CONFIG_NOSYSTEM=1`, explicit identity, no network), verifying its own premise (premise failure → exit 2, never a verdict), then running an auditor subprocess (timeout 30 s). Grading target is the expected correct outcome per the tool's own docstring kinds (`tools/report-landing-audit.py:17-26`): a round commit cited in ANY `## Landed changes` section is not omitted; an unresolvable checkable token in ANY such section is `landed-unresolved` (plus `unresolved-full-hash` when 40 hex — the kind pair the repo grid itself demands for a fake inside a Landed section, `tests/report-audit/repo-state-grid.py:543-544`). Ambiguity-overwrite is a separate open item: every fixture token is verified absent from both repos, so the two items cannot contaminate each other. Ambiguity (`landed-ambiguous`) is deliberately not exercised here.

Cases (SL = fault, SLC = control, all with report committed at `.ufo/reports/round-1/kama.md`, cutoff = first-add 2000, round commits at 1000/1500):

| row | kind | layout | correct outcome |
|---|---|---|---|
| SL1-second-section-omission | fault | §1 cites A; §Notes; §2 cites B | exit 0, [] |
| SL2-second-section-unchecked-token | fault | §1 cites A; §2 cites only `abc123def012` | exit 1, [landed-unresolved] |
| SL3-second-section-token-kind | fault | §1 cites A; §2 cites only FAKE 40-hex | exit 1, [landed-unresolved, unresolved-full-hash] |
| SLC1-single-section-cites-all | control | one section cites A+B | exit 0, [] |
| SLC2-single-section-omission | control | one section cites A; B nowhere in text | exit 1, [landed-omitted] |
| SLC3-first-section-unchecked-token | control | `abc123def012` in §1 | exit 1, [landed-unresolved] |

## Evidence (run 2026-10-21, both arms)

Command:
```
python3 .ufo/waves/round-23/falsify/out/ExecSecondLanded/second-landed-grid.py --arm both \
  --save .ufo/waves/round-23/falsify/out/ExecSecondLanded/runs-second-landed.json
```
Observed: grid exit `1` (violations exist); frozen `faults=0/3 controls=3/3 tracebacks=0 timeouts=0 violations=3`; current `faults=0/3 controls=3/3 tracebacks=0 timeouts=0 violations=3`. Full document retained in `runs-second-landed.json` (`population_sha256 e4da8422…`, auditor sha256 frozen `09ecd63b…` / current `f228f174…`, `arms_identical: false` — the arms differ as files, yet not on this fault).

Per row (identical in both arms):

- SL1: exit `1`, `kinds=['landed-omitted']`, defect `{'cited_elsewhere': True, 'kind': 'landed-omitted', 'token': '29e8ea6…'}` — correct outcome exit 0 → NOT-MET.
- SL2: exit `0`, `kinds=[]` — an unresolvable 12-hex Landed citation passes clean → NOT-MET (correct: exit 1, landed-unresolved).
- SL3: exit `1`, `kinds=['unresolved-full-hash']` only — the `landed-unresolved` kind is dropped for a fake inside a Landed section → NOT-MET.
- SLC1/SLC2/SLC3: met in both arms (`exit=0 kinds=[]`; `exit=1 kinds=['landed-omitted']`; `exit=1 kinds=['landed-unresolved']`) — the tool's single-section verdicts are intact.

Root cause, current arm (path:line at `245a37f`):
- `tools/report-landing-audit.py:168-170` — `landed_match` returns `re.search(r"^## Landed changes[^\n]*\n(.*?)(?=^## |\Z)", text, re.S | re.M)` — quote: "`re.search`", i.e. first match only. Frozen arm identical at `:135-137` of blob `4fe9339f` (verified by `git cat-file blob` + diff of the two files: the function is byte-identical; the files differ elsewhere in git-isolation code).
- `tools/report-landing-audit.py:316` + `:323` — `section = … landed.group(1)`; `cited = set(ABBREV.findall(section))` — omission clearance and token checks see only that first section.
- `tools/report-landing-audit.py:331-337` — `cited_anywhere` scans the whole text but only feeds the `cited_elsewhere` annotation, so the false positive is emitted while knowingly annotated.

## What this does NOT verify

- Draft mode (`--report N=PATH`) with two sections — only committed-report mode was exercised.
- Rounds other than 1; the errata path (`--no-errata` throughout).
- `landed-ambiguous` in a second section — excluded on purpose (belongs to the separate ambiguity-overwrite item).
- The correct-outcome pairing for SL3 (both kinds) is mirrored from the repo grid's own F04 expectation (`tests/report-audit/repo-state-grid.py:543-544`), not a separately ratified spec; a union-all-sections fix and a refuse-ambiguous-report fix would both satisfy SL1/SL2, and this grid does not adjudicate between them.
- I did not rerun the selftest or rounds-10-22 ledger no-harm checks (L1's declared evidence; out of seat scope).

## Files written

- `.ufo/waves/round-23/falsify/out/ExecSecondLanded/second-landed-grid.py` (fixture, grid-style builders + both-arm runner)
- `.ufo/waves/round-23/falsify/out/ExecSecondLanded/runs-second-landed.json` (retained both-arm run document)
- `.ufo/waves/round-23/falsify/advice/ExecSecondLanded.md` (this report)

No tools were installed or upgraded (python3 + git already present; no pacman use).
