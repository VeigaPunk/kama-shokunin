VERDICT: partial - no lane or fleet commit is unresolved; 25 unresolved 40-hex tokens (59 occurrences, all corpus/**): 24 real upstream commits, 1 non-git hex
# AuditLaneDocHashes, round 21 (findings only; lane not modified)

Scope: SCORECARD.md, LOG.md, SKILL.md, corpus/**/*.md = 54 files at a29bb84 (HEAD, byte-identical to working tree). Token = 40 hex bounded by non-alphanumerics; 88 64-hex runs excluded. 218 occurrences, 78 unique: 43 resolve in lane, 10 fleet-only, 25 unresolved. LOG 19, SCORECARD 18, SKILL 1 occurrences, all resolved.
Artifacts: .ufo/waves/round-21/build/out/AuditLaneDocHashes-6/ (scan_doc_hashes.py, guess_unresolved.py, verify_upstream.py, occurrences.tsv, unique-tokens.tsv, candidates.tsv, context.txt, upstream-check.tsv, followup-probes.txt).

Commands and exits (all executed):
- `python3 .../scan_doc_hashes.py` -> exit 0 (per token `git --no-replace-objects -C <repo> cat-file -e <tok>`; codes seen: 0 present, 1 absent)
- `python3 .../guess_unresolved.py` -> exit 0 (12,576 objects; best local match per unresolved token: common prefix <=4 chars, 29-31 of 40 differ)
- `python3 .../verify_upstream.py` -> exit 0 (27 curl HEAD probes; 3 GitHub API calls returned HTTP 403 rate limit)
- `git cat-file -e 704366d7...` (lane) exit 1; `a29bb84...` (lane) exit 0; `dff1730...` lane exit 1 / fleet exit 0
- `git ls-remote --tags` llama.cpp exit 0 (8119 lines), linux exit 0 (1906 lines); `git ls-remote <llama.cpp> refs/pull/18001/head` exit 0
- curl HEAD probes (ollama, stryker) exit 0; details in followup-probes.txt
Tools installed or updated: none (git 2.56.0, curl, python3 pre-existing). Scratch dir removed (`ls -d` exit 2).

## Unresolved tokens: file:line and guess
KEEP = the token is a real upstream object (HTTP 200 or ls-remote); lane and fleet clones simply lack upstream history, so no local correction exists.
1. 16d1c93b3d28227a40f0b4c5559f12dedbb64b26 | SOURCES.md:18 | KEEP: sgl-project/sglang docs/docs/basic_usage/native_api.mdx at commit, 200
2. 370c9b6739e38df6542ca906b1848434e71ab551 | SOURCES.md:21 | KEEP: ollama/ollama docs/api/introduction.mdx, 200
3. 410443d27be8bc911af86a826beb13c25d46e4dd | SOURCES.md:30 | KEEP: prometheus/docs docs/practices/naming.md, 200
4. 499bc8821c6b12b4e53c5bffcb21ec206f212d81 | SOURCES.md:51 | KEEP: HF ggml-org/models-moved revision, tinyllamas/stories260K.gguf resolves, 200
5. 51ace48387ad8b86e6c81988de4bbbe6a014a544 | SOURCES.md:19 | KEEP: sgl-project/sglang docs/docs/references/production_metrics.mdx, 200
6. 614bec6fd16670852e94c8cc03a002f6bf05db09 | SOURCES.md:57 | KEEP: hcoles/pitest-site commit, 200 (owner inferred from "pitest-site gh-pages" [INFERENCE])
7. 678913a0f029394ad1f4ee64d1439421e9ea56ef | SOURCES.md:36 (cols 76, 248); lessons/round-10.md:84 | KEEP: sgl-project/sglang docs/docs/advanced_features/sgl_model_gateway.mdx, 200
8. 6af560d55df03ad92116e3c0a697779584477e85 | SOURCES.md:26 | KEEP: ggml-org/ggml docs/gguf.md, 200
9. 6d02a43a75cd3364b3c230e9070f1413e60f0d02 | SOURCES.md:25 | KEEP hash, FIX PATH: commit 200; cited docs/import.md is 404 at it, docs/import.mdx is 200. Guess: `docs/import.mdx`
10. 704366d76f8748cf9ad3df62a464bfcc8d1ae6ad | 21 occ: SOURCES.md:47,48,49,50,54,55,59,66,68,71,72; knowledge/llamacpp-loading-lifecycle.md:1; lessons/round-16-verifier-spotcheck.md:127; lessons/round-16.md:188; lessons/round-17.md:60,62; lessons/round-18.md:41,50,54; lessons/round-20.md:52,53 | KEEP: ggml-org/llama.cpp commit 200; refs/tags/b11755 = this commit
11. 8d2cff8140eb2c5f6a7b28948c0944d11898d9d2 | SOURCES.md:35 (cols 90, 272); lessons/round-10.md:83 | KEEP: vllm-project/vllm examples/observability/prometheus_grafana/README.md, 200
12. 8d3ae59288f1e7d58d76558a6ee96d533bc5019f | SOURCES.md:60 | KEEP: torvalds/linux net/ipv6/tcp_ipv6.c, 200; refs/tags/v7.2^{} peels to this commit
13. 96f460f9c1e2ca43d0adc1c682b832525a2c0ea3 | SOURCES.md:51 (col 363) | KEEP: HF file revision of stories260K.gguf, 200
14. a56f265c77c1cc811b10f0bae73ec1b0083d52a9 | SOURCES.md:74; lessons/round-20.md:55 | KEEP, NAME REPO: row S062 names no repo. Commit and docs/mutant-states-and-metrics.md exist only in stryker-mutator/mutation-testing-elements (200, 200); stryker-js and stryker-mutator.github.io give 404
15. ad1b88ca0d37a2171efba1c04f1a3531c78f1b52 | SOURCES.md:27 | KEEP: ggml-org/llama.cpp tools/quantize/README.md, 200
16. aec7bdb42b33b3177ae232ba36d08535eeaae1fe | SOURCES.md:38 | KEEP: ggml-org/llama.cpp commit 200; refs/pull/18001/head = this commit
17. bdf8886ad386685b4d089c8e66725b9280533591 | SOURCES.md:20 | KEEP: sgl-project/sglang docs/docs/advanced_features/quantization.mdx, 200
18. c0fd78626405c6d9b934efef0ec7291fcc20e3d6 | SOURCES.md:13; knowledge/runtime-health-surface-matrix.md:54; knowledge/served-identity-crosswalk.md:1,80; lessons/round-11-verifier-spotcheck.md:156; lessons/round-11.md:67 | KEEP: ggml-org/llama.cpp tools/server/README.md, 200
19. c1737589973d5cefd676ef16eb43835663540035 | SOURCES.md:22; knowledge/served-identity-crosswalk.md:81 | KEEP: ollama/ollama docs/api/openai-compatibility.mdx, 200
20. c396f25f2f8112d7761097b7b0217808dc65ddd4 | SOURCES.md:28; knowledge/served-identity-crosswalk.md:79 | KEEP: openai/openai-openapi commit, 200 (owner inferred [INFERENCE]; "metadata version 2.3.0" not checked)
21. d4ee7fe7a98b3012f64309e18dd425e565069a01 | SOURCES.md:17 | KEEP: vllm-project/vllm docs/features/quantization/README.md, 200 (repo inferred from path [INFERENCE])
22. da8e2a54b919557b816b1c2beb432ccb766f7ce0 | SOURCES.md:70; lessons/round-20.md:51 | KEEP: ggml-org/ggml docs/gguf.md (raw URL in row), 200
23. efb50993780079460b0cbed1363e2166a2de1d9f | lessons/round-1-critic.md:106:50 | NOT A GIT OBJECT: component of a Hyprland IPC socket path `/run/user/1000/hypr/<hex>_<ts>_<pid>/.socket2.sock` in a pasted process line. Guess: none; exempt from object-existence rules [INFERENCE on naming]
24. efe43c5561047d8baf8c862730b2151249d51fd5 | SOURCES.md:37 | KEEP: ollama/ollama commit, 200 (repo inferred from "Ollama API docs source commit" [INFERENCE])
25. f7fe5adfa5fb6e727c12d2403a48f5e4e9dd2fc6 | SOURCES.md:75; lessons/round-20.md:56 | KEEP: hcoles/pitest pitest/src/main/java/org/pitest/mutationtest/DetectionStatus.java, 200

## Findings
- F1: no lane-internal or fleet commit is unresolved; all 43+10 resolving tokens are present.
- F2 (path defect): SOURCES.md:25 cites `docs/import.md` at 6d02a43a; the file is `docs/import.mdx` there.
- F3 (ambiguity): SOURCES.md:74 and lessons/round-20.md:55 cite a56f265c without a repo; the commit lives only in stryker-mutator/mutation-testing-elements.
- F4: lessons/round-1-critic.md:106 hex is not a git identifier.
- F5 [INFERENCE, for C1]: a local-only `cat-file -e` rule flags all 25 here, 24 of them real upstream commits. Check the r20 `unresolved-full-hash` for an external citation before counting it.

## Corrections and limits
- My interim reading that linux `refs/tags/v7.2` was lightweight was wrong: `git ls-remote --tags` shows `refs/tags/v7.2^{}` = 8d3ae592, so row 12 is correct. Pattern queries omit peel lines.
- Unchecked: dates, metadata claims, line-number citations inside upstream files, HF file sizes and digests.
