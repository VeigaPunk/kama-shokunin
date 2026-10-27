# N2Couple2 — round-50 separability at the build

VERDICT: SEPARABLE — each counter meets on the freeze tree (601c8889) plus only its own build files. C1: `bind=1 teardown=1 newrow=1 bound=3/3 met=True` exit 0 (14.7 s). C2: `fixture=1 lane=1 scenarios=12/12 met=True` exit 0 (4.5 s). No coupling defect found.

## Fixtures

One `git clone --shared` of the lane in scratch; two commits parented on freeze 601c8889f33d1797c712feb753974c20cf891264 (full construction record and diffs in `N2Couple2/fixtures.txt`; blob identity with 97c864be verified via `git rev-parse`):

- C1 tip `e19de92e6bce9733edb3f0cd1255c11e37d3ec82`: + `tools/kama-live-replay.py`, + `tools/kama-llamacpp-live.py` from 97c864be, + corpus/SOURCES.md with the S496 and S497 rows spliced verbatim (S498 deliberately excluded — it is the C2 build's row).
- C2 tip `66205824583917c053d7c8305228a52b33071ce4`: + `tools/append-only-audit.py` from 97c864be only (no SOURCES change).

## Commands and results

```
python3 tools/round50-replay-bind-audit.py   --repo $S/lane --tip e19de92e…  --scratch $S/c1s
  → exit 0: bind=1 teardown=1 newrow=1 bound=3/3 met=True
     bind b1/b2/b3: exe+listen+tree+env+mapped ok, child_pid joined, model_mapping dev/inode recorded
     teardown: invoker SIGKILLed, 3 descendants gone in 0.10 s, port refuses
     newrow: 2 rows new since base; 1 names proc_pid_maps(5): S496
python3 tools/round50-append-audit-v5-check.py --repo $S/lane --tip 66205824… --scratch $S/c2s
  → exit 0: fixture=1 lane=1 scenarios=12/12 met=True
     all 12 scenarios ok incl. order-a/order-b, fence, crlf-launder
     lane: tool exit 0, events 5, bad_declarations 0, ungraded_lines 89,
           event dd9f5dc6c0e6 ungraded 17 <= v5 natively exempt 23
```

Both match the L1 full-build dry-run outputs exactly (same event lines, same counts), so neither counter reads anything the other's build files provide.

## Path inventory read by each counter (from the counter sources)

**C1 — tools/round50-replay-bind-audit.py** (sha256 ff6ac2ac… matches preregistration):
- from `--repo`: `git rev-parse --verify <tip>`; `git archive --format=tar <tip>` (whole tree extracted under --scratch, but only these tree paths consumed); `git show <tip>:corpus/SOURCES.md` and `git show 26ecba64…:corpus/SOURCES.md` (hardcoded BASE, tools/round50-replay-bind-audit.py:107,530-537).
- consumed tree paths: `tools/kama-live-replay.py` (executed; line 109,402), the three receipts `.ufo/waves/round-48/c2/live/receipt-{1,2,3}.json` (line 108,581-585), and `tools/kama-llamacpp-live.py` transitively — the replay resolves it as `<tree>/tools/kama-llamacpp-live.py` (kama-live-replay.py:83 `DEFAULT_LIVE`).
- host/network: HF model URL (frozen sha 270cba1b…), GitHub llama.cpp b11909 archive via the receipts, `/proc` (net/tcp{,6}, <pid>/{exe,fd,stat,environ,maps}), loopback HTTP, planted sitecustomize + KAMA_R50_CANARY under --scratch only.

**C2 — tools/round50-append-audit-v5-check.py** (sha256 925f07a4… matches preregistration):
- from `--repo`: `git archive <tip>` → only `tools/append-only-audit.py` executed (lines 100,521-526); `git show <tip>:registry/append-only-contract.tsv` (line 401); `git show <tip>:<declaring path>` per contract row (line 405); `git rev-list --parents <tip>` + `cat-file --batch-check`/`blob` over every blob of every contract path reachable from tip (lines 417-434); `git diff`/`--numstat`/`show` per reported event (lines 366-385,472,486).
- the audited tool itself reads the contract at `<to>:registry/append-only-contract.tsv` when `--contract` is absent (append-only-audit.py:116,455-456) and the fixture contract text the counter writes under --scratch. 12 fixture repos are built fresh under --scratch (lines 148-184). No SOURCES.md read anywhere.

## Findings

1. **The two claims are independently landable, exactly as preregistration's separability paragraph predicts** (`.ufo/waves/round-50/preregistration.json:9`). C1's build files carry bind+teardown+newrow alone; C2's single file carries fixture+lane alone.
2. **Asymmetric sourcing enforcement (observation, within the declared contract):** C1's counter has a `newrow` leg and requires a proc_pid_maps(5) SOURCES row — met by S496 in my fixture. The same leg does *not* look for PR_SET_PDEATHSIG(2const): my fixture included S497, but a tip carrying only S496 would still satisfy `newrow` — the pdeathsig mechanism is enforced behaviorally (teardown leg), not by row. C2's counter has no row leg at all: it met with S498 absent entirely. The S498 row is asserted by the claim text and the SOURCES registry, not enforced by this counter — same class of counter/claim gap the preregistration limits already name for C1's canary and C2's binder.
3. **Receipt reuse:** C1 replays the committed round-48 v5 receipts from the tip tree — they are freeze-tree files, so no C2 content participates; and C1's counter never opens the contract, while C2's never touches `/proc` or the network. The two claim surfaces share exactly one file class (`corpus/SOURCES.md`), and only C1 reads it.

## Notes

- Counter sha256s verified against `.ufo/waves/round-50/preregistration.json` before any run.
- No tool installs (pacman paused; stdlib+git sufficed). The single llama-server pid observed during the run belonged to sibling seat Rev1Base's counter (cmdline `/fast/scratch/hyaku/kama-r50/Rev1Base/…`); all processes from my runs reaped — `pgrep -f llama-server` shows none under `N2Couple2/`.
- `git archive` extracts the whole tip tree per counter; "paths read" above means paths whose *content* is consumed — the archive read is whole-tree but read-only.

## Files written

- `.ufo/waves/round-50/w1/out/N2Couple2.md` (this report)
- `.ufo/waves/round-50/w1/out/N2Couple2/c1-separable.out` (counter receipt)
- `.ufo/waves/round-50/w1/out/N2Couple2/c2-separable.out` (counter receipt)
- `.ufo/waves/round-50/w1/out/N2Couple2/fixtures.txt` (fixture construction + verification)
