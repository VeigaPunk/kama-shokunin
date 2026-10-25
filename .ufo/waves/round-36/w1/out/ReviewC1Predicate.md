# ReviewC1Predicate

Axis: calibration. Compared `tools/round36-statement-audit.py` with `.ufo/waves/round-36/preregistration.json`. The counter was not edited. The predicate was not retargeted.

## Findings

No actionable defect.

### Byte identity

The C1 predicate sentence is byte-identical in both files.

Compared strings, all length 288, UTF-8 equal, no JSON escapes inside the sentence:

- `preregistration.json` claim C1 `predicate` (decoded; the surrounding JSON quotes are syntax, not part of the sentence)
- `tools/round36-statement-audit.py` `PREDICATE` (lines 17-22, adjacent literals)
- the same sentence in that file's module docstring (the line after `Predicate (identical in the preregistration, this file, and the receipt):`)

Python equality held for docstring vs constant, constant vs decoded JSON, and constant vs `json.raw_decode` of the source value. The sentence is:

```
A frozen r35 routed statement is corrected iff corpus/lessons/round-36.md contains a correction row naming its id, the counter re-derives the cited committed-byte fact, the correction row does not contain the token 429, and the r35 lesson blob and the r35 fleet report blob are unchanged.
```

`PREDICATE` is assigned once and not read at runtime. That does not split the two copies today. Identity is a static fact, not a check the counter enforces.

### Counting command

Canonical runtime: `/usr/bin/python3` (3.14.8) on `tools/round36-statement-audit.py`. That file does not re-exec another script. It is absent from tip `e5a8ececf3d60fd53b36bb74299693a29e8f74b6` (`git cat-file -e` exit 128); the command scores that tip with the working-tree counter, which is what the frozen command names.

Command:

```
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round36-statement-audit.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --tip e5a8ececf3d60fd53b36bb74299693a29e8f74b6
```

Line:

```
uncorrected 4 false_corrections 0 lesson_unchanged 1 report_unchanged 1 met False
```

Exit code: `1`.

That line matches `.ufo/waves/round-36/controls/c1-noop.out`. Exit `1` is the counter's not-met code (`main` returns 1 when `met` is false), not usage (`2`).

### Missing lesson

A missing lesson cannot meet the target. The target is C1 met: `met True` and exit `0`.

At tip `e5a8ececf3d60fd53b36bb74299693a29e8f74b6`:

- `git cat-file -e <tip>:corpus/lessons/round-36.md` exited 128, path does not exist.
- `git show <tip>:corpus/lessons/round-36.md` exited 128 with empty stdout.
- `git ls-tree -r --name-only <tip>` printed no `round-36.md` path.

Counter path for that absence (`tools/round36-statement-audit.py`):

- `git_show` returns `None` on non-zero (lines 49-58).
- line 278 coerces that to `""`.
- `rows_of` (lines 85-91) only keeps lines starting with `R35-S211:`, `R35-WORDS:`, `R35-MIRROR:`, or `R35-KEEP:`. An empty lesson yields no rows.
- `score` (lines 121-135) increments `uncorrected` for each missing row. `met` requires `uncorrected == 0` plus `false_corrections == 0` and both blob pins. Four missing rows force `met` false and exit 1.

The observed `uncorrected 4` is that path, not a crash and not a substituted file. Blob pins on this run are not hiding a pass: `corpus/lessons/round-35.md` at the tip is `428f1f8a0e8871022f7c1e8ea47e50ba5a8d6412` (`LESSON_BLOB`), fleet `HEAD:.ufo/reports/round-35/kama.md` is `6d8f317378ba6048d8a3dfb4944adaf24f341eea` (`REPORT_BLOB`), and the tip `ExecDisposition.md` blob is `9307c5d61c1942857a17cb259b4313460b37d0da` (`DISP_BLOB`). `lesson_unchanged 1` and `report_unchanged 1` match those pins. The fail is only the missing correction rows.

A git failure on the lesson path also cannot meet the target: `None` becomes `""`, and a missing blob pin would clear `lesson_unchanged` or `report_unchanged`. Both fail closed.

## Residual risk and verification gaps

- No round-36 receipt file holds a third copy. The docstring names one. That third-copy claim is unverified, not a mismatch between the two assigned files.
- The fleet report is read from hardcoded `/home/vgpnk/Projects/shokunin` `HEAD`, not from `--repo`/`--tip`. It matches `REPORT_BLOB` now. A later fleet HEAD move could flip `report_unchanged` without a lane change. It cannot turn this missing lesson into `met True`.
- This run does not saturate the positive arm. Rows that should pass `holds`, a `429` kill, or a rewritten r35 blob were not executed. `--selftest` was not run.
- No resume path was invoked. The counter only reads git. Working-tree status for the counter and the preregistration was clean after the run. No mutation.

## Recommendation

Do not edit the counter. The predicate sentence already matches. A missing `corpus/lessons/round-36.md` does not meet C1.

