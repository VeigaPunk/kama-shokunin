# R57Item13SourceAudit — distinct case 34 evidence

Case 34 = re-open S515 and verify the runtime Git environment-pair claim. This file is the separate
evidence record required for that case; it tests the assignment independently of the seat narrative
in `R57Item13SourceAudit.md`.

## Instrument

`measured/R57Item13SourceAudit/audit-s515.py` — parses the S515 row out of `corpus/SOURCES.md`,
fetches the canonical URL (or opens a saved page), locates
`id="Documentation/git-config.txt-GITCONFIGCOUNT"`, extracts the sentence from “all environment
pairs” through “runtime configuration.”, apostrophe-normalizes both sides, compares the quote and
re-counts words against the row's declared count. It has no expected literal for the quote and no
expected literal for the count, so it can fail.

## Positive runs

```
python3 audit-s515.py --registry <lane>/corpus/SOURCES.md                    # live fetch
# exit 0: page_sha256=706b1566…, anchor_present=True, revision_marker=True,
#         registry_words=18, located_words=18, word_count_matches=True,
#         within_25_words=True, quote_matches=True, verdict=PASS
# receipt: receipts-s515-main.out

python3 audit-s515.py --registry <lane>/corpus/SOURCES.md \
  --page <lane>/.ufo/waves/round-57/sources/git-config-live-2026-10-27.html
# exit 0; same field values; verdict=PASS
# receipt: measured/R57Item13SourceAudit/case34-snapshot.out
```

The saved page used in the second run is byte-identical to this seat's own fetch
(`cmp` exit 0; `sha256 706b1566467e9cd8c6cdda853a5fc82118a48fde3119777d18cefc014bcd3d5a`), so the
two positive runs are the same bytes through two code paths (live fetch vs saved page).

## Controls — each must fail

| Control | Invocation | Observed | Exit |
|---|---|---|---|
| Quote mutation (`runtime`→`system` in the registry row) | `audit-s515.py --mutate` (and `--registry registry-quote-mutant.md`) | `quote_matches=False`, `verdict=FAIL` | 1 |
| Word mutation (`will be added`→`will not be added`) | `--registry registry-word-mutant.md` | `quote_matches=False`, `verdict=FAIL` | 1 |
| Count mutation (`(18 words)`→`(19 words)`) | `--registry registry-count-mutant.md` | `registry_words=19`, `located_words=18`, `word_count_matches=False`, `verdict=FAIL` | 1 |
| Wrong page (git(1) manual, no GIT_CONFIG_COUNT anchor) | `--page .ufo/waves/round-56/sources/git-docs-git.html` | `anchor missing` | 1 |

Receipts: `receipts-s515-mutant.out`, `ctl_registry-quote-mutant.md`, `ctl_registry-word-mutant.md`,
`ctl_registry-count-mutant.md`, `case34-quote-mutant.out`, `case34-count-mutant.out`,
`case34-wrong-page.out`; the mutated registry copies are `registry-{quote,word,count}-mutant.md`.

The quote control shows that a one-word change in the registry row alone flips the verdict — the
instrument is bound to the row's bytes, not to a satisfying literal. The wrong-page control shows
the anchor/location check is live rather than always-true.

## Case verdict

S515 re-derives: anchor present, quote exact after apostrophe normalization, 18 words (≤25),
revision marker `git-config last updated in 2.56.0`, page bytes stable across two fetches and equal
to the committed round-56 snapshot. Runtime semantics were separately exercised on host
`git version 2.56.0` (nine cases, `runtime-git-env-pairs.out`): pairs inject runtime config (exit 0),
env overrides config file (exit 0), `git -c` overrides env (exit 0), missing value errors (exit 128),
empty/zero count adds nothing (exit 1). Case 34: **PASS**, with all four controls failing as
required.

Authorities: `corpus/SOURCES.md:268`; `corpus/lessons/round-56.md:18`;
`corpus/lessons/round-56-verifier-spotcheck.md:33`; live URL
`https://git-scm.com/docs/git-config#Documentation/git-config.txt-GITCONFIGCOUNT`, accessed
2026-10-27T18:07:56Z / 18:09:37Z.

Bindings: this seat wrote only
`.ufo/waves/round-57/w1/out/R57Item13SourceAudit.md`, this file,
`.ufo/waves/round-57/sources/R57Item13SourceAudit-gitconfig-env-section.txt`, and
`.ufo/waves/round-57/measured/R57Item13SourceAudit/`. No shared file edited, no commit/push.
