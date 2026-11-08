# CN02SourceFrontier — r94 w1 · C3 frontier/calibration check (source rows + census)

Seat CN02SourceFrontier (leaf, read-only). Lane `/home/vgpnk/Projects/shokunin/kama-shokunin`. Scratch `/fast/scratch/hyaku/kama-r94/CN02SourceFrontier/` removed at end. Host load during runs: load1 135.97 (23:42) → 148.53 (23:50), 32-core box; no timing claim is made here.

## Scope

Read-only verification of C3's frontier step at `M2 = 6aa5fa6bd9bbf44c4b2ca3f1e2158e7d5aa92623` (child of `M1 = a27656a454b1a2364f8b6e55f42fbca8c2e86ee4`; base `e6f1dccecbad6dea44a129dabc928822c458e824`; tip `11d2770b5e61e997245dce74eadeff8b3ce9ea1f`): (1) every new `corpus/SOURCES.md` row **S604–S615** — URL resolves to the stated file; the ≤25-word quote really sits at the stated line in the pinned `b12177` archive; the row's `sha256` equals the archive member's; the `teaches` cell teaches rather than restates; `used-by` names `SKILL.md` where the row is cited. (2) The census (exit code, row count, invariants). (3) The claim's own receipts (`corpus/lessons/round-94.md`, census receipts). No tracked lane file edited; no git mutation in the lane; no live endpoint touched.

## Commands and outputs (exit codes exact)

```
$ curl -sSL -o llama-b12177.tar.gz https://codeload.github.com/ggml-org/llama.cpp/tar.gz/refs/tags/b12177
$ sha256sum llama-b12177.tar.gz
f50a52f4ba45dd5b4b906db97cf230ce2e3b1117a0b9017411322ecba63eea13    # == pinned sha256
$ tar xzf llama-b12177.tar.gz                                          # -> llama.cpp-b12177/
$ bash /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama
… W04 (pre-existing) … W01 S481 (pre-existing) …
kama	ok	/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md      EXIT=0
$ bash …/sources-census.sh census --root /home/vgpnk/Projects/shokunin kama | grep ^kama
kama rows 355 | tier.A 339 | tier.B 11 | tier.C 5 | status.mined 319 | queued 8 | rejected 28
$ grep -E "S60[0-9]|S61[0-5]" census-validate-HEAD.out      -> 0 matches (rc=1)
# base re-derivation: base SOURCES.md into a mirrored lane dir, all other lane paths symlinked in
$ bash …/sources-census.sh validate --root <scratch>/baseroot kama  -> EXIT=0 (ok); census rows 343
$ bash …/sources-census.sh validate --root <scratch>/baseroot kama  -> EXIT=0 (ok); census rows 355  (M2 file)
```
343 → 355 confirmed by command. Delta = +12 = S604–S615 exactly (`git show 6aa5fa6b -- corpus/SOURCES.md` = 12 added lines, no other row touched). Per-row machine check (`out/check_rows_quotes.py`, `out/check_ranges_teaches.py`, `out/check_skill_prows.py`; results `out/row-verification.json`):

```
S604 MISSTATES (corpus/SOURCES.md:359) stated_line=150 words=2 quote='opt.handler_string(params, val);'
        actual_at_stated='        if (opt.handler_string) {'   quote_found_at=[151]
S605…S615 HOLDS (11/11): quote at stated line; sha256 == archive member == HTTP body; quote 2–9 words
```

## Findings

**F1 — DEFECT (a row misstates its located quote; off by one line).** `corpus/SOURCES.md:359` (S604) states the quote `opt.handler_string(params, val);` at **line 150** of `common/preset.cpp` @ b12177; it is at **line 151** (line 150 is `if (opt.handler_string) {`). Evidence: `out/row-verification.json` (S604, `quote_found_at=[151]`), archive `common/preset.cpp:150-151`. The same off-by-one is copied into the lesson Gate table, `corpus/lessons/round-94.md` (S604 row: "`opt.handler_string(params, val);` (line 150, inside `apply_to_params`)"). The other 11 rows land exactly on their stated line, so this is a single-row locator error, not a systematic offset. Consequence: C3's "≤25-word **located** quote per row" holds for 11 of 12 new rows and the lesson's S604 entry is not a faithful locator. Everything else about S604 is exact: URL 200, HTTP body sha256 = archive member sha256 = `793ad2c7…cbb25`, 2-word quote, `used-by SKILL.md`, cited in SKILL.md P44/P45 and in the claims' C2 paragraph.

**F2 — DEFECT (the claim's evidence trail is absent from the lane).** `plans/round-94-claims.md` states "Every control named here was executed before this file was committed; its receipt is committed with it under `.ufo/waves/round-94/controls/`", and C3's predicate names `controls/census-start.out` for the "before: rows=343, exit 0" output. At the freeze commit `F=285f1783` the path `.ufo/waves/round-94/` **does not exist** (`git ls-tree -r 285f1783 -- .ufo/waves/round-94/` → empty), and at `M1` it is still empty. Present today: `controls/c2-build-candidate.py`, `measured/c1.out`, `measured/c2.out` only. **Absent**: `controls/census-start.out`, `controls/sources-opened.out`, `controls/c1-base.out`, `controls/c1-forgeries.py`/`.out`, `controls/c2-base.out`, `controls/c2-forgeries.py`/`.out`, `controls/harm-base.out`, `controls/c2-rows.md`, `controls/c2-section.md` (the last two are named as receipts in my wave brief), `measured/gate-final.out`. Precedent: round-93's freeze commit `0f272a37` carried 15 control receipts incl. `census-start.out` and `sources-opened.out`. Substantively I re-derived the census numbers myself (343 → 355, exit 0 at both ends), so the claim's arithmetic is sound; what is missing is the committed receipt it points at.

**F3 — NOTE (lesson cites a receipt label that does not exist).** `corpus/lessons/round-94.md` grounds "Every P-row's text cell is the archive line byte for text" in "`measured/c2.out` B2". `.ufo/waves/round-94/measured/c2.out` has no `B2` label — only `SETTER_ROW`, `SETTER_DECISION`, `SETTER_SWEEP`, `SETTER_DIGEST` (`grep -cE "B[0-9]" … = 0`; round-93's `measured/c2.out` likewise has no `B2`); the dangling `B2` is carried from `corpus/lessons/round-93.md:20`. I re-verified the underlying claim independently: **92/92** round-94 P-row text cells match their archive line byte-for-byte (P56 needs the markdown `\|` unescaping the counter itself performs — `tools/round94-setter-sweep.py` `split_cells` — after which `} else if (arg == "-p" || arg == "--port") {` matches `tools/rpc/rpc-server.cpp:132` exactly).

**F4 — NOTE (S604's scope cell reaches past its own anchor).** S604's scope claims "the option ordering that decides which setter wins", but `common/preset.cpp` has no ordering construct (`grep -n "sort|order|operator<" common/preset.cpp` → no hits). The ordering lives in `common/arg.h:91-96` (`common_arg::operator<`, S610) and reaches `preset.cpp` only via `common_preset::options` being `std::map<common_arg, std::string>` (`common/preset.h:23`, S611), so `apply_to_params` (`preset.cpp:143`) iterates options in `strcmp(args[0])` order. True in combination, but S604's anchor cites only `preset.cpp` 142-160 / 285 and does not cross-reference S610/S611.

**F5 — NOTE (rendering defect in the landed SKILL.md section; C2 territory).** The round-94 table has its header row and separator twice: `SKILL.md:2111-2114`, both pairs added by `M2`; rendered, the second pair becomes two junk body rows. The counter tolerates it (`P_RE`/`D_RE` match only `Pnn`/`Rnn`), so `SETTER_SWEEP 92 92 … derived_disagree=0` is unaffected — visible, not grading.

**F6 — NOTE (re-opened rows re-verified clean).** The lesson re-opens S593, S596–S603; all nine claimed digests equal their `b12177` archive member's (`common/common.h`, `common/arg.cpp`, `tools/server/server.cpp`, `server-http.cpp`, `server-models.cpp`, `common/http.h`, `server-connect.cpp`, `server-http.h`, `server-models.h` — 9/9 match).

## Holds (verified, no finding)

- **URLs**: all 12 raw `b12177` URLs return HTTP 200; each body sha256 equals both the archive member's and the row's claimed digest. **Quotes**: 11/12 land exactly on the stated line, 2–9 words each (all ≤ 25); F1 is the exception. **`teaches`**: all 12 give a mechanism, consequence or scope distinction rather than repeating the quote — thinnest are S608 (its second clause is verbatim the source file's own trailing comment at `server-common.h:765`) and S611 (names the two functions and the routes using them). **`used-by`**: all 12 name `SKILL.md` and all 12 S-ids really appear in SKILL.md (S604×5, S605×2, S606×5, S607×2, S608×2, S609×2, S610×3, S611×3, S612×2, S613×1, S614×3, S615×3), each in the round-94 section's `Source` cell.
- **Census**: exit 0 at base (343), at M2 (355) and at the tip; no E-code and no W-code attributable to S604–S615 (only the pre-existing `W04` duplicate-URL list and `W01` S481, identical at base); `NF=13` for all 355 rows; no new row breaks a census invariant.
- **Lesson shape**: `corpus/lessons/round-94.md` carries `## Gate` (12 admits + 1 rejection with reason and flip + the re-opened row) and `## Mistakes` (M1/M2/M3, each class · evidence · captured-by · fix · "shown able to fail").

## Deliverables

`.ufo/waves/round-94/w1/out/CN02SourceFrontier/` — `row-verification.json` (per-row verdicts); `check_rows_quotes.py`, `check_ranges_teaches.py`, `check_skill_prows.py` (three checkers, re-runnable against any pinned archive); `census-validate-BASE-343.out`, `census-validate-M2-355.out`, `census-validate-HEAD.out`, `census-rows-BASE-343.out`, `census-rows-HEAD.out` (census receipts).

## Notes for the L1

F1 is a one-token fix in `corpus/SOURCES.md` (150 → 151) plus the same word in the lesson Gate table; it is the only misstatement among the 12 new rows. F2 is about the committed evidence trail, not the arithmetic: if `controls/census-start.out` is to exist as the claim states, it has to be committed. No tool was installed or upgraded this seat (no pacman / uv / cargo / release-binary action). Not exercised here (other seats own them): C1 probe behaviour, C2 counter semantics.

VERDICT: partial — 11 of 12 new source rows hold byte-for-byte and the census is clean (343→355, exit 0), but S604 misstates its quote's line (150 vs 151, repeated in the lesson Gate) and the round-94 receipts the frozen claims name — including `controls/census-start.out` — are absent from the lane tree.
