# Report — ScribeSrcPrettyFormats

## Behavior and gate

Opened the official Git pretty-formats page and saved the fetched bytes as `page.html`. Its PRETTY FORMATS placeholders state `%ct` as `committer date, UNIX timestamp` and `%cI` as `committer date, strict ISO 8601 format` (saved-page lines 2840–2850; located by `#ct` and `#cI`). The round-29 frozen C1 counter uses `git show -s --format=%ct` for W's committer time (`.ufo/waves/round-29/count-c1.py:110–112`); the counter docstring describes the time check at lines 25–26. The one located quote (two exact spans, 10 words total) is recorded in `quote.txt`; the Gate line with URL, UTC access time, and locations is in `row.md`.

The proposed S177 has the existing 11-column SOURCES shape, official-docs tier A, opened date 2026-10-23, and on-release recheck. `CORPUS.md` §“SOURCES.md — where a shokunin learns” defines tier/status/used-by and Gate requirements (lines 86–115); `corpus/SOURCES.md` header and latest row (S173) confirm the table shape. Existing S073 already teaches `%ct` as a UNIX timestamp; S177's additional value is the official pretty-formats `#cI` strict-ISO definition. The proposal is currently `queued` with `used-by —`: peer `KamaR29.ScribeKnowledgeEntry` identified `.ufo/waves/round-29/w1/out/ScribeKnowledgeEntry/self-assessment-at-writing.md` as the intended use-by path, but reading that path returned “not found.” I did not report an unobserved citation as mined. The local counter uses `%ct`; `%cI` is included only to document the strict ISO form distinction.

## Commands and outcomes

- `timeout 10s mkdir -p /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/w1/out/ScribeSrcPrettyFormats` — completed with no output.
- `timeout 75s sh -c 'timeout 60s curl -sSfL https://git-scm.com/docs/pretty-formats -o /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/w1/out/ScribeSrcPrettyFormats/page.html && sha256sum /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/w1/out/ScribeSrcPrettyFormats/page.html && date -u +%Y-%m-%dT%H:%M:%SZ'` — succeeded; SHA-256 `fac8765c2ea1925a60f999799056c8ab58688ad51140d20f5f5125e9577efc5d`; UTC access time `2026-10-23T12:02:47Z`.
- `timeout 10s git --version` — `git version 2.56.0`.
- `timeout 20s man -P cat git-pretty-formats > /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/w1/out/ScribeSrcPrettyFormats/installed-man.txt` — exit 16, `No manual entry for git-pretty-formats`; shell redirection created the capture file but no manual text was returned.
- `read /usr/share/doc/git` — path not found. Thus neither queried local-manual location supplied a local text match; the official fetched page did.
- `timeout 10s mkdir -p /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/w1/advice` — completed with no output.

## Surfaces, limits, and out of scope

Files created only in the authorized output/advice paths: `page.html`, `installed-man.txt`, `row.md`, `quote.txt`, `REPORT.md`, and `.ufo/waves/round-29/w1/advice/ScribeSrcPrettyFormats.md`. No tracked lane file was edited; no C1 correction/data row was written. No tools were installed and no tests/builds were run. The web page is live and not pinned to a Git source commit; its bytes are identified by the hash above. Local installed-manual equivalence could not be checked because the man entry and `/usr/share/doc/git` path were unavailable.
