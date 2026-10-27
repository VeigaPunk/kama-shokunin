# X2Battery no-harm table — measure.sh instrument list at base vs build

- base = `57a2e25bf702b03aa61f9265e968cf68058ecb82` (round-50 closure)
- build = `138af25b963450b6520794995605fa7dbbcd87e0` (build b6bed925 + build-fix 73bf2a7a + build-fix 2 138af25b)
- Each instrument ran in a fresh `git clone --shared` checkout of the tip; receipts in `runs/` (one `<name>-<label>.out` per instrument, full output + `exit=`).
- The two round-51 counters don't exist in the base tree; there the frozen lane bytes were invoked with `--repo <clone>` (same invocation that produced `controls/base.c{1,2}.out`; sha256 = the preregistration pins at both tips).
- `census` reads the live lane tree (`--root /home/vgpnk/Projects/shokunin`), not the clone — it is tip-invariant and its two runs are byte-identical; see the report.

| instrument | base 57a2e25 line (exit) | build 138af25b line (exit) | verdict |
|---|---|---|---|
| c1 round51-replay-exe-audit | `bind=1 own=0 teardown=1 newrow=0 bound=3/3 owned=0/3 met=False` (1) | `bind=1 own=1 teardown=1 newrow=1 bound=3/3 owned=3/3 met=True` (0) | improved — the claim |
| c2 round51-append-audit-v6-check | `fixture=0 lane=0 scenarios=0/9 lost=0 disclosed=0 met=False` (1) | `fixture=1 lane=1 scenarios=9/9 lost=142 disclosed=166 met=True` (0) | improved — the claim |
| gate-registry-check | `registered 46 unregistered 0 defective 0` (0) | `registered 46 unregistered 2 defective 0` (1) | WORSE — expected integration item (2 counters not yet in SKILL registry) |
| capability-repertoire-audit | `listed 11 observed 11 missing 0 unsubstantiated 0 met True` (0) | `listed 11 observed 11 missing 0 unsubstantiated 0 met True` (0) | unchanged |
| r41-scorecard-reconcile | `axes=6 facts=36 hash_bad=0 lines_bad=0 run_bad=1 dead=0 score_bad=0 hollow=0 mismatches=1 met=False` (1) | identical (1) | unchanged — pre-existing `run_bad=1` (known item) |
| r42-selfdesc-reconcile | `r41=1 banner=0 planned=0 retired=0 saturation=0 caps=0 receipts=0 readme=0 province=0 rel=0 mismatches=1 maxN=50 met=False` (1) | identical (1) | unchanged — carries r41 |
| r43-registry-audit | `unreg=0 defect=0 flags=0 pins=0 selftest=0 dc=0 spot=1 hidden=0 pop=46 registered=46 mismatches=1 met=False` (1) | `unreg=2 defect=0 flags=0 pins=0 selftest=1 dc=0 spot=1 hidden=0 pop=48 registered=46 mismatches=4 met=False` (1) | WORSE — same expected-integration cause (see note) |
| planned-pointer-check | `met=True` (0) | `met=True` (0) | unchanged |
| digest-ledger scan | `tokens=132 blob=117 external_ok=8 external_absent=1 unverifiable=5 wrong_flagged=1 ledger_bad=0 wrong_unflagged=0 unknown=0` (0) | identical (0) | unchanged — and strictly better than the `*-build.out` measured receipt (unknown=166, exit 1 at 73bf2a7a) because build-fix 2 removed the disclosures ledger from its scope |
| hexrun-census scan | `tokens=1885 distinct=318 lane_oid=210 md5_blob=1 upstream_ok=94 unverifiable=9 wrong_flagged=2 ledger_bad=0 unknown=2` (1) | `tokens=2051 distinct=340 lane_oid=232 md5_blob=1 upstream_ok=94 unverifiable=9 wrong_flagged=2 ledger_bad=0 unknown=2` (1) | unchanged verdict — `unknown=2` carried from base (9e38a361, f8cdb853; known item); token drift is new build files |
| sources-append-only | `no append-only violations` (0) | `added S499 (allowed)` + `no append-only violations` (0) | unchanged/improved — S499 row is the allowed C1 newrow |
| append-only-audit (aoa) | `summary commits=337 files=96 events=5 restored=5 … ungraded_lines=89 …` (0) | `summary commits=341 files=96 events=106 restored=19 disclosed=51 permitted_lines=58 disclosed_lines=166 … bad_disclosures=0 regressed=0` (0) | improved — v6 graded 101 events v5 could not see, exit 0 at both |
| aoa-selftest | `AOA_SELFTEST pass=36 fail=0` (0) | `AOA_SELFTEST pass=47 fail=0` (0) | improved — 11 new selftest cases |
| klr-selftest | `KLR_SELFTEST pass=23 fail=0` (0) | `KLR_SELFTEST pass=26 fail=0` (0) | improved — 3 new selftest cases (server-exe checks) |
| live-selftest | `selftest: ok` (0) | `selftest: ok` (0) | unchanged |
| cr-selftest | `selftest: 16 VALID and 1 NOT-EVALUATED receipts accepted; 107 mutations + unreadable case rejected` (0) | identical (0) | unchanged |
| shortcut-tally | `rounds=40-47 rows=8` (0) | identical (0) | unchanged |
| r48c2 live-replay-v5-audit | `receipts=1 recordcheck=1 replay=1 compare=1 tamper=1 urlswap=1 newrow=1 replayed=3/3 met=True` (0) | identical (0) | unchanged — the replay change is replay-visible-compatible to the v5 counter |
| r49c1 replay-witness-audit | `witness=1 cap=1 newrow=1 witnessed=3/3 met=True` (0) | identical (0) | unchanged |
| r49c2 append-audit-v4-check | `fixture=1 lane=0 scenarios=8/8 met=False` (1) | `fixture=1 lane=0 scenarios=8/8 met=False` (1) | same verdict — already failing at base; lane-leg detail grew under the v6 tool (supersession family, see note) |
| r50c1 replay-bind-audit | `bind=1 teardown=1 newrow=1 bound=3/3 met=True` (0) | identical (0) | unchanged — all round-50 legs preserved inside C1 |
| r50c2 append-audit-v5-check | `fixture=1 lane=1 scenarios=12/12 met=True` (0) | `fixture=1 lane=0 scenarios=12/12 met=False` (1) | WORSE — expected supersession: the v6 tool supersedes v5 definitions (known item: lane=0) |
| census sources-census.sh validate | `E=0 W=95` — `kama ok …/corpus/SOURCES.md` (0) | byte-identical (0) | unchanged — TIP-INVARIANT: reads the live lane, not the clone; the measured-receipt `E11 S499` has since resolved on the live tree (corpus/lessons/round-51.md exists at integration) |

## Instruments worse at the build

| instrument | what changed | classification |
|---|---|---|
| gate | `unregistered 0 → 2`, exit 0 → 1 | **Expected** — SKILL registry lacks the two round-51 counters; known integration item ("gate unregistered 2"), resolved when the registry rows land |
| r43 | `unreg 0→2`, `selftest 0→1`, `pop 46→48`, `mismatches 1→4` | **Expected** — same unregistration: r43's selftest leg runs gate's `--selftest` on the audited tree, whose "lane-tip" arm fails while the two counters are unregistered (`detail: selftest: documented 'GATE_SELFTEST pass=6 fail=0', run printed 'GATE_SELFTEST pass=5 fail=1' exit 1`). `pop=48` is the two new tools. `spot=1` carried from base. |
| r50c2 | `lane 1→0`, `met True→False`, exit 0→1 | **Expected supersession** — the counter runs the tip's append-only-audit, which is v6; v5's lane leg no longer matches the v6 report shape (`fixture=1` still holds; known item "round-50 C2 counter now lane=0") |

## Not newly worse, worth noting

- **r49c2**: `met=False` at base already (`event 0718b6abbda6 SCORECARD.md ungraded 72 > natively exempt 65`). At the build the lane leg sees the v6 tool (`events 5 → 106`, `ungraded_lines 89 → 205`) and reports more detail lines — same supersession family as r50c2, not a new harm.
- **digest**: identical to base and *better* than the receipt at 73bf2a7a (unknown=166→0) — build-fix 2 is a measured improvement inside this wave.
- **hexrun**: `wrong_flagged=2` / `unknown=2` identical at both tips (carried base state).
- **census**: cannot separate tips by construction (live-tree read); both lines are `E=0 W=95`, exit 0.

No instrument regressed for a reason other than (a) the two counters' pending registry integration, or (b) the intentional v6 supersession of the older append-only counters. No new harms found.
