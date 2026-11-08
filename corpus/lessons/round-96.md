# Round 96 — the step budget decides the files it prices; the instrument cannot pass without load evidence

Lane `kama`, round 96, L1 `KamaR96`. Base `5d43528b` (round-95 admitted). Freeze `58001b71`; amendments 1
`e2fed9f5`, 2 `fb5cd3cd`, 3 `b3289c18`, 4 `20317286`. Claims: C1 operability (step budget decidability +
instrument honesty), C2 depth (the `5 + nd` step-cost table), C3 calibration (filings agree with the bytes
beside them).

## Gate

Every row below was opened this round (2026-11-08) at tag `b12177`; the digest is the `sha256sum` of the
bytes fetched, not a transcription.

| Candidate | Decision | URL / access date | Located quote (≤25 words) and location | Reason |
|---|---|---|---|---|
| S618 `ggml/include/ggml.h` @ b12177 | **admit** (A, code, mined) | https://raw.githubusercontent.com/ggml-org/llama.cpp/b12177/ggml/include/ggml.h — 2026-11-08, sha256 `590e00a522b8791235353a8c7388d67ff2fe929554f1834c58528b82afd67392` | "nb[0] = ggml_type_size(type)" (line 697; `ne[GGML_MAX_DIMS]` line 694) | The tensor descriptor a GGUF header mirrors: one element count and one byte stride per rank, which is why a header costs `5 + nd` read/seek steps and why the ceiling is per rank. |
| S619 `gguf-py/README.md` @ b12177 | **reject** (docs, C-class lead only) | https://raw.githubusercontent.com/ggml-org/llama.cpp/b12177/gguf-py/README.md — 2026-11-08, sha256 `f759ed01b8899c392cee7f1bc9012356090dd46014898c2cface1cca5f1e18af` | "This is a Python package for writing binary files in the [GGUF](https://github.com/ggml-org/ggml/pull/302) (GGML Universal File) format." (line 3) | The page documents the Python writer, not the file layout the probe parses; it would ground no step cost. Flip: the page states the header field order and widths the parser prices. |
| `ggml/src/gguf.cpp` @ b12177 as a new row | **reject** (duplicate) | https://raw.githubusercontent.com/ggml-org/llama.cpp/b12177/ggml/src/gguf.cpp — 2026-11-08 | already S129 | The loader is already a Registry row; round 96 cites it through S129, so a second row would be a duplicate URL (census W04). |

`status`/`recheck`/`used-by` changes on existing rows: none. Census before → after: 357 → 358 rows,
`scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama` exit 0.

Assimilation: none taken this round — `considerthese/2026-11-07.md` was read for a candidate claim and
nothing in it beat the three claims declared; it remains unopened for a claim.

## Mistakes

**M1 — a fixture that could never grade its own expected value, twice.**
Class: `vacuous`. Evidence: the frozen W12-strings fixture wrote one 6 MB string with a declared array
length of 6 000 000, so the probe's `base + 8 * n > size` guard graded `invalid` before the step loop; the
counter's own oracle special-cased the header counts and printed `-`, so the sanity gate agreed with the
wrong expectation. Amendment 2 replaced it with `8n` prefixes followed by one payload run — still wrong,
because each element is `[u64 length][payload]` and the reader landed one byte inside the next prefix.
Amendment 3 interleaves (`(pack("<Q",1)+b"x") * n`, 54 000 049 B) and the cell grades `MODEL_OK` in 0.8 s.
Captured-by: wave-1 `RV01StepBudget` F1 and `CR01BudgetCounter` (independently), i.e. the attack seats, not
the L1 — the L1's own oracle was written to agree with the fixture. Fix: the oracle now derives the class
from the array's byte length as well as the header counts, and the fixture is verified through the probe
before the freeze (`MODEL_OK` measured, not asserted). Shown able to fail: the frozen base receipt and
every CR01 attack run carry `W12-strings ok=0`.

**M2 — one constant re-derived by hand and a table row left at the naive quotient.**
Class: `arithmetic`. Evidence: the preamble's four steps were subtracted for ranks 0, 1, 2 and 4 but not
for rank 3, so SKILL.md stated `625,000` where the parser decides 624 999 headers; the depth counter
carried the same wrong value as a required needle, so it blessed the error. Captured-by: nothing in the
round — wave-1 `SC02BaseDiscriminator` binary-searched every row against the tip's own parser and found the
one mismatch. Fix: the row is 624,999, and the counter now derives `(MAX_STEPS - 4) // (5 + nd)` for every
rank and compares it to both its own expectation and the SKILL text. Shown able to fail: the old table plus
the new counter prints `mismatches=1` (the 625,000 needle), and the base revision prints `mismatches=14`.

**M3 — two measurement runs destroyed by the lane's shared scratch root.**
Class: `scratch`. Evidence: both receipts were written with `--work /fast/scratch/hyaku/kama-r96`, the root
the wave's seats also used; a seat deleting its own tree took the in-flight `r96-budget-*` dirs with it, and
both files ended as `FileNotFoundError` tracebacks. Captured-by: wave-1 `SC02BaseDiscriminator`, which saw
the tracebacks and named the cause. Fix: the L1 measures under a seat-private root
(`/fast/scratch/hyaku/kama-r96-c1/<run>`) and writes each receipt to its own file; the frozen counter
already honours `--work`. Shown able to fail: the earlier receipts at `.ufo/waves/round-96/` were committed
as tracebacks by the first attempt and are replaced by complete receipts in this round.

**M4 — the base control was run at the tip.**
Class: `scope`. Evidence: the first `controls/c1-base.out` was produced with `--rev b3289c18`, the amended
tip, so it printed `mismatches=0` — the plan's own "the counter cannot discriminate, the claim is void"
condition — while pretending to be the do-nothing control. Captured-by: `SC02BaseDiscriminator` (the
summary's `probe_sha256=11e5b01b` is the tip's probe, not the base's `b49d961a`). Fix: the control is run
with `--rev 5d43528b`, and the receipt's `probe_sha256`/`rev` fields are quoted in the report so the
revision cannot be mistaken again. Shown able to fail: the receipt now prints
`base_sha256 == probe_sha256` at base and `rev=5d43528b`.

**M5 — the W03 discriminator was frozen to one host's seconds.**
Class: `portability`. Evidence: the margin guard refuses to claim the discriminator unless the W03 pass
costs ≥ 1.25 × 60 s; at 40 files on this host it costs 47–67 s, so the frozen command returns exit 2
(`could-not-evaluate`) and the receipt cannot be reproduced as written. Captured-by: `CR01BudgetCounter`
attack 5 and `SC02BaseDiscriminator`, both naming the host-speed dependence. Fix: amendment 3 names the
file count as a host-speed parameter and the M1 receipt is measured at `--slow-files 96` (163 s / 324 s
observed), with the count and rate quoted in the report.
