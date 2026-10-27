# J7Thresh20 — round 51, lane kama, C2 (calibration) ablation: CLI default threshold back to 20

**Verdict: the mutant is caught, three ways over — frozen C2 counter on the ablated tip prints
`fixture=0 lane=0 scenarios=1/9 lost=0 disclosed=166 met=False`, exit 1 (control at the same tree
prints `fixture=1 lane=1 scenarios=9/9 lost=142 disclosed=166 met=True`, exit 0). No defect found in
the frozen counter, the frozen tool, the preregistration or the ledger.** Two calibration
observations (the in-tree selftest is blind to this exact line; the counter's `lost` aggregate is
threshold-coupled) are recorded below as advisory, not as predicate defects.

## 1. Mutant identity

| item | value |
|---|---|
| lane base of the mutant | `138af25b963450b6520794995605fa7dbbcd87e0` (build-fix 2) |
| clone | `git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin $S/lane`, `rev-parse --show-toplevel` = `$S/lane` (checked before the commit) |
| change | `tools/append-only-audit.py:1417` `ap.add_argument("--threshold", type=int, default=1)` → `default=20` (one line, nothing else) |
| file sha256 | pristine `3d0eaa168c26f006da656e635995f14d43c57c3a9af43ddf1b954f5ca3070c11` → mutated `c819756d5b9bcd4b0d57191f2b5188383829ba36ee38eaf1d05ad437b98e2b18` |
| commit | `29d78d1317b8e013ee7aa83e2b17b12d9ab16b20`, fixture identity `fx <fx@invalid>` (`-c user.name=fx -c user.email=fx@invalid -c commit.gpgsign=false`), detached on top of `138af25b`, `git -C $S/lane status --porcelain` empty afterwards |
| frozen counter | `tools/round51-append-audit-v6-check.py`, sha256 `254e63bab046428d4099d008929751701ed7b0600b96874760838a56eb9a1660` — equals `preregistration.json` `counter_sha256` for C2, run unmodified from the lane checkout |

Diff (`ablation.patch` in the out dir):

```diff
@@ -1416,3 +1416,3 @@ def main(argv=None):
     ap.add_argument("--to", default="HEAD")
-    ap.add_argument("--threshold", type=int, default=1)
+    ap.add_argument("--threshold", type=int, default=20)
```

The tool's docstring (line 8, "threshold default 1 (v1-v5: 20)") and its emitted JSON `definition`
(still `v6`) are deliberately left alone: the ablation is the single CLI default, so anything the
counter reports is attributable to that line.

## 2. Commands and results

All commands from `/home/vgpnk/Projects/shokunin` (fleet root), `S=/fast/scratch/hyaku/kama-r51/J7Thresh20`, `TMPDIR=$S`.

**(a) The measured mutant**

```
$ python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round51-append-audit-v6-check.py \
    --repo $S/lane --tip 29d78d1317b8e013ee7aa83e2b17b12d9ab16b20 --scratch $S \
    --out .ufo/waves/round-51/a2w1/out/J7Thresh20/c2-ablated-threshold20.out      # real 4.1 s
tip=29d78d1317b8e013ee7aa83e2b17b12d9ab16b20
fixture=0 lane=0 scenarios=1/9 lost=0 disclosed=166 met=False
EXIT=1
```

Exactly the expected two legs: **fixture=0 via the default threshold, lane=0 via threshold != 1**
(plus the semantic failure below). The 12 fixture cases (`c2-ablated-threshold20.out`):

```
fixture default-threshold: exit 0 (want 1) FAIL events=[]
fixture arow-mutable:      exit 0 (want 0) FAIL events=[]
fixture arow-immutable:    exit 0 (want 1) FAIL events=[]
fixture code-span-pipe:    exit 0 (want 1) FAIL events=[]
fixture row-dropped:       exit 0 (want 1) FAIL events=[]
fixture disclosed:         exit 1 (want 0) FAIL events=[]
fixture bad-disclosure-1..4: exit 1 (want 1) ok  events=[]
fixture partial-disclosure: exit 1 (want 1) FAIL events=[]
fixture two-files-one-commit: exit 1 (want 1) FAIL events=[]
```

Every 1–6-line deletion now yields no event at all (`events=[]`), so 8 of the 12 constructed
verdicts invert; `scenarios=1/9` (the four bad-disclosure sub-cases are the only ones left standing,
and see observation O2 — they stand for the wrong reason).

Lane leg, first detail line and the shape of the rest:

```
detail: lane: tool definition v6 threshold 20 exit 1 {'unrestored': 0, 'partial': 0, 'regressed': 0,
        'bad_disclosures': 166, 'bad_declarations': 0}
detail: lane: c6199a254244 corpus/README.md: own deleted 5 numstat 5 tool no event
... 101 such lines ...
detail: lane: tool v6 threshold 20 exit 1 events 5 disclosed_lines 0 permitted_lines 0;
        own lost lines in whole-file-graded files 0; ledger lines 166
```

So the lane leg fails on **three independent grounds**, not just the threshold pin: `threshold != 1`
(counter line 269), `exit 1` from the tool, and `bad_disclosures 166` — every ledger row now names a
line whose event no longer exists (`bad_disclosures` = count of bad disclosure rows,
`tools/append-only-audit.py:722`). The 101 `tool no event` lines are the round-50 defect reproduced
exactly: **101 of 106 events hidden** (the preregistration's "hid 101 of 106").

**(b) Control at the unablated tree, same clone, same counter**

```
$ python3 .../round51-append-audit-v6-check.py --repo $S/lane \
    --tip 138af25b963450b6520794995605fa7dbbcd87e0 --scratch $S \
    --out .ufo/waves/round-51/a2w1/out/J7Thresh20/c2-control-pristine-138af25b.out
tip=138af25b963450b6520794995605fa7dbbcd87e0
fixture=1 lane=1 scenarios=9/9 lost=142 disclosed=166 met=True
EXIT=0
```

Identical to the build receipt `measured/c2-build.out` (taken at `73bf2a7a`: `fixture=1 lane=1
scenarios=9/9 lost=142 disclosed=166 met=True`), so the one-line default is the only difference in
tree and the only cause of the flip. Base control `controls/base.c2.out` remains
`fixture=0 lane=0 scenarios=0/9 ... met=False` (unchanged, copied into the out dir).

**(c) Isolation: the default is the only variable**

Run the mutated tree's own CLI at the mutant tip (`tool-default20.json`, `tool-explicit1.json`):

| invocation | exit | threshold | events | disclosed_lines | permitted_lines | bad_disclosures |
|---|---|---|---|---|---|---|
| no `--threshold` (the ablation) | 1 | 20 | 5 | 0 | 0 | 166 |
| `--threshold 1` (explicit) | 0 | 1 | 106 | 166 | 58 | 0 |

The five survivors under threshold 20 are the mass-restore commits
(`dd9f5dc6c0e6 SCORECARD.md`, `0718b6abbda6 LOG.md/SCORECARD.md/corpus/QUALITY.md/corpus/README.md`,
all `restored`). The 101 hidden events carry **all 166 disclosed lines** and 208 graded lines — the
disclosure ledger becomes 100 % orphaned. With `--threshold 1` the mutated tree reproduces the build
metric exactly (106 events / 166 disclosed / 58 permitted / exit 0), proving the mutant's blast
radius is that one default and nothing else.

**(d) The tool's own selftest is blind to this line**

```
$ (cd $S/lane && python3 tools/append-only-audit.py --selftest --scratch $S/selftest)
AOA_SELFTEST pass=47 fail=0        EXIT=0
```

`v6-default-threshold` (`tools/append-only-audit.py:1273-1281`) calls the library function
`full(f.d, t, files=F)` — the library default is `def audit(..., threshold=1)` at
`tools/append-only-audit.py:544` — so it never touches the argparse default at line 1417. The
`--help` text also prints no default value, so the CLI self-description cannot reveal the change.
**Only the frozen counter's CLI-level fixture `default-threshold` (counter lines 226-227, executed as a CLI by `run_tool`, counter line 162) pins this line**, and it fails loudly. This is a point in favour of the
out-of-tree counter, not a defect in the lane.

## 3. Calibration reading (why this strengthens C2 rather than weakening it)

* The C2 predicate is sensitive to exactly the reversible step a hostile or careless author would
  take to escape it, and it is sensitive at the interface the counter itself fixes: the tool's
  *CLI default*, not the library function. An ablation that only changed `def audit(..., threshold=20)`
  would be caught too, but by the fixture verdicts (`arow-*` would emit no events → exit 0 where 1
  is wanted) — here both survive: 8/9 scenarios invert.
* `lost=0` under the mutant versus `lost=142` pristine is not evidence of no loss: the counter's
  loss recomputation is entered only for events the tool emitted (counter line 317-318, `continue`),
  so a tool that emits fewer events shrinks the counter's own loss total. Under this mutant the kill
  is carried by the threshold/exit/summary checks, not by `lost`. See O1.
* No change to C1 was made or needed; the counter hash matches the preregistration and its base
  control is untouched.

## 4. Advisory observations (not defects; counters are frozen, nothing edited)

**O1 — `lost` is threshold-coupled.** `tools/round51-append-audit-v6-check.py:317-319` `continue`s on
a missing tool event, so the "own lost lines in whole-file-graded files" figure only counts events the
tool chose to emit. Evidence: the mutant prints `lost=0` while `--threshold 1` on the same tree shows
101 hidden events holding 208 graded lines. The met-predicate is still sound (threshold pin line 269,
exit and summary 267-269), but the `lost=` summary field should be read as "losses among emitted
events". If a later round wants `lost` to be threshold-independent, the `continue` at 318 would need
a distinguish-and-count branch — a change for a new frozen counter, not for this one.

**O2 — the bad-disclosure scenario passes vacuously under the ablation.** Counter lines 244-245 assert
only `summary.bad_disclosures == 1` plus exit 1. With no events at all, every disclosure row becomes a
"no event" bad row (166 of them, `tools/append-only-audit.py:722`), so the four constructed
wrong-row cases still "ok" — which is why the mutant scores `scenarios=1/9` and not `0/9` (base
control scores `0/9` because it has no ledger file at all). Tightening would mean also asserting the
event exists and the failure *reason* (e.g. `ev(r,t,"LOG.md")` present and `status != "disclosed"`);
again, a change for a successor counter.

No finding against the lane: the mutant tree's only divergence is the injected line, and the frozen
counter, the preregistration and `registry/append-only-disclosures.tsv` are exactly as at
`138af25b` (166 rows, all classes checked by the control run).

## 5. Limits

* One lane revision (`138af25b`) and one commit-hash counter; the ablated commit lives only in the
  shared clone, deleted with the scratch dir — the patch is retained (section 1, `ablation.patch`)
  and re-applies cleanly to `138af25b:tools/append-only-audit.py`.
* Only the mock/fixture leg and the read-only lane leg of C2 were exercised; C1 (replay/own-server)
  is another seat's ticket and was neither run nor touched. No llama-server was started by this
  seat (`pgrep -af llama-server` showed only `K1Cheat3`'s own replay process, untouched).
* No pacman/uv/npx installs were made; no tools added or upgraded.

## 6. Retained evidence (all under `.ufo/waves/round-51/a2w1/out/J7Thresh20/`)

| file | content |
|---|---|
| `c2-ablated-threshold20.out` | counter receipt at the mutant tip, `fixture=0 lane=0 scenarios=1/9 lost=0 disclosed=166 met=False`, exit 1 |
| `c2-control-pristine-138af25b.out` / `.stdout` | counter receipt at the unablated `138af25b`, `fixture=1 lane=1 scenarios=9/9 lost=142 ... met=True`, exit 0 |
| `ablation.patch` | the one-line diff |
| `ablation-commit.txt` | mutant commit id, identity, subject |
| `tool-default20.json` / `tool-explicit1.json` | mutated CLI, default vs `--threshold 1` (5 vs 106 events; 166 bad disclosures vs 0) |
| `tool-selftest-ablated.out` | mutated tree's selftest, `pass=47 fail=0`, exit 0 (the blind spot) |
| `c2-build-receipt.copy.out` | copy of `measured/c2-build.out` (`73bf2a7a`, met=True) for comparison |
| `base.c2.control.copy.out` | copy of `controls/base.c2.out` (`fixture=0 lane=0 scenarios=0/9`) |
