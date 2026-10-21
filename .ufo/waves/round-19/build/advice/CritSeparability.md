VERDICT: partial - C1 and C2 are causally separable by counting command (2x2 toggle matrix is block-diagonal, 8/8 equality checks hold), but the lesson's "No shared source file" is false: SOURCES.md and SCORECARD.md carry text from both claims and both are scanned by the C1 counter, and run.py couples them at harness level.

# Scope and bounds

- Copy: /tmp/kama-r19-CritSeparability (`cp -a` exit 0). Copy HEAD is 8bf99ca, one commit past the declared round start 1b85a24; 8bf99ca adds only corpus/lessons/round-18-verifier-spotcheck.md, which is in neither claim's file set and contains no cite() token (grep, executed).
- Lane: read-only except this report. No installs or updates. curl (read-only) fetched https://man7.org/linux/man-pages/man8/ld.so.8.html, exit 0, 41398 bytes, sha256 d9b7737e6c9a38f6c7ce11a4feec834704d6ad5139dc790afa9798faf0379f83.
- NOT executed: `.ufo/waves/round-18/runs/run.py`. It hardcodes `L=/home/vgpnk/Projects/shokunin/kama-shokunin` (line 5), so it would write into the lane, and it launches a live llama-server. Its dirty guard (lines 8-13) was replicated on the copy with the same expression.
- Receipts: /tmp/kama-r19-CritSeparability/out/ (commands.json: 41 commands with argv, cwd, exit, stdout/stderr sha256; receipts/*.{stdout,stderr,exit}; states/S00,S10,S01,S11 reconstructed doc sets; matrix.json; s057-quotes.json; ld.so.8.html).

# File-set partition (working tree vs HEAD 8bf99ca)

| File | C1 | C2 | Counter reads it |
|---|---|---|---|
| tools/citation-provenance.py (new) | yes | | C1 |
| registry/required-citations.json (new) | yes | | C1 |
| .ufo/waves/round-18/residual/assignments.json (new) | yes | | none (grep: no reader) |
| corpus/lessons/round-18.md (EOF append, 3 tokens) | yes | | C1 (DEFAULT_DOCS) |
| tests/llamacpp-live/check-receipt.py (sixth pin, selftest cases) | | yes | grid, gate |
| tests/llamacpp-live/install-tree-grid.py (new) | | yes | grid |
| .ufo/waves/round-18/runs/run.py | | yes | none (not executed) |
| corpus/SOURCES.md | S055 block, EOF lines 217-224 | S057 row, line 69 | **C1 (DEFAULT_DOCS)** |
| SCORECARD.md | defect-3 erratum 809-813, C1 para 821-826 | C2 para 828-835 | **C1 (DEFAULT_DOCS)** |
| corpus/lessons/round-19.md (untracked) | declares | declares; S057 gate table | none (inert) |

# Counting-command separability: 2x2 toggle matrix

C1 toggle = tokens and C1 text in round-18.md, SOURCES.md, SCORECARD.md. C2 toggle = gate pin plus S057 row plus C2 SCORECARD paragraph. Held constant: C1 tool and registry, grid script, LOG.md, receipt-1.json (sha256 89728a02…, identical to HEAD). Pins are read from the receipt: model 270cba1b…, server b6a31a8e…, impl e404b91a…, probe 36b64978…, tool 83eac5c0…, tree 6c216313…

| state (C1,C2) | C1 `citation-provenance.py` | grid, no pin | grid, `--tree-sha` | gate `--expect-install-tree-sha256` |
|---|---|---|---|---|
| S00 (off,off) | exit 1: `required=3 found=0 verified=0 missing=3 mismatch=0` | exit 1: `baseline=VALID members=3 rejected=0/3 tree_pin=off` | exit 2: `baseline=INVALID members=3 rejected=3/3 tree_pin=on` | exit 2 (argparse: unrecognized argument) |
| S10 (on,off) | exit 0: `required=3 found=3 verified=3 missing=0 mismatch=0` | exit 1: 0/3 | exit 2: INVALID, 3/3 | exit 2 |
| S01 (off,on) | exit 1: missing=3 | exit 1: 0/3 | exit 0: `baseline=VALID members=3 rejected=3/3 tree_pin=on` | exit 0 |
| S11 (on,on) = working tree | exit 0: verified=3 | exit 1: 0/3 | exit 0: VALID 3/3 | exit 0 |

Equality checks, all true: c1-default == c1-S11; c1 S10 == S11 (C2 toggle, C1 on); c1 S00 == S01 (C2 toggle, C1 off); grid-nopin S00 == S10, S01 == S11, S00 == S01 (optional flag leaves the pre-pin measurement unchanged); grid-pin S00 == S10, S01 == S11.

Selftests: `citation-provenance.py --selftest` exit 0 ("selftest: ok (5 cases)"); `check-receipt.py --selftest` exit 0 in all four states. Mutant gate_exit under the pin is 1 for all three members; without the pin it is 0.

Command shapes (exact argv in out/commands.json): C1 `python3 tools/citation-provenance.py` (default run, exit 0). Grid `python3 tests/llamacpp-live/install-tree-grid.py --gate <gate> --receipt .ufo/waves/round-18/live-recovery/receipt-1.json --model-sha 270cba1b… --server-sha b6a31a8e… --impl-sha e404b91a… --probe-sha 36b64978… --tool-sha 83eac5c0…` with `--tree-sha 6c216313…` for the pinned run. The SCORECARD command elides these pins with "…" and is not reproducible from the prose.

# Shared-file coupling (named)

1. **corpus/SOURCES.md and SCORECARD.md (both shared; both C1 counter inputs).** Inert today: C2 text holds no cite() token (tokens_per_doc = 0 for both in S01 and S11). But the counter accepts a token from any scanned doc. Adversarial: the three tokens placed only in SOURCES.md, with round-18.md at HEAD, gives `required=3 found=3 verified=3 missing=0 mismatch=0`, exit 0, documents=[SOURCES.md] (c1-adv-tokens-in-sources-json). Document precedence is missing (the lesson's own mined class (a)), and the shared file is the open route.
2. **corpus/lessons/round-19.md** declares both claims and holds the S057 gate table. No reader: grep for round-19 across tools, tests, and run.py finds only a docstring line in install-tree-grid.py (line 13). Inert.
3. **registry/required-citations.json.** S057's used-by cell (SOURCES.md line 69) names it, but `grep -c S057` = 0. C2's grounding is covered by no required row, so "required=3" says nothing about S057.
4. **.ufo/waves/round-18/runs/run.py (C2-owned), harness coupling.**
   - Dirty guard (lines 8-16) refuses unless every dirty path is under runs/ (not run.py) or live-recovery/. Replicated on the copy, it blocks 11 lane paths: M run.py, M SCORECARD.md, M corpus/SOURCES.md, M corpus/lessons/round-18.md, M tests/llamacpp-live/check-receipt.py, ?? residual/assignments.json, ?? .ufo/waves/round-19/, ?? corpus/lessons/round-19.md, ?? registry/required-citations.json, ?? tests/llamacpp-live/install-tree-grid.py, ?? tools/citation-provenance.py. Neither claim can be measured through the harness until both are committed together.
   - No citation-provenance step: grep finds no citation/required-citations in run.py, and its exit (line 95) covers only its own records. The harness pass says nothing about C1.
   - run.py rewrites runs/commands.json cumulatively. C1's three required rows pin older blobs (commands.json@1c325b2, live-gate-1.stdout@eb78788, c2-survivors.stdout@1b85a24), so the coupling is provenance prose, not counts.
5. **receipt-1.json (C2 input) vs C1 prose.** SOURCES.md S055 block and round-18.md line 399 cite "tool 83eac5c0"; receipt-1 tool sha256 = 83eac5c0… (consistent today; not registry-checked).
6. **Naming collision.** "C2" in registry id `c2-official-stdout`, round-18.md erratum (line 421) and SCORECARD erratum (809-813) denotes round-18's survivors counter. Round-19's C2 is the grid. No numeric effect, but readers will conflate them.

# Defects found (each reproduced)

- **D1 (calibration, C1 authority).** No per-row document binding; see coupling 1. Smallest correction: each registry row names its authoritative doc (e.g. `"doc": "corpus/lessons/round-18.md"`), and `check()` filters hits to that doc.
- **D2 (calibration, S057 row and lesson Gate row).** Quotes are verbatim (s057-quotes.json: q1_found true, q2_found true), but the word counts are wrong. q2 "are searched only to find those objects required by DT_NEEDED" is 10 tokens; the row says 11. q1 quoted as "$ORIGIN ... expands to the directory containing the program or shared object" is 11 tokens; the row says 14. The page span "$ORIGIN (or equivalently ${ORIGIN} ) This expands ... shared object" is 16 tokens. Smallest correction: state 10 and 11 (or drop counts), and remove the used-by registry clause or add a registry row.
- **D3 (operability, grid summary).** `rejected` counts any nonzero gate exit (install-tree-grid.py lines 93-94) and ignores baseline validity. Reproduced: HEAD gate plus `--tree-sha` prints `baseline=INVALID members=3 rejected=3/3 tree_pin=on` with mutant gate_exit=2 (grid exit 2). The exit code prevents a false pass, but the summary and JSON show 3/3. Smallest correction: count only gate_exit==1, and print `rejected=n/a` when the baseline is INVALID.
- **D4 (operability, silent member fallback).** When none of the three named members is in the receipt tree, lines 71-73 substitute `sorted(tree)[:3]`. Reproduced on a synthetic receipt: prints `members=3` with rows LICENSE, ggml-rpc-server, libggml-cpu-alderlake.so, exit 1, stderr empty. The current receipt is unaffected. Smallest correction: exit 2 instead of falling back.
- **D5 (lesson text).** round-19.md line 21 "No shared source file." is false (SOURCES.md, SCORECARD.md, and round-19.md itself hold both claims). Smallest correction: name the three shared files and state that the 2x2 shows them count-inert.

# Advice for the main agent (checks I did not run)

After a joint commit of both claims (the harness refuses dirty trees): run `python3 tools/citation-provenance.py` (expect exit 0, counts above), and the grid with and without `--tree-sha 6c216313…` (expect exit 1 with 0/3, then exit 0 with 3/3). Run the C1 counter alongside the harness; the harness does not cover it. Apply D1-D4 before the claims are re-measured.

# Unexecuted reasoning

- [INFERENCE] run.py would print "refusing: lane working tree is dirty" and exit 2 on the lane today. The guard was replicated, not run.
- [INFERENCE] Rev-pinned registry rows remain valid after any future run.py re-run. This follows from git cat-file at a fixed rev; the registry was not re-verified against regenerated outputs.
