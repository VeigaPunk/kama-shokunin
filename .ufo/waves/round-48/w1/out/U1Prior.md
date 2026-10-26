# U1Prior report

Verdict: no primary source scopes append-only to document sections, and `git blame --reverse` closes neither named blind spot; the Go generated-header idiom (regex plus position) is the one transferable technique, giving two round-49 candidates (`preamble=<regex>`, `marker=<regex>` on `exempt=`).

Evidence and sources: see `.ufo/waves/round-48/w1/out/U1Prior/prior.md` (5 located quotes: pkg.go.dev cmd/go generated-code rule, git-blame `--reverse`, gitattributes xfuncname + merge=union, Keep a Changelog 1.0.0 FAQ, towncrier tutorial).

Observed (new vs the L1 list): at the unmodified v3 tool, a scratch fixture replacing an exempt `## Axes` section's 30 lines with 30 `JUNK n` lines gives `deleted=30 graded=0 ungraded=30 ... bad_declarations=0`, exit 0 (`out/U1Prior/demo-junk.txt`, rerun with `out/U1Prior/fixture.sh`). Exempt eligibility is a line-count test only (tools/append-only-audit.py:409-411). Preamble (section None): `exempt=` cannot name it; `only=` skips it silently (tools/append-only-audit.py ~415); build workaround is the appended banners at SCORECARD.md:2736.
Inferred, not run: `sections()` (line 231) is fence-blind.
Search gap: two web searches for a changelog-immutability linter returned only synthesized prose; not cited.

No tools installed. Scratch removed.

Written:
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/U1Prior.md
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/U1Prior/prior.md
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/U1Prior/demo-junk.txt
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/U1Prior/fixture.sh

Note: demo-junk.txt came from an equivalent python-built fixture; fixture.sh is a shell transcription of it and has NOT been run.
