## Round 89 — unloadable router model files and a wire-bound router error table (2026-11-06)

Fresh-start round after six rejected closures (rounds 83-88). Base `56174a1fa6a27faa91d3664ef4730b48dd3149c0`;
frozen plan `plans/round-89-claims.md`, counters `tools/round89-unloadable-cells.py` and
`tools/round89-signature-rows.py`, frozen at `4eb75c62f6deb1a586a291d611b71775049b34a6`. Two claims on two
axes, causally separable (C1's counter never reads `SKILL.md`; C2's counter never runs the probe or a
server). **No canned expectation**: every C1 cell's expected verdict is the router's answer to a real
completion at run time, and every C2 row binds to a captured wire answer.

| Claim | Axis | Counting command | Before (base, committed receipt) | Target |
|---|---|---|---|---|
| C1 unloadable router model files (capability `router-unloadable-file-verdict`, sourced S583/S584/S585) | operability | `python3 tools/round89-unloadable-cells.py --repo . --rev <M> --work <scratch>` | `ROUTER_UNLOADABLE cells=11 mismatches=5 positive_mismatches=0 probe=rev`, exit 1, probe `99dd1ab8…` (`.ufo/waves/round-89/controls/c1-base.out`); forgeries F1 `mismatches=3 positive_mismatches=3` (`controls/c1-f1.out`), F2 `mismatches=7 positive_mismatches=2` (`controls/c1-f2.out`) | `cells=11 mismatches=0 positive_mismatches=0 probe=rev`, exit 0, probe `a4f496bb…`; counter bytes equal to freeze; the five harm receipts (`controls/harm-base-probe-verdicts.out`, `controls/harm-base-test-snapshot.out`, `controls/harm-base-r88-oracle.out`, `controls/harm-base-r88-cells.out`, `controls/harm-base-operator-1234.out`) unchanged |
| C2 router error signature table (capability `router-error-signature-table`) | depth | `python3 tools/round89-signature-rows.py --repo . --rev <M2>` | `SIGNATURE_ROWS rows=0 bound=0 unbound=0 duplicates=0`, exit 1 (`.ufo/waves/round-89/controls/c2-base.out`); forgery battery `rows=7 bound=1 unbound=5 duplicates=1`, exit 1 (`controls/c2-forgeries.out`) | `rows=8 bound=8 unbound=0 duplicates=0`, exit 0; counter bytes equal to freeze |

Receipt summary lines, verbatim (`.ufo/waves/round-89/`):

- `controls/c1-base.out` line 13 — `ROUTER_UNLOADABLE cells=11 mismatches=5 positive_mismatches=0 probe=rev probe_sha256=99dd1ab8d41bb682bb24d4747b85d1f86fb84c145c6531cd2f0201d738d54be5 server_sha256=ba272ee3446d9b98c9150c79667e6a8b217f25ee58ce0c6156cc96d2b5b362b0 rev=56174a1fa6a27faa91d3664ef4730b48dd3149c0` (exit 1, line 14)
- `controls/c1-f1.out` line 13 — `ROUTER_UNLOADABLE cells=11 mismatches=3 positive_mismatches=3 probe=rev probe_sha256=bd7a6a2228d04b69abcc5d19f2907a9caf737347ef96ff92722edbc3180e7bdf server_sha256=ba272ee3446d9b98c9150c79667e6a8b217f25ee58ce0c6156cc96d2b5b362b0 rev=138a75437bcd11b72446087e970f5dfc5abf9ccd`
- `controls/c1-f2.out` line 13 — `ROUTER_UNLOADABLE cells=11 mismatches=7 positive_mismatches=2 probe=rev probe_sha256=0943fb461d0226e29d1b8a3b6af67740d4fe6863505ee6ed771719a30fdc3d19 server_sha256=ba272ee3446d9b98c9150c79667e6a8b217f25ee58ce0c6156cc96d2b5b362b0 rev=9b4c7af16fdd4bba9e4815f4615f4b003f340747`
- `controls/c2-base.out` line 2 — `SIGNATURE_ROWS rows=0 bound=0 unbound=0 duplicates=0 rev=56174a1fa6a27faa91d3664ef4730b48dd3149c0` (exit 1, line 3)
- `controls/c2-forgeries.out` line 22 — `SIGNATURE_ROWS rows=7 bound=1 unbound=5 duplicates=1 rev=0c09884dad924640b92135209b9fc7e361f991ee` (exit 1, line 23)
- `measured/c1.out` line 14 — `ROUTER_UNLOADABLE cells=11 mismatches=0 positive_mismatches=0 probe=rev probe_sha256=a4f496bb0ed931792641171a1269a91a8307dce5d534d5f4ee03daba01a7ddaf server_sha256=ba272ee3446d9b98c9150c79667e6a8b217f25ee58ce0c6156cc96d2b5b362b0 rev=4f9eacf720aa59ed806b31b758571e364658179b` (exit 0, line 15)
- `measured/c2.out` line 11 — `SIGNATURE_ROWS rows=8 bound=8 unbound=0 duplicates=0 rev=21b9e36d6192e0a691550b32e0e6c38412227f4c` (exit 0, line 12)
- `measured/harm-M.out` line 2 — `tests=72 passes=72 failures=0` (exit 0, line 3); line 4 — `RESULT pass=30 fail=0` (exit 0, line 5)
- `measured/harm-M.out` line 10 — `ORACLE_CELLS rev=4f9eacf720aa59ed806b31b758571e364658179b cells=3 mismatches=0` (exit 0, line 11)
- `measured/harm-M.out` line 16 — `ROUTER_CELLS cells=17 mismatches=2 canned=14 live=3 probe=rev probe_sha256=a4f496bb0ed931792641171a1269a91a8307dce5d534d5f4ee03daba01a7ddaf` (exit 1, line 17; the two are C05 and C12, lines 13 and 15 — the frozen counter's expected residual, not a green)
- `measured/host-gguf-sweep.out` line 38 — `HOST_GGUF_SWEEP files=36 ok=36` (no loadable local file graded invalid)

### Round-89 measured results

| Claim | Measured commit | Counting command → output | Verdict (author) |
|---|---|---|---|
| C1 operability | `4f9eacf720aa59ed806b31b758571e364658179b` | `python3 tools/round89-unloadable-cells.py --repo . --rev 4f9eacf7… --work <scratch>` → `ROUTER_UNLOADABLE cells=11 mismatches=0 positive_mismatches=0 probe=rev`, exit 0; counter sha256 `1d86194c…` at M equal to freeze (line 1 of `measured/c1.out`); harm (`measured/harm-M.out`): `tests=72 passes=72 failures=0`, `RESULT pass=30 fail=0`, `ORACLE_CELLS … cells=3 mismatches=0`, `ROUTER_CELLS … mismatches=2` (C05, C12), operator router GET `MODEL_OK router-unloaded-autoload` on all four entries | Frozen predicate met at M: K1 `positive_mismatches=0`; K2 every harm receipt agrees with its base counterpart (the round-88 counter keeps its own residual, C05 and C12); K3 the counter's bytes are unchanged from the freeze. |
| C2 depth | `21b9e36d6192e0a691550b32e0e6c38412227f4c` | `python3 tools/round89-signature-rows.py --repo . --rev 21b9e36d…` → `SIGNATURE_ROWS rows=8 bound=8 unbound=0 duplicates=0`, exit 0; counter sha256 `30f3af7f…` at M2 equal to freeze (line 1 of `measured/c2.out`) | Frozen predicate met at M2; K2 holds — no row carries a message the receipt does not hold (the forgery battery's fabricated row was unbound at base). |

Score deltas: none claimed — no axis score moves this round. Two capabilities enter the repertoire with
first-working round 89, and the `router-mode-readiness` row's evidence pointer is re-pointed so it names
a green of the landed rule (round-88 closure D1/R2).

### Round-89 disclosed limits

- The probe reads the GGUF **header only** and never opens a non-regular file or any tensor data, so a file
  whose header parses but whose tensor payload is corrupt still grades `MODEL_OK`; only a real load tells.
- The file check runs only when `status.args[0]` is a local file as this host sees it. A containerised or
  remote router, a relative path, an unknown tensor type and a parse-budget overrun keep the previous
  verdict on purpose: a false red is worse than the known false green.
- Operator-router evidence differs in form between base and M (base: one registry row,
  `model_ok=1 drift=0 exit=0`; M: per-model lines, `MODEL_OK router-unloaded-autoload` on four entries);
  both receipts agree on the verdict and neither loads a model.

