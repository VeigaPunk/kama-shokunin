# S515 re-open receipt — R57Item39TrendBoundary (2026-10-27)

Seat: R57Item39TrendBoundary (sentinel, round57/TrendBoundary/39, distinct case 60).
Read-only receipt; nothing outside this seat's wave out-dir was written.

## Fetch

```
$ curl -sS -L --max-time 60 -o git-config-live.html -w "http=%{http_code} bytes=%{size_download}\n" \
    "https://git-scm.com/docs/git-config"
http=200 bytes=830605
$ sha256sum git-config-live.html
706b1566467e9cd8c6cdda853a5fc82118a48fde3119777d18cefc014bcd3d5a  git-config-live.html
```

Byte-identity with the prior round's committed copy (no new fetch needed to trust it):

```
$ sha256sum .ufo/waves/round-56/sources/git-docs-git-config.html
706b1566467e9cd8c6cdda853a5fc82118a48fde3119777d18cefc014bcd3d5a
$ sha256sum .ufo/waves/round-57/sources/git-config-live-2026-10-27.html
706b1566467e9cd8c6cdda853a5fc82118a48fde3119777d18cefc014bcd3d5a
```

The round-57 wave snapshot is the same 830605 bytes. This seat's independent fetch
reproduced it byte-for-byte, so the source is unchanged between round 56 and round 57.

## Location and revision

- Document: `git-config(1)`, canonical URL
  `https://git-scm.com/docs/git-config#Documentation/git-config.txt-GITCONFIGCOUNT`.
- Section: `GIT_CONFIG_COUNT` / `GIT_CONFIG_KEY_<n>` / `GIT_CONFIG_VALUE_<n>`; the located
  sentence is the first paragraph under those headings.
- Anchor present in the fetched HTML: `git-config.txt-GITCONFIGCOUNT` (first occurrence of
  `GIT_CONFIG_COUNT` at HTML byte offset 168495; anchor text at 168985).
- Revision marker shown by the page: `git-config last updated in 2.56.0`; the version
  selector lists 2.56.0 dated 2026-09-28 as the latest.

## Located quote (18 words)

> all environment pairs GIT_CONFIG_KEY_<n> and GIT_CONFIG_VALUE_<n> up to that number will be
> added to the process's runtime configuration

Word count re-derived from the fetched copy: 18 (same count the round-56 lesson records).
The sentence sits at character 21467 of the whitespace-normalised, tag-stripped page text
(curly apostrophe U+2019 normalised to U+0027 for matching).

Immediate continuation in the same paragraph (verbatim, de-tagged), for scoping:

> The config pairs are zero-indexed. Any missing key or value is treated as an error. An
> empty GIT_CONFIG_COUNT is treated the same as GIT_CONFIG_COUNT=0, namely no pairs are
> processed. These environment variables will override values in configuration files, but
> will be overridden by any explicit options passed via git -c. This is useful for cases
> where you want to spawn multiple git commands with a common configuration but cannot
> depend on a configuration file, for example when writing scripts.

## Relation to the lane rows (no row cell changed by this seat)

- `corpus/SOURCES.md:268` (S515): same anchor, same 18-word quote, same 2.56.0 revision
  marker, `mined`, `recheck 180d`, `used-by corpus/lessons/round-56.md`.
- `corpus/SOURCES.md:264` (S511): same URL, same 18-word quote. S515 is a correction row
  that records the revision marker S511 omitted; it adds no new source and no new ground.
- `corpus/lessons/round-56.md:18` records the same quote and location; this re-open
  reproduces it.
