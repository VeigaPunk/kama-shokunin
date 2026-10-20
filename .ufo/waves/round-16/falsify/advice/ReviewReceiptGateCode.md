VERDICT: partial — `tests/llamacpp-live/check-receipt.py` does re-derive the ten check predicates from stored evidence (9/10 resist fully consistent forgeries), but it does not bind the producer's exact evidence keys: 29 of 32 single-field evidence mutations still validate, including contradictory loading evidence, unbound probe argv, an unrederived `install_tree_sha256`, unchecked capture statuses/digests, unbound `--host`/`-c`/`-t`, and ignored `pdeathsig`. Two of the ten checks (`models_alias_id`, `models_owned_by_llamacpp`) also diverge from the producer's predicate on incomplete `data[]` entries and can be made true against a body the producer grades false.

# ReviewReceiptGateCode — attack on the receipt gate

Item: does `check-receipt.py` bind to the producer's exact keys and re-derive
every check from stored evidence? Lane commit b8e485c; both files are new in
that commit (`git show --stat b8e485c -- tests/llamacpp-live/check-receipt.py
tools/kama-llamacpp-live.py` → 1014 + 989 insertions).

## Axes

1. **Exact-key binding** — every key the producer emits is read, type-checked,
   and cross-bound to its sibling evidence.
2. **Check re-derivation** — each `checks[].passed: true` is recomputed from
   raw evidence with the producer's exact predicate, not trusted from
   `observed`, `summary`, or `passed`.
3. **Coverage of the claimed claim** — the live receipts actually exercise the
   branch being claimed (loading vs ready).

## What I ran (exact commands, exits)

All under `/home/vgpnk/Projects/shokunin/kama-shokunin`; scratch in
`/tmp/kama-r16-ReviewReceiptGateCode/`.

| command | exit | output excerpt |
|---|---|---|
| `python3 tests/llamacpp-live/check-receipt.py .ufo/waves/round-16/live/receipt.json` | 0 | `VALID …/receipt.json` |
| same on `receipt-frozen-probe.json` | 0 | `VALID` |
| `python3 tests/llamacpp-live/check-receipt.py --selftest` | 0 | `selftest: 16 mutations + unreadable case all rejected; valid receipt accepted` |
| gate on both receipts with `--expect-model-sha256 270cba1…` `--expect-server-sha256 b6a31a8…` `--expect-probe-sha256 6edd3c4…` / `93ee430…` | 0, 0 | `VALID` both — pinned identity is accepted |
| gate with `--expect-server-sha256 ''` | 1 | `server.sha256 … != expected`, `--expect-server-sha256 '' is not 64 lowercase hex` |
| `python3 /tmp/kama-r16-ReviewReceiptGateCode/mutate.py` (32 single-field evidence mutations) | base 0 | **29 ACCEPTED / 3 rejected**; rejected: `observed-key-removed` 1, `ownership-unproven` 1, `teardown-rc-1` 1 |
| `python3 /tmp/kama-r16-ReviewReceiptGateCode/consistent.py` (10 evidence+observed forgeries) | base 0 | 9 rejected (exit 1 each), `teardown-rc-crash-consistent` accepted (exit 0) |
| `python3 -c 'refused_ports()'` from the producer | — | `[8080, 34113]` — receipt's refusal set matches today |

Positive controls the gate catches (all exit 1): declared-endpoint port
mismatch, `child_env_keys` containing `PATH=/x`, port inside
`port_refusal_set`, install tree missing `llama-server`, extra check id,
`passed: false`, wrong `--expect-model-sha256`.

## Findings, severity order

### F1 [High] Loading evidence is unbound; contradictory receipts validate

Gate `:340-360` only checks that `loading_503` is a dict and that
`loading_envelope_exact` equals a re-parse of its `body`. It never reads
`loading_503.status`, `path`, `t_ms`, `body_sha256`, and never cross-checks
`transitions`. Accepted mutations (all gate exit 0):

- `loading-claim-empty`: `loading_observed: true`, `loading_503: {}`,
  `loading_envelope_exact: false` → VALID. A receipt can claim a load window
  with zero evidence.
- `loading-status-200`: a `loading_503` dict whose `status` is **200** and whose
  body is the loading envelope, `loading_envelope_exact: true` → VALID. The
  producer only ever writes this dict after a live 503
  (`tools/kama-llamacpp-live.py:429-431`), so `status: 503` is part of the key's
  meaning and is unchecked.
- `loading-contradicts-transitions`: append a `transitions` row with
  `status: 503` and the envelope body while `loading_observed: false` →
  VALID. The gate never reads `transitions` beyond `isinstance(list)`.
- `transitions-empty`: `transitions: []` → VALID.

Coverage: **both live receipts have `loading_observed: false`,
`loading_503: null`, `loading_envelope_exact: null`** (verified by JSON read;
the frozen receipt is identical here). So the gate's loading re-derivation is
exercised only by the synthetic selftest fixture, never by a live receipt. The
knowledge entry is honest about this — "No 503 was captured: `loading_observed`
false" (`corpus/knowledge/llamacpp-loading-lifecycle.md`) — so this is primarily
a binding defect, not a false live claim.

### F2 [High] `models_alias_id` / `models_owned_by_llamacpp` do not mirror the producer for incomplete entries

Gate `:386-394` builds `ids`/`owners` by **dropping `None`**
(`if e.get("id") is not None`). Producer `:876-879` keeps them:

```python
ids = [e.get('id') for e in data if isinstance(e, dict)]
owners = [e.get('owned_by') for e in data if isinstance(e, dict)]
```

A body with one complete entry plus one incomplete entry therefore splits the
two oracles. Demonstrated with `models.data = [{"id": "<alias>",
"owned_by": "llamacpp"}, {"object": "model"}]`, all `checks` left
`passed: true`:

```
=== models-second-entry-incomplete: exit 0
VALID /tmp/kama-r16-ReviewReceiptGateCode/final-models-second-entry-incomplete.json
producer would see ids= ['kama-stories260k', None] owners= ['llamacpp', None]
producer models_alias_id= False
producer models_owned_by= False
```

The gate says VALID for a receipt whose stored `/v1/models` body violates both
checks it claims to re-derive. The other eight predicates are exact mirrors
(health 200, metrics 501, props alias, probe verdict/exit, teardown rc non-null,
port refuses, digest equality); this `None`-filter is the only predicate
divergence found.

### F3 [Medium] Probe record chain is unbound

Gate `:405-475` reads `probes[].expect/exit/result.rows[0]` but **never reads
`probes[].argv`**. Mutations that pass (exit 0):

- `probe-argv-replaced`: probe argv pointing at `/somewhere/else.sh` with
  `--port 1` while the row and receipt still say port 32845 → VALID.
- `probe-subcommand-classify`: `result.subcommand: "classify"` instead of
  `"check"` → VALID (only `schema` and `summary.exit` are checked).
- `probe-expected-id-null`: `rows[0].expected_model_id: null` → VALID (the gate
  only compares it when non-null, `:470-473`).

`rows[0].declared` is bound to the port, so a replaced argv with a correct
declared endpoint is internally inconsistent but accepted. Since the probe run
is the verdict evidence, the receipt can name a different invocation than the
identity recorded in `probe{path,sha256}`.

### F4 [Medium] `port_listener_ownership` accepts a token the producer never emits

Gate `:362-368` accepts `child | foreign | unknown`, rejecting `foreign`.
Producer `:850-852` maps ownership to `child | foreign | unproven` — there is no
`unknown`. Accepted mutation `ownership-unknown` → VALID; the real producer
token `unproven` is rejected by name (correct for a complete receipt, since it
would carry `setup_error`, but the vocabulary is not the producer's). A
complete run can only be `child`; requiring exactly `child` is the one-line
binding fix. Note the gate cannot independently re-derive ownership (no `/proc`
snapshot is stored), so this token is the only ownership evidence it has.

### F5 [Medium-low] `install_tree_sha256` is not re-derived; tree membership is unbound

Gate `:254-256` only checks the combined digest is hex or null. Accepted:
`install-tree-sha-wrong` (`"0"*64`), `install-tree-member-removed`
(`libllama.so.0.7.0` deleted), `install-tree-extra-member` (`libevil.so` added).
The launcher digest *is* bound (`tree[basename] == server.sha256`), but the
combined digest — a pure function of the stored tree (`tools/kama-llamacpp-live.py:744`,
computed at `install_tree()`) — is decorative. Recomputation is one expression
over sorted `name sha` lines.

### F6 [Medium-low] Capture status, body digest, and truncation flags are unchecked

Gate reads only `captures.health.status`, `captures.metrics.status`,
`captures.props.fields`, and `captures.models.body`. Accepted:
`models-status-500`, `props-status-500`, `slots-status-500`,
`models-body-sha-wrong`, `models-body-truncated-true`. So a receipt can claim a
500 capture (or `body_truncated: true`) and still pass the alias checks, and no
stored `body` is ever hashed against its `body_sha256`. `body_read_truncated`
and `body_truncated` are never read.

### F7 [Medium-low] `argv` binds alias/port/tail but not host/ctx/threads

Gate `:325-335` requires `--host`, `-c`, `-t` to be *present* and the tail to be
`["--no-webui","--offline"]`, but never compares their values. Accepted:
`argv-host-0.0.0.0`, `argv-ctx-mismatch` (`-c 999999` with `ctx: 256`),
`argv-threads-mismatch` (`-t 999` with `threads: 1`). The capability's
loopback-only property is therefore asserted by `rows[0].declared` and the
receipt's port, not by the recorded launch line.

### F8 [Low] `pdeathsig`, `port_pick_note`, and key presence are ignored

The module docstring lists `pdeathsig` and `port_pick_note` as bound keys
(`:7-14`), but neither is read. Accepted: `pdeathsig-removed`,
`pdeathsig-prctl-false` (a failed `PR_SET_PDEATHSIG`), `setup_error-key-removed`,
`port_pick_note-removed`. Producer emits `pdeathsig` as a dict
(`tools/kama-llamacpp-live.py:846`); the selftest's "valid receipt literal in
the producer's exact shape" uses a **string** (`check-receipt.py:812`) and
`validate()` returns `[]` for it — so the fixture itself falsifies the
exact-shape claim in the permissive direction.

### F9 [Low] `observed` cross-checks are conditional; `documented_by` content unbound

`observed-empty-all-checks` (`observed: {}` on every check) → VALID. All
observed comparisons are `if "status" in o` / `if "data_ids" in o` guards
(`:544`, `:587`, `:601`, …), and `documented_by` is only required to be a
non-empty string (`:514-516`). The raw re-derivation still keeps the ten checks
sound when evidence is honest, so this is a key-binding/claim gap, not a direct
false acceptance.

### F10 [Informational] `teardown_exited` is vacuous, identical to the producer

`teardown-rc-crash-consistent` (rc `1`, observed updated to `1`) → VALID. This
mirrors the producer exactly (`returncode is not None`,
`tools/kama-llamacpp-live.py:953-956`), so it is not a gate divergence; the
check only proves the subprocess was reaped, and `sigkill_sent` is never
cross-checked against rc. Note `teardown-rc-1` was rejected only because the
base `observed.returncode` still said 0; the gate's rejection came from the
observed comparison, not the predicate.

## What holds (confirmation side)

- Consistent forgery matrix: mutating raw evidence **and** the corresponding
  `observed`/`summary` values, keeping `passed: true`, is rejected for 9 of 10
  checks with exit 1 and one problem each: health 500, models id, models owner,
  metrics 200, props alias, both probe flips, teardown port open, model digest
  drift. The tenth (`teardown_exited`) is vacuous by producer definition (F10).
  So the "a bare `passed: true` is never trusted" claim is substantively true
  for the ten checks, with F2 as the exception.
- The selftest's 16 mutations plus the unreadable-receipt case are all rejected
  (exit 0 overall).
- Pinned digests pass both live receipts; malformed `--expect-*` values are
  rejected. The gate never opens a socket, never launches a process except its
  own selftest children, and does not reroute to another runtime.
- `port_refusal_set` re-derives to exactly `[8080, 34113]` today, so the gate's
  hard pins are complete for the current registry; the gate does not parse
  `registry/endpoint-consumers.tsv`, so a future registry port would not be
  detected in a receipt that omitted it.

## Residual risk and verification gaps

- No live receipt exercises `loading_observed: true`; F1's permissiveness is
  demonstrated only on synthetic copies. A future receipt with loading true is
  validated by a path that has never seen live data.
- The gate's digest fields are shape-only unless the caller passes
  `--expect-{model,server,probe}-sha256`; the live `controls.txt` "VALID" lines
  do not show the flags. The ten checks themselves do not depend on external
  pins.
- I did not start `llama-server` (no need for this item) and did not run
  `measure.py`. No `lsp` device appears in this session's tool inventory, so
  caller/definition checks were executed as the validator plus producer-side
  predicates rather than symbolically; this is behaviorally stronger for a
  predicate comparison but does not provide a symbol graph.
- `receipt-frozen-probe.json` and `receipt.json` both have
  `loading_observed: false`; the frozen-probe control therefore cannot
  distinguish loading behavior, only ready behavior (consistent with the
  knowledge entry's disclaimer).

## Suggested repairs (advice only, smallest first)

1. `own != "child"` → invalid; delete `unknown`, name `unproven` as the
   producer's non-child token.
2. In the models loop, append `e.get("id")`/`e.get("owned_by")` even when
   `None`, matching producer `:876-879`; then `all(...)` fails exactly as the
   producer's does.
3. Require `loading_503.status == 503`; require its keys
   `{t_ms,path,status,headers,body_sha256,body}`; require at least one
   `transitions` row with `status == 503` and the same `body_sha256` when
   `loading_observed` is true (and require `transitions` rows have the producer's
   key set).
4. Recompute `install_tree_sha256` from `install_tree` (sorted `name sha` lines)
   and compare.
5. Hash `captures.*.body` where present and compare to `body_sha256`; reject
   when `body_truncated`/`body_read_truncated` is true for a body being parsed.
6. Require `captures.models.status == 200` (and props/slots 200).
7. Bind `argv -c` to `ctx`, `-t` to `threads`, `--host` to `127.0.0.1`.
8. Validate `probes[].argv`: argv[1] == `receipt.probe.path`, `--port` ==
   `port`, `--expect` == `expect`; require `result.subcommand == "check"` and
   `rows[0].expected_model_id == expect`.
9. Validate `pdeathsig == {"requested": true, "prctl_ok": true}` and require
   `setup_error`/`port_pick_note` keys to exist.
10. Require each check's `observed` key set to be the producer's exact set
    (it is stable per check id), and compare `documented_by` to the producer's
    `DOC` strings.

## Installs

None. No pacman/uv/npx/cargo transaction; no host service touched.
