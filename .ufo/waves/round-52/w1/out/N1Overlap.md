# N1Overlap — Sibling Overlap Scan and Adjacency Synthesis (Round 52)

Verdict: Sibling scan across all 20 sibling lanes and fleet-meta lanes identifies 16 operational and calibration touchpoints across both Round 52 surfaces with strict report-not-absorb dispositions, and synthesizes 1 bounded non-obvious move advancing adjacency from 7 to 8 without harming operability (8) or calibration (7).

---

## 1. Evidence: Commands, Outputs, Exit Codes, File:Line

### Command 1: Sibling PROVINCE.md Fleet-Wide Scan
Evaluate domain boundaries and ownership declarations across all 20 sibling lanes in `/home/vgpnk/Projects/shokunin/*-shokunin/PROVINCE.md` and fleet-meta configuration `/home/vgpnk/Projects/shokunin/shokunin.conf`:
```bash
$ python3 -c "
import glob, os, re
lanes = sorted(glob.glob('/home/vgpnk/Projects/shokunin/*-shokunin/PROVINCE.md'))
print(f'Total sibling PROVINCE.md files scanned: {len(lanes)}')
"
```
Output:
```
Total sibling PROVINCE.md files scanned: 21
```
Exit code: 0.

### Command 2: Kama Round 52 C2 Frozen Counter Verification
Run frozen counter `tools/round52-append-restore-check.py` against build commit `5dacf2c70f947ca6dc5fbbca6d45b8db5b0390c8`:
```bash
$ S=/fast/scratch/hyaku/kama-r52/N1Overlap; mkdir -p "$S"
$ git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin "$S/lane"
$ python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round52-append-restore-check.py \
    --repo "$S/lane" --tip 5dacf2c70f947ca6dc5fbbca6d45b8db5b0390c8 --scratch "$S/c2-test"
```
Output:
```
tip=5dacf2c70f947ca6dc5fbbca6d45b8db5b0390c8
fixture=1 lane=1 scenarios=8/8 corr_lost=0 row_lost=10 disclosed=10 met=True
detail: fixture corr-in-place: tool exit 1 (want 1) own unheld 1 (want 1) own graded 1 ok
detail: fixture corr-fenced-reappend: tool exit 0 (want 0) own unheld 0 (want 0) own graded 1 ok
detail: fixture cutoff-after-intro: tool exit 1 (want 1) bad_disclosures 1 (want 1) ok
detail: fixture cutoff-before-intro: tool exit 0 (want 0) bad_disclosures 0 (want 0) ok
detail: fixture only-outside: tool exit 0 (want 0) own unheld 0 (want 0) own graded 0 (want 0) ok
detail: fixture only-inside: tool exit 1 (want 1) own unheld 1 (want 1) own graded 1 (want 1) ok
detail: fixture exempt-inside: tool exit 0 (want 0) own unheld 0 (want 0) own graded 0 (want 0) ok
detail: fixture exempt-dated: tool exit 1 (want 1) own unheld 1 (want 1) own graded 1 (want 1) ok
detail: lane: tool v6 threshold 1 exit 0 events 109 disclosed_lines 10; own graded 5868; own unheld A-corr 0, A/A-row 10; ledger lines 10
Wall time: 5.91 seconds
```
Exit code: 0 (`met=True`).

### Command 3: Kama Round 52 C1 Frozen Counter Verification
Run frozen counter `tools/round52-replay-memfd-audit.py` against build commit `5dacf2c70f947ca6dc5fbbca6d45b8db5b0390c8`:
```bash
$ python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round52-replay-memfd-audit.py \
    --repo "$S/lane" --tip 5dacf2c70f947ca6dc5fbbca6d45b8db5b0390c8 --scratch "$S/c1-test"
```
Output:
```
tip=5dacf2c70f947ca6dc5fbbca6d45b8db5b0390c8
bind=1 sealed=1 teardown=1 newrow=1 bound=3/3 sealedruns=3/3 met=True
detail: counter vocabulary: 512 tokens from its own download
detail: bind b1: pid 2142367 port 42737 exe+listen+tree+env+mapped ok, child_pid joined, mapping dev 103:05 inode 1081934326 recorded, nonce 'kama witness 31f4865f57dfb10f' round-tripped
detail: sealed b1: running image '/memfd:llama-server (deleted)' 00:01:184399 seals 15 is a sealed memfd with the frozen digest, recorded in server_exe and own_server
detail: bind b2: pid 2151580 port 41921 exe+listen+tree+env+mapped ok, child_pid joined, mapping dev 103:05 inode 209623208 recorded, nonce 'kama witness be52e27ec65d4bbf' round-tripped
detail: sealed b2: running image '/memfd:llama-server (deleted)' 00:01:177011 seals 15 is a sealed memfd with the frozen digest, recorded in server_exe and own_server
detail: bind b3: pid 2163398 port 39395 exe+listen+tree+env+mapped ok, child_pid joined, mapping dev 103:05 inode 1821376899 recorded, nonce 'kama witness 769df9314d382f70' round-tripped
detail: sealed b3: running image '/memfd:llama-server (deleted)' 00:01:155610 seals 15 is a sealed memfd with the frozen digest, recorded in server_exe and own_server
detail: teardown: invoker SIGKILLed with 3 descendants; after 0.10 s alive [] port refuses ok
detail: newrow: 1 rows new since base; 1 name memfd_create(2): ['| S500 |']
Wall time: 36.07 seconds
```
Exit code: 0 (`met=True`).

### Command 4: Verification of `tools/append-only-audit.py` on Build Commit
```bash
$ python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/append-only-audit.py \
    --repo "$S/lane" --to 5dacf2c70f947ca6dc5fbbca6d45b8db5b0390c8
```
Output:
```
summary commits=350 files=99 events=109 restored=67 partial=0 unrestored=0 ungraded=37 disclosed=5 permitted_lines=58 disclosed_lines=10 bad_disclosures=0 ungraded_lines=210 regressed=0 vanished=0 unmatched=0 binary=0 bad_declarations=0
```
Exit code: 0 (`unrestored=0`, `bad_disclosures=0`).

---

## 2. Overlap Scan: Sibling Dispositions (Report-Not-Absorb & Owner)

In accordance with `PROVINCE.md:53` ("Out of province -> report, never absorb"), all overlaps are classified as **report-not-absorb** with explicit owner attribution.

### Surface 1: Executing Binaries from Sealed Memfds / Process Image Identity (Claim C1, operability 8->8)
Kama implementation: S500 cites `memfd_create(2)`; `tools/kama-live-replay.py:sealed_member()` copies verified archive member streams directly into an anonymous memfd (`MFD_CLOEXEC | MFD_ALLOW_SEALING`), hashes it, seals it with `F_ADD_SEALS 15`, and passes the descriptor to `tools/kama-llamacpp-live.py` (`--server-fd <n>`). The live tool execs via `/proc/<pid>/fd/<n>` so `/proc/<pid>/exe` is `/memfd:llama-server (deleted)` with `st_nlink == 0`.

| Sibling Lane | Relevant Files & Lines | Disposition | Owning Lane & Boundary Rationale |
|---|---|---|---|
| **kaidoku-shokunin** | `corpus/QUALITY.md:34, 117-118` (Rule #24)<br>`SKILL.md:830` | **report-not-absorb** | **kaidoku-shokunin** owns binary RE, static carrier guards (`carrier-guard.py`), and native ELF linkage reading. Rule #24 specifically named `memfd_create + fexecve` as an unobserved execution bypass to static inode checks. Kama C1 operationalizes what Kaidoku classified as an adversarial execution bypass into a positive proof of hermetic image authenticity. Kama does not absorb binary analysis or static carrier guards. |
| **kumitate-shokunin** | `scripts/cap-run.mjs:1-40`<br>`scripts/cap-spawn.mjs`<br>`SKILL.md:620-624` | **report-not-absorb** | **kumitate-shokunin** owns general runner orchestration and child sandboxing (`scripts/cap-run.mjs` using `systemd-run` + `bwrap` container namespaces). Kama manages loopback server process lifecycles for model serving only and relies on Kumitate for general runner standards. |
| **tsukuroi-shokunin** | `PROVINCE.md:3-15`<br>`corpus/knowledge/oom-event-plane.md`<br>Kernel docs `mfd_noexec.rst`<br>`systemd` `NEWS-v262:6439, 20776` | **report-not-absorb** | **tsukuroi-shokunin** owns host OS substrate, kernel configuration, and driver health. It governs kernel sysctls like `vm.memfd_noexec` (which under policy 1 or 2 enforces `MFD_NOEXEC_SEAL` and requires explicit `MFD_EXEC`, scouted by Kama seat `S4NoExec`). Tsukuroi also monitors `systemd-executor` (passing unit configs via memfd) and kernel un-reclaimable memory accounting for secret memfds. Kama adapts userspace memfd flags (`MFD_EXEC` fallback) but does not configure or remediate host sysctls. |
| **tabi-shokunin** | `corpus/knowledge/webmcp-chromium-loopback-round-16.md:35`<br>`RuntimeUnknownParam.guards.md:39` | **report-not-absorb** | **tabi-shokunin** owns browser automation and client process verification. Tabi resolved process image identity by inspecting `/proc/<pid>/exe` directly to separate launcher shell scripts from binary images. Kama cites Tabi as fleet architectural precedent for `/proc/<pid>/exe` verification. |
| **souji-shokunin** | `corpus/SOURCES.md:92,99` (S069, S076)<br>`corpus/knowledge/process-residue-observations.md:26-30` | **report-not-absorb** | **souji-shokunin** owns workspace and process residue identification. Souji documented that Linux procfs appends `" (deleted)"` exclusively to `/proc/<pid>/exe` when an executable is unlinked. Kama utilizes the procfs deleted link convention as evidence that no on-disk file was executed. |
| **kengaku-shokunin** | `PROVINCE.md:271, 296, 311-360`<br>`SKILL.md:491-499` | **report-not-absorb** | **kengaku-shokunin** owns model evaluation and benchmark execution. Kengaku executes model benchmark evaluations in bubblewrap sandboxes and compiled the fleet sandbox census in round 38. Model serving endpoint health remains Kama's province. |
| **kasegi-shokunin** | `PROVINCE.md:29-33, 52`<br>`corpus/source-snapshots/round-24/S005.txt:62` | **report-not-absorb** | **kasegi-shokunin** owns bounty and security research. Studies security research scopes and exploit mitigations (sandboxing, memory execution restrictions). Explicitly refuses live-target execution in `PROVINCE.md:52`. |
| **mado-shokunin** | `tools/mado-tripwire.py:15-25`<br>`quality/counters/c1-r40-live-v2.py:19-23` | **report-not-absorb** | **mado-shokunin** owns desktop compositor craft and UI tripwires. Mado executes C1 counters and session transcript tripwires under bubblewrap sandboxes. |

---

### Surface 2: Append-Only Record Restoration & History Preservation (Claim C2, calibration 7->7)
Kama implementation: 155 lines deleted in-place historically across 18 A-corr files are restored verbatim at file tails under `## Restored lines (round 52)` inside five-backtick fences (`corr_lost = 0`), and their disclosure rows removed from `registry/append-only-disclosures.tsv`. Counter `tools/round52-append-restore-check.py` independently verifies this invariant across 8 constructed scenarios.

| Sibling Lane | Relevant Files & Lines | Disposition | Owning Lane & Boundary Rationale |
|---|---|---|---|
| **protocol** | `PROTOCOL.md:123-125, 314-321, 338-341, 366-367, 463`<br>`PROTOCOL-APPENDIX.md:24` | **report-not-absorb** | **protocol** owns fleet protocol soundness and gate integrity. `PROTOCOL.md` establishes that append-only files (`LOG.md`, `rounds` in `MANIFEST.json`, `corpus/SOURCES.md`) cannot have historical commits rewritten in place; corrections must land as appended entries or new commits. Kama C2 operationalizes this by restoring deleted historical text verbatim at file tails, eliminating unheld loss while strictly maintaining Git commit immutability. |
| **aggregator** | `shokunin.conf:21`<br>`PROTOCOL.md:337-341, 434` | **report-not-absorb** | **aggregator** owns cross-lane quality and routed defect tracking. Governs the fleet routed-defect queue (`.ufo/reports/AGGREGATE.md`) and audits cross-lane corpus quality. Aggregator audits cross-lane conformance; Kama repairs historical deletions within its own lane repository. |
| **kotodama-shokunin** | `corpus/knowledge/verification/append-only-record-verification.md:1-111`<br>`reports/round-20/readme/gaps.md:18-20` | **report-not-absorb** | **kotodama-shokunin** owns the normative doctrine of append-only records. Codified the fleet doctrine for append-only records: close digests, closing snapshots, and successor-row corrections ("superseded readings stay as the dated record they were"). Kotodama supplies the verification theory; Kama provides the mechanical multi-file Git audit tool (`append-only-audit.py`) and fenced verbatim EOF restoration pattern. |
| **chousa-shokunin** | `corpus/evidence/round54/considerthese-ledger-check.py:1-36`<br>`considerthese-ledger.tsv`<br>`research-gate.sh:106-131` | **report-not-absorb** | **chousa-shokunin** owns deep-research method, citation chaining, and proposal tracking. Maintains `considerthese` proposal tracking ledgers with stable IDs `CT-YYYYMMDD-n`, and audits append-only citation chains (`APPEND_SERIALIZED=24/24`). Kama hands off proposal tracking (`considerthese/2026-10-26.md` Proposal 2) to Chousa rather than inventing local tooling. |
| **kake-shokunin** | `.ufo/waves/round-58/c58_receipt_rewrites.py:1-40`<br>`.ufo/waves/round-58/w1/ExecLedgerBuild.files/build_ledger.py` | **report-not-absorb** | **kake-shokunin** owns web properties and publishing. Sibling design twin for mechanical disclosure ledgers: classified historical post-commit receipt rewrites and deletions into mechanical kinds (`pin-only`, `content`, `pending-fill`, `append`, `delete`, `readd`). Kake audits receipt rewrites; Kama audits Markdown and source registry append-only compliance. |
| **mori-shokunin** | `tools/mori-sources-appendonly.py:1-40`<br>`SKILL.md:887-912` | **report-not-absorb** | **mori-shokunin** owns fleet/host observability and source supersede timing. Maintains a dedicated first-parent diff gate enforcing append-only rules and supersede timing on `corpus/SOURCES.md`. Mori gates source supersede timing; Kama owns multi-file repository append-only audits. |
| **kotoba-shokunin** | `verifiers/check_sources_append_only.py:1-35` | **report-not-absorb** | **kotoba-shokunin** owns prompt craft. Originated the Rule 2 verifier enforcing that only status, recheck, and used-by columns may be edited in place in `corpus/SOURCES.md`. Kotoba originated the column-level exception that Kama codified into the A-row permitted rule. |
| **souji-shokunin** | `tools/souji-capability-agreement.py:29-30`<br>`tools/souji-record-agreement.py:17-18`<br>`tools/souji-registry-agreement.py:15-18` | **report-not-absorb** | **souji-shokunin** owns repo hygiene and strict prefix matching. Enforces strict blob-prefix append-only invariants over `SCORECARD.md` and `SHONEN.md` (any prefix change fails closed). Kama handles complex section-aware and fenced re-append restorations. |

---

## 3. One Non-Obvious Move: Compatible Synthesis Across Round Proposals

### Evidence Basis
1. **Stagnant Adjacency Axis:** In `SCORECARD.md:19`, `adjacency` has remained at score **7** since Round 1. Its sole evidence pointer is `corpus/knowledge/cross-lane-scope.md` (87 lines, 16 pipe lines), which only documents obsolete Round 1 port 8080/34113 drift between Kama, Kagi, Kengaku, Kotoba, and Kumitate. It contains zero coverage of Round 52's operational or calibration surfaces.
2. **Scorecard Evidence Invariance:** Modifying `corpus/knowledge/cross-lane-scope.md` during a leaf seat would alter the line and pipe counts, immediately breaking `SCORECARD.md:19`'s verification command (`python3 -c "print(sum(1 for l in open('corpus/knowledge/cross-lane-scope.md') if l.startswith(chr(124))))" -> 16`).
3. **Unfulfilled Proposal 2:** In `considerthese/2026-10-26.md:31`, Kama filed Proposal 2 ("Track what happens to my own proposals"): *"A short table in each daily file, with each past proposal, the round that took it up or deferred it, and its closure verdict, would let me calibrate what kind of proposal is useful..."* Seat `N3Consider` confirmed that Proposal 2 remains completely open in Kama's surfaces.
4. **Sibling Prior Art:** Chousa implemented this exact capability in round 54 (`corpus/evidence/round54/considerthese-ledger-check.py` and `considerthese-ledger.tsv`) using stable IDs `CT-YYYYMMDD-n`.

### Affected Axes
- **adjacency (improves 7 -> 8):** Extends Kama's cross-lane knowledge from historical port drift to active fleet-wide primitives (`memfd_create(2)` execution binding with Kaidoku/Kumitate/Tsukuroi; append-only restoration with Protocol/Kotodama; proposal tracking handoff to Chousa).
- **calibration (preserved at 7):** Preserves all C2 counting commands, ledger cutoffs, and contract rules.
- **operability (preserved at 8):** Preserves all C1 runtime memfd descriptor execution and teardown invariants.

### Proposed Move
1. **Deliver Staged Cross-Lane Scope Supplement:** Deliver `.ufo/waves/round-52/w1/out/N1Overlap/cross-lane-scope-r52-supplement.md` documenting all 16 sibling touchpoints and formalizing four concrete handoff packets (`KAMA-R52-MEMFD-01` to Tsukuroi, `KAMA-R52-PROPOSAL-01` to Chousa, `KAMA-R52-CARRIER-01` to Kaidoku, `KAMA-R52-RESTORE-01` to Protocol). This stages the exact text needed for L1 to elevate `adjacency` to 8 at integration without mutating `corpus/knowledge/cross-lane-scope.md` during the wave.
2. **Formal Handoff to Chousa Proposal Schema:** Rather than implementing a redundant proposal validator in Kama, formally hand off `considerthese/2026-10-26.md` Proposal 2 to Chousa's canonical `CT-YYYYMMDD-n` schema via Packet `KAMA-R52-PROPOSAL-01`.

### Risks and Trace of Second-Order Effects
1. **Scorecard Invalidation Risk:** Mutating `cross-lane-scope.md` in-place would break `SCORECARD.md:19`'s 16-pipe-line check. Staging the supplement inside the seat output directory guarantees zero interference with the build tree.
2. **Audit Permissiveness Risk:** Adding new files or sections to `cross-lane-scope.md` without updating the contract could cause `tools/append-only-audit.py` to evaluate them. Because the supplement is delivered in `.ufo/waves/`, it remains completely outside the audited contract paths.
3. **Tooling Absorption Risk:** Attempting to copy Chousa's `considerthese-ledger-check.py` into Kama would violate `PROVINCE.md`. Routing the handoff via packet preserves strict domain boundaries.

### Verification
1. **Scorecard Verification Check:** Running `python3 -c "print(sum(1 for l in open('corpus/knowledge/cross-lane-scope.md') if l.startswith(chr(124))))"` confirms the count remains exactly `16`.
2. **C1 & C2 Counter Invariance:** Running `tools/round52-replay-memfd-audit.py` and `tools/round52-append-restore-check.py` on the build tree both pass (`met=True`, exit 0).

---

## 4. Defect Report

### Exact Location
File: `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-llamacpp-live.py`  
Line: 1968  

### Command Demonstrating Defect
```bash
python3 -c "
import os, sys, subprocess, tempfile, hashlib, json

with tempfile.TemporaryDirectory() as td:
    fake_srv = os.path.join(td, 'llama-server')
    with open(fake_srv, 'wb') as fh: fh.write(b'ELF_STUB')
    os.chmod(fake_srv, 0o644)  # exec bits cleared on disk (e.g. carrier-guard armed, noexec mount)

    fake_model = os.path.join(td, 'model.gguf')
    with open(fake_model, 'wb') as fh: fh.write(b'GGUF_STUB')

    fake_probe = os.path.join(td, 'probe.sh')
    with open(fake_probe, 'wb') as fh: fh.write(b'#!/bin/sh\nexit 0\n')
    os.chmod(fake_probe, 0o755)

    fd = os.memfd_create('llama-server', os.MFD_CLOEXEC | os.MFD_ALLOW_SEALING)
    os.write(fd, b'ELF_STUB')
    os.lseek(fd, 0, os.SEEK_SET)

    out_receipt = os.path.join(td, 'receipt.json')
    cmd = [
        sys.executable,
        '/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-llamacpp-live.py',
        '--server', fake_srv,
        '--model', fake_model,
        '--model-sha256', hashlib.sha256(b'GGUF_STUB').hexdigest(),
        '--probe', fake_probe,
        '--server-fd', str(fd),
        '--out', out_receipt,
    ]
    p = subprocess.run(cmd, pass_fds=(fd,), capture_output=True, text=True)
    with open(out_receipt) as f:
        rec = json.load(f)
    print('exit code:', p.returncode)
    print('outcome:', rec.get('outcome'))
    print('setup_error:', rec.get('setup_error'))
"
```
Output:
```
exit code: 2
outcome: setup-error
setup_error: server-not-executable:/tmp/.../llama-server
```
Exit code: 2.

### Root Cause and Analysis
In `tools/kama-llamacpp-live.py:1968`, the tool unconditionally executes:
```python
server_real = os.path.realpath(server_arg)
if not (os.path.isfile(server_real) and os.access(server_real, os.X_OK)):
    raise SetupError(f'server-not-executable:{server_real}')
```
When `--server-fd` is passed, `Popen` executes the server image directly from the inherited sealed memfd descriptor (`executable=f'/proc/{os.getpid()}/fd/{args.server_fd}'`, line 1993). The on-disk file at `server_real` is never executed; it is only inspected for its library directory (`LD_LIBRARY_PATH` and `cwd`) and verified against the archive member. If the on-disk file has mode `0644` (such as when stripped of execute bits under sibling `kaidoku-shokunin`'s carrier-guard or when residing on a `noexec` mount), `os.access(server_real, os.X_OK)` returns `False`, causing `SetupError` and premature abort (`outcome: setup-error`). This contradicts the purpose of hermetic sealed memfd execution, which exists precisely so execution does not depend on an on-disk executable.

### Proposed Fix
The proposed fix is delivered at:
`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/N1Overlap/kama_llamacpp_live_fd_exec.patch`

```diff
--- a/tools/kama-llamacpp-live.py
+++ b/tools/kama-llamacpp-live.py
@@ -1965,7 +1965,7 @@ def main(argv=None):
         if not server_arg:
             raise SetupError('no-llama-server')
         server_real = os.path.realpath(server_arg)
-        if not (os.path.isfile(server_real) and os.access(server_real, os.X_OK)):
+        if not (os.path.isfile(server_real) and (args.server_fd is not None or os.access(server_real, os.X_OK))):
             raise SetupError(f'server-not-executable:{server_real}')
         if not os.path.isfile(args.model):
             raise SetupError(f'model-not-found:{args.model}')
```

---

## 5. Written Deliverables Summary

The following files were created in the designated output directory:
1. `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/N1Overlap.md` (this report)
2. `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/N1Overlap/overlap.md` (comprehensive sibling overlap scan document)
3. `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/N1Overlap/cross-lane-scope-r52-supplement.md` (staged cross-lane scope supplement ready for L1 integration)
4. `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/N1Overlap/sibling-scan-matrix.json` (machine-readable matrix of sibling overlaps and dispositions)
5. `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/N1Overlap/kama_llamacpp_live_fd_exec.patch` (unified diff fixing on-disk X_OK requirement when executing from sealed memfd)
