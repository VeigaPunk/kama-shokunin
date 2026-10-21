VERDICT: partial - KQ28 is drafted and grounded in the round-20 defects; the audit reproduces them (exit 1) and passes a corrected draft (exit 0), but three tool gaps bound what exit 0 proves.

# QualityCriterion: KQ28 draft (text only; lane not modified)

Executed in lane `a29bb84` with scratch fixtures; outputs and fixtures under `.ufo/waves/round-21/build/out/QualityCriterion/`. Scratch `/tmp/kama-r21-QualityCriterion` deleted. No tool installed or updated (python 3.14.8, git 2.56.0 observed).

## Draft row (append to `corpus/QUALITY.md` as a new round-21 table; no existing row changes)

| ID | Admit only when | Reject or limit when | Motivating lesson |
|---|---|---|---|
| KQ28 | A round report's `## Landed changes` cites, by a >=7-hex prefix, every lane commit authored `<lane>-shokunin` whose subject starts `round-N:` or `checkpoint(rN)` and that is no later than the fleet commit adding the report; every full 40-hex token in the report is a git object in the lane or fleet repo, and every token in that section resolves as a commit. Both `python3 tools/report-landing-audit.py --rounds N --report N=<draft> --no-errata` (round N raw) and `python3 tools/report-landing-audit.py --report N=<draft>` (prior rounds, errata in force) must exit 0, run on the uncommitted draft immediately before the fleet commit. | A draft passes on exit 0 alone when: a body-only >=7-hex abbreviation is unchecked by the tool and was not hand-checked with `git cat-file -t`; a 40-hex token resolving only to a tree is accepted (tool tests `cat-file -e`, not type); round-N defects are cleared by errata rows added for round N; `--rounds N` is paired with default errata (a pass-looking shape that fails on prior-round rows); a lane commit made after the draft check is not re-checked; a numeric false positive (e.g. `1234567` in Landed) is errata-corrected rather than reworded. | `.ufo/reports/round-20/kama.md` line 7 cites `0957ce619789d13d894ef21bc863486bcb35b56c` (no object; the correct `0957ce619789d13bb5779606078fa1498114d2c7` is at line 10) and its `## Landed changes` cites 5 of 9 required commits (omits `846e366`, `92b1462`, `0957ce6`, `33a6777`); `registry/report-landing-errata.tsv` round-20 rows; MANIFEST kama round-20 closure note (caller-supplied pointer, not re-read here). |

## Executed evidence (exit codes observed)

| # | Command (run from lane root) | Exit | Observed |
|---|---|---|---|
| 1 | `python3 tools/report-landing-audit.py --no-errata` | 1 | 9 defects: r10 x1, r18 x3, r20 x5 (`unresolved-full-hash 0957ce619789d13d894ef21bc863486bcb35b56c`; `landed-omitted` 846e366, 92b1462, 0957ce6, 33a6777) |
| 2 | `python3 tools/report-landing-audit.py` | 0 | 9 corrected, 0 uncorrected, status clean |
| 3 | `python3 tools/report-landing-audit.py --selftest` | 0 | `selftest cases=15 failed=0` |
| 4 | `--rounds 20 --no-errata` (committed r20) | 1 | round 20: required=9, defects=5 |
| 5 | `--rounds 20 --report 20=fixture-r20-controlled-draft.md --no-errata` (line 7 hash fixed, 4 bullets added) | 0 | required=9, defects=0 |
| 6 | same, bullet 846e366 removed | 1 | `landed-omitted 846e366…` (detected) |
| 7 | same, body-only `deadbeef` added | 0 | defects=0 (GAP: body abbreviation unchecked) |
| 8 | same, Landed bullet with `1234567` | 1 | `landed-unresolved 1234567` (false-positive class) |
| 9 | same, body fake 40-hex `0123…4567` | 1 | `unresolved-full-hash` (detected) |
| 10 | same, body tree `e8ced4d6…a4` | 0 | defects=0 (GAP: tree accepted; `git cat-file -t` = tree; `^{commit}` lookup exit 128) |
| 11 | `--report 20=<controlled draft>` (default errata) | 1 | 5 `errata-unmatched` rows: a corrected draft of a committed round orphans its own ledger rows |
| 12 | `--rounds 21 --report 21=<r21 minimal, no cite> --no-errata` | 1 | `landed-omitted a29bb84abbb8b4d328f5970a89e448330a3a42ac` (lane tip is required; author `kama-shokunin`, subject `round-21:`) |
| 13 | `--report 21=<r21 minimal>` (default) | 1 | same single defect |
| 14 | `--rounds 21 --report 21=<r21 cites a29bb84> --no-errata` | 0 | required=1, defects=0 (strict round-N self-check) |
| 15 | `--report 21=<r21 cites a29bb84>` (default) | 0 | clean; prior rounds corrected by errata |
| 16 | `--rounds 21 --report 21=<r21 cites a29bb84>` (default errata) | 1 | 9 `errata-unmatched` for rounds 10-20: `--rounds N` must not be used with default errata |
| 17 | `git cat-file -e 0957ce619789d13d894ef21bc863486bcb35b56c` | 1 | no object (the r20 line-7 hash) |
| 18 | `git cat-file -e 0957ce619789d13bb5779606078fa1498114d2c7^{commit}` | 0 | resolves |

Round-20 required set from `git log` (kama-shokunin, `round-20:`): 33a6777, 0957ce6, 846e366, 92b1462, c731103, 04de7a8, 9add96e, 3ec5ea6, 7a6bc91 = 9 (executed, `required=9`).

## Gaps the criterion must bound (executed)

1. Body abbreviations (cases 7) and tree-typed full hashes (case 10) pass. The criterion therefore names them as limits, not as checked.
2. Numeric tokens in Landed are flagged as unresolved hashes (case 8). The fix is rewording, not errata.
3. The `--rounds` override and default errata interact (cases 11, 16). The admission command is `--report N=<draft>` (defaults) plus `--rounds N --no-errata`, not `--rounds N` with errata.

## Limits and [INFERENCE]

- The audit's population is `kama-shokunin` plus `round-N:`/`checkpoint(rN)` only. `protocol-shokunin` integrator commits (`8bf99ca` round-18, `37bd4c5` round-19, seen in `git log`) are not required. Whether "every round commit" includes them is a criterion decision, not a tool result. [INFERENCE: read from the filter at `tools/report-landing-audit.py:92`, not exercised.]
- Draft cutoff is `time.time()`, so a commit landing after the draft check but before the fleet commit becomes required at fleet time. [INFERENCE: from `run`/`audit_round` cutoff logic; not executed.] Hence the re-run-before-commit clause.
- Passing KQ28 shows the structural citation check only. It is not a claim that the Landed prose is accurate (KQ14 semantic-human boundary remains).

## Artifacts

- `.ufo/waves/round-21/build/out/QualityCriterion/audit-runs.txt` (runs 1-3, exits recorded)
- `.ufo/waves/round-21/build/out/QualityCriterion/probe-runs.txt` (runs 4-16, exits recorded)
- `.ufo/waves/round-21/build/out/QualityCriterion/strict-r21-ok.txt` (run 14 repeated)
- fixtures: `fixture-r20-controlled-draft.md`, `fixture-r20-omit-one.md`, `fixture-r20-body-7hex-gap.md`, `fixture-r21-minimal.md`, `fixture-r21-ok.md`
