# sources row — S542 · pytest exit codes · SCR02SourceRow (round 70, wave 1)

Seat: `SCR02SourceRow` (advisory leaf; no lane writes). Read-only on
`/home/vgpnk/Projects/shokunin/kama-shokunin`, tip measured at
`0e14facd0c619f45a6461821d2bd80ddac9855b1` (round-start base
`6035e952c2521999e192d6f236331f265ac98392` is an ancestor: `git merge-base --is-ancestor` → 0).

## 0. Read this first — the URL is already in the registry (S052)

`grep -n 'pytest' corpus/SOURCES.md` (exit 0) returns **line 64**:

```
| S052 | pytest exit codes — https://docs.pytest.org/en/stable/reference/exit-codes.html | docs | A | how one widely used test runner keeps "nothing was collected" distinct from "collected and failed" in its exit status; convention precedent only, not the lane's numbering; the `stable` alias, whose pytest version the page does not state | §Exit codes, entries "Exit code 1" and "Exit code 5" | Exit 1 means tests were collected and run and some failed; exit 5 means no tests were collected: an empty observation has its own non-zero status, distinct from failure. | mined | 2026-10-20 | on-release | corpus/knowledge/llamacpp-loading-lifecycle.md, corpus/lessons/round-18.md |
```

S052 already teaches the C2 distinction ("an empty observation has its own non-zero status"),
and its `recheck` is `on-release`. It carries **no retained bytes and no sha256** (pre-r67 practice).

Contract consequence, measured (not argued) — `sources-census.sh validate`:

- `E04` keys on the pair **URL + scope**. A new row with a different `scope` cell does **not** earn E04; it earns `W04 duplicate url … across scopes` (a warning, does not change the exit).
- Same scope text would earn `E04 … duplicate url … within scope …` unless `teaches` contains `supersedes S###`.

So there are two contract-legal landings; the frozen round-70 frontier step names only the second:

- **Option A (cheapest, no new row):** extend S052's `used-by` with `corpus/lessons/round-70.md`, keep every other S052 cell. Precedent: round-14 (`corpus/SOURCES.md` §"Round-14 used-by addition", used-by-only edits). Validator: exit 0, **no new warning at all** (W04 stays 104).
- **Option B (the assignment's shape, one new row):** land S542 with a scope cell narrowed to the *completeness rule* C2 needs, accept one `W04` (same URL, different scope). Validator with the round-70 lesson present: exit 0, W04 104 → 105.

**Recommendation to the L1:** if the round wants exactly one new row (freeze §Frontier step), land Option B — it is the only option that adds today's byte identity for the page (S052 has none). If row count matters more than byte freshness, land Option A; do not land both.

## 1. Candidate row — Option B (11 columns, one line, no pipe inside any cell)

Exact bytes are also at `evidence/row-s542.txt` (949 bytes, 1 line, 0 tabs, 12 `|` ⇒ `awk -F'|'` NF=13):

```
| S542 | pytest exit codes — https://docs.pytest.org/en/stable/reference/exit-codes.html | docs | A | the pytest process exit-code contract as a completeness rule: exit 0 is the code for all tests collected and passed, while "No tests were collected" is its own nonzero code 5 — a run that collected and executed nothing is never success | §Exit codes, list items "Exit code 0" and "Exit code 5" (anchor #exit-codes); fetched bytes sha256 a403306a1d763fc8123749544905dd64e8e0cfa5ed46a416679001c3142e3977 retained at `.ufo/waves/round-70/w1/out/SCR02SourceRow/source/pytest-exit-codes.html` (accessed 2026-11-03) | grounds C2's design rule for the round-70 host census: a census member that did not run is not a pass, so the verdict's exit is derived from the not-evaluated count — the same distinction pytest draws between exit 0 and the no-tests-collected code 5 | mined | 2026-11-03 | on-release | SCORECARD.md,corpus/lessons/round-70.md |
```

Cell-by-cell, against `SOURCES-CONTRACT-v1` as implemented by
`/home/vgpnk/Projects/shokunin/scripts/sources-census.sh` (v1, bash 5.3.20 + gawk 5.4.1):

| # | column | value | rule it satisfies |
|---|---|---|---|
| 1 | id | `S542` | `E02` id matches `S[0-9]{3,}`; highest existing id is `S541` (`grep -oE '^\| *S[0-9]+' corpus/SOURCES.md \| tail -1` → `| S541`), so S542 is next and `E03` cannot fire |
| 2 | source | `pytest exit codes — <URL>` | same `Name — URL` shape as S539–S541; URL unique to the registry except S052 (see §0) |
| 3 | kind | `docs` | `E05` enum |
| 4 | tier | `A` | `E06` enum; tier A justified in `gate-block.md` (first-party reference, self-declared public API) |
| 5 | scope | the completeness rule only | deliberately narrower than S052's scope cell (so `E04` cannot fire; `W04` does) |
| 6 | anchor | `§Exit codes`, items "Exit code 0"/"Exit code 5", anchor `#exit-codes`, sha256 + retained path + access date | matches r67–r69 practice (anchor carries retained-byte identity) |
| 7 | teaches | the C2 design rule | `W02` not applicable (`status` is mined); length > 8 |
| 8 | status | `mined` | `E07` enum |
| 9 | opened | `2026-11-03` | `E08`: ISO, not future (`--today 2026-11-03`) |
| 10 | recheck | `on-release` | `E09`: symbolic cadence accepted; same cadence S052 already carries |
| 11 | used-by | `SCORECARD.md,corpus/lessons/round-70.md` | `E11` needs both paths on disk; `SCORECARD.md` exists, `corpus/lessons/round-70.md` is landed by this round's lesson seat |

`used-by` note: every r67–r69 row pairs `SCORECARD.md` with its lesson. If the L1 prefers the
lesson alone, drop `SCORECARD.md,` — nothing else in the row changes.

## 2. Insertion point (E12)

- The registry is `## Registry` at **line 9**, and the section ends where `## Paths` starts at **line 298**; the table's last row is **line 293** (`| S541 | …`), lines 294–297 are blank.
- Insert the row as **new line 294, immediately after S541** — inside the section. Same line number at the base `6035e952` and at the measured tip `0e14facd` (`git show <rev>:corpus/SOURCES.md | sed -n '293p'` → `| S541 | Python \`datetime\` — https://d…` for both).
- **Never append at EOF.** `corpus/SOURCES.md` carries ~350 lines of contract prose after the table; an EOF append produced `kama E12 S541 row outside Registry section`, exit 1, in round 69 (mistake 10) and in rounds 31/36/67.
- Row count: `grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md` → **281** before, **282** after.

## 3. Validator receipts (real runs, scratch mirror of this lane)

The lane has no `scripts/` directory at the tip, so the fleet validator was used:
`/home/vgpnk/Projects/shokunin/scripts/sources-census.sh` (mode `validate`, `--today 2026-11-03`).
The scratch mirror is a symlink farm over the real lane (`corpus/knowledge`, `corpus/lessons`,
`.ufo`, `SKILL.md`, `SCORECARD.md`, `tools`, `registry`, `tests` all resolve to the real files);
only `corpus/SOURCES.md` is a real scratch copy. The lane's own `corpus/SOURCES.md` sha256 was
identical before and after every run (`lane_unchanged=yes`).

```
# V1 baseline (unmodified registry copy)
$ bash /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate \
    --file "$S/lane3/corpus/SOURCES.md" --today 2026-11-03
file	ok	/fast/scratch/hyaku/kama-r70/SCR02SourceRow/lane3/corpus/SOURCES.md
EXIT=0        # W04=104 W01=1 (pre-existing warnings), no E finding

# V2 + S542 row, lesson NOT yet present
file	E11	S542 missing used-by corpus/lessons/round-70.md
file	W04	S542 duplicate url docs.pytest.org/en/stable/reference/exit-codes.html across scopes
EXIT=1        # the ONLY new findings; no E01/E04/E05/E06/E07/E08/E09/E12

# V3 + S542 row, scratch stub corpus/lessons/round-70.md present (fixture, not landed)
file	ok	/fast/scratch/hyaku/kama-r70/SCR02SourceRow/lane3/corpus/SOURCES.md
EXIT=0        # W04=105 (104 + S542) W01=1

# V4 Option A: S052 used-by += corpus/lessons/round-70.md, stub present
file	ok	/fast/scratch/hyaku/kama-r70/SCR02SourceRow/lane3/corpus/SOURCES.md
EXIT=0        # W04=104 W01=1 — no new warning
```

Full outputs: `evidence/validate-baseline.out`, `evidence/validate-s542-nostub.out`,
`evidence/validate-s542-withstub.out`, `evidence/validate-s052-withstub.out`.
Note the V2/V3 sequence is what makes the E11 finding attributable: the diff against V1 is a
single line, so the row introduces no schema defect; the lesson file is the only missing path.

## 4. Option A bytes (only if the L1 chooses the no-new-row landing)

The only cell that changes is `used-by`:

- old: `corpus/knowledge/llamacpp-loading-lifecycle.md, corpus/lessons/round-18.md`
- new: `corpus/knowledge/llamacpp-loading-lifecycle.md, corpus/lessons/round-18.md, corpus/lessons/round-70.md`

Full replacement bytes for S052's line 64 (`evidence/row-s052-extended.txt`, 710 bytes; sha256
`cfacb4cc31c58eeda60219257d934a58ca790565fef4ea11556e1272e117e228`):

```
| S052 | pytest exit codes — https://docs.pytest.org/en/stable/reference/exit-codes.html | docs | A | how one widely used test runner keeps "nothing was collected" distinct from "collected and failed" in its exit status; convention precedent only, not the lane's numbering; the `stable` alias, whose pytest version the page does not state | §Exit codes, entries "Exit code 1" and "Exit code 5" | Exit 1 means tests were collected and run and some failed; exit 5 means no tests were collected: an empty observation has its own non-zero status, distinct from failure. | mined | 2026-10-20 | on-release | corpus/knowledge/llamacpp-loading-lifecycle.md, corpus/lessons/round-18.md, corpus/lessons/round-70.md |
```

## 5. Post-landing check the L1 should run

```
cd /home/vgpnk/Projects/shokunin/kama-shokunin
bash /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama; echo EXIT=$?
python3 .ufo/waves/round-70/w1/out/SCR02SourceRow/verify-quote.py; echo EXIT=$?
```

Expected: `kama ok` (exit 0) with the pre-existing W04/W01 warnings and, for Option B, one
`W04 S542 …` line; verifier prints three `MATCH` lines and exits 0.

## 6. What I could NOT verify

- No lane write, no commit: the row above is candidate bytes only.
- E11 for Option B depends on `corpus/lessons/round-70.md` existing **at the same tip** as the
  row; landing the row alone leaves validate red (V2).
- The page states no pytest version (`grep -o -i 'pytest [0-9][^<]\{0,12\}'` → no output), so the
  row cannot pin a version and `on-release` is a cadence, not a version pin; S052 records the same
  limitation.
