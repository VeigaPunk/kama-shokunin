VERDICT: confirm - §Gate standard pins 0=clean, 1=failed fleet-wide, undeclared nonzero=could-not-evaluate (kimi-shokunin e737d2ea, lines 393-397); row candidate S058 drafted and census-validated.
Seat: SrcGateStandard-2, BUILD wave, round 20, lane tip 37bd4c5. No tools installed. No processes or scratch left behind.

1. Source identity and revision (all commands executed)
- `git -C /home/vgpnk/Projects/kimi-shokunin log -1 --format=%H -- skills/shokunin/protocol/PROTOCOL.md`
  → `e737d2ea97f6b0198503e077676c3f2ea07974a9` (commit "shokunin: unify source curation, mistake learning and verified craft rounds", 2026-10-19T21:21:25-03:00), exit 0.
- Worktree equal to that revision: `git status --porcelain=v1 -- <file>` → empty, exit 0; local HEAD = e737d2ea; `git rev-parse e737d2ea:<path>` → blob `2a50081fab213d46019b697c81191bbff2fa5378`, exit 0.
- `sha256sum` worktree file → `622b29a043046f0b3b3c7a2240fe62ab516898922885685dd8d89f50b1739fd0`; raw.githubusercontent.com at e737d2ea → identical digest (exit 0); blob URL and raw URL answer HTTP 200 unauthenticated.
- Remote moved ahead: `git ls-remote origin refs/heads/main` → e5eccc0c (exit 0). Fetched that head into a scratch clone only (lane and fleet repos untouched); `git diff e737d2ea..FETCH_HEAD -- <path>` → empty and blob at FETCH_HEAD is the same 2a50081f — PROTOCOL.md unchanged upstream.

2. Verbatim verdict-map rules, §Gate standard (heading at line 388)
- **Verdict.** (lines 393-397):
  "- **Verdict.** `0` = `clean` and `1` = `failed` fleet-wide; every other code a gate exits (`2`, `3`,
    `64`, …) is declared in its registry entry and mapped onto `clean | failed | could-not-evaluate`,
    and an undeclared nonzero code reads as `could-not-evaluate`. Nothing else is pinned: a gate's own
    vocabulary — WARN vs HIT, a missing baseline, finding kinds — stays lane-owned, and this section
    governs the outer interface only."
- Related, same section: an edited snapshot is `snapshot_tampered` (could-not-evaluate) at line 409; registry rows carry "verdict map (code → class)" at line 415; **Closure consequence.** (lines 425-430): the integrator verifies committed evidence and "does not execute a sibling's gate".
- Which copy is canonical: byte-identical Verdict bullet also in fleet-root /home/vgpnk/Projects/shokunin/PROTOCOL.md (lines 380-384) at 7c5b34f0743e1c0779b32e5de113c5b18c03ef9f (worktree sha256 886e459b…d4411a); `diff` of the two §Gate standard sections differs only in the **Delivery.** parenthetical (canonical driver). The kimi-shokunin copy is the one lane verifiers line-cite: corpus/lessons/round-12-verifier-spotcheck.md:44 cites "lines 425-430", which match kimi's **Closure consequence.**, not the root copy's 412-417.
- [INFERENCE] Scope caveat: the text pins the meaning of exit codes for *gates*; "1 = failed fleet-wide" is stated in the same bullet that covers every other code, so no registry declaration can remap 1. Whether probes (registered as such) fall under the same pin, and whether a signal death (no exit code) is governed at all, is not answered by this section.

3. SOURCES row candidate — validated
- Draft (queued, kind spec, tier A, own-protocol scope), quote and integration note:
  .ufo/waves/round-20/build/out/SrcGateStandard/sources-row-S058.md (row bytes cmp-verified exit 0 against the validated scratch copy).
- Validation: lane tree at 37bd4c5 extracted to scratch (git archive; sha256 of corpus/SOURCES.md 8b6b1c7d…97c96 before and after extraction); baseline `bash scripts/sources-census.sh validate --today 2026-10-21 <scratch>` → only the 3 known W04 rows, exit 0, matching .ufo/waves/round-20/sources/census-before.txt (57 rows, A 54, C 3, queued 5, mined 46, rejected 6). After appending S058: validate exit 0, no new E/W codes; census → 58 rows, tier.A 55, tier.C 3, queued 6; overdue → `lane cadence S058 recheck=every round opened=2026-10-21`; row NF=13 (11 columns). Census script copies byte-identical across fleet root and kimi-shokunin (cmp exit 0, sha256 3fb72615…4a64e30).
- Located quote for the round-20 lesson §Gate (rule 1, ≤25 words): "`0` = `clean` and `1` = `failed` fleet-wide" (8 words, line 393); "an undeclared nonzero code reads as `could-not-evaluate`" (7 words, line 395). The middle clause "…mapped onto `clean | failed | could-not-evaluate`" (lines 393-394) cannot go inside a registry cell (literal `|`); it is quoted in full above.
- L1 owns SOURCES.md: id S058 assumes no other row lands first; renumber if needed.

4. Bonus observations for C1 "errors are not verdicts" (executed, exit shown for each)
- Python 3.14.8 on this host: uncaught `raise RuntimeError` → exit 1, and `sys.exit("msg")` → exit 1 (both observed, exit 0 for the probe commands). Under this section exit 1 reads `failed` fleet-wide, so the outer interface alone cannot separate a gate crash from a gate verdict; separating them requires observing the gate's lane-owned stdout (e.g. the `INVALID ` literal) — exactly the C1 fix direction. Signal death: `Popen.returncode` = -15, shell status 143 (observed); no lane registry I checked declares 143, so per this section it reads could-not-evaluate, not failed.
- citation-provenance.py exits 1 where it documents 2 (routed defect): by this section that maps a could-not-evaluate condition onto `failed`. [INFERENCE] Repair should give it a non-1 code (declared, mapped to could-not-evaluate).
- Conformance conflict in the lane's own registry: SKILL.md:303 and :306 (bytes equal to tip 101f3991, tree clean at 37bd4c5) map `bash tools/kama-probe.sh check|snapshot` as "2 failed/drift; 1 could-not-evaluate/probe error", while the tool `die()`s with exit 1 (kama-probe.sh:90) and gates drift with exit 2 (:883). Observed: unknown flag → exit 1, missing subcommand → exit 1 (scratch copy). Since 1 is pinned `failed` fleet-wide and only "every other code" is registry-declarable, every kama-probe tool error misreads as a failed verdict fleet-side. SKILL.md:463-464 already warns "Do not transfer exit meanings across tools", and lessons/round-5.md:106 records the drift exit 2 — the 1/2 inversion against the fleet pin looks unrecorded (grep over corpus/LOG/QUALITY found no prior mention). Routing is the L1's call: change exit codes (consumer-visible) or record as an error-injection cell.

Scratch /tmp/kama-r20-SrcGateStandard deleted after these runs.
Report: .ufo/waves/round-20/build/advice/SrcGateStandard.md
