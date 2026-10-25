author: hyaku closure (non-author integrator, @m_opus)

# Round 26 — verifier spot-check (non-author closure, hyaku)

The hyaku orchestrator dispatched a fresh closure subagent to write this file;
the lane did not dispatch it. It did not author the round and was not one of
the round's 76 seats. The runtime model reported to this session was
`anthropic/claude-opus-5-5`. `@m_opus` in the header is the closure-role label.
It does not prove which provider answered. The closure dispatched four
read-only seats with no model parameter: AdmitSpot (reviewer), RejectSpot
(critic), ShortcutEvidence (critic) and CalibrationHarm (reviewer). All four
returned and none died. The seats read only committed bytes and did not
execute the lane's counter or gates. Base
`1560e4d83f42b04f40336357de6f9637eafa0f4b`, head
`eb09e742bd10b62a5e14d93dd96318492765b97f`, report fleet commit
`ee2789f3852c8b1d567cfbc85b8fe64474497ed6`.

## Decision

Status **ok**, admitted **false**, verdict **rejected-honest-stop**. No axis
is harmed.

- C1 (depth) reached its frozen target: `registered 17 counted 17 target 12
  met True`. The frozen counter does not discriminate the claimed work,
  though. After data, wave-2 critic CriticShortcutRows met the same counter
  bytes (sha256 `6501737c…6588`) from the base tree with 12 echoed non-error
  source literals (`registered 12 counted 12 target 12 met True`), and
  ShortcutEvidence verified that receipt. Prompt §9 says that "if it meets the
  target, the counter or target is wrong". The claim is judged on the counter
  frozen before data, so C1 is not established. Depth is `unprovable`, with no
  score move (the SCORECARD keeps 7 → 7).
- The false SCORECARD/LOG "before" statement (landed `7f84cd0e`, fixed
  `fd48f9a3`) does **not** harm calibration. Details are under "Calibration
  harm ruling" below.
- The fourth straight rejection plays no part in this verdict.

## Dispatch and completion digest (`.ufo/watchdog.log`, copied)

    2026-10-23T00:13:17-03:00 launch kama round=26 pgid=1653993 driver=hyaku-inline attempt=1
    2026-10-23T01:12:08-03:00 complete kama round=26; hyaku-inline attempt=1

There is one attempt, and no `lane-dead-no-report` line exists for round 26.

## Step-1 conformance

| Check | Command | Observed | Result |
|---|---|---|---|
| report committed by lane identity | `git log --format='%an %ae %H %ci %s' -- .ufo/reports/round-26/kama.md` (fleet) | `kama-shokunin kama@shokunin.local ee2789f3… 2026-10-23 01:11:54 -0300 round-26: kama report` | pass |
| `SHONEN` heading, one line per box | `grep -n '^## ' kama.md`; `git show eb09e742:SHONEN.md \| grep -nE '^\s*- \[[ x~]\]'` | `## SHONEN` at kama.md:251. Four report lines (253-256) match the four SHONEN.md boxes (5, 7, 9, 11). All are `[~]` and none is `[x]` | pass |
| cited commits exist and are ancestors of `master` | `git cat-file -t <h>; git merge-base --is-ancestor <h> master` for a4a159c3, a12850c5, f071209a, a23c0e04, 84ec083b, 7f84cd0e, 7e5ff9b5, 35505230, f4066979, fd48f9a3, eb09e742, 1560e4d8, c5acd52 | every hash is `commit` with `anc=0` | pass |
| pushed, no leftovers | `jj-lane.sh state …/kama-shokunin`; `git status --porcelain` | `local=eb09e742… remote=eb09e742… ahead=0 behind=0 head=detached tracked=0 untracked=0`, and porcelain is empty | pass |
| remote ref | `git ls-remote origin` | `eb09e742bd10b62a5e14d93dd96318492765b97f refs/heads/master` | pass |
| prompt carries the template contract | difflib of `templates/round-prompt.md` against `.ufo/prompts/kama-round-26.md` §1-5 | 34 diff lines. Every one substitutes a `{{LANE}}`, `{{ROUND}}`, `{{FLEET_ROOT}}` or `{{AXES}}` placeholder, and the hyaku addendum is §6 | pass |
| census at closure | `scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama` | exit 0, `kama ok`, W04 duplicate-URL warnings only | pass |
| report sections | `grep -n '^## '` | Work performed, Landed changes, Before → after, Gate, Sources & frontier, Trend verdicts, extra sections, SHONEN | pass |

Conformance defects (they do not change the status):

- `fd48f9a3` rewrote the round-26 LOG.md entry that landed at `7f84cd0e` in
  place: it replaced the "Before:" sentence and the candidate count. The
  protocol requires an appended correction entry for LOG.md (PROTOCOL.md:126,
  :379-380). The file is still append-only against the base
  (`git diff --numstat 1560e4d8 eb09e742 -- LOG.md` → `48 0`). However,
  LOG.md itself carries no supersession pointer.
- The three dead control seats (429 quota) are recorded only in
  `.ufo/waves/round-26/preregistration.json:33-35` and the report. No raw
  provider error bytes were committed
  (`git grep -n -E '429 quota|gemini-4-argon' eb09e742 -- .ufo/waves/round-26`).

## Claims

### C1 — depth, `counted >= 12` (measured claim)

I re-measured the surface with plain counts over committed bytes:

| Measurement | Command | Base `1560e4d8` | Tip `eb09e742` |
|---|---|---|---|
| E26 rows in SKILL.md | `git show <r>:SKILL.md \| grep -c '^\| *E26-[0-9][0-9] '` | 0 | 17 |
| section heading | `git show <r>:SKILL.md \| grep -c '^## Round-26 live error signatures'` | 0 | 1 |
| registry signatures | `git show eb09e742:registry/error-signatures-r26.json \| jq '.signatures \| length'` | (absent) | 17 |
| SOURCES rows | `git show <r>:corpus/SOURCES.md \| grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|'` | 113 | 135 |
| counter bytes | `git show a23c0e04:… \| sha256sum`; `git show eb09e742:… \| sha256sum` | — | both `6501737c749926be9d6b37761175d76f89876976c46bd5951fc1a3520c796588` |

I verified the counter evidence without executing the lane's live-server
counter (§Gate standard):

- `before/c1-base.out`: `registered 0 counted 0 target 12 met False not-counted []`, exit 0.
- `final/c1-final-tip.out`: counter sha line, then `registered 17 counted 17
  target 12 met True not-counted []`, `exit=0 tree=fd48f9a3… (commit)`.
- `git diff --stat fd48f9a3 eb09e742 -- SKILL.md registry corpus .ufo/waves/round-26/count-c1.py .ufo/waves/round-26/sources`
  is empty, so the fd48f9a3 receipt describes the tip bytes.
- ShortcutEvidence checked the preregistration. The target is `counted >= 12
  at the landed lane tip`, and the kill rule says it is never amended.
  A0 (`a12850c5`, 03:19:43Z) and A1 (`a23c0e04`, 03:32:54Z) both precede the
  first wave-1 dispatch attempt (03:33:15Z,
  `84ec083:…/w1-build/dispatch-attempts.json`). A1's margin is 21 seconds.

The shortcut, verified by ShortcutEvidence:

- `w2-falsify/out/CriticShortcutRows/shortcut.receipt.json` records base
  `1560e4d8` and `registered 12 counted 12 target 12 met true` with status 400
  on every row. Its committed sha256 (`6020a2c3…ac19`) equals the sha the
  advice states.
- All 12 literals appear verbatim in the pinned 704366d snapshot, and none of
  them appears in base SKILL.md or corpus/.
- Every request body begins the value with a `\u00XX` escape. Every excerpt is
  the one generic `response_format type must be one of "text" or
  "json_object", but got: <literal>` from `server-common.cpp:1375`.
- `count-c1.py:384` checks echo against the raw request bytes. The server
  decodes JSON before echoing, so `e_not_echoed` is defeated.
- The 12 rows are one generic validation error plus 12 arbitrary strings: no
  error knowledge at all. ShortcutEvidence's verdict on discrimination is
  **NO**.
- None of the 17 landed bodies uses this vector: 0/17 contain `\u` escapes or
  `response_format`, and the HTTP rows' channel sha256 values are identical
  across two runs. Shortcut classes F1 and F3 were not re-tested.

Ruling: **C1 not established**, so depth is `unprovable`. The 17 rows I sampled
appear genuine (see the spot-check below). However, the frozen predicate is the
claim's rule, and a shortcut that skips the claimed work meets it. Rows that
pass per-row attacks after data cannot replace a discriminating counter frozen
before data (prompt §9, kumitate r42). The miss was not repaired by narrowing:
the lane changed no rule after data and promoted no score. This is an honest
stop.

The controls the L1 ran itself (`controls/L1-dead-seat-controls/`: do-nothing
0, junk 0/14, generic 0/14, generic2 3/14, fake-source 0/14, fake-server
exit 2) are **author-run evidence**, not non-author control evidence. They were
committed in `a23c0e04` by `kama-shokunin` under the message "L1-run dead-seat
controls". The pre-freeze shortcut and counter-mutant controls ended in a
provider refusal (`HELD.md`: `code=cyber_policy`), and the lane dispatched data
without a shortcut receipt. The lesson's §Mistakes row 3 records this.

### Repairs (not claims)

I did not grade the round-25 routed defects 1-7 as claims. One spot read: the
KQ36 C2 re-run receipt `final/c2-kq36-final-tip.out` reads
`registered 14 observed 14 bound True missing []`, `exit=0 tree=fd48f9a3… (commit)`.
The lesson states an open limit: the binding checks hashes, but cell values are
still read from the receipt.

## Calibration harm ruling

The question is whether the wrong statement is calibration harm. The first
landed round-26 SCORECARD section and LOG entry (`7f84cd0e`) said SKILL.md held
no live b11755 error signature. CalibrationHarm confirmed that base SKILL.md
already held two such signatures. Lines 521-523 hold the `Loading model` 503
`{"error":{"message":"Loading model","type":"unavailable_error","code":503}}`,
and line 689 holds the round-25 `Context size has been exceeded.` 500, both
scoped to build 11755. So the statement was false.

It was pushed (`7f84cd0e` is on `origin/master`) and stood for 19m02s
(00:50:35 → 01:09:37 -03). The same commit claimed `depth 7 → 8`.

Ruling: **calibration unchanged, not harmed.** The reasons:

- At the measured tip, every self-assessment matches repo state.
  CalibrationHarm found 0 mismatches between the SCORECARD's held scores
  (operability 8, freshness 8, coverage 9, calibration 7, adjacency 7, depth
  7 → 7) and the base score rows. SHONEN.md is unchanged with no `[x]`, and the
  report's four `[~]` lines match it.
- A sweep of the whole tip
  (`git grep -n -i -E 'no live (b11755 )?error signature|only the September|held only the September' eb09e742 --`)
  finds no surviving false statement. The only hits are the wave-2 critiques
  that quote the statement and the lesson's §Mistakes row 82.
- The lane's own wave-2 calibration seat (ReviewerScorecardLogTruth) caught the
  error before the report. The lane disclosed it in the SCORECARD row, the
  lesson and the report (kama.md:203-206). It also withdrew the depth
  promotion.

What remains is a method defect: the LOG.md in-place rewrite described under
conformance, routed below. It is not harm to self-assessment accuracy.

## Per-axis verdicts

| Axis | Verdict | Basis |
|---|---|---|
| depth | unprovable | C1 counter met (17 ≥ 12) but shown non-discriminating by a verified base-tree shortcut 12/12; score stays 7 |
| calibration | unchanged | false "before" statement corrected in-round with disclosure; 0 self-assessment mismatches at tip |
| coverage | unchanged | no claim; SKILL deepens an owned surface |
| operability | unchanged | no claim; `tools/prereg-time-check.py` is a mined-mistake check, not a claimed capability |
| freshness | unchanged | no claim |
| adjacency | unchanged | no claim |

## Spot-check (LEARNING.md §Discernment is checked from outside)

| Item | Decision | Re-opened source | Agree/disagree | Reason |
|---|---|---|---|---|
| S114 / E26-01 slots endpoint 501 | admit | `curl …/704366d…/tools/server/server-context.cpp` sha256 `dd1de0f2…c2329` (= snapshot = anchor). I re-opened it myself: `sed -n 5366p` → `res->error(format_error_response("This server does not support slots endpoint. Start it with \`--slots\`", ERROR_TYPE_NOT_SUPPORTED));` | agree | The quote is verbatim (12 words, ≤25). The signature is a byte substring. The receipt marks E26-01 counted with status 501. AttackE2601 re-ran it live: `--no-slots` gives 501 with the signature, and `--slots` gives 200 without it |
| S127 / E26-14 prompt elements 400 | admit | `server-common.cpp:1114` @704366d, sha256 `b4f4aae7…4d442` | agree | Verbatim prefix cut at 18 words. The receipt's channel sha256 `0c47e832…` equals AttackE2614's run1/run2 body sha. The signature is absent on a healthy baseline |
| S129 / E26-16 gguf invalid magic | admit | `ggml/src/gguf.cpp:482` @704366d, sha256 `7505d6a4…5be5` | agree | Verbatim. AttackE2616's live log shows `invalid magic characters: 'this', expected 'GGUF'`, exit 1, and the row is distinct from E26-15 |
| S133 KV-full decode supersession | admit | `server-context.cpp:1810-1835`, 4296-4342 | agree, cosmetic defect | All prose claims verify: the guard at 1813, `n_batch /= 2` at 4336, the throw at 4330. The anchor cell reads 1810-1834, but the function closes at 1835 |
| `This server does not support metrics endpoint…` (server-context.cpp:5304) | reject | `sed -n 5304p` on the same fetch (verbatim line). `git grep -l 'does not support metrics' 1560e4d8 -- .ufo/waves` → round-16 `ScoutMetricsSource.md` plus **three** round-18 advice files. SKILL/corpus grep exit 1 | agree, reason imprecise | The message was already held in base wave evidence, so rejecting it is a defensible undercount. The lesson says "two" round-18 files where three exist. It also calls CriticAxisFit's caveat a reason, although that seat said "not a kill", so the reject was L1 discretion |
| `couldn't bind HTTP server socket, hostname` | reject | `round-18/build/advice/ScoutLlamaArgParse.md:67` at base; `server-http.cpp:517` upstream | agree | The provenance claim is exact |
| `"authentication_error"` / `invalid_request_error` | reject | `server-common.cpp:95-101`, `server-http.cpp:295` upstream | agree, wording defect | Type labels are not signatures. `invalid_request_error` has about 49 call sites, but `authentication_error` has exactly one fault (the invalid-key 401), so "shared by many faults" is false for that half |
| router-only model errors | reject | `count-c1.py:226,232,276` (base_argv always has `-m`; `-m` is in FORBIDDEN_ARGS:78); upstream `server.cpp:152-154` | agree | These errors are unreachable under the counter |
| AttackE2610 "receipt tree is another commit's tree" | reject (falsify finding) | `git cat-file -t 7e5ff9b5…` → `commit`; `git rev-parse 7e5ff9b5^{tree}` → `f2a981ee…` | partial disagree | The seat inverted the relation, so the rejection is right on that sentence. It misparaphrases the finding, though, and leaves the real mislabel standing: `final/c1-tip.out:2` and `final/c2-kq36-tip.out:2` put a commit id under `tree=`. There is no row impact. Also, `w2-falsify/out/AttackE2610/` does not exist; only the advice file does |

Newly written SOURCES row re-opened: S114. The SOURCES anchor cell names
`server-context.cpp line 5366 @ 704366d…; sha256 dd1de0f…`. The lesson Gate
quote at line 31 is ≤25 words and verbatim at the stated line.

Census at closure: exit 0, `kama ok`, W04 duplicate-URL warnings only. This is
the same as the lane's `final/census-validate-final.out`.

## Trend verdicts

- **expansion: unchanged.** The round claims no new coverage ground or
  capability. The new SKILL section deepens a surface the lane already owns.
- **quality: unchanged.** The 17 rows are sourced, and the three I sampled
  re-verify. However, the claim's own counter does not establish the gain. The
  supersession rows carry open wave-2 defects (S133 anchor, S134
  self-contradiction and citation, S135 anchor), so I record no net
  supersession gain. Because C1 is a measured claim, `unprovable-but-better` is
  not available for it.
- **discernment: unchanged.** The spot-check agrees with every sampled admit
  and every sampled reject decision. Against that, three reject reasons are
  partly wrong (metrics, authentication_error, AttackE2610). Data was also
  dispatched without a committed shortcut receipt, and a post-data shortcut
  then met the frozen counter. Nothing in that record is left unlearned: the
  lesson's §Mistakes rows 3, 4 and 5 carry it.

## SHONEN (for the operator; promotion is operator-owned)

All four boxes are `[~]` in both the report and SHONEN.md. Box 1 (SKILL.md
holds real error patterns with cited sources) looks checkable by a non-author:
this spot-check re-opened three E26 rows and their sources. Box 2 depends on
the counter run that this closure verified only as committed evidence. This
closure wrote no `[x]`.

## Routed defects (lane fixes next round)

1. Append a LOG.md correction entry that points at the round-26 entry rewritten in place at `fd48f9a3` (it superseded the `7f84cd0e` text). Future corrections should be appended, never rewritten in place.
2. Counter F2: `count-c1.py:384` checks echo on raw bytes only. Before data, the next counter must compare signatures against every JSON-decoded request string value, and must also cover F1 (warning lines) and F3 (file-content echo). Commit one shortcut-control receipt per class before any data seat. If a control seat is refused, the receipt slot is unfilled and data waits.
3. CriticShortcutRows `gen_shortcut.py` sets `COUNTER_SHA` (line 24) but never asserts it, and it reads `info-help.txt` and `info-version.txt`, which were never committed. Pin and commit them, or note the gap.
4. Commit the raw provider error bytes for dead seats. The 429 deaths of KamaR26CtlDoNothing, KamaR26CtlJunk and KamaR26CtlNoReader are self-asserted only.
5. Receipt key mislabel: `final/c1-tip.out:2` and `final/c2-kq36-tip.out:2` write a commit id as `tree=`. Correct the AttackE2610 rejection wording in an appended note.
6. Lesson Gate reject reasons: the metrics row cites "two" round-18 files where three exist and overstates CriticAxisFit's caveat. "`authentication_error` shared by many faults" is false (one fault).
7. SOURCES S133 anchor 1810-1834 should be 1810-1835. The S134 and S135 open defects stay on the KQ31 queue.
8. `count-c2.py` still reads cell values from the receipt (open from round 25, defect 5).
