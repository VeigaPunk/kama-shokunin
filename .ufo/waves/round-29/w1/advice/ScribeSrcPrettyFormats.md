# ScribeSrcPrettyFormats — scoped findings

- Fetched `https://git-scm.com/docs/pretty-formats` with `timeout 60s curl -sSfL ...`; saved bytes: `.ufo/waves/round-29/w1/out/ScribeSrcPrettyFormats/page.html`, SHA-256 `fac8765c2ea1925a60f999799056c8ab58688ad51140d20f5f5125e9577efc5d`, UTC access `2026-10-23T12:02:47Z`.
- Saved page at PRETTY FORMATS anchors `#ct` and `#cI`: `%ct` text is “committer date, UNIX timestamp”; `%cI` text is “committer date, strict ISO 8601 format.” C1 counter line 111 uses `git show -s --format=%ct`; quote file has one 10-word ellipsis quote with both exact spans.
- `CORPUS.md` §“SOURCES.md — where a shokunin learns” lines 86–115 provided the tier/status/used-by and Gate rules; lane `corpus/SOURCES.md` lines 11–12 and last row S173 confirmed the table form. Existing S073 already documents `%ct` as a UNIX timestamp; S177 adds the pretty-formats `#cI` strict-ISO definition.
- Local `git --version` returned `git version 2.56.0`. `timeout 20s man -P cat git-pretty-formats` exited 16 with `No manual entry for git-pretty-formats`; read of `/usr/share/doc/git` returned path not found. No local manual text match was verified.
- Proposed row is in `row.md`. It remains queued / `used-by —` because the intended peer draft `.ufo/waves/round-29/w1/out/ScribeKnowledgeEntry/self-assessment-at-writing.md` was not found when read. Do not count the planned citation as mined until it exists and cites S177.
- No product files, counter data rows, tests, or installed tools were changed/run. Web documentation is live and not pinned to a source commit; saved hash preserves the bytes inspected.

Artifacts: `.ufo/waves/round-29/w1/out/ScribeSrcPrettyFormats/{page.html,installed-man.txt,row.md,quote.txt,REPORT.md}`; `.ufo/waves/round-29/w1/advice/ScribeSrcPrettyFormats.md`.
