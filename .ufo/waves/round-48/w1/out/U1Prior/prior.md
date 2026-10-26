# U1Prior - prior art for region-scoped append-only checks (round 48)

Verdict: no tool found scopes "append-only" to document sections; the primary sources give only path-level or positional/marker idioms. v3's section-graded, window-maximised multiset audit is not a copy of anything found. Two idioms are worth borrowing for the two named blind spots: a **marker-bound, position-bound eligibility rule** (Go generated-file header) for the preamble banner, and **structural supersede-don't-delete** (Keep a Changelog `[YANKED]`, towncrier fragments) which the build already uses for the banner. `git blame --reverse` closes neither.

## Primary sources (quotes <= 25 words; located)

1. Go, `cmd/go` "Generate Go files by processing source" - https://pkg.go.dev/cmd/go#hdr-Generate_Go_files_by_processing_source (text line 1312-1314 of fetched page)
   - "generated source should have a line that matches the following regular expression ... ^// Code generated .* DO NOT EDIT\.$"
   - "This line must appear before the first non-comment, non-blank text in the file."
   -> how generated header is recognised: by content (regex) AND position (before first real text), independent of the header's wording changing per regeneration.
2. git-blame manual - https://git-scm.com/docs/git-blame (OPTIONS, `--reverse`; DESCRIPTION)
   - "Instead of showing the revision in which a line appeared, this shows the last revision in which a line has existed."
   - "The report does not tell you anything about lines which have been deleted or replaced; you need to use a tool such as git diff or the 'pickaxe'"
   -> per-line identity tracked forward over `<start>..<end>`; `-L :<funcname>` restricts to a range.
3. gitattributes (custom hunk header) - https://git-scm.com/docs/gitattributes#_defining_a_custom_hunk_header
   - "you can use a customized pattern to make a selection" ; `diff.<name>.xfuncname` "a regular expression that matches a line that you would want to appear as the hunk header"
   -> git already supports "section = last line matching a heading regex" (the `## ` rule v3 hand-implements in `sections()`), and, in the same file, `merge=union`: "take lines from both versions, instead of leaving conflict markers" - git's only built-in append-only-ish policy, scoped by path, not by section.
4. Keep a Changelog 1.0.0 FAQ - https://keepachangelog.com/en/1.0.0/
   - "Keep an Unreleased section at the top to track upcoming changes." (the one editable region; history below it is the frozen part)
   - Yanked releases: "They should [appear]." shown as `## [0.0.5] - 2014-12-13 [YANKED]` - a correction is an annotation on the old heading, not a deletion.
   -> the format names an editable head region and annotate-don't-delete corrections (v3's `A-corr`), but ships no linter; it is a format, not an enforcement.
5. towncrier tutorial - https://towncrier.readthedocs.io/en/stable/tutorial.html
   - "look into './changes' for news fragments and write them into './NEWS.rst'" -> the generated file is output of append-only fragments; the generated file itself is not the source of truth.

Search gap (observed): two web searches for a CI "changelog history unchanged" guard returned only synthesized how-to prose (a base-sha `endswith(history)` suffix check, first-release-heading boundary read from the BASE file) and no primary linter; I do not cite them as sources. The suffix idea is recorded below only as an idea. No keep-a-changelog linter with immutability scoping was found in primary docs.

## How these treat regenerated headers

- Go: header identified by regex + position; its text may change every regeneration; never diffed. (Eligibility is content-bound and positional.)
- Keep a Changelog: head `[Unreleased]` is rewritten at every release by design; frozen region is everything below.
- towncrier: header regenerated wholesale because the file is derived output.
- git blame --reverse / pickaxe: no notion of regenerated header; a rewritten line is a deletion plus a new line.

## What v3 does differently (read from tools/append-only-audit.py)

- Scope is declared in a contract cell and bound to the lane's own declaring line (`binds()`); the sources above scope by path, regex or convention.
- Section = last `## ` line before a deleted line, taken at the parent position (`sections()`, line 231); equivalent to git's xfuncname idea but per line, so a hunk spanning two sections is attributed correctly (git's hunk header names only the section before the hunk's first line - [INFERENCE] from the gitattributes text).
- Restoration is a content multiset maximised over the event window, not line identity; blame --reverse is line identity and cannot call an identical re-added line a restoration.
- Exempt eligibility is a size test: `max over window count(T,x) >= count(T,parent)` (lines 409-411).

## Blind spots and whether any technique closes them

1. Content-blind eligibility. Demonstrated (unmodified tool, scratch fixture, `demo-junk.txt`, fixture.sh): replacing the 30 lines of an exempt `## Axes` with 30 lines `JUNK n` reports `deleted=30 graded=0 ungraded=30 ... status=ungraded`, `bad_declarations=0`, exit 0. Only a shrink is graded (the gutting case). Closes?
   - blame --reverse: no. It reports the commit that removed each line; it does not judge replacement content. Could only serve as a second, line-identity cross-check of D.
   - Go-style marker rule: yes, partially. Add an optional `marker=<regex>` to `exempt=`: a title stays eligible only if its section at x keeps its heading line and >=1 line matching the marker (for Axes, the `| axis |` table row shape; for banner, `^\*\*Current authority \(round \d+\)`). Stops junk padding, not an adversary who keeps the marker. Cost: one regex per row and a counter change (the C1 counter is frozen for round 48; this is a round-49 candidate).
   - Honest limit: SCORECARD.md:6 declares those sections re-derived in place, so arbitrary content change is allowed by policy; only "not gutted" is defensible, and a size test is a proxy for that.
2. Preamble banner (section None). v3 can neither exempt nor grade it consistently: `exempt=` names only `## ` titles, so line 6 was graded and regressed at base; `only=` skips `s is None` (line ~415) so the preamble is silently ungraded under `only=`. Closes?
   - Go-style positional region: yes. Add `preamble=<regex>`: lines before the first `## ` matching the regex are ungraded while >=1 matching line remains ("must appear before the first non-comment, non-blank text" is the same shape). This would let the banner be rewritten in place and remove the build's workaround of appending the r45/r46 banners at `SCORECARD.md:2736` (### Superseded head banners), which grows the file by a banner per round.
   - Keep a Changelog / `[YANKED]` style: that is what the build did (supersede, keep verbatim); sound for append-only, costs growth, and passes the frozen C1 counter.
   - blame --reverse / `git log -S`/`-G` pickaxe: no. Pickaxe finds when a banner string changed but cannot say it is allowed.
3. Fence-blind sections (code read, not run): `sections()` starts a section at any line beginning `## `, including inside a fenced code block, so a fenced `## Axes` example could re-scope lines. Not tested; marked [INFERENCE]. Remedy: track fence toggles; no cited source needed.

## Idea only (not cited, not run)

Freeze-boundary read from the base: a guard that reads the protected suffix from the BASE blob, not the new one, so editing a heading cannot move the boundary. v3's window/parent-position design already measures against the parent, so it is not needed; the point stands for any future `preamble=`/`marker=` row: bind the regex at the parent commit.

## Files
- demo-junk.txt, fixture.sh (this directory)

Note: demo-junk.txt came from an equivalent python-built fixture; fixture.sh is a shell transcription of it and has NOT been run.
