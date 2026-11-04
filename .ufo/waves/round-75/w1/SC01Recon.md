# SC01Recon — scoped findings

Report: `.ufo/waves/round-75/w1/SC01Recon/report.md` (receipts in the same directory).

Short form: the S547 page is unchanged (byte-identical to the retained copy, sha256
`ceb3351f931ae86283f51416cf0042fd78265eda59e5af7d09e17581ec0f77f7`, 131174 bytes); the audit's
53 undisclosed events / 389 hash entries re-derive from git history with **zero disagreement**, of
which exactly one event (`ea33a78f2b0b`, 639 lines) is pure CRLF→LF noise and 52 are content edits;
5 of 10 contract rows are unbound and all five are drifted pointers that bound when written.
