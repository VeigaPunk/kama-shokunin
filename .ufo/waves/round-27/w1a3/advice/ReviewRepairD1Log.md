VERDICT: partial — the correction entry exists, is genuinely appended (append-only verified 0ec32cac→324d5d62), cites the right commits and times, and correctly diagnoses the false "Before" sentence; but it miscounts the rewrite as "three sentences" where the diff (and its own enumeration) shows four changed, and it omits the intermediate in-place edit `f4066979` from the history it documents.

Scope: round-26 spot-check routed defect 1 — the appended LOG.md entry `## Correction (appended round 27, 2026-10-23) — the round-26 entry was rewritten in place` at LOG.md:1728–1745 (tip 324d5d62e61276af312c8eb42f678004aec245d1). All git commands run read-only in /home/vgpnk/Projects/shokunin/kama-shokunin.

## Append-only check (required output)

```
$ git diff --numstat 0ec32cac09b58a213450ff9f67c319100f21ac27 324d5d62e61276af312c8eb42f678004aec245d1 -- LOG.md
19	0	LOG.md        (exit 0)
$ git log --format='%H %cI %s' 0ec32cac..324d5d62 -- LOG.md
324d5d62e61276af312c8eb42f678004aec245d1 2026-10-23T03:54:43-03:00 round-27: attempt 3 — …   ← the only commit touching LOG.md in range
$ git diff 0ec32cac 324d5d62 -- LOG.md | head -8
@@ -1724,3 +1724,22 @@ …   (3 context lines are the old file's last lines; +19 new lines follow)
$ git show 0ec32cac:LOG.md | wc -l → 1726 ; wc -l LOG.md → 1745 = 1726+19
```

Append-only is strictly confirmed: the single hunk inserts 19 lines after old line 1726 (old EOF), zero deletions; the correction block occupies LOG.md:1727–1745, heading at :1728.

## Commit times

```
$ git show -s --format='%H author=%aI committer=%cI' 7f84cd0e f4066979 fd48f9a3 324d5d62
7f84cd0e author=2026-10-23T00:50:35-03:00 committer=2026-10-23T00:50:35-03:00
f4066979 author=2026-10-23T00:56:41-03:00 committer=2026-10-23T00:56:41-03:00   (uncited by the entry)
fd48f9a3 author=2026-10-23T01:09:37-03:00 committer=2026-10-23T01:09:37-03:00
324d5d62 author=2026-10-23T03:54:42-03:00 committer=2026-10-23T03:54:43-03:00
```

Both times quoted in the entry (00:50:35 -0300, 01:09:37 -0300) match author and committer time exactly.

## Statement table (LOG.md:1728–1745 vs `git diff 7f84cd0e fd48f9a3 -- LOG.md`, 25+/7−)

| # | Statement (LOG.md line) | Verdict | Evidence |
|---|---|---|---|
| 1 | Round-26 entry "starts at LOG.md line 1680" (:1731) | holds | `git show 7f84cd0e:LOG.md \| grep -n '## Round 26'` → 1680; same in current file (:1680) |
| 2 | Entry "landed at 7f84cd0e … is not the text first landed" (:1730–1731) | holds | `git show 7f84cd0e^:LOG.md \| grep -c '## Round 26'` → 0; present at 1680 in 7f84cd0e |
| 3 | Landing time "2026-10-23 00:50:35 -0300" (:1732) | holds | matches %aI/%cI above |
| 4 | "rewritten in place at fd48f9a3 (01:09:37 -0300)" (:1732–1733) | holds but incomplete | fd48f9a3 diff confirms in-place rewrite + time. However the same entry was **also** edited in place at `f4066979` (00:56:41, message "LOG candidate count corrected"): `git diff 7f84cd0e f4066979 -- LOG.md` rewrites the candidates sentence to "executors filed 57 candidate entries … scout listed 8 more, 3 of them not found by an executor". The correction presents a two-commit history for a three-commit history — it omits an in-place edit in an entry whose purpose is exposing in-place edits |
| 5 | "The rewrite changed three sentences" (:1733–1734) | **breaks** | `git diff 7f84cd0e fd48f9a3 -- LOG.md` changes four sentences: (a) "Before … no live error signature" → two-signature account; (b) "found 58 candidates" → 57+8 account; (c) "ports that are now dead" → "registered ports; 34113 does not listen today"; (d) repairs sentence "42 late paths committed (a4a159c3)" → 220/2/1 + 7e5ff9b5 account. The entry's own list (:1734–1738) enumerates exactly these four items — internally inconsistent with "three" |
| 6 | "and appended two paragraphs" (:1733–1734) | holds (nit) | Diff adds "**Counter discrimination (found after data).**" and "**Falsify wave (34 seats).**". Nit: only the Falsify paragraph is appended at end-of-entry; Counter-discrimination is inserted mid-entry before "Motivating evidence" |
| 7 | Before-sentence "no live error signature … became held two live b11755 error signatures" (:1734–1736) | holds | verbatim vs diff hunks @@ -1679,8 +1679,9 @@ |
| 8 | "'58 candidates' sentence became the 57 + 8 candidate account" (:1736–1737) | holds (nit) | cumulative diff matches; "57 + 8" is a paraphrase of "57 candidate entries … scout listed 8". Fine print: the change happened in two steps — f4066979 already wrote "57 … 8 more"; fd48f9a3 reworded to "8, of which 3 no executor found" (see #4) |
| 9 | "ports that are now dead" → "registered ports; 34113 does not listen today" (:1737–1738) | holds (nit) | diff matches; actual new text adds "(8790 and 8791 do)", omitted from the entry's quote |
| 10 | repairs sentence "gained the 220/2/1 file account and 7e5ff9b5" (:1738) | holds | diff: "220 added, 2 modified and 1 deleted round-25 files … committed at 7e5ff9b5" |
| 11 | "Original text: `git show 7f84cd0e:LOG.md`; full change: `git diff 7f84cd0e fd48f9a3 -- LOG.md`" (:1740–1741) | holds | both commands run; second produces the 25+/7− diff reviewed here |
| 12 | "The current text is the corrected one" (:1741–1742) | holds | fd48f9a3 blob 28ed1c1 == 0ec32cac blob; sole later change is the +19/−0 append — entry bytes unchanged since fd48f9a3 |
| 13 | "the original 'Before' sentence was false (base SKILL.md held the `Loading model` 503 and the `Context size has been exceeded.` 500)" (:1742–1743) | holds | `git show 1560e4d8:SKILL.md` (counter's stated base) and `git show 7f84cd0e^:SKILL.md` both contain `Loading model` 503 row at :518/:523 (under "## Round-16 verdict vocabulary…" :509) and `Context size has been exceeded.` 500 at :689 (under "### Round-25 decision rows…" :677) |
| 14 | "Routed by corpus/lessons/round-26-verifier-spotcheck.md defect 1" (:1743–1744) | holds | spotcheck :233 routes exactly this repair ("Append a LOG.md correction entry that points at the round-26 entry rewritten in place at fd48f9a3 (it superseded the 7f84cd0e text)") |
| 15 | "From this round on a LOG correction is a new appended entry like this one, never an in-place edit" (:1744–1745) | holds | matches defect-1's "appended, never rewritten in place"; self-consistent — this entry itself is appended (append-only check above) |
| 16 | Heading "(appended round 27, 2026-10-23)" (:1728) | holds | landed in 324d5d62 (2026-10-23T03:54:43-03:00), commit message "round-27: attempt 3" |

## Findings

1. **Wrong count in the correction's own accounting (statement #5).** "changed three sentences" vs. four changed sentences in the cited diff — and the entry enumerates all four in the next lines. For an artifact whose only job is accurate accounting of a stealth rewrite, this is a real defect, not a style nit.
2. **History omission (statement #4).** The round-26 entry was edited in place twice: `f4066979` (candidates sentence) and `fd48f9a3` (rest). The correction names only fd48f9a3. The routed defect (:233) names only 7f84cd0e→fd48f9a3, so the letter of the repair is satisfied — but a correction whose thesis is "the landed text was silently rewritten" understates the rewrites by one commit, and consequently mis-describes the candidates sentence as a single-step change (#8 fine print).

## Residual risk / verification gaps

- Whether the new factual claims inside the correction's *content* (e.g., "57 + 8", 220/2/1, "34113 does not listen today") are true is out of this seat's scope — I verified only that the correction entry's description of the diff matches the diff, plus commit times and the false-"Before" diagnosis.
- The "never an in-place edit" policy is stated but unenforced; nothing prevents a future round violating it. [INFERENCE]

No installs performed (none needed; pacman transactions paused host-wide per RULES.md). No live server started; no git/jj writes; all commands read-only under the lane repo.
