Verdict: No actionable counter-vs-preregistration defect found for C1.

Evidence (all paths relative to `kama-shokunin/`):

- `tools/round52-replay-memfd-audit.py` compared with `tools/round51-replay-exe-audit.py` using `diff -u` (exit 1, expected differences). The delta replaces the extracted-path identity leg with the sealed-memfd leg and updates base, source reference, outputs, and labels; round-50 bind and teardown checks remain. In the new `sealed_exe()` (lines 361–392), the counter reads `/proc/<pid>/exe`, obtains `fstat`, F_GET_SEALS, and hashes the open image; it requires a `/memfd:` link, `st_nlink == 0`, all four seal bits, and the frozen server digest (lines 384–391).
- Predicate parity: preregistration `claims[0].predicate` and the docstring PREDICATE at lines 49–56 are exactly equal after joining docstring line wraps (normalized string comparison: `True`). The sentence includes the three receipts, observed image properties, receipt server_exe and replay own_server correspondence, round-50 bind, teardown, new source row, and all four output leg flags.
- Clause coverage: receipt `server_exe` is checked for opened/digest/dev/inode/seals at lines 499–503; `own_server` for memfd/dev/inode at 504–507. Per-receipt results are aggregated as all three runs at 623–627; `met` is solely `bool(bl and ol and tl and nl)` at line 631. Thus no non-predicate condition directly decides `met`; bind/teardown/newrow are the predicate legs. Model availability and replay/receipt health contribute to bind/sealed leg failures rather than being independent met conditions.
- `newrow_leg()` compares new SOURCES rows from tip against BASE and requires the memfd_create URL (565–575). `teardown_leg()` checks invoker kill, descendant disappearance, port refusal within KILL_WAIT=30 (533–562). Existing bind checks remain within `bind_one()` (459–530).
- SHA-256: `sha256sum tools/round52-replay-memfd-audit.py` produced `053ff50261812de3236697dd8dc847b3dff9507f8290b0d42aaf65c12e1121f5`, equal to preregistration `counter_sha256` at claims[0].

No counter execution was performed; this review covered frozen source, predicate parity, and checksum only. No tools installed or updated.
