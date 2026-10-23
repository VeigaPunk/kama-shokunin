# C1 counter review — findings (ReviewCounterCode)

Reviewed: `.ufo/waves/round-29/count-c1.py` (frozen, sha256 `fe11d599…b647383` verified
against preregistration; line references below are to that file). Claim C1 (calibration),
pre-data counter review of 69 base statements (11 false at W per before/c1-base.json).

**Verification performed (all evidence reproduced, nothing fabricated):**
- Fresh clone of the lane repo under `/fast/scratch/hyaku/kama-r29/w1/ReviewCounterCode/clone`;
  reran the frozen counter at base (`--tip 2aa46e2… --list`): output identical to
  `before/c1-base.json` — statements 69, by_class C27 H2 N2 P10 Q25 T3, mismatch 11,
  mismatch sids+observed identical. Determinism confirmed.
- Live lane master tip `513eba3ba51a` currently measures `mismatched_at_base 11
  append_only True valid_corrections 11 false_corrections 0 unresolved 0 met True`
  (rows introduced by commit 513eba3b, "round-29: C1 data (11 appended self-assessment
  correction rows)"); all 11 rows parse to exactly the canonical sids/observed.
- Unit/behavior tests imported the frozen module and ran `corrections`, `measured_cells`,
  `nlines`, regexes, and `check` against the clone; env-injection runs below.

---

## Findings by severity

### HIGH — env sanitization is incomplete; `met` is flip-able by the caller environment

`git()` (count-c1.py:78-87) strips `GIT_DIR`, `GIT_WORK_TREE`, `GIT_INDEX_FILE`,
`GIT_OBJECT_DIRECTORY`, `GIT_ALTERNATE_OBJECT_DIRECTORIES`, `GIT_REPLACE_REF_BASE`, and
sets `GIT_NO_REPLACE_OBJECTS=1` + `--no-replace-objects`. It does **not** strip (or
neutralize):

1. **`GIT_LITERAL_PATHSPECS`** — turns the Q-class pathspec exclusions
   `:(exclude)SCORECARD.md|SHONEN.md|LOG.md|corpus` (const lines 69-70, used in
   `check()` Q branch ~line 278) into literal paths, so `git grep -F` finds every Q span
   in SCORECARD.md **itself at W** (each Q line's own text exists at its writing commit).
   - Trigger: `GIT_LITERAL_PATHSPECS=1` on the same clone/tip. Result: the 7 Q
     mismatches flip to `holds=True`; mismatched_at_base drops 11 → 4.
   - **met-flip demo**: clone2 with SCORECARD.md = base + the 4 P correction rows
     committed. Clean run: `mismatched_at_base 11 valid_corrections 4 unresolved 7 met
     False`. Same clone/tip with `GIT_LITERAL_PATHSPECS=1`: `mismatched_at_base 4 valid
     _corrections 4 unresolved 0 met True`.
   - So the environment can make `met` **True wrongly** (on data that a clean run
     resolves to 7 unresolved) and a polluted runner's observed strings/needed-row set
     diverge from canonical.
   - Kins: `GIT_PATHSPEC_FROMFILE` (same class), `GIT_CONFIG_*`/`GIT_CONFIG_COUNT`.

2. **`GIT_CONFIG_COUNT`/`GIT_CONFIG_KEY_*`/`GIT_CONFIG_VALUE_*`** — env-level git config
   injection. Demonstrated with `blame.ignoreRevsFile` → `.git-blame-ignore-revs`
   (created in the clone) listing W `ea72c3ea…`:
   - Result: 8 statements get a different W (`83bee7fa…`), mismatch count 11 → 15, and
     observed strings change (e.g. `SCORECARD.md:H:cda32b698f:0` holds `md5=1f81e859…`
     at canonical W but fails `md5=61e82ee2…` at the shifted W; two Q spans flip to
     `q:no-artifact`). A seat correcting from a polluted run would produce rows that are
     false under a clean run (wrong W basis → wrong observed), i.e. met False / false
     corrections on the canonical measurement.
   - Also `blame.markUnblamableLines`, `core.attributesfile`, etc. are injectable.

3. **`GIT_COMMON_DIR`** (and `GIT_NAMESPACE`) — redirect ref resolution. Demo:
   `GIT_COMMON_DIR=/nonexistent/common` ⇒ `tip … unresolved` → exit 2
   (`could-not-evaluate`): honest runner with a lingering variable cannot evaluate (met
   False wrongly / no verdict).

Net: the counter's "reads committed objects only" guarantee holds for replace refs, but
the verdict is **not environment-independent**. The canonical run must be executed in a
cleansed env (no `GIT_*` beyond the six already stripped); recommend the L1 pin an
explicit clean env for the final measurement (cannot be fixed in the frozen counter; this
is a disclosed limit).

### MEDIUM — P-class bare-basename pointers are checked at the repo root (2 of the 11 mismatches are arguably true statements)

`RE_P` (line 65) captures whatever path token starts at a match position; it does not
resolve bare basenames to their real directory. `in_lane` (137-138) accepts a bare
basename. `check()` P (255-264) probes `W:<path>` at the repository root.

- Base line 740, `SCORECARD.md:P:312b3e69b1:0` token `round-17-verifier-spotcheck.md:217–221`
  → `p:absent`. The intended referent `corpus/lessons/round-17-verifier-spotcheck.md`
  **exists at W=c6dc46fa with 276 lines** (≥221) — verified via
  `git cat-file -e c6dc46fa:corpus/lessons/round-17-verifier-spotcheck.md` and line count.
- Base line 1375, `SCORECARD.md:P:17a7db7c81:0` token `count-c1.py:384` → `p:absent`;
  the lane file `.ufo/waves/round-26/count-c1.py` exists at W=d183ec57 (root
  `count-c1.py` does not).
- Effect: these statements are counted false (correction rows required with observed
  `p:absent`) although the stated pointer plausibly holds. The master data rows (commit
  513eba3b) already record these causes ("bare file name; the lane file is .ufo/…") —
  consistent with the counter, but the statements are arguably true under directory
  resolution. Calibration disclosure; a policy that "corrects" by resolving the real
  path would write observed `ok` → false correction (met False on that row).

### MEDIUM — docstring failure labels ≠ actual printed observed strings (latent this round)

Docstring (lines 20-44) and predicate name fail labels `p:beyond-eof`, `n:count`,
`h:digest`, `c:not-ancestor`; `check()` actually prints `eof=N`, `newlines=…`;
unterminated=…`, `<algo>=<hex>`, `commit=<full-sha> not-ancestor` (verified: C
not-ancestor prints `commit=2aa46e2… not-ancestor`; H bad prefix prints
`sha256=7af59c…`; N prints `newlines=1441 unterminated=false`). Currently **all 11 base
mismatches are P/Q** whose labels coincide (`p:absent`, `q:no-artifact`), so this cannot
trigger in-round; a future/extended use keying on the docstring labels would write wrong
observed values → false corrections.

### MEDIUM — silent non-extraction gaps (statements invisible; nothing checked)

Each is a base-fixed extraction behavior (affects the 69/11 set, not the tip-dependent
verdict, but shapes which rows are required):
- **Uppercase hex digests/tokens are never extracted**: `RE_HN` (71), `RE_HEX` (73),
  `RE_CWORD` (74) accept only `[0-9a-f]`. `H` with an uppercase digest matches only the
  path (no H statement); `commit 1E41928ABA` yields no C; a cell with an uppercase SHA
  yields no C.
- **`RE_CWORD` binds only `word [backtick?] hex`**: `measured: 1e41928…` (colon) and
  `commit: …` produce no C. `measured_cells` covers `Measured commit:` lines (exact
  case) and table columns only.
- **`RE_T` (72) misses `~` without space/T**: `2026-10-19~10:00Z` not extracted;
  `T~`/` ~` forms are. Invalid calendar values reach `strptime` (below).
- **`RE_P` range stops at first colon**: `file.md:12:34` → `file.md:12` (end=12);
  trailing `:34` ignored.
- **41-hex tokens match nothing** (`RE_HEX` lookahead rejects), so an over-long hex in a
  Measured cell is silently ignored.
- **`measured_cells` (140-157)**: a data row whose cells are all dashes/colons/spaces
  (`| - | - |`) is treated as the separator row and skipped; an escaped pipe in a cell
  (`val \| more`) shifts columns — demo produced a garbled token `more`` for the C cell;
  `Measured commit:` matching is case-sensitive; header phrase variants
  (`Measured-commit`, doubled spaces) are missed.

### MEDIUM — T-class invalid dates crash the whole run (latent; cannot trigger at the frozen base)

`check()` T (267-272) uses `calendar.timegm(strptime(...))`. `strptime` ValueError for
e.g. month 13 (`2026-13-45T99:99:99Z` — verified raises), caught by `main()` → exit 2,
whole evaluation fails. Seconds 60 are accepted by `strptime` (no crash; treated as 60).
No base statement currently matches an invalid date, so untriggerable in this round but a
latent fragility (a future frozen base with a typo'd date would hard-fail the claim).

### LOW — correction-row parsing strictness (formatting traps; all verified)

`corrections()` (286-299): rows are only recognized under the exact heading
`## Round 29 — self-assessment corrections` (em dash), starting at column 0, with `|`
at column 0.
- Silent-ignore traps (rows unseen → valid=0 → the 11 stay unresolved, met False wrongly
  for a well-intentioned policy): hyphen `-` instead of em dash; trailing ` ##`; leading
  space before `##`; indented rows (` | SA29:…`); rows without the leading `|`.
- Wrong-value traps (row parsed but false): escaped pipe in the observed cell (last cell
  becomes the post-pipe fragment); empty last cell (observed `""`); extra trailing column
  (observed becomes the extra cell); `SA29: sid` with embedded space (sid `" sid"` not in
  mism).
- Backtick-wrapped first/last cells are stripped (OK); rows inside a fenced code block
  under the heading are counted (doc-example trap — a policy that documents an example
  row in a fence would create a real row).
- All are consistent with the predicate's literal format; the exact heading/row grammar
  is documented in the docstring, so RefPaste is safe.

### LOW — output/exit behaviors

- Receipt overwrite refusal (`main()` ~349-353): exit 2 + stderr message; the **old
  receipt file is left in place** — a harness that ignores stderr may read a stale (old
  tip / old counts) receipt and treat it as fresh.
- Exit 2 doubles as "could not evaluate" and "refused to write" — callers cannot
  distinguish without parsing stderr.
- Unhandled errors outside the try block (receipt JSON/write failures, e.g. disk full)
  produce a traceback and exit 1 (undocumented).
- `counter_sha256` is the running file's self-hash; the counter never compares it to the
  frozen `fe11d599…` — tamper detection depends on the runner comparing.
- `blame()` (126-135)/line alignment: `len(revs) != len(lines)` → RuntimeError → exit 2
  (safe); strict UTF-8 `decode()` on blobs — a non-UTF-8 base file would fail evaluation
  (latent; base is UTF-8).
- Duplicate-sid guard (`main()` ~329-330) is dead code — sids are provably unique
  (line-hash + occurrence + class-index); harmless.
- SHONEN.md contributes **0 statements** at base (all 69 from SCORECARD.md) — verified;
  the empty contribution is handled cleanly.
- Default `--repo` is the live lane checkout; the command spec mandates a fresh clone
  (runner responsibility).

## met-flip summary

| Defect | trigger | met True wrongly | met False wrongly |
|---|---|---|---|
| GIT_LITERAL_PATHSPECS / pathspec exclusions bypassed | env var set | YES (demo: 4-row tip met=True vs clean met=False) | — |
| GIT_CONFIG_* blame/attrs injection | env config | — | YES (W/observed shift → rows false on canonical run) |
| GIT_COMMON_DIR / GIT_NAMESPACE | env var set | — | YES (tip unresolved → exit 2) |
| correction-row formatting strictness | non-exact heading/rows | — | YES (rows ignored → 11 unresolved) |
| P basename root-resolution | base statements 740/1375 | — | (2 statements arguably true but counted false — workload inflation, not verdict) |
| docstring-vs-printed observed labels | only if H/N/T/C mismatches arise | — | latent |
| T invalid date crash | only if a base statement carries one | — | latent |

## Residual risk / verification gaps

- Replace-ref end-to-end fuzz not run; the dual mechanism (`--no-replace-objects` arg +
  `GIT_NO_REPLACE_OBJECTS=1` + stripped `GIT_REPLACE_REF_BASE`) is the documented
  complete disable, and the CtlObjectStore control is expected to fail under it.
- Repo-level `objects/info/alternates` are not disabled (not env-disableable; they are
  part of the measured clone — a clone with foreign alternates is out of the command
  spec's "fresh clone" contract).
- Git grep binary-blob matching: `grep -q` counts a match in a binary blob at W as
  evidence (predicate says "any blob" — consistent).
- The live-master met=True observation (11 valid rows, commit 513eba3b) is reported as
  observed state; the verdict's validity depends on the runner's environment being clean
  per the HIGH finding above.

Evidence artifacts (scratch): `/fast/scratch/hyaku/kama-r29/w1/ReviewCounterCode/`
(`clone`, `clone2`, `fresh1.json`, `fresh_lp.json`, `fresh_cfg2.json`, `fresh_c2_clean.json`,
`fresh_c2_lit.json`, `fresh_gcd.json`, base blob dumps). No lane/fleet files were
modified; no installs performed.
