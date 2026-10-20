VERDICT: confirm — per-task background-job refusals now count once by distinct task label; spawned counting is preserved.

Axes: calibration (provenance accuracy, primary) and operability (clear refused-versus-spawned records).

## Change

Copied round-17 `dispatch-provenance.py` into the round-18 work path and changed refusal extraction. For task-specific `Background job limit reached (N)` messages, the tool counts distinct labels; that text count takes precedence over legacy integer/status tallies to avoid double-counting duplicate representations. Without such text, the round-16 tally remains the fallback. Existing spawned extraction and the documented canonicalization are unchanged. The selftest now covers refused-only, spawned-only, mixed, and empty results, including duplicate refusal labels.

## Retained evidence

- The frozen implementation recorded the round-17 refused result as `refused: 0, spawned: 0`; the corrected implementation recorded `refused: 82, spawned: 0`. This matches the 82 task-specific messages described in `corpus/lessons/round-17.md:293-295` and `round-17/falsify/advice/ProvenanceRerun.md:5-7`; the input text is `round-17/build/refused-result-1.json:4`.
- `--selftest`: `selftest: 30/30 checks passed` (exit 0). `python3 -m py_compile` also exited 0.
- The docstring still specifies the single taskCall canonicalization exactly as `json.dumps(taskCall, sort_keys=True, separators=(',',':'), ensure_ascii=False).encode('utf-8')`.

## Design, limits, and risks

- Text evidence is restricted to result `text` fields (or the raw UTF-8 fallback for non-JSON input). The pattern expects a task label followed by a colon and the exact case-sensitive `Background job limit reached (<digits>)` wording; the result delimiter is semicolon. Repeated identical labels count once.
- The code cannot recognize different/localized refusal wording, infer failures that are not present in the captured result, or prove that the reported tasks were actually submitted to or refused by a server. If only some refusals appear in text while a legacy tally contains additional distinct refusals, the text observation wins and those extra tally items are not added. These are deliberate bounds of the available result representation.
- LSP is unavailable in the mounted tool inventory; no LSP references/definition/refactor queries were made. No tools were installed or updated. No blockers.

## Delivered files

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/build/out/C2Provenance-2/dispatch-provenance.py` — SHA-256 `93705f17a2b2dfeab1e80c886bcb53ae5a8e43b0c6e86e91b73a65ad5c1ea72f`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/build/out/C2Provenance-2/dispatch-provenance.py.diff` — unified diff against `.ufo/waves/round-18/frozen/round-17_dispatch-provenance.py`; SHA-256 `df68ca5d6bb59d2099d9bcc18987be908fa326f80fe24ac1520e969c343a2dd7`

## Commands and exit codes

- `git clone -q /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/kama-r18-C2Provenance-2 && git -C /tmp/kama-r18-C2Provenance-2 switch -q -c seat/C2Provenance-2` — 0.
- `python3 /tmp/kama-r18-C2Provenance-2/.ufo/waves/round-17/dispatch-provenance.py --attempt-result /tmp/kama-r18-C2Provenance-2/.ufo/waves/round-17/build/refused-result-1.json --label refused --out /tmp/kama-r18-C2Provenance-2/.ufo/waves/round-18/frozen-refusal-ledger.json` — 0; frozen result `refused=0`, `spawned=0`.
- `python3 -m py_compile /tmp/kama-r18-C2Provenance-2/.ufo/waves/round-18/dispatch-provenance.py` — 0.
- `python3 /tmp/kama-r18-C2Provenance-2/.ufo/waves/round-18/dispatch-provenance.py --selftest` — 0; 30/30 checks passed.
- `python3 /tmp/kama-r18-C2Provenance-2/.ufo/waves/round-18/dispatch-provenance.py --attempt-result /tmp/kama-r18-C2Provenance-2/.ufo/waves/round-17/build/refused-result-1.json --label refused --out /tmp/kama-r18-C2Provenance-2/.ufo/waves/round-18/corrected-refusal-ledger.json` — 0; corrected result `refused=82`, `spawned=0`.
- `diff -u /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/frozen/round-17_dispatch-provenance.py /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/build/out/C2Provenance-2/dispatch-provenance.py > /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/build/out/C2Provenance-2/dispatch-provenance.py.diff` — 1, expected because the files differ.
- `sha256sum <delivered script> <delivered diff>` — 0; digests listed above.
- `rm -rf -- /tmp/kama-r18-C2Provenance-2` — 0; isolated clone removed.

Only the staged implementation, its required diff, and this exclusive report were written in the lane; L1 integration remains outstanding.