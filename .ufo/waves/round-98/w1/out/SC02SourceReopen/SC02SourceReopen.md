# SC02SourceReopen — independent re-open of the two round-98 sources (S622, S623)

Seat: SC02SourceReopen (leaf member, no subagent dispatch). Lane: `kama-shokunin`.
Milestone: kama r98 w1. Scope: re-open the two sources round 98 writes to `corpus/SOURCES.md`
and verify the registry rows; check the contract rules for where the rows land.
No tracked lane file was edited; no fleet/sibling/lane-jj state and no lane Git index was touched.
Only read-only git (`show`/`diff`/`rev-parse`/`cat-file`) was used.

## 1. Fetch (required step 1)

```
$ curl -sS -o gguf.md -w 'http_code=%{http_code} size=%{size_download}\nurl_effective=%{url_effective}\n' \
    'https://raw.githubusercontent.com/ggml-org/ggml/57e2c2ca2a7cae756b1c4dfafa0cdfef9051d234/docs/gguf.md'
http_code=200 size=43175
url_effective=https://raw.githubusercontent.com/ggml-org/ggml/57e2c2ca2a7cae756b1c4dfafa0cdfef9051d234/docs/gguf.md
$ sha256sum gguf.md
1dead27b6a522709f0127d194e58c21dbbbf00ba1c64fe37c54d1a9048b05020  gguf.md
```

**HTTP 200, 43 175 bytes, sha256 `1dead27b6a522709f0127d194e58c21dbbbf00ba1c64fe37c54d1a9048b05020`.**

Digest agreement (all three independent records carry the same value):

| record | location | digest |
|---|---|---|
| my fetch (this seat) | — | `1dead27b6a522709f0127d194e58c21dbbbf00ba1c64fe37c54d1a9048b05020` |
| S622 registry anchor | `corpus/SOURCES.md:377` | same |
| S620 registry anchor (same URL) | `corpus/SOURCES.md:375` | same |
| freeze-time receipt | `.ufo/waves/round-98/controls/sources-opened.out:4` | same ("HTTP 200, 43175 bytes") |

## 2. Per-row verdict

### S622 — **AGREE** on digest / quote / line / mechanics; **DISAGREE** on the scope+teaches wording (real, gradeable defect — see F1)

`corpus/SOURCES.md:377`

| cell | content |
|---|---|
| kind / tier / status | `spec` / `A` / `mined` |
| scope | "That the GGUF header is four fields — magic, version, tensor_count, metadata_kv_count — so a parser pays four preamble steps before the first tensor header" |
| anchor | "Commit 57e2c2ca, lines 277-300, sha256 1dead27b…, opened 2026-11-08: \"struct gguf_header_t {\" (line 277)" |
| teaches | "the header cost a parser pays before the first tensor is the four struct fields, grounding the boundary table's preamble term" |
| used-by | "SKILL.md, corpus/lessons/round-98.md" |

Verified:

* **Quote verbatim at the named line** — `sed -n '277p' gguf.md` → `struct gguf_header_t {`;
  `grep -Fx 'struct gguf_header_t {'` matches line 277 exactly (whole-line equality, the
  strongest form). Occurrence count in the file: **1** (`grep -c -F 'struct gguf_header_t {'`).
* **Digest** — matches (table above).
* **Anchor range** — the quoted struct `gguf_header_t` occupies lines **277–299** (`};` at 299;
  line 300 is blank). The row's range "277-300" brackets it (one trailing blank line over).
* **Contract mechanics** — 11 columns (`awk -F'|'` → NF=13, content cells = 11); no `|` inside
  any cell; id is the next unused (`S622`/`S623` do not exist at base `681c80a4`); kind/tier/
  status are in-enum; `opened` = today (2026-11-08, not future); `recheck` = `on-release`
  (symbolic cadence, allowed); `used-by` paths exist on disk; the row is **appended**, not
  edited: `git diff --numstat 681c80a4..HEAD -- corpus/SOURCES.md` → `2  0`.
* **Append-only gate** — `python3 tools/sources-append-only.py --from 681c80a4 --to HEAD --repo . --json`
  → `"violations": []`, `"added": ["S622","S623"]`, `"ok": true`. S620/S621 are byte-identical
  base→HEAD (`diff` of lines 375–376 → identical), so no existing row's immutable cells moved.

**The disagreement (F1) — the row says "four fields" about a struct that declares five.**
`gguf.md` lines 277–299, i.e. inside the row's *own* cited anchor range, declare **five** members:

```
277: struct gguf_header_t {
283:     uint32_t magic;
290:     uint32_t version;
294:     uint64_t tensor_count;
296:     uint64_t metadata_kv_count;
298:     gguf_metadata_kv_t metadata_kv[metadata_kv_count];
299: };
```

```
$ awk 'NR>=277 && NR<=300' gguf.md | grep -cE '^[[:space:]]+(uint32_t|uint64_t|gguf_metadata_kv_t) [a-z_]+'
5
```

So the scope cell ("the GGUF header is four fields") and the teaches cell ("the four struct
fields") are contradicted by the very lines the row anchors. The fifth member is the
variable-length `metadata_kv[]` array — which is exactly why the boundary table's class is
"KV-free" (`SKILL.md:2460`).

**What is NOT falsified:** the *step* count 4 is correct, and the table's `preamble = 4` term
recomputes from the probe independently of this row. `tools/kama-probe.sh` charges exactly four
preamble reads before the KV loop — `rd(4)` magic (line 720), `ver = u32()` (722),
`n_tensors, n_kv = u64(), u64()` (725) — and the `metadata_kv` array is walked entry-by-entry in
the separate KV loop (734), which is why KV-bearing files cost extra. So C3's arithmetic
(`steps = 4 + T x (5 + nd)`) and the `preamble = 4` term survive; the defect is confined to the
row's own field-count wording. Note the plan repeats the shape ("magic/version/tensor_count/
metadata_kv_count — the four preamble fields", `plans/round-98-claims.md:156`) and the freeze
receipt repeats it (`controls/sources-opened.out:5-6`), so the same wording is carried in three
places; only the *step* framing ("the four preamble fields") is safe, the *struct* framing
("the header is four fields" / "the four struct fields") is not.

Under `SOURCES-CONTRACT-v1` rule 2, `scope`/`teaches` are immutable in place — a correction is a
**new** row whose `teaches` opens `supersedes S622 —`, not an edit of S622. I did not edit the
lane; this is a finding for KamaR98 to land as a superseding row (or to fold into the M3
landing).

### S623 — **AGREE** on all checked properties (no disagreement)

`corpus/SOURCES.md:378`

| cell | content |
|---|---|
| kind / tier / status | `spec` / `C` / `rejected` |
| scope | "Whether the spec's naming-convention section states the GGUF header field order and widths a parser pays" |
| anchor | "Commit 57e2c2ca, section lines 21-27, same digest as S622, opened 2026-11-08: \"It is not intended to be perfectly parsable in the field due to the diversity of existing gguf filenames.\" (line 23)" |
| teaches | "REJECTED: filename provenance, not header layout, and grounds no step cost; flip: the section states header field order and widths" |
| used-by | `—` |

Verified:

* **Quote at the named line** — the sentence occurs verbatim in line 23 and is **unique** in the
  file (`grep -c -F 'It is not intended to be perfectly parsable in the field due to the diversity of existing gguf filenames.'` → 1; the same string at line 23 → 1). Note for the record: line 23 is the whole naming-convention
  paragraph and the quote is its trailing sentence, so the quote is a *substring* of line 23, not
  the entire line. That is the lane's own convention, not a slip of this row — S620's anchor
  quotes the fragment "Currently at most 4" from line 310, which is likewise a substring of a
  longer comment line. Both anchors are honest under the lane convention "the quote appears at
  the named line".
* **Digest** — the row points at the same URL/commit as S622/S620; my fetch of that URL returns
  `1dead27b6…`, so "same digest as S622" is correct. (S623 is the only row in the registry that
  writes "same digest as" — a traceability convenience, not a contract breach; the digest is
  recorded in S620 and S622 on the same URL.)
* **Rejection holds.** The flip condition is "the section states header field order and widths".
  Over the *whole* named section (lines 21–141, next `###` heading is line 142 `### File
  Structure`) there is no header-layout statement:
  `sed -n '21,141p' gguf.md | grep -inE 'header|magic|byte|width|field order|preamble|tensor_count|metadata_kv'` → no
  hits. Header layout is stated in a *different* section (File Structure, lines 277+), so the
  rejection is correctly scoped and the flip is unreachable within the cited section.
* **Contract mechanics** — 11 columns, no `|` in any cell, id is next unused, `rejected` rows are
  kept (rule: "a rejection is evidence of taste"), rejected-row `teaches` follows the mandated
  `REJECTED: <reason>; flip: <what would change the verdict>` shape, `used-by` = `—`, quote is
  19 words ≤ 25 (contract rule 1).
* **Minor note (not a disagreement):** the anchor says "section lines 21-27"; the real
  `### GGUF Naming Convention` section spans 21–141 (with a `####` sub-heading at line 56). The
  cited range brackets the quoted line 23 but understates the section. Same class of
  under-statement as the prior admitted S586 row ("File Structure lines 147-352" vs the real
  section 142–368), so it is lane convention rather than a new defect.

## 3. Contract rules for where the rows land (required step 3)

| rule | check | result |
|---|---|---|
| no `|` inside any cell | per-cell scan of lines 377–378 | **pass** (13 raw parts, 11 content cells each, no cell contains `|`) |
| 11 columns | `awk -F'|'` NF=13 → 11 content cells | **pass** (whole-file malformed count = 0) |
| append-only, S620/S621 unchanged | `git diff --numstat 681c80a4..HEAD -- corpus/SOURCES.md` = `2 0`; S620/S621 lines identical base→HEAD; `tools/sources-append-only.py --from 681c80a4 --to HEAD` → violations `[]`, added `["S622","S623"]`, ok `true` | **pass** |
| rejected row kept | S623 present, `status=rejected`, `teaches` = `REJECTED: …; flip: …` | **pass** |
| ids unique / next unused | base max id = 621; `awk … | sort | uniq -d` → empty | **pass** |
| census validate | `sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama` → **exit 0**, 0 E-codes, lane `ok` | **pass** |
| census row/tier delta | base 361 → HEAD 363 rows; tier.A 344→345, tier.B 11, tier.C 6→7; mined 324→325, queued 8, rejected 29→30 | **pass** — matches the plan's "361 → 363 (S622 admitted, S623 rejected)"; +1 A/mined = S622, +1 C/rejected = S623 |

### Same-URL-different-anchor duplicate situation against S620 (the specific question)

The `57e2c2ca…/docs/gguf.md` URL is now on **four** registry rows, not three:

| row | scope (distinct) | status | W04? |
|---|---|---|---|
| S586 (`:341`) | "Whether a GGUF file will load in llama.cpp b12177 (pre-load verdict rule)" | rejected | — (first claimant) |
| S620 (`:375`) | "That a GGUF tensor info is five fields … `5 + nd` reads per header …" | mined | yes (at base) |
| S622 (`:377`) | "That the GGUF header is four fields … four preamble steps …" | mined | yes (new) |
| S623 (`:378`) | "Whether the spec's naming-convention section states the GGUF header field order and widths …" | rejected | yes (new) |

The census distinguishes E04 (same URL **and** same scope, no `supersedes`) from W04 (same URL,
**across** scopes). All four scopes differ, so E04 cannot fire and only W04 fires — exactly the
standing warning class S620 and S621 already carried at base. `validate` exits 0 with **zero
E-codes**. The delta against the freeze-time receipt is exactly two lines:

```
$ diff .ufo/waves/round-98/controls/census-start.out <validate at HEAD>
121a122,123
> kama	W04	S622 duplicate url …/docs/gguf.md across scopes
> kama	W04	S623 duplicate url …/docs/gguf.md across scopes
123d124
< census_exit=0
```

**Conclusion on the census question: both new warnings are the known duplicate-URL warning
class, not a real defect.** No E-code fires; `S622` does not need and must not carry
`supersedes S620 —` (different scope, not a correction of S620, so contract rule 2 is not
engaged). No census warning in this round indicates a real defect.

## 4. Findings

**F1 — S622's scope/teaches mis-state the struct's field count (real defect; lands in the
M3/superseding-row path, not in the table arithmetic).**
`corpus/SOURCES.md:377` scope "the GGUF header is four fields" and teaches "the four struct
fields" vs. the five members of `gguf_header_t` at the row's own cited lines 277–299
(`magic` 283, `version` 290, `tensor_count` 294, `metadata_kv_count` 296, `metadata_kv[]` 298).
The step count 4 is right for the probe's preamble (`tools/kama-probe.sh:720,722,725`) and the
boundary table's `preamble = 4` term is unaffected; what is wrong is that a tier-A mined row
asserts the struct has four fields when opening its anchor shows five. Same wording is repeated
in `plans/round-98-claims.md:156` and `.ufo/waves/round-98/controls/sources-opened.out:5-6`.
Fix shape per contract rule 2: a new row whose `teaches` opens `supersedes S622 —` (scope/teaches
are immutable in place), or fold the correction into the M3 landing.

**F2 — the round-98 lesson's census tier histogram is the base histogram mislabelled "at HEAD"
(real receipt defect, in the same Gate block that carries S622/S623).**
`corpus/lessons/round-98.md:28-30` reads "tiers measured with the census at HEAD (361 rows:
A 344, B 11, C 6; mined 324, queued 8, rejected 29) against base (361: A 344, B 11, C 6;
mined 324, queued 8, rejected 29)". Measured:

```
HEAD  rows 363 | tier.A 345 | tier.B 11 | tier.C 7 | mined 325 | queued 8 | rejected 30
BASE  rows 361 | tier.A 344 | tier.B 11 | tier.C 6 | mined 324 | queued 8 | rejected 29
```

The "at HEAD" half carries the *base* numbers, so the lesson's tier sentence contradicts its
own row-count sentence four lines above ("Census before → after: 361 → 363 rows", `:25`).
[INFERENCE] The string is byte-identical to round 97's lesson line 28
(`corpus/lessons/round-97.md:28`, "at HEAD (361 rows: A 344, B 11, C 6; mined 324 …)") where it
*was* correct for that round — i.e. round 97's HEAD sentence was carried over without
re-measuring; the round-97 base was 358 rows, so "against base (361: …)" here is right.
Separately, the lesson cites `controls/census-end.out`, which does not exist in the lane yet
(`ls .ufo/waves/round-98/controls/` → six freeze-time files only); the plan lists it as a
measurement-time receipt, so the citation is a forward reference to be discharged with M1/M2/M3.

**F3 — the lesson mis-cites the round-97 precedent for the duplicate-URL warning (minor).**
`corpus/lessons/round-98.md:21-22`: "both rows carry the same URL as S620 with a different
anchor (standing W04 duplicate-URL warning, cross-scope, same as the round-97 S619 row)". As
written, the cited precedent does not exhibit the pattern: S619's URL is unique in the registry
(`grep -c 'b12177/gguf-py/README.md' corpus/SOURCES.md` → 1) and S619 carries **no** W04 line in
either round's census receipt (`grep -c 'W04	S619' .ufo/waves/round-97/controls/census-end.out`
→ 0; it is absent from the round-98 receipt too). The rows that *do* carry this warning are:

* **S620** — same `gguf.md` URL as the earlier **S586** (`corpus/SOURCES.md:341`, scope "Whether a
  GGUF file will load in llama.cpp b12177 (pre-load verdict rule)", rejected 2026-11-06); W04
  present at round-97 census-end (`census-end.out:120`) and at the round-98 freeze receipt
  (`census-start.out:120`). This is the direct ancestor of the two new warnings: the census emits
  W04 on the *second and later* rows of a URL under a new scope, and S586/S620/S622/S623 are
  that chain (S586 first, so S620, S622, S623 each warn).
* **S621** — same `ggml.h` URL as **S618**, W04 at round-97 census-end (`census-end.out:121`).

[INFERENCE] The likely intent was "the same as the round-97 **S620** row" (which did carry the
standing W04), i.e. a one-id slip; but as written the citation points at a row with a unique URL
and no warning. The lesson also says "the same URL as S620" while the URL now sits on **four**
rows (S586, S620, S622, S623) — S586 is the other claimant and is the row that made S620 warn in
the first place. Neither point changes a verdict: the W04s themselves are the known duplicate
class (§3, F4).

**F4 — no census warning in this round indicates a real defect.** See §3: the two new W04 lines
are the standing cross-scope duplicate-URL class; `validate` exits 0 with zero E-codes; the
delta from the freeze-time receipt is exactly those two lines.

**F5 — `S622`'s `used-by` names `SKILL.md`, which does not yet cite it (observation; discharged
at M3).** `grep -c 'S622' SKILL.md` → 0 today; the depth counter requires the string in the
`### Round 97 correction` section (`tools/round98-depth-boundary-audit.py:119`), which the M3
landing supplies. The row's `mined` status is honest under the contract ("cited by ≥1 path"):
`corpus/lessons/round-98.md` cites S622 (2 mentions, lines 17 and 20).

**F6 — anchor-range nits (observation, lane-consistent).** S622 "lines 277-300" vs the struct's
277–299; S623 "section lines 21-27" vs the real section 21–141. Both bracket the quoted line;
S620's "lines 305-325" is exact and S586 understates its section the same way, so this is
existing lane convention, not a round-98 defect.

## 5. Cross-check of the S622 grounding against the probe (why C3's table is unaffected)

`tools/kama-probe.sh` preamble, four charged reads (`need()` per read):

```
720:            if rd(4) != b"GGUF":      # magic
722:            ver = u32()               # version
725:            n_tensors, n_kv = u64(), u64()
```

→ preamble = 4 steps. The `metadata_kv[]` array is traversed in the *separate* KV loop
(`734: for _ in range(n_kv):`), each entry costing ≥4 more steps, which is why the boundary
table's class is KV-free (`SKILL.md:2460`) and why the row's *step* claim is right even though
its *struct-field* claim is not. Recomputation of the eight required rows from `MAX_STEPS =
5 000 000` (`tools/kama-probe.sh:584`), `steps = 4 + T x (5 + nd)`:

| T | nd | steps | verdict | overcharge (+1/header) |
|---|---|---|---|---|
| 833 332 | 1 | 4 999 996 | invalid | 5 833 328 → `-` |
| 833 333 | 1 | 5 000 002 | `-` | 5 833 335 → `-` |
| 900 000 | 1 | 5 400 004 | `-` | 6 300 004 → `-` |
| 700 000 | 4 | 6 300 004 | `-` | 7 000 004 → `-` |
| 555 555 | 4 | 4 999 999 | invalid | 5 555 554 → `-` |
| 555 556 | 4 | 5 000 008 | `-` | 5 555 564 → `-` |
| 800 000 | 1 | 4 800 004 | invalid | 5 600 004 → `-` |
| 520 000 | 4 | 4 680 004 | invalid | 5 200 004 → `-` |

The two new rows sit strictly inside the overcharge window (nd=1: 714 286 ≤ T ≤ 833 332;
nd=4: 500 000 ≤ T ≤ 555 555), and the overcharge class is ≥ +1 per header, so the window claim
recomputes. Nothing here depends on S622's field-count wording.

## 6. Scope note

The three frozen claims are L1's; this seat verified only the two sources and their registry
rows. `tools/round98-depth-boundary-audit.py` at HEAD prints
`DEPTH_BOUNDARY98 rows=6 checks=12 mismatches=4 met=False` (exit 1) — the expected pre-M3 state
(SKILL.md still has six rows and does not yet name S622), not a defect of the sources.

Tooling: no tool was installed or upgraded in this seat (no `uv tool install`, no `npx`, no
release binary, no `cargo install`, no pacman). Nothing to record on that account.

## 7. Files written / cleanup

* This report: `.ufo/waves/round-98/w1/SC02SourceReopen.md` (Report: path).
* Copy with receipts: `.ufo/waves/round-98/w1/out/SC02SourceReopen/SC02SourceReopen.md`,
  `.ufo/waves/round-98/w1/out/SC02SourceReopen/receipts.txt`.
* Scratch `/fast/scratch/hyaku/kama-r98/SC02SourceReopen/` (fetched `gguf.md`, base/HEAD
  `SOURCES.md` blobs, census outputs, evidence file) was deleted after the receipts were copied
  out. No clone or worktree was created; the only fetch artefact was the single 43 KB spec file.
