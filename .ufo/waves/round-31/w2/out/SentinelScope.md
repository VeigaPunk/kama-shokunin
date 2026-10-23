```RESULTS
- `git -C /home/vgpnk/Projects/shokunin/kama-shokunin log --format='%H %an %s' 07794a4d..382d11b2107d335705875da1a4d889b074bd6fa6` — exit 0; tail: `54c6f4fe070c5d4edd994a8894277083be64118c ...`, `3b1e84f8212e136351f078b4d5c1cc170aaf12fa ...`, `0e6f8ed6891c09d5208ac1fdcb294ed9a842832e ...`.
- `git show --name-status --format=''` for each of the six listed commits — exit 0 for all; full raw receipts are in `.ufo/waves/round-31/w2/out/SentinelScope/<commit>.show.txt`.
- Changed-path allowlist and size scans — exit 0; `paths_total=226 allowed=226 outside=0`; one oversize: `OVERSIZE\t1201398\t.ufo/waves/round-31/w1/out/CriticIgnoredClass/raw.json`.
- `grep -rInE 'sk-[A-Za-z0-9]{20,}|api[_-]?key *= *[A-Za-z0-9]{16,}'` over the archived changed-file set — archive pipeline exit 0, grep exit 1 (no matches).
- `git -C /home/vgpnk/Projects/shokunin/kama-shokunin status --short --untracked-files=all` — exit 0; included `M SKILL.md`, untracked C1/C2 receipts, C3 receipts, numerous `w2/out/**` files, and `w2/validate.err` / `w2/validate.json`.
```
FINDING: Scope clean: **no** — all changed committed paths stay within allowed surfaces, but one file exceeds 1 MiB and the C1/C2 receipts were not the only uncommitted lane files in the captured status.

LIMITS: The status was one snapshot while other wave-2 work was active. The secret scan covers only the two requested patterns and only committed changed files.

| Finding | Evidence | Result |
|---|---|---|
| Commit path bounds | Six commits listed by the requested log command; per-commit name-status receipts are saved in `.ufo/waves/round-31/w2/out/SentinelScope/`. The allowlist scan found 226 changed paths, all repo-relative, `outside=0`. | Pass |
| File-size bound | `.ufo/waves/round-31/w1/out/CriticIgnoredClass/raw.json`: 1,201,398 bytes, exceeding 1,048,576 bytes. | **Fail** |
| Credential-shaped strings | Requested regex returned no matches (`grep` exit 1). | Pass for these patterns only |
| Only two uncommitted receipts? | No. In addition to `.ufo/waves/round-31/c1/c1-382d11b2.json` and `c2/c2-382d11b2.json`, status showed `M SKILL.md`, two C3 files, numerous wave-2 output files, validation files, and audit raw files. | **No** |

Severity: Low (repository-scope hygiene; no credential-shaped match or out-of-surface committed path found).

Exploit path: None established. The observed issue is ordinary inclusion of a 1.2 MB raw evidence artifact, causing repository transfer/storage overhead.

Impact: File-size criterion fails, and the working tree contains more uncommitted files than the two named receipts.

Smallest remediation: Replace or remove the oversized raw capture if evidence-retention requirements allow. No lane file was edited by this audit.

Overall scope clean: **no**.

Full command manifest, output tails, per-commit summaries, and raw logs: `.ufo/waves/round-31/w2/out/SentinelScope/report.md` and sibling receipt files.
