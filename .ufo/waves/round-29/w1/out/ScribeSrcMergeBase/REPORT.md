# ScribeSrcMergeBase — C1 source evidence

## Axes
- Calibration: source provenance for the Git exit-status behavior consumed by the frozen round-29 C1 counter. This is documentation evidence, not a measurement of the C1 result.

## Behavior and findings
- Opened and saved the official manual at `https://git-scm.com/docs/git-merge-base` as `page.html`; it identifies the `--is-ancestor` mode and says status 0 when the first commit is an ancestor of the second, status 1 when not, and another nonzero status for errors.
- The saved online page says `git-merge-base last updated in 2.43.0`. Local `git --version` returned `git version 2.56.0`; the installed `git-merge-base` manual output contains the same status text and has footer `Git 2.56.0`.
- The frozen C1 counter docstring describes the C check as strict ancestry. Its helper at `count-c1.py:114-120` returns false on equality before calling `git merge-base --is-ancestor` and treats only return code 0 as ancestor. Thus strictness is the counter's separate equality guard; it is not attributed to the manual.
- Read the requested `CORPUS.md` SOURCES section and the `SOURCES.md` registry header / last row (S173). The proposed row follows the 11-column registry shape. The cited knowledge-entry draft at `.ufo/waves/round-29/w1/out/ScribeKnowledgeEntry/self-assessment-at-writing.md` explicitly cites S175 and describes the counter's separate equality guard.

## Gate
Gate: URL `https://git-scm.com/docs/git-merge-base`; UTC access-time sample `2026-10-23T12:03:03Z` (the date command ran concurrently with the fetch); §OPTIONS `--is-ancestor`, saved page line 1704; verbatim quote (13 words): “and exit with status 0 if true, or with status 1 if not.”

Saved page SHA-256: `0dc2f88a4935851e824b3d35c8236d7d4ad4603554b2ff24cc25ec83962868f3`.

## Commands and outcomes
- `timeout 45s curl -sSfL --max-filesize 1048576 https://git-scm.com/docs/git-merge-base -o /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/w1/out/ScribeSrcMergeBase/page.html` — no diagnostic output; the saved HTML was read and hashed. The 1 MiB maximum was set on the fetch.
- `timeout 10s date -u +%Y-%m-%dT%H:%M:%SZ` — `2026-10-23T12:03:03Z`; sampled concurrently with the fetch, so subsecond/request-bound timing was not captured.
- `timeout 10s sha256sum /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/w1/out/ScribeSrcMergeBase/page.html` — `0dc2f88a4935851e824b3d35c8236d7d4ad4603554b2ff24cc25ec83962868f3`.
- `timeout 10s git --version` — `git version 2.56.0`.
- `timeout 15s man -P cat git-git-merge-base` — `No manual entry for git-git-merge-base`, exit 16.
- `timeout 15s man -P cat git-merge-base` — displayed the installed manual including the matching `--is-ancestor` status text and `Git 2.56.0` footer.
- Read `/usr/share/doc/git` — path not found. The installed manual was available through the corrected `git-merge-base` man-page name.

## Touched surfaces and artifacts
- Read-only lane inputs: `.ufo/waves/round-29/preregistration.json`, `.ufo/waves/round-29/count-c1.py`, `CORPUS.md`, `corpus/SOURCES.md`.
- New scoped outputs only: `.ufo/waves/round-29/w1/out/ScribeSrcMergeBase/page.html`, `row.md`, `quote.txt`, `REPORT.md`; advice at `.ufo/waves/round-29/w1/advice/ScribeSrcMergeBase.md`.
- No tracked lane file was edited. No source row was integrated into `corpus/SOURCES.md`; this is a proposal for the L1. No counter run, test, build, server run, or tool installation occurred.

## Limits / out of scope
- This verifies the manual's documented exit semantics and the installed manual's matching text; it does not execute the counter or establish any commit's ancestry.
- The access time is a UTC sample concurrent with `curl`, not a timestamp obtained from the HTTP transaction. The requested report marks that limit rather than asserting a finer-grained time.
