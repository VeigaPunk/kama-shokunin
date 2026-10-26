# R2Rerun — round 48, lane kama — independent re-measurement of C2

**Verdict: C2 independently reproduced — counter bytes match the frozen sha256, `met=True` with all seven legs 1 and `replayed=3/3` at tip 380bcdff9c8af06997c482f6eb03db926a794a2b on two fresh runs (exit 0 both), and `met=False` with all legs 0 (exit 1) at base 33e005827742b29772b153cda036ec9f27f653be, matching the frozen before-state; no new defect found.**

Axes (godspeed): reproducibility (same result on independent reruns), provenance (frozen counter bytes + frozen digests), base-contrast (counter discriminates base from tip), evidence-completeness (every output and receipt line reported). No tool installs were needed (python3 and git as present on the host; nothing added to PATH).

## 1. Provenance of the counter bytes

- Fresh full clone per item: `git clone /home/vgpnk/Projects/shokunin/kama-shokunin $S/lane` → clone HEAD `b85783e889c261ff870da65d091ff1014ffe7c10` (lane has moved past the build; the counter takes `--tip` explicitly). `git status --porcelain | wc -l` = 0 (clean); both target commits present as `commit` objects.
- `sha256sum lane/tools/round48-live-replay-v5-audit.py` → `6bc16e2532469f160cee59c78103688b8d16a9713fdb4d3c255f894975fb0c09` = frozen `counter_sha256` for C2 in `.ufo/waves/round-48/preregistration.json` → `C2-COUNTER-MATCH`.
- `sha256sum lane/tools/round48-append-audit-v3-check.py` → `92b0f9f1027b8214c7a702d928f89e5a6d9fb814fc565c234f6deee3f2d82ac7` = frozen C1 `counter_sha256` → `C1-COUNTER-MATCH` (checked for completeness; not my lane leg).
- `git log --oneline -1` at tip → `380bcdff round-48: build - append-only-audit v3 + v3 contract with bound regions (C1), superseded r45/r46 SCORECARD banners appended (v3 regressed finding); live tool v5 record-time provenance, replay v5 + stable projection + --compare, three v5 b11909 receipts, S492-S493 (C2); freeze-time receipt`; at base → `33e00582 round-47 verifier spot-check (integrator, hyaku): non-author admit/reject`.

## 2. The three runs (exact commands, every output line)

All runs: `TMPDIR=$S`, cwd `$S`, counter invoked from my own clone, `--repo $S/lane`, counter is read-only on the repo and removes its scratch on exit (docstring, tools/round48-live-replay-v5-audit.py:128-131), so each run re-acquired the ~70 MB archive and ~4 MB model over the network independently.

Run 1 (tip 380bcdff…, `--out …/out/R2Rerun/c2-build.out`), wall 12.9 s, exit 0:
```
receipts=1 recordcheck=1 replay=1 compare=1 tamper=1 urlswap=1 newrow=1 replayed=3/3 met=True
tip=380bcdff9c8af06997c482f6eb03db926a794a2b started=2026-10-26T22:35:45.519029+00:00
```

Run 2 (same command, same `--out`), wall 13.2 s, exit 0:
```
receipts=1 recordcheck=1 replay=1 compare=1 tamper=1 urlswap=1 newrow=1 replayed=3/3 met=True
tip=380bcdff9c8af06997c482f6eb03db926a794a2b started=2026-10-26T22:36:47.618407+00:00
```
`diff run1.log run2.log` → only line 2 (`started=` timestamp) differs; the leg line is byte-identical.

Base run (tip 33e0058…), wall 3.6 s, exit 1:
```
receipts=0 recordcheck=0 replay=0 compare=0 tamper=0 urlswap=0 newrow=0 replayed=0/3 met=False
tip=33e005827742b29772b153cda036ec9f27f653be started=2026-10-26T22:37:07.172422+00:00
detail: receipts: .ufo/waves/round-48/c2/live/receipt-1.json absent or not a JSON object at tip
detail: receipts: .ufo/waves/round-48/c2/live/receipt-2.json absent or not a JSON object at tip
detail: receipts: .ufo/waves/round-48/c2/live/receipt-3.json absent or not a JSON object at tip
detail: recordcheck partial-flags: exit 2 executed=True outcome=setup-error  |
detail: recordcheck all-right-control: exit 2 executed=False outcome=None  | -asset-sha256 SERVER_ASSET_SHA256] … [--model-url MODEL_URL] [--selftest] kama-llamacpp-live.py: error: unrec[ognized argument --server-archive]
detail: newrow: no registry row contains https://huggingface.co/ggml-org/models-moved/resolve/499bc8821c6b12b4e53c5bffcb21ec206f212d81/tinyllamas/stories260K.gguf
```
This equals the frozen before-state in preregistration.json (`receipts=0 recordcheck=0 replay=0 compare=0 tamper=0 urlswap=0 newrow=0 met=False`, controls/base.c2.out) and the detail lines are the expected base facts: no v5 receipts at base, the base v4 live tool rejects `--server-archive` (unrecognized argument), no pinned-URL source row. The counter discriminates base from tip on every leg.

Evidence-preservation note: the item's command reuses one `--out` path, so each run overwrote the previous out-receipt. Preserved copies: run 2 → `c2-build-run2.out`, base → `c2-base.out`, and the final `c2-build.out` (base's). Run 1's out-receipt was overwritten before I could copy it; its stdout is preserved verbatim in `run1.log` and its leg line is byte-identical to run 2's (diff above). All three out-receipts are the same summary text as stdout (180 B tip, 987 B base).

## 3. Receipt lines at the tip (extracted from `git show 380bcdff:.ufo/waves/round-48/c2/live/receipt-N.json`)

All three receipts: `schema=kama-llamacpp-live/v5`, `outcome=pass`, 11 checks entries / 11 `passed=True` (≥ 10 required), `started_utc` 2026-10-26T22:26:23.509Z / .935Z / 24.331Z, `ended_utc` 22:26:23.879Z / 24.273Z / 24.676Z, `build_info=b11909-caa8191df` (frozen release commit caa8191df159f764…), `teardown.log_path=None`.

Per receipt, identical provenance (each line verified against the frozen values in the counter docstring lines 15-26 and preregistration.json):
- `server.sha256=35ac50fb2cfd9c4f363720bb88ac17e799716595802c9105103593977d8d7ff0`
- `model.sha256=270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d` (= frozen model digest)
- `provenance.server.asset_url=https://github.com/ggml-org/llama.cpp/releases/download/b11909/llama-b11909-bin-ubuntu-x64.tar.gz` (frozen asset URL)
- `provenance.server.asset_sha256=bf94332a3001f3ee0b032cda37259f68460e28732ef9a579bfb1b918197e695b` (= frozen asset digest)
- `provenance.server.member=llama-b11909/llama-server`
- `provenance.model.url=https://huggingface.co/ggml-org/models-moved/resolve/499bc8821c6b12b4e53c5bffcb21ec206f212d81/tinyllamas/stories260K.gguf` (pinned `/resolve/<40-hex>/`)
- `provenance.model.commit=499bc8821c6b12b4e53c5bffcb21ec206f212d81`
- `provenance.verified={"at":"record","archive_sha256":"bf94332a…","member_sha256":"35ac50fb…","model_sha256":"270cba1b…"}` — archive_sha256 = frozen asset digest, member_sha256 = server.sha256, model_sha256 = frozen model digest, exactly the v5 contract.

## 4. Independent spot-checks of counter legs

- newrow: `git show 380bcdff:corpus/SOURCES.md | grep -n 499bc882…` → line 245: row `| S492 | … https://huggingface.co/ggml-org/models-moved/resolve/499bc8821c6b12b4e53c5bffcb21ec206f212d81/tinyllamas/stories260K.gguf | dataset | A | …` — the pinned URL in full in a registry row (S039 line 51 names the commit, S490 line 243 the moving `main` URL, as the counter's newrow leg states).
- Receipts leg: the three receipts at tip carry the frozen digests and `at=record` verified block (section 3), outcome pass, 11/11 checks.
- The replay, compare, tamper, urlswap, recordcheck legs were exercised inside the counter on both tip runs (all 1, replayed=3/3, exit 0, twice) with scratch removed between runs, so the re-acquisition was fresh each time; I did not re-implement them outside the counter.

## 5. Findings

- No new defect. The counter reproduced the target state twice at the tip and the frozen before-state at the base, with correct exit codes (0 met / 1 not met) and no lane mutation (`git status --porcelain` = 0 after all runs).
- Known integration items (gate-registry-check unregistered round-48 counters; round-41/42/43 spot-check count 33 vs 34; hexrun-census d0012618) not re-reported, per the brief.
- Residual risk (documented, not new): the receipts leg is structural — a fabricated receipt with self-consistent digests passes it (preregistration limits; control junk-c2-r47-relabel) — so the replay and urlswap legs carry the evidence; both passed here. The counter's recordcheck leg uses a stub archive/server, so it shows refusal-before-execution, not archive genuineness; the receipts' verified block and the replay leg cover that. My re-measurement inherits these documented limits.

## 6. Cleanup

Scratch `/fast/scratch/hyaku/kama-r48/R2Rerun` removed (`SCRATCH_REMOVED`; `ls` confirms gone). Lane untouched (read-only clone deleted with it). No tools installed; no pacman use.

## Files written (all under /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/R2Rerun/)

- `R2Rerun.md` (this report; also at `.ufo/waves/round-48/w1/out/R2Rerun.md`)
- `c2-build.out` (counter out-receipt, last writer = base run), `c2-build-run2.out` (run 2), `c2-base.out` (base)
- `run1.log`, `run2.log`, `runbase.log` (verbatim stdout of each run)
- `receipt-1.json`, `receipt-2.json`, `receipt-3.json` (tip copies of the three committed receipts)
