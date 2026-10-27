# K8Routed — round-53 routed-defect completeness report

Verdict: **pass — no routed item (R1–R4, both operator items, the three orchestrator notes, the four SHONEN boxes) is silently dropped by the round-53 build `c22602bd`; every item has build bytes, a live wave seat, or a disclosed preregistration limit, with two forwarding/integration watch items flagged below.**

Full analysis: `.ufo/waves/round-53/w1/out/K8Routed/routed.md`. Method: read-only git over a
`--shared` clone (`/fast/scratch/hyaku/kama-r53/K8Routed/lane`, toplevel asserted); no counter
executed (completeness review only); wave outputs not yet committed, so "wave seat" rows cite
`.ufo/waves/round-53/w1/spec.json` / `build_spec.py` dispatch.

## Item-by-item dispositions (evidence: command → output)

- **R1 (S505 anchor, closure line 134) → answered in build.** `git show c22602bd -- corpus/SOURCES.md`
  adds S509 at `corpus/SOURCES.md:262` (quote line 491, 7 words; supersedes S505; S505 left as
  filed), lesson `corpus/lessons/round-53.md` Gate row, copy
  `.ufo/waves/round-53/c1/ggml-backend-reg.cpp.b11909`. Remains: lesson Mistakes/Errata
  (W1Mistakes, W5Routed seats live), anchor-check QUALITY row (S6Anchors seat live).
- **R2 (carried C1 limits, closure lines 135–140) → libraries CLOSED, rest disclosed/carried.**
  `measured/c1-build.out:5,8,11` — 8 archive libraries byte-equal in /proc/<pid>/mem ×3,
  `code_mappings`/`own_code` recorded (`tools/kama-llamacpp-live.py:774` `code_mappings()` new in
  build diff). Model mapping NOT compared — disclosed in preregistration limit 3
  (`grep gguf\|model measured/c1-build.out` code lines → 0 hits); host-install memfd still meets —
  preregistration limit 1; seats J6HostMemfd, S5Limits, K1Cheat live for the open sub-items.
- **R3 (round-52 C2 limits, closure lines 141–145) → all four carried, none dropped.**
  `git diff 4229ea1b..c22602bd --stat` does not touch `tools/round52-append-restore-check.py`;
  W5Routed's errata item explicitly answers R3; round-53 C2 adds its own disclosed limits
  (preregistration limits 4–5; K6Scope/K7Calib seats live).
- **R4 (seat-report immutability, closure line 146) → not in build, seat live.**
  Build stat has no new immutability tool; seat **X9Immut** (build_spec.py:169) builds and runs it.
  Watch: if X9Immut's output is not integrated, R4 silently carries to round 54.
- **Operator ed135b3c (closure line 147) → no lane bytes (correct), Rv1Ed135 drafts the L0.**
  `LOG.md` untouched by build; restored block persists at `LOG.md:2358`; seat **Rv1Ed135**
  (build_spec.py:189) drafts `kama | round-53 | <question>`. **Watch item 1:** the lane cannot
  file L0 at the fleet root — the L1 must forward the drafted question in the round report; round
  52 dropped it exactly this way ("routed it only in its report and filed no L0 line").
- **Operator carried L0 (closure line 148, planner/axes/worktree) → carried by design;**
  W5Routed errata item names them; nothing for the lane to build.
- **SHONEN promotion boxes (closure lines 149–153) → all four `[~]` at build (`SHONEN.md:7–19`,
  untouched); box 1 ← X6Battery + SKILL §Round-53 registry (integration item); box 2 evidence
  persists and the round-53 counter keeps the sealed leg
  (`tools/round53-replay-code-audit.py:35`); box 3 ← **X4Fresh** seat live (the exact gap the
  closure named); box 4 ← Sc3Province seat live. Promotion itself stays operator-owned — no seat
  marks it, correctly.
- **Orchestrator note M09/M10/M11 → target code unchanged by build.** Build diff on
  `tools/kama-llamacpp-live.py` adds only `code_mappings`/`_code_mappings_selftest` and selftest
  wiring; `sealed_fd()` (:861), `file_seals()` (:853), `server_exe()` (:731),
  `_server_fd_selftest()` (:1713) byte-identical to base. Round-52 fact:
  `.ufo/waves/round-52/w1/out/M3Live/c1-matrix.tsv` rows M09–M11 `met=True` (survived). Seat
  **M4SealedFd** re-applies all three at the build and writes killing selftest cases.
- **Orchestrator note kama-probe.sh /tmp → closed at round 52, re-verified this round.**
  `tools/kama-probe.sh:1128` honours `KAMA_PROBE_TMPDIR`/`TMPDIR` (round-52 seat Sen2Scratch);
  neither round-53 counter references the probe and `grep '"/tmp\|/tmp/'` over both counters and
  both changed tools → no hardcoded /tmp. Seat **Sen2Scratch** reruns the bwrap read-only-/tmp
  watcher against the round-53 C1 counter.
- **Orchestrator note provider exhaustion → process obligation on the L1.**
  `.ufo/waves/round-53/w1/dispatch.json` registry: 66 members, `counts {spawn:66, resume:0,
  total:66}`, none dead as of commit. **Watch item 2:** at WAVE-DONE the L1 records dead seats in
  w1-results + round report (round-16/17 fleet-report format); nothing records them
  automatically.

## Findings (not new lane defects; integration watch items)

1. **ed135b3c L0 forwarding (risk: drop repeats).** Closure line 147 records round 52 filed no L0
   line; round 53 again only drafts the question (Rv1Ed135). Fix: L1 quotes the drafted
   `kama | round-53 | …` line in the round report to the operator. Cost: one paragraph.
2. **R2 open limits must reach SCORECARD §Round 53 / Planned (round 54).** Today they live only in
   the frozen preregistration (`limits[0]` provenance, `limits[2]` model). If the integration
   SCORECARD text omits them, they become silently dropped at the measured commit. Fix: in the
   §Round-53 limits text name (a) the archive-stream witness / provenance and (b) the model
   mapping compare as round-54 carries.

## Commands exercised (all read-only; clone toplevel asserted)

- `git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin $S/lane` →
  `git rev-parse --show-toplevel` = `/fast/scratch/hyaku/kama-r53/K8Routed/lane`; tip `bc8e6e7f`
  (build `c22602bd`, freeze `d01b2b6d`, base `4229ea1b`).
- `git show --stat c22602bd` → 12 files, 2980 insertions; LOG.md/SHONEN.md/QUALITY.md absent
  (integration pending, as the assignment states).
- `git show c22602bd -- corpus/SOURCES.md registry/cited-path-corrections.tsv SKILL.md` →
  S506–S509, 14 ledger rows + header, two SKILL in-place corrections (lines 113, 895).
- `git diff 4229ea1b..c22602bd -- tools/kama-llamacpp-live.py | grep -iE 'seal|nlink|def '` →
  only new code-mapping code and comments; sealed_fd region untouched.
- `grep -n '"/tmp\|/tmp/' tools/round53-*.py tools/kama-live-replay.py tools/kama-llamacpp-live.py`
  → no hardcoded /tmp.
- `python3 -c json` over `preregistration.json` (6 limits), `dispatch.json` (66 members),
  `w1/spec.json` (66 seats incl. M4SealedFd, Sen2Scratch, X9Immut, X4Fresh, Sc3Province,
  X6Battery, Rv1Ed135, W1Mistakes, W5Routed, S5Limits).
- `grep` of `round-52-verifier-spotcheck.md` §6 lines 134–153; `M3Live/c1-matrix.tsv` M09–M11;
  `measured/c1-build.out` lines 5/8/11; `SHONEN.md:7–19`; `LOG.md:2358,2428`;
  `tools/kama-probe.sh:1128`; `tools/round53-replay-code-audit.py:35`.

No installs or upgrades were needed (no tool missing for a read-only git/grep review); per the
pacman guard none were attempted.

Wrote:
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/K8Routed.md` (this report)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/K8Routed/routed.md`
