# R57Item13SourceAudit — S515 re-open and runtime Git env-pair verification

Seat: R57Item13SourceAudit (item round57/SourceAudit/13), leaf executor. Lane: kama, round 57 wave 1.
Axes touched: calibration (registry anchor/quote fidelity), operability (live runtime semantics).
Scope: read-only audit; no repo shared-file edits; no commits, pushes or jj/git mutations. Installs: none.

## Assignment and result

Re-open source S515 (`corpus/SOURCES.md:268`) from its canonical URL and verify the runtime Git
environment-pair claim, then record quote, location and date.

**Result: S515 verified — source bytes, anchor, quote (18 words), revision marker, opened date and
runtime semantics all re-derive at the live URL on 2026-10-27. One advisory on the admit-record and
one on location/date precision; no source defect found.**

## Source facts re-derived this round

| Field | Re-derived value |
|---|---|
| Registry row | `corpus/SOURCES.md:268` (`S515`, docs, tier B, mined, recheck 180d, used-by `corpus/lessons/round-56.md`) |
| URL | `https://git-scm.com/docs/git-config#Documentation/git-config.txt-GITCONFIGCOUNT` |
| Access date | 2026-10-27 (UTC `2026-10-27T18:07:56Z` and `2026-10-27T18:09:37Z`; local `2026-10-27T15:07:56-03:00` / `15:09:37-03:00`) |
| HTTP | `HTTP/2 200`, `last-modified: Mon, 26 Oct 2026 14:52:03 GMT`, `etag: W/"6adf6913-cac8d"` |
| Anchor present | `id="Documentation/git-config.txt-GITCONFIGCOUNT"` |
| Section path | `ENVIRONMENT` → `GIT_CONFIG_COUNT` / `GIT_CONFIG_KEY_<n>` / `GIT_CONFIG_VALUE_<n>` |
| Revision marker | page header: `git-config last updated in 2.56.0`; version selector entry `2.56.0` carries `<em class="date">2026-09-28</em>`; host `git --version` = `git version 2.56.0` |
| Located quote | “all environment pairs GIT_CONFIG_KEY_<n> and GIT_CONFIG_VALUE_<n> up to that number will be added to the process’s runtime configuration” (18 words, ≤25) |
| Quote uniqueness | 1 occurrence in the tag-stripped page |
| Snapshot identity | fetch1 = fetch2 = round-56 snapshot `.ufo/waves/round-56/sources/git-docs-git-config.html`, all `sha256 706b1566467e9cd8c6cdda853a5fc82118a48fde3119777d18cefc014bcd3d5a`; `cmp` exit 0 both ways |

Commands (scratch `/fast/scratch/hyaku/kama-r57/R57Item13SourceAudit/`):

```
curl -sS -L --max-time 60 -D headers.txt -o live-git-config.html https://git-scm.com/docs/git-config
# exit 0; HTTP/2 200; 830605 bytes; sha256 706b1566…
curl -sS -L --max-time 60 -H 'Cache-Control: no-cache' -D headers2.txt -o live2-git-config.html \
  'https://git-scm.com/docs/git-config#Documentation/git-config.txt-GITCONFIGCOUNT'
# exit 0; HTTP/2 200; sha256 706b1566…; cmp fetch1 fetch2 → exit 0
cmp -s live-git-config.html <lane>/.ufo/waves/round-56/sources/git-docs-git-config.html ; echo $?
# 0
wc -w receipts/quote.txt    # 18
grep -o 'id="Documentation/git-config.txt-GITCONFIG[A-Z_]*"' live-git-config.html
# id="Documentation/git-config.txt-GITCONFIG" … -GITCONFIGCOUNT … -GITCONFIGGLOBAL … -GITCONFIGNOSYSTEM … -GITCONFIGSYSTEM
grep -c '2026-09-28' live-git-config.html    # 1 (2.56.0 entry date in the version dropdown)
```

The located paragraph (context, tags stripped):

> GIT_CONFIG_COUNT GIT_CONFIG_KEY_<n> GIT_CONFIG_VALUE_<n> If GIT_CONFIG_COUNT is set to a positive
> number, all environment pairs GIT_CONFIG_KEY_<n> and GIT_CONFIG_VALUE_<n> up to that number will be
> added to the process’s runtime configuration. The config pairs are zero-indexed. Any missing key or
> value is treated as an error. An empty GIT_CONFIG_COUNT is treated the same as GIT_CONFIG_COUNT=0,
> namely no pairs are processed. These environment variables will override values in configuration
> files, but will be overridden by any explicit options passed via git -c.

## Runtime verification (operability, host git 2.56.0)

Documentation text alone is not runtime evidence, so the claimed semantics were exercised with
read-only `git config --get` queries in a scratch directory that is not a repository.

| # | Case | Output | Exit |
|---|---|---|---|
| A | `GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=probe.key GIT_CONFIG_VALUE_0=probe-value git config --get probe.key` | `probe-value` | 0 |
| B | same pair + `git -c probe.key=cli-value` | `cli-value` | 0 |
| C | `GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=probe.key` (no value) | `error: missing config value GIT_CONFIG_VALUE_0` / `fatal: unable to parse command-line config` | 128 |
| D | `GIT_CONFIG_COUNT=` (empty) + full pair | *(no value)* | 1 |
| E | `GIT_CONFIG_COUNT=0` + full pair | *(no value)* | 1 |
| F | no environment pairs | *(no value)* | 1 |
| G | config file via `GIT_CONFIG_GLOBAL=filecfg`, pair absent | `file-value` | 0 |
| H | same file + env pair `env-value` | `env-value` | 0 |
| I | same file + env pair + `git -c probe.key=cli-value` | `cli-value` | 0 |

This matches the located text on every clause: pairs are injected into the process runtime
configuration (A), environment values override configuration files (H/G), explicit `git -c` options
override environment values (I/B), missing key or value is an error (C), and empty/zero count adds
no pairs (D/E/F). Receipt: `.ufo/waves/round-57/measured/R57Item13SourceAudit/runtime-git-env-pairs.out`.

## Admit/reject spot check (advisory only)

`S515` was admitted (tier B, mined) in round 56 as an append-only correction superseding `S511`.
Comparing the row against the reopened source:

- Quote, anchor, version marker and opened date in the row all re-derive at the live URL; the
  snapshot path named in the row exists and is byte-identical to the live fetch (`cmp` exit 0). The
  admit decision is **source-supported** (KQ6: engine named, revision named, section named, opened
  row cited; tier B fits a vendor/manual statement).
- Advisory 1 (record precision): the row's relevance cell reads “corrected revision anchor for
  runtime Git config injection through environment pairs”, while `S511` also carried the concrete
  why (“overriding config files (e.g. core.hooksPath reaches an attacker hook)”). Since `S511`'s row
  is not rewritten, no content is lost, but a reader following “supersedes S511” could read the
  narrower cell as replacing that rationale. Recommend that the round lesson state the
  supersession is **anchor-only** and that S511's relevance stands.
- Advisory 2 (admit-record completeness): the round-56 non-author spot-check
  (`corpus/lessons/round-56-verifier-spotcheck.md`) re-opened S512/S513/S514 in its discernment
  table and asserted S515's 18 words only in prose; S515's admit decision therefore has **no explicit
  non-author row**. Recommend an explicit S515 admit row in the round-57 lesson.
- Advisory 3 (date wording): siblings' round-57 notes phrase the revision as “last updated
  2026-09-28”. The page's own string is “git-config last updated in 2.56.0”; `2026-09-28` is the
  `<em class="date">` on the `2.56.0` entry in the version selector (2.56.0's date). Both are true,
  but the registry wording (“page last updated in 2.56.0”) is the exact page claim and should be
  kept as-is rather than restated as a date.

Per the wave rule, dispatched seats are lane-authors, so these are advisories only — this seat does
not adjudicate the admit decision.

## Round-56 outside defects (lesson-addressed check)

Round-56 routed defects that touch this source path are defect 6 (S510/S511 revision-anchor
omissions) and the absent SCORECARD/SHONEN calibration check on the C2 counter. Defect 6 is
addressed by the appended S514/S515 rows with revision markers, which this re-open confirms are
factually correct. The C2 no-op defect is a counter/operability matter outside this source row and
is covered by the wave's C1/C2 seats; this audit confirms only that S515 is not part of that
defect.

## Evidence artifacts (lane-relative)

- `.ufo/waves/round-57/sources/R57Item13SourceAudit-gitconfig-env-section.txt` — URL, access
  timestamps, HTTP headers, hashes, `cmp` exits, anchor, section path, revision marker, quote,
  `wc -w`, located paragraph.
- `.ufo/waves/round-57/measured/R57Item13SourceAudit/runtime-git-env-pairs.out` — nine runtime cases
  with outputs and exits.
- `.ufo/waves/round-57/measured/R57Item13SourceAudit/{headers.txt,headers2.txt,quote.txt,located-section.txt}` — fetch headers and extracted text.
- `.ufo/waves/round-57/measured/R57Item13SourceAudit/audit-s515.py` plus
  `receipts-s515-main.out` / `receipts-s515-mutant.out` and the three registry-mutant controls —
  independent checker for distinct case 34 (see `R57Item13SourceAudit.distinct34.md`).
- Round-56 snapshot used for byte identity: `.ufo/waves/round-56/sources/git-docs-git-config.html`.

## Risks and blockers

- No blocker. The live page is CDN-served (`server: cloudflare`, `x-origin-cache: HIT`); byte
  identity across two accesses and with the committed round-56 snapshot makes a stale-cache
  artifact unlikely, and the page's revision marker plus `last-modified` agree.
- Quote glyph note: the page uses `process’s` (U+2019); the registry row and round-56 lesson use
  the ASCII `process's`. Content is identical after apostrophe normalization; normalization must be
  applied by any exact-string checker or it will report a false mismatch (my first checker run did
  exactly that, `quote_matches=False`, before normalizing).
- Scratch directory `/fast/scratch/hyaku/kama-r57/R57Item13SourceAudit/` holds the two 830 KB
  fetches; they are not copied into the lane because they are byte-identical to the committed
  round-56 snapshot whose hash is recorded in the receipt.
