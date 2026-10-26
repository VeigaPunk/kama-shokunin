# S9Log — round-48 LOG entry draft (lane kama, wave w1)

**Verdict: draft delivered** — the `## Round 48` entry is written at `.ufo/waves/round-48/w1/out/S9Log/log.md`, built only from frozen/preregistered bytes, round-47 closure D1–D9 and round-47 seat reports, with every build-time value re-measured on my own shared clone at `380bcdff9c8af06997c482f6eb03db926a794a2b` (C1 `met=True`, exit 0, 5.9 s; C2 `met=True`, `replayed=3/3`, exit 0, 14.2 s) and every not-yet-existing value left as an explicit `<PLACEHOLDER>`. One **new** integration defect found and patched: the lane's independent receipt validator refuses the round-48 v5 receipts (`tests/llamacpp-live/check-receipt.py`), verified patch at `out/S9Log/check-receipt-v5.diff`.

## 1. What the draft contains

Shape follows the round-47 entry at `LOG.md:2310` (three long claim/routing bullets, a freeze/build/wave bullet, an integration paragraph, and a `- Lesson:` trailer):

| Part | Content | Grounding |
|---|---|---|
| Heading | `## Round 48 — append-only audit v3 grades the declared carve-outs; live evidence a shortcut cannot replay (2026-10-26)` | SCORECARD `### Planned (round 48)` |
| C1 bullet | motivating evidence (D5 `corpus/lessons/round-47-verifier-spotcheck.md:101`; seats Rev1Restore `:3`, K1Design `:58`/`:59`, V1Ctr F1 `:20`, K1Fixture `:3`, X1Stable `:3`), the v3 tool + 9-row contract, the build's `regressed=1` banner finding and its byte-exact append, build measurements, the non-vacuous binding probe, preregistration limits + the sub-threshold consequence | my runs §2.1–2.5 |
| C2 bullet | motivating evidence (D1–D4, D6 `:97`–`:100`, `:102`; seats K2Cheat, K2Tamper, M2Ctr/M2Replay, K2Design F1/F2, K2Checks, X2Revision), the v5 live tool / replay / `--compare`, the three pinned receipts, build measurements, the `junk-c2-r47-relabel` bound, preregistration limits | my runs §2.6–2.8; committed receipts |
| Routed bullet | r47-D1…D4, D6 → C2; D5 → C1; D7 limit; D8 frontier; D9 report discipline; frontier items (proposal 3, b11906 ledger at b11909+); assimilation none; **the new validator finding with its verified fix** | closure §6; preregistration `routed` |
| Freeze/build/wave bullet | freeze `12284ba3` (counters' sha256 equal prereg; five control receipts all `met=False`; start census; pinned HF record; KQ64 check exit 0), build `380bcdff` (23 files, +4359/−79), wave `kama-r48-w1` (69 seats, role split) | controls, `census/start.out`, `freeze/prereg-time-check.out`, `w1/dispatch.json`, `w1/spec.json` |
| Integration paragraph | `<MEASURED_COMMIT>`, `<C1_AT_MEASURED>`, `<C2_AT_MEASURED>`, `<SOURCES_EDITS>`, `<CENSUS_END>`, `<KQ_NUMBERS>`, `<GATE_COUNTS>`, `<CAPABILITY_ROWS>`, `<PROVINCE_CELL>`, `<W1_RESULTS>`, `<REPORT_COMMIT>` | placeholders only — none of these exist at the build |
| Trailer | `- Lesson: corpus/lessons/round-48.md.` | lesson file exists untracked in the lane working tree |

Placeholders are deliberately upper-case and angle-bracketed so they cannot be mistaken for a measured value; the L1 fills them at integration and deletes any placeholder whose item did not land.

## 2. Evidence (read-only; my own `git clone --shared`)

```
S=/fast/scratch/hyaku/kama-r48/S9Log; export TMPDIR="$S"; mkdir -p "$S"
git clone --shared -q /home/vgpnk/Projects/shokunin/kama-shokunin "$S/lane"
git -C "$S/lane" rev-parse --show-toplevel   # → /fast/scratch/hyaku/kama-r48/S9Log/lane
```

### 2.1 C1 counter at the build (exit 0)

```
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round48-append-audit-v3-check.py \
  --repo $S/lane --tip 380bcdff9c8af06997c482f6eb03db926a794a2b --scratch $S/c1 --out $S/c1-build.out
```
```
selftest=1 contract=1 lane=1 fixture=1 stable=1 rows=9 files=89 lane_events=5 lane_failures=0 ungraded_lines=89 fixture_fail=0 met=True
tip=380bcdff9c8af06997c482f6eb03db926a794a2b
```
exit 0, 5.94 s → `out/S9Log/c1-build.out`.

### 2.2 The v3 tool's own JSON at the build (exit 0)

`git show 380bcdff:tools/append-only-audit.py` → `$S/aoa-v3.py` (sha256 `ec9c6d20…`, equal to the committed blob), `git show 380bcdff:registry/append-only-contract.tsv` → `$S/contract-v3.tsv` (sha256 `ca0618e5…`).

```
python3 aoa-v3.py --repo $S/lane --to 380bcdff… --contract contract-v3.tsv --json
```
| commit | file | deleted | graded | ungraded | restored_max | held_at_to | status |
|---|---|---|---|---|---|---|---|
| dd9f5dc6 | SCORECARD.md | 31 | 14 | 17 | 14 | 14 | restored |
| 0718b6ab | LOG.md | 2292 | 2292 | 0 | 2292 | 2292 | restored |
| 0718b6ab | SCORECARD.md | 2421 | 2349 | 72 | 2349 | 2349 | restored |
| 0718b6ab | corpus/QUALITY.md | 375 | 375 | 0 | 375 | 375 | restored |
| 0718b6ab | corpus/README.md | 663 | 663 | 0 | 663 | 663 | restored |

`summary`: `commits 311, files 89, events 5, restored 5, partial 0, unrestored 0, ungraded 0, ungraded_lines 89, regressed 0, vanished 0, unmatched 0, binary 0, bad_declarations 0`; all nine declarations `ok=True`.

### 2.3 The build's C1 finding reproduced (base `33e00582`, exit 1)

Same tool, same v3 contract, `--to 33e005827742b29772b153cda036ec9f27f653be`:
`summary … regressed 1`, with `0718b6ab` SCORECARD.md `restored_max 2349`, `held_at_to 2348` — the one graded missing line is the round-45 authority banner (`SCORECARD.md:6`, before any `## ` heading). exit 1 → `out/S9Log/c1-base-tip-contract.out`. This is the finding the build repaired by appending the r45/r46 banners under `### Superseded head banners (kept verbatim; round 48)` (`SCORECARD.md:2736-2742`).

### 2.4 The binding rule is not vacuous (exit 1)

The round-47 contract's declaring pointers, re-expressed in v3 form (5-cell header, `region=*`):
`LOG.md ok, SCORECARD.md ok, corpus/QUALITY.md **unbound**, corpus/README.md **unbound**, corpus/SOURCES.md ok, corpus/lessons/*.md ok, registry/history/DELTA.md ok` → `bad_declarations=2`, exit 1 (`out/S9Log/v2-pointers-under-v3.out`). Root cause is exactly V1Ctr F1: at `33e00582`, `corpus/QUALITY.md:24` reads "Same columns as the table above; appended so no existing line moves." (contains `append` only as a substring of "appended") and `corpus/README.md:86` reads "Appended rather than inserted, so no existing line moves (`QUALITY.md` KQ7)." — no "append-only". The build re-pointed those two rows to `corpus/README.md:761`, the paragraph that names the five append-only files.

### 2.5 Tool selftest

```
python3 tools/append-only-audit.py --selftest --scratch $S/st   # → AOA_SELFTEST pass=27 fail=0, exit 0
```

### 2.6 C2 counter at the build (exit 0)

```
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round48-live-replay-v5-audit.py \
  --repo $S/lane --tip 380bcdff… --scratch $S/c2 --out $S/c2-build.out
```
```
receipts=1 recordcheck=1 replay=1 compare=1 tamper=1 urlswap=1 newrow=1 replayed=3/3 met=True
tip=380bcdff9c8af06997c482f6eb03db926a794a2b started=2026-10-26T22:35:31.285967+00:00
```
exit 0, 14.25 s → `out/S9Log/c2-build.out`. The scratch tree it used was removed by the counter on exit (empty afterwards), so the receipt, not the scratch, is the evidence.

### 2.7 The three v5 receipts (committed bytes)

| receipt | schema | outcome | checks passed | verified.at | model.commit | teardown.log_path |
|---|---|---|---|---|---|---|
| receipt-1/2/3 | `kama-llamacpp-live/v5` | pass | 11/11 | record | 499bc882 | null |

`provenance.verified`: archive `bf94332a…695b`, member `35ac50fb…7d8d7ff0`, model `270cba1b…d256d`; `install.txt` records the same digests, the b11909 archive URL, the member path and the pinned model URL, and states no new install this round. `tools/kama-live-replay.py --selftest` → `KLR_SELFTEST pass=21 fail=0`.

### 2.8 Freeze and controls

`controls/base.c1.out` (`selftest=0 … fixture_fail=11`, exit 1), `base.c2.out` (`receipts=0 … replayed=0/3`, exit 1), `junk-c1-v2-relabel.c1.out` (`met=False`), `junk-c1-drop-scorecard.c1.out` (`rows=8 files=88 met=False`), `junk-c2-r47-relabel.c2.out` (`met=False`, with `replay N: … not under scratch`). Counter sha256 equal the preregistration: C1 `92b0f9f1…2ac7`, C2 `6bc16e25…c09`. `freeze/prereg-time-check.out` → `RESULT pass`, exit 0.

## 3. Findings

### F1 (medium, new — not in the task's known-integration list): the independent validator refuses the round-48 v5 receipts

- **File:line.** `tests/llamacpp-live/check-receipt.py` — constants `:51-54` (v1–v4 only), schema gate `:310-314`, required-check fallback `:1005` (`required = REQUIRED_CHECKS_V2 if is_v2 else REQUIRED_CHECKS_V1`).
- **Command that shows it** (at `380bcdff`, lane working tree is irrelevant — the file is unchanged since round 47):

  ```
  python3 tests/llamacpp-live/check-receipt.py .ufo/waves/round-48/c2/live/receipt-1.json
  ```
  → exit 1:
  ```
  INVALID .ufo/waves/round-48/c2/live/receipt-1.json: 4 problem(s)
    - schema is 'kama-llamacpp-live/v5', want '…/v1', '…/v2', '…/v3' or '…/v4'
    - required check 'teardown_exited' is absent
    - unexpected check id 'teardown_graceful' (the schema names exactly 10)
    - unexpected check id 'loading_envelope_graded' (the schema names exactly 10)
  ```
  The last three are collateral: with v5 unrecognised, `is_v2` is false and the v1 required set is applied. The v5 receipts' check ids are byte-identical to the v4 set (`health_ready … model_unchanged`, 11 ids), so nothing about the evidence is wrong — only the validator's schema list.
- **Proposed fix** (`out/S9Log/check-receipt-v5.diff`, 51 lines): one constant `RECEIPT_SCHEMA_V5`, v5 in the `is_v5`/`is_v4`/`is_v3`/`is_v2` memberships (so v5 gets the v4 provenance and `teardown.log_path` checks), the schema gate, and the `--require-schema` map (`v5: 5`). Verified on a scratch copy: `VALID` for receipts 1, 2 and 3 (exit 0) and `--selftest` still prints `14 VALID and 1 NOT-EVALUATED receipts accepted; 103 mutations + unreadable case rejected` (`out/S9Log/check-receipt-v5-patched.out`, `…-patched-selftest.out`); the diff carries repo-relative `a/`…`b/` headers and `git -C $S/lane apply --check out/S9Log/check-receipt-v5.diff` at `380bcdff` prints nothing and exits 0. A fuller fix would also validate `provenance.model.commit` (40-hex, present in the URL) and the `verified` digest equalities; the minimal patch deliberately adds acceptance only, so the existing mutation corpus keeps its meaning.
- **Note for the L1.** This is an integration edit, not a counter/claim change: the frozen counters and the preregistration are untouched by it, and the wave seats cannot fix it (the file is not in either claim's separability set).

### F2 (low, drafting note): build-time values are mine, not the build commit's receipts

The build carried no counter receipt under `.ufo/waves/round-48/measured/` (empty at my read) and no `c1-build.out`/`c2-build.out` beside the controls. The C1/C2 build values in the draft are therefore my runs, copied verbatim to `out/S9Log/c1-build.out` and `out/S9Log/c2-build.out`; the L1 can cite them as wave evidence or re-run at the measured commit and keep only the measured receipt.

### F3 (cosmetic observation): the replay selftest does not create its `--scratch` parent

```
python3 tools/kama-live-replay.py --selftest --scratch $S/st2   # st2 absent
FileNotFoundError: [Errno 2] No such file or directory: '…/st2/klr-st-2dhv0kw5'
```
With `mkdir -p $S/st2` first it prints `KLR_SELFTEST pass=21 fail=0`, exit 0. Not a claim defect (the counter always passes an existing scratch); worth a one-line `os.makedirs(..., exist_ok=True)` if a future seat trips on it.

### Not re-reported (already in the task's known-integration list)

`gate-registry-check` listing the two round-48 counters unregistered; the round-41/42/43 counters' spot-check count 33 vs 34; `hexrun-census`'s single unknown `d0012618`. I did not run those gates and add nothing to them.

## 4. Scope and limits

- **Not done, by design of this seat:** no measured-commit values, no integration edits, no commit, no push, no wave dispatch, no lane file edited. `.ufo/waves/round-48/measured/` was empty at my read; the measured commit does not exist yet.
- **Read-only lane.** I observed the lane working tree carrying the L1's in-progress integration (`git status --porcelain`: ` M SCORECARD.md`, ` M SKILL.md`, `?? corpus/lessons/round-48.md`, `?? .ufo/waves/round-48/w1.ready`, `?? .ufo/waves/round-48/w1.ready.dispatched`, `?? .ufo/waves/round-48/w1/out/`). The draft cites committed build bytes only (`git show 380bcdff:…`); it does not depend on the working tree.
- **Tooling:** no installs, no pacman, no uv, no npx, no network except the C2 counter's own github.com/huggingface.co downloads. Nothing was served or left running; the counter's llama-server instances were loopback and torn down by the tool, and its scratch tree was removed.
- **Scratch:** `S=/fast/scratch/hyaku/kama-r48/S9Log` removed after copying the receipts (`rm -rf "$S"`; the clone and the patched copy went with it). All cited evidence is committed bytes or a copy under `out/S9Log/`.

## 5. Paths written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/S9Log/log.md` — the proposed `## Round 48` LOG entry (placeholders `<MEASURED_COMMIT>`, `<C1_AT_MEASURED>`, `<C2_AT_MEASURED>`, `<SOURCES_EDITS>`, `<CENSUS_END>`, `<KQ_NUMBERS>`, `<GATE_COUNTS>`, `<CAPABILITY_ROWS>`, `<PROVINCE_CELL>`, `<W1_RESULTS>`, `<REPORT_COMMIT>`)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/S9Log/c1-build.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/S9Log/c1-base-tip-contract.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/S9Log/v2-pointers-under-v3.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/S9Log/c2-build.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/S9Log/c2-build.log`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/S9Log/check-receipt-v5.diff`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/S9Log/check-receipt-v5-orig.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/S9Log/check-receipt-v5-patched.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/S9Log/check-receipt-v5-patched-selftest.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/S9Log.md` — this report
