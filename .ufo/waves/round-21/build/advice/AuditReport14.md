VERDICT: confirm - independent hand re-derivation of round-14 C1 defects finds 0 defects; tool output matches exactly; no false positive, no false negative, and no tool-invisible defect found on the checks run.

Scope: `/home/vgpnk/Projects/shokunin/.ufo/reports/round-14/kama.md`, lane repo `/home/vgpnk/Projects/shokunin/kama-shokunin` (master), fleet repo `/home/vgpnk/Projects/shokunin`. Lane untouched; all commands read-only. Scratch `/tmp/kama-r21-AuditReport14` deleted after use. Tools installed: none.

## Hand derivation (not via the tool)

1. Round-14 lane commits, `git -C <lane> log --format='%H|%an|%ct|%s' master` filtered to author `kama-shokunin` and subject `^round-14:` or `^checkpoint(r14)` — exit 0, exactly 2:
   - `e545ed99aaa519196a2a7779b0a293b2ce4c765c` ct=1792478292 "round-14: add fail-closed offline Ollama evidence replay"
   - `06cc6dbea42b88849fb1808d40ae38a08dced21c` ct=1792478463 "round-14: record measured replay capability and precedence controls"
   Same 2 under `git log --all` (exit 0); both `merge-base --is-ancestor` of master (exit 0).
2. Fleet commit first adding the report: `git -C <fleet> log --diff-filter=A --format='%H %ct' -- .ufo/reports/round-14/kama.md` — exit 0: `52c833d19cf2429c47ccd57623470833e66e1484 1792478534`. It is the ONLY commit ever touching the report and the only add (checked with `--all` too).
3. Split: both commits ct <= 1792478534 → 2 required (pre-report), 0 post-report.
4. `## Landed changes` cites: full-hash tokens `06cc6dbe…` (lines 17, 22) and `e545ed99…` (line 21). Both required commits cited by >=7-hex prefix → 0 landed-omitted. No other 7..40-hex token in the section.
5. Token resolution: all three distinct 40-hex tokens in the report (`e545ed99…`, `06cc6dbe…`, `e1b3d746dbfd2100b61c67b6389217252592460f`) resolve via `git cat-file -e` in the lane repo (True/True/True); none resolve in the fleet repo (expected — lane objects). Both Landed-section tokens resolve as commits (`^{commit}`) in the lane. → 0 unresolved-full-hash, 0 landed-unresolved. Section present → 0 landed-section-missing.

Hand defect set: **empty (0 of 4 kinds)**.

## Tool comparison

`python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/report-landing-audit.py --rounds 14 --no-errata --json` — exit 0: `defects: []`, `round_commits: 2`, `required: 2`, `post_report: []`, `cutoff: 1792478534`, `status: clean`. **Exact match with hand derivation — no false negative, no false positive.**

Errata interplay: same run without `--no-errata` exits 1 with `errata_rows: 9, errata_unmatched: 9`. Not a round-14 defect: all 9 registry rows target rounds 20/18/10, out of the requested `--rounds 14` scope, so they are correctly reported unmatched. Registry path is lane-relative `registry/report-landing-errata.tsv` (default in tool `run()`); note it lives in the LANE repo, not a fleet-root `registry/`.

## Tool-invisible defect probes (all negative)

- Cited-but-other-round: the two cited commits have subjects `round-14: …` — they are this round's own commits, not another round's.
- Wrong-hash-to-unrelated-object: `06cc6dbe^` == `e545ed99` (work then receipt, as the Landed table describes); `e1b3d746…` is a real commit "round-13 verifier spot-check …" ct=1792473289, ancestor of `e545ed99` — consistent with its "initial tree" use (lines 13, 44). Its ls-tree claim verified: `git -C <lane> ls-tree e1b3d746… -- tools/kama-ollama-evidence.py` exit 0, empty output (tool genuinely absent at start-tree).
- 64-hex SHA-256 (invisible to both tool regexes — verified `FULL` does not match it): claimed cases digest `4a4de0b85009c42804e43c8ae8833bd6f0673edc71ae5ec8baa1e3201e158ae4` recomputed from `git show e545ed99…:tests/ollama-evidence/cases.json` and from `06cc6dbe…` — both match exactly (rc 0).
- Stray abbreviations: zero 6..39-hex tokens outside the Landed section, so nothing abbreviated escapes the tool's 40-hex-anywhere / 7..40-in-Landed policy on this report.
- Audit input integrity: fleet worktree report == HEAD (`git status --porcelain` and `git diff HEAD` both empty, exit 0); single add commit makes the cutoff unambiguous.
- Commit content matches Landed-table claims: `e545ed99` touches `tools/kama-ollama-evidence.py`, `tests/ollama-evidence/cases.json`, `corpus/knowledge/ollama-evidence-replay.md`, `corpus/lessons/round-14.md`, `QUALITY.md`, `SKILL.md`; `06cc6dbe` touches `.ufo/waves/round-14/{acceptance.json,frozen/precedence-only-red.py,preservation.json,sources-*}`, `LOG.md`, `SCORECARD.md`, `corpus/lessons/round-14.md`.
- Both commits authored and committed as `kama-shokunin <kama@shokunin.local>`, matching the report's claim.

## Limits

- Master-only scope (tool and hand run share it): `--all` shows no extra matching commits; dangling/unreachable objects were not enumerated (fsck skipped to keep the read-only footprint trivial). [INFERENCE: no hidden round-14 commit exists off-master.]
- Report prose claims like "Lane was clean after that push" are outside the mechanical defect kinds and were not verified. [INFERENCE-free: explicitly unexecuted.]
- Conclusion: for round 14 the tool is exact on all four mechanical kinds; the round-21 raw count's 9 defects correctly attribute none to round 14.
