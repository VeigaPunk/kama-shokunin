# S01SourcesReopen — distinct case 6 evidence

Independent test of the assigned case: *open S515 from the lane lesson, verify the located
quote is under 25 words, report access date and source location*. Run separately from the
report narrative; script and raw outputs are in
`.ufo/waves/round-57/sources/S01SourcesReopen/`.

- Verifier: `S01SourcesReopen/s515_reopen_check.py` (Python 3.14.8, stdlib only).
- Inputs: the fetched page bytes, plus the lane's own `corpus/SOURCES.md` S515 row and the
  round-56 lesson S515 bullet (read-only). The verifier never reads a self-description as
  evidence: every content check is against the page's parsed `ENVIRONMENT` /
  `GIT_CONFIG_COUNT` definition and the page's own revision marker.
- No lane file was written. Working copy: `/fast/scratch/hyaku/kama-r57/S01SourcesReopen/`.

## Base checks (live page, 2026-10-27, HTTP 200)

Command: `python3 s515_reopen_check.py --html git-config-live.html --label live-2026-10-27`
→ **exit 0**, `run-live.out`:

```
sha256=706b1566467e9cd8c6cdda853a5fc82118a48fde3119777d18cefc014bcd3d5a bytes=830605
check=anchor_present ok=True detail=id=Documentation/git-config.txt-GITCONFIGCOUNT
check=dt_names_config_count ok=True detail=dt text == GIT_CONFIG_COUNT
check=quote_in_git_config_count_dd ok=True detail=occurrences=1
check=quote_word_count_matches_declared ok=True detail=declared=18 counted=18
check=quote_word_count_under_limit ok=True detail=counted=18 limit=25
check=revision_marker_present ok=True detail=marker=git-config last updated in 2.56.0
check=lesson_quote_agrees_with_registry ok=True detail=lesson_words=18
check=url_matches_expected_anchor ok=True detail=https://git-scm.com/docs/git-config#Documentation/git-config.txt-GITCONFIGCOUNT
```

Same command over the committed round-56 snapshot
(`--html .ufo/waves/round-56/sources/git-docs-git-config.html --label round56-snapshot`)
→ **exit 0**, identical 8/8 checks (`run-snapshot.out`); the fetched bytes are identical
(`cmp` exit 0, same sha256), so the round-56 snapshot is a faithful copy of today's page.

## Controls that must be red (the check cannot pass a no-op)

| Control | Result | Receipt line |
|---|---|---|
| insert one word into the quote | rejected | `mutant_insert_word applied=True rejected=True failed_checks=quote_in_git_config_count_dd` |
| reorder a clause of the quote | rejected | `mutant_reorder_clause applied=True rejected=True failed_checks=quote_in_git_config_count_dd` |
| replace the `GIT_CONFIG_COUNT` definition with “no pairs are processed.” | rejected | `mutant_blank_dd applied=True rejected=True failed_checks=quote_in_git_config_count_dd` |
| delete the whole `GIT_CONFIG_COUNT` group | rejected | `mutant_drop_section applied=True rejected=True failed_checks=anchor_present,dt_names_config_count,quote_in_git_config_count_dd` |
| 26-word quote against the ≤25 limit | rejected | `control_word_limit_26 rejected=True counted=26 limit=25` |
| wrong page (git(1) manual instead of git-config(1)) | rejected | `run-wrong-source.out`: anchor/dt/quote/revision `ok=False`, `met=False`, **exit 1** |

Summary from `run-live.out`: `base_checks_ok=True`, `mutants_rejected=4/4`, `met=True`,
exit 0. `applied=` is asserted per mutant because an unapplied mutation and a passing check
look the same (the round-56 C2 no-op failure mode; see report §Calibration).

## Falsifiers

The case would fail — and the verifier would print `met=False` with a non-zero exit — if any
of these held: HTTP non-200 or an empty/short page; the anchor id absent or duplicated; a
different `dt` name; the quoted sentence absent, reworded, or occurring more than once in the
definition; a declared word count that disagrees with the counted words; more than 25 words; a
missing `git-config last updated in 2.56.0` marker; or disagreement between the lesson quote
and the registry quote (after quote-glyph normalisation).

## Reported facts (case answer)

- Access date: **2026-10-27** (HTTP `date: Tue, 27 Oct 2026 18:07:05 GMT`).
- Source location: **§`ENVIRONMENT` / `GIT_CONFIG_COUNT`** on
  https://git-scm.com/docs/git-config#Documentation/git-config.txt-GITCONFIGCOUNT, anchor id
  unique, next section `EXAMPLES`; page revision `2.56.0` (dropdown date `2026-09-28`).
- Located quote: **18 words** (≤25), verbatim apart from the ASCII/U+2019 apostrophe
  transcription noted in the report.
