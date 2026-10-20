VERDICT: partial — two reruns confirm 0 accepted-bad, but the K7 target-check claim is not established.

## Finding — Low: K7 is rejected but not target-attributed

- `SCORECARD.md:681` claims “current 0 of 8, each failing its targeted check”.
- `tests/llamacpp-live/controls.py:322-323` defines K7 with `expected_failed=[]` and describes it as “hang: listens, never answers (bounded by --ready-timeout 2)”. `_attributed()` returns `None` when no expected tokens are supplied (`tests/llamacpp-live/controls.py:454-460`); `inconclusive` is counted only when `attributed is False` (`:567-570`).
- The recorded K7 row has `expected_failed: []`, `attributed: null`, and `inconclusive: false`, despite `failed_checks` listing three checks; it records `setup_error: "ready-timeout"`, tool exit 2, and gate exit 1 (`.ufo/waves/round-17/runs/controls-current.json:188-209`). Thus K7 is rejected on the timeout path, but there is no explicit expected-check assertion for it. The aggregate accepted-bad count is confirmed; the stronger “each ... targeted check” wording is not evidenced for K7. Qualify that clause or give K7 an explicit target criterion.

## Rerun result

- Both requested full runs returned the same nine control rows and summary: K0 accepted; K1–K8 rejected; `accepted_bad=0`, `gate_flip_bad=0`, `inconclusive=0`, `good_ok=true`. K1–K6 and K8 had `attributed=true` with their expected tokens present in failed check IDs; K7 is the exception above. The displayed Run 1 JSON matched Run 2 at every field. Run 2's captured JSON was byte-for-byte equal to the recorded baseline (`cmp` exit 0; SHA-256 `75fd6ca93d423c68ecae57937a0577e308fe1e8d10d0f2f22b298b379ce7a315`).
- Tool and gate identities matched the recorded baseline: tool SHA-256 `0efd1723b02ef748d720a6036d3ac481b1d5fe9755110999d7c9acaf486c46ac`; gate SHA-256 `ad6801791f2ada896a7ee188609391aac86185c47320dbf415331869ca9cd2a5`.
- These are fake-server controls, not another real b11755 run. The tool hard-refuses ports 8080 and 34113 (`tools/kama-llamacpp-live.py:66-69`); post-run `ss -ltnp` snapshots showed neither port listening.

## Process cleanup

- After Run 1, the broad process scan found PID 3689974 running a fake under another seat's `/tmp/KamaR17.ShonenProvince-overflow-hu7tccly/...` directory. It was not this seat's process and was left untouched. No process under this seat's clone/control temp paths was listed.
- After Run 2, the targeted `pgrep` filter returned no fake-server, llama-server, controls-harness, or this-seat process. `ss -ltnp` still showed other local Python/omp/chromium listeners; these were not attributed to this run. This seat's clone and captured JSON scratch were removed.

## Commands and observed status

- `git clone -q /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/KamaR17.RerunControlsCurrent-clone && git -C /tmp/KamaR17.RerunControlsCurrent-clone checkout -q 54a29268e2083caa2b1e0d54ee1e7d90961302f3 && git -C /tmp/KamaR17.RerunControlsCurrent-clone rev-parse HEAD` — exit 0; HEAD was `54a29268e2083caa2b1e0d54ee1e7d90961302f3`.
- Run 1: `PYTHONDONTWRITEBYTECODE=1 python3 /tmp/KamaR17.RerunControlsCurrent-clone/tests/llamacpp-live/controls.py --tool /tmp/KamaR17.RerunControlsCurrent-clone/tools/kama-llamacpp-live.py --gate /tmp/KamaR17.RerunControlsCurrent-clone/tests/llamacpp-live/check-receipt.py --json` — completed successfully; exit 0 [INFERENCE: the direct invocation did not print its status].
- Run 2: `PYTHONDONTWRITEBYTECODE=1 python3 /tmp/KamaR17.RerunControlsCurrent-clone/tests/llamacpp-live/controls.py --tool /tmp/KamaR17.RerunControlsCurrent-clone/tools/kama-llamacpp-live.py --gate /tmp/KamaR17.RerunControlsCurrent-clone/tests/llamacpp-live/check-receipt.py --json > /tmp/KamaR17.RerunControlsCurrent-run2.json; rc=$?; cat /tmp/KamaR17.RerunControlsCurrent-run2.json; printf '\ncommand_exit=%s\n' "$rc"; exit "$rc"` — `command_exit=0`.
- `cmp -s /tmp/KamaR17.RerunControlsCurrent-run2.json /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/runs/controls-current.json; rc=$?; printf 'cmp_exit=%s\n' "$rc"; sha256sum /tmp/KamaR17.RerunControlsCurrent-run2.json /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/runs/controls-current.json; test "$rc" -eq 0` — `cmp_exit=0`; both hashes were `75fd6ca93d423c68ecae57937a0577e308fe1e8d10d0f2f22b298b379ce7a315`.
- `sha256sum /tmp/KamaR17.RerunControlsCurrent-clone/tools/kama-llamacpp-live.py /tmp/KamaR17.RerunControlsCurrent-clone/tests/llamacpp-live/check-receipt.py /tmp/KamaR17.RerunControlsCurrent-clone/tests/llamacpp-live/controls.py` — exit 0; hashes were tool `0efd1723b02ef748d720a6036d3ac481b1d5fe9755110999d7c9acaf486c46ac`, gate `ad6801791f2ada896a7ee188609391aac86185c47320dbf415331869ca9cd2a5`, controls `aad8b1c758fe9616ecd7ad78538dbfd82227c7e99df3b051d2bf82d34d6e3a06`.
- `ss -ltnp; printf '\n--- matching processes ---\n'; pgrep -a -f '[f]ake_server\.py|[l]lama-server|[k]ama-live-controls' || true` (after Run 1), and `ss -ltnp; printf '\n--- this-seat processes ---\n'; pgrep -a -f '[f]ake_server\.py|[l]lama-server|KamaR17\.RerunControlsCurrent|kama-live-controls-' || true` (after Run 2) — both shell commands exit 0; observations above.
- `rm -rf /tmp/KamaR17.RerunControlsCurrent-clone /tmp/KamaR17.RerunControlsCurrent-run2.json && test ! -e /tmp/KamaR17.RerunControlsCurrent-clone && test ! -e /tmp/KamaR17.RerunControlsCurrent-run2.json` — exit 0.

## Installs

None.