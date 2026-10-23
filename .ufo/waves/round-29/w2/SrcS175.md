# SrcS175 — git-merge-base `--is-ancestor` quote check

Seat: SrcS175 (kama round 29, attempt 2, wave w2). Read-only verification. Outputs are this file and `.ufo/waves/round-29/w2/out/SrcS175/report.md`. No other lane file was edited. No tool was installed.

## Axes

1. Verbatim presence of the S175 exit-status quote on the live manual.
2. Whether the row's paraphrased `teaches` cell still matches that wording.
3. UTC access date of the page that was actually opened.

## Verdict

- **Verbatim quote: present.** The 13-word gate quote appears once, unchanged, in the live page.
- **`teaches` claim: holds.** It is a paraphrase, not a quotation, and it does not overclaim the page.
- **Access (UTC): `2026-10-23T18:30:30Z`.**
- **Defect:** none in the quote or the `teaches` paraphrase. The row is still an uncommitted working-tree line (expected attempt-1 leftover), not a wording defect.

## Row under check

Working tree only. `git blame -L 187,187 corpus/SOURCES.md` reports author `Not Committed Yet` against previous `513eba3ba51a142c9936553e3a85918345eb5c4c` (HEAD at check time). `git status --porcelain -- corpus/SOURCES.md` was ` M corpus/SOURCES.md`. Last committed touch of the file is `e49b4cf77046024551ba83d490ef83d9dee061ed` (round-28, S140–S173).

Path: `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md` line 187.

| cell | text |
|---|---|
| id | S175 |
| source | Git git-merge-base manual — https://git-scm.com/docs/git-merge-base |
| anchor | §OPTIONS `--is-ancestor`; online manual last updated in Git 2.43.0; same semantics in installed Git 2.56.0 manual, opened 2026-10-23 |
| teaches | For the ordered commits, status 0 means the first is an ancestor of the second, 1 means it is not, and errors use a nonzero status other than 1. |

The verbatim quote this row was gated on is not the `teaches` cell. It is the wave-1 gate sentence in `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/w1/out/ScribeSrcMergeBase/quote.txt` line 1 and `REPORT.md` Gate:

> and exit with status 0 if true, or with status 1 if not.

(13 words; location claimed: §OPTIONS `--is-ancestor`, saved page line 1704.)

## Live page

Opened `https://git-scm.com/docs/git-merge-base` with `curl -sSfL --max-time 30`.

- `date -u` immediately before and after the fetch: both `2026-10-23T18:30:30Z`.
- Response header `date: Fri, 23 Oct 2026 18:30:30 GMT` (same instant). `HTTP/2 200`. `content-type: text/html; charset=utf-8`.
- `last-modified: Fri, 23 Oct 2026 13:46:13 GMT` (later than the wave-1 sample `2026-10-23T12:03:03Z`).
- Saved body: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/w2/out/SrcS175/page.html` (41269 bytes). SHA-256 `65a481b44c983b101b9465963dcf04f040502618fba6952033704d867f7215d1`. Headers: `.../w2/out/SrcS175/headers.txt`.

The quote is a contiguous substring once, at character offset 30006, line 1704, inside the OPTIONS definition whose anchor id is `Documentation/git-merge-base.txt---is-ancestor`. Visible text of that block:

```
--is-ancestor
Check if the first <commit> is an ancestor of the second <commit>,
and exit with status 0 if true, or with status 1 if not.
Errors are signaled by a non-zero status that is not 1.
```

Banner on the same page, line 1326: `git-merge-base last updated in 2.43.0`.

The whole-file hash differs from the wave-1 save (`0dc2f88a4935851e824b3d35c8236d7d4ad4603554b2ff24cc25ec83962868f3`, 41401 bytes). A line diff of the two HTML files is only two asset URLs (stylesheet and `application.min.*.js`; the new tags drop `integrity=`). The `--is-ancestor` HTML block is byte-identical. Its SHA-256 in both saves is `9be7a9da594c774c574a3b681601a2dda2d61fea98a9a3de5e9b428727920ff8`. The later `Last-Modified` is site chrome, not a manual-text change.

## Does `teaches` still hold?

Page wording, mapped onto the cell:

| row phrase | page | holds? |
|---|---|---|
| For the ordered commits | Synopsis is `git merge-base --is-ancestor <commit> <commit>`; the option says "the first `<commit>`" and "the second `<commit>`". | yes, paraphrase of argument order |
| status 0 means the first is an ancestor of the second | "exit with status 0 if true", where the check is "the first `<commit>` is an ancestor of the second" | yes |
| 1 means it is not | "or with status 1 if not" | yes |
| errors use a nonzero status other than 1 | "Errors are signaled by a non-zero status that is not 1." | yes; "nonzero" vs "non-zero" is spelling only |

The cell does not say the manual itself rejects equality. The scope cell says C1 separately rejects equality. That matches `strict_ancestor` in `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/count-c1.py` lines 114–120: equal commits return false before `git merge-base --is-ancestor`, and only return code 0 is treated as ancestor. The manual's "ancestor" includes a commit as an ancestor of itself; the row does not attribute strictness to the manual. No overclaim.

## Same sentence elsewhere (not a substitute for the page)

- Upstream source, tag `v2.43.0`, `Documentation/git-merge-base.txt`, and current `master` `Documentation/git-merge-base.adoc`, are byte-identical (SHA-256 `d3cf8078bc9e34dfca1342d1f4d9a5485cc81f0bb624d124ce87725624f60e82`, 7759 bytes). Copies: `.../w2/out/SrcS175/git-merge-base-v2.43.0.txt` and `git-merge-base-master.adoc`. The option body is:

```
--is-ancestor::
	Check if the first <commit> is an ancestor of the second <commit>,
	and exit with status 0 if true, or with status 1 if not.
	Errors are signaled by a non-zero status that is not 1.
```

  `master` `Documentation/git-merge-base.txt` returns HTTP 404 (the file is `.adoc` now). This agrees with the site banner "last updated in 2.43.0".

- Installed manual: `git version 2.56.0`. `man -P cat git-merge-base` saved as `.../w2/out/SrcS175/man.txt` (SHA-256 `2ff9f2367abfd70865d61f3ae1dbf9ba8fc9e835c434227ada88bf8b7339e49e`, footer `Git 2.56.0  2026-09-27`). Formatted lines 45–48 wrap and justify the same words (`exit  with  status 0 if true, or with status 1 if not. Errors are sig‐ naled by a non-zero status that is not 1.`). The groff source `/usr/share/man/man1/git-merge-base.1.gz` has the unwrapped sentence with roff escapes (`not\&.`, `non\-zero`), so a raw substring search for the HTML quote misses it; the words are the same. Anchor claim "same semantics in installed Git 2.56.0" holds.

## Limits

This check reopened the manual page and compared wording. It did not run `count-c1.py` and does not decide any commit's ancestry.

Full seat copy: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/w2/out/SrcS175/report.md`.
