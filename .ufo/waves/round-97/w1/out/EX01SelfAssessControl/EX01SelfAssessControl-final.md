# EX01SelfAssessControl — final output (verbatim from w1-results.json by the L1)

Seat `EX01SelfAssessControl`, agent `executor`, wave kama r97 w1. This file is the seat's final
output string copied verbatim from `.ufo/waves/round-97/w1-results.json`; the L1 added only
this header. The seat's own receipts sit beside it.

```
{
  "seat": "EX01SelfAssessControl",
  "wave": "kama r97 w1",
  "claim_attacked": "C1 calibration — tools/round97-self-assessment-audit.py (14 checks; base mismatches=9)",
  "files_changed": [
    ".ufo/waves/round-97/w1/EX01SelfAssessControl.md (advisory report)",
    ".ufo/waves/round-97/w1/out/EX01SelfAssessControl/ (27 receipts: canonical runs, per-check matrices, 12 mutant receipts, strace, K1 bytes, instrumented observer, runner)"
  ],
  "lane_tracked_files_changed": "none; no lane git/jj mutation, no commits, no tracked-file edits",
  "revisions_graded": {
    "base": "40763bd2ca1e3f99881247eaa9f5e3ef3b596653",
    "freeze": "9e605d416c199b3c9913a2125b04f9c5a16f5668",
    "master_at_grading": "e057166e09ec069725bd0b0433fc50275ecd03ea"
  },
  "predicate_reproduction": {
    "base": "SELF_ASSESS97 checks=14 mismatches=9 met=False, exit 1",
    "freeze": "SELF_ASSESS97 checks=14 mismatches=0 met=True, exit 0",
    "master": "SELF_ASSESS97 checks=14 mismatches=0 met=True, exit 0",
    "measured_c1_out_at_grading": "untracked in lane worktree; content SELF_ASSESS97 checks=14 mismatches=0 met=True / c1_exit=0; no M1 commit exists yet"
  },
  "required_mutants": [
    {
      "mutation": "SCORECARD depth-row digest last nibble wrong",
      "rev": "a8bea94b",
      "result": "red, mismatches=1, check 1 fires"
    },
    {
      "mutation": "SKILL round-97 boundary ceiling 833,332 -> 833,334, one line",
      "rev": "ed67f5b2",
      "result": "red, mismatches=1, check 1 fires only (digest collateral, not ceiling content); C3 red mismatches=2"
    },
    {
      "mutation": "same ceiling change + SCORECARD depth digest re-anchored to mutant bytes (self-consistent liar)",
      "rev": "f1c18f9f",
      "result": "GREEN (14,0); C3 red mismatches=2 — C1 does not grade the round-97 boundary table"
    },
    {
      "mutation": "S621 teaches reverted to constant-6 sentence",
      "rev": "aa79007d",
      "result": "red, mismatches=1, check 10 fires"
    },
    {
      "mutation": "probe MAX_STEPS 5_000_000 -> 4_000_000, comment untouched",
      "rev": "4a8f8f3e",
      "result": "red, mismatches=2, checks 8+9 fire; C3 red mismatches=3"
    }
  ],
  "green_false_passes": [
    {
      "tag": "B4p",
      "rev": "4971edba",
      "mutation": "round-96 step-cost nd=1 ceiling 833,332 -> 833,334 + digest re-anchor",
      "c1": "GREEN",
      "c3": "green",
      "round96_depth_audit": "green",
      "mechanism": "check 9 whole-file substring; 833,332 survives in the round-97 boundary table — sharpest gap: a false decidable-header cell passes all three counters"
    },
    {
      "tag": "B1p",
      "rev": "f1c18f9f",
      "c1": "GREEN",
      "c3": "red",
      "mechanism": "round-97 table arithmetic not a C1 surface; digest re-anchored"
    },
    {
      "tag": "B2p",
      "rev": "c55477eb",
      "mutation": "boundary row steps 5,000,002 -> 4,999,998 + digest",
      "c1": "GREEN",
      "c3": "red mismatches=1"
    },
    {
      "tag": "C2",
      "rev": "5283e185",
      "mutation": "S621 teaches keeps prefix+token but asserts constant 6 is the budget",
      "c1": "GREEN",
      "mechanism": "check 10 tests prefix + token presence, not what the cell says"
    },
    {
      "tag": "E1",
      "rev": "af7bf3fd",
      "mutation": "probe comment says 'a constant six steps per tensor header'",
      "c1": "GREEN",
      "mechanism": "check 7 exact-string absence; 'six' is not '6 steps per tensor header'"
    },
    {
      "tag": "E2",
      "rev": "d5bde629",
      "mutation": "graded ceiling comment states 900,001 at nd=1; correct digits on a non-graded line",
      "c1": "GREEN",
      "mechanism": "check 8 whole-file search, not comment-scoped"
    },
    {
      "tag": "F",
      "rev": "c281bc67",
      "mutation": "SCORECARD round-96 C2 quote falsified checks=14 -> checks=99; banner keeps true needle",
      "c1": "GREEN",
      "mechanism": "checks 13-14 needle anywhere in SCORECARD"
    }
  ],
  "per_check_matrix": {
    "base": "1:F 2:F 3:F 4:P 5:P 6:F 7:F 8:F 9:F 10:F 11:F 12:P 13:P 14:P (9 mismatches)",
    "freeze_master": "all 14 P",
    "k3_literal": "FAILS: checks 4,5,12,13,14 are green at base and at M1 for the same reason; literal K3 voids C1",
    "k3_defect_class": "passes: checks 1,2,3,6,7,8,9,10,11 flip F->P and are exactly the 9 base mismatches",
    "k2": "not evaluable: no M1 commit; untracked measured/c1.out reproduces the predicate line"
  },
  "offline_verification": {
    "static": "imports only argparse/re/subprocess/sys/pathlib/hashlib; every subprocess argv is git; no socket/urllib/http/requests/curl and no endpoint strings",
    "strace": "strace -f -e trace=network: 0 network syscalls",
    "namespace": "bwrap --dev-bind / / --unshare-net run: checks=14 mismatches=0 met=True exit 0",
    "unshare": "unshare -n unavailable in container (Operation not permitted), recorded"
  },
  "exit_codes": {
    "nonexistent_rev": "exit 2 with could-not-evaluate",
    "tree_rev_40763bd2^{tree}": "exit 2",
    "root_commit_missing_files": "exit 2"
  },
  "kill_rule_verdict": {
    "K1": "pass — working counter sha256 6b912747…c794c equals the 9e605d41 blob; only 9e605d41 on master touches the file; git diff vs freeze empty",
    "K2": "not evaluable at M1 (M1 absent); green at 9e605d41 and e057166e; untracked receipt reproduces",
    "K3": "fails on literal wording (5 checks green at both); passes only if scoped to the 9 defect-class checks; counter output exposes no per-check identity so K3 is uncheckable from the frozen predicate alone"
  },
  "verdict": "C1's predicate reproduces and the base control is honest (9 mismatches exactly the nine defect-class checks), but the counter does not grade the binding claim semantically: checks 7/8/9/10/13/14 are literal-presence tests over the whole file, and check 1 makes SKILL content changes detectable only as a digest red. Seven concrete green false passes are shown. Admit at most as a point-in-time byte/provenance receipt for the 14 named surfaces; calibration should not move on this counter alone. Successor recommendations (section-scoped parsing of the comment/tables, semantic rejection of constant-6 equivalents, row-scoped receipt quotes, per-check output, K3 scoped to defect-class checks) are in the report; no frozen file was edited.",
  "risks_blockers": [
    "No M1 commit: C1's predicate cannot be verified at M1 until integration commits it; measured/c1.out is untracked.",
    "Lane is concurrently written by other wave seats; master may advance beyond e057166e.",
    "Mutant commits exist only in the deleted scratch clone; receipts in the out dir preserve exact diffs, revisions and outputs.",
    "Round-96 disclosure audit is red at the round-97 tree by design (it requires the false constant-6 string) — noted so it is not misread."
  ],
  "tooling": "no installs or upgrades; no pacman; no host/sysctl/service changes",
  "scratch": "/fast/scratch/hyaku/kama-r97/EX01SelfAssessControl created, used, and deleted after copying receipts"
}
```
