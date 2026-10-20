# Round 13 — TeachingSweep (Operator Lessons & Unreflected Teaching Sweep for C1)

**Seat:** `KamaR13.TeachingSweep` (scout)  
**Lane:** `kama-shokunin` (root `/home/vgpnk/Projects/shokunin/kama-shokunin`)  
**Date:** 2026-10-20 UTC  
**Scope:** Discover and read `operator-*.md` lessons if any; sweep command/output or no-found file discovery; identify unreflected operator and verifier teaching relevant to calibration claim C1; zero inspection of secret paths. Read-only apart from this report.  
**Boundary:** Leaf scout report only. No subagent dispatch, no background jobs, no git commit/push, no execution of gates, tests, builds, linters, or formatters. Unrun $\neq$ pass. Tools installed/updated: none.

---

## 1. Executive Summary

1. **File Discovery Outcome (No `operator-*.md` Lessons Found):**
   - In `kama-shokunin`, exhaustive sweeps of the current working tree and full git commit history reveal **zero** files matching `operator-*.md` or `*operator*.md`.
   - In the parent fleet repository (`/home/vgpnk/Projects/shokunin`), exactly two files match `operator-*.md`:
     - `.ufo/scopes/shokunin-12h-20261014/operator-demand.md` (commit `cb3c1039`)
     - `.ufo/scopes/souji-mint-20261018/operator-demand.md` (commit `7bf2b1ab`)
     Both are campaign/mint demand scoping documents under `.ufo/scopes/`, **not** corpus lesson files (`corpus/lessons/operator-*.md` does not exist at fleet root or lane level).
2. **Relevant Operator & Verifier Teachings for C1:**
   - **Operator demand boundary:** "do not change global configs, but do it how it was written"; never touch operator config, host services, credentials, or secret paths; calibration is strictly bounded textual precision.
   - **Verifier spotcheck D1 teaching (`round-12-verifier-spotcheck.md`):** Append a precise KQ15 wording erratum (do not alter code or historical criterion bytes); separate finding IDs from exit classes (`source_mismatch=1; snapshot_tampered=2; source_unavailable=2`); separate capture from comparison (`capture: git show; comparison: git cat-file blob`).
   - **Quality attribution teaching (`round-12-verifier-spotcheck.md`):** Quality attribution belongs to Round 12 D4 knowledge interpretation (`served-identity-crosswalk.md`), never to gate or snapshot machinery. C1 is calibration-only (score 7 $\to$ 7, delta 0).
   - **C0 / Sibling boundary:** Sibling gate execution belongs to orchestrator/protocol owner; kama does not re-run sibling gates or alter closure prompts.
3. **Secret Path Hygiene:**
   - No credential, token, key, private configuration, or environment body was inspected. All searches were strictly constrained to public repository markdown and code structures.

---

## 2. Sweep Commands and Verifiable Output

### 2.1 Lane-Level Sweeps (`/home/vgpnk/Projects/shokunin/kama-shokunin`)

#### Sweep 1: Filesystem Pattern Match for `operator-*.md`
- **Command:** `find /home/vgpnk/Projects/shokunin/kama-shokunin -name 'operator-*.md'`
- **Exit Code:** `0`
- **Output:**
```text
(empty - 0 files found)
```

#### Sweep 2: Case-Insensitive Filesystem Match for `*operator*.md`
- **Command:** `find /home/vgpnk/Projects/shokunin/kama-shokunin -iname '*operator*.md'`
- **Exit Code:** `0`
- **Output:**
```text
(empty - 0 files found)
```

#### Sweep 3: Full Git History Search for `operator-*.md`
- **Command:** `git -C /home/vgpnk/Projects/shokunin/kama-shokunin log --all --name-only -- '**/operator-*.md' 'operator-*.md'`
- **Exit Code:** `0`
- **Output:**
```text
(empty - 0 commits found)
```
*Conclusion:* No file named `operator-*.md` exists or has ever existed in `kama-shokunin` history.

#### Sweep 4: Complete Inventory of Existing Corpus Lessons
- **Command:** `find /home/vgpnk/Projects/shokunin/kama-shokunin/corpus/lessons -type f | sort`
- **Exit Code:** `0`
- **Output:**
```text
/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/lessons/probe-mutation-matrix.md
/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/lessons/round-10-verifier-spotcheck.md
/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/lessons/round-10.md
/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/lessons/round-11-verifier-spotcheck.md
/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/lessons/round-11.md
/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/lessons/round-12-verifier-spotcheck.md
/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/lessons/round-12.md
/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/lessons/round-13.md
/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/lessons/round-1-citations.md
/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/lessons/round-1-critic.md
/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/lessons/round-1-relaunch-freshness.md
/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/lessons/round-1-safety.md
/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/lessons/round-1.md
/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/lessons/round-2.md
/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/lessons/round-4-recensus.md
/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/lessons/round-5.md
```
*Total lessons present:* 16 files. None are named `operator-*.md`.

---

### 2.2 Fleet-Level Discovery (`/home/vgpnk/Projects/shokunin`)

#### Sweep 5: Fleet Git History for `operator-*.md`
- **Command:** `git -C /home/vgpnk/Projects/shokunin log --all --name-only -- '**/operator-*.md' 'operator-*.md'`
- **Exit Code:** `0`
- **Output:**
```text
commit 7bf2b1ab7d7c86e9d9d7ac75a7b4bda5d49334df
Author: souji-shokunin <souji@shokunin.local>
Date:   Sun Oct 18 11:55:14 2026 -0300

    mint: souji lane wiring — operator demand, roster scan, conf lane, MANIFEST mint entry

.ufo/scopes/souji-mint-20261018/operator-demand.md

commit cb3c1039297b6dd112bb745bf8ba771e09910347
Author: protocol-shokunin <protocol@shokunin.local>
Date:   Wed Oct 14 21:24:03 2026 -0300

    ops: phase 1 — six-lane re-census closure, mint scaffolds, wave evidence

.ufo/scopes/shokunin-12h-20261014/operator-demand.md
```

#### Sweep 6: Reading the Discovered Fleet Demand Files
1. **`.ufo/scopes/shokunin-12h-20261014/operator-demand.md`:**
   - *Key Quotes:*
     - "do not change global configs, but do it how it was written" (line 5)
     - "content seats on m_composer, audit/review/scout/critic seats on grok, resolved via the global OMP seat table — never pin per-dispatch models beyond this split" (line 7)
     - "The program selects existing aliases only in this session. It does not save routing configuration or edit global files." (lines 10–11)
2. **`.ufo/scopes/souji-mint-20261018/operator-demand.md`:**
   - *Key Quotes:*
     - "It never touches operator config, credentials, or a lane with dirty or unpushed work." (lines 26–27)
     - "Axes: calibration, operability and coverage. A false 'safe' verdict is its worst failure." (lines 34–35)

---

## 3. Identification of Unreflected Teachings Relevant to C1

Examining operator demand excerpts, system directives, verifier spotchecks (`round-11-verifier-spotcheck.md`, `round-12-verifier-spotcheck.md`), and historical lessons (`round-1-safety.md`, `round-5.md`, `round-10.md`, `round-12.md`), seven distinct teachings directly constrain Calibration claim C1. If unreflected, each represents a known failure mode.

| Teaching Source | Operator / Verifier Directive | Potential Unreflected Failure / Trap | Required Reflection in Round 13 C1 Implementation |
|---|---|---|---|
| **Verifier D1** (`round-12-verifier-spotcheck.md:145–148`) | Finding IDs are distinct (`source_mismatch`, `snapshot_tampered`, `source_unavailable`), but exit classes are **not** distinct nonzero exits (`source_mismatch=1`, others share `2`). | **Trap:** Altering valid `fidelity.py` implementation to force exit codes 1, 2, 3, or retaining KQ15's false "distinct nonzero exits" claim. | **Reflection:** Do not touch code. Append KQ16 superseding only the wording discrepancy. Exact literal audit phrase: `source_mismatch=1; snapshot_tampered=2; source_unavailable=2`. |
| **Verifier D1** (`round-12-verifier-spotcheck.md:147`) | Historical snapshot capture used `git show`, while runtime comparison used `git cat-file blob`. | **Trap:** Citing `git show` as the comparator, or claiming `git cat-file blob` performed capture. | **Reflection:** Append KQ16 with exact literal audit phrase: `capture: git show; comparison: git cat-file blob`. Add S033 for `git cat-file` OUTPUT raw contents. |
| **Verifier Spotcheck** (`round-12-verifier-spotcheck.md:120–123, 149`) | D1 gate/snapshot machinery is verification plumbing, **not** new domain knowledge or quality gain. Quality improvement in Round 12 was grounded in D4 (`served-identity-crosswalk.md`). | **Trap:** Claiming Round 13 criterion fix improves `quality`, `operability`, or `expansion`. | **Reflection:** Keep C1 strictly on calibration (score 7 $\to$ 7, delta 0). Explicitly attribute prior quality credit to Round 12 D4, not to Round 13 criterion errata. |
| **Operator Demand** (`shokunin-12h-20261014:5`, `PROVINCE.md:45-49`) | "do not change global configs, but do it how it was written"; host service, route, and credentials are operator-owned. | **Trap:** Inspecting host listeners, calling external APIs, modifying system configuration, or executing probes against live ports. | **Reflection:** C1 is purely static/textual criterion correspondence against immutable git history; zero live network, zero host modifications. |
| **Gate Protocol & C0** (`round-12-verifier-spotcheck.md:44–47, 148`) | Canonical protocol forbids executing sibling gates; C0 belongs to orchestrator/protocol owner. | **Trap:** Re-running `fidelity.py`, executing sibling gates, or modifying orchestrator closure prompts. | **Reflection:** Skip all gate executions. Read code and acceptance receipts statically. C0 is noted and left to its owner. |
| **Fixed Denominator** (`claims.json`, `spec.json`, `round-13.md:11–13`) | Calibration denominator is strictly the two routed KQ15 propositions, not all criteria or the full corpus. | **Trap:** Expanding the denominator to all corpus prose or counting historical intentional errors as active defects. | **Reflection:** Fixed denominator = 2. Before missing assertions = 2; target after = 0. Measured delta = 0. |
| **Append-Only Rule** (`KQ3`, `KQ7`, `KQ14`, `round-12-verifier-spotcheck.md:147`) | Historical criterion and receipt bytes are immutable. Never rewrite line 49 of `QUALITY.md`. | **Trap:** Directly editing line 49 to erase the historical mistake. | **Reflection:** Leave KQ15 line 49 byte-intact. Append a new section `## Criteria added — round 13` with KQ16 explicitly superseding the two formulations. |

---

## 4. Secret Path and Credential Boundary Compliance

Per scout instructions: *“do not inspect secret paths”*.
- **No Private Paths Accessed:**
  - Neither `~/.config/opencode/opencode.json` nor systemd private environment files were opened or read.
  - No `.ssh`, `.gnupg`, `.auth`, `.env`, or credential-bearing tokens were queried or globbed.
- **Verification Integrity:**
  - All inspections were conducted using static filesystem queries (`find`, `glob`, `read`, `git log`) targeting only public `.md` files, `.json` descriptors, and git commits within the repository tree.

---

## 5. Limits & Grounding Disclaimers

1. **Discovery Limitation:**  
   The statement that *zero `operator-*.md` lesson files exist* is an observed empirical fact over the current filesystem and complete git history of `/home/vgpnk/Projects/shokunin/kama-shokunin`. It does not exclude the existence of operator demand notes in untracked external directories or other unmounted repositories `[INFERENCE]`.
2. **Static Review Only:**  
   No probe, test, gate, or benchmark script was executed to produce this report. All line citations, quote lengths, and exit mappings are derived from static text and committed historical receipts.
3. **No Tool Modifications:**  
   No tools were installed or updated during this assignment.
