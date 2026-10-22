# ReviewerLessonMistakes — verification log (wave 2, falsify; 2026-10-22)

Target: `corpus/lessons/round-25.md` §Mistakes. Bytes reviewed: lane working copy at
review time (mtime 07:13, sha256 `c26728b01de53fb6fe272f98d32ae972df2a211121edf0039144d5b40c73e188`
per ScoutMisroot), which differs from pinned tip `fa3b62ae` (blob sha256
`9d7ec2953b39469b7094ee830c429a5ac7c3a6add72625d77a2e856592476a16`, same bytes at master
`46be41cf`). `git diff fa3b62ae -- corpus/lessons/round-25.md` (read-only) shows the
uncommitted deltas: the misroot row and the axis-misfiled row are NEW (not present at
`fa3b62ae`), the chronology and false-timestamp rows are rewritten, and §C1 result is
rewritten ("Axis fit is contested..." → "Axis fit is not established..."). Per-row verdicts
cover the working-copy text; fa3b62ae deltas are named per row. Per-row verdicts
cover the working-copy text; fa3b62ae deltas are named per row.

All lane git commands read-only (`diff`, `show`, `log`, `status` via clone only). Git-writing
(checkouts) ran only in my clone `/fast/scratch/hyaku/kama-r25a2w2/ReviewerLessonMistakes/clone`.
No llama-server child, no port, no installs, no jj command.

## A. Re-runs (commands + observed output + exit code)

A1. Registered C1 counting command (preregistration.json C1.command), run from my clone
    checked out at each revision. Output `rc` is the command's exit code:

```
147f5bdd rc=0 :: registered 27 stale 2 ['M11-listing-surrogates', 'M17-ref-shadow']
efe58e96 rc=0 :: registered 27 stale 2 ['M11-listing-surrogates', 'M17-ref-shadow']
92063cf  rc=0 :: registered 27 stale 2 ['M11-listing-surrogates', 'M17-ref-shadow']
1fc41e34 rc=0 :: registered 28 stale 0 []
fa3b62ae rc=0 :: registered 28 stale 0 []
e876b95  rc=0 :: registered 31 stale 0 []
ed1cc3a  rc=0 :: registered 27 stale 0 []
```

Confirms row 1 (red at efe58e96, green at 1fc41e34, both exit 0), the row-1 claim that the
M11 literal stopped matching at 92063cf (stale 0 at ed1cc3a, stale 2 first at 92063cf), and
the row-7 parenthetical "counter `stale 0` at e876b95 and ed1cc3a, stale from 92063cf".
Cross-check: CriticC1AxisFit §1 (`a2-falsify/out/CriticC1AxisFit/c1-command-history.txt`)
reports the same outputs at the same revisions, including 2e254a1 27/0 and 46be41c 28/0.

A2. C2 counting command (amendment-4 counter bytes, `.ufo/waves/round-25/count-c2.py`):

```
python3 .ufo/waves/round-25/count-c2.py
  -> registered 14 observed 14 bound True missing []   rc=0
git show 5ea4fc4:.ufo/waves/round-25/final/context-capacity-receipt.json > scratch/receipt-5ea4fc4.json
python3 .ufo/waves/round-25/count-c2.py <that file>
  -> registered 14 observed 11 bound True missing ['L1', 'L2', 'L3']   rc=0
```

Confirms row 3's "first committed receipt ... scores 11 of 14 under amendment 4 because it
lacks request times" (missing set is exactly the three load cells).

A3. Committed C1 full-run evidence `final/c1/c1-tip-mutants.json`:

```
mutants: 28  killed: 26  pristine: passed
surviving: ['M17-ref-shadow', 'M20-log-sha-shape']
retired: ['M14-promisor-config', 'M22-promisor-pack', 'M27-promisor-boolean', 'M29-promisor-pack-pairing']
M17-ref-shadow: killed False, grid_exit 0, failed_rows []
M33-ref-shadow-bare-objects: killed True, grid_exit 1, failed_rows ['F13-ref-named-abbreviation']
final/c1/c1-tip-mutants.exit -> "exit=0"
```

Confirms row 2's "full run lists it (28 mutants, 26 killed, survivors M17 and M20)" and that
F13's kill now belongs to M33.

A4. Chronology (row 5/6), `git log --date=iso-strict --format='%h %cI %s'`:

```
5c95c8f 2026-10-22T06:42:57-03:00  (receipt re-run; 09:42:57Z)
46fb04b 2026-10-22T06:42:31-03:00  (amendment 4;  09:42:31Z)  -> committed BEFORE the re-run
c808ba0 2026-10-22T06:38:45-03:00  (amendment 3;  09:38:45Z)
5ea4fc4 2026-10-22T06:37:28-03:00  (first receipt; 09:37:28Z) -> amendment 3 AFTER it
5388b7c 2026-10-22T06:28:44-03:00  (amendment 2;  09:28:44Z)
1fc41e3 2026-10-22T06:28:54-03:00  (C1 re-anchor)
```

5ea4fc4 is on master's linear history (stays in history). Confirms row 5 both orderings and
row 6's two stamp-vs-commit pairs (09:30Z > 09:28:44Z; 09:40Z > 09:38:45Z).

A5. Fleet-root leftover check (row 4):

```
ls /home/vgpnk/Projects/shokunin/literal-id-checks.py
  -> No such file or directory
ls /home/vgpnk/Projects/shokunin/m17-reachability-probe.py
  -> No such file or directory
```

Matches ReviewerC1Patch's removal claim and ScoutMisroot D5 ("no fleet-root copy remains").
ScoutMisroot D2 additionally found two pre-existing fleet-root strays with intent-to-add
index entries (`write`, `scripts/hyaku/__pycache__/append-closure.cpython-314.pyc`) that any
L1 misroot sweep must also clear (index entries, not just files).

A6. Working copy vs pinned tip: `git show fa3b62ae:corpus/lessons/round-25.md | cmp - corpus/lessons/round-25.md`
    → "differ: char 5367, line 51" (uncommitted L1 edits in flight).

## B. Pointer resolutions (read, not re-run)

- `corpus/lessons/round-24-verifier-spotcheck.md:80-82` — "The registered M-series mutation
  source is stale at the measured auditor: M11 has zero matching anchor occurrences and M17
  has two; its own unique-match guard would abort." Resolves. `:151-152` — routed defect 2
  ("Correct stale PM08/registered mutation semantics only through separately authorized
  future work..."). Resolves.
- Row 1 fix cell "KQ36 below": KQ36 exists at `corpus/QUALITY.md:203` (round-25 criterion,
  registered counting commands re-run at the landed tip) but NOWHERE in round-25.md — the
  in-file pointer "below" does not resolve; the lesson never names QUALITY.md as its home.
- Row 1 captured-by "none": KQ28-KQ35 (QUALITY.md) verified to contain no re-run requirement.
  Caveat: KQ27's admit text ("independently enumerated after the artifact changes") arguably
  covers a stale registered count; ScribeMistake.md Finding 3 argues the narrow reading.
- Row 2: `a2-build/advice/RevengerM17Sites.md` (causal ed1cc3a run §N2), `CriticC1NoHarm.md`
  (Harm 1), `MutationM17M33Kill.md` — all exist and capture the finding. Instrument docstring
  `tests/report-audit/isolation-mutants.py:33-39` says M17 survives and why (verified).
  SKILL.md contains NO statement that M17 survives or why: :882-884 "M17 follows the current
  local-store spelling. Survival alone does not establish defensive-only status."; :889
  registry row "28 retained literals since round 25 (M11 and M17 re-anchored; M33 is the
  second call site of the M17 refusal)..." (grep `surviv` over SKILL.md: no M17-survival
  sentence).
- Row 3: `MutationC2Counter.md` documents kv_pool_suffix_collision (`= 12048` accepted for
  pool 2048), kv_pool_non_numeric_log (`nonsense2048`), wrong_server_build_prefix_collision
  (`build 117550`); `CriticC2SizingA2.md` documents A03 (X1 fit-probe pool line) and A09/A09b
  (unrecorded L1 overlap). All four lesson specifics resolve. Amendment 3 contains
  `check_after_change` (synthetic negatives, all reproduced in its text);
  `a2-build/out/CriticC2SizingA2/counter-attacks-proposed.out` exists.
- Row 4: `a2-build/advice/ReviewerC1Patch.md:94` (disclosure bullet), `out/ReviewerC1Patch/
  evidence.md:73` (two files named, `cmp`, three directories removed 06:45),
  `CriticC1Calibration.md:79` (`/tmp/ccal-aud-tip.py` scope deviation),
  `ScribeQualityCriterion.md:50-51` (`/tmp/mutants-red.json`, `/tmp/mutants-green.json`),
  `a2-falsify/advice/ScoutMisroot.md` (D4: three unattributed /tmp copies; D5: fleet root
  clean). All resolve. Wave-1 context (a2-build/dispatch.json contract) and falsify context
  (a2-falsify/dispatch.json contract) both verified verbatim.
- Row 5: amendment 3 `order_disclosure` present in its committed bytes; CriticC2SizingA2
  verdict "Register a stricter counter in an amendment 3 before any receipt is committed";
  receipt→amendment-3 delta 77 s ("a minute later"); ReviewerAmendment2 I2 corroborates.
- Row 6: amendment 4 `errata_to_amendment_2[0]` (amendment-2 stamp) and
  `errata-attempt-2.json` entry for `preregistration-amendment-3.json written_utc`;
  ReviewerAmendment2 M1 (amendment-3 stamp) and M2 (amendment-2 stamp); amendment 1
  corrections[0] "false timestamp" (the "same class" reference); amendment-4 `written_utc`
  names only `date -u` output and defers to the commit. All resolve.
- Row 7: `a2-falsify/advice/CriticC1AxisFit.md` §1-4 and `a2-build/advice/CriticC1Calibration.md`
  exist and argue the axis misfile. The prompt rule "A calibration claim must count mismatches
  between the lane's self-assessment (SCORECARD/SHONEN) and observed repo state" is at
  `/home/vgpnk/Projects/shokunin/.ufo/prompts/kama-round-25.md:347-348` (FLEET root). The
  lesson's pointer `.ufo/prompts/kama-round-25.md:347-348` does NOT resolve relative to the
  lane root (verified: lane path not found); it resolves only from the fleet root.

## C. Not run (cost or out of reach), with corroboration

- Full instrument run `isolation-mutants.py --json` (~16 min): not re-run. Corroborated by
  `final/c1/c1-tip-mutants.json` (committed, exit 0), ReviewerC1Patch's independent full run
  (exit 0, wall 983.9 s, same survivors), and ExecC1TipReplicate.md.
- Row 2 causal grid run on ed1cc3a: not re-run (~2 min). Corroborated by RevengerM17Sites §N2
  committed outputs (`ed1cc3a-tipM17-causal.json`), ReviewerC1Patch's r23 targeted run, and
  the code history (peel path moved lookup()→bare_objects() at 92063cf; blame/pickaxe in
  RevengerM17Sites §1/§3).
- Amendment-3 synthetic negatives under /fast/scratch/hyaku/kama25-a2/: not regenerated;
  amendment 3 records their outputs and I verified the counter's stricter behavior directly
  (A2) and via the committed counter-attacks outputs.

## D. Environment notes

- No tool installed or upgraded (git 2.56.0, Python as found). No pacman/uv/npm activity.
- No `lsp` device is mounted in this session's device set (sibling seats record
  `xd://lsp` → "No such tool. Mounted devices: ast_edit, debug"); the target is Markdown and
  JSON artifacts, so all semantic checks were done by direct execution of the registered
  commands and text-level pointer reads, never by grep-as-proof for a code claim.
- No llama-server child started; no port touched. Scratch:
  `/fast/scratch/hyaku/kama-r25a2w2/ReviewerLessonMistakes/` (clone at fa3b62ae after the
  revision loop; `receipt-5ea4fc4.json`).
