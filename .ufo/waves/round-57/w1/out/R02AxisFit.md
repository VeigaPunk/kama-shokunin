# R02AxisFit — axis attribution, claim separability, frozen predicates, before controls (distinct case 10)

Independent review, no edits. Every command read-only; receipts in `receipts/` beside this file, produced in scratch `/fast/scratch/hyaku/kama-r57/R02AxisFit/` (cleaned after copy). No git/jj mutation; HEAD and index untouched.

## Verdict summary

| Check | Result |
|---|---|
| Axis attribution (lane) | **VALID** — operability + calibration everywhere live; MISSION.md:29 conflict left unresolved as instructed |
| Per-claim axis mapping | **VALID** — stale count → calibration; no-op binding → operability, identical in freeze.txt, amendment, and landed §Round 57 |
| Claim separability | **VALID** — distinct instruments, predicates, baselines; one labeling hazard (below) |
| Frozen predicates and before controls | **VALID** — both freeze commits present and committed pre-landing; frozen base receipt re-derives byte-exactly at the pinned tip; round-56 false-green baseline receipt exists and matches the amendment |
| Wave context claim text | **INVALID** — stale C1/C2 ordering and a bogus "expected 46" (details below); amendment is authoritative |

## 1. Axis attribution

Live authority: `shokunin.conf` LANES row `kama|kama-shokunin|operability + calibration (local model serving and endpoint health)`; SCORECARD head banner (round 57): "the assigned axes are operability + calibration"; `w1-spec.json`/`swarm-registry.json` `axes: ["calibration","operability"]` for every seat; counter `tools/round42-selfdesc-reconcile.py` hard-codes `ASSIGNED = ("operability", "calibration")`. Conflict on record, not resolved here: `MISSION.md:29` still reads `kama: { axes: "operability + freshness (local model serving/endpoints)" }` — the historical example the lane has carried as an open L0 question since round 35. The dispatch instruction ("axes … per lane SCORECARD/shokunin.conf; MISSION.md historical example conflicts; don't resolve") is consistent with the live assignment. No invalidity.

## 2. Claim separability

Amended freeze (`controls/freeze-amendment.txt`, committed as `7c873d7b`, present and reachable from HEAD; explicitly "supersedes the earlier round-57 freeze's claim ordering only"):

- **C1 — operability** — `tools/round56-prereg-check.py` no-op defect: checker declares `met=True` for a battery carrying the matching roster literal while executing no entries. Predicate: repaired checker rejects a matching-roster no-op while the genuine roster stays accepted. Baseline: `.ufo/waves/round-56/measured/c2-noop-control.out` — verified on disk: `present=1 roster_match=1 kills=1 controls=2 met=True` / `exit=0` (the false green).
- **C2 — calibration** — `tools/round42-selfdesc-reconcile.py` stale count: stated verifier-spotcheck count 42, actual committed count 43. Predicate: count-only self-description update, then `mismatches=0`.

Distinct instruments, distinct axes, distinct predicates, distinct baselines, independently runnable (`round56-prereg-check.py` vs `round42-selfdesc-reconcile.py`); the amendment closes with "C1 and C2 are distinct axes, each measured independently." Separable. **Hazard:** the wave's `taskCall.context` (w1-dispatch.json / w1-spec.json) and `freeze.txt` still carry the pre-amendment numbering (C1 calibration stale count / C2 operability no-op). Only the labels swapped — the axis mapping is the same in all three sources — but any seat quoting the context's "C1/C2" without the amendment mislabels its claim. The landed §Round 57 table uses the amended numbering; the amendment wins.

## 3. Frozen predicates and before controls — replayed

- **Base receipt re-derives byte-exactly.** `python3 tools/round42-selfdesc-reconcile.py --repo <lane> --tip b89bdab2cc114735ec5d331c6c610134258f7864` → `tip=b89bdab…`, `r41=1 … mismatches=1 maxN=56 met=False`, detail `… no stdout line == '42' (exit 0)`, exit 1 — identical to `controls/base-c1.out` (its extra tail line `base_c1_exit=1` is the receipt wrapper's). `base-c2-frozen.out` is the same counter output frozen for the second claim; both claims' before-state is therefore the same real red, not a fixture.
- **No-op vacuity replays.** `c1-noop.py` (scratch copy, sha256 `1910e45e…` identical to the frozen fixture) prints `mismatches=0 maxN=46 met=True`, exit 0 — matching `noop-c1.out`; `noop-c2.out` records the same literal with `canonical_table_reads=0 self_description_reads=0`. The printed `maxN=46` is the round-46 historical counter line (SCORECARD.md:2676, commit `4340cf2f`), i.e. a stale-but-authentic literal — which is precisely the vacuity being demonstrated.
- **Freeze ordering holds observably.** Base `b89bdab…` (14:42:40) is an ancestor of HEAD; freeze commits `89dc4f52` (pre-data freeze) and `7c873d7b` (ordering correction) both exist, `7c873d7b` reachable from HEAD; control-file mtimes 15:03–15:06 precede the first landing commit 15:12:08. At the base commit: zero `## Round 57` headings and head reads "Latest measured round: 56" — so the frozen before-state predates any round-57 result recording.
- **Instrument delta matches the amendment.** `git diff --stat b89bdab… HEAD -- tools/` shows exactly one changed file: `tools/round56-prereg-check.py` (12 insertions, 1 deletion — the C1 repair). `round42-selfdesc-reconcile.py` is untouched, matching "update only the stale self-description count".

## 4. Invalidities found

1. **Wave context numbers are wrong (severity: medium — misdescribes C2's target).** The dispatch context says "counter currently reports maxN=56 instead of expected 46". Nothing expects 46: `maxN` is derived (greatest `^## Round (\d+)` heading in SCORECARD.md) and equals 56 at the frozen tip, where "Latest measured round: 56" is correct; the actual frozen defect is the r41 calibration literal 42 vs. actual 43 (verified: `ls corpus/lessons/*verifier-spotcheck.md | wc -l` → 43). The only `maxN=46` strings in the tree are the round-46 historical note and the wave's own no-op fixture literals. The amendment's statement (42 → 43, `mismatches=0` after count-only update) is the valid target and is what the landed §Round 57 table records. Related context phrases ("stale canonical capability row count", "stale maxN derivation" in seat prompts) misname the defect: the canonical list selection and its count are consistent; only the stated spotcheck count is stale.
2. **Stale claim numbering in the frozen context (severity: low — labeling hazard, already superseded).** freeze.txt + context say C1=calibration/C2=operability; the committed amendment and §Round 57 reverse the labels while keeping each claim's axis. Seats must cite claims per the amendment.
3. **Tooling note (not a repo defect):** my first `glob` of `.ufo/waves/round-57` listed `controls/census/` with `start.exit`/`start.out`; the directory does not exist (read and `ls` both fail). Reported via `xd://report_issue`.

## 5. Residual risk and verification gaps

- I verified the before-state and freeze chain, not the after-state: `.ufo/waves/round-57/measured/{noop-c1,c1-committed-tip,c2-committed-tip}.out` were landing mid-wave (untracked siblings' receipts; HEAD advanced at 15:14/15:15 while I worked). Whether the repaired `round56-prereg-check.py` truly rejects the no-op while accepting the genuine roster is the executor/attacker seats' claim to demonstrate; I make no verdict on it.
- "Committed before seat findings" is evidenced by commit timestamps/reachability and control mtimes, not by cryptographic pre-registration; a determined actor rewriting history is out of scope for a leaf reviewer.
- Mixed object-id formats observed (HEAD line 40-hex `16efcf5e…`, frozen tip 64-hex `b89bdab…` — both resolve in this repo); no consequence observed, noting for anyone scripting rev-parse comparisons.

**No shared file was edited; no score, target, or predicate changed.** Report: `.ufo/waves/round-57/w1/out/R02AxisFit.md`; receipts: `.ufo/waves/round-57/w1/out/R02AxisFit/receipts/{replay-base-c1.out,replay-base-c1.exit,replay-c1-noop.out,replay-c1-noop.exit,commands.txt}`.
