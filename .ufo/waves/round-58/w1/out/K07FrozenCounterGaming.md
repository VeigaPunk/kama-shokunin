# K07FrozenCounterGaming — round 58 C1 counter attack

Axes: operability; calibration.

## Counterexample and evidence

The counter’s oracle is the checker’s exit code on 15 fixture repositories. It creates each repository under `work/<case-name>` and commits the same shared files plus the chosen committed variant as `tools/round56-env-leg-battery.py` (counter lines 103–121). It does not require the checker to inspect that blob or any source: its only classification is whether the checker exits 0 (lines 64–68, 130–144).

A checker that branches solely on the fixture directory basename passes the complete frozen predicate. I ran the unchanged counter code against a scratch checker that accepts only names `genuine`, `B1-rename-comment`, `B2-helper-leg`, `B3-concat-labels` and rejects all others. Exact command: `TMPDIR=/fast/scratch/hyaku/kama-r58/K07FrozenCounterGaming; cd "$TMPDIR" && python3 <inline Python harness importing tools/round58-c1-counter.py and invoking main with --repo /home/vgpnk/Projects/shokunin/kama-shokunin --tip HEAD --checker gaming.py>`; output: `genuine=1/1 benign=3/3 noop_rejected=11/11 errors=0 met=True`, all 15 details matched those basename classifications, `fixture-name-only-checker rc=0`; exit 0. Scratch checker and harness were removed.

A checker that branches solely on commit author/message (`c1-counter|fixture`) does *not* pass as currently implemented: output was `genuine=1/1 benign=3/3 noop_rejected=0/11 errors=0 met=False`, counter exit 1. The name-only checker is stronger because those names are explicit and stable in counter source. The fixture commit is indeed stamped with author `c1-counter` and subject `fixture` (lines 119–121), so it is a visible metadata cue, but as an identical marker across cases it cannot alone distinguish positive/negative classes; I did not count it as a successful full-predicate exploit.

A second checker that classifies only by basename also passes while reading no variants. It can trivially be written to read the committed variant file by basename instead; the counter provides no evidence that source caused the verdict. Hence reading committed variant blobs is not required, though a malicious checker can also use repository-relative source paths. The counter does fetch and commit the selected variant (line 114), so the distinguishing source is present, but it does not bind the verdict to it.

Evidence limitation: these tests use current `HEAD` (`e4f207f544315612a6ea55b5b7a1cc2d2d4b4a79` printed by counter), which may be moving, rather than frozen build tip `e4891d8a4c9c70e97124980c2ec9aee5762a7f0a`. The exploit relies on counter construction and case names, both directly visible in the frozen source at the stated build revision only if confirmed there; this run is not a frozen-tip receipt and does not establish a canonical judge outcome.

## Smallest safe correction

Treat this strictly as a **LIMIT** under the frozen kill rule, not as a retroactive C1 predicate change. For a future counter, make fixture identity uninformative: use opaque/random directory names and vary commit identity/message independently of case; then constrain checker execution to a sanitized harness that supplies only the prescribed repo/tip and blocks environment/path-based access to case labels and outside files. Keep the committed battery blob as the semantic input and verify it is the exact evaluated program. A name randomization alone addresses this demonstrated exploit; ensuring the checker cannot consult external lane files is needed to address committed-variant/path gaming. Any revised counter needs its own frozen controls and counter-gaming checks.

## Check record

- `python3` inline harness invoking unchanged counter with author/message marker-only checker — exit 0 as harness, counter `met=False`, `noop_rejected=0/11`; attempted test, not a passing checker.
- `python3` inline harness invoking unchanged counter with fixture-basename-only checker — exit 0; counter `met=True`, `genuine=1/1 benign=3/3 noop_rejected=11/11 errors=0`.
- `python3` inline harness invoking unchanged counter with basename-only committed-variant-name checker — exit 0; counter `met=True`, same full score.
- `rm -rf "$S"` for the assigned scratch root after copying findings into this report — exit 0.
