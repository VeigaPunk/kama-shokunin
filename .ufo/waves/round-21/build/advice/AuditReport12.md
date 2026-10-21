VERDICT: confirm - the tool's round-12 result (0 defects, exit 0) matches my hand derivation; five tool blind-spot classes are real, and none fires on round 12
# AuditReport12 - C1 re-derivation for `.ufo/reports/round-12/kama.md`

Scope: lane `master` at a29bb84 (82 commits). Hand derivation from git first, tool second, 17 probe runs on temp copies; lane not modified. Evidence: `.ufo/waves/round-21/build/out/AuditReport12-6/` (`lane-master.psv`, `manual-derivation.tsv`, `hand-hash-check.json`, `probe-results.json`, `extra-probe-results.json`). Tools installed/updated: none (git, python3 stdlib).

## 1. Hand derivation (no tool)
- kama-shokunin commits on master, subject `round-12:` or `checkpoint(r12)`: **2**: `33f46685b418af868259952884e34b93633820cb` (ct 1792470952) and `1df80eab01bc5663deea65680673fef24f35d5b0` (ct 1792471040). Excluded: `941bb32` (protocol-shokunin, no colon).
- Fleet first add: `5ee71e4c0675d6e3dfc6d0cfd9b8d313ba845dee`, ct 1792471121 (`git log --diff-filter=A` rc 0; sole commit touching the path).
- Split: pre **2**, post **0**. Landed section cites both by full 40-hex (lines 24-25; line 20 also names `1df80ea`). Omitted: **0**.
- 40-hex tokens, 5 unique (`git cat-file -e`): lane rc 0 x5, fleet rc 1 x5. `7de1360` is a blob; the other four are commits.
- Landed hex tokens (`cat-file -t`): commit x2. Landed-unresolved: 0.
- 64-hex SHA-256 values are not objects (`cat-file -e` rc 128 in both repos). Checked as file digests: `9dc40d25...` = sha256 of `2f7303c:corpus/SOURCES.md` (blob `7de1360`, 18898 B); `52665cf2...` = sha256 of `1df80ea:.ufo/waves/round-11/frozen/before/corpus/SOURCES.md` (18793 B).
- Hand result: **0 defects**, all four kinds.

## 2. Tool vs hand
`python3 tools/report-landing-audit.py --rounds 12 --no-errata --json` -> rc 0; defects 0; required 2; post 0; round_commits 2; cutoff 1792471121; report_committed true; status clean. Exact agreement; no false positive or false negative on round 12.

## 3. Invisible-to-tool checks on round 12 (all pass)
- `2f7303c` (body) is a protocol source revision; `7de1360` matches its path and sha256. `79fa257` (body, line 13) is round-11 and the parent of `33f4668`: correct use, not cited as landed.
- `acceptance.json` @1df80ea: exit 0, ok true, measured_commit `33f4668`, head_before = head_after = `33f4668`.
- LOG bindings exact: round-12 headings at LOG.md:606 (@33f4668) and :672 (@1df80ea); hunk `@@ -670,0 +671,30 @@`.
- Landed row contents match touched files; S032 (SOURCES.md) and KQ15 (QUALITY.md) present @1df80ea.
- Gate/code/frozen bytes unchanged 33f4668 -> 1df80ea; round-11 frozen and spotcheck unchanged 79fa257 -> 1df80ea (`git diff --name-only` empty).
- D5: original SEAT-PROTOCOL (4413 B, sha e9fbaa02...) is an exact suffix from line 32.
- Push timing: origin/master reflog shows `1df80ea` entering at 1792471042, before the cutoff.
- Wave files cited in Swarm all exist @33f4668.
- [INFERENCE, not verifiable now] "initial tree clean" and "final lane status empty".

## 4. Probes: `--report 12=<temp copy>` (cutoff = now); round 12 has none of these inputs
| Probe | Edit | rc / defects | Verdict |
|---|---|---|---|
| P0 | none | 0 / none | control agrees |
| P1 | body fake lowercase 40-hex | 1 / unresolved-full-hash | TP |
| P2 | body fake UPPERCASE 40-hex | 0 / none | FN: `[0-9a-f]` only; git accepts uppercase |
| P3 | body tree OID `1df80ea^{tree}` | 0 / none | FN: any object type passes |
| P4 | Landed adds round-11 commit `79fa257` | 0 / none | FN: no round/author check |
| P5 | Landed row `33f4668` written UPPERCASE | 1 / landed-omitted `33f4668` | FP: correct citation unseen |
| P6 | Landed row `1df80ea` deleted | 0 / none | FN: "cited" = any token in section, incl. prose line 20 |
| P16 | Landed row `33f4668` deleted | 1 / landed-omitted | TP (no prose mention) |
| P7/P8/P12 | Landed `deadbee`; blob `7de1360` short/full | 1 / landed-unresolved | TP (`^{commit}`) |
| P9 | Landed fake full 40-hex | 1 / two kinds, one token | double count |
| P10 | body 41-hex | 0 / none | FN: length not checked |
| P13 | body short `deadbee` | 0 / none | by design: body abbreviations unchecked |
| P11 | Landed heading renamed | 1 / section-missing + 2 omitted | cascade |
| P14/P15 | Landed 7-hex prefixes | 0 / none | control agrees |

## 5. Out of population (not defects by the stated rule)
- Fleet `9a7867cc` (kama-shokunin, ct 1792469778, "round-12: kama dispatch evidence") touches only `.ufo/prompts/kama-round-12.md`. The tool reads lane commits only. [INFERENCE: intended scope.]
- `git log --all` (incl. `refs/jj/keep/*`): 3 round-12 subject hits, all accounted for. No hidden kama round-12 commit.

## 6. Verdict and fixes (not applied; lane untouched)
- Round 12: 0 defects, confirmed by hand and tool.
- Tool gaps in `tools/report-landing-audit.py`: lowercase-only regex (:50-51); any-type `cat-file -e` (:70-76); body full hashes unchecked for type (:116-118); "cited" = every token in section (:130); no round/author check on Landed commits (:126-137). Suggested: case-insensitive hex, `^{commit}` on body hashes, row-scoped Landed parsing, round/author check. [INFERENCE: value of each fix.]

## 7. Commands run (rc; python subprocess where noted)
- `git -C <lane> log --format=... master` rc 0 (82 lines); `git -C <fleet> log --diff-filter=A --format=... -- .ufo/reports/round-12/kama.md` rc 0; `merge-base --is-ancestor 5ee71e4 master` rc 0.
- `git -C <lane|fleet> cat-file -e|-t <tok>`: 40-hex lane 0 / fleet 1; 64-hex 128. `rev-parse 2f7303c:corpus/SOURCES.md` rc 0; `cat-file -s 7de1360` rc 0; blob sha256 rc 0.
- `git rev-parse 33f4668^` rc 0 (= 79fa257); `cat-file -e` and `rev-parse --verify` on UPPERCASE 33f4668 rc 0.
- `python3 tools/report-landing-audit.py --rounds 12 --no-errata --json` rc 0; P0-P16 via `--report 12=<file>`: rc as in section 4.
- `git reflog show --date=unix refs/remotes/origin/master` rc 0; `git diff -U0 33f4668 1df80ea -- LOG.md` rc 0; `git show 1df80ea:.ufo/waves/round-12/acceptance.json` rc 0.
