# Round 96 — amendment 3 (W12 element layout; the W03 count is a host-speed parameter)

Date: 2026-11-08. Author: L1 `KamaR96`. Amendment 2 `fb5cd3cd`; this amendment lands the two fixes its
own measurement exposed.

## A — W12's element bytes were contiguous, not interleaved

Amendment 2 wrote `8 * n` length prefixes followed by one 6 MB payload run. The parser reads each
element as `[u64 length][payload]`, so after element 0 the reader lands one byte into the next length
prefix, reads a huge length, and the `base + off > size` guard grades the file `invalid`. Amendment 3
writes `(pack("<Q", 1) + b"x") * n` — 9 bytes per element, 54 000 049 bytes total — and the cell grades
`MODEL_OK/router-unloaded-autoload` through the probe (0.79 s, measured).

## B — the W03 pass must be sized to the host, not to one host's seconds

The counter refuses to claim the discriminator unless the W03 pass costs ≥ 1.25 × 60 s (the round-94
constant). On this host at the amended revision, 40 distinct 600 000-tensor files cost 47.4 s, so the
frozen `--slow-files 40` returns `could-not-evaluate` (exit 2). The file count is therefore a
host-speed parameter of the same cell: the receipt for M1 is measured with `--slow-files 96`
(≈1.9 s/file at the observed rate → ≈114 s, above the guard). The cell's identity — "many distinct
slow files, each undecidable under the base wrapper, all of them graded" — is unchanged; only the
count that makes the guard true on this host changes, and the receipt names the count it used.

Kill rule K3 binds the amended commit as the reference: the counter is byte-identical at this
commit and at the M1 receipt's revision.
