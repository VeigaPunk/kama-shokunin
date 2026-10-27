# J5NoLedger — round 51, lane kama, ablation control C2 (no disclosure ledger)

**Verdict: the control passes as specified.** At build-fix 2 (138af25b) with `registry/append-only-disclosures.tsv` deleted, the frozen C2 counter returns `fixture=1 lane=0 scenarios=9/9 lost=142 disclosed=0 met=False`, exit 1; the same tree without the deletion returns `fixture=1 lane=1 ... disclosed=166 met=True`, exit 0. The claim's mechanism (the ledger) is therefore load-bearing, and the counter's own bytes are the frozen ones (`sha256 254e63ba…9a1660` = preregistration `claims[C2].counter_sha256`). No defect in the frozen counter, the tool, or the ledger was found; the observed kill decomposition is exactly the preregistered limit, measured.

## Setup and integrity

- Scratch: `/fast/scratch/hyaku/kama-r51/J5NoLedger` (`TMPDIR` set there; removed at the end).
- Clone: `git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin $S/lane`; `git -C $S/lane rev-parse --show-toplevel` → `/fast/scratch/hyaku/kama-r51/J5NoLedger/lane` (asserted before every commit). Lane HEAD at clone time `4eca4892` (wave a2w1 spec); `138af25b` confirmed an ancestor (`git merge-base --is-ancestor` exit 0).
- Counter bytes: `sha256sum tools/round51-append-audit-v6-check.py` → `254e63bab046428d4099d008929751701ed7b0600b96874760838a56eb9a1660`, identical to `preregistration.json` `C2.counter_sha256`; run by absolute path, never edited.
- Frozen ledger at 138af25b: `git show 138af25b:registry/append-only-disclosures.tsv | sha256sum` → `17d2b067ad7272976bda88fac9d8cbc0b77d2d93d2f2a376b3b0a5171d2803bb`; 166 data rows over 51 distinct `(commit, file)` events.

## The ablation (primary)

```
git -C $S/lane checkout -q -B ablation 138af25b963450b6520794995605fa7dbbcd87e0
git -C $S/lane rm -q registry/append-only-disclosures.tsv
git -C $S/lane -c user.name=r51-j5-fixture -c user.email=r51-j5@invalid -c commit.gpgsign=false \
    commit -q -m "r51 ablation J5NoLedger: delete registry/append-only-disclosures.tsv at build-fix 2 (control: no ledger)"
# -> 7b3bea81e6e1cf988439e901a986295fc16271bd  (1 file changed, 167 deletions; fixture only, lane untouched)
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round51-append-audit-v6-check.py \
    --repo $S/lane --tip 7b3bea81e6e1cf988439e901a986295fc16271bd --scratch $S/c2 --out <out>/c2-noledger.out
# exit 1
```

Receipt (`c2-noledger.out`, verbatim head):

```
tip=7b3bea81e6e1cf988439e901a986295fc16271bd
fixture=1 lane=0 scenarios=9/9 lost=142 disclosed=0 met=False
detail: lane: tool definition v6 threshold 1 exit 1 {'unrestored': 47, 'partial': 4, 'regressed': 0, 'bad_disclosures': 0, 'bad_declarations': 0}
detail: lane: <42 × "own lost N ledger 0 (N keys differ)">   # 42 distinct (commit,file), Σ=142
detail: lane: tool v6 threshold 1 exit 1 events 106 disclosed_lines 0 permitted_lines 58; own lost lines in whole-file-graded files 142; ledger lines 0
```

Both lane legs fire independently: the tool leg (`got != want`, `tools/round51-append-audit-v6-check.py:267-273`) because the tip's tool exits 1 with 47 unrestored + 4 partial events, and the counter's own recomputation (`:361-365`) for 42 events / 142 lines. `scenarios=9/9` shows the fixture leg is unaffected by the ablation, so the loss of `met` is attributable to the lane leg alone.

## Paired arm (same tip bytes, ledger present)

```
python3 …/round51-append-audit-v6-check.py --repo $S/lane --tip 138af25b963450b6520794995605fa7dbbcd87e0 --scratch $S/c2 --out <out>/c2-paired.out
# exit 0
fixture=1 lane=1 scenarios=9/9 lost=142 disclosed=166 met=True
detail: lane: tool v6 threshold 1 exit 0 events 106 disclosed_lines 166 permitted_lines 58; own lost lines in whole-file-graded files 142; ledger lines 166
```

Only one file differs between the two runs. `lost` is 142 in both (the counter's own recomputation is ledger-independent), `disclosed` 166→0, tool exit 0→1. This reproduces the build receipt (`measured/c2-build.out`, `lost=142 disclosed=166 met=True` at 73bf2a7a) at the later build-fix tip and isolates the ledger as the graded mechanism.

## Where the kill comes from (supplementary measurement)

The ledger's 166 lines split by contract region: 142 lines in 42 whole-file-graded events (`*`) and 24 lines in 9 `SCORECARD.md` events (region `exempt=…`). The counter recomputes lost lines key-for-key only for `*` files (`:350-365`); for region-restricted files it only bounds ledger rows against deleted keys (`:366-375`) — the preregistered limit #4.

A second fixture commit on 138af25b with only the 24 `SCORECARD.md` rows removed (`24a12f3b`, 24 deletions, patch in the out dir) gives:

```
fixture=1 lane=0 scenarios=9/9 lost=142 disclosed=142 met=False   # exit 1
detail: lane: tool definition v6 threshold 1 exit 1 {'unrestored': 7, 'partial': 2, …}
detail: lane: tool v6 … ledger lines 142
```

i.e. with the ledger present but 24 lines short, the counter's own comparison is silent (142 = 142) and the kill rests solely on the tool leg (7 unrestored + 2 partial = 9 SCORECARD events). So the counter is sound but the 24/166 = 14.5% of disclosed lines on region-restricted files are outside its key-for-key check — a documented limit, not a defect; the control still returns met=False either way.

## Not mine / carried

- `pgrep -af llama-server` shows two processes under `/fast/scratch/hyaku/kama-r51/X1Fresh/work5/` (seats' C1 replay). I started no server; nothing of mine is left running.
- Both fixture commits live only in my shared clone (deleted with scratch); the lane, fleet repo and `shokuknow` were never written. No pacman or tool install was needed (python3 + git already present; nothing upgraded).

## Retained evidence

- `c2-noledger.out` — primary ablation receipt (exit 1, `met=False`).
- `c2-paired.out` — unmodified arm at 138af25b (exit 0, `met=True`).
- `c2-supp-scorecard-rows-removed.out` — supplementary partial-ledger ablation (exit 1).
- `ablation-7b3bea81.patch`, `ablation-7b3bea81.commit.txt`, `supp-scorecard-rows-removed-24a12f3b.patch` — the two fixture diffs and the primary commit object.
