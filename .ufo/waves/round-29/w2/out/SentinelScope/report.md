# SentinelScope — write-boundary audit

**Verdict: scope violations / unsafe ambiguities found.** Static review only; no task commands, tests, clones, or lane mutations were run. Reviewed the current `spec.json` bytes (SHA-256 `1326cdceba3c6222f331d209870ea20e587f3d2aeae9a205994e9f7c4cf2e083`) with lane `HEAD` `513eba3ba51a142c9936553e3a85918345eb5c4c`.

## Findings

### High — `VerifyLogFreshness`, `VerifyMistakeFix` (and bare reruns requested by `VerifyLogEntries`): selftest writes outside the authorized roots

- **Offending instructions:** `VerifyLogFreshness` says to run `/usr/bin/python3 .../tools/prereg-time-check.py --selftest`; `VerifyMistakeFix` says “run --selftest in the working tree”; `VerifyLogEntries` requires the listed re-verification commands to be run.
- **Exploit path:** the command omits `--scratch`. In the inspected tool, `DEFAULT_SCRATCH` is `/fast/scratch/hyaku/kama-r26/ExecPreregTimeCheck` (`tools/prereg-time-check.py:43`). `main()` creates that directory and invokes the selftest without an override (`:248-250`); the selftest creates a persistent `ptc-selftest-*` repository there (`:164-169`), writes `f.json`, and runs `git add`/`git commit` in it (`:173-179`). No cleanup is performed in the shown selftest.
- **Impact:** each run creates files and Git metadata under `/fast/scratch/...`, outside both the seat output directory and the allowed `/tmp` scratch area. This can also leave shared scratch artifacts between seats.
- **Smallest remediation:** pass a unique seat-scoped `/tmp` scratch path with `--scratch` on every invocation (and make the allowed selftest scratch-repo exception explicit if “scratch clones” is intended literally).

### Medium — `VerifyMistakeFix`: includes a lane-mutating command as an option

- **Offending sentence:** “Extract revisions to /tmp: `git -C /home/vgpnk/Projects/shokunin/kama-shokunin worktree add /tmp/kama-w2-ptc-<name> 75b78bb4` (or archive) — NEVER mutate the lane; instead use: `git -C /home/vgpnk/Projects/shokunin/kama-shokunin archive 75b78bb4 | tar -x -C /tmp/kama-w2-ptcA-<name>`.”
- **Exploit path:** choosing the first offered option runs `git worktree add` against the lane repository; even though the destination is `/tmp`, Git updates lane worktree metadata. The later prohibition and archive alternative conflict with the earlier executable option.
- **Impact:** mutates lane Git administrative state, expressly forbidden by the assignment.
- **Smallest remediation:** remove the `worktree add` option and retain only the `git archive | tar` extraction.

### Medium — `RerunCounter` / `RerunCounterBase`: receipt destination and counter script are CWD-relative

- **Offending instruction:** `RerunCounter` says to run `... python3 .ufo/waves/round-29/count-c1.py --repo <clone> ... --out receipt.json`; `RerunCounterBase` inherits this via “Same as RerunCounter”.
- **Evidence:** `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/count-c1.py:351-356` writes `o.out` directly with `open(o.out, "w")`; the relative path is not rooted at `--repo`. The script path `.ufo/.../count-c1.py` is also relative to the caller's working directory.
- **Exploit path:** if invoked from the lane (or another non-clone CWD), the command can execute that CWD's counter and create `receipt.json` there, outside the allowed seat output or `/tmp` clone. `--repo <clone>` only selects the repository inspected; it does not anchor the script or output paths.
- **Impact:** accidental lane write and/or checking a different counter than the clone whose hash is claimed.
- **Smallest remediation:** use an absolute counter path inside `<clone>` and an absolute `--out` path inside that unique `/tmp` clone (or the seat's allowed output directory).

### Medium — wave/report destinations point outside the allowed per-seat directory

- **Evidence:** `spec.json` top-level field is `"reportDir": ".ufo/waves/round-29/w2"`, which is outside `w2/out/<seat>/`. The current `w2/` directory listing also contains root-level reports such as `SrcS174.md` and `VerifyRow01.md` alongside `out/` (observed; their origin is not established by this audit). The task's own `Report:` target `.ufo/waves/round-29/w2/SentinelScope.md` is likewise outside the explicit write allowance.
- **Impact:** a report writer using `reportDir` or that `Report:` path would write outside the seat's permitted directory. I therefore wrote only `w2/out/SentinelScope/report.md`; I did not create `w2/SentinelScope.md`.
- **Smallest remediation:** route generated reports to each seat's `w2/out/<seat>/` directory and remove/override root-level report targets for leaf seats.

## Checked without finding a scope violation

- `CensusRun` invokes `sources-census.sh validate` without `--out`. The script documents itself as read-only and says it writes only stdout or explicit `--out` (`/home/vgpnk/Projects/shokunin/scripts/sources-census.sh:6-7,20,94-95`).
- The other reviewed item prompts are read-only, mutate only an explicitly described clone under `/tmp`, or ask for a draft as the response rather than a filesystem write. I found no item directing edits to `.ufo/state/`, `.ufo/watchdog.log`, `MANIFEST.json`, fleet scripts, or templates, and no other lane/fleet/sibling `git`/`jj` mutation command.

## Evidence / execution record

Read-only fingerprint command output:

```text
1326cdceba3c6222f331d209870ea20e587f3d2aeae9a205994e9f7c4cf2e083  .ufo/waves/round-29/w2/spec.json
513eba3ba51a142c9936553e3a85918345eb5c4c
```

Relevant absolute evidence paths: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/w2/spec.json`; `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/count-c1.py`; `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/prereg-time-check.py`; `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh`. No test/check was executed, so no runtime result is claimed.