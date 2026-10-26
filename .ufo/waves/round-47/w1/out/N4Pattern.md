# N4Pattern — round-47 cross-claim pattern report (calibration + operability)

**Verdict: the round-47 "checkable from outside" pattern (C1 vs git numstat + constructed fixture; C2 vs fresh re-acquisition from recorded URLs/digests) is correctly applied to the two claims, but 8 lane instruments and 2 receipt families still carry host-path, decoded-text or shared tool/counter definitions — one fails today on this host with the default binary (kama-context-capacity server-version mark), and the only independent receipt validator is already INVALID on the v4 receipts.**

Deliverable: `.ufo/waves/round-47/w1/out/N4Pattern/patterns.md` (ranked inventory, file:line, evidence commands). Audited at lane tip `46a924e0` (build `3a09a1d9`), read-only.

## Evidence (commands / outputs / file:line)

1. **D1 — host-path + decoded-text, failing now.** `tools/kama-context-capacity.py:63` `SERVER_VERSION_MARK='build 11755'`, checked at `:746-754` against `--version` stdout. Measured:
   - `readlink -f /home/vgpnk/.local/bin/llama-server` → `/home/vgpnk/.local/opt/llama-b11755/llama-server`
   - `sha256sum` of that binary → `b6a31a8e…` (equals echo-recheck's pinned server, `tools/echo-recheck.py:64`)
   - `…/llama-b11755/llama-server --version` → `version: 0.7.0-dev (build 11909, commit caa8191df)`, rc=0
   - Mark absent → `SetupError('server-version-mismatch:…')`; a fresh session on the documented defaults fails immediately.
2. **H1 — host path.** `tools/echo-recheck.py:69-71` `LANE = Path("/home/vgpnk/Projects/shokunin/kama-shokunin")`, default receipt under `.ufo/waves/round-27/w1a3/out/ExecLiveEchoProbe/`.
3. **H4 — host paths.** `tools/round35-statement-audit.py:31`, `round36-statement-audit.py:28`, `round37-statement-audit.py:32-33` (`FLEET`, `SHOKUKNOW=/home/vgpnk/Projects/shokuknow/merge/kama/SOURCES.append.md`), `round38-statement-audit.py:38-39` (`STAGED`); no `--fleet`/`--staged` args. Existence confirmed (`ls -ld`, 196639 bytes, 2026-10-24).
4. **H5 — host path.** `tools/round42-capacity-audit.py:76` and `tools/round43-health-audit.py:88` `CENSUS="/home/vgpnk/Projects/shokunin/scripts/sources-census.sh"` (exists; `ls -ld` → -rwxr-xr-x).
5. **H6 — host path.** `tools/sources-append-only.py:599` `--repo` default `"/home/vgpnk/Projects/shokunin/kama-shokunin"`.
6. **H2/H3 — per-user/shared scratch defaults.** `tools/kama-context-capacity.py:61` `DEFAULT_SCRATCH=/fast/scratch/hyaku/kama-context-capacity` (absent; the tool mkdirs it, `:767`); `tools/prereg-time-check.py:45` `DEFAULT_SCRATCH=/fast/scratch/hyaku/kama-r26/ExecPreregTimeCheck`.
7. **H7 — dead receipt pointer.** `.ufo/waves/round-46/c1/live/receipt-{1,2,3}.json:548` `teardown.log_path="/fast/scratch/hyaku/kama-r46/X1Live/kama-llamacpp-live-*.log"` (copy cited: `w1/out/N4Pattern/receipt-r46-c1-live-1.json`); round-47 C2 receipts fix it (`receipt-1.json:559` null; copy: `receipt-r47-c2-live-1.json`).
8. **S1 — shared definition.** `tools/round42-selfdesc-reconcile.py:130-134` imports `round41-scorecard-reconcile.py` via `importlib` (docstring line 22 "imported unchanged"; `SKILL.md:1404` row documents the import).
9. **S2 — shared definition.** `tools/kama-context-capacity.py:602-635` loads `.ufo/waves/round-25/count-c2.py` CELLS; `:187-191` loads `kama-llamacpp-live.py`.
10. **S3 — shared definition + decoded text.** `tools/round43-registry-audit.py:116-131` runs the gate blob and regex-parses its summary (`registered (\d+) …`) — the instrument under audit is its own oracle.
11. **S4 — shared definition.** `tools/round46-release-recheck-audit.py:109-112` copy-pastes `ROW`/`URL` regexes from `tools/release-recheck.py:38,61-63`; both use `holds` = range text-equality (round-46 lesson: K1Cheat relocation script greened all 91 rows; carried as frontier `r46-D3`).
12. **S5 — shared definition (schema copy drift), failing now.** `tests/llamacpp-live/check-receipt.py:47-49,86-112` re-implements schema v1-v3 + pinned upstream spans at `LLAMA_COMMIT 704366d76`; measured INVALID on v4 receipts (`schema is 'kama-llamacpp-live/v4', want …v1/v2/v3`, exit 1 — K0Harm command 11 report).
13. **S6 — historical instance.** round-46 v1 counter shared the `---`-filter with v1 tool (D1); v2's outside ground truth (numstat, fixture) is disclosed in preregistration `limits` (line 24).

No tools were installed (python3/git only; no pacman/uv/npx — nothing to record under RULES.md).

## Absolute paths written
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/N4Pattern/patterns.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/N4Pattern/receipt-r46-c1-live-1.json`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/N4Pattern/receipt-r47-c2-live-1.json`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/N4Pattern.md` (this report)
