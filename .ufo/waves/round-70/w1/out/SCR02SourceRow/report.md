# SCR02SourceRow — report (round 70, w1, lane kama)

Seat: `SCR02SourceRow` — advisory leaf, read-only on the lane. Nothing under
`/home/vgpnk/Projects/shokunin/kama-shokunin` was modified; every write is inside
`.ufo/waves/round-70/w1/out/SCR02SourceRow/` (plus the Report-trailer file named in §7).
No commit, no `git add`, no jj mutation, no subagents.

Measured tip: `0e14facd0c619f45a6461821d2bd80ddac9855b1` (HEAD, `git rev-parse HEAD`);
frozen round-start base `6035e952c2521999e192d6f236331f265ac98392` is an ancestor
(`git merge-base --is-ancestor` → exit 0). Lane `corpus/SOURCES.md` at measure time:
sha256 `f04caae05fa5eeb7f09d969cc15eb6cb054a6a1f5aee067929f390acb1ebe0f6`,
blob `f87e815319c2f8dc60fe5dc0f763862bcf2bc6d0`, 281 registry rows, `S542` absent
(`grep -c 'S542'` → 0, exit 1).

Environment: Linux 7.2.11-arch1-1, python3 3.14.8, curl 8.23.0, GNU Awk 5.4.1, bash 5.3.20.
Tool installs/upgrades: **none** (nothing was needed; no pacman, no uv/npx).

## 1. Commands, outputs, exit codes

### 1.1 Registry id derivation

```
$ grep -oE '^\| *S[0-9]+' corpus/SOURCES.md | tail -1
| S541
$ grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md
281
$ grep -n '^## ' corpus/SOURCES.md | head -3
9:## Registry
298:## Paths
309:## Search log
```

Next id = **S542**. Registry section spans lines 9–297; last table row is line 293.

### 1.2 Fetch (retained bytes)

```
$ curl -sSL --max-time 30 -w 'HTTP:%{http_code} SIZE:%{size_download} URL:%{url_effective}\n' \
    -o pytest-exit-codes.html https://docs.pytest.org/en/stable/reference/exit-codes.html
HTTP:200 SIZE:25787 URL:https://docs.pytest.org/en/stable/reference/exit-codes.html
EXIT:0
$ sha256sum pytest-exit-codes.html
a403306a1d763fc8123749544905dd64e8e0cfa5ed46a416679001c3142e3977  pytest-exit-codes.html
```

Retained at `.ufo/waves/round-70/w1/out/SCR02SourceRow/source/pytest-exit-codes.html`
(25787 bytes, sha256 above; copied, not linked — `sha256sum` of the retained copy is the same
string). Stripped-text derivative: `source/pytest-exit-codes.txt`, 3099 bytes, sha256
`61978456441037deafad7f99593e3f3cd3efa2036c8624eacce7139bb4c4b572`.

Response headers (`curl -sSI`, exit 0), abbreviated to the freshness fields:

```
HTTP/2 200
date: Tue, 03 Nov 2026 23:48:53 GMT
etag: W/"dcccfb52d0fbf192adbde399f77ff99c"
last-modified: Tue, 27 Oct 2026 21:36:00 GMT
x-amz-meta-mtime: 1793136756.032975742
cf-cache-status: HIT
```

`cf-cache-status: HIT` means the served bytes may be a CDN copy of the 2026-10-27 build; the
sha256 pins what was actually read, which is what the row cites.

### 1.3 Quote location (tag-strip, byte-exact)

Extraction rule: remove `<script>/<style>`, remove comments, remove all tags (replaced with the
empty string), unescape entities, collapse `\s+` to one space. Raw HTML at the located section:

```
Exit code 5<span class="colon">:</span></dt>
<dd class="field-even"><p>No tests were collected</p>
```

```
$ python3 verify-quote.py; echo EXIT=$?
PATH …/SCR02SourceRow/source/pytest-exit-codes.html
SHA256 a403306a1d763fc8123749544905dd64e8e0cfa5ed46a416679001c3142e3977
MATCH 7 words: Exit code 5: No tests were collected
MATCH 10 words: Exit code 0: All tests were collected and passed successfully
MATCH 10 words: The exit codes being a part of the public API
EXIT=0
```

Negative arms (same session): with `No tests were collected` → `No tests were gathered` and the
expected-hash constant swapped so the matcher runs, output is
`MISS  7 words: Exit code 5: No tests were collected` and `MISS_ARM_EXIT 1`; without the hash swap
the script exits 1 at `SHA256_MISMATCH`. The matcher is not vacuous.

### 1.4 Registry validation (fleet validator on a scratch mirror)

The lane has **no** `scripts/` directory at the tip, so the fleet copy was used:
`/home/vgpnk/Projects/shokunin/scripts/sources-census.sh` (usage header: exit 0 clean/warnings,
1 E/overdue, 2 usage/missing registry). The mirror (`/fast/scratch/.../lane3`) is a symlink farm
whose `corpus/knowledge`, `corpus/lessons`, `.ufo`, `SKILL.md`, `SCORECARD.md`, `tools`,
`registry`, `tests` resolve to the real lane; only `corpus/SOURCES.md` is a real scratch copy.
Lane `corpus/SOURCES.md` sha256 was checked before and after every run (`lane_unchanged=yes`).

```
# V1 — unmodified registry copy
$ bash /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate \
    --file "$S/lane3/corpus/SOURCES.md" --today 2026-11-03
file	ok	/fast/scratch/hyaku/kama-r70/SCR02SourceRow/lane3/corpus/SOURCES.md
EXIT=0        # W04=104, W01=1 (pre-existing)

# V2 — + candidate S542 row, corpus/lessons/round-70.md NOT present
file	E11	S542 missing used-by corpus/lessons/round-70.md
file	W04	S542 duplicate url docs.pytest.org/en/stable/reference/exit-codes.html across scopes
EXIT=1

# V3 — + S542 row, scratch lesson stub present (fixture only)
file	ok	/fast/scratch/hyaku/kama-r70/SCR02SourceRow/lane3/corpus/SOURCES.md
EXIT=0        # W04=105, W01=1

# V4 — Option A: S052 used-by += corpus/lessons/round-70.md, lesson stub present
file	ok	/fast/scratch/hyaku/kama-r70/SCR02SourceRow/lane3/corpus/SOURCES.md
EXIT=0        # W04=104, W01=1 (no new warning)
```

Receipts (copies of the run output, byte-for-byte): `evidence/validate-baseline.out`,
`evidence/validate-s542-nostub.out`, `evidence/validate-s542-withstub.out`,
`evidence/validate-s052-withstub.out`. Each run's `file …` line names the scratch mirror because
that is the file the validator actually read; the mirror was deleted at seat end, and the receipt
bytes are preserved under `evidence/`.

Row-shape checks:

```
$ awk -F'|' '{print "NF="NF}' evidence/row-s542.txt
NF=13
$ grep -c $'\t' evidence/row-s542.txt
0
$ grep -c 'S542' /home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md
0            # exit 1; the lane registry does not contain the candidate
```

## 2. Findings

1. **The URL is already registered: S052** (`corpus/SOURCES.md` line 64), same URL, scope "how one
   widely used test runner keeps 'nothing was collected' distinct from 'collected and failed' …",
   `status mined`, `opened 2026-10-20`, `recheck on-release`, used-by
   `corpus/knowledge/llamacpp-loading-lifecycle.md, corpus/lessons/round-18.md`. S052 carries **no
   retained bytes and no sha256**.
2. **Contract mechanics, measured:** `E04` keys on URL **+ scope**; a different scope cell yields
   only `W04 duplicate url … across scopes` (warning; exit unchanged). Same-scope text would need
   `supersedes S###` in `teaches` to avoid E04. Hence Option B (new row, distinct scope) is legal
   and lands one W04; Option A (extend S052's used-by) lands no new warning at all.
3. **E11 is the only landing dependency:** a `mined` row's `used-by` paths must exist on disk;
   `corpus/lessons/round-70.md` does not exist yet, so the row alone is red (V2) and green only with
   the lesson at the same tip (V3). `SCORECARD.md` already exists.
4. **The quote is byte-exact and the page declares its own authority:** “The exit codes being a
   part of the public API” (same retained bytes), which is the tier-A justification for a page that
   states no pytest version.
5. **Freshness:** page `last-modified 2026-10-27T21:36:00Z`, fetched 2026-11-03T23:48:53Z,
   sha256 `a403306a…3977`. The page has no version string, so `on-release` is a cadence, not a pin
   (same limitation S052 records).

## 3. Exact bytes the L1 must land

- **Option B (recommended, matches the freeze's one-row frontier step):**
  `evidence/row-s542.txt` — one line, 949 bytes, 11 cells, no pipe inside a cell — inserted as new
  line 294 of `corpus/SOURCES.md`, immediately after `| S541 | …` (line 293), inside `## Registry`
  (lines 9–297). Row count 281 → 282. Never at EOF (E12; round-69 mistake 10).
- **Option A (only if no new row is wanted):** `evidence/row-s052-extended.txt` — replace S052's
  line 64 with these bytes (only the `used-by` cell changes).

## 4. What I could not verify

- Cannot verify a landed state: no write to the lane, no commit, no census run over the real tip.
- Cannot verify `corpus/lessons/round-70.md` will exist at the landing tip; E11 is conditional on it.
- Cannot verify a pytest version for the page (none is stated; not inferred).
- Cannot verify that CDN bytes equal the origin's 2026-10-27 build beyond the sha256 of what was served.

## 5. Mistakes made in this seat (disclosed, none affected the lane)

- First mirror attempt used `cp -al` (hard links): failed `Invalid cross-device link` between
  `/fast/scratch` and the home filesystem, producing a huge stderr dump and no usable mirror.
- First working mirror lacked `corpus/knowledge`, `corpus/lessons` and `.ufo`, so E11 fired ~300
  times on pre-existing rows; that harness was discarded. Fix: symlink the real subdirectories and
  the real `.ufo`, then the baseline validated clean.
- One `cp` into the mirror went through a symlink to the real `corpus/SOURCES.md` and was refused
  with "are the same file"; the lane file's sha256 was re-checked immediately (`lane_unchanged=yes`).
  Lesson: in a symlink farm, replace the target file with `rm` + `cp`, never `cp` over the link.

## 6. Files in this out dir

```
report.md                 this file
sources-row.md            the 11-column row, insertion point, contract/validator receipts
gate-block.md             the lesson ## Gate row (quote, sha256, tier-A and C2 scope sentences)
verify-quote.py           re-derives the three quotes from the retained bytes (exit 0/1)
source/pytest-exit-codes.html   retained fetched bytes (25787 B, sha256 a403306a…3977)
source/pytest-exit-codes.txt    tag-stripped derivative (3099 B, sha256 61978456…b572)
evidence/row-s542.txt                  candidate row bytes (Option B)
evidence/row-s052-extended.txt         used-by-extended S052 line bytes (Option A)
evidence/validate-*.out                validator runs V1–V4
```

## 7. Report trailer

`Report:` names `.ufo/waves/round-70/w1/out/SCR02SourceRow.md`; that file was written at exactly
that lane-relative path and repeats the findings and the two landing options (the detailed command
log stays here).
