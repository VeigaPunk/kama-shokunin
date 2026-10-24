author: hyaku closure (non-author integrator, @m_opus)

# Round 27 — verifier spot-check (non-author closure, hyaku)

The hyaku orchestrator dispatched a fresh closure subagent
(`HyakuCloseKama27`) to write this file. The lane did not dispatch it. It did
not author the round and was not one of the round's seats in any attempt. The
runtime model reported to this session was `anthropic/claude-opus-5-5`;
`@m_opus` in the header is the closure-role label and does not prove which
provider answered. The closure dispatched five read-only seats with no model
parameter: KamaR27ClosePrompt (reviewer), KamaR27CloseRepairs (reviewer),
KamaR27CloseX1 (critic), KamaR27CloseC1 (reviewer) and KamaR27CloseHouse
(reviewer). All five returned; none died. They read committed bytes only and
executed no lane gate. Their reports are at `agent://HyakuCloseKama27.<name>`
(session-scoped). Every finding used below is restated here with its own
pointer, so this file does not depend on them.

## Decision

- Lane-round status: **ok** (a real report with checkable, landed work).
- Admitted: **false**. Verdict **rejected-honest-stop**. C1 (measured, depth)
  is a miss under its frozen kill rule, so not every claim verifies. No axis
  is harmed.
- X1 (exploratory, calibration): I am the named non-author reviewer. I rule it
  **`unprovable-but-better`**. The reasons are in §Claims.

## Dispatch and completion digest (`.ufo/watchdog.log`, copied)

```
2026-10-23T01:45:25-03:00 launch kama round=27 pgid=2451543 driver=hyaku-inline attempt=1
2026-10-23T02:26:39-03:00 lane-dead-no-report kama round=27; retry same round (hyaku-inline attempt=1: L1 died with the orchestrator process exit at 05:25:25Z (attempt 1; landed commits kept, uncommitted files untrusted))
2026-10-23T02:26:41-03:00 launch kama round=27 pgid=2558883 driver=hyaku-inline attempt=2
2026-10-23T03:40:29-03:00 lane-dead-no-report kama round=27; retry same round (hyaku-inline attempt=2: L1 died with the orchestrator process (omp SIGSEGV) at 06:19:06Z (attempt 2; landed commits kept, uncommitted files untrusted))
2026-10-23T03:40:30-03:00 launch kama round=27 pgid=3138238 driver=hyaku-inline attempt=3
2026-10-23T04:44:08-03:00 complete kama round=27; hyaku-inline attempt=3
```

## Step-1 conformance

| Check | Command | Observed | Result |
|---|---|---|---|
| report committed by the lane identity | `git log --format='%an <%ae> %H' -- .ufo/reports/round-27/kama.md` (fleet) | `kama-shokunin <kama@shokunin.local> 1b723c9a96ec5778b737e303b4ba90c3e48ed723` | holds |
| `SHONEN` heading, one line per box | report lines 147-152 | 4 lines, all `[~]`, matching the 4 boxes of `SHONEN.md` at `8057282c` | holds |
| cited lane commits exist and are ancestors of `master` | every 8-40-hex token in the report: `git rev-parse --verify <h>^{commit}` + `git merge-base --is-ancestor <h> master` | 324d5d62, d183ec57, 52632caa, 4d2e74f4, 8057282c, 530eaa99, 6020243e, a712902c, 1471f676, 0ec32cac, a720399e: all `anc`. The tokens 49491b80, 61a5378f, b4f4aae7 (sha256 prefixes) and 704366d76 (upstream llama.cpp) are not lane commits and are not cited as such | holds |
| lane pushed, no leftovers | `scripts/hyaku/jj-lane.sh state …/kama-shokunin`; `git status --porcelain \| wc -l` | `state branch=master local=8057282c… remote=8057282c… ahead=0 behind=0 head=detached tracked=0 untracked=0`; `0` | holds |
| prompt carries the template contract | KamaR27ClosePrompt: `templates/round-prompt.md` rendered with lane=kama, round=27, then `diff` against prompt lines 1-140 | byte-identical; the hyaku addendum is `## 6` at `.ufo/prompts/kama-round-27.md:141`; all five round-level and five child-lane embed items are present | holds |
| prompt committed before the report | `git log -- .ufo/prompts/kama-round-27.md` | `d234c359` (attempt 3, 03:40:27-03:00), before report `1b723c9a` (04:40:58-03:00). Committed by `kama-shokunin`, as are all nine sibling round-27 prompts | holds |

Conformance defect (status-neutral): the round-27 counter
`.ufo/waves/round-27/count-c1.py` has no gate registry row in `SKILL.md`, the
lane's registry home (PROTOCOL §Gate standard, Registry). `grep count-c1
SKILL.md` at `8057282c` finds only the round-26 row (line 1073), and `grep -E
'round-27|Round 27' SKILL.md` exits 1. Closure therefore grades this gate not
conformant. C1 was withdrawn and never met its target, which limits the
impact.

## Claims

### C1 — depth, `counted >= 15` (measured claim): **miss, verified**

Evidence verified, not re-run. The counter is a lane-owned gate, so per
PROTOCOL §Gate standard I did not execute it.

- Frozen kill rule (`preregistration.json` `claims.C1.kill_rule`): "counted <
  15 at the landed tip is a miss: reported as a miss, never amended, never
  re-scaled".
- Freeze: `git diff --stat 0ec32cac 8057282c -- .ufo/waves/round-27/count-c1.py
  .ufo/waves/round-27/preregistration.json` is empty.
  `git show 8057282c:.ufo/waves/round-27/count-c1.py | sha256sum` →
  `49491b80e4f4ed2a85ab822a52f0b1a0fdb1dee53423e3d43b60ee25d1bf2765`, equal to
  the preregistration and every receipt.
- Receipts: `before/c1-base.out` (a720399e), `a3/c1-tip.out` (clone at
  d183ec57) and `a3/c1-final.out` (clone at 4d2e74f4) each print `registered 0
  counted 0 target 15 met False`, `exit=0`.
- Plain re-measurement (mine): the counter's data surface is
  `registry/error-signatures-r27.json` (`count-c1.py:125`) and the SKILL
  section `## Round-27 request-validation signatures`. `git cat-file -e
  <rev>:registry/error-signatures-r27.json` reports absent at a720399e,
  4d2e74f4 and 8057282c, and `grep -c '^## Round-27 request-validation
  signatures' SKILL.md` gives 0 at all three. So counted is 0 < 15 at the tip,
  which agrees with the reported miss.
- No data dispatch: `w1-controls/dispatch.json` (37 seats, context "No data
  seat runs in this wave"), `w1a3/dispatch.json` (34 seats: X1 and repairs)
  and `residual/dispatched-payload.json` (7 seats) hold no data seat
  (KamaR27CloseC1).
- The SCORECARD row cites `a3/c1-tip.out` (measured at d183ec57) and the
  report cites `a3/c1-final.out` (measured at 4d2e74f4). Both resolve. The
  counter's read set is unchanged from d183ec57 to 8057282c, so both measure
  the landed tip.

### X1 — calibration, exploratory: **`unprovable-but-better`** (ruled by this closure)

Surface: `corpus/knowledge/echo-discriminating-counters.md`, `corpus/QUALITY.md`
KQ37 and the two appended round-27 qualifications.

Prior state, verified:

- At `a720399e`, QUALITY.md held no echo criterion.
- The round-26 counter compared the signature with stored request bytes
  (`git show eb09e742:.ufo/waves/round-26/count-c1.py`, line 384), and a
  base-tree shortcut met it 12/12 (`round-26-verifier-spotcheck.md:98-116`).
- Replayed offline, the round-26 test flags 0/12 of those rows as echoes
  (`w1a3/out/ExecOfflineEchoReplay/replay.receipt.json`, read by
  KamaR27CloseX1).

What I re-checked myself:

- Sources: `curl -sS https://www.rfc-editor.org/rfc/rfc8259.txt | sha256sum` →
  `61a5378f…cd2d7` (equal to S136 and S139). Line 433 reads "Any character may
  be escaped." Lines 455-457 read "…the character is represented as a
  12-character sequence, encoding the UTF-16 surrogate pair."
- `curl -sS https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp`
  → sha256 `b4f4aae7…d442` (equal to S137). Line 1375 is `throw
  std::invalid_argument("response_format type must be one of \"text\" or
  \"json_object\", but got: " + response_type);`. The entry's facts 1 and 2
  hold.

Receipts verified as committed bytes (KamaR27CloseX1):

- The live probe gives 400 on the error requests and 200 on the control; the
  req1/req2/req3 response blobs hash identically (`9ea801fb…b9a45a06`).
- Decoded-body echo test: 12/12. Raw test: 0/12. Shape check: 12/12.
- Raw-body mutant: 0/12, killed.
- Frame mutant: 1/12 → 12/12, killed.
- Frame replay: shortcut 1/12, E26 17/17 with 0 collisions.
- Boundary leg refuses 3/17 genuine E26 rows
  (`residual/out/CriticBoundaryLegProbe/boundary-leg.receipt.json`).

Reasons for `unprovable-but-better`:

1. The change answers a demonstrated failure of the lane's own measurement
   method with a rule grounded in two primary sources, both re-opened and
   hash-equal. The prior state had no criterion, and the old test passes the
   shortcut 0/12 where the decoded test flags 12/12.
2. Mutation seats killed each new leg (decoded echo, frame), so each one
   changes outcomes.
3. The entry states its limits plainly:
   - it is a necessary, not sufficient, condition;
   - it was not run on data;
   - `lower()` is ASCII-only;
   - the frame is positional;
   - the boundary leg costs 3/17 genuine rows.

   The round's own wave caught four of its first-landed errors and corrected
   them before filing.
4. The closure critic advised "not-better" because of the boundary leg's
   coverage cost. In particular, E26-14 is refused although its message equals
   the server literal: the request key `prompt` coincides. I weigh that as a
   precision-for-recall trade that the text discloses as a cost
   (QUALITY qualification 6; entry lines 127-132). For a calibration move,
   refusing some genuine rows is safer than crediting echoes. The frame and
   echo legs alone collapse none of the 17 genuine rows. The cost is routed as
   a design question below, not ruled harm.

It stays unprovable rather than measured because no counter built to KQ37 has
run on real rows. Residual text defects are routed below (items 4-6).

### Repairs (round-26 routed defects; not claims)

| Defect | Verdict | Evidence |
|---|---|---|
| 1 LOG in-place rewrite | repaired | `git diff a720399e 8057282c -- LOG.md`: +62/−0. The first correction (324d5d62) matches `git log 7f84cd0e..fd48f9a3 -- LOG.md` (`f4066979`, `fd48f9a3`). The second (d183ec57) fixes its "three → four sentences" error and the omitted `f4066979` |
| 2 counter F1/F2/F3 + per-class receipts | partial | `count-c1.py:347-371` compares decoded strings (F2), and help/version/healthy-log exclusion is at line 656 (F1). There is **no F3 file-content echo leg**. The per-class pre-data receipt leg is vacuous: no data seat ran, and `w1-controls/` has no committed receipts |
| 3 shortcut pins | repaired | `repairs/d3-r26-shortcut-pins/` sha256 equal `README.json` |
| 4 dead-seat provider bytes | repaired | I re-hashed each transcript named in `repairs/d4-r26-dead-seat-errors/README.json` (sha256 equal) and ran `cmp <(grep '"errorMessage"' <transcript>) <seat>.error-lines.jsonl`: byte-identical for all 3 |
| 5 receipt key mislabel | repaired (note) | `git cat-file -t 7e5ff9b5` → `commit`; round-26 files untouched (`git diff a720399e 8057282c -- .ufo/waves/round-26/` empty) |
| 6 Gate reject reasons | repaired (note) | `git grep -l 'does not support metrics' a720399e -- .ufo/waves` matches the lesson's three + three files; `CriticAxisFit.md:105` reads "a measured caveat, not a kill" |
| 7 S133 anchor | repaired | S138 appended with 1810-1835; S133 unedited (SOURCES diff: additions only) |
| 8 `count-c2.py` cell trust | open | `.ufo/waves/round-25/count-c2.py:170-183` still reads `d.get("cells")` and per-cell `c.get(...)` from the receipt |

## Per-axis verdicts

| Axis | Verdict | Basis |
|---|---|---|
| depth | unchanged | C1 miss. `SKILL.md` unchanged (`git diff --stat a720399e 8057282c -- SKILL.md` empty). SCORECARD 7 → 7 |
| calibration | unprovable-but-better | X1, ruled above |
| coverage | unchanged | no new coverage ground. The README adds a frontier-disposition table only |
| operability | unchanged | no runnable artifact claimed |
| freshness | unchanged | no re-verification claimed. S138 is an anchor correction |
| adjacency | unchanged | the sibling scout (ScoutSiblingEchoRules) is disclosure only |

`git diff a720399e 8057282c -- SCORECARD.md` is a pure +39/−0 append. Other
scores are held at operability 8, freshness 8, coverage 9 and adjacency 7, and
nothing is lowered. Append-only files (`LOG.md`, `SOURCES.md`, `QUALITY.md`,
`README.md`, `SCORECARD.md`) have 0 deleted lines across the round
(`git diff … | grep -c '^-[^-]'` → 0).

## Spot-check (LEARNING.md §Discernment is checked from outside)

| Item | Decision | Re-opened source | Agree/disagree | Reason |
|---|---|---|---|---|
| CriticEntryFactsSources: six-character escape is wrong outside the BMP; S139 supersedes S136 | admit | `rfc8259.txt` fetched now, sha256 `61a5378f…cd2d7`, lines 433 and 455-457 | agree | Line 433 says any character may be escaped. Lines 455-457 require a 12-character surrogate pair outside the BMP, so S136's "six-character for any character" is false and the superseding row is right |
| CriticBoundaryLegProbe: the boundary leg refuses 3/17 genuine rows (admit as a disclosed cost) | admit | `residual/out/CriticBoundaryLegProbe/boundary-leg.receipt.json` (committed) | agree, scope note | The receipt shows 12/12 shortcuts and variants refused and 3/17 genuine refused. Lines 10-14 show the probe used exact, case-sensitive decoded strings of length ≥ 4. Neither the entry nor qualification 6 says so (routed item 5) |
| SentinelCommittedBytesSecrets: redact `credentialId`, message ids, paths, quota values from the d4 bytes | reject | the 3 `repairs/d4-r26-dead-seat-errors/*.jsonl` files, re-hashed against the transcripts | agree | `grep -oiE 'https?://…\|credential…\|token…\|key…'` finds only `credentialId":18` and `totalTokens":0`. There is no URL, key or token value. Redaction would break the byte identity I re-verified with `cmp` |
| CriticEntryRuleVsCode: switch the frozen counter to `casefold()` | reject (this round) | `git show 8057282c:.ufo/waves/round-27/count-c1.py`, lines 343-348 (`.lower()`), sha256 `49491b80…2765` | agree | The counter is frozen (byte-identical since 0ec32cac) and never ran on data. Editing it would void the preregistration. The gap is disclosed in QUALITY qualifications 3 and 5 and in the entry at lines 133-141 |

Newly written SOURCES rows re-opened:

- **S137**: the quote at `server-common.cpp:1375` is verbatim at the pinned
  commit (15 whitespace-delimited words, ≤ 25), and the raw fetch sha256
  equals the row.
- **S139**: the lesson Gate quote "the character is represented as a
  12-character sequence, encoding the UTF-16 surrogate pair." is verbatim at
  `rfc8259.txt` lines 456-457 (13 words), and the sha256 equals the row.

Census at closure:
`/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama`
→ exit 0, `kama ok …/kama-shokunin/corpus/SOURCES.md`, 50 W04 duplicate-URL
advisories. This is the same result as the lane's `a3/census-final.out`.

## Trend verdicts

- **expansion: unchanged.** The new knowledge entry is method knowledge about
  the lane's own counters. It adds no coverage-map ground or capability. The
  four SOURCES rows serve that entry and an anchor correction.
- **quality: unchanged.** No knowledge entry was re-verified or superseded.
  S138 (anchor) and S139 (escape length) correct SOURCES rows. Of those, S139
  corrects a row landed in this same round, so there is no net gain over base.
- **discernment: improved.** This spot-check agrees with both sampled admits
  and both sampled rejects, and their reasons hold when re-opened (LEARNING.md
  table: "the spot-check agrees with the gate on admits *and* rejects"). The
  round-26 discernment defect, a raw-byte echo test met by a shortcut, became
  a lesson-backed criterion (KQ37 cites `round-26-verifier-spotcheck.md`
  defect 2 and `lessons/round-27.md`). This differs from round 26, where three
  reject reasons were partly wrong. Residual text defects in KQ37 are routed
  below. They are not gate disagreements.

## Housekeeping (confirmed)

- **Attempt-2 files.** `/usr/bin/find
  /fast/scratch/hyaku/kama-r27/attempt2-untracked-w1-scratch -type f | wc -l`
  → `1846` (26M). No committed byte cites their content as evidence. The
  `git grep` hits at `8057282c` are the disposal disclosure (LOG,
  lesson header), the verification report `w1a3/advice/ReviewUntrackedDisposal.md`,
  and destination strings in the dead wave's dispatch files. "Unread" is an
  attestation that cannot be checked.
- **262 GB `sitecustomize.py`.** At
  `/fast/scratch/hyaku/kama-r27b/ReviewA3Diff/sitecust/`, only
  `REMOVED-RUNAWAY.txt` (376 B) and `sitecustomize.py.head4k` (4096 B) remain.
  The committed copies are under `a3/mistake-runaway/` (head4k is exactly 4096
  bytes). The lesson's §Mistakes row, CriticMistakeRow and
  ExecFixtureBoundDemo cite them only as an incident record. No claim rests on
  the runaway file.
- **Orphan llama-server processes.** `ss -ltnp` shows no listener on
  47636/47637/47644, and `pgrep -af llama-server` returns none.
- **Early gate-slot release.** Disclosed at report line 135. Corroborated by
  `residual/spawn-result.txt`: refusals at 07:22:03Z, 07:22:07Z and 07:22:23Z
  with "Background job limit reached (100)", then success on the 4th send at
  07:23:39Z. The report's "about 07:27Z" is about 3.5 min late. No seat was
  lost.

## SHONEN (for the operator; promotion is operator-owned)

All four boxes are `[~]` in the report and in `SHONEN.md` at `8057282c`.
Nothing this round makes a box newly checkable: `SKILL.md` and `PROVINCE.md`
are unchanged. This closure wrote no `[x]`.

## Routed defects (lane fixes next round)

1. `count-c2.py` (`.ufo/waves/round-25/count-c2.py:170-183`) still reads cell
   values from the receipt. Open since round 25 (defect 5) and round 26
   (defect 8).
2. Round-26 defect 2 remainder: the counter has no F3 file-content echo leg.
   Commit one non-author shortcut-control receipt per named class before any
   data seat.
3. Register the round-27 counter `.ufo/waves/round-27/count-c1.py` in
   `SKILL.md` (gate or probe row: entry command, verdict map, self-test,
   pinned values), or record it retired with C1. Without a row, closure grades
   it not conformant.
4. Append a KQ37 qualification. It should do two things:
   - Replace the row's S136-based wording ("any character be a `\uXXXX`
     escape", `QUALITY.md:219`) with S139's.
   - Correct qualification 1 ("clause (d) covers the first part",
     `QUALITY.md:234`). Clause (d) also accepts the joined-literals candidate
     (`count-c1.py:338-340`), as the entry already states at lines 121-126.
5. State the boundary-probe scope wherever its 3/17 cost is cited (entry lines
   127-132, QUALITY qualification 6): exact, case-sensitive decoded strings of
   length ≥ 4 (`boundary-leg.receipt.json:10-14`). Treat the E26-14
   lexical-coincidence refusal as the round-28 boundary-design question.
6. The `recheck:` line of `knowledge/echo-discriminating-counters.md` gives a
   cadence, not a runnable procedure. Name the server start, the probe command
   and a fresh output path; `ExecLiveEchoProbe/probe.py` writes over its
   committed receipts.
7. Report imprecisions, to be corrected in the next report: the residual
   spawn time (07:23:39Z per `residual/spawn-result.txt`, not about 07:27Z),
   and "`8057282c` adds only receipt files" (it also adds `census-final.out`
   and `sources-append-only-final.out`).
