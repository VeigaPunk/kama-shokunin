# AttackAmbiguity — round 14 critic (static, no run)

Seat: `KamaR14.AttackAmbiguity`. Read-only except this file. Nothing was executed, nothing was installed, and no endpoint, fleet, or config was read.

## State observed
- `tools/kama-ollama-evidence.py` and `tests/ollama-evidence/cases.json` were **absent** when I looked (glob on 2026-10-20). They are pending, not defective. Every finding below was derived from the contract text (spec.json goal, "Classifier shared interface") and from earlier source reports. Each one is a candidate input for the owners to pin. None is an observed failure.
- The `/api/ps` schema as quoted in earlier reports (`round-11/verification/SourceContract.md:66`: `expires_at`, `size_vram`, `context_length`) does not mention `remote_model`/`remote_host`. The contract still requires the classifier to honour those markers on a selected ps entry. [INFERENCE] Upstream Ollama sets `name == model` (both the shortest display name) on both tags and ps entries. That means a selected entry where name ≠ model is a non-native shape. Classifying it as `identity_conflict` is safe.

## Axes affected
False exit0 (most severe: it reads as a readiness/loaded claim), deterministic finding_id, fail-closed coverage, no over-rejection of legitimate `ollama cp` aliases.

## Counterexamples. Each must not yield exit0. The expected result is the one the contract implies.
Shorthand: `T` = tags file body, `P` = ps file body, `E` = `--expect`. The digest values `d1`/`d2` stand for distinct nonempty strings.

| # | Attack | Candidate input | Wrong result a naive impl gives | Contract-implied result |
|---|---|---|---|---|
| A1 | `ollama cp` alias joined by digest | T `[{name:"llama3.2:latest",model:"llama3.2:latest",digest:d1},{name:"gpt-x:latest",model:"gpt-x:latest",digest:d1}]`; P `[{name:"llama3.2:latest",model:"llama3.2:latest",digest:d1}]`; E `gpt-x:latest` | `loaded_same_digest` 0 (digest join) | `available_not_loaded` 1. Selection is by name/model only, never by digest. |
| A2 | Over-rejection of a legitimate shared digest | same T as A1; P `[{name:"gpt-x:latest",model:"gpt-x:latest",digest:d1}]`; E `gpt-x:latest` | `unknown`/`identity_conflict` (rejecting any duplicate digest) | `loaded_same_digest` 0. Only duplicate *selected* entries fail. |
| A3 | Two entries select the same name across keys | T `[{name:"x",model:"x",digest:d1},{name:"y",model:"x",digest:d1}]`; P `[{name:"x",model:"x",digest:d1}]`; E `x` | `loaded` 0 (first match wins) | duplicate selected, so `unknown` 2. B is also an internal conflict, and the precedence must be pinned (see P1). |
| A4 | Same entry counted twice | T `[{name:"x",model:"x",digest:d1}]`; P same; E `x` | `unknown` 2, if matches are summed per key (name hit + model hit = 2) | `loaded_same_digest` 0. Count entries, not key hits. |
| A5 | Byte-identical duplicate entries in tags or ps | P `[{name:"x",model:"x",digest:d1},{name:"x",model:"x",digest:d1}]`, tags valid | `loaded` 0 (dedup by equality) | `unknown` 2 |
| A6 | ps duplicates with differing digests | P `[{…x…,digest:d1},{…x…,digest:d2}]` | depends on loop order | pin `unknown` 2 (duplicate) over `identity_conflict`, per P1 |
| A7 | Name/model conflict on the **ps** side only | T `[{name:"x",model:"x",digest:d1}]`; P `[{name:"other",model:"x",digest:d1}]`; E `x` | `loaded` 0 (conflict checked on tags only) | `identity_conflict` 1 |
| A8 | Remote marker only on the selected ps entry | T local `{name:"x",model:"x",digest:d1}`; P `[{name:"x",model:"x",digest:d1,remote_host:"https://h"}]` | `loaded` 0 | `remote_inventory` 1 |
| A9 | Whitespace remote value | P entry `remote_model:" "` | `loaded` 0, if `.strip()` treats it as absent | `remote_inventory` 1. `" "` is a nonempty string. |
| A10 | Falsy non-string remote value | P entry `remote_host:0`, `false`, `[]`, or `null` | `loaded` 0 (`if e.get(...)` is falsy) | `invalid_input` 2. A present non-string is the wrong type. |
| A11 | Remote plus digest mismatch | T `{x,d1,remote_model:"up"}`; P `{x,d2}` | `identity_conflict` 1 | `remote_inventory` 1 ("regardless digest") |
| A12 | Remote on an **unselected** entry | T `[{x,d1},{name:"y",model:"y",digest:d2,remote_host:"h"}]`; P `[{x,d1}]`; E `x` | `remote_inventory` (global taint) | `loaded_same_digest` 0 |
| A13 | Non-string digest that compares equal | T and P entries for x with `digest:["a"]` (or `{"k":1}`) | `loaded` 0 (Python `==` is true and `if digest` is truthy) | `invalid_input` 2. Require `isinstance(str)` and nonempty. |
| A14 | Malformed **unselected** entry | T `[{name:"x",model:"x",digest:d1},{name:7}]`, or an entry that is not an object (`"x"`, `null`) | `loaded` 0 (non-matching entries skipped) | `invalid_input` 2. Validate every entry before selection. |
| A15 | Missing `model` on the selected entry | T and P `{name:"x",digest:d1}` | `loaded` 0 | `invalid_input` 2 ("missing identity"). Require both `name` and `model` to be nonempty strings. |
| A16 | JSON duplicate keys | T raw `{"models":[{"name":"x","model":"x","digest":"d2","digest":"d1"}]}`; P digest `d1` | `loaded` 0 (stdlib keeps the last key) | `invalid_input` 2. Use `object_pairs_hook` to reject duplicate keys at every level, including a repeated top-level `models`. |
| A17 | Empty expect | E `""` with T and P `{name:"",model:"",digest:d1}` | `loaded` 0 | `invalid_input` 2 (empty expect or empty identity) |
| A18 | Same capture used for both inputs | `--tags t.json --ps t.json` (or swapped files) with T `{x,d1}` | `loaded` 0. It is trivially self-consistent. | Smallest fix: reject when `os.path.samefile` is true → `invalid_input` 2. Limit: a byte-identical copy still passes, because the contract has no field that tells ps from tags (no `expires_at` inference is allowed). |
| A19 | Tag normalization | T `{name:"llama3.2:latest",…}`; E `llama3.2`, or `Llama3.2:latest`, or `llama3.2:latest ` (trailing space), or NFD vs NFC | `loaded`/`available` (`:latest`/case/Unicode normalization) | `unknown` 2 (no tags match) |
| A20 | Digest format skew | T digest `abc…`, P digest `sha256:abc…` (or a case difference) | `loaded` 0, if prefix or case is normalized | `identity_conflict` 1 (fail-safe). Do not normalize: a prefix join beyond the docs is [INFERENCE]. |
| A21 | ps-only presence | T `{"models":[]}`; P `{x,d1}` | `loaded` 0 | `unknown` 2 (no tags match) |
| A22 | Repeated `--expect` | `--expect a --expect x` | argparse silently keeps the last value | [tradeoff] Rejecting the repeat as `invalid_input` is optional. Pin the behaviour or document it. |

## P1 — precedence must be explicit (determinism defect if left implicit)
The contract maps several conditions to exit1 or exit2 but does not order them. Cases A3, A6, A11 and A7+remote get a finding_id that depends on loop order. Smallest correction: write one ordered ladder into the classifier and the registry, and pin it with fixtures A3, A6 and A11. The ladder:
1. `invalid_input`: unreadable file; non-object top level; duplicate JSON keys; `models` missing or not an array; any entry not an object; `name`, `model` or `digest` not a nonempty string; a present `remote_*` that is not a string; samefile.
2. `unknown`: no tags match; more than one selected entry in tags or ps.
3. `remote_inventory`: nonempty `remote_model`/`remote_host` on the selected tags entry or the selected ps entry.
4. `identity_conflict`: name ≠ model within the selected tags entry or ps entry; selected digests differ.
5. `available_not_loaded`: tags match, valid ps, no ps match.
6. `loaded_same_digest`: exit0, `readiness:"unknown"`.

Steps 3 and 4 could be swapped. Either order is acceptable as long as it is pinned. Placing remote first matches "regardless digest".

## Limits
- Static only. I ran no fixtures or CLI, so all of the above are candidate inputs, not observed failures.
- The ps `remote_*` absence and the native `name == model` claim are [INFERENCE]: they come from earlier quoted reports and recall of upstream handlers. I did not open any documentation this round.
- A18 cannot be fully closed under the contract (no ps/tags discriminator). It remains a known exit0 false-positive path when byte-identical copies are supplied.

## Owner messages sent
Bounded recommendations went to `KamaR14.Classifier` (P1 ladder, A10/A13/A14/A16/A18) and `KamaR14.Fixtures` (A1, A2, A3, A7, A8, A12, A16 as the highest-yield fixtures).
