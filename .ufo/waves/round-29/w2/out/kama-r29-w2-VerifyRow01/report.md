# kama round-29 w2 — VerifyRow01: hand-verification of correction row 1 (C1)

Seat: kama-r29-w2-VerifyRow01 · 2026-10-23 · Lane repo: /home/vgpnk/Projects/shokunin/kama-shokunin (branch master, read-only; no git state mutated)

## Verdict

**confirmed-false** — hand-derived observed value: **`q:no-artifact`** (equals the correction row's last cell exactly).

Corrections table row verified: `513eba3ba51a142c9936553e3a85918345eb5c4c:SCORECARD.md:1454`

```
| SA29:SCORECARD.md:Q:f4c42debcc:0 | SCORECARD.md:20 | Q | `snapshot=20261014T124232Z prev=20260929T043044Z rows=3 model_ok=0 drift=3 transitions=16 exit=2` | ea72c3ea | quoted as live re-census output; no committed file at W holds this line | q:no-artifact |
```

The frozen counter itself was NOT run on the lane tree (per item bounds); every step below re-derives the counter's behavior from its text and applies it with independent commands.

## Evidence per step

### 0. Frozen inputs confirmed
- `sha256sum .ufo/waves/round-29/count-c1.py` → `fe11d599d064f5749c829394fc813f43921de2f9903e41c7217e3daa4b647383` — matches the frozen hash in the goal and `preregistration.json`.
- `refs/heads/master` = `513eba3ba51a142c9936553e3a85918345eb5c4c` (data commit); `git for-each-ref refs/replace` → empty, so the counter's `--no-replace-objects` is a no-op and plain git grep is equivalent.

### 1. Base statement located
`git show 2aa46e2481d2ec41a7ee5ed793fc50ae967a6e5d:SCORECARD.md` line 20 (base file has 1441 lines):

> `| **freshness** (worked round 2) | **6 → 7** | `snapshot` writes dated `kama-probe/v2` JSON and diffs tracked `registry/history/latest.tsv` into append-only `DELTA.md`; live re-census run: `snapshot=20261014T124232Z prev=20260929T043044Z rows=3 model_ok=0 drift=3 transitions=16 exit=2` — the 16 transitions are the honest record of 8 consumer files deleted from the box plus MODEL_OK→DEAD on the dead ports; stable re-run `transitions=0`; `tools/test-snapshot.sh` md5 `860f26ac05938cdfc1a8816eff1570b4` → `RESULT pass=24 fail=0` | round 3 |`

Row pointer cell `SCORECARD.md:20` ✓.

### 2. Writing revision W via blame
`git blame --line-porcelain 2aa46e2481d2ec41a7ee5ed793fc50ae967a6e5d -L 20,20 -- SCORECARD.md` →
`ea72c3eae4ecc68dab2b0a08153c9c1d2e16df21` ("round-3: re-census — derived --ufo-src, registry cut to live rows, corpus errata", committer time 1791981983 = 2026-10-14 09:46:23 -0300). `merge-base --is-ancestor ea72c3ea 2aa46e2` → exit 0 (W is a strict ancestor of base). Row W cell `ea72c3ea` ✓.

**Sid semantics note:** the sid's digest field is NOT a commit prefix. Per the frozen extractor (`extract()` in count-c1.py: `lsha = hashlib.sha256(line.encode()).hexdigest()[:10]`), it is the sha256 (first 10 hex) of the exact base line text. I reproduced it independently: `sha256(line 20 text)[:10]` = `f4c42debcc` ✓, and `f4c42debcc` occurs for exactly one line across both base files (SCORECARD.md:20), so the duplicate-suffix scheme (`#1`, …) is not triggered and the sid maps uniquely to line 20. "W's prefix matches the sid" is therefore satisfied only via the row's separate W cell (which matches blame); the sid itself encodes (file, class, line digest, span index).

### 3. Q class rule applied by hand at W
Docstring rule (count-c1.py): a backticked span 6–200 chars containing a digit and either `=` or (a space and one of met/registered/counted/stale/observed/verified/RESULT), not starting with python3/python/bash/sh␣/git/node/`./`/`tools/`/`/`; HOLDS iff the span occurs verbatim in ≥1 blob of tree W other than SCORECARD.md, SHONEN.md, LOG.md, corpus/**. Failure observed string: `q:no-artifact`.

Span classification on line 20 (my own reimplementation of RE_Q + filters): 3 qualifying spans in order — Q#0 `snapshot=20261014T124232Z prev=20260929T043044Z rows=3 model_ok=0 drift=3 transitions=16 exit=2` (95 chars), Q#1 `transitions=0`, Q#2 `RESULT pass=24 fail=0`. My statement is Q index 0 → `SCORECARD.md:Q:f4c42debcc:0` ✓ (and the second committed row's sid `…:2` is consistent with the same enumeration). `tools/test-snapshot.sh` (excluded prefix) and the md5 span (no `=`/keyword) are correctly not Q. The row's token cell is byte-identical to the extracted span ✓.

Check at W with the frozen excludes:
`git grep -F -n -e '<span>' ea72c3eae4ecc68dab2b0a08153c9c1d2e16df21 -- . ':(exclude)SCORECARD.md' ':(exclude)SHONEN.md' ':(exclude)LOG.md' ':(exclude)corpus'` → **exit 1, no output** → statement does NOT hold at W → observed value `q:no-artifact`, hand-derived.

Honesty search (whole tree at W, no excludes): the span DOES occur verbatim at W in exactly two places — `LOG.md:239` (`snapshot: snapshot=20261014T124232Z …`) and SCORECARD.md itself (line 11 at W, the same self-assessment line). Both are in the counter's excluded evidence classes, so the frozen rule marks the statement false at writing; the measurement quoted is nevertheless corroborated by the committed LOG.md of W (the statement is imprecise evidence, not a fabricated measurement).

### 4. Correction row validity
- Last cell `q:no-artifact` == counter's Q failure string (check(): `return p.returncode == 0, ("ok" if p.returncode == 0 else "q:no-artifact")`), exactly, no whitespace/backtick drift ✓.
- Row sits under the frozen heading `## Round 29 — self-assessment corrections` at the tip; tip SCORECARD.md starts with base bytes byte-for-byte (append-only ✓); exactly 11 rows under the heading; sid appears exactly once; all 11 row sids unique ✓.
- Cross-check: Q#1 (`transitions=0`) DOES hold at W (same grep → exit 0), consistent with no correction row for it and with exactly 11 committed rows for 11 mismatches.

## Findings by severity

1. **Minor (wording, not validity):** the row's cause cell says "no committed file at W holds this line". Literally false: `ea72c3ea…:LOG.md:239` holds it verbatim. Accurate phrasing: "no committed file outside the counter's excluded evidence classes (SCORECARD.md/SHONEN.md/LOG.md/corpus\*\*) at W holds this line". The cause cell is free text and is not one of the frozen predicate's validity conditions (first cell sid, last cell exact observed value, unique sid, under frozen heading, names a base mismatch) — the row remains a valid correction under the frozen rules.
2. **Note (item phrasing, no defect):** "confirm W's prefix matches the sid" — the sid digest is the base line's content sha256 (`f4c42debcc`), not W's prefix; W (`ea72c3ea`) is carried in the row's fifth cell and matches blame exactly.

## Residual risk / verification gaps
- Did not execute the frozen counter on the lane tree (item bounds); behavioral equivalence rests on reproducing `extract()`/`check()` logic for this one statement by hand (shown above).
- `git grep -F` semantics assumed identical to the counter's (same git binary, empty refs/replace, `.` pathspec from repo root — same CWD used).
- Only row 1 was in scope; the other 10 rows and the fresh-clone receipt were not re-derived here.

## Tooling
No tools installed (operator 2026-10-19 channel unused): system `git 2.56.0` and `python3 3.14.8` sufficed; no pacman touched.

A copy of this report lives at `.ufo/waves/round-29/w2/out/kama-r29-w2-VerifyRow01/report.md`.
