VERDICT: holds — S139's re-fetch is byte-identical to the row's pinned sha256, both quoted line ranges are verbatim inside §7, the `supersedes S136 —` correction shape and every contract cell check out, and both validators pass (append-only exit 0; census validate exit 0 with W04 advisories only).

Reviewer: ReviewS139Row (residual, round-27 attempt 3, lane kama-shokunin, 2026-10-23).
Scope: `corpus/SOURCES.md` row S139 (line 151), its Gate row (`corpus/lessons/round-27.md:106`), contract shape (`/home/vgpnk/Projects/shokunin/CORPUS.md:86-118`).
Lane tip verified: `git -C /home/vgpnk/Projects/shokunin/kama-shokunin rev-parse HEAD` → `52632caa2ed813c1c12f7a9dcab3556b4f0bd9eb` (exit 0).
No tool installs (none needed). No llama-server started (this item names no port block). Artifacts: `.ufo/waves/round-27/residual/out/ReviewS139Row/` (`rfc8259.txt`, `rfc8259-info.html`, `rfc8259-datatracker.html`); scratch `/fast/scratch/hyaku/kama-r27c/res-ReviewS139Row/`. All fetches/writes ran under `ulimit -f 1048576` inside `timeout`; every command exited 0 unless stated; no processes left running.

## Checks

### 1. Re-fetch rfc8259.txt — HOLDS
```
bash -c 'ulimit -f 1048576; timeout 120 curl -fsSL https://www.rfc-editor.org/rfc/rfc8259.txt -o rfc8259.txt'
# curl_exit=0
# 61a5378f4255c720beb2a4b4a63b29540147c140f36988bf086291989b4cd2d7  rfc8259.txt
# 28360 rfc8259.txt
```
The sha256 matches in full: S139 row (`corpus/SOURCES.md:151`), S136 row (`corpus/SOURCES.md:148`), Gate rows' truncated `61a5378f…2d7` (`corpus/lessons/round-27.md:103,106`). "Same fetch as S136" (Gate row) is supported by hash equality, not by re-executing the L1's fetch [INFERENCE: identical bytes is the property the Gate claim needs].

### 2. Registry anchor "lines 433-440 (BMP six-character form)" — HOLDS
`sed -n '433,440p' rfc8259.txt` →
```
   Any character may be escaped.  If the character is in the Basic
   Multilingual Plane (U+0000 through U+FFFF), then it may be
   represented as a six-character sequence: a reverse solidus, followed
   ...
   as "\u005C".
```
§7 heading `7.  Strings` is at `rfc8259.txt:424`, so 433-440 lies inside §7 "Strings" as the anchor states.

### 3. Registry anchor "455-459 (surrogate pair)" and Gate quote — HOLDS
`sed -n '455,459p' rfc8259.txt` →
```
   To escape an extended character that is not in the Basic Multilingual
   Plane, the character is represented as a 12-character sequence,
   encoding the UTF-16 surrogate pair.  So, for example, a string
   containing only the G clef character (U+1D11E) may be represented as
   "\uD834\uDD1E".
```
Gate quote "the character is represented as a 12-character sequence, encoding the UTF-16 surrogate pair." is verbatim, spanning `rfc8259.txt:456-457` (line 456 ends `...12-character sequence,`; line 457 begins `encoding the UTF-16 surrogate pair.`). 13 words ≤ 25; location "§7, rfc8259.txt lines 456-457" correct (`corpus/lessons/round-27.md:106`).

### 4. `supersedes S136` prefix and correction shape — HOLDS
- S139 `teaches` opens exactly `supersedes S136 —` (`corpus/SOURCES.md:151`), matching CORPUS rule 2: "A correction is a new row whose `teaches` opens `supersedes S0NN —`" (`/home/vgpnk/Projects/shokunin/CORPUS.md:107-108`).
- S136 stays landed unchanged: `git diff 0ec32cac..52632caa -- corpus/SOURCES.md` = 6 insertions, 0 deletions — the four rows S136-S139 (`corpus/SOURCES.md:148-151`), one Search-log bullet (rule 5 note: identified 2 / screened 2 / included 2 for S136+S137, plus the S138 correction note), one blank line.
- S139's statement about what S136 said is accurate against the base-added S136 text (diff line: title `(Dec 2017, Internet Standard STD 90)`, teaches "any character of a JSON string may be written as a six-character \uXXXX escape").

### 5. STD 90 attribution — HOLDS
- The fetched RFC text contains no self-attribution "STD 90": `grep -n 'STD' rfc8259.txt` → only `753: ... STD 63, RFC 3629` and `757: ... STD 68, RFC 5234`; line 30 says "This is an Internet Standards Track document." This matches S139 teaches' parenthetical "(...named STD 90 although the RFC text itself does not)".
- External attribution verified by fetch: `https://www.rfc-editor.org/info/rfc8259` contains "STD 90" ×2 (plus 6× "Internet Standard"); `https://datatracker.ietf.org/doc/rfc8259/` contains "STD 90" ×1. The title's "Internet Standard, STD 90 per the RFC Editor and IETF Datatracker indexes" is accurate.

### 6. Contract shape (CORPUS.md:86-118) — HOLDS
Against `| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |`:
11 cells (validator-parsed, NF=13 with edge pipes), no bare `|`; id `S139` = `S`+3 digits, next unused after S138 (`corpus/SOURCES.md:150-151`); kind `spec` (enum ✓); tier `A` (spec is primary for its scope; community≠A n/a); scope narrow, explicitly negative-scoped; anchor exact section+lines+fetch date+raw sha256, not a bare homepage; status `mined`; opened `2026-10-23` (ISO, present); recheck `180d` (cadence); used-by = two repo-relative comma-separated paths, both on disk and both citing S139: `corpus/knowledge/echo-discriminating-counters.md:1,46` (line 46: "S139, superseding S136's wording") and `corpus/lessons/round-27.md:36,106,109,126,140`.

### 7. Append-only validator — HOLDS (exit 0)
From lane root:
```
python3 tools/sources-append-only.py --from 0ec32cac --to 52632caa2ed813c1c12f7a9dcab3556b4f0bd9eb
# added S136 (allowed)
# added S137 (allowed)
# added S138 (allowed)
# added S139 (allowed)
# no append-only violations
# append_only_exit=0
```
Tool semantics read from source (`tools/sources-append-only.py:15-21`): MUTABLE_CELLS = {status, recheck, used-by}; source/kind/tier/scope/anchor/teaches/opened immutable; violations exit 1, parse faults exit 2. No existing row was mutated in the range; consistent with the 6-insertion diff.

### 8. Census validate — HOLDS (exit 0)
From lane root:
```
/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama
# 50 lines: kama  W04  <id> duplicate url <url> across scopes   (S031, S043, ..., S135, S137)
# kama	ok	/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md
# census_exit=0
```
Script header (`/home/vgpnk/Projects/shokunin/scripts/sources-census.sh:15-16,32`): exit 0 = "clean or warnings"; "W04 same URL across scopes (warnings do not affect clean lanes)". No E-codes fired — in particular no E01 (malformed row), E04 (duplicate URL+scope without supersedes), E08/E09 (bad dates), E11 (dangling used-by). The W04 set includes long-pre-existing rows (S031, S043, S056...), so it is not introduced by this round; several rows per URL across scopes is the registry's established shape.

### 9. Gate row completeness (contract rule 1) — HOLDS
`corpus/lessons/round-27.md:106` carries URL, access timestamp (2026-10-23T06:48Z, same fetch as S136), and the ≤25-word verbatim quote with location (check 3). The non-author re-open reports the Gate cites exist: `ScoutReopenS136.md`, `ScoutReopenS137.md`, `ReviewLessonGate.md` in `.ufo/waves/round-27/w1a3/advice/` (heads read: both open with `VERDICT: holds`; ReviewLessonGate re-verified S136-S138 byte-for-byte with matching fresh sha256s). Note: those three seats re-opened S136/S137/S138; S139 landed afterward as the CriticEntryFactsSources repair and has no dedicated w1a3 re-open report. Contract rule 1 requires non-author verification to "re-open a sample", not every row [INFERENCE: no defect], and this residual review re-opens S139 directly above.

## Residual risk
- The STD 90 attribution rests on today's fetches of the RFC Editor and Datatracker index pages; the row's 180d recheck is the correct control if those pages change.
- Byte-identity claims rest on sha256 equality between my fetch and the pinned hash; I did not reproduce the L1's exact fetch pipeline.
- Census W04 (50 advisories) is curation hygiene, out of my item's scope.
- Not checked here (other items' targets): S137/S138 code-line anchors, the frozen counter, C1/X1 measurement logic (C1 withdrawn before data; not scored).

## Verification gaps
None blocking. All nine checks executed with exit 0; no live server used; writes confined to `.ufo/waves/round-27/residual/out/ReviewS139Row/` and `/fast/scratch/hyaku/kama-r27c/res-ReviewS139Row/`.
