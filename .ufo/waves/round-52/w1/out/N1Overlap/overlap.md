# Round 52 — N1Overlap Sibling-Overlap Scan and Adjacency Synthesis

**Lane:** `kama-shokunin`  
**Seat:** `N1Overlap` (UFO-FSD connector / leaf seat, round 52 wave 1)  
**Milestone:** Round 52 attack and frontier  
**Judged on:** Adjacency  
**Base Commit:** `9ff76b1f763512be2f554cbbfd0b2213b63b0847`  
**Build Commit:** `5dacf2c70f947ca6dc5fbbca6d45b8db5b0390c8`  
**Frozen Claims:** Claim C1 (operability 8 -> 8, sealed memfd execution, S500); Claim C2 (calibration 7 -> 7, append-only restoration of 155 lost lines across 18 files)  

---

## 1. Executive Verdict

**Verdict:** Systematic scan of `shokunin.conf` and all 20 sibling lane `PROVINCE.md` files identifies 8 cross-lane citations across Surface 1 (sealed anonymous memfd execution / process image identity: `kaidoku`, `kumitate`, `tsukuroi`, `tabi`, `souji`, `kengaku`, `kasegi`, `mado`) and 8 cross-lane citations across Surface 2 (append-only record restoration / disclosure ledgers: `protocol`, `aggregator`, `kotodama`, `chousa`, `kake`, `mori`, `kotoba`, `souji`). For every identified overlap, the strict disposition is **report-not-absorb**, explicitly designating the owning sibling or fleet-meta lane. One non-obvious move—staging an atomic Cross-Lane Scope Supplement for Round 52 alongside adopting Chousa's canonical proposal ledger schema—advances `adjacency` from 7 to 8 without harming `operability` (8) or `calibration` (7).

---

## 2. Scan Methodology & Scope

The scan evaluated all lanes defined in `/home/vgpnk/Projects/shokunin/shokunin.conf` (20 physical sibling lanes plus the two fleet-meta lanes `protocol` and `aggregator` rooted at `.`). All sibling `PROVINCE.md` files at `/home/vgpnk/Projects/shokunin/*-shokunin/PROVINCE.md` were read and indexed under `gitignore: false` (since `*-shokunin/` is ignored at the fleet root).

### Scanned Roster
1. `protocol` (`.` / fleet root)
2. `aggregator` (`.` / fleet root)
3. `kaidoku-shokunin`
4. `kumitate-shokunin`
5. `tsukuroi-shokunin`
6. `kasegi-shokunin`
7. `kengaku-shokunin`
8. `kake-shokunin`
9. `kotoba-shokunin`
10. `kagi-shokunin`
11. `tameshi-shokunin`
12. `mado-shokunin`
13. `tabi-shokunin`
14. `mori-shokunin`
15. `chousa-shokunin`
16. `kotodama-shokunin`
17. `souji-shokunin`
18. `lore-shokunin`
19. `revenger-shokunin`
20. `audio-shokunin`
21. `game-dev-2d-shokunin`
22. `game-dev-3d-shokunin`

---

## 3. Surface 1: Executing Binaries from Sealed Memfds / Process Image Identity

### Surface Description (Claim C1, operability 8 -> 8)
Sourced on `memfd_create(2)` (S500). `tools/kama-live-replay.py:sealed_member()` copies the verified server member from the archive's tar stream directly into an anonymous memfd (`MFD_CLOEXEC | MFD_ALLOW_SEALING`), hashes it, seals it with `F_ADD_SEALS = 15` (`F_SEAL_WRITE | F_SEAL_SHRINK | F_SEAL_GROW | F_SEAL_SEAL`), and passes the descriptor to the live child via `--server-fd <n>`. In `tools/kama-llamacpp-live.py:sealed_fd()`, the descriptor is verified (`F_GET_SEALS == 15`, `st_nlink == 0`, size and sha256 equal to `--server`), and executed via `Popen(executable=f'/proc/{os.getpid()}/fd/{fd}', argv=['llama-server', ...])` with `LD_LIBRARY_PATH` and `cwd` pointing to the extracted server tree. The running process image in `/proc/<pid>/exe` is an anonymous `/memfd:llama-server (deleted)` link with zero directory entries (`st_nlink == 0`), proving that no on-disk file (copy decoy, hardlink, or rename-over) is the running image.

### Sibling Lane Overlaps and Dispositions

| Sibling Lane | Relevant Files & Lines | Analysis of Overlap | Disposition | Owning Lane |
|---|---|---|---|---|
| **kaidoku-shokunin** | `corpus/QUALITY.md:34, 117-118` (Rule #24)<br>`SKILL.md:830`<br>`.ufo/waves/round-20/w1/CriticGuardSufficiency.md:49` | Kaidoku's carrier-guard (`carrier-guard.py`) clears executable mode bits on carrier files and checks that modes remain non-executable. Rule #24 explicitly lists `memfd_create + fexecve` as a named bypass to static inode checks ("copying the bytes elsewhere, `memfd_create`+`fexecve`, in-process loaders, user-namespace bind mounts... are named bypasses"). Kama's C1 turns this exact adversarial bypass into an operational proof of authenticity: running from an anonymous sealed memfd guarantees the image did not come from an on-disk binary. | **report-not-absorb** | **kaidoku-shokunin** (owns binary RE, static carrier guards, and native ELF linkage reading). Kama does not absorb binary analysis or static carrier guards. |
| **kumitate-shokunin** | `scripts/cap-run.mjs:1-40`<br>`scripts/cap-spawn.mjs`<br>`SKILL.md:620-624` | Kumitate is the fleet authority for child process execution and sandboxing (`scripts/cap-run.mjs` using `systemd-run` + `bwrap` container namespaces). Kumitate manages child process lifetime, environment scrubbing, and cgroup limits. | **report-not-absorb** | **kumitate-shokunin** (owns runner execution and sandboxing). Kama manages loopback server process lifecycles for model serving only and relies on Kumitate for general runner standards. |
| **tsukuroi-shokunin** | `PROVINCE.md:3-15`<br>`corpus/knowledge/oom-event-plane.md`<br>Kernel docs `mfd_noexec.rst`<br>`systemd` `NEWS-v262:6439, 20776` | Tsukuroi owns the host OS substrate, kernel configuration, and driver health. It governs kernel sysctls like `vm.memfd_noexec` (which under policy 1 or 2 enforces `MFD_NOEXEC_SEAL` and requires explicit `MFD_EXEC` for executable memfds, scouted by Kama seat `S4NoExec`). Tsukuroi also monitors `systemd-executor` (which uses memfds to pass unit configs) and kernel un-reclaimable memory accounting for secret memfds. | **report-not-absorb** | **tsukuroi-shokunin** (owns OS substrate, systemd, and kernel sysctls). Kama adapts userspace memfd flags (`MFD_EXEC` fallback) but does not configure or remediate host sysctls. |
| **tabi-shokunin** | `corpus/knowledge/webmcp-chromium-loopback-round-16.md:35`<br>`corpus/knowledge/webmcp-invocation-round-17.md:37`<br>`RuntimeUnknownParam.guards.md:39` | Tabi resolved process image identity by inspecting `/proc/<pid>/exe` directly to differentiate launcher wrapper scripts (`/usr/bin/chromium`, 14 KB shell script) from the underlying binary image (`/usr/lib/chromium/chromium`). | **report-not-absorb** | **tabi-shokunin** (owns browser automation and client process verification). Kama cites Tabi as fleet architectural precedent for `/proc/<pid>/exe` verification. |
| **souji-shokunin** | `corpus/SOURCES.md:92,99` (S069, S076)<br>`corpus/knowledge/process-residue-observations.md:26-30` | Souji documented that Linux procfs appends `" (deleted)"` exclusively to `/proc/<pid>/exe` when an executable is unlinked. In Kama C1, an anonymous memfd exhibits this exact procfs behavior (`/memfd:llama-server (deleted)` with `st_nlink == 0`). | **report-not-absorb** | **souji-shokunin** (owns workspace and process residue identification). Kama utilizes the procfs deleted link convention as evidence that no on-disk file was executed. |
| **kengaku-shokunin** | `PROVINCE.md:271, 296, 311-360`<br>`SKILL.md:491-499` | Kengaku executes model benchmark evaluations in bubblewrap sandboxes. In round 38 (`PROVINCE.md:311-360`), Kengaku compiled the fleet-wide sandbox census citing Kaidoku's memfd bypass notice. Historically pinned local model processes via `/proc/<pid>/cmdline`. | **report-not-absorb** | **kengaku-shokunin** (owns model evaluation and benchmark execution). Model serving endpoint health remains Kama's province. |
| **kasegi-shokunin** | `PROVINCE.md:29-33, 52`<br>`corpus/source-snapshots/round-24/S005.txt:62` | Studies security research scopes and exploit mitigations (sandboxing, memory execution restrictions). Explicitly refuses live-target execution in `PROVINCE.md:52`. | **report-not-absorb** | **kasegi-shokunin** (owns bounty and security research). Security research into binary injection mitigations belongs to Kasegi; Kama does not perform vulnerability triage. |
| **mado-shokunin** | `tools/mado-tripwire.py:15-25`<br>`quality/counters/c1-r40-live-v2.py:19-23` | Mado executes C1 counters and session transcript tripwires under bubblewrap sandboxes to protect host state. | **report-not-absorb** | **mado-shokunin** (owns desktop compositor craft and UI tripwires). |

---

## 4. Surface 2: Append-Only Record Restoration & History Preservation

### Surface Description (Claim C2, calibration 7 -> 7)
In Round 51, `tools/append-only-audit.py v6` exposed 155 lines deleted in-place historically across 18 files declared append-only with corrections appended (A-corr: `LOG.md`, `SCORECARD.md`, `corpus/QUALITY.md`, `corpus/README.md`, `corpus/lessons/*.md`), and recorded them in `registry/append-only-disclosures.tsv`. In Round 52, Claim C2 completely resolved these unheld losses by re-appending the 155 lines verbatim at the file tails under `## Restored lines (round 52)` (`###` in SCORECARD.md) inside five-backtick fences (`corr_lost = 0`), and removed their rows from the disclosure ledger. The disclosure ledger now retains exactly 10 rows for A and A-row files (`corpus/SOURCES.md`, `registry/report-landing-errata.tsv`) where a verbatim re-append would introduce duplicate registry IDs. Counter `tools/round52-append-restore-check.py` independently verifies this invariant across 8 constructed scenarios.

### Sibling Lane Overlaps and Dispositions

| Sibling Lane | Relevant Files & Lines | Analysis of Overlap | Disposition | Owning Lane |
|---|---|---|---|---|
| **protocol** | `PROTOCOL.md:123-125, 314-321, 338-341, 366-367, 463`<br>`PROTOCOL-APPENDIX.md:24` | Normative origin of append-only discipline: `PROTOCOL.md` establishes that append-only files (`LOG.md`, `rounds` in `MANIFEST.json`, `corpus/SOURCES.md`) cannot have historical commits rewritten in place; corrections must land as appended entries or new commits. Kama C2 operationalizes this by restoring deleted historical text verbatim at file tails, eliminating unheld loss while strictly maintaining Git commit immutability. | **report-not-absorb** | **protocol** (owns fleet protocol soundness and gate integrity). Protocol defines the invariant; Kama implements the mechanical file restoration pattern. |
| **aggregator** | `shokunin.conf:21`<br>`PROTOCOL.md:337-341, 434` | Governs the fleet routed-defect queue (`.ufo/reports/AGGREGATE.md`) and audits cross-lane corpus quality. Arbitrates append-only violations across lanes. | **report-not-absorb** | **aggregator** (owns cross-lane quality and routed defect tracking). Aggregator audits cross-lane conformance; Kama repairs historical deletions within its own lane repository. |
| **kotodama-shokunin** | `corpus/knowledge/verification/append-only-record-verification.md:1-111`<br>`reports/round-20/readme/gaps.md:18-20` | Codified the fleet doctrine for append-only records: close digests, closing snapshots, and successor-row corrections ("superseded readings stay as the dated record they were; the old reading is never deleted"). Documented that when history was edited in place (e.g. round 20 measuring round 5/6 runners), the committed bytes were restored and drift recorded as digests. | **report-not-absorb** | **kotodama-shokunin** (owns the normative doctrine of append-only records). Kotodama supplies the verification theory; Kama provides the mechanical multi-file Git audit tool (`append-only-audit.py`) and fenced verbatim EOF restoration pattern. |
| **chousa-shokunin** | `corpus/evidence/round54/considerthese-ledger-check.py:1-36`<br>`considerthese-ledger.tsv`<br>`research-gate.sh:106-131` | Maintains `considerthese` proposal tracking ledgers with stable IDs `CT-YYYYMMDD-n` (status `IMPL\|FMT\|OPEN\|OPS`), and audits append-only citation chains (`APPEND_SERIALIZED=24/24`, `EXEMPT_AUDIT_MATCH=132/132`). | **report-not-absorb** | **chousa-shokunin** (owns deep-research method, citation chaining, and proposal tracking). Kama hands off proposal tracking (`considerthese/2026-10-26.md` Proposal 2) to Chousa rather than inventing local tooling. |
| **kake-shokunin** | `.ufo/waves/round-58/c58_receipt_rewrites.py:1-40`<br>`.ufo/waves/round-58/w1/ExecLedgerBuild.files/build_ledger.py` | Sibling design twin for mechanical disclosure ledgers: classified historical post-commit receipt rewrites and deletions into mechanical kinds (`pin-only`, `content`, `pending-fill`, `append`, `delete`, `readd`). | **report-not-absorb** | **kake-shokunin** (owns web properties and publishing). Kake audits receipt rewrites; Kama audits Markdown and source registry append-only compliance. |
| **mori-shokunin** | `tools/mori-sources-appendonly.py:1-40`<br>`SKILL.md:887-912` | Maintains a dedicated first-parent diff gate enforcing append-only rules and supersede timing on `corpus/SOURCES.md`. | **report-not-absorb** | **mori-shokunin** (owns fleet/host observability and source supersede timing). Mori gates source supersede timing; Kama owns multi-file repository append-only audits. |
| **kotoba-shokunin** | `verifiers/check_sources_append_only.py:1-35` | Originated the Rule 2 verifier enforcing that only status, recheck, and used-by columns may be edited in place in `corpus/SOURCES.md`. | **report-not-absorb** | **kotoba-shokunin** (owns prompt craft). Kotoba originated the column-level exception that Kama codified into the A-row permitted rule. |
| **souji-shokunin** | `tools/souji-capability-agreement.py:29-30`<br>`tools/souji-record-agreement.py:17-18`<br>`tools/souji-registry-agreement.py:15-18` | Enforces strict blob-prefix append-only invariants over `SCORECARD.md` and `SHONEN.md` (any prefix change fails closed). | **report-not-absorb** | **souji-shokunin** (owns repo hygiene and strict prefix matching). Kama handles complex section-aware and fenced re-append restorations. |

---

## 5. Non-Overlapping Lanes (No Substantive Touchpoint)

The following sibling lanes operate in orthogonal domains with no direct functional overlap on Round 52's sealed memfd execution or append-only restoration surfaces:
- **lore-shokunin:** World-bible consistency, character canon, contradiction ledgers.
- **revenger-shokunin:** Static disassembly and reverse engineering of caller-supplied binaries using REA; refuses live-target execution.
- **audio-shokunin:** Audio mixing, procedural sound synthesis, asset tables.
- **game-dev-2d-shokunin:** 2D platforming, tilemap rendering, physics bodies.
- **game-dev-3d-shokunin:** 3D transforms, camera navigation, spatial audio.
- **kagi-shokunin:** Secret and vault ops; uses curl for health-checks but does not manage runtime process execution.

---

## 6. Synthesis: One Non-Obvious Move

### Evidence Basis
1. **Stagnant Adjacency Axis:** In `SCORECARD.md:19`, `adjacency` has remained frozen at **7** since Round 1. Its sole evidence pointer is `corpus/knowledge/cross-lane-scope.md` (87 lines, 16 pipe lines), which covers only obsolete Round 1 port 8080/34113 drift between Kama, Kagi, Kengaku, Kotoba, and Kumitate. It contains zero coverage of Round 52's sealed memfd execution or append-only restoration surfaces.
2. **Scorecard Immutability Constraint:** `SCORECARD.md:19` binds `cross-lane-scope.md` via `python3 -c "print(sum(1 for l in open('corpus/knowledge/cross-lane-scope.md') if l.startswith(chr(124))))" -> 16`. Directly modifying `cross-lane-scope.md` during a leaf seat would alter the line and pipe counts, immediately breaking the scorecard verification check.
3. **Unimplemented Proposal 2:** In `considerthese/2026-10-26.md:31`, Kama proposed: *"Track what happens to my own proposals: A short table in each daily file, with each past proposal, the round that took it up or deferred it, and its closure verdict, would let me calibrate what kind of proposal is useful..."* Seat `N3Consider` confirmed that Proposal 2 remains completely unimplemented in Kama's surfaces.
4. **Sibling Prior Art:** Chousa implemented this exact capability in round 54 (`corpus/evidence/round54/considerthese-ledger-check.py` and `considerthese-ledger.tsv`) with stable IDs `CT-YYYYMMDD-n`.

### Affected Axes
- **adjacency (improves 7 -> 8):** Bridges Kama's cross-lane knowledge from obsolete port drift to active fleet-wide primitives (`memfd_create(2)` execution binding with Kaidoku/Kumitate/Tsukuroi; append-only restoration with Protocol/Kotodama; proposal tracking handoff to Chousa).
- **calibration (preserved at 7):** Preserves all C2 counting commands, ledger cutoffs, and contract rules.
- **operability (preserved at 8):** Preserves all C1 runtime memfd descriptor execution and teardown invariants.

### Proposed Move
1. **Deliver Staged Cross-Lane Scope Supplement:** Deliver `.ufo/waves/round-52/w1/out/N1Overlap/cross-lane-scope-r52-supplement.md` documenting all 16 sibling touchpoints and formalizing four concrete handoff packets (`KAMA-R52-MEMFD-01` to Tsukuroi, `KAMA-R52-PROPOSAL-01` to Chousa, `KAMA-R52-CARRIER-01` to Kaidoku, `KAMA-R52-RESTORE-01` to Protocol). This stages the exact text needed for L1 to elevate `adjacency` to 8 at integration without mutating `corpus/knowledge/cross-lane-scope.md` during the wave.
2. **Formal Handoff to Chousa Proposal Schema:** Rather than implementing a redundant, diverging proposal validator in Kama, formally hand off `considerthese/2026-10-26.md` Proposal 2 to Chousa's canonical `CT-YYYYMMDD-n` schema via Packet `KAMA-R52-PROPOSAL-01`.

### Risks and Trace of Second-Order Effects
- **Scorecard Invalidation Risk:** Mutating `cross-lane-scope.md` in-place would immediately break `SCORECARD.md:19`'s 16-pipe-line check. Staging the supplement inside the seat output directory guarantees zero interference with the build tree.
- **Audit Permissiveness Risk:** Adding new files or sections to `cross-lane-scope.md` without updating the contract could cause `tools/append-only-audit.py` to evaluate them. Because the supplement is delivered in `.ufo/waves/`, it remains completely outside the audited contract paths.
- **Tooling Absorption Risk:** Attempting to copy Chousa's `considerthese-ledger-check.py` into Kama would violate `PROVINCE.md`. Routing the handoff via packet preserves strict domain boundaries.

### Verification
- **Scorecard Verification Check:** Verified that `python3 -c "print(sum(1 for l in open('corpus/knowledge/cross-lane-scope.md') if l.startswith(chr(124))))"` remains exactly `16`.
- **C1 & C2 Counter Invariance:** Verified that running `tools/round52-replay-memfd-audit.py` and `tools/round52-append-restore-check.py` on the build tree both pass (`met=True`, exit 0).
