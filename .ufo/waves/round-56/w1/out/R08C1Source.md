# R08C1Source — S512 quote check

Axes: operability, calibration.

## Finding

S512’s source anchor and quote are verified. The committed snapshot `.ufo/waves/round-56/sources/rtld-audit.7.html` is indexed in Git at blob `e705ff591094963aaaf990b6fea96772c638e717` and its working-tree hash matches. The quote appears under the `DESCRIPTION` heading (snapshot lines 75–92): “the environment variable LD_AUDIT must be defined to contain a colon-separated list of shared libraries”. The same wording appears in the live `https://man7.org/linux/man-pages/man7/rtld-audit.7.html` fetched 2026-10-27 (HTTP 200); that page identifies man-pages 6.19, dated 2025-05-17, matching S512’s revision metadata.

Word count: 15 whitespace-delimited words, within the 25-word limit. The round-56 lesson and registry both declare 15; the anchor is §DESCRIPTION. The wording removes HTML markup around `LD_AUDIT` and collapses the source line break; text content is otherwise verbatim.

## Scope note

The source establishes that LD_AUDIT is defined as a colon-separated list of shared libraries for the auditing interface. By itself it does not establish that every supplied library loads successfully or that a particular DSO is accepted; the lesson appropriately treats the variable name as the gate target.

No tools installed. No counter/battery checks run.
