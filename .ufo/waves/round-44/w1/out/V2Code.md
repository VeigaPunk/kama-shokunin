# V2Code — code review of tools/round44-verdict-ledger-audit.py (round-44 C2 counter)

**Verdict:** the frozen counter (sha256 `1933e75b2a5308d09d0cfafd166c95cfcb1b7c15eaf1bf9ad2b321a453224bd1`, equal to the preregistration's `counter_sha256` and to the bytes at tip 77d1bbf5) implements its docstring exactly on every branch I exercised — freeze-commit run, all four control trees re-run byte-identically, and 20+ synthetic rule probes including a met=True path — with **4 defects, all latent on the frozen data and none able to flip `met` on the real population**: a Unicode-digit `line` field crashes the run (D1), out-of-population ledger rows are silently ignored (D2), substring tokenization reads `unimproved`/`not improved` as `improved` (D3), and `absent` is accepted for the self side when the self file is missing (D4).

Reviewed bytes: `tools/round44-verdict-ledger-audit.py` (264 lines). Hash proof:
`sha256sum tools/round44-verdict-ledger-audit.py` and `git show 77d1bbf55c62a1d5fc08fcbd682f22277a5cdb40:tools/round44-verdict-ledger-audit.py | sha256sum` both → `1933e75b…24bd1`; preregistration `.ufo/waves/round-44/preregistration.json` C2 `counter_sha256` → same.

## Defects

### D1 — Unicode-digit `line` field crashes the counter instead of flagging the row (low; reachable only via a crafted ledger)
- **Where:** `tools/round44-verdict-ledger-audit.py:179` — `elif not d["line"].isdigit() or not 1 <= int(d["line"]) <= len(text):`. `"²".isdigit()` is True but `int("²")` raises ValueError.
- **Docstring:** line 24 (`line: 1-based line … or '-' for absent`) makes a non-decimal `line` an invalid row; line 53 promises exit 2 for "could not evaluate".
- **Command that shows it:** probe1.py P1 — fixture clone of the lane at BASE under scratch, ledger row `10 expansion self improved fleet b0fd7b7f… .ufo/reports/round-10/kama.md ² probe`, committed with fixture identity, then `python3 tools/round44-verdict-ledger-audit.py --repo <fixture> --tip <sha> --fleet /home/vgpnk/Projects/shokunin` → `ValueError: invalid literal for int() with base 10: '²'`, exit 1, no summary line, no `could-not-evaluate` (probe1-output.txt).
- **Impact:** fail-closed (the crash exits 1 = not met, so it cannot false-approve), but the structured output and all detail lines are lost, and the exit code is 1 rather than the promised 2.
- **Fix:** replace `d["line"].isdigit()` with `re.fullmatch(r"[0-9]+", d["line"])` (or wrap the `int()` in try/except ValueError → "line out of range").

### D2 — out-of-population ledger rows are silently ignored (low)
- **Where:** parse loop `tools/round44-verdict-ledger-audit.py:142-150` keys every parsed row (`k = (d["round"], d["trend"], d["side"])`, lines 148-150) but only the 204 population keys are ever validated; a row with round 9, an unknown trend, or an unknown side is counted in `rows=R` and never flagged.
- **Docstring:** lines 18-19 declare the ledger = "one row per (round 10..43, trend, side self|outside) = 204 rows"; an extra row violates the declared format and passes unflagged.
- **Command that shows it:** probe1.py P2 — ledger containing only a round-9 row → `rows=1 valid=0 missing=204 bad=0 … met=False` with no detail line mentioning the round-9 row (probe1-output.txt).
- **Impact:** completeness-of-check gap, not soundness — population keys are unaffected, so `met` cannot be flipped by junk rows.
- **Fix:** after the validation loop, for each parsed key outside `{(str(r), t, s) for r in ROUNDS for t in TRENDS for s in ("self","outside")}`, append `detail: out-of-population row <k>` and count it in `bad`.

### D3 — verdict tokens are matched as substrings, not tokens (low; latent on the frozen data)
- **Where:** `tools/round44-verdict-ledger-audit.py:71-72` (TOK regex, no word boundaries) used by `read_line` (lines 91-107).
- **Docstring:** lines 25-28 — "A line is read as tokens: trend words … and verdict words …". `unimproved` is not the token `improved`; `unharmed` is not `harmed`.
- **Command that shows it:** importing the frozen module and calling its own `read_line`:
  - `read_line("expansion: unimproved")` → `{'expansion': {'improved'}}`
  - `read_line("quality not improved this round")` → `{'quality': {'improved'}}`
  - `read_line("discernment unharmed")` → `{'discernment': {'harmed'}}`
- **Latency check (frozen population unaffected):** scanned all 64 existing side files (34 self at b0fd7b7f + 30 outside at 9d9cc93e; rounds 20-23 outside files do not exist at the base — verified with `git cat-file -e`, which is why the docstring's absent rule exists) for `unimproved|unharmed|disimproved|preimproved` → 0 hits; also 0 exotic line-boundary chars (`\x0b\x0c\x85\u2028\u2029`) that would shift `splitlines()` numbering.
- **Fix:** word-boundary the alternatives, e.g. `r"\b(expansion|quality|discernment)\b|\b(unprovable[- ]but[- ]better)\b|\b(unprovable)\b|\b(improved|harmed|unchanged)\b"` — the compound alternative stays first so `finditer` consumes it before the bare `unprovable`. Note: negation ("not improved") remains read as the verdict word under either regex — that is the docstring's mechanical rule, not an implementation bug.

### D4 — `absent` accepted for the self side when the self file is missing (low; doc-vs-code; latent on the frozen data)
- **Where:** `tools/round44-verdict-ledger-audit.py:172-178` — the `elif text is None: why = "file missing at rev"` guard (line 177) is only reached when `v != "absent"`, so a self row with `verdict=absent`, note ≥ 20, `line=-` validates even when the fleet file does not exist at the fleet rev.
- **Docstring:** line 31 scopes the file-missing justification to the outside side: "absent — *(outside)* the file does not exist at the rev, or *(either side)* no line of the file gives the row's trend any verdict word".
- **Command that shows it:** harness.py MAIN run (frozen bytes with `FLEET_REV`/`BASE`/`ROUNDS` patched to synthetic fixture repos; round-14 fleet file deliberately absent) → the three r14 self `absent` rows are accepted and the run is `met=True exit=0`; probe "r14 self rows flagged? NONE (accepted as valid/absent)" (harness-output.txt).
- **Latency check:** unreachable on the frozen data — all 34 self files exist at b0fd7b7f (`git cat-file -e` per round 10..43 → no MISSING fleet lines).
- **Fix:** inside the absent branch add `elif side == "self" and text is None: why = "file missing at rev"` (`side` is in scope). Alternative reading: "no line of the file gives the trend a verdict" is vacuously true for a missing file, which would license absent for self too — but then the docstring's "(outside)" parenthetical is dead text. Flagging for L1 to settle; either tighten the code or the docstring.

## Verified correct (each exercised, not read off the code)

1. **Population/keys:** `ROUNDS = range(10, 44)` (line 66) → 34 rounds × 3 trends × 2 sides = 204 (line 250); every missing key reported individually (freeze run: `missing=204`, one detail line per key).
2. **Side spec** (lines 110-113): self → (`fleet`, b0fd7b7f…, `.ufo/reports/round-N/kama.md`); outside → (`lane`, 9d9cc93e…, `corpus/lessons/round-N-verifier-spotcheck.md`); enforced by the equality check at line 167 (harness M2: wrong rev → `repo/rev/path differ from the side's file`).
3. **Evidence rule** (lines 91-107, 179-190): verdict word belongs to the nearest preceding trend on the line (word before any trend word is dropped — `read_line("harmed unprovable but better")` → `{}`); spaced `unprovable but better` normalizes to `unprovable-but-better` (MAIN r10 quality self row validated on a spaced line); line reading case-insensitive but the ledger's verdict field is case-sensitive (`Improved` rejected, M18); `mixed` = ≥ 2 distinct words on the cited line (MAIN r10 discernment; M8 one-word line rejected); `absent` rejected when any line of the file gives the trend a verdict (M7); `absent` requires `line=-` and note ≥ 20 chars, boundary inclusive (M5fix/M6fix rejected, M19 exactly-20 accepted).
4. **Only-row-per-key:** duplicate → invalid (M1; and the junk-c2-allimproved control's `bad=204`).
5. **Comparison/ordering** (lines 70, 196-214): harmed < unchanged < unprovable < unprovable-but-better < improved; agree/over/under/other exact on constructed data (MAIN: agree=1 over=2 under=1 other=1); a key with an absent side counts once as absent and is excluded from the ordering (MAIN absent=10 includes 7 both-absent keys counted once); mixed takes precedence over ordering (self=mixed vs outside=harmed → other, not over).
6. **Summary formula** (lines 235-237): `n = agree + over + under` exactly; `absent` = keys with an absent side (lines 203-205); the exact `want` string must appear in the section (M9 perturbed figure → `summary=0`; MAIN/M19/M20 exact → `summary=1`).
7. **SCORECARD section parsing** (lines 217-234): heading equality on the stripped line (M13 `ledgar` typo → section empty → `table_missing=4 summary=0`); table rows parsed only from section lines, first four cells, round cell must be digits and trend cell in the vocabulary; mismatch rows placed after the next heading are ignored (M16 → `table_missing=4`); separator/header rows ignored; set equality on (round, trend, self, outside) (M10 extra → `table_extra=1`; M11 missing → `table_missing=1`).
8. **Axes calibration-row detection** (lines 240-246): inside a `## Axes` section (heading equality), a table row whose second cell contains `calibration` (case-insensitive) and that names `registry/verdict-ledger.tsv`. Matches the real SCORECARD shape: at the freeze tip the Axes calibration row is `SCORECARD.md:18` (`| calibration | **7** | run … |`) — second cell is `calibration` — and M20 shows the detection accepts that exact row shape (bold score, long run cell) once the ledger path is added; at the freeze tip `axes=0` is correct because the row does not yet name the ledger path.
9. **Exit codes:** 0 met (MAIN, M19, M20), 1 not met (all mutations, freeze run, all four control trees), 2 could-not-evaluate (unresolvable tip → `could-not-evaluate: git … rev-parse` on stderr, P3/M15).
10. **Read-only claim** (docstring line 54): mtime-walk over the fixture repo across an audit run → 0 files created/changed (P4); the builder's fixtures are `git clone --shared --no-checkout` + `checkout` inside `--scratch` with an isolation check (`rev-parse --show-toplevel` == fixture dir).

## Runs

**Freeze commit** — `python3 tools/round44-verdict-ledger-audit.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --tip 77d1bbf55c62a1d5fc08fcbd682f22277a5cdb40 --fleet /home/vgpnk/Projects/shokunin` →
`rows=0 valid=0 missing=204 bad=0 agree=0 overclaim=0 underclaim=0 other=0 absent=0 table_missing=0 table_extra=0 summary=0 axes=0 met=False`, **exit 1**. Correct do-nothing-base result: `registry/verdict-ledger.tsv` does not exist at the tip (`git cat-file -e 77d1bbf…:registry/verdict-ledger.tsv` → exit 128, "path does not exist"), SCORECARD.md exists but has no `### Round-44 calibration ledger` section, and the Axes calibration row (SCORECARD.md:18) does not yet name the ledger path. Consistent with `controls/base.c2.out` (which used tip=BASE) modulo the tip line.

**Controls re-run** — copied the frozen builder (sha256 of both the committed copy and the working tree: `1d3553b75f2a50e8a718e0220671a326f4f9183bb70c4627b2234cb9664cf03d`) to scratch and ran
`python3 build_controls.py --lane /home/vgpnk/Projects/shokunin/kama-shokunin --upstream /fast/scratch/hyaku/kama-r44/shared/llama.cpp --fleet /home/vgpnk/Projects/shokunin --scratch /fast/scratch/hyaku/kama-r44/V2Code/ctl` → builder exit 0, all 10 control scores printed; **every receipt byte-identical to its frozen counterpart except the fixture `tip=` line** (commit timestamps differ): base.c2.out IDENTICAL; junk-c2-allimproved.c2.out and junk-c2-noscorecard.c2.out differ only on line 1; same for the three c1 receipts (c1 is outside my scope, noted for the integrator).
- `junk-c2-allimproved` (204 rows, every verdict `improved` on line 1): `rows=204 valid=0 missing=0 bad=204 … met=False` exit 1 — every row rejected; the all-improved shortcut is caught.
- `junk-c2-noscorecard` (automatic last-hit ledger, no SCORECARD section): `rows=204 valid=204 missing=0 bad=0 agree=61 overclaim=3 underclaim=8 other=15 absent=15 table_missing=26 table_extra=0 summary=0 axes=0 met=False` exit 1 — the evidence rule accepts the self-consistent ledger but all three scorecard legs fail. (This control's ledger is built with the counter's own `read_line`, so `valid=204` is self-fulfilling by design; the control exercises the scorecard legs.)

**Synthetic harness** — frozen bytes with `FLEET_REV`/`BASE`/`ROUNDS` patched to fixture repos (disclosed substitution; the code object is the frozen one): MAIN run `met=True exit=0` with the constructed figures (`valid=30 agree=1 overclaim=2 underclaim=1 other=1 absent=10 table_missing=0 table_extra=0 summary=1 axes=1`), then 14 mutation runs each failing on exactly the intended leg (duplicate key, wrong rev, line 0/99, unknown verdict word, short absent note, numeric absent line, absent-but-line-gives-verdict, one-word mixed, wrong summary figure, extra/missing table row, axes row without ledger path, heading typo, rows outside the section, bad tip → exit 2).

## Residual risk / verification gaps
- The met=True path on the **real** 204-row ledger + real SCORECARD is untested — the ledger is the integrator's deliverable and no control builds a passing c2 tree; the positive path is covered only by the synthetic harness (patched constants).
- `rows=R` is not defined by the docstring; the counter prints distinct keyed rows (duplicates collapse in `rows` but are caught by the duplicate rule) — cosmetic.
- `show()` maps any git failure to "file missing" (lines 84-88); a partial/corrupt clone would read as file-absence (absent rows pass). The upfront `cat-file -e` checks cover rev existence only. Latent.
- Any `#`-prefixed line ends the calibration section (lines 220-222) while the Axes scan only terminates on `## ` headings (line 242) — asymmetric nesting handling; a `####` subheading inside the calibration section would truncate it. No realistic SCORECARD shape in the controls hits this; noted.

## Tooling
Nothing installed or upgraded (no need arose); pacman untouched.

## Artifacts
All under `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-44/w1/out/V2Code/`:
`freeze-run.txt` (freeze-commit receipt), `receipts/` (my 10 re-run control receipts), `harness.py` + `harness-output.txt`, `probe1.py` + `probe1-output.txt`, `probe2.py` + `probe2-output.txt`. Scratch `/fast/scratch/hyaku/kama-r44/V2Code` removed at the end; no lane file was edited; no pacman; no subagents.
