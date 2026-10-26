# V1Tool — code review of tools/append-only-audit.py v3 (round 48, C1)

Verdict: **no calibration defect found** — the v3 diff implements its docstring and the C1
counter's frozen v3 definitions correctly on every reviewed point (hunk-header positions
incl. `-0,0`/`+0,0`/no-final-newline markers, parent-side sections, per-event eligibility,
region union, `--files` mode, `declaration()` failure paths, determinism, lane performance
0.93 s); four low-severity robustness defects remain where the tool crashes with an uncaught
exception (exit 1 + traceback) instead of the docstring-promised exit 2, all outside what the
frozen counter/lane can reach, plus one stale docstring sentence.

Reviewed: `git diff 33e005827742b29772b153cda036ec9f27f653be..380bcdff9c8af06997c482f6eb03db926a794a2b -- tools/append-only-audit.py`
(340 insertions, 50 deletions; 898-line v3 file), against the frozen contract sources
`tools/round48-append-audit-v3-check.py` (docstring + `recompute()`, `del_positions()`,
`row_binds()`) and `registry/append-only-contract.tsv`. Every case below was executed on a
minimal fixture repo under my scratch; full transcript with line numbers:
`.ufo/waves/round-48/w1/out/V1Tool/evidence-log.txt` (driver: `run_all.py` there; tool copy:
`tool-at-380bcdff.py`). The wave commit b85783e8 does not touch the tool (diff --stat: only
`.ufo/waves/round-48/w1/*`), so the working-tree file equals the tip blob.

## Findings (by severity)

### 1. LOW — `Repo.blobs` cannot encode non-UTF-8 path bytes: uncaught UnicodeEncodeError, exit 1 instead of promised exit 2
- Site: `tools/append-only-audit.py:309` — `inp=("\n".join(specs) + "\n").encode()`; specs
  contain paths decoded with `surrogateescape` at `:244`/`:352`, which `.encode()` (utf-8
  strict) rejects.
- Command: fixture repo with `corpus/lessons/x\xff.md` (30 lines, then 25 deleted) matching
  contract row `corpus/lessons/*.md`; `python3 tool-tip.py --repo F --to <c> --json`.
- Observed: exit 1, `UnicodeEncodeError: 'utf-8' codec can't encode character '\udcff' ...`
  (evidence-log X2). Expected per docstring `:96` ("2 could not evaluate") and per the
  docstring's own path-safety claim `:80-81`/`:242` ("non-ASCII ... bytes in a path are not
  C-quoted away"). The C1 counter's own path (`cat-file -p <rev>:<path>` per spec, argv-encoded
  via os.fsencode) handles the same repo — divergence from the counter.
- Proposed fix: `("\n".join(specs) + "\n").encode("utf-8", "surrogateescape")` at `:309`, or
  fall back to one `cat-file --batch-check` argv call per spec.

### 2. LOW — path containing a newline misaligns the batch-check stream: both specs resolve None → IndexError at `:414`
- Site: `tools/append-only-audit.py:308-311` — specs are joined with `\n`, so a path holding a
  `\n` splits into two input lines; every later output shifts by one and `zip` pairs wrong;
  here both specs came back "missing" → `psec == []` → `psec[pos - 1]` (`:414`) raises.
- Command: fixture with `corpus/lessons/a\nb.md` (30 lines, then 25 deleted), contract row
  `corpus/lessons/*.md`; same invocation. Observed: exit 1, `IndexError: list index out of
  range` (evidence-log J). Expected: exit 2 (or correct grading).
- Proposed fix: same as finding 1 (per-spec argv calls are newline-safe).

### 3. LOW — `--contract` file with an invalid-UTF-8 byte: uncaught UnicodeDecodeError, exit 1 instead of promised exit 2
- Site: `tools/append-only-audit.py:887-888` — `open(a.contract, encoding="utf-8")` raises
  `UnicodeDecodeError` (a ValueError); `:890` catches only `(AuditError, OSError)`.
- Command: `python3 tool-tip.py --repo F --contract bad.tsv` where bad.tsv holds a `0xff` byte.
- Observed: exit 1 + traceback (evidence-log X1). Docstring `:96` promises exit 2 for a
  malformed contract. The counter reads the tip contract via `git show` + `decode(replace)` —
  never crashes.
- Proposed fix: read bytes and decode with `errors="replace"` (parse_contract then validates
  structure), or add `UnicodeDecodeError`/`ValueError` to the `:890` except tuple → exit 2.

### 4. LOW — gitlink (submodule) bump at `--threshold 1`: IndexError at `:414` (unreachable at the frozen threshold 20)
- Site: `tools/append-only-audit.py:414` — `s = psec[pos - 1]` with `psec == []`: numstat
  counts a gitlink change as 1 deletion (verified: `numstat → {'sub': 1}`), so at threshold 1
  it becomes an event; the parent object is a commit, `Repo.blobs` (`:312`) maps it to None,
  `list_lines(None)` → `[]`.
- Command: fixture superproject with submodule bump; `python3 tool-tip.py --repo F --to <c>
  --threshold 1 --files sub --json`. Observed: exit 1, `IndexError: list index out of range`
  (evidence-log X3). Expected: exit 2, or skip non-blob objects like the binary case.
- Reachability: at the frozen threshold 20 the event is skipped (`1 < 20`, `:397`), so neither
  the lane run nor the C1 counter can hit it. Proposed fix: when `pb is None`, skip the file
  for that commit and record it beside `binary_changes` (mirrors the numstat `-` handling).

### 5. COSMETIC — stale v2 sentence contradicts v3 in the kept docstring block
- `tools/append-only-audit.py:79` (kept v2 text): "Informational: the exit code follows
  status." vs `:15` (v3): "`regressed` ... now exits 1" and `exit_code()` (`:494-497`) which
  exits 1 on regressed. A reader of the kept block alone is misled.
- Proposed fix: one-line v3 annotation on the kept sentence, e.g. "(v3: regressed now exits
  1 — see the v3 header)".

## Verified correct (fixture evidence, evidence-log section)

- **Positions from hunk headers** — A1/A2/A3: parent ending without a newline; deletion of the
  final line(s) with the `\ No newline at end of file` marker after the `-` line(s) yields
  exact parent positions (26; 26; 26,27). B1: `-0,0` hunk (empty parent) records no deletion,
  no crash, exit 0. B2: `+0,0` new side, positions 1..10. B3: `@@ -1,25 +0,0 @@` (all lines
  deleted) → 25 deletions at 1..25, event unrestored, exit 1. H: full 25-line rewrite with the
  marker mid-hunk → 25 deletions at 1..25. I: two hunks in one diff → positions from each
  header (1,2,19,20), no state carry-over (`gd/ga` reset per hunk, `:285`). Header regex is
  prefix-match, so trailing function context (`@@ -26 +25,0 @@ p24 24`, A2) parses; deleted
  lines whose content starts with `-`/`@@` are consumed inside the hunk body scan and can never
  be mistaken for headers (v2's `--` defect stays fixed, selftest dashdash + B-series).
- **Section of a deleted line computed on the parent** — C: renaming an exempt heading
  (`## Old` → `## Renamed`) grades the 25 deleted lines (title absent at <to> → not eligible →
  gutted), exactly the frozen definition; C2: pre-heading lines (section None) under
  `only=## Errata` are ungraded (graded 0, exit 0).
- **Eligibility computed per event** — D: c1 (head rewritten in place) ungraded/eligible while
  c2 (head gutted, never regrown) graded 24 unrestored in the same run; a global (base-parent)
  eligibility would have graded neither — the tool uses each event's own parent (`:407-411`).
- **Union of regions when two rows match a file** — E1: `*` + `exempt=## Axes` → the exempt
  carve-out still applies (graded 0). E2: `exempt` + `only=## Round 1` → dated-section
  deletion graded 25. E3: `only` alone → head-section deletion ungraded. Matches docstring
  "union of their exempt titles and only prefixes" and the counter's `regions[f]` list.
- **--files mode** — F: no regions (section deletion graded 25), `declarations: []`,
  `vanished: []`; nonexistent path → no events, exit 0; `--files` + `--contract` → exit 2
  (`:880-881`).
- **declaration() failure paths** — G: missing declared file, out-of-range declared line,
  missing pointer file, out-of-range pointer line → each `ok=False` with reason,
  `bad_declarations=4`, exit 1 (docstring "an unbound row exits 1"). Binding itself matches the
  counter's `row_binds()` term for term (`:184-229` vs counter `row_binds`).
- **held/status/regressed/exit over G** — code `:412-436` matches the counter's recompute
  (held over G with the `max(0, M-K)` clamp, `restored_best` first-max, `restored_by` first
  `h == ng > 0`, `regressed` only for restored/partial, exit 1 on partial/unrestored/regressed/
  vanished/bad declarations); selftest `window-max` and counter S8 exercise the regression exit.
- **Determinism** — two lane runs byte-identical (X4).
- **Performance on the lane** — `python3 tool-tip.py --repo <clone> --to 380bcdff... --json`:
  **0.93 s wall** (311 commits, 89 contract-expanded files, 5 events, all restored,
  ungraded_lines 89, regressed 0, vanished 0, bad_declarations 0, exit 0). C1 counter on my
  own `git clone --shared` clone: `selftest=1 contract=1 lane=1 fixture=1 stable=1 rows=9
  files=89 lane_events=5 lane_failures=0 ungraded_lines=89 fixture_fail=0 met=True`, exit 0
  (~5 s). No superlinear trap: per-commit numstat is O(commits) git calls (311), window blob
  fetches are one batch-check per event with per-blob caching (`Repo._raw/_lines/_sections`).

## Residual risk and verification gaps

- Findings 1-4 are unreachable on this lane (no non-UTF-8/newline paths match the contract; no
  submodules; threshold frozen at 20) and the frozen C1 counter cannot reach them either — they
  are robustness debt against the tool's own docstring promises, not calibration errors.
- I did not review C2 (live replay v5) — not in this seat's scope.
- The `exempt`/`only` pointer regexes (`:114`, counter-identical) cannot express a pointer path
  containing `@` or `:`; consistent with the frozen counter, so not a defect, but a contract
  expressiveness limit worth knowing.
- No tool installs were needed or made (nothing recorded per the 2026-10-19 directive).

Scratch `/fast/scratch/hyaku/kama-r48/V1Tool` (incl. the shared lane clone) removed after
writing the deliverables.
