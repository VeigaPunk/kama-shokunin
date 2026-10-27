#!/usr/bin/env python3
"""Emit rows.md for seat S1Rows2, inlining the proposed rows byte-exactly."""
import pathlib

S = pathlib.Path("/fast/scratch/hyaku/kama-r50/S1Rows2")
O = pathlib.Path("/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/S1Rows2")


def row(path, sid):
    for line in (S / path).read_text(encoding="utf-8").splitlines():
        if line.startswith(f"| {sid} |"):
            return line
    raise SystemExit(f"{sid} not in {path}")


R496 = row("proposed-C.md", "S496")
R497 = row("proposed-C.md", "S497")
R498A = row("proposed-C.md", "S498")
R498B = row("proposed-B.md", "S498")

body = f"""# S1Rows2 — rows S496, S497, S498 re-opened against their sources (round 50, wave 1)

**Verdict.** S496 is clean: no cell is wrong, both quotes verbatim, 12 and 13 words. S497's
`teaches` cell fails (28 words, and the ` ... ` stands where the page has
`(see PR_SET_CHILD_SUBREAPER(2const))`, so the quote is not present verbatim). S498's
`teaches` cell fails (the words `(&#96;)` and `(~)` were deleted) and its `anchor` lost a
verified full-page sha256 — and the parity arithmetic that forced the deletion of the
single backtick glyph did **not** force the loss of the sha256, proved in §5 F3. Replacement
rows are proposed in §6; both variants validate at exit 0 and parse in the append-only guard.

Registry read at lane HEAD `3b79eaddf38246c637cc7ba1a94ab363422876b6` (build
`97c864bead3ee4a2f629574e77263d33834ec98a`; freeze
`601c8889f33d1797c712feb753974c20cf891264`): `corpus/SOURCES.md:249` (S496), `:250` (S497),
`:251` (S498). Nothing in the lane, the fleet repo or `shokuknow` was written; every run
below used `/fast/scratch/hyaku/kama-r50/S1Rows2`.

## 1. Sources opened

| source | copy under `.ufo/waves/round-50/` | copy sha256 | page identity in the copy |
|---|---|---|---|
| https://man7.org/linux/man-pages/man5/proc_pid_maps.5.html | `c1/proc_pid_maps.5.txt` | `e7cdf0ff1c8d8d87e5c92e529a09270945ca3b7cafb8e823a7ca3d294f3c16a2` | `Linux man-pages 6.19            2026-02-08               proc_pid_maps(5)` (copy:187) |
| https://man7.org/linux/man-pages/man2/PR_SET_PDEATHSIG.2const.html | `c1/PR_SET_PDEATHSIG.2const.txt` | `906bbe5cc7e38c02a82bb60ff3b7e0d1cfb21089a1a24f00f045fb1b86edb1e4` | `Linux man-pages 6.19            2026-02-08       PR_SET_PDEATHSIG(2const)` (copy:149) |
| https://spec.commonmark.org/0.31.2/#fenced-code-blocks | `c2/commonmark-0.31.2-s4.5.txt` | `2dbd3f25b72d95ad2653bfcd9af704d7400a027ff0ed3e81e0391c3284c66d73` | copy:1 records the URL, `opened 2026-10-27T00:14:13Z` and `full page sha256 c85f56cc2101f761cc94215c677cd2c7c1ecca9c47be016479fdfe718af60f0d` |

### Live re-fetch (2026-10-27T00:55Z)

```
curl -sS -L --max-time 60 -o page-<sha8>.html <url>      # all three 200
200 11702  https://man7.org/linux/man-pages/man5/proc_pid_maps.5.html
200 10684  https://man7.org/linux/man-pages/man2/PR_SET_PDEATHSIG.2const.html
200 514698 https://spec.commonmark.org/0.31.2/
c85f56cc2101f761cc94215c677cd2c7c1ecca9c47be016479fdfe718af60f0d  page-628a625f.html
```

The fetched spec page hashes to exactly the value the c2 copy records, so the excerpt's
provenance is exact, not asserted. In the two man-page fetches `Linux man-pages 6.19` and
`2026-02-08` each appear once and `obtained from the tarball man-pages-6.19.tar.gz` is
present, matching both anchors. Each quoted span was also found in the fetched HTML
(`each subreaper process`, `cleared for the child of a`, `process-directed`,
`at least three consecutive backtick`, `preceded by up to three spaces of indentation`);
`id="fenced-code-blocks"` is present, so S498's fragment is the section it names.

## 2. Quote check, machine result

`python3 /fast/scratch/hyaku/kama-r50/S1Rows2/check_rows.py` normalises whitespace in the
copy and asks `quote in copy` (the `grep -F` test a reader would run), plus the word count:

```
S496 words=12 copy=VERBATIM live=hit :: dev is the device (major:minor); inode is the inode on that device
S496 words=13 copy=VERBATIM live=hit :: The pathname field will usually be the file that is backing the mapping.
S497 words=28 copy=MISS live=MISS :: The parent-death signal is sent upon subsequent termination of the parent thread and also upon termination of each subreaper process ... to which the caller is subsequently reparented.
      source-text form present=True :: ... each subreaper process (see PR_SET_CHILD_SUBREAPER(2const)) to which ...
      OVER 25 WORDS (28)
S498 words=15 copy=MISS live=MISS :: A code fence is a sequence of at least three consecutive backtick characters or tildes.
      source-text form present=True :: A code fence is a sequence of at least three consecutive backtick characters (`) or tildes (~).
exit=1
```

So: S496 2/2 verbatim inside the cap; S497 0/1 (28 words, ellipsis); S498 0/1 (15 words,
two glyph parentheticals deleted).

`live=MISS` on S497/S498 is an artifact of that script's tag stripping (it inserts a space
at every element boundary, so `PR_SET_CHILD_SUBREAPER(2const)` and the `(`)` glyph are split
by a space); the raw `grep -F` checks in §1 found every span in the fetched HTML, so the
copies are faithful and the `MISS` verdict above is about the *row's* wording, not the page.

## 3. Cell audit

### S496 — `corpus/SOURCES.md:249`

| cell | observed | verdict |
|---|---|---|
| id | `S496`, one occurrence in the registry (no E03) | pass |
| source | `Linux proc_pid_maps(5) — https://man7.org/linux/man-pages/man5/proc_pid_maps.5.html`; fetch 200 | pass |
| kind | `docs` (a man page) | pass |
| tier | `A` (kernel/libc manual page, not community) | pass |
| scope | matches §DESCRIPTION: `dev` is `major:minor`, `inode` is the inode on that device, `pathname` is the backing file (copy:113-121); inode 0 = no inode associated (copy:115-117); the page's ptrace read check is correctly excluded ("not a permission model") | pass, one wording note (F7) |
| anchor | §DESCRIPTION holds both quoted paragraphs (copy:113-121); footer `Linux man-pages 6.19  2026-02-08` verified in the copy and the live fetch | pass |
| teaches | both quotes verbatim, 12 + 13 words; inference "so the live tool can read which file a running server maps, then hash that same file through its pathname" is grounded at `tools/kama-llamacpp-live.py:678-726` (reads `/proc/<pid>/maps`, keeps `dev`/`inode`, re-opens the pathname `O_NOFOLLOW`, `fstat`-checks dev+inode, hashes) | pass |
| status | `mined`; the build's live tool depends on it | pass |
| opened | `2026-10-27`; host UTC date is 2026-10-27 (validator E08 uses `date -u +%F`), so not future | pass |
| recheck | `on-release`; man-pages text changes with a man-pages release | pass |
| used-by | names `corpus/knowledge/llamacpp-loading-lifecycle.md` and `corpus/lessons/round-50.md`; the lesson is the known integration item, but the knowledge file has no S496 content at HEAD and the tool is not named (F5) | note |

### S497 — `corpus/SOURCES.md:250`

| cell | observed | verdict |
|---|---|---|
| id | `S497`, one occurrence | pass |
| source | `Linux PR_SET_PDEATHSIG(2const) — https://man7.org/linux/man-pages/man2/PR_SET_PDEATHSIG.2const.html`; fetch 200 | pass |
| kind / tier | `docs` / `A` | pass |
| scope | every clause is in §DESCRIPTION: parent-thread termination (copy:87-90), subreaper reparenting (copy:89-90), parent already gone at prctl time (copy:90-93), cleared for a `fork(2)` child (copy:100-101), process-directed (copy:95). Omits the other clearing cases (F6) | pass with note |
| anchor | §DESCRIPTION; `man-pages 6.19`, `2026-02-08` verified in copy:149 and live fetch | pass |
| teaches | **fails**: 28 words and the ` ... ` is not in the page — the page has `(see PR_SET_CHILD_SUBREAPER(2const))` at copy:89, so the quoted string is absent (F1) | **FAIL** |
| status / opened / recheck | `mined` / `2026-10-27` (UTC today) / `on-release` | pass |
| used-by | knowledge file has no S497 content at HEAD; the two tools that set the signal are not named (F5) | note |

### S498 — `corpus/SOURCES.md:251`

| cell | observed | verdict |
|---|---|---|
| id | `S498`, one occurrence | pass |
| source | `CommonMark spec 0.31.2 §4.5, Fenced code blocks — https://spec.commonmark.org/0.31.2/#fenced-code-blocks`; fetch 200, `id="fenced-code-blocks"` present | pass |
| kind / tier | `spec` / `A` | pass |
| scope | covers opening (≥3 backticks or tildes, ≤3 spaces), closing (same character, ≥ as many), unclosed-runs-to-end, literal content. **Omits two §4.5 clauses the counter implements**: the backtick info-string restriction (copy:12-14) and "Tildes and backticks cannot be mixed" (copy:7) — the tool enforces both (F4) | **under-covered** |
| anchor | §4.5 named and the copy path is right, but `; full page sha256 c85f56cc…` was removed by `3d42897b` (F2) | **regressed** |
| teaches | **fails**: `backtick characters or tildes.` is not in §4.5 — the spec reads `backtick characters (&#96;) or tildes (~).` at copy:5-7 (F2) | **FAIL** |
| status / opened / recheck | `mined` / `2026-10-27` / `360d` — `360d` is a valid E09 cadence; the URL is version-pinned, so the only drift is the site republishing 0.31.2, which the recorded full-page sha256 detects | pass |
| used-by | names only `corpus/lessons/round-50.md`; `tools/append-only-audit.py` implements the rule (F5) | note |

## 4. Gate result as committed

`bash /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --file <clone>/corpus/SOURCES.md`
on a `git clone --shared` of the lane at HEAD:

```
file\tE11\tS496 missing used-by corpus/lessons/round-50.md
file\tE11\tS497 missing used-by corpus/lessons/round-50.md
file\tE11\tS498 missing used-by corpus/lessons/round-50.md
exit=1        codes: 93 W04, 3 E11, 1 W01
```

The three `E11` are the known integration item (the lesson lands at integration). With a
placeholder `corpus/lessons/round-50.md` in the scratch clone the same command prints
`file\tok\t…/corpus/SOURCES.md` and exits 0 (`93 W04, 1 W01`), so no other error is hidden
behind them. The `E11` are the only E-codes; the W04/W01 are standing warnings unrelated to
these rows.

## 5. Findings

Each carries the command that shows it. Counters, preregistration, controls and the registry
were not edited.

### F1 — S497 `teaches`: quote over the cap and not verbatim (`corpus/SOURCES.md:250`)

The cell quotes `... each subreaper process ... to which the caller is subsequently
reparented.` The page reads `(see PR_SET_CHILD_SUBREAPER(2const))` at
`.ufo/waves/round-50/c1/PR_SET_PDEATHSIG.2const.txt:89`, so the string is not present;
with the ellipsis counted as a word the quote is 28 words, over the 25-word cap.

```
python3 -c 'import re;t=re.sub(r"\\s+"," ",open(".ufo/waves/round-50/c1/PR_SET_PDEATHSIG.2const.txt").read());q="The parent-death signal is sent upon subsequent termination of the parent thread and also upon termination of each subreaper process ... to which the caller is subsequently reparented.";print(len(q.split()), q in t)'
28 False
```

Fix: two verbatim sentences from the same paragraph, 20 and 12 words (row in §6). The
fork-clearing sentence is not decoration: it is why the build must set the signal at every
link (`tools/kama-live-replay.py:587` self; `:314-332` live child, SIGTERM;
`tools/kama-llamacpp-live.py:661-668` + `:1888` server, SIGKILL).

### F2 — S498 `teaches` and `anchor` regressed by `3d42897b` (`corpus/SOURCES.md:251`)

At the build the cell read `"A code fence is a sequence of at least three consecutive
backtick characters (&#96;) or tildes (~)."` and the anchor carried the span
`` `; full page sha256 c85f56cc…` ``. Commit `3d42897b65294ad963cd3686ced4666822e0ec73`
("build-fix - S498 row markdown tick parity so sources-append-only row parser accepts it")
replaced both. After it, the quote drops two glyph parentheticals (so it is not in the
spec) and the anchor drops a value that re-fetches byte-identically today.

```
git -C /home/vgpnk/Projects/shokunin/kama-shokunin show 3d42897b -- corpus/SOURCES.md
git -C … show 97c864be:corpus/SOURCES.md | sed -n '251p'      # the verbatim form plus sha256
sha256sum page-628a625f.html                                   # c85f56cc… == the recorded value
```

### F3 — the guard could not grade the commit that made that edit, and the sha256 loss was not forced

At the build the row is unparseable for `tools/sources-append-only.py`, because one raw
backtick in a table cell inverts that parser's code-span state and merges the following
cells:

```
python3 tools/sources-append-only.py --from 97c864bead3ee4a2f629574e77263d33834ec98a --to 3d42897b65294ad963cd3686ced4666822e0ec73
error: 97c864bead3ee4a2f629574e77263d33834ec98a:corpus/SOURCES.md:251: unterminated table row (no closing pipe)
exit=2
python3 tools/sources-append-only.py --from 3d42897b65294ad963cd3686ced4666822e0ec73 --to 3b79eaddf38246c637cc7ba1a94ab363422876b6
no append-only violations
exit=0
```

Exit 2 on the old blob means the immutable-cell rewrite in `3d42897b` was never compared:
the guard's own repair is invisible to the guard. And the repair over-corrected. Three
fixture runs in `/fast/scratch/hyaku/kama-r50/S1Rows2/fixture.*` (each a fresh `git init -q`,
`rev-parse --show-toplevel` asserted equal to the fixture dir, commits made with `-C` and a
scoped `-c user.name/-c user.email`):

| fixture variant (from the HEAD registry) | guard result |
|---|---|
| proposed C (entity form for the glyph, sha256 restored) | `exit 1`, 5 immutable cells on 2 rows, **no parse error** |
| proposed D (raw `(&#96;)` restored, sha256 restored) | `exit 2`, `HEAD:corpus/SOURCES.md:251: unterminated table row` |
| proposed E (HEAD row + `; full page sha256 …` restored, glyph still absent) | `exit 1`, one cell (`S498 anchor`), **no parse error** |

So the single raw backtick is genuinely unrepresentable in that cell (D), but the sha256
span was removable-free (E) and the quote was recoverable losslessly (C, §6). Fix: restore
both, with the glyph written as the `&#96;` entity (parity-even, decodes to the spec's text)
or use the tick-free sentences of variant B.

### F4 — S498 `scope` does not cover two §4.5 clauses the counter enforces

`tools/append-only-audit.py:282-292` (`fence_open`) returns `None` when a backtick fence's
info string contains a backtick — copy:12-14 — and models `>= 3` of one character, i.e. the
`(Tildes and backticks cannot be mixed.)` rule at copy:7. Neither clause is in the row's
`scope`, so the behaviour rests on an unregistered part of §4.5.

```
sed -n '282,292p' tools/append-only-audit.py
grep -n "may not contain any backtick\\|cannot be mixed" .ufo/waves/round-50/c2/commonmark-0.31.2-s4.5.txt
13:after a backtick fence, it may not contain any backtick
7:tildes (~).  (Tildes and backticks cannot be mixed.)
```

Fix: the scope in §6 adds `(not mixed)` and `a backtick fence whose info string holds no
backtick`.

### F5 — `used-by` omits the tools that carry these sources, and the named knowledge file has no round-50 content

The convention already lists code (`S089`, `S091`, `S096`, `S100`, `S101`, `S102` name
`tools/report-landing-audit.py`). The three round-50 sources are used by code that cites
them by name, not by id: `tools/kama-llamacpp-live.py:681` (`proc_pid_maps(5)`),
`tools/kama-live-replay.py:102` (`PR_SET_PDEATHSIG(2const)`),
`tools/append-only-audit.py:8` (`CommonMark 0.31.2 §4.5`). None is in any of the three
`used-by` cells. Separately, S496/S497 name
`corpus/knowledge/llamacpp-loading-lifecycle.md`, which carries no round-50 paragraph at
HEAD — unlike S494/S495, whose knowledge append landed in the round-49 build:

```
grep -n "S496\\|S497\\|model_mapping\\|pdeathsig\\|proc/.*maps" corpus/knowledge/llamacpp-loading-lifecycle.md
(no output)
grep -n "S494, S495" corpus/knowledge/llamacpp-loading-lifecycle.md
453:**Round-49 execution witness … (appended 2026-10-26; S494, S495).**
```

This is not on the prompt's known-integration list (which names only
`corpus/lessons/round-50.md`), so it is reported as a new integration item: either the
round-50 knowledge paragraph lands at integration or S496/S497's `used-by` is claiming a
file that does not use them. Fix: `used-by` in §6 names the three tools; the knowledge
append is an integration action, not a row change.

### F6 — S497 `scope` omits the other clearing cases (observation)

copy:101-105: the setting is also cleared when executing a set-user-ID/set-group-ID binary
or one with capabilities, and on changes to effective/fs user and group IDs. Nothing in the
build trips this (`python -I` only, no credential change), so the scope is not wrong — but a
future wrapper that changes credentials would silently drop the mechanism. Suggested
extension if the lane wants the boundary stated; I did not put it in the replacement row to
keep the scope at what the counter relies on.

### F7 — provenance nits (observations)

- The two c1 copies carry no in-file fetch record (no URL, time or hash), unlike the c2 copy
  whose first line has all three. The Gate entry's access time is the only record for the
  man pages. Suggested: the copy sha256 values above belong in the S496/S497 anchors; §6's
  S496 row keeps its anchor unchanged and the hardened variant in §7 adds them.
- `proc_pid_maps(5)` says the pathname is shown unescaped except newlines (copy:155-160),
  is ` (deleted)`-suffixed for a deleted backing file (copy:161-163) and is blank for an
  anonymous mapping (copy:150-153). `tools/kama-llamacpp-live.py:693` compares the row's
  pathname to `realpath(model)` exactly, so an unlinked or newline-bearing model path
  reports `mapped: false` and the replay refuses — fail-closed, but the boundary belongs in
  the knowledge paragraph F5 asks for, not in a row change.
- S496 `scope` says an inode of 0 means "a memory region has no file"; the page says "no
  inode is associated with the memory region" (copy:115-117). Same intent, slightly stronger
  wording; the tool compares `f[4] != '0'`, which matches the page. Left as written; the
  verbatim alternative is `0 indicates that no inode is associated with the memory region`
  (11 words) if the lane prefers exactness.

## 6. Proposed replacement rows (primary: variant C)

S496 needs no immutable-cell change. S497 and S498 do. The rows below were generated by
`make_proposed.py`, are 11 cells each, have even raw-backtick parity, and all quotes were
re-checked verbatim in the copies at 20/12 (S497) and 17/15 (S498) words.

```
{R496}
```

```
{R497}
```

```
{R498A}
```

The `&#96;` in S498's first quote decodes to the backtick of the spec's `(&#96;)`; the
verification step for the Gate is
`python3 -c 'import html,re;...html.unescape(cell)...'` — receipt
`check-candidates.out` prints `entity-decodes-equal: True`. If the canonical judge requires a
raw `grep -F` match rather than a decode, use variant B, which quotes three tick-free
sentences of the same section (17/13/15 words, all verbatim, no entity):

```
{R498B}
```

Both variants were run through the real gate:

```
cp proposed-C.md <clone>/corpus/SOURCES.md; printf placeholder > <clone>/corpus/lessons/round-50.md
bash scripts/sources-census.sh validate --file <clone>/corpus/SOURCES.md   → exit 0, 0 E-codes
cp proposed-B.md <clone>/corpus/SOURCES.md; (same placeholder)
bash scripts/sources-census.sh validate --file <clone>/corpus/SOURCES.md   → exit 0, 0 E-codes
```

and through the append-only guard on fixture repos (§5 F3): exit 1 with the immutable-cell
diffs, never exit 2 — the rows parse.

### Rule-2 note for whoever lands these

`SOURCES-CONTRACT-v1` rule 2 freezes {{source, kind, tier, scope, anchor, teaches, opened}}, so
the rows cannot be edited in place without a violation. The lane's precedent for a wording
repair is an appended section that leaves the row byte-identical (`## Round-21 falsify
corrections — S066–S074`, which still leaves S067's overstated `teaches` live at
`corpus/SOURCES.md:79`). That precedent has a cost this round shows: the registry keeps a
quote that fails the Gate's own verbatim rule. Two landing options, both append-only-clean
for the `## Registry` table:

1. **Errata section** `## Round-50 source correction — S497, S498` carrying the corrected
   `teaches`/`anchor`/`scope` text above, the two `used-by` additions (mutable, so these can
   also go straight into the rows), and the fixture evidence. The rows keep the defective
   quote.
2. **New superseding rows** — the lane's pattern for content changes (`S040` supersedes
   `S021`, `S047` supersedes `S043`, `S056` supersedes `S054`) — with the corrected cells and
   `supersedes S497` / `supersedes S498` in `teaches`, plus `S497`/`S498` moving to a
   `recheck` note. This leaves a correct quote in a row a reader reaches.

I recommend 2 for S498 (the quote is wrong, not merely reworded) and 1 for S497's wording
plus the `used-by` edits, and I am reporting rather than choosing, since the registry is
frozen and the choice is the L1's.

## 7. Optional hardening, not a defect

Anchors for the two man pages, if the lane wants the same provenance the S498 anchor had
before `3d42897b` (copy hashes re-computed at HEAD, §1):

- S496 anchor → `§DESCRIPTION, paragraphs on offset/dev/inode/pathname; man-pages 6.19, page dated 2026-02-08 (text copy `.ufo/waves/round-50/c1/proc_pid_maps.5.txt`, sha256 `e7cdf0ff1c8d8d87e5c92e529a09270945ca3b7cafb8e823a7ca3d294f3c16a2`)`
- S497 anchor → `§DESCRIPTION; man-pages 6.19, page dated 2026-02-08 (text copy `.ufo/waves/round-50/c1/PR_SET_PDEATHSIG.2const.txt`, sha256 `906bbe5cc7e38c02a82bb60ff3b7e0d1cfb21089a1a24f00f045fb1b86edb1e4`)`

It is in variant A (`proposed-A.md`) but not in the recommended variant C, because for S496
no cell is wrong.

## 8. Lesson `## Gate` entries (draft, access time 2026-10-27T00:14:13Z)

| Row | Decision | URL | Opened (UTC) | Located quote (≤ 25 words) | Why |
|---|---|---|---|---|---|
| S496 | admit (tier A, mined) | https://man7.org/linux/man-pages/man5/proc_pid_maps.5.html | 2026-10-27T00:14:13Z (text copy `.ufo/waves/round-50/c1/proc_pid_maps.5.txt`, sha256 `e7cdf0ff…`; man-pages 6.19, page dated 2026-02-08) | "dev is the device (major:minor); inode is the inode on that device" (copy:113-115, 12 words) and "The pathname field will usually be the file that is backing the mapping." (copy:119-120, 13 words) | grounds reading dev, inode and pathname for the file a running server maps and hashing that same file; the live tool does exactly that (`tools/kama-llamacpp-live.py:678-726`) |
| S497 | admit (tier A, mined) | https://man7.org/linux/man-pages/man2/PR_SET_PDEATHSIG.2const.html | 2026-10-27T00:14:13Z (text copy `.ufo/waves/round-50/c1/PR_SET_PDEATHSIG.2const.txt`, sha256 `906bbe5c…`; man-pages 6.19, page dated 2026-02-08) | "The parent-death signal is sent upon subsequent termination of the parent thread and also upon termination of each subreaper process" (copy:87-90, 20 words) and "The parent-death signal setting is cleared for the child of a fork(2)." (copy:100-101, 12 words) | grounds the teardown chain and why every link sets its own signal: fork(2) clears it (`tools/kama-live-replay.py:314-332`, `tools/kama-llamacpp-live.py:1888`) |
| S498 | admit (tier A, mined) | https://spec.commonmark.org/0.31.2/#fenced-code-blocks | 2026-10-27T00:14:13Z (text copy `.ufo/waves/round-50/c2/commonmark-0.31.2-s4.5.txt`, sha256 `2dbd3f25…`; full page sha256 `c85f56cc…`, re-fetched and matched 2026-10-27T00:55Z) | "A code fence is a sequence of at least three consecutive backtick characters (`) or tildes (~)." (copy:5-7, 17 words) and "The content of a code fence is treated as literal text, not parsed as inlines." (copy:36-37, 15 words) | grounds the fence-aware section scanner (`tools/append-only-audit.py:282-321`): a `## ` line inside a fence is literal text and cannot re-title a section |

Rejects this seat's evidence supports for the lesson's reject list:

- **Reject `backtick characters or tildes.` as the located quote.** It is not in §4.5 (the
  spec has `(&#96;)` and `(~)`); `grep -F` on the copy finds nothing. Flip: a parity-safe
  rendering (the `&#96;` entity, or variant B's tick-free sentences), never a silent
  deletion of glyphs.
- **Reject a `... `-elided 28-word span as a located quote.** Over the cap and not
  contiguous. Flip: quote a contiguous span ≤ 25 words.
- **Reject "the anchor's sha256 had to go for the row parser."** Proven false (fixture E):
  the HEAD row plus the sha256 span parses; only the raw glyph had to go.

## 9. Receipts (in `.ufo/waves/round-50/w1/out/S1Rows2/`)

| file | what it holds |
|---|---|
| `validate-head.out` | gate at HEAD without the lesson placeholder: `93 W04, 3 E11, 1 W01`, exit 1 |
| `validate-head-with-placeholder.out` | same registry, placeholder lesson present: `file ok`, exit 0 |
| `validate-proposed-C.out` | proposed C rows: exit 0, 0 E-codes |
| `validate-proposed-B.out` | proposed B rows: exit 0, 0 E-codes |
| `sources-append-only-at-build.out` | the build blob is unparseable at `:251`, exit 2 |
| `sources-append-only-head.out` | `3d42897b → HEAD`: no violations, exit 0 |
| `append-only-proposed-C.out` | fixture base → C: exit 1, 5 immutable cells, no parse error |
| `append-only-D-raw-glyph.out` | fixture base → D (raw glyph): exit 2 at `:251` |
| `append-only-E-sha-restored.out` | fixture base → E (sha restored on the HEAD row): exit 1, anchor only |
| `fetch-hashes.out` | the three fetches: HTTP status, bytes, sha256 |
| `check-quotes.out` | `check_rows.py` output (verbatim + word counts) |
| `check-candidates.out` | candidate quotes, all verbatim, plus the entity decode equality |
| `proposed-C.md`, `proposed-B.md`, `proposed-A.md`, `proposed-D-raw-glyph.md`, `proposed-E-head-plus-sha.md` | the variant registries the fixtures were built from |
| `rows.md` | this file |
| `receipt-notes.txt` | exact commands, exit codes and the scratch paths they ran in |

Scratch `/fast/scratch/hyaku/kama-r50/S1Rows2` (clone, fixture repos, fetches, outputs) was
removed after these receipts were copied here.
"""

O.mkdir(parents=True, exist_ok=True)
(O / "rows.md").write_text(body, encoding="utf-8")
print("wrote", O / "rows.md", len(body), "bytes")
