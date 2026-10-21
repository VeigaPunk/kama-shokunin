VERDICT: confirm - hand re-derivation for round-11 matches the tool exactly: 0 raw defects, no false positive, no false negative, no tool-invisible defect.

Independent derivation (all commands executed; cwd noted per command)

1. Lane round-11 commit inventory
   `git -C /home/vgpnk/Projects/shokunin/kama-shokunin log --format='%H %an %ct %s' master`
   -> exit 0, 82 lines (transcript: .ufo/waves/round-21/build/out/AuditReport11-6/lane-log.txt).
   Author `kama-shokunin`, subject matching `^round-11:` or `^checkpoint(r11)`: exactly 2:
   - 3285cdf7a50481694a36c4425cf32c915ab5e5f0  ct 1792468575  round-11: calibrate historical provenance and extend identity coverage
   - fe57cc8a01acba9b6d7ed20e11b4914dfb68d903  ct 1792468676  round-11: record committed measurements and frontier verdicts
   `grep -c 'checkpoint(r11)' lane-log.txt` -> 0 matches (grep exit 1). No checkpoint(r11) exists.

2. Fleet first-add cutoff
   `git -C /home/vgpnk/Projects/shokunin log --diff-filter=A --format='%H %ct' -- .ufo/reports/round-11/kama.md`
   -> exit 0: dff173077a887df99b458d6fa07f68a099d92e9d 1792468776 (single add = first add).
   Split: both commits pre-report (<= 1792468776); post-report set empty.
   Window audit `awk '$2=="kama-shokunin" && $3>=1792450061 && $3<=1792468776'` -> exit 0, only those
   2 rows: no unpatterned kama-shokunin commit in the round-11 window (neighbors are protocol-shokunin's),
   so the subject-prefix filter hides nothing for this round.

3. Landed section tokens (## Landed changes span, chars 6226-7092)
   Tokens >=7 hex: `3285cdf7a50481694a36c4425cf32c915ab5e5f0`, `fe57cc8a01acba9b6d7ed20e11b4914dfb68d903`.
   `git -C lane cat-file -t` on each -> `commit`, exit 0. Both are the round-11 commits themselves;
   both pre-report commits cited in full -> landed-omitted 0, landed-unresolved 0, section present.

4. 40-hex tokens, whole report: 3 distinct — fe57cc8a…, 3285cdf7…, 2f7303c242319c1dc96c6bcf7702ac18b3ca1aad.
   `cat-file -t` in lane -> `commit` for all 3 (exit 0). In fleet -> fatal for all 3 (loop exit 128; negative
   evidence only — tool's is_object ORs lane-then-fleet, lane hit suffices). unresolved-full-hash 0.

5. Tool cross-check
   `python3 tools/report-landing-audit.py --rounds 11 --no-errata --json` (cwd lane root) -> exit 0:
   round_commits 2, required 2, post_report [], defects [], summary.status "clean", errata_rows 0.
   Matches my derivation exactly. No false positive, no false negative.

Tool-invisible-defect probes (all negative for round 11)
- Foreign-round citation: the only Landed citations are the two round-11 commits (subjects verified `round-11:`). None.
- Wrong hash to unrelated object: 2f7303c2… resolves to a real lane commit (protocol-shokunin, "Integrate remote
  documentation; preserve local round log") used outside Landed as the frozen-baseline pointer; no kind applies. None.
- Regex false positive: `feedbac` inside "lesson §Prior outside feedback" is matched by a hex-only-bounded probe
  but NOT by the tool: FULL/ABBREV use `(?<![0-9A-Za-z])…(?![0-9A-Za-z])`, so trailing `k` blocks it. Correctly ignored.
- [INFERENCE] Semantics attested by reading audit_round/round_commits/report_cutoff (tools/report-landing-audit.py:61-143):
  citation = any 7..40-hex Landed token t with commit sha.startswith(t); cutoff inclusive `ctime <= cutoff`;
  author via %an; branch master default. My manual rules mirrored these before reading the source.

Axes (godspeed): calibration+operability evidence quality improved by an executed independent re-derivation; no lane, fleet, or tool mutation. Tool installs: none.
