VERDICT: partial — the current suite rejects all bad controls, but attribution and three gate-flip results do not establish the advertised targeted checks and re-derivation.

Attacked axes: per-control attribution fidelity; gate-flip re-derivation coverage; K3 repeatability. Reviewed commit `54a29268e2083caa2b1e0d54ee1e7d90961302f3` in a temporary clone.

## Findings (severity order)

### Medium — attribution is substring/any-match, not a literal expected-check set

`tests/llamacpp-live/controls.py:297-299` documents expected failed-check *substrings*; `:454-460` implements `any(tok in fid for tok in expected for fid in low)`. It neither compares exact check IDs nor requires every listed token. This differs from the module docstring's “do not cover the token set” wording (`:23-26`). K4 expects `teardown`, `sigkill`, `kill`, and `graceful` (`:313-315`), so a failure ID containing only `teardown` suffices. I exercised `_attributed` with K4's expectation and the real check ID `teardown_port_closed`: it returned `True`, despite that ID containing no `sigkill`, `kill`, or `graceful` token. [INFERENCE] A port-closed failure can therefore be counted as attribution for K4 even when the SIGTERM-escalation failure was not identified.

K7 has `expected_failed=[]` (`:322-323`); `_attributed` returns `None` for it (`:457-460`), and `run_control` counts a rejection inconclusive only when attribution is exactly `False` (`:567-570`). Thus any rejected K7 run counts as detection regardless of its failed-check cause. In my current full run K7 did report `setup_error: ready-timeout`, the intended failure, but the counter does not enforce that cause.

### Medium — gate-flip does not isolate check re-derivation for K3, K6, or K7

`tests/llamacpp-live/controls.py:463-491` flips the failed checks' `passed` fields but preserves all other receipt fields. Its comment explicitly says a non-null `setup_error` can make the gate reject without isolating re-derivation (`:489-491`). `tests/llamacpp-live/check-receipt.py:203-211` rejects every non-null `setup_error`; flipping checks cannot remove that independent rejection reason. The current run produced K3 `post-probes:child-exited-rc0`, K6 `internal:RuntimeError`, and K7 `ready-timeout`; all three flipped receipts still exited 1 (2, 1, and 3 checks flipped, respectively). The aggregate increments `gate_flip_bad` for any accepted flipped receipt without excluding these non-isolating cases (`controls.py:676-678`). Therefore `gate_flip_bad=0` is valid as a raw count, but it does not demonstrate check re-derivation for K3/K6/K7.

### K3 repeatability — no defect observed in the tested sequence

The fake exits after its second curl `/v1/models` response (`tests/llamacpp-live/controls.py:216-224`); the tool makes two probe runs and then checks liveness at `post-probes` (`tools/kama-llamacpp-live.py:1208-1219`). Five sequential `--only k3` runs at this commit all returned the same outcome: tool exit 2, gate exit 1, `setup_error=post-probes:child-exited-rc0`, failed checks `teardown_graceful` and `teardown_port_closed`. K3 is repeatable in this harness/environment; [INFERENCE] five repetitions do not prove behavior under every possible host schedule.

## Residual risk and verification gaps

- The full current controls invocation exited 0: K0 accepted, K1–K8 rejected, `accepted_bad=0`, `inconclusive=0`, and `gate_flip_bad=0`. The two findings above limit what the latter two zero counts prove; this review found no current accepted-bad control.
- I did not rerun the frozen tool/gate pair; this scoped attack used the round-17 current tool and gate plus the committed source.
- The LSP route is unavailable in this session (`read xd://lsp` returned “No such tool”); no LSP status/references/definition/diagnostics were possible. I used direct source reads and execution, not grep as semantic proof.
- Post-run `ss -ltnp` showed transient loopback Python listeners including `127.0.0.1:34113`; `ps` identified the observed processes as `check.py --probe /tmp/KamaR17.RerunMutantGrid-clone/...`, not this seat's control fake. I did not contact or terminate them. The controls runs used their own temporary directories and their cleanup paths; this seat's clone was removed.

## Commands run (exit codes)

- `git clone -q /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/KamaR17.ControlsAttribution-clone && git -C /tmp/KamaR17.ControlsAttribution-clone checkout -q 54a29268e2083caa2b1e0d54ee1e7d90961302f3 && git -C /tmp/KamaR17.ControlsAttribution-clone log -1 --format='%H %ci %s'; echo "EXIT:$?"` — 0.
- `cd /tmp/KamaR17.ControlsAttribution-clone && wc -l tests/llamacpp-live/controls.py tests/llamacpp-live/check-receipt.py tests/llamacpp-live/*.py tools/kama-llamacpp-live.py 2>/dev/null; ls tests/llamacpp-live/; echo "EXIT:$?"` — 0.
- `ls -la /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/runs/ /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/live/ /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/frozen/ 2>&1 | sed 's/^/  /'; echo "EXIT:$?"` — 0.
- `cd /tmp/KamaR17.ControlsAttribution-clone && PYTHONDONTWRITEBYTECODE=1 python3 tests/llamacpp-live/controls.py --tool /tmp/KamaR17.ControlsAttribution-clone/tools/kama-llamacpp-live.py --gate /tmp/KamaR17.ControlsAttribution-clone/tests/llamacpp-live/check-receipt.py --json` — controls exit 0 (the wrapper printed `EXIT:0`).
- `cd /tmp/KamaR17.ControlsAttribution-clone && for n in 1 2 3 4 5; do printf 'TRIAL:%s\n' "$n"; PYTHONDONTWRITEBYTECODE=1 python3 tests/llamacpp-live/controls.py --tool /tmp/KamaR17.ControlsAttribution-clone/tools/kama-llamacpp-live.py --gate /tmp/KamaR17.ControlsAttribution-clone/tests/llamacpp-live/check-receipt.py --only k3 --json; rc=$?; printf 'TRIAL_EXIT:%s\n' "$rc"; done; exit 0` — each control invocation 0; loop 0.
- `cd /tmp/KamaR17.ControlsAttribution-clone && PYTHONDONTWRITEBYTECODE=1 python3 -c 'import importlib.util; p="tests/llamacpp-live/controls.py"; s=importlib.util.spec_from_file_location("c",p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); expected=m.CONTROLS["k4"][3]; print("k4_expected=",expected); print("failed=[teardown_port_closed] attributed=",m._attributed(["teardown_port_closed"],expected))'; printf 'EXIT:%s\n' "$?"` — 0.
- `ss -ltnp; printf 'EXIT:%s\n' "$?"` — 0 (run twice).
- `ps -p 3777656,3777661,3777660,3777657,3777659,3777658 -o pid=,etimes=,args=` — 1 (the listed processes had already exited).
- `ps -p 3797750,3797752,3797753,3797751,3797754,3797749 -o pid=,ppid=,etimes=,args=` — 0.
- `rm -rf /tmp/KamaR17.ControlsAttribution-clone; printf 'EXIT:%s\n' "$?"` — 0.

Installs/updates: none.
