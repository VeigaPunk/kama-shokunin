# RecallA — extractor recall, SCORECARD.md lines 1–720

Window: `SCORECARD.md` at base `2aa46e2481d2ec41a7ee5ed793fc50ae967a6e5d`, lines 1–720 only. Extractor: frozen `count-c1.py` (`--list --tip 2aa46e24`). No tools installed.

## Totals

| | n |
|---|---|
| Extractor statements in this window | 20 (of 69; all 69 are in SCORECARD.md; SHONEN.md contributes 0) |
| Missed statements (this list) | 32 |
| Of which hold at W | 31 |
| Of which do not hold at W | 1 |
| Extracted P/H/N bound to the wrong path | 0 |

By class missed: Q 15, C 9, H 5, T 3, N 0, P 0.

The one that does not hold: line 41, Q `` `file=yes` ``, W `ea72c3eae4ecc68dab2b0a08153c9c1d2e16df21`. `git grep -F -e file=yes` at W hits only `LOG.md` and `SCORECARD.md`, both excluded by the frozen Q check. These misses are limits of the frozen extractor; they are not counted.

Rows: `missed.json` (`line`, `class`, `text`, `W`, `holds`, `evidence`). W is `git blame --line-porcelain` of that line at the base. `holds` uses the frozen class check (C strict ancestor, H digest, T committer time, Q `git grep -F` with the frozen excludes).

## Why the extractor drops them

- **C.** `measured_cells` only takes a line that is exactly `Measured commit:` or that table column. `RE_CWORD` needs the cue word, a space, then the hex on the same line. Dropped: `commit:` / `revision:` with a colon (259, 313, 436, 712), `revision is \`hex\`` (295, 296), a cue on the previous line (411, 516), and `pinned to \`hex\`` with no cue word (488). All nine tokens are commits and strict ancestors of their W.
- **H.** `RE_HN` only binds `` `path` md5|sha256 <hex> `` with the path immediately before a lowercase algorithm word. Dropped: an unbound md5 (199; the hex equals `md5(tools/kama-probe.sh)` and not the registry or `test-snapshot.sh`), `SHA-256` of the corpus split across 447–448 (equals `sha256(tests/ollama-evidence/cases.json)`), and ellipsis abbreviations (610 set sha256 `bf9068d8…1f32`; 683 probe `36b64978…` and matrix `bf9068d8…`). The set digest recomputed from `measure.py` `matrix_digest` (sorted `name sha256\n` of `tests/probe-verdicts/*.json`) is `bf9068d89e4cb8a080167cb32cc818943d717a65fcbd21edb2b8256e22771f32` at both W. The probe prefix is `sha256(tools/kama-probe.sh)`, not the md5.
- **T.** `RE_T` is `YYYY-MM-DD` plus `T`/` ~`/`T~` and a colon clock ending in `Z`. Dropped compact stamps `20261014T124232Z` (lines 20 and 569) and `20260929T043044Z` (line 20). All three are at or before W's committer time. The line-20 stamps sit inside a Q span the extractor did extract.
- **Q.** A backtick needs a digit and either `=` or a space plus one of `met|registered|counted|stale|observed|verified|RESULT`. Dropped quoted results that fail that filter. Fourteen hold in some non-excluded blob. Line 41 does not.
- **N, P.** No missed line-count of a named file, and no missed in-lane `path:L` / `path:L-M`. The extracted bindings in this window match the path written beside the token: line 19 `tools/kama-probe.sh` (H and N), line 20 `tools/test-snapshot.sh` (H), line 21 `SKILL.md` (N), line 192 `MISSION.md:29` (P), line 654 `SKILL.md:533` (P).

## Looked at and not listed

- `` `../shokunin.conf:52` `` at lines 285, 342, 561. Real `path:L`, but the frozen class rejects a path starting `../`. Not an in-lane miss.
- Line 597 `704366d76` after `llama.cpp code at`. Not a lane commit; the extractor's 40-character upstream screen (`llama.cpp`) would drop it anyway.
- Heading dates `(2026-10-18)` and the like have no clock. Not class T.
- `ls … | wc -l` results (lines 197, 212) count names, not lines of one file. Not class N.
- Bare or very common backticks, where a Q hit would not mean this measurement: `` `true` `` (323), `` `clean` `` (320), `` `VALID` `` (611, 681, 685). Frozen grep hits 43, 62, and 38–73 files. Verdict identifiers (`FOREIGN_SERVICE`, `non-2xx-non-model-http`, `MODEL_LOADING`, `llamacpp-loading`) are names, not a run's output span.
- Commands, paths, and hexes already classed as C or H are not also Q.
