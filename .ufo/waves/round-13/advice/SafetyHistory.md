# SafetyHistory — round 13 preservation and stale historical-authority review

Seat: KamaR13.SafetyHistory (sentinel, author-side advice, not outside closure).
Scope: read-only review of preservation and stale-authority risk. I did not run any
gate, selftest, reproduce.py, fidelity.py, measure.py, build, or test. The only
commands I ran were read-only `git`/`sha256sum`/`grep` inspections, listed below.
C0 belongs to the orchestrator. Tools installed or updated: none.

Axes: (P) old bytes and anchors stay preserved; (A) no stale historical text acts as
current authority; (G) no old gate is executed or presented as freshly executed.

## Observed state (2026-10-20, during the wave)

- The round starts at `941bb32c3f591bc63cbf7579b2b6c552228307cd` (`inherited-state.json:2`).
- I compared `git hash-object` against `git rev-parse 941bb32:<path>` for 13 paths. All 13 were **same**:
  `corpus/QUALITY.md` (24d73eb…), `corpus/SOURCES.md` (6f68222…, before the L1 edit),
  `SKILL.md`, `LOG.md` (before the L1 append), `corpus/lessons/round-12{,-verifier-spotcheck}.md`,
  `.ufo/waves/round-12/{fidelity.py,reproduce.py,acceptance.json,frozen/expected.json,frozen/corpus/SOURCES.md}`,
  `.ufo/waves/round-11/frozen/before/corpus/SOURCES.md`, and `.ufo/round-10/SEAT-PROTOCOL.md`.
- Re-check later in the wave: `git status --porcelain` showed ` M LOG.md`, ` M SCORECARD.md`,
  ` M corpus/SOURCES.md`, a new `corpus/lessons/round-13.md`, and wave JSON files.
  `QUALITY.md` was still `24d73eb…`, so KQ16 had not yet landed.
- `git diff --numstat 941bb32`: LOG.md `28 0`, SCORECARD.md `28 0`, SOURCES.md `4 0`.
  I compared the start blob's byte prefix by SHA-256: LOG.md **yes**, SCORECARD.md **yes**,
  SOURCES.md **NO**. The SOURCES.md additions are lines inserted at hunks
  `@@ -44`, `@@ -59` and `@@ -70`, i.e. the S033 registry row, a search-log line and a
  clarification. No old line was deleted.
- `git replace -l | wc -l` returned 0. No `.git/info/grafts` exists.

## Findings (most severe first)

| # | Sev | Exploit path / risk | Evidence | Smallest remediation |
|---|---|---|---|---|
| F1 | Medium (P) | The probe's mutant "reintroduced bad wording" might scan the whole file. KQ15 at `QUALITY.md:49` will always contain "distinct nonzero exits" and `git show <pinned-commit>`. A whole-file scan therefore either stays red forever or pushes a later editor to rewrite KQ15 to get green. That would delete the historical mistake. | `QUALITY.md:49` (raw read). The Measure spec item scopes the check to "active KQ16". | Scope the bad-wording detection to the KQ16 row or section only. Also assert that the start blob (`git cat-file blob 941bb32:corpus/QUALITY.md`, 8619 B, 49 lines, ends in LF) is an exact byte prefix of the final QUALITY. Then an append at EOF is the only passing shape, and any edit to KQ15 is caught. |
| F2 | Medium (A) | After KQ16 lands, two headers become stale: `QUALITY.md:43` "author-appended; no outside review yet" and `:45` "No earlier criterion is superseded". A reader could take them as current. Separately, an unqualified "supersedes KQ15" would remove KQ15's still-valid clauses: manifest/override, old-receipt erratum, the reject column, and KQ14. | `QUALITY.md:43,45,49`. Precedent for a qualified header: `:41` "KQ14 (supersedes KQ7's sufficiency, preserves its append-only rule)". | Do not edit lines 43 and 45. Open a new KQ16 section that states three things: outside review now exists (`round-12-verifier-spotcheck.md` D1); KQ16 supersedes **only** the exit-class formulation and the capture/comparison formulation; all other KQ15 clauses stay in force. |
| F3 | Low-Med (G) | Live-looking invocation text for the old gate still exists: `SKILL.md:396` (gate entry and `--selftest`), `fidelity.py:5-7` usage, `LOG.md:675` and `round-12.md:201` "Executed once: python3 …/reproduce.py". A seat asked to "inspect actual round12 code" could run it. That violates the spec ("No … re-executing fidelity.py") and, at closure, `PROTOCOL.md:415-417`. | The paths and lines above, found by grep. | Change no files. Cite exit facts only as static or receipt evidence: `fidelity.py:24-25` (exit map), `:319` (`exit_code` mapping) and `:272` (`cat-file blob`); `SKILL.md:396`; `acceptance.json` (blob b15846c…). Label them "receipt/static, not freshly executed". |
| F4 | Info (A, C0) | C0 is owned by the orchestrator. The fleet prompt `kama-round-13.md:223-225` asks the lane to turn every routed defect into a fix **or say why not**. Silence on C0 would be a report-conformance gap. Editing fleet files would be a scope breach. | Fleet commit `62b225e` (2026-10-20 01:40:51 -0300) put "verify its committed evidence … never execute a sibling's gate" at `scripts/hyaku/closure-prompt.md:30-32`. The round-12 closure commit `941bb32` is later (01:46:26 -0300). [INFERENCE] The round-12 closure was rendered from the prompt as it stood before that fix. | Report: "C0 → orchestrator; observed fleet commit 62b225e; lane makes no change." `round-13.md:21-22` already says this. Make sure the fleet report repeats it. To avoid a repeat of C0, the two literal assertions should be recountable with plain `git cat-file blob` plus grep. The round-13 closure (`closure-prompt.md:26-28`) can then re-measure without running lane code. Do not register measure.py as a gate. |
| F5 | Low (P) | A claim that "old bytes were preserved as a byte prefix" would be false for SOURCES.md. The registry-row insert is in mid-file. It is line-preserving only. | The SOURCES.md prefix check above returned NO, with numstat `4 0`. The only line anchor into SOURCES found is `round-11-verifier-spotcheck.md:213` → `SOURCES.md:6–7`, which these inserts do not shift. Round 12 used the same convention (`round-12-verifier-spotcheck.md:151`). | In LOG and the lesson, say "no old line or row cell changed or deleted (numstat +4/−0)", not "byte-prefix". |
| F6 | Low (A) | The new SCORECARD "Planned — supersedes earlier planned statements" drops the explicit round-11 line "K05 remains runtime-dependent". | `git cat-file blob 941bb32:SCORECARD.md`, line 254. The round-13 append only says that runtime restoration remains operator-dependent. | Optional: add "K05 stays runtime-dependent". The history itself is retained. |
| F7 | Info (A) | `.ufo/round-{6,7,8,9}/SEAT-PROTOCOL.md` line 1 still reads "L1-issued, binding on all 64 seats" with no archival banner. Only round 10 has one (`round-10/SEAT-PROTOCOL.md:1-7`). The round-13 read list does not include these files (`kama-round-13.md:164-166`). | Line 1 of each file (via `sed -n 1p`). Disclosed as residue at `round-12-verifier-spotcheck.md:151`. | No change this round: it is outside the fixed denominator of two, and editing would alter old bytes. Leave it as disclosed residue. |
| F8 | Info (A) | The stale quality basis is `round-12.md:268-269`: "quality improved (fail-capable exact-source repair…)", i.e. gate machinery. Citing it would contradict closure item 3. | `round-12-verifier-spotcheck.md:149`. In the current drafts, `round-13.md:55-61` and the LOG append cite the D4 entry (`served-identity-crosswalk.md:87`) and claim no new quality delta. | Compliant as observed. Keep any report quality text tied to `served-identity-crosswalk.md:87`, never `round-12.md:268`. |

Not sustained: changing the code in `fidelity.py`. The exit map 1/2/2 is correct. `round-13.md:29` already rejects the change. Round-12 advice `QualityCriterion.md:26` also carries the bad wording, but it is immutable author advice and outside the denominator. The probe must not scan `.ufo/waves/*/advice`.

## Commands executed (read-only)

```sh
git -C <lane> status --porcelain [--untracked-files=all]; git rev-parse HEAD; git log --oneline -5
for p in <13 paths>; do git rev-parse 941bb32:$p; git hash-object $p; done
git diff --numstat 941bb32 -- LOG.md SCORECARD.md corpus/SOURCES.md
git cat-file -s/blob 941bb32:<p> | sha256sum  vs  head -c <n> <p> | sha256sum
git diff -U1 941bb32 -- corpus/SOURCES.md; git diff -U0 941bb32 -- LOG.md SCORECARD.md
git replace -l | wc -l; test -e .git/info/grafts; git config --get-regexp ...
git log -1 941bb32; git -C <fleet> log -1 62b225e; git -C <fleet> log -8 -- templates PROTOCOL.md scripts/hyaku*
wc -l / tail -c1 corpus/QUALITY.md; sed -n 1p .ufo/round-{6..9}/SEAT-PROTOCOL.md
git cat-file blob 941bb32:SCORECARD.md | grep -n -i -A4 planned
```

I also used static grep and reads over QUALITY, SKILL, LOG, the lessons, fidelity.py, reproduce.py, PROTOCOL.md, the fleet round-13 prompt and the closure prompt.

## Limits

- This is a snapshot taken mid-wave. KQ16 and measure.py were absent, so F1 and F2 are design obligations, not observed defects. Re-check after integration.
- I verified no semantic correctness and executed no gate.
- `[INFERENCE]` marks the C0 timing interpretation and the claim that `cat-file blob` is unaffected by filters.
