VERDICT: confirm - sibling scan finds no duplicate work; grounds C1 in kotodama R31 errata precedent and contrasts C2 with repo anti-symlink gates.

## Evidence (Executed Sibling & Tool Findings)
- `install_tree`: 0 hits across all 20 sibling repos (`rg 'install_tree' *-shokunin`, exit 0); unique to kama-shokunin.
- `S_ISLNK` / `readlink` in siblings (`souji/tools/souji-rev-pin.py:140`, `tameshi/tools/witness-metadata.py:346`, `kagi/corpus/revision-audit.py:165`): siblings treat symlinks as attacks/escapes in Git worktrees and refuse them. Kama C2 operates on compiled binary installs (`~/.local/opt/llama-b11755`), where sonames require intra-directory symlinks terminating at pinned regular members without escaping `/`.
- Landed changes missing & audit precedent: `kotodama-shokunin` round 31 (`reports/round-31/closure-ledger.json:52-59`) logged finding `F-C31-1` for round 23 missing `## Landed changes`, ruling: "recorded, not repaired: filed round artifacts are never rewritten (AGENTS.md)...". Kama's `registry/report-landing-errata.tsv` exactly operationalizes this fleet precedent.
- `cat-file` & commit audits: `tabi` (`round-16-verifier-spotcheck.md:31`), `tsukuroi` (`round-19-verifier-spotcheck.md:25`), `tameshi` (`round-15-verifier-spotcheck.md:22`) pair `git cat-file -e` with `git merge-base --is-ancestor refs/heads/master`. `tsukuroi/tools/_revision.py:53` and `souji/tools/souji-landing-gate.py:170` set `GIT_OPTIONAL_LOCKS=0` and unset `GIT_*` to prevent lock contention.
- Executed commands in scratch (`/tmp/kama-r21-ConnectorSiblingLinks/lane` @ a29bb84):
  - `python3 tools/report-landing-audit.py --fleet-repo /home/vgpnk/Projects/shokunin --no-errata` -> exit 1 (`defects=9 uncorrected=9 status=failed`)
  - `python3 tools/report-landing-audit.py --fleet-repo /home/vgpnk/Projects/shokunin` -> exit 0 (`defects=9 corrected=9 status=clean`)
  - `python3 tools/report-landing-audit.py --selftest` -> exit 0 (`15 cases passed`)
  - `python3 tests/llamacpp-live/check-receipt.py --selftest` -> exit 0 (`9 VALID, 1 NOT-EVALUATED, 90 mutations rejected`)
  - `python3 tests/llamacpp-live/install-links-grid.py --arm current` -> exit 0 (`link=9/9 regular=2/2 type=1/1 null=0/1`)
  - `python3 tests/llamacpp-live/install-links-grid.py` -> exit 1 (frozen link 0/9 vs current 9/9; back_compat equal)

## Affected Axes
- **Calibration (7 -> 7/8)**: Grounding kama's append-only report errata in kotodama's fleet-wide R31 `F-C31-1` immutability precedent reinforces calibration without claiming false novelty or duplicating audit mechanisms.
- **Operability (8 -> 8)**: Adopting sibling best-practice (`GIT_OPTIONAL_LOCKS=0`, stripped `GIT_*` environment) in `tools/report-landing-audit.py` prevents lock contention during multi-agent concurrent audits.

## Proposed Move
One bounded synthesis:
1. In round-21 C1 lesson/narrative, cite `kotodama` R31 `F-C31-1` (`reports/round-31/closure-ledger.json`) as fleet precedent establishing that historical report defects are recorded in an append-only ledger rather than modifying filed reports, and cite `souji` (`souji-rev-pin.py:140`) / `tameshi` (`witness-metadata.py:346`) to contrast binary install soname chain verification against worktree anti-symlink gates.
2. In `tools/report-landing-audit.py`, harden `git()` to set `GIT_OPTIONAL_LOCKS=0` and strip `GIT_*` env (following `tsukuroi/_revision.py:53`), preventing flakes under concurrent fleet runs.

## Risks & Contradictions
- **Contradiction**: Siblings forbid symlinks to guarantee integrity; kama permits them. This contradiction is resolved by domain scope: repo checkouts have arbitrary file authority; library installs have ABI soname obligations bounded by same-directory terminal checks.
- **Risk**: Sibling `cat-file` checkers enforce branch ancestry (`merge-base --is-ancestor`), whereas `report-landing-audit.py:is_object` checks object presence. Expanding to ancestry would fail if reports cited valid unmerged commits or foreign tags; keeping `is_object` for `unresolved-full-hash` while checking log ancestry for `round_commits` is the correct middle ground.

## Verification & Deliverables
- Deliverables: `.ufo/waves/round-21/build/out/ConnectorSiblingLinks/sibling-overlap-scan.json` + raw output receipts.
- Scratch `/tmp/kama-r21-ConnectorSiblingLinks` deleted. No lane files modified. Tooling: no installs or updates.
Report: `.ufo/waves/round-21/build/advice/ConnectorSiblingLinks.md`
