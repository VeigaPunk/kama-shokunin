# CR01ClaimC1 — C1 operability, closure attack (kama r89 w1)

## Scope
Attacked frozen C1 only, as its own predicate defines it: (a) predicate/counter/receipt alignment, (b) independent reruns
at B/F1/F2/M, (c) an overfit forgery against the 11 cells plus held-out cells outside the counter, (d) the oracle mapping,
(e) harm and the plain verification statement. Read-only in the lane; one scratch dir; no subagents; no tools installed;
no request to 127.0.0.1:1234; every router child lane-owned and killed by process group.

## Commands and outputs (true exit codes)
1. `git show <rev>:tools/round89-unloadable-cells.py | sha256sum` — F `4eb75c62…`, M `4f9eacf7…`, M2 `21b9e36d…` all
   `1d86194c27740a8afa6e49bfdedfcef535016a20f75af2bcf6582fd2cdfdc315`; at B/F1/F2 the file is **absent** (`git show`
   rc=128), so those controls necessarily ran the freeze counter against historical probe bytes.
2. Probe bytes: F `99dd1ab8…d54be5`, F1 `bd7a6a22…0e7bdf`, F2 `0943fb46…3d19`, M=M2 `a4f496bb…a7ddaf` — each equals the
   `probe_sha256` its receipt records.
3. `python3 tools/round89-unloadable-cells.py --repo <lane> --rev <rev> --work <scratch>/work-<rev8>`:
   B exit=1 (`mismatches=5 positive_mismatches=0`), F1 exit=1 (3/3), F2 exit=1 (7/2), M exit=0 (0/0). After dropping
   each receipt's `#` header and `exit=` line, **every line is byte-identical** to `controls/c1-base.out`,
   `controls/c1-f1.out`, `controls/c1-f2.out`, `measured/c1.out` (diff of all cell+summary lines, empty).
4. `--probe-file` runs at `--rev M`: `forged-probe.sh` (never opens a model file) exit=0 `cells=11 mismatches=0
   positive_mismatches=0`; `forged-probe-bogus-reason.sh` (all reasons `bogus`) exit=0 11/0/0; `forged-m-probe.sh`
   (byte copy of M probe + five-line fixture-name shortcut) exit=0 11/0/0. Files: `forged-*counter.out`.
5. Held-out harness (imports the counter's own `start/run_probe/oracle/http/kill_children`; one lane-owned b12177 child;
   default autoload; absolute `--models-dir` + preset), `overfit-disagreement.out`: `validmodel` oracle 200 / real OK /
   forgery OK; **`trunc.gguf` = a valid full model**: oracle 200, real M probe `MODEL_OK`, stub forgery
   `MODEL_UNLOADED/router-model-invalid` (false red); **`weird-bad.gguf` = GGUF magic+v3+4096-byte noise, name not in
   the fixture set**: oracle 500 `model name=weird-bad failed to load`, real `MODEL_UNLOADED/invalid`, forgery `MODEL_OK`;
   **`absentx` = missing preset, name not in the set**: oracle 500, real `MODEL_UNLOADED/missing`, forgery `MODEL_OK`.
   `one_side_wrong=3`. `overfit-disagreement-mcopy.out`: the patched M probe also false-reds the valid file named
   `trunc.gguf` (`one_side_wrong=1`), and is correct on the neutral bad-header/missing cells.
6. S583 @ `6c01da62` GET (`sha256 cab14969b9e5adf08a057c622d1abfc30fd8a17484de5b35942632d739a71108`, matches the
   lesson): line 1641 `throw … "failed to load"`, 1951 `"model name is missing…"`, 1956 `"model '%s' not found"`,
   1962 `"model is not loaded"` (excerpt: `s583-oracle-lines.txt`).

## Findings
1. NOTE (predicate alignment, a): `plans/round-89-claims.md:25`, counter docstring
   `tools/round89-unloadable-cells.py:7` and `measured/c1.out:14` state the same condition — `cells=11 mismatches=0
   positive_mismatches=0`, exit 0, counter bytes equal to the freeze; wording differs only in `<M>/<R>` placeholders.
   The receipt header records counter sha at M and at freeze as the same `1d86194c…`, which `git show` confirms at F, M, M2.
2. NOTE (counter availability, a/b): the counter exists only from F onward; the B/F1/F2 controls ran it from the freeze
   bytes against old probe revs, and their headers say exactly that (`counter_sha256=1d86194c…`). Not a defect — but it
   means those three receipts test probe bytes, not a counter at those revisions.
3. DEFECT (evidence strength, c): the 11 cells are satisfied by fixture-name keying, not the rule. A probe that opens no
   file passes 11/0/0 exit 0, and a copy of the real M probe with only `absent-model|gone → missing`,
   `notgguf|badhdr|trunc → invalid` added to `file_state` also passes 11/0/0 exit 0. Outside the counter the forgery and
   the rule disagree in both directions: a valid GGUF named `trunc.gguf` is false-red (oracle 200) while M is MODEL_OK,
   and a bad header named `weird-bad.gguf` is false-green while M is MODEL_UNLOADED/invalid
   (`overfit-disagreement*.out`). The cells bind fixture basenames and verdict polarity, not GGUF validation.
4. DEFECT (unbound reasons, c): the counter compares only the verdict — `ok = exp == got` (:309), `reason` is returned at
   :188 but never compared. `forged-probe-bogus-reason.sh` prints `reason=bogus` on all 11 cells and still exits 0 with
   0 mismatches. The receipt's `router-model-missing` vs `router-model-invalid` columns therefore bind nothing; returning
   `router-model-missing` for U2–U4 would pass.
5. NOTE (cell coverage, c): of the claimed header checks the cells exercise only magic (U2), the count-fit check
   `n_kv*13+n_tensors*24 > size` (U3, whose body is magic+v3+4096 bytes of `sha256("kama-r89-<i>")`), and data-past-EOF
   (U4 = first half of valid bytes). No cell covers version, alignment, >4 dims, `ne[0]` block multiple, or non-contiguous
   offsets; a candidate implementing magic+counts+EOF only would pass 11/11.
6. NOTE (blanket probes, c): yes, the positive cells stop a blanket refusal — F1 (round-88 measured probe, unloaded/
   sleeping always drift) reruns at `mismatches=3 positive_mismatches=3` (P1, P3, P4) exit 1; F2 (any listed id OK) at
   7/2. But N1/N2 are oracle-UNLOADED on an autoload-off router whose 400 cannot distinguish a healthy unloaded model
   from an unloadable one; those two positives pin the pre-existing no-autoload branch, not the new rule.
7. NOTE (oracle, d): no observed answer in the 11 cells is mislabelled. The five U answers are the exact
   `{"error":{"code":500,"message":"model name=<id> failed to load","type":"server_error"}}` envelope (captured for two
   held-out cells; the oracle would exit 2 otherwise), the four P answers are 200, the two N answers are the 400
   `model is not loaded` branch. Anything else (e.g. `model '<id>' not found`, S583:1956) exits 2, which is correct.
   Two residual points: the mapping is message-based, so a future 500 `failed to load` from a non-file cause (OOM) would
   expect MODEL_UNLOADED although the file rule would say OK — no such cell exists; and claims R7 ("S583 lines
   1641/1956/1962 match the three mapped answers") is inaccurate — 1956 is `model '%s' not found`, which the oracle does
   *not* map (400 is 1962, 500 is 1641). No effect on the frozen counter.
8. NOTE (harm, e): K1 holds — my M rerun prints `positive_mismatches=0`. K2 holds per receipts: `measured/harm-M.out`
   72/72, 30/0, r88 oracle 0 mismatches, r88 router-cells 2 (C05, C12 only, as allowed), operator 1234 all four entries
   `MODEL_OK/router-unloaded-autoload`; base and M agree on every line. Held-out: the shipped M probe is correct on 4/4
   cells, with no false red on a valid file carrying a fixture name.

## Deliverables
`.ufo/waves/round-89/w1/out/CR01ClaimC1/`: `rerun-{56174a1f,138a7543,9b4c7af1,4f9eacf7}.out`,
`forged-probe.sh`, `forged-probe-bogus-reason.sh`, `forged-m-probe.sh` (M bytes + name shortcut),
`forged-counter.out`, `forged-bogus-reason.out`, `forged-m-probe-counter.out`, `overfit-disagreement.py`,
`overfit-disagreement.out`, `overfit-disagreement-mcopy.out`, `s583-oracle-lines.txt`.

## Bottom line (e)
C1 verifies on its frozen predicate with no harm: the counter is byte-identical at F/M/M2, my independent reruns reproduce
every committed receipt line-for-line (M exit 0, 0/0), and the shipped M probe is correct on all 11 frozen cells plus 4
held-out cells. The gate is weaker than it reads: a name-keyed probe passes 11/11 and the reason column is unbound, so the
counter is necessary but not sufficient evidence of the rule. Smallest safe correction for the *next* counter revision
(the frozen predicate must not change this round): randomize fixture basenames per run, promote the three held-out cells
(valid file under an invalid-sounding name, bad header under a neutral name, missing preset under a neutral name), and
assert the per-cell reason class (a fixture property, not a canned runtime answer).

VERDICT: holds — counter reproduces 0/0 at M with identical bytes and the shipped probe is correct on 4/4 held-out cells, but a name-keyed forgery passes the 11 cells, so the gate is necessary, not sufficient.
