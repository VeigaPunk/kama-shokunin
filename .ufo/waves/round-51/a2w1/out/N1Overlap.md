# N1Overlap — Sibling Overlap Scan and Adjacency Synthesis (Round 51)

Verdict: Sibling scan identifies 5 cross-lane citations across both surfaces (souji, tabi, kake, kotoba, kotodama) and 1 handoff (chousa), with 1 bounded synthesis move advancing adjacency from 7 without harming operability or calibration.

---

## 1. Evidence: Commands, Outputs, Exit Codes, File:Line

### Command 1: Fleet-Wide Sibling Repo Grep
Search all sibling lane repos (`/home/vgpnk/Projects/shokunin/*-shokunin`, excluding `kama-shokunin`) for the two Round 51 surfaces (`proc/.*exe` and `append-only-audit|disclosure`):
```bash
$ python3 -c "
import glob, os, re
sibling_dirs = [d for d in sorted(glob.glob('/home/vgpnk/Projects/shokunin/*-shokunin')) if not d.endswith('/kama-shokunin')]
pat_exe = re.compile(r'/proc/(\w+|\[pid\]|\$pid|<pid>|\{pid\}|\d+|\*)/exe|proc_pid_exe|/proc/\$!/exe|readlink.*proc.*exe')
pat_audit = re.compile(r'append-only-audit|append_only_audit')
pat_disc = re.compile(r'append-only-disclosures|receipt-rewrites')
# [Walk non-scratch .py and .md files]
"
```
Output:
- Surface 1 (`proc/.*exe`): 462 total occurrences across `souji`, `tabi`, `mado`, `kengaku`, `mori`, `tsukuroi`.
- Surface 2 (`append-only-audit` & disclosure ledgers): 8 tool/result occurrences across `kaidoku`, `chousa`, `kengaku`, `tabi`; 249 disclosure references including `kake` round-58 `c58_receipt_rewrites.py` and `build_ledger.py`.
Exit code: 0.

### Command 2: Kama Round 51 C2 Frozen Counter Verification
Run frozen counter `tools/round51-append-audit-v6-check.py` against a clean shared clone of `kama-shokunin` at build commit `138af25b963450b6520794995605fa7dbbcd87e0`:
```bash
$ S=/fast/scratch/hyaku/kama-r51/N1Overlap; mkdir -p "$S"
$ git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin "$S/lane"
$ python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round51-append-audit-v6-check.py \
    --repo "$S/lane" --tip 138af25b963450b6520794995605fa7dbbcd87e0 --scratch "$S"
```
Output:
```
tip=138af25b963450b6520794995605fa7dbbcd87e0
fixture=1 lane=1 scenarios=9/9 lost=142 disclosed=166 met=True
detail: fixture default-threshold: exit 1 (want 1) ok events=[('LOG.md', 'unrestored', 0, 0)]
detail: fixture arow-mutable: exit 0 (want 0) ok events=[('SRC.md', 'ungraded', 1, 0)]
detail: fixture arow-immutable: exit 1 (want 1) ok events=[('SRC.md', 'unrestored', 0, 0)]
detail: fixture code-span-pipe: exit 1 (want 1) ok events=[('SRC.md', 'unrestored', 0, 0)]
detail: fixture row-dropped: exit 1 (want 1) ok events=[('SRC.md', 'unrestored', 0, 0)]
detail: fixture disclosed: exit 0 (want 0) ok events=[('LOG.md', 'disclosed', 0, 1)]
detail: fixture bad-disclosure-1: exit 1 (want 1) ok events=[('LOG.md', 'unrestored', 0, 0)]
detail: fixture bad-disclosure-2: exit 1 (want 1) ok events=[('LOG.md', 'unrestored', 0, 0)]
detail: fixture bad-disclosure-3: exit 1 (want 1) ok events=[('LOG.md', 'unrestored', 0, 0)]
detail: fixture bad-disclosure-4: exit 1 (want 1) ok events=[('LOG.md', 'unrestored', 0, 0)]
detail: fixture partial-disclosure: exit 1 (want 1) ok events=[('LOG.md', 'unrestored', 0, 1)]
detail: fixture two-files-one-commit: exit 1 (want 1) ok events=[('LOG.md', 'disclosed', 0, 1), ('SRC.md', 'unrestored', 0, 0)]
detail: lane: tool v6 threshold 1 exit 0 events 106 disclosed_lines 166 permitted_lines 58; own lost lines in whole-file-graded files 142; ledger lines 166
```
Exit code: 0 (`met=True`).

### Command 3: Live Verification of `tools/append-only-audit.py` on Build Commit
```bash
$ python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/append-only-audit.py \
    --repo /home/vgpnk/Projects/shokunin/kama-shokunin --to 138af25b963450b6520794995605fa7dbbcd87e0
```
Output:
```
summary commits=341 files=96 events=106 restored=19 partial=0 unrestored=0 ungraded=36 disclosed=51 permitted_lines=58 disclosed_lines=166 bad_disclosures=0 ungraded_lines=205 regressed=0 vanished=0 unmatched=0 binary=0 bad_declarations=0
```
Exit code: 0.

---

## 2. Overlap Scan: Sibling Dispositions (Cite, Hand Off, or Ignore)

In accordance with the lane boundary directive ("report drift, never absorb"), overlaps are classified strictly into **CITE**, **HAND OFF**, or **IGNORE**.

### Surface 1: Process Image Identity via `/proc/<pid>/exe` (Claim C1, operability 8->8)
Kama implementation: S499 cites `proc_pid_exe(5)`; `tools/kama-llamacpp-live.py:server_exe(pid)` opens `/proc/<pid>/exe`, asserts `S_ISREG`, hashes the file descriptor, and extracts `(dev, inode)`; `tools/kama-live-replay.py` matches rerun `server_exe` against the extracted archive member `<work>/server/<member>` and checks `st_nlink == 1` to defeat decoy executions of external host binaries (round-50 seat J4Decoy).

| Sibling Lane | Relevant Files & Lines | Disposition | Boundary Rationale |
|---|---|---|---|
| **souji-shokunin** | `corpus/SOURCES.md:92,99` (S069, S076)<br>`corpus/knowledge/process-residue-observations.md:26-30`<br>`.ufo/waves/round-18/w2/ReopenS069.md:89-94`<br>`.ufo/waves/round-18/w1/SrcProcCwd.md:65,110` | **CITE** | Souji established that Linux kernel procfs appends `" (deleted)"` exclusively to `/proc/<pid>/exe` when an executable is unlinked (neither `cwd` nor `fd` carries this suffix). Kama cites S499 `proc_pid_exe(5)` ("attempting to open it will open the executable"); Kama should cite Souji's S076 as prior fleet verification of the man-page authority, recognizing that `/proc/<pid>/exe` path text ending in `" (deleted)"` confirms an unlinked binary image. |
| **tabi-shokunin** | `corpus/knowledge/webmcp-chromium-loopback-round-16.md:35`<br>`corpus/knowledge/webmcp-invocation-round-17.md:37`<br>`.ufo/waves/round-18/w1/ConnHarnessDiff.md:34,105`<br>`.ufo/waves/round-19/w2/RuntimeUnknownParam.guards.md:39` | **CITE** | Tabi solved the identical architectural problem in rounds 16–19: distinguishing launcher wrapper scripts (`/usr/bin/chromium`, 14 KB shell script) from the underlying binary image (`/usr/lib/chromium/chromium`) by opening `/proc/<pid>/exe` directly and recording `realExecutableSha256`. Kama's `server_exe(pid)` solves the identical anti-decoy problem for `llama-server`. Kama should cite Tabi's `RuntimeUnknownParam.guards.md` pattern as prior fleet architectural precedent for process image binding. |
| **mado-shokunin** | `corpus/knowledge/walker-deep-r9.md:126`<br>`corpus/knowledge/walker-route-r18.md:288`<br>`.ufo/waves/round-26/harness/pilot.py:31`<br>`.ufo/waves/round-41/w2/CritEntryOverreach/overreach.md:61,160,174` | **IGNORE** | Mado uses `readlink` on `/proc/<pid>/exe` to verify whether running desktop daemons match pacman package records on disk. No hash of open fd or dev/inode replay extraction binding is performed. |
| **kengaku-shokunin** | `corpus/evidence/round10-fleet/r10-scout-endpoint.md:25,58,97`<br>`corpus/evidence/round14-fleet/r14-scout-surfaces.md:125` | **IGNORE** | Kengaku inspected Kama's background llama-server daemon PID 1299 via `ls -l /proc/1299/exe` during fleet scout sweeps; passive historical observation rather than an operational runtime primitive. |
| **mori-shokunin** | `.ufo/waves/round-31/w1/SrcProcBaseCmdline.md:5,52,91` | **IGNORE** | Mori scouted kernel C source for `fs/proc/base.c` cmdline null-byte semantics (rejected duplicate row S166); no userspace child attestation logic. |
| **tsukuroi-shokunin** | `.ufo/waves/round-30/w2/SentinelProbeHollow.md:9` | **IGNORE** | C LD_PRELOAD constructor inspecting `/proc/self/exe` to intercept git invocations; out of scope for model server verification. |

---

### Surface 2: Append-Only Audits & Disclosure Ledgers (Claim C2, calibration 7->7)
Kama implementation: `tools/append-only-audit.py v6` (threshold 1 default; permitted A-row status/recheck/used-by edits; mechanical disclosure ledger at `registry/append-only-disclosures.tsv`; `.ufo/waves/round-51/c2/build_ledger.py`; `tools/round51-append-audit-v6-check.py`).

| Sibling Lane | Relevant Files & Lines | Disposition | Boundary Rationale |
|---|---|---|---|
| **kake-shokunin** | `.ufo/waves/round-58/c58_receipt_rewrites.py:1-40`<br>`.ufo/waves/round-58/w1/ExecLedgerBuild.files/build_ledger.py`<br>`.ufo/waves/round-58/receipt-rewrites.json` | **CITE** | Kake independently created a disclosure ledger for post-commit receipt rewrites/deletions under `control(s)/`. Both lanes took proposals from `considerthese/2026-10-26.md`. Kake used `build_ledger.py` to mechanically derive kinds (`pin-only`, `content`, `pending-fill`, `append`, `delete`, `readd`) and enforced that live receipts cannot be rewritten (`new_rewritten == 0`). Kama cites Kake's receipt ledger as sibling design twin validation for mechanical classification of historical discrepancies. |
| **kotoba-shokunin** | `verifiers/check_sources_append_only.py:1-35` | **CITE** | Kotoba created the original Rule 2 verifier enforcing that only `status`, `recheck`, and `used-by` may change in place. Kama's `append-only-audit.py v6` generalized this exact three-column exception into the A-row permitted rule. Kama cites Kotoba as the normative origin of the A-row rule. |
| **mori-shokunin** | `tools/mori-sources-appendonly.py:1-40` | **CITE** | Mori built an exhaustive gate measuring `supersedes S###` linkages (`superseded_as_of` vs `stale_supersede`). Precedent for supersession lineage verification. |
| **kotodama-shokunin** | `corpus/knowledge/verification/append-only-record-verification.md:1-45` | **CITE** | Kotodama codified the fleet doctrine governing append-only record integrity, checkpoint digests, and non-destructive disclosure ("superseded readings stay as the dated record they were; the old reading is never deleted"). Kama cites Kotodama for foundational doctrine. |
| **chousa-shokunin** | `corpus/evidence/round54/considerthese-ledger-check.py:1-36`<br>`corpus/evidence/round54/considerthese-ledger.tsv`<br>`.ufo/waves/round-52/w1/R52ConnCrossClaim.md`<br>`.ufo/waves/round-53/w1/R53ConnSiblings.md` | **HAND OFF** | Chousa automated the tracking of `considerthese` proposals using stable IDs (`CT-YYYYMMDD-n`). Kama's `considerthese/2026-10-26.md` proposal 2 called for tracking proposals, their adoption, and closure verdicts. Kama hands off proposal ledger validation to Chousa's schema rather than inventing an incompatible local format. |
| **tsukuroi-shokunin** | `tools/check-appended-notices.py:1-35` | **IGNORE** | Specific to Tsukuroi's round-18 JSON freshness notices; not general repository append-only verification. |
| **tameshi-shokunin** | `.ufo/evidence/round-50/w1/T50ExecAppendOnly/seat-report-append-only.py` | **IGNORE** | Single-seat test fixture for wave report appends. |

---

## 3. One Non-Obvious Move: Compatible Synthesis Across Round Proposals

### Evidence
1. **Unfulfilled Proposal 2:** In `kama-shokunin/considerthese/2026-10-26.md:25-35`, Kama filed four self-improvement proposals:
   - Proposal 1 (flag deletions in append-only files) was implemented in Round 51 as Claim C2 (`tools/append-only-audit.py v6` + `registry/append-only-disclosures.tsv`).
   - Proposal 3 (counter shortcut & mutant trending) was promoted in round 48 to `tools/shortcut-tally.py` (v2).
   - Proposal 4 (report upstream pin gap) is monitored by `tools/pin-watch.py`.
   - **Proposal 2 ("Track what happens to my own proposals")** remains open: *"A short table in each daily file, with each past proposal, the round that took it up or deferred it, and its closure verdict, would let me calibrate what kind of proposal is useful and stop repeating ones that keep getting deferred."*
2. **Sibling Implementation Twin:** Chousa implemented this exact capability in round 54 (`corpus/evidence/round54/considerthese-ledger-check.py`), auditing proposals in `considerthese/*.md` against a TSV ledger with stable IDs `CT-YYYYMMDD-n` and statuses `IMPL|FMT|OPEN|OPS`.
3. **Stagnant Adjacency Axis:** In `kama-shokunin/SCORECARD.md:22`, `adjacency` has remained at score **7** since Round 1. Its sole evidence pointer is `corpus/knowledge/cross-lane-scope.md` (87 lines, 16 pipe lines), which only documents obsolete Round 1/10 port 8080/34113 drift between Kama, Kagi, Kengaku, Kotoba, and Kumitate. It contains zero coverage of Round 51's operational or calibration surfaces.

### Affected Axes
- **adjacency (improves 7 -> 8):** Extends Kama's cross-lane knowledge from historical port drift to active fleet-wide primitives (`proc_pid_exe(5)` process image identity with Souji/Tabi; append-only disclosure ledgers with Kake/Kotodama; proposal tracking handoff to Chousa).
- **calibration (improves 7 -> 8):** Closes the self-assessment feedback loop by tracking proposal adoption and closure verdicts across rounds.
- **operability (preserved at 8):** Zero modification to runtime binary invocation, loopback probing, or C1 counter execution.

### Proposed Move
1. **Deliver Cross-Lane Scope Supplement:** Stage `.ufo/waves/round-51/a2w1/out/N1Overlap/cross-lane-scope-r51-supplement.md` documenting the 5 citations (Souji S076, Tabi R19, Kake R58, Kotoba Rule 2, Kotodama doctrine) and 1 handoff (Chousa Proposal Ledger) for atomic integration into `corpus/knowledge/cross-lane-scope.md` at round closure.
2. **Adopt Chousa Proposal Ledger Schema:** Deliver `.ufo/waves/round-51/a2w1/out/N1Overlap/proposal-ledger-template.tsv` using Chousa's canonical `CT-YYYYMMDD-n` schema to track proposals from `considerthese/2026-10-25.md` and `2026-10-26.md`, fulfilling Proposal 2 without inventing divergent tooling.

### Risks and Trace of Second-Order Effects
1. **Scorecard Evidence Invalidation Risk:** In-place modification of `corpus/knowledge/cross-lane-scope.md` during a leaf seat would alter the line and pipe counts, immediately breaking `SCORECARD.md:22`'s evidence check (`python3 -c "print(sum(1 for l in open('corpus/knowledge/cross-lane-scope.md') if l.startswith(chr(124))))" -> 16`).
   *Mitigation:* Deliver the supplement exclusively inside `.ufo/waves/round-51/a2w1/out/N1Overlap/` for atomic application by L1 when SCORECARD is reconciled at integration.
2. **Contract Disruption Risk (Second-Order Audit Failure):** Adding `registry/append-only-disclosures.tsv` to `registry/append-only-contract.tsv` would cause `tools/append-only-audit.py` to grade the ledger regeneration at commit `73bf2a7a` as an unpermitted deletion, failing the frozen C2 counter.
   *Mitigation:* Retain `append-only-disclosures.tsv` outside `append-only-contract.tsv` for round 51, relying on `append-only-audit.py`'s built-in ancestor check (`_git_ok(..., "merge-base", "--is-ancestor", row[0], since)`).
3. **Tooling Absorption Risk:** Copying Chousa's `considerthese-ledger-check.py` code into Kama would violate the "report, never absorb" directive.
   *Mitigation:* Hand off validation to Chousa; Kama maintains only the data TSV.

### Verification
1. **Counter Invariance:** Running frozen counters on `$S/lane` at tip `138af25b` confirms C2 passes (`fixture=1 lane=1 scenarios=9/9 lost=142 disclosed=166 met=True`, exit 0).
2. **Proposal Ledger Syntax:** Running Python TSV validation against `proposal-ledger-template.tsv` confirms all rows match `id\tstatus\tpointer\tnote` with statuses in `{"IMPL", "OPEN", "FMT", "OPS"}`.
3. **Contract Unbroken:** Verified that `registry/append-only-contract.tsv` remains unmodified at 10 declared entries.

---

## 4. Defect Report

### Exact Location
File: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-51/c2/build_ledger.py`
Lines: 22–23

### Command Demonstrating Defect
```bash
$ python3 -c "
e = {'commit': 'a'*40, 'file': 'LOG.md', 'undisclosed': [{'line_sha256': 'b'*64, 'count': 2, 'classes': ['in-place-edit', 'removal']}]}
for u in e['undisclosed']:
    if len(u['classes']) != 1:
        raise SystemExit(f\"{e['commit'][:12]} {e['file']}: classes {u['classes']}\")
"
```
Output:
```
SystemExit: aaaaaaaaaaaa LOG.md: classes ['in-place-edit', 'removal']
```
Exit code: 1.

### Root Cause and Analysis
In `build_ledger.py`, line 22 asserts `len(u["classes"]) == 1`. In `tools/append-only-audit.py:688-690`, `cls[key]` aggregates the mechanical classes (`revert`, `in-place-edit`, `removal`) of every hunk deleting that line key. If an event deletes an identical line key across multiple hunks where one hunk adds replacement lines (`in-place-edit`) and another hunk adds no replacement lines (`removal`), `u["classes"]` contains both classes (`len == 2`). `build_ledger.py` crashes with `SystemExit` instead of selecting the dominant class (`in-place-edit`) or splitting rows. While current lane history happens to have single-class line keys across its 51 events, any future commit with mixed hunks on duplicate lines will fail ledger generation.

### Proposed Fix
The proposed fix is delivered at:
`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-51/a2w1/out/N1Overlap/build_ledger_classes.patch`

```diff
--- a/.ufo/waves/round-51/c2/build_ledger.py
+++ b/.ufo/waves/round-51/c2/build_ledger.py
@@ -19,8 +19,15 @@ def main(src, repo, out):
                               capture_output=True, text=True, check=True).stdout.strip()
         note = ("deleted in place by: " + subj).replace("\t", " ")[:160]
         for u in e["undisclosed"]:
-            if len(u["classes"]) != 1:
-                raise SystemExit(f"{e['commit'][:12]} {e['file']}: classes {u['classes']}")
+            # When a key appears in multiple hunks of differing kinds (e.g. both in-place-edit
+            # and removal), prefer 'in-place-edit' if any hunk added replacement lines,
+            # else the single available class; fail only if classes is empty.
+            if not u["classes"]:
+                raise SystemExit(f"{e['commit'][:12]} {e['file']}: empty classes")
+            chosen_class = "in-place-edit" if "in-place-edit" in u["classes"] else u["classes"][0]
             rows.append("\t".join([e["commit"], e["file"], u["line_sha256"], str(u["count"]),
-                                   u["classes"][0], note]))
+                                   chosen_class, note]))
     with open(out, "w") as fh:
         fh.write("\n".join(rows) + "\n")
```

---

## 5. Written Deliverables Summary

The following files were created in the designated output directory:
1. `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-51/a2w1/out/N1Overlap.md` (this report)
2. `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-51/a2w1/out/N1Overlap/sibling-scan-matrix.json` (machine-readable matrix of sibling overlaps and dispositions)
3. `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-51/a2w1/out/N1Overlap/cross-lane-scope-r51-supplement.md` (staged cross-lane scope supplement ready for L1 integration)
4. `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-51/a2w1/out/N1Overlap/proposal-ledger-template.tsv` (staged proposal ledger synthesizing Proposal 2 via Chousa's schema)
5. `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-51/a2w1/out/N1Overlap/build_ledger_classes.patch` (unified diff fixing multi-class line handling in `build_ledger.py`)
