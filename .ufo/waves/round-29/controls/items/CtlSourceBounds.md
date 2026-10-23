# CtlSourceBounds (mutation-tester)

Policy: predict from statement text alone. Using only the base SCORECARD.md/SHONEN.md text and the extraction code (no blob at any revision other than those two base files, no git log/blame/grep, no receipt), predict which statements are false from their text (e.g. a pointer path without a directory or naming a fleet file, a quoted output that looks like transient terminal output); write correction rows only for the predicted ones with the class failure string; record your prediction rule in REPORT.md BEFORE scoring. Commit and score.

Your item name: CtlSourceBounds. Output dir: /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/controls/CtlSourceBounds/. Clone path: /fast/scratch/hyaku/kama-r29/ctl/CtlSourceBounds/repo.
