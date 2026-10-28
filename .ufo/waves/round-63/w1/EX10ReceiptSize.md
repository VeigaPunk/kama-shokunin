# EX10ReceiptSize — v2 completion receipt size / leak / wall-time measurement

Tip under test 03a6a1d850902a66a13dfad33f89cf3a8b759a09 (v2), comparison base 7ee8cbdf160f8c945954e4737e7a2f797e3b2987 (v1).
Both checked out as `git clone --shared` + `git checkout` in scratch (`$S/clone` = tip, `$S/base` = base); tools run from those checkouts, `--work`/`--out` in scratch, no `--hold-dir` unless stated. No tool installs. Advisory only; no verdict.
Evidence: `.ufo/waves/round-63/w1/out/EX10ReceiptSize/` (r-{base,clone}-1.json = plain runs, m-{base,clone}-hold-1.json = hold runs, m.py = timing driver, sha256.txt).

## Before / after table (plain run, 3 timed repeats each, driver m.py, `--nonce` given)

| | base v1 (7ee8cbd) | tip v2 (03a6a1d) | delta |
|---|---|---|---|
| schema | kama-completion-live/v1 | kama-completion-live/v2 | |
| receipt bytes (3 runs) | 9285 / 9283 / 9284 (earlier, no nonce: 9278, 9280) | 12974 / 12976 / 12962 (earlier, no nonce: 12966, 12969) | ≈ +3.69 kB (+39.7%) |
| checks (all passed) | 16/16 | 22/22 | +6 net |
| wall time (3 runs) | 0.192 / 0.174 / 0.179 s | 0.175 / 0.177 / 0.178 s | none measurable |
| captures | 6 | 7 (+`tokenize`) | +1 |
| verdict / rc / stdout / stderr | REQUEST_OK / 0 / 0 B / 0 B | REQUEST_OK / 0 / 0 B / 0 B | same |
| hold-mode run (`--hold-dir`, released by driver ~0.2 s after ready.json) | 9475 B, 17 checks, 0.427 s | 13165 B, 23 checks, 0.422 s | +3690 B, +6 checks |

Hold mode adds exactly one check (`hold_released`) and ≈190 B to both versions; the receipt is written only to `--out` (nothing on stdout).
Wall time is dominated by llama-server start on the 260K model (~0.17 s); v2's extra requests (/tokenize) and extra checks are inside timing noise.

Note on check count: the freeze text says "nine added checks"; the receipt diff is 16 → 22 names, +6 net. Names added: `completion_choice_shape`, `completion_headers`, `completion_id_created`, `completion_prompt_tokens`, `completion_request_bound`, `completion_untruncated`. No v1 check removed (the 16 v1 names are all present in v2). So the net count is 6 added to the receipt `checks` map; if "nine" counts something else (e.g. sub-checks inside a check) I did not find it in the receipt. [observed: the 6-name diff; the nine is a claim in freeze.txt, not reproduced in receipt]

## Key sets
Top level, identical in v1 and v2 (18 keys): alias, argv, at, captures, checks, child_pid, hold, model, nonce, port, request, schema, server, server_log, teardown, tool, verdict.

Per capture:
- v1 (6 captures: bad_request, completion, completion2, health, models, props): `body, body_sha256, body_truncated, error, status` (5 keys).
- v2 (7 captures: the same 6 + `tokenize`):
  - health, models, props: `body, body_bytes, body_sha256, body_truncated, error, headers, status` (7 keys).
  - bad_request, completion, completion2, tokenize: those 7 + `request_body, request_sha256` (9 keys).
  - `headers` is a dict of 5 keys on every capture: access-control-allow-origin, connection, content-length, content-type, server.

Size contribution (tip, bytes of json per capture): bad_request 662, completion 1248, completion2 1247, health 356, models 1165, props 2615, tokenize 547 (sum 7940; v1 captures sum 5607 → +2333 B of the +3688 B total; checks block 2048 → 3052 B, +1004 B; remainder ≈ +350 B of per-capture rewrapping/fixed fields).

## Leak check (paths / user name)
Absolute paths in the tip receipt (set, plain run): 
- `/home/vgpnk/.local/opt/llama-b11755/llama-server` (server.path, argv[0])
- `/home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf` (model.path, argv[2])
- `<--work>/server.log` (server_log; here `/fast/scratch/hyaku/kama-r63/w/EX10ReceiptSize/work-clone-1/server.log`)
- hold run only: `hold.dir` = the `--hold-dir` path as given.

Leaf fields containing the user name `vgpnk`: exactly 5 in both versions: argv[0], argv[2], model.path, server.path, and `captures.props.body` (the server's own /props reply echoes the model path). All five are the model/server paths; no other `/home/` string. `hyaku` appears once (server_log, because I chose the scratch path) and twice in hold runs (+hold.dir): these come from caller-supplied `--work`/`--hold-dir`, not from the tool's own state. No `/tmp`, `/root` paths. v2 adds no new path field and no new leak vs v1 (identical leak set; v1 and v2 counts both 5/1).
Caveat: `--work` and `--hold-dir` are echoed verbatim, so a caller whose scratch path contains a user name or secret directory name leaks it into the receipt; the tool does not scrub them.

## Environment variables
- The receipt contains no environment block: no key containing `env`/`environ` other than the check name `completion_envelope`; no `NAME=value` pattern for PATH, HOME, USER, LOGNAME, SHELL, LANG, TMPDIR, XDG_*, HOSTNAME.
- Substring test of every environment value (len ≥ 6) of my shell against the raw receipt text: only HOME, PWD, XDG_CACHE_HOME values match, and in each case as the leading path of the model/server/work paths (`/home/vgpnk`, `/home/vgpnk/.cache`, my scratch cwd) — all are path-prefix coincidences; non-path env values matched: none (checked plain and hold runs, both versions). (The bare name `TERM` matches as a substring of another word; no `TERM=`.)
- Source note: the tool filters the child server env to PATH, HOME, LANG, LC_ALL, LD_LIBRARY_PATH, LLAMA_ARG_THREADS, XDG_CACHE_HOME (tools/kama-completion-live.py:278-280) and never writes that dict into the receipt (receipt['argv'] is the only launch record).
- Conclusion: confirmed no environment variables in the v2 receipt.

## Other observations
- v2 response headers captured contain only the five llama.cpp fields listed above (no cookies/auth/host fields).
- `completion.request_body` is the exact request bytes (includes `timings_per_token:false`), `request_sha256` binds them; `created` and `id` are server-random so two runs' completion bodies differ by design (completion2's size differs by 3 B from completion: 618 vs 621).
- `server_log` is a path only; the log content is not embedded (receipt does not exceed ~13 kB).
- Run-to-run size jitter at tip: 12962–12976 B (±7 B), from `at`/ports/`created`/`id`/timings digits.

Counter-free tally: v1 9285 B/16 checks/0.18 s → v2 12974 B/22 checks/0.18 s; leak set unchanged (5 vgpnk fields = model/server paths); env vars in receipt: 0.
