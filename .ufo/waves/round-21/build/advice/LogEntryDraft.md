VERDICT: confirm - round-21 LOG skeleton drafted in round-20 format; C1 and C2 motivating evidence reproduced; all measured values left as placeholders for the L1 official run.

# LogEntryDraft — round 21 (scribe seat, leaf, no lane edits)

Full draft text: `.ufo/waves/round-21/build/out/LogEntryDraft/LOG-round-21-draft.md` (text delivered there and below in summary; lane untouched).

## Motivating evidence checked

| Claim | Evidence | Command / source | Exit |
|---|---|---|---|
| C1 closure defect: unresolvable hash | `.ufo/reports/round-20/kama.md:7` cites `0957ce619789d13d894ef21bc863486bcb35b56c`; `git rev-parse --verify` MISSING; correct hash line 10 `0957ce619789d13bb5779606078fa1498114d2c7` | `git rev-parse --verify -q <h>^{commit}` in clone of `a29bb84` | 1 (missing), 0 (correct) |
| C1 closure defect: Landed omits 4 commits | Landed section lines 13-19 list `c7311039`, `04de7a8`, `9add96e`, `3ec5ea6`, `7a6bc91` only; `33a6777`, `0957ce6`, `92b1462`, `846e366` absent | `read` of report; closure `MANIFEST.json:10104-10112` | n/a |
| Closure record | round 20 closed `2026-10-21T10:16:40Z`, reviewer CloseKama20 (non-author), round commits list in `notes` | `read MANIFEST.json:10104-10112` | n/a |
| Audit raw counts | 9 defects: r10 landed-omitted 1; r18 landed-omitted 3; r20 unresolved-full-hash 1 + landed-omitted 4 | `python3 tools/report-landing-audit.py --lane-repo /tmp/…/lane --fleet-repo /home/vgpnk/Projects/shokunin --no-errata` (tool from `a29bb84`) | 1 (`status=failed`, `uncorrected=9`) |
| Audit with errata | 9 corrected, 0 uncorrected, 0 unmatched/invalid | same tool, no `--no-errata` | 0 (`status=clean`) |
| Audit selftest | 15 cases, 0 failed | `python3 tools/report-landing-audit.py --selftest` | 0 |
| Default invocation | from scratch clone outside fleet layout: `could-not-evaluate … not a git repository`; default fleet root = `here.parent` | `python3 tools/report-landing-audit.py --no-errata` (no flags) | 2 |
| C2 TreeCap debt | `corpus/lessons/round-19.md:53-55` "Symlinked sonames are unpinned (TreeCap)"; `SKILL.md:647-648` names TreeCap as a limit | `git show 7a6bc91:…` | n/a |
| C2 code delta | `tools/kama-llamacpp-live.py` +28 / −0 at `7a6bc91..a29bb84`; `install_links()` at line 205, `install_links_sha256` at 1309 | `git diff --stat 7a6bc91 a29bb84 -- tools/kama-llamacpp-live.py`; `git show a29bb84:…` grep | 0 (diff exit 0; removed-lines grep exit 1 = no removed lines) |
| Syntax of changed Python | `tools/report-landing-audit.py`, `install-links-grid.py`, `check-receipt.py`, `kama-llamacpp-live.py` at `a29bb84` parse | `ast.parse` one-liner per file | 0 each |
| Gate and grid CLI | `check-receipt.py --selftest` and `--expect-install-links-sha256` exist; grid `--arm {frozen,current,both} --json --selftest` exist | `grep add_argument` on `a29bb84` files | n/a |

Not executed by this seat (official L1 run per assignment): grid run, gate selftest run, `--report 21=` gate. Cell counts (frozen 0/9, current 9/9, controls 3/3, null 0/1) and "9 VALID + 1 NOT-EVALUATED, 90 mutations" come from the draft commit message [INFERENCE until L1 runs them].

## Draft LOG entry (summary of the out-dir file)

- Heading `## round 21 — report landing audit and symlink-aware install identity (2026-10-21)`, bullets only (round-20 style, `LOG.md:1199-1252`).
- Declared claims C1 calibration 7 → `<7|8>`, C2 operability 8 → `<8>`; round start `7a6bc91`, draft `a29bb84`.
- Motivation C1 and C2 as above; changed files as above; no measured numbers.
- Official commands listed with exit placeholders `<E1>`–`<E7>`; measured results `<…>`; measured commits `<MEASURED_C1_COMMIT>`, `<MEASURED_C2_COMMIT>`; landed hashes `<LANDED_HASH_1…N>`.
- Limits line with `<closed | narrowed>` for TreeCap placeholder.

## Notes for L1

- Use explicit `--lane-repo`/`--fleet-repo` when auditing from anywhere but the fleet layout; the default exit 2 is fail-closed behaviour, not a defect.
- Landed list must include every round-21 lane commit by `kama-shokunin` (round-20 omission pattern repeats if omitted).
- Do not write the C2 gate counts into LOG until the grid/gate run from the committed tree exits as the grid header predicts (`--arm frozen` exit 1, `current` 0 expected).

## Artifacts and tooling

- `.ufo/waves/round-21/build/out/LogEntryDraft/LOG-round-21-draft.md` — draft entry (4025 B).
- `.ufo/waves/round-21/build/out/LogEntryDraft/audit-noerrata.txt`, `audit-errata.txt`, `selftest.txt`, `default-noerrata.txt` — captured outputs of the commands above.
- `.ufo/waves/round-21/build/out/LogEntryDraft/report-landing-audit.a29bb84.py` — copy of `tools/report-landing-audit.py` at `a29bb84` (sha256 `a60acc3a2444eddb34122d84f8d88cd0bcc5c6b103c90f2ca2e9ef330c28df9d`).
- Tools installed: none (stdlib python3 and git only). Scratch `/tmp/kama-r21-LogEntryDraft` removed at end of run.
