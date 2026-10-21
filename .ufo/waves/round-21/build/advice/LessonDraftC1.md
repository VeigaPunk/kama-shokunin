VERDICT: confirm - the round-20 defects are real: the audit fails raw (exit 1, 9 defects) and passes only with the errata ledger (exit 0); draft Mistakes rows M1-M3 are below.

# LessonDraftC1 — round-21 Mistakes text for the round-20 report defects

Scope: text only. Lane not modified. Scratch clone `/tmp/kama-r21-LessonDraftC1/lane` at `a29bb84abbb8b4d328f5970a89e448330a3a42ac`, removed at end. Draft: `.ufo/waves/round-21/build/out/LessonDraftC1/round-21-mistakes-draft.md` (not filed to `corpus/lessons/round-21.md`).

## Executed runs (exit observed)

| Command (run from scratch lane; fleet `/home/vgpnk/Projects/shokunin`) | Exit | Observed |
|---|---|---|
| `tools/report-landing-audit.py --no-errata --rounds 10-20` | 1 | `round=10 defects=1`, `round=18 defects=3`, `round=20 defects=5`; `defects=9 uncorrected=9 status=failed` |
| `tools/report-landing-audit.py` (errata on, default ledger) | 0 | `corrected=9 uncorrected=0 errata_unmatched=0 errata_invalid=0 status=clean` |
| `tools/report-landing-audit.py --selftest` | 0 | 15 cases, `failed=0` |
| `--no-errata --rounds 20 --report 20=<as-committed copy>` | 1 | 5 defects, same as fleet report |
| `--no-errata --rounds 20 --report 20=<copy with line-7 hash fixed>` | 1 | 4 `landed-omitted` remain |
| `git cat-file -e 0957ce619789d13d894ef21bc863486bcb35b56c^{commit}` | 128 | `Not a valid object name` |
| `git cat-file -e 0957ce619789d13bb5779606078fa1498114d2c7^{commit}` | 0 | resolves |
| `git ls-tree -r --name-only 37bd4c5 -- tools` | 0 | 6 files; no `report-landing-audit.py` |
| `git grep -c -e landed-omitted -e 'Landed changes' 37bd4c5 -- tools` | 1 | no match at base |

Outputs saved under `.ufo/waves/round-21/build/out/LessonDraftC1/`: `raw-run.txt`, `corrected-run.txt`, `selftest.txt`, `hashfix-only-run.txt`, `r20-as-committed.md`, `r20-hash-fixed-only.md`. The raw and corrected runs were executed in the scratch clone, which is now deleted; the commands above reproduce them.

## Findings

- **Splice (M1).** `.ufo/reports/round-20/kama.md:7` cites `0957ce619789d13d894ef21bc863486bcb35b56c` (`git cat-file` rc 128). Line 10 cites the real `0957ce619789d13bb5779606078fa1498114d2c7` (rc 0). Errata row 3 records the correction.
- **Omissions (M2).** Landed changes at `kama.md:13-19` list `c7311039`, `04de7a87`, `9add96e4`, `3ec5ea68`, `7a6bc911`. The audit reports `33a6777`, `0957ce61` (`cited_elsewhere: True`, line 10 and the measurement table), `92b1462`, `846e366` as `landed-omitted`. Their lane-log subjects are `round-20:` by `kama-shokunin`. Closure `221707d` lists the same four as D2.
- **Earlier omissions (M3).** r18: `101f3991` (line 19), `1c325b2`, `c6dc46f` (lines 26-27) are absent from Landed. r10: `40660352` is cited only at `round-10/kama.md:114` (`## Post-review fixes`), absent from Landed `:28-39`.
- **Captured-by.** Closure `221707d` (CloseKama20, non-author) found D1 and D2 by manual recheck and admitted with them routed `status-neutral` to r21. The base `tools/` directory has no Landed-coverage check (grep above, exit 1). Grep of the committed round-10 through round-19 spot-checks for `omit|coverage` found no Landed-coverage check. Round-19's table row "Cited commits exist, ancestors of branch" checks existence and ancestry, not coverage. [INFERENCE: this covers only the committed spot-check files; no other manual check is ruled out.]
- **Fix.** `tools/report-landing-audit.py` (added at `a29bb84`) fails the raw run (exit 1, 9 defects) and passes the corrected run (exit 0) only through the append-only errata ledger (9 rows, 9 matched, 0 unmatched, 0 invalid). The report itself is not rewritten.

## Limits (for the narrative)

- The audit cannot tell a wrong-but-real full hash from a right one: `unresolved-full-hash` accepts any object type (code read of `is_object` without a kind; not executed) [INFERENCE on consequence].
- Landed coverage is by ≥7-hex prefix and only for `kama-shokunin` commits with `round-N:`/`checkpoint(rN)` subjects. A commit under another subject or author is invisible to it (code read).
- An errata row makes the corrected run pass without any report change; the raw run stays the honest defect count.

## Tools

None installed or updated. Used the existing `git` and `python3` on the host.

## Routed to main

Insert the draft text from `out/LessonDraftC1/round-21-mistakes-draft.md` into `corpus/lessons/round-21.md` at L1 integration. I did not file it.
