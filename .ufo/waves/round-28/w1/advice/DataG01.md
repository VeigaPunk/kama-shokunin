# DataG01 — C1 request-field rows (round 28, wave 1)

Seat: KamaR28.DataG01-2. Live run on port 48201 only.
Binary `~/.local/opt/llama-b11755/llama-server`, model `~/.cache/kama-shokunin/models/stories260K.gguf`,
argv exactly `-m <model> --host 127.0.0.1 --port 48201`, under `timeout`, process group killed,
`ss -ltnp` confirms 48201 closed. No tool installed; no repo file written in the lane checkout.

## Output

- `out/DataG01/rows.json` — 4 row drafts, `no_rows: []`.
- `out/DataG01/reject_{sse_ping_interval_-2,n_predict_-2,n_indent_-1,n_keep_-2}.json` — raw 400 bodies cited by the rows.
- `out/DataG01/base.json` (counter's base body), `base_no_n_predict.json` (field-omitted default),
  `probe_*.json` (identity / absent-key probes), `server-schema.cpp.raw` (own fetch), `server.log`, `server2.log`.
- Scratch: `/fast/scratch/hyaku/kama-r28/w1/DataG01/{probe.py,probe2.py}`.

## Source pins verified

- Snapshot `sources/llama.cpp-704366d/server-schema.cpp` sha256 = `1f9d7b73...4050`, as pinned.
- Own `curl` of `https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp`
  at 2026-10-23T08:33:24Z → same sha256; bytes identical to the snapshot.
- Mechanism read at the pin: `server-schema.h` `set_limits` clamps via `std::max(min, std::min(max, ...))`,
  `set_hard_limits` sets `is_hard_limit = true`; `field_num<T>::eval` (server-schema.cpp:532-547) throws
  `"Value must be between " + std::to_string(min) + " <= value <= " + std::to_string(max) + ", but got " + std::to_string(tmp)`,
  wrapped by `handle_with_catch` (server-schema.cpp:519-525) as `Field '<name>': <e.what()>`.

## Live results (all from port 48201)

| probe | body extra | status | message / generation_settings |
|---|---|---|---|
| base (counter body) | — | 200 | n_predict 1, max_tokens 1, n_keep 0, n_discard 0, n_indent absent, sse_ping_interval absent |
| sse_ping_interval | -2 | 400 | `Field 'sse_ping_interval': Value must be between -1 <= value <= 2147483647, but got -2` |
| n_predict | -2 (replaces 1) | 400 | `Field 'n_predict': Value must be between -1 <= value <= 2147483647, but got -2` |
| n_indent | -1 | 400 | `Field 'n_indent': Value must be between 0 <= value <= 2147483647, but got -1` |
| n_keep | -2 | 400 | `Field 'n_keep': Value must be between -1 <= value <= 2147483647, but got -2` |
| n_keep | 100000 | 200 | n_keep 100000 (identity) |
| n_keep | 2147483647 | 200 | n_keep 2147483647 (identity) |
| n_keep | -1 | 200 | n_keep -1 (identity) |
| n_predict | 0 | 200 | n_predict 0 (identity) |
| n_predict | 100000 | 200 | n_predict 100000 (identity) |
| n_indent | 3 | 200 | n_indent absent from generation_settings |
| sse_ping_interval | 5 | 200 | sse_ping_interval absent from generation_settings |
| prompt only (no n_predict) | — | 200 | n_predict -1 (field-omitted default), n_keep 0, predicted_n 2043 |

`report_issue` check: no tool output contradicted its documented behavior.

## Why reject is the only countable outcome per field

- `n_indent` and `sse_ping_interval` have no `generation_settings` key at the pin
  (`task_params::to_json`, server-task.cpp:30-143, has no such entries) and the live 200 confirmed
  absence, so an `effective` row is structurally impossible for them.
- `n_predict` and `n_keep` are stored verbatim inside the hard bounds: measured identity at 0, -1,
  100000, 2147483647; the omitted default for n_predict is -1. An `effective` row would have to be
  neither the sent value nor the default, so none exists for these two either.
- Therefore each field gets exactly one reject row, one per declaring line (distinct lines 40/44/50/54),
  which also satisfies the counter's duplicate-field and duplicate-line controls.

## Integration notes for L1 (counter shape)

`count-c1.py` `static_checks` needs, per registry entry: `source.file == "server-schema.cpp"`,
`source.line` = 40/44/50/54, a new `source.row` S### token added this round whose SOURCES.md text contains
`server-schema.cpp`, `704366d` and `L40`-style line reference. Skill cell text must be canonical:
value cell `-2`/`-2`/`-1`/`-2`; outcome cell `reject 400, bounds -1 to 2147483647` (n_indent:
`reject 400, bounds 0 to 2147483647`); source cell = the S### token; meaning cell = the row's `meaning`
(26-29 words). `limits_line` (41/45/51/55) is extra provenance for the table/notes, not used by the counter.
Registered bounds survive `same()` (float32 tolerance) exactly: 2147483647 is representable in float64
and the comparison is relative 1e-6.

## Rows (field, line/limits, set, bounds)

1. sse_ping_interval, L40/L41, -2, [-1, 2147483647]
2. n_predict, L44/L45, -2, [-1, 2147483647]
3. n_indent, L50/L51, -1, [0, 2147483647]
4. n_keep, L54/L55, -2, [-1, 2147483647]

## Risks / limits on this evidence

- `base_effective` is null on every row: a reject row has no generation_settings key to compare; the
  omitted-field defaults observed (n_predict -1, n_keep 0, n_indent/sse_ping_interval absent) are recorded
  in the table above and in `out/DataG01/base_no_n_predict.json` instead.
- The 4 rows are reject-only; they cannot demonstrate soft-limit clamping for these fields because all
  four declare `set_hard_limits`. Fields with `set_limits` (e.g. top_k, top_p) are where clamp-to-bound
  rows must come from.
- Evidence is a single short-lived server instance per batch (two lifetimes: probes, then the omitted-default
  probe); `server.log`/`server2.log` (~10 KB) are retained if the run needs replaying.
- No installs; pacman transactions untouched. Nothing committed anywhere.
