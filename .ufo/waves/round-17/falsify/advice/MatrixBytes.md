VERDICT: confirm — the matrix JSON set, round-16 matrix digest, and probe bytes are unchanged at the round-17 commit.

## Findings

- **No actionable finding (C1 byte-identity constraint confirmed).** Compared `cff9e62f05aa7cfb9059444f62eb787100719713` with `54a29268e2083caa2b1e0d54ee1e7d90961302f3`: each tree contains the same nine JSON paths and the same Git blob IDs; `git diff --quiet` found no JSON differences. The nine names are `AuthAndDead.json`, `EnvelopeShapes.json`, `ForeignControls.json`, `LoadingEnvelope.json`, `LoadingRace.json`, `NearMissTriple.json`, `NonLoadingStatuses.json`, `Overbroad503.json`, and `ReadyControls.json`. Thus there is no added JSON in `tests/probe-verdicts/` at the round commit.
- **Round-16 matrix digest reproduced.** Called `matrix_digest()` from `.ufo/waves/round-16/measure.py` after checking out the round commit in a temporary clone. Result: 9 files, SHA-256 `bf9068d89e4cb8a080167cb32cc818943d717a65fcbd21edb2b8256e22771f32`, matching the pinned digest.
- **Probe unchanged.** `tools/kama-probe.sh` has the same blob ID at both commits (`ce45ea8e53ee75d558615eeb4327faa2ed286a03`) and the same file SHA-256, `36b64978ee3a3aa29e1b73f04ca5c7ad04a9aee880e7032abfd894fa7b3a29d3`.

Evidence anchors: `corpus/lessons/round-17.md:30` — “The nine matrix files and the probe stay byte-identical.”; `corpus/lessons/round-17.md:49-50` — “`tools/kama-probe.sh` is byte-identical”; `corpus/lessons/round-17.md:174-175` — “matrix set digest unchanged”; `.ufo/waves/round-16/measure.py:278-290` — “The digest covers every `*.json` file name and its sha256 ... sorted by name.”

## Commands and results

All commands below completed with exit 0 unless a different result is stated; command outputs and counts are from the lane repository or the explicitly noted clone.

- `git -C /home/vgpnk/Projects/shokunin/kama-shokunin diff --stat cff9e62 54a29268e2083caa2b1e0d54ee1e7d90961302f3 -- 'tests/probe-verdicts/*.json'` — empty diff stat.
- `git -C /home/vgpnk/Projects/shokunin/kama-shokunin diff --quiet cff9e62 54a29268e2083caa2b1e0d54ee1e7d90961302f3 -- 'tests/probe-verdicts/*.json'` — exit 0.
- `git -C /home/vgpnk/Projects/shokunin/kama-shokunin ls-tree -r --format='%(objectname) %(path)' cff9e62 -- tests/probe-verdicts/` and the same command with `54a29268e2083caa2b1e0d54ee1e7d90961302f3` — same nine JSON paths and object IDs. The `--name-only` listings and counts also yielded nine JSONs at each commit.
- `git -C /home/vgpnk/Projects/shokunin/kama-shokunin rev-parse cff9e62:tools/kama-probe.sh 54a29268e2083caa2b1e0d54ee1e7d90961302f3:tools/kama-probe.sh` — same blob ID; `git show <rev>:tools/kama-probe.sh | sha256sum` at each revision — same SHA-256 above.
- `git clone -q /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/kama-r17-matrixbytes-clone && git -C /tmp/kama-r17-matrixbytes-clone checkout -q 54a29268e2083caa2b1e0d54ee1e7d90961302f3` — exit 0. In that clone, `PYTHONDONTWRITEBYTECODE=1 python3 -c 'import importlib.util; p=".ufo/waves/round-16/measure.py"; s=importlib.util.spec_from_file_location("round16_measure", p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); n,d=m.matrix_digest(); print(f"matrix_files={n} matrix_sha256={d}")'` — exit 0; printed `matrix_files=9 matrix_sha256=bf9068d89e4cb8a080167cb32cc818943d717a65fcbd21edb2b8256e22771f32`.
- `rm -rf /tmp/kama-r17-matrixbytes-clone && test ! -e /tmp/kama-r17-matrixbytes-clone` — exit 0; temporary clone removed.

## Residual risk and verification gaps

None for the assigned matrix/probe byte-identity and digest checks. This review did not assess C1 detector behavior or the C2 live lifecycle changes. No tools were installed.