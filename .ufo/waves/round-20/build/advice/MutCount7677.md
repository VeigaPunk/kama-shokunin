VERDICT: confirm — 76 and 77 are both correct, but for different gate revisions.

## Finding

- **76** is the clean gate result at `7229fa95` and `5b108c1a`. Both commits resolve `tests/llamacpp-live/check-receipt.py` to blob `fe53e78963c1ef8cfec6313018835d06a98c905a`; the selftest prints 76 and exits 0 at each. This supports round-19 report line 91 when read against the round's measured/start gate.
- **77** is the result at `f1790e25`, `028235e6`, and round tip `37bd4c5b`. They share gate blob `e90be78d58c5bf11e402f9c137a81767ad44df23`; each selftest prints 77 and exits 0. This supports report line 112 and the report's named work-measurement commit `028235e6`.
- The increment is one concrete case, not a recounting error: `5b108c1a..f1790e25` adds the fail-closed check for an empty `server.install_tree` and the `tree-empty-map-with-pin` selftest (diff: +7 lines, exit 0). The static census rises from helper cases `mut=36` to `mut=37`; `mut2=13`, `mut3=25`, and literal exit-1 cases remain unchanged.

## Why final-selftests.txt says 77 on 5b108c1a

`.ufo/waves/round-19/evidence/final-selftests.txt:1` labels its measurement `working-tree-on-5b108c1a…`, while lines 3 and 9 record 77 and C1 `required=3`. It is a dirty-working-tree label, not a source-blob pin. Clean `5b108c1a` reproduces 76; the evidence file is committed in `f1790e25`, whose gate contains the added case and reproduces 77. **[INFERENCE]** The measured working tree had acquired the f1790e2 empty-tree gate change before the selftest was run; the evidence records no gate digest, so the exact executed bytes cannot be proven from that receipt alone. The C1 count of three also places the recorded snapshot before `028235e6`'s four-row registry change; 028235e6 retained the 77-case gate.

## Static-count qualification

The gate itself computes `n_mut = sum(1 for c in cases if c[3] == 1)` (`check-receipt.py:2164–2169`); the printed 76/77 therefore means **expected exit-1 selftest cases**. It includes two `--require-schema` rejection cases using unmutated base receipts (`v1-require-schema-v2-rejects-v1` and `v2-require-schema-v3-rejects-v2`). If “mutations” means cases that actually mutate a receipt, the counts are 74 at `7229fa95`/`5b108c1a` and 75 from `f1790e25` onward. The gate's own summary calls the broader exit-1 total “mutations.”

## Commands run / observed exits

1. Static AST census (stdlib only; reads committed gate blobs, does not import/run the gate): `python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-20/build/out/MutCount7677/gate-case-census.py /home/vgpnk/Projects/shokunin/kama-shokunin` — **exit 0**. Output: `7229fa95` and `5b108c1a` blob `fe53e789`, expected exit-1 total 76 (`mut=36, mut2=13, mut3=25, literal=2`); `f1790e25`, `028235e6`, and `37bd4c5b` blob `e90be78d`, total 77 (`37,13,25,2`).
2. Dynamic reproduction: `python3 tests/llamacpp-live/check-receipt.py --selftest` in detached worktrees for `5b108c1`, `f1790e2`, `028235e`, and `37bd4c5` — respectively **exit 0** and output `76`, `77`, `77`, `77` mutations, each with `6 VALID` and `1 NOT-EVALUATED` receipt accepted.
3. `git -C /tmp/kama-r20-MutCount7677/lane show f1790e25b421f02596798ad665488b066541ae3a:.ufo/waves/round-19/evidence/final-selftests.txt` — **exit 0**, outputs the dirty-tree label and recorded 77 / required=3 values above.
4. `git -C /tmp/kama-r20-MutCount7677/lane diff --unified=2 5b108c1a7e943c571140df3a1d7e2e29bfdfb501 f1790e25b421f02596798ad665488b066541ae3a -- tests/llamacpp-live/check-receipt.py` — **exit 0**, reports 7 additions including `tree-empty-map-with-pin`.
5. `git -C /tmp/kama-r20-MutCount7677/lane log -1 --format='%H %s' f1790e25b421f02596798ad665488b066541ae3a -- .ufo/waves/round-19/evidence/final-selftests.txt` — **exit 0**, identifies `f1790e25… round-19: empty-tree rejection, C1 scope erratum, separability correction, final receipts` as the commit adding the evidence.

No tools were installed. No lane source or history was modified; only this report and the static census script under the assigned round-20 output/advice paths were created.