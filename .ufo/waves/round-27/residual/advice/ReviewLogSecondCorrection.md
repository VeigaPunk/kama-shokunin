VERDICT: holds — every statement in the second LOG.md correction (`## Correction … — to the correction entry above`) and the `## Round 27 — …` entry checks against git history and the cited a3/ and w1a3/ files, and LOG.md is strictly append-only 0ec32cac→52632caa2ed813c1c12f7a9dcab3556b4f0bd9eb (+62/−0 across the two commits that carry the entries).

Scope: LOG.md:1747–1758 (second correction) and LOG.md:1760–1788 (Round-27 entry) at lane tip 52632caa. First correction entry (LOG.md:1728–1745, landed 324d5d62) is in scope only as the object the second correction describes. All git commands read-only in /home/vgpnk/Projects/shokunin/kama-shokunin. Raw evidence captured under `.ufo/waves/round-27/residual/out/ReviewLogSecondCorrection/` (`git-evidence.txt`, `log-rewrite-diffs.txt`, `context-evidence.txt`).

## Append-only check (required output)

```
$ git diff --numstat 0ec32cac 52632caa -- LOG.md
62	0	LOG.md        (exit 0; zero deleted lines)
$ git log --numstat --format='COMMIT %h %ci %s' 0ec32cac..52632caa -- LOG.md
COMMIT d183ec5 2026-10-23 04:20:53 -0300   43	0	LOG.md   ← second correction + Round-27 entry
COMMIT 324d5d6 2026-10-23 03:54:43 -0300   19	0	LOG.md   ← first correction
$ git status --porcelain -- LOG.md          → (empty; working-tree LOG.md == tip)
$ git rev-parse HEAD                        → 52632caa2ed813c1c12f7a9dcab3556b4f0bd9eb
```

d183ec57's diff is a single EOF hunk (`@@ -1743,3 +1743,46 @@`) whose +43 lines are exactly the two target entries. Strictly append-only: no commit in range touches a prior LOG.md line.

## Statement table — `## Correction … — to the correction entry above` (LOG.md:1747–1758)

| # | Statement (LOG.md line) | Verdict | Evidence |
|---|---|---|---|
| 1 | "The correction entry immediately above (landed `324d5d62`)" (:1750) | holds | `git log 0ec32cac..52632caa -- LOG.md`: 324d5d6 is the commit that added the first correction (+19/−0); 324d5d62e61276af312c8eb42f678004aec245d1 per ReviewRepairD1Log's own citation |
| 2 | "has two errors, found by wave seat ReviewRepairD1Log (`…/w1a3/advice/ReviewRepairD1Log.md`)" (:1750–1751) | holds | file exists; its verdict line names exactly the two errors: "miscounts the rewrite as 'three sentences' … and it omits the intermediate in-place edit `f4066979`" |
| 3 | 'It says the rewrite "changed three sentences"; the diff changes four (the Before, candidate-count, ports and repairs sentences), as its own list shows' (:1752–1754) | holds | `git diff 7f84cd0e fd48f9a3 -- LOG.md` (25+/7−) rewrites four sentences — "Before…no live error signature" → two-signature account; "58 candidates" → 57+8 account; "ports that are now dead" → registered-ports account; "42 late paths committed (a4a159c3)" → 220/2/1 + 7e5ff9b5 account — and adds two paragraphs. The first entry's own list (LOG.md:1734–1738) enumerates all four + the two paragraphs, contradicting its "three". Same finding as ReviewRepairD1Log statement #5 (its verdict: **breaks**) |
| 4 | "it presents a two-step history: the round-26 entry was also rewritten in place at `f4066979` (00:56:41 -0300, \"LOG candidate count corrected\") between `7f84cd0e` and `fd48f9a3`" (:1754–1756) | holds | `git log --format='%h %ci %s' 7f84cd0e..fd48f9a3 -- LOG.md` → `fd48f9a 2026-10-23 01:09:37 -0300` and `f406697 2026-10-23 00:56:41 -0300 round-26: LOG candidate count corrected…`; `git diff 7f84cd0e f4066979 -- LOG.md` is an in-place rewrite of the candidates sentence. The first correction names only 7f84cd0e→fd48f9a3. Same finding as ReviewRepairD1Log #4 and Findings 2 |
| 5 | "so the candidate sentence reached its final form in two steps (`git log …`)" (:1755–1757) | holds | step 1 (f4066979): "executors filed 57 candidate entries … scout listed 8 more, 3 of them not found by an executor"; step 2 (fd48f9a3): "… scout listed 8, of which 3 no executor found". Both sub-diffs in `log-rewrite-diffs.txt` |
| 6 | "The \"Counter discrimination\" paragraph was inserted mid-entry, not appended." (:1757–1758) | holds | fd48f9a3 hunk: `+**Counter discrimination (found after data).**` lands before the pre-existing `**Motivating evidence.**`; only `**Falsify wave (34 seats).**` is appended at end-of-entry. Confirms ReviewRepairD1Log #6 nit; the first entry's "appended two paragraphs" is thereby half-wrong — consistent with the entry's own "has two errors" framing |
| 7 | "The entry above is not edited." (:1758) | holds | d183ec57 is +43/−0 at EOF; no commit 0ec32cac→52632caa deletes or modifies any prior LOG.md line |

Nit (not a defect): "a two-step history" loosely describes the first entry's two-commit narrative (land→rewrite); the actual history is three commits. ReviewRepairD1Log phrased it "a two-commit history for a three-commit history". The correction's substantive claim — f4066979 is an omitted in-place rewrite — is exact.

## Statement table — `## Round 27 — …` (LOG.md:1760–1788)

**C1 paragraph (:1763–1766)**

| # | Statement | Verdict | Evidence |
|---|---|---|---|
| 8 | "Preregistered by attempt 1 (`530eaa99`, amendments A1-A3 to `1471f676`), target `counted >= 15`" | holds | `git log -- .ufo/waves/round-27/preregistration.json` → 530eaa9 (A0 freeze, attempt-1 commit msg), 6020243 (A1), a712902 (A2), 1471f67 (A3, attempt 2); preregistration.json:16 `counted >= 15 at the landed lane tip` |
| 9 | "The attempt-2 control wave (37 seats, 05:41:33Z) died with the orchestrator at 06:19:06Z without committed receipts" | holds | w1-controls/spawn-result.txt:1 = `2026-10-23T05:41:33.096709Z` + "Spawned 37 background agents" (KamaR27A2.* names); dispatch.json `counts.spawn=37`; `git log 0ec32cac..52632caa -- .ufo/waves/round-27/w1-controls/` → empty: only dispatch artifacts were committed at 0ec32cac, zero receipts after. 06:19:06Z death is attested by a3/plan.json (the committed record; the process's death is un-re-observable by nature) |
| 10 | "a dead seat's task is not resent and no data seat was dispatched" | holds | `.ufo/waves/round-27/` holds no data-wave dir; plan.json: "No data seat of round 27 was ever dispatched" |
| 11 | "Attempt 3 withdrew C1 before data (`a3/plan.json`); under the frozen kill rule the landed tip's count is a miss." | holds | plan.json `C1.disposition: "withdrawn before data"`; kill rule preregistration.json:17 ("counted < 15 at the landed tip is a miss"); `a3/c1-tip.out` = `registered 0 counted 0 target 15 met False` run on a fresh clone at d183ec57 with counter sha256 49491b80…2765 (frozen); at the actual tip `git ls-tree HEAD registry/` shows no r27 registry and SKILL.md has no Round-27 section → counted=0 forced at 52632caa too |

**X1 paragraph (:1767–1773)**

| # | Statement | Verdict | Evidence |
|---|---|---|---|
| 12 | `corpus/knowledge/echo-discriminating-counters.md` and QUALITY KQ37 (+ round-27 qualification) exist; rule = "refuse decoded-request echoes, one row per message frame, signature inside server-owned text" | holds | file exists; QUALITY.md:219 KQ37 ("refuses the signature when it occurs … in any JSON-decoded key or value of the request body … credits at most one row per message frame"); :221–242 qualification; :231 "the signature lies wholly inside text the server owns" |
| 13 | Motivating evidence `lessons/round-26-verifier-spotcheck.md:98-116` | holds | lines 98–116 record the verified shortcut (12/12 receipt, `\u00XX` escapes, raw-byte echo check at round-26 count-c1.py:384 defeated by JSON decoding) |
| 14 | "RFC 8259 §7 (S136, S139)" | holds | SOURCES.md:148 (S136, §7 Strings) and :151 (S139, supersedes, same fetch sha256 61a5378f…2d7) |
| 15 | "`server-common.cpp:1375` (S137)" | holds | SOURCES.md:149 "throw at 1375" |
| 16 | "live probe `w1a3/out/ExecLiveEchoProbe/receipt.json`; offline replay and mutation receipts under `w1a3/out/`" | holds | receipt.json present (`all_decoded_sig_in_message: true`, `frames_equal_all_error_cases: true`, observed 2026-10-23T07:11:54Z); dirs ExecOfflineEchoReplay, ExecOfflineFrameReplay, MutEchoDecodedLoadBearing, MutFrameLoadBearing all present |
| 17 | "Verdict pending a named non-author reviewer." | holds | plan.json X1 verdict_rule: `unprovable-but-better` only with a named non-author reviewer on record; no verdict asserted in the entry — consistent |

**Repairs paragraph (:1775–1777)**

| # | Statement | Verdict | Evidence |
|---|---|---|---|
| 18 | defect 1 → "LOG correction entries above" | holds | spotcheck :233 routes defect 1 as an appended LOG correction; the two entries above are that repair |
| 19 | defect 3 → `repairs/d3-r26-shortcut-pins/`, defect 4 → `repairs/d4-r26-dead-seat-errors/` | holds | both dirs exist and are populated (`ls` in context-evidence; lesson §Repairs items 3–4 describe contents) |
| 20 | defects 5,6 → "lesson §Repairs"; defect 7 → "S138"; defect 2 → "A3 + KQ37"; "8 open" | holds | lesson §Repairs items 5/6 handle the receipt-key mislabel and Gate reject reasons; item 7 is S138 supersedes S133; item 2 is the A3 counter + KQ37 repair; item 8 "count-c2.py … **not fixed** this round … stays open" |

**Re-verification paragraph (:1779–1781)**

| # | Statement | Verdict | Evidence |
|---|---|---|---|
| 21 | "Round-start census re-run on a clone at `0ec32cac` (`a3/census-start-0ec32cac.out`, exit 0) and reproduced by ReviewCensusStart" | holds | file tail: `ok` line + `exit=0` trailer naming the 0ec32cac clone; ReviewCensusStart verdict: holds — "reproduces byte-for-byte … modulo the path-dependent `ok` line and the seat-added trailer" |
| 22 | "S133's source re-fetched (sha256 unchanged) for S138" | holds | SOURCES.md:145 (S133) and :150 (S138) carry identical raw sha256 `dd1de0f26536ce…2329`; changelog :172 says the anchor was "re-read in the snapshot whose sha256 dd1de0f2…2329 equals S133's" |

**Housekeeping paragraph (:1783–1788)**

| # | Statement | Verdict | Evidence |
|---|---|---|---|
| 23 | "1846 untrusted attempt-2 files moved out of the lane unread (`/fast/scratch/hyaku/kama-r27/attempt2-untracked-w1-scratch/`)" | holds | `/usr/bin/find /fast/scratch/hyaku/kama-r27/attempt2-untracked-w1-scratch/ -type f \| wc -l` → **1846** (dirs `advice/` + `out/`). "unread"/"untrusted" is an attestation consistent with the untrusted-scratch rule; contents not inspected by design |
| 24 | "three orphan llama-server processes left by attempt-2 seats (ports 47636, 47637, 47644) killed at 07:18Z" | holds (attribution verified; kill instant unrecorded) | w1-controls dispatch assigns port block 47636–47637 to attempt-2 seat `KamaR27A2.CtlLogHelpWarning` and 47644–47645 to `KamaR27A2.CtlEnvPathDecoy` (dispatch.json/dispatched-payload.json). Three w1a3 seats independently recorded exactly those three processes alive: ExecFixtureBoundDemo receipt.log:95–97 (pgrep snapshot: pids 1238214/2205681/3200589, `llama-server -m stories260K.gguf --host 127.0.0.1 --port 47636/47637/47644`, noted as started 05:53–06:15Z — inside the w1-controls wave window 05:41:33Z–06:19:06Z), ReviewCensusStart:5, ExecLiveEchoProbe:115 (~07:11Z). My own `pgrep -af llama-server` now → exit 1 (none): they are gone. The exact "07:18Z" instant has no committed receipt; it sits inside the bounded window alive≈07:11:54Z → c1-tip run ~07:21Z |

## Findings by severity

None. All 24 checked statements hold; append-only is strict for the full range.

## Residual risk and verification gaps

- "killed at 07:18Z" has no committed receipt of the kill itself; bounded by the last observed-alive (07:11:54Z, ExecLiveEchoProbe) and the L1's ~07:21Z c1-tip run. Nothing contradicts it; the window is minutes.
- Orchestrator death at 06:19:06Z rests on a3/plan.json's attestation; a process death cannot be re-observed post-hoc. All committable consequences (zero w1-controls receipts 0ec32cac→52632caa; no data wave) are independently confirmed.
- "unread" for the 1846 scratch files is an attestation by construction; file count and location verified, contents deliberately not opened.
- Phrasing nit in the second correction ("two-step history" for a two-commit narrative) — substantively exact, noted in the table.
- No LSP server applies to this prose-audit lane task; all semantic claims rest on `git diff`/`git show`/`git log`/`git ls-tree` outputs (primary evidence), with text grep used only to locate cited lines, never as semantic proof.
- No installs performed (none needed; pacman transactions paused host-wide per RULES.md). No git/jj writes; all git commands read-only. No llama-server started; `pgrep -af llama-server` shows none of mine at return. Writes confined to this report and `residual/out/ReviewLogSecondCorrection/`; all fixture-writing commands ran under `ulimit -f 1048576`.
