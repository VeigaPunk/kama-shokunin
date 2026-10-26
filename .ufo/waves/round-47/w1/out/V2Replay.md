# V2Replay — code review of `tools/kama-live-replay.py` (round 47, lane kama)

**Verdict: the replay tool is correct against its docstring and the C2 counter's replay contract on every verdict path I probed; two findings worth hardening — the live tool's non-zero exit is masked whenever a matching rerun receipt is written (replay `:157–165`), and the selftest never runs the real live tool (selftest `:174–242`) — both currently unreachable with the shipped live tool and compensated by the C2 counter's own replay leg.**

Reviewed object: `tools/kama-live-replay.py` at lane head `46a924e0` (build `3a09a1d9`), against:
- its docstring (`:2–21`) and exit contract (`:18–19`),
- `tools/round47-live-replay-audit.py` (C2) replay/tamper legs (`:184–319`),
- `tools/kama-llamacpp-live.py` (live tool) exit/outcome invariant (`:943–955`, `:1817`),
- the three committed b11909 receipts (schema v4, outcome pass, 11/11 evaluated-passes each; `provenance.server.member = llama-b11909/llama-server` verified for all three).

Method: offline fixture probes against the lane tool via `subprocess` (argv as the C2 counter invokes it), plus the tool's own selftest and the live tool's selftest. No lane file was modified; no subagents used.

---

## 1. Findings

### M1 — Live-tool exit code is masked when a matching rerun receipt exists (medium, defense-in-depth)
- Where: `tools/kama-live-replay.py:158–165` — `res["live_exit"] = p.returncode` is recorded but never used in the verdict; if `rerun` exists, `compare()` decides alone.
- Probe F2 (`probes-driver1.txt`): fake live tool exits **2** yet writes a matching pass receipt → replay exits **0**, `match=true`, `live_exit=2`. J evidence: `F2-J.json` (`{..., "live_exit": 2, "match": true, "mismatches": [], ...}`).
- Impact: unreachable with the shipped live tool — its exit code derives from the same receipt state (`kama-llamacpp-live.py:943–955 _outcome_exit`, `:1817 return exit_code if emitted else 2`), so exit 2 always pairs with outcome `setup-error`/`not-evaluated`, which `compare()` flags (probe F3 → exit 1). But any `--live` tool that exits non-zero while writing a pass-shaped receipt substitutes as "match".
- Proposed fix (unified diff):
```diff
--- a/tools/kama-live-replay.py
+++ b/tools/kama-live-replay.py
@@ -158,8 +158,10 @@ def replay(receipt_path, work, live=DEFAULT_LIVE, timeout=600):
         p = subprocess.run(argv, capture_output=True, text=True, env=env, timeout=timeout)
         res["live_exit"] = p.returncode
         if not os.path.isfile(rerun):
             raise Refused(f"no-rerun-receipt:exit={p.returncode}:{p.stderr[-300:]}")
         res["rerun_receipt"] = rerun
         with open(rerun) as fh:
             res["mismatches"] = compare(rec, json.load(fh))
+        if p.returncode != 0:
+            # the live tool's exit and receipt outcome are coupled; an exit 2
+            # alongside a pass receipt means the receipt is not trustworthy
+            res["mismatches"].append(f"live-exit:{p.returncode}")
         res["match"] = not res["mismatches"]
         return res, (0 if res["match"] else 1)
```

### M2 — Selftest never runs the real live tool or a real download (medium, coverage)
- Where: `tools/kama-live-replay.py:174–242` — all 10 cases call `run(..., live=fake_live)` (default `:219`) against a hand-written fake that always writes the same receipt (`:194–198`); URLs are `file://` only (`:205–207`). No case exercises `kama-llamacpp-live.py` (real server, real lifecycle, real network), and no case covers: timeout/hung live tool, missing rerun receipt, live exit≠0 with receipt (M1), or the `compare()` branches (schema/sha256/missing-check/extra-check).
- The real end-to-end path is exercised only by the C2 counter's replay leg (`round47-live-replay-audit.py:184–292`) against receipt-1 and the real b11909 assets; the L1 pre-wave dry run at `3a09a1d9` recorded `replay=1 rerun_checks=11` (assessment brief; not re-run here — see §4).
- Proposed fix (minimal, offline): add to `_selftest` an assertion that `DEFAULT_LIVE` exists and that `[sys.executable, DEFAULT_LIVE, "--selftest"]` exits 0, so the shipped pair stays coherent; full lifecycle coverage remains the counter's job.

### L1 — Vacuous match when the original receipt has zero evaluated checks (low)
- Where: `tools/kama-live-replay.py:118–124` — `evaluated(orig)` empty ⇒ loop never runs ⇒ `mismatches=[]` ⇒ match, regardless of the rerun.
- Probe F10 (`probes-driver1.txt`): orig `checks: []` → exit 0, `match=true`.
- Impact: real receipts are `>=10` evaluated, all passed (C2 leg `:147–149`), so not exploitable in-lane; the guard costs one line.
- Proposed fix: in `compare()`, `if not eo: return ["no-evaluated-checks-in-original"]` (or refuse in `replay()`).

### L2 — `.part` temp file leaks on aborted downloads (low, cosmetic)
- Where: `tools/kama-live-replay.py:57–65` (`fetch` writes `dest + ".part"`, replaces on success), `:89–95` (`acquire` unlinks `dest` on digest mismatch only).
- A `URLError`/timeout mid-copy leaves `dest + ".part"` under `work/download`; digest mismatch cleans `dest` but there is no `.part` then (the replace already happened). Harmless (work dir is scratch-owned), untidy.

## 2. Question-by-question evidence

| Question | Answer | Evidence |
|---|---|---|
| Exit codes | 0 match / 1 ran-and-differs / 2 refused or could-not-run — matches docstring `:18–19` and C2 `:36–39` | F1=0, F3/G1–G5=1, F4/F5/F12/F13=2 |
| Refusal reasons | `not-a-v4-receipt`, `provenance-missing:...`, `provenance-bad-digest:...`, `provenance-model-digest-differs-from-receipt-model`, `unsafe-member:...`, `url-scheme:...`, `digest-mismatch:<base>:want=...:got=...`, `member-absent:...`, `no-rerun-receipt:exit=...:...`, `receipt-not-an-object`, `could-not-run:<Exc>:...` — all reachable and surfaced in J.`refused` | F5, F12, F13; selftest cases (`selftest-replay.txt`) |
| compare() rules | schema must be v4; outcome equal; server.sha256 and model.sha256 equal; every evaluated check of the original re-evaluated with equal passed; **extra** evaluated checks in the rerun are ignored | G1–G7, F9 |
| Timeout (hung live tool) | `subprocess.run(..., timeout=)` → `TimeoutExpired` → refused `could-not-run:TimeoutExpired:...`, exit 2, J still written; the child is killed (no leftover process; `pgrep -af fake_live.py` empty after F4) | F4, `F4-timeout-J.json` |
| Timeout (hung **server**) | handled upstream: live tool `readiness_loop` ready-timeout 60 s (`kama-llamacpp-live.py:1535–1548`) → `SetupError` → receipt outcome `setup-error` → replay exits 1 with outcome/check mismatches (semantics: ran and differs, not refusal) | F3 pattern |
| Live tool exits 2 with partial receipt | exit 1, `mismatches` lists outcome + sha + not-evaluated checks; the receipt (not the exit code) drives the verdict | F3 |
| Exit codes | 0 match / 1 ran-and-differs / 2 refused or could-not-run — matches docstring `:18–19` and C2 `:36–39` | F1/F2/F8/F10/G6/G7=0, F3/F6/F9/F11/G1–G5=1, F4/F5/F7/F12/F13=2 |

## 3. Verified-positive checklist
- Digest verification happens before extraction and before the live tool runs: F12 (asset digest tampered) and F13 (model provenance digest tampered) show `live_tool_invoked=False` and no rerun receipt; the C2 tamper leg (`:294–319`) is satisfied by the same refusal paths.
- Post-extract member containment: `realpath` prefix check plus `isfile` (`:146`) — defense in depth over `tarfile` `filter="data"` (`:98–100`).
- J is written on every path, including refusals and timeouts (`main` `:259–262`); J carries `schema`, `receipt`, `work`, `rerun_receipt`, `match`, `refused`, `mismatches`, `inputs`, `live_exit`.
- Argv handed to the live tool matches the receipt's alias/ctx/threads and the provenance fields (`:152–156`); env adds a TMPDIR under `work` (`:150–151`).
- C2 interop: J schema `kama-live-replay/v1`, `rerun_receipt` path, `match` bool all match what `round47-live-replay-audit.py:264–292` reads; freshness (`started_utc`) and inputs-under-scratch are (correctly, per contract) counter-level checks, not replay checks — the `junk-c2-r46-relabel` control (`controls/junk-c2-r46-relabel.c2.out`) shows the counter catching a receipt-copying replay.

## 4. Verification notes / gaps
- I did **not** re-run the full C2 counter (downloads ~25 MB and re-runs the real lifecycle); I rely on the recorded L1 pre-wave dry run at `3a09a1d9` (`replay=1 rerun_checks=11`, `newrow=0` ⇒ met=False) plus my offline probes. If a fresh full C2 run is wanted, `python3 tools/round47-live-replay-audit.py --repo <clone> --tip <full> --scratch <dir>` at integration will exercise the real path.
- `tools/kama-llamacpp-live.py --selftest` passes (exit 0) — the tool replay drives is healthy offline.
- No tools were installed (stdlib only; nothing recorded under the tooling directive).

## 5. Files written
- Report: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/V2Replay.md`
- Out dir `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/V2Replay/`: `probes-driver1.txt`, `probes-driver2.txt`, `selftest-replay.txt`, `selftest-live.txt`, `F2-J.json`, `F2-rerun-receipt.json`, `F4-timeout-J.json`, `G1-J.json`, `receipt-1.json`, `receipt-2.json`, `receipt-3.json` (cited copies), `findings.json`.
