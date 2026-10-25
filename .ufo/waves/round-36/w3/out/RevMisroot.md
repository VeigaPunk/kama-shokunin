# RevMisroot — untracked fleet-root files vs "kama" / "round-36"

Seat: round-36 / wave 3 / RevMisroot (kama lane, leaf, no subagents). Date: 2026-10-24.
Scope: exactly the commanded enumeration — `git -C /home/vgpnk/Projects/shokunin status --porcelain`
— then first 40 lines of every untracked (`??`) file it lists. Read-only session: only reads at
the fleet root plus this one report write inside the lane. Nothing moved, copied, deleted,
staged, or committed.

## Measured results

Enumeration (measured, both plain `--porcelain` and `--untracked-files=all`; the two lists are
identical, so there are no untracked directories to expand — all 18 entries are files):

```
?? .omp/mcp.json
?? .ufo/reports/round-34/mado.md
?? .ufo/reports/round-50/kake.md
?? .ufo/state/kotoba.report-baseline
?? .ufo/state/kotodama.report-baseline
?? .ufo/state/revenger.report-baseline
?? bm.json
?? live.html
?? live_s228.html
?? nama.html
?? s395.txt
?? scripts/hyaku/append-closure.py.bak-20261023T040735Z
?? scripts/hyaku/fleet-commit.sh.bak-20261023T040735Z
?? tf_bavelas.html
?? unblob.log
?? wb2.html
?? write
?? xc.xml
```

Trigger check (measured two ways, both case-insensitive count via
`head -n 40 <file> | grep -icE 'kama|round-36'` and my direct read of the first 40 lines of
each file; all reads returned complete ranges, no truncation):

| File | first-40-lines names `kama` or `round-36`? |
|---|---|
| .omp/mcp.json | No (name-only ripgrep scan, see gaps) |
| .ufo/reports/round-34/mado.md | No — names round-32/33/34 and mado-shokunin only |
| .ufo/reports/round-50/kake.md | No — names round-49/50 and kake-shokunin only |
| .ufo/state/kotoba.report-baseline | No — `<n> e3b0c442...` baseline line |
| .ufo/state/kotodama.report-baseline | No — same shape |
| .ufo/state/revenger.report-baseline | No — same shape |
| bm.json | No — Cloudflare challenge page, cZone www.britishmuseum.org |
| live.html | No — National Museum of Ireland collections page |
| live_s228.html | No — Anubis challenge page, OpenEdition |
| nama.html | No — namuseum.gr 404 page |
| s395.txt | No — 0 bytes, 0 lines |
| scripts/hyaku/append-closure.py.bak-20261023T040735Z | No — hyaku closure helper backup |
| scripts/hyaku/fleet-commit.sh.bak-20261023T040735Z | No — hyaku fleet-commit backup |
| tf_bavelas.html | No — Cloudflare challenge, www.tandfonline.com DOI page |
| unblob.log | No — unblob extraction log over /tmp/test-fw.bin |
| wb2.html | No — Wayback Machine abuse-block notice |
| write | No — single line `agent://U100N079H334f935b` |
| xc.xml | No — Perseus "Too many requests" page |

Mechanical cross-check printed `0` for all 18 files.

**Answer to the trigger — Report any file that names kama or round-36: none.** Zero of the 18
untracked fleet-root files name `kama` or `round-36` in their first 40 lines. No file path or
directory in the untracked set carries either string either (round-34 and round-50 are adjacent
rounds, not round-36).

## Findings by severity

- **Trigger findings: none.** No untracked fleet-root file meets the kama/round-36 naming
  condition in its first 40 lines.
- **Info (anomaly, out of trigger):** fleet-root file `write` holds the single line
  `agent://U100N079H334f935b` — an agent-URI stranded as a file, consistent with a mis-redirected
  shell write by some session (message target landed as `> write` instead of being delivered).
  It does not name kama or round-36, so it is not a trigger hit; recorded as evidence
  (`head -n 1 write`) and left untouched per bounds. I did not act on the URI.
- **Info (scope honesty):** the tracked-and-modified `.ufo/state/kama.report-baseline`
  (status ` M`) does contain "kama" in its status line but is not untracked, so it is outside the
  commanded population. Mentioned only so the negative result is not misread as "no kama string
  anywhere in status output".

## Residual risk and verification gaps

- Population is defined by the commanded `--porcelain` semantics: gitignored paths
  (including the nested `*-shokunin/` lane repos, gitignored per fleet AGENTS.md) are outside it
  by construction. No claim is made about ignored files.
- `.omp/mcp.json` was not content-dumped (bounds: never read secrets/credentials). Its answer
  rests on a ripgrep name-match scan (`kama|round-36`, no match). That is a literal text search
  over the whole file — recorded as such, not semantic proof — and it covers strictly more than
  the first-40-line scope. The Grep tool reported "No non-sensitive matches found".
- The grep cross-check was case-insensitive; my direct reads also confirm zero case-sensitive
  occurrences in every captured first-40-line byte range, so the negative holds both ways.
- Single-line minified captures (bm.json, tf_bavelas.html) were each fully captured in one line,
  so "first 40 lines" equals the whole file for them; no residual unread bytes affect the verdict.
- No mutation performed anywhere; fleet root touched only by `git status --porcelain`,
  `git status --porcelain -untracked-files=all`, `git rev-parse --show-toplevel`, reads, and
  `head|grep` pipes. No git-mutating or jj command was run.
