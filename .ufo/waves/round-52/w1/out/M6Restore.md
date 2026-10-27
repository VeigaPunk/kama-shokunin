INCOMPLETE — only the drop-one-restored-line mutation was exercised; remaining five requested probes were not run.

Evidence (C2: `tools/round52-append-restore-check.py`):
- Pristine build tip `5dacf2c70f947ca6dc5fbbca6d45b8db5b0390c8`: `fixture=1 lane=1 scenarios=8/8 corr_lost=0 row_lost=10 disclosed=10 met=True`, exit 0.
- Base tip `9ff76b1f763512be2f554cbbfd0b2213b63b0847`: `fixture=1 lane=0 scenarios=8/8 corr_lost=151 row_lost=10 disclosed=165 met=False`, exit 1 (matches the supplied base control).
- Drop-line mutant commit `a180cf38db5086cbe70ada0ed00e359c5bdb5445`: removed the restored LOG.md line `.ufo/waves/shokunin12h-20261014-p1-repair/members/.` from its fenced block. Counter output: `fixture=1 lane=0 scenarios=8/8 corr_lost=2 row_lost=10 disclosed=10 met=False`, exit 1. Tool v6 exit 1; summary reported `unrestored=1`, `regressed=1`; counter detail reported `unheld lines in A-corr files: {'LOG.md': 2}`. Verdict: KILLED.
- The remaining requested mutants (one-byte change, cross-file move, trailing space, duplicate block, fence removal) were NOT run; no verdict is claimed for them.

Restoration evidence: pristine LOG.md SHA-256 before mutation `7ce31c07e17d59be4bff8e1ae27bc253df71a614980ebf200998c6d4f0b8618f`; after `git reset --hard 5dacf2c70f947ca6dc5fbbca6d45b8db5b0390c8`, same SHA-256. Scratch clone was removed. No llama-server process was started by this probe. No tools installed.
