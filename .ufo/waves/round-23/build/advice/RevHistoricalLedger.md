# RevHistoricalLedger: round-23 findings (read-only, no production edits)

Seat: CloseKama22.RevHistoricalLedger (leaf; no dispatch). Lane base master=4fe9339f; fleet HEAD=7f48c5ed.
Frozen base blob `tools/report-landing-audit.py` = `fcc255ce` (4fe9339f). Candidate = lane working tree (moving; see "Moving target").

## Answer

1. **At the current repository state the candidate cannot change any rounds 10-22 verdict.** For `--rounds 10-22` and `--rounds 10-`, the candidate's JSON, text and `--no-errata` JSON are byte-identical to base for all three candidate blobs I captured (`609902`, `eafb27`, `9755654a`, the last also checked in place).
2. **The clean verdict depends on the errata ledger.** Without errata, base and candidate both exit 1 with 9 uncorrected defects, the same as the round-22 raw audit. With the 9 rows applied, both exit 0 clean.
3. **The fix changes verdicts only when a repo-local trigger is present.** Neither repo has one. Scratch-clone probes show the direction of each change; base flips in every injected case (table below).
4. **History scan:** no commit in either repo has an `encoding` header, and none has invalid UTF-8 in subject, author or message. Non-ASCII subjects exist (lane 11, fleet 304). Only one lane non-ASCII subject is a kama round commit inside the audit window (round-16, valid UTF-8, decodes identically under both).

## Round-22 outputs and errata

- `.ufo/waves/round-22/report-source-fix/runs/80a6d07c/audit-historical-ledger.stdout` (exit 0): rounds 10-21, `status clean`, `defects 9`, `corrected 9`, `errata_rows 9`, `required_commits 49`.
- `.../audit-historical-raw.stdout` (exit 1, `audit-historical-raw.exit`): same audit without errata, `status failed`, `uncorrected 9`.
- Current base run, rounds 10-21: per-round result dicts equal the R22 ledger's dicts (python comparison: `True`). Round 22 is new since 80a6d07c: `required 5`, `defects 0`. Current 10-22: 13 reports, `required_commits 54` (= 49 + 5), `status clean`.
- `registry/report-landing-errata.tsv` lines 3-11 (9 rows; rounds 20, 18, 10). All corrections are lane/fleet commits. `errata_invalid 0` and `errata_unmatched 0` under base and candidate. The candidate's new 7-40-hex shape check on corrections accepts all 9.

## Identity: base vs candidate (commands: `python3 <script> --lane-repo /home/vgpnk/Projects/shokunin/kama-shokunin --fleet-repo /home/vgpnk/Projects/shokunin --rounds <R> [--no-errata] [--json]`)

| Input | Base `fcc255ce` | Candidate `609902` / `eafb27` / `9755654a` |
|---|---|---|
| `10-22 --json` | exit 0, 5803 bytes | byte-identical (all three) |
| `10-22 --no-errata --json` | exit 1, 9 uncorrected | identical |
| `10-22` text | `summary ... status=clean` | identical |
| `10- ` (all) | same as 10-22 (no kama.md for rounds >=23 at fleet HEAD) | identical |

## Trigger inventory (current repos)

- `refs/replace/*`: none (lane, fleet). `.git/info/grafts`: absent. Shallow: false. `objects/info/alternates`: absent. Object format: sha1. Tags: none.
- Promisor / partialclone config: none. Local config keys: no `log.*`, `i18n.*`, `core.sshcommand`, `remote.*.promisor`. `.mailmap`: none.
- Refs: lane 215 (1 head, 11 remotes, 203 `refs/jj/keep/<40-hex>`); fleet 22 (12 heads, 10 remotes). Bare short tokens cannot reach `refs/jj/keep/*` through DWIM. Probe: `git cat-file --batch-check` with `0957ce6` returns commit `0957ce61...`, not a ref.

## History scan (read-only `rev-list` + `cat-file --batch`; rows in `out/RevHistoricalLedger/history-scan.tsv`)

| Repo / scope | Commits | `encoding` headers | Non-ASCII subject | Non-ASCII author | Invalid UTF-8 |
|---|---|---|---|---|---|
| lane `master` (audited branch) | 96 | 0 | 11 | 4 | 0 |
| lane `--all` | 248 | 0 | 11 | 4 | 0 |
| fleet `HEAD` | 1025 | 0 | 304 | 1 | 0 |
| fleet `--all` | 1032 | 0 | 304 | 1 | 0 |

- Lane non-ASCII subjects, all valid UTF-8 (em dash or section sign):
  - In audit window: `726f737a942f` `round-16: falsify-wave repairs — ...` (kama-shokunin; matches the round-16 pattern, so it is in round 16's `round_commits`).
  - Outside window: kama round commits `35e9175f` (r9), `d0f5a2d2` (r8), `4bcae65a` (r7), `f396b989` (r6), `47f3aedd` (r4), `ea72c3ee` (r3), `c6199a25` (r1); `96bbd742` (kama-shokunin, not a round pattern); `ed135b3c` and `33b167ec` (ci, HOURS.md).
- Lane non-ASCII author lines (`João Pedro Veiga`, not kama, not round commits): `3d79fc57`, `836b0188`, `893e3c5d`, `5396a876`.
- Fleet: 304 non-ASCII subjects, mostly `rounds ledger: ...—...`. The audit reads fleet history only through `git log --format=%at` (`report_cutoff`) and `ls-tree`, so fleet subjects never reach a verdict.

## Trigger probes (scratch clones of the lane; real fleet read-only; rounds 10-22)

| Probe | Injected state | Base `fcc255ce` | Candidate `9755654a` |
|---|---|---|---|
| T1 | `refs/replace/40660352...` -> HEAD 4fe9339f | exit 1 failed: uncorrected 1 (round-22 `landed-omitted` 40660352, since the replacement carries a round-22 subject); errata_unmatched 1 (row 11); required 53 | exit 0 clean; required 54 |
| T1b | `refs/replace/40660352...` -> non-round 96bbd742 | exit 1 failed: uncorrected 0, errata_unmatched 1 (row 11). `--no-errata`: uncorrected 8 | exit 0 clean; `--no-errata`: uncorrected 9 |
| T3 | clone `config i18n.logOutputEncoding ISO-8859-1` | exit 1: `UnicodeDecodeError: 0xe3` traceback, no verdict | exit 0 clean; required 54 |
| T7 | clone `.git/info/grafts` = `33a6777866d0...` | exit 1 failed: unmatched rows 8-11; required 21 | exit 2 `could-not-evaluate: ... rewrites history` |
| control | none | identical to candidate | identical to base |

Predicted from code, not probed:
- `log.follow=true` may move `report_cutoff`.
- A promisor remote plus `core.sshCommand` would run through base lazy fetch; the candidate refuses partial clones.
- Invalid UTF-8 in a committed report: base traceback (exit 1), candidate exit 2.
- A tag named `master` shadows the branch in base; the candidate resolves `refs/heads/` first.
- A hex-named branch shadows a short token: base reports `found`, candidate raises EvalError. Probe: `git cat-file --batch-check` with bare `1234567` returned the branch's commit `71973a0d...`.

## Other checks

- Mailmap (scratch repo): `%an` = `Other Name` with or without `log.mailmap=false`; `%aN` = `Canon Name` either way. The audit reads only `%an`, so the candidate's `log.mailmap=false` is inert here.
- Ambiguity handling is unchanged: ambiguous lines are consumed first (`cand-audit-3.py:151-154`, same as `base-audit.py:122-125`); the new ref-shadow check runs only on resolved lines (`cand-audit-3.py:160-162`).
- Locale: base decodes git output with the locale codec (`text=True`); the candidate pins UTF-8. This environment's preferred encoding is UTF-8, so no difference here. A non-UTF-8 locale is [INFERENCE].

## Moving target

`tools/report-landing-audit.py` in the lane working tree changed during this review:
- `609902048b...` (901 lines) at 12:14;
- `17a670a936...` (hash only, not snapshotted);
- `eafb27e572...` (906 lines) at 12:15;
- `9755654acd...` (921 lines) at 12:19, unchanged at the last check (sha256 `79d9e124...`).

HEAD stayed `4fe9339f`. The lane's `git status` gained `?? tests/report-audit/`. The identity result above holds for the three captured blobs only. Re-run `--rounds 10-22` (about 2 s) against the final blob before integration.

## Not verified

- The selftest (`--selftest`) was not run by me, so the 50/50 claim is not re-checked.
- L1's fault grid (probes a-e) and the R22 `c1`/`c2` grids were not re-run.
- Blob `17a670...` was never captured.
- The "predicted from code" triggers and the non-UTF-8 locale behavior are inference only.

## Disclosures

- My first lane command, `git status --short --branch`, ran without `--no-optional-locks`. It may have refreshed the index stat cache; no content change was observed. Later lane git calls were read-only (`rev-list`, `cat-file`, `log`, `for-each-ref`, `ls-tree`, `show`, `config --list`, `rev-parse`, `hash-object`).
- Scratch clones (`/tmp/kama-r23/RevHistoricalLedger/clone-t1`, `clone-t1b`, `clone-t3`, `clone-t7`) were made with plain `git clone --no-hardlinks` (local path) and configured without `GIT_CONFIG_GLOBAL=/dev/null`. No fetch, hooks or network. They were removed after the probes. The audit runs used the scripts' own isolated environment.
- No installs or updates. Tools: git 2.56.0; Python 3.14.8 (already present).

## Files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-23/build/advice/RevHistoricalLedger.md` (this report).
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-23/build/out/RevHistoricalLedger/history-scan.tsv` (320 rows; the audit-window column is filled only for lane rows).
- Scratch only, not deliverables: `/tmp/kama-r23/RevHistoricalLedger/` (base and candidate snapshots, diffs, JSON outputs, probe outputs, `probe-mm/`, `probe-hx/`).

## Checks for the main agent after integration

- `python3 tools/report-landing-audit.py --lane-repo <lane> --fleet-repo <fleet> --rounds 10-22 --json` should be identical to base for the final blob.
- `--no-errata` should exit 1 with 9 uncorrected.
- Round 22 should be clean (`required 5`, `defects 0`).
