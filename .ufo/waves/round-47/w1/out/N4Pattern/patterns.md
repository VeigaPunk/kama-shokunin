# N4Pattern — cross-claim pattern: instruments that still rest on host paths, decoded text, or a shared tool/counter definition

Verdict: the round-47 C1/C2 pattern (evidence checkable from outside the instrument: C1 vs git numstat + a constructed fixture; C2 vs fresh re-acquisition from recorded URLs/digests) is applied to the two claims, but **eight lane instruments and two receipt families still carry the three failure modes the pattern was built to remove** — one of them fails today on this host with the default binary.

Audited at lane tip `46a924e0` (round-47 wave spec commit; build `3a09a1d9`), read-only, against `kama-shokunin/tools/` (57 files), `SKILL.md` §§Round-4x registries + Local gate/probe registry, `.ufo/waves/round-47/` (preregistration, controls, receipts) and `.ufo/waves/round-46/c1/live/` receipts. Every line cited was read at that commit; every command below was executed by this seat unless the source is named.

---

## 1. Host paths (absolute, host-shaped, or per-user layout)

| ID | File:line | Constant / use | What a fresh session does |
|----|-----------|----------------|---------------------------|
| H1 | `tools/echo-recheck.py:69-71` | `LANE = Path("/home/vgpnk/Projects/shokunin/kama-shokunin")`; `DEFAULT_RECEIPT = LANE / ".ufo/waves/round-27/w1a3/out/ExecLiveEchoProbe/receipt.json"` | The tool is anchored to this host even when the lane is cloned elsewhere; the default receipt points at a round-27 seat out-dir (exists in the tree today, but depends on that historical wave layout). |
| H2 | `tools/kama-context-capacity.py:58-61` | `DEFAULT_SERVER = Path.home() / '.local/bin/llama-server'`; `DEFAULT_MODEL = Path.home() / '.cache/kama-shokunin/models/stories260K.gguf'`; `DEFAULT_SCRATCH = Path('/fast/scratch/hyaku/kama-context-capacity')` | Defaults assume the operator's home layout and a shared `/fast/scratch/hyaku` tree. The scratch default is a single path shared by all sessions (collision/race risk), and `/fast/scratch/...` does not exist on any other machine (here it is absent but the tool `mkdir`s it, line 767). |
| H3 | `tools/prereg-time-check.py:45` | `DEFAULT_SCRATCH = "/fast/scratch/hyaku/kama-r26/ExecPreregTimeCheck"` | Hardcoded round-26 seat scratch name; stale host path. |
| H4 | `tools/round35-statement-audit.py:31`; `tools/round36-statement-audit.py:28`; `tools/round37-statement-audit.py:32-33`; `tools/round38-statement-audit.py:38-39` | `FLEET = Path("/home/vgpnk/Projects/shokunin")`; `SHOKUKNOW`/`STAGED = Path("/home/vgpnk/Projects/shokuknow/merge/kama/SOURCES.append.md")` | Four statement counters read the fleet repo and an external `shokuknow` merge file at hardcoded absolute paths; there is no `--fleet`/`--staged` argument, so any other machine or fresh clone fails deterministically (the shokuknow file exists here, `ls -ld` → 196639 bytes, 2026-10-24). |
| H5 | `tools/round42-capacity-audit.py:76`; `tools/round43-health-audit.py:88` | `CENSUS = "/home/vgpnk/Projects/shokunin/scripts/sources-census.sh"` | Both counters invoke a fleet script by absolute path (exists here; `ls -ld` → -rwxr-xr-x). If the fleet root moves, the census leg cannot run; the counters take `--repo` but no `--fleet`. |
| H6 | `tools/sources-append-only.py:599` | `--repo default="/home/vgpnk/Projects/shokunin/kama-shokunin"` | The documented invocation without `--repo` silently targets this host's lane. |
| H7 | `.ufo/waves/round-46/c1/live/receipt-{1,2,3}.json:548`; `.ufo/waves/round-46/w1/out/X1Replica/receipt-{1,2}.json:548` (and `.../round-46/c1/live/fixture-live/receipt-{1,2,3}.json:548`) | `teardown.log_path: "/fast/scratch/hyaku/kama-r46/X1Live/kama-llamacpp-live-*.log"` | Dead pointers — the operator scratch directive deletes these before any reader arrives (round-46 lesson row `dead-pointer`). The receipt inlines a 3-line tail, so the loss is bounded, but the recorded path never resolves. This is the exact defect the round-47 C2 claim fixes (`teardown.log_path: null` in `.ufo/waves/round-47/c2/live/receipt-1.json:559`). |
| H8 | `.ufo/waves/round-47/c2/live/receipt-1.json` (and -2, -3): lines 4, 6, 264-265, 404, 473, 569, 282, 309 | `argv[0]`, `model.path`, `server.realpath`, `tool.path`, `probe.path`, `registry` all record `/home/vgpnk/...` | Host-bound residue only: replay is driven by the `provenance` URLs/digests (receipt-1.json:391-401), so these do not block a fresh session, but a reader can no longer trust any embedded path as a locator. |

## 2. Decoded text (human/porcelain output parsed as truth)

| ID | File:line | What is decoded | Risk |
|----|-----------|-----------------|------|
| D1 | `tools/kama-context-capacity.py:63` and `:746-754` | `--version` stdout substring match `SERVER_VERSION_MARK = 'build 11755'`; mismatch raises `SetupError('server-version-mismatch:…')` | **Fails today.** Verified: `readlink -f /home/vgpnk/.local/bin/llama-server` → `/home/vgpnk/.local/opt/llama-b11755/llama-server`; `sha256sum` → `b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804` (echo-recheck's pinned server); running `…/llama-b11755/llama-server --version` prints `version: 0.7.0-dev (build 11909, commit caa8191df)` (rc=0). The mark `'build 11755'` is absent, so the tool exits `server-version-mismatch` against its own default server. A fresh session using the documented default runs straight into this. |
| D2 | `tools/echo-recheck.py:241-248` | `ss -ltnp` human lines matched with `re.compile(r":%d\b" % port)`; `ss` missing → `CannotEvaluate` | Depends on `ss` text shape/permissions; a `ss` format change silently finds no listener. |
| D3 | `tools/kama-probe.sh` (`load_listeners` ~238-284; `body_is_llamacpp_loading` ~422-449) | `ss -ltn` lines; and the exact llama.cpp loading envelope (documented against upstream `b11755 tools/server/server-http.cpp:307-328`) | Upstream text/body changes silently re-classify verdicts. |
| D4 | `tools/round43-registry-audit.py:124-131` | Runs the gate blob and `re.search(r"registered (\d+) unregistered (\d+) defective (\d+)", p.stdout)` | If the gate ever rewords its summary, the counter breaks; it also makes the counter depend on the gate's stdout format (see S3). |
| D5 | `tools/report-landing-audit.py:350-376` | `git log -z --format=%H%x00%an%x00%at%x00%s` split into fields; subjects matched against `^(?:round-{rnd}:|checkpoint\(r{rnd}\))`; malformed records → `EvalError` | Commit-subject convention is decoded as ground truth; a subject-format drift silently zeroes a round's landing detection. |

## 3. Shared definition between tool and counter (round-46 blind-spot class)

| ID | Pair | Sharing | Consequence |
|----|------|---------|-------------|
| S1 | `tools/round42-selfdesc-reconcile.py:130-134` (imports `tools/round41-scorecard-reconcile.py` via `importlib`; docstring line 22: “imported unchanged”) | Counter imports sibling counter source | Any defect in the r41 head-table counter is inherited verbatim; the r42 counter has no independent recomputation for those fields. The registry row itself documents this (`SKILL.md:1404`: “the imported round-41 counter's helpers”). |
| S2 | `tools/kama-context-capacity.py:602-635` (loads `.ufo/waves/round-25/count-c2.py` `CELLS` via `importlib`) and `:187-191` (`load_live_module` loads `tools/kama-llamacpp-live.py`) | Tool loads the counter's and sibling tool's source at runtime | The tool's drift gate trusts the exact definition it should challenge; if `count-c2.py`'s `CELLS` is wrong, the tool “agrees” with it. |
| S3 | `tools/round43-registry-audit.py:116-131` (writes the gate blob from the tip and runs it; uses its printed `registered/unregistered/defective` counts as ground truth) | Counter uses the instrument under audit as its own oracle | Circular: the counter can never detect a defect the gate shares; it only detects formatting drift (D4). |
| S4 | `tools/round46-release-recheck-audit.py:109-112` vs `tools/release-recheck.py:38,61-63`; verdict rule text-equality (round46 docstring lines 46-49) | Copy-pasted `ROW`/`URL` regexes; same `holds` = text-equal-ranges rule | The round-46 lesson (“K1Cheat greened all 91 rows with a relocation script”) is exactly this pattern; the sufficiency family is carried open this round (preregistration `routed.r46-D3`). |
| S5 | `tests/llamacpp-live/check-receipt.py:47-49,86-112` vs `tools/kama-llamacpp-live.py` (schema v4) | Independent validator re-implements the receipt schema knowledge (v1-v3) and pins upstream source spans at `LLAMA_COMMIT = "704366d76f8748cf9ad3df62a464bfcc8d1ae6ad"` | The copies drifted: measured INVALID on v4 receipts — `python3 tests/llamacpp-live/check-receipt.py .ufo/waves/round-47/c2/live/receipt-1.json` → exit 1, `schema is 'kama-llamacpp-live/v4', want …v1/v2/v3` (seat K0Harm command 11 report). The outside verifier can no longer verify the lane's live receipts. |
| S6 | `tools/round46-append-audit-check.py` (v1 counter) with `tools/append-only-audit.py` v1 | v1 counter shared the `---`-line filter rule (round-46 closure D1: “the counter that shares its rule”) | Historical instance of the pattern; fixed this round by v2's numstat cross-check. Note the v2 design still shares the v2 definition between tool and counter by contract — the preregistration discloses this and pins *outside* ground truth (git numstat; fixture construction) instead (preregistration `limits` line: “The counter's recomputation and the tool share the v2 definition by contract; ground truth independent of both is git numstat … and the fixture's construction”). |

## 4. Ranked: what a fresh session fails on first

1. **D1 (kama-context-capacity server-version mark)** — fails now on this host with the default server (verified `--version` output `build 11909` vs mark `'build 11755'`). Immediate, deterministic, with the documented defaults.
2. **S5 (check-receipt.py vs v4)** — already INVALID on the round-47 receipts today; the lane's only independent receipt validator is out of sync with the producer (verified via K0Harm's measured command 11).
3. **H4/H5 (statement counters and census counters with absolute fleet/shokuknow paths)** — deterministic failure as soon as the lane runs off this host; on-host they silently depend on sibling trees that are not passed as arguments.
4. **H7 (round-46 receipts' dead `teardown.log_path`)** — a reader following the receipts hits deleted scratch; bounded by inlined tails, but the pointer is dead (fixed for round-47 C2 receipts, not retroactively for the round-46 family).
5. **S1/S2/S3 (import/execute of the sibling definition)** — no crash, but silent under-verification: defects in the shared source are invisible to the counter that is supposed to grade it.
6. **S4 (release-recheck text-equality sufficiency)** — the K1Cheat relocation vector stays open; carried as frontier (`r46-D3`), not closed.
7. **H2/H3 (per-user + shared `/fast/scratch` defaults)** — host-shaped; collision-prone on-host, broken off-host.
8. **D4/D5 (gate summary regex; git-log subject decode)** — medium: break only when upstream text/conventions change.

## 5. Proposed moves (edges only; none applied to the lane)

- **D1**: make `SERVER_VERSION_MARK` derive from the resolved server's own `--version` parse (regex over `build (\d+)`) or drop the mark check in favor of the already-recorded `server_version` + sha256 (lines 739-754) — or pin the mark to the current artifact and document it like echo-recheck's PINS.
- **S5**: make `check-receipt.py` read the schema/check contract from a single committed source (e.g., a `registry/receipt-schema-v4.json` or the producer's committed docstring) instead of a re-implemented copy; or bump its v1-v3 tables to v4.
- **H4/H5**: replace constants with `--fleet`/`--scripts` arguments (defaulting to `Path(__file__).resolve().parent.parent` as newer counters do), and make the shokuknow path a parameter.
- **H7**: apply the round-47 rule (null or repo-relative `log_path`) retroactively by regenerating the round-46 receipts' teardown blocks, or add a one-line note that the recorded log paths are historical and the tails are the evidence.
- **S1/S2/S3**: give r42/r43 counters an independent oracle where feasible (like this round's numstat), or at least snapshot the imported helper at the tip and pin its sha256 so drift is detected.

Evidence commands (run by this seat):
```
readlink -f /home/vgpnk/.local/bin/llama-server
# -> /home/vgpnk/.local/opt/llama-b11755/llama-server
sha256sum /home/vgpnk/.local/opt/llama-b11755/llama-server
# -> b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804
/home/vgpnk/.local/opt/llama-b11755/llama-server --version
# -> version: 0.7.0-dev (build 11909, commit caa8191df)   [rc=0]
```
