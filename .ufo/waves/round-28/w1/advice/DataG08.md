# DataG08 — C1 request-field outcomes (round 28, wave 1)

Seat: `KamaR28.DataG08-2` (data, leaf). Port 48208, server `~/.local/opt/llama-b11755/llama-server -m ~/.cache/kama-shokunin/models/stories260K.gguf --host 127.0.0.1 --port 48208` launched under `timeout 900` from a separate process group, then SIGTERM (SIGKILL on timeout); `ss -ltnp` confirmed 48208 closed after the run. Version `0.7.0-dev (build 11755, commit 704366d76)`, binary sha256 `b6a31a8e...cd804`.

## Outputs (all absolute under the lane)
- `.ufo/waves/round-28/w1/out/DataG08/rows.json` — 4 row drafts, 0 no_rows.
- `.ufo/waves/round-28/w1/out/DataG08/run-notes.json` — argv, env, base body, every probe (including the non-countable alternatives), base generation_settings, fetch status/time.
- `.ufo/waves/round-28/w1/out/DataG08/*.raw.json` — 18 raw response bodies (`base`, 17 probes) plus `props.raw.json`; every `response_sha256` in rows.json matches its stored file.
- `.ufo/waves/round-28/w1/advice/DataG08.md` — this report.

## Rows (all from my own run on 48208)

Base request `{"prompt":"Once upon a time","n_predict":1}` → 200, sha256 `4ae15568...37189`; its generation_settings baseline: `adaptive_target=-1.0`, `adaptive_decay=0.8999999761581421`, `seed=4294967295`, `n_probs=0`.

| field | line / limits_line | sent | observed | live |
|---|---|---|---|---|
| `adaptive_target` | 167 / 168 | `5.0` | 200, `adaptive_target = 1.0` (soft clamp at 1.0; default -1.0) | `18405e06...029171` |
| `adaptive_decay` | 171 / 172 | `1.5` | 400 `Field 'adaptive_decay': Value must be between 0.000000 <= value <= 0.990000, but got 1.500000` | `dda12a91...975b19` |
| `seed` | 176 / null | `4294967296` | 200, `seed = 0` (uint32 truncation; default 4294967295) | `6cafc9db...80cb` |
| `n_probs` | 179 / null | `2.5` | 200, `n_probs = 2` (fractional truncation; default 0) | `a56617fb...991aa2` |

Each row satisfies the ticket: reject bounds are exactly the message bounds (0.000000/0.990000); each effective value differs from the value sent and from the field-omitted default. Outcome keys are the flat `generation_settings` keys from `server-task.cpp::to_json` (`adaptive_target`, `adaptive_decay` in both branches; `seed`; `n_probs`).

## Behaviour notes for integration
- `set_limits` is a silent clamp (`std::max(min, std::min(max, v))`), `set_hard_limits` throws the 400 message; `field_num::eval` wraps throws as `Field '<name>': <what>` (server-schema.cpp:522-546). The declaring/limits lines quoted in rows.json are verbatim substrings of the pinned snapshot (checked programmatically).
- `seed` has **no** `set_limits`/`set_hard_limits`/handler despite the comment at line 175 ("use a handler"); its `limits_line` is null. `n_probs` also has no limits/handler; line 180 is `add_alias("logprobs")`, not a limit.
- Non-countable observations retained in run-notes + raw files: `seed=-1` → 4294967295, which equals the field-omitted default (not countable); `seed=12345`/`4294967295` and `n_probs=5`/`-1`/`1000000`/`2147483647` are identities; `adaptive_decay=0.5` is identity; `adaptive_decay=0.995` rejects with the same bounds; `n_probs=4294967295` → -1 and `seed=1.5` → 1 are alternative transforms not used for the rows.
- Own raw fetch of the pinned URL now: HTTP 200, 29572 bytes, sha256 `1f9d7b73...004050`, identical to the snapshot and to the preregistration pin; accessed `2026-10-23T08:33:29Z`.

## Risks
- The `seed` and `n_probs` rows rely on silent numeric conversion (uint32 wrap / float→int truncation) rather than a declared limit; if a reviewer wants only declared-limit transformations, these two should be re-examined, but the live evidence is exact and reproducible.
- Row ids and the new `S###` SOURCES rows are not mine to create; each row needs a fresh S### (line-specific) before the counter can count it — otherwise `c:no-new-sources-row` / `a:no-skill-row`.
- Mechanism prose above is grounded in the pinned schema lines and the live bodies only; the `adaptive_*` sampler semantics beyond the stored value are not inferred.

## Blockers / installs
None. No tool installed or updated; only `/usr/bin/curl`, `/usr/bin/python3`, `/usr/bin/sha256sum`, `ss`. `df -h /fast` showed 197G free before scratch use; scratch lives at `/fast/scratch/hyaku/kama-r28/w1/DataG08/`.
