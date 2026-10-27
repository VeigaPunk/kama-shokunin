# R05SourcesGate — S515 reopen and distinct case 13

## S515 canonical source

- URL reopened: https://git-scm.com/docs/git-config#Documentation/git-config.txt-GITCONFIGCOUNT
- Access date: 2026-10-27. Fetched successfully with `curl -L --fail --silent --show-error https://git-scm.com/docs/git-config`; exit 0; 830605 bytes. Snapshot: `.ufo/waves/round-57/sources/git-config-live-2026-10-27.html`.
- Location: `§GIT_CONFIG_COUNT`, anchor `Documentation/git-config.txt-GITCONFIGCOUNT`, lines 5850–5852 of retrieved HTML.
- Located quote (18 words): “all environment pairs GIT_CONFIG_KEY_<n> and GIT_CONFIG_VALUE_<n> up to that number will be added to the process’s runtime configuration”. This is a direct substring after HTML entity decoding; HTML spells the possessive as `process&#8217;s` (U+2019), not ASCII apostrophe.
- Semantics: when `GIT_CONFIG_COUNT` is positive, indexed key/value environment pairs through that count are added to the process runtime configuration; the immediately following source text says pairs are zero-indexed and missing key/value is an error. Round-56 lesson §S515 gives the same 18-word clause and says it adds revision element omitted by S511. It paraphrases the possessive with ASCII apostrophe; underlying source uses typographic U+2019. The claim is otherwise supported.

## Distinct case 13 independent check

Control checked: `.ufo/waves/round-57/controls/freeze.txt` says baseline round-56 no-op C2 reports `met=True exit=0` despite no data execution; amendment clarifies case concerns round-56 `round56-prereg-check.py` matching roster without battery calls. This confirms the frozen control is an actual declared no-op counterexample, not a source/citation assertion. No execution was performed here; this seat's case is source reopening and semantic/citation comparison.

Commands and exact results:

1. `curl -L --fail --silent --show-error https://git-scm.com/docs/git-config > /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-57/sources/git-config-live-2026-10-27.html` — exit 0.
2. `wc -c < .../git-config-live-2026-10-27.html` — `830605`.
3. Read `corpus/lessons/round-56.md` lines 17–19 and `.ufo/waves/round-57/controls/freeze.txt` — S515 quote/anchor/date and no-op receipt declaration match the evidence above.

No tools installed; no shared/source files edited. No judgment or integration performed.
