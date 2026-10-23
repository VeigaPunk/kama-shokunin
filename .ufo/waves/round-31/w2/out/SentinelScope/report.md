```RESULTS
- `mkdir -p /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/out/SentinelScope /tmp/kama-r31w2/SentinelScope` — exit 0; verbatim output: (empty).
- `git -C /home/vgpnk/Projects/shokunin/kama-shokunin log --format='%H %an %s' 07794a4d..382d11b2107d335705875da1a4d889b074bd6fa6` — exit 0; verbatim tail:
  `54c6f4fe070c5d4edd994a8894277083be64118c kama-shokunin round-31: remap S180-S191 to the twelve measured source lines and drop the duplicate K31-14 row`
  `3b1e84f8212e136351f078b4d5c1cc170aaf12fa kama-shokunin round-31: chat-adapter surface — SKILL table, registry, 13 pinned source rows, knowledge entry, PROVINCE/QUALITY/README; wave-1 fragments + control receipts`
  `0e6f8ed6891c09d5208ac1fdcb294ed9a842832e kama-shokunin round-31: freeze — C1 chat-adapter counter + registry pins, C2 claim-row revision counter, preregistration, pilot receipts`
- `git -C /home/vgpnk/Projects/shokunin/kama-shokunin show --name-status --format='' 382d11b2107d335705875da1a4d889b074bd6fa6` — exit 0; verbatim tail:
  `A\t.ufo/waves/round-31/w1/out/DataA06/row.json`
  `M\tcorpus/SOURCES.md`
  `M\tcorpus/lessons/round-31.md`
- `git -C /home/vgpnk/Projects/shokunin/kama-shokunin show --name-status --format='' d45f947e289a8d5eeb1ccac78115cb70ca9cdc75` — exit 0; verbatim tail:
  `A\t.ufo/waves/round-31/c2/c2-b4f3edc0.json`
  `M\tLOG.md`
  `A\tcorpus/lessons/round-31.md`
- `git -C /home/vgpnk/Projects/shokunin/kama-shokunin show --name-status --format='' b4f3edc0bfc1f797dc3dceedfea9507ad5c7d3ea` — exit 0; verbatim output: `M\tSCORECARD.md`
- `git -C /home/vgpnk/Projects/shokunin/kama-shokunin show --name-status --format='' 54c6f4fe070c5d4edd994a8894277083be64118c` — exit 0; verbatim output:
  `M\tSKILL.md`
  `M\tcorpus/SOURCES.md`
  `M\tcorpus/knowledge/chat-adapter-outcomes.md`
  `M\tregistry/chat-param-outcomes-r31.json`
- `git -C /home/vgpnk/Projects/shokunin/kama-shokunin show --name-status --format='' 3b1e84f8212e136351f078b4d5c1cc170aaf12fa` — exit 0; verbatim tail:
  `M\tcorpus/SOURCES.md`
  `A\tcorpus/knowledge/chat-adapter-outcomes.md`
  `A\tregistry/chat-param-outcomes-r31.json`
- `git -C /home/vgpnk/Projects/shokunin/kama-shokunin show --name-status --format='' 0e6f8ed6891c09d5208ac1fdcb294ed9a842832e` — exit 0; verbatim tail:
  `A\t.ufo/waves/round-31/sources/llama.cpp-704366d/server-schema.cpp`
  `A\t.ufo/waves/round-31/sources/llama.cpp-704366d/server-task.cpp`
  `A\t.ufo/waves/round-31/sources/llama.cpp-704366d/utils.hpp`
- `git -C /home/vgpnk/Projects/shokunin/kama-shokunin status --short --untracked-files=all` — exit 0; verbatim tail:
  `?? .ufo/waves/round-31/w2/validate.err`
  `?? .ufo/waves/round-31/w2/validate.json`
- Changed-path allowlist scan (`git diff --name-only -z BASE TIP`, checking each result against `SKILL.md|SCORECARD.md|LOG.md|PROVINCE.md|corpus/*|registry/*|.ufo/waves/round-31/*|tools/*`) — exit 0; verbatim output: `paths_total=226 allowed=226 outside=0`.
- Committed-size scan (`git diff --name-only -z BASE TIP`; `git cat-file -s TIP:<path>` for each path; threshold 1,048,576 bytes) — exit 0; verbatim output:
  `OVERSIZE\t1201398\t.ufo/waves/round-31/w1/out/CriticIgnoredClass/raw.json`
  `checked=226 threshold_bytes=1048576 oversized=1 max_bytes=1201398 max_path=.ufo/waves/round-31/w1/out/CriticIgnoredClass/raw.json`
- Initial credential scan: extracted the changed paths from the tip with `git archive` into `/tmp/kama-r31w2/SentinelScope/committed-changes`, then ran `grep -rInE 'sk-[A-Za-z0-9]{20,}|api[_-]?key *= *[A-Za-z0-9]{16,}' <extracted-directory>` — recorded archive-pipeline status 0 and grep exit 1; verbatim output: `archive-exit=0` then `grep-exit=1` (no grep output).
- Confirming credential scan: repeated archive+grep with `set -o pipefail` into `/tmp/kama-r31w2/SentinelScope/committed-changes-checked` — archive pipeline exit 0, grep exit 1; verbatim output: `archive-pipeline-exit=0` then `grep-exit=1` (no grep output).
```
FINDING: Scope clean: **no** — all 226 committed paths are within the lane and allowed surfaces, but one changed file exceeds 1 MiB and the status snapshot contains uncommitted files beyond the two C1/C2 receipts.

LIMITS: The status output is a single snapshot taken while other wave-2 work was active; later status may differ. The credential check covers only the two requested patterns in the committed changed files, not other secret formats or uncommitted files.

## Findings table

| Finding | Evidence | Result |
|---|---|---|
| Commit `382d11b2107d335705875da1a4d889b074bd6fa6` | Adds round-31 census receipts and two W1 outputs; modifies `corpus/SOURCES.md` and `corpus/lessons/round-31.md`. Full `--name-status` receipt: `382d11b2107d335705875da1a4d889b074bd6fa6.show.txt`. | All paths within allowed surfaces |
| Commit `d45f947e289a8d5eeb1ccac78115cb70ca9cdc75` | Adds C1/C2 and hold receipts; modifies `LOG.md`; adds the round-31 lesson. Full receipt: `d45f947e289a8d5eeb1ccac78115cb70ca9cdc75.show.txt`. | All paths within allowed surfaces |
| Commit `b4f3edc0bfc1f797dc3dceedfea9507ad5c7d3ea` | Modifies `SCORECARD.md`. Full receipt: `b4f3edc0bfc1f797dc3dceedfea9507ad5c7d3ea.show.txt`. | Allowed |
| Commit `54c6f4fe070c5d4edd994a8894277083be64118c` | Modifies `SKILL.md` and `corpus/SOURCES.md`; adds/updates the knowledge entry and registry JSON. Full receipt: `54c6f4fe070c5d4edd994a8894277083be64118c.show.txt`. | All paths within allowed surfaces |
| Commit `3b1e84f8212e136351f078b4d5c1cc170aaf12fa` | Adds round-31 controls and W1 items/outputs; modifies `PROVINCE.md`, `SKILL.md`, and `corpus/{QUALITY.md,README.md,SOURCES.md}`; adds the knowledge entry and registry JSON. Full receipt: `3b1e84f8212e136351f078b4d5c1cc170aaf12fa.show.txt`. | All paths within allowed surfaces |
| Commit `0e6f8ed6891c09d5208ac1fdcb294ed9a842832e` | Adds round-31 preregistration/counters, pilot receipts, and pinned sources. Full receipt: `0e6f8ed6891c09d5208ac1fdcb294ed9a842832e.show.txt`. | All paths within allowed surfaces |
| Lane and allowed-surface bounds | 226 unique changed paths; all `git show` paths are repo-relative; allowlist result `allowed=226 outside=0`. | Pass |
| File-size threshold | `.ufo/waves/round-31/w1/out/CriticIgnoredClass/raw.json` is 1,201,398 bytes (>1,048,576). | **Fail** |
| Credential-shaped strings | Exact requested regex returned no matches (`grep` exit 1) across the committed changed-file snapshot. | Pass for these patterns only |
| Only two uncommitted C1/C2 receipts? | Status also showed `M SKILL.md`, untracked `.ufo/waves/round-31/c3/gate-after-progress.out` and `c3/r29-at-tip.json`, numerous `w2/out/**` files, `w2/validate.err`, and `w2/validate.json` (as well as this audit's raw files). | **No** |

Severity: Low (repository-scope hygiene; no credential-shaped match or out-of-surface committed path was found).

Exploit path: No security exploit was established. The observed path is ordinary commit inclusion of a 1.2 MB raw evidence file, with corresponding repository transfer/storage overhead.

Impact: The changed-file set stays within the requested lane surfaces, but the file-size condition fails and the uncommitted working tree is not limited to the two named receipts.

Smallest remediation: Remove or replace the oversized raw capture with a compact evidence record if retention requirements allow. No lane file was edited by this audit.

Overall scope clean: **no**.
