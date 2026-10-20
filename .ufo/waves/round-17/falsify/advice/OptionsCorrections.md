VERDICT: partial — all five appended corrections are accurately anchored; three broad claims remain uncorrected.

## Findings (by severity)

### Low — two tool comments still claim every non-frontend request gets the loading 503

- `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-probe.sh:422-423`: “is_ready is false every non-frontend path returns 503 with the exact envelope”.
- `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-llamacpp-live.py:137-138`: “is_ready is false every non-frontend path answers 503”.

Both omit the `OPTIONS` bypass. The pinned source handles `OPTIONS` and returns `Handled` at `server-http.cpp:347-352`, before the state gate at `:354`; these comments should say non-OPTIONS requests to non-frontend paths. This is a documentation/comment defect, not evidence of a runtime behavior defect in either tool.

### Low — the loading fixture rationale also overstates the source behavior

`/home/vgpnk/Projects/shokunin/kama-shokunin/tests/probe-verdicts/LoadingEnvelope.json:143-145` says the gate returns the envelope for “EVERY non-frontend path”. That excludes no method, although OPTIONS bypasses the gate. Narrow the rationale; the shown `/v1/models` and `/health` fixture paths remain consistent with the source. This is a fixture-description defect, not a demonstrated classifier failure.

## Correction accuracy

All five correction targets and source references match the pinned `server-http.cpp` at commit `54a29268e2083caa2b1e0d54ee1e7d90961302f3`:

- `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/README.md:232` correctly identifies its target row at `:206`.
- `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/knowledge/endpoint-identity.md:218` correctly targets `:202`.
- `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/knowledge/runtime-health-surface-matrix.md:77` correctly targets `:65`.
- `/home/vgpnk/Projects/shokunin/kama-shokunin/SKILL.md:555` correctly targets `:519`.
- `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/knowledge/llamacpp-loading-lifecycle.md:204-207` correctly refers to its earlier line `:29`.

The source anchors are exact: `frontend_paths` is checked at `:309-311`; the OPTIONS condition, response setup and `Handled` return are at `:347-352`; state and API-key gates are at `:354` and `:357`; body fields are message `:318`, type `:319`, code `:320`. The cited OPTIONS range ends at its handled return; its closing brace is `:353`, unnecessary to establish the short-circuit. The `/health` and `/v1/health` public-endpoint set at `:251-258` is consulted by API-key validation at `:267`, not by the loading-state gate, so the correction that they remain gated is accurate.

`corpus/SOURCES.md:48` retains the earlier S036 wording, but its append-only note at `:140-141` explicitly says the claim excludes OPTIONS; I do not count that occurrence as uncorrected.

## Search, verification, and limits

- Pinned-clone command: `git clone -q /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/KamaR17.OptionsCorrections-clone && git -C /tmp/KamaR17.OptionsCorrections-clone checkout -q 54a29268e2083caa2b1e0d54ee1e7d90961302f3 && git -C /tmp/KamaR17.OptionsCorrections-clone rev-parse HEAD` — exit 0; returned the requested commit.
- `wc -l` on the five target documents and pinned `server-http.cpp` — exit 0; lengths were 245, 218, 77, 583, 211 and 940 lines, respectively.
- Specialized `grep` search for literal `non-frontend` over the pinned clone's `corpus/`, `tools/`, `tests/`, `registry/` and `SKILL.md` paths found the claims cited above and the corrected S036 occurrence. The search tool exposes no shell exit code. These safe paths did not include `.git`, `.jj`, or `.ufo/interactive-sessions`; historical wave material was not exhaustively searched.
- LSP unavailable: querying `xd://lsp` returned `No such tool: xd://lsp`; no LSP status, references, definition, or diagnostics could be obtained. Review therefore used pinned-source reads and text search only. No tests/builds were run.
- Scratch cleanup: `rm -rf /tmp/KamaR17.OptionsCorrections-clone && test ! -e /tmp/KamaR17.OptionsCorrections-clone` — exit 0.
- Installs/updates: none.
