VERDICT: partial — capability row `live-llamacpp-lifecycle` (SCORECARD §Round 16, SKILL.md §Round-16 registry rows, citations in SHONEN, corpus/README, knowledge entry, lesson)

Axes: calibration (honest "before" and limits), operability (evidence pointers), freshness (dated-sample wording).

Summary: nothing is pre-claimed. The evidence pointers resolve, and I re-derived them independently: the receipt gate passes and the official release asset matches byte-for-byte. First-working round 16 holds. Two problems remain. (1) The C2 "before" statement is wrong about round 3. (2) The row text in SCORECARD and SHONEN does not state the toy-model and self-chosen-alias limits, which the knowledge entry does state. Smaller items: a pending pointer that does not resolve yet, a naming split, and no harness digest in the receipt.

## A. Pre-claiming — CONFIRM (not pre-claimed, as of b8e485c)

- AXES.md:62-64 says rows enter "only through a round that demonstrates the capability running; a capability without a passing demonstration in the round report is pre-claiming".
- SCORECARD.md:588-598 states C2 only as *planned* ("Planned score **8 → 8** with a capability row"; "Measured values are appended below after execution"). No capabilities table row exists for it yet.
- SCORECARD.md:565-567 "Capability rows held" lists only `sources-registry` and `ollama-offline-evidence-replay`. This is consistent.
- `ls /home/vgpnk/Projects/shokunin/.ufo/reports/round-16/` → no `kama.md` yet. So the row MUST NOT enter the table until L1's round report carries the passing demonstration. As of now, entering it would be pre-claiming.
- The passing demonstration itself exists and is committed: `git ls-files .ufo/waves/round-16/live` lists receipt.json, receipt-frozen-probe.json and controls.txt in b8e485c.

## B. Evidence-pointer resolvability — CONFIRM, with two gaps

Commands I ran (cwd = lane root):
- `python3 tests/llamacpp-live/check-receipt.py .ufo/waves/round-16/live/receipt.json --expect-model-sha256 270cba1b…256d --expect-server-sha256 b6a31a8e…d804` → exit 0
- `python3 tests/llamacpp-live/check-receipt.py .ufo/waves/round-16/live/receipt-frozen-probe.json --expect-probe-sha256 $(sha256 of frozen probe)` → exit 0
- `python3 tests/llamacpp-live/check-receipt.py .ufo/waves/round-16/live/receipt.json --expect-probe-sha256 $(sha256 of tools/kama-probe.sh)` → exit 0. The current probe 6edd3c4c… equals receipt `.probe.sha256`.
- `python3 tests/llamacpp-live/check-receipt.py --selftest` → exit 0
- `sha256sum`: model `270cba1b…256d` (1,185,376 B); `~/.local/opt/llama-b11755/llama-server` `b6a31a8e…d804`; `libllama-server-impl.so` `e404b91a…59ed`. All equal the receipt.
- Independent provenance check: `curl -sSL https://github.com/ggml-org/llama.cpp/releases/download/b11755/llama-b11755-bin-ubuntu-x64.tar.gz` → exit 0. The tarball sha256 is `753bfa73…e226`, matching S038 and SKILL.md:532. Unpacked `llama-b11755/llama-server` = `b6a31a8e…d804` and `libllama-server-impl.so` = `e404b91a…59ed`. Installed binary = official asset contents, so the asset-digest → binary-digest link now holds by direct check, not only by the LOG.
- SCORECARD.md:594 "Counting command: the live tool plus the gate (SKILL.md §Round-16)" resolves to SKILL.md:532-533. "caps at lines 26-28" resolves to SCORECARD.md:26-29. S041 exists (SOURCES.md:53).
- `pgrep -x llama-server` → exit 1 (none running). I started no server.

Gap B1 — pointer does not resolve yet:
- `corpus/lessons/round-16.md:91-92` says "Final numbers at the measured commit are in `.ufo/waves/round-16/acceptance.json`". But `ls .ufo/waves/round-16/acceptance.json` → exit 2, no such file.
- LOG.md:953 "Measured results follow in the next entry": there is no next entry yet.
- Both must resolve before the capability row's evidence pointer cites "measured values".

Gap B2 — harness version not pinned in the receipt:
- `grep -c kama-llamacpp-live.py .ufo/waves/round-16/live/receipt.json` → 0 (exit 1). The receipt pins probe, server, install tree and model, but never the producing harness (`tools/kama-llamacpp-live.py`) digest or commit.
- File mtimes are all identical (10:50:49.14, the checkout time), so they carry no evidence either.
- The SCORECARD pointer is "the live tool plus the gate". Nothing ties the committed tool to the receipt except time adjacency: receipt at 13:49:38Z, commit at 10:50:42 -03 ≈ 13:50:42Z. [INFERENCE] It was most likely the same revision, but this is not shown.
- Smallest fix: record `harness.sha256` in `kama-llamacpp-live/v1` receipts going forward. For this round, have L1 re-run the committed tool once, at the measured commit, for the acceptance record.

## C. First-working round — CONFIRM 16; the "before" text is REFUTED in part

- First working = 16 holds. `git grep -nE 'llama-server|Popen|vllm serve|ollama serve' 20e392e -- tools tests` finds only audit-name strings in `tests/ollama-corpus-guard/check.py`. No pre-round lane tool started a runtime. The L1 10:17 smoke was manual and not a lane tool.
- **Refuted: "last real llama.cpp sample round 3".**
  - SCORECARD.md:593 says "(last real llama.cpp sample round 3)".
  - `corpus/lessons/round-16.md:28-29` says "the last real llama.cpp observation was round 3 (2026-10-14)".
  - Round 3 sampled *no* llama.cpp:
    - LOG.md:211 says "`registry_rows_evaluated=11 model_ok=0 drift=11 exit=2` — every row DEAD `connection-refused`".
    - LOG.md:246 says "ports 34113 and 8080 both refuse connections".
    - `registry/history/DELTA.md:9,12` say "2026-10-14T12:42:32Z ufo-fsd-thetick verdict MODEL_OK -> DEAD" (local-helper likewise). Both 2026-10-14 snapshots are model_ok=0.
  - The last real llama.cpp answer is the round-2 baseline 2026-09-29T04:30:44Z (DELTA.md:6; LOG.md:159-161 "34113 still serves the expected llama.cpp model").
  - Effect: this overstates prior live coverage by about two weeks. It is a calibration defect of the same family as M1 (stale state described as something it wasn't).
  - Smallest fix: append a correction (do not rewrite) to both places: "last real llama.cpp answer: round 2 baseline 2026-09-29T04:30:44Z; round 3 (2026-10-14) sampled every registered endpoint DEAD."

## D. Toy-model limits at each citation — PARTIAL

The model facts are verified by me: 1,185,376 B (= 1.19 MB / 1.13 MiB, so "1.2 MB" is fair), and the official CPU-only build. The facts from build-wave CriticC2ToyModel.md:9 are not re-derived by me: F32, 292,800 params, 5 blocks, no chat template.

| Citation | States toy / size? | States no generation / quality / performance? | States MODEL_OK is self-alias? | Verdict |
|---|---|---|---|---|
| knowledge `llamacpp-loading-lifecycle.md:104,118-122` | "tiny model" | yes: generation, quality, performance, GPU, router/sleep, live MODEL_LOADING | yes, "(the id is the caller's alias)" | within limits |
| `corpus/README.md:215-221` | "tiny model" | live loading not graded; consumers not probed | no | within limits for its scope |
| PROVINCE.md:55-60 | "pinned 1.2 MB GGUF" | n/a (boundary note) | n/a | within limits |
| lesson round-16.md:24-25 | "pinned 1.2 MB GGUF" | gate table rejects consumer-health; no perf line | no | mostly within limits |
| SKILL.md:532,535-537 | no (only the filename `stories260K`) | "grades no model quality"; performance/generation unstated | no | partial |
| **SCORECARD.md:588-595** (the row itself) | **no**: "with a pinned GGUF" | **no** | **no** | **outside limits** |
| **SHONEN.md:8** | **no**: "pinned llama.cpp b11755 build and GGUF" | "not … generation or model quality"; performance/timing unstated | **no**: cites "`MODEL_OK`/`matched` exit 0" as an end-to-end domain task | **partial** |
| README.md (top-level) | does not cite C2 at all | — | — | n/a |

Notes on the README rows: the "README round-16 append" in the wave context is `corpus/README.md`. `git show --stat b8e485c` lists `corpus/README.md | 21 +` and no `README.md`.

Counterexamples for D:

1. **MODEL_OK is self-fulfilling.**
   - Receipt `.argv` sets `--alias kama-stories260k`, and `.probes[0].expect` is the same `kama-stories260k` → MODEL_OK exit 0. `.probes[1]` uses `kama-not-this-model` → MODEL_MISMATCH exit 2.
   - So the receipt shows that alias plumbing and the mismatch path work. It shows nothing about model-id reconciliation of a consumer pin, which is the domain's core task (README.md:6 "model-id reconciliation").
   - SHONEN.md:8 lists this pair under "end-to-end domain task executed" and does not say the expected id was chosen by the harness itself. The knowledge entry does say so (:119); the row and SHONEN do not.
   - SHONEN's "a lane-owned control, not registered-consumer reconciliation" partly covers this.
2. **Timing must not travel.**
   - SCORECARD's row and SHONEN omit that the load window is toy-scale. The receipt `.teardown.log_lines` shows load_model at 0.00.004.591 and "model loaded" at 0.00.008.725, and the first `/health` 200 came at `t_ms` 22.
   - CriticC2ToyModel N5 already warned that such timings must not set probe timeouts or expectations for a real MODEL_LOADING window. Without the qualifier, the row reads like SCORECARD.md:26 ("verified against a real llama.cpp runtime") newly re-confirmed at scale.
   - Minor: "loads in about 8 ms" (knowledge:104, corpus/README:217) is 8.7 ms since process start. The load itself spans about 4.1 ms in the log. [INFERENCE] The figure is harmless, but the "server log" it cites was deleted after reduction (SKILL.md:532 "a temporary server log, deleted"). Its only surviving copy is the three receipt `log_lines`, so cite those instead.
3. **Pre-release label.**
   - S038 (SOURCES.md:50) and the lesson gate table record that the b11755 page is labelled "Pre-release".
   - SCORECARD.md:589 ("pinned official llama.cpp b11755 server") and SKILL do not.
   - "Official" is accurate: I checked the official asset bytes above. The release channel status is the unstated limit. Low severity.

Smallest safe correction for D: when L1 appends the SCORECARD capability row, word the "what it can now do" cell within its limits. For example: "on-demand pinned llama.cpp b11755 (CPU, pre-release tag) lifecycle on a non-registered loopback port with a 1.2 MB toy GGUF: capture, probe (self-chosen alias MODEL_OK + mismatch control), proven teardown; no generation/quality/performance/GPU, no live MODEL_LOADING grade, no registered consumer touched". Then append one SHONEN qualifier: "toy 1.2 MB model; expected id is the harness's own alias". This matches the shape CriticScoreDeltas.md:54 proposed.

## E. Naming / duplicate authority — minor

- The id `live-llamacpp-lifecycle` appears only in SCORECARD.md:588. SKILL.md:532 names the row "Live llama.cpp lifecycle". `git grep` of SKILL/SHONEN/corpus README/PROVINCE for the id → no match.
- The round-14 capability has the same pattern, so this is an existing convention, not a new defect.
- Per CriticScoreDeltas.md:55, the canonical `## Capabilities` table (SCORECARD.md:122-128) still holds only `sources-registry`, while round 14's row lives at :457-459. A round-16 row appended in its own section deepens that split. A pointer from the canonical table, or a note there, keeps one authority.

## Impacted axes

- calibration: the C "before" misstatement, and the D row/SHONEN limits.
- operability: the B1 pending pointer and B2 harness pin.
- No safety finding: no server is running; 8080/34113 were not touched by me.

## Limitations

- I did not re-run `tools/kama-llamacpp-live.py`, because the item did not authorize starting llama-server. So the committed-tool ⇔ receipt equivalence (B2) stays unshown.
- GGUF tensor-level facts come from build-wave advice and were not re-derived.
- I read fleet-root AXES.md and listed `../.ufo/reports/round-16/` read-only. Nothing was written outside my Report and /tmp scratch.
- Scratch `/tmp/kama-r16-CriticCapabilityRow/` held the downloaded official tarball and gate outputs; it is removed.

## Installs

None. `curl`/`tar`/`sha256sum` were already present. The release tarball was fetched to /tmp only and is not installed.
