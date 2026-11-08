# SC02SourceReopen — independent re-open of the three round-97 sources + registry-row verification

Seat: SC02SourceReopen (leaf member, no dispatch). Lane: `kama-shokunin`.
Date: 2026-11-08. Verdict axes: operability, calibration, depth.

Scope: re-fetch the three sources round 97 writes to `corpus/SOURCES.md`; verify the S619/S620/S621
registry rows (id, kind, tier, anchor lines, ≤25-word quote + location, status, used-by); check the
contract rules (no `|` in any cell, 11 columns, append-only, S618 unchanged, S621's `teaches` opens
`supersedes S618 —`, rejected row kept); report any census warning that indicates a real defect
rather than a known duplicate.

**Bottom line: all three rows AGREE.** Every quote is verbatim at the named line, every digest
matches the freshly fetched bytes, the append-only rule holds by the lane's own checker, and the
rejected row is kept. The two census `W04` warnings that touch these rows are known duplicates, not
defects (see §5). One disclosure-grade nit is noted in §4.3 — it is *not* a defect in the frozen
claims.

---

## 1. Re-fetch: HTTP codes and sha256

Command (each, fresh, `curl -sS -L -o FILE -w '%{http_code}'`):

```
HTTP 200  1dead27b6a522709f0127d194e58c21dbbbf00ba1c64fe37c54d1a9048b05020  bytes=43175  https://raw.githubusercontent.com/ggml-org/ggml/57e2c2ca2a7cae756b1c4dfafa0cdfef9051d234/docs/gguf.md
HTTP 200  590e00a522b8791235353a8c7388d67ff2fe929554f1834c58528b82afd67392  bytes=119369 https://raw.githubusercontent.com/ggml-org/llama.cpp/b12177/ggml/include/ggml.h
HTTP 200  f759ed01b8899c392cee7f1bc9012356090dd46014898c2cface1cca5f1e18af  bytes=3339   https://raw.githubusercontent.com/ggml-org/llama.cpp/b12177/gguf-py/README.md
HTTP 404  d5558cd419c8d46bdc958064cb97f963d1ea793866414c025906ec15033512ed  bytes=14    https://raw.githubusercontent.com/ggml-org/llama.cpp/b12177/docs/gguf.md
```

All four match the lane's own freeze-time receipt `.ufo/waves/round-97/controls/sources-opened.out`
byte-for-byte (200/200/200/404, same digests, same byte counts). The 404 body is the literal
`404: Not Found` (14 bytes) — the rejected "llama.cpp `docs/gguf.md`" candidate in the round-97
Gate is honestly recorded as absent, not dressed up as a source.

Receipts: `out/SC02SourceReopen/fetch-receipts.txt`.

## 2. Per-row verdicts

### S619 — AGREE (rejected row, kept)

- id `S619`, kind `docs`, tier `C`, status `rejected`, used-by `—`, opened `2026-11-08`, recheck
  `on-release`. 11 columns, `NF=13`.
- Anchor: `Tag b12177, line 3, sha256 f759ed01…, opened 2026-11-08: "This is a Python package for
  writing binary files in the [GGUF](https://github.com/ggml-org/ggml/pull/302)" (lines 3-4)`.
- **Digest matches the freshly fetched bytes** (`f759ed01…18af`, 3339 bytes). ✓
- **Quote verbatim at the named line:** the quoted string is exactly line 3 of `README.md`; its
  continuation `(GGML Universal File) format.` is exactly line 4. Both inside the ±3 window. ✓
- `teaches` reads `REJECTED: documents the Python writer, not the file layout the probe parses, and
  grounds no step cost; flip: the page states the header field order and widths` — the contract's
  required rejected-row shape (`REJECTED: <reason>; flip: <what would change the verdict>`). ✓
- The row is **kept**, not deleted: a rejection is evidence of taste (CORPUS.md rule 2 / contract
  `status` semantics).
- Reason is true on the bytes: the full 99-line README documents the Python writer package
  (installation, `writer.py`/`reader.py`/`gguf_dump.py` examples, CI, TODO) and contains **no**
  statement of GGUF header field order or widths. The flip condition is not met. ✓
- Continuity note (not a defect): the round-96 lesson already carried this same rejection as a
  *prose-only* Gate line labelled `S619` (`corpus/lessons/round-96.md:16`). Round 97 promoted it to
  a registry row. The id was unused in the base registry (`grep -c S619` on the base blob = 0), so
  the id is not reused and no duplicate-id finding exists.

### S620 — AGREE (admitted spec row)

- id `S620`, kind `spec`, tier `A`, status `mined`, used-by `SKILL.md, corpus/lessons/round-97.md`
  (both paths exist on disk → census E11 clean). 11 columns, `NF=13`.
- Anchor: `Commit 57e2c2ca, lines 305-325, sha256 1dead27b…, opened 2026-11-08: "uint64_t
  dimensions[n_dimensions];" (line 313; "Currently at most 4" line 310)`.
- **Digest matches** the freshly fetched `docs/gguf.md` (43175 bytes, `1dead27b…5020`). ✓
- **Quotes verbatim at the named lines:** `"uint64_t dimensions[n_dimensions];"` is exactly line
  313; `"Currently at most 4"` is exactly line 310 (the source line reads `// Currently at most 4,
  but this may change in the future.`). The cited range 305-325 is exactly the
  `struct gguf_tensor_info_t { … };` block, five members as claimed: `name` (308), `n_dimensions`
  (311), `dimensions[n_dimensions]` (313), `type` (315), `offset` (324). ✓
- The scope/teaches claim is **arithmetically true of the source**: the struct's five fields are
  name (a `gguf_string_t` = `uint64_t len` + bytes, lines 232-237 → u64 read + skip = 2 steps),
  `n_dimensions` u32 (1 step), `nd` dims u64 (`nd` steps), `type` (`enum ggml_type : uint32_t`,
  line 154 → 1 step), `offset` u64 (1 step) → **2 + 1 + nd + 2 = `5 + nd`**, which is exactly what
  `tools/kama-probe.sh:747-752` prices (`skip(u64())` name = 2, `nd = u32()` = 1,
  `ne = [u64() for _ in range(nd)]` = nd, `tt, off = u32(), u64()` = 2). The spec's
  `n_dimensions` cap of 4 matches `ggml.h:222` `#define GGML_MAX_DIMS 4` and the probe's own
  `if nd > 4: return "invalid"`. ✓
- Tier `A` for a spec is correct under the contract's tier definitions (primary/authoritative for
  that scope; `spec` is an allowed kind).

### S621 — AGREE (append-only correction row)

- id `S621`, kind `code`, tier `A`, status `mined`, used-by `SKILL.md, corpus/lessons/round-97.md`
  (both exist). 11 columns, `NF=13`.
- Anchor: `Tag b12177, lines 695-697, sha256 590e00a5…, opened 2026-11-08: "nb[0] =
  ggml_type_size(type)" (line 697; "int64_t ne[GGML_MAX_DIMS];" line 695; S618's anchor line 690 was
  the struct header)`.
- **Digest matches** the freshly fetched `ggml.h` (119369 bytes, `590e00a5…7392`). ✓
- **Quotes verbatim at the named lines:** `"int64_t ne[GGML_MAX_DIMS];"` is exactly line 695;
  `"nb[0] = ggml_type_size(type)"` is exactly line 697 (the source line is
  `// nb[0] = ggml_type_size(type)`). ✓
- The parenthetical claim about S618 is **true on the bytes**: line 690 of `ggml.h` is
  `struct ggml_tensor {`, i.e. the struct header, not a field — so S618's `anchor` "line 690"
  pointed at the header while its quote is at 697. S621 records that correction inside its own
  anchor cell rather than editing S618 in place. ✓
- `teaches` opens exactly `supersedes S618 — ` (U+2014 em dash, then a space — verified by
  codepoint: `0x2014 0x20`), then the `5 + nd` arithmetic and the ceiling
  `(5 000 000 - 4) / (5 + nd)`. This satisfies CORPUS.md rule 2 exactly
  ("A correction is a new row whose `teaches` opens `supersedes S0NN —`"). ✓
- The ceiling arithmetic in the row **recomputes from the probe's `MAX_STEPS`**: with
  `MAX_STEPS = 5 000 000` and preamble 4, `(5 000 000 - 4) // (5 + nd)` gives 999,999 / 833,332 /
  714,285 / 624,999 / 555,555 for nd = 0…4 — identical to `SKILL.md:2434-2439`. ✓ (Receipt:
  `out/SC02SourceReopen/boundary-recompute.txt`.)

## 3. Contract rules

| Rule | Result | Evidence |
|---|---|---|
| No `|` inside any cell; 11 columns (`NF=13`) | **PASS** | `awk -F'|' '… && NF!=13 {n++}'` → `0` malformed rows across all 361 rows; census E01 clean, exit 0 |
| Append-only (`corpus/SOURCES.md`, rule `A-row`) | **PASS** | `python3 tools/sources-append-only.py --from 40763bd2 --to HEAD --repo .` → `added S619/S620/S621 (allowed)`, `no append-only violations`, exit 0; `--json` → `"violations": [], "ok": true` |
| S618 unchanged | **PASS** | `git show 40763bd2:corpus/SOURCES.md \| grep '^\| S618 ' \| sha256sum` == the same grep at HEAD → `ef78fece278cc32289838f7fa222151b835d9403e0c13e06a4813e0dc8efc935` (identical). The whole-file diff is `3 insertions(+), 0 deletions(-)` — three new rows, nothing edited |
| S621's `teaches` opens `supersedes S618 —` | **PASS** | `SOURCES.md:376`; codepoint check `0x2014 0x20` after `S618`; the C1 counter's own predicate `teaches.startswith("supersedes S618 —")` (em dash literal) evaluates `True` on the live row |
| Rejected row kept | **PASS** | S619 present, `status = rejected`, `teaches` in `REJECTED: …; flip: …` form, `used-by = —` |
| No duplicate ids; enum/tier clean | **PASS** | `uniq -d` on the id column → empty; tier/status/kind enum + community-at-A check → empty |
| Used-by paths exist (E11) | **PASS** | `SKILL.md` and `corpus/lessons/round-97.md` both present on disk; census validate exit 0, `kama ok` |
| Gate block carries URL / access date / ≤25-word quote + location per new row | **PASS** | `corpus/lessons/round-97.md:15-18`; quote word counts: S620 → 2 + 4, S621 → 3 + 2, S619 → 12 (all ≤ 25) |

Receipts: `out/SC02SourceReopen/contract-rules.txt`, `out/SC02SourceReopen/registry-verification.txt`.

## 4. Cross-checks that bear on the frozen claims

### 4.1 The `5 + nd` arithmetic is grounded in the *source*, not just the probe
S620 (spec) and S621 (code) each independently ground the per-rank element count; the `5 + nd`
price recomputes from the probe's own read sequence and matches both source rows' arithmetic (§2).
The six C3 boundary rows in `SKILL.md:2453-2458` recompute from `MAX_STEPS`:
`833,332@nd=1 → 4,999,996` (<=) · `833,333@nd=1 → 5,000,002` (>) · `900,000@nd=1 → 5,400,004` (>) ·
`700,000@nd=4 → 6,300,004` (>) · `555,555@nd=4 → 4,999,999` (<=) · `555,556@nd=4 → 5,000,008` (>) —
**every row agrees with the table as written**, with the `<=`/`>` split on the stated `5,000,000`.
This is a source-side confirmation of C3's arithmetic, independent of `tools/round97-depth-boundary-audit.py`.

### 4.2 The registry rows are what the C1 counter actually grades
`tools/round97-self-assessment-audit.py:167-186` (checks 10-11) reads S620/S621 out of
`corpus/SOURCES.md` via `sources_rows()` and asserts: S621 exists, `status == "mined"`,
`teaches.startswith("supersedes S618 —")`, `"5 + nd" in teaches`; S620 `kind == "spec"`,
`tier == "A"`, `status == "mined"`. I re-ran that indexing on the live rows: all five predicates
hold (`True`). The counter does **not** grade the anchor digests, the quote locations, or S618's
unchanged bytes — so those are graded here by the non-author re-open, which is exactly the
contract's rule 1 obligation ("Non-author verification re-opens a sample").

### 4.3 Disclosure-grade nit (not a defect; no claim is falsified)
`corpus/SOURCES.md:373` — **S618's `teaches` cell still says the false thing**: "…so 6 read/seek
steps per header is the budget against which MAX_STEPS is sized". This is *append-only-correct*:
CORPUS.md rule 2 freezes a corrected row in place and requires the correction to arrive as a new
row opening `supersedes S0NN —`, which is precisely what S621 does; the round-97 plan and lesson
both state "S618 stays `mined` as history (CORPUS.md rule 2: corrections are new rows)". The
contract permits it, so this is not a defect and it is not a finding against any frozen predicate.
The one residual risk worth naming: S618 remains `mined` with `used-by: SKILL.md`, and
`SKILL.md:2441` still cites S618 as the source of the round-96 per-rank table (whose prose is the
correct `5 + nd`, but whose source line points at the superseded row's anchor). A reader following
SKILL.md's round-96 citation lands on a row whose `teaches` says 6, one section before the
round-97 section that cites S620/S621. The round-97 correction section (`SKILL.md:2468-2470`) is
adjacent and explicit, so the tree is coherent; a future round should retire or re-point the
round-96 attribution when it next amends that section. I flag it as a **taste/traceability note for
the L1 to weigh**, not as a C1/C2/C3 defect — no frozen predicate grades it.

## 5. Census warnings on the three rows: known duplicates, not defects

`scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama` → exit 0,
`kama ok`, 122 output lines, all `W04`/`W01` warnings plus the ok line. Two warnings name the new
rows:

```
kama  W04  S620  duplicate url raw.githubusercontent.com/ggml-org/ggml/57e2c2ca2a7cae756b1c4dfafa0cdfef9051d234/docs/gguf.md across scopes
kama  W04  S621  duplicate url raw.githubusercontent.com/ggml-org/llama.cpp/b12177/ggml/include/ggml.h across scopes
```

Both are the **known-duplicate class, not real defects**, for reasons that are checkable:

- **S620 vs S586** — same URL (`ggml/57e2c2ca/docs/gguf.md`), different scope. S586 is the *rejected*
  row ("describes the format, not what the b12177 loader enforces"); S620 is the *admitted* row for
  a different question (the tensor-info struct's field count). Two scopes on one document is the
  registry's designed shape, not duplication. The census's `E04` rule (same URL **and** scope
  without a `supersedes` clause) does not fire — confirmed by exit 0 and the absence of any E-code.
- **S621 vs S618** — same URL (`llama.cpp/b12177/ggml/include/ggml.h`), different scope, and S621 is
  the declared correction of S618 with the `supersedes S618 —` opener, which is exactly what the
  `E04` exemption in the census looks for. Same document, two scopes, one of them the correction of
  the other.
- The same URL also appears earlier under S058 (`ggml/da8e2a54/docs/gguf.md`) — I fetched that URL
  and its bytes are **identical** to the `57e2c2ca` copy (`cmp` → identical, same sha256
  `1dead27b…`), so the "two commits" are the same document content at two pins; that is another
  known-duplicate warning shape, not a defect.

The lane's own census exit status is 0 with `kama ok`; there is **no E-code** against any of the
three rows, and the only `W01` in the lane output (`S481 tierC mined used-by=…`) is a pre-existing
round-43-era row untouched by round 97.

Census row counts: base `40763bd2` = **358** rows → HEAD = **361** rows (+3, exactly S619/S620/S621),
with `status.rejected` 28 → 29 and `status.mined` 322 → 324. The plan's "rows 358 → 361" claim is
**true** and independently reproduced.

Receipts: `out/SC02SourceReopen/census-receipts.txt`.

## 6. Findings summary

| # | Item | Verdict |
|---|---|---|
| F1 | S619 row (kind/tier/status/used-by/quote/digest) | **AGREE** — verbatim at line 3, digest matches, rejection shape correct, row kept |
| F2 | S620 row | **AGREE** — five-field struct at 305-325 confirmed, both quotes verbatim at 310/313, digest matches, `5 + nd` recomputes |
| F3 | S621 row | **AGREE** — quotes verbatim at 695/697, digest matches, `supersedes S618 —` opener present with the right em dash, ceiling recomputes from `MAX_STEPS` |
| F4 | Contract rules (11 cols, no pipe, append-only, S618 unchanged, rejected kept, no dup ids, E11) | **PASS** — lane's own `tools/sources-append-only.py` reports `ok: true`, `violations: []` |
| F5 | Census `W04` on S620/S621 | **KNOWN DUPLICATE, not a defect** — different scopes; the correction row carries the `supersedes` opener the `E04` exemption expects |
| F6 | Round-97 Gate block (URL, access date, ≤25-word quote, location per new row) | **PASS** — all present, all quotes ≤ 12 words |
| F7 | S618's stale `teaches` cell + SKILL.md:2441's attribution to S618 | **NOT A DEFECT** (append-only-correct; S621 supersedes) — a **traceability note** for the L1: the round-96 section still points at the superseded row's anchor one section before the correcting citation |
| F8 | C3's six boundary rows recompute from the probe's `MAX_STEPS` | **AGREE** — all six step sums and `<=`/`>` splits match `SKILL.md:2453-2458` exactly |

## 7. Remaining unknowns / limits of this seat

- I verified the *three* sources round 97 names plus the rejected-path 404. I did **not** re-open
  the other 358 registry rows, and the census's `W04` set (≈110 same-URL-different-scope warnings)
  was not individually adjudicated row by row — only the two that name S620/S621.
- The `≤25-word quote` rule is applied to the round-97 `## Gate` table; the `SOURCES.md` anchor
  cells carry longer text (digest + quote + location) by design, which is the file's own format.
- Whether the round-96 attribution in `SKILL.md:2441` should be re-pointed (F7) is a curation call
  for L1 `KamaR97`, not a predicate I can settle from source evidence.

## 8. Tooling

No packages installed, upgraded, or removed this seat; no host service touched; no `pacman`
invocation (pacman is paused host-wide). Tools used, all pre-existing on the host:
`curl 8.23.0`, `python3 3.14.8`, `git 2.56.0`, `GNU Awk 5.4.1`, plus the lane's own
`tools/sources-append-only.py` and the fleet's `scripts/sources-census.sh`. No network fetch
outside the three declared URLs plus the one 404-path check and the S058 pin comparison
(`da8e2a54`) used to classify the `W04` warnings.

## 9. Bounds honoured

- Wrote only under the two paths my seat spec names: receipts in
  `.ufo/waves/round-97/w1/out/SC02SourceReopen/` and this report at
  `.ufo/waves/round-97/w1/SC02SourceReopen.md` (the `Report:` trailer path, relative to the lane
  root, as specified).
- Scratch `/fast/scratch/hyaku/kama-r97/SC02SourceReopen/` created for the fetched bytes, the base
  registry snapshot and the receipt generation; **removed before this report was finalised**
  (`shutil.rmtree` in the finalisation step).
- No tracked lane file edited; no `git add/commit/stash/checkout/switch/reset/pull/push`, no mutating
  `jj`. Git use was read-only (`rev-parse`, `log`, `show`, `diff`, `ls-files`, `cat-file`).
- No fixture repo was needed (no commits, no `mktemp -d` repos), so no toplevel assertion was
  required; the only scratch repo interaction was `git show <rev>:corpus/SOURCES.md` into scratch.
- Nothing written outside the lane's `.ufo/waves/round-97/w1/` subtree and my scratch dir; the
  fleet repo's tracked files (`LOG.md`, `SCORECARD.md`, `MANIFEST.json`, …) were not touched.
