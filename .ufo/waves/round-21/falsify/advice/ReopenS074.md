VERDICT: partial - quote, anchor, access date, tier, status and used-by hold; the rationale "S066 already carries the claim" is refuted by ldconfig(8); kind, version provenance and recheck disagree.
Attacked: registry row S074 (corpus/SOURCES.md:86); its Gate row (corpus/lessons/round-21.md:50, identical at committed b76727f3); contract v1 (/home/vgpnk/Projects/shokunin/CORPUS.md:112-118 rules 1-2; :133-147 census).

## Executed (exit in brackets; lane untouched; scratch /tmp/kama-r21-ReopenS074 removed, rm exit 0)
- curl -sS -D shared-hdr.txt -o shared-fresh.html https://tldp.org/HOWTO/Program-Library-HOWTO/shared-libraries.html -> http=200 bytes=28706, no redirect [0]; cmp vs first fetch [0]; sha256 61c31cade7efaab4b8101c5e4ac67eb8203df3aa621abf87e37e681817ac38f6 (same as build seat's).
- Headers: `date: Wed, 21 Oct 2026 11:23:33 GMT`; `last-modified: Fri, 11 Apr 2003 23:07:25 GMT`.
- index.html -> http=200 bytes=4374, cmp identical [0], sha256 9f798583410099a7589ec0bc88b569503e24b1304e84c17bb1867568f0200575. ldconfig.8.html -> http=200 bytes=11926, sha256 6a81540a534692ed7cb6d5434275e08b3ade388311bdb88f1e4e506be2bfde38 [0].
- Contract census (CORPUS.md:133-145, run verbatim from lane root): rows 74 [0]; NF!=13 -> 0 [0]; tiers A=70 B=1 C=3 [0]; statuses mined=60 queued=7 rejected=7 [0]; duplicate ids none [0]; enum and tier-inflation none [0].
- python (eval): mined used-by paths checked 104, missing none; S074 cells identical in b76727f3 and a6617149 (git show exit 0); S075 absent; 11 cells, no stray `|`.
- python: Gate quote verbatim in whitespace-normalised page = True, in worktree and in the b76727f3 lesson; 16 words (wc -w [0]).
- _grep (no exit reported by tool): ldconfig.8.html `install|linker|symbolic` -> no line contains "install"; corpus/knowledge `installer|linker name|linker-name` -> No matches.

## Per field
- source/URL - AGREE. Resolves 200, no redirect; title matches the §3.1.1 heading.
- anchor §3.1.1 (#AEN49) - AGREE. `NAME="AEN49"` raw line 119; heading "3.1.1. Shared Library Names" line 121; §3.1.1 spans raw 116-198.
- revision "HOWTO version 1.20, 11 April 2003" - PARTIAL. The version appears only on index.html:35-36 (PUBDATE). The cited page has no "1.20", "2003" or "Wheeler" (only the DocBook "Version 1.7" generator, line 7). Last-Modified corroborates the date. The anchor should cite index.html:35-36.
- quote - AGREE. "installers must specifically modify symbolic links to update what the linker will use for a library": 16 words, raw lines 174-175, inside §3.1.1.
- access date 2026-10-21 - AGREE (Date header). The Gate gives the date in its preamble only, as for S066-S073.
- scope - AGREE on content (roles at lines 129-131, 144-146, 156-162). "corroboration only" is a usage note, not a topic.
- teaches, content - PARTIAL. Page: installers must modify links "to update what the linker will use" (174-175), a link-time claim; the row's "what is used" drops that limit. The page's operative sentence, that ldconfig does NOT set up linker names (160-162), is omitted.
- teaches, rationale "S066 already carries the claim" - DISAGREE (refuted). S066 teaches (SOURCES.md:78): "which file it names is install state that a regular-file digest cannot see." It never says installers modify links. ldconfig(8) has no installer statement; its only chain is `libfoo.so -> libfoo.so.1 -> libfoo.so.1.12` (lines 98-102). grep `[Ii]nstall|linker` over SOURCES.md matches nine rows; none but S074 says installers retarget links.
- teaches, form - MINOR. The six other queued rows (S021, S022, S023, S025, S029, S059) hold one benefit sentence; S074 adds status rationale. A bare "flip:" is not a violation (S065 is mined with one).
- kind `docs` - DISAGREE (judgment). Scope says "older community guide"; the contract has `community`; the registry's three community rows (S027-S029) are tier C. [INFERENCE] `community` fits; if reclassified, tier B needs its own stated reason (expert write-up, B definition).
- tier B - AGREE. Expert write-up (David A. Wheeler, index.html:32) with reproducible commands; not official glibc/ld.so docs, so not A.
- status `queued` - AGREE with contract; the stated rationale is the defect. If the premise is judged unneeded, `rejected` with a REJECTED teaches is the honest alternative (in-place status change, logged old->new).
- used-by `—` - AGREE. Outside SOURCES.md only corpus/lessons/round-21.md names S074 (Gate line 50; renumber note line 56); no knowledge file cites it. Same practice as the six queued rows, which lessons cite with used-by `—`. [INFERENCE] The contract's "lessons citing the row" literally covers Gate mentions; practice does not count them.
- recheck `365d` - DISAGREE (unexplained). The seat draft says 180d (SrcTldpSoname.md:21, :28). 365d is the only one of 74 rows; the Gate gives no reason. [INFERENCE] The seat's liveness rationale argues shorter: S040 records S021's URL returning 404.
- opened 2026-10-21; id S074 - AGREE (next unused id).

## Consequences [INFERENCE]
- Rule 2: teaches, kind, scope and anchor are not in-place fields, and b76727f3 commits S074 as-is. A correction needs a new row opening `supersedes S074 —`, which moves the frontier count 74 -> 75; or log the rationale error as a lesson erratum.
- C2 scope: the installer claim is link-time (linker names). It does not support the runtime soname retarget that corpus/knowledge/llamacpp-loading-lifecycle.md:324-362 describes; that supplement cites S066, S067, S068 only (line 330).
- Side finding: S066's "install state" wording is not in ldconfig(8). S074's rationale rests on S066, so S066 needs the same check.

## Housekeeping
- Tools installed or updated: none. Used curl, git (scratch clone only), python3, awk, sha256sum, cp as found.
- Out: .ufo/waves/round-21/falsify/out/ReopenS074/ (shared-fresh.html, index-fresh.html, ldconfig.8.html, shared-hdr.txt; sha256 as above).
