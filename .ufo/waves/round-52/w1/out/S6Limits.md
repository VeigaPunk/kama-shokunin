# S6Limits — carried C1 limits

**Verdict: the R52 memfd design closes disk-path copy, hardlink, and rename-over substitution for the observed running server image; it does not prove archive-source provenance or close the R50 operational limits.**

The detailed carried-limits table, with evidence paths/symbols and disposition for each R48–R51 C1 limit and D5 item, is in `w1/out/S6Limits/limits.md`. Evidence was read from the frozen R52 counter contract (`tools/round52-replay-memfd-audit.py:32-48`), preregistration (`.ufo/waves/round-52/preregistration.json:39-45`), R48/R49/R50/R51 SCORECARD sections, and R51 closure D5 (`corpus/lessons/round-51-verifier-spotcheck.md:52-56`).

The counter's `sealed` leg opens `/proc/<pid>/exe` during the hold, checks `/memfd:`, `st_nlink == 0`, all four seals and the frozen digest, then checks matching dev/inode/seals/digest in the rerun receipt and replay `own_server`. This addresses the R51 disk member copy/hardlink/rename-over image substitution. It leaves archive provenance open: the preregistration explicitly accepts a host-byte-identical install as memfd content and says archive download/read is unobserved (`preregistration.json:41`). R50's probe-PATH execution, post-map model rewrite, and kills during download/readiness remain explicitly unaddressed (`:43`). Linux `/proc`, network access to GitHub/Hugging Face, and the b11909 prerelease dependency remain.

This is a source-based limits classification, not a runtime verification; I ran no counter. Output: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/S6Limits/limits.md`.
