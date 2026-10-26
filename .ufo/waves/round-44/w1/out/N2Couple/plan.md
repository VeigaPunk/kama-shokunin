# N2Couple — round-44 cross-claim coupling scan: C1 ⇄ C2 separability

Verdict: **C1 and C2 are causally separable.** No file is read by both counters,
and neither claim's write set intersects the other counter's read set. Both
separability controls pass on stand-in trees built from the round drafts; the
integration reruns them with the final files (exact steps below).

---

## 1. Files each counter reads (from `tools/round44-release-recheck-audit.py`,
`tools/round44-verdict-ledger-audit.py`, lane commit `77d1bbf5`)

| File / object | C1 counter reads | C2 counter reads |
|---|---|---|
| `corpus/SOURCES.md` | yes — at BASE for the population (`show(repo, BASE, SOURCES)`, c1 L267); at TIP for the section (`show(repo, tip, SOURCES)`, c1 L306) | no |
| `registry/release-recheck-b11889.tsv` | yes — at TIP (`show(repo, tip, LEDGER)`, c1 L273) | no |
| `corpus/knowledge/*.md` (each row's used-by at TIP) | yes — only for valid drifted/removed rows (c1 L316-331; path regex `corpus/knowledge/[\w.\-]+\.md` at L324) | no |
| upstream llama.cpp objects (pin + `d854d98b`) | yes — `git rev-parse <pin>:<path>`, `git show` (c1 L193-206, L272) | no |
| `registry/verdict-ledger.tsv` | no | yes — at TIP (`show(repo, tip, LEDGER)`, c2 L137) |
| `SCORECARD.md` | no | yes — at TIP (`show(repo, tip, "SCORECARD.md")`, c2 L217; `## Axes` calibration-row cite at L240-246) |
| fleet `.ufo/reports/round-N/kama.md` (N=10..43) | no | yes — at `b0fd7b7f` (side_spec, c2 L112/L133) |
| lane `corpus/lessons/round-N-verifier-spotcheck.md` | no | yes — at BASE `9d9cc93` (side_spec, c2 L113/L133) |

## 2. Files each claim's work will write

- C1: `registry/release-recheck-b11889.tsv`; `corpus/SOURCES.md` (round-44
  section heading containing `Round-44 release re-verification` + rows S482
  [llama.cpp release b11889] and S483 [vLLM preload.py v0.31.0, drafted by
  S9D2Row]); knowledge-entry flags in `corpus/knowledge/*.md` used-by files
  (draft has no drifted/removed rows, so no flags needed; S483's source-line
  clause goes in `corpus/knowledge/runtime-health-surface-processes.md`).
- C2: `registry/verdict-ledger.tsv`; `SCORECARD.md` (`### Round-44 calibration
  ledger` section + `## Axes` calibration row naming `registry/verdict-ledger.tsv`).

## 3. Shared files

Build the 2×2 read/write incidence over the claim surfaces:

| File | read by C1 counter | written by C1 | read by C2 counter | written by C2 |
|---|---|---|---|---|
| `corpus/SOURCES.md` | yes (BASE+TIP) | yes | no | no |
| `registry/release-recheck-b11889.tsv` | yes (TIP) | yes | no | no |
| `corpus/knowledge/*.md` | yes (TIP, flags only) | yes | no | no |
| `registry/verdict-ledger.tsv` | no | no | yes (TIP) | yes |
| `SCORECARD.md` | no | no | yes (TIP) | yes |
| fleet reports, lane lessons | no | no | yes (frozen revs) | no |
| upstream llama.cpp objects | yes | no | no | no |

Result: **there is no file shared between the two claims** — no file appears in
both claims' write sets, and no file read by one claim's counter is written by
the other claim's work. The only shared objects are the lane clone itself and
the `--tip` commit both counters resolve in it; that is structural (both
measure the same tree), not causal. Prediction: applying either claim's files
alone to the freeze tree leaves the other claim's counter in exactly its base
(not-met) state.

## 4. Separability controls (exact shell steps)

Both controls clone the lane at the frozen base into scratch, apply **only**
one claim's files, commit (fixture identity inside the scratch clone only),
then run **both** frozen counters at that tip. Isolation gate before the first
commit; the `--out` receipts record exit codes.

Common preamble:

```bash
S=$(mktemp -d -p /fast/scratch/hyaku/kama-r44/N2Couple)
LANE=/home/vgpnk/Projects/shokunin/kama-shokunin
UP=/fast/scratch/hyaku/kama-r44/shared/llama.cpp
FLEET=/home/vgpnk/Projects/shokunin
BASE=9d9cc93ec50783cd114829a91757b90d57c78dc6
C1TOOL="$LANE/tools/round44-release-recheck-audit.py"
C2TOOL="$LANE/tools/round44-verdict-ledger-audit.py"

git clone -q --shared --no-checkout "$LANE" "$S/a"   # Control A
git -C "$S/a" checkout -q "$BASE"
test "$(git -C "$S/a" rev-parse --show-toplevel)" = "$S/a" || exit 9   # isolation gate
```

### Control A — C1 files alone must leave C2 met=False

```bash
mkdir -p "$S/a/registry"
cp <final C1 ledger> "$S/a/registry/release-recheck-b11889.tsv"
# SOURCES.md: append the round-44 section heading (must contain
# "Round-44 release re-verification") and the S482/S483 rows:
python3 - <<'PY'
import pathlib
out = pathlib.Path("$S/a/corpus/SOURCES.md")
with out.open("a") as f:
    f.write("\n## Round-44 release re-verification\n\nRe-verified at b11889; "
            "see registry/release-recheck-b11889.tsv.\n")
PY
git -C "$S/a" add -A
git -C "$S/a" -c user.name=r44-sep -c user.email=r44-sep@fixture.invalid \
    commit -qm "sepA: C1 files alone on base"
TIPA=$(git -C "$S/a" rev-parse HEAD)

python3 "$C1TOOL" --repo "$S/a" --tip "$TIPA" --upstream "$UP" --out "$S/A.c1.out"
echo "exit=$?" >> "$S/A.c1.out"
python3 "$C2TOOL" --repo "$S/a" --tip "$TIPA" --fleet "$FLEET" --out "$S/A.c2.out"
echo "exit=$?" >> "$S/A.c2.out"

# PASS iff C2's output is byte-identical to its base output modulo the tip line:
diff <(tail -n +2 "$S/base.c2.out") <(tail -n +2 "$S/A.c2.out")
```

Expected on pass: `A.c2.out` summary exactly `rows=0 valid=0 missing=204 bad=0
agree=0 overclaim=0 underclaim=0 other=0 absent=0 table_missing=0
table_extra=0 summary=0 axes=0 met=False`, `exit=1` (the base shape). The C1
run on the same tree must show C1's own full result (e.g. with the round draft:
`pop=91 rows=91 valid=85 unverified=6 … section=1 met=False`), proving the C1
counter is exercised while C2 stays untouched.

### Control B — C2 files alone must leave C1 met=False

```bash
git clone -q --shared --no-checkout "$LANE" "$S/b"
git -C "$S/b" checkout -q "$BASE"
test "$(git -C "$S/b" rev-parse --show-toplevel)" = "$S/b" || exit 9

mkdir -p "$S/b/registry"
cp <final C2 ledger> "$S/b/registry/verdict-ledger.tsv"
# SCORECARD.md: add the final "### Round-44 calibration ledger" section and the
# "## Axes" calibration row citing registry/verdict-ledger.tsv.
git -C "$S/b" add -A
git -C "$S/b" -c user.name=r44-sep -c user.email=r44-sep@fixture.invalid \
    commit -qm "sepB: C2 files alone on base"
TIPB=$(git -C "$S/b" rev-parse HEAD)

python3 "$C1TOOL" --repo "$S/b" --tip "$TIPB" --upstream "$UP" --out "$S/B.c1.out"
echo "exit=$?" >> "$S/B.c1.out"
python3 "$C2TOOL" --repo "$S/b" --tip "$TIPB" --fleet "$FLEET" --out "$S/B.c2.out"
echo "exit=$?" >> "$S/B.c2.out"

# PASS iff C1's output is byte-identical to its base output modulo the tip line:
diff <(tail -n +2 "$S/base.c1.out") <(tail -n +2 "$S/B.c1.out")
```

Expected on pass: `B.c1.out` summary exactly `pop=91 rows=0 valid=0
unverified=91 unchanged=0 holds=0 reworded=0 drifted=0 removed=0
flags_missing=0 section=0 met=False`, `exit=1` (the base shape).

### Validation runs (this seat, stand-ins = round drafts)

Base first, on a pristine clone at `9d9cc93`:
- `base.c1.out`: `pop=91 rows=0 valid=0 unverified=91 … section=0 met=False` (exit 1) — reproduces the preregistration `controls.base.c1` (also `junk-*` shapes in the frozen control receipts).
- `base.c2.out`: `rows=0 valid=0 missing=204 … summary=0 axes=0 met=False` (exit 1) — reproduces `controls.base.c2`.

Control A (`a759e4e2bf3d0451e72a0c106312fa3feed7ffd4`, C1 draft ledger + section heading + S482 row):
- `A.c1.out`: `pop=91 rows=91 valid=85 unverified=6 unchanged=4 holds=81 … section=1 met=False` (exit 1) — C1 counter fully exercised; the 6 invalid rows are the draft's TODO rows (S001/S015/S037/S043/S059/S108).
- `A.c2.out`: `rows=0 valid=0 missing=204 … met=False` (exit 1) — **identical to `base.c2.out` modulo the tip line** (`diff-A-c2-vs-base.txt` empty). PASS.

Control B (`3cd65aa254cbc94272fd6c7d813a1234d922b8d1`, C2 draft ledger + placeholder scorecard section):
- `B.c1.out`: `pop=91 rows=0 valid=0 unverified=91 … section=0 met=False` (exit 1) — **identical to `base.c1.out` modulo the tip line** (`diff-B-c1-vs-base.txt` empty). PASS.
- `B.c2.out`: `rows=204 valid=204 missing=0 bad=0 agree=61 overclaim=3 underclaim=8 other=15 absent=15 table_missing=26 table_extra=0 summary=0 axes=0 met=False` (exit 1) — the draft ledger itself is fully valid; only the scorecard legs are missing (placeholder section), as expected.

## 5. Risks / integration notes

- Keep the C1 commit free of `registry/verdict-ledger.tsv` and `SCORECARD.md`
  changes, and the C2 commit free of `corpus/SOURCES.md`,
  `registry/release-recheck-b11889.tsv`, and `corpus/knowledge/*.md` changes.
  C2's counter reads `SCORECARD.md` at TIP (c2 L217, L240-246): if C1's
  integration commit edits SCORECARD.md (e.g. the freshness row) it remains
  harmless to C2 unless it breaks the `## Axes` heading or the calibration row's
  ledger cite — the control A diff guards the latter.
- Both counters run at the same TIP; the control tip must be exactly base + the
  one claim's files (nothing else) — the isolation gate + fresh clone guarantee this.
- At integration, rerun with the final files; the assertions are the two
  `diff` commands above, not the stand-in outputs.

Receipts: `base.c1.out`, `base.c2.out`, `A.c1.out`, `A.c2.out`, `B.c1.out`,
`B.c2.out`, `diff-A-c2-vs-base.txt`, `diff-B-c1-vs-base.txt`,
`diff-A-c1-vs-base.txt`, `diff-B-c2-vs-base.txt` (this directory).
