# R2Restore — round-46 w1, lane kama: restore-claim verification (0718b6ab / 82b5e9d3 / 4a2a4d55) and dd9f5dc6 SCORECARD deletions

**Verdict: HOLDS.** Every line of `LOG.md`, `corpus/QUALITY.md` and `corpus/README.md` present at `0718b6ab^1` is present — multiset-exact and in order — at both `82b5e9d3` and `4a2a4d55d09dfacf83dc62d1b3fddae5f6d2a050` (blobs identical at the two revs). `SCORECARD.md` restores 2428/2429 lines; the single absent line is the round-44 depth row that `82b5e9d3` deliberately re-derived (commit subject: "depth re-anchor"), and the lane's own frozen counter flags exactly this as `0718b6ab SCORECARD partial (2416/2417)`. The 7 round-42 `dd9f5dc6` SCORECARD deletions that never came back are exactly the round-41 head preamble + six round-41 axis rows superseded by round-42 claim C1's head re-derivation; each is documented (citations below). Findings: no High, no Medium, one Low (documentation ambiguity), one observation.

## Method

- Line extraction: `git -C /home/vgpnk/Projects/shokunin/kama-shokunin show <rev>:<path>` (revs resolved: `0718b6ab` = 0718b6abbda6afa6b0ce586f46739fbb92c7cf9c, round-45 truncator; `82b5e9d3` = 82b5e9d33a19734a1f33985acabe7021593e9199, its child (`git rev-parse 82b5e9d3^1` = 0718b6ab…), restorer; `4a2a4d55…`, tip; `dd9f5dc6` = dd9f5dc6c0e63d038bdd070094d7f38290eeee1b, round-42).
- Multiset check: `collections.Counter(old) - Counter(new)` (per-line text, newline stripped; deficit = missing occurrences). In-order check: order-preserving embedding via `difflib.SequenceMatcher(None, old, new, autojunk=False)` — `matched == len(old)` is an existence proof that every old line appears in order; unmatched indices reported when it fails.
- Blobs: `git ls-tree <rev> -- <path>`. Worktree freshness: `git -C <lane> diff --stat 4a2a4d55… -- SCORECARD.md LOG.md corpus/QUALITY.md corpus/README.md` → empty, rc 0.
- Cross-check with the landed frozen tool: `TMPDIR=<scratch> python3 tools/append-only-audit.py --repo <lane> --to 0163fea2dab3f282ebd70c71da9ab5de4cedf733 --json` → **exit 1**, 5 events, byte-agreeing with the preregistration's claim and my independent recompute:
  - `dd9f5dc6 SCORECARD.md deleted=31 restored_at_tip=24 partial restored_by=null`
  - `0718b6ab SCORECARD.md deleted=2417 restored_at_tip=2416 partial restored_by=null`
  - `0718b6ab LOG.md 2290/2290 restored by 82b5e9d3`; `corpus/QUALITY.md 375/375 restored`; `corpus/README.md 663/663 restored`
  (Edit-script deletion counts are smaller than my whole-file line counts — e.g. SCORECARD 2417 vs 2429, LOG 2290 vs 2295 — because the -U0 edit script keeps matching context lines in place; the multiset view is the stricter population. Both agree on the deficits.)

## Part 1 — round-45 restoration claim (0718b6ab → 82b5e9d3 → 4a2a4d55)

| file | lines at 0718b6ab^1 | at 82b5e9d3 | at 4a2a4d55 | blob 82b5e9d3 = blob tip |
|---|---|---|---|---|
| LOG.md | 2295 | 2295/2295 present, in order | identical | 93cc222a4a59 = TRUE |
| corpus/QUALITY.md | 376 | 376/376 present, in order | identical | ffe982635448 = TRUE |
| corpus/README.md | 666 | 666/666 present, in order | identical | 9d9993ee1db3 = TRUE |
| SCORECARD.md | 2429 | **2428/2429** in order; 1 absent | same 1 absent | b1e0318fb949 = TRUE |

**Exact difference (SCORECARD.md, line 16 at `0718b6ab^1`, absent at 82b5e9d3 and at tip):**

```
| depth | **7** | `SKILL.md` sha256 `91440eb8ff4220d647b2b99378a48cb7dc93a3425aedd66ff4ae6f817db4c63b` (1420 lines); run `grep -c '^## ' SKILL.md` → `32`; `corpus/knowledge/endpoint-identity.md` sha256 `0100ac6d…` (218 lines) | score round 1; evidence re-anchored round 44 |
```

`82b5e9d3` inserted instead the re-derived round-45 variant (restore diff line 27; tip `SCORECARD.md:16`):

```
| depth | **7** | `SKILL.md` sha256 `3046955b2fd5140a9439dee7ff1c67d7d03432a4c4ca73870b1393d805ef7297` (1432 lines); run `grep -c '^## ' SKILL.md` → `33`; … | score round 1; evidence re-anchored round 45 |
```

The re-derivation is forced: `82b5e9d3` itself edits `SKILL.md` ("SKILL v2 row flags"), so the round-44 hash would have been stale on a byte restore. Documentation: commit subject 82b5e9d3 ("…; SKILL v2 row flags; **depth re-anchor**"), `LOG.md:2297` ("SCORECARD head re-anchored (banner, calibration row spot-check count 31, depth hash)"), the row's own `evidence re-anchored round 45` cell, and `corpus/lessons/round-45.md` Mistakes row 5 (documents the `open(p,'w').write(open(p).read()+…)` truncation at 0718b6ab and the restore).

## Part 2 — dd9f5dc6 (round-42) SCORECARD deletions: 7 lines not back at the tip

Multiset `Counter(dd9f5dc6^1) - Counter(dd9f5dc6)`: 7 occurrences deleted, 7 distinct, **all 7 absent at 4a2a4d55** (whole-file check; `dd9f5dc6-scorecard-deletions.tsv`). The 24/31 restored occurrences are the round-5-era head lines, which dd9f5dc6 moved verbatim under §Historical head sections — present at tip `SCORECARD.md:147-150` (banner), `:155-158` (Planned), `:166-169` (Retired).

The 7 not-back lines (line numbers at `dd9f5dc6^1`), each a 1:1 replacement in the same commit:

1. `:17` — round-41 reconciliation preamble paragraph.
2. `:21` — operability row (…`report-landing-audit.py --selftest`…, "evidence re-anchored round 41", no pin-watch fact).
3. `:22` — freshness row (no ls-remote drift fact).
4. `:23` — depth row, `SKILL.md` sha256 `151023b9…` (1375 lines), no `grep -c '^## '` run fact.
5. `:24` — coverage row, `PROVINCE.md` sha256 `dbb5f4f7…` (169 lines).
6. `:25` — calibration row (counter = round41 tool; latest closure = round-40 honest stop).
7. `:26` — adjacency row (no pipe-count run fact).

**Are they the head re-derivation round-42 claim C1 made? Yes.** `dd9f5dc6-scorecard.diff` shows each replaced by its round-42 re-derivation: preamble → same text preceded by "Round 42 adds, to every row, one axis-specific run fact (routed defect R41A03 …) and re-anchors the `PROVINCE.md` hash after the round-42 edit."; each row → same row + one axis-specific run fact, "evidence re-anchored round 42" (PROVINCE `dbb5f4f7…169 lines` → `5abc9fdf…181 lines`; depth gains `grep -c '^## ' SKILL.md` → `30` at the unchanged SKILL hash `151023b9`). That is claim C1's declared work: `corpus/lessons/round-42.md:10` ("C1 calibration 7 → 7 — the SCORECARD head and the files that describe the lane (README, PROVINCE) are the lane's standing self-description… `tools/round42-selfdesc-reconcile.py` reads `mismatches=40 met=False` at base `0b606b03`") and `LOG.md:2267` (round-42 C1 bullet: "Round 41's counter covered only the `## Axes` table… The head sections were re-derived from the tree and the round-5 text moved verbatim under §Historical head sections").

**Is each documented? Yes — collectively and 1:1:**

- In-file: tip `SCORECARD.md:10` carries the round-42 preamble sentence and embeds the old round-41 sentence verbatim as a substring; `SCORECARD.md:14-19` are the six superseding rows, each ending `evidence re-anchored round 42`; `SCORECARD.md:6` names the re-derivation tool and the "kept current in rounds 43, 44 and 45" chain.
- Lesson: `corpus/lessons/round-42.md:10` (§Claims C1) and `:50` (Mistakes stale-premise row: "Head sections re-derived and the old text kept verbatim under §Historical head sections; … KQ52 widens KQ49 to the whole head").
- LOG: `LOG.md:2267` (round-42 C1 bullet), `LOG.md:2297` (round-45 head re-anchor, covering the later round-45 depth substitution).
- No line claims the round-41 *rows* are kept verbatim; the verbatim-retention promise (`SCORECARD.md:6`) covers "the round-5 banner and the head sections they replace", and that text is indeed at the tip verbatim. The deletions are deliberate re-derivations under a documented claim, not losses — the frozen counter's `partial (24/31)` is the honest mechanical reading.

## Findings

- **High: none.**
- **Medium: none.**
- **Low (documentation ambiguity), `SCORECARD.md:139`:** "The text below is the lane's head self-description as it stood through round 41, kept verbatim" can be read as including the round-41 `## Axes` rows deleted by dd9f5dc6 — they are not reproduced anywhere in the file (whole-file multiset proof); only banner/Planned/Retired/Saturation/Capabilities are. Proposed fix (unified diff, not applied): `out/R2Restore/proposed-fix-historical-head-wording.diff` — name the reproduced sections explicitly and point at `dd9f5dc6^1` for the round-41 row bytes.
- **Observation (no defect):** `corpus/lessons/round-45.md` Mistakes row 5 says "Restored from `21945c61` plus the appendix in `82b5e9d3`", which reads as a byte restore; for SCORECARD the depth row is a re-derived line, not the `21945c61` bytes. The substitution is nonetheless documented (commit subject "depth re-anchor", `LOG.md:2297`, the row's `re-anchored round 45` cell) and is exactly the 1 line behind the counter's `partial (2416/2417)`.

## Residual risk / verification gaps

- The order-preserving check uses a difflib embedding (existence proof — sound for "all present, in order"); the single SCORECARD absence is established by multiset deficit, which is authoritative for absence regardless of alignment.
- The round-46 C2 checker counter (`tools/round46-append-audit-check.py`) itself was not run here (L1 scope); the cross-check ran the landed audited tool `tools/append-only-audit.py` at 0163fea directly (exit 1, 5 events, matching the preregistration text).
- Lane untouched except `w1/out/R2Restore/` (+ this report); no installs (none needed); no services; no fixture commits; scratch removed at end.

## Artifacts (all under `.ufo/waves/round-46/w1/out/R2Restore/`)

`restoration-analysis.json`, `round42-dd9f5dc6-analysis.json`, `dd9f5dc6-scorecard-deletions.tsv`, `dd9f5dc6-scorecard.diff`, `82b5e9d3-scorecard-restore.diff`, `append-audit-0163fea.json` (+ `.stderr`), `proposed-fix-historical-head-wording.diff`, per-file pre-store/pretip diffs: `LOG.md.prestore-diff.diff`, `LOG.md.pretip-diff.diff`, `corpus__QUALITY.md.prestore-diff.diff`, `corpus__QUALITY.md.pretip-diff.diff`, `corpus__README.md.prestore-diff.diff`, `corpus__README.md.pretip-diff.diff`, `SCORECARD.md.prestore-diff.diff`, `SCORECARD.md.pretip-diff.diff`.
