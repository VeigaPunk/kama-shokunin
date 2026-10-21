# Row F17 — errata-revision-correction (fault)

**Verdict: HOLDS.** The fault premise is real and reproduced in the frozen arm;
the expected outcome (exit 1, defect kind `unresolved-full-hash`) is the
semantically correct one; and near variants through the same correction channel
are closed in the committed auditor — every tested variant lands on exit 1
(conservative invalid) or exit 2 (refusal), never a flip to clean.

Auditor under test: committed blob at 245a37f69628c2c6bb29bbf17897d8fb5946c857
(`tools/report-landing-audit.py`, sha256 f228f1742013…). NOTE: the lane
worktree copy has uncommitted modifications (39+/23-); all runs used the
committed blob extracted to /tmp, not the worktree file. Frozen arm: blob
4fe9339f:tools/report-landing-audit.py (sha256 09ecd63bdc3a…). git 2.56.0.

## 1. Fault premise — REAL, observed in frozen

Hand-built equivalent fixture in /tmp/kama-r23w2/f17fix (no grid import):
lane = commit LC@1000 "round-1: work" + errata commit@1600 containing
`1\tunresolved-full-hash\t1234567890abcdef1234567890abcdef12345678\tHEAD\tev`;
fleet = report@2000 citing LC under `## Landed changes` and FAKE under
`## Notes`. Built with GIT_CONFIG_GLOBAL=/dev/null, GIT_CONFIG_NOSYSTEM=1,
explicit identities — matches the grid builder
(tests/report-audit/repo-state-grid.py:405-411) byte-for-semantics.

Observed, `python3 frozen-audit.py --lane-repo … --fleet-repo … --json --rounds 1`:
- **exit 0**, `"status": "clean"`, `corrected: 1`, `errata_invalid: 0` —
  the fabricated hash is laundered into a corrected defect. The row fails on
  frozen exactly as the wave claims (fault mode: verdict flip, not crash).

Mechanism (frozen blob :355-356): `lookup(repos, [e["correction"] for e in
errata if e["kind"] in RESOLVABLE], "^{commit}")` feeds every correction to
`git cat-file --batch-check`. `HEAD^{commit}` resolves to the lane tip → row
valid → defect corrected → exit 0. Confirmed the hole is a whole class, not
just HEAD: frozen exits 0 for `master` and `@` corrections as well (via
`--errata PATH`). (`HEAD~1`, `f^{commit}`, `:/text` exit 1 on frozen — git's
batch-check only resolves single-token revnames.)

Independent confirmation via the grid itself, run inside my clone at 245a37f6
(--case F17-errata-revision-correction --arm both): frozen exit=0 **met=False**;
current exit=1 **met=True** kinds=['unresolved-full-hash'], no traceback,
timeout, or marker execution.

## 2. Expected outcome is the CORRECT one

Committed auditor (tools/report-landing-audit.py@245a37f6 :390-391) looks up
only corrections matching `[0-9a-f]{7,40}`; `HEAD` never reaches git →
`status.get("HEAD") is None` → row `errata-invalid` → `status = 0 if
uncorrected==0 and not unmatched and not invalid` (:499-500) → **exit 1** with
`errata_invalid:[{…correction:"HEAD"…}]` and the defect still reported. Correct:
a symbolic name is no evidence that the cited 40-hex object exists; accepting
it lets a report launder fabricated citations through any lane ref.

Cosmetic note (not a defect): the defect still carries `corrected_by:[1]` and
`summary.uncorrected` is 0 — the verdict is driven solely by `errata_invalid`.
Honest but slightly odd JSON; verdict is right.

## 3. Near variants through the same channel (committed arm)

| Variant (correction field) | Committed | Assessment |
|---|---|---|
| `deadbee` = hex-named **tag** → other commit | exit 2 "citation deadbee names a ref" | refused; the bare pre-lookup (:139-142) + `parts[0].startswith(token)` guard (:161-163) catches ref-preferring resolution. Consistent with declared F13 refusal |
| `deadbee` = hex-named **branch** | exit 2 same | as above |
| 7-hex prefix that is a refname → **same** object | exit 0, clean | honest: the hex does name that object; no laundering |
| Uppercase hex of lane tip | exit 1 errata-invalid | stricter than git (hex is case-insensitive); conservative direction, cannot flip. (Worktree copy already case-folds.) |
| Fleet-only commit hash | exit 0 | consistent: `unresolved-full-hash` is defined cross-repo, so a fleet correction is in-contract; residual semantic softness noted |
| blob / tree hash | exit 1 | `^{commit}` peel fails → invalid |
| `:/text`, `master`, `HEAD~1`, `@`, `f^{commit}`, `@{u}` | exit 1 | non-hex → never resolved |
| 40-hex refname (update-ref accepts it) | n/a | git itself never resolves a bare 40-hex name to the ref (object-name rule wins → "missing"); spoof path dead |
| Invalid row on an **unselected** round | exit 1 | `invalid` is not scoped to `selected` rounds while `unmatched` is (:388 vs :396) — asymmetric strictness; fails more, never less. Residual observation |
| `--errata PATH` file (uncommitted) | exit 1 | same parse/apply path as committed blob |

No variant produced a traceback, timeout, program execution, or a flip to
clean that the semantics don't justify. The only exit-0 corrections were real
commit-object names, which is the defined contract.

## Not verified
- The wave's aggregate claims (frozen 0/26 faults, 8/8 controls; mutants
  22/24; selftest 50/50) — out of scope; only F17's arms were run.
- Frozen arm on V2–V15 battery beyond `master`/`@`/`HEAD~1`/`f^{commit}`/`:/text`.

## Files written
- This report.
- Scratch (outside lane): /tmp/kama-r23w2/{RowF17ErrataRevision,frozen-audit.py,
  current-committed.py,f17fix,f17v1..v14,errata-file.tsv,grid-f17.json}.

## Tooling
No installs or upgrades performed; existing git 2.56.0 / python 3.14 sufficed.
