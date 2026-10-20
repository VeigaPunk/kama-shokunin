VERDICT: partial — the gate is byte-identical to the one GateForgeries attacked, so all 16 accepted-bad rows persist, and 115 of 237 distinct receipt leaves are read by no predicate.

Scope: `tests/llamacpp-live/check-receipt.py` (receipt gate) only. The live tool and
`controls.py` are cited only where they define a field's semantics. No gate run was made by
this seat (measurement is L1's); every "still accepted" row below rests on a hash identity,
and every "ungraded" row on the absence of any read in `validate()`.

# Bound bytes (identity, not inference)

| Artifact | sha256 |
|---|---|
| frozen gate `.ufo/waves/round-18/frozen/tests_llamacpp-live_check-receipt.py` | `ad6801791f2ada896a7ee188609391aac86185c47320dbf415331869ca9cd2a5` |
| `git show 54a29268…:tests/llamacpp-live/check-receipt.py` (GateForgeries' reviewed rev) | `ad680179…` (same) |
| `git show e75cf680…:tests/llamacpp-live/check-receipt.py` (round-18 start) | `ad680179…` (same) |
| `git diff --stat 54a29268 e75cf68 -- tests/llamacpp-live/` | empty |
| round-17 `live/receipt-1.json` (GateForgeries' base) | `f34afb545db28fc37b2df8179f5872d2e84a20a140a0f3367a9f60d1864702a4` |
| round-17 `receipt-2` / `receipt-3` | `3df31ddb…dcc39ad9` / `5e2c0511…91e36d90` |
| round-16 `live/receipt.json` (v1 base) | `076865e5…bdbd4669` |

Gate and base receipts are bit-identical to the ones GateForgeries exercised at `54a29268`,
and `validate()` has no clock, environment or filesystem input beyond the receipt and the four
pins. Each accepted row in its matrix therefore carries over unchanged; I re-derive the reason
from code for every row rather than relying on that document's prose.

# 1. v2 predicate map (global blocks)

`validate()` spans `:192-963`; `claim()` `:662-669`; `obs()` `:671-674`. Line numbers are the
frozen copy above. "Reads" lists fields a predicate actually dereferences, not fields the
schema merely requires to exist.

| Blk | lines | reads | re-derives / enforces |
|---|---|---|---|
| G1 schema/outcome | 203-211 | `schema`, `setup_error` | schema ∈ {v1,v2}; `setup_error` null. **Schema is self-declared** (`:205` `is_v2 = schema == RECEIPT_SCHEMA_V2`) |
| G2 timestamps | 213-225 | `started_utc`, `ended_utc` | parseable; `ended >= started` |
| G3 alias/scalars | 226-234 | `alias`, `ctx`, `threads` | non-empty str; positive int |
| G4 port/refusal | 235-264 | `port`, `port_refusal_set` | range, sorted, unique, hard pins present, port not pinned/refused |
| G5 server | 265-310 | `server.{arg,realpath,sha256,install_tree,install_tree_sha256,server_impl_sha256}` | digest shapes; tree basename == `server.sha256`; `install_tree_sha256` recomputed **over the receipt's own tree** |
| G6 model | 311-330 | `model.path`, `model.sha256`, `model_sha256_post` | shapes; hex or `rehash-error:*` |
| G7 probe identity | 331-349 | `probe.path`, `probe.sha256` | shapes only — never tied to `probes[].argv` |
| G8 tool identity | 350-370 | `tool.path`, `tool.sha256` | optional block; pin only if `--expect-tool-sha256` given |
| G9 child env | 371-386 | `child_env_keys` | allowlist, sorted-unique |
| G10 argv | 387-422 | `argv` (whole vector, via `argv_flag`) | `argv[0]==realpath`; `-m/--alias/--host/--port/-c/-t` first occurrence; last two tokens are `--no-webui --offline` |
| G11 loading lifecycle | 423-479 | `loading_observed`, `loading_503.{status,path,body}`, `loading_envelope_exact`, `transitions[].status`, `port_listener_ownership`, `pdeathsig.requested` | consistency among the three; envelope flag re-derived from `loading_503.body`; ownership == `child` |
| G12 captures | 480-505 | `captures.{health,models,props,slots,metrics}` (dict-ness), `captures.health.{status,body}`, `captures.models.body`, `captures.props.fields`, `captures.metrics.status` | only existence for all five; see §3 for the holes |
| G13 probes | 506-604 | `expect`, `argv`, `exit`, `result.schema`, `result.summary.exit`, `rows[0].{verdict,reason,drift,expected_model_id,declared}` | two records (one alias, one mismatch); verdict↔exit↔drift↔reason coherent; declared endpoint names the served port |
| G14 teardown shape | 605-624 | `teardown.{returncode,port_refuses,sigterm_sent,sigkill_sent,alive_at_teardown_start}` | int|null, bool|null; v2 requires the three bools present |
| G15 checks array | 626-660 | `checks[].{id,documented_by,passed,observed}` | unique ids; `documented_by` non-empty str; `passed` is bool **True**; observed is a dict; id set == `REQUIRED_CHECKS_{V1,V2}` |
| G16 claim/obs | 662-674 | `checks[].passed`, `checks[].observed` | `claim()` fires only when `passed` is a bool; `obs()` returns the check's own observed dict |

# 2. Per-check v2 predicates and the evidence each actually consumes

| Check | lines | v2 predicate re-derives | evidence consumed | independent? |
|---|---|---|---|---|
| `health_ready` | 680-700 | `status==200` and `body == {"status":"ok"}` | `captures.health.status/body` | yes (raw body stored) |
| `models_alias_id` | 702-723 | every `data[].id == alias` | `captures.models.body` only | yes, but `captures.models.status` unread |
| `models_owned_by_llamacpp` | 724-740 | every `data[].owned_by == "llamacpp"` | same body | yes |
| `metrics_not_enabled` | 741-754 | `status == 501` | `captures.metrics.status` | the status is the evidence — fine |
| `props_alias` | 755-774 | `props.fields.model_alias == alias` | **producer projection** `fields`; no body exists | **no — circular** (see §2 note) |
| `probe_model_ok` | 775-803 | row0 verdict `MODEL_OK`, reason `matched`, exit 0 | `probes[].result.rows[0]` | partial — `served_model` unread |
| `probe_mismatch` | 804-833 | row0 verdict `MODEL_MISMATCH`, reason `served-id-mismatch`, exit 2 | same | partial — `served_model` unread |
| `teardown_graceful` | 847-882 | alive, SIGTERM, no SIGKILL, rc 0 | `teardown.*` four bools/int | yes for the shape; `observed.error` unread |
| `teardown_port_closed` | 883-907 | `port_refuses is True` **and** ownership `child` | `teardown.port_refuses`, top-level ownership | yes |
| `loading_envelope_graded` | 908-941 | `loading_envelope_exact` true **and** every `loading_503_bodies[].body` exact | two self-selected lists | **no** — `transitions` 503 bodies unread, `loading_bodies_dropped` unread |
| `model_unchanged` | 942-961 | `model.sha256 == model_sha256_post` | two hex fields | yes (both are declared digests, not recomputed) |

§2 note (props circularity, P1 for the "sourced" axis). `ready_captures` captures `/props` and
`/slots` with `keep_body=False` (tool `:674,693`), so `body_sha256` is recorded while the bytes
it digests are discarded (`:642-655`). `props_alias` compares
`captures.props.fields.model_alias` — the producer's own projection — against `alias`, another
receipt field, then compares `observed.fields.model_alias` against that projection. No predicate
in the chain touches a byte the server sent; a receipt that rewrites `alias`, the stored models
body and `fields` together is internally consistent and passes — and every one of those is a
field the forger controls. Same exposure covers the four ungraded props
fields and `slots.element_count`.

v1-only: `teardown_exited` `:834-846` (rc non-null). The v1 branch is the escape hatch behind
F1; it must not be reachable when a v2/v3 minimum is requested.

# 3. Fields no predicate reads (ungraded)

Counted over the live v2 receipt: **237 distinct leaf paths, 115 never dereferenced** by
`validate()`/`claim()`/`obs()`/`probe_row0()`. Grouped by owner, with the producer line that
emits the field. Two further reads are conditional and skip silently when the key is absent or
null: `probes[].result.summary.exit` (`:566`, skipped if MISSING) and
`probes[].result.rows[].expected_model_id` (`:593`, skipped when null).

## 3a. Claim-bearing (a contradiction here certifies a false claim)

| Field | producer | why it matters |
|---|---|---|
| `captures.{models,props,slots}.status` | tool `:646` | body graded from a 500/404 response; gate never asks 200 (`:503-504` reads only metrics+health) |
| `captures.*.error` | tool `:647,706` | a capture recorded as failed is graded as if complete |
| `captures.*.body_sha256`, `.body_truncated`, `.body_read_truncated` | tool `:649-655` | the only integrity link from body to bytes; also the "graded a truncated body" vacuous pass |
| `captures.props.fields.{build_info,total_slots,is_sleeping,n_ctx}` | tool `:680-690` | only `model_alias` is graded; the rest of the props evidence is free |
| `captures.props` has **no** `body` | live receipt; tool `:674` `keep_body=False` | `props_alias` grades a projection against another receipt field — no bytes exist to re-derive from |
| `captures.slots.{status,element_count}` | tool `:693-702` | no check owns `/slots` at all |
| `transitions[].body` (503 rows) | tool `:436-446` | every 503 row can carry any body (see §4 row 20) |
| `transitions[].{body_sha256,repeats,t_ms,phase,path,error,body_over_cap}` | tool `:436-450` | count/order/dedup are unpinned; `total_503_responses` cannot be checked |
| `loading_503_bodies[].{body_sha256,path,repeats}` | tool `:558-565` | dedup list is self-selected and unlabelled |
| `loading_bodies_dropped` | tool `:1070,1151` | cap overflow (256, tool `:75`) is invisible; grading can be partial yet pass |
| `checks[].observed.all_exact`, `.bodies_dropped`, `.distinct_bodies`, `.total_503_responses`, `.loading_observed` | tool `:1349-1356` | the check's own evidence can contradict `exact` and the gate will not notice |
| `checks[].observed.body`, `.expected_body` (health), `.fields.*` (props), `.error` (teardown) | tool `:1178,1206,1331` | observed evidence can disagree with the capture it claims to summarize |
| `probes[].result.rows[].served_model` | probe | the C1-owned oracle added in round 17; a row can say `ghost-model` with verdict `MODEL_OK` |
| `probes[].result.rows[1..]` | probe | `probe_row0()` (`:179-190`) reads only `rows[0]`; later contradictory rows are invisible |
| `probes[].result.summary.{model_ok,drift,registry_rows_evaluated}` | probe | counters can contradict the rows they summarize |
| `probes[].argv` beyond `check/--port/--expect` | tool `:715-717` | never tied to `probe.path`/`probe.sha256` |
| `source_binding.*` (9 leaves) | tool `:866-940` | the entire sourced-claim binding is unverified (SourceBindingCheck's medium finding) |
| `internal_fault` | tool `:1078,1371` | a receipt can advertise an internal fault and still exit VALID |
| `pdeathsig.prctl_ok` | tool `:1087` | `requested: true` alone passes; the prctl result is free |
| `checks[].documented_by` content | tool `:831` | only "non-empty string" (`:644-646`); the selftest uses `"d"` — receipt provenance is decorative |
| `server.server_impl_sha256` vs `install_tree` | tool `:1052` | never tied to a member; the member can be absent or forged |
| `teardown.{log_lines,log_path,log_lines_truncated,log_tail_truncated,term_wait_ms}` | tool `:778-821` | cosmetic today, but a truncated log cannot certify the graceful path |

## 3b. Cosmetic (do not add predicates for these)

`port_pick_note`, `child_pid`, all `*.headers.*`, `probes[].stderr_tail`,
`probes[].result.{subcommand,registry,verdict_vocabulary,exit_codes}`. None can change a
verdict; grading them buys maintenance and no fail-capability. `child_pid` is the one arguable
exception if a future check wants PID↔listener binding.

# 4. GateForgeries cross-check — every accepted row still accepted

Still accepted (bare invocation; row 24 is accepted bare and rejected under
`--expect-tool-sha256`). "Catching predicate" is the one predicate that closes each row.

| Row | Forged change | Catching predicate | v3 outcome |
|---|---|---|---|
| 09b | v1 label + v1 check set on v2 evidence | `--require-schema v2` minimum: declared < required ⇒ INVALID; bind schema to `tool.sha256` | fail (1) |
| 11 | `--api-key X` before `--no-webui` | exact argv equality with the re-derived vector; reject duplicate flags and any token outside the allowlist; reject credential flags outright | fail (1) |
| 12 | 2nd `--host 0.0.0.0` | same totality predicate (`count("--host") == 1`) | fail (1) |
| 13 | 2nd `--port 9999` | same | fail (1) |
| 14 | 2nd `--alias evil` | same | fail (1) |
| 15 | `--metrics` inserted, `/metrics` still 501 | totality + cross-field: `--metrics` present ⇒ metrics status ≠ 501 | fail (1) |
| 16 | `internal_fault: "internal:RuntimeError"` | `internal_fault` non-null must mirror into `setup_error` (tool `:1371-1373`); mirror missing ⇒ inconsistent; mirrored ⇒ never pass | mirror missing ⇒ fail (1); mirrored ⇒ not-evaluated (3) |
| 17 | `loading_bodies_dropped: 37` | `loading_envelope_graded` may pass only when `loading_bodies_dropped == 0`; else not-evaluated | not-evaluated (3) |
| 18 | `captures.health.body_sha256: "0"*64` | recompute sha256 over every stored `captures.*.body`; mismatch ⇒ INVALID | fail (1) |
| 19 | `total_503_responses: 9999` | `total == sum(1+b.repeats) + loading_bodies_dropped == sum(1+t.repeats)` over the 503 transitions | fail (1) |
| 20 | non-exact 503 in `transitions`, exact dedup list | grade every `transitions` row with `status==503` (and `path=="/v1/models"`) via `loading_envelope_ok`; recompute its `body_sha256` | fail (1) |
| 21 | `captures.health.body_truncated: true` | any capture whose body is graded must have `body_truncated is False` and `body_read_truncated is False` | fail (1) |
| 22 | `observed.body: {"status":"degraded"}` with capture ok | `observed.body == health_body` for `health_ready` | fail (1) |
| 23 | `served_model: "ghost-model"`, verdict MODEL_OK | `rows[].served_model == alias` for both probe rows | fail (1) |
| 24 | `tool` block deleted | require the tool block for v2/v3 and require `--expect-tool-sha256` (or `tool.path` basename) | fail (1) |
| 25 | composite downgrade (09b + health + teardown + loading) | same as 09b | fail (1) |

Still rejected at the frozen gate, no action: 01-08 (health body, sigterm, sigkill, rc −15,
alive-at-start, ownership, later non-exact dedup body, `loading_observed` inconsistency), 09
(v1 label with v2 ids → unexpected ids), 10 (v2 label on the v1 receipt), 11b (`--api-key`
after the tail). The v2 core does hold for the shapes it names.

Scope question for the same predicate: only `/v1/models` 503 rows are contract-bound. A
`/health` 503 row with an arbitrary body is currently invisible, and the gate neither grades it
nor declares it exempt; v3 should say which paths it grades so any exemption is auditable.

Bookkeeping: the matrix contains **16** bold accepted variants (15 under all four pins, since
24 is then rejected), while the prose prints "15 of 24" and "14 of 24" (`GateForgeries.md:73`).
One-row slip; direction unchanged.

# 5. New accepted forgeries not in GateForgeries

Each is a minimal mutation of the accepted `receipt-1.json` (one field, one deletion, or one
appended element); acceptance follows because no predicate in §1-§2 dereferences the field and
no other predicate depends on it transitively. These are static proofs, not runs — L1 can
confirm the whole set with one loop.

| # | Recipe | Ungraded field(s) | Catching predicate | v3 outcome |
|---|---|---|---|---|
| N1 | `captures.models.status=500` (also props, slots) | capture status | status 200 for every capture a check consumes | fail |
| N2 | `captures.models.error="TimeoutError"` | capture error | `error is None` for every graded capture | fail |
| N3 | `captures.props.body_sha256="0"*64`, keep `fields` | props digest + projection | store `captures.props.body`, re-parse `model_alias`; grade `observed.fields` == `captures.props.fields` wholesale | fail |
| N4 | `captures.slots.element_count=99`, `slots.status=500` | slots capture | either give `/slots` an owning check (status 200, `element_count` int ≥ 1, digest) or drop the capture as dead weight | fail |
| N5 | delete `result.summary` from both probes | `summary` optional (`:566`) | require `summary`; re-derive `model_ok`, `drift`, `registry_rows_evaluated` from `rows` | fail |
| N6 | append a contradictory `rows[1]` to `probes[0].result` | `rows[1..]` | require `len(rows) == registry_rows_evaluated`; grade every row to the same verdict | fail |
| N7 | `rows[].expected_model_id=null` | conditional cross-check (`:593`) | require present and `== rec.expect` for every row | fail |
| N8 | `alias="kama-not-this-model"` (== `MISMATCH_EXPECT`) | probe selection (`:518-522`) | reject `alias == MISMATCH_EXPECT`; require the two `--expect` vectors differ | fail |
| N9 | rewrite `source_binding[0]`: `row=S999`, `commit=bad`, zero `file_sha256`, `span_text="forged\n"` | all 9 leaves | recompute `span_sha256 == sha256(span_text)`; `file_sha256` == pinned file; `span_text` == exact lines `[start,end]` of the pinned copy; `url` derived from `commit`/`path`; `check ∈ checks[].id`; `row ∈ S-ids ∪ {null}` (see §6) | fail |
| N10 | `transitions[1].body` non-exact, `repeats=0`, `t_ms=999999` | transitions body/count/order | grade the body (row 20), recompute `body_sha256`, require monotone `t_ms` within the run duration, `phase ∈ {models,health}` | fail |
| N11 | `loading_503_bodies[0].body_sha256="0"*64`, `path="/metrics"` | dedup-list identity | recompute digest; `path ∈ {/v1/models,/health}` and equal to the matching transition's path | fail |
| N12 | `pdeathsig.prctl_ok=false` | prctl result | require `prctl_ok is True` | fail |
| N13 | add a fabricated `install_tree["evil.so"]`; or drop `libllama-server-impl.so` while `server_impl_sha256` stays set | tree completeness | pin the tree (`--expect-install-tree-sha256`; the recomputation is self-referential today) and require the impl member `== server_impl_sha256` | fail |
| N14 | set every `documented_by` to `"x"` | provenance content | require the producer's DOC map entry (stable citation id) and, for `docs.python.org` URLs, the `/3.14/` form | fail |
| N15 | `checks[teardown_graceful].observed.error="TimeoutError"` | observed error | `observed.error is None` when `teardown_graceful` passes | fail |

N9 and N13 are the two that change what the receipt can *assert about the world* rather than
about its own bookkeeping; N1/N2/N3/N6/N7 change a health claim. The rest are count/identity
contradictions.

# 6. SourceBindingCheck cross-check

Its medium finding is confirmed by construction: `source_binding` appears nowhere in the gate
(grep: zero hits in the frozen file), so the corruption it demonstrated ("VALID" on a forged
binding) is still available at `e75cf68`. Its second finding — the teardown binding omits
`server.cpp:29-38`, including `signal_handler` → `shutdown_handler` — is a *completeness* gap
in the receipt data, not something the gate could ever flag; if the gate grades bindings it
should also require, per check, a non-empty binding list, which is what makes that omission
visible.

Predicate set that makes bindings fail-capable offline (pinned copies already exist under
`.ufo/waves/round-17/sources/`, so no network):

1. `span_sha256 == sha256(span_text.encode())` — self-consistency (catches N9's all-`f`).
2. `file_sha256 == sha256(pinned file at commit)` — catches `commit=bad` / wrong tree.
3. `span_text == "\n".join(file_lines[lines[0]-1:lines[1]])` and `len(lines)==2`,
   `1 <= lines[0] <= lines[1] <= len(file)` — catches forged ranges and `[1,1]`.
4. `url == raw_url(commit, path)` — catches a mismatched citation.
5. `check ∈ checks[].id`; `row ∈ S-ids ∪ {null}` — catches S999.
6. For a v3 pass: every check in the required set has ≥1 binding, and `teardown_graceful`
   carries the `signal_handler` span (the S043 completeness correction).

Outcome: `false` (a forged binding is a false claim, not an unobservable), because the pinned
copies are local. If the pinned tree is absent, `not-evaluated` — never `pass`.

# 7. v3 delta: where the frozen code blocks the declared contract

The declared v3 contract is absent from these bytes: `--require-schema` (0 hits),
`not_evaluated_reason` (0 hits), and `outcome`/`evaluated` as receipt fields (0 hits; the only
textual matches are a section comment at `:203` and the probe counter name
`registry_rows_evaluated` at `:998`). Concretely:

| Contract clause | Blocking code |
|---|---|
| `passed ∈ {true,false,null}` + `evaluated` bool | `:647-650` rejects a non-bool and rejects `false`; no `evaluated` read |
| `passed:null` only for `loading_envelope_graded` with `loading_observed false` | `:913-915` fails a null outright ("nothing graded"); `:922-925` requires a non-empty body list |
| `observed.not_evaluated_reason` == literal | field unread; see §3a |
| top-level `outcome` | field absent from `validate()`; `main()` `:1380-1399` derives only 0/1/2 |
| `--require-schema v1|v2|v3`, lower declared ⇒ INVALID | `:205`, `:653` choose the check set from the self-declared schema; no minimum |
| exit 3 NOT-EVALUATED | no return path produces 3 |

Design warning, same class as F1: `outcome` and `evaluated` are self-declarable. The gate must
re-derive both — fail if any `passed is False`; setup-error if `setup_error`/`internal_fault`
non-null; not-evaluated if no false and ≥1 null; pass otherwise — and must reject a receipt
whose declared `outcome` disagrees with that re-derivation. Otherwise v3 reintroduces the
downgrade it is meant to close, one level up.

Also required: `loading_bodies_dropped > 0` must force `loading_envelope_graded` to
`null`/`evaluated:false` (reason e.g. `bodies-dropped`), because the cap (tool `:75`) makes
coverage partial by construction — the producer's own `loading_envelopes_all` (tool `:231-236`)
returns True over the surviving subset.

# 8. What should be retained as tests (calibration)

The gate's `--selftest` (`:1192-1356`, "39 mutations + unreadable case") is derived from the
predicates that exist, so it can detect a *deleted* predicate but never a *missing* one. Each
new predicate above therefore needs a retained bad control in `tests/llamacpp-live/controls.py`
(the R5 mechanism) and a named selftest mutation; without both, v3 grows ungraded code and the
calibration axis moves backwards while the selftest count grows. Priority order by
claim-bearing value: rows 09b/11-15 (schema+argv, one predicate each), 19/20/17
(counts/transitions/cap), N9/N13 (world-claims), N5/N6/N7/N8 (probe evidence), then the
cosmetic list in §3b explicitly *not* graded.

# Limitations

- Static analysis only. I did not execute the gate, the tool, `controls.py`, `measure.py` or
  any server; no port was bound. L1 should confirm §5 with one loop over mutated copies of
  `receipt-1.json` in its own scratch clone before quoting any accepted count.
- "Ungraded" is asserted from the absence of a dereference in `validate()`; a field could still
  be graded indirectly through a container (family/observed dicts are the only such cases and
  are handled per key in §3).
- §4's carry-over depends on the frozen gate and round-17 receipts being identical to those
  GateForgeries used; hashes above establish that, but I did not re-run its 27 commands.
- I did not evaluate `controls.py` K0-K8 or the tool's `_listen_inodes`; those are sibling
  seats' questions (R5/R6/R7 and listener ownership).
- 115 ungraded leaves counts distinct paths, not array instances; the live receipt's five
  `source_binding` entries collapse to 9 paths.

# Installs

None. No package, tool or upgrade was installed or invoked; no pacman/uv/npx/cargo/npm command
was run. No scratch directory was created, so nothing needed removal.
