# considerthese proposal audit — Round 52 (kama lane)

**Seat:** `N3Consider` (UFO-FSD connector / leaf seat, round 52 wave 1)  
**Assigned task:** Read the latest file in `/home/vgpnk/Projects/shokunin/kama-shokunin/considerthese/` (`ls -t`) and the one before; list each proposal marked not implemented; check against the lane tree at commit `5dacf2c70f947ca6dc5fbbca6d45b8db5b0390c8` whether each is now implemented (grepping `tools/`, `corpus/QUALITY.md`, `SKILL.md`); pick the ONE that fits this round's claims best with the exact text it would land as (lesson row, QUALITY criterion or SOURCES row citing `considerthese/<file>` + date).  
**Judged on:** calibration, operability  
**Base revision:** `9ff76b1f763512be2f554cbbfd0b2213b63b0847`  
**Freeze commit:** `8551ba7f2056f2465d20f5b50586978133212fe1`  
**Build commit evaluated:** `5dacf2c70f947ca6dc5fbbca6d45b8db5b0390c8`  

---

## 1. Input Files Inspected

Per `ls -lt /home/vgpnk/Projects/shokunin/kama-shokunin/considerthese/`:
1. **Latest file:** `/home/vgpnk/Projects/shokunin/kama-shokunin/considerthese/2026-10-26.md` (mtime Oct 26 09:30 BRT, commit range `df61204c`..`a553bd7c`, tip `a553bd7c`)
2. **One before:** `/home/vgpnk/Projects/shokunin/kama-shokunin/considerthese/2026-10-25.md` (mtime Oct 26 01:03 BRT, commit range `5c9ef1fe`..`c5545d89`, tip `c5545d89`)

Both files group their proposals under `## Self-improvement suggestions` with the author qualification:
> *"These are proposals only; I am not acting on any of them."*

---

## 2. Inventory of Proposals Marked Not Implemented

### From `considerthese/2026-10-25.md` (`:25-33`)
1. **Proposal 1 (line 27) — Recompute every digest and S-id that a new lesson or row cites:**
   > *"the S472 digest (right prefix, wrong body) and round 36's five misattributed ids are exactly the kind of thing a read-only daily pass can check mechanically. I could hash each committed evidence file a new row points at and compare full digests, and cross-check every S-id named in lesson prose against the row it is said to be, then report mismatches the morning after they land instead of one round later. This differs from re-opening quotes (suggested 10-24) because it checks identifiers and hashes, not wording."*
2. **Proposal 2 (line 29) — Watch the version pins for upstream releases:**
   > *"round 38 pinned SGLang knowledge to v0.5.22 and recorded that no v0.5.23 or v0.5.24 tag existed. I could run the same `git ls-remote --tags` check daily for each pinned engine (SGLang, and the vLLM doc versions v0.9.0, v0.17.0, v0.19.1, v0.32.0 the rows cite) and flag when a newer release appears, so freshness has a concrete trigger instead of waiting for each row's 90-day `recheck`."*
3. **Proposal 3 (line 31) — Keep a ledger of staged items the lane keeps rejecting:**
   > *"the same Google Cloud health-route file (and its r4 amendment) was offered from the shokuknow merge package and rejected as out of province in rounds 35, 36 and 37. A short table of rejected staged files, the reason and how many rounds they reappeared would show João whether the upstream package should stop offering them, which saves a seat and a closure check every round."*
4. **Proposal 4 (line 33) — Report seat yield per wave:**
   > *"round 34 launched 33 seats with `rc=1` for all of them and only 5 committed reports, round 36's first attempt died on a provider route failure, and round 36 seats hit `429` rate limits. A daily line with seats launched, reports landed and the failure reason (rate limit, provider route, timeout) would show whether waves are sized beyond what the providers allow. This extends the 10-24 attempt-count idea with the provider-failure evidence that only appeared in this window."*

### From `considerthese/2026-10-26.md` (`:27-35`)
1. **Proposal 1 (line 29) — Flag deletions in append-only files the morning after they happen:**
   > *"0718b6ab removed thousands of lines from four files the lane treats as append-only, and only a same-round repair caught it. In my daily pass I could list every window commit whose numstat shows deletions in `SCORECARD.md`, `LOG.md`, `corpus/QUALITY.md`, `corpus/README.md` or `corpus/SOURCES.md` beyond a small threshold, and say whether a later commit restored the bytes. That is a read-only check I can do with the GitHub API alone."*
2. **Proposal 2 (line 31) — Track what happens to my own proposals:**
   > *"three of the four 2026-10-25 proposals became rounds 41 to 43 (and round 40 first deferred pin-watch as 'detects nothing today'). A short table in each daily file, with each past proposal, the round that took it up or deferred it, and its closure verdict, would let me calibrate what kind of proposal is useful and stop repeating ones that keep getting deferred."*
3. **Proposal 3 (line 33) — Keep a running count of counters that a shortcut can satisfy:**
   > *"each SCORECARD section now has a 'What `met=True` does not show' paragraph, but nothing trends it. I could tally, per round, the shortcut controls that met the frozen counter, the mutants that survived, and whether the falsify wave ran, so João can see whether counter design is actually getting harder to fool or just better disclosed."*
4. **Proposal 4 (line 35) — Report the pin gap every morning:**
   > *"round 45 already samples llama.cpp at b11897 while the corpus is re-verified at b11889. Reading upstream tags is read-only, so I could add one line per pinned engine (newest tag, how many releases sit above the pin) to each daily file, which gives the next freshness round a dated trigger without anyone running `pin-watch` by hand."*

---

## 3. Implementation Verification Against Lane Tree at Commit `5dacf2c70f947ca6dc5fbbca6d45b8db5b0390c8`

Mechanical scan command executed:
`git -C /home/vgpnk/Projects/shokunin/kama-shokunin grep -n -E "<pattern>" 5dacf2c70f947ca6dc5fbbca6d45b8db5b0390c8 -- tools/ corpus/QUALITY.md SKILL.md`

### Summary Matrix

| Day & Proposal | Short Name | Implemented at `5dacf2c70f947ca6dc5fbbca6d45b8db5b0390c8`? | Primary Location & Git Evidence |
|---|---|---|---|
| `2026-10-25` #1 | Digests & S-id cross-check | **Partially Implemented** (Digests & hex runs implemented; S-id prose check open) | `tools/digest-ledger.py:2`, `tools/hexrun-census.py`, `SKILL.md:1403,1421,1536`, `corpus/QUALITY.md:352,363` (KQ50, KQ55). S-id cross-check remains open in `corpus/README.md:120` and `SCORECARD.md:2887`. |
| `2026-10-25` #2 | Watch version pins | **Implemented in substance** (Tool & consumer landed; daily cron scheduler omitted) | `tools/pin-watch.py`, `tools/pin-trigger-consumed.py`, `SKILL.md:1400,1418`, `corpus/QUALITY.md:373` (KQ58). Mined in round 41 C2, consumed in round 44 C1. |
| `2026-10-25` #3 | Staged refusals ledger | **Implemented** | `registry/staged-refusals.tsv` (73 rows), `corpus/QUALITY.md:365` (KQ57). Built in round 43 frontier. |
| `2026-10-25` #4 | Seat yield per wave | **Implemented** | `tools/seat-yield.py:2`, `SKILL.md:1431`, `corpus/QUALITY.md:377` (KQ62). Mined in round 45. |
| `2026-10-26` #1 | Flag append-only deletions / restoration | **Implemented & Completed in Round 52** | `tools/append-only-audit.py:2` (v1-v6), `SKILL.md:1441-1495`, `corpus/QUALITY.md:395,441` (KQ67, KQ86). Completed in round 52 C2 by verbatim re-append of 155 lost lines across 18 files (`corr_lost=0`). |
| `2026-10-26` #2 | Track own proposals | **NOT Implemented in lane surfaces** | 0 hits in `tools/`, `corpus/QUALITY.md`, `SKILL.md`. Executed only as ephemeral wave seat reports (`S8Proposals`, `S8Considerthese`, `T8Considerthese`, `T9Considerthese`, `N3Consider`). |
| `2026-10-26` #3 | Shortcut tally across rounds | **Implemented** | `tools/shortcut-tally.py:2`, `SKILL.md:1476-1485`, `LOG.md:2314`. Promoted from round-47 seat `X9Tally` into `tools/` in round 48. |
| `2026-10-26` #4 | Daily pin gap report | **NOT Implemented in lane surfaces** | 0 hits in `tools/`, `corpus/QUALITY.md`, `SKILL.md`. Ad-hoc runs by wave seat `U2Pins` in rounds 47–49, but no standing tool or criterion. |

---

## 4. Selection: The ONE Proposal That Fits Round 52's Claims Best

### The Chosen Proposal
**`considerthese/2026-10-26.md` Proposal 1 (`considerthese/2026-10-26.md:29`, dated 2026-10-26):**
> *"Flag deletions in append-only files the morning after they happen: `0718b6ab` removed thousands of lines from four files the lane treats as append-only, and only a same-round repair caught it. In my daily pass I could list every window commit whose numstat shows deletions in `SCORECARD.md`, `LOG.md`, `corpus/QUALITY.md`, `corpus/README.md` or `corpus/SOURCES.md` beyond a small threshold, **and say whether a later commit restored the bytes**."*

### Why It Fits Round 52's Claims Best
Round 52 has two claims:
- **C1 (operability 8→8):** Server replay executed from a sealed anonymous memfd (`memfd_create(2)`, S500).
- **C2 (calibration 7→7):** Every line the A-corr files lost in place across repository history is re-appended verbatim under `## Restored lines (round 52)` inside five-backtick fences across 18 files, eliminating unheld loss (`corr_lost=0`) and removing their rows from `registry/append-only-disclosures.tsv`.

The verbatim re-append in Claim C2 is the exact substantive completion of `considerthese/2026-10-26.md` Proposal 1:
1. **The lineage of Proposal 1:**
   - **Round 46 C2:** Built `tools/append-only-audit.py` with a 20-line threshold.
   - **Round 50 closure (R6):** Verifier spot-check demonstrated that the 20-line threshold hid 97 real deletion events (including the `ed135b3c` `LOG.md` loss).
   - **Round 51 C2:** Audited every deletion at threshold 1 (106 events) and created `registry/append-only-disclosures.tsv`, disclosing 165 lost lines across 51 events, but leaving the bytes unrestored in the files.
   - **Round 52 C2:** Closes the loop by having a later commit restore the bytes verbatim: 155 lost lines across 18 A-corr files are re-appended verbatim inside five-backtick fences, achieving `corr_lost=0` and removing all A-corr rows from the disclosure ledger.
2. **Resolution of Round-51 Closure Defect D7:**
   The round-51 verifier spot-check (`corpus/lessons/round-51-verifier-spotcheck.md:125`) recorded defect D7: `KQ86` cited `C2; round-50 R6; considerthese/2026-10-26.md proposal 1` without citing a producing lesson file. Landing the exact lesson row in `corpus/lessons/round-52.md` and the superseding `KQ86`/`KQ89` rows in `corpus/QUALITY.md` heals this defect.
3. **The Lesson Gap at `5dacf2c70f947ca6dc5fbbca6d45b8db5b0390c8`:**
   At commit `5dacf2c70f947ca6dc5fbbca6d45b8db5b0390c8`, `corpus/lessons/round-52.md:12` claims C2 but omits any citation of `considerthese/2026-10-26.md` Proposal 1. Supplying this exact text bridges the round build to the operator reflection.

---

## 5. Exact Text for Landing

### A. Lesson Row for `corpus/lessons/round-52.md`
To be added to `corpus/lessons/round-52.md` at the end of the `## Claims` section (or following claim C2):

```markdown
- **considerthese:** `considerthese/2026-10-26.md` (dated 2026-10-26) proposal 1 ("and say whether a later commit restored the bytes") is fulfilled by claim C2: the 155 lines lost in place across 18 A-corr files are re-appended verbatim at the end of each file under `## Restored lines (round 52)` (`###` in `SCORECARD.md`), achieving `corr_lost=0`, removing their disclosure ledger rows from `registry/append-only-disclosures.tsv`, and verifying that later commits restored the declared append-only bytes.
```

### B. QUALITY Criterion Rows for `corpus/QUALITY.md`
To be appended to `corpus/QUALITY.md`:

#### 1. New Criterion `KQ89` (The Append-Only Verbatim Restoration Invariant):
```markdown
| KQ89 | A file declared append-only with corrections appended (A-corr) holds every line it ever committed: lines lost in place in historical commits are restored verbatim at the file's tail inside fences under `## Restored lines (<round>)` (`###` in `SCORECARD.md`), achieving `corr_lost=0`; disclosure in `registry/append-only-disclosures.tsv` is reserved for unrepairable A/A-row conflicts (such as `corpus/SOURCES.md` immutable-cell edits or errata keys) where re-append would create duplicate IDs. | An A-corr file deletion is left as a permanent disclosure row in `registry/append-only-disclosures.tsv` without verbatim restoration; lines re-appended without verbatim match or outside fences; `corr_lost > 0` on A-corr files. | C2; SCORECARD §Planned (round 52) item 2; `considerthese/2026-10-26.md` proposal 1 (opened 2026-10-26); `corpus/lessons/round-52.md` |
```

#### 2. Superseding Row for `KQ86` (Healing Round-51 Closure Defect D7):
```markdown
| KQ86 (superseded by this row per round-51 closure D7) | An append-only audit grades every deletion: no line-count threshold may hide an event, because a one-line in-place edit of an append-only file is the commonest violation | a policy constant (20 lines) that hid 101 of 106 deletion events, the real `LOG.md` loss at `ed135b3c` among them | C2; round-50 R6; `considerthese/2026-10-26.md` proposal 1 (opened 2026-10-26); `corpus/lessons/round-50-verifier-spotcheck.md:120`; `corpus/lessons/round-51.md:13` |
```

### C. SOURCES Row (if Recorded as S501 in `corpus/SOURCES.md`)
```markdown
| S501 | considerthese/2026-10-26.md Proposal 1 — operator reflection on append-only loss restoration | docs | A | operator daily reflection proposing checking whether later commits restored bytes deleted from append-only files | considerthese/2026-10-26.md:29 (§Self-improvement suggestions item 1) | "and say whether a later commit restored the bytes." — grounds the verbatim re-append of 155 lost lines under ## Restored lines (round 52) to achieve corr_lost=0 | mined | 2026-10-27 | 360d | corpus/lessons/round-52.md |
```

---

## 6. UFO-FSD Connector Synthesis

### Evidence
1. `considerthese/2026-10-26.md:29` asked for monitoring deletions in append-only files and determining "whether a later commit restored the bytes."
2. Round 51 introduced `registry/append-only-disclosures.tsv`, which disclosed 165 lost lines across 51 events, establishing provenance without restoration.
3. Round 52 build `5dacf2c70f947ca6dc5fbbca6d45b8db5b0390c8` re-appends 155 of these lines verbatim under `## Restored lines (round 52)` across 18 A-corr files, removing their disclosure rows and verifying `corr_lost=0` via `tools/round52-append-restore-check.py`.
4. Defect D7 from `corpus/lessons/round-51-verifier-spotcheck.md:125` noted that `KQ86` cited `considerthese/2026-10-26.md proposal 1` without a producing lesson file citation.
5. In `corpus/lessons/round-52.md` at `5dacf2c70f947ca6dc5fbbca6d45b8db5b0390c8`, Claim C2 describes the 155-line restoration but omits the `considerthese:` citation line.

### Affected Axes
- **Calibration (improved):** Unifies the lane's declared append-only invariants (`registry/append-only-contract.tsv`), disclosure ledger (`registry/append-only-disclosures.tsv`), operator suggestions (`considerthese/2026-10-26.md`), quality criteria (`KQ86`/`KQ89`), and lesson prose (`corpus/lessons/round-52.md`) into a single self-consistent historical record without loss.
- **Operability (held/neutral):** C1 sealed memfd server execution (`memfd_create(2)`, S500) remains untouched, clean, and decoupled from C2 text restoration.

### Proposed Move
Integrate the completion of `considerthese/2026-10-26.md` Proposal 1 into the durable record of Round 52:
1. Append the explicit `considerthese:` attribution to `corpus/lessons/round-52.md:13`.
2. Add criterion `KQ89` to `corpus/QUALITY.md` defining the verbatim restoration requirement for A-corr files (`corr_lost=0`).
3. Add the superseding row for `KQ86` in `corpus/QUALITY.md`, citing `corpus/lessons/round-50-verifier-spotcheck.md:120` and `corpus/lessons/round-51.md:13` to resolve defect D7.

### Risks and Second-Order Effects
- **Heading Pollution / Parser Confusion:** Historical markdown lines restored verbatim may contain headings (`## ` or `### `) that naive parsers could mistake for active document sections.
  - *Mitigation:* In Round 52, all restored blocks are enclosed inside five-backtick fences (` `````text ... ````` `), and both `tools/append-only-audit.py` and `tools/round52-append-restore-check.py` are explicitly fence-aware (KQ83).
- **Duplicate Identifiers:** If immutable registry rows (such as `corpus/SOURCES.md` S-ids or `registry/report-landing-errata.tsv` errata keys) were re-appended verbatim, duplicate key defects would occur.
  - *Mitigation:* The build correctly restricts verbatim re-append to the 18 A-corr files (155 lines), leaving the 10 unrepairable A/A-row lines in `registry/append-only-disclosures.tsv`.

### Verification
1. Counter verification:
   `python3 tools/round52-append-restore-check.py --repo /fast/scratch/hyaku/kama-r52/N3Consider/lane --tip 5dacf2c70f947ca6dc5fbbca6d45b8db5b0390c8 --scratch /fast/scratch/hyaku/kama-r52/N3Consider`
   Yields: `fixture=1 lane=1 scenarios=8/8 corr_lost=0 met=True` (exit 0).
2. Heading and fence isolation:
   Grep across all 18 files confirms restored lines reside exclusively within `## Restored lines (round 52)` (`###` in SCORECARD.md) five-backtick blocks.
3. Citation integrity:
   Verification that `KQ86` superseding row cites lesson files `round-50-verifier-spotcheck.md` and `round-51.md`, and `KQ89` cites `round-52.md`.
