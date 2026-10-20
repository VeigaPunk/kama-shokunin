VERDICT: confirm — `owned_by` is a fixed literal "llamacpp" and `data[].id` is the loaded model-name/alias in llama.cpp @704366d76; a comma list does change `data[].id`, to the lexicographically smallest alias, never to a comma-joined string.

# ScoutOwnedByLlamacpp — server-context.cpp: owned_by and alias-as-id

Read-only falsify seat. Source-only: I started no server, ran no probe, no gate, no harness,
and touched no lane file. The lane's pinned `sources/` tree lacks `server-context.cpp`, so I
fetched it and its dependencies at the pinned commit and proved byte-identity against git
objects (below). Scratch `/tmp/kama-r16-ScoutOwnedByLlamacpp` removed after writing.

## What I ran (command → exit)

1. `curl -sS -f -o server-context.cpp https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp` → **0**;
   sha256 `dd1de0f26536ce3e115e39110f2f0719427f2796885c2a1ea2db071b603c2329`, 6320 lines.
2. same fetch for `common/arg.cpp` → **0** (sha256 `bf4c58c1…0d5822d`), `common/common.h` → **0**
   (`8bcc5708…9d2540a9`), `common/common.cpp` → **0** (`d10ea1ff…213ebd4`).
3. `common/string.cpp` fetch → **22** (404). Wrong path on my part; the helpers are in
   `common/common.h`/`common/common.cpp`. Recorded, not treated as absence.
4. `git clone --filter=blob:none --no-checkout --depth 1 https://github.com/ggml-org/llama.cpp.git` → **0**;
   `git fetch --depth 1 origin 704366d76…` → **0**; `git rev-parse FETCH_HEAD` →
   `704366d76f8748cf9ad3df62a464bfcc8d1ae6ad`.
5. `git rev-parse FETCH_HEAD:<path>` + `git cat-file -p` + `cmp` against each raw download → **0 for all four**.
   Blobs: server-context.cpp `b2116b1740a39be2412a33caf52adb9e322e95ee`, arg.cpp
   `267b84874912508f5ce205916a1abaaf6fd878b8`, common.h `b172b4efe7e0f87267e8145539b9b36a1b792e40`,
   common.cpp `b59e66e3bd3ff7d53896981b8364975bdee32853`.
6. GitHub contents API blob cross-check → **HTTP 403 rate limit** (`urllib HTTPError`, process exit 1);
   replaced by the git-object cmp in 5, which is the stronger check.
7. `strings -a ~/.local/opt/llama-b11755/libllama-server-impl.so` → contains `owned_by`, `aliases`;
   `libllama-common.so.0.7.0` → 1 occurrence of `set model name aliases, comma-separated (to be used by API)`
   and `LLAMA_ARG_ALIAS`.
8. `pgrep -x llama-server` → **1** (no process; I started none).

## Findings

### 1. `owned_by` is a hard-coded literal — CONFIRMED

`server-context.cpp:5168-5193` (`get_res_model_info`), line 5182:

> `{"owned_by", "llamacpp"},`

The same function supplies `{"id", meta.model_name}` (5172) and `{"aliases", meta.model_aliases}`
(5173). `owned_by` is not configurable: `owned_by` appears exactly once in `server-context.cpp`
and zero times in `arg.cpp`, `common.h`, `common.cpp`; no CLI/env path touches it.
`/models` and `/v1/models` share this handler in single-model mode (`server.cpp:283-284`).
Corroboration: live receipt `.ufo/waves/round-16/live/receipt.json` `captures.models.body`
(200, Content-Length 682) contains `"owned_by":"llamacpp"`; check `models_owned_by_llamacpp`
`passed: true`. Documented example too: pinned `README.md:1300` `"owned_by": "llamacpp"`.

### 2. Alias-as-id — CONFIRMED for the single-alias case (the exercised one)

`server-context.cpp:1116` `bool load_model(common_params & params)`; at 1521-1533:

> `if (!params_base.model_alias.empty()) { // backward compat: use first alias as model name`
> `model_name = *params_base.model_alias.begin();`

`model_name` becomes `meta.model_name` (`get_meta`, 4819) and is emitted as `data[].id` (5172);
`model_aliases` (4819-4820) is emitted as `data[].aliases` (5173). `data[]` is always exactly one
element (5223-5225); the Ollama-shaped `models[].name`/`models[].model` collapse to the same value
(5202-5203). The live receipt shows `"id":"kama-stories260k","aliases":["kama-stories260k"],
"owned_by":"llamacpp"` for `--alias kama-stories260k`; check `models_alias_id` `passed: true`.
Sleep mode does not change it: `cached_models = get_res_models(*meta)` at 6306, served at 5730.

### 3. `--alias` comma lists DO change `data[].id` — but not the way a comma string implies

Parser `common/arg.cpp:3024-3035`:

> `{"-a", "--alias"}, "STRING",` … `for (auto & alias : string_split<std::string>(value, ','))`
> … `alias = string_strip(alias); if (!alias.empty()) params.model_alias.insert(alias);`

Same handler for env `LLAMA_ARG_ALIAS` (`set_env("LLAMA_ARG_ALIAS")`, 3035). `model_alias` is
`std::set<std::string>` (`common/common.h:514`); `string_split<std::string>(char)` keeps empty parts
(`common.h:836-847`), `string_strip` trims `std::isspace` at both ends (`common.cpp:461-471`), empties
are dropped, `insert` dedupes and orders. Because the id is `*set.begin()`, the selected id is the
**lexicographically smallest** alias (std::less<std::string>, byte order) — *not* the first element
typed and *not* the joined list. Derived cases (source semantics, not run):

| argv | alias set | `data[0].id` | `data[0].aliases` |
|---|---|---|---|
| `-m /p/x.gguf` (no alias) | {`/p/x.gguf`} (inserted, server.cpp:191-192) | `/p/x.gguf` | `["/p/x.gguf"]` |
| `-m /p/x.gguf --alias b` | {b} | `b` | `["b"]` |
| `--alias b,a` | {a,b} | `a` | `["a","b"]` |
| `--alias a,b` / `--alias "b, a"` / `--alias b,a,b` | {a,b} | `a` | `["a","b"]` |
| `-a z -a y` (repeat) | {y,z} | `y` | `["y","z"]` |
| `--alias "a,"` | {a} | `a` | `["a"]` |
| `--alias ","` | {} → default inserted | path/HF repo | `[path/HF repo]` |

So `--alias b,a` rewrites `data[].id` from what `--alias b` would return (`b`) to `a`; it never
produces `"b,a"`, never adds a second `data[]` entry, and exposes the full set only in `aliases[]`.
The README documents only single aliases (`README.md:1258` one element; `:1284` "`--alias`" replaces
the `-m` path); comma semantics exist only in the help text. `served-identity-crosswalk.md:27`
calls that choice undocumented — the code now answers it: min of the set.

### 4. No `--alias` at all

`server.cpp:189-193` inserts `params.model.get_name()` when the alias set is empty. `get_name()` is
`hf_repo` if set, else `docker_repo`, else `path` (`common.h:312-320`). Hence the default id is the
`-m` path (as the README says), but an `-hf`/Docker launch yields the repo string, not a local path.
With any `--alias`, the model path is *not* added to the set: the live `aliases` array held only
`kama-stories260k`, not the GGUF path.

## Consequences to integrate

- `corpus/knowledge/llamacpp-loading-lifecycle.md:37` "id = the `--alias`" and `:119` "the id is the
  caller's alias" are exact for the single-alias run they describe, but should be qualified:
  **id = `model_name` = lexicographically smallest alias of the `--alias`/`LLAMA_ARG_ALIAS` set, else
  `get_name()` (HF repo > Docker repo > `-m` path)**; the full set is `data[].aliases`.
- Probe consequence: `tools/kama-probe.sh` compares expectations to `data[].id` (id precedence at
  `:332`, extraction at `:356`). For a server launched `--alias foo,bar`, `<alias>` must be `bar`
  (min), not `foo`; configuring `foo` yields a false `MODEL_MISMATCH` exit 2. No claim here that the
  deployed 34113 server uses aliases — `consumer-registry.md:155` shows a path id, consistent with
  no `--alias`.
- An identity record keyed on `data[].id` sees only the smallest alias; the other aliases survive
  solely in `aliases[]`.

## Limitations

- Source-level only. Per the lane contract this item does not authorize starting `llama-server`, so
  I did not run a comma-list server or capture its body; `kama-llamacpp-live.py:775` passes a single
  `--alias`, so no existing receipt exercises a comma list.
- Source↔shipped binary is **[INFERENCE]**: the receipt records `/props.build_info`
  `b11755-704366d76`, and the installed tree contains the same help string and JSON keys, but I did
  not execute the binary. The source itself is git-blob-verified at `704366d76`.
- Single-model mode only. In router mode `/v1/models` is `models_routes->get_router_models`
  (`server.cpp:269`), a different builder I did not analyze; per-model alias selection and its
  `owned_by` remain unverified here.
- Array order and "smallest" are standard `std::set`/`std::less<std::string>` semantics; the
  single-element live body cannot observe ordering. Serialization of the set as a JSON array follows
  nlohmann's container handling **[INFERENCE, standard]**.
- `string_split<…>(char)` retaining empty tokens is moot here because empties are dropped; only
  whitespace-trim + comma split matters, as quoted.

Installs: none (no package, tool, or binary was installed or upgraded; no pacman transaction).
