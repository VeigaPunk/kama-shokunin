# RV01ProbeDiff — review of C1 diff (kama-probe.sh, operability)

## Scope
- Diff reviewed: `git diff 99cdb4d6270455494dd27901efe84a0f3b342062 f968fb19bb2a0c2afe271bfe606f11b52d10823f -- tools/kama-probe.sh` (136 lines; `out/RV01ProbeDiff/c1.diff`).
- Revisions measured: base B=`99cdb4d6270455494dd27901efe84a0f3b342062` (probe sha256 `c15ffca8f6b4f07f19fe378d08b8495f2b345dd53face17b686c78ea5cc73238`, matches frozen base); M=`f968fb19bb2a0c2afe271bfe606f11b52d10823f` (probe sha256 `c197912f8b3b5567e3ffd38178cb3a6e87187d7fb13136308c9a461ba8d2ef97`). Also an `oldcurl` variant = M with the two `--max-filesize` flags removed (simulates a curl that ignores the cap, to exercise the `wc -c` re-check).
- Method: both probes extracted with `git show` into scratch; a raw-socket stub (one hostile scenario per loopback port) served 24 scenario cells + 4 router/props variants; each probed with `check --port P --expect X` (JSON and table). `listeners` was NOT used, so the operator router on 127.0.0.1:1234 was never touched. No POST/load/unload/completion anywhere.
- Frozen counter `tools/round90-hostile-answers.py` was NOT run (not my seat). Predicate verdict for C1 is therefore not mine; findings below are held-out and diff-review.
- Tools installed: none. Lane writes: this report and `out/RV01ProbeDiff/` only.

## Commands and outputs (exit codes)
1. `git -C <lane> diff 99cdb… f968… -- tools/kama-probe.sh` → rc 0, 136 lines.
2. `git -C <wt> show <rev>:tools/kama-probe.sh | sha256sum` → base `c15ffca8…` (= frozen), M `c197912f…`.
3. `python3 drive.py base,M,oldcurl` → rc 0, 84 cells (`out/RV01ProbeDiff/matrix.out`, `results.json`, `summary.out`).
4. `python3 jstr_check.py` → rc 0 (`jstr_check.out`): M round-trips bytes 1..127 in C, C.UTF-8, en_US.UTF-8 (127/127 each; the single "bad" line is my own invalid-UTF-8 sample `\xff`, see DEFECT-2). base fails 29/127 per locale.
5. `precheck.sh` under three locales → rc 0 (`precheck.out`).
6. `grep` binary-detection proof → `grep_binary_proof.out`.
7. Dead port: `bash M/tools/kama-probe.sh check --port <free> --expect stories260K.gguf` → rc 2, `DEAD connection-refused` (clean, no set -e abort).

## Findings

### BLOCKER-1 — held-out harm: false green for a wildcard consumer when a router entry id has a control byte
- M filters router entries by id: `probe:727-730` `any(ord(c) < 0x20 or 0x7F <= ord(c) <= 0x9F for c in e["id"])` → `continue`. Base dropped only ids containing `\t\r\n`.
- Entry dropped ⇒ `router_refine` (`probe:782-795`) sees no status ⇒ `any_status=0` ⇒ returns; the verdict stays the id-only `MODEL_OK expected-wildcard`.
- Reproduced (stub `router-ctlid-loading` / `router-ctlid-unl`, one entry `{"id":"bad\u001bid","status":{"value":"loading"|"unloaded"}}`, expect `*`):
  - base table: `MODEL_LOADING | router-loading` (rc 2) and `MODEL_UNLOADED | router-unloaded` (rc 2) — correct.
  - M table: `MODEL_OK | expected-wildcard`, rc 0 — FALSE GREEN. oldcurl identical.
  - Evidence: `results.json` keys `base|M|oldcurl:router-ctlid-*`; `summary.out`.
- Fix direction: do not drop the entry; render its id via the same escaping as `clean()` (or keep the drop only for the one case that must be dropped), so an unreadable router entry can never read as absent.

### DEFECT-2 — regression: a non-UTF-8 byte in the Server header makes `--json` exit 1 (base exit 0)
- M `probe:354` uses `grep -a -i '^server:'`; base used `grep -i` (no `-a`). The grep on this host (`pi-uu-grep 0.2.0`) binary-detects the non-UTF-8 header and prints nothing to stdout (`binary file matches` to stderr, discarded by `2>/dev/null`), so base silently drops `Server:`. M passes the raw bytes through.
- `jstr` (`probe:204-222`) passes bytes ≥0x80 unchanged, `emit_json` (`probe:229-232`) then fails to parse.
- Reproduced (stub `badutf8server`, `Server: llama.cpp\xff\xfe`):
  - base: `--json` rc 0, `MODEL_OK matched`. M: `--json` rc 1, stderr `UnicodeDecodeError ... byte 0xff` + `kama-probe: internal error: generated JSON failed to parse (this is a probe bug)`. oldcurl: rc 1.
  - M table shows the raw bytes: `Server: llama.cpp��`.
  - Evidence: `results.json` `base:badutf8server` vs `M:badutf8server`; `grep_binary_proof.out`.
- Also `jstr_check.out` shows the only jstr failure in M is the raw `\xff` sample (passed through unchanged).
- Fix direction: validate/replace invalid UTF-8 in `strip_ctl` (e.g. `iconv -c` or a python `decode('utf-8','replace')`), and do not let a single hostile header abort `--json`.

### DEFECT-3 — verdict regression: a 401/403 with an oversize body is reclassified FOREIGN_SERVICE
- `classify` checks `case "$F_RC"` (`probe:831`) with the new `63)` branch (`probe:843-847`) before the status case (`probe:870-873`, 401/403 → UNAUTHORIZED_SERVICE).
- Reproduced (stub `big401`, 401 with 5 MiB text/html body): base `UNAUTHORIZED_SERVICE http-401` (rc 2); M `FOREIGN_SERVICE body-too-large` (rc 2); oldcurl same as M.
- Operator action differs: SKILL row 133 (UNAUTHORIZED: "Escalate auth handling to kagi") vs row 175 (FOREIGN_SERVICE: "stop the consumer, name the owner, repoint").
- Fix direction: honour 401/403 before the size branch, or check whether `-w` still reports the status on exit 63.

### DEFECT-4 — pre-existing (base and M identical), not fixed by C1: lone surrogate in JSON breaks listings
- `python3 -c 'print("\ud800")'` → `UnicodeEncodeError`, rc 1 (verified). `served_ids` (`probe:418-421`) and `router_entries` (`probe:727-738`) print the whole list / per entry; the error is swallowed by `|| true` / `2>/dev/null`.
- `surr-mixed` (expect the real model, listing also has `\ud800`): base and M both `MODEL_MISMATCH unresolvable-id` — FALSE RED on a listing that contains the expected model.
- `router-surr-first` (expect `*`, first router entry `\ud800`, second an unloaded model): base, M and oldcurl all `MODEL_OK expected-wildcard`, served `-` — FALSE GREEN (the unloaded entry is lost).
- Not in the frozen predicate, but in the spirit of "cannot break output". Fix: encode lone surrogates as `\udXXX` text (as `clean()` does for controls) before print.

### NOTE-5 — inconsistent C1 handling across fields (terminal-control gap)
- `strip_ctl` (`probe:226`) is `tr -d '\000-\037\177'` (C0 + DEL only). `clean()` (`probe:416`) escapes U+0080–U+009F for ids, but the Server header / Content-Type / curl error path does not.
- Reproduced (stub `c1server`, `Server: llama.cpp\xc2\x9b31m\xe2\x80\xaeEVIL`): M table contains U+009B and U+202E raw (checked in `results.json`). The frozen rule names only U+0000–U+001F/U+007F for the header, so the predicate is met; the stated intent ("ESC drives the operator's terminal") is not fully met.

### NOTE-6 — bidi and line-separator characters survive in ids (table output)
- `u2028` cell: M table shows U+2028 and U+202E raw in served ids (`clean()` keeps them). `--json` is safe (json.dumps escapes non-ASCII). Held-out per the claim; report only.

### NOTE-7 — oversize root page loses its evidence
- `root-big` (404 on /v1/models, 5 MiB `text/html` on `/`): base evidence `200|text/html @ /`; M `err-63 @ /`. Verdict unchanged (FOREIGN html-non-model). `probe_short` (`probe:373-379`) is the source; the operator sees a bare error code with no reason.

### NOTE-8 — item (5): is FOREIGN_SERVICE body-too-large defensible?
- Defensible as "not verifiable, never MODEL_OK". Weak point: SKILL row 175 gives FOREIGN_SERVICE the operator action "stop the consumer, name the owner, repoint", which is wrong for a genuine >4 MiB model listing. Recommend a SKILL row for body-too-large saying "identity not established; the cap is the cause; do not repoint".
- Boundary verified: exact 4194304 bytes → `MODEL_OK matched` (CL and close-delimited); 4194305 → `FOREIGN_SERVICE body-too-large` (rc 2), both M and oldcurl.
- Oversize `/props` (`props-big`): base `MODEL_OK router-unloaded-autoload` → M `MODEL_UNLOADED router-unloaded` (rc 2, drift). Matches the stated design, but it is a drift for a real router with a >4 MiB `/props`; low likelihood, unmeasured.

### NOTE-9 — header flood: bounded by curl, not by the probe (not reproduced as a defect)
- 128 MiB of headers in 64 KiB lines: curl 8.23 aborts with `rc=56 Too large response headers: 327793 > 307200` → NOT_HTTP connection-reset, identical base and M. No unbounded-header hazard reproduced.

## set -euo pipefail hazards (item 1) — none reproduced
- `wc -c < "$FBODY"` on a missing body: the `[ -f ]` guard covers fetch; `router_autoload` `props-empty` (200 with empty body): curl creates the file, no stderr, verdict same base/M.
- `strip_ctl` inside `|| true` pipelines: no abort in 84 cells, including NUL-free C0/DEL/C1 inputs.
- `[ "$F_RC" -eq 63 ] && : > "$FBODY"` (`probe:347`): not the last command of `fetch` (the trailing `if` returns 0); oldcurl re-check path yields rc 63 correctly for >cap close-delimited bodies.

## Item (2) jstr and pre-check
- Per-byte `json.loads` of `jstr` output: M 127/127 in C, C.UTF-8, en_US.UTF-8 (`jstr_check.out`). Base: 105/134 (29 control bytes unescaped).
- Pre-check `[[ $s == *[$'\x01'-$'\x1f'$'\x7f']* ]]` (`probe:214`): fires exactly on 0x01–0x1f and 0x7f; never on ASCII printable, `é`, U+0085, U+2028, U+202E, U+009B, emoji (`precheck.out`). Cost ≈5 µs per call in all three locales (20k calls ≈100 ms). Correct, no false fires.
- Only jstr gap: bytes ≥0x80 that are not valid UTF-8 (DEFECT-2).

## Item (3) clean() and router filters
- `clean()` escapes C0/DEL/U+0080–U+009F (verified in `u2028`, `ctlid`). U+2028/U+202E kept (NOTE-6). Lone surrogates crash the whole listing (DEFECT-4). Non-UTF-8 ids: `json.load` fails, so no ids are printed (fails closed to `-`).
- Router `status.value` filter maps controls to `?` → `router-?` reason; verdict unchanged (`router-esc`: MODEL_UNLOADED both).

## Item (4) listener text reaching output
- C_EVIDENCE: `base` built from `F_CODE` (numeric, from `-w`), `F_CT`/`F_SERVER`/`F_ERRMSG` (C0/DEL stripped; C1 and non-UTF-8 not), `probe_short` (C0/DEL stripped). Unsanitised remainders: NOTE-5, DEFECT-2.
- C_SERVED: `served_ids` via `clean()`; surrogates crash (DEFECT-4); U+2028/U+202E kept (NOTE-6).
- C_REASON: constants, plus `router_refine` `router-$val` where `val` only had C0/DEL/C1 filtered (non-control Unicode passes).
- `F_SIZE`, `F_CODE`: numeric from curl `-w`. JSON built by `jstr`, tables by `print_table`.

## Deliverables (out dir: `.ufo/waves/round-90/w1/out/RV01ProbeDiff/`)
- `c1.diff`, `results.json` (84 cells, base/M/oldcurl, JSON and table outputs and stderr), `matrix.out`, `summary.out`, `jstr_check.out`, `precheck.out`, `grep_binary_proof.out`.
- Harness: `stub.py`, `drive.py`, `summarise.py`, `jstr_run.sh`, `jstr_check.py`, `precheck.sh`, `jstr_M.sh`, `jstr_base.sh`.
- Scratch removed; no stub processes left (one stray stub from my manual test killed by pid).

VERDICT: falsified — held-out harm reproduced: a router entry whose id carries a control byte is dropped, turning a loading/unloaded router into `MODEL_OK` for wildcard consumers (base correct), and a non-UTF-8 Server header turns `--json` exit 0 into exit 1; the 4 MiB cap, C0/DEL escaping and the 13 stub cells' hostile cases do hold on these stubs.
