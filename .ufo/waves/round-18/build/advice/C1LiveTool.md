VERDICT: confirm — the scoped tool-side v3 receipt, tcp6 ownership parser, and no-loading-observation classification are implemented; requested clone checks passed.

## Axes
- **Operability:** v3 receipt verdicts, exact argv evidence, internal-fault receipts, teardown/log cleanup, and tcp6 child ownership.
- **Calibration:** zero observed `/v1/models` loading 503s are explicitly not-evaluated rather than treated as a subject failure.

## Delivered artifacts
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/build/out/KamaR18.C1LiveTool-2/kama-llamacpp-live.py` — SHA-256 `cdcb1bc5c2e4649a8b4dce0578457b9e77c1e376e916624e9c50eda211b7748a`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/build/out/KamaR18.C1LiveTool-2/kama-llamacpp-live.py.diff` — SHA-256 `ae39ee0fd815c01e2c8ce5cf641680c204ab723c1bc340778df712972574fd6e`
- This report: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/build/advice/C1LiveTool.md`

## Behavior and implementation evidence
- The module declares `kama-llamacpp-live/v3`, tri-state `passed` plus `evaluated`, top-level outcomes, and exit codes 0/1/2. `_check` and `_outcome_exit` implement the mapping; only the loading-envelope check may be null, with `observed.not_evaluated_reason = "no-loading-503-observed"`. Evidence: delivered tool `:16-24,857-891,1485-1509`.
- Preflight `SetupError`s now emit a minimal v3 `setup-error` receipt; model-digest mismatch maps to exit 2 under the v3 0/1/2 contract (previously exit 3). Evidence: `:1131-1219,1393-1398`.
- `loading_observed`, `loading_503`, and `loading_503_bodies` now represent only proven `/v1/models` 503 responses. `/health` 503 responses remain in `transitions` but do not become loading observations. Each `/v1/models` transition is retained with the existing response-body and truncation fields. Evidence: `:580-604`; selftest exercises literal procfs-format rows and live `/proc/net/tcp6` rows.
- `_listen_inodes` reverses each 32-bit tcp6 word before testing native `::1` or IPv4-mapped `127.0.0.0/8`; wildcard addresses remain fail-closed. Evidence: `:311-367`. `--selftest` binds loopback-only listeners to `::1` and `::ffff:127.0.0.1` and checks their live procfs inodes: output was `selftest: ok; closed tcp6 listeners ::1:42019, ::ffff:127.0.0.1:37183`.
- Internal `BaseException` faults are converted to `setup_error`/`internal_fault` `internal:<ExcType>` and exit 2 across the run, teardown, cleanup, timestamp, emit, and signal-restoration paths; handler restoration attempts each saved handler. A separate log unlink retry runs after teardown. Evidence: `:888-891,1391-1411,1423-1448,1523-1533,1536-1584`.
- Receipt argv is the exact list passed to `Popen`; `model.arg` retains the original model argument needed to re-derive it, alongside the existing server realpath, alias, port, context, and threads fields. No launch flags were added. The model digest comparison remains before launch, `--host 127.0.0.1` is unchanged, child env remains allowlisted, and the existing process-group teardown / pdeathsig path remains in use. Evidence: `:1157-1177,1191-1258,1260-1293`.
- Python return-code documentation now uses the pinned Python 3.14 anchor: `https://docs.python.org/3.14/library/subprocess.html#subprocess.Popen.returncode` (`:59-61`).

## Commands and retained results
Commands were run only in `/tmp/kama-r18-KamaR18.C1LiveTool-2` or for the required artifact delivery. No lane gate, measurement script, fake server, or real llama-server was run.

1. `git clone -q /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/kama-r18-KamaR18.C1LiveTool-2 && git -C /tmp/kama-r18-KamaR18.C1LiveTool-2 switch -q -c seat/KamaR18.C1LiveTool-2` — **exit 0**.
2. `python3 -m py_compile tools/kama-llamacpp-live.py` — **exit 0** (run twice; final run after all edits).
3. `python3 tools/kama-llamacpp-live.py --selftest` — **exit 0**, output above. The run checked synthetic literal `/proc/net/tcp6` rows, then parsed actual live rows for both listeners and verified each inode through `_listen_inodes`.
4. `ss -H -ltnp '( sport = :42019 or sport = :37183 )'` — **exit 0**, no matching rows after selftest closed both sockets. A separate unfiltered `ss -H -ltnp` completed with exit 0 and showed other already-running listeners; those were not used by this work.
5. Artifact delivery copied the clone file and generated the required `diff -u` against `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/frozen/tools_kama-llamacpp-live.py`. Overall delivery command exit was **0**; `diff` returned **1** as expected for changed content. Hashes are listed above.
6. LSP availability was checked via `grep` on `xd://lsp`; the tool returned `No such tool: xd://lsp`. No LSP definitions/references/diagnostics were available. No tools were installed or updated.

## Risks, limitations, blockers
- No live llama-server/fake-server lifecycle was exercised, so server-version-specific behavior and full receipt/gate interoperability remain unmeasured; L1 owns the integration gate.
- No observed loading 503 cannot distinguish an absent server response from a scheduling/observation gap; the receipt intentionally marks that check not-evaluated.
- Listener ownership depends on Linux procfs visibility. Missing/unreadable or transiently incomplete `/proc/net/tcp{,6}` data remains unproven and fails closed. Persistent filesystem denial can still prevent temp-log unlink despite the independent retry; in that case the tool records an internal fault and exits 2.
- The tool cannot prove that a descendant which escaped the child's process group has terminated. If child liveness cannot be established by `poll()`, it deliberately does not issue `killpg`, because signaling an unproven/dead process group could hit a reused group ID.
- Receipt publication cannot be guaranteed when the requested destination/stdout is persistently unwritable; the tool returns 2 after recording the failure as far as possible.
- No blockers identified; no installs.