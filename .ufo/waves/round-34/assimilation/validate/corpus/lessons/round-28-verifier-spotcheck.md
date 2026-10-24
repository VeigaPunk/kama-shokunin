author: hyaku closure (non-author integrator, @m_opus)

# Round 28 — verifier spot-check (non-author closure, hyaku)

Lane `kama`, lane-round 28 (L1 `KamaR28`). Base `4179301f7516ad667509d54b5ebfe0a70a002d5b`,
lane tip `bdb2a5b4e41010659661342b42c79c34cbf9e43c`, report
`.ufo/reports/round-28/kama.md` (fleet commit `b459870bc9b6d6bb3766e55b1e90baa5c963ecd0`).
This closure did not author the round and changed nothing in it. It ran 5 read-only reviewer
seats (KamaCloseA1Timing, KamaCloseRepairs, KamaCloseSources, KamaCloseNoHarm,
KamaCloseControls). All 5 returned; none died. No tool was installed or updated.

## Decision

- status `ok`: this is a real report with 8 cited lane commits, all ancestors of `master`.
- admitted `false`, verdict `rejected-honest-stop`.
- C1 (depth) does **not** verify under the claim's rule.
  - The rule frozen before data (A0, `d8bf1804`) is met by a type-only control:
    `controls-A1/CtlA1Conversion/receipt-A0.json` gives `registered 52 counted 20 met true`
    against target 18.
  - Amendment A1 (`75b78bb4`) was written after data seat DataG01 had scored live drafts
    with the A0 counter's functions (08:35:54Z). The round prompt
    (`.ufo/prompts/kama-round-28.md:357-358`) says: "A rule changed after any seat has scored
    is not the claim's rule". So A1 is a disclosed repair and not the claim's rule.
  - A1 is also met by a post-data projection of declared bounds:
    `w2/out/ExecShortcutPostData/shortcut-receipt.json` gives `v1-A1, registered 20 counted 20
    met true`.
- No axis was harmed. The author held depth at 7 and declined promotion, which this closure
  upholds.

## Dispatch and completion digest (`.ufo/watchdog.log`, copied)

```
2026-10-23T04:59:29-03:00 launch kama round=28 pgid=504272 driver=hyaku-inline attempt=1
2026-10-23T06:43:02-03:00 complete kama round=28; hyaku-inline attempt=1
```

These are lines 883 and 908 of `.ufo/watchdog.log` at closure time. Line numbers drift, so the
text above is the pointer.

## Step-1 conformance

| Check | Command | Observed | Result |
|---|---|---|---|
| Report committed by the lane identity | `git log --format='%an %ae %H %cI' -- .ufo/reports/round-28/kama.md` (fleet) | `kama-shokunin kama@shokunin.local b459870bc9b6d6bb3766e55b1e90baa5c963ecd0 2026-10-23T06:42:39-03:00` | holds |
| Report lands last | the report commit (06:42:39) vs lane tip `bdb2a5b4` (06:41:26) | the report comes after the tip and cites it | holds |
| `SHONEN` heading, one line per box | report lines 294-308; `git show bdb2a5b4:SHONEN.md \| grep -cE '^- \[[ x~]\]'` | 4 lines, all `[~]`; SHONEN.md has 4 boxes and is unchanged (`git diff --stat 4179301f bdb2a5b4 -- SHONEN.md` is empty) | holds |
| Cited commits exist and are ancestors of `master` | `git cat-file -t <h>`; `git merge-base --is-ancestor <h> master` | d8bf1804, 5ebe7b1b, 75b78bb4, fb10d9da, e49b4cf7, 9ce5bd37, c23ebaa4, bdb2a5b4 and base 4179301f: all `commit anc`. `704366d76` is upstream llama.cpp; it is not cited as a lane commit | holds |
| Lane pushed, no leftovers | `scripts/hyaku/jj-lane.sh state …/kama-shokunin`; `git status --porcelain` | `state branch=master local=bdb2a5b4… remote=bdb2a5b4… ahead=0 behind=0 head=detached tracked=0 untracked=0`; porcelain empty; `ls-remote origin refs/heads/master` = `bdb2a5b4…` | holds |
| Prompt carries the template contract | KamaCloseNoHarm read the prompt | 5 round-level items (§1 lines 3-7; §3 lines 80-82; §5 lines 131-139) and 5 child-lane items (report path line 101, SHONEN line 118, write scope lines 252-254, landed-hash rule line 274, lands-last line 318) | holds |
| Prompt committed before the report | `git log --format='%an %h %cI' -- .ufo/prompts/kama-round-28.md` | `kama-shokunin 6dd5e59 2026-10-23T04:59:28-03:00` | holds |
| Required report sections | KamaCloseNoHarm | Sources & frontier (line 173), Trend verdicts (line 201), Stale-lane line, tool-install line: all present | holds |

Conformance defect, status-neutral (routed item 2): `preregistration.json` key
`pre_data_amendment_A1` says "Written 2026-10-23 ~08:45Z by the L1". That bytes landed in
`75b78bb4`, whose commit time is `2026-10-23T05:38:16-03:00` (08:38:16Z). Evidence dated after
the commit that ships it breaks PROTOCOL §Evidence standard. `git show 75b78bb4:… | grep -c
08:45Z` gives 1. CriticA1Legitimacy found the error, but no correction was appended.

Fleet-root note: `git -C /home/vgpnk/Projects/shokunin status --porcelain` shows
` M .ufo/state/kama.report-baseline`. That is a driver state file, operator-side. It is not
lane work.

## Claims

### C1 — depth, `counted >= 18` (measured, sourced): **does not verify**

C1 was re-measured over committed bytes and also checked against the committed counter evidence.
I did not execute the counter. It launches the pinned llama-server and is lane-owned.

| Measurement | Command (lane repo) | Observed | Reported |
|---|---|---|---|
| Registry rows | `git show bdb2a5b4:registry/request-field-outcomes-r28.json \| jq '.rows\|length'` | 34 | 34 |
| SKILL table rows | `git show bdb2a5b4:SKILL.md \| awk '/^## Round-28 request-field outcomes/{f=1} f&&/^## /&&!/Round-28 request-field outcomes/{f=0} f' \| grep -cE '^\| F28-[0-9]{2} \|'` | 34 (base: `grep -c 'Round-28 request-field'` = 0) | 34 |
| SOURCES rows | `grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md` at base / tip | 139 / 173. S140-S173: 34 rows, all naming `704366d` | 139 → 173 |
| Generic-conversion rows (A1 clause e), derived by hand from registry `set`/`outcome` | jq listing of the 34 rows | F28-11/14/16/17/21/22: value above float32 max stored as `3.4028234663852886e+38`. F28-25: seed `4294967296` → `0` (uint32 wrap). F28-26: n_probs `2.5` → `2` (truncation). That is 8 rows, so 34 − 8 = **26** | A1: counted 26, not-counted exactly these 8 |
| Committed receipts | `final/c1-c23ebaa4.out`, `final/c1-A0-9ce5bd37.out`, `before/c1-base.out` | A1 `registered 34 counted 26 target 18 met True`; A0 `registered 34 counted 34 … met True`; base `registered 0 counted 0 … met False` | same |
| Counter identity | `git show <rev>:.ufo/waves/round-28/count-c1.py \| sha256sum` | A0 at d8bf1804 `e6a706bb…0540c`; A1 at bdb2a5b4 `a38faefe…49a5` | same |

Ruling on the author's two questions:

1. **Does C1 verify under the frozen (pre-A1) rule, given a control meets it? No.**
   - The prompt (`kama-round-28.md:352-356`) requires a target that a control skipping the
     claimed work cannot reach: "if it meets the target, the counter or target is wrong".
   - `CtlA1Conversion` is type-only and byte-blind: per its REPORT.md, no bound, default,
     handler or observed outcome was encoded. Under A0 it scores 20/52 (met). Under A1 it
     scores 0/52 (receipts above, counter shas `e6a706bb…` / `a38faefe…`).
   - So A0 cannot tell the claimed work apart from a type-conversion guess. The 34/34 under A0
     is not evidence of depth.
2. **Is A1 a rule change after scoring? Yes.**
   - DataG01 imported the frozen counter and applied `REJECT_RE`/`literals`/`same`/
     `outcome_text` to 4 live drafts. The tool call is at 08:35:53.929Z and its result, "all
     rows pass counter primitives: True", at 08:35:54.037Z
     (`w2/out/CriticA1Legitimacy/evidence.md:27-51`, quoting session transcript
     `KamaR28.DataG01-2`). DataG15 replayed the predicate at 08:36:53Z (`evidence.md:63`).
   - A1 was first edited at 08:37:23Z and committed at 08:38:16Z. At 08:37:50Z the L1 told
     DataG03 to re-probe min_p so that the clamp result would differ from every conversion
     (`w1/advice/DataG03.md`). Landed data was therefore shaped by the new rule.
   - A1's diff (`git diff d8bf1804 75b78bb4 -- count-c1.py preregistration.json`) changes only
     clause (e), so A1 accepts a subset of what A0 accepts. It is still a post-scoring rule.
   - Under prompt line 357-358 it is not the claim's rule. "Written before any data row was
     committed" does not cure this: the rule binds from the first seat that scores.
3. **Even A1 would not discriminate the claimed work.**
   - ExecShortcutPostData ran the A1 counter once (09:06:54Z, `counter-run.txt`) in a scratch
     clone of `e49b4cf7` with the landed C1 data stripped (`state-check.txt`). It met target
     with 20/20 rows projected from `set_limits`/`set_hard_limits`, and its writer ran no
     server.
   - The lane rejected it as "source-blind". I agree it is not source-blind. It reads the
     source semantics.
   - But it shows that about 20 of the 34 counted outcomes are predictable from
     `server-schema.cpp` alone. The live-measurement half of the depth claim is not what the
     counter credits (routed item 1).

Weighing without the five held control classes (no-reader, object-store, all-false, echo,
source-misuse; HOLDS.md, provider refusals and auto-switches). KamaCloseControls read the tip
counter and found:

- no-reader: refused by construction. Re-exec under the pinned `python3 -I -S`, an env equality
  check, and binary/library/model pins (count-c1.py:184-193, 375-392, 500-520).
- object-store: refused by construction. Base read by fixed oid through `--no-replace-objects`
  with per-object rehash (:69, :129-143).
- all-false: refused by the live replay. Bounds go through the `REJECT_RE` numeric match (:610)
  and values through `same()` (:616).
- source-misuse: refused by construction. `b:duplicate-line-or-field` (:560-566),
  `b:line-does-not-declare-field` (:490), `c:no-new-sources-row` (:480).
- echo: can pass under A0 only. Identity and default echoes are refused (:622, :626). Conversion
  echoes count under A0 and are refused under A1 (:624).

The holds therefore leave no open countable path that would change the ruling. The ruling rests
only on evidential receipts (CtlA1Conversion, ExecShortcutPostData) and on the committed timing
quotation. The 08:35:54Z timestamps come from transcripts outside the repo. The committed
pointer is the critic's verbatim quotation (routed item 3).

The content itself holds up. KamaCloseSources and this closure re-checked the sampled rows, and
wave 2 had re-measured all 34 rows live (RowReview01-17). The rows are true. What fails is the
claim's rule.

### Repairs (round-27 routed defects 1-7; not claims) — evidence-verified by KamaCloseRepairs

| Defect | Verdict | Evidence |
|---|---|---|
| 1 count-c2 cell trust | repaired | `git diff 4179301f bdb2a5b4 -- .ufo/waves/round-25/count-c2.py` (+217/−25) adds `derive_cell`/`cell_matches_raw`. The forged-cells demo goes from `observed 14 bound True` to `observed 11 bound False missing ['K2','K4','L1']`. The committed receipt still gives `registered 14 observed 14 bound True`. Coordinated forgery of cell, raw body and hash still passes, as disclosed. The round-25 file was edited in place |
| 2 F3 leg / per-class receipts | repaired as a criterion | QUALITY KQ37 item 4 requires them for future counters. The round-27 counter is retired without data. No F3 code leg exists, and the lane says so |
| 3 instrument registry | repaired, two deviations | SKILL.md `## Round-28 instrument registry`: 5 rows. `final/gate-registry-final.out`: `registered 5 unregistered 0`. Kinds include `measurement:`, which is not in PROTOCOL's `gate\|probe`. The retired row has no kind and no entry command |
| 4 S139/S136 wording | repaired | QUALITY KQ37 items 1-2 |
| 5 boundary-leg scope | repaired | QUALITY KQ37 item 3; echo entry lines 129-134 |
| 6 runnable recheck | repaired | `corpus/knowledge/echo-discriminating-counters.md` line 3 now carries a runnable recheck. `ExecEchoRecheck/run1.json`, `run2.json`: `same 6 total 6`. The drift falsifier gives `same 5 exit 1`. The exit 2 on an existing path is asserted, but only the sentinel file is committed |
| 7 r27 report facts | repaired | `round-27/residual/spawn-result.txt` shows resend at `07:23:39.921107+00:00`. `final/r27-8057282c-stat.out` lists 4 files |

New tool `tools/gate-registry-check.py` is registered as a gate but is occurrence-only:
`unregistered = [p for p in counters if p not in text]` (lines 129-131). It has no fixture
self-test: argparse takes only `--repo`/`--rev` (lines 136-141). That misses the PROTOCOL §Gate
standard self-test clause. Its final output does not name the revision it measured (routed
item 4).

## Per-axis verdicts

`git diff 4179301f bdb2a5b4 -- SCORECARD.md`: +39/−0. Scores are the same before and after:
operability 8, freshness 8, coverage 9, depth 7, calibration 7, adjacency 7.

| Axis | Verdict | Basis |
|---|---|---|
| depth | unprovable | C1 does not verify under its own rule (above). The rows are true and live-reproduced, but the frozen counter is met by a type-only control, and the post-scoring A1 is met by a declared-bounds projection. SCORECARD 7 → 7 |
| calibration | unchanged | not claimed. ResSelfAssessment's 3/46 mismatches are a disclosure: 2 were corrected by an appended LOG entry and 1 is open in SHONEN box 2 |
| coverage | unchanged | not claimed |
| operability | unchanged | not claimed. The tools are repairs |
| freshness | unchanged | not claimed |
| adjacency | unchanged | ConnectorSiblings: no contested scope |

No harm:

- LOG.md +45/−0, SOURCES.md +34/−0, QUALITY.md +15/−0, SKILL.md +97/−0, SHONEN.md unchanged.
- The only deletions in the diff are the routed count-c2 repair and the echo entry's recheck
  line, which was replaced by a runnable command with nothing lost.
- Census: exit 0 (below).

## Spot-check (LEARNING.md §Discernment is checked from outside)

| Item | Decision | Re-opened source | Agree/disagree | Reason |
|---|---|---|---|---|
| S152 `temperature` (L116) SOURCES row | admit | `curl -sSfL https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp`, fetched 2026-10-23T09:46Z, sha256 `1f9d7b73b4363b90b08de0360b0a5ce0b3d152750bfb8d587a367e90c7904050` (equal to the pin) | agree | Lines 116-117, whitespace-joined, read `add((new field_num("temperature", params.sampling.temp)) ->set_limits(0.0f, std::numeric_limits<float>::infinity())`. That is verbatim and 5 words. `set_limits` is a soft clamp, which matches F28-13 (`-1.0` → 200, `temperature = 0.0`) |
| S140, S165, S173 SOURCES rows (KamaCloseSources) | admit | the same fetch; lines 40-41, 179-180, 453-454 | agree | Verbatim, 5 / 11 / 22 words. The snapshot under `sources/llama.cpp-704366d/` is byte-identical |
| CriticA1Legitimacy timing correction | admit | `w2/out/CriticA1Legitimacy/evidence.md:27-51`; `git log -1 --format=%cI 75b78bb4` = `05:38:16-03:00` | agree, with a defect | DataG01 scored at 08:35:54Z, before A1 (08:37:23Z / 08:38:16Z). The lesson and report carry the correction, but `preregistration.json` still says "~08:45Z" (routed item 2) |
| Count the float32-saturation rows and seed/n_probs as field knowledge (DataG03/05/07/08) | reject | the same fetch, lines 101-102: `top_n_sigma` has only `set_desc`, with no limits | agree | `3.5e+38` → `3.4028234663852886e+38` is float32 saturation of the value sent, and the field declares no bound. `4294967296` → `0` is a uint32 wrap and `2.5` → `2` is truncation. These are conversions, not field behaviour |
| DataG12 json_schema → grammar row (KamaCloseSources) | reject | `w1/out/DataG12/rows.json`; count-c1.py:218 | agree | The live GBNF contains a literal `\|` (`space ::= \| " " \| …`). The table parser splits on `\|`, so the row cannot be held. The no-row disclosure is kept |
| ExecShortcutPostData "as a source-blind control meeting A1" | reject | `w2/out/ExecShortcutPostData/shortcut-receipt.json` (`v1-A1 registered 20 counted 20 met true`, counter `a38faefe…`) | agree, with a scope note | It is not source-blind, because it reads `set_limits`/`set_hard_limits`. But it meets the A1 counter without a server run by the writer. The lane records this as a counter limit. This closure treats it as further evidence that C1's counter does not credit the live work (routed item 1) |

Census: `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root
/home/vgpnk/Projects/shokunin kama` gives `kama ok …/kama-shokunin/corpus/SOURCES.md`, exit 0.
The only warnings are W04 duplicate-URL advisories, including S141-S173, which share one file
URL with different anchors.

Minor discrepancy: the lesson's `## Gate` preamble says "Four seat-supplied quotes were not
verbatim". `final/quote-check.out` and the Mistakes row say 8 (four paraphrased, four joined with
"…"). The published gate quotes are unaffected (`gate quotes 34 not-verbatim 0`).

## Trend verdicts

- **expansion: unprovable-but-better.**
  - A surface with zero lane hits at base (`ScoutProvince/grep-hits.txt`; SKILL count 0) now
    holds 34 live-reproduced field outcomes and 34 opened tier-A sources. The sampled quotes
    and the sha256 re-verify.
  - The ground did not arrive through an admitted claim, so this closure does not grade it
    `improved`.
- **quality: unchanged.**
  - I agree with the author. The repairs (count-c2 binding, KQ37, the runnable recheck) fix
    defects and supersede no entry.
  - The 16 meaning-cell corrections were made to this round's own unadmitted rows.
- **discernment: improved.**
  - The spot-check agrees with the gate on every sampled admit and reject.
  - The lane reported both rule results and declined promotion instead of citing the
    favourable A1 number.
  - The A0 blind spot became a Mistakes row with a shown-able-to-fail fix.

## SHONEN (for the operator; promotion is operator-owned)

All 4 boxes are `[~]`, as the author asserts. Box 1 (decision tables with cited sources) is
checkable by a non-author from SKILL.md and S140-S173. Box 2 carries the open round-17 wording
mismatch (ResSelfAssessment). This closure writes no `[x]`.

## Routed defects (lane fixes next round)

1. **C1 counter design.** A depth re-claim on the request-field table needs a counter frozen
   before any seat scores. Its pre-data receipts must include a type-only control and a
   declared-bounds projection control (the ExecShortcutPostData policy). The counted property
   must be one that `server-schema.cpp` alone does not predict. Otherwise the table is sourced
   quality work, not depth.
2. **Future-dated amendment text.** `preregistration.json` `pre_data_amendment_A1` says "~08:45Z"
   but was committed at 08:38:16Z. Append a named correction (lesson/LOG) giving 08:37:23Z
   (edit) and 08:38:16Z (commit). Leave the frozen bytes untouched.
3. **Timing evidence outside the repo.** The DataG01 and DataG15 scoring times rest on session
   transcripts quoted in `CriticA1Legitimacy/evidence.md`. Commit the raw transcript excerpt
   with its sha256, or state that the source is unreachable.
4. **`tools/gate-registry-check.py`.** Add a fixture self-test with committed expected
   finding-ids and record its spelling in the registry row. Check full registry-row fields, not
   path occurrence. Print the revision it measured.
5. **Instrument registry.** Map `measurement:` rows to `gate|probe` (PROTOCOL §Gate standard
   Registry). Give the retired round-27 row a kind and an entry command, or mark it explicitly
   as non-runnable.
6. **`tools/echo-recheck.py`.** Commit a receipt of the exit code for the exit-2 refusal on an
   existing path. Only the sentinel file is committed now.
7. **Lesson Gate preamble.** It says 4 non-verbatim seat quotes; `final/quote-check.out` says 8.
   Append a correction.
8. **Report wording.** `reports/round-28/kama.md:156-160` and `:278-280` do not say that the final
   A1 counter is also met by a post-data declared-bounds projection (20/20). Correct this in the
   round-29 report.
9. **SHONEN box 2.** The round-17 wording mismatch is still open (carried from this round's
   ResSelfAssessment).
