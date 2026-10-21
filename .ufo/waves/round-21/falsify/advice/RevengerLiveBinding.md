VERDICT: partial - receipt bytes match b76727f (tool, probe, upstream spans, manifest, timing agree), but no receipt field names a revision and the official gate never checks tool/probe identity
Attacked: that live-receipt.json binds to b76727f (tool/probe/source_binding identity, revision attribution, run residue). Read-only: git reads on a scratch clone and the lane object store; no lane writes.
Probe: falsify/out/RevengerLiveBinding/binding_probe.py -> binding_probe.out.txt (exit 0; 50 OK, 0 FAIL). First run had one under-listed expectation (checks[].observed.fields.build_info); corrected, re-run exit 0.

## 1. Binding fields (receipt sha256 e1fc04ab..., equal to committed blob at a6617149)
- tool: lane tools/kama-llamacpp-live.py, sha256 e4cc6d8885c7755717157fd23bfce3be39288990a9cf5985cb1c56a4b11cf68f = sha256(tool@b76727f). Producer hashes its own file at setup (producer:1417).
- probe: lane tools/kama-probe.sh, sha256 36b64978ee3a3aa29e1b73f04ca5c7ad04a9aee880e7032abfd894fa7b3a29d3 = sha256(probe@b76727f) (producer:1384).
- source_binding: 5 spans at llama.cpp 704366d76f8748cf9ad3df62a464bfcc8d1ae6ad (upstream, not the lane). Producer constants source_bindings() == receipt field (eval, True). span_sha256 re-derives 5/5.
- Upstream, fetched 2026-10-21 with curl (rc 0 x3) from raw.githubusercontent.com/ggml-org/llama.cpp/704366d76.../tools/server/: server-context.cpp dd1de0f2..., server-http.cpp 24ede172..., server.cpp 21439622... equal the entries' file_sha256; bytes at each cited line range equal span_text 5/5.
- server.sha256 b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804 = sha256 of ~/.local/opt/llama-b11755/llama-server (sha256sum rc 0).

## 2. Does any field name the producer revision? No.
- Revision-like key paths: captures.props.fields.build_info and checks[].observed.fields.build_info (server self-report "b11755-704366d76"); source_binding[].commit (llama.cpp). No lane commit, no measured_commit.
- Schema kama-llamacpp-live/v3 is unchanged since round 18 (producer:49; SOURCES S055), so it does not separate producers. install_links and the tool block are both optional to the gate.
- Blob windows (rev-list from a6617149; linear, 0 merges): tool e4cc... is carried by exactly {a6617149, b76727f, 4e75d9e, 1471344b}; probe 36b6... by 41 commits 726f737a..a6617149. The four tool-carrying commits hold identical producer code, so the receipt cannot choose among them.

## 3. Does it match b76727f? Consistent by content and manifest; not authenticated by the receipt.
- commands.json (in a6617149; sha256 e550d98d...): measured_commit b76727f31e522763ce24e43d6ec86d21b507a11f; recipe_sha256 9d68997d... = sha256(recipe.json@b76727f). It hashes per-command stdout/stderr only, never the receipt file.
- Timeline: b76727f author 2026-10-21T08:13:58-03:00; receipt started 11:14:09.332Z (08:14:09 -03:00), ended 11:14:09.482Z; a6617149 08:14:24-03:00. The run sits in that gap. [INFERENCE: HEAD was b76727f during the run; run.py:25-27 checks for a clean tree only at start.]
- Receipt absent from b76727f tree (git cat-file -e rc 128). a6617149 vs b76727f: 86 files, all added (+3628 -0), none outside .ufo/ (git diff rc 0).

## 4. Gate binding strength: tests/llamacpp-live/check-receipt.py@b76727f, official argv (recipe.json:140-154). Each rc is the gate exit.
  as written                                    rc 0 VALID
  tool.sha256 = 7x64                            rc 0 VALID        unpinned
  tool block deleted                            rc 0 VALID        block optional (gate:525-530)
  tool.path nonexistent                         rc 0 VALID        path never opened
  probe.sha256 = 7x64                           rc 0 VALID        unpinned
  install_links + digest removed                rc 1 INVALID      --require-install-links
  source_binding[0].row = S042                  rc 1 INVALID      row pinned to null (gate:94-112)
  source_binding[2].file_sha256 = 7x64          rc 1 INVALID
  tool pin from git + tool.sha256 = 7x64        rc 1 INVALID
  tool + probe pins from git, as written        rc 0 VALID
  server.sha256 = 7x64, no pins (eval rc 1)     INVALID           server cross-checked against install_tree
- Tool/probe pins exist only as flags (gate:287-289, 513-538); the recipe passes neither. Model, install-tree and install-links pins are recipe constants, not copies of the receipt.

## 5. source_binding traceability (stale link, not a byte error)
- row is null for health_ready and three teardown spans, though SOURCES S042 (5288-5299) and S043 (519-523, 529-534, 575-576, 590) quote the same file digests (probe output). Producer:963-965 says null means "still owes a row"; gate pins null. Only loading_envelope_graded is linked (S036).

## 6. Residue (asked directly)
- pgrep -a llama-server: rc 1 before and after the probe. 127.0.0.1:45311 refused.
- ls -la /tmp/kama-llamacpp-live-*: rc 0, six files, all dated 2026-10-20 -03:00 (12:46 to 20:29), before the run. None names port 45311 or 0eeenn7. The run's log /tmp/kama-llamacpp-live-0eeenn7_.log is absent (ls rc 2); producer unlinks it (producer:894, 1690). The receipt keeps its three teardown log lines.
- Seen, not llama-server, not mine, untouched: install-links-grid.py (pid 3043525); fault-controls.py (pids 3102018, 3108791).

## 7. Limits and not checked
- tool.sha256 is the setup-time hash of the file on disk, not of the running image. No post-run clean check exists.
- kama-probe.sh --port mode does not read the registry (read_registry only in the non-port branch, probe:841-857), so the registry is not a receipt input.
- Release link unverified: build_info is self-reported; S038 records asset digest 753bfa73...; tarball not on this host.
- Gate and grid code identity is recorded nowhere except measured_commit. Gate selftest not run (out of scope).
- Installs/updates: none. Processes started: none persistent. Scratch /tmp/kama-r21-RevengerLiveBinding removed.

Advice (L1 decides): record the receipt sha256 in commands.json; have the recipe pass --expect-tool-sha256 and --expect-probe-sha256 from git; hash the gate into the manifest; re-link S042/S043 rows.
