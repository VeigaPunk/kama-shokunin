# ReviewQualityAppend — KQ37 landing conformance (kama round 27, attempt 3)

VERDICT: holds — QUALITY.md gained exactly 6 appended lines ending in a well-formed 4-cell KQ37 row whose id was unused tree-wide before this round, and the new knowledge entry carries the sibling source/verified-at/recheck headers with every citation I checked (counter sha256, landed commit, line pointers, SOURCES rows) exact; corpus/README.md is untouched, so the coverage-map row is still absent as expected before L1's later add.

Reviewer: KamaR27A3.ReviewQualityAppend (leaf, no subagents). 2026-10-23.
Scope: corpus/QUALITY.md and corpus/knowledge/ changes 0ec32cac..324d5d62e61276af312c8eb42f678004aec245d1 (lane read-only; no git/jj writes; working tree confirmed clean for corpus/, so working-tree reads are tip-equivalent).

## Evidence

### 1. QUALITY.md changed by appended lines only — CONFIRMED

- `git -C <lane> diff --numstat 0ec32cac 324d5d62e61276af312c8eb42f678004aec245d1 -- corpus/` → exit 0:
  `6 0 corpus/QUALITY.md`, `5 0 corpus/SOURCES.md`, `68 0 corpus/knowledge/echo-discriminating-counters.md`, `92 0 corpus/lessons/round-27.md`. No deletions anywhere; README.md absent from the diff (untouched).
- `git diff -U4 0ec32cac 324d5d62... -- corpus/QUALITY.md` → exit 0, exactly one hunk `@@ -210,4 +210,10 @@`; 6 added lines appended after the base EOF context ("...is not a landed-tip measurement."), 0 removed lines.
- Line counts: base 213 → tip 219 (`git show <rev>:corpus/QUALITY.md | wc -l`). +6 = the 6 appended lines; append-only at end-of-file, no interleaving.

### 2. KQ37 table has 4 cells — CONFIRMED

- Tip QUALITY.md:219 row parsed with `awk -F'|' '{print NF-2}'` → `cells: 4`; header row (tip:217) is `| ID | Admit only when | Reject or limit when | Motivating lesson |` = 4 columns. Visual scan of the full hunk shows no embedded `|` inside cell text, so 4 is the true cell count.
- Row content (QUALITY.md:219): criterion = refuse signature echoed (case-folded or whitespace-removed) in request path / any JSON-decoded key or value at any depth / either serialisation of the decoded body, and ≤1 row per message frame; reject cell cites S136 (RFC 8259 §7 `\uXXXX`) and S137 (`server-common.cpp:1375` frame splice); lesson cell points at `lessons/round-26-verifier-spotcheck.md` routed defect 2, `lessons/round-27.md`, `knowledge/echo-discriminating-counters.md`.
- Semantics conformance [verified, text level]: the frozen counter implements exactly this rule — `occurs`/`squash` (count-c1.py:343-348: case-fold OR whitespace-squashed substring), `json_strings` (:351-362: decoded keys/values at any depth), `request_surfaces` (:365-372: path + decoded strings + `json.dumps` with and without `ensure_ascii` = "either serialisation"), echo check `f:in-request` at :586-587, frame clause `h:same-message-frame` at :708-709 (signature cut out, case-folded, non-blank remainder equality).

### 3. KQ37 id unused before — CONFIRMED

- `git grep -c KQ37 0ec32cac -- .` → exit 1, zero occurrences anywhere in the base tree. Prior max id at base is KQ36 (QUALITY.md:203); KQ37 is the next free id.

### 4. Knowledge entry headers like siblings — CONFIRMED

- `corpus/knowledge/echo-discriminating-counters.md:1-3`: `source:` (S136, S137 @704366d76 with the raw sha note, lane evidence pointer, counter path + sha256 + landed 1471f676), `verified-at: 2026-10-23 — both sources opened this round`, `recheck: on-release — reopen S137 when the installed llama.cpp build changes; S136 180d`. Then `# Echo-discriminating error-signature counters`.
- Sibling census (all 20 files in corpus/knowledge/): every file carries the same `source:`/`verified-at:`/`recheck:` trio. 8 files (incl. this one) are headers-first (`source:` at line 1, e.g. llamacpp-loading-lifecycle.md:1-3, context-capacity.md, error-is-not-a-verdict.md); 12 are title-first with the trio lower down (e.g. serving-metrics-crosswalk.md:2-4). Both positions are established conventions; the trio itself is universal, so the entry conforms.
- `verified-at` 2026-10-23 matches the round-27 Gate table access times (S136/S137 06:48Z, S138 06:53Z; corpus/lessons/round-27.md §Gate).

### 5. README coverage map does not list it yet — CONFIRMED (expected; L1 adds later)

- `git grep -n 'echo' 324d5d62... -- corpus/README.md` → exit 1 (no match, so `knowledge/echo-discriminating-counters.md` is not in the coverage map).
- corpus/README.md has no entry in the round diff numstat — the file is byte-identical between the two revisions. NOTE: the round-27 knowledge entry is therefore absent from README's per-round coverage tables (lines 29-35, 41, 47, 90-92, 119, 167, 206, 238 end at round 17+); the assignment states L1 adds that row later. Flagging so the later add is not forgotten: until then README's map understates the corpus by one knowledge entry.

### 6. Citation conformance of the new entry (extra checks, all exact)

- `sha256sum .ufo/waves/round-27/count-c1.py` → `49491b80e4f4ed2a85ab822a52f0b1a0fdb1dee53423e3d43b60ee25d1bf2765` — equals the entry's pinned sha, the round context's frozen sha, AND `git show 1471f676:.ufo/waves/round-27/count-c1.py | sha256sum` (same hash). `git merge-base --is-ancestor 1471f676 324d5d62...` → ancestor=yes; 1471f676 dated 2026-10-23, subject "round-27: C1 pre-data amendment A3 ... one message frame one row".
- Line pointers in the entry are exact against those frozen bytes: `request_surfaces`/`json_strings`/`occurs` at lines 343-372 (`squash` def 343, `occurs` 347-348, `json_strings` 351-362, `request_surfaces` 365-372, grep-verified); echo check at line 586; `h:same-message-frame` at lines 708-709.
- SOURCES.md diff = 5 appended rows (S134-S138 at SOURCES.md:146-150 at tip); S136 (RFC 8259) and S137 (server-common.cpp#L1375 @704366d) cited by KQ37 and the entry exist as claimed; S138 present per repair 7 (S133 supersede).
- KQ37's third reject clause ("a control seat for a named class was refused or died → class unscored, claim exploratory or waits") is consistent with C1's withdrawn-before-data disposition (lessons/round-27.md §Claims; plan.json C1).

## Nits (non-blocking)

1. QUALITY.md:215 section header reads "Criterion added — round27 error-signature counters..." — "round27" lacks the separator used by sibling headers ("Round 26 qualification — KQ36...", QUALITY.md:205) and carries no date paren. Cosmetic only.
2. The KQ37 section has no trailing prose line (KQ35/KQ36 sections each end with a scoping sentence, QUALITY.md:187, 207). No template rule requires one. Cosmetic.

## Residual risk and verification gaps

- Text-level conformance only: I did not execute the counter or replay shortcut rows (executor seats' surface), so "KQ37's rule discriminates on data" remains unverified here — the entry itself says so (§What this does not establish). LSP diagnostics not applicable: the changed files are Markdown; all checks above are git/grep text facts, quoted verbatim.
- The README coverage-map row is a deferred add by L1; unverified by me (not yet existing by design).
- No processes, servers, or scratch files were created; nothing to clean up. No installs performed (none needed).
