# SrcS177 — pretty-formats `%ct` / `%cI`

VERDICT: hold. On the live page, `%ct` is “committer date, UNIX timestamp” and `%cI` is “committer date, strict ISO 8601 format.” Both sentences are paired with those placeholders in the PRETTY FORMATS definition list. No defect in the inherited S177 claim.

## Axes
- Verbatim match of the two placeholder definitions.
- Access time in UTC, with a saved byte record.
- Whether the landed S177 row and the lesson quote still say what the page says.

## Access
- URL: `https://git-scm.com/docs/pretty-formats` (final URL the same; HTTP 200).
- Access (UTC): `2026-10-23T18:31:15Z` (response `Date: Fri, 23 Oct 2026 18:31:15 GMT`). An earlier fetch in the same check returned `Date: Fri, 23 Oct 2026 18:30:37 GMT` and the same body hash.
- Title: `Git - pretty-formats Documentation`.
- Revision banner, verbatim: `pretty-formats last updated in 2.54.0`. Version menu, verbatim: `2.55.0 → 2.56.0 no changes`.
- Saved body: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/w2/out/kama-r29-w2-SrcS177-5/page.html` — 104718 bytes, sha256 `3c86dbfaa35e846ddc7b056aa76b2484137c304e0955b149bd2c03a10e82d11e`.
- Heading, verbatim, at `page.html:2442`: `<h2 id="_pretty_formats">…PRETTY FORMATS</h2>`.

## Verbatim fragments
Each placeholder occurs once, as `<code>…</code></span></dt><dd><p>…</p>`:

| placeholder | definition (verbatim) |
|---|---|
| `%ct` | committer date, UNIX timestamp |
| `%ci` | committer date, ISO 8601-like format |
| `%cI` | committer date, strict ISO 8601 format |

`%ci` is the adjacent contrast the S177 teaches cell uses (“unlike `%ci`'s ISO 8601-like form”). That contrast is on the page. The author-date twins on the same page are `%at` “author date, UNIX timestamp” and `%aI` “author date, strict ISO 8601 format”; they are not what S177 claims.

## Landed text
- `corpus/SOURCES.md` row S177 (line 189) points at this URL and §PRETTY FORMATS placeholders `%ct` and `%cI`, access date 2026-10-23. Its teaches cell says the counter reads W's committer date with `git show -s --format=%ct` as a UNIX timestamp, and that `%cI` is the strict ISO 8601 committer-date form unlike `%ci`. The two format sentences match the page. This seat did not re-run the counter.
- `corpus/lessons/round-29.md` line 103 located quote, verbatim: `committer date, UNIX timestamp` (PRETTY FORMATS, placeholder `%ct`), accessed `2026-10-23T12:02:47Z`, opened by ScribeSrcPrettyFormats. That quote is the `%ct` sentence only. It is verbatim. It does not quote `%cI`; the `%cI` sentence is in the scribe quote file and in the S177 teaches cell, and it is on the page.

## Wave-1 bytes vs this fetch
Saved w1 page `.ufo/waves/round-29/w1/out/ScribeSrcPrettyFormats/page.html` is 104850 bytes, sha256 `fac8765c2ea1925a60f999799056c8ab58688ad51140d20f5f5125e9577efc5d` (the hash the scribe recorded). Unified diff against this fetch is four content lines, all asset URLs: the stylesheet and application-script `href`/`src` changed and their `integrity` attributes were dropped. The `%ct`, `%ci`, and `%cI` definition sentences are unchanged. The scribe quote file still has both spans: “committer date, UNIX timestamp” … “committer date, strict ISO 8601 format”.

## Installed manual (cross-check, not the cited URL)
`git --version` → `git version 2.56.0`. `man -w git-log` → `/usr/share/man/man1/git-log.1.gz`. There is no `git-pretty-formats` manual (the w1 scribe's `man git-pretty-formats` miss). The same sentences are in `git-log(1)` PRETTY FORMATS:

```
1400:             %ct
1401:                 committer date, UNIX timestamp
1403:             %ci
1404:                 committer date, ISO 8601-like format
1406:             %cI
1407:                 committer date, strict ISO 8601 format
```

## Tools
None installed. Pacman not used.

## Unknowns
None for the assigned question. The page is not pinned to a Git source commit; the revision shown is “last updated in 2.54.0” with “2.55.0 → 2.56.0 no changes.”
