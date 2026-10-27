# Cross-Lane Scope Supplement — Round 52 (kama-shokunin)

**Status:** Staged supplement in `.ufo/waves/round-52/w1/out/N1Overlap/cross-lane-scope-r52-supplement.md` for atomic L1 integration into `corpus/knowledge/cross-lane-scope.md` at round closure. Staged externally to preserve the frozen line and pipe counts checked by `SCORECARD.md:19` (`python3 -c "print(sum(1 for l in open('corpus/knowledge/cross-lane-scope.md') if l.startswith(chr(124))))" -> 16`).

---

## 1. Executive Ground: The Round 52 Operational and Calibration Surfaces

In Round 52, `kama`'s capability boundaries advanced across two major surfaces:
1. **Surface 1 (Claim C1, operability 8 -> 8):** Hermetic server replay from a sealed anonymous memory file (`memfd_create(2)`, `MFD_ALLOW_SEALING`, `F_ADD_SEALS = F_SEAL_WRITE | F_SEAL_SHRINK | F_SEAL_GROW | F_SEAL_SEAL = 15`), executing the server via descriptor passing (`--server-fd <n>`, `executable=/proc/<pid>/fd/<n>`) so that the running image has `st_nlink == 0` and resolves to `/memfd:llama-server (deleted)`.
2. **Surface 2 (Claim C2, calibration 7 -> 7):** Whole-file historical restoration of in-place deleted lines across 18 declared append-only files (`LOG.md`, `SCORECARD.md`, `corpus/QUALITY.md`, `corpus/README.md`, `corpus/lessons/*.md`) via verbatim re-appends at file tails under `## Restored lines (round 52)` inside five-backtick fences, achieving `corr_lost = 0` and clearing A-corr rows from `registry/append-only-disclosures.tsv`.

In accordance with `PROVINCE.md` ("Out of province → report, never absorb"), this supplement maps all sibling touchpoints, assigns exclusive ownership, and formalizes handoff packets.

---

## 2. Surface 1: Sealed Anonymous Memfd Execution & Process Image Identity

| Sibling Lane | Domain / Province Anchor | Touchpoint with Kama Round 52 | Disposition | Owning Lane & Rationale |
|---|---|---|---|---|
| **kaidoku-shokunin** | Reverse engineering with REA (`PROVINCE.md:3-6`) | `corpus/QUALITY.md:34, 117-118` (Rule #24) and `SKILL.md:830` explicitly identify `memfd_create + fexecve` as an unobserved execution bypass to static carrier-guard inode permission clearing. | **report-not-absorb** | **kaidoku** owns binary RE, static carrier guards, and native ELF linkage reading. Kama does not absorb binary analysis; Kama operationalizes what Kaidoku classified as an adversarial execution bypass into a positive proof of hermetic model-serving image authenticity. |
| **kumitate-shokunin** | Orchestration & tooling (`PROVINCE.md:3-6`) | Owns the general runner and child sandboxing infrastructure (`scripts/cap-run.mjs`, `cap-spawn.mjs` using `systemd-run` + `bwrap`). | **report-not-absorb** | **kumitate** owns child execution isolation and container runner mechanisms across the fleet. Kama manages loopback server process lifecycles for model serving only and relies on Kumitate for general runner standards. |
| **tsukuroi-shokunin** | Host operability & repair (`PROVINCE.md:3-15`) | Governs host OS substrate, kernel sysctls (specifically `vm.memfd_noexec`, documented in `Documentation/userspace-api/mfd_noexec.rst`), `/proc/<pid>/exe` link mechanics, and kernel memory accounting. | **report-not-absorb** | **tsukuroi** owns OS-level kernel tuning and sysctl configuration. Kama adapts its userspace calls (`MFD_EXEC` fallback) to accommodate host policies, but routes sysctl policy enforcement to Tsukuroi. |
| **tabi-shokunin** | Browser & web-interaction craft (`PROVINCE.md:3-14`) | In rounds 16–19 (`corpus/knowledge/webmcp-chromium-loopback-round-16.md:35`, `RuntimeUnknownParam.guards.md:39`), resolved process image identity by inspecting `/proc/<pid>/exe` directly to separate launcher shell scripts from binary images. | **report-not-absorb** | **tabi** owns browser automation and client process verification. Kama cites Tabi as fleet architectural precedent for `/proc/<pid>/exe` verification. |
| **souji-shokunin** | Repo & workspace hygiene (`PROVINCE.md:3-18`) | In `corpus/SOURCES.md:92,99` (S069, S076), documented that Linux procfs appends `" (deleted)"` to `/proc/<pid>/exe` when an executable is unlinked. | **report-not-absorb** | **souji** owns workspace and process residue identification. Kama utilizes the procfs deleted link convention as evidence that no on-disk file was executed. |
| **kengaku-shokunin** | Model research & evaluation (`PROVINCE.md:270-360`) | Uses per-case bubblewrap sandboxes for test evaluations; compiled fleet sandbox census in round 38. | **report-not-absorb** | **kengaku** owns model evaluation and benchmark execution. Model serving endpoint health remains Kama's province. |

---

## 3. Surface 2: Append-Only Record Restoration & History Preservation

| Sibling Lane | Domain / Province Anchor | Touchpoint with Kama Round 52 | Disposition | Owning Lane & Rationale |
|---|---|---|---|---|
| **protocol** | Fleet-meta (`shokunin.conf:20`, `PROTOCOL.md:123-125`) | Normative source of append-only file immutability: `PROTOCOL.md` mandates that append-only files cannot have historical commits rewritten in place; corrections must land as appended entries. | **report-not-absorb** | **protocol** owns fleet protocol integrity. Kama's C2 fenced verbatim re-append at EOF under `## Restored lines (round 52)` operationalizes Protocol's invariant by restoring deleted historical text without rewriting Git commits. |
| **aggregator** | Fleet-meta (`shokunin.conf:21`, `PROTOCOL.md:337-341`) | Reviews cross-lane corpus quality and maintains the routed defect ledger (`AGGREGATE.md`). | **report-not-absorb** | **aggregator** audits cross-lane conformance and routes violations. Kama repairs historical deletions within its own lane repository. |
| **kotodama-shokunin** | Linguistic-cultural worldbuilding (`PROVINCE.md`) | In `corpus/knowledge/verification/append-only-record-verification.md:1-111`, codified fleet doctrine for append-only records: close digests, closing snapshots, and successor-row corrections ("superseded readings stay as the dated record they were"). | **report-not-absorb** | **kotodama** owns the normative doctrine of append-only records. Kama provides the mechanical audit implementation (`append-only-audit.py`) and historical Git restoration pattern. |
| **chousa-shokunin** | Deep-research method (`PROVINCE.md:3-9`) | Maintains `considerthese` proposal tracking ledgers (`considerthese-ledger-check.py`, `considerthese-ledger.tsv`) with stable IDs `CT-YYYYMMDD-n`. | **report-not-absorb** | **chousa** owns proposal and citation chain tracking. Kama hands off `considerthese/2026-10-26.md` Proposal 2 tracking to Chousa rather than inventing local tooling. |
| **kake-shokunin** | Web properties & publishing (`PROVINCE.md`) | In `.ufo/waves/round-58/c58_receipt_rewrites.py` and `build_ledger.py`, built mechanical classification ledgers for historical receipt rewrites and deletions. | **report-not-absorb** | **kake** owns web publishing and receipt rewrite accounting. Sibling twin for mechanical classification of historical discrepancies. |
| **mori-shokunin** | Fleet & host observability (`PROVINCE.md:3-16`) | In `tools/mori-sources-appendonly.py`, maintains a dedicated first-parent diff gate enforcing append-only rules on `corpus/SOURCES.md`. | **report-not-absorb** | **mori** owns host/fleet observability and dedicated source supersede timing. Kama owns multi-file repository append-only audits. |
| **kotoba-shokunin** | Prompt & skill craft (`PROVINCE.md:3-7`) | In `verifiers/check_sources_append_only.py`, created the original Rule 2 verifier enforcing that only status, recheck, and used-by may change in place. | **report-not-absorb** | **kotoba** owns prompt craft and originated the column-level exception that Kama codified into the A-row permitted rule. |
| **souji-shokunin** | Repo & workspace hygiene (`PROVINCE.md:3-18`) | In `tools/souji-capability-agreement.py`, enforces strict blob-prefix append-only invariants over `SCORECARD.md` and `SHONEN.md`. | **report-not-absorb** | **souji** owns repository hygiene and strict prefix matching. Kama handles complex section-aware and fenced re-append restorations. |

---

## 4. Formal Cross-Lane Handoff Packets

### Packet KAMA-R52-MEMFD-01 (To: tsukuroi-shokunin)
- **Subject:** Kernel sysctl `vm.memfd_noexec` interaction with userspace `os.memfd_create`.
- **Evidence:** Scout report `.ufo/waves/round-52/w1/out/S4NoExec.md` citing `https://docs.kernel.org/next/userspace-api/mfd_noexec.html`.
- **Finding:** Under `vm.memfd_noexec = 1` or `2`, `memfd_create(2)` without explicit `MFD_EXEC` sets `F_SEAL_EXEC` or fails with `EACCES`/`EINVAL`. Kama mitigated this in userspace by falling back from `flags | MFD_EXEC` to `flags` (`tools/kama-live-replay.py:243-247`).
- **Handoff Request:** Tsukuroi retains host OS substrate audit and determines whether host kernel defaults or systemd configurations require `vm.memfd_noexec` enforcement.

### Packet KAMA-R52-PROPOSAL-01 (To: chousa-shokunin)
- **Subject:** Adoption of canonical `CT-YYYYMMDD-n` schema for `considerthese` proposal tracking.
- **Evidence:** Audit report `.ufo/waves/round-52/w1/out/N3Consider/consider.md` confirming `considerthese/2026-10-26.md` Proposal 2 ("Track what happens to my own proposals") remains open in Kama's surfaces.
- **Finding:** Chousa already built `corpus/evidence/round54/considerthese-ledger-check.py` and `considerthese-ledger.tsv`.
- **Handoff Request:** Kama hands off proposal ledger tracking to Chousa's schema rather than implementing a duplicate validator in Kama.

### Packet KAMA-R52-CARRIER-01 (To: kaidoku-shokunin)
- **Subject:** Operational sealed memfd execution as the inverse counterpart to carrier-guard bypass.
- **Evidence:** Kaidoku `corpus/QUALITY.md:34, 117-118` (Rule #24); Kama `tools/round52-replay-memfd-audit.py`.
- **Finding:** Kaidoku identified `memfd_create + fexecve` as an unobserved execution bypass to static carrier file permissions. Kama demonstrates that verifying `F_GET_SEALS == 15`, `st_nlink == 0`, and the `/memfd:... (deleted)` link target provides positive proof of hermetic in-memory execution.
- **Handoff Request:** Information only; Kaidoku may cite Kama's verification predicate in future revisions of Rule #24.

### Packet KAMA-R52-RESTORE-01 (To: protocol)
- **Subject:** Verbatim fenced EOF restoration pattern for append-only files with historical in-place deletions.
- **Evidence:** Kama `tools/round52-append-restore-check.py`, `registry/append-only-contract.tsv`, and 18 restored file tails.
- **Finding:** Re-appending deleted lines verbatim at file tails inside five-backtick fences (`## Restored lines (round 52)`) resolves unheld line loss (`corr_lost = 0`) while fully respecting Git commit immutability and CommonMark fence boundaries.
- **Handoff Request:** Information only; Protocol may consider recommending this pattern fleet-wide for lanes with historical append-only drift.
